"""슬랙 Socket Mode 봇. 슬래시 명령으로 스레드를 열고, 그 스레드 답글로 대화를 이어 갑니다."""

from __future__ import annotations

import re
import threading
import time
import urllib.request
from pathlib import Path

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.errors import SlackApiError

from . import config, dictionary, game, mystery
from .runner import FRUITS, Fruit, Threads, check, inbox_dir, offline, run

CHUNK = 11000  # markdown 블록 한 메시지 한도(12,000자)보다 조금 작게
COMMANDS = {"/saerok-sql": "sql", "/saerok-idea": "idea", "/saerok-prd": "prd", "/saerok-interview": "interview"}
NOT_OWNER = "새록이는 이 PC 주인만 부를 수 있습니다. `/saerok-dict` 사전, `/saerok-word` 끝말잇기, `/saerok-case` 숲속 추리는 누구나 쓸 수 있습니다."
FREE = "그동안에도 `/saerok-dict` 사전, `/saerok-dict` 오늘의 용어, `/saerok-word` 끝말잇기, `/saerok-case` 숲속 추리는 그대로 쓸 수 있어요."
RESTING = "🌙 새록이는 지금 쉬는 중이에요. " + FREE
OFFLINE = "🌙 새록이 AI가 지금 답할 수 없어요(주인의 Claude 로그인, 구독, 사용 한도 중 하나를 확인해야 해요). " + FREE
MASTER_HELP = """*🌳 마스터 명령* (주인에게만 보입니다)
• `/saerok-master` 또는 `상태`: 켜진 시간, AI 상태, 대화 채널, 처리 중인 일
• `점검`: AI가 지금 답할 수 있는지 짧게 물어봅니다(구독·로그인 확인)
• `쉬기` / `깨우기`: 다른 사람의 @saeroki 수다를 잠시 끄고 켭니다. 사전과 게임은 그대로 됩니다.
• `대화 켜기` / `대화 끄기`: 지금 채널을 @saeroki 수다 채널로 넣고 뺍니다."""


def chunks(text: str, size: int = CHUNK) -> list[str]:
    out, buf = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > size:
            out.append(buf + line[: size - len(buf)])
            line, buf = line[size - len(buf):], ""
        if len(buf) + len(line) > size:
            out.append(buf)
            buf = ""
        buf += line
    if buf.strip():
        out.append(buf)
    return out or ["(빈 답)"]


def wants_file(fruit: Fruit, text: str) -> bool:
    if not fruit.file_skill:
        return False
    if fruit.key == "interview":
        return True
    return text.strip() in ("", "검사", "review")


def safe_name(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|\s]+', "_", name)[:80] or "file"


