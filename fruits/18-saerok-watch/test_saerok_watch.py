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

from saerok_watch import apply, export, hook, scan, server, statusline  # noqa: E402


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

    def test_plugin_counts_as_installed_hook(self):
        (self.claude / "settings.json").write_text(json.dumps({"enabledPlugins": {"saerok-watch@saeroki": True}}), encoding="utf-8")
        self.assertIn("이미", apply.apply("hook_install")["message"])

    def test_hook_remove_keeps_other_hooks(self):
        settings = self.claude / "settings.json"
        other = {"hooks": [{"type": "command", "command": "echo other"}]}
        settings.write_text(json.dumps({"hooks": {"Stop": [other]}, "enabledPlugins": {}}), encoding="utf-8")
        apply.apply("hook_install")
        s = json.loads(settings.read_text(encoding="utf-8"))
        s["enabledPlugins"]["saerok-watch@saeroki"] = True
        settings.write_text(json.dumps(s), encoding="utf-8")
        from saerok_watch import advise
        self.assertIn("hook-duplicate", [x["id"] for x in advise.suggestions([], {"caution": 200_000, "warn": 400_000})])
        entry = apply.apply("hook_remove")["entry"]
        s = json.loads(settings.read_text(encoding="utf-8"))
        self.assertEqual(s["hooks"]["Stop"], [other])
        apply.undo(entry["id"])
        self.assertTrue(apply.hook_installed(json.loads(settings.read_text(encoding="utf-8"))))

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

    def test_falls_back_without_growth(self):
        # 플러그인으로 설치한 컴퓨터에는 저장소 루트의 growth.py가 없습니다.
        from saerok_watch import character
        with mock.patch.object(character, "_growth", side_effect=ImportError):
            rows, colors = character.sentry_sprite()
            self.assertEqual(rows, list(character.FALLBACK))
            self.assertTrue(set("".join(rows)) - {" "} <= set(colors))
            self.assertTrue(character.render_png().startswith(bytes([0x89]) + b"PNG"))


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


class SpikeTest(Sandbox):
    def test_finds_spike_and_its_cause(self):
        # 파일 읽기 결과 9만 글자(약 3만 토큰)가 들어온 뒤 컨텍스트가 3만 커지면 급증으로 잡습니다.
        path = self.write_transcript("s1", [
            user("시작"),
            assistant("m1", 50_000, tools=[("t1", "Read", {"file_path": "C:/big/data.csv"})]),
            user([{"type": "tool_result", "tool_use_id": "t1", "content": "x" * 90_000}]),
            assistant("m2", 80_000),
            user("작은 질문"),
            assistant("m3", 81_000),
            {"type": "attachment", "attachment": {"type": "deferred_tools_delta"}, "rendered": [{"content": "t" * 120_000}]},
            assistant("m4", 125_000),
        ])
        s = scan.scan_file(path)
        self.assertEqual(s["timeline"], [50_000, 80_000, 81_000, 125_000])
        self.assertEqual(len(s["spikes"]), 2)
        # Claude Code가 끼워 넣은 도구 목록(첨부)도 원인으로 잡습니다.
        self.assertEqual(s["spikes"][0]["causes"][0]["kind"], "도구·스킬·지침 목록")
        spike = s["spikes"][1]
        self.assertEqual((spike["n"], spike["delta"]), (2, 30_000))
        self.assertEqual(spike["causes"][0]["kind"], "파일 읽기")
        self.assertEqual(spike["causes"][0]["target"], "data.csv")
        self.assertIn("파일 읽기", scan.spike_summary([s]))

    def test_explain_scales_down_and_fills_rest(self):
        big = scan.explain(10_000, [{"kind": "명령 출력", "tokens": 40_000}])
        self.assertEqual(big[0]["tokens"], 10_000)
        small = scan.explain(30_000, [{"kind": "명령 출력", "tokens": 5_000}])
        self.assertEqual([c["kind"] for c in small], [scan.OTHER, "명령 출력"])
        self.assertEqual(sum(c["tokens"] for c in small), 30_000)

    def test_downsample_keeps_peaks(self):
        values = [1] * 1000
        values[517] = 99
        out = scan.downsample(values, points=100)
        self.assertEqual(len(out), 100)
        self.assertIn([518, 99], out)
        self.assertEqual(scan.downsample([5, 6]), [[1, 5], [2, 6]])


class StatuslineTest(Sandbox):
    config = {"caution": 200_000, "warn": 300_000}

    def test_line_by_level(self):
        self.assertEqual(statusline.line(182_000, self.config, color=False), "🪖 18.2만 █████░░░ 주의까지 1.8만")
        self.assertIn("경고까지 5.0만", statusline.line(250_000, self.config, color=False))
        over = statusline.line(340_000, self.config, color=False)
        self.assertIn("████████ 경고 넘음 +4.0만 · 새 세션 권장", over)
        self.assertIn("[31m", statusline.line(340_000, self.config))

    def test_context_from_payload_or_transcript(self):
        usage = {"input_tokens": 10, "cache_read_input_tokens": 100_000, "cache_creation_input_tokens": 90}
        self.assertEqual(statusline.context_from({"context_window": {"current_usage": usage}}), 100_100)
        path = self.write_transcript("s1", [user("hi"), assistant("m1", 120_000)])
        payload = {"context_window": {"current_usage": None}, "transcript_path": str(path)}
        self.assertEqual(statusline.context_from(payload), 120_000)
        self.assertEqual(statusline.context_from({}), 0)

    def test_main_never_fails(self):
        out = io.BytesIO()
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"not json"))),                 mock.patch.object(sys, "stdout", io.TextIOWrapper(out)):
            self.assertEqual(statusline.main(), 0)
            sys.stdout.flush()
            text = out.getvalue().decode("utf-8")
        self.assertIn("파수꾼 대기 중", text)

    def test_install_and_undo(self):
        settings = self.claude / "settings.json"
        old = {"type": "command", "command": "my-line"}
        settings.write_text(json.dumps({"statusLine": old}), encoding="utf-8")
        entry = apply.apply("statusline_install")["entry"]
        s = json.loads(settings.read_text(encoding="utf-8"))
        self.assertTrue(apply.statusline_installed(s))
        self.assertIn("saerok_watch statusline", s["statusLine"]["command"])
        self.assertIn("이미", apply.apply("statusline_install")["message"])
        apply.undo(entry["id"])
        self.assertEqual(json.loads(settings.read_text(encoding="utf-8"))["statusLine"], old)


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

    def test_session_detail(self):
        sid = json.loads(urllib.request.urlopen(self.base + "/api/summary", timeout=10).read())["sessions"][0]["session_id"]
        d = json.loads(urllib.request.urlopen(self.base + "/api/session?id=" + sid, timeout=10).read())
        self.assertEqual(d["timeline"], [[1, 120_000]])
        with self.assertRaises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(self.base + "/api/session?id=nope", timeout=5)
        self.assertEqual(err.exception.code, 404)

    def test_blocks_path_traversal(self):
        with self.assertRaises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(self.base + "/../saerok_watch/apply.py", timeout=5)
        self.assertEqual(err.exception.code, 404)


if __name__ == "__main__":
    unittest.main()
