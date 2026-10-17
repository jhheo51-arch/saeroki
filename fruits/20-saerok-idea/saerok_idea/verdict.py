"""투표와 가정 검증으로 판정을 냅니다(PRD 4장 19번). 같은 입력이면 언제나 같은 판정입니다."""

from . import rubric

INSUFFICIENT = "판단 보류(정보 부족)"


def decide(idea: dict, judges: dict, assumptions: list[dict]) -> dict:
    """판정과, 판정에 이른 단계를 순서대로 돌려줍니다."""
    steps = []
    missing = [rubric.FIELDS[k] for k in rubric.CORE_FIELDS if _unknown(idea.get(k))]
    if missing:
        steps.append(f"핵심 칸이 미정: {', '.join(missing)}")
        return {"verdict": INSUFFICIENT, "steps": steps}
    status = {a["key"]: a["status"] for a in assumptions}
    if all(s == "확인 못 함" for s in status.values()):
        steps.append("가정 3개를 모두 확인하지 못함")
        return {"verdict": INSUFFICIENT, "steps": steps}

    votes = [judges[k]["vote"] for k in rubric.ORDER]
    count = {v: votes.count(v) for v in rubric.VOTES}
    shown = " · ".join(f"{v} {count[v]}" for v in rubric.VOTES)
    if count["보류"] >= 2:
        verdict = "보류"
        steps.append(f"투표 {shown}: 보류 2표 이상이라 보류")
    elif count["진행"] >= 2 and count["보류"] == 0:
        verdict = "진행"
        steps.append(f"투표 {shown}: 진행 2표 이상, 보류 0표라 진행")
    else:
        verdict = "조건부"
        steps.append(f"투표 {shown}: 진행·보류 조건에 들지 않아 조건부")

    if status.get("problem") == "반박":
        if verdict != "보류":
            steps.append(f"'{rubric.ASSUMPTIONS['problem']}' 가정이 반박되어 보류")
        verdict = "보류"
    elif verdict == "진행":
        refuted = [rubric.ASSUMPTIONS[k] for k in rubric.ASSUMPTIONS if status.get(k) == "반박"]
        if refuted:
            verdict = "조건부"
            steps.append(f"반박된 가정({', '.join(refuted)})이 있어 진행을 조건부로 낮춤")
    return {"verdict": verdict, "steps": steps}


def _unknown(value) -> bool:
    return not (value or "").strip() or value.strip() == rubric.UNKNOWN
