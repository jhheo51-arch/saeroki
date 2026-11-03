"""무료 플랜 90일 규칙으로 곧 안 보이게 될 슬랙 파일 알림.

    python scripts/slack_files.py            # SLACK_TREND_WEBHOOK으로 보내기
    python scripts/slack_files.py --dry-run  # 보내지 않고 메시지만 출력

SLACK_BOT_TOKEN(files:read 권한)으로 파일 목록을 읽습니다.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request

HIDE_AFTER = 90  # 무료 플랜은 90일 지난 메시지와 파일을 숨깁니다
WARN_WITHIN = 14  # 남은 날짜가 이 안이면 알립니다
TYPE_ICON = {"pdf": "📄", "quip": "📘", "canvas": "📘", "docx": "📝", "xlsx": "📊", "csv": "📊", "pptx": "📽️"}


def files(token: str) -> list[dict]:
    out, page = [], 1
    while True:
        query = urllib.parse.urlencode({"count": 200, "page": page})
        req = urllib.request.Request(f"https://slack.com/api/files.list?{query}",
                                     headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.load(r)
        if not data.get("ok"):
            raise SystemExit(f"files.list 실패: {data.get('error')}")
        out += data["files"]
        paging = data.get("paging", {})
        if page >= paging.get("pages", 1):
            return out
        page += 1


def icon(f: dict) -> str:
    if f.get("mimetype", "").startswith("image/"):
        return "🖼️"
    return TYPE_ICON.get(f.get("filetype", ""), "📎")


def urgency(left: int) -> str:
    if left <= 3:
        return "🚨"
    if left <= 9:
        return "⚠️"
    return "🕰️"


def build(all_files: list[dict], now: float | None = None) -> str:
    now = now or time.time()
    soon = []
    for f in all_files:
        left = HIDE_AFTER - int((now - f["created"]) // 86400)
        if 0 < left <= WARN_WITHIN:
            soon.append((left, f))
    head = "🗂️ *곧 안 보이게 될 파일* (무료 플랜은 90일 지나면 숨겨져요)"
    if not soon:
        return f"{head}\n\n🌿 앞으로 2주 안에 숨겨질 파일은 없어요."
    lines = []
    for left, f in sorted(soon, key=lambda x: x[0]):
        canvas = f.get("filetype") in ("quip", "canvas")
        name = f"캔버스 「{f.get('title') or f.get('name')}」 _(참고용)_" if canvas else f"`{f.get('name') or f.get('title')}`"
        where = " ".join(f"<#{c}>" for c in f.get("channels", []))
        who = f"<@{f['user']}>" if f.get("user") else ""
        lines.append(f"{urgency(left)} *D-{left}*  {icon(f)} {name}  {where} {who}".rstrip())
    return "\n".join([head, "", *lines, "", "💾 필요한 파일은 내려받아 따로 보관하세요."])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print("SLACK_BOT_TOKEN이 없습니다.", file=sys.stderr)
        return 1
    text = build(files(token))
    if args.dry_run:
        sys.stdout.buffer.write(text.encode("utf-8") + b"\n")
        return 0
    url = os.environ.get("SLACK_TREND_WEBHOOK")
    if not url:
        print("SLACK_TREND_WEBHOOK이 없습니다.", file=sys.stderr)
        return 1
    req = urllib.request.Request(url, data=json.dumps({"text": text}).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()
    return 0


if __name__ == "__main__":
    sys.exit(main())
