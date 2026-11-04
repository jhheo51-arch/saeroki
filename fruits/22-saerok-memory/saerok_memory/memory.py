"""기억 파일 검사(PRD v2.3 5.1절). 같은 파일이면 같은 후보를 냅니다."""

import hashlib
import json
import re
import time
from datetime import date, datetime
from pathlib import Path

from .paths import projects_dir
from .store import CHARS_PER_TOKEN, INDEX_LIMIT, LINE_LIMIT, MEMORY_DAYS

INDEX = "MEMORY.md"
ARCHIVE = "_archive"
INDEX_LINE = re.compile(r"^\s*-\s*\[(?P<title>[^\]]+)\]\((?P<file>[^)\s]+)\)\s*(?:[—–-]+\s*(?P<hook>.*))?$")
FULL_DATE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})[^,—]{0,12}?(마감|중단)")
SHORT_DATE = re.compile(r"(?<![\d/])(\d{1,2})/(\d{1,2})(?![\d/])[^,—]{0,12}?(마감|중단)")
TICK_PATH = re.compile(r"`((?:[A-Za-z]:[\\/]|~[\\/])[^`<>*?\"|]+)`")
REPO = re.compile(r"github\.com/[\w.-]+/[\w.-]+")
MOVED_HEADING = "## 목차에서 옮긴 기록"


def cid(*parts) -> str:
    return hashlib.sha1("\x1f".join(str(p) for p in parts).encode("utf-8")).hexdigest()[:12]


