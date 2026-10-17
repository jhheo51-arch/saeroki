"""면접 화면의 Claude API 키를 Windows 자격 증명 관리자(keyring)에 보관합니다. 파일이나 기록에는 남기지 않습니다.
keyring이 없으면 이번 실행 동안 메모리에만 둡니다."""

import os

try:
    import keyring
    from keyring.errors import KeyringError, PasswordDeleteError
except ImportError:  # keyring 없이도 화면은 열립니다.
    keyring = None

SERVICE = "saerok-interview"
SHARED = ["saerok-idea", "saerok-sql"]  # 20번 새록 심사단·16번 새록 SQL에 이미 등록한 키가 있으면 같이 씁니다.
USERNAME = "anthropic-api-key"
_memory: dict[str, str] = {}


def get_key() -> tuple[str | None, str]:
    """(키, 어디서 읽었는지)."""
    if keyring:
        for service in [SERVICE, *SHARED]:
            try:
                key = keyring.get_password(service, USERNAME)
            except KeyringError:
                key = None
            if key:
                return key, f"자격 증명 관리자({service})"
    if _memory.get("key"):
        return _memory["key"], "이번 실행 메모리"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"], "환경 변수 ANTHROPIC_API_KEY"
    return None, ""


def set_key(key: str) -> str:
    key = key.strip()
    if not key.startswith("sk-ant-"):
        raise ValueError("Anthropic API 키는 sk-ant-로 시작합니다.")
    if keyring:
        try:
            keyring.set_password(SERVICE, USERNAME, key)
            return f"자격 증명 관리자({SERVICE})"
        except KeyringError:
            pass
    _memory["key"] = key
    return "이번 실행 메모리"


def delete_key() -> bool:
    found = bool(_memory.pop("key", None))
    if keyring:
        try:
            keyring.delete_password(SERVICE, USERNAME)
            found = True
        except (PasswordDeleteError, KeyringError):
            pass
    return found


def masked(key: str | None) -> str:
    if not key:
        return "등록 안 됨"
    return f"{key[:10]}…{key[-4:]}"
