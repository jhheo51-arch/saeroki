"""17번 새록 사전 용어집에서 바로 찾아 슬랙 글로 만듭니다. AI를 부르지 않고, 사전에 없는 말은 짓지 않습니다."""

from __future__ import annotations

import difflib
import json
from datetime import date
from pathlib import Path

from .config import REPO

TERMS_PATH = REPO / "fruits" / "17-saerok-dictionary" / "data" / "terms.json"


def norm(text: str) -> str:
    return "".join(text.lower().split())


def names(entry: dict) -> list[str]:
    return [n for n in (entry.get("term"), entry.get("korean"), entry.get("original"), *entry.get("aliases", [])) if n]


def load(path: Path = TERMS_PATH) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))


def find(query: str, terms: list[dict]) -> tuple[list[dict], list[str]]:
    """같은 이름이 있으면 그 용어들을, 없으면 비슷한 이름 후보를 돌려줍니다."""
    q = norm(query)
    exact = [t for t in terms if any(norm(n) == q for n in names(t))]
    if exact:
        return exact, []
    partial = [t for t in terms if q and any(q in norm(n) for n in names(t))]
    if 0 < len(partial) <= 3:
        return partial, []
    pool = {norm(n): t["term"] for t in terms for n in names(t)}
    near = difflib.get_close_matches(q, pool, n=8, cutoff=0.5)
    hints = list(dict.fromkeys([t["term"] for t in partial] + [pool[n] for n in near]))[:5]
    return [], hints


def render(entry: dict) -> str:
    head = f"*{entry['term']}*"
    if entry.get("original") and entry["original"] != entry["term"]:
        head += f" ({entry['original']})"
    lines = [head]
    for sense in entry["senses"]:
        mark = "" if sense["status"] == "verified" else " _(확인 필요: 공식 출처 대조 전)_"
        lines.append(f"• {sense['definition']}{mark}")
        if sense.get("formula"):
            lines.append(f"   공식: `{sense['formula']}`")
        if sense.get("examples"):
            lines.append(f"   예문: “{sense['examples'][0]}”")
        for src in sense.get("sources", []):
            lines.append(f"   출처: <{src['url']}|{src['title']}> · 확인 {src['checked_at']}")
    if entry.get("confusable"):
        lines.append("헷갈리는 말: " + " / ".join(f"{c['term']}: {c['difference']}" for c in entry["confusable"]))
    if entry.get("related"):
        lines.append("함께 보기: " + ", ".join(r["term"] for r in entry["related"]))
    return "\n".join(lines)


def today(terms: list[dict] | None = None, day: date | None = None) -> str:
    """오늘의 용어. 날짜로만 고르니 AI 없이 매일 같은 답이 나오고, 출처를 확인한 말을 먼저 고릅니다."""
    terms = load() if terms is None else terms
    pool = [t for t in terms if all(s["status"] == "verified" for s in t["senses"])] or terms
    entry = pool[(day or date.today()).toordinal() % len(pool)]
    return "📅 *오늘의 용어*\n" + render(entry) + "\n_다른 말은 `/saerok-dict 리텐션`처럼 찾습니다._"


def answer(query: str, terms: list[dict] | None = None) -> str:
    query = query.strip()
    if not query:
        return "찾을 용어를 함께 적어 주세요. 예: `/saerok-dict 리텐션`"
    terms = load() if terms is None else terms
    found, hints = find(query, terms)
    if found:
        return "\n\n".join(render(t) for t in found)
    text = f"새록 사전에 ‘{query}’는 아직 없습니다. 확인되지 않은 뜻은 지어 쓰지 않습니다."
    if hints:
        text += "\n비슷한 말: " + ", ".join(hints)
    return text
