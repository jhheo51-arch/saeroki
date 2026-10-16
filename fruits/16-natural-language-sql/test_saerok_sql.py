"""새록 SQL 자동 검사. Claude API를 부르지 않고 가짜 두뇌로 흐름을 확인합니다."""

import io
import json
import os
import tempfile
import unittest
from pathlib import Path

try:
    import duckdb  # noqa: F401
    import rich  # noqa: F401
    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

HERE = Path(__file__).resolve().parent
_TMP = tempfile.TemporaryDirectory()
os.environ["SAEROK_SQL_HOME"] = _TMP.name

if HAS_DEPS:
    from rich.console import Console

    from saerok_sql import dictionary as dict_mod
    from saerok_sql.agent import Agent
    from saerok_sql.cli import App, render_answer
    from saerok_sql.db import Database, QueryError
    from saerok_sql.history import History
    from saerok_sql.llm import EXPLAIN_SCHEMA, GENERATE_SCHEMA, LLMError
    from saerok_sql.router import route
    from saerok_sql.safety import check_sql


class FakeBrain:
    """미리 정한 응답을 차례로 돌려주는 가짜 두뇌."""

    model = "fake"

    def __init__(self, drafts=None, explanation=None, error=None):
        self.drafts = list(drafts or [])
        self.explanation = explanation
        self.error = error
        self.calls = []

    def generate(self, question, schema_text, failed_sql="", error=""):
        self.calls.append({"question": question, "failed_sql": failed_sql, "error": error, "schema_text": schema_text})
        if self.error:
            raise LLMError(self.error)
        return self.drafts.pop(0)

    def explain(self, sql, schema_text):
        self.calls.append({"sql": sql})
        return self.explanation


def draft(sql, assumptions=(), cannot=""):
    return {"cannot_answer": cannot, "assumptions": list(assumptions), "sql": sql,
            "explanation": [{"part": "FROM", "meaning": "표를 고릅니다"}], "caveats": []}


