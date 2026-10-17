"""17번 새록 사전 용어집에서 실무·숫자 검증 면접관에게 줄 핵심 용어를 고릅니다.
플러그인은 저장소 밖에 설치되므로 원본을 줄인 사본(data/terms-lite.json)을 함께 싣고, 자동 검사로 원본과 맞춰 둡니다."""

import json
from pathlib import Path

LITE = Path(__file__).resolve().parent.parent / "data" / "terms-lite.json"
INTERVIEW_LEVELS = ["실무", "심화", "입문"]  # 17번 '면접 준비' 목적과 같은 순서(실무·심화 먼저)


def _first_sentence(text: str) -> str:
    end = text.find("다. ")
    return text[: end + 2] if end != -1 else text.strip()


def build(terms_file: Path, catalog_file: Path) -> dict:
    catalog = json.loads(Path(catalog_file).read_text(encoding="utf-8-sig"))
    terms = json.loads(Path(terms_file).read_text(encoding="utf-8-sig"))
    rows = []
    for t in terms:
        for s in t["senses"]:
            rows.append({
                "term": t["term"],
                "original": t.get("original", ""),
                "industries": s["industries"],
                "roles": s["roles"],
                "level": s["level"],
                "importance": s.get("importance", 0),
                "definition": _first_sentence(s["definition"]),
            })
    return {
        "source": "fruits/17-saerok-dictionary/data (terms.json, catalog.json)",
        "industries": [{"id": i["id"], "name": i["name"]} for i in catalog["industries"]],
        "roles": [{"id": r["id"], "name": r["name"]} for r in catalog["roles"]],
        "terms": rows,
    }


def dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def load(path: Path = LITE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def pick(industry: str, role: str, limit: int = 20, data: dict | None = None) -> dict:
    data = data or load()
    ids = {"industry": {i["id"] for i in data["industries"]}, "role": {r["id"] for r in data["roles"]}}
    if industry not in ids["industry"]:
        raise ValueError(f"모르는 산업입니다: {industry}. 가능한 값: {', '.join(sorted(ids['industry']))}")
    if role not in ids["role"]:
        raise ValueError(f"모르는 직무입니다: {role}. 가능한 값: {', '.join(sorted(ids['role']))}")
    found = [t for t in data["terms"] if industry in t["industries"] and role in t["roles"]]
    found.sort(key=lambda t: (-t["importance"], INTERVIEW_LEVELS.index(t["level"]) if t["level"] in INTERVIEW_LEVELS else 9, t["term"]))
    seen, out = set(), []
    for t in found:
        if t["term"] in seen:
            continue
        seen.add(t["term"])
        out.append({k: t[k] for k in ("term", "original", "level", "importance", "definition")})
        if len(out) >= limit:
            break
    return {"industry": industry, "role": role, "terms": out}
