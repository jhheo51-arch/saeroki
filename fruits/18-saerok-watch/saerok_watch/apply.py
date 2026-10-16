"""적용 탭의 조치. 바꾸기 전에 파일을 백업하고, 바꾼 키의 이전 값을 기록해 그 키만 되돌립니다."""

import shutil
import sys
import time
from pathlib import Path

from .paths import claude_home, claude_json, data_home
from .store import read_json, write_json

MISSING = {"__missing__": True}
HOOK_MARK = "saerok_watch hook"


def files() -> dict[str, Path]:
    return {"settings": claude_home() / "settings.json", "claude_json": claude_json()}


def hook_command() -> str:
    """bash에서 실행할 훅 명령. 설치(pip install -e) 여부와 관계없이 이 폴더의 코드를 씁니다."""
    python = sys.executable.replace("\\", "/")
    fruit = str(Path(__file__).resolve().parent.parent).replace("\\", "/")
    return f'PYTHONPATH="{fruit}" "{python}" -m {HOOK_MARK}'


def _get(obj, path):
    for key in path:
        if not isinstance(obj, dict) or key not in obj:
            return MISSING
        obj = obj[key]
    return obj


def _set(obj, path, value):
    for key in path[:-1]:
        obj = obj.setdefault(key, {})
    if value == MISSING:
        obj.pop(path[-1], None)
    else:
        obj[path[-1]] = value


PLUGIN_PREFIX = "saerok-watch@"


def plugin_active(settings: dict) -> bool:
    """플러그인으로 설치해 훅이 이미 돌고 있는지."""
    return any(k.startswith(PLUGIN_PREFIX) and v is True for k, v in (settings.get("enabledPlugins") or {}).items())


def hook_installed(settings: dict) -> bool:
    for group in (settings.get("hooks") or {}).get("Stop") or []:
        for hook in group.get("hooks") or []:
            if HOOK_MARK in str(hook.get("command", "")):
                return True
    return False


def plan(action: str) -> tuple[str, list[dict]]:
    """조치 이름을 (설명, 바꿀 키 목록)으로 바꿉니다. 이미 그 상태면 목록이 비어 있습니다."""
    settings = read_json(files()["settings"], {}) or {}
    name, _, arg = action.partition(":")
    changes = []

    if name == "hook_install":
        if not hook_installed(settings) and not plugin_active(settings):
            before = _get(settings, ["hooks", "Stop"])
            after = list(before) if isinstance(before, list) else []
            after.append({"hooks": [{"type": "command", "command": hook_command(), "shell": "bash"}]})
            changes.append({"file": "settings", "path": ["hooks", "Stop"], "after": after})
        return "새록 파수꾼 훅 설치", changes

    if name == "hook_remove":
        # 플러그인과 직접 넣은 훅이 함께 돌면 직접 넣은 쪽만 뺍니다.
        before = _get(settings, ["hooks", "Stop"])
        if isinstance(before, list):
            after = []
            for group in before:
                kept = [h for h in group.get("hooks") or [] if HOOK_MARK not in str(h.get("command", ""))]
                if kept:
                    after.append({**group, "hooks": kept})
            if after != before:
                changes.append({"file": "settings", "path": ["hooks", "Stop"], "after": after})
        return "직접 넣은 파수꾼 훅 빼기", changes

    if name == "autocompact":
        value = int(arg)
        if not 100_000 <= value <= 1_000_000:
            raise ValueError("자동 압축 창은 100000~1000000 사이여야 합니다.")
        if settings.get("autoCompactWindow") != value:
            changes.append({"file": "settings", "path": ["autoCompactWindow"], "after": value})
        return f"자동 압축 창을 {value // 1000}K로", changes

    if name == "mcp_off":
        cj = read_json(files()["claude_json"], {}) or {}
        if arg not in (cj.get("mcpServers") or {}):
            raise ValueError(f"사용자 MCP 서버 '{arg}'를 찾지 못했습니다.")
        for project, conf in (cj.get("projects") or {}).items():
            current = conf.get("disabledMcpServers") or []
            if arg not in current:
                changes.append({
                    "file": "claude_json",
                    "path": ["projects", project, "disabledMcpServers"],
                    "after": list(current) + [arg],
                })
        return f"MCP 서버 {arg} 끄기(모든 프로젝트)", changes

    if name == "plugin_off":
        if (settings.get("enabledPlugins") or {}).get(arg) is True:
            changes.append({"file": "settings", "path": ["enabledPlugins", arg], "after": False})
        return f"플러그인 {arg} 끄기", changes

    raise ValueError(f"알 수 없는 조치: {action}")


def _log_path() -> Path:
    return data_home() / "apply-log.json"


def load_log() -> list[dict]:
    return read_json(_log_path(), []) or []


def _backup(path: Path, stamp: str) -> None:
    if path.exists():
        folder = data_home() / "backups"
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, folder / f"{stamp}-{path.name}")


def apply(action: str) -> dict:
    label, changes = plan(action)
    if not changes:
        return {"ok": True, "message": f"{label}: 이미 적용된 상태라 바꾼 것이 없습니다."}
    stamp = time.strftime("%Y%m%d-%H%M%S")
    by_file = {}
    for c in changes:
        by_file.setdefault(c["file"], []).append(c)
    for key, items in by_file.items():
        path = files()[key]
        _backup(path, stamp)
        obj = read_json(path, {}) or {}
        for c in items:
            c["before"] = _get(obj, c["path"])
            _set(obj, c["path"], c["after"])
        write_json(path, obj)
    entry = {"id": stamp + f"-{len(load_log())}", "action": action, "label": label,
             "at": time.strftime("%Y-%m-%d %H:%M:%S"), "changes": changes, "undone_at": None}
    log = load_log()
    log.append(entry)
    write_json(_log_path(), log)
    return {"ok": True, "message": f"{label}: 적용했습니다. 새로 여는 Claude Code 세션부터 반영됩니다.", "entry": entry}


def undo(entry_id: str) -> dict:
    log = load_log()
    entry = next((e for e in log if e["id"] == entry_id), None)
    if not entry or entry.get("undone_at"):
        raise ValueError("되돌릴 기록을 찾지 못했거나 이미 되돌렸습니다.")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    skipped = []
    by_file = {}
    for c in reversed(entry["changes"]):
        by_file.setdefault(c["file"], []).append(c)
    for key, items in by_file.items():
        path = files()[key]
        _backup(path, stamp)
        obj = read_json(path, {}) or {}
        for c in items:
            # 적용 뒤 누가 같은 키를 또 바꿨다면 덮어쓰지 않고 알립니다.
            if _get(obj, c["path"]) != c["after"]:
                skipped.append(" > ".join(c["path"]))
                continue
            _set(obj, c["path"], c["before"])
        write_json(path, obj)
    entry["undone_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    write_json(_log_path(), log)
    message = f"{entry['label']}: 되돌렸습니다."
    if skipped:
        message += " 적용 뒤 다시 바뀐 항목은 건드리지 않았습니다: " + ", ".join(skipped)
    return {"ok": True, "message": message, "skipped": skipped}
