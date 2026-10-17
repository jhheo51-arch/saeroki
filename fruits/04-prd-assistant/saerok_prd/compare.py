"""고치기 전후 PRD를 비교해 기준이 몇 개 나아졌는지, 지적 중 몇 개를 고쳤는지 셉니다."""

from collections import Counter

from .check import KIND, MARK, check

RANK = {"missing": 0, "weak": 1, "ok": 2}


def _key(f: dict) -> tuple[str, str]:
    # 고치면 줄 번호가 밀리므로 종류와 원문 일부로 짝짓습니다.
    return f["kind"], " ".join(f["quote"].split())


def compare(before_text: str, after_text: str, config: dict | None = None) -> dict:
    before, after = check(before_text, config), check(after_text, config)
    after_status = {c["key"]: c["status"] for c in after["criteria"]}
    criteria = []
    for c in before["criteria"]:
        new = after_status[c["key"]]
        if "skip" in (new, c["status"]):  # 해당 없음으로 바꾼 것은 나아짐도 나빠짐도 아닙니다.
            change = "same" if new == c["status"] else "skip"
        else:
            change = "better" if RANK[new] > RANK[c["status"]] else "worse" if RANK[new] < RANK[c["status"]] else "same"
        criteria.append({"key": c["key"], "label": c["label"], "before": c["status"], "after": new, "change": change})

    left = Counter(_key(f) for f in after["findings"])
    fixed = []
    for f in before["findings"]:
        if left[_key(f)]:
            left[_key(f)] -= 1
        else:
            fixed.append(f)
    still = Counter(_key(f) for f in before["findings"])
    added = []
    for f in after["findings"]:
        if still[_key(f)]:
            still[_key(f)] -= 1
        else:
            added.append(f)

    total = len(before["findings"])
    return {
        "title": after["title"] or before["title"],
        "criteria": criteria,
        "fixed": fixed,
        "added": added,
        "summary": {
            "ok_before": before["summary"]["ok"], "ok_after": after["summary"]["ok"],
            "total_before": before["summary"]["total"], "total_after": after["summary"]["total"],
            "findings_before": total, "findings_after": len(after["findings"]),
            "fixed": len(fixed), "added": len(added),
            "fix_rate": round(len(fixed) / total * 100) if total else None,
        },
    }


def render(result: dict) -> str:
    s = result["summary"]
    rate = f"{s['fix_rate']}%" if s["fix_rate"] is not None else "고칠 지적 없음"
    out = [f"# {result['title'] or '(제목 없음)'} 고치기 전후",
           f"기준 충족 {s['ok_before']}/{s['total_before']}개 → {s['ok_after']}/{s['total_after']}개",
           f"줄 지적 {s['findings_before']}개 → {s['findings_after']}개: 고친 지적 {s['fixed']}개({rate}), 새 지적 {s['added']}개",
           "", "## 기준 변화"]
    changed = [c for c in result["criteria"] if c["change"] != "same"]
    if not changed:
        out.append("- 바뀐 기준 없음")
    for c in changed:
        word = {"better": "나아짐", "worse": "나빠짐", "skip": "해당 없음 바뀜"}[c["change"]]
        out.append(f"- {c['label']}: {MARK[c['before']]} → {MARK[c['after']]} ({word})")
    for title, rows, side in (("고친 지적", result["fixed"], "이전"), ("새 지적", result["added"], "이후")):
        out += ["", f"## {title}"]
        if not rows:
            out.append("- 없음")
        for f in rows:
            out.append(f"- {side} {f['line']}줄 [{KIND[f['kind']]}] {f['text']} — \"{f['quote']}\"")
    return "\n".join(out)
