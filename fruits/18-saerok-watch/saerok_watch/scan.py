"""Claude Code 세션 기록(~/.claude/projects/*/*.jsonl)에서 토큰 사용량을 셉니다.

대화 원문은 저장하지 않고 숫자만 모읍니다. 로컬 대시보드에서 세션을 알아보도록
첫 요청 앞부분(제목)과 프로젝트 폴더 이름만 내 PC 캐시에 둡니다.
"""

import json
from datetime import datetime
from pathlib import Path

from .paths import claude_home, data_home
from .store import read_json, write_json

# 컨텍스트 크기 구간: 10만 미만, 10~30만, 30~60만, 60만 이상
BUCKET_EDGES = (100_000, 300_000, 600_000)
CACHE_VERSION = 3


def bucket_of(ctx: int) -> int:
    for i, edge in enumerate(BUCKET_EDGES):
        if ctx < edge:
            return i
    return len(BUCKET_EDGES)


def context_of(usage: dict) -> int:
    """한 응답이 읽은 컨텍스트 크기 = 새 입력 + 캐시 읽기 + 캐시 쓰기."""
    return (
        int(usage.get("input_tokens") or 0)
        + int(usage.get("cache_read_input_tokens") or 0)
        + int(usage.get("cache_creation_input_tokens") or 0)
    )


def local_day(ts: str | None) -> str | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().date().isoformat()
    except ValueError:
        return None


def _new_day():
    return {"processed": 0, "responses": 0, "images": 0, "over300": 0, "max_ctx": 0}


def _result_size(content) -> tuple[int, int]:
    """도구 결과의 (글자 수, 이미지 수)."""
    if isinstance(content, list):
        chars = images = 0
        for item in content:
            if isinstance(item, dict) and item.get("type") == "image":
                images += 1
            elif isinstance(item, dict):
                chars += len(item.get("text") or "")
        return chars, images
    return len(str(content or "")), 0


def _title_from(content) -> str | None:
    texts = [content] if isinstance(content, str) else [
        b.get("text") or "" for b in content or [] if isinstance(b, dict) and b.get("type") == "text"]
    for text in texts:
        text = text.strip()
        # 시스템이 붙인 <...> 블록은 건너뛰고 사람이 쓴 첫 문장을 제목으로 씁니다.
        if text and not text.startswith("<"):
            return " ".join(text.split())[:60]
    return None


def scan_file(path: Path) -> dict:
    s = {
        "session_id": path.stem,
        "project": None,
        "cwd": None,
        "title": None,
        "first_ts": None,
        "last_ts": None,
        "responses": 0,
        "processed": 0,
        "output": 0,
        "first_ctx": 0,
        "max_ctx": 0,
        "last_ctx": 0,
        "buckets": [0, 0, 0, 0],
        "images": 0,
        "compactions": 0,
        "tool_chars": {},
        "tool_counts": {},
        "mcp_used": {},
        "skills_used": {},
        "days": {},
    }
    seen = set()
    tool_names = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(d, dict):
                continue
            ts = d.get("timestamp")
            if ts:
                s["first_ts"] = s["first_ts"] or ts
                s["last_ts"] = ts
            if d.get("cwd") and not s["cwd"]:
                s["cwd"] = d["cwd"]
                s["project"] = Path(d["cwd"]).name
            if d.get("subtype") == "compact_boundary":
                s["compactions"] += 1
            msg = d.get("message") if isinstance(d.get("message"), dict) else {}
            day = local_day(ts)
            kind = d.get("type")

            if kind == "assistant":
                for block in msg.get("content") or []:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = block.get("name") or "?"
                    tool_names[block.get("id")] = name
                    if name.startswith("mcp__"):
                        server = name.split("__")[1]
                        s["mcp_used"][server] = s["mcp_used"].get(server, 0) + 1
                    if name == "Skill":
                        skill = str((block.get("input") or {}).get("skill") or "?")
                        s["skills_used"][skill] = s["skills_used"].get(skill, 0) + 1
                usage = msg.get("usage") or {}
                ctx = context_of(usage)
                key = msg.get("id") or d.get("uuid")
                # 한 응답이 블록마다 여러 줄로 저장되므로 메시지 ID로 한 번만 셉니다.
                if not ctx or key in seen:
                    continue
                seen.add(key)
                s["responses"] += 1
                s["processed"] += ctx
                s["output"] += int(usage.get("output_tokens") or 0)
                s["first_ctx"] = s["first_ctx"] or ctx
                s["max_ctx"] = max(s["max_ctx"], ctx)
                s["last_ctx"] = ctx
                s["buckets"][bucket_of(ctx)] += ctx
                if day:
                    dd = s["days"].setdefault(day, _new_day())
                    dd["processed"] += ctx
                    dd["responses"] += 1
                    dd["max_ctx"] = max(dd["max_ctx"], ctx)
                    if ctx >= 300_000:
                        dd["over300"] += ctx

            elif kind == "user":
                content = msg.get("content")
                if s["title"] is None and not d.get("isMeta") and not d.get("isCompactSummary"):
                    s["title"] = _title_from(content)
                if not isinstance(content, list):
                    continue
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    images = 0
                    if block.get("type") == "tool_result":
                        name = tool_names.get(block.get("tool_use_id"), "?")
                        chars, images = _result_size(block.get("content"))
                        s["tool_chars"][name] = s["tool_chars"].get(name, 0) + chars
                        s["tool_counts"][name] = s["tool_counts"].get(name, 0) + 1
                    elif block.get("type") == "image":
                        images = 1
                    if images:
                        s["images"] += images
                        if day:
                            s["days"].setdefault(day, _new_day())["images"] += images
    return s


