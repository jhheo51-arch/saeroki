"""새록 지원서(21번 열매) 결정적 계층 검사. 가상 예시만 쓰고, 실제 기록은 임시 지원 폴더에만 만듭니다."""

import contextlib
import http.client
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from saerok_apply import cli, core, store, subscription, terms, web

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"
COMPANY = EXAMPLES / "가상커머스"
DICTIONARY = HERE.parent / "17-saerok-dictionary" / "data"
CORE_JS = HERE / "web" / "apply-core.js"
NODE = shutil.which("node")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


DRAFT = read(COMPANY / "draft-2026-10-17.md")
LEDGER = read(EXAMPLES / "ledger.md")
ANALYSIS = read(COMPANY / "analysis.md")
POSTING = read(COMPANY / "posting.md")
STYLE = read(EXAMPLES / "style.md")
DATA = terms.load()
COMPANIES = [{"name": "가상커머스", "from": "folder"}, {"name": "가상물류", "from": "folder"}] + \
    [{"name": n, "from": "dictionary"} for n in DATA["companies"]]

# 짧은 초안 한 문항: 경험 문단 원칙(상황·행동·이유·연결) 검사용
MINI = """# 자기소개서 · 가상커머스

- 회사: 가상커머스

## 문항 1. 데이터로 문제를 해결한 경험을 써 주세요.
- 유형: 경험형
- 제한: 없음
- 판: v1 · 첫 판
- 상태: 작성 중

{body}
"""


def replace(text: str, old: str, new: str) -> str:
    assert old in text, f"예시에 '{old}'가 없습니다."
    return text.replace(old, new, 1)


def run_check(draft=DRAFT, ledger=LEDGER, analysis=ANALYSIS, posting=POSTING, style=STYLE, companies=COMPANIES,
              previous=""):
    return core.check(draft, ledger, analysis, posting, style, companies, DATA, previous)


def codes(result: dict, level: str | None = None) -> set:
    return {i["code"] for i in result["issues"] if level is None or i["level"] == level}


class ExampleTest(unittest.TestCase):
    """가상 예시는 그대로 오류 0이어야 합니다(오탐 기준선)."""

    def test_example_draft_passes(self):
        r = run_check()
        self.assertEqual(r["summary"]["errors"], 0, r["issues"])
        self.assertTrue(r["summary"]["submittable"])
        self.assertEqual(codes(r), {"coverage_missing"})  # 장부에 SQL 경험이 없음은 경고로만 남습니다.
        self.assertEqual([(q["count"]["with_spaces"], q["fit"]) for q in r["questions"]], [(470, "ok"), (285, "ok")])

    def test_example_ledger_and_analysis(self):
        report = core.ledger_report(LEDGER)
        self.assertEqual(report["summary"], {"experiences": 2, "errors": 0, "unconfirmed": 0})
        a = core.check_analysis(POSTING, ANALYSIS, DATA)
        self.assertEqual(a["summary"]["errors"], 0, a["issues"])
        self.assertFalse(a["blocked"])
        self.assertEqual(a["flags"], {"posting_failed": False, "image_unconfirmed": False, "research_none": True,
                                      "terms_missing": ["개선 우선순위"]})

    def test_examples_have_no_privacy_shape(self):
        for path in EXAMPLES.rglob("*.md"):
            self.assertEqual(store.scan(read(path)), [], path)


class CountTest(unittest.TestCase):
    def test_count_and_fit(self):
        self.assertEqual(core.count("가A 😀\n"), {"with_spaces": 5, "without_spaces": 3, "bytes": 10})
        self.assertEqual(core.fit(core.count("가" * 95), 100, "with_spaces")["fit"], "ok")
        self.assertEqual(core.fit(core.count("가" * 89), 100, "with_spaces")["fit"], "short")
        self.assertEqual(core.fit(core.count("가" * 101), 100, "with_spaces")["fit"], "over")
        self.assertEqual(core.fit(core.count("가 나"), 2, "without_spaces")["fit"], "ok")
        self.assertEqual(core.fit(core.count("가나"), 6, "bytes")["fit"], "ok")
        self.assertEqual(core.fit(core.count("가나"), 0, "with_spaces")["fit"], "no-limit")


