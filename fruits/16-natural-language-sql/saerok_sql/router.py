"""입력 구분: /명령, SQL(풀이), 질문(SQL 만들기)."""

from __future__ import annotations

import re
from dataclasses import dataclass

# SQL 문장을 시작하는 단어. 조회가 아닌 문장도 풀이로 보내고, 실행은 안전 검사가 막습니다.
SQL_KEYWORDS = {
    "select", "with", "insert", "update", "delete", "drop", "create", "alter", "truncate", "merge",
    "copy", "attach", "detach", "pragma", "set", "install", "load", "grant", "revoke", "export", "import",
}


@dataclass(frozen=True)
class Route:
    kind: str  # "empty" | "command" | "sql" | "question"
    text: str = ""
    command: str = ""
    arg: str = ""


def _strip_leading_comments(text: str) -> str:
    previous = None
    while previous != text:
        previous = text
        text = text.lstrip()
        text = re.sub(r"^--[^\n]*\n?", "", text)
        text = re.sub(r"^/\*.*?\*/", "", text, flags=re.S)
    return text.lstrip("( \t\r\n")


def looks_like_sql(text: str) -> bool:
    """SQL 키워드로 시작하고 바로 뒤가 한글이 아니면 SQL로 봅니다. 'with 문법이 뭐야?'는 질문입니다."""
    words = _strip_leading_comments(text).split(None, 1)
    if not words or words[0].lower() not in SQL_KEYWORDS:
        return False
    rest = words[1] if len(words) > 1 else ""
    return not re.match(r"[가-힣]", rest)


def route(raw: str) -> Route:
    text = (raw or "").strip()
    if not text:
        return Route("empty")
    if text.startswith("/"):
        name, _, arg = text[1:].partition(" ")
        return Route("command", text, name.lower(), arg.strip())
    if looks_like_sql(text):
        return Route("sql", text)
    return Route("question", text)
