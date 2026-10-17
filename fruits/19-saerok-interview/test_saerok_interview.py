"""새록 면접관(19번 열매) 결정적 계층 검사. 실제 기록은 임시 면접 폴더에만 만듭니다."""

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from saerok_interview import cli, compare, rubric, session, store, terms

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"
DICTIONARY = HERE.parent / "17-saerok-dictionary" / "data"


def doc_result(who: str, *, line: int = 12, quote: str = "전환율을 30% 올렸습니다") -> dict:
    """그 면접관의 항목 앞 두 개로 질문 2개, 점수는 모두 배점의 절반(내림)."""
    specs = rubric.INTERVIEWERS[who]["items"]
    return {
        "interviewer": who,
        "questions": [
            {"question": f"{who} 질문 {n}", "item": specs[n]["key"],
             "evidence": [{"doc": "resume_letter", "line": line, "quote": quote}], "direction": "방향"}
            for n in range(2)
        ],
        "items": {s["key"]: s["max"] // 2 for s in specs},
        "na": {},
        "comment": "한 줄 평",
        "fixes": ["고칠 점"],
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "interviews"
        self.old = os.environ.get(session.HOME_ENV)
        os.environ[session.HOME_ENV] = str(self.home)

    def tearDown(self):
        if self.old is None:
            os.environ.pop(session.HOME_ENV, None)
        else:
            os.environ[session.HOME_ENV] = self.old
        self.tmp.cleanup()

    def new(self, posting=True, **kw) -> Path:
        files = {"resume_letter": EXAMPLES / "resume-letter.md"}
        if posting:
            files["posting"] = EXAMPLES / "posting.md"
        return Path(session.create(files, company="골목장터", **kw)["folder"])


class SessionTest(Base):
    def test_create_copies_inputs_and_empty_score(self):
        folder = self.new(date="2026-10-17")
        self.assertEqual(folder.name, "2026-10-17-골목장터")
        meta, score = session.load(folder)
        self.assertTrue(meta["posting"])
        self.assertEqual(set(meta["inputs"]), {"resume_letter", "posting"})
        self.assertTrue((folder / "inputs" / "자기소개서.md").is_file())
        self.assertEqual(score, {"version": 1, "document": {}, "answers": [], "real": []})
        self.assertEqual(self.new(date="2026-10-17").name, "2026-10-17-골목장터-2")

    def test_refuses_inside_git(self):
        repo = Path(self.tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True)
        with self.assertRaises(ValueError):
            session.create({"resume_letter": EXAMPLES / "resume-letter.md"}, base=repo / "interviews")

    def test_needs_resume_letter_and_text_files(self):
        with self.assertRaises(ValueError):
            session.create({"posting": EXAMPLES / "posting.md"})
        pdf = Path(self.tmp.name) / "a.pdf"
        pdf.write_text("x", encoding="utf-8")
        with self.assertRaises(ValueError):
            session.create({"resume_letter": pdf})

    def test_scan_masks_personal_data(self):
        found = session.scan("연락처 010-1234-5678\n메일 someone@example.com\n주민 900101-1234567")
        self.assertEqual([f["kind"] for f in found], ["전화번호", "이메일", "주민등록번호"])
        self.assertTrue(all(f["masked"].endswith("*") and "5678" not in f["masked"] for f in found))
        self.assertEqual(session.scan((EXAMPLES / "resume-letter.md").read_text(encoding="utf-8")), [])


class RubricTest(unittest.TestCase):
    def test_each_interviewer_totals_ten(self):
        for who in rubric.ORDER:
            self.assertEqual(sum(i["max"] for i in rubric.INTERVIEWERS[who]["items"]), 10, who)

    def test_total10_skips_not_applicable(self):
        self.assertEqual(rubric.total10("pressure", {"evidence": 3, "role": 3, "consistency": 2, "composure": None}), 10.0)
        self.assertEqual(rubric.total10("pressure", {"evidence": 0, "role": 0, "consistency": 0, "composure": None}), 0.0)
        self.assertIsNone(rubric.total10("pressure", {k: None for k in ("evidence", "role", "consistency", "composure")}))
        self.assertEqual(rubric.verdict(7.0), "합격권")
        self.assertEqual(rubric.verdict(None), "판단 보류")

    def test_agents_match_rubric(self):
        for who in rubric.ORDER:
            text = (HERE / "agents" / f"{who}.md").read_text(encoding="utf-8")
            self.assertIn(f"name: {who}", text)
            self.assertIn("model: sonnet", text)
            for spec in rubric.INTERVIEWERS[who]["items"]:
                self.assertIn(f"`{spec['key']}`", text, (who, spec["key"]))


class RecordTest(Base):
    def test_document_grounded_and_auto_na(self):
        folder = self.new(posting=False)
        doc = store.record_document(folder, doc_result("pressure"))
        self.assertTrue(all(q["grounded"] for q in doc["questions"]))
        self.assertIsNone(doc["items"]["composure"])  # 답변에서만 봄
        out = store.record_document(folder, doc_result("executive"))
        self.assertIsNone(out["items"]["company"])  # 공고 없음

    def test_document_marks_invented_quote(self):
        folder = self.new()
        doc = store.record_document(folder, doc_result("hr", quote="없는 문장을 지어냈습니다"))
        self.assertFalse(any(q["grounded"] for q in doc["questions"]))
        self.assertEqual(doc["questions"][0]["evidence"][0]["status"], "확인 안 됨")

    def test_document_rejects_bad_shape(self):
        folder = self.new()
        bad = doc_result("hr")
        bad["questions"] = bad["questions"][:1]
        with self.assertRaises(ValueError):
            store.record_document(folder, bad)
        bad = doc_result("hr")
        bad["items"]["motivation"] = 4
        with self.assertRaises(ValueError):
            store.record_document(folder, bad)
        bad = doc_result("hr")
        bad["questions"][0]["item"] = "evidence"
        with self.assertRaises(ValueError):
            store.record_document(folder, bad)

    def test_example_result_records(self):
        folder = self.new()
        result = json.loads((EXAMPLES / "pressure-result.json").read_text(encoding="utf-8"))
        doc = store.record_document(folder, result)
        self.assertTrue(all(q["grounded"] for q in doc["questions"]))

    def test_report_next_and_answers(self):
        folder = self.new()
        for who in rubric.ORDER:
            r = doc_result(who)
            if who == "numbers":
                r["items"] = {s["key"]: 0 for s in rubric.INTERVIEWERS[who]["items"]}
            store.record_document(folder, r)
        report = (Path(store.write_report(folder))).read_text(encoding="utf-8")
        self.assertIn("## 판정표", report)
        self.assertIn("## 질문 10개", report)
        self.assertIn("Q10", report)
        nxt = store.next_question(folder)
        self.assertEqual((nxt["interviewer"], nxt["no"]), ("numbers", 9))  # 서류 점수가 가장 낮은 면접관부터
        self.assertEqual(store.next_question(folder, ["hr"])["no"], 3)
        answer = {"no": 9, "interviewer": "numbers", "level": "매운맛", "question": "q", "answer": "a",
                  "items": {"source": 3, "calculation": 3, "definition": 2, "baseline": 2}}
        self.assertEqual(store.record_answer(folder, answer)["total"], 10.0)
        self.assertEqual(store.next_question(folder)["no"], 10)
        self.assertTrue((folder / "practice.md").is_file())
        with self.assertRaises(ValueError):
            store.record_answer(folder, {**answer, "level": "아주매운맛"})
        with self.assertRaises(ValueError):
            store.record_answer(folder, {**answer, "followups": [{}, {}, {}]})

    def test_real_counts_only_confirmed(self):
        folder = self.new()
        store.record_document(folder, doc_result("pressure"))
        store.record_real(folder, {"questions": [
            {"question": "본인 역할은?", "matched": 1, "confirmed": True},
            {"question": "왜 우리 회사?", "matched": None, "confirmed": True},
        ]})
        with self.assertRaises(ValueError):
            store.record_real(folder, {"questions": [{"question": "x", "matched": 7}]})
        result = compare.compare([session.load(folder)])
        self.assertEqual(result["hit"], {"real_questions": 2, "confirmed": 1, "rate": 50})


class CompareTest(Base):
    def session_with(self, date, total_items):
        folder = self.new(date=date)
        store.record_document(folder, doc_result("hr"))
        store.record_answer(folder, {"no": 1, "interviewer": "hr", "question": "q", "answer": "a", "items": total_items})
        return folder

    def test_change_goal_and_weak_items(self):
        low = {"motivation": 0, "collaboration": 1, "fit": 1, "tenure": 1}
        high = {"motivation": 3, "collaboration": 3, "fit": 2, "tenure": 1}
        folders = [self.session_with("2026-10-01", low), self.session_with("2026-10-08", low)]
        two = compare.compare([session.load(f) for f in folders])
        self.assertIsNone(two["change"]["goal"])  # 3회부터 판단
        folders.append(self.session_with("2026-10-15", high))
        result = compare.compare([session.load(f) for f in folders])
        self.assertEqual(result["change"]["diff"], 6.0)
        self.assertTrue(result["change"]["goal"])
        self.assertIn("motivation", [w["item"] for w in result["weak_items"]])
        self.assertTrue(result["retest"])  # 같은 자소서·공고
        self.assertFalse(any(r["over"] for r in result["retest"]))
        self.assertIn("목표(+2점): 달성", compare.render(result))


class TermsTest(unittest.TestCase):
    @unittest.skipUnless(DICTIONARY.is_dir(), "17번 새록 사전이 없는 설치본")
    def test_lite_matches_dictionary(self):
        built = terms.build(DICTIONARY / "terms.json", DICTIONARY / "catalog.json")
        self.assertEqual(terms.dump(built), terms.LITE.read_text(encoding="utf-8"),
                         "17번 용어가 바뀌었습니다. data/terms-lite.json을 다시 만드세요.")

    def test_pick(self):
        out = terms.pick("platform", "pm", limit=5)
        self.assertLessEqual(len(out["terms"]), 5)
        self.assertEqual(len({t["term"] for t in out["terms"]}), len(out["terms"]))
        with self.assertRaises(ValueError):
            terms.pick("space", "pm")


class CliTest(Base):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_flow(self):
        code, out, _ = self.run_cli("new", str(EXAMPLES / "resume-letter.md"), "--posting", str(EXAMPLES / "posting.md"),
                                    "--company", "골목장터", "--industry", "platform", "--role", "pm")
        self.assertEqual(code, 0)
        folder = json.loads(out)["folder"]
        code, out, _ = self.run_cli("record", folder, "document", "--file", str(EXAMPLES / "pressure-result.json"))
        self.assertEqual(code, 0)
        code, out, _ = self.run_cli("next", folder, "--who", "pressure")
        self.assertEqual(json.loads(out)["no"], 1)
        code, out, _ = self.run_cli("compare")
        self.assertEqual(code, 0)
        self.assertIn("회차 비교 (1회)", out)

    def test_errors_exit_2(self):
        code, _, err = self.run_cli("new", str(EXAMPLES / "resume-letter.md"), "--industry", "platform")
        self.assertEqual(code, 2)
        self.assertIn("함께", err)
        self.assertEqual(self.run_cli("compare")[0], 2)  # 세션 없음


if __name__ == "__main__":
    unittest.main()
