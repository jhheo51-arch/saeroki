"""Claude 세션 기록 검사(PRD v2.3 5.3절).

projects/*/*.jsonl 중 30일 넘게 바뀌지 않은 기록만 후보로 둡니다. 30분 안에 바뀐 기록은 열려 있다고 보고 뺍니다.
버리기 전에 숫자 집계(응답 수, 처리 토큰, 최대 컨텍스트, 첫·마지막 시각)를 session-archive.jsonl에 남깁니다. 대화 원문은 남기지 않습니다.
"""

import json
import time
from pathlib import Path

from .memory import cid
from .paths import data_home, projects_dir
from .store import OPEN_SECONDS, SESSION_DAYS


def _context(usage: dict) -> int:
    return sum(int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))


def summarize(log: Path) -> dict:
    """세션 기록 한 개의 숫자 집계."""
    out = {"session_id": log.stem, "project": log.parent.name, "responses": 0, "processed": 0,
           "max_ctx": 0, "first_ts": "", "last_ts": "", "cwd": ""}
    try:
        with open(log, encoding="utf-8", errors="replace") as f:
            for line in f:
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = row.get("timestamp") or ""
                if ts:
                    out["first_ts"] = out["first_ts"] or ts
                    out["last_ts"] = ts
                if not out["cwd"] and row.get("cwd"):
                    out["cwd"] = row["cwd"]
                msg = row.get("message") if row.get("type") == "assistant" else None
                if isinstance(msg, dict) and msg.get("usage"):
                    ctx = _context(msg["usage"])
                    out["responses"] += 1
                    out["processed"] += ctx + int(msg["usage"].get("output_tokens") or 0)
                    out["max_ctx"] = max(out["max_ctx"], ctx)
    except OSError:
        pass
    return out


def _size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file()) if path.is_dir() else 0


def scan(now: float | None = None) -> dict:
    now = now or time.time()
    root = projects_dir()
    logs = sorted(root.glob("*/*.jsonl")) if root.is_dir() else []
    candidates, total, opened = [], 0, 0
    for log in logs:
        try:
            st = log.stat()
        except OSError:
            continue
        side = log.with_suffix("")  # 같은 이름 폴더(subagents 등)
        size = st.st_size + _size(side)
        total += size
        age = now - st.st_mtime
        if age <= OPEN_SECONDS:
            opened += 1
            continue
        if age <= SESSION_DAYS * 86400:
            continue
        candidates.append({
            "id": cid("session", str(log), int(st.st_mtime), st.st_size), "kind": "session",
            "project": log.parent.name, "path": str(log), "extra": str(side) if side.is_dir() else "",
            "title": log.stem, "actionable": True, "bytes": size,
            "reason": f"마지막 기록 {int(age // 86400)}일 전",
        })
    candidates.sort(key=lambda c: -c["bytes"])
    return {"logs": len(logs), "bytes": total, "open": opened, "candidates": candidates}


def archive_summary(log: Path) -> dict:
    """버리기 전에 집계 한 줄을 남깁니다. 같은 세션은 한 번만 적습니다."""
    row = summarize(log) | {"archived_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    path = data_home() / "session-archive.jsonl"
    seen = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                seen.add(json.loads(line).get("session_id"))
            except json.JSONDecodeError:
                pass
    if row["session_id"] not in seen:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
