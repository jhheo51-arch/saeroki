"""Claude API로 SQL을 만들고 풀이합니다. 응답은 JSON 형식으로 고정합니다."""

from __future__ import annotations

import json
from typing import Protocol

import anthropic

DEFAULT_MODEL = "claude-sonnet-5-5"
MODELS = {
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
    "haiku": "claude-haiku-5-5",
}

_PART = {
    "type": "object",
    "properties": {"part": {"type": "string"}, "meaning": {"type": "string"}},
    "required": ["part", "meaning"],
    "additionalProperties": False,
}
_STRINGS = {"type": "array", "items": {"type": "string"}}

GENERATE_SCHEMA = {
    "type": "object",
    "properties": {
        "cannot_answer": {"type": "string"},
        "assumptions": _STRINGS,
        "sql": {"type": "string"},
        "explanation": {"type": "array", "items": _PART},
        "caveats": _STRINGS,
    },
    "required": ["cannot_answer", "assumptions", "sql", "explanation", "caveats"],
    "additionalProperties": False,
}

EXPLAIN_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "steps": {"type": "array", "items": _PART},
        "result_shape": {"type": "string"},
        "caveats": _STRINGS,
    },
    "required": ["summary", "steps", "result_shape", "caveats"],
    "additionalProperties": False,
}

RULES = """당신은 '새록 SQL'입니다. SQL을 모르는 회사 직원이 우리말로 물으면 아래 데이터 사전의 표로 DuckDB SQL을 만들고, 받은 SQL은 쉬운 우리말로 풀어 줍니다.

SQL을 만들 때:
- DuckDB 문법으로 SELECT 또는 WITH로 시작하는 문장 하나만 씁니다. 세미콜론은 붙이지 않습니다.
- 데이터 사전에 있는 표와 컬럼만 씁니다. 파일을 직접 읽거나 표를 바꾸는 SQL은 쓰지 않습니다.
- 결과 컬럼에는 큰따옴표로 감싼 한국어 별칭을 붙입니다. 예: SUM(board) AS "승차 인원"
- '많이', '요즘', '인기' 같은 애매한 말은 하나로 정해 쓰고, 그 선택을 assumptions에 한 줄씩 적습니다. 기간을 말하지 않았으면 데이터 전체 기간을 쓰고 그렇게 적습니다.
- 사전의 '주의'를 지킵니다. 예: 카페 매장 수는 분기 하나를 골라 셉니다. 따릉이 기간 비교는 하루 평균을 씁니다. 배달 값은 주문 건수가 아니라 사용일수입니다.
- 순위를 물으면 ORDER BY와 LIMIT를 씁니다. 그 밖에는 LIMIT를 붙이지 않아도 됩니다(화면은 최대 1,000행).
- 데이터로 답할 수 없는 질문(없는 기간·지역·지표, 개인 정보, 미래 예측)은 sql을 빈 문자열로 두고 cannot_answer에 이유를 적습니다. 답할 수 있으면 cannot_answer는 빈 문자열입니다.
- explanation은 SQL의 각 부분(FROM, JOIN, WHERE, GROUP BY, 집계, ORDER BY 등)을 순서대로 짚어 무엇을 하는지 한 줄씩 씁니다.
- caveats에는 이 결과를 읽을 때 알아야 할 데이터 한계를 적습니다(사전의 주의에서 해당하는 것).
- 이전 SQL이 오류를 냈다는 메시지를 받으면 오류를 읽고 고친 SQL을 다시 냅니다.

SQL을 풀이할 때:
- summary에 이 SQL이 무엇을 구하는지 한두 문장으로 씁니다.
- steps에 SQL의 각 부분을 순서대로 짚어 쉬운 말로 풀이합니다.
- result_shape에 결과 한 행이 무엇을 뜻하는지 씁니다.
- caveats에 이 SQL의 함정(중복 집계, 기간 누락, 사전의 주의와 어긋나는 점 등)을 적습니다. 없으면 빈 배열입니다.

모든 글은 존댓말 한국어로 짧게 씁니다."""


class LLMError(Exception):
    """AI 호출이 실패했거나 쓸 수 없는 응답이 왔습니다."""


class SQLBrain(Protocol):
    model: str

    def generate(self, question: str, schema_text: str, failed_sql: str = "", error: str = "") -> dict: ...

    def explain(self, sql: str, schema_text: str) -> dict: ...


class ClaudeBrain:
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, client: anthropic.Anthropic | None = None):
        self.model = model
        self.client = client or anthropic.Anthropic(api_key=api_key)

    def _call(self, schema_text: str, user_text: str, schema: dict) -> dict:
        try:
            response = self.client.beta.messages.create(
                model=self.model,
                max_tokens=16000,
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
                system=[
                    {"type": "text", "text": RULES},
                    {"type": "text", "text": schema_text, "cache_control": {"type": "ephemeral"}},
                ],
                messages=[{"role": "user", "content": user_text}],
                output_config={"effort": "medium", "format": {"type": "json_schema", "schema": schema}},
            )
        except anthropic.AuthenticationError:
            raise LLMError("API 키가 맞지 않습니다. /key로 다시 등록해 주세요.")
        except anthropic.PermissionDeniedError:
            raise LLMError("이 API 키로는 이 모델을 쓸 수 없습니다.")
        except anthropic.NotFoundError:
            raise LLMError(f"모델을 찾지 못했습니다: {self.model}")
        except anthropic.RateLimitError:
            raise LLMError("요청이 너무 많아 잠시 막혔습니다. 조금 뒤 다시 물어봐 주세요.")
        except anthropic.APIStatusError as error:
            raise LLMError(f"Claude API 오류({error.status_code}): {error.message}")
        except anthropic.APIConnectionError:
            raise LLMError("인터넷 연결을 확인해 주세요.")
        if response.stop_reason == "refusal":
            raise LLMError("Claude가 이 요청에 답하지 않았습니다. 질문을 바꿔 다시 물어봐 주세요.")
        if response.stop_reason == "max_tokens":
            raise LLMError("답이 너무 길어 중간에 끊겼습니다. 질문을 좁혀 주세요.")
        text = next((block.text for block in response.content if block.type == "text"), "")
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            raise LLMError("AI 응답을 읽지 못했습니다.")

    def generate(self, question: str, schema_text: str, failed_sql: str = "", error: str = "") -> dict:
        user_text = f"질문: {question}"
        if failed_sql:
            user_text += f"\n\n이전에 만든 SQL이 실행되지 않았습니다.\nSQL:\n{failed_sql}\n\n오류:\n{error}\n\n고친 SQL을 다시 주세요."
        return self._call(schema_text, user_text, GENERATE_SCHEMA)

    def explain(self, sql: str, schema_text: str) -> dict:
        return self._call(schema_text, f"이 SQL을 풀이해 주세요.\n\n{sql}", EXPLAIN_SCHEMA)
