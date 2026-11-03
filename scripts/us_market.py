"""미국 주요 지수 아침 알림. Yahoo Finance 시세를 받아 슬랙 웹훅으로 보냅니다.

    python scripts/us_market.py            # SLACK_MARKET_WEBHOOK으로 보내기
    python scripts/us_market.py --dry-run  # 보내지 않고 메시지만 출력
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
WEEKDAYS = "월화수목금토일"
CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=5d&interval=1d"

# (심볼, 이름, 소수 자리)
INDICES = [("^GSPC", "S&P 500", 2), ("^DJI", "다우존스", 2), ("^IXIC", "나스닥", 2),
           ("^RUT", "러셀 2000", 2), ("^SOX", "필라델피아 반도체", 2)]
EXTRAS = [("^VIX", "VIX 공포지수", 2), ("^TNX", "미국 10년물 금리", 3), ("KRW=X", "원/달러 환율", 2)]


def quote(symbol: str) -> dict:
    """마지막 종가, 직전 종가, 기준 시각."""
    req = urllib.request.Request(CHART.format(urllib.parse.quote(symbol)), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        result = json.load(r)["chart"]["result"][0]
    closes = [c for c in result["indicators"]["quote"][0]["close"] if c is not None]
    meta = result["meta"]
    price = meta.get("regularMarketPrice") or closes[-1]
    prev = closes[-2] if len(closes) >= 2 else meta.get("chartPreviousClose")
    return {"price": price, "prev": prev, "time": datetime.fromtimestamp(meta["regularMarketTime"], NY)}


def mark(pct: float) -> str:
    if pct >= 1:
        return "🚀"
    if pct > 0:
        return "🔺"
    if pct <= -1:
        return "🧊"
    if pct < 0:
        return "🔻"
    return "➖"


def line(name: str, q: dict, digits: int, suffix: str = "") -> str:
    pct = (q["price"] / q["prev"] - 1) * 100 if q["prev"] else 0.0
    diff = q["price"] - (q["prev"] or q["price"])
    return f"{mark(pct)} *{name}*  {q['price']:,.{digits}f}{suffix}  ({diff:+,.{digits}f}, {pct:+.2f}%)"


def last_session(now: datetime) -> datetime.date:
    """지금 기준으로 가장 최근에 끝난 미국 평일."""
    day = now.astimezone(NY).date() - timedelta(days=1)
    while day.weekday() >= 5:
        day -= timedelta(days=1)
    return day


def build(now: datetime | None = None) -> str:
    now = now or datetime.now(timezone.utc)
    quotes = {s: quote(s) for s, _, _ in INDICES + EXTRAS}
    session = quotes["^GSPC"]["time"].date()
    head = f"🌅 *미국 증시 마감* ({session:%m/%d} {WEEKDAYS[session.weekday()]}요일 뉴욕 기준)"
    if session < last_session(now):
        head += "\n🏖️ 어제는 미국 증시가 쉬었어요. 그 전 거래일 기준입니다."
    rows = [line(n, quotes[s], d) for s, n, d in INDICES]
    extra = [line(n, quotes[s], d, "%" if s == "^TNX" else "") for s, n, d in EXTRAS]
    return "\n".join([head, "", *rows, "", *extra, "", "_🚀 +1% 이상  🔺 상승  🔻 하락  🧊 -1% 이하  (자료: Yahoo Finance)_"])


def send(text: str, url: str) -> None:
    body = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        r.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    text = build()
    if args.dry_run:
        sys.stdout.buffer.write(text.encode("utf-8") + b"\n")
        return 0
    url = os.environ.get("SLACK_MARKET_WEBHOOK")
    if not url:
        print("SLACK_MARKET_WEBHOOK이 없습니다.", file=sys.stderr)
        return 1
    send(text, url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
