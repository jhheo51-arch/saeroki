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
from saerok_memory.store import LINE_LIMIT

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


if __name__ == "__main__":
    unittest.main()
