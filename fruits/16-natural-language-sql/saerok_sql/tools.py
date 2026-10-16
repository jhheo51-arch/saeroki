"""AI 없이 쓰는 명령: Claude Code 스킬이 데이터 사전을 읽고 SQL을 안전하게 실행할 때 씁니다.

saerok-sql --schema                     데이터 사전 글 출력
saerok-sql --run - --label "질문" < sql  SQL을 안전 검사 후 실행하고 JSON으로 출력
saerok-sql --install-skill              Claude Code 스킬을 ~/.claude/skills/saerok-sql에 설치
"""

from __future__ import annotations

import json
import shutil
from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path

from . import dictionary as dict_mod
from .agent import Agent, Answer
from .db import Database, QueryError
from .history import History

SKILL_SOURCE = Path(__file__).resolve().parents[1] / "claude-skill" / "SKILL.md"
JSON_ROWS = 50


def _plain(value):
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    return value


def schema_text(db: Database) -> str:
    return dict_mod.render(dict_mod.load(), db.tables())


def run_json(db: Database, sql: str, label: str = "", history: History | None = None) -> dict:
    """SQL을 실행해 Claude Code가 읽기 쉬운 JSON으로 돌려줍니다. 결과 값은 앞 50행까지만 담습니다."""
    helper = Agent(None, db)
    answer = Answer("question" if label else "sql", label or sql, "error", sql=sql.strip(), attempts=1)
    answer.data_notes = helper._data_notes(answer.sql)
    try:
        answer.result = db.run(answer.sql)
        answer.review = helper._review(answer.result)
        answer.status = "review" if answer.review else "ok"
    except QueryError as e:
        answer.status = "blocked" if e.blocked else "error"
        answer.message = str(e)
    if history:
        history.add(answer, "claude-code")
    out = {
        "status": answer.status,
        "message": answer.message,
        "review": answer.review,
        "data_notes": answer.data_notes,
    }
    if answer.result is not None:
        r = answer.result
        out.update({
            "columns": r.columns,
            "types": r.types,
            "row_count": len(r.rows),
            "truncated_at_1000": r.truncated,
            "rows_shown": min(len(r.rows), JSON_ROWS),
            "rows": [[_plain(v) for v in row] for row in r.rows[:JSON_ROWS]],
            "seconds": round(r.seconds, 3),
        })
    return out


def install_skill(target_root: Path | None = None) -> Path:
    target = (target_root or Path.home() / ".claude" / "skills") / "saerok-sql"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SKILL_SOURCE, target / "SKILL.md")
    return target / "SKILL.md"


def dumps(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False)
