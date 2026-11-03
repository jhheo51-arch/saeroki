"""saerok-slack 명령.

saerok-slack setup      # 토큰 두 개와 내 멤버 ID를 자격 증명 관리자에 등록
saerok-slack status     # 등록 상태(토큰은 가려서)
saerok-slack manifest   # 슬랙 앱 만들 때 붙여 넣을 매니페스트
saerok-slack forget     # 등록한 값 지우기
saerok-slack chat C…    # 그 채널에서 @saeroki로 일상 대화 받기(--off C…로 끄기, ID 없이 치면 목록)
saerok-slack            # 봇 켜기
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

from . import config

MANIFEST = Path(__file__).resolve().parent / "manifest.json"


def setup() -> int:
    print("값은 Windows 자격 증명 관리자에만 저장되고 파일·기록·화면에는 남지 않습니다. 그대로 두려면 빈칸으로 Enter.")
    for name, (_, _, label) in config.FIELDS.items():
        ask = input if name == "owner" else getpass.getpass
        while True:
            value = ask(f"{label} [{config.masked(name, config.get(name))}]: ").strip()
            if not value:
                break
            try:
                config.put(name, value)
                break
            except ValueError as err:
                print(err)
    return status()


def status() -> int:
    for name, (_, _, label) in config.FIELDS.items():
        print(f"{label}: {config.masked(name, config.get(name))}")
    return 0


def chat(args: list[str]) -> int:
    try:
        if len(args) == 2 and args[0] == "--off":
            config.set_chat_channel(args[1], on=False)
        elif len(args) == 1:
            config.set_chat_channel(args[0])
        elif args:
            print(__doc__)
            return 2
    except ValueError as err:
        print(err)
        return 2
    print("대화 채널: " + (", ".join(config.chat_channels()) or "없음") + " (봇을 다시 켜면 적용됩니다)")
    return 0


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    cmd = argv[0] if argv else "run"
    if cmd == "setup":
        return setup()
    if cmd == "status":
        return status()
    if cmd == "manifest":
        print(MANIFEST.read_text(encoding="utf-8"))
        return 0
    if cmd == "forget":
        for name in config.FIELDS:
            config.delete(name)
        print("등록한 값을 지웠습니다.")
        return 0
    if cmd == "chat":
        return chat(argv[1:])
    if cmd == "run":
        from .app import serve
        serve()
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