def transcript_files() -> list[Path]:
    root = claude_home() / "projects"
    if not root.exists():
        return []
    return sorted(root.glob("*/*.jsonl"))


def scan_all(use_cache: bool = True) -> list[dict]:
    """모든 세션을 셉니다. 바뀌지 않은 파일은 캐시를 씁니다."""
    cache_path = data_home() / "scan-cache.json"
    cache = read_json(cache_path, {}) if use_cache else {}
    if cache.get("version") != CACHE_VERSION:
        cache = {"version": CACHE_VERSION, "files": {}}
    fresh = {}
    sessions = []
    for path in transcript_files():
        try:
            stat = path.stat()
        except OSError:
            continue
        sig = [stat.st_size, int(stat.st_mtime)]
        hit = cache["files"].get(str(path))
        if hit and hit.get("sig") == sig:
            stats = hit["stats"]
        else:
            stats = scan_file(path)
        stats["mtime"] = stat.st_mtime
        fresh[str(path)] = {"sig": sig, "stats": stats}
        if stats["responses"]:
            sessions.append(stats)
    write_json(cache_path, {"version": CACHE_VERSION, "files": fresh})
    sessions.sort(key=lambda x: x.get("last_ts") or "", reverse=True)
    return sessions


def totals(sessions: list[dict]) -> dict:
    t = {"sessions": len(sessions), "responses": 0, "processed": 0, "images": 0, "buckets": [0, 0, 0, 0]}
    firsts = []
    for s in sessions:
        t["responses"] += s["responses"]
        t["processed"] += s["processed"]
        t["images"] += s["images"]
        t["buckets"] = [a + b for a, b in zip(t["buckets"], s["buckets"])]
        if s["first_ctx"]:
            firsts.append(s["first_ctx"])
    firsts.sort()
    t["baseline_median"] = firsts[len(firsts) // 2] if firsts else 0
    return t


def daily(sessions: list[dict]) -> list[dict]:
    days = {}
    for s in sessions:
        for day, v in s["days"].items():
            d = days.setdefault(day, {"date": day, "sessions": 0, **_new_day()})
            d["sessions"] += 1 if v["responses"] else 0
            for k in ("processed", "responses", "images", "over300"):
                d[k] += v[k]
            d["max_ctx"] = max(d["max_ctx"], v["max_ctx"])
    return [days[k] for k in sorted(days)]


def simulate_cap(sessions: list[dict], cap: int, restart: int = 100_000) -> float:
    """상한 cap에서 압축해 restart로 돌아간다고 가정했을 때 처리량이 지금의 몇 배가 되는지(단순 모형).

    응답별 크기 대신 구간 대표값을 쓰는 근사입니다. 상한보다 큰 구간은
    restart와 cap 사이를 오가는 톱니 평균으로 바꿉니다. 압축 요약을 만드는 비용은 뺐습니다.
    """
    mids = (50_000, 200_000, 450_000, 800_000)
    total = capped = 0.0
    for s in sessions:
        for amount, mid in zip(s["buckets"], mids):
            total += amount
            capped += amount if mid < cap else amount * ((restart + cap) / 2) / mid
    return capped / total if total else 1.0
