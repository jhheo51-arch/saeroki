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
# 낱말은 맞지만 다른 뜻인 제목: '사용자 흐름'은 사용자가 아니라 기능, '위험 신호'는 위험이 아니라 기능입니다.
NOT_KEYS = {"users": ("사용자 흐름", "사용자 지정", "사용자 확인", "사용자 설정", "사용자 반응"),
            "risk": ("위험 신호",)}
LONG_LINES = 500  # 표본 27개 중 이보다 긴 PRD 2개는 모두 구현 기록이 섞여 있었습니다.

INLINE_CODE = re.compile(r"`[^`]*`")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
NUMBER = re.compile(r"\d")
UNIT_NUMBER = re.compile(r"\d[\d,.]*\s*(%|배|명|건|개|회|번|만|억|원|시간|분|초)(?![성째차])")  # '1회성'은 통계가 아님
SOURCE = re.compile(r"https?://|출처|기준|공식|발표|따르면|소개|조사|측정|세어|센 |인터뷰|설문|자료|통계|보고서|로그|기록"
                    r"|\d{4}[-.]\d{1,2}|\d{4}년")
# 성공 지표는 '얼마나'가 있어야 잴 수 있습니다. 날짜·버전 번호만 있는 것은 세지 않습니다.
TARGET = re.compile(r"\d[\d,.]*\s*(%|배|명|건|개|회|번|만|억|원|시간|분|초|일|주|개월|점|위|ms)(?![성째차])|\d+\s*/\s*\d+")
PLAN = re.compile(r"목표로 한다|목표로 합니다|예정|계획|할 것이다|하겠습니다")  # 앞으로 할 조사는 근거가 아님
STRUCK = re.compile(r"~~.+~~|→\s*확정|\[x\]", re.IGNORECASE)  # 이미 풀린 질문
SKIP = re.compile(r"<!--\s*saerok-prd:\s*해당\s*없음\s+(\S+)\s*(.*?)\s*-->")
PENDING = re.compile(r"TBD|TODO|NEEDS CLARIFICATION|미정|추후\s*(결정|확정|논의)|\?\?|XXX", re.IGNORECASE)
NEGATION = re.compile(r"않|아니")
VAGUE = ("빠르게", "쉽게", "편리", "직관적", "다양한", "많은", "대부분", "최적", "효율적", "개선", "향상",
         "극대화", "획기적", "혁신", "사용자 친화", "원활", "간편")


def _subject(word: str) -> str:
    """받침에 맞춰 '이/가'를 붙입니다."""
    last = word[-1]
    return word + ("이" if "가" <= last <= "힣" and (ord(last) - ord("가")) % 28 else "가")


def _keys(title: str, extra: dict | None = None) -> set[str]:
    low = title.lower()
    for word in ("목표 사용자", "목표 고객", "target user"):  # '목표'가 지표가 아니라 사용자를 뜻할 때
        low = low.replace(word, "사용자")
    keys = set()
    for key, _, words in CRITERIA:
        words = (*words, *(w.lower() for w in (extra or {}).get(key, ())))
        rest = low
        for wrong in NOT_KEYS.get(key, ()):
            rest = rest.replace(wrong, "")
        if any(w in rest for w in words):
            keys.add(key)
    return keys


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


def _all(sections: list[Section], key: str, extra: dict | None = None) -> list[Section]:
    return [s for s in sections if key in _keys(s.title, extra) and s.level > 1]


def criterion(name: str) -> str | None:
    """'users'나 '대상 사용자'처럼 키나 이름으로 적은 기준을 키로 바꿉니다."""
    name = name.strip().lower().replace(" ", "")
    return next((k for k, label, _ in CRITERIA
                 if name in (k, label.lower().replace(" ", ""), label.split("(")[0].replace(" ", ""))), None)


def skips(text: str, config: dict | None = None) -> dict[str, str]:
    """'해당 없음'으로 밝힌 기준과 이유. 이유가 없으면 받지 않고, 문서 안 주석이 프로젝트 설정보다 우선합니다."""
    out = {}
    for name, why in ((config or {}).get("skip") or {}).items():
        if criterion(name) and str(why).strip():
            out[criterion(name)] = str(why).strip()
    for m in SKIP.finditer(text):
        if criterion(m.group(1)) and m.group(2):
            out[criterion(m.group(1))] = m.group(2)
    return out


