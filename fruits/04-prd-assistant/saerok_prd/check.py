"""PRD를 기준표로 검사합니다.

AI 없이 규칙만으로 검사하므로 같은 PRD는 언제나 같은 결과가 나옵니다.
문장이 좋은지 나쁜지는 판단하지 않고, 빠진 칸과 근거 없이 쓴 줄만 짚습니다.
"""

import re
from dataclasses import dataclass, field


@dataclass
class Section:
    title: str
    level: int
    line: int  # 제목 줄 번호(1부터)
    body: list[tuple[int, str]] = field(default_factory=list)  # 하위 절까지 포함한 본문

    def text(self) -> str:
        return "\n".join(t for _, t in self.body)


# 제목에 이 말이 들어 있으면 그 기준의 절로 봅니다. '사용자와 목표'처럼 한 제목이 여러 기준에 들 수 있습니다.
CRITERIA = [
    ("problem", "해결할 문제", ("문제", "배경", "pain", "problem")),
    ("evidence", "문제의 근거", ("근거", "증거", "조사", "인터뷰", "리서치", "evidence", "research")),
    ("metric", "성공 지표", ("성공", "지표", "판정", "성과", "목표", "kpi", "metric", "success", "goal")),
    ("scope_out", "하지 않을 것", ("비목표", "범위 밖", "하지 않", "다루지 않", "제외", "만들지 않", "보류",
                         "non-goal", "out of scope")),
    ("risk", "가정과 위험", ("가정", "위험", "리스크", "한계", "열린 질문", "확인하지 못", "risk", "assumption")),
    ("users", "대상 사용자", ("사용자", "대상", "페르소나", "고객", "타깃", "독자", "사용하는 사람",
                        "user", "persona", "reader")),
    ("solution", "해결책(기능)", ("기능", "해결책", "요구사항", "요구 사항", "설계", "솔루션", "화면", "흐름", "확정", "명령", "구성", "동작",
                          "solution", "feature", "requirement", "flow")),
]
LABELS = {key: label for key, label, _ in CRITERIA}

INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBER = re.compile(r"\d")
UNIT_NUMBER = re.compile(r"\d[\d,.]*\s*(%|배|명|건|개|회|번|만|억|원|시간|분|초)(?![성째차])")  # '1회성'은 통계가 아님
SOURCE = re.compile(r"https?://|출처|기준|공식|발표|따르면|소개|조사|측정|세어|센 |인터뷰|설문|자료|통계|보고서|로그|기록"
                    r"|\d{4}[-.]\d{1,2}|\d{4}년")
PENDING = re.compile(r"TBD|TODO|미정|추후\s*(결정|확정|논의)|\?\?|XXX", re.IGNORECASE)
NEGATION = re.compile(r"않|아니")
VAGUE = ("빠르게", "쉽게", "편리", "직관적", "다양한", "많은", "대부분", "최적", "효율적", "개선", "향상",
         "극대화", "획기적", "혁신", "사용자 친화", "원활", "간편")


def _subject(word: str) -> str:
    """받침에 맞춰 '이/가'를 붙입니다."""
    last = word[-1]
    return word + ("이" if "가" <= last <= "힣" and (ord(last) - ord("가")) % 28 else "가")


def _keys(title: str) -> set[str]:
    low = title.lower()
    for word in ("목표 사용자", "목표 고객", "target user"):  # '목표'가 지표가 아니라 사용자를 뜻할 때
        low = low.replace(word, "사용자")
    return {key for key, _, words in CRITERIA if any(w in low for w in words)}


def parse(text: str) -> tuple[str | None, list[Section], list[tuple[int, str]]]:
    """제목, 절 목록, 코드 블록을 뺀 본문 줄을 돌려줍니다."""
    title = None
    sections: list[Section] = []
    lines: list[tuple[int, str]] = []
    fenced = False
    for no, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced:
            continue
        m = HEADING.match(line)
        if m:
            level, head = len(m.group(1)), m.group(2)
            if level == 1 and title is None:
                title = head
            sections.append(Section(head, level, no))
            continue
        if not line.strip():
            continue
        lines.append((no, line))
        # 하위 절의 본문은 위 절의 본문이기도 합니다.
        for s in sections:
            if s is sections[-1] or all(o.level > s.level for o in sections[sections.index(s) + 1:]):
                s.body.append((no, line))
    return title, sections, lines


def _first(sections: list[Section], key: str) -> Section | None:
    return next((s for s in sections if key in _keys(s.title) and s.level > 1), None)


