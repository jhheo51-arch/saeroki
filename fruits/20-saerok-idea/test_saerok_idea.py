"""새록 심사단(20번 열매) 결정적 계층 검사. 실제 기록은 임시 기록 폴더에만 만듭니다."""

import contextlib
import http.client
import importlib.util
import io
import json
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path

from saerok_idea import cli, money, rubric, store, subscription, verdict, web

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE / "examples"
ROOT = HERE.parent.parent


def example(name: str) -> dict:
    return json.loads((EXAMPLES / name).read_text(encoding="utf-8"))


def judges(*votes: str) -> dict:
    return {k: {"vote": v} for k, v in zip(rubric.ORDER, votes)}


def assumptions(problem="받침", alternative="받침", pay="받침") -> list[dict]:
    return [{"key": "problem", "status": problem}, {"key": "alternative", "status": alternative}, {"key": "pay", "status": pay}]


IDEA = {"line": "한 줄", "what": "무엇", "who": "누구", "money": "미정", "why_now": "미정"}


class VerdictTest(unittest.TestCase):
    def check(self, votes, expected, **status):
        self.assertEqual(verdict.decide(IDEA, judges(*votes), assumptions(**status))["verdict"], expected)

    def test_votes(self):
        self.check(("진행", "진행", "진행"), "진행")
        self.check(("진행", "진행", "조건부"), "진행")
        self.check(("진행", "진행", "보류"), "조건부")  # 보류가 한 표라도 있으면 진행이 아님
        self.check(("진행", "조건부", "조건부"), "조건부")
        self.check(("보류", "보류", "진행"), "보류")

    def test_assumptions_adjust(self):
        self.check(("진행", "진행", "진행"), "보류", problem="반박")
        self.check(("진행", "조건부", "조건부"), "보류", problem="반박")
        self.check(("진행", "진행", "진행"), "조건부", pay="반박")
        self.check(("진행", "진행", "진행"), "조건부", alternative="반박")
        self.check(("보류", "보류", "진행"), "보류", pay="반박")

    def test_insufficient(self):
        self.check(("진행",) * 3, verdict.INSUFFICIENT, problem="확인 못 함", alternative="확인 못 함", pay="확인 못 함")
        for key in rubric.CORE_FIELDS:
            out = verdict.decide({**IDEA, key: "미정"}, judges("진행", "진행", "진행"), assumptions())
            self.assertEqual(out["verdict"], verdict.INSUFFICIENT)
        # 돈·왜 지금이 미정이어도 판정은 냅니다.
        self.assertEqual(verdict.decide(IDEA, judges("진행", "진행", "진행"), assumptions())["verdict"], "진행")

    def test_steps_explain(self):
        out = verdict.decide(IDEA, judges("진행", "진행", "진행"), assumptions(pay="반박"))
        self.assertEqual(len(out["steps"]), 2)
        self.assertIn("진행 3", out["steps"][0])


class MoneyTest(unittest.TestCase):
    def test_breakeven(self):
        out = money.breakeven(example("money.json"))
        self.assertEqual(out, {"computed": True, "margin": 8400, "customers": 36,
                               "note": "고정비를 고객당 남는 돈으로 나눈 뒤 올림한 월 고객 수입니다."})

    def test_missing_values_not_computed(self):
        out = money.breakeven({"price": {"value": 9900, "source": "사용자 입력"}})
        self.assertFalse(out["computed"])
        self.assertEqual(len(out["needed"]), 2)

    def test_no_margin(self):
        values = {k: {"value": v, "source": "사용자 입력"} for k, v in (("price", 1000), ("unit_cost", 1000), ("fixed_cost", 10))}
        self.assertIsNone(money.breakeven(values)["customers"])

    def test_refuses_ai_guess_and_unlinked(self):
        with self.assertRaises(ValueError):
            money.breakeven({"price": {"value": 9900, "source": "AI 추정·시뮬레이션"}})
        with self.assertRaises(ValueError):
            money.breakeven({"price": {"value": 9900, "source": "확인됨"}})


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "idea"
        self.old = os.environ.get(store.HOME_ENV)
        os.environ[store.HOME_ENV] = str(self.home)

    def tearDown(self):
        if self.old is None:
            os.environ.pop(store.HOME_ENV, None)
        else:
            os.environ[store.HOME_ENV] = self.old
        self.tmp.cleanup()

    def full_run(self, date="2026-10-17") -> Path:
        folder = Path(store.create(example("idea.json"), date=date)["folder"])
        for key in rubric.ORDER:
            store.record(folder, "judge", example(f"judge-{key}.json"))
        for part in ("assumptions", "competitors", "panel", "money", "directions"):
            store.record(folder, part, example(f"{part}.json"))
        return folder


class StoreTest(Base):
    def test_create_keeps_runs_by_date(self):
        first = Path(store.create(example("idea.json"), date="2026-10-17")["folder"])
        again = Path(store.create(example("idea.json"), date="2026-10-17")["folder"])
        self.assertEqual(first.parent, again.parent)
        self.assertEqual(again.name, "2026-10-17-2")
        self.assertEqual(store.load(first)["idea"]["why_now"], "미정")

    def test_refuses_inside_git(self):
        repo = Path(self.tmp.name) / "repo"
        (repo / ".git").mkdir(parents=True)
        with self.assertRaises(ValueError):
            store.create(example("idea.json"), base=repo / "idea")

    def test_needs_line(self):
        with self.assertRaises(ValueError):
            store.create({"what": "무엇"})

    def test_full_run_report(self):
        folder = self.full_run()
        self.assertEqual(store.decide(folder)["verdict"], "조건부")  # 진행 2표지만 pay 가정 반박
        text = store.write_report(folder).read_text(encoding="utf-8")
        self.assertIn("**조건부**", text)
        self.assertIn(rubric.NOTICE, text)
        self.assertIn("손익분기 월 고객 수: 36명", text)
        self.assertIn("### 방향 1. 무료 알림 + 거래처 연동 수수료 (추천)", text)
        self.assertIn("/saerok-prd:design --from", text)
        self.assertIn("반박 근거를 먼저 찾은 검색어", text)
        self.assertEqual(text, store.render(folder))  # 같은 기록이면 같은 결과

    def test_rerecord_keeps_old(self):
        folder = self.full_run()
        store.record(folder, "judge", {**example("judge-business.json"), "vote": "보류"})
        result = store.load(folder)
        self.assertEqual(result["judges"]["business"]["vote"], "보류")
        self.assertEqual(result["replaced"][0]["part"], "judge:business")
        self.assertEqual(result["replaced"][0]["old"]["vote"], "조건부")

    def test_decide_needs_all_parts(self):
        folder = Path(store.create(example("idea.json"))["folder"])
        with self.assertRaises(ValueError):
            store.decide(folder)


class CheckTest(unittest.TestCase):
    def test_judge_format(self):
        good = example("judge-business.json")
        for bad in ({**good, "score": 6}, {**good, "score": True}, {**good, "vote": "통과"},
                    {**good, "judge": "investor"}, {**good, "concerns": []}):
            with self.assertRaises(ValueError):
                store.check_judge(bad)

    def test_assumptions_need_matching_evidence_and_links(self):
        data = example("assumptions.json")
        no_link = json.loads(json.dumps(data))
        no_link["assumptions"][0]["evidence"][0]["url"] = ""
        no_counter = json.loads(json.dumps(data))
        no_counter["assumptions"][0]["counter_query"] = ""
        wrong_side = json.loads(json.dumps(data))
        wrong_side["assumptions"][2]["status"] = "받침"  # 반박 근거만 있는데 받침
        missing = {"assumptions": data["assumptions"][:2]}
        for bad in (no_link, no_counter, wrong_side, missing):
            with self.assertRaises(ValueError):
                store.check_assumptions(bad)
        unknown = json.loads(json.dumps(data))
        unknown["assumptions"][0].update(status="확인 못 함", evidence=[])
        self.assertEqual(store.check_assumptions(unknown)[0]["status"], "확인 못 함")

    def test_panel_and_directions(self):
        panel = example("panel.json")
        with self.assertRaises(ValueError):
            store.check_panel({**panel, "size": 50})
        with self.assertRaises(ValueError):
            store.check_panel({**panel, "personas": panel["personas"][:2]})
        directions = example("directions.json")
        with self.assertRaises(ValueError):
            store.check_directions({**directions, "recommended": 3})
        with self.assertRaises(ValueError):
            store.check_directions({**directions, "directions": directions["directions"][:1]})


class AgentFilesTest(unittest.TestCase):
    def test_agents_match_rubric(self):
        for key in rubric.ORDER:
            text = (HERE / "agents" / f"{key.replace('_', '-')}.md").read_text(encoding="utf-8")
            self.assertIn(f'"judge": "{key}"', text)
            for criterion in rubric.JUDGES[key]["criteria"]:
                self.assertIn(criterion, text)

    def test_plugin_manifest(self):
        plugin = json.loads((HERE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["name"], "saerok-idea")
        market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        self.assertIn("./fruits/20-saerok-idea", [p["source"] for p in market["plugins"]])


class CliTest(Base):
    def run_cli(self, *argv) -> tuple[int, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(list(argv))
        return code, out.getvalue() + err.getvalue()

    def test_direction_rerun_and_compare(self):
        folder = self.full_run()
        store.write_report(folder)
        code, out = self.run_cli("new", "--from", str(folder / "verdict.md"), "--direction", "2", "--date", "2026-10-18")
        self.assertEqual(code, 0)
        new = Path(json.loads(out)["folder"])
        self.assertEqual(new.parent, folder.parent)
        self.assertEqual(store.load(new)["idea"]["what"], "우유 유통기한·재고 알림만")
        self.assertEqual(store.load(new)["from"]["direction"], 2)
        code, out = self.run_cli("compare", str(folder.parent))
        self.assertEqual(code, 0)
        self.assertIn("| 2026-10-17 | 조건부 |", out)
        self.assertIn("| 2026-10-18 | 미완료 |", out)

    def test_breakeven_and_errors(self):
        code, out = self.run_cli("breakeven", "--price", "9900", "--unit-cost", "1500", "--fixed-cost", "300000")
        self.assertEqual((code, json.loads(out)["customers"]), (0, 36))
        code, _ = self.run_cli("new", "--direction", "1")
        self.assertEqual(code, 2)


NODE = shutil.which("node")
CORE = HERE / "web" / "idea-core.js"


def run_node(script: str, data) -> dict:
    out = subprocess.run([NODE, "-e", script, str(CORE)], input=json.dumps(data, ensure_ascii=False).encode("utf-8"),
                         capture_output=True, check=True, timeout=60)
    return json.loads(out.stdout.decode("utf-8"))


@unittest.skipUnless(NODE, "node가 없어 웹 화면 계산 검사를 건너뜁니다.")
class WebCoreTest(Base):
    """web/idea-core.js가 saerok_idea와 같은 판정·기록·verdict.md를 내는지 봅니다."""

    def test_same_report_as_python(self):
        folder = self.full_run()
        parts = ("assumptions", "competitors", "panel", "money", "directions")
        script = r"""const S=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
          const i=JSON.parse(d);const r=S.newResult(i.idea,'2026-10-17',null);for(const j of i.judges)S.record(r,'judge',j,'t');
          for(const p of i.order)S.record(r,p,i.parts[p],'t');process.stdout.write(JSON.stringify({md:S.render(r,i.run,i.path),result:r}))})"""
        out = run_node(script, {"idea": example("idea.json"), "order": parts, "parts": {p: example(f"{p}.json") for p in parts},
                                "judges": [example(f"judge-{k}.json") for k in rubric.ORDER],
                                "run": folder.name, "path": str(folder / "verdict.md")})
        self.assertEqual(out["md"], store.render(folder))
        self.assertEqual(out["result"], store.load(folder))

    def test_same_verdict_for_every_case(self):
        statuses = rubric.STATUSES
        cases = [{"idea": {**IDEA, "what": what}, "votes": [a, b, c], "status": [p, q, r]}
                 for what in ("무엇", "미정") for a in rubric.VOTES for b in rubric.VOTES for c in rubric.VOTES
                 for p in statuses for q in statuses for r in statuses]
        script = r"""const S=require(process.argv[1]);let d='';process.stdin.on('data',c=>d+=c).on('end',()=>{
          const keys=['problem','alternative','pay'];
          process.stdout.write(JSON.stringify(JSON.parse(d).map(c=>S.decide(c.idea,Object.fromEntries(S.ORDER.map((k,i)=>[k,{vote:c.votes[i]}])),
            keys.map((k,i)=>({key:k,status:c.status[i]}))))))})"""
        js = run_node(script, cases)
        for case, got in zip(cases, js):
            want = verdict.decide(case["idea"], judges(*case["votes"]), assumptions(*case["status"]))
            self.assertEqual(got, want, case)

    def test_same_rubric(self):
        script = r"""const S=require(process.argv[1]);process.stdin.on('data',()=>{}).on('end',()=>process.stdout.write(JSON.stringify(
          {judges:S.JUDGES,votes:S.VOTES,assumptions:S.ASSUMPTIONS,statuses:S.STATUSES,fields:S.FIELDS,core:S.CORE_FIELDS,
           panel:S.PANEL_SIZES,notice:S.NOTICE,insufficient:S.INSUFFICIENT})))"""
        js = run_node(script, {})
        self.assertEqual(js["judges"], rubric.JUDGES)
        self.assertEqual((js["votes"], js["assumptions"], js["statuses"], js["fields"], js["core"], js["panel"], js["notice"]),
                         (rubric.VOTES, rubric.ASSUMPTIONS, rubric.STATUSES, rubric.FIELDS, list(rubric.CORE_FIELDS),
                          dict(rubric.PANEL_SIZES), rubric.NOTICE))
        self.assertEqual(js["insufficient"], verdict.INSUFFICIENT)


class WebServerTest(Base):
    """`saerok-idea`가 여는 내 PC 서버. 임시 기록 폴더와 빈 포트에서만 돌립니다."""

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
        self.assertIn("idea-core.js", page)
        self.assertEqual(self.call("/agents/business.md")[0], 200)
        status, info = self.call("/api/info")
        self.assertEqual((status, info["mode"], info["home"], info["key"]), (200, "local", str(store.home()), "등록 안 됨"))

    def test_full_flow(self):
        status, made = self.call("/api/new", {"idea": example("idea.json")})
        self.assertEqual(status, 200)
        folder = made["folder"]
        for key in rubric.ORDER:
            self.assertEqual(self.call("/api/record", {"folder": folder, "part": "judge", "data": example(f"judge-{key}.json")})[0], 200)
        for part in ("assumptions", "competitors", "panel", "money", "directions"):
            self.assertEqual(self.call("/api/record", {"folder": folder, "part": part, "data": example(f"{part}.json")})[0], 200)
        status, report = self.call("/api/report", {"folder": folder})
        self.assertEqual((status, report["decided"]["verdict"]), (200, "조건부"))
        self.assertTrue(Path(report["path"]).is_file())
        status, again = self.call("/api/new", {"from": {"folder": folder, "direction": 2}})
        self.assertEqual((again["slug"], again["result"]["from"]["direction"]), (made["slug"], 2))
        self.assertEqual(again["result"]["idea"]["what"], "우유 유통기한·재고 알림만")
        status, ideas = self.call("/api/runs")
        self.assertEqual([r["run"] for r in ideas[0]["runs"]], sorted([made["run"], again["run"]]))

    def test_parallel_records_kept(self):
        # 화면은 심사위원 3명 결과를 동시에 보냅니다. 하나라도 덮어쓰이면 안 됩니다.
        folder = self.call("/api/new", {"idea": example("idea.json")})[1]["folder"]
        for _ in range(3):
            workers = [threading.Thread(target=self.call, args=("/api/record", {"folder": folder, "part": "judge",
                                                                                "data": example(f"judge-{k}.json")}))
                       for k in rubric.ORDER]
            for w in workers:
                w.start()
            for w in workers:
                w.join()
            self.assertEqual(sorted(store.load(Path(folder))["judges"]), sorted(rubric.ORDER))

    def test_guards(self):
        self.assertEqual(self.call("/api/info", headers={"Host": f"evil.example:{self.port}"})[0], 403)
        self.assertEqual(self.call("/api/info", headers={web.API_HEADER: ""})[0], 403)
        self.assertEqual(self.call("/api/new", {"idea": example("idea.json")}, headers={"Origin": "https://evil.example"})[0], 403)
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        self.assertEqual(self.call("/api/record", {"folder": str(outside), "part": "panel", "data": {}})[0], 400)
        self.assertEqual(self.call("/../saerok_idea/web.py")[0], 404)
        self.assertEqual(self.call("/api/claude", {"model": "x", "messages": []})[0], 401)  # 키 없으면 밖으로 안 나감

    def test_key_in_memory_without_keyring(self):
        self.assertEqual(self.call("/api/key", {"key": "nope"})[0], 400)
        status, saved = self.call("/api/key", {"key": "sk-ant-test-0000000000"})
        self.assertEqual((status, saved["key_from"]), (200, "이번 실행 메모리"))
        self.assertNotIn("0000000000", json.dumps(self.call("/api/info")[1]))  # 키 전체를 화면에 돌려주지 않음
        self.call("/api/key/delete", {})
        self.assertEqual(self.call("/api/info")[1]["key"], "등록 안 됨")

    def test_engine_switch_to_subscription(self):
        subscription.cli = lambda: None
        self.assertEqual(self.call("/api/engine", {"engine": "subscription"})[0], 400)  # claude 명령이 없으면 못 고름
        self.assertEqual(self.call("/api/engine", {"engine": "free"})[0], 400)
        seen = []
        subscription.cli = lambda: "claude"
        subscription.call = lambda body: seen.append(body) or {"content": [{"type": "text", "text": "{}"}], "stop_reason": "end_turn"}
        self.assertEqual(self.call("/api/engine", {"engine": "subscription"}), (200, {"engine": "subscription"}))
        info = self.call("/api/info")[1]
        self.assertEqual((info["engine"], info["claude_cli"]), ("subscription", True))
        body = {"model": "claude-sonnet-5-5", "messages": [{"role": "user", "content": "가상"}]}
        self.assertEqual(self.call("/api/claude", body)[1]["stop_reason"], "end_turn")  # 키 없이도 구독으로 돎
        self.assertEqual(seen, [body])
        subscription.call = lambda body: (_ for _ in ()).throw(RuntimeError("로그인 필요"))
        self.assertEqual(self.call("/api/claude", body), (502, {"error": "로그인 필요"}))


STREAM = [
    {"type": "system", "subtype": "init", "tools": ["WebSearch"], "apiKeySource": "none"},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "찾아봅니다."},
        {"type": "tool_use", "id": "t1", "name": "WebSearch", "input": {"query": "일반 낱말", "mode": "standard"}}]}},
    {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content":
        'Web search results for query: "일반 낱말"\n\nLinks: [{"title":"가상 \\"제목\\"","url":"https://example.com/a"},'
        '{"title":"나쁜 링크","url":"javascript:alert(1)"}]'}]}},
    {"type": "assistant", "message": {"content": [{"type": "text", "text": "```json\n{\"ok\": 1}\n```"}]}},
    {"type": "result", "subtype": "success", "is_error": False,
     "usage": {"input_tokens": 4, "cache_creation_input_tokens": 10, "cache_read_input_tokens": 6, "output_tokens": 7}},
]


