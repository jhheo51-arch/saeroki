"""여러 세션의 score.json만 읽어 회차별 점수 변화, 반복해서 낮은 항목, 실제 면접 적중률을 셉니다(PRD v2.1 6장)."""

from . import rubric

GOAL_RISE = 2.0      # 3회차 답변 평균이 1회차보다 이만큼 오르면 목표 달성
LOW_RATIO = 0.5      # 항목 점수/배점이 이보다 낮으면 '낮음'
RETEST_LIMIT = 2.0   # 같은 문서 재심사 점수 차이 허용 폭


def _avg(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


def _row(meta: dict, score: dict) -> dict:
    by_who = {}
    for a in score["answers"]:
        by_who.setdefault(a["interviewer"], []).append(a["total"])
    return {
        "session": meta["session"],
        "date": meta["date"],
        "company": meta.get("company", ""),
        "document": {who: score["document"].get(who, {}).get("total") for who in rubric.ORDER},
        "answers": {who: _avg(by_who.get(who, [])) for who in rubric.ORDER},
        "answer_avg": _avg(a["total"] for a in score["answers"]),
        "answered": len(score["answers"]),
    }


def _weak_items(pairs) -> list[dict]:
    """답변에서 항목 점수 비율이 LOW_RATIO보다 낮았던 세션이 2개 이상인 항목."""
    low = {}
    for meta, score in pairs:
        ratios = {}
        for a in score["answers"]:
            for key, value in a["items"].items():
                if value is not None:
                    ratios.setdefault((a["interviewer"], key), []).append(value / rubric.item(a["interviewer"], key)["max"])
        for k, values in ratios.items():
            if sum(values) / len(values) < LOW_RATIO:
                low.setdefault(k, []).append(meta["session"])
    out = []
    for (who, key), names in low.items():
        if len(names) >= 2:
            out.append({"interviewer": who, "item": key, "name": rubric.item(who, key)["name"], "sessions": names})
    out.sort(key=lambda r: (-len(r["sessions"]), rubric.ORDER.index(r["interviewer"]), r["item"]))
    return out


def _retest(pairs) -> list[dict]:
    """자기소개서(와 공고)가 같은 세션끼리 서류 점수 차이를 봅니다."""
    groups = {}
    for meta, score in pairs:
        key = tuple(meta["inputs"].get(k, {}).get("sha256") for k in ("resume_letter", "posting"))
        groups.setdefault(key, []).append((meta, score))
    out = []
    for same in groups.values():
        if len(same) < 2:
            continue
        for who in rubric.ORDER:
            totals = [s["document"].get(who, {}).get("total") for _, s in same]
            totals = [t for t in totals if t is not None]
            if len(totals) >= 2:
                diff = round(max(totals) - min(totals), 1)
                out.append({"sessions": [m["session"] for m, _ in same], "interviewer": who, "diff": diff, "over": diff > RETEST_LIMIT})
    return out


def compare(pairs: list[tuple[dict, dict]]) -> dict:
    rows = [_row(m, s) for m, s in pairs]
    with_answers = [r for r in rows if r["answer_avg"] is not None]
    change = None
    if len(with_answers) >= 2:
        first, last = with_answers[0], with_answers[-1]
        diff = round(last["answer_avg"] - first["answer_avg"], 1)
        change = {
            "first": first["session"], "last": last["session"],
            "first_avg": first["answer_avg"], "last_avg": last["answer_avg"], "diff": diff,
            "sessions": len(with_answers),
            "goal": None if len(with_answers) < 3 else diff >= GOAL_RISE,
        }
    real = [q for _, s in pairs for r in s["real"] for q in r["questions"]]
    hits = sum(q["confirmed"] for q in real)
    return {
        "sessions": rows,
        "change": change,
        "weak_items": _weak_items(pairs),
        "hit": {"real_questions": len(real), "confirmed": hits, "rate": round(hits / len(real) * 100) if real else None},
        "retest": _retest(pairs),
    }


def _fmt(v) -> str:
    return "-" if v is None else f"{v:g}"


def render(result: dict) -> str:
    names = [rubric.INTERVIEWERS[w]["name"] for w in rubric.ORDER]
    lines = [f"# 새록 면접관 회차 비교 ({len(result['sessions'])}회)", "", "## 답변 점수(10점, 면접관별 평균)", ""]
    lines += ["| 세션 | " + " | ".join(names) + " | 평균 | 답한 수 |", "|---|" + "---:|" * (len(names) + 2)]
    for r in result["sessions"]:
        lines.append(f"| {r['session']} | " + " | ".join(_fmt(r["answers"][w]) for w in rubric.ORDER) + f" | {_fmt(r['answer_avg'])} | {r['answered']} |")
    lines += ["", "## 서류 점수(10점)", "", "| 세션 | " + " | ".join(names) + " |", "|---|" + "---:|" * len(names)]
    for r in result["sessions"]:
        lines.append(f"| {r['session']} | " + " | ".join(_fmt(r["document"][w]) for w in rubric.ORDER) + " |")

    lines += ["", "## 변화", ""]
    c = result["change"]
    if not c:
        lines.append("- 답변 기록이 있는 세션이 2개 이상이어야 변화를 셉니다.")
    else:
        lines.append(f"- 첫 세션 {_fmt(c['first_avg'])}점 → 마지막 세션 {_fmt(c['last_avg'])}점 ({c['diff']:+g}점, {c['sessions']}회)")
        if c["goal"] is None:
            lines.append(f"- 목표(+{GOAL_RISE:g}점)는 세션 3회부터 판단합니다.")
        else:
            lines.append(f"- 목표(+{GOAL_RISE:g}점): {'달성' if c['goal'] else '아직'}")

    lines += ["", "## 반복해서 낮은 항목", ""]
    if result["weak_items"]:
        for w in result["weak_items"]:
            lines.append(f"- {rubric.INTERVIEWERS[w['interviewer']]['name']} · {w['name']}: {len(w['sessions'])}회 ({', '.join(w['sessions'])})")
    else:
        lines.append("- 2회 이상 낮았던 항목이 없습니다.")

    h = result["hit"]
    lines += ["", "## 실제 면접 적중률", ""]
    if h["rate"] is None:
        lines.append("- 실제 면접 질문 기록이 없습니다.")
    else:
        lines.append(f"- 실제 질문 {h['real_questions']}개 중 모의 질문과 비슷했다고 확인한 것 {h['confirmed']}개 ({h['rate']}%)")

    if result["retest"]:
        lines += ["", "## 같은 문서 재심사 차이", ""]
        for r in result["retest"]:
            mark = f" (허용 {RETEST_LIMIT:g}점 넘음, 기준 설명을 다듬을 때)" if r["over"] else ""
            lines.append(f"- {rubric.INTERVIEWERS[r['interviewer']]['name']}: {r['diff']:g}점{mark}")
    return "\n".join(lines) + "\n"
