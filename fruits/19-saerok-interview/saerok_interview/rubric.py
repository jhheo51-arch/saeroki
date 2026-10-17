"""면접관 5명과 기준 항목. 회차를 같은 잣대로 비교하려고 항목과 배점을 고정합니다(PRD v2.1 4장)."""

# 항목 옵션: answer_only = 서류만으로는 볼 수 없어 서류 점수에서 빠짐, needs_posting = 공고가 없으면 '해당 없음'
INTERVIEWERS = {
    "pressure": {
        "name": "압박",
        "looks_at": "과장·모순·빈틈",
        "items": [
            {"key": "evidence", "name": "주장과 근거 일치", "max": 3},
            {"key": "role", "name": "역할 범위가 분명함", "max": 3},
            {"key": "consistency", "name": "앞뒤 일관성", "max": 2},
            {"key": "composure", "name": "흔들림 없는 답", "max": 2, "answer_only": True},
        ],
    },
    "hr": {
        "name": "인사",
        "looks_at": "지원 동기·협업·태도",
        "items": [
            {"key": "motivation", "name": "지원 동기의 구체성", "max": 3},
            {"key": "collaboration", "name": "협업·갈등 해결 사례", "max": 3},
            {"key": "fit", "name": "조직 적합성", "max": 2},
            {"key": "tenure", "name": "오래 다닐 근거", "max": 2},
        ],
    },
    "practitioner": {
        "name": "실무",
        "looks_at": "바로 투입 가능한지",
        "items": [
            {"key": "judgment", "name": "상황 판단", "max": 3},
            {"key": "execution", "name": "실행 순서", "max": 3},
            {"key": "terms", "name": "직무 용어를 바르게 씀", "max": 2},
            {"key": "posting", "name": "공고 요건과 연결", "max": 2, "needs_posting": True},
        ],
    },
    "executive": {
        "name": "임원",
        "looks_at": "회사 방향과 장기 포부",
        "items": [
            {"key": "company", "name": "회사·산업 이해", "max": 3, "needs_posting": True},
            {"key": "why_us", "name": "'왜 우리 회사'", "max": 3},
            {"key": "vision", "name": "3~5년 포부의 현실성", "max": 2},
            {"key": "summary", "name": "한 문장 요약력", "max": 2},
        ],
    },
    "numbers": {
        "name": "숫자 검증",
        "looks_at": "성과 수치의 출처와 계산",
        "items": [
            {"key": "source", "name": "수치의 출처", "max": 3},
            {"key": "calculation", "name": "계산 과정", "max": 3},
            {"key": "definition", "name": "지표 정의", "max": 2},
            {"key": "baseline", "name": "비교 기준(이전·대조군)", "max": 2},
        ],
    },
}

ORDER = list(INTERVIEWERS)
LEVELS = ["순한맛", "보통", "매운맛"]
NOTICE = "연습용 판정입니다. 실제 면접 방식·합격 여부와 다를 수 있습니다."


def item(interviewer: str, key: str) -> dict | None:
    return next((i for i in INTERVIEWERS[interviewer]["items"] if i["key"] == key), None)


def auto_na(interviewer: str, key: str, *, stage: str, posting: bool) -> str | None:
    """규칙으로 정해지는 '해당 없음' 이유. 없으면 None."""
    spec = item(interviewer, key)
    if stage == "document" and spec.get("answer_only"):
        return "답변에서만 봄"
    if spec.get("needs_posting") and not posting:
        return "공고 없음"
    return None


def total10(interviewer: str, items: dict) -> float | None:
    """해당 없음(None)은 분모에서 빼고 10점으로 환산합니다. 셀 항목이 없으면 None."""
    got = top = 0
    for spec in INTERVIEWERS[interviewer]["items"]:
        value = items.get(spec["key"])
        if value is None:
            continue
        got += value
        top += spec["max"]
    return round(got / top * 10, 1) if top else None


def verdict(score: float | None) -> str:
    if score is None:
        return "판단 보류"
    if score >= 7:
        return "합격권"
    if score >= 5:
        return "보류"
    return "부족"
