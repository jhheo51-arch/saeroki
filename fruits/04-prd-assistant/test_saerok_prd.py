import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from saerok_prd import check, cli, compare

HERE = Path(__file__).resolve().parent
WEAK = (HERE / "examples" / "weak-prd.md").read_text(encoding="utf-8")
REVISED = (HERE / "examples" / "weak-prd-revised.md").read_text(encoding="utf-8")


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


class StricterTest(unittest.TestCase):
    def test_resolved_questions_are_weak_risk(self):
        r = check.check("# 제목\n## 열린 질문\n1. ~~언어~~ → 확정: 한국어\n2. ~~환경~~ → 확정: CPU\n")
        self.assertEqual(status(r, "risk"), "weak")

    def test_empty_section_is_weak(self):
        r = check.check("# 제목\n## 하지 않을 것\n## 기능\n알림\n")
        self.assertEqual(status(r, "scope_out"), "weak")

    def test_planned_research_is_not_evidence(self):
        r = check.check("# 제목\n## 문제\n찾기 어렵습니다.\n## 팬 조사\n팬 20명 인터뷰를 목표로 한다.\n")
        self.assertEqual(status(r, "evidence"), "weak")
        r = check.check("# 제목\n## 문제\n찾기 어렵습니다.\n## 팬 조사\n2026-10 팬 5명을 인터뷰했습니다.\n")
        self.assertEqual(status(r, "evidence"), "ok")

    def test_feature_titles_are_not_users_or_risk(self):
        r = check.check("# 제목\n## 사용자 흐름\n입력 → 결과\n## 위험 신호 규칙\n비가 오면 경고\n")
        self.assertEqual((status(r, "users"), status(r, "risk")), ("missing", "missing"))

    def test_every_problem_section_is_checked(self):
        text = "# 제목\n## 배경\n설명 한 줄\n## 문제\n대부분 손으로 셉니다.\n"
        self.assertEqual([(f["line"], f["kind"]) for f in check.check(text)["findings"]], [(5, "vague")])

    def test_metric_needs_measurable_target(self):
        # 목록 번호·날짜·화면 너비는 '얼마나'가 아닙니다.
        r = check.check("# 제목\n## 성공 기준\n1. 2026-10-31까지 추천 이유가 납득됩니다.\n2. 375px 화면에서 봅니다.\n")
        self.assertEqual(status(r, "metric"), "weak")
        r = check.check("# 제목\n## 성공 기준\n4주 안에 다시 쓴 사람 30% 이상\n")
        self.assertEqual(status(r, "metric"), "ok")
        r = check.check("# 제목\n## 성공 기준\n예시 질문 20/20 정답\n")
        self.assertEqual(status(r, "metric"), "ok")

    def test_needs_clarification_marker_is_pending(self):
        r = check.check("# 제목\n## 기능\n로그인은 [NEEDS CLARIFICATION: 방식 미확인]\n")
        self.assertEqual([f["kind"] for f in r["findings"]], ["pending"])

    def test_warnings(self):
        self.assertEqual([w["kind"] for w in check.check("# 메모\n할 일\n")["warnings"]], ["not_prd"])
        long = "# 제목\n## 문제\n" + "줄\n" * 600
        self.assertIn("long", [w["kind"] for w in check.check(long)["warnings"]])
        self.assertEqual(check.check(WEAK)["warnings"], [])


class TopicTest(unittest.TestCase):
    """주제가 달라 기준이 맞지 않을 때: 이유를 밝힌 '해당 없음'과 프로젝트 낱말."""

    def test_skip_comment_needs_reason(self):
        r = check.check("# 제목\n<!-- saerok-prd: 해당 없음 users 혼자 쓰는 도구라 사용자는 나 하나 -->\n## 문제\n지연\n")
        users = next(c for c in r["criteria"] if c["key"] == "users")
        self.assertEqual((users["status"], users["note"]), ("skip", "해당 없음: 혼자 쓰는 도구라 사용자는 나 하나"))
        self.assertEqual(r["summary"]["total"], 6)  # 해당 없음은 분모에서 뺌
        r = check.check("# 제목\n<!-- saerok-prd: 해당 없음 users -->\n")
        self.assertEqual(status(r, "users"), "missing")  # 이유가 없으면 받지 않음

    def test_skip_does_not_hide_existing_section(self):
        r = check.check("# 제목\n## 대상 사용자\n대학생\n", {"skip": {"대상 사용자": "개인 도구"}})
        self.assertEqual(status(r, "users"), "ok")

    def test_project_words(self):
        text = "# 쇼츠 기획\n## 시청자\n역사에 관심 있는 20대\n"
        self.assertEqual(status(check.check(text), "users"), "missing")
        self.assertEqual(status(check.check(text, {"words": {"users": ["시청자"]}}), "users"), "ok")

    def test_compare_marks_skip_separately(self):
        r = compare.compare("# 제목\n## 문제\n지연\n", "# 제목\n<!-- saerok-prd: 해당 없음 risk 하루짜리 실험 -->\n## 문제\n지연\n")
        risk = next(c for c in r["criteria"] if c["key"] == "risk")
        self.assertEqual((risk["before"], risk["after"], risk["change"]), ("missing", "skip", "skip"))
        self.assertEqual((r["summary"]["total_before"], r["summary"]["total_after"]), (7, 6))