class DraftRuleTest(unittest.TestCase):
    """규칙마다 예시 초안을 한 곳만 바꿔 잡히는지(미탐) 봅니다. 바꾸지 않은 예시에는 없어야 합니다(오탐)."""

    BASE = codes(run_check())

    def hit(self, code, level="error", **kw):
        self.assertNotIn(code, self.BASE)
        r = run_check(**kw)
        self.assertIn(code, codes(r, level), r["issues"])
        return r

    def test_facts(self):
        self.hit("number_not_in_ledger", draft=replace(DRAFT, "18%에서 11%로", "18%에서 9%로"))
        self.hit("period_not_in_ledger", draft=replace(DRAFT, "12주치", "15주치"))
        self.hit("title_not_in_ledger", draft=replace(DRAFT, "기획 팀장을 맡았던", "동아리 회장을 맡았던"))
        self.hit("change_unsupported", "warn", draft=replace(DRAFT, "노쇼율을 18%에서", "노쇼율을 처음으로 18%에서"))
        self.hit("plan_as_done", draft=replace(DRAFT, "대기 예약 기능도 설계해 두었지만 아직 도입 전입니다. <!-- 의견 -->",
                                               "노쇼가 잦은 시간대에 대기 예약을 받는 기능을 만들었습니다. <!-- E01 행동 -->"))
        # 설계안을 설계안으로 쓰면 잡지 않습니다.
        ok = run_check(draft=replace(DRAFT, "대기 예약 기능도 설계해 두었지만 아직 도입 전입니다. <!-- 의견 -->",
                                     "노쇼가 잦은 시간대에 대기 예약을 받는 기능을 설계했습니다. <!-- E01 행동 -->"))
        self.assertNotIn("plan_as_done", codes(ok))

    def test_metrics(self):
        self.hit("metric_name_mismatch", draft=replace(DRAFT, "주간 좌석 노쇼율을", "주간 좌석 이용 비율을"))
        self.hit("metric_unit_mismatch", draft=replace(DRAFT, "주간 좌석 노쇼율을", "회원당 주간 좌석 노쇼율을"))
        self.hit("metric_time_mismatch", draft=replace(DRAFT, "주간 좌석 노쇼율을", "2024년 주간 좌석 노쇼율을"))

    def test_unconfirmed_ledger(self):
        ledger = replace(LEDGER, "- 팀 성과: 운영진 4명이", "- 팀 성과: (AI 정리, 확인 전) 운영진 4명이")
        r = run_check(ledger=ledger)
        self.assertIn("unconfirmed_ledger", codes(r, "warn"))
        ledger = replace(LEDGER, "| 규모: 회원 120명 |", "| 규모: 회원 120명 (AI 정리, 확인 전) |")
        self.assertIn("unconfirmed_ledger", codes(run_check(ledger=ledger), "warn"))

    def test_sources(self):
        self.hit("number_not_in_posting", draft=replace(DRAFT, "주문·배송 경험 개선을", "주문·배송 경험 개선 7가지를"))
        self.hit("research_none_cited", draft=replace(DRAFT, "줄이는 일을 하고 싶습니다. <!-- 공고 -->",
                                                      "줄이는 일을 하고 싶습니다. <!-- 조사 -->"))
        research = replace(ANALYSIS, "### 회사 조사\n\n- 조사 안 됨",
                           "### 회사 조사\n\n- 회원 3만 명 규모입니다. (https://example.com/a, 2026-10-17)")
        r = run_check(analysis=research, draft=replace(DRAFT, "줄이는 일을 하고 싶습니다. <!-- 공고 -->",
                                                         "회원 5만 명의 불편을 줄이는 일을 하고 싶습니다. <!-- 조사 -->"))
        self.assertIn("number_not_in_research", codes(r, "error"))
        self.assertNotIn("research_none_cited", codes(r))

    def test_other_company(self):
        self.hit("other_company", draft=replace(DRAFT, "주문·배송 경험 개선을 주요 업무로 둔 가상커머스에서",
                                                "주문·배송 경험 개선을 주요 업무로 둔 가상물류에서"))
        name = DATA["companies"][0]
        r = run_check(draft=replace(DRAFT, "짧은 설문을 돌렸습니다.", f"{name}로 짧은 설문을 돌렸습니다."))
        self.assertIn("other_company", codes(r, "warn"))
        self.assertNotIn("other_company", codes(r, "error"))

    def test_style(self):
        self.hit("style_banned", "warn", draft=replace(DRAFT, "하고 싶습니다.", "열정으로 하고 싶습니다."))
        self.hit("style_replace", "warn", draft=replace(DRAFT, "고객 경험을 바꾼다", "고객님 경험을 바꾼다"))
        self.hit("style_tone", "warn", draft=replace(DRAFT, "만들었습니다. <!-- E01 행동 -->", "만들었다. <!-- E01 행동 -->"))
        self.hit("style_length", "warn", draft=replace(DRAFT, "도입 전입니다.", "도입 전입니다" + "만" * 80 + "."))

    def test_terms(self):
        self.hit("term_confused", "warn", draft=replace(DRAFT, "도입 전입니다. <!-- 의견 -->",
                                                        "도입 전입니다. <!-- 의견 -->\n전환율(클릭률)도 함께 보겠습니다. <!-- 의견 -->"))
        ok = run_check(draft=replace(DRAFT, "도입 전입니다. <!-- 의견 -->",
                                     "도입 전입니다. <!-- 의견 -->\n전환율(구매까지 간 비율)도 함께 보겠습니다. <!-- 의견 -->"))
        self.assertNotIn("term_confused", codes(ok))

    def test_meta_and_length(self):
        self.hit("draft_meta", draft=replace(DRAFT, "- 회사: 가상커머스\n", ""))
        self.hit("question_meta", draft=replace(DRAFT, "- 유형: 경험형", "- 유형: 아무형"))
        self.hit("question_meta", draft=replace(DRAFT, "- 판: v1 · 첫 판\n", ""))
        self.hit("length_over", draft=replace(DRAFT, "500자(공백 포함)", "400자(공백 포함)"))
        self.hit("length_short", draft=replace(DRAFT, "500자(공백 포함)", "600자(공백 포함)"))
        self.hit("no_limit", "warn", draft=replace(DRAFT, "500자(공백 포함)", "없음"))
        r = run_check(draft=replace(DRAFT, "500자(공백 포함)", "360자(공백 제외)"))
        self.assertEqual((r["questions"][0]["basis"], r["questions"][0]["fit"]), ("without_spaces", "ok"))
        r = run_check(draft=replace(DRAFT, "500자(공백 포함)", "1200바이트"))
        self.assertEqual((r["questions"][0]["basis"], r["questions"][0]["fit"]), ("bytes", "ok"))
        self.hit("ledger_empty", ledger="")

    def test_comments(self):
        self.hit("placeholder", draft=replace(DRAFT, "도입 전입니다. <!-- 의견 -->",
                                              "도입 전입니다. <!-- 의견 -->\n[사용자 확인 필요: 협업 경험] <!-- 의견 -->"))
        self.hit("unknown_tag", "warn", draft=replace(DRAFT, "<!-- E01 상황 -->", "<!-- E01 메모 -->"))
        self.hit("unknown_id", draft=replace(DRAFT, "<!-- E01 상황 -->", "<!-- E09 상황 -->"))
        self.hit("no_id", draft=replace(DRAFT, "짧은 설문을 돌렸습니다. <!-- E01 행동 -->", "짧은 설문을 돌렸습니다."))
        self.hit("para_abstract", "warn", draft=replace(DRAFT, "줄이는 기획이 고객 경험을 바꾼다는 것을 배웠습니다.",
                                                        "줄이는 기획으로 큰 성과를 냈다고 배웠습니다."))
        # 의견·포부 문장은 근거 ID 없이도 됩니다.
        self.assertNotIn("no_id", codes(run_check(draft=replace(DRAFT, "하는 기획자가 되겠습니다. <!-- 연결 -->",
                                                                     "하는 기획자가 되겠습니다."))))

    def test_short_fields(self):
        self.hit("short_no_id", draft=replace(DRAFT, "| 가상리빙 <!-- E02 --> |", "| 가상리빙 |"))
        self.hit("length_over", draft=replace(DRAFT, "| 인턴 회사명 | 10자 |", "| 인턴 회사명 | 3자 |"))

    def test_between_questions(self):
        extra = "\n예약 기록을 시간대별로 나눠 동아리 스터디룸의 주간 좌석 노쇼율을 18%에서 11%로 낮췄습니다. <!-- E01 결과 -->"
        r = self.hit("dup_experience", "warn", draft=replace(DRAFT, "문의 2,400건을 7개 유형으로 나눴습니다. <!-- E02 -->",
                                                             "문의 2,400건을 7개 유형으로 나눴습니다. <!-- E02 -->" + extra))
        self.assertIn("dup_number", codes(r, "warn"))
        self.assertIn("dup_sentence", codes(r, "warn"))

    def test_coverage(self):
        self.hit("no_analysis", "warn", analysis="")
        self.hit("coverage_unknown", "warn", draft=replace(DRAFT, "- 연결: 고객 이해", "- 연결: 고객 이해, 없는 역량"))
        r = run_check(draft=replace(DRAFT, "- 연결: 고객 이해", "- 연결: 고객 이해, SQL"))
        self.assertNotIn("coverage_missing", codes(r))

    def test_confirmed_question_protected(self):
        changed = replace(DRAFT, "이 일로 주문 뒤의", "이 일로 저는 주문 뒤의")
        self.hit("confirmed_changed", draft=changed, previous=DRAFT)
        self.hit("confirmed_changed", draft=replace(DRAFT, "가상커머스에 지원한 이유", "가상커머스를 고른 이유"), previous=DRAFT)
        self.hit("confirmed_changed", draft=replace(DRAFT, "- 상태: 확정\n- 연결: 고객 이해", "- 상태: 작성 중\n- 연결: 고객 이해"),
                 previous=DRAFT)
        self.assertNotIn("confirmed_changed", codes(run_check(previous=DRAFT)))
        # 이전 판에서 작성 중이던 문항은 고쳐도 됩니다.
        before = replace(DRAFT, "- 상태: 확정\n- 연결: 고객 이해", "- 상태: 작성 중\n- 연결: 고객 이해")
        self.assertNotIn("confirmed_changed", codes(run_check(draft=changed, previous=before)))


