"""새록 가지치기가 읽고 쓰는 위치. 검사에서는 환경 변수로 바꿉니다."""

import os
from pathlib import Path


def claude_home() -> Path:
    return Path(os.environ.get("SAEROK_MEMORY_CLAUDE_HOME") or Path.home() / ".claude")


def projects_dir() -> Path:
    return claude_home() / "projects"


def data_home() -> Path:
    path = Path(os.environ.get("SAEROK_MEMORY_HOME") or Path.home() / ".saerok" / "memory")
    path.mkdir(parents=True, exist_ok=True)
    return path


def desktops() -> list[Path]:
    """보호 목록의 바탕화면. OneDrive로 옮겨진 바탕화면도 함께 봅니다."""
    env = os.environ.get("SAEROK_MEMORY_DESKTOP")
    if env:
        return [Path(p) for p in env.split(os.pathsep) if p]
    home = Path.home()
    found = [home / "Desktop", home / "바탕 화면"]
    found += [p / "Desktop" for p in home.glob("OneDrive*")] + [p / "바탕 화면" for p in home.glob("OneDrive*")]
    return [p for p in found if p.is_dir()]
