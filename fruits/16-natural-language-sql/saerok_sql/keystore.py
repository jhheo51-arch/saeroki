"""Claude API 키를 Windows 자격 증명 관리자(keyring)에 보관합니다. 파일이나 기록에는 남기지 않습니다."""

from __future__ import annotations

import keyring
from keyring.errors import KeyringError, PasswordDeleteError

SERVICE = "saerok-sql"
USERNAME = "anthropic-api-key"


def get_key() -> str | None:
    try:
        return keyring.get_password(SERVICE, USERNAME)
    except KeyringError:
        return None


def set_key(key: str) -> None:
    key = key.strip()
    if not key.startswith("sk-ant-"):
        raise ValueError("Anthropic API 키는 sk-ant-로 시작합니다")
    keyring.set_password(SERVICE, USERNAME, key)


def delete_key() -> bool:
    try:
        keyring.delete_password(SERVICE, USERNAME)
        return True
    except (PasswordDeleteError, KeyringError):
        return False


def masked(key: str | None) -> str:
    if not key:
        return "등록 안 됨"
    return f"{key[:10]}…{key[-4:]}"