class ParagraphRuleTest(unittest.TestCase):
    """경험 문단 원칙: STAR 표시, 상황 길이, 팀 성과만 쓴 문단, 판단 이유, 직무 연결."""

    def check(self, body):
        return codes(core.check(MINI.format(body=body), LEDGER, "", "", "", [], DATA))

    def test_good_paragraph(self):
        found = self.check("동아리 예약 노쇼가 잦았습니다. <!-- E01 상황 -->\n"
                           "원인을 알기 위해 저는 예약 시트 12주치를 시간대별로 나눴습니다. <!-- E01 행동 -->\n"
                           "이 경험을 살려 기획 직무에서 원인부터 확인하겠습니다. <!-- 연결 -->")
        self.assertFalse(found & {"para_no_star", "para_situation_long", "para_team_only", "para_no_reason", "para_no_link"})

    def test_bad_paragraphs(self):
        self.assertIn("para_no_star", self.check("예약 시트 12주치를 시간대별로 나눴습니다. <!-- E01 -->"))
        found = self.check("동아리 스터디룸 예약에서 노쇼가 아주 잦아서 빈 좌석이 남는 일이 매주 되풀이되었고 운영진도 늘 곤란해했습니다. <!-- E01 상황 -->\n"
                           "예약 시트 12주치를 나눴습니다. <!-- E01 행동 -->\n"
                           "동아리는 노쇼율을 18%에서 11%로 낮췄습니다. <!-- E01 결과 -->")
        self.assertTrue({"para_situation_long", "para_team_only", "para_no_reason", "para_no_link"} <= found, found)


