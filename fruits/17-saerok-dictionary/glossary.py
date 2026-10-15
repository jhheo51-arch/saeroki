"""새록 사전 용어집 검사와 화면용 데이터 파일 생성.

python glossary.py check   # 형식·출처·칸별 개수 검사
python glossary.py build   # web/data.js 다시 만들기
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CATALOG_PATH = ROOT / "data" / "catalog.json"
TERMS_PATH = ROOT / "data" / "terms.json"
DATA_JS_PATH = ROOT / "web" / "data.js"

LEVELS = ("입문", "실무", "심화")
STATUSES = ("verified", "needs_check")
SOURCE_KINDS = ("official", "company_guide", "tech_blog")
CELL_MINIMUM = 30
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_RE = re.compile(r"^[a-z0-9_]+$")


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_catalog(path: Path = CATALOG_PATH) -> dict:
    return load_json(path)


def load_terms(path: Path = TERMS_PATH) -> list[dict]:
    return load_json(path)


def validate_source(source: dict, where: str) -> list[str]:
    errors = []
    for key in ("title", "url", "kind", "checked_at"):
        if not source.get(key):
            errors.append(f"{where}: 출처에 {key}가 없습니다")
    url = source.get("url") or ""
    if url and not url.startswith("https://"):
        errors.append(f"{where}: 출처 주소는 https://로 시작해야 합니다 ({url})")
    if source.get("kind") and source["kind"] not in SOURCE_KINDS:
        errors.append(f"{where}: 알 수 없는 출처 종류 {source['kind']}")
    if source.get("checked_at") and not DATE_RE.match(source["checked_at"]):
        errors.append(f"{where}: 확인 날짜 형식은 YYYY-MM-DD입니다")
    return errors


def validate_sense(sense: dict, where: str, industries: set, roles: set) -> list[str]:
    errors = []
    for key in ("industries", "roles", "level", "importance", "definition", "examples", "sources", "status"):
        if key not in sense:
            errors.append(f"{where}: {key}가 없습니다")
    if errors:
        return errors
    if not sense["industries"] or set(sense["industries"]) - industries:
        errors.append(f"{where}: 산업 목록이 비었거나 catalog에 없는 값이 있습니다")
    if not sense["roles"] or set(sense["roles"]) - roles:
        errors.append(f"{where}: 직무 목록이 비었거나 catalog에 없는 값이 있습니다")
    if sense["level"] not in LEVELS:
        errors.append(f"{where}: 난이도는 입문·실무·심화 중 하나입니다")
    if not isinstance(sense["importance"], int) or not 1 <= sense["importance"] <= 5:
        errors.append(f"{where}: 중요도는 1~5 정수입니다")
    if not str(sense["definition"]).strip():
        errors.append(f"{where}: 쉬운 뜻이 비었습니다")
    if not isinstance(sense["examples"], list) or not sense["examples"]:
        errors.append(f"{where}: 실무 예문이 1개 이상 필요합니다")
    if sense["status"] not in STATUSES:
        errors.append(f"{where}: status는 verified 또는 needs_check입니다")
    if sense["status"] == "verified" and not sense["sources"]:
        errors.append(f"{where}: 출처 없는 뜻을 verified로 둘 수 없습니다")
    for i, source in enumerate(sense["sources"]):
        errors.extend(validate_source(source, f"{where} 출처 {i + 1}"))
    return errors


def validate(catalog: dict, terms: list[dict]) -> list[str]:
    """용어집 형식 오류를 모두 모아 돌려줍니다. 빈 목록이면 통과입니다."""
    industries = {item["id"] for item in catalog["industries"]}
    roles = {item["id"] for item in catalog["roles"]}
    errors = []
    seen_ids = set()
    seen_terms = set()
    for index, term in enumerate(terms):
        where = term.get("id") or f"#{index}"
        for key in ("id", "term", "original", "korean", "aliases", "senses", "related", "confusable"):
            if key not in term:
                errors.append(f"{where}: {key}가 없습니다")
        if not ID_RE.match(term.get("id", "")):
            errors.append(f"{where}: id는 영문 소문자·숫자·밑줄만 씁니다")
        if term.get("id") in seen_ids:
            errors.append(f"{where}: id가 겹칩니다")
        seen_ids.add(term.get("id"))
        key = (term.get("term") or "").strip().lower()
        if key in seen_terms:
            errors.append(f"{where}: 같은 표제어가 이미 있습니다. 뜻을 합쳐 주세요")
        seen_terms.add(key)
        if not term.get("senses"):
            errors.append(f"{where}: 뜻이 하나 이상 필요합니다")
        for n, sense in enumerate(term.get("senses") or [], start=1):
            errors.extend(validate_sense(sense, f"{where} 뜻 {n}", industries, roles))
        for item in term.get("related") or []:
            if not item.get("term") or not item.get("note"):
                errors.append(f"{where}: 관련어에는 term과 note가 필요합니다")
        for item in term.get("confusable") or []:
            if not item.get("term") or not item.get("difference"):
                errors.append(f"{where}: 헷갈리는 말에는 term과 difference가 필요합니다")
    for (industry, role), count in cell_counts(catalog, terms).items():
        if count < CELL_MINIMUM:
            errors.append(f"{industry}×{role}: 용어가 {count}개입니다. {CELL_MINIMUM}개 이상 필요합니다")
    return errors


def cell_counts(catalog: dict, terms: list[dict]) -> dict:
    counts = {}
    for industry in catalog["industries"]:
        for role in catalog["roles"]:
            counts[(industry["id"], role["id"])] = sum(
                1
                for term in terms
                if any(industry["id"] in s.get("industries", []) and role["id"] in s.get("roles", []) for s in term.get("senses", []))
            )
    return counts


def summary(catalog: dict, terms: list[dict]) -> dict:
    statuses = Counter(sense.get("status") for term in terms for sense in term.get("senses", []))
    return {
        "terms": len(terms),
        "senses": sum(statuses.values()),
        "verified": statuses.get("verified", 0),
        "needs_check": statuses.get("needs_check", 0),
        "without_official_source": sum(
            1
            for term in terms
            for sense in term.get("senses", [])
            if sense.get("sources") and not any(src.get("kind") == "official" for src in sense["sources"])
        ),
        "cells": {f"{i}×{r}": n for (i, r), n in cell_counts(catalog, terms).items()},
    }


def render_data_js(catalog: dict, terms: list[dict]) -> str:
    payload = json.dumps({"catalog": catalog, "terms": terms}, ensure_ascii=False, indent=1)
    return (
        "/* 자동 생성 파일입니다. data/*.json을 고친 뒤 `python glossary.py build`로 다시 만듭니다. */\n"
        f"window.SAEROK_DATA = {payload};\n"
    )


def main(argv: list[str]) -> int:
    command = argv[1] if len(argv) > 1 else "check"
    catalog, terms = load_catalog(), load_terms()
    errors = validate(catalog, terms)
    print(json.dumps(summary(catalog, terms), ensure_ascii=False, indent=2))
    if errors:
        print("\n".join(f"- {e}" for e in errors))
        return 1
    if command == "build":
        DATA_JS_PATH.write_text(render_data_js(catalog, terms), encoding="utf-8", newline="\n")
        print(f"{DATA_JS_PATH.relative_to(ROOT)}을 다시 만들었습니다")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv))
