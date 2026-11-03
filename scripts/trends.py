"""구글 트렌드 한국 급상승 검색어 알림. 슬랙 Block Kit 표 블록으로 웹훅에 보냅니다.

    python scripts/trends.py            # SLACK_TREND_WEBHOOK으로 보내기
    python scripts/trends.py --dry-run  # 보내지 않고 블록 JSON만 출력
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from zoneinfo import ZoneInfo

SEOUL = ZoneInfo("Asia/Seoul")
WEEKDAYS = "월화수목금토일"
RSS = "https://trends.google.com/trending/rss?geo=KR"
NS = {"ht": "https://trends.google.com/trending/rss"}
MEDALS = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
TITLE_MAX = 28


def fetch() -> list[dict]:
    """키워드, 검색량, 첫 번째 관련 뉴스. 검색량이 많은 순서."""
    req = urllib.request.Request(RSS, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        root = ET.fromstring(r.read())
    items = []
    for it in root.iter("item"):
        traffic = it.findtext("ht:approx_traffic", "", NS)
        news = it.find("ht:news_item", NS)
        items.append({
            "keyword": it.findtext("title", "").strip(),
            "traffic": traffic,
            "volume": int("".join(c for c in traffic if c.isdigit()) or 0),
            "news": news.findtext("ht:news_item_title", "", NS).strip() if news is not None else "",
            "url": news.findtext("ht:news_item_url", "", NS) if news is not None else "",
            "source": news.findtext("ht:news_item_source", "", NS) if news is not None else "",
        })
    return sorted(items, key=lambda i: -i["volume"])


def fire(volume: int) -> str:
    if volume >= 2000:
        return "🔥🔥🔥"
    if volume >= 1000:
        return "🔥🔥"
    if volume >= 500:
        return "🔥"
    return "🌱"


def text_cell(text: str) -> dict:
    return {"type": "raw_text", "text": text or " "}


def news_cell(item: dict) -> dict:
    if not item["news"]:
        return text_cell("-")
    title = item["news"].replace("\n", " ")
    if len(title) > TITLE_MAX:
        title = title[:TITLE_MAX].rstrip() + "…"
    part = {"type": "link", "url": item["url"], "text": title} if item["url"] else {"type": "text", "text": title}
    return {"type": "rich_text", "elements": [{"type": "rich_text_section", "elements": [part]}]}


def build(items: list[dict], now: datetime | None = None) -> dict:
    now = (now or datetime.now(SEOUL)).astimezone(SEOUL)
    edition = "☀️ 아침판" if now.hour < 12 else "🌙 저녁판"
    head = f"📈 *급상승 검색어*  {edition}\n🗓️ {now:%m/%d} ({WEEKDAYS[now.weekday()]}) {now:%H}시, 한국 구글 기준"
    rows = [[text_cell("순위"), text_cell("검색어"), text_cell("검색량"), text_cell("📰 관련 뉴스")]]
    for medal, item in zip(MEDALS, items):
        rows.append([text_cell(medal), text_cell(item["keyword"]),
                     text_cell(f"{fire(item['volume'])} {item['traffic']}"), news_cell(item)])
    legend = "🔥🔥🔥 2,000+  🔥🔥 1,000+  🔥 500+  🌱 그 아래  |  🔍 자료: Google Trends (최근 몇 시간 동안 검색이 급히 늘어난 키워드)"
    fallback = "급상승 검색어: " + ", ".join(i["keyword"] for i in items[:10])
    return {
        "text": fallback,
        "blocks": [
            {"type": "section", "text": {"type": "mrkdwn", "text": head}},
            {"type": "table", "column_settings": [{"align": "center"}, {"is_wrapped": True}, {}, {"is_wrapped": True}],
             "rows": rows},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": legend}]},
        ],
    }


def send(payload: dict, url: str) -> None:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    payload = build(fetch())
    if args.dry_run:
        sys.stdout.buffer.write(json.dumps(payload, ensure_ascii=False, indent=1).encode("utf-8") + b"\n")
        return 0
    url = os.environ.get("SLACK_TREND_WEBHOOK")
    if not url:
        print("SLACK_TREND_WEBHOOK이 없습니다.", file=sys.stderr)
        return 1
    send(payload, url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
