"""새록 가지치기 검사(PRD v2.3 8장). 임시 폴더에서만 돌고, 휴지통 보내기는 가짜로 바꿉니다."""

import json
import os
import subprocess
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

from saerok_memory import apply, hook, memory, sessions, versions
from saerok_memory.store import BUDGET_MIN_LINE, INDEX_LIMIT, LINE_LIMIT

DAY = 86400


def age(path: Path, days: float) -> None:
    t = time.time() - days * DAY
    os.utime(path, (t, t))


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.claude = root / "claude"
        self.data = root / "data"
        self.desk = root / "desktop"
        self.work = root / "work"
        for p in (self.claude / "projects", self.data, self.desk, self.work):
            p.mkdir(parents=True)
        self.env = mock.patch.dict(os.environ, {
            "SAEROK_MEMORY_CLAUDE_HOME": str(self.claude),
            "SAEROK_MEMORY_HOME": str(self.data),
            "SAEROK_MEMORY_DESKTOP": str(self.desk),
        })
        self.env.start()
        self.trashed = []
        self.fake_trash = mock.patch("saerok_memory.trash.send", side_effect=self._send)
        self.fake_trash.start()

    def tearDown(self):
        self.fake_trash.stop()
        self.env.stop()
        self.tmp.cleanup()

    def _send(self, path: Path):
        self.trashed.append(Path(path))
        if Path(path).is_dir():
            import shutil
            shutil.rmtree(path)
        else:
            Path(path).unlink()

    def project(self, name="C--work"):
        folder = self.claude / "projects" / name
        (folder / "memory").mkdir(parents=True, exist_ok=True)
        return folder


class MemoryTest(Base):
    def make_memory(self):
        mem = self.project() / "memory"
        long_hook = ", ".join(f"항목 {i}번 정리" for i in range(40))
        (mem / "long.md").write_text("---\nname: long\n---\n\n본문\n", encoding="utf-8")
        ended = (date.today() - timedelta(days=60)).isoformat()
        (mem / "done.md").write_text(f"---\nname: done\ndescription: {ended} 마감\n---\n\n끝난 일\n", encoding="utf-8")
        age(mem / "done.md", 45)
        (mem / "fresh.md").write_text("---\nname: fresh\n---\n\n지금 하는 일\n", encoding="utf-8")
        index = (f"- [긴 기억](long.md) — {long_hook}\r\n"
                 f"- [끝난 일](done.md) — {ended} 마감\r\n"
                 "- [지금 일](fresh.md) — 진행 중\r\n")
        (mem / "MEMORY.md").write_bytes(index.encode("utf-8"))
        return mem

    def by_kind(self, kind):
        return [c for c in memory.scan()["candidates"] if c["kind"] == kind]

    def test_same_input_same_candidates(self):
        self.make_memory()
        self.assertEqual([c["id"] for c in memory.scan()["candidates"]],
                         [c["id"] for c in memory.scan()["candidates"]])

    def test_long_line_proposal_fits(self):
        self.make_memory()
        [c] = self.by_kind("index_line")
        self.assertLessEqual(len(c["proposal"]), LINE_LIMIT)
        self.assertTrue(c["proposal"].startswith("- [긴 기억](long.md) — 항목 0번 정리"))

    def test_trim_moves_hook_and_undo_restores(self):
        mem = self.make_memory()
        before_index = (mem / "MEMORY.md").read_bytes()
        before_body = (mem / "long.md").read_bytes()
        [c] = self.by_kind("index_line")
        res = apply.index_trim(c["id"])
        index = (mem / "MEMORY.md").read_bytes().decode("utf-8")
        self.assertIn(c["proposal"] + "\r\n", index)  # CRLF 유지
        self.assertIn("항목 39번 정리", (mem / "long.md").read_text(encoding="utf-8"))
        self.assertEqual(self.by_kind("index_line"), [])
        self.assertTrue(list((self.data / "backup").rglob("*MEMORY.md")))
        apply.undo(res["entry"]["id"])
        self.assertEqual((mem / "MEMORY.md").read_bytes(), before_index)
        self.assertEqual((mem / "long.md").read_bytes(), before_body)

    def test_trim_rejects_bad_text(self):
        self.make_memory()
        [c] = self.by_kind("index_line")
        with self.assertRaises(ValueError):
            apply.index_trim(c["id"], "- [다른 기억](fresh.md) — 짧게")
        with self.assertRaises(ValueError):
            apply.index_trim(c["id"], "- [긴 기억](long.md) — " + "가" * LINE_LIMIT)

    def test_undo_skips_file_changed_after_apply(self):
        mem = self.make_memory()
        [c] = self.by_kind("index_line")
        res = apply.index_trim(c["id"])
        (mem / "MEMORY.md").write_text("사용자가 다시 고침\n", encoding="utf-8")
        out = apply.undo(res["entry"]["id"])
        self.assertIn("MEMORY.md", out["skipped"])
        self.assertEqual((mem / "MEMORY.md").read_text(encoding="utf-8"), "사용자가 다시 고침\n")

    def test_archive_moves_not_trash_and_undo(self):
        mem = self.make_memory()
        [c] = self.by_kind("archive")
        self.assertEqual(Path(c["path"]).name, "done.md")
        self.assertFalse(self.by_kind("archive")[1:])
        res = apply.archive(c["id"])
        self.assertFalse((mem / "done.md").exists())
        self.assertTrue((mem / "_archive" / "done.md").exists())
        self.assertNotIn("done.md", (mem / "MEMORY.md").read_text(encoding="utf-8"))
        self.assertEqual(self.trashed, [])
        apply.undo(res["entry"]["id"])
        self.assertTrue((mem / "done.md").exists())
        self.assertIn("done.md", (mem / "MEMORY.md").read_text(encoding="utf-8"))

    def test_review_only_candidates_have_no_action(self):
        mem = self.make_memory()
        (mem / "orphan.md").write_text("목차에 없음", encoding="utf-8")
        [c] = [c for c in self.by_kind("broken") if c["path"].endswith("orphan.md")]
        self.assertFalse(c["actionable"])
        with self.assertRaises(ValueError):
            apply.archive(c["id"])

    def test_unknown_id_rejected(self):
        self.make_memory()
        with self.assertRaises(ValueError):
            apply.archive("../../etc")