class Bot:
    def __init__(self, bot_token: str, owner: str, threads: Threads | None = None):
        self.app = App(token=bot_token)
        self.token = bot_token
        self.owner = owner
        self.bot_user = ""  # serve()가 auth_test로 채웁니다.
        self.chat_channels = set(config.chat_channels())
        self.threads = threads or Threads()
        self.busy: set[str] = set()
        self.busy_lock = threading.Lock()
        self.game_lock = threading.Lock()
        self.words = game.load()
        self.cases = mystery.load()
        self.started_at = time.time()
        self.last_error: tuple[float, str] | None = None
        self.app.command("/saerok-dict")(self.on_dict)
        self.app.command("/saerok-word")(self.on_word)
        self.app.command("/saerok-case")(self.on_case)
        self.app.command("/saerok-master")(self.on_master)
        for name in COMMANDS:
            self.app.command(name)(self.on_fruit)
        self.app.event("message")(self.on_message)

    # 슬랙에 글 올리기
    def post(self, client, channel: str, thread: str, text: str, replace_ts: str | None = None) -> None:
        for i, piece in enumerate(chunks(text)):
            kwargs = dict(channel=channel, text=piece[:3000], blocks=[{"type": "markdown", "text": piece}])
            try:
                if i == 0 and replace_ts:
                    client.chat_update(ts=replace_ts, **kwargs)
                else:
                    client.chat_postMessage(thread_ts=thread, **kwargs)
            except SlackApiError:  # markdown 블록을 못 받는 곳이면 글만 보냅니다.
                kwargs.pop("blocks")
                kwargs["text"] = piece
                if i == 0 and replace_ts:
                    client.chat_update(ts=replace_ts, **kwargs)
                else:
                    client.chat_postMessage(thread_ts=thread, **kwargs)

    def process(self, client, thread: str, record: dict, prompt: str) -> None:
        with self.busy_lock:
            if thread in self.busy:
                client.chat_postMessage(channel=record["channel"], thread_ts=thread,
                                        text="아직 앞 메시지를 처리하는 중입니다. 답이 온 뒤 다시 보내 주세요.")
                return
            self.busy.add(thread)
        try:
            fruit = FRUITS[record["fruit"]]
            note = "🌱 …" if fruit.chat else f"🌱 {fruit.label}이(가) 생각하는 중입니다. 몇 분 걸릴 수 있습니다."
            wait = client.chat_postMessage(channel=record["channel"], thread_ts=thread, text=note)
            text, failed = run(fruit, prompt, record["session"], resume=record["started"])
            if not failed or record["started"]:
                record["started"] = True
                self.threads.put(thread, record)
            if failed:
                self.last_error = (time.time(), text[:200])
                if offline(text):
                    text = f"{OFFLINE}\n_원인: {text[:200]}_"
            self.post(client, record["channel"], thread, ("⚠️ " if failed else "") + text, replace_ts=wait["ts"])
        finally:
            with self.busy_lock:
                self.busy.discard(thread)

    # 명령
    def on_dict(self, ack, command, respond):
        ack()
        text = command.get("text", "").strip()
        respond(response_type="in_channel", text=dictionary.answer(text) if text else dictionary.today())

    # 끝말잇기: 누구나, AI 없이
    def on_word(self, ack, command, client, respond):
        ack()
        first = command.get("text", "").strip()
        channel, ts = self.open_root(client, command["channel_id"],
                                     f"🎮 새록이 끝말잇기 · <@{command['user_id']}> 이 스레드에 단어를 답글로 달면 누구나 함께할 수 있어요. 그만하려면 `졌다`.")
        if channel != command["channel_id"]:
            respond("이 대화방에는 새록이가 들어올 수 없어 새록이와의 DM에서 이어 갑니다.")
        record = game.new(channel)
        if first:
            reply = game.play(record, first, self.words) or "두 글자 이상의 한글 단어로 시작해 주세요. 스레드에 다시 적어도 돼요."
        else:
            reply = f"제가 먼저 할게요. *{game.bot_move(record, self.words)}*\n다음은 ‘{game.need(record)}’(으)로 시작하는 말이에요."
        self.threads.put(ts, record)
        client.chat_postMessage(channel=channel, thread_ts=ts, text=reply)

    def word_turn(self, client, event: dict, thread: str) -> None:
        with self.game_lock:
            record = self.threads.get(thread)
            reply = game.play(record, event.get("text", ""), self.words)
            if reply:
                self.threads.put(thread, record)
        if reply:
            client.chat_postMessage(channel=record["channel"], thread_ts=thread, text=reply)

    # 숲속 추리: 누구나, AI 없이
    def on_case(self, ack, command, client, respond):
        ack()
        arg, user = command.get("text", "").strip(), command["user_id"]
        solved = {r["case"] for r in self.threads.load().values()
                  if r["fruit"] == "case" and r.get("solved") and r.get("user") == user}
        if arg in ("목록", "회차"):
            respond(mystery.listing(self.cases, solved))
            return
        case = mystery.find(self.cases, int(arg)) if arg.isdigit() else None if arg else mystery.next_case(self.cases, solved)
        if not case:
            respond(f"그런 사건은 아직 없어요.\n{mystery.listing(self.cases, solved)}")
            return
        channel, ts = self.open_root(client, command["channel_id"],
                                     f"🦉 숲속 추리 제{case['id']}화 · <@{user}> 이 스레드에 답글로 누구나 함께 풀 수 있어요.")
        if channel != command["channel_id"]:
            respond("이 대화방에는 새록이가 들어올 수 없어 새록이와의 DM에서 이어 갑니다.")
        self.threads.put(ts, mystery.new(channel, case, user))
        client.chat_postMessage(channel=channel, thread_ts=ts, text=mystery.opening(self.cases, case))

    def case_turn(self, client, event: dict, thread: str) -> None:
        with self.game_lock:
            record = self.threads.get(thread)
            reply = mystery.play(record, event.get("text", ""), self.cases)
            if reply:
                self.threads.put(thread, record)
        if reply:
            client.chat_postMessage(channel=record["channel"], thread_ts=thread, text=reply)

    # 마스터: 주인만, AI 없이(점검만 AI에 아주 짧게 물어봄)
    def on_master(self, ack, command, client, respond):
        ack()
        if command["user_id"] != self.owner:
            respond("마스터 명령은 새록이 주인만 쓸 수 있습니다.")
            return
        respond(self.master(" ".join(command.get("text", "").split()), command["channel_id"], client))

    def master(self, arg: str, channel: str, client) -> str:
        if arg in ("", "상태"):
            return self.status_text()
        if arg == "점검":
            ok, text = check()
            return "✅ AI가 답할 수 있어요." if ok else f"⚠️ AI가 답하지 못했어요. 구독·로그인을 확인해 주세요.\n_{text}_"
        if arg in ("쉬기", "깨우기"):
            config.set_resting(arg == "쉬기")
            return RESTING if arg == "쉬기" else "🌱 새록이가 깨어났어요. 다시 @saeroki로 부르면 답합니다."
        if arg in ("대화 켜기", "대화 끄기"):
            on = arg == "대화 켜기"
            try:
                config.set_chat_channel(channel, on=on)
            except ValueError:
                return "DM에서는 대화 채널을 정할 수 없어요. 공개·비공개 채널에서 쳐 주세요."
            (self.chat_channels.add if on else self.chat_channels.discard)(channel)
            if on:
                try:
                    client.conversations_join(channel=channel)
                except SlackApiError:
                    return f"<#{channel}>을 대화 채널로 넣었어요. 비공개 채널이면 `/invite @saeroki`도 해 주세요."
            return f"<#{channel}>을 대화 채널로 {'넣었어요. 이제 @saeroki로 부르면 답합니다' if on else '뺐어요'}."
        return MASTER_HELP

    def status_text(self) -> str:
        minutes = int(time.time() - self.started_at) // 60
        records = list(self.threads.load().values())
        counts = {k: sum(r["fruit"] == k for r in records) for k in ("chat", "word", "case", *COMMANDS.values())}
        names = {"chat": "수다", "word": "끝말잇기", "case": "숲속 추리", "sql": "SQL", "idea": "심사단", "prd": "검토관", "interview": "면접관"}
        if self.last_error:
            ago = int(time.time() - self.last_error[0]) // 60
            error = f"{ago}분 전 · {self.last_error[1][:120]}"
        else:
            error = "없음"
        return "\n".join([
            "*🌳 새록이 상태*",
            f"• 켜진 지: {minutes // 60}시간 {minutes % 60}분",
            f"• 수다: {'🌙 쉬는 중' if config.resting() else '🌱 받는 중'}",
            "• 대화 채널: " + (", ".join(f"<#{c}>" for c in sorted(self.chat_channels)) or "없음"),
            f"• 지금 처리 중: {len(self.busy)}건",
            "• 지금까지 연 스레드: " + ", ".join(f"{names[k]} {v}" for k, v in counts.items() if v) if any(counts.values())
            else "• 지금까지 연 스레드: 없음",
            f"• 마지막 AI 오류: {error}",
            "_`/saerok-master 도움말`로 다른 명령을 볼 수 있어요._",
        ])

    def on_fruit(self, ack, command, client, respond):
        ack()
        if command["user_id"] != self.owner:
            respond(NOT_OWNER)
            return
        fruit = FRUITS[COMMANDS[command["command"]]]
        text = command.get("text", "").strip()
        waiting = wants_file(fruit, text)
        if not text and not waiting:
            respond(f"`{command['command']}` 뒤에 질문이나 아이디어를 함께 적어 주세요.")
            return
        channel, ts = self.open_root(client, command["channel_id"], f"{fruit.label} · <@{command['user_id']}> {text}".strip())
        if channel != command["channel_id"]:
            respond("이 대화방에는 새록이가 들어올 수 없어 새록이와의 DM에서 이어 갑니다.")
        record = Threads.new(fruit, channel, waiting)
        self.threads.put(ts, record)
        if waiting:
            client.chat_postMessage(channel=channel, thread_ts=ts, text=fruit.file_hint)
            return
        self.process(client, ts, record, f"{fruit.skill} {text}")

    def open_root(self, client, channel: str, text: str) -> tuple[str, str]:
        """명령을 친 곳에 첫 글을 올립니다. 봇이 없는 공개 채널이면 들어가고, 못 들어가는 곳이면 주인 DM으로 옮깁니다."""
        try:
            return channel, client.chat_postMessage(channel=channel, text=text)["ts"]
        except SlackApiError as err:
            if err.response.get("error") not in ("not_in_channel", "channel_not_found"):
                raise
        try:
            client.conversations_join(channel=channel)
            return channel, client.chat_postMessage(channel=channel, text=text)["ts"]
        except SlackApiError:  # 비공개 채널, 다른 사람과의 DM
            dm = client.conversations_open(users=self.owner)["channel"]["id"]
            return dm, client.chat_postMessage(channel=dm, text=text)["ts"]

    # 스레드 답글
    def download(self, file: dict, thread: str) -> Path:
        url = file.get("url_private_download") or file["url_private"]
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"})
        path = inbox_dir() / f"{thread.replace('.', '')}_{safe_name(file.get('name', 'file'))}"
        with urllib.request.urlopen(req, timeout=60) as resp:
            path.write_bytes(resp.read())
        return path

    def on_message(self, event, client):
        if event.get("bot_id") or event.get("subtype") not in (None, "file_share"):
            return
        thread = event.get("thread_ts")
        record = self.threads.get(thread) if thread else None
        if record and record["fruit"] == "word":
            return self.word_turn(client, event, thread)
        if record and record["fruit"] == "case":
            return self.case_turn(client, event, thread)
        if record and record["fruit"] == "chat":
            return self.chat(client, event, thread, record)
        if not record and self.called(event):
            return self.chat(client, event, thread or event["ts"], None)
        if not record or event.get("user") != self.owner:
            return
        fruit = FRUITS[record["fruit"]]
        text = event.get("text", "").strip()
        paths = [self.download(f, thread) for f in event.get("files", [])]
        note = ("\n\n(슬랙에 올린 파일: " + ", ".join(str(p) for p in paths) + ")") if paths else ""
        if record["waiting_file"]:
            if not paths:
                client.chat_postMessage(channel=record["channel"], thread_ts=thread, text=fruit.file_hint)
                return
            record["waiting_file"] = False
            self.threads.put(thread, record)
            prompt = f"{fruit.file_skill} {paths[0]} {text}{note}"
        else:
            prompt = f"{text}{note}" or "계속해 주세요."
        self.process(client, thread, record, prompt)

    # 대화 채널의 일상 대화: @saeroki로 부르면 스레드가 열리고, 그 스레드에서는 누구나 부르지 않고도 이어 갑니다.
    def called(self, event: dict) -> bool:
        return (event.get("channel") in self.chat_channels and bool(self.bot_user)
                and f"<@{self.bot_user}>" in event.get("text", ""))

    def chat(self, client, event: dict, thread: str, record: dict | None) -> None:
        if record is None:
            record = Threads.new(FRUITS["chat"], event["channel"], False)
            self.threads.put(thread, record)
        if config.resting() and event.get("user") != self.owner:
            client.chat_postMessage(channel=event["channel"], thread_ts=thread, text=RESTING)
            return
        text = re.sub(rf"<@{re.escape(self.bot_user)}>\s*", "", event.get("text", "")).strip()
        self.process(client, thread, record, f"<@{event.get('user', '?')}>: {text or '(부르기만 함)'}")


def serve() -> None:
    bot_token, app_token, owner = (config.get(n) for n in ("bot-token", "app-token", "owner"))
    missing = [config.FIELDS[n][2] for n, v in zip(("bot-token", "app-token", "owner"), (bot_token, app_token, owner)) if not v]
    if missing:
        raise SystemExit("먼저 `saerok-slack setup`으로 등록해 주세요: " + ", ".join(missing))
    bot = Bot(bot_token, owner)
    me = bot.app.client.auth_test()
    bot.bot_user = me["user_id"]
    print(f"새록이가 {me['team']} 워크스페이스에 연결됐습니다(봇 {me['user']}). 끄려면 Ctrl+C.")
    for channel in sorted(bot.chat_channels):
        try:
            bot.app.client.conversations_join(channel=channel)
            print(f"대화 채널 {channel}: @saeroki로 부르면 답합니다.")
        except SlackApiError as err:
            print(f"대화 채널 {channel}에 들어가지 못했습니다({err.response.get('error')}). 그 채널에서 /invite @saeroki 해 주세요.")
    SocketModeHandler(bot.app, app_token).start()
