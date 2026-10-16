"""JSON 파일 읽기·쓰기와 사용자 설정."""

import json
import os
import tempfile
from pathlib import Path

from .paths import data_home

DEFAULT_CONFIG = {"caution": 200_000, "warn": 400_000, "toast": True}


def read_json(path: Path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
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


def load_config() -> dict:
    config = dict(DEFAULT_CONFIG)
    config.update(read_json(data_home() / "config.json", {}) or {})
    return config


def save_config(caution: int, warn: int, toast: bool = True) -> dict:
    if not (10_000 <= caution < warn <= 1_000_000):
        raise ValueError("주의 기준은 1만 이상이고 경고 기준보다 작아야 하며, 경고 기준은 100만 이하여야 합니다.")
    config = {"caution": int(caution), "warn": int(warn), "toast": bool(toast)}
    write_json(data_home() / "config.json", config)
    return config
