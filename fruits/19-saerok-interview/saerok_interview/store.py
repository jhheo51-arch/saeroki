"""면접관 결과·답변·실제 면접 질문을 검사해 score.json에 쌓고, 판정.md·practice.md를 만듭니다.
같은 score.json에서는 언제나 같은 파일이 나옵니다."""

import time
from pathlib import Path

from . import rubric
from .session import DOC_NAMES, load, read, write_json

QUESTIONS_PER_INTERVIEWER = 2


def _check_items(who: str, items: dict, na: dict, *, stage: str, posting: bool) -> tuple[dict, dict]:
    """항목 점수를 검사하고, 규칙으로 정해지는 해당 없음을 채웁니다. 잘못되면 ValueError."""
    if not isinstance(items, dict):
        raise ValueError(f"{who}: items는 항목별 점수 객체여야 합니다.")
    keys = {i["key"] for i in rubric.INTERVIEWERS[who]["items"]}
    unknown = set(items) - keys
    if unknown:
        raise ValueError(f"{who}: 모르는 기준 항목입니다: {', '.join(sorted(unknown))}")
    out_items, out_na = {}, {}
    for spec in rubric.INTERVIEWERS[who]["items"]:
        key = spec["key"]
        auto = rubric.auto_na(who, key, stage=stage, posting=posting)
        reason = auto or (na or {}).get(key)
        value = items.get(key)
        if auto or (reason and value is None):  # 규칙상 해당 없음이거나, 점수 없이 이유만 준 경우
            out_items[key], out_na[key] = None, reason
            continue
        if value is None:
            raise ValueError(f"{who}.{key}: 점수가 없습니다. 볼 수 없으면 na에 이유를 적어 주세요.")
        if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value <= spec["max"]:
            raise ValueError(f"{who}.{key}: 0~{spec['max']} 사이 정수여야 합니다(받은 값 {value!r}).")
        out_items[key] = value
    return out_items, out_na


def _verify_evidence(folder: Path, meta: dict, evidence: list) -> list[dict]:
    """근거 원문이 입력 파일의 그 줄(앞뒤 한 줄 허용)에 실제로 있는지 확인합니다."""
    checked = []
    for ev in evidence or []:
        doc, line, quote = ev.get("doc"), ev.get("line"), (ev.get("quote") or "").strip()
        status = "확인 안 됨"
        info = meta["inputs"].get(doc)
        if info and isinstance(line, int) and quote:
            lines = read(folder / info["file"]).splitlines()
            near = lines[max(line - 2, 0):line + 1]
            squash = lambda s: "".join(s.split())
            if any(squash(quote) in squash(row) for row in near):
                status = "확인"
        checked.append({"doc": doc, "line": line, "quote": quote, "status": status})
    return checked


def record_document(folder: Path, result: dict) -> dict:
    """면접관 한 명의 서류 심사 결과를 기록합니다. 같은 면접관을 다시 넣으면 바꿔 씁니다."""
    folder = Path(folder)
    meta, score = load(folder)
    who = result.get("interviewer")
    if who not in rubric.INTERVIEWERS:
        raise ValueError(f"모르는 면접관입니다: {who!r}. 가능한 값: {', '.join(rubric.ORDER)}")
    questions = result.get("questions") or []
    if len(questions) != QUESTIONS_PER_INTERVIEWER:
        raise ValueError(f"{who}: 질문은 {QUESTIONS_PER_INTERVIEWER}개여야 합니다(받은 수 {len(questions)}).")
    items, na = _check_items(who, result.get("items") or {}, result.get("na") or {}, stage="document", posting=meta["posting"])
    clean = []
    for q in questions:
        if not (q.get("question") or "").strip():
            raise ValueError(f"{who}: 빈 질문이 있습니다.")
        if q.get("item") not in items:
            raise ValueError(f"{who}: 질문의 item은 이 면접관의 기준 항목이어야 합니다(받은 값 {q.get('item')!r}).")
        evidence = _verify_evidence(folder, meta, q.get("evidence"))
        clean.append({
            "question": q["question"].strip(),
            "item": q["item"],
            "direction": (q.get("direction") or "").strip(),
            "evidence": evidence,
            "grounded": any(e["status"] == "확인" for e in evidence),
        })
    score["document"][who] = {
        "items": items,
        "na": na,
        "total": rubric.total10(who, items),
        "comment": (result.get("comment") or "").strip(),
        "fixes": [f.strip() for f in result.get("fixes") or [] if f.strip()],
        "questions": clean,
    }
    write_json(folder / "score.json", score)
    return score["document"][who]


