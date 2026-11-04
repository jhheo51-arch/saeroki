"""작업 폴더 옛 버전 검사(PRD v2.3 5.2절).

같은 폴더, 같은 줄기 이름, 같은 확장자끼리 묶어 가장 높은 버전과 바로 앞 버전은 남기고,
나머지 중 14일 넘게 수정이 없는 파일만 후보로 둡니다. git이 추적하는 파일과 보호 목록은 뺍니다.
"""

import os
import re
import subprocess
import time
from pathlib import Path

from .memory import cid, project_cwd
from .paths import desktops, projects_dir
from .store import VERSION_DAYS

VERSION = re.compile(r"^(?P<stem>.*?)[ _.-]?[vV](?P<major>\d+)(?:\.(?P<minor>\d+))?(?P<tail>[ _-]?[^.]*)$")
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist", "build", ".cache"}
PROTECT_WORDS = ("제출", "최종", "final")


def work_roots() -> list[Path]:
    """세션 기록에 남은 작업 폴더. 다른 폴더 안에 든 폴더는 바깥 폴더 하나로 합칩니다.
    홈 폴더나 드라이브 맨 위처럼 너무 넓은 곳은 뺍니다."""
    root = projects_dir()
    cwds = [project_cwd(p) for p in root.iterdir() if p.is_dir()] if root.is_dir() else []
    home = Path.home().resolve()
    found = sorted({Path(c).resolve() for c in cwds if c and Path(c).is_dir()}, key=lambda p: len(p.parts))
    roots = []
    for p in found:
        if p == home or p.parent == p:
            continue
        if not any(p == r or r in p.parents for r in roots):
            roots.append(p)
    return roots


def protected(path: Path) -> str:
    """보호 이유. 보호 대상이 아니면 빈 문자열."""
    low = path.name.lower()
    if any(w in low for w in PROTECT_WORDS):
        return "이름에 제출·최종·final"
    for d in desktops():
        try:
            path.resolve().relative_to(d.resolve())
            return "바탕화면 아래"
        except ValueError:
            pass
    return ""


def git_tracked(root: Path) -> set[str]:
    """root 아래 git 저장소들이 추적하는 파일(소문자 절대 경로)."""
    tracked = set()
    for dirpath, dirnames, _ in os.walk(root):
        if ".git" in dirnames:
            repo = Path(dirpath)
            try:
                out = subprocess.run(["git", "-C", str(repo), "ls-files", "-z"], capture_output=True, timeout=60)
                for name in out.stdout.decode("utf-8", errors="replace").split("\0"):
                    if name:
                        tracked.add(str((repo / name).resolve()).lower())
            except (OSError, subprocess.SubprocessError):
                pass
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    return tracked


def parse(name: str):
    stem, ext = os.path.splitext(name)
    m = VERSION.match(stem)
    if not m or not m["stem"]:
        return None
    return (m["stem"].lower() + (m["tail"] or "").lower(), ext.lower()), (int(m["major"]), int(m["minor"] or 0))


def scan(roots: list[Path] | None = None, now: float | None = None) -> dict:
    now = now or time.time()
    roots = work_roots() if roots is None else roots
    groups: dict[tuple, list[tuple]] = {}
    tracked = set()
    for root in roots:
        tracked |= git_tracked(root)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for name in filenames:
                parsed = parse(name)
                if parsed:
                    key, version = parsed
                    groups.setdefault((dirpath.lower(),) + key, []).append((version, Path(dirpath) / name))

    candidates, kept, guarded = [], 0, 0
    total_files = total_bytes = 0
    for key, items in groups.items():
        if len(items) < 2:
            continue
        items.sort(key=lambda x: x[0])
        versions = sorted({v for v, _ in items})
        keep = set(versions[-2:])
        newest = items[-1][1]
        for version, path in items:
            try:
                st = path.stat()
            except OSError:
                continue
            total_files += 1
            total_bytes += st.st_size
            if version in keep:
                kept += 1
                continue
            if str(path.resolve()).lower() in tracked or protected(path):
                guarded += 1
                continue
            if now - st.st_mtime <= VERSION_DAYS * 86400:
                continue
            candidates.append({
                "id": cid("version", str(path), int(st.st_mtime), st.st_size), "kind": "version",
                "path": str(path), "title": path.name, "actionable": True, "bytes": st.st_size,
                "reason": f"새 버전 {newest.name}이 있고 마지막 수정 {int((now - st.st_mtime) // 86400)}일 전",
            })
    candidates.sort(key=lambda c: -c["bytes"])
    return {"roots": [str(r) for r in roots], "versioned_files": total_files, "versioned_bytes": total_bytes,
            "kept": kept, "guarded": guarded, "candidates": candidates}
