"""새록 파수꾼 검사. 실제 ~/.claude는 건드리지 않고 임시 폴더만 씁니다."""

import io
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))

from saerok_watch import apply, export, hook, scan, server  # noqa: E402


def assistant(msg_id, ctx, ts="2026-10-16T01:00:00Z", tools=()):
    content = [{"type": "tool_use", "id": t[0], "name": t[1], "input": t[2] if len(t) > 2 else {}} for t in tools]
    return {"type": "assistant", "timestamp": ts, "cwd": "C:/work/saeroki",
            "message": {"id": msg_id, "content": content or [{"type": "text", "text": "ok"}],
                        "usage": {"input_tokens": 10, "cache_read_input_tokens": ctx - 10, "output_tokens": 5}}}


def user(content, ts="2026-10-16T01:00:01Z"):
    return {"type": "user", "timestamp": ts, "message": {"content": content}}


class Sandbox(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.claude = root / "claude"
        (self.claude / "projects" / "p").mkdir(parents=True)
        self.claude_json = root / "claude.json"
        self.env = mock.patch.dict(os.environ, {
            "SAEROK_WATCH_CLAUDE_HOME": str(self.claude),
            "SAEROK_WATCH_CLAUDE_JSON": str(self.claude_json),
            "SAEROK_WATCH_HOME": str(root / "watch"),
        })
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def write_transcript(self, name, rows):
        path = self.claude / "projects" / "p" / f"{name}.jsonl"
        path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
        return path


class ScanTest(Sandbox):
    def test_counts_split_response_once(self):
        # 한 응답이 블록마다 두 줄로 저장돼도 한 번만 셉니다.
        path = self.write_transcript("s1", [
            user("새록 파수꾼 만들어 줘"),
            assistant("m1", 250_000, tools=[("t1", "Read")]),
            assistant("m1", 250_000),
            user([{"type": "tool_result", "tool_use_id": "t1", "content": [{"type": "text", "text": "x" * 100},
                                                                             {"type": "image", "source": {}}]}]),
            assistant("m2", 350_000, tools=[("t2", "mcp__rea__open_binary"), ("t3", "Skill", {"skill": "saerok-sql"})]),
        ])
        s = scan.scan_file(path)
        self.assertEqual(s["responses"], 2)
        self.assertEqual(s["processed"], 600_000)
        self.assertEqual(s["max_ctx"], 350_000)
        self.assertEqual(s["buckets"], [0, 250_000, 350_000, 0])
        self.assertEqual(s["images"], 1)
        self.assertEqual(s["tool_chars"]["Read"], 100)
        self.assertEqual(s["mcp_used"], {"rea": 1})
        self.assertEqual(s["skills_used"], {"saerok-sql": 1})
        self.assertEqual(s["title"], "새록 파수꾼 만들어 줘")
        self.assertEqual(s["project"], "saeroki")

    def test_cap_simulation_lowers_large_contexts_only(self):
        small = {"buckets": [100, 0, 0, 0]}
        big = {"buckets": [0, 0, 0, 100]}
        self.assertEqual(scan.simulate_cap([small], 200_000), 1.0)
        self.assertLess(scan.simulate_cap([big], 200_000), 0.25)


class HookTest(Sandbox):
    def setUp(self):
        super().setUp()
        # 검사 중에는 진짜 Windows 알림을 띄우지 않고 부른 기록만 남깁니다.
        patcher = mock.patch("saerok_watch.notify.toast")
        self.toast = patcher.start()
        self.addCleanup(patcher.stop)

    def test_toast_follows_config(self):
        from saerok_watch import store
        path = self.write_transcript("abc", [user("hi"), assistant("m1", 210_000)])
        self.run_hook(path)
        title, body = self.toast.call_args.args
        self.assertIn("파수꾼 새록이 · 주의", title)
        store.save_config(200_000, 400_000, toast=False)
        self.toast.reset_mock()
        path = self.write_transcript("abc", [user("hi"), assistant("m1", 210_000), assistant("m2", 450_000)])
        self.assertIn("경고", self.run_hook(path))
        self.toast.assert_not_called()

    def run_hook(self, path):
        stdin = io.TextIOWrapper(io.BytesIO(json.dumps({"session_id": "abc", "transcript_path": str(path)}).encode()))
        out = io.BytesIO()
        with mock.patch.object(sys, "stdin", stdin), mock.patch.object(sys, "stdout", mock.Mock(buffer=out)):
            self.assertEqual(hook.main(), 0)
        return json.loads(out.getvalue() or b"{}").get("systemMessage")

    def test_warns_once_per_level_and_again_after_shrinking(self):
        rows = [user("hi"), assistant("m1", 150_000)]
        path = self.write_transcript("abc", rows)
        self.assertIsNone(self.run_hook(path))
        rows.append(assistant("m2", 210_000)); path = self.write_transcript("abc", rows)
        self.assertIn("주의", self.run_hook(path))
        rows.append(assistant("m3", 220_000)); path = self.write_transcript("abc", rows)
        self.assertIsNone(self.run_hook(path))
        rows.append(assistant("m4", 410_000)); path = self.write_transcript("abc", rows)
        self.assertIn("경고", self.run_hook(path))
        rows.append(assistant("m5", 90_000)); path = self.write_transcript("abc", rows)
        self.assertIsNone(self.run_hook(path))
        rows.append(assistant("m6", 205_000)); path = self.write_transcript("abc", rows)
        self.assertIn("주의", self.run_hook(path))

    def test_never_fails_on_bad_input(self):
        out = io.BytesIO()
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"not json"))), \
                mock.patch.object(sys, "stdout", mock.Mock(buffer=out)):
            self.assertEqual(hook.main(), 0)
        self.assertEqual(out.getvalue(), b"")


