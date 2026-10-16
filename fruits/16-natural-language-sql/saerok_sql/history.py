"""물어본 기록: 내 PC에만 쌓고, 파일로 내보내 다른 PC에서 불러옵니다.

결과 값 전체는 남기지 않고 질문·SQL·행 수·상태만 남깁니다.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path

from .db import app_dir


class History:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else app_dir() / "history.jsonl"

    def add(self, answer, model: str) -> dict:
        entry = {
            "id": uuid.uuid4().hex,
            "at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "mode": answer.mode,
            "input": answer.input,
            "sql": answer.sql,
            "status": answer.status,
            "rows": len(answer.result.rows) if answer.result else None,
            "truncated": bool(answer.result and answer.result.truncated),
            "attempts": answer.attempts,
            "message": answer.message,
            "model": model,
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def all(self) -> list[dict]:
        if not self.path.exists():
            return []
        entries = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                entries.append(json.loads(line))
        return entries

    def recent(self, n: int = 10) -> list[dict]:
        return self.all()[-n:]

    def export(self, target: Path) -> int:
        entries = self.all()
        Path(target).write_text(json.dumps({"saerok_sql_history": 1, "entries": entries}, ensure_ascii=False, indent=1), encoding="utf-8")
        return len(entries)

    def import_(self, source: Path) -> int:
        data = json.loads(Path(source).read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "entries" not in data:
            raise ValueError("새록 SQL 기록 파일이 아닙니다")
        known = {e["id"] for e in self.all()}
        new = [e for e in data["entries"] if e.get("id") not in known]
        new.sort(key=lambda e: e.get("at", ""))
        with self.path.open("a", encoding="utf-8") as f:
            for entry in new:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return len(new)
