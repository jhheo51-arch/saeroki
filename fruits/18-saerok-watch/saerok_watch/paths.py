"""새록 파수꾼이 읽고 쓰는 위치. 검사에서는 환경 변수로 바꿉니다."""

import os
from pathlib import Path


def claude_home() -> Path:
    return Path(os.environ.get("SAEROK_WATCH_CLAUDE_HOME") or Path.home() / ".claude")


def claude_json() -> Path:
    return Path(os.environ.get("SAEROK_WATCH_CLAUDE_JSON") or Path.home() / ".claude.json")


def data_home() -> Path:
    path = Path(os.environ.get("SAEROK_WATCH_HOME") or Path.home() / ".saerok-watch")
    path.mkdir(parents=True, exist_ok=True)
    return path


FRUIT_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DAILY = FRUIT_DIR / "data" / "public-daily.json"
