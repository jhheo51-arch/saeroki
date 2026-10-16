"""질문 → SQL → 안전 검사 → 실행 → 자기 검토 흐름."""

from __future__ import annotations

from dataclasses import dataclass, field

from . import dictionary as dict_mod
from .db import Database, QueryError, QueryResult
from .llm import LLMError, SQLBrain
from .safety import check_sql

MAX_FIXES = 2


@dataclass
class Answer:
    mode: str  # "question" | "sql"
    input: str
    status: str  # "ok" | "review" | "error" | "cannot_answer" | "blocked"
    sql: str = ""
    assumptions: list[str] = field(default_factory=list)
    explanation: list[dict] = field(default_factory=list)
    summary: str = ""
    result_shape: str = ""
    caveats: list[str] = field(default_factory=list)
    data_notes: list[str] = field(default_factory=list)
    review: list[str] = field(default_factory=list)
    result: QueryResult | None = None
    attempts: int = 0
    message: str = ""


class Agent:
    def __init__(self, brain: SQLBrain, database: Database, dictionary: dict | None = None):
        self.brain = brain
        self.db = database
        self.dictionary = dictionary or dict_mod.load()
        self.schema_text = dict_mod.render(self.dictionary, database.tables())

    def _data_notes(self, sql: str) -> list[str]:
        notes = []
        for table in dict_mod.tables_in_sql(sql, self.dictionary):
            notes += [f"{table}: {note}" for note in self.dictionary["tables"][table]["notes"]]
        return notes

    def _review(self, result: QueryResult) -> list[str]:
        flags = []
        if not result.rows:
            flags.append("결과가 0행입니다. 조건·기간·이름 표기가 데이터와 맞는지 확인해 주세요.")
        if result.truncated:
            flags.append("결과가 1,000행을 넘어 앞 1,000행만 가져왔습니다. 조건을 좁히거나 집계해 보세요.")
        if result.rows and all(all(v is None for v in row) for row in result.rows):
            flags.append("모든 값이 비어 있습니다(NULL). 컬럼·조건을 확인해 주세요.")
        return flags

    def ask(self, question: str) -> Answer:
        answer = Answer("question", question, "error")
        failed_sql = error = ""
        for attempt in range(1, MAX_FIXES + 2):
            answer.attempts = attempt
            try:
                draft = self.brain.generate(question, self.schema_text, failed_sql, error)
            except LLMError as e:
                answer.message = str(e)
                return answer
            answer.assumptions = draft.get("assumptions", [])
            answer.explanation = draft.get("explanation", [])
            answer.caveats = draft.get("caveats", [])
            answer.sql = (draft.get("sql") or "").strip()
            if draft.get("cannot_answer") and not answer.sql:
                answer.status = "cannot_answer"
                answer.message = draft["cannot_answer"]
                return answer
            answer.data_notes = self._data_notes(answer.sql)
            try:
                answer.result = self.db.run(answer.sql)
            except QueryError as e:
                failed_sql, error = answer.sql, str(e)
                answer.status = "blocked" if e.blocked else "error"
                answer.message = str(e)
                continue
            answer.review = self._review(answer.result)
            answer.status = "review" if answer.review else "ok"
            answer.message = ""
            return answer
        answer.message = f"{MAX_FIXES}번 고쳐 봤지만 실행하지 못했습니다. 마지막 오류: {answer.message}"
        return answer

    def explain(self, sql: str) -> Answer:
        answer = Answer("sql", sql, "error", sql=sql.strip(), attempts=1)
        try:
            draft = self.brain.explain(answer.sql, self.schema_text)
        except LLMError as e:
            answer.message = str(e)
            return answer
        answer.summary = draft.get("summary", "")
        answer.explanation = draft.get("steps", [])
        answer.result_shape = draft.get("result_shape", "")
        answer.caveats = draft.get("caveats", [])
        answer.data_notes = self._data_notes(answer.sql)
        verdict = check_sql(answer.sql)
        if not verdict.ok:
            answer.status = "blocked"
            answer.message = f"풀이만 했고 실행하지 않았습니다: {verdict.reason}"
            return answer
        try:
            answer.result = self.db.run(answer.sql)
        except QueryError as e:
            answer.status = "error"
            answer.message = f"풀이는 했지만 실행 중 오류가 났습니다: {e}"
            return answer
        answer.review = self._review(answer.result)
        answer.status = "review" if answer.review else "ok"
        return answer
