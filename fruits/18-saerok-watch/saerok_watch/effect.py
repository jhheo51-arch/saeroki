"""적용한 조치가 실제로 효과가 있었는지 적용 전후 세션을 비교합니다.

설정은 새로 여는 세션부터 반영되므로 세션 시작 시각으로 나눕니다.
적용 전 7일에 시작한 세션과 적용 뒤(되돌렸다면 되돌리기 전까지) 7일에 시작한 세션을 비교합니다.
"""

import time
from datetime import datetime

WINDOW_DAYS = 7
MIN_SESSIONS = 3
MIN_DAYS = 3  # 적용 직후 세션은 아직 덜 자라 작게 나오므로 며칠 기다립니다.
IDLE_SECONDS = 30 * 60  # 아직 진행 중인 세션은 비교에서 뺍니다.
SAME = 0.05  # 5% 안쪽 변화는 '그대로'로 봅니다.

METRICS = {
    "first_ctx": "세션 기본 부담(첫 응답 크기) 평균",
    "avg_ctx": "응답당 평균 컨텍스트",
    "max_ctx": "세션 최대 크기 평균",
    "over300": "30만 이상 응답의 처리량 몫",
}


def _subject(word: str) -> str:
    """받침에 맞춰 '이/가'를 붙입니다."""
    last = word[-1]
    has_final = "가" <= last <= "힣" and (ord(last) - ord("가")) % 28
    return word + ("이" if has_final else "가")


def _toward(word: str) -> str:
    """받침에 맞춰 '으로/로'를 붙입니다(ㄹ 받침은 '로')."""
    last = word[-1]
    final = (ord(last) - ord("가")) % 28 if "가" <= last <= "힣" else 0
    return word + ("으로" if final and final != 8 else "로")


def primary_metric(action: str) -> str:
    """조치마다 효과가 가장 잘 드러나는 지표."""
    if action.startswith(("mcp_off:", "plugin_off:")):
        return "first_ctx"
    if action.startswith("autocompact:"):
        return "over300"
    return "max_ctx"  # 훅·상태줄: 경고를 보고 세션을 일찍 끊었는지


def _epoch_utc(ts: str | None) -> float | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return None


def _epoch_local(text: str | None) -> float | None:
    if not text:
        return None
    try:
        return time.mktime(time.strptime(text, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        return None


def measure(sessions: list[dict]) -> dict:
    sessions = [s for s in sessions if s.get("responses")]
    n = len(sessions)
    processed = sum(s["processed"] for s in sessions)
    responses = sum(s["responses"] for s in sessions)
    big = sum(s["buckets"][2] + s["buckets"][3] for s in sessions)
    return {
        "sessions": n,
        "first_ctx": round(sum(s["first_ctx"] for s in sessions) / n) if n else 0,
        "avg_ctx": round(processed / responses) if responses else 0,
        "max_ctx": round(sum(s["max_ctx"] for s in sessions) / n) if n else 0,
        "over300": round(big / processed, 4) if processed else 0,
    }


def effect(entry: dict, sessions: list[dict], log: list[dict], now: float | None = None) -> dict:
    now = now or time.time()
    at = _epoch_local(entry.get("at"))
    if at is None:
        return {"id": entry.get("id"), "status": "unknown", "text": "적용 시각을 읽지 못했습니다."}
    end = min(_epoch_local(entry.get("undone_at")) or now, at + WINDOW_DAYS * 86400)
    starts = [(s, _epoch_utc(s.get("first_ts"))) for s in sessions]
    before = measure([s for s, t in starts if t is not None and at - WINDOW_DAYS * 86400 <= t < at])
    after = measure([s for s, t in starts if t is not None and at <= t < end
                     and (_epoch_utc(s.get("last_ts")) or 0) < now - IDLE_SECONDS])
    key = primary_metric(entry.get("action", ""))
    # 같은 비교 기간에 다른 조치가 있었다면 효과가 섞입니다.
    overlaps = sum(1 for e in log if e.get("id") != entry.get("id")
                   and (t := _epoch_local(e.get("at"))) is not None and abs(t - at) < WINDOW_DAYS * 86400)
    out = {"id": entry.get("id"), "metric": key, "metric_label": METRICS[key],
           "before": before, "after": after, "overlaps": overlaps}
    waited = (end - at) / 86400
    if before["sessions"] < MIN_SESSIONS or after["sessions"] < MIN_SESSIONS or waited < MIN_DAYS:
        out.update(status="early", text=f"판단하기 이릅니다. 적용 전 세션 {before['sessions']}개, "
                                        f"끝난 적용 뒤 세션 {after['sessions']}개, 지난 날 {waited:.1f}일"
                                        f"(세션 각 {MIN_SESSIONS}개와 {MIN_DAYS}일 이상 필요).")
        return out
    b, a = before[key], after[key]
    change = (a - b) / b if b else 0
    status = "better" if change <= -SAME else "worse" if change >= SAME else "same"
    word = {"better": "줄었습니다", "worse": "늘었습니다", "same": "거의 그대로입니다"}[status]
    fmt = (lambda v: f"{v:.0%}") if key == "over300" else (lambda v: f"{v / 10_000:.1f}만")
    text = f"{_subject(METRICS[key])} {fmt(b)}에서 {_toward(fmt(a))} {word}({change:+.0%})."
    if overlaps:
        text += f" 같은 기간 다른 조치 {overlaps}개와 효과가 섞여 있습니다."
    out.update(status=status, change=round(change, 4), text=text)
    return out


def effects(sessions: list[dict], log: list[dict], now: float | None = None) -> dict:
    return {e["id"]: effect(e, sessions, log, now) for e in log if e.get("id")}