def question_list(score: dict) -> list[dict]:
    """서류 질문 10개에 번호(Q1~)를 붙입니다. 면접관 순서는 rubric.ORDER."""
    out, no = [], 0
    for who in rubric.ORDER:
        for q in score["document"].get(who, {}).get("questions", []):
            no += 1
            out.append({"no": no, "interviewer": who, **q})
    return out


def next_question(folder: Path, who: list[str] | None = None) -> dict | None:
    """아직 답하지 않은 질문 중, 서류 점수가 낮은 면접관의 질문부터. who를 주면 그 면접관 질문만."""
    _, score = load(Path(folder))
    done = {a["no"] for a in score["answers"] if a.get("no")}
    totals = {who: score["document"].get(who, {}).get("total") for who in rubric.ORDER}
    for w in who or []:
        if w not in rubric.INTERVIEWERS:
            raise ValueError(f"모르는 면접관입니다: {w!r}. 가능한 값: {', '.join(rubric.ORDER)}")
    rest = [q for q in question_list(score) if q["no"] not in done and (not who or q["interviewer"] in who)]
    rest.sort(key=lambda q: (totals[q["interviewer"]] if totals[q["interviewer"]] is not None else 99, q["no"]))
    return rest[0] if rest else None


def record_answer(folder: Path, answer: dict) -> dict:
    folder = Path(folder)
    meta, score = load(folder)
    who = answer.get("interviewer")
    if who not in rubric.INTERVIEWERS:
        raise ValueError(f"모르는 면접관입니다: {who!r}")
    level = answer.get("level", "보통")
    if level not in rubric.LEVELS:
        raise ValueError(f"강도는 {', '.join(rubric.LEVELS)} 중 하나여야 합니다.")
    followups = answer.get("followups") or []
    if len(followups) > 2:
        raise ValueError("꼬리 질문은 질문당 2번까지입니다.")
    if not (answer.get("question") or "").strip() or not (answer.get("answer") or "").strip():
        raise ValueError("질문과 답이 모두 있어야 합니다.")
    items, na = _check_items(who, answer.get("items") or {}, answer.get("na") or {}, stage="answer", posting=meta["posting"])
    row = {
        "no": answer.get("no"),
        "date": answer.get("date") or time.strftime("%Y-%m-%d"),
        "interviewer": who,
        "level": level,
        "question": answer["question"].strip(),
        "answer": answer["answer"].strip(),
        "followups": [{"question": f.get("question", "").strip(), "answer": f.get("answer", "").strip()} for f in followups],
        "items": items,
        "na": na,
        "total": rubric.total10(who, items),
        "missing": [m for m in answer.get("missing") or [] if m],
        "better": (answer.get("better") or "").strip(),
    }
    score["answers"].append(row)
    write_json(folder / "score.json", score)
    (folder / "practice.md").write_text(render_practice(meta, score), encoding="utf-8")
    return row


def record_real(folder: Path, real: dict) -> dict:
    """실제 면접에서 받은 질문. matched(Q 번호)는 사용자가 확인한 것만 적중으로 셉니다."""
    folder = Path(folder)
    meta, score = load(folder)
    numbers = {q["no"] for q in question_list(score)}
    rows = []
    for q in real.get("questions") or []:
        text = (q.get("question") or "").strip()
        if not text:
            continue
        matched = q.get("matched")
        if matched is not None and matched not in numbers:
            raise ValueError(f"모의 질문 Q{matched}가 이 세션에 없습니다.")
        rows.append({"question": text, "matched": matched, "confirmed": bool(q.get("confirmed")) and matched is not None})
    if not rows:
        raise ValueError("실제 면접 질문이 없습니다.")
    entry = {"date": real.get("date") or time.strftime("%Y-%m-%d"), "company": real.get("company", meta.get("company", "")), "questions": rows}
    score["real"].append(entry)
    write_json(folder / "score.json", score)
    return entry


def _items_text(who: str, items: dict, na: dict) -> str:
    parts = []
    for spec in rubric.INTERVIEWERS[who]["items"]:
        value = items.get(spec["key"])
        shown = f"해당 없음({na.get(spec['key'], '')})" if value is None else f"{value}/{spec['max']}"
        parts.append(f"{spec['name']} {shown}")
    return " · ".join(parts)


