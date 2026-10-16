"""Claude Code 상태줄. 지금 세션의 컨텍스트 크기와 다음 기준까지 남은 양을 한 줄로 늘 보여 줍니다.

예: 🪖 18.2만 ████░░░░ 주의까지 1.8만
어떤 오류가 나도 상태줄을 비우지 않도록 짧은 기본 문장을 내보냅니다.
"""

import json
import sys
from pathlib import Path

from .hook import last_context, level_of
from .store import load_config

CELLS = 8
COLORS = ("\033[32m", "\033[33m", "\033[31m")  # 여유 초록 · 주의 노랑 · 경고 빨강
RESET = "\033[0m"


def _man(n: int) -> str:
    return f"{n / 10_000:.1f}만"


def context_from(payload: dict) -> int:
    """Claude Code가 넘겨준 마지막 응답 크기를 쓰고, 없으면 기록 파일에서 찾습니다."""
    usage = (payload.get("context_window") or {}).get("current_usage")
    if isinstance(usage, dict):
        ctx = sum(int(usage.get(k) or 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
        if ctx:
            return ctx
    transcript = Path(payload.get("transcript_path") or "")
    return last_context(transcript) if transcript.is_file() else 0


def line(ctx: int, config: dict, color: bool = True) -> str:
    level = level_of(ctx, config)
    filled = min(CELLS, round(ctx / config["warn"] * CELLS))
    bar = "█" * filled + "░" * (CELLS - filled)
    if level == 0:
        rest = f"주의까지 {_man(config['caution'] - ctx)}"
    elif level == 1:
        rest = f"경고까지 {_man(config['warn'] - ctx)}"
    else:
        rest = f"경고 넘음 +{_man(ctx - config['warn'])} · 새 세션 권장"
    if color:
        bar = f"{COLORS[level]}{bar}{RESET}"
    return f"🪖 {_man(ctx)} {bar} {rest}"


def main() -> int:
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        text = line(context_from(json.loads(raw or "{}")), load_config())
    except Exception:  # 상태줄은 절대 Claude Code를 방해하지 않습니다.
        text = "🪖 파수꾼 대기 중"
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0