class BudgetTest(Base):
    """목차 예산(4,000바이트), 여러 줄 한 번에 줄이기, 기록 집계."""

    def make_big_index(self, lines=30):
        mem = self.project() / "memory"
        rows = []
        for i in range(lines):
            (mem / f"m{i:02d}.md").write_text(f"---\nname: m{i}\n---\n\n본문 {i}\n", encoding="utf-8")
            hook = f"기억 {i}번 요약, 진행 기록 가나다라마바사 {i}, 커밋 abc{i:04d} 반영(1차, 2차), 남은 일 아자차카"
            rows.append(f"- [기억 {i}](m{i:02d}.md) — {hook}")
        (mem / "MEMORY.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
        return mem

    def trims(self):
        return [c for c in memory.scan()["candidates"] if c["kind"] == "index_line"]

    def test_clauses_keep_parentheses(self):
        self.assertEqual(memory.clauses("가, 나(1, 2), 다"), ["가", "나(1, 2)", "다"])
        row = {"title": "t", "file": "f.md", "hook": "앞, 포폴 7차(21건 표현 수정, 86점) push 완료, 뒤"}
        out = memory.propose_line(row, 32)
        self.assertEqual(out.count("("), out.count(")"))

    def test_propose_keeps_description_before_progress_records(self):
        row = {"title": "t", "file": "f.md",
               "hook": "11/3 시작, 설명 핵심 문장, 커밋 abc1234 반영, 열 때 볼 것"}
        out = memory.propose_line(row, 32)
        self.assertIn("설명 핵심 문장", out)
        self.assertLessEqual(len(out), 32)
        self.assertNotIn("abc1234", out)
        self.assertNotIn("11/3", out)
        # 전부 진행 기록이면 예전처럼 앞에서부터 남깁니다.
        rec = {"title": "t", "file": "f.md", "hook": "11/3 시작, 11/4 이어서"}
        self.assertIn("11/3 시작", memory.propose_line(rec, 60))

    def test_budget_none_when_small(self):
        self.make_big_index(lines=3)
        [p] = memory.scan()["projects"]
        self.assertIsNone(p["budget"])
        self.assertEqual(self.trims(), [])

    def test_budget_finds_limit_under_index_limit(self):
        mem = self.make_big_index()
        [p] = memory.scan()["projects"]
        self.assertGreater(p["index_bytes"], INDEX_LIMIT)
        plan = p["budget"]
        self.assertTrue(plan["reachable"])
        self.assertLessEqual(plan["projected_bytes"], INDEX_LIMIT)
        trims = self.trims()
        self.assertTrue(trims)
        self.assertTrue(all(c["budget_only"] and len(c["proposal"]) <= plan["line"] for c in trims))
        # 모두 적용하면 예상대로 기준 안에 듭니다.
        res = apply.index_trim_many([{"id": c["id"]} for c in trims])
        self.assertLessEqual(len((mem / "MEMORY.md").read_bytes()), INDEX_LIMIT)
        self.assertEqual(res["saved_bytes"], p["index_bytes"] - len((mem / "MEMORY.md").read_bytes()))

    def test_budget_unreachable_is_reported(self):
        mem = self.project() / "memory"
        rows = []
        for i in range(120):
            (mem / f"m{i:03d}.md").write_text("본문\n", encoding="utf-8")
            rows.append(f"- [아주 긴 제목의 기억 번호 {i}번](m{i:03d}.md) — 짧은 설명")
        (mem / "MEMORY.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
        [p] = memory.scan()["projects"]
        self.assertFalse(p["budget"]["reachable"])
        self.assertEqual(p["budget"]["line"], BUDGET_MIN_LINE)

    def test_trim_many_one_entry_one_undo(self):
        mem = self.make_big_index()
        before = {p.name: p.read_bytes() for p in mem.glob("*.md")}
        picked = self.trims()[:3]
        res = apply.index_trim_many([{"id": c["id"]} for c in picked])
        self.assertEqual(len(apply.load_log()), 1)
        self.assertEqual(sum(op["path"].endswith("MEMORY.md") for op in res["entry"]["ops"]), 1)
        for c in picked:
            self.assertIn("## 목차에서 옮긴 기록", Path(c["path"]).read_text(encoding="utf-8"))
        apply.undo(res["entry"]["id"])
        self.assertEqual({p.name: p.read_bytes() for p in mem.glob("*.md")}, before)

    def test_trim_many_all_or_nothing(self):
        mem = self.make_big_index()
        before = (mem / "MEMORY.md").read_bytes()
        good, bad = self.trims()[:2]
        with self.assertRaises(ValueError):
            apply.index_trim_many([{"id": good["id"]}, {"id": bad["id"], "text": "- [딴 기억](zz.md) — 틀림"}])
        self.assertEqual((mem / "MEMORY.md").read_bytes(), before)
        self.assertEqual(apply.load_log(), [])

    def test_stats_undo_rate_and_saved(self):
        self.make_big_index()
        trims = self.trims()
        a = apply.index_trim_many([{"id": trims[0]["id"]}])
        b = apply.index_trim_many([{"id": trims[1]["id"]}])
        apply.undo(a["entry"]["id"])
        st = apply.stats()
        self.assertEqual((st["actions"], st["undone"], st["undo_rate"]), (2, 1, 50.0))
        self.assertEqual(st["index_bytes_saved"], b["saved_bytes"])


class VersionTest(Base):
    def make(self, folder: Path, names, days=30):
        folder.mkdir(parents=True, exist_ok=True)
        for n in names:
            (folder / n).write_text(n, encoding="utf-8")
            age(folder / n, days)

    def test_keeps_two_newest(self):
        self.make(self.work / "a", ["자소서_v1.md", "자소서_v2.md", "자소서_v3.md", "자소서_v10.md"])
        out = versions.scan([self.work])
        self.assertEqual(sorted(Path(c["path"]).name for c in out["candidates"]), ["자소서_v1.md", "자소서_v2.md"])
        self.assertEqual(out["kept"], 2)
        self.assertEqual([c["id"] for c in out["candidates"]], [c["id"] for c in versions.scan([self.work])["candidates"]])

    def test_recent_files_wait(self):
        self.make(self.work / "a", ["plan_v1.md", "plan_v2.md", "plan_v3.md"], days=3)
        self.assertEqual(versions.scan([self.work])["candidates"], [])

    def test_protected_names_and_desktop(self):
        self.make(self.work / "a", ["포폴_최종_v1.pdf", "포폴_최종_v2.pdf", "포폴_최종_v3.pdf"])
        self.make(self.work / "b", ["deck_final_v1.pptx", "deck_final_v2.pptx", "deck_final_v3.pptx"])
        self.make(self.desk / "c", ["메모_v1.txt", "메모_v2.txt", "메모_v3.txt"])
        out = versions.scan([self.work, self.desk])
        self.assertEqual(out["candidates"], [])
        self.assertEqual(out["guarded"], 3)

    def test_git_tracked_excluded(self):
        repo = self.work / "repo"
        self.make(repo, ["doc_v1.md", "doc_v2.md", "doc_v3.md", "note_v1.md", "note_v2.md", "note_v3.md"])
        subprocess.run(["git", "init", "-q", str(repo)], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "doc_v1.md"], check=True)
        names = [Path(c["path"]).name for c in versions.scan([self.work])["candidates"]]
        self.assertEqual(names, ["note_v1.md"])

    def test_trash_only_known_ids(self):
        self.make(self.work / "a", ["x_v1.md", "x_v2.md", "x_v3.md"])
        [c] = versions.scan([self.work])["candidates"]
        with mock.patch.object(versions, "work_roots", return_value=[self.work]):
            with self.assertRaises(ValueError):
                apply.trash_items([c["id"], "없는아이디"])
            self.assertEqual(self.trashed, [])
            res = apply.trash_items([c["id"]])
        self.assertEqual(self.trashed, [Path(c["path"])])
        self.assertIn("휴지통", res["message"])
        self.assertFalse(apply.undo(res["entry"]["id"])["ok"])  # 휴지통은 직접 복원


class SessionTest(Base):
    def log(self, name, days):
        folder = self.project()
        path = folder / f"{name}.jsonl"
        rows = [{"type": "user", "timestamp": "2026-09-01T00:00:00Z", "cwd": str(self.work)},
                {"type": "assistant", "timestamp": "2026-09-01T00:01:00Z",
                 "message": {"usage": {"input_tokens": 10, "cache_read_input_tokens": 90, "output_tokens": 5}}}]
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
        age(path, days)
        return path

    def test_open_and_recent_logs_are_not_candidates(self):
        self.log("open", 0)
        self.log("recent", 10)
        old = self.log("old", 40)
        out = sessions.scan()
        self.assertEqual(out["open"], 1)
        self.assertEqual([c["path"] for c in out["candidates"]], [str(old)])

    def test_summary_written_before_trash(self):
        old = self.log("old", 40)
        side = old.with_suffix("")
        (side / "subagents").mkdir(parents=True)
        (side / "subagents" / "a.jsonl").write_text("{}", encoding="utf-8")
        age(old, 40)
        [c] = sessions.scan()["candidates"]
        archive = self.data / "session-archive.jsonl"

        def check_then_send(path):
            if path == old:
                self.assertTrue(archive.exists(), "집계를 먼저 남겨야 합니다")
            self._send(path)

        with mock.patch("saerok_memory.trash.send", side_effect=check_then_send), \
                mock.patch.object(versions, "work_roots", return_value=[]):
            apply.trash_items([c["id"]])
        [row] = [json.loads(l) for l in archive.read_text(encoding="utf-8").splitlines()]
        self.assertEqual((row["session_id"], row["responses"], row["processed"], row["max_ctx"]), ("old", 1, 105, 100))
        self.assertFalse(side.exists())
        self.assertNotIn("message", row)


class HookTest(Base):
    def test_install_and_undo_keep_other_hooks(self):
        settings = self.claude / "settings.json"
        other = {"hooks": [{"type": "command", "command": "echo 다른 훅"}]}
        settings.write_text(json.dumps({"theme": "dark", "hooks": {"Stop": [other]}}), encoding="utf-8")
        res = apply.hook_install()
        self.assertTrue(apply.hook_installed())
        self.assertIn("이미", apply.hook_install()["message"])
        apply.undo(res["entry"]["id"])
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8")), {"theme": "dark", "hooks": {"Stop": [other]}})

    def test_install_without_settings_then_remove(self):
        apply.hook_install()
        self.assertTrue(apply.hook_installed())
        apply.hook_remove()
        self.assertFalse(apply.hook_installed())

    def test_hook_speaks_only_on_change(self):
        folder = self.project()
        (folder / "memory" / "MEMORY.md").write_text("- [a](a.md) — " + "가" * 200 + "\n", encoding="utf-8")
        stdin = json.dumps({"transcript_path": str(folder / "s.jsonl")})
        first = hook.run(stdin)
        self.assertIn("150자 넘는 줄 1개", json.loads(first)["systemMessage"])
        self.assertEqual(hook.run(stdin), "")
        self.assertEqual(hook.run("깨진 입력"), "")

    def test_hook_message_includes_budget(self):
        mem = BudgetTest.make_big_index(self)
        stdin = json.dumps({"transcript_path": str(mem.parent / "s.jsonl")})
        msg = json.loads(hook.run(stdin))["systemMessage"]
        plan = memory.scan()["projects"][0]["budget"]
        self.assertIn(f"줄마다 {plan['line']}자 안으로 줄이면 기준 안에 듭니다", msg)


if __name__ == "__main__":
    unittest.main()