def _fmt(score) -> str:
    return "-" if score is None else f"{score:g}"


def render_report(folder: Path) -> str:
    """판정.md 본문."""
    meta, score = load(Path(folder))
    lines = [
        f"# 새록 면접관 판정: {meta.get('company') or '회사 미지정'} ({meta['date']})",
        "",
        f"> {rubric.NOTICE}",
        "",
        "입력: " + ", ".join(DOC_NAMES[k] for k in meta["inputs"]) + ("" if meta["posting"] else " (공고 없음: 공고 관련 항목은 해당 없음)"),
    ]
    if meta.get("industry") or meta.get("role"):
        lines.append(f"산업·직무: {meta.get('industry') or '-'} / {meta.get('role') or '-'}")
    lines += ["", "## 판정표", "", "| 면접관 | 서류 점수 | 판정 | 한 줄 평 |", "|---|---:|---|---|"]
    missing = []
    for who in rubric.ORDER:
        doc = score["document"].get(who)
        name = rubric.INTERVIEWERS[who]["name"]
        if not doc:
            missing.append(name)
            lines.append(f"| {name} | - | 결과 없음 | |")
            continue
        lines.append(f"| {name} | {_fmt(doc['total'])}/10 | {rubric.verdict(doc['total'])} | {doc['comment']} |")
    if missing:
        lines += ["", f"아직 결과가 없는 면접관: {', '.join(missing)}"]
    lines += ["", "## 기준 항목", ""]
    for who in rubric.ORDER:
        if doc := score["document"].get(who):
            lines.append(f"- **{rubric.INTERVIEWERS[who]['name']}**: {_items_text(who, doc['items'], doc['na'])}")
    lines += ["", f"## 질문 {len(question_list(score))}개", ""]
    for q in question_list(score):
        spec = rubric.item(q["interviewer"], q["item"])
        lines.append(f"### Q{q['no']}. [{rubric.INTERVIEWERS[q['interviewer']]['name']} · {spec['name']}] {q['question']}")
        lines.append("")
        if q["evidence"]:
            for e in q["evidence"]:
                lines.append(f"- 근거({e['status']}): {DOC_NAMES.get(e['doc'], e['doc'])} {e['line']}줄 \"{e['quote']}\"")
        if not q["grounded"]:
            lines.append("- 근거 없음(일반 질문)" if not q["evidence"] else "- 근거 원문을 입력 파일에서 찾지 못했습니다. 일반 질문으로 봅니다.")
        if q["direction"]:
            lines.append(f"- 좋은 답의 방향: {q['direction']}")
        lines.append("")
    lines += ["## 고칠 점", ""]
    for who in rubric.ORDER:
        for fix in score["document"].get(who, {}).get("fixes", []):
            lines.append(f"- [{rubric.INTERVIEWERS[who]['name']}] {fix}")
    return "\n".join(lines).rstrip() + "\n"


def render_practice(meta: dict, score: dict) -> str:
    lines = [f"# 실전 연습 기록: {meta.get('company') or '회사 미지정'} ({meta['date']})", "", f"> {rubric.NOTICE}", ""]
    for n, a in enumerate(score["answers"], 1):
        who = rubric.INTERVIEWERS[a["interviewer"]]["name"]
        tag = f"Q{a['no']}" if a.get("no") else "추가 질문"
        lines += [f"## {n}. {tag} [{who} · {a['level']}] {a['question']}", "", f"**내 답**: {a['answer']}", ""]
        for f in a["followups"]:
            lines += [f"- 꼬리 질문: {f['question']}", f"  - 내 답: {f['answer']}"]
        lines += [
            "",
            f"**답변 점수**: {_fmt(a['total'])}/10 ({rubric.verdict(a['total'])}) · {_items_text(a['interviewer'], a['items'], a['na'])}",
        ]
        if a["missing"]:
            lines.append(f"**빠진 항목**: {', '.join(a['missing'])}")
        if a["better"]:
            lines.append(f"**더 좋은 답의 뼈대**: {a['better']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_report(folder: Path) -> Path:
    path = Path(folder) / "판정.md"
    path.write_text(render_report(folder), encoding="utf-8")
    return path
