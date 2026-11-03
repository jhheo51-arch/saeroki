"""슬랙 토큰과 주인 ID를 Windows 자격 증명 관리자(keyring)에 보관합니다. 파일이나 기록에는 남기지 않습니다."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

SERVICE = "saerok-slack"
REPO = Path(__file__).resolve().parents[2]
HOME = Path(os.environ.get("SAEROK_SLACK_HOME", Path.home() / ".saerok" / "slack"))

# 이름: (환경 변수, 앞머리 검사, 설명)
FIELDS = {
    "bot-token": ("SLACK_BOT_TOKEN", re.compile(r"^xoxb-[\w-]+$"), "Bot Token(xoxb-로 시작)"),
    "app-token": ("SLACK_APP_TOKEN", re.compile(r"^xapp-[\w-]+$"), "App-Level Token(xapp-로 시작)"),
    "owner": ("SAEROK_SLACK_OWNER", re.compile(r"^[UW][A-Z0-9]{6,}$"), "내 슬랙 멤버 ID(U로 시작)"),
}


def get(name: str) -> str | None:
    env, _, _ = FIELDS[name]
    if os.environ.get(env):
        return os.environ[env].strip()
    try:
        return keyring.get_password(SERVICE, name)
    except KeyringError:
        return None


def check(name: str, value: str) -> str:
    value = value.strip()
    _, pattern, label = FIELDS[name]
    if not pattern.match(value):
        raise ValueError(f"{label} 형식이 아닙니다")
    return value


def put(name: str, value: str) -> None:
    keyring.set_password(SERVICE, name, check(name, value))


def delete(name: str) -> bool:
    try:
        keyring.delete_password(SERVICE, name)
        return True
    except (PasswordDeleteError, KeyringError):
        return False


def masked(name: str, value: str | None) -> str:
    if not value:
        return "등록 안 됨"
    if name == "owner":
        return value
    return f"{value[:9]}…{value[-4:]}"


# 일상 대화를 받을 채널. 비밀이 아니므로 ~/.saerok/slack/settings.json에 둡니다.
CHANNEL = re.compile(r"^[CG][A-Z0-9]{6,}$")


def settings_path() -> Path:
    return HOME / "settings.json"


def settings() -> dict:
    path = settings_path()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def save_setting(key: str, value) -> None:
    data = settings()
    data[key] = value
    path = settings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def chat_channels() -> list[str]:
    return settings().get("chat_channels", [])


def set_chat_channel(channel: str, on: bool = True) -> list[str]:
    channel = channel.strip()
    if not CHANNEL.match(channel):
        raise ValueError(f"채널 ID 형식이 아닙니다(C로 시작): {channel}")
    channels = [c for c in chat_channels() if c != channel] + ([channel] if on else [])
    save_setting("chat_channels", channels)
    return channels


# 주인이 /saerok-master 쉬기로 AI 대화를 잠시 끈 상태. 사전과 끝말잇기는 그대로 됩니다.
def resting() -> bool:
    return bool(settings().get("resting"))


def set_resting(on: bool) -> None:
    save_setting("resting", on)
