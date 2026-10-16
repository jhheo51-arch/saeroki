"""Claude Code Stop 훅. 응답이 끝날 때마다 컨텍스트 크기를 재고, 기준을 처음 넘으면 한 줄로 알립니다.

어떤 오류가 나도 Claude Code를 멈추지 않도록 항상 조용히 0으로 끝납니다.
"""

import json
import sys
import time
from pathlib import Path

from . import notify
from .paths import data_home
from .scan import context_of
from .store import load_config, read_json, write_json

TAIL_BYTES = 2_000_000


def last_context(transcript: Path) -> int:
    """기록 파일 끝부분에서 마지막 응답의 컨텍스트 크기를 찾습니다."""
    with open(transcript, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - TAIL_BYTES))
        lines = f.read().decode("utf-8", errors="replace").splitlines()
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "assistant":
            ctx = context_of((d.get("message") or {}).get("usage") or {})
            if ctx:
                return ctx
    return 0


def level_of(ctx: int, config: dict) -> int:
    if ctx >= config["warn"]:
        return 2
    if ctx >= config["caution"]:
        return 1
    return 0


def parts(ctx: int, level: int) -> tuple[str, str]:
    """(제목, 본문). 대화 한 줄과 Windows 알림이 같은 문장을 씁니다."""
    size = f"{ctx / 10_000:.1f}만"
    if level == 2:
        return (f"파수꾼 새록이 · 경고: 컨텍스트 {size} 토큰",
                "이 대화는 응답마다 이만큼 다시 읽어요. 지금 작업을 정리하고 새 세션이나 /compact를 권해요.")
    return (f"파수꾼 새록이 · 주의: 컨텍스트 {size} 토큰",
            "작업이 바뀌면 새 세션에서 이어 가면 사용량을 아낄 수 있어요.")


def message(ctx: int, level: int) -> str:
    title, body = parts(ctx, level)
    return f"🪖 {title}. {body}"


def check(payload: dict) -> str | None:
    """경고 문장을 돌려주거나, 알릴 것이 없으면 None."""
    transcript = Path(payload.get("transcript_path") or "")
    if not transcript.is_file():
        return None
    session = str(payload.get("session_id") or transcript.stem)
    config = load_config()
    ctx = last_context(transcript)
    level = level_of(ctx, config)

    state_path = data_home() / "hook-state.json"
    state = read_json(state_path, {}) or {}
    previous = state.get(session, {}).get("level", 0)
    state[session] = {"level": level, "ctx": ctx, "at": time.time()}
    # 일주일 넘은 세션 상태는 지웁니다.
    cutoff = time.time() - 7 * 86400
    state = {k: v for k, v in state.items() if v.get("at", 0) >= cutoff}
    write_json(state_path, state)

    if level <= previous:
        return None
    with open(data_home() / "alerts.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({
            "at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "session_id": session,
            "ctx": ctx,
            "level": level,
        }, ensure_ascii=False) + "\n")
    if config.get("toast", True):
        try:
            notify.toast(*parts(ctx, level))
        except Exception:  # 알림이 실패해도 대화 안 한 줄은 그대로 보냅니다.
            pass
    return message(ctx, level)


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        text = check(json.loads(raw or "{}"))
        if text:
            sys.stdout.buffer.write(json.dumps({"systemMessage": text}, ensure_ascii=False).encode("utf-8"))
    except Exception:  # 훅은 절대 Claude Code를 방해하지 않습니다.
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
