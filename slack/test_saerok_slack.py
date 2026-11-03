"""새록 슬랙 검사. 슬랙·Claude Code에는 접속하지 않습니다."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from saerok_slack import app, config, dictionary, game, mystery, runner

TERMS = [
    {"id": "retention", "term": "리텐션", "original": "Retention", "korean": "리텐션", "aliases": ["잔존율"],
     "senses": [{"definition": "다시 돌아온 사용자 비율입니다.", "formula": "재방문 ÷ 전체", "examples": ["리텐션이 올랐어요."],
                 "sources": [{"title": "공식 문서", "url": "https://example.com/r", "kind": "official", "checked_at": "2026-10-15"}],
                 "status": "verified"}],
     "related": [{"term": "코호트", "note": ""}], "confusable": []},
    {"id": "churn", "term": "이탈률", "original": "Churn Rate", "korean": "이탈률", "aliases": [],
     "senses": [{"definition": "떠난 사용자 비율입니다.", "examples": ["이탈률이 높아요."], "sources": [], "status": "needs_check"}],
     "related": [], "confusable": []},
]


class DictionaryTest(unittest.TestCase):
    def test_alias_and_case(self):
        self.assertIn("*리텐션* (Retention)", dictionary.answer("retention", TERMS))
        self.assertIn("다시 돌아온", dictionary.answer("잔존율", TERMS))

    def test_shows_source_and_unchecked_mark(self):
        self.assertIn("<https://example.com/r|공식 문서> · 확인 2026-10-15", dictionary.answer("리텐션", TERMS))
        self.assertIn("확인 필요", dictionary.answer("이탈률", TERMS))

    def test_unknown_term_is_not_invented(self):
        text = dictionary.answer("리텐숀", TERMS)
        self.assertIn("아직 없습니다", text)
        self.assertIn("리텐션", text)

    def test_today_prefers_verified(self):
        from datetime import date
        for n in range(3):
            self.assertIn("리텐션", dictionary.today(TERMS, date(2026, 11, 3 + n)))

    def test_real_glossary_loads(self):
        terms = dictionary.load()
        self.assertGreater(len(terms), 100)
        self.assertIn("전환율", dictionary.answer("CVR", terms))


class RunnerTest(unittest.TestCase):
    def test_command_limits_tools_and_loads_plugin(self):
        with mock.patch.object(runner, "claude_path", return_value="claude"):
            cmd = runner.build_command(runner.FRUITS["idea"], "/saerok-idea:judge 아이디어", "abc", resume=False)
        tools = cmd[cmd.index("--allowedTools") + 1]
        self.assertIn("Bash(saerok-idea:*)", tools)
        self.assertNotIn("Bash,", tools + ",")  # 아무 명령이나 허용하지 않음
        self.assertEqual(cmd[cmd.index("--plugin-dir") + 1], str(runner.FRUITS_DIR / "20-saerok-idea"))
        self.assertEqual(cmd[cmd.index("--session-id") + 1], "abc")

    def test_resume(self):
        with mock.patch.object(runner, "claude_path", return_value="claude"):
            cmd = runner.build_command(runner.FRUITS["sql"], "더 알려 줘", "abc", resume=True)
        self.assertEqual(cmd[cmd.index("--resume") + 1], "abc")
        self.assertNotIn("--plugin-dir", cmd)

    def test_chat_has_no_tools(self):
        with mock.patch.object(runner, "claude_path", return_value="claude"):
            cmd = runner.build_command(runner.FRUITS["chat"], "<@U1>: 안녕", "abc", resume=False)
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        for flag in ("--strict-mcp-config", "--disable-slash-commands", "--system-prompt"):
            self.assertIn(flag, cmd)
        for flag in ("--allowedTools", "--add-dir", "--plugin-dir", "--append-system-prompt"):
            self.assertNotIn(flag, cmd)

    def test_plugin_folders_exist(self):
        for fruit in runner.FRUITS.values():
            if fruit.plugin:
                self.assertTrue((runner.FRUITS_DIR / fruit.plugin / ".claude-plugin" / "plugin.json").exists(), fruit.key)

    def test_parse_output(self):
        self.assertEqual(runner.parse_output(json.dumps({"result": "답", "is_error": False})), ("답", False))
        text, failed = runner.parse_output(json.dumps({"result": "일부", "permission_denials": [{"tool_name": "Bash"}]}))
        self.assertIn("막혔습니다: Bash", text)
        self.assertTrue(runner.parse_output("깨진 출력")[1])

    def test_threads_saved_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = runner.Threads(Path(tmp) / "t.json")
            store.put("1.2", runner.Threads.new(runner.FRUITS["sql"], "C1", False))
            self.assertEqual(runner.Threads(Path(tmp) / "t.json").get("1.2")["fruit"], "sql")


class AppTest(unittest.TestCase):
    def test_chunks_keep_everything(self):
        text = "\n".join(f"줄 {i} " + "가" * 50 for i in range(500))
        parts = app.chunks(text, 1000)
        self.assertTrue(all(len(p) <= 1000 for p in parts))
        self.assertEqual("".join(parts), text)

    def test_wants_file(self):
        self.assertTrue(app.wants_file(runner.FRUITS["interview"], ""))
        self.assertTrue(app.wants_file(runner.FRUITS["prd"], "검사"))
        self.assertFalse(app.wants_file(runner.FRUITS["prd"], "동네 중고 거래 앱"))
        self.assertFalse(app.wants_file(runner.FRUITS["sql"], ""))

    def test_manifest_matches_commands(self):
        manifest = json.loads((Path(app.__file__).parent / "manifest.json").read_text(encoding="utf-8"))
        names = {c["command"] for c in manifest["features"]["slash_commands"]}
        self.assertEqual(names, set(app.COMMANDS) | {"/saerok-dict", "/saerok-word", "/saerok-case", "/saerok-master"})
        self.assertTrue(manifest["settings"]["socket_mode_enabled"])
        # 봇 표시 이름은 영어 소문자·숫자·-_.만 받습니다.
        self.assertRegex(manifest["features"]["bot_user"]["display_name"], r"^[a-z0-9._-]{1,80}$")
        for c in manifest["features"]["slash_commands"]:  # 슬랙은 빈 칸을 거절합니다.
            self.assertTrue(c["description"] and c["usage_hint"], c["command"])

    def test_open_root_joins_or_moves_to_dm(self):
        from slack_sdk.errors import SlackApiError
        missing = SlackApiError("x", {"error": "not_in_channel"})
        bot = app.Bot.__new__(app.Bot)
        bot.owner = "U0OWNER"

        client = mock.Mock()
        client.chat_postMessage.side_effect = [missing, {"ts": "1.1"}]
        self.assertEqual(bot.open_root(client, "C1", "글"), ("C1", "1.1"))
        client.conversations_join.assert_called_once_with(channel="C1")

        client = mock.Mock()
        client.chat_postMessage.side_effect = [SlackApiError("x", {"error": "channel_not_found"}), {"ts": "2.2"}]
        client.conversations_join.side_effect = SlackApiError("x", {"error": "method_not_supported_for_channel_type"})
        client.conversations_open.return_value = {"channel": {"id": "D9"}}
        self.assertEqual(bot.open_root(client, "G1", "글"), ("D9", "2.2"))
        client.conversations_open.assert_called_once_with(users="U0OWNER")

    def test_chat_mention_from_anyone(self):
        with tempfile.TemporaryDirectory() as tmp:
            bot = app.Bot.__new__(app.Bot)
            bot.owner, bot.bot_user, bot.chat_channels = "U0OWNER", "UBOT", {"C0CHAT"}
            bot.threads = runner.Threads(Path(tmp) / "t.json")
            bot.process = mock.Mock()
            event = {"channel": "C0CHAT", "user": "U0OTHER", "ts": "5.5", "text": "<@UBOT> 안녕?"}
            bot.on_message(event, mock.Mock())
            self.assertEqual(bot.process.call_args.args[3], "<@U0OTHER>: 안녕?")
            self.assertEqual(bot.threads.get("5.5")["fruit"], "chat")
            # 스레드에서는 부르지 않아도 이어 가고, 다른 채널이나 부르지 않은 글에는 답하지 않습니다.
            bot.on_message({"channel": "C0CHAT", "user": "U0THIRD", "ts": "5.6", "thread_ts": "5.5", "text": "나도"}, mock.Mock())
            self.assertEqual(bot.process.call_count, 2)
            bot.on_message({"channel": "C0CHAT", "user": "U0OTHER", "ts": "6.0", "text": "그냥 글"}, mock.Mock())
            bot.on_message({"channel": "C0ELSE", "user": "U0OTHER", "ts": "7.0", "text": "<@UBOT> 안녕"}, mock.Mock())
            self.assertEqual(bot.process.call_count, 2)

    def test_safe_name(self):
        self.assertEqual(app.safe_name('a b/c:"d".md'), "a_b_c_d_.md")

    def bot(self, tmp):
        bot = app.Bot.__new__(app.Bot)
        bot.owner, bot.bot_user, bot.chat_channels = "U0OWNER", "UBOT", {"C0CHAT"}
        bot.threads = runner.Threads(Path(tmp) / "t.json")
        bot.words, bot.game_lock, bot.busy, bot.started_at, bot.last_error = ["기차", "차표"], app.threading.Lock(), set(), 0, None
        bot.cases = mystery.load()
        bot.process = mock.Mock()
        return bot

    def test_word_game_in_thread_from_anyone(self):
        with tempfile.TemporaryDirectory() as tmp:
            bot = self.bot(tmp)
            client = mock.Mock()
            client.chat_postMessage.return_value = {"ts": "8.8"}
            bot.on_word(mock.Mock(), {"channel_id": "C1", "user_id": "U0OTHER", "text": "자기"}, client, mock.Mock())
            self.assertIn("*기차*", client.chat_postMessage.call_args.kwargs["text"])
            bot.on_message({"channel": "C1", "user": "U0THIRD", "ts": "8.9", "thread_ts": "8.8", "text": "차표"}, client)
            self.assertIn("졌어요", client.chat_postMessage.call_args.kwargs["text"])
            bot.process.assert_not_called()  # 끝말잇기는 AI를 부르지 않습니다.

    def test_master_owner_only_and_resting(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(config, "HOME", Path(tmp)):
            bot = self.bot(tmp)
            respond = mock.Mock()
            bot.on_master(mock.Mock(), {"user_id": "U0OTHER", "channel_id": "C1", "text": "쉬기"}, mock.Mock(), respond)
            self.assertIn("주인만", respond.call_args.args[0])
            self.assertFalse(config.resting())
            bot.on_master(mock.Mock(), {"user_id": "U0OWNER", "channel_id": "C1", "text": "쉬기"}, mock.Mock(), respond)
            self.assertTrue(config.resting())
            client = mock.Mock()
            bot.on_message({"channel": "C0CHAT", "user": "U0OTHER", "ts": "9.0", "text": "<@UBOT> 안녕"}, client)
            self.assertIn("쉬는 중", client.chat_postMessage.call_args.kwargs["text"])
            bot.process.assert_not_called()
            bot.on_message({"channel": "C0CHAT", "user": "U0OWNER", "ts": "9.1", "text": "<@UBOT> 안녕"}, client)
            bot.process.assert_called_once()  # 주인은 쉬는 중에도 부를 수 있습니다.
            self.assertIn("새록이 상태", bot.master("", "C1", mock.Mock()))
            bot.master("대화 켜기", "C0NEWCHAN1", mock.Mock())
            self.assertIn("C0NEWCHAN1", config.chat_channels())
            self.assertIn("C0NEWCHAN1", bot.chat_channels)
            self.assertIn("DM", bot.master("대화 켜기", "D0DMCHAN11", mock.Mock()))

    def test_case_game_in_thread_and_series(self):
        with tempfile.TemporaryDirectory() as tmp:
            bot = self.bot(tmp)
            client = mock.Mock()
            client.chat_postMessage.return_value = {"ts": "3.3"}
            bot.on_case(mock.Mock(), {"channel_id": "C1", "user_id": "U0OTHER", "text": ""}, client, mock.Mock())
            self.assertIn("제1화", client.chat_postMessage.call_args.kwargs["text"])
            bot.on_message({"channel": "C1", "user": "U0THIRD", "ts": "3.4", "thread_ts": "3.3", "text": "단서"}, client)
            self.assertIn("단서 1", client.chat_postMessage.call_args.kwargs["text"])
            bot.on_message({"channel": "C1", "user": "U0OTHER", "ts": "3.5", "thread_ts": "3.3", "text": "범인 쪼르"}, client)
            self.assertIn("정답", client.chat_postMessage.call_args.kwargs["text"])
            bot.process.assert_not_called()  # 추리 게임은 AI를 부르지 않습니다.
            client.chat_postMessage.return_value = {"ts": "4.4"}
            bot.on_case(mock.Mock(), {"channel_id": "C1", "user_id": "U0OTHER", "text": ""}, client, mock.Mock())
            self.assertIn("제2화", client.chat_postMessage.call_args.kwargs["text"])  # 푼 사건 다음 회차
            respond = mock.Mock()
            bot.on_case(mock.Mock(), {"channel_id": "C1", "user_id": "U0OTHER", "text": "목록"}, client, respond)
            self.assertIn("✅ 제1화", respond.call_args.args[0])

    def test_offline_detected(self):
        self.assertTrue(runner.offline("Invalid API key · Please run /login"))
        self.assertTrue(runner.offline("Claude AI usage limit reached|1793"))
        self.assertFalse(runner.offline("사과 401개"))


class GameTest(unittest.TestCase):
    def test_dueum(self):
        self.assertEqual(game.starts("력"), {"력", "역"})
        self.assertEqual(game.starts("라"), {"라", "나"})
        self.assertEqual(game.starts("녀"), {"녀", "여"})
        self.assertEqual(game.starts("기"), {"기"})

    def test_rules(self):
        record = game.new("C1")
        words = ["역사", "사자", "자두"]
        record["last"], record["used"] = "달력", ["달력"]
        self.assertIn("*사자*", game.play(record, "역사", words))  # 두음법칙: 력 → 역
        self.assertIn("‘자’", game.play(record, "사과", words))
        self.assertIn("이미", game.play({**record, "last": "가역"}, "역사", words))
        self.assertIsNone(game.play(record, "ㅋㅋ 좋다", words))
        reply = game.play(record, "자유", words)  # 단어장에 없는 말, 새록이는 ‘유’로 이을 말이 없음
        self.assertIn("믿을게요", reply)
        self.assertIn("제가 졌어요", reply)
        self.assertIsNone(game.play(record, "유리", words))  # 끝난 판
        record = game.new("C1")
        record["last"] = "기차"
        self.assertIn("이겼어요", game.play(record, "졌다", words))

    def test_real_words_load(self):
        words = game.load()
        self.assertGreater(len(words), 500)
        self.assertEqual(len(words), len(set(words)))


class MysteryTest(unittest.TestCase):
    def test_cases_are_solvable(self):
        book = mystery.load()
        self.assertGreaterEqual(len(book["cases"]), 3)
        self.assertEqual([c["id"] for c in book["cases"]], list(range(1, len(book["cases"]) + 1)))
        for case in book["cases"]:
            names = [s["name"] for s in case["suspects"]]
            self.assertIn(case["culprit"], names, case["title"])
            self.assertIn(case["culprit"], case["solution"])
            self.assertGreaterEqual(len(case["clues"]), 3)
            for s in case["suspects"]:  # 이름을 부르면 그 동물 한 명만 나와야 합니다.
                self.assertEqual(mystery.suspect_in(case, "범인 " + s["name"]), [s], s["name"])

    def test_wrong_guesses_and_chatter(self):
        book = mystery.load()
        record = mystery.new("C1", mystery.find(book, 1), "U1")
        self.assertIsNone(mystery.play(record, "어렵다 ㅋㅋ", book))
        self.assertIn("“", mystery.play(record, "꿀꿀", book))
        self.assertIn("꿀꿀은 범인이 아니에요", mystery.play(record, "범인 꿀꿀", book))
        self.assertIn("한 명만", mystery.play(record, "범인 꿀꿀 쪼르", book))
        self.assertIn("사건 종료", mystery.play(record, "범인 토리", book))
        self.assertFalse(record["solved"])
        self.assertIsNone(mystery.play(record, "범인 쪼르", book))  # 끝난 사건
        record = mystery.new("C1", mystery.find(book, 2), "U1")
        for _ in range(6):
            mystery.play(record, "단서", book)
        self.assertEqual(record["clues"], 5)
        self.assertIn("너굴", mystery.play(record, "포기", book))


class ConfigTest(unittest.TestCase):
    def test_check_formats(self):
        self.assertEqual(config.check("owner", " U0ABCDEF12 "), "U0ABCDEF12")
        with self.assertRaises(ValueError):
            config.check("bot-token", "xapp-1-abc")
        self.assertEqual(config.masked("bot-token", "xoxb-1234567890-abcd"), "xoxb-1234…abcd")

    def test_chat_channels_saved(self):
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(config, "HOME", Path(tmp)):
            config.set_chat_channel("C0CF57Y2E48")
            self.assertEqual(config.chat_channels(), ["C0CF57Y2E48"])
            config.set_chat_channel("C0CF57Y2E48", on=False)
            self.assertEqual(config.chat_channels(), [])
            with self.assertRaises(ValueError):
                config.set_chat_channel("agent-saeroki")


if __name__ == "__main__":
    unittest.main()
