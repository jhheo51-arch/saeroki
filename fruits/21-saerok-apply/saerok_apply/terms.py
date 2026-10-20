"""17번 새록 사전 용어집을 줄인 사본(data/terms-lite.json)을 만들고 읽습니다.
공고 용어 찾기, 자기소개서 용어 오용 검사, 다른 회사 이름 검사(사전 출처의 기업명)에 씁니다.
플러그인은 저장소 밖에 설치되므로 사본을 함께 싣고, 자동 검사로 원본과 맞춰 둡니다."""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

LITE = Path(__file__).resolve().parent.parent / "data" / "terms-lite.json"
SPLIT = re.compile(r"\s+[|\-–—]\s+")
TAIL = re.compile(r"\s*(?:Optimization\s+)?(?:mobile\s+|marketing\s+)?"
                  r"(?:Glossary|glossary|용어집|블로그|Blog|Team Playbook|Enterprising Investor)$")
PAREN = re.compile(r"\(([^()]+)\)\s*$")
SKIP_HOSTS = {"dictionary", "cambridge", "martinfowler", "nice"}


def _first_sentence(text: str) -> str:
    end = text.find("다. ")
    return text[: end + 2] if end != -1 else text.strip()


def _name_ok(name: str) -> bool:
    return bool(name) and len(name.split()) <= 3 and "Dictionary" not in name and "." not in name


def companies(terms: list) -> list[str]:
    """사전 출처(company_guide) 제목과 주소에서 기업·브랜드 이름을 뽑습니다. 같은 입력이면 같은 순서."""
    names, hosts = [], []
    for t in terms:
        for s in t["senses"]:
            for src in s.get("sources", []):
                if src.get("kind") != "company_guide":
                    continue
                title = src.get("title", "")
                pieces = SPLIT.split(title)
                if len(pieces) > 1:
                    name = TAIL.sub("", pieces[-1].strip())
                    if _name_ok(name):
                        names.append(name)
                m = PAREN.search(title)
                if m:
                    name = TAIL.sub("", m.group(1).strip())
                    if name != m.group(1).strip() and _name_ok(name):
                        names.append(name)
                host = urlparse(src.get("url", "")).hostname or ""
                labels = host.removeprefix("www.").split(".")
                if len(labels) >= 2 and labels[-2] not in SKIP_HOSTS:
                    hosts.append(labels[-2])
    out, seen = [], set()
    for name in names + hosts:
        if name.lower() not in seen:
            seen.add(name.lower())
            out.append(name)
    return out


def build(terms_file: Path, catalog_file: Path) -> dict:
    catalog = json.loads(Path(catalog_file).read_text(encoding="utf-8-sig"))
    terms = json.loads(Path(terms_file).read_text(encoding="utf-8-sig"))
    rows = []
    for t in terms:
        rows.append({
            "term": t["term"],
            "original": t.get("original", ""),
            "korean": t.get("korean", ""),
            "aliases": t.get("aliases", []),
            "confusable": [{"term": c["term"], "difference": c["difference"]} for c in t.get("confusable", [])],
            "senses": [{"industries": s["industries"], "roles": s["roles"], "level": s["level"],
                        "definition": _first_sentence(s["definition"])} for s in t["senses"]],
        })
    return {
        "source": "fruits/17-saerok-dictionary/data (terms.json, catalog.json)",
        "industries": [{"id": i["id"], "name": i["name"]} for i in catalog["industries"]],
        "roles": [{"id": r["id"], "name": r["name"]} for r in catalog["roles"]],
        "companies": companies(terms),
        "terms": rows,
    }


def dump(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, indent=1) + "\n"


def load(path: Path = LITE) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))
