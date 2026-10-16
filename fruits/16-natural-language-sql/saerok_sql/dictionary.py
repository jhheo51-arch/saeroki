"""한글 데이터 사전: AI가 SQL을 쓸 때 보는 유일한 표 설명입니다."""

from __future__ import annotations

import json
import re
from pathlib import Path

from .db import DATA_DIR

DICTIONARY_PATH = DATA_DIR / "dictionary.json"


def load(path: Path = DICTIONARY_PATH) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def coverage_errors(dictionary: dict, schema: dict[str, list[tuple[str, str]]]) -> list[str]:
    """사전과 실제 DB의 표·컬럼이 서로 빠짐없이 맞는지 확인합니다."""
    errors = []
    tables = dictionary["tables"]
    for table, columns in schema.items():
        if table not in tables:
            errors.append(f"사전에 없는 표: {table}")
            continue
        described = tables[table]["columns"]
        for column, _ in columns:
            if column not in described:
                errors.append(f"{table}.{column}: 사전 설명이 없습니다")
        for column in described:
            if column not in {c for c, _ in columns}:
                errors.append(f"{table}.{column}: 사전에는 있지만 DB에 없습니다")
    for table in tables:
        if table not in schema:
            errors.append(f"DB에 없는 표: {table}")
    for table, info in tables.items():
        for key in ("description", "grain", "period", "source", "license", "notes", "columns"):
            if key not in info:
                errors.append(f"{table}: {key}가 없습니다")
    return errors


def render(dictionary: dict, schema: dict[str, list[tuple[str, str]]]) -> str:
    """프롬프트에 넣을 사전 글. 표 순서와 내용이 바뀌지 않으면 글자 하나까지 같아 캐시가 맞습니다."""
    lines = [f"# 데이터: {dictionary['dataset']} ({dictionary['period']})", ""]
    lines += [f"- {note}" for note in dictionary["common_notes"]]
    for table in sorted(dictionary["tables"]):
        info = dictionary["tables"][table]
        types = dict(schema.get(table, []))
        lines += ["", f"## {table}: {info['description']}", f"- 한 행: {info['grain']}", f"- 기간: {info['period']}"]
        lines += [f"- 주의: {note}" for note in info["notes"]]
        lines.append("- 컬럼:")
        for column, meaning in info["columns"].items():
            lines.append(f"  - {column} ({types.get(column, '?')}): {meaning}")
    return "\n".join(lines) + "\n"


def tables_in_sql(sql: str, dictionary: dict) -> list[str]:
    """FROM·JOIN 뒤에 나온 표만 셉니다. 'dong'처럼 컬럼과 이름이 같은 표를 잘못 세지 않게 합니다."""
    lowered = sql.lower()
    return [
        t for t in sorted(dictionary["tables"])
        if re.search(rf"\b(from|join)\s+(main\.)?\"?{re.escape(t)}\"?(\s|$|,|\))", lowered)
    ]