class ApplyTest(Sandbox):
    def test_apply_and_undo_restore_only_changed_keys(self):
        settings = self.claude / "settings.json"
        settings.write_text(json.dumps({"theme": "dark", "enabledPlugins": {"superpowers@x": True}}), encoding="utf-8")
        self.claude_json.write_text(json.dumps({"mcpServers": {"rea": {}}, "projects": {
            "C:/a": {}, "C:/b": {"disabledMcpServers": ["other"]}}}), encoding="utf-8")

        hook_entry = apply.apply("hook_install")["entry"]
        compact = apply.apply("autocompact:200000")["entry"]
        mcp = apply.apply("mcp_off:rea")["entry"]
        plugin = apply.apply("plugin_off:superpowers@x")["entry"]
        s = json.loads(settings.read_text(encoding="utf-8"))
        cj = json.loads(self.claude_json.read_text(encoding="utf-8"))
        self.assertTrue(apply.hook_installed(s))
        self.assertEqual(s["autoCompactWindow"], 200000)
        self.assertFalse(s["enabledPlugins"]["superpowers@x"])
        self.assertEqual(cj["projects"]["C:/b"]["disabledMcpServers"], ["other", "rea"])
        self.assertIn("이미", apply.apply("autocompact:200000")["message"])

        # 사용자가 적용 뒤에 다른 키를 바꿔도 되돌리기는 그 키를 건드리지 않습니다.
        s["theme"] = "light"
        settings.write_text(json.dumps(s), encoding="utf-8")
        for entry in (plugin, mcp, compact, hook_entry):
            apply.undo(entry["id"])
        s = json.loads(settings.read_text(encoding="utf-8"))
        cj = json.loads(self.claude_json.read_text(encoding="utf-8"))
        self.assertEqual(s["theme"], "light")
        self.assertNotIn("autoCompactWindow", s)
        self.assertTrue(s["enabledPlugins"]["superpowers@x"])
        self.assertFalse(apply.hook_installed(s))
        self.assertNotIn("disabledMcpServers", cj["projects"]["C:/a"])
        self.assertEqual(cj["projects"]["C:/b"]["disabledMcpServers"], ["other"])
        self.assertTrue(any((Path(os.environ["SAEROK_WATCH_HOME"]) / "backups").iterdir()))

    def test_undo_skips_key_changed_after_apply(self):
        settings = self.claude / "settings.json"
        settings.write_text("{}", encoding="utf-8")
        entry = apply.apply("autocompact:200000")["entry"]
        settings.write_text(json.dumps({"autoCompactWindow": 300000}), encoding="utf-8")
        result = apply.undo(entry["id"])
        self.assertEqual(result["skipped"], ["autoCompactWindow"])
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8"))["autoCompactWindow"], 300000)

    def test_rejects_unknown_or_bad_actions(self):
        with self.assertRaises(ValueError):
            apply.apply("rm -rf")
        with self.assertRaises(ValueError):
            apply.apply("autocompact:5")


class CharacterTest(unittest.TestCase):
    def test_sentry_holds_rifle_at_each_stage(self):
        from saerok_watch import character
        for level in (1, 10, 60, 100):
            rows, colors = character.sentry_sprite(level)
            text = "".join(rows)
            self.assertIn("E", text)  # 새록이 눈
            self.assertIn("h", text)  # 소총 가늠자·소염기
            self.assertTrue(set(text) - {" "} <= set(colors))
        self.assertTrue(character.render_png(10).startswith(b"\x89PNG"))
        self.assertIn("K-2", character.render_svg(10))


class ExportTest(Sandbox):
    def test_public_rows_have_numbers_only(self):
        self.write_transcript("s1", [user("비밀 프로젝트 제목"), assistant("m1", 320_000)])
        out = Path(self.tmp.name) / "public.json"
        export.export(scan.scan_all(use_cache=False), out)
        text = out.read_text(encoding="utf-8")
        self.assertNotIn("비밀", text)
        self.assertNotIn("saeroki", text)
        self.assertNotIn("s1", text)
        day = json.loads(text)["days"][0]
        self.assertEqual(set(day), {"date", "sessions", "responses", "processed", "max_ctx", "images", "over300_share"})
        self.assertEqual(day["over300_share"], 1.0)


class ServerTest(Sandbox):
    def setUp(self):
        super().setUp()
        (self.claude / "settings.json").write_text("{}", encoding="utf-8")
        self.write_transcript("s1", [user("hi"), assistant("m1", 120_000)])
        server.Handler.token = "secret-token"
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.base = f"http://127.0.0.1:{self.httpd.server_port}"
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        super().tearDown()

    def post(self, path, body, token=None):
        req = urllib.request.Request(self.base + path, data=json.dumps(body).encode(), method="POST",
                                     headers={"Content-Type": "application/json", **({"X-Saerok-Token": token} if token else {})})
        return urllib.request.urlopen(req, timeout=5)

    def test_summary_and_page_token(self):
        summary = json.loads(urllib.request.urlopen(self.base + "/api/summary", timeout=10).read())
        self.assertEqual(summary["totals"]["responses"], 1)
        page = urllib.request.urlopen(self.base + "/", timeout=5).read().decode("utf-8")
        self.assertIn("secret-token", page)

    def test_apply_requires_token(self):
        with self.assertRaises(urllib.error.HTTPError) as err:
            self.post("/api/apply", {"action": "autocompact:200000"})
        self.assertEqual(err.exception.code, 403)
        res = json.loads(self.post("/api/apply", {"action": "autocompact:200000"}, "secret-token").read())
        self.assertTrue(res["ok"])

    def test_blocks_path_traversal(self):
        with self.assertRaises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(self.base + "/../saerok_watch/apply.py", timeout=5)
        self.assertEqual(err.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