@unittest.skipUnless(HAS_DEPS, "duckdb·rich가 없어 새록 SQL 검사를 건너뜁니다(pip install -e fruits/16-natural-language-sql)")
class SaerokSqlTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = Database()
        cls.dictionary = dict_mod.load()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # 안전 검사
    def test_only_single_select_or_with_passes(self):
        allowed = ["SELECT 1", "with a as (select 1) select * from a", "-- 주석\nSELECT * FROM dong", "(SELECT 1)"]
        blocked = ["DELETE FROM dong", "SELECT 1; DROP TABLE dong", "CREATE TABLE x AS SELECT 1", "COPY dong TO 'x.csv'",
                   "ATTACH 'x.db'", "INSTALL httpfs", "SET threads=1", "PRAGMA version", "SHOW TABLES", "DESCRIBE dong",
                   "SELECT * FROM read_csv('a.csv')", "SELECT * FROM 'fruits/x.parquet'", "SELECT getenv('PATH')", ""]
        for sql in allowed:
            self.assertTrue(check_sql(sql).ok, sql)
        for sql in blocked:
            self.assertFalse(check_sql(sql).ok, sql)

    def test_database_is_read_only_and_closed_to_files(self):
        for sql in ("CREATE TABLE x AS SELECT 1", "SET enable_external_access=true", "SELECT * FROM read_parquet('x.parquet')"):
            with self.assertRaises(Exception):
                self.db.con.execute(sql)

    def test_run_limits_rows_and_reports_errors(self):
        result = self.db.run("SELECT * FROM subway_daily")
        self.assertEqual(len(result.rows), 1000)
        self.assertTrue(result.truncated)
        small = self.db.run("SELECT gu FROM dong GROUP BY gu")
        self.assertEqual(len(small.rows), 25)
        self.assertFalse(small.truncated)
        with self.assertRaises(QueryError) as ctx:
            self.db.run("SELECT no_such_column FROM dong")
        self.assertFalse(ctx.exception.blocked)
        with self.assertRaises(QueryError) as ctx:
            self.db.run("DELETE FROM dong")
        self.assertTrue(ctx.exception.blocked)

    # 데이터 사전
    def test_dictionary_covers_every_table_and_column(self):
        self.assertEqual(dict_mod.coverage_errors(self.dictionary, self.db.tables()), [])
        text = dict_mod.render(self.dictionary, self.db.tables())
        self.assertEqual(text, dict_mod.render(self.dictionary, self.db.tables()))
        self.assertIn("## subway_daily", text)
        self.assertIn("board (BIGINT)", text)

    def test_tables_in_sql_reads_from_and_join_only(self):
        sql = "SELECT gu, dong FROM bike_dong_hourly b JOIN weather_daily w ON b.year = w.year WHERE dong = '여의동'"
        self.assertEqual(dict_mod.tables_in_sql(sql, self.dictionary), ["bike_dong_hourly", "weather_daily"])
        self.assertEqual(dict_mod.tables_in_sql("SELECT * FROM dong", self.dictionary), ["dong"])
        self.assertEqual(dict_mod.tables_in_sql('SELECT 1 FROM "cafes",dong', self.dictionary), ["cafes"])

    def test_every_table_has_source_and_license(self):
        for name, info in self.dictionary["tables"].items():
            self.assertTrue(info["source"].strip(), name)
            self.assertTrue(info["license"].strip(), name)
        sources = (HERE / "data" / "SOURCES.md").read_text(encoding="utf-8")
        self.assertIn("Open-Meteo", sources)

    # 입력 구분
    def test_router_separates_commands_sql_and_questions(self):
        self.assertEqual(route("  ").kind, "empty")
        r = route("/describe subway_daily")
        self.assertEqual((r.kind, r.command, r.arg), ("command", "describe", "subway_daily"))
        self.assertEqual(route("select * from dong").kind, "sql")
        self.assertEqual(route("-- 메모\nWITH a AS (SELECT 1) SELECT * FROM a").kind, "sql")
        self.assertEqual(route("2025년 따릉이 많이 탄 동은?").kind, "question")
        self.assertEqual(route("selection 기준이 뭐야?").kind, "question")
        self.assertEqual(route("with 문법이 뭐야?").kind, "question")
        self.assertEqual(route("DELETE FROM dong").kind, "sql")

    # 질문 흐름
    def test_question_runs_sql_and_attaches_table_notes(self):
        brain = FakeBrain([draft("SELECT gu AS \"구\", count(*) AS \"동 수\" FROM dong GROUP BY gu ORDER BY 2 DESC LIMIT 3", ["동 수 = 행정동 개수"])])
        answer = Agent(brain, self.db, self.dictionary).ask("동이 많은 구 3곳")
        self.assertEqual(answer.status, "ok")
        self.assertEqual(answer.result.columns, ["구", "동 수"])
        self.assertEqual(len(answer.result.rows), 3)
        self.assertEqual(answer.assumptions, ["동 수 = 행정동 개수"])
        self.assertTrue(any(n.startswith("dong:") for n in answer.data_notes))
        self.assertIn("## dong", brain.calls[0]["schema_text"])

    def test_execution_error_is_fixed_at_most_twice(self):
        brain = FakeBrain([draft("SELECT wrong FROM dong"), draft("SELECT gu FROM dong LIMIT 1")])
        answer = Agent(brain, self.db, self.dictionary).ask("구 하나")
        self.assertEqual((answer.status, answer.attempts), ("ok", 2))
        self.assertEqual(brain.calls[1]["failed_sql"], "SELECT wrong FROM dong")
        self.assertIn("wrong", brain.calls[1]["error"])

        brain = FakeBrain([draft("SELECT a FROM dong"), draft("SELECT b FROM dong"), draft("SELECT c FROM dong")])
        answer = Agent(brain, self.db, self.dictionary).ask("계속 틀림")
        self.assertEqual((answer.status, answer.attempts, len(brain.calls)), ("error", 3, 3))
        self.assertIn("2번 고쳐 봤지만", answer.message)
        self.assertIsNone(answer.result)

    def test_unsafe_sql_from_ai_is_never_run(self):
        brain = FakeBrain([draft("DELETE FROM dong")] * 3)
        answer = Agent(brain, self.db, self.dictionary).ask("동을 지워 줘")
        self.assertEqual(answer.status, "blocked")
        self.assertIsNone(answer.result)
        self.assertEqual(self.db.run("SELECT count(*) FROM dong").rows[0][0], 430)

    def test_empty_result_is_flagged_not_hidden(self):
        brain = FakeBrain([draft("SELECT * FROM dong WHERE gu = '없는구'")])
        answer = Agent(brain, self.db, self.dictionary).ask("없는구의 동")
        self.assertEqual(answer.status, "review")
        self.assertTrue(any("0행" in r for r in answer.review))

    def test_cannot_answer_and_llm_failure_are_reported(self):
        answer = Agent(FakeBrain([draft("", cannot="2030년 데이터는 없습니다")]), self.db, self.dictionary).ask("2030년 지하철")
        self.assertEqual((answer.status, answer.message), ("cannot_answer", "2030년 데이터는 없습니다"))
        answer = Agent(FakeBrain(error="인터넷 연결을 확인해 주세요."), self.db, self.dictionary).ask("아무거나")
        self.assertEqual((answer.status, answer.message), ("error", "인터넷 연결을 확인해 주세요."))

    def test_explain_runs_safe_sql_and_refuses_unsafe(self):
        explanation = {"summary": "구별 동 수", "steps": [{"part": "GROUP BY gu", "meaning": "구별로 묶습니다"}],
                       "result_shape": "구 하나", "caveats": []}
        agent = Agent(FakeBrain(explanation=explanation), self.db, self.dictionary)
        answer = agent.explain("SELECT gu, count(*) FROM dong GROUP BY gu")
        self.assertEqual((answer.status, answer.summary, len(answer.result.rows)), ("ok", "구별 동 수", 25))
        answer = agent.explain("DELETE FROM dong")
        self.assertEqual(answer.status, "blocked")
        self.assertIsNone(answer.result)
        self.assertIn("실행하지 않았습니다", answer.message)

    # 기록
    def test_history_keeps_no_result_values_and_moves_between_pcs(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = History(Path(tmp) / "a.jsonl"), History(Path(tmp) / "b.jsonl")
            answer = Agent(FakeBrain([draft("SELECT gu FROM dong LIMIT 2")]), self.db, self.dictionary).ask("구 두 개")
            entry = a.add(answer, "fake")
            self.assertEqual((entry["rows"], entry["status"]), (2, "ok"))
            self.assertNotIn("result", entry)
            self.assertNotIn("종로구", json.dumps(entry, ensure_ascii=False))
            exported = Path(tmp) / "move.json"
            self.assertEqual(a.export(exported), 1)
            self.assertEqual(b.import_(exported), 1)
            self.assertEqual(b.import_(exported), 0)
            self.assertEqual(b.all()[0]["input"], "구 두 개")
            bad = Path(tmp) / "bad.json"
            bad.write_text("[]", encoding="utf-8")
            with self.assertRaises(ValueError):
                b.import_(bad)

    # 화면
    def test_render_shows_assumptions_sql_result_explanation_and_notes(self):
        brain = FakeBrain([draft("SELECT gu AS \"구\" FROM dong GROUP BY gu ORDER BY 1 LIMIT 25", ["전체 기간"])])
        answer = Agent(brain, self.db, self.dictionary).ask("구 목록")
        console = Console(record=True, width=120, force_terminal=False, file=io.StringIO())
        render_answer(console, answer)
        out = console.export_text()
        for text in ("완료", "AI가 작성", "가정", "전체 기간", "SQL", "구", "25행 · 앞 20행 표시", "풀이", "한계·주의"):
            self.assertIn(text, out)

    def test_commands_work_without_api_key(self):
        console = Console(record=True, width=120, force_terminal=False, file=io.StringIO())
        app = App(console, keep_history=False)
        self.assertTrue(app.handle("/tables", interactive=False))
        self.assertTrue(app.handle("/describe bike_dong_hourly", interactive=False))
        self.assertTrue(app.handle("/model haiku", interactive=False))
        self.assertTrue(app.handle("/nope", interactive=False))
        self.assertFalse(app.handle("/exit", interactive=False))
        out = console.export_text()
        for text in ("subway_daily", "avg_rides_per_day", "claude-haiku-5-5", "모르는 명령"):
            self.assertIn(text, out)

    # Claude Code 스킬용 명령(AI 없이)
    def test_run_json_executes_safely_and_logs_without_values(self):
        from saerok_sql.tools import run_json

        with tempfile.TemporaryDirectory() as tmp:
            history = History(Path(tmp) / "h.jsonl")
            ok = run_json(self.db, 'SELECT gu AS "구" FROM dong GROUP BY gu ORDER BY 1', "구 목록", history)
            self.assertEqual((ok["status"], ok["row_count"], ok["rows_shown"], ok["columns"]), ("ok", 25, 25, ["구"]))
            json.dumps(ok, ensure_ascii=False)
            big = run_json(self.db, "SELECT * FROM weather_daily")
            self.assertEqual((big["row_count"], big["rows_shown"], big["truncated_at_1000"]), (1000, 50, True))
            self.assertTrue(any("1,000행" in r for r in big["review"]))
            self.assertIsInstance(big["rows"][0][0], str)
            bad = run_json(self.db, "DELETE FROM dong", "", history)
            self.assertEqual(bad["status"], "blocked")
            self.assertNotIn("rows", bad)
            entries = history.all()
            self.assertEqual([(e["mode"], e["status"], e["model"]) for e in entries],
                             [("question", "ok", "claude-code"), ("sql", "blocked", "claude-code")])

    def test_skill_file_uses_only_safe_commands(self):
        from saerok_sql.tools import SKILL_SOURCE, install_skill

        text = SKILL_SOURCE.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\nname: saerok-sql\n"))
        for needle in ("saerok-sql --schema", "saerok-sql --run -", "최대 2번", "검토 필요", "$ARGUMENTS"):
            self.assertIn(needle, text)
        with tempfile.TemporaryDirectory() as tmp:
            installed = install_skill(Path(tmp))
            self.assertEqual(installed.read_text(encoding="utf-8"), text)

    def test_response_schemas_are_strict(self):
        for schema in (GENERATE_SCHEMA, EXPLAIN_SCHEMA):
            self.assertFalse(schema["additionalProperties"])
            self.assertEqual(set(schema["required"]), set(schema["properties"]))

    # 채점 세트
    def test_eval_matching_ignores_extra_columns_but_not_order_or_values(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("run_eval", HERE / "eval" / "run_eval.py")
        run_eval = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_eval)
        gold = [("강남", 100), ("잠실", 90)]
        self.assertTrue(run_eval.matches(gold, [("2호선", "강남", 100.0), ("2호선", "잠실", 90.0)], True))
        self.assertTrue(run_eval.matches(gold, [("잠실", 90), ("강남", 100)], False))
        self.assertFalse(run_eval.matches(gold, [("잠실", 90), ("강남", 100)], True))
        self.assertFalse(run_eval.matches(gold, [("강남", 100), ("잠실", 80)], True))
        self.assertFalse(run_eval.matches(gold, [("강남", 100)], True))
        self.assertTrue(run_eval.matches([(1.0,)], [(1.004,)], False))
        rainy = [(False, 113254.3), (True, 81428.8)]
        labelled = [("비 안 온 날", 245, 113254.3), ("비 온 날", 108, 81428.8)]
        self.assertFalse(run_eval.matches(rainy, labelled, False))
        self.assertTrue(run_eval.matches(rainy, labelled, False, [1]))

    def test_score_answers_without_api(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("run_eval", HERE / "eval" / "run_eval.py")
        run_eval = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(run_eval)
        questions = [q for q in json.loads((HERE / "eval" / "questions.json").read_text(encoding="utf-8")) if q["id"] in ("q19", "q04", "q16")]
        answers = {
            "q19": {"sql": "SELECT count(*) AS \"동 수\" FROM dong WHERE gu = '마포구'", "attempts": 1},
            "q04": {"sql": "SELECT count(*) FROM weather_daily WHERE year = 2024 AND rainy_day", "attempts": 1},
        }
        passed, report = run_eval.score_answers(self.db, questions, answers)
        by_id = {r["id"]: r for r in report}
        self.assertEqual(passed, 1)
        self.assertTrue(by_id["q19"]["pass"])
        self.assertFalse(by_id["q04"]["pass"])
        self.assertEqual(by_id["q16"]["status"], "missing")

    def test_eval_gold_sql_runs_and_returns_rows(self):
        questions = json.loads((HERE / "eval" / "questions.json").read_text(encoding="utf-8"))
        self.assertEqual(len(questions), 20)
        self.assertEqual(len({q["id"] for q in questions}), 20)
        for q in questions:
            result = self.db.run(q["gold_sql"])
            self.assertTrue(result.rows, q["id"])
            self.assertFalse(result.truncated, q["id"])


if __name__ == "__main__":
    unittest.main()
