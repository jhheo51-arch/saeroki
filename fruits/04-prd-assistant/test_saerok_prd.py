import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from saerok_prd import check, cli

HERE = Path(__file__).resolve().parent
WEAK = (HERE / "examples" / "weak-prd.md").read_text(encoding="utf-8")


def status(result, key):
    return next(c["status"] for c in result["criteria"] if c["key"] == key)


class CriteriaTest(unittest.TestCase):
    def test_weak_example(self):
        r = check.check(WEAK)
        self.assertEqual(r["title"], "동네 산책 메이트 PRD")
        self.assertEqual(status(r, "problem"), "ok")
        self.assertEqual(status(r, "metric"), "weak")  # '목표' 절에 숫자가 없음
        self.assertEqual(status(r, "users"), "missing")
        self.assertEqual(r["summary"], {"ok": 3, "total": 7, "findings": 5})

    def test_line_findings(self):
        kinds = [(f["line"], f["kind"]) for f in check.check(WEAK)["findings"]]
        self.assertEqual(kinds, [(3, "order"), (10, "vague"), (11, "unsourced"), (16, "vague"), (17, "pending")])

    def test_code_blocks_are_skipped(self):
        self.assertFalse(any(f["line"] > 18 for f in check.check(WEAK)["findings"]))

    def test_complete_prd(self):
        text = """# 좋은 PRD
## 문제
2026-10 인터뷰 8명 중 6명이 주 3회 이상 겪었습니다.
## 대상 사용자
혼자 사는 20대 직장인
## 해결책
알림 기능
## 성공 지표
출시 4주 뒤 재방문 30%
## 하지 않을 것
결제
## 가정과 위험
알림을 끌 수 있음
"""
        r = check.check(text)
        self.assertEqual(r["summary"], {"ok": 7, "total": 7, "findings": 0})

    def test_done_list_is_not_a_metric(self):
        r = check.check("# 제목\n## 문제\n문제\n## 완료 기준\n- 화면 3개\n")
        metric = next(c for c in r["criteria"] if c["key"] == "metric")
        self.assertEqual(metric["status"], "missing")
        self.assertIn("완료 기준", metric["note"])

    def test_target_users_heading_is_users(self):
        r = check.check("# 제목\n## 목표 사용자\n대학생\n")
        self.assertEqual(status(r, "users"), "ok")
        self.assertEqual(status(r, "metric"), "missing")

    def test_table_follows_sourced_sentence_and_inline_code_is_quoted(self):
        text = """# 제목
## 문제
2026-10-17 직접 센 결과입니다.
| 항목 | 값 |
| A | 30% |
규칙은 `미정`을 찾습니다.
그냥 쓴 문장입니다.
| B | 40% |
"""
        kinds = [(f["line"], f["kind"]) for f in check.check(text)["findings"]]
        self.assertEqual(kinds, [(8, "unsourced")])  # 출처 없는 문장 뒤의 표만 짚음

    def test_compound_heading_counts_for_each_criterion(self):
        r = check.check("# 제목\n## 사용자와 목표\n대학생, 4주 뒤 재방문 30%\n## 목표와 비목표\n### 비목표 (Non-goals)\n결제\n"
                        "## 해결하려는 문제와 독자\n찾기 어렵습니다.\n## 열린 질문\n가격\n")
        for key in ("users", "metric", "scope_out", "problem", "risk"):
            self.assertEqual(status(r, key), "ok", key)

    def test_job_posting_requirement_is_not_solution(self):
        r = check.check("# 제목\n## 1. 공고에서 요구하는 역할\n분석\n## 2. 문제\n지연\n## 3. 기능 요구사항\n알림\n")
        self.assertEqual([f["kind"] for f in r["findings"]], [])
        self.assertEqual(next(c for c in r["criteria"] if c["key"] == "solution")["line"], 6)

    def test_source_and_unit_exceptions(self):
        text = """# 제목
## 문제
혜택은 1회성 가치가 섞이기 쉽습니다.
2026년 10월 8일 직접 호출해 평균 74.8%를 확인했습니다.
공식 노하우에는 재고 소진 29.6%가 소개되어 있습니다.
사용자의 70%가 겪습니다.
"""
        self.assertEqual([(f["line"], f["kind"]) for f in check.check(text)["findings"]], [(6, "unsourced")])

    def test_vague_only_in_claims_and_not_negated(self):
        text = """# 제목
## 문제
대부분 손으로 셉니다.
가상 수치로 성과 향상을 주장하지 않습니다.
우선순위가 매겨진 개선 과제로 이어집니다.
## 기능
직관적인 화면
"""
        self.assertEqual([(f["line"], f["kind"]) for f in check.check(text)["findings"]], [(3, "vague")])

    def test_evidence_weak_without_numbers(self):
        r = check.check("# 제목\n## 문제\n찾기 어렵습니다.\n")
        self.assertEqual(status(r, "evidence"), "weak")


class CliTest(unittest.TestCase):
    def test_json_output(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["check", str(HERE / "examples" / "weak-prd.md"), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["summary"]["findings"], 5)

    def test_missing_file(self):
        self.assertEqual(cli.main(["check", str(HERE / "없는파일.md")]), 2)

    def test_text_render(self):
        text = check.render(check.check(WEAK))
        self.assertIn("기준 7개 중 3개 충족", text)
        self.assertIn("11줄 [출처]", text)


if __name__ == "__main__":
    unittest.main()
