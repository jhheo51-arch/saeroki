"""대시보드 버튼으로만 하는 조치. 바꾸기 전에 백업하고, 기록을 남겨 되돌릴 수 있게 합니다.

서버는 경로를 받지 않고 후보 id만 받습니다. 여기서 다시 검사해 id가 맞는 후보만 손댑니다.
기억 파일은 휴지통으로 보내지 않고 _archive/로 옮기기만 합니다.
"""

import hashlib
import shutil
import sys
import time
from pathlib import Path

from . import memory, sessions, trash, versions
from .paths import claude_home, data_home
from .store import LINE_LIMIT, read_json, write_json, write_text

MISSING = {"__missing__": True}
HOOK_MARK = "saerok_memory hook"


def _read(path: Path) -> str:
    """줄바꿈(CRLF)을 바꾸지 않고 읽습니다."""
    return path.read_bytes().decode("utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest() if path.is_file() else ""


def _log_path() -> Path:
    return data_home() / "apply-log.json"


def load_log() -> list[dict]:
    return read_json(_log_path(), []) or []


def _save(label: str, action: str, ops: list[dict], saved: int = 0) -> dict:
    """saved는 이 조치로 줄인 바이트(목차는 목차 바이트, 휴지통은 파일 크기)입니다."""
    log = load_log()
    entry = {"id": time.strftime("%Y%m%d-%H%M%S") + f"-{len(log)}", "action": action, "label": label,
             "at": time.strftime("%Y-%m-%d %H:%M:%S"), "ops": ops, "saved_bytes": saved, "undone_at": None}
    log.append(entry)
    write_json(_log_path(), log)
    return entry


def _backup(path: Path) -> str:
    """~/.saerok/memory/backup/<날짜>/ 아래에 복사해 둡니다."""
    folder = data_home() / "backup" / time.strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{time.strftime('%H%M%S')}-{path.parent.parent.name[:40]}-{path.name}"
    n = 1
    while target.exists():
        target = target.with_name(f"{target.stem}-{n}{target.suffix}")
        n += 1
    shutil.copy2(path, target)
    return str(target)


def _write(path: Path, text: str) -> dict:
    """백업한 뒤 쓰고, 되돌리기용 기록을 돌려줍니다."""
    backup = _backup(path) if path.exists() else ""
    write_text(path, text)
    return {"type": "write", "path": str(path), "backup": backup, "sha": _sha(path)}


def _find(result: dict, cid: str, kinds: tuple) -> dict:
    for c in result["candidates"]:
        if c["id"] == cid and c["kind"] in kinds:
            if not c.get("actionable"):
                raise ValueError("확인만 하는 후보라 버튼으로 바꾸지 않습니다.")
            return c
    raise ValueError("후보를 찾지 못했습니다. 화면을 새로 고친 뒤 다시 누르세요.")


def _index_of(candidate: dict) -> Path:
    return Path(candidate["path"]).parent / memory.INDEX


# ---- 기억 파일 ----

def index_trim(cid: str, text: str | None = None) -> dict:
    """긴 목차 줄 하나를 줄이고, 원래 설명은 그 기억 파일 끝으로 옮깁니다."""
    return index_trim_many([{"id": cid, "text": text}])


def index_trim_many(items: list[dict]) -> dict:
    """고른 목차 줄을 한 번에 줄입니다. 하나라도 맞지 않으면 아무것도 바꾸지 않고, 기록은 한 건이라 한 번에 되돌립니다."""
    if not items:
        raise ValueError("고른 목차 줄이 없습니다.")
    result = memory.scan()
    plan: dict[Path, list[tuple[dict, str]]] = {}
    seen = set()
    for item in items:
        cid = str(item.get("id", ""))
        if cid in seen:
            continue
        seen.add(cid)
        c = _find(result, cid, ("index_line",))
        new = str(item.get("text") or c["proposal"]).strip()
        row = memory.parse_index(new)
        if len(row) != 1 or row[0]["file"] != Path(c["path"]).name:
            raise ValueError(f"{c['title']}: 고친 줄은 '- [제목](파일) — 설명' 꼴이고 같은 파일을 가리켜야 합니다.")
        if len(new) > LINE_LIMIT:
            raise ValueError(f"{c['title']}: 고친 줄이 {len(new)}자입니다. {LINE_LIMIT}자 안으로 줄여 주세요.")
        plan.setdefault(_index_of(c), []).append((c, new))

    # 먼저 모든 줄을 찾아 본 뒤에 씁니다.
    edits = []
    for index, pairs in plan.items():
        raw = _read(index)
        lines = raw.split("\n")
        for c, new in pairs:
            hits = [i for i, line in enumerate(lines) if line.rstrip("\r") == c["before"]]
            if len(hits) != 1:
                raise ValueError("목차가 그새 바뀌었습니다. 화면을 새로 고치세요.")
            end = "\r" if lines[hits[0]].endswith("\r") else ""
            lines[hits[0]] = new + end
        edits.append((index, raw, lines, pairs))

    ops, before_bytes, after_bytes = [], 0, 0
    today = time.strftime("%Y-%m-%d")
    for index, raw, lines, pairs in edits:
        for c, _ in pairs:
            target = Path(c["path"])
            body = _read(target)
            block = memory.moved_block(memory.parse_index(c["before"])[0], today)
            if "\r\n" in body:
                block = block.replace("\n", "\r\n")
            ops.append(_write(target, body.rstrip("\r\n") + block))
        text = "\n".join(lines)
        ops.append(_write(index, text))
        before_bytes += len(raw.encode("utf-8"))
        after_bytes += len(text.encode("utf-8"))

    pairs = [p for _, _, _, ps in edits for p in ps]
    saved = before_bytes - after_bytes
    if len(pairs) == 1:
        c, new = pairs[0]
        label = f"목차 줄 줄이기: {c['title']}"
        message = f"{c['title']} 목차 줄을 {len(c['before'])}자에서 {len(new)}자로 줄였습니다. 원래 설명은 본문 끝으로 옮겼습니다."
    else:
        label = f"목차 줄 {len(pairs)}개 줄이기"
        message = (f"목차 줄 {len(pairs)}개를 줄였습니다. 목차가 {before_bytes:,}바이트에서 {after_bytes:,}바이트가 됐습니다. "
                   "원래 설명은 각 기억 파일 끝으로 옮겼습니다.")
    entry = _save(label, "index_trim", ops, saved)
    return {"ok": True, "entry": entry, "message": message, "saved_bytes": saved}


def archive(cid: str) -> dict:
    """끝난 기억 파일을 memory/_archive/로 옮기고 목차 줄을 뺍니다."""
    c = _find(memory.scan(), cid, ("archive",))
    src = Path(c["path"])
    index = _index_of(c)
    dst = src.parent / memory.ARCHIVE / src.name
    if dst.exists():
        raise ValueError(f"_archive에 같은 이름이 이미 있습니다: {src.name}")
    raw = _read(index)
    lines = raw.split("\n")
    kept = [line for line in lines if (memory.parse_index(line.rstrip("\r")) or [{}])[0].get("file") != src.name]
    _backup(src)
    ops = [_write(index, "\n".join(kept))]
    dst.parent.mkdir(exist_ok=True)
    shutil.move(str(src), str(dst))
    ops.append({"type": "move", "src": str(src), "dst": str(dst)})
    saved = len(raw.encode("utf-8")) - len("\n".join(kept).encode("utf-8"))
    entry = _save(f"끝난 기억 보관: {c['title']}", "archive", ops, saved)
    return {"ok": True, "entry": entry, "message": f"{src.name}을 _archive로 옮기고 목차에서 뺐습니다."}


# ---- 옛 버전, 세션 기록 ----

def trash_items(ids: list[str]) -> dict:
    """고른 후보를 Windows 휴지통으로 보냅니다. 세션 기록은 집계를 먼저 남깁니다."""
    if not ids:
        raise ValueError("고른 후보가 없습니다.")
    pool = {c["id"]: c for c in versions.scan()["candidates"] + sessions.scan()["candidates"]}
    missing = [i for i in ids if i not in pool]
    if missing:
        raise ValueError(f"후보 {len(missing)}개를 찾지 못했습니다. 화면을 새로 고친 뒤 다시 고르세요.")
    ops, failed, freed = [], [], 0
    for i in dict.fromkeys(ids):
        c = pool[i]
        path = Path(c["path"])
        try:
            if c["kind"] == "session":
                sessions.archive_summary(path)
            trash.send(path)
            if c.get("extra"):
                trash.send(Path(c["extra"]))
            ops.append({"type": "trash", "path": str(path), "extra": c.get("extra", ""), "bytes": c["bytes"]})
            freed += c["bytes"]
        except RuntimeError as e:
            failed.append(str(e))
    if not ops:
        raise RuntimeError("하나도 보내지 못했습니다. " + " / ".join(failed[:3]))
    entry = _save(f"휴지통으로 {len(ops)}개", "trash", ops, freed)
    message = f"{len(ops)}개({freed / 1e6:,.1f}MB)를 휴지통으로 보냈습니다. 비우기는 직접 하세요."
    if failed:
        message += f" 실패 {len(failed)}개: " + " / ".join(failed[:3])
    return {"ok": True, "message": message, "entry": entry}


# ---- Stop 훅(settings.json) ----

def settings_path() -> Path:
    return claude_home() / "settings.json"


def hook_command() -> str:
    """bash에서 실행할 명령. 설치 여부와 관계없이 이 폴더의 코드를 씁니다."""
    python = sys.executable.replace("\\", "/")
    fruit = str(Path(__file__).resolve().parent.parent).replace("\\", "/")
    return f'PYTHONPATH="{fruit}" "{python}" -m {HOOK_MARK}'


def hook_installed(settings: dict | None = None) -> bool:
    if settings is None:
        settings = read_json(settings_path(), {}) or {}
    return any(HOOK_MARK in str(h.get("command", ""))
               for g in (settings.get("hooks") or {}).get("Stop") or [] for h in g.get("hooks") or [])


def _settings_change(label: str, action: str, after_fn) -> dict:
    path = settings_path()
    obj = read_json(path, {}) or {}
    before = (obj.get("hooks") or {}).get("Stop", MISSING)
    after = after_fn(before if isinstance(before, list) else [])
    if after == before or (before == MISSING and not after):
        return {"ok": True, "message": f"{label}: 이미 그 상태라 바꾼 것이 없습니다."}
    backup = _backup(path) if path.exists() else ""
    hooks = obj.setdefault("hooks", {})
    if after:
        hooks["Stop"] = after
    else:
        hooks.pop("Stop", None)
    write_json(path, obj)
    op = {"type": "settings", "path": str(path), "backup": backup, "before": before, "after": after or MISSING}
    entry = _save(label, action, [op])
    return {"ok": True, "entry": entry, "message": f"{label}: 적용했습니다. 새로 여는 Claude Code 세션부터 반영됩니다."}


def hook_install() -> dict:
    def add(groups):
        if any(HOOK_MARK in str(h.get("command", "")) for g in groups for h in g.get("hooks") or []):
            return groups
        return groups + [{"hooks": [{"type": "command", "command": hook_command(), "shell": "bash"}]}]
    return _settings_change("목차 알림 훅 켜기", "hook_install", add)


def hook_remove() -> dict:
    def drop(groups):
        out = []
        for g in groups:
            kept = [h for h in g.get("hooks") or [] if HOOK_MARK not in str(h.get("command", ""))]
            if kept:
                out.append({**g, "hooks": kept})
        return out
    return _settings_change("목차 알림 훅 끄기", "hook_remove", drop)


# ---- 기록 집계 ----

def stats(log: list[dict] | None = None) -> dict:
    """PRD v2.3 6장 성공 지표. 되돌린 비율과, 되돌리지 않은 조치로 줄인 바이트."""
    log = load_log() if log is None else log
    acts = [e for e in log if e.get("action") != "hook_install" and e.get("action") != "hook_remove"]
    undone = [e for e in acts if e.get("undone_at")]
    kept = [e for e in acts if not e.get("undone_at")]
    index = sum(e.get("saved_bytes", 0) for e in kept if e.get("action") in ("index_trim", "archive"))
    files = sum(e.get("saved_bytes", 0) for e in kept if e.get("action") == "trash")
    return {"actions": len(acts), "undone": len(undone),
            "undo_rate": round(len(undone) / len(acts) * 100, 1) if acts else 0.0,
            "index_bytes_saved": index, "trashed_bytes": files}


# ---- 되돌리기 ----

def undo(entry_id: str) -> dict:
    log = load_log()
    entry = next((e for e in log if e["id"] == entry_id), None)
    if not entry or entry.get("undone_at"):
        raise ValueError("되돌릴 기록을 찾지 못했거나 이미 되돌렸습니다.")
    if all(op["type"] == "trash" for op in entry["ops"]):
        names = [Path(op["path"]).name for op in entry["ops"]]
        return {"ok": False, "message": f"휴지통으로 보낸 {len(names)}개는 Windows 휴지통에서 '복원'하세요: " + ", ".join(names[:5])}
    done, skipped = 0, []
    for op in reversed(entry["ops"]):
        if op["type"] == "write":
            path = Path(op["path"])
            if _sha(path) != op["sha"]:  # 적용 뒤 누가 또 고쳤다면 덮어쓰지 않습니다.
                skipped.append(path.name)
                continue
            if op["backup"]:
                _backup(path)
                shutil.copy2(op["backup"], path)
            done += 1
        elif op["type"] == "move":
            src, dst = Path(op["src"]), Path(op["dst"])
            if src.exists() or not dst.exists():
                skipped.append(src.name)
                continue
            shutil.move(str(dst), str(src))
            done += 1
        elif op["type"] == "settings":
            path = Path(op["path"])
            obj = read_json(path, {}) or {}
            if (obj.get("hooks") or {}).get("Stop", MISSING) != op["after"]:
                skipped.append("settings.json hooks > Stop")
                continue
            _backup(path)
            if op["before"] == MISSING:
                obj.get("hooks", {}).pop("Stop", None)
            else:
                obj.setdefault("hooks", {})["Stop"] = op["before"]
            write_json(path, obj)
            done += 1
    entry["undone_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    write_json(_log_path(), log)
    message = f"{entry['label']}: 되돌렸습니다."
    if skipped:
        message += " 적용 뒤 다시 바뀐 것은 건드리지 않았습니다: " + ", ".join(skipped)
    return {"ok": True, "message": message, "skipped": skipped}
