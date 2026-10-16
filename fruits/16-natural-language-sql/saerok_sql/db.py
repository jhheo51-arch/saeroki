"""데이터 준비와 읽기 전용 실행.

저장소의 Parquet을 처음 한 번 로컬 DuckDB 파일로 묶고, 이후에는 읽기 전용·외부 접근 차단으로 엽니다.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path

import duckdb

from .safety import check_sql

FRUIT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.environ.get("SAEROK_SQL_DATA", FRUIT_DIR / "data"))
MAX_ROWS = 1000
TIMEOUT_SECONDS = 30


def app_dir() -> Path:
    base = os.environ.get("SAEROK_SQL_HOME") or os.environ.get("LOCALAPPDATA") or str(Path.home() / ".local" / "share")
    path = Path(base) / "saerok-sql"
    path.mkdir(parents=True, exist_ok=True)
    return path


class QueryError(Exception):
    """SQL이 안전 검사에서 막혔거나 실행 중 오류가 났습니다."""

    def __init__(self, message: str, blocked: bool = False):
        super().__init__(message)
        self.blocked = blocked


@dataclass
class QueryResult:
    columns: list[str]
    rows: list[tuple]
    truncated: bool
    seconds: float
    types: list[str] = field(default_factory=list)


def parquet_files(data_dir: Path = DATA_DIR) -> list[Path]:
    files = sorted(data_dir.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"데이터 파일(.parquet)이 없습니다: {data_dir}")
    return files


def _fingerprint(files: list[Path]) -> str:
    digest = hashlib.sha256()
    for f in files:
        stat = f.stat()
        digest.update(f"{f.name}:{stat.st_size}:{int(stat.st_mtime)}".encode())
    return digest.hexdigest()[:12]


def build_database(data_dir: Path = DATA_DIR, target_dir: Path | None = None) -> Path:
    """Parquet 묶음을 DuckDB 파일 하나로 만듭니다. 이미 같은 데이터로 만든 파일이 있으면 그대로 씁니다."""
    files = parquet_files(data_dir)
    target_dir = target_dir or app_dir()
    db_path = target_dir / f"seoul-{_fingerprint(files)}.duckdb"
    if db_path.exists():
        return db_path
    tmp = db_path.with_suffix(".building")
    if tmp.exists():
        tmp.unlink()
    con = duckdb.connect(str(tmp))
    try:
        for f in files:
            con.execute(f'CREATE TABLE "{f.stem}" AS SELECT * FROM read_parquet(?)', [str(f)])
    finally:
        con.close()
    tmp.replace(db_path)
    return db_path


class Database:
    def __init__(self, db_path: Path | None = None):
        self.path = Path(db_path) if db_path else build_database()
        self.con = duckdb.connect(
            str(self.path),
            read_only=True,
            config={"enable_external_access": False, "lock_configuration": True},
        )

    def close(self) -> None:
        self.con.close()

    def tables(self) -> dict[str, list[tuple[str, str]]]:
        rows = self.con.execute(
            "SELECT table_name, column_name, data_type FROM information_schema.columns "
            "WHERE table_schema = 'main' ORDER BY table_name, ordinal_position"
        ).fetchall()
        out: dict[str, list[tuple[str, str]]] = {}
        for table, column, dtype in rows:
            out.setdefault(table, []).append((column, dtype))
        return out

    def run(self, sql: str, max_rows: int = MAX_ROWS, timeout: float = TIMEOUT_SECONDS) -> QueryResult:
        verdict = check_sql(sql)
        if not verdict.ok:
            raise QueryError(verdict.reason, blocked=True)
        timer = threading.Timer(timeout, self.con.interrupt)
        start = time.perf_counter()
        timer.start()
        try:
            cursor = self.con.execute(sql.strip().rstrip(";"))
            columns = [d[0] for d in cursor.description]
            types = [str(d[1]) for d in cursor.description]
            rows = cursor.fetchmany(max_rows + 1)
        except duckdb.InterruptException:
            raise QueryError(f"{timeout:.0f}초 안에 끝나지 않아 멈췄습니다")
        except duckdb.Error as error:
            raise QueryError(str(error).strip())
        finally:
            timer.cancel()
        return QueryResult(columns, rows[:max_rows], len(rows) > max_rows, time.perf_counter() - start, types)