class LedgerRuleTest(unittest.TestCase):
    def test_ledger_errors(self):
        for code, ledger in [
            ("ledger_dup_id", LEDGER.replace("## E02.", "## E01.")),
            ("ledger_action_tag", replace(LEDGER, "[한 일] 회원 30명", "[했음] 회원 30명")),
            ("ledger_metric", replace(LEDGER, "| 출처: 동아리 예약 시트", "")),
            ("ledger_field", replace(LEDGER, "- 판단 이유: 노쇼가", "- 메모: 노쇼가")),
            ("ledger_empty", "# 경험 장부\n"),
        ]:
            report = core.ledger_report(ledger)
            self.assertIn(code, {i["code"] for i in report["issues"]}, (code, report["issues"]))
            self.assertGreater(report["summary"]["errors"], 0, code)

    def test_unconfirmed_fields_listed(self):
        ledger = replace(LEDGER, "- 결과: 알림 규칙을", "- 결과: (AI 정리, 확인 전) 알림 규칙을")
        rows = core.ledger_report(ledger)["experiences"]
        self.assertEqual(rows[0]["unconfirmed"], ["결과"])
        self.assertEqual(rows[0]["actions"], {"한 일": 3, "설계안(도입 가정)": 1, "계획": 0})


class PostingTest(unittest.TestCase):
    """공고 읽기 실패·이미지 확인 전·회사 조사 없음·사전에 없는 용어를 따로 표시합니다."""

    def flags(self, posting, analysis=""):
        return core.check_analysis(posting, analysis, DATA)

    def test_blocked_postings(self):
        r = self.flags("")
        self.assertTrue(r["blocked"] and r["flags"]["posting_failed"])
        r = self.flags(replace(POSTING, "- 상태: 확인함", "- 상태: 읽기 실패(로그인 필요)"))
        self.assertTrue(r["blocked"] and r["flags"]["posting_failed"])
        self.assertIn("posting_failed", codes(r))
        image = replace(POSTING, "- 상태: 확인함", f"- 상태: {core.IMAGE_MARK}\n- 원본 이미지: cap.png")
        r = self.flags(image)
        self.assertTrue(r["blocked"] and r["flags"]["image_unconfirmed"])
        self.assertFalse(r["flags"]["posting_failed"])
        r = self.flags(POSTING.split("## 원문")[0] + "## 원문\n\n")
        self.assertTrue(r["blocked"])
        self.assertIn("posting_empty", codes(r))

    def test_posting_meta(self):
        self.assertIn("posting_source", codes(self.flags(replace(POSTING, "- 출처: 붙여넣기\n", ""))))
        self.assertIn("posting_date", codes(self.flags(replace(POSTING, "- 확인 날짜: 2026-10-17", "- 확인 날짜: 어제"))))

    def test_analysis_rules(self):
        r = self.flags(POSTING, replace(ANALYSIS, "## 숨은 키워드 (AI 해석)", "## 숨은 키워드"))
        self.assertIn("keyword_not_marked", codes(r))
        r = self.flags(POSTING, replace(ANALYSIS, "| 퍼널 | 단계별 이탈을 보는 흐름 |", "| 없는말 | 지어낸 뜻 |"))
        self.assertIn("term_not_in_dictionary", codes(r))
        r = self.flags(POSTING, replace(ANALYSIS, "- 조사 안 됨", "- 회원 3만 명 규모입니다."))
        self.assertIn("research_no_source", codes(r))
        self.assertFalse(r["flags"]["research_none"])
        r = self.flags(POSTING, replace(ANALYSIS, "## 용어", "## 낱말"))
        self.assertIn("analysis_section", codes(r))

    def test_match_terms(self):
        found = core.match_terms(core.parse_posting(POSTING)["body"], DATA)
        self.assertEqual([t["term"] for t in found], ["퍼널", "전환율", "SQL"])

    def test_cli_terms_refuses_image_posting(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "posting.md"
            path.write_text(replace(POSTING, "- 상태: 확인함", f"- 상태: {core.IMAGE_MARK}"), encoding="utf-8")
            code, _, err = run_cli("terms", str(path))
            self.assertEqual(code, 2)
            self.assertIn("확인한 공고만", err)


class SubmissionTest(unittest.TestCase):
    def test_submission_strips_comments(self):
        text = core.submission(DRAFT)
        self.assertNotIn("<!--", text)
        self.assertNotIn("- 판:", text)
        self.assertIn("예약 기록을 시간대별로 나눠", text)


class PrivacyTest(unittest.TestCase):
    def test_scan(self):
        found = store.scan("가상 900101-1234567\n전화 010-1234-5678, 메일 a.b@example.com\n2026-10-17 10:30")
        self.assertEqual([(f["line"], f["kind"]) for f in found], [(1, "주민등록번호"), (2, "전화번호"), (2, "이메일")])
        self.assertEqual(found[0]["masked"], "900" + "*" * 11)
        self.assertEqual(store.scan("문의 2,400건, 2025-03 ~ 2025-08, 12345678901234"), [])


def run_cli(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class Home(unittest.TestCase):
    """임시 지원 폴더(예시 복사본)와 임시 19번 면접 폴더."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.home, self.interview = root / "apply", root / "interview"
        shutil.copytree(EXAMPLES, self.home)
        self.old = {k: os.environ.get(k) for k in (store.HOME_ENV, store.INTERVIEW_ENV)}
        os.environ[store.HOME_ENV] = str(self.home)
        os.environ[store.INTERVIEW_ENV] = str(self.interview)
        self.draft = self.home / "가상커머스" / "draft-2026-10-17.md"

    def tearDown(self):
        for k, v in self.old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        self.tmp.cleanup()


class StoreCliTest(Home):
    def test_cli_exit_codes(self):
        code, out, _ = run_cli("check", str(self.draft))
        self.assertEqual(code, 0)
        self.assertIn("## 글자 수", out)
        code, out, _ = run_cli("check", str(self.draft), "--json")
        self.assertEqual(json.loads(out)["summary"]["errors"], 0)
        bad = self.home / "가상커머스" / "draft-2026-10-18.md"
        bad.write_text(replace(DRAFT, "18%에서 11%로", "18%에서 9%로"), encoding="utf-8")
        self.assertEqual(run_cli("check", str(bad))[0], 2)
        self.assertEqual(run_cli("check", str(bad), "--previous", str(self.draft))[0], 2)
        self.assertEqual(run_cli("ledger")[0], 0)
        self.assertEqual(run_cli("analysis", "가상커머스")[0], 0)
        (self.home / "가상커머스" / "posting.md").write_text("", encoding="utf-8")
        self.assertEqual(run_cli("analysis", "가상커머스")[0], 2)
        self.assertEqual(run_cli("privacy", str(self.home / "ledger.md"))[0], 0)
        leak = self.home / "leak.md"
        leak.write_text("010-1234-5678\n", encoding="utf-8")
        self.assertEqual(run_cli("privacy", str(leak))[0], 2)
        self.assertEqual(run_cli("check", str(self.home / "없음.md"))[0], 2)
        code, out, _ = run_cli("diff", str(self.draft), str(bad))
        self.assertIn("+예약 기록을 시간대별로 나눠 동아리 스터디룸의 주간 좌석 노쇼율을 18%에서 9%로", out)

    def test_where_and_init(self):
        code, out, _ = run_cli("where")
        info = json.loads(out)
        self.assertEqual((info["home"], info["companies"]), (str(self.home.resolve()), ["가상커머스"]))
        fresh = Path(self.tmp.name) / "fresh"
        made = store.init(fresh)
        self.assertEqual(sorted(Path(p).name for p in made["made"]), ["ledger.md", "style.md"])
        self.assertEqual(store.init(fresh)["made"], [])  # 이미 있으면 건드리지 않습니다.
        self.assertEqual(read(fresh / "ledger.md"), store.TEMPLATES["ledger.md"])

    def test_templates(self):
        data = json.loads(read(HERE / "data" / "templates.json"))
        self.assertEqual(data, store.TEMPLATES)
        self.assertEqual(sorted(data), ["ledger.md", "style.md"])
        self.assertEqual(core.ledger_report(data["ledger.md"])["summary"]["experiences"], 1)
        self.assertEqual(store.scan(data["ledger.md"] + data["style.md"]), [])

    def test_git_warning(self):
        self.assertEqual(store.git_warning(self.home), "")
        (self.home / ".git").mkdir()
        self.assertIn("git 저장소", store.git_warning(self.home / "가상커머스"))

    def test_new_draft_never_overwrites(self):
        first = store.new_draft_path("가상커머스", "2026-10-17")
        self.assertEqual(first.name, "draft-2026-10-17-2.md")
        first.write_text("x", encoding="utf-8")
        self.assertEqual(store.new_draft_path("가상커머스", "2026-10-17").name, "draft-2026-10-17-3.md")
        self.assertEqual(store.new_draft_path("가상커머스", "2026-10-18").name, "draft-2026-10-18.md")

    def test_submit_never_overwrites(self):
        dry = store.submit(self.draft, dry_run=True, date="2026-10-17")
        self.assertFalse(dry["saved"])
        self.assertFalse((self.interview / "서류").exists())
        first = store.submit(self.draft, date="2026-10-17")
        self.assertEqual([Path(f["path"]).name for f in first["files"]], ["자기소개서-가상커머스.md", "공고-가상커머스.md"])
        letter = self.interview / "서류" / "자기소개서-가상커머스.md"
        letter.write_text("사용자가 고친 글", encoding="utf-8")
        second = store.submit(self.draft, date="2026-10-17")
        self.assertEqual([Path(f["path"]).name for f in second["files"]],
                         ["자기소개서-가상커머스-2026-10-17.md", "공고-가상커머스-2026-10-17.md"])
        third = store.submit(self.draft, date="2026-10-17")
        self.assertEqual(Path(third["files"][0]["path"]).name, "자기소개서-가상커머스-2026-10-17-2.md")
        self.assertEqual(read(letter), "사용자가 고친 글")
        self.assertNotIn("<!--", read(Path(second["files"][0]["path"])))

    def test_submit_refuses(self):
        work = self.home / "가상커머스" / "draft-2026-10-18.md"
        work.write_text(replace(DRAFT, "- 상태: 확정", "- 상태: 작성 중"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "확정"):
            store.submit(work)
        work.write_text(replace(DRAFT, "18%에서 11%로", "18%에서 9%로"), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "오류"):
            store.submit(work)
        self.assertEqual(run_cli("submit", str(work))[0], 2)
        # 이미지 공고를 확인하지 않았으면 공고는 넘기지 않습니다.
        posting = self.home / "가상커머스" / "posting.md"
        posting.write_text(replace(POSTING, "- 상태: 확인함", f"- 상태: {core.IMAGE_MARK}"), encoding="utf-8")
        files = store.submit(self.draft, dry_run=True)["files"]
        self.assertEqual([f["kind"] for f in files], ["자기소개서"])


class TermsTest(unittest.TestCase):
    def test_lite_matches_dictionary(self):
        if not (DICTIONARY / "terms.json").is_file():
            self.skipTest("17번 사전 원본이 없습니다.")
        built = terms.build(DICTIONARY / "terms.json", DICTIONARY / "catalog.json")
        self.assertEqual(terms.dump(built), (HERE / "data" / "terms-lite.json").read_text(encoding="utf-8"),
                         "data/terms-lite.json이 17번 사전과 다릅니다. saerok_apply.terms로 다시 만들어 주세요.")


def run_node(script: str, data) -> dict:
    r = subprocess.run([NODE, "-e", script, str(CORE_JS)], input=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                       capture_output=True, timeout=60)
    if r.returncode:
        raise AssertionError(r.stderr.decode("utf-8", "replace"))
    return json.loads(r.stdout.decode("utf-8"))


@unittest.skipUnless(NODE, "node가 없어 web/apply-core.js 비교를 건너뜁니다.")
class WebCoreTest(unittest.TestCase):
    """web/apply-core.js가 saerok_apply.core와 같은 결과를 내는지 봅니다."""

    SCRIPT = r'''
const A = require(process.argv[1]); let d = "";
process.stdin.on("data", (c) => d += c).on("end", () => {
  const cases = JSON.parse(d);
  console.log(JSON.stringify(cases.map((a) => ({
    check: A.check(a.draft, a.ledger, a.analysis, a.posting, a.style, a.companies, a.terms, a.previous),
    ledger: A.ledgerReport(a.ledger), analysis: A.checkAnalysis(a.posting, a.analysis, a.terms),
    submission: A.submission(a.draft), terms: A.matchTerms(a.posting, a.terms), scan: A.scan(a.draft + "\n" + a.ledger),
    count: A.count(a.draft), guess: A.guessType(a.draft.split("\n").find((l) => l.startsWith("## 문항")) || "") }))));
});'''

    def cases(self):
        base = dict(draft=DRAFT, ledger=LEDGER, analysis=ANALYSIS, posting=POSTING, style=STYLE, companies=COMPANIES,
                    terms=DATA, previous=DRAFT)
        variants = [
            {},
            {"draft": replace(DRAFT, "18%에서 11%로", "2024년 회원당 18%에서 9%로"), "previous": ""},
            {"draft": replace(DRAFT, "가상커머스에 지원한 이유", "가상물류를 고른 이유")},
            {"draft": replace(DRAFT, "대기 예약 기능도 설계해 두었지만 아직 도입 전입니다. <!-- 의견 -->",
                              "노쇼가 잦은 시간대에 대기 예약을 받는 기능을 만들었습니다. <!-- E01 행동 -->\n"
                              "전환율(클릭률)도 열정으로 봤다. <!-- 메모 -->\n[사용자 확인 필요: 협업]")},
            {"draft": replace(DRAFT, "| 가상리빙 <!-- E02 --> |", "| 가상리빙 010-1234-5678 |"),
             "ledger": replace(LEDGER, "- 결과: 알림 규칙을", "- 결과: (AI 정리, 확인 전) 알림 규칙을")},
            {"draft": MINI.format(body="동아리는 노쇼율을 18%에서 11%로 낮췄습니다. <!-- E01 결과 -->"), "analysis": "", "style": ""},
            {"posting": replace(POSTING, "- 상태: 확인함", f"- 상태: {core.IMAGE_MARK}"), "ledger": ""},
            {"draft": replace(DRAFT, "500자(공백 포함)", "1200바이트"), "analysis": replace(ANALYSIS, "- 조사 안 됨",
                                                                                         "- 회원 3만 명 규모입니다.")},
        ]
        return [{**base, **v} for v in variants]

    def python(self, a):
        body = core.parse_posting(a["posting"])["body"] if False else a["posting"]
        heading = next((l for l in a["draft"].split("\n") if l.startswith("## 문항")), "")
        out = {"check": core.check(a["draft"], a["ledger"], a["analysis"], a["posting"], a["style"], a["companies"],
                                   a["terms"], a["previous"]),
               "ledger": core.ledger_report(a["ledger"]), "analysis": core.check_analysis(a["posting"], a["analysis"], a["terms"]),
               "submission": core.submission(a["draft"]), "terms": core.match_terms(body, a["terms"]),
               "scan": store.scan(a["draft"] + "\n" + a["ledger"]), "count": core.count(a["draft"]),
               "guess": core.guess_type(heading)}
        return json.loads(json.dumps(out, ensure_ascii=False))

    def test_same_results(self):
        cases = self.cases()
        js = run_node(self.SCRIPT, cases)
        for n, (a, got) in enumerate(zip(cases, js)):
            want = self.python(a)
            for key in want:
                self.assertEqual(got[key], want[key], f"사례 {n}의 {key}가 다릅니다.")

    def test_variants_are_not_trivial(self):
        results = [self.python(a)["check"]["summary"]["errors"] for a in self.cases()]
        self.assertEqual(results[0], 0)
        self.assertTrue(all(e > 0 for e in results[1:5]), results)


class WebServerTest(Home):
    """`saerok-apply`가 여는 내 PC 서버. 임시 지원 폴더와 빈 포트에서만 돌립니다."""

    def setUp(self):
        super().setUp()
        self.old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        self.old_keyring, web.keystore.keyring = web.keystore.keyring, None  # 실제 자격 증명 관리자는 건드리지 않음
        self.old_cli, self.old_call = subscription.cli, subscription.call
        web.ENGINE["now"] = "api"  # 검사에서는 실제 Claude Code·Anthropic을 부르지 않음
        self.server = web.make_server(0)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        web.keystore.keyring = self.old_keyring
        subscription.cli, subscription.call = self.old_cli, self.old_call
        web.ENGINE["now"] = None
        web.keystore._memory.clear()
        if self.old_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = self.old_key
        super().tearDown()

    def call(self, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        send = {"Host": f"127.0.0.1:{self.port}", web.API_HEADER: "1", "Content-Type": "application/json"}
        send.update(headers or {})
        payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
        conn.request("GET" if body is None else "POST", path, body=payload, headers=send)
        response = conn.getresponse()
        raw = response.read()
        conn.close()
        try:
            return response.status, json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return response.status, raw.decode("utf-8")

    def test_page_and_info(self):
        status, page = self.call("/")
        self.assertEqual(status, 200)
        self.assertIn("apply-core.js", page)
        self.assertEqual(self.call("/app.js")[0], 200)
        self.assertEqual(self.call("/data/terms-lite.json")[1], DATA)
        self.assertEqual(self.call("/data/templates.json")[1], store.TEMPLATES)
        status, info = self.call("/api/info")
        self.assertEqual((status, info["mode"], info["home"], info["companies"], info["key"]),
                         (200, "local", str(store.home()), ["가상커머스"], "등록 안 됨"))

    def test_guards(self):
        self.assertEqual(self.call("/api/info", headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.call("/", headers={"Host": f"evil.example:{self.port}"})[0], 403)
        self.assertEqual(self.call("/api/info", headers={web.API_HEADER: "0"})[0], 403)
        self.assertEqual(self.call("/api/info", headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.call("/api/file", {"name": "ledger.md", "text": "x"},
                                   headers={"Origin": "https://evil.example"})[0], 403)
        for path in ["/../saerok_apply/web.py", "/%2e%2e/saerok_apply/web.py", "/data/../saerok_apply/core.py",
                     "/data/%2e%2e/pyproject.toml"]:
            self.assertEqual(self.call(path)[0], 404, path)

    def test_file_allow_list(self):
        self.assertEqual(web.file_path("", "ledger.md"), store.home() / "ledger.md")
        self.assertEqual(web.file_path("가상커머스", "draft-2026-10-17.md").name, "draft-2026-10-17.md")
        for company, name, writing in [("", "../x.md", False), ("", "draft-2026-10-17.md", False),
                                       ("가상커머스", "draft-2026-10-17.md", True), ("가상커머스", "../ledger.md", False),
                                       ("가상커머스", "notes.md", False), ("", "posting.md", False)]:
            with self.assertRaises(ValueError, msg=(company, name, writing)):
                web.file_path(company, name, writing)
        self.assertEqual(web.file_path("../../밖", "posting.md").parent.parent, store.home())
        status, j = self.call("/api/file?company=&name=..%2Fx.md")
        self.assertEqual(status, 400)
        status, _ = self.call("/api/file", {"company": "가상커머스", "name": "draft-2026-10-17.md", "text": "덮어쓰기"})
        self.assertEqual(status, 400)
        self.assertEqual(read(self.draft), DRAFT)

    def test_full_flow(self):
        status, j = self.call("/api/file?" + "company=%EA%B0%80%EC%83%81%EC%BB%A4%EB%A8%B8%EC%8A%A4&name=posting.md")
        self.assertEqual((status, j["text"]), (200, POSTING))
        status, j = self.call("/api/file", {"name": "ledger.md", "text": LEDGER + "\n연락처 010-1234-5678\n"})
        self.assertEqual((status, [p["kind"] for p in j["privacy"]]), (200, ["전화번호"]))
        self.assertEqual(self.call("/api/drafts?company=%EA%B0%80%EC%83%81%EC%BB%A4%EB%A8%B8%EC%8A%A4")[1],
                         ["draft-2026-10-17.md"])
        names = [self.call("/api/draft/new", {"company": "가상커머스", "text": DRAFT})[1]["name"] for _ in range(2)]
        self.assertEqual(len(set(names)), 2)
        self.assertNotIn("draft-2026-10-17.md", names)
        status, r = self.call("/api/check", {"company": "가상커머스", "draft": "draft-2026-10-17.md",
                                             "previous": "draft-2026-10-17.md"})
        self.assertEqual((status, r["summary"]["errors"]), (200, 0))
        self.call("/api/file", {"name": "ledger.md", "text": LEDGER})
        status, r = self.call("/api/check", {"company": "가상커머스", "draft": "draft-2026-10-17.md"})
        self.assertEqual((status, r["summary"]["submittable"]), (200, True))
        self.assertEqual(self.call("/api/check", {"company": "가상커머스", "draft": "posting.md"})[0], 400)
        status, dry = self.call("/api/submit", {"company": "가상커머스", "draft": "draft-2026-10-17.md", "dry_run": True})
        self.assertEqual((status, dry["saved"]), (200, False))
        self.assertFalse((self.interview / "서류").exists())
        first = self.call("/api/submit", {"company": "가상커머스", "draft": "draft-2026-10-17.md"})[1]
        second = self.call("/api/submit", {"company": "가상커머스", "draft": "draft-2026-10-17.md"})[1]
        self.assertNotEqual(first["files"][0]["path"], second["files"][0]["path"])
        self.assertEqual(self.call("/api/submit", {"company": "가상커머스", "draft": "analysis.md"})[0], 400)

    def test_claude_routes(self):
        image = {"model": "m", "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": "AA=="}}]}]}
        status, j = self.call("/api/claude", image)
        self.assertEqual(status, 401)  # API 키 방식인데 키가 없음
        subscription.cli = lambda: "claude"
        subscription.call = lambda body: {"content": [{"type": "text", "text": "옮긴 글"}]}
        self.assertEqual(self.call("/api/engine", {"engine": "subscription"})[1], {"engine": "subscription"})
        status, j = self.call("/api/claude", image)
        self.assertEqual(status, 400)
        self.assertIn("이미지", j["error"])
        status, j = self.call("/api/claude", {"model": "m", "messages": [{"role": "user", "content": "글"}]})
        self.assertEqual((status, j["content"][0]["text"]), (200, "옮긴 글"))
        self.assertEqual(self.call("/api/engine", {"engine": "other"})[0], 400)

    def test_key_roundtrip(self):
        status, j = self.call("/api/key", {"key": "sk-ant-test-0000000000"})
        self.assertEqual(status, 200)
        self.assertNotIn("0000000000", json.dumps(j))
        self.assertEqual(self.call("/api/key/delete", {})[1]["key"], "등록 안 됨")


if __name__ == "__main__":
    unittest.main()