def check(text: str, config: dict | None = None) -> dict:
    """config는 프로젝트 설정(.saerok-prd.json): {"words": {기준: [제목 낱말]}, "skip": {기준: 이유}}."""
    title, sections, lines = parse(text)
    extra = {criterion(k): v for k, v in ((config or {}).get("words") or {}).items() if criterion(k)}
    every = {key: _all(sections, key, extra) for key, _, _ in CRITERIA}
    found = {key: (secs[0] if secs else None) for key, secs in every.items()}
    criteria = []

    def add(key, status, note, sec=None):
        criteria.append({"key": key, "label": LABELS[key], "status": status, "note": note,
                         "line": sec.line if sec else None})

    problem = found["problem"]
    add("problem", "ok" if problem else "missing",
        f"'{problem.title}'" if problem else "무엇이 문제인지 따로 적은 절이 없습니다.", problem)

    evidence = found["evidence"]
    signal = problem and (UNIT_NUMBER.search(problem.text()) or SOURCE.search(problem.text()))
    done = [t for _, t in evidence.body if not PLAN.search(t)] if evidence else []
    if evidence and any(UNIT_NUMBER.search(t) or SOURCE.search(t) for t in done):
        add("evidence", "ok", f"'{evidence.title}'", evidence)
    elif evidence and signal:
        add("evidence", "ok", "문제 절 안에 숫자나 출처가 있습니다.", problem)
    elif evidence:
        add("evidence", "weak", f"'{evidence.title}'에 이미 확인한 숫자·날짜·출처가 없습니다. "
            "앞으로 할 조사 계획은 근거로 세지 않습니다.", evidence)
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
    elif not TARGET.search(re.sub(r"\d{4}[-.]\d{1,2}([-.]\d{1,2})?|v\d[\d.]*", "", metric.text())):
        add("metric", "weak", "얼마나 바뀌면 성공인지 단위 있는 숫자(%, 명, 회, 4주 등)가 없습니다.", metric)
    else:
        add("metric", "ok", f"'{metric.title}'", metric)

    for key, missing_note in (("users", "누구를 위한 것인지 적은 절이 없습니다."),
                              ("scope_out", "이번에 하지 않을 것을 적은 절이 없습니다."),
                              ("risk", "틀릴 수 있는 가정이나 위험을 적은 절이 없습니다."),
                              ("solution", "무엇을 만들지 적은 절이 없습니다.")):
        sec = found[key]
        body = [t for _, t in sec.body] if sec else []
        rows = [t for t in body if not set(t.strip()) <= set("|-: ")]  # 표 구분선은 내용이 아님
        open_rows = [t for t in rows if not STRUCK.search(t)]
        if not sec:
            add(key, "missing", missing_note)
        elif not rows:
            add(key, "weak", f"'{sec.title}' 제목만 있고 내용이 없습니다.", sec)
        elif key == "risk" and not open_rows:
            add(key, "weak", f"'{sec.title}'의 질문이 모두 풀렸습니다. 아직 남은 가정이나 위험을 적어 주세요.", sec)
        else:
            add(key, "ok", f"'{sec.title}'", sec)

    declared = skips(text, config)
    for c in criteria:
        if c["key"] in declared and c["status"] != "ok":
            c.update(status="skip", note=f"해당 없음: {declared[c['key']]}")

    findings = []
    if problem and found["solution"] and found["solution"].line < problem.line:
        findings.append({"line": found["solution"].line, "kind": "order",
                         "text": "해결책이 문제보다 먼저 나옵니다. 문제와 근거를 앞에 두세요.",
                         "quote": found["solution"].title})

    # '배경'과 '문제'처럼 문제 절이 여럿이면 모두 봅니다. 근거 절은 '남길 증거'처럼 다른 뜻이 많아 첫 절만 봅니다.
    evidence_lines = {no for s in every["problem"] + [evidence] if s for no, _ in s.body}
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

    warnings = []
    size = len(text.splitlines())
    if size > LONG_LINES:
        warnings.append({"kind": "long", "text": f"{size}줄로 깁니다. 구현 기록이나 회의록이 섞였다면 따로 빼고 결정만 남기세요."})
    missing = sum(c["status"] == "missing" for c in criteria)
    if missing >= 5:
        warnings.append({"kind": "not_prd", "text": f"기준 {missing}개가 빠졌습니다. PRD가 아니거나 `##` 제목으로 절을 나누지 않은 문서일 수 있습니다."})

    ok = sum(c["status"] == "ok" for c in criteria)
    total = sum(c["status"] != "skip" for c in criteria)  # '해당 없음'은 분모에서 뺍니다.
    return {"title": title, "criteria": criteria, "findings": findings, "warnings": warnings,
            "summary": {"ok": ok, "total": total, "findings": len(findings)}}


MARK = {"ok": "✅ 있음", "weak": "⚠️ 약함", "missing": "❌ 빠짐", "skip": "➖ 해당 없음"}
KIND = {"order": "순서", "pending": "미정", "vague": "모호", "unsourced": "출처"}


def render(result: dict) -> str:
    s = result["summary"]
    out = [f"# {result['title'] or '(제목 없음)'}",
           f"기준 {s['total']}개 중 {s['ok']}개 충족, 줄 지적 {s['findings']}개"]
    out += [f"⚠️ {w['text']}" for w in result.get("warnings", [])]
    out += ["", "## 기준표"]
    for c in result["criteria"]:
        where = f" ({c['line']}줄)" if c["line"] else ""
        out.append(f"- {MARK[c['status']]} {c['label']}{where}: {c['note']}")
    out += ["", "## 줄 지적"]
    if not result["findings"]:
        out.append("- 없음")
    for f in result["findings"]:
        out.append(f"- {f['line']}줄 [{KIND[f['kind']]}] {f['text']} — \"{f['quote']}\"")
    return "\n".join(out)
