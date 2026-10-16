"""저장소에 공개할 날짜별 숫자 집계. 제목·원문·경로·세션 ID·프로젝트 이름은 담지 않습니다."""

from pathlib import Path

from .paths import PUBLIC_DAILY
from .scan import daily
from .store import write_json

PUBLIC_FIELDS = ("date", "sessions", "responses", "processed", "max_ctx", "images")


def public_rows(sessions: list[dict]) -> list[dict]:
    rows = []
    for d in daily(sessions):
        row = {k: d[k] for k in PUBLIC_FIELDS}
        row["over300_share"] = round(d["over300"] / d["processed"], 3) if d["processed"] else 0
        rows.append(row)
    return rows


def export(sessions: list[dict], out: Path = PUBLIC_DAILY) -> Path:
    write_json(out, {
        "about": "새록 파수꾼 공개 집계: 날짜별 Claude Code 처리 토큰(응답마다 읽은 컨텍스트의 합)과 스크린샷 수",
        "fields": {
            "processed": "그날 응답들이 읽은 컨텍스트 토큰 합",
            "max_ctx": "그날 가장 컸던 컨텍스트",
            "over300_share": "처리량 중 컨텍스트 30만 이상 응답의 비율",
        },
        "days": public_rows(sessions),
    })
    return out
