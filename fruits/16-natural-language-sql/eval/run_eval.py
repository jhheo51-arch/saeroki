"""예시 질문 20개 채점. Claude API를 실제로 불러 비용이 듭니다(질문당 요청 1~3번).

python eval/run_eval.py            # 전체
python eval/run_eval.py q01 q07    # 일부만

채점 방법: 정답 SQL 결과의 각 컬럼이 새록 SQL 결과의 어떤 컬럼과 값이 같은지 봅니다(숫자는 0.5% 오차 허용).
행 수가 같고 정답 컬럼이 모두 짝을 찾으면 통과입니다. 순위 질문(ordered)은 행 순서까지 같아야 합니다.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from saerok_sql import keystore  # noqa: E402
from saerok_sql.agent import Agent  # noqa: E402
from saerok_sql.db import Database  # noqa: E402
from saerok_sql.llm import DEFAULT_MODEL, ClaudeBrain  # noqa: E402

HERE = Path(__file__).resolve().parent


def _norm(value):
    if isinstance(value, (datetime, date)):
        return value.isoformat()[:10]
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return float(value)
    return str(value).strip()


def _same(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float):
        return abs(a - b) <= max(abs(a), abs(b)) * 0.005 + 1e-9
    return a == b


def column_values(rows, index, ordered):
    values = [_norm(row[index]) for row in rows]
    return values if ordered else sorted(values, key=lambda v: (str(type(v)), str(v)))


def matches(gold_rows, got_rows, ordered: bool) -> bool:
    if len(gold_rows) != len(got_rows) or not gold_rows:
        return False
    got_columns = [column_values(got_rows, i, ordered) for i in range(len(got_rows[0]))]
    for i in range(len(gold_rows[0])):
        gold = column_values(gold_rows, i, ordered)
        if not any(len(gold) == len(got) and all(_same(a, b) for a, b in zip(gold, got)) for got in got_columns):
            return False
    return True


def main(selected: list[str]) -> int:
    key = keystore.get_key()
    if not key:
        print("API 키가 없습니다. saerok-sql을 실행해 /key로 먼저 등록해 주세요.")
        return 2
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    if selected:
        questions = [q for q in questions if q["id"] in selected]
    db = Database()
    agent = Agent(ClaudeBrain(key, DEFAULT_MODEL), db)
    passed, report = 0, []
    for q in questions:
        gold = db.run(q["gold_sql"]).rows
        answer = agent.ask(q["question"])
        ok = answer.result is not None and matches(gold, answer.result.rows, q["ordered"])
        passed += ok
        report.append({"id": q["id"], "pass": ok, "status": answer.status, "attempts": answer.attempts, "sql": answer.sql, "message": answer.message})
        print(f"{q['id']} {'통과' if ok else '실패'} ({answer.status}, 시도 {answer.attempts})")
    out = HERE / f"result-{datetime.now():%Y%m%d-%H%M}.local.json"
    out.write_text(json.dumps({"model": DEFAULT_MODEL, "passed": passed, "total": len(questions), "items": report}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{passed}/{len(questions)} 통과 · 자세한 결과: {out}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
