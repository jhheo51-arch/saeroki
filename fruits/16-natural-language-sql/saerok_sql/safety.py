"""실행 전 SQL 안전 검사: 문장 하나의 SELECT·WITH 조회만 통과시킵니다."""

from __future__ import annotations

import re
from dataclasses import dataclass

import duckdb

# 파일·네트워크·환경에 닿는 함수. DB를 외부 접근 차단으로 열어 두지만, 실행 전에 한 번 더 막습니다.
FORBIDDEN_FUNCTIONS = (
    "read_csv", "read_csv_auto", "read_parquet", "parquet_scan", "parquet_metadata", "parquet_schema",
    "read_json", "read_json_auto", "read_json_objects", "read_ndjson", "read_ndjson_auto",
    "read_text", "read_blob", "glob", "sniff_csv", "iceberg_scan", "delta_scan", "read_xlsx",
    "st_read", "getenv", "query", "query_table", "httpfs",
)


@dataclass(frozen=True)
class SafetyResult:
    ok: bool
    reason: str = ""


def _strip_strings_and_comments(sql: str) -> str:
    sql = re.sub(r"--[^\n]*", " ", sql)
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.S)
    sql = re.sub(r"'(?:[^']|'')*'", "''", sql)
    return sql


def check_sql(sql: str) -> SafetyResult:
    text = (sql or "").strip()
    if not text:
        return SafetyResult(False, "SQL이 비어 있습니다")
    try:
        statements = duckdb.extract_statements(text)
    except duckdb.Error as error:
        return SafetyResult(False, f"SQL 문법을 읽지 못했습니다: {error}")
    if len(statements) != 1:
        return SafetyResult(False, f"SQL 문장은 하나만 실행합니다(지금 {len(statements)}개)")
    if statements[0].type != duckdb.StatementType.SELECT:
        return SafetyResult(False, f"조회(SELECT·WITH)만 실행합니다. 이 문장은 {statements[0].type.name}입니다")
    body = _strip_strings_and_comments(text).lower()
    # DuckDB는 PRAGMA·SHOW 등도 SELECT로 분류하므로 첫 단어까지 확인합니다.
    if not re.match(r"[\s(]*(select|with)\b", body):
        return SafetyResult(False, "조회는 SELECT나 WITH로 시작해야 합니다")
    for name in FORBIDDEN_FUNCTIONS:
        if re.search(rf"\b{name}\s*\(", body):
            return SafetyResult(False, f"파일·외부 접근 함수 {name}()는 쓸 수 없습니다")
    if re.search(r"'[^']*\.(csv|parquet|json|txt|xlsx|db|duckdb)'", text, flags=re.I):
        return SafetyResult(False, "파일 경로를 직접 읽는 SQL은 쓸 수 없습니다")
    return SafetyResult(True)
