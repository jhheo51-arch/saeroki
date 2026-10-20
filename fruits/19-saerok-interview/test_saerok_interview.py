"""새록 면접관(19번 열매) 결정적 계층 검사. 실제 기록은 임시 면접 폴더에만 만듭니다."""

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

from saerok_interview import cli, compare, docs, rubric, session, store, subscription, terms, web

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


class DocsTest(Base):
    def put(self, name: str, src: Path = EXAMPLES / "resume-letter.md") -> Path:
        path = docs.folder() / name
        path.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        return path

    def test_init_makes_templates_once(self):
        first = docs.init()
        self.assertEqual(first["created"], ["자기소개서.md", "공고-회사이름.md"])
        self.assertEqual(docs.init()["created"], [])
        with self.assertRaises(ValueError) as e:  # 양식 그대로면 시작하지 않습니다.
            docs.pick()
        self.assertIn("양식", str(e.exception))
        self.assertEqual(session.sessions(), [])  # 서류 폴더는 세션으로 세지 않습니다.

    def test_init_refuses_inside_git(self):
        repo = Path(self.tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True)
        os.environ[session.HOME_ENV] = str(repo / "interviews")
        with self.assertRaises(ValueError):
            docs.init()

    def test_pick_by_file_name(self):
        docs.init()
        self.put("자기소개서.md")
        self.put("공고-골목장터.md", EXAMPLES / "posting.md")
        (docs.folder() / "공고-회사이름.md").unlink()
        (docs.folder() / "이력서.hwp").write_bytes(b"x")
        found = docs.pick()
        self.assertEqual(found["company"], "골목장터")
        self.assertEqual(set(found["pick"]), {"resume_letter", "posting"})
        self.assertEqual(found["unreadable"], ["이력서.hwp"])
        self.assertEqual(found["template"], [])

    def test_pick_asks_when_many_companies(self):
        docs.init()
        self.put("자기소개서.md")
        self.put("공고-골목장터.md", EXAMPLES / "posting.md")
        self.put("공고-꽃길마켓.md", EXAMPLES / "posting.md")
        self.put("자기소개서-꽃길마켓.md")
        self.assertIsNone(docs.pick()["pick"])
        self.assertEqual(docs.pick()["choices"], ["골목장터", "꽃길마켓"])
        mine = docs.pick("꽃길마켓")["pick"]
        self.assertTrue(mine["resume_letter"].endswith("자기소개서-꽃길마켓.md"))
        self.assertTrue(docs.pick("골목장터")["pick"]["resume_letter"].endswith("자기소개서.md"))

    def test_pick_company_resume_letter(self):
        # 21번 새록 지원서가 저장하는 이름(자기소개서-회사이름·공고-회사이름)을 --company로 고릅니다.
        docs.init()
        (docs.folder() / "자기소개서.md").unlink()
        (docs.folder() / "공고-회사이름.md").unlink()
        self.put("자기소개서-골목장터.md")
        self.assertTrue(docs.pick()["pick"]["resume_letter"].endswith("자기소개서-골목장터.md"))  # 공고 없이도 회사를 정함
        self.put("공고-골목장터.md", EXAMPLES / "posting.md")
        self.put("자기소개서-꽃길마켓.md")
        mine = docs.pick()  # 공고가 한 회사면 그 회사로 정합니다.
        self.assertEqual(mine["company"], "골목장터")
        self.assertTrue(mine["pick"]["resume_letter"].endswith("자기소개서-골목장터.md"))
        self.assertTrue(mine["pick"]["posting"].endswith("공고-골목장터.md"))
        with self.assertRaises(ValueError):  # 이름 없는 자기소개서가 없으면 다른 회사로 돌아가지 않습니다.
            docs.pick("모르는회사")
        self.put("자기소개서.md")
        self.assertTrue(docs.pick("모르는회사")["pick"]["resume_letter"].endswith("자기소개서.md"))


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
        self.assertIsNone(out["items"]["summary"])  # 답변에서만 봄
        self.assertEqual(out["total"], 4.0)  # why_us 1/3 + vision 1/2, 분모 5
        answer = {"interviewer": "executive", "question": "q", "answer": "a",
                  "items": {"company": None, "why_us": 3, "vision": 2, "summary": 2}}
        self.assertEqual(store.record_answer(folder, answer)["items"]["summary"], 2)  # 답변에서는 채점

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
        self.assertEqual(self.run_cli("new")[0], 2)  # 서류 폴더 없음

    def test_new_from_docs(self):
        self.assertEqual(self.run_cli("init")[0], 0)
        (docs.folder() / "자기소개서.md").write_text((EXAMPLES / "resume-letter.md").read_text(encoding="utf-8"), encoding="utf-8")
        (docs.folder() / "공고-회사이름.md").unlink()
        (docs.folder() / "공고-골목장터.md").write_text((EXAMPLES / "posting.md").read_text(encoding="utf-8"), encoding="utf-8")
        code, out, _ = self.run_cli("new", "--date", "2026-10-17")
        self.assertEqual(code, 0)
        made = json.loads(out)
        self.assertEqual(Path(made["folder"]).name, "2026-10-17-골목장터")
        self.assertTrue(made["posting"])


