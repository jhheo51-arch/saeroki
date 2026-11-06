"""Stop 훅. 이 세션 프로젝트의 MEMORY.md가 기준을 넘으면 한 줄로 알립니다.

상태가 바뀔 때만 알리고, 무슨 일이 있어도 0으로 끝나 Claude Code를 막지 않습니다.
"""

import json
import sys
from pathlib import Path

from . import memory
from .paths import data_home
from .store import INDEX_LIMIT, LINE_LIMIT, read_json, write_json


def check(index: Path) -> str:
    """기준을 넘었으면 알림 문장, 아니면 빈 문자열."""
    if not index.is_file():
        return ""
    raw = index.read_bytes()  # CRLF도 실제 크기로 셉니다.
    text = raw.decode("utf-8", errors="replace")
    size = len(raw)
    rows = memory.parse_index(text)
    long_lines = sum(len(r["line"]) > LINE_LIMIT for r in rows)
    parts = []
    if size > INDEX_LIMIT:
        parts.append(f"{size:,}바이트(기준 {INDEX_LIMIT:,})")
    if long_lines:
        parts.append(f"{LINE_LIMIT}자 넘는 줄 {long_lines}개")
    if not parts:
        return ""
    msg = "새록 가지치기: MEMORY.md가 " + ", ".join(parts) + "입니다."
    plan = memory.budget(rows, size) if size > INDEX_LIMIT else None
    if plan:
        if plan["reachable"]:
            msg += f" 줄마다 {plan['line']}자 안으로 줄이면 기준 안에 듭니다."
        else:
            msg += f" {plan['line']}자까지 줄여도 {plan['projected_bytes']:,}바이트라 끝난 기억 보관도 필요합니다."
    return msg + " /saerok-memory:dashboard에서 줄일 수 있습니다."


def run(stdin_text: str) -> str:
    try:
        transcript = (json.loads(stdin_text or "{}") or {}).get("transcript_path")
        if not transcript:
            return ""
        index = Path(transcript).parent / "memory" / memory.INDEX
        message = check(index)
        state_path = data_home() / "hook-state.json"
        state = read_json(state_path, {}) or {}
        if state.get(str(index), "") == message:
            return ""
        state[str(index)] = message
        write_json(state_path, state)
        return json.dumps({"systemMessage": message}, ensure_ascii=False) if message else ""
    except Exception:  # 훅은 절대 세션을 막지 않습니다.
        return ""


def main() -> int:
    try:
        data = sys.stdin.buffer.read().decode("utf-8", errors="replace")
    except Exception:
        data = ""
    out = run(data)
    if out:
        sys.stdout.buffer.write(out.encode("utf-8"))
    return 0
