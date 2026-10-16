"""예시 질문 20개 채점. Claude API를 실제로 불러 비용이 듭니다(질문당 요청 1~3번).

python eval/run_eval.py            # 전체
python eval/run_eval.py q01 q07    # 일부만
python eval/run_eval.py --answers 답안.json   # Claude Code 스킬 등으로 받은 답안 채점(API 없이)

채점 방법: 정답 SQL 결과의 각 컬럼이 새록 SQL 결과의 어떤 컬럼과 값이 같은지 봅니다(숫자는 0.5% 오차 허용).
행 수가 같고 정답 컬럼이 모두 짝을 찾으면 통과입니다. 순위 질문(ordered)은 행 순서까지 같아야 합니다.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from saerok_sql import keystore  # noqa: E402
from saerok_sql.agent import Agent  # noqa: E402
from saerok_sql.db import Database, QueryError  # noqa: E402
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


def matches(gold_rows, got_rows, ordered: bool, check_columns: list[int] | None = None) -> bool:
    """check_columns를 주면 정답의 그 컬럼만 비교합니다. 예: 참/거짓 구분을 '비 온 날' 같은 글자로 바꿔 쓴 답안."""
    if len(gold_rows) != len(got_rows) or not gold_rows:
        return False
    got_columns = [column_values(got_rows, i, ordered) for i in range(len(got_rows[0]))]
    for i in (check_columns if check_columns is not None else range(len(gold_rows[0]))):
        gold = column_values(gold_rows, i, ordered)
        if not any(len(gold) == len(got) and all(_same(a, b) for a, b in zip(gold, got)) for got in got_columns):
            return False
    return True


def score_answers(db: Database, questions: list[dict], answers: dict[str, dict]) -> tuple[int, list[dict]]:
    """미리 받은 답안 SQL(Claude Code 스킬 등)을 정답과 비교합니다. API를 부르지 않습니다."""
    passed, report = 0, []
    for q in questions:
        gold = db.run(q["gold_sql"]).rows
        item = answers.get(q["id"], {})
        sql = (item.get("sql") or "").strip()
        status, rows, message = "missing", None, "답안 없음"
        if sql:
            try:
                rows = db.run(sql).rows
                status, message = "ok", ""
            except QueryError as e:
                status, message = ("blocked" if e.blocked else "error"), str(e)
        ok = rows is not None and matches(gold, rows, q["ordered"], q.get("check_columns"))
        passed += ok
        report.append({"id": q["id"], "pass": ok, "status": status, "attempts": item.get("attempts"), "sql": sql, "message": message})
    return passed, report


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="새록 SQL 예시 질문 채점")
    parser.add_argument("ids", nargs="*", help="채점할 질문 id(없으면 전체)")
    parser.add_argument("--answers", type=Path, help="답안 JSON으로 채점(API 없이). 형식: {\"model\": ..., \"answers\": [{\"id\", \"sql\", \"attempts\"}]}")
    parser.add_argument("--export-questions", type=Path, help="정답 SQL을 뺀 질문 목록만 내보내기")
    args = parser.parse_args(argv)
    questions = json.loads((HERE / "questions.json").read_text(encoding="utf-8"))
    if args.ids:
        questions = [q for q in questions if q["id"] in args.ids]
    if args.export_questions:
        args.export_questions.write_text(json.dumps([{"id": q["id"], "question": q["question"]} for q in questions], ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"질문 {len(questions)}개를 내보냈습니다: {args.export_questions}")
        return 0
    db = Database()
    if args.answers:
        data = json.loads(args.answers.read_text(encoding="utf-8"))
        model = data.get("model", "unknown")
        passed, report = score_answers(db, questions, {a["id"]: a for a in data["answers"]})
        for item in report:
            print(f"{item['id']} {'통과' if item['pass'] else '실패'} ({item['status']})")
    else:
        key = keystore.get_key()
        if not key:
            print("API 키가 없습니다. saerok-sql을 실행해 /key로 먼저 등록하거나 --answers로 채점해 주세요.")
            return 2
        model = DEFAULT_MODEL
        agent = Agent(ClaudeBrain(key, DEFAULT_MODEL), db)
        passed, report = 0, []
        for q in questions:
            gold = db.run(q["gold_sql"]).rows
            answer = agent.ask(q["question"])
            ok = answer.result is not None and matches(gold, answer.result.rows, q["ordered"], q.get("check_columns"))
            passed += ok
            report.append({"id": q["id"], "pass": ok, "status": answer.status, "attempts": answer.attempts, "sql": answer.sql, "message": answer.message})
            print(f"{q['id']} {'통과' if ok else '실패'} ({answer.status}, 시도 {answer.attempts})")
    out = HERE / f"result-{datetime.now():%Y%m%d-%H%M}.local.json"
    out.write_text(json.dumps({"model": model, "passed": passed, "total": len(questions), "items": report}, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print(f"{passed}/{len(questions)} 통과 · 자세한 결과: {out}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