def project_cwd(project: Path) -> str:
    """세션 기록에 남은 작업 폴더. 폴더 이름(C--STA-Track-Claude)은 원래 경로로 되돌릴 수 없어서 기록에서 읽습니다."""
    logs = sorted(project.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for log in logs[:5]:
        try:
            with open(log, encoding="utf-8", errors="replace") as f:
                for _, line in zip(range(200), f):
                    if '"cwd"' in line:
                        cwd = (json.loads(line) or {}).get("cwd")
                        if cwd:
                            return str(cwd)
        except (OSError, json.JSONDecodeError):
            continue
    return ""


def memory_dirs() -> list[dict]:
    rows = []
    root = projects_dir()
    if not root.is_dir():
        return rows
    for project in sorted(p for p in root.iterdir() if p.is_dir()):
        folder = project / "memory"
        if folder.is_dir():
            rows.append({"project": project.name, "cwd": project_cwd(project), "dir": folder})
    return rows


def parse_index(text: str) -> list[dict]:
    rows = []
    for n, line in enumerate(text.splitlines()):
        m = INDEX_LINE.match(line)
        if m:
            rows.append({"n": n, "line": line, "title": m["title"], "file": m["file"], "hook": (m["hook"] or "").strip()})
    return rows


def frontmatter(text: str) -> dict:
    """맨 위 --- 사이에서 name, description만 읽습니다."""
    out = {}
    if not text.startswith("---"):
        return out
    end = text.find("\n---", 3)
    for line in text[3:end if end > 0 else 0].splitlines():
        key, _, value = line.partition(":")
        if key.strip() in ("name", "description"):
            out[key.strip()] = value.strip().strip('"')
    return out


def end_date(text: str, mtime: float) -> date | None:
    """요약 글에 적힌 마감·중단 날짜 중 가장 늦은 날. 연도가 없으면 파일 수정 연도로 봅니다."""
    found = []
    for m in FULL_DATE.finditer(text):
        try:
            found.append(date(int(m[1]), int(m[2]), int(m[3])))
        except ValueError:
            pass
    modified = datetime.fromtimestamp(mtime).date()
    for m in SHORT_DATE.finditer(text):
        month, day = int(m[1]), int(m[2])
        year = modified.year - 1 if month - modified.month > 6 else modified.year
        try:
            found.append(date(year, month, day))
        except ValueError:
            pass
    return max(found) if found else None


def propose_line(row: dict) -> str:
    """목차 줄 줄이기 제안. 앞에서부터 쉼표 마디를 150자 안에서 남깁니다. 원래 줄 전체는 본문으로 옮기므로 잃는 것이 없습니다."""
    head = f"- [{row['title']}]({row['file']})"
    if not row["hook"]:
        return head[:LINE_LIMIT]
    keep = ""
    for part in re.split(r",\s*", row["hook"]):
        trial = f"{keep}, {part}" if keep else part
        if len(f"{head} — {trial}") > LINE_LIMIT:
            break
        keep = trial
    if not keep:
        room = LINE_LIMIT - len(head) - 4
        keep = row["hook"][:max(room, 0)].rstrip() + "…"
    return f"{head} — {keep}"


def moved_block(row: dict, today: str) -> str:
    return f"\n\n{MOVED_HEADING} ({today})\n\n{row['hook']}\n"


def _tokens(text: str) -> set[str]:
    tokens = {m.group(0).rstrip(".,)") for m in REPO.finditer(text)}
    tokens |= {m.group(1).rstrip("\\/").replace("/", "\\") for m in TICK_PATH.finditer(text)}
    return tokens


def scan(now: float | None = None) -> dict:
    """모든 프로젝트 기억의 현황과 후보."""
    now = now or time.time()
    today = datetime.fromtimestamp(now).date()
    projects, candidates = [], []
    for info in memory_dirs():
        folder, name = info["dir"], info["project"]
        index_path = folder / INDEX
        index_text = index_path.read_text(encoding="utf-8") if index_path.is_file() else ""
        index = parse_index(index_text)
        files = sorted(p for p in folder.glob("*.md") if p.name != INDEX)
        total = sum(p.stat().st_size for p in files)
        index_bytes = len(index_text.encode("utf-8"))
        if not index_text and not files:
            continue
        longest = max((len(r["line"]) for r in index), default=0)
        projects.append({
            "project": name, "cwd": info["cwd"], "dir": str(folder),
            "index_bytes": index_bytes, "index_lines": len(index), "longest_line": longest,
            "long_lines": sum(len(r["line"]) > LINE_LIMIT for r in index),
            "files": len(files), "file_bytes": total,
            "index_tokens": len(index_text) // CHARS_PER_TOKEN,
            "over_limit": index_bytes > INDEX_LIMIT,
        })

        listed = {r["file"] for r in index}
        texts = {}
        for row in index:
            target = folder / row["file"]
            if len(row["line"]) > LINE_LIMIT:
                candidates.append({
                    "id": cid("index_line", name, row["line"]), "kind": "index_line", "project": name,
                    "path": str(target), "title": row["title"], "actionable": target.is_file(),
                    "reason": f"목차 줄 {len(row['line']):,}자(기준 {LINE_LIMIT}자)",
                    "before": row["line"], "proposal": propose_line(row),
                    "saves": len(row["line"].encode("utf-8")) - len(propose_line(row).encode("utf-8")),
                })
            if not target.is_file():
                candidates.append({
                    "id": cid("broken", name, row["file"]), "kind": "broken", "project": name,
                    "path": str(target), "title": row["title"], "actionable": False,
                    "reason": "목차가 가리키는 파일이 없습니다(확인 필요)",
                })
                continue
            text = target.read_text(encoding="utf-8", errors="replace")
            texts[row["file"]] = text
            mtime = target.stat().st_mtime
            meta = frontmatter(text)
            ended = end_date(f"{row['hook']}\n{meta.get('description', '')}", mtime)
            if ended and (today - ended).days > MEMORY_DAYS and now - mtime > MEMORY_DAYS * 86400:
                candidates.append({
                    "id": cid("archive", name, row["file"], int(mtime)), "kind": "archive", "project": name,
                    "path": str(target), "title": row["title"], "actionable": True,
                    "reason": f"{ended.isoformat()} 마감·중단 뒤 {(today - ended).days}일, 마지막 수정 {int((now - mtime) // 86400)}일 전",
                    "saves": len(row["line"].encode("utf-8")) + 1,
                })
            for token in sorted(_tokens(text)):
                if token.startswith("~") or Path(token).exists():
                    continue
                if not re.match(r"^[A-Za-z]:\\", token):
                    continue
                candidates.append({
                    "id": cid("stale", name, row["file"], token), "kind": "stale", "project": name,
                    "path": str(target), "title": row["title"], "actionable": False,
                    "reason": f"본문의 경로가 지금 없습니다: {token}",
                })

        for p in files:
            if p.name not in listed:
                candidates.append({
                    "id": cid("unlisted", name, p.name), "kind": "broken", "project": name,
                    "path": str(p), "title": p.stem, "actionable": False,
                    "reason": "목차에 없는 기억 파일입니다(확인 필요)",
                })

        roots = {info["cwd"].rstrip("\\/").replace("/", "\\").lower()} if info["cwd"] else set()
        owners: dict[str, list[str]] = {}
        for file, text in texts.items():
            for token in _tokens(text):
                if token.lower() in roots:
                    continue
                owners.setdefault(token, []).append(file)
        pairs: dict[tuple, list[str]] = {}
        for token, who in owners.items():
            who = sorted(set(who))
            for i in range(len(who)):
                for j in range(i + 1, len(who)):
                    pairs.setdefault((who[i], who[j]), []).append(token)
        for (a, b), shared in sorted(pairs.items()):
            candidates.append({
                "id": cid("duplicate", name, a, b), "kind": "duplicate", "project": name,
                "path": str(folder / a), "other": str(folder / b), "title": f"{a} · {b}", "actionable": False,
                "reason": "두 파일이 같은 위치를 적습니다: " + ", ".join(sorted(shared)[:3]),
            })
    return {"projects": projects, "candidates": candidates}