class CompareTest(unittest.TestCase):
    def test_revised_example(self):
        r = compare.compare(WEAK, REVISED)
        self.assertEqual(r["summary"], {"ok_before": 3, "ok_after": 6, "total_before": 7, "total_after": 7, "findings_before": 5,
                                        "findings_after": 2, "fixed": 3, "added": 0, "fix_rate": 60})
        self.assertEqual([f["kind"] for f in r["fixed"]], ["order", "unsourced", "vague"])
        changed = {c["key"]: c["change"] for c in r["criteria"] if c["change"] != "same"}
        self.assertEqual(changed, {"metric": "better", "users": "better", "scope_out": "better"})

    def test_moved_line_is_not_fixed_and_new_one_is_added(self):
        before = "# 제목\n## 문제\n가격은 미정입니다.\n"
        after = "# 제목\n## 배경\n설명 한 줄\n## 문제\n가격은  미정입니다.\n출시일 TBD\n"
        r = compare.compare(before, after)
        self.assertEqual(r["summary"]["fixed"], 0)  # 줄이 밀리고 띄어쓰기가 달라도 같은 지적
        self.assertEqual([(f["line"], f["kind"]) for f in r["added"]], [(6, "pending")])

    def test_repeated_finding_counts_each(self):
        before = "# 제목\n## 문제\n미정\n미정\n"
        r = compare.compare(before, "# 제목\n## 문제\n미정\n")
        self.assertEqual((r["summary"]["fixed"], r["summary"]["fix_rate"]), (1, 50))

    def test_no_findings_before(self):
        r = compare.compare("# 제목\n", "# 제목\n")
        self.assertIsNone(r["summary"]["fix_rate"])
        self.assertIn("고칠 지적 없음", compare.render(r))
        self.assertIn("바뀐 기준 없음", compare.render(r))


class CliTest(unittest.TestCase):
    def test_json_output(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["check", str(HERE / "examples" / "weak-prd.md"), "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["summary"]["findings"], 5)

    def test_missing_file(self):
        self.assertEqual(cli.main(["check", str(HERE / "없는파일.md")]), 2)

    def test_compare_command(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli.main(["compare", str(HERE / "examples" / "weak-prd.md"), str(HERE / "examples" / "weak-prd-revised.md")])
        self.assertEqual(code, 0)
        self.assertIn("고친 지적 3개(60%)", out.getvalue())
        self.assertIn("대상 사용자: ❌ 빠짐 → ✅ 있음", out.getvalue())
        self.assertEqual(cli.main(["compare", str(HERE / "없는파일.md"), str(HERE / "examples" / "weak-prd.md")]), 2)

    def test_config_file_is_found_above_prd(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / ".saerok-prd.json").write_text('{"words": {"대상 사용자": ["시청자"]}}', encoding="utf-8")
            (root / "docs").mkdir()
            (root / "docs" / "plan.md").write_text("# 기획\n## 시청자\n20대\n", encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                cli.main(["check", str(root / "docs" / "plan.md"), "--json"])
            self.assertEqual(status(json.loads(out.getvalue()), "users"), "ok")
            (root / ".saerok-prd.json").write_text("{깨짐", encoding="utf-8")
            self.assertEqual(cli.main(["check", str(root / "docs" / "plan.md")]), 2)

    def test_compare_since_commit_and_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git = lambda *a: subprocess.run(["git", "-C", tmp, *a], check=True, capture_output=True)
            git("init", "-q")
            prd = root / "prd.md"
            prd.write_text(WEAK, encoding="utf-8")
            git("add", ".")
            git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "v1")
            prd.write_text(REVISED, encoding="utf-8")
            log = root / "log.jsonl"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(cli.main(["compare", str(prd), "--since", "HEAD", "--log", str(log)]), 0)
                self.assertEqual(cli.main(["compare", str(prd), "--since", "없는커밋"]), 2)
            row = json.loads(log.read_text(encoding="utf-8"))
            self.assertEqual((row["fixed"], row["fix_rate"], row["after"]), (3, 60, str(prd)))

    def test_text_render(self):
        text = check.render(check.check(WEAK))
        self.assertIn("기준 7개 중 3개 충족", text)
        self.assertIn("11줄 [출처]", text)


if __name__ == "__main__":
    unittest.main()
