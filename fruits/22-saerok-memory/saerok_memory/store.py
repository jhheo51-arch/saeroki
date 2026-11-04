"""JSON 파일 읽기·쓰기와 기준값."""

import json
import os
import tempfile
from pathlib import Path

# PRD v2.3 4장에서 확정한 기준. 바꾸려면 PRD부터 고칩니다.
LINE_LIMIT = 150            # 목차 한 줄 글자 수
INDEX_LIMIT = 4_000         # 목차 MEMORY.md 바이트
BUDGET_MIN_LINE = 60        # 목차 예산을 맞출 때 이보다 짧게 자르자고 하지 않음
MEMORY_DAYS = 30            # 마감·중단 뒤 지난 날
VERSION_DAYS = 14           # 옛 버전 파일 마지막 수정 뒤
SESSION_DAYS = 30           # 세션 기록 마지막 수정 뒤
OPEN_SECONDS = 30 * 60      # 이 안에 바뀐 세션 기록은 열려 있다고 봄
CHARS_PER_TOKEN = 3         # 18번 파수꾼과 같은 글자 수 어림


def read_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return default


def write_json(path: Path, value) -> None:
    """임시 파일에 쓴 뒤 바꿔 끼워, 쓰다 끊겨도 원래 파일이 깨지지 않게 합니다."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise
