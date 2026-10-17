"""새록 심사단(20번 열매) 결정적 계층 검사. 실제 기록은 임시 기록 폴더에만 만듭니다."""

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path

from saerok_idea import cli, money, rubric, store, verdict

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