class SubscriptionTest(unittest.TestCase):
    """구독(claude -p) 응답을 화면이 읽는 Messages API 모양으로 바꾸는지. 실제 claude는 부르지 않습니다."""

    def test_convert(self):
        r = subscription.convert([json.dumps(e, ensure_ascii=False) for e in STREAM] + ["", "깨진 줄"])
        kinds = [c["type"] for c in r["content"]]
        self.assertEqual(kinds, ["text", "server_tool_use", "web_search_tool_result", "text"])
        self.assertEqual(r["content"][1], {"type": "server_tool_use", "id": "t1", "name": "web_search", "input": {"query": "일반 낱말"}})
        self.assertEqual(r["content"][2]["content"], [{"type": "web_search_result", "title": '가상 "제목"', "url": "https://example.com/a"}])
        self.assertEqual(r["usage"], {"input_tokens": 20, "output_tokens": 7, "server_tool_use": {"web_search_requests": 1}})
        self.assertEqual(r["stop_reason"], "end_turn")

    def test_convert_errors(self):
        with self.assertRaises(RuntimeError):
            subscription.convert([json.dumps(STREAM[1])])
        with self.assertRaisesRegex(RuntimeError, "한도"):
            subscription.convert([json.dumps({"type": "result", "is_error": True, "result": "한도 초과"})])

    def test_call_args_and_env(self):
        seen = {}

        def fake_run(args, **kw):
            seen.update(args=args, **kw)
            seen["system"] = Path(args[args.index("--system-prompt-file") + 1]).read_text(encoding="utf-8")
            out = "\n".join(json.dumps(e, ensure_ascii=False) for e in STREAM)
            return subprocess.CompletedProcess(args, 0, out.encode("utf-8"), b"")

        body = {"model": "claude-sonnet-5-5", "system": "심사위원", "messages": [{"role": "user", "content": "가상 아이디어"}],
                "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}]}
        old_run = subprocess.run
        os.environ["ANTHROPIC_API_KEY"], old_key = "sk-ant-test-0000", os.environ.get("ANTHROPIC_API_KEY")
        try:
            subscription.subprocess.run = fake_run
            r = subscription.call(body, command="claude")
        finally:
            subscription.subprocess.run = old_run
            if old_key is None:
                os.environ.pop("ANTHROPIC_API_KEY")
            else:
                os.environ["ANTHROPIC_API_KEY"] = old_key
        args = seen["args"]
        self.assertEqual(r["content"][-1]["text"], '```json\n{"ok": 1}\n```')
        self.assertNotIn("ANTHROPIC_API_KEY", seen["env"])  # API 크레딧이 아니라 구독으로
        self.assertEqual(seen["input"].decode("utf-8"), "가상 아이디어")  # 아이디어는 명령줄이 아니라 표준 입력으로
        self.assertNotIn("가상 아이디어", " ".join(args))
        for flag in ("--no-session-persistence", "--strict-mcp-config", "--disable-slash-commands"):
            self.assertIn(flag, args)
        self.assertEqual(args[args.index("--tools") + 1], "WebSearch")
        self.assertEqual(args[args.index("--model") + 1], "claude-sonnet-5-5")
        self.assertIn("최대 3번", seen["system"])
        self.assertFalse(Path(seen["cwd"]).exists())  # 임시 폴더는 지움
        no_search = subscription.args_for({"messages": []}, Path("s.md"))
        self.assertEqual(no_search[no_search.index("--tools") + 1], "")

    def test_bad_body(self):
        with self.assertRaises(ValueError):
            subscription.call({"messages": []}, command="claude")


def load_sync():
    spec = importlib.util.spec_from_file_location("sync_idea_prd", ROOT / "scripts" / "sync_idea_prd.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SyncTest(unittest.TestCase):
    """10장 버전 맞춤. 임시 저장소 꼴 폴더에서만 고칩니다."""

    def setUp(self):
        self.sync = load_sync()
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "PRD-v2.0.md").write_text("# 새록이 4번 열매 PRD v2.0: 새록 검토관\n", encoding="utf-8")
        (docs / "PRD-v2.1.md").write_text("# 새록이 19번 열매 PRD v2.1: 새록 면접관\n", encoding="utf-8")
        (docs / "PRD-v2.0-idea.md").write_text(
            "# 새록이 20번 열매 PRD v2.0-idea: 새록 심사단\n\n"
            "- 문서 버전: 4번 새록 검토관 PRD의 짝 문서. 검토관 [PRD v2.0](PRD-v2.0.md)을 따름(10장)\n\n본문 v2.0 그대로\n",
            encoding="utf-8")
        (self.root / "README.md").write_text("[PRD v2.0-idea](docs/PRD-v2.0-idea.md)\n", encoding="utf-8")
        skill = self.root / "fruits" / "04-prd-assistant" / "skills" / "design"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("`--from <verdict.md>`\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_in_sync(self):
        self.assertEqual(self.sync.problems(self.root), [])

    def test_follows_new_reviewer_version(self):
        (self.root / "docs" / "PRD-v2.3.md").write_text("# 새록이 4번 열매 PRD v2.3: 새록 검토관\n", encoding="utf-8")
        (self.root / "docs" / "PRD-v2.4.md").write_text("# 새록이 21번 열매 PRD v2.4: 다른 것\n", encoding="utf-8")
        self.assertTrue(self.sync.problems(self.root))
        changed = self.sync.sync(self.root, use_git=False)
        self.assertIn("README.md", changed)
        new = self.root / "docs" / "PRD-v2.3-idea.md"
        self.assertTrue(new.is_file())
        self.assertFalse((self.root / "docs" / "PRD-v2.0-idea.md").exists())
        text = new.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 새록이 20번 열매 PRD v2.3-idea: 새록 심사단"))
        self.assertIn("검토관 [PRD v2.3](PRD-v2.3.md)", text)
        self.assertIn("본문 v2.0 그대로", text)  # 본문은 바꾸지 않음
        self.assertIn("내용 다시 보기 전", text)
        self.assertEqual((self.root / "README.md").read_text(encoding="utf-8"), "[PRD v2.3-idea](docs/PRD-v2.3-idea.md)\n")
        self.assertEqual(self.sync.problems(self.root), [])
        self.assertEqual(self.sync.sync(self.root, use_git=False), [])  # 두 번 돌려도 그대로

    def test_missing_reviewer_fails(self):
        (self.root / "docs" / "PRD-v2.0.md").write_text("# 다른 제목\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.sync.problems(self.root)

    def test_link_check(self):
        (self.root / "fruits" / "04-prd-assistant" / "skills" / "design" / "SKILL.md").write_text("없음\n", encoding="utf-8")
        self.assertTrue(any("--from" in p for p in self.sync.problems(self.root)))
        (self.root / "fruits" / "04-prd-assistant" / "skills" / "design" / "SKILL.md").write_text("`--from <verdict.md>`\n", encoding="utf-8")
        (self.root / "README.md").write_text("[옛 이름](docs/PRD-v1.9-idea.md)\n", encoding="utf-8")
        self.assertTrue(any("PRD-v1.9-idea.md" in p for p in self.sync.problems(self.root)))


if __name__ == "__main__":
    unittest.main()