NODE = shutil.which("node")
CORE = HERE / "web" / "interview-core.js"


def run_node(script: str, data):
    out = subprocess.run([NODE, "-e", script, str(CORE)], input=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                         capture_output=True, check=True, timeout=60)
    return json.loads(out.stdout.decode("utf-8"))


def example_texts() -> dict:
    return {"resume_letter": session.read(EXAMPLES / "resume-letter.md"), "posting": session.read(EXAMPLES / "posting.md")}


ANSWER = {"no": 1, "interviewer": "pressure", "level": "보통", "question": "q", "answer": "a", "date": "2026-10-17",
          "followups": [{"question": "꼬리", "answer": "답"}], "items": {}, "na": {}, "missing": ["수치 출처"], "better": "방향"}


@unittest.skipUnless(NODE, "node가 없어 웹 화면 계산 검사를 건너뜁니다.")
class WebCoreTest(Base):
    """web/interview-core.js가 saerok_interview와 같은 세션·검사·verdict.md·practice.md·비교를 내는지 봅니다."""

    def records(self):
        docs_ = [json.loads((EXAMPLES / "pressure-result.json").read_text(encoding="utf-8"))]
        docs_ += [doc_result(w, line=99, quote="없는 문장") for w in rubric.ORDER if w != "pressure"]
        items = {s["key"]: s["max"] // 2 for s in rubric.INTERVIEWERS["pressure"]["items"]}
        return docs_, {**ANSWER, "items": items}

    def test_same_session_records_and_reports(self):
        texts = example_texts()
        made = session.create_texts(texts, company="골목장터", industry="platform", role="pm", date="2026-10-17")
        folder = Path(made["folder"])
        docs_, answer = self.records()
        for d in docs_:
            store.record_document(folder, d)
        store.record_answer(folder, answer)
        real = {"date": "2026-10-18", "questions": [{"question": "본인 역할은?", "matched": 1, "confirmed": True}]}
        store.record_real(folder, real)
        meta, score = session.load(folder)
        script = r"""const S=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c).on('end',async()=>{
          const i=JSON.parse(d);const s=await S.createSession(i.texts,{date:'2026-10-17',company:'골목장터',industry:'platform',role:'pm'},[]);
          for(const r of i.docs)S.recordDocument(s,r);S.recordAnswer(s,i.answer,'x');S.recordReal(s,i.real,'x');
          const cmp=S.compare([[s.meta,s.score]]);
          process.stdout.write(JSON.stringify({meta:s.meta,score:s.score,privacy:s.privacy,report:S.renderReport(s),
            practice:S.renderPractice(s.meta,s.score),next:S.nextQuestion(s,['hr']),cmp,cmpMd:S.renderCompare(cmp)}))})"""
        out = run_node(script, {"texts": texts, "docs": docs_, "answer": answer, "real": real})
        self.assertEqual(out["meta"], meta)
        self.assertEqual(out["privacy"], made["privacy"])
        self.assertEqual(out["score"], score)
        self.assertEqual(out["report"], store.render_report(folder))
        self.assertEqual(out["practice"], store.render_practice(meta, score))
        self.assertEqual(out["next"], store.next_question(folder, ["hr"]))
        result = compare.compare([(meta, score)])
        self.assertEqual(out["cmp"], result)
        self.assertEqual(out["cmpMd"], compare.render(result))

    def test_same_errors(self):
        folder = self.new()
        bad = [{**doc_result("hr"), "questions": []}, {**doc_result("hr"), "items": {"motivation": 99}},
               {**doc_result("hr"), "interviewer": "boss"}, {**doc_result("hr"), "items": {"nope": 1}}]
        meta, _ = session.load(folder)
        script = r"""const S=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
          const i=JSON.parse(d);process.stdout.write(JSON.stringify(i.bad.map(b=>{try{S.recordDocument({meta:i.meta,inputs:i.texts,
            score:{version:1,document:{},answers:[],real:[]}},b);return null}catch(e){return e.message}})))})"""
        js = run_node(script, {"bad": bad, "meta": meta, "texts": session.inputs(folder, meta)})
        for b, msg in zip(bad, js):
            with self.assertRaises(ValueError) as caught:
                store.record_document(folder, b)
            self.assertEqual(msg, str(caught.exception))

    def test_same_rubric_scan_and_terms(self):
        text = "연락처 010-1234-5678\n메일 a.b@example.com · 900101-1234567\n전환율 30%"
        script = r"""const S=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
          const i=JSON.parse(d);process.stdout.write(JSON.stringify({rubric:S.INTERVIEWERS,order:S.ORDER,levels:S.LEVELS,notice:S.NOTICE,
            verdicts:i.scores.map(S.verdict),scan:S.scan(i.text),terms:S.pickTerms(i.lite,'platform','pm',20)}))})"""
        scores = [None, 0, 4.9, 5, 6.9, 7, 10]
        js = run_node(script, {"text": text, "scores": scores, "lite": terms.load()})
        self.assertEqual((js["rubric"], js["order"], js["levels"], js["notice"]),
                         (rubric.INTERVIEWERS, rubric.ORDER, rubric.LEVELS, rubric.NOTICE))
        self.assertEqual(js["verdicts"], [rubric.verdict(s) for s in scores])
        self.assertEqual(js["scan"], session.scan(text))
        self.assertEqual(js["terms"], terms.pick("platform", "pm", 20))


class WebServerTest(Base):
    """`saerok-interview`가 여는 내 PC 서버. 임시 면접 폴더와 빈 포트에서만 돌립니다."""

    def setUp(self):
        super().setUp()
        self.old_key = os.environ.pop("ANTHROPIC_API_KEY", None)
        self.old_keyring, web.keystore.keyring = web.keystore.keyring, None  # 실제 자격 증명 관리자는 건드리지 않음
        self.old_cli, self.old_call = subscription.cli, subscription.call
        web.ENGINE["now"] = "api"  # 검사에서는 실제 Claude Code·Anthropic을 부르지 않음
        self.server = web.ThreadingHTTPServer(("127.0.0.1", 0), web.Handler)
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
        self.assertIn("interview-core.js", page)
        self.assertEqual(self.call("/agents/pressure.md")[0], 200)
        self.assertEqual(self.call("/data/terms-lite.json")[1], terms.load())
        status, info = self.call("/api/info")
        self.assertEqual((status, info["mode"], info["home"], info["key"]), (200, "local", str(session.home()), "등록 안 됨"))

    def test_full_flow(self):
        status, made = self.call("/api/new", {"texts": {**example_texts(), "resume": "  "}, "company": "골목장터",
                                              "industry": "platform", "role": "pm"})
        self.assertEqual(status, 200)
        folder = made["folder"]
        self.assertEqual(sorted(made["inputs"]), ["posting", "resume_letter"])  # 빈 서류는 두지 않음
        self.assertTrue(Path(folder, "inputs", "자기소개서.md").is_file())
        # 화면은 면접관 5명 결과를 동시에 보냅니다. 하나라도 덮어쓰이면 안 됩니다.
        workers = [threading.Thread(target=self.call, args=("/api/record", {"folder": folder, "kind": "document", "data": doc_result(w)}))
                   for w in rubric.ORDER]
        for w in workers:
            w.start()
        for w in workers:
            w.join()
        self.assertEqual(sorted(session.load(Path(folder))[1]["document"]), sorted(rubric.ORDER))
        items = {s["key"]: s["max"] for s in rubric.INTERVIEWERS["pressure"]["items"]}
        status, row = self.call("/api/record", {"folder": folder, "kind": "answer", "data": {**ANSWER, "items": items}})
        self.assertEqual((status, row["result"]["total"]), (200, 10.0))
        status, entry = self.call("/api/record", {"folder": folder, "kind": "real",
                                                  "data": {"questions": [{"question": "역할은?", "matched": 1, "confirmed": True}]}})
        self.assertEqual(entry["result"]["questions"][0]["confirmed"], True)
        status, report = self.call("/api/report", {"folder": folder})
        self.assertEqual(status, 200)
        self.assertEqual(report["verdict"], store.render_report(Path(folder)))
        self.assertIn("꼬리", report["practice"])
        self.assertTrue(Path(report["path"]).is_file())
        status, rows = self.call("/api/sessions")
        self.assertEqual([r["folder"] for r in rows], [folder])
        self.assertNotIn("inputs", rows[0])
        status, one = self.call("/api/session?folder=" + web.urllib.parse.quote(folder))
        self.assertEqual(one["inputs"]["resume_letter"], example_texts()["resume_letter"])

    def test_docs_folder(self):
        status, err = self.call("/api/docs?company=")
        self.assertEqual(status, 400)
        self.assertIn("서류 폴더가 없습니다", err["error"])
        self.assertEqual(self.call("/api/docs/init", {})[0], 200)
        (docs.folder() / "자기소개서.md").write_text(example_texts()["resume_letter"], encoding="utf-8")
        status, found = self.call("/api/docs?company=")
        self.assertEqual(status, 200)
        self.assertEqual(found["texts"]["resume_letter"], example_texts()["resume_letter"])

    def test_guards(self):
        self.assertEqual(self.call("/api/info", headers={"Host": f"evil.example:{self.port}"})[0], 403)
        self.assertEqual(self.call("/api/info", headers={web.API_HEADER: ""})[0], 403)
        self.assertEqual(self.call("/api/new", {"texts": example_texts()}, headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.call("/api/new", {"texts": example_texts(), "industry": "platform"})[0], 400)
        self.assertEqual(self.call("/api/new", {"texts": {"posting": "공고"}})[0], 400)  # 자기소개서 없음
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        self.assertEqual(self.call("/api/record", {"folder": str(outside), "kind": "real", "data": {}})[0], 400)
        self.assertEqual(self.call("/api/session?folder=" + web.urllib.parse.quote(str(outside)))[0], 400)
        self.assertEqual(self.call("/../saerok_interview/web.py")[0], 404)
        self.assertEqual(self.call("/data/../saerok_interview/web.py")[0], 404)
        self.assertEqual(self.call("/api/claude", {"model": "x", "messages": []})[0], 401)  # 키 없으면 밖으로 안 나감

    def test_key_and_engine(self):
        self.assertEqual(self.call("/api/key", {"key": "nope"})[0], 400)
        status, saved = self.call("/api/key", {"key": "sk-ant-test-0000000000"})
        self.assertEqual(status, 200)
        self.assertNotIn("0000000000", json.dumps(self.call("/api/info")[1]))  # 키 전체를 화면에 돌려주지 않음
        self.call("/api/key/delete", {})
        self.assertEqual(self.call("/api/info")[1]["key"], "등록 안 됨")
        subscription.cli = lambda: None
        self.assertEqual(self.call("/api/engine", {"engine": "subscription"})[0], 400)  # claude 명령이 없으면 못 고름
        seen = []
        subscription.cli = lambda: "claude"
        subscription.call = lambda body: seen.append(body) or {"content": [{"type": "text", "text": "{}"}], "stop_reason": "end_turn"}
        self.assertEqual(self.call("/api/engine", {"engine": "subscription"}), (200, {"engine": "subscription"}))
        body = {"model": "claude-sonnet-5-5", "messages": [{"role": "user", "content": "가상"}]}
        self.assertEqual(self.call("/api/claude", body)[1]["stop_reason"], "end_turn")  # 키 없이도 구독으로 돎
        self.assertEqual(seen, [body])


class SubscriptionTest(unittest.TestCase):
    def test_convert_and_args(self):
        lines = [json.dumps(e, ensure_ascii=False) for e in [
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "{\"ok\": 1}"}]}},
            {"type": "result", "is_error": False, "usage": {"input_tokens": 4, "cache_read_input_tokens": 6, "output_tokens": 7}}]]
        out = subscription.convert(lines)
        self.assertEqual(out["content"], [{"type": "text", "text": "{\"ok\": 1}"}])
        self.assertEqual(out["usage"], {"input_tokens": 10, "output_tokens": 7})
        with self.assertRaises(RuntimeError):
            subscription.convert([])
        args = subscription.args_for({"model": "claude-sonnet-5-5"}, Path("s.md"))
        self.assertEqual(args[args.index("--tools") + 1], "")  # 도구를 하나도 주지 않음
        self.assertIn("--no-session-persistence", args)

    def test_call_drops_api_key(self):
        seen = {}

        def fake_run(args, **kw):
            seen.update(kw)
            out = json.dumps({"type": "result", "is_error": False, "usage": {}})
            return subprocess.CompletedProcess(args, 0, out.encode("utf-8"), b"")

        old_run, old_key = subscription.subprocess.run, os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        try:
            subscription.subprocess.run = fake_run
            subscription.call({"messages": [{"role": "user", "content": "가상"}]}, command="claude")
        finally:
            subscription.subprocess.run = old_run
            if old_key is None:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            else:
                os.environ["ANTHROPIC_API_KEY"] = old_key
        self.assertNotIn("ANTHROPIC_API_KEY", seen["env"])
        self.assertEqual(seen["input"], "가상".encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