def check(text: str) -> dict:
    title, sections, lines = parse(text)
    found = {key: _first(sections, key) for key, _, _ in CRITERIA}
    criteria = []

    def add(key, status, note, sec=None):
        criteria.append({"key": key, "label": LABELS[key], "status": status, "note": note,
                         "line": sec.line if sec else None})

    problem = found["problem"]
    add("problem", "ok" if problem else "missing",
        f"'{problem.title}'" if problem else "무엇이 문제인지 따로 적은 절이 없습니다.", problem)

    evidence = found["evidence"]
    signal = problem and (UNIT_NUMBER.search(problem.text()) or SOURCE.search(problem.text()))
    if evidence:
        add("evidence", "ok", f"'{evidence.title}'", evidence)
    elif signal:
        add("evidence", "ok", "문제 절 안에 숫자나 출처가 있습니다.", problem)
    else:
        add("evidence", "missing" if not problem else "weak",
            "문제가 실제로 있다는 숫자·인터뷰·출처가 보이지 않습니다.", problem)

    metric = found["metric"]
    if not metric:
        done = next((s for s in sections if "완료" in s.title), None)
        add("metric", "missing", f"'{done.title}'은 만들 목록일 뿐, 만든 뒤 효과를 볼 지표가 없습니다." if done
            else "무엇을 보고 성공이라 할지 적은 절이 없습니다.", done)
    elif not NUMBER.search(metric.text()):
        add("metric", "weak", "숫자로 된 기준(얼마나, 언제까지)이 없습니다.", metric)
    else:
        add("metric", "ok", f"'{metric.title}'", metric)

    for key, missing_note in (("users", "누구를 위한 것인지 적은 절이 없습니다."),
                              ("scope_out", "이번에 하지 않을 것을 적은 절이 없습니다."),
                              ("risk", "틀릴 수 있는 가정이나 위험을 적은 절이 없습니다."),
                              ("solution", "무엇을 만들지 적은 절이 없습니다.")):
        sec = found[key]
        add(key, "ok" if sec else "missing", f"'{sec.title}'" if sec else missing_note, sec)

    findings = []
    if problem and found["solution"] and found["solution"].line < problem.line:
        findings.append({"line": found["solution"].line, "kind": "order",
                         "text": "해결책이 문제보다 먼저 나옵니다. 문제와 근거를 앞에 두세요.",
                         "quote": found["solution"].title})

    evidence_lines = {no for s in (problem, evidence) if s for no, _ in s.body}
    # 모호한 말은 주장이 담기는 문제·근거·지표 절에서만 짚습니다.
    claim_lines = evidence_lines | ({no for no, _ in found["metric"].body} if found["metric"] else set())
    sourced = False  # 표 바로 위 문장에 출처가 있으면 표의 숫자도 그 출처를 따릅니다.
    for no, raw in lines:
        quote = raw.strip()[:80]
        line = INLINE_CODE.sub("", raw)  # `미정`처럼 따옴표로 든 말은 검사하지 않습니다.
        table = raw.lstrip().startswith("|")
        if not table:
            sourced = bool(SOURCE.search(line))
        if PENDING.search(line):
            findings.append({"line": no, "kind": "pending", "text": "정하지 않은 칸이 남아 있습니다.", "quote": quote})
        # '개선 과제'처럼 이름으로 쓴 말과 '주장하지 않습니다' 같은 부정문은 빼고 봅니다.
        plain = re.sub(r"(개선|향상)\s*(과제|안|사항|제안|점|본|조건|탭)", "", line)
        words = [w for w in VAGUE if w in plain] if no in claim_lines and not NEGATION.search(line) else []
        if words and not NUMBER.search(line):
            findings.append({"line": no, "kind": "vague",
                             "text": f"'{words[0]}'{_subject(words[0])[len(words[0]):]} 얼마만큼인지 숫자가 없습니다.", "quote": quote})
        if (no in evidence_lines and UNIT_NUMBER.search(line) and not SOURCE.search(line)
                and not (table and sourced)):
            findings.append({"line": no, "kind": "unsourced",
                             "text": "숫자의 출처나 잰 날짜가 없습니다.", "quote": quote})
    findings.sort(key=lambda f: f["line"])

    ok = sum(c["status"] == "ok" for c in criteria)
    return {"title": title, "criteria": criteria, "findings": findings,
            "summary": {"ok": ok, "total": len(criteria), "findings": len(findings)}}


MARK = {"ok": "✅ 있음", "weak": "⚠️ 약함", "missing": "❌ 빠짐"}
KIND = {"order": "순서", "pending": "미정", "vague": "모호", "unsourced": "출처"}


def render(result: dict) -> str:
    s = result["summary"]
    out = [f"# {result['title'] or '(제목 없음)'}",
           f"기준 {s['total']}개 중 {s['ok']}개 충족, 줄 지적 {s['findings']}개", "", "## 기준표"]
    for c in result["criteria"]:
        where = f" ({c['line']}줄)" if c["line"] else ""
        out.append(f"- {MARK[c['status']]} {c['label']}{where}: {c['note']}")
    out += ["", "## 줄 지적"]
    if not result["findings"]:
        out.append("- 없음")
    for f in result["findings"]:
        out.append(f"- {f['line']}줄 [{KIND[f['kind']]}] {f['text']} — \"{f['quote']}\"")
    return "\n".join(out)
