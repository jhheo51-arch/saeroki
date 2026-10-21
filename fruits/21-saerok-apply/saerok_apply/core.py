"""새록 지원서의 결정적 규칙: 장부·공고·분석·초안 형식을 읽고, 글자 수와 사실 검사를 합니다.

파일을 읽거나 쓰지 않고 글만 받아 결과(dict)를 돌려줍니다. 같은 입력이면 언제나 같은 결과입니다.
웹 화면의 `web/apply-core.js`가 이 파일과 한 줄씩 같은 규칙을 갖고, 자동 검사가 두 결과를 비교합니다.
그래서 정규식은 두 언어에서 뜻이 같은 것만 씁니다(`\\d`·`\\w` 대신 `[0-9]`·`[A-Za-z]`)."""

import re

TYPES = ["경험형", "성장과정형", "지원 동기형", "직무 이해형", "미래·상상형"]
STAR = ["상황", "과제", "행동", "결과", "연결"]
SOURCES = ["공고", "조사", "의견"]
ACTION_TAGS = ["한 일", "설계안(도입 가정)", "계획"]
REQUIRED = ["기간", "소속·직함", "내 역할", "판단 이유", "행동", "결과", "역량"]
METRIC_REQUIRED = ["지표", "시점", "비교", "출처"]
METRIC_VALUES = ["전", "후", "값"]
UNCONFIRMED = "(AI 정리, 확인 전)"
IMAGE_MARK = "(이미지에서 옮김, 확인 전)"
NEED = "[사용자 확인 필요"
SPACES = " \t\n\r\f\v 　"

# 직함 낱말. 앞뒤가 다른 글자로 이어지면(리더십, 멘토링) 직함으로 보지 않습니다.
TEMPLATE_TITLE = "경험 이름"
LEDGER_EMPTY = "경험 장부가 비어 있습니다. 지원서를 쓰려면 먼저 경험을 전달해 주세요. 가지고 있는 이력서, 경력기술서, 메모 파일을 지원 폴더의 '경험자료' 폴더에 넣거나, 새록이 양식('## E01. 경험 이름')에 맞춰 ledger.md에 직접 써 주세요."
TITLES = ["프로젝트 매니저", "프로덕트 매니저", "부위원장", "위원장", "부회장", "회장", "팀장", "파트장", "리더", "대표",
          "총무", "매니저", "인턴", "기획자", "운영진", "운영자", "개발자", "디자이너", "분석가", "조장", "멘토",
          "간사", "사원", "주임", "대리", "과장", "차장", "부장", "실장", "본부장", "선임", "연구원", "조교", "반장",
          "PM", "PO"]
PARTICLES = ["으로서", "로서", "으로", "이었", "이자", "에게", "로", "을", "를", "이", "가", "은", "는", "의", "와",
             "과", "도", "에", "직", "였", "님", "들"]
# 시점·변화 표현. 장부에 같은 말이 있어야 씁니다.
CHANGE = ["벌어", "좁혀", "처음", "최초", "최대", "최고", "최저", "최소", "역대", "넘어섰", "돌파", "아래로", "밑으로",
          "역전", "앞질", "따라잡", "유일", "1위", "두 배", "절반"]
HEDGE = ["가정", "설계", "계획", "제안", "구상", "초안", "예정", "검토"]
ABSTRACT = ["크게 개선", "크게 향상", "크게 늘", "크게 줄", "크게 기여", "많이 기여", "많은 기여", "큰 성과", "많은 성과",
            "좋은 성과", "눈에 띄게", "획기적", "대폭", "상당히", "극대화", "많은 도움", "큰 도움", "큰 변화"]
TEAM = ["우리 팀", "저희 팀", "팀 전체", "팀은", "팀이", "저희는", "저희가", "우리는", "우리가", "동아리는", "동아리가"]
SELF = ["제가", "저는", "나는", "내가", "저 혼자", "직접", "제 역할", "저의", "제 몫"]
REASON = ["때문", "위해", "이유", "판단", "근거로", "보고", "생각해", "하려고", "고자", "목표로", "알기 위해", "봤기", "보았기"]
LINK = ["직무", "입사", "지원한", "살려", "하겠습니다", "기여하고", "이어가"]
UNITS = ["%p", "%", "퍼센트", "개월", "명", "건", "개", "원", "만", "억", "천", "배", "주", "년", "월", "일", "시간",
         "분기", "학기", "회", "위", "점", "곳", "권", "장", "달"]
PERIOD_UNITS = ["개월", "주", "년", "월", "일", "시간", "분기", "학기", "달"]
TYPE_WORDS = [
    ("미래·상상형", ["10년", "미래", "일기", "상상", "만약", "뒤의 나", "후의 모습"]),
    ("지원 동기형", ["지원 동기", "지원한 이유", "지원하게 된", "입사 후", "포부", "왜 우리"]),
    ("성장과정형", ["성장 과정", "성장과정", "가치관", "살아온", "성격", "좌우명"]),
    ("경험형", ["실패", "성과", "협업", "갈등", "어려움", "극복", "도전", "경험", "문제를 해결", "주도"]),
    ("직무 이해형", ["직무", "역량", "이해", "업무", "전문성"]),
]
TERM_GLOSS = ["이란", "란", "은", "는", "이", "가"]

NUM = re.compile(r"[0-9][0-9,]*(?:\.[0-9]+)?")
ID = re.compile(r"^E[0-9]{2,}$")
DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
URL = re.compile(r"https?://[^\s)>\]|]+")
COMMENT_SPLIT = re.compile(r"<!--([\s\S]*?)-->")
FIELD = re.compile(r"^-\s*([^:：]+?)\s*[:：]\s*(.*)$")
SUBITEM = re.compile(r"^\s+[-*]\s*(.*)$")
ACTION = re.compile(r"^\[([^\]]+)\]\s*(.*)$")
LEDGER_HEAD = re.compile(r"^##\s+(E[0-9]{2,})(?![0-9])[\s.·:\-]*(.*)$")
LIMIT = re.compile(r"([0-9][0-9,]*)\s*(자|바이트|byte|bytes)\s*(?:\(\s*(공백 포함|공백 제외)\s*\))?")
VERSION = re.compile(r"^v([0-9]+)\s*[·:\-—–]\s*(.+)$")
PER_UNIT = re.compile(r"[가-힣0-9]+당")
YEAR = re.compile(r"20[0-9]{2}")
HALF = re.compile(r"상반기|하반기|[1-4]분기")


# ---------- 작은 도구 ----------

def chars(text: str) -> list[str]:
    return list(text)


def count(text: str) -> dict:
    """공백 포함·공백 제외·바이트(UTF-8, 한글 3바이트). 줄바꿈은 공백 포함 수에 1자로 셉니다."""
    no_space = sum(1 for ch in text if ch not in SPACES)
    return {"with_spaces": len(text), "without_spaces": no_space, "bytes": len(text.encode("utf-8"))}


def fit(counted: dict, limit: int | None, basis: str) -> dict:
    """제한의 90~100%면 ok, 넘으면 over, 90% 아래면 short. 제한이 없으면 no-limit."""
    if not limit:
        return {"value": counted["with_spaces"], "ratio": None, "fit": "no-limit"}
    value = counted[basis]
    ratio = value * 100 // limit
    state = "over" if value > limit else ("short" if value * 10 < limit * 9 else "ok")
    return {"value": value, "ratio": ratio, "fit": state}


def norm_num(n: str) -> str:
    n = n.replace(",", "")
    if "." in n:
        n = n.rstrip("0").rstrip(".")
        return n or "0"
    return n.lstrip("0") or "0"


def numbers(text: str, strict: bool = True) -> list[dict]:
    """문장 속 숫자. strict면 '1인당'처럼 단위 앞 숫자와 영문 낱말 속 숫자(B2B)는 뺍니다."""
    out = []
    for m in NUM.finditer(text):
        raw = m.group(0).rstrip(",")
        start, end = m.start(), m.start() + len(raw)
        before = text[start - 1] if start > 0 else ""
        rest = text[end:]
        if strict and before and ("A" <= before <= "Z" or "a" <= before <= "z"):
            continue
        unit = ""
        stripped = rest.lstrip(" ")
        for u in UNITS:
            if stripped.startswith(u):
                unit = u
                break
        if strict and (stripped[len(unit):].startswith("당") or (not unit and stripped[:2] in ("인당", "건당"))):
            continue
        if strict and stripped[:1] == "당":
            continue
        out.append({"raw": raw, "value": norm_num(raw), "unit": unit,
                    "kind": "기간" if unit in PERIOD_UNITS else "숫자"})
    return out


def is_past(text: str) -> bool:
    """'했습니다'·'였다'처럼 과거형으로 끝나는 문장(받침 ㅆ). '있다'·'하겠다'는 빼고 봅니다."""
    s = re.sub(r"[\s.!?\"'”’)\]]+$", "", text)
    if s.endswith("습니다"):
        prev = s[-4:-3]
    elif s.endswith("다"):
        prev = s[-2:-1]
    else:
        return False
    if not prev or prev in "있겠없":
        return False
    code = ord(prev) - 0xAC00
    return 0 <= code < 11172 and code % 28 == 20


def is_future(text: str) -> bool:
    """'하겠습니다'·'하고 싶습니다'처럼 앞으로의 일을 말하는 문장."""
    s = re.sub(r"[\s.!?\"'”’)\]]+$", "", text)
    return "겠" in s[-6:] or "싶" in s[-6:]


def _hangul_or_latin(ch: str) -> bool:
    return bool(ch) and ("가" <= ch <= "힣" or "A" <= ch <= "Z" or "a" <= ch <= "z")


def titles_in(text: str) -> list[str]:
    found = []
    for title in TITLES:
        i = text.find(title)
        while i != -1:
            before = text[i - 1] if i > 0 else ""
            after = text[i + len(title):]
            ok_before = not _hangul_or_latin(before)
            ok_after = (not after or not _hangul_or_latin(after[0]) or any(after.startswith(p) for p in PARTICLES))
            if ok_before and ok_after and title not in found:
                found.append(title)
                break
            i = text.find(title, i + 1)
    return found


def _is_ascii_word(ch: str) -> bool:
    return bool(ch) and ("A" <= ch <= "Z" or "a" <= ch <= "z" or "0" <= ch <= "9")


def find_name(text: str, name: str) -> int:
    """이름이 처음 나오는 자리(없으면 -1). 영문 이름은 대소문자를 가리지 않고 낱말 경계를 봅니다."""
    if not name:
        return -1
    ascii_name = all(ord(ch) < 128 for ch in name)
    hay, needle = (text.lower(), name.lower()) if ascii_name else (text, name)
    i = hay.find(needle)
    while i != -1:
        if not ascii_name:
            return i
        before = hay[i - 1] if i > 0 else ""
        after = hay[i + len(needle)] if i + len(needle) < len(hay) else ""
        if not _is_ascii_word(before) and not _is_ascii_word(after):
            return i
        i = hay.find(needle, i + 1)
    return -1


def bigrams(text: str) -> set[str]:
    s = "".join(ch for ch in text if ch not in SPACES and ch not in ".,!?'\"“”‘’()[]·:;-")
    return {s[i:i + 2] for i in range(len(s) - 1)}


def plain(text: str) -> str:
    """주석을 지운 글."""
    return COMMENT_SPLIT.sub("", text)


def squash(text: str) -> str:
    return "".join(ch for ch in plain(text) if ch not in SPACES and ch not in ".,!?'\"“”‘’()[]·:;-")


def guess_type(title: str) -> str:
    for kind, words in TYPE_WORDS:
        if any(w in title for w in words):
            return kind
    return "경험형"


# ---------- 문장 나누기 ----------

def _parse_tag(raw: str) -> dict:
    tag = {"ids": [], "labels": [], "sources": [], "unknown": []}
    for token in re.split(r"[\s,]+", raw.strip()):
        if not token:
            continue
        if ID.match(token):
            tag["ids"].append(token)
        elif token in STAR:
            tag["labels"].append(token)
        elif token in SOURCES:
            tag["sources"].append(token)
        else:
            tag["unknown"].append(token)
    return tag


def sentences(block: str) -> list[dict]:
    """문단을 문장으로 나누고, 문장 뒤의 `<!-- E01 행동 -->` 주석을 그 문장에 붙입니다."""
    parts = COMMENT_SPLIT.split(block)
    out = []
    for k, part in enumerate(parts):
        if k % 2 == 1:
            if out:
                tag = _parse_tag(part)
                for key in ("ids", "labels", "sources", "unknown"):
                    for v in tag[key]:
                        if v not in out[-1][key]:
                            out[-1][key].append(v)
            continue
        start = 0
        for i, ch in enumerate(part):
            if ch in ".!?" and (i + 1 == len(part) or part[i + 1] in SPACES):
                text = part[start:i + 1].strip()
                if text:
                    out.append({"text": text, "ids": [], "labels": [], "sources": [], "unknown": []})
                start = i + 1
        tail = part[start:].strip()
        if tail:
            out.append({"text": tail, "ids": [], "labels": [], "sources": [], "unknown": []})
    return out


def _paragraphs(lines: list[str]) -> list[str]:
    paras, cur = [], []
    for line in lines:
        if not line.strip():
            if cur:
                paras.append("\n".join(cur))
                cur = []
        elif line.lstrip().startswith(">"):
            continue
        else:
            cur.append(line.strip())
    if cur:
        paras.append("\n".join(cur))
    return paras


def body_text(paras: list[str]) -> str:
    """제출·글자 수 세기에 쓰는 본문: 주석을 지우고 문단 사이를 줄바꿈 하나로 잇습니다."""
    out = []
    for p in paras:
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in plain(p).split("\n")]
        text = "\n".join(ln for ln in lines if ln)
        if text:
            out.append(text)
    return "\n".join(out)


def _table_rows(lines: list[str]) -> list[list[str]]:
    rows = []
    for line in lines:
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
            continue
        rows.append(cells)
    return rows[1:] if rows else []


def _sections(text: str, level: str = "## ") -> tuple[list[str], list[tuple[str, list[str]]]]:
    head, sections = [], []
    for line in text.replace("\r\n", "\n").split("\n"):
        if line.startswith(level):
            sections.append((line[len(level):].strip(), []))
        elif sections:
            sections[-1][1].append(line)
        else:
            head.append(line)
    return head, sections


def _fields(lines: list[str]) -> dict:
    out = {}
    for line in lines:
        m = FIELD.match(line.strip())
        if m and m.group(1).strip() not in out:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


# ---------- 경험 장부 ----------

def parse_ledger(text: str) -> dict:
    experiences, issues = [], []
    _, sections = _sections(text)
    seen = set()
    for heading, lines in sections:
        m = LEDGER_HEAD.match("## " + heading)
        if not m:
            continue
        exp = {"id": m.group(1), "title": m.group(2).strip(), "fields": {}, "actions": [], "metrics": [],
               "competencies": [], "unconfirmed": []}
        where = exp["id"]
        if exp["id"] in seen:
            issues.append({"level": "error", "code": "ledger_dup_id", "where": where, "text": "",
                           "message": f"경험 ID {exp['id']}가 두 번 나옵니다."})
        seen.add(exp["id"])
        current = ""
        for line in lines:
            if not line.strip():
                continue
            sub = SUBITEM.match(line)
            if sub and current in ("행동", "수치"):
                item = sub.group(1).strip()
                if current == "행동":
                    a = ACTION.match(item)
                    if not a or a.group(1) not in ACTION_TAGS:
                        issues.append({"level": "error", "code": "ledger_action_tag", "where": where, "text": item,
                                       "message": "행동 앞에 [한 일]·[설계안(도입 가정)]·[계획] 중 하나를 붙여 주세요."})
                        continue
                    exp["actions"].append({"tag": a.group(1), "text": a.group(2).strip(),
                                           "confirmed": UNCONFIRMED not in item})
                    if UNCONFIRMED in item and "행동" not in exp["unconfirmed"]:
                        exp["unconfirmed"].append("행동")
                else:
                    metric = {"raw": item, "confirmed": UNCONFIRMED not in item}
                    for piece in item.split("|"):
                        kv = re.match(r"^\s*([^:：]+?)\s*[:：]\s*(.*?)\s*$", piece)
                        if kv:
                            metric[kv.group(1)] = kv.group(2)
                    missing = [k for k in METRIC_REQUIRED if not metric.get(k)]
                    if not (metric.get("값") or (metric.get("전") and metric.get("후"))):
                        missing.append("전·후 또는 값")
                    if missing:
                        issues.append({"level": "error", "code": "ledger_metric", "where": where, "text": item,
                                       "message": f"수치에 {', '.join(missing)} 칸이 없습니다."})
                    exp["metrics"].append(metric)
                    if UNCONFIRMED in item and "수치" not in exp["unconfirmed"]:
                        exp["unconfirmed"].append("수치")
                continue
            f = FIELD.match(line.strip()) if not line.startswith((" ", "\t")) else None
            if f:
                current = f.group(1).strip()
                exp["fields"][current] = f.group(2).strip()
                if UNCONFIRMED in f.group(2) and current not in exp["unconfirmed"]:
                    exp["unconfirmed"].append(current)
        for key in REQUIRED:
            if key == "행동":
                if not exp["actions"]:
                    issues.append({"level": "error", "code": "ledger_field", "where": where, "text": "",
                                   "message": "행동이 없습니다. '- 행동:' 아래에 [한 일] 등으로 적어 주세요."})
            elif not exp["fields"].get(key):
                issues.append({"level": "error", "code": "ledger_field", "where": where, "text": "",
                               "message": f"'{key}' 칸이 비었습니다."})
        exp["competencies"] = [c.strip() for c in re.split(r"[,，]", plain(exp["fields"].get("역량", "")))
                               if c.strip() and c.strip() != UNCONFIRMED]
        confirmed, everything = [exp["title"]], [exp["title"]]
        for key, value in exp["fields"].items():
            everything.append(value)
            if UNCONFIRMED not in value:
                confirmed.append(value)
        for a in exp["actions"]:
            everything.append(a["text"])
            if a["confirmed"]:
                confirmed.append(a["text"])
        for mt in exp["metrics"]:
            everything.append(mt["raw"])
            if mt["confirmed"]:
                confirmed.append(mt["raw"])
        exp["evidence"] = "\n".join(confirmed)
        exp["all_text"] = "\n".join(everything)
        experiences.append(exp)
    # 경험이 없거나 init이 만든 양식('경험 이름')만 있으면 빈 장부로 봅니다.
    if all(e["title"] == TEMPLATE_TITLE for e in experiences):
        issues.append({"level": "error", "code": "ledger_empty", "where": "장부", "text": "", "message": LEDGER_EMPTY})
    return {"experiences": experiences, "issues": issues}


def ledger_report(text: str) -> dict:
    parsed = parse_ledger(text)
    rows = [{"id": e["id"], "title": e["title"], "period": e["fields"].get("기간", ""),
             "competencies": e["competencies"], "actions": {t: sum(1 for a in e["actions"] if a["tag"] == t)
                                                            for t in ACTION_TAGS},
             "metrics": len(e["metrics"]), "unconfirmed": e["unconfirmed"]} for e in parsed["experiences"]]
    errors = sum(1 for i in parsed["issues"] if i["level"] == "error")
    return {"experiences": rows, "issues": parsed["issues"],
            "summary": {"experiences": len(rows), "errors": errors,
                        "unconfirmed": sum(1 for r in rows if r["unconfirmed"])}}


# ---------- 공고·분석 ----------

def parse_posting(text: str) -> dict:
    head, sections = _sections(text)
    meta = _fields(head)
    body = ""
    for heading, lines in sections:
        if heading.startswith("원문"):
            body = "\n".join(lines).strip()
    status = meta.get("상태", "")
    if IMAGE_MARK in text and "확인함" not in status:
        status = IMAGE_MARK
    return {"company": meta.get("회사", ""), "source": meta.get("출처", ""), "checked_at": meta.get("확인 날짜", ""),
            "image": meta.get("원본 이미지", ""), "status": status or "확인함", "body": body}


def parse_analysis(text: str) -> dict:
    out = {"items": [], "keywords": [], "posting_info": "", "research": [], "research_status": "",
           "research_text": "", "terms": [], "sections": []}
    _, sections = _sections(text)
    for heading, lines in sections:
        out["sections"].append(heading)
        if heading.startswith("요구·우대 역량"):
            for cells in _table_rows(lines):
                if cells and cells[0]:
                    out["items"].append({"item": plain(cells[0]).strip(), "kind": cells[1] if len(cells) > 1 else "",
                                         "ids": re.findall(r"E[0-9]{2,}", cells[3]) if len(cells) > 3 else [],
                                         "gap": cells[4] if len(cells) > 4 else ""})
        elif heading.startswith("세부 업무"):
            for line in lines:
                m = re.match(r"^\s*[-*]\s+(.+)$", line)
                if m:
                    out["items"].append({"item": plain(m.group(1)).strip(), "kind": "업무", "ids": [], "gap": ""})
        elif heading.startswith("숨은 키워드"):
            marked = "AI 해석" in heading
            for line in lines:
                m = re.match(r"^\s*[-*]\s+(.+)$", line)
                if m:
                    out["keywords"].append({"text": m.group(1).strip(), "ai": marked or "AI 해석" in m.group(1)})
        elif heading.startswith("회사·직무 맥락"):
            sub_head, subs = _sections("\n".join(lines), "### ")
            for sub, sub_lines in subs:
                joined = "\n".join(sub_lines).strip()
                if sub.startswith("공고 안 정보"):
                    out["posting_info"] = joined
                elif sub.startswith("회사 조사"):
                    out["research_text"] = joined
                    for line in sub_lines:
                        m = re.match(r"^\s*[-*]\s+(.+)$", line)
                        if not m:
                            continue
                        item = m.group(1).strip()
                        if "자료 없음" in item or "조사 안 됨" in item:
                            continue
                        url, date = URL.search(item), DATE.search(item)
                        out["research"].append({"text": item, "url": url.group(0) if url else "",
                                                "date": date.group(0) if date else ""})
                    if "조사 안 됨" in joined:
                        out["research_status"] = "조사 안 됨"
                    elif "자료 없음" in joined or not out["research"]:
                        out["research_status"] = "자료 없음"
                    else:
                        out["research_status"] = "있음"
        elif heading.startswith("용어"):
            for cells in _table_rows(lines):
                if cells and cells[0]:
                    out["terms"].append({"term": cells[0], "meaning": cells[1] if len(cells) > 1 else ""})
    return out


def _term_names(entry: dict) -> list[str]:
    names = []
    for name in [entry.get("term", ""), entry.get("korean", ""), entry.get("original", ""), *entry.get("aliases", [])]:
        if name and len(name) >= 2 and name not in names:
            names.append(name)
    return names


def _term_index(terms: dict | None) -> dict:
    index = {}
    for entry in (terms or {}).get("terms", []):
        for name in _term_names(entry):
            index.setdefault(name.lower(), entry)
    return index


def _sense(entry: dict, industry: str, role: str) -> dict:
    senses = entry.get("senses", [])
    for s in senses:
        if (not industry or industry in s["industries"]) and (not role or role in s["roles"]):
            return s
    return senses[0] if senses else {"definition": "", "level": ""}


def match_terms(text: str, terms: dict | None, industry: str = "", role: str = "") -> list[dict]:
    """공고 글에 나오는 17번 사전 용어(표제어·원어·별칭). 처음 나온 순서대로."""
    found = []
    for entry in (terms or {}).get("terms", []):
        best = -1
        hit = ""
        for name in _term_names(entry):
            i = find_name(text, name)
            if i != -1 and (best == -1 or i < best):
                best, hit = i, name
        if best != -1:
            s = _sense(entry, industry, role)
            found.append({"term": entry["term"], "found": hit, "at": best, "level": s.get("level", ""),
                          "definition": s.get("definition", "")})
    found.sort(key=lambda f: (f["at"], f["term"]))
    return [{k: f[k] for k in ("term", "found", "level", "definition")} for f in found]


def check_analysis(posting_text: str, analysis_text: str, terms: dict | None = None) -> dict:
    """공고·분석 파일 점검. 공고 읽기 실패, 이미지 확인 전, 회사 조사 없음, 사전에 없는 용어를 따로 표시합니다."""
    issues = []
    posting = parse_posting(posting_text or "")
    flags = {"posting_failed": False, "image_unconfirmed": False, "research_none": False, "terms_missing": []}
    if not posting_text or not posting_text.strip():
        flags["posting_failed"] = True
        issues.append({"level": "error", "code": "posting_missing", "where": "posting.md", "text": "",
                       "message": "공고 원문이 없습니다. 붙여넣기나 캡처 이미지로 넣어 주세요."})
    elif "읽기 실패" in posting["status"]:
        flags["posting_failed"] = True
        issues.append({"level": "error", "code": "posting_failed", "where": "posting.md", "text": posting["source"],
                       "message": "공고를 읽지 못했습니다. 빈 공고로 분석하지 않습니다. 본문을 붙여 넣거나 캡처를 넣어 주세요."})
    elif posting["status"] == IMAGE_MARK:
        flags["image_unconfirmed"] = True
        issues.append({"level": "error", "code": "image_unconfirmed", "where": "posting.md", "text": posting["image"],
                       "message": "이미지에서 옮긴 공고를 아직 확인하지 않았습니다. 확인 전에는 분석하지 않습니다."})
    else:
        if not posting["body"]:
            flags["posting_failed"] = True
            issues.append({"level": "error", "code": "posting_empty", "where": "posting.md", "text": "",
                           "message": "'## 원문' 아래가 비었습니다."})
        if not posting["source"]:
            issues.append({"level": "error", "code": "posting_source", "where": "posting.md", "text": "",
                           "message": "'- 출처:'(URL, 붙여넣기, 이미지)가 없습니다."})
        if not DATE.search(posting["checked_at"]):
            issues.append({"level": "error", "code": "posting_date", "where": "posting.md", "text": "",
                           "message": "'- 확인 날짜: YYYY-MM-DD'가 없습니다."})
    blocked = flags["posting_failed"] or flags["image_unconfirmed"]
    analysis = parse_analysis(analysis_text or "")
    if analysis_text and analysis_text.strip():
        for name in ["요구·우대 역량", "숨은 키워드", "회사·직무 맥락", "용어"]:
            if not any(h.startswith(name) for h in analysis["sections"]):
                issues.append({"level": "error", "code": "analysis_section", "where": "analysis.md", "text": "",
                               "message": f"'## {name}' 칸이 없습니다."})
        if not analysis["items"]:
            issues.append({"level": "error", "code": "analysis_items", "where": "analysis.md", "text": "",
                           "message": "요구·우대 역량 표가 비었습니다."})
        for k in analysis["keywords"]:
            if not k["ai"]:
                issues.append({"level": "error", "code": "keyword_not_marked", "where": "analysis.md", "text": k["text"],
                               "message": "숨은 키워드는 'AI 해석'으로 표시합니다."})
        if analysis["research_status"] in ("자료 없음", "조사 안 됨", ""):
            flags["research_none"] = True
            issues.append({"level": "warn", "code": "research_none", "where": "analysis.md", "text": "",
                           "message": f"회사 조사: {analysis['research_status'] or '자료 없음'}. 자기소개서에 회사 조사 내용을 쓰지 않습니다."})
        for r in analysis["research"]:
            if not r["url"] or not r["date"]:
                issues.append({"level": "error", "code": "research_no_source", "where": "analysis.md", "text": r["text"],
                               "message": "회사 조사 항목에는 출처 링크와 확인 날짜(YYYY-MM-DD)가 있어야 합니다."})
        index = _term_index(terms)
        for t in analysis["terms"]:
            if "사전에 없음" in t["meaning"]:
                flags["terms_missing"].append(t["term"])
            elif t["term"].lower() not in index:
                issues.append({"level": "error", "code": "term_not_in_dictionary", "where": "analysis.md", "text": t["term"],
                               "message": "17번 사전에 없는 용어입니다. 뜻 칸을 '사전에 없음'으로 바꿔 주세요."})
        if flags["terms_missing"]:
            issues.append({"level": "warn", "code": "terms_missing", "where": "analysis.md",
                           "text": ", ".join(flags["terms_missing"]),
                           "message": "사전에 없는 용어입니다. 뜻은 공고 원문으로 확인해 주세요."})
    errors = sum(1 for i in issues if i["level"] == "error")
    return {"posting": {k: posting[k] for k in ("company", "source", "checked_at", "image", "status")},
            "blocked": blocked, "flags": flags, "items": analysis["items"], "issues": issues,
            "summary": {"errors": errors, "warnings": len(issues) - errors, "ready": errors == 0}}


# ---------- 표기 규칙 ----------

def parse_style(text: str) -> dict:
    style = {"banned": [], "replace": [], "max_sentence": 0, "tone": ""}
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        m = FIELD.match(line.strip())
        if not m:
            continue
        key, value = m.group(1).strip(), m.group(2).strip()
        if key == "쓰지 않음" and value:
            style["banned"].append(value)
        elif key == "바꿈" and "→" in value:
            a, b = value.split("→", 1)
            if a.strip():
                style["replace"].append([a.strip(), b.strip()])
        elif key == "문장 길이":
            n = re.search(r"[0-9]+", value)
            style["max_sentence"] = int(n.group(0)) if n else 0
        elif key == "말투" and value in ("합니다", "해요", "한다"):
            style["tone"] = value
    return style


def _tone_ok(text: str, tone: str) -> bool:
    s = re.sub(r"[\s.!?\"'”’)\]]+$", "", text)
    if tone == "합니다":
        return s.endswith("니다") or s.endswith("니까")
    if tone == "해요":
        return s.endswith("요")
    if tone == "한다":
        return s.endswith("다") and not s.endswith("니다")
    return True


# ---------- 자기소개서 초안 ----------

def parse_draft(text: str) -> dict:
    head, sections = _sections(text)
    meta = _fields(head)
    questions, short = [], []
    for index, (heading, lines) in enumerate(sections):
        if heading.startswith("짧은 칸"):
            for cells in _table_rows(lines):
                if len(cells) < 3 or not cells[0]:
                    continue
                n = re.search(r"[0-9]+", cells[1])
                content = cells[2]
                tags = sentences(content)
                ids, sources = [], []
                for s in tags:
                    ids += [i for i in s["ids"] if i not in ids]
                    sources += [i for i in s["sources"] if i not in sources]
                short.append({"name": cells[0], "limit": int(n.group(0)) if n else None,
                              "content": plain(content).strip(), "ids": ids, "sources": sources})
            continue
        m = re.match(r"^문항\s*([0-9]+)\s*[.:)·]?\s*(.*)$", heading)
        q = {"no": int(m.group(1)) if m else len(questions) + 1, "title": (m.group(2) if m else heading).strip(),
             "meta": {}, "paras": [], "raw": ""}
        main = []
        for line in lines:
            if line.startswith("### "):
                break
            main.append(line)
        i = 0
        while i < len(main) and not main[i].strip():
            i += 1
        while i < len(main):
            f = FIELD.match(main[i].strip())
            if not main[i].strip():
                i += 1
                continue
            if not f or f.group(1).strip() not in ("유형", "제한", "판", "상태", "연결", "경험"):
                break
            q["meta"][f.group(1).strip()] = f.group(2).strip()
            i += 1
        q["paras"] = _paragraphs(main[i:])
        q["raw"] = "\n\n".join(q["paras"])
        limit = LIMIT.search(q["meta"].get("제한", ""))
        q["limit"] = int(limit.group(1).replace(",", "")) if limit else None
        q["basis"] = ("bytes" if limit and limit.group(2) != "자" else
                      "without_spaces" if limit and limit.group(3) == "공백 제외" else "with_spaces")
        ver = VERSION.match(q["meta"].get("판", ""))
        q["version"] = f"v{ver.group(1)}" if ver else ""
        q["change"] = ver.group(2).strip() if ver else ""
        q["confirmed"] = q["meta"].get("상태", "").strip() == "확정"
        q["type"] = q["meta"].get("유형", "").strip()
        q["links"] = [c.strip() for c in re.split(r"[,，]", q["meta"].get("연결", "")) if c.strip()]
        questions.append(q)
    return {"company": meta.get("회사", ""), "mode": meta.get("모드", "초안"), "original": meta.get("원문", ""),
            "date": meta.get("날짜", ""), "questions": questions, "short": short}


def submission(text: str) -> str:
    """제출용 본문: 장부 ID 주석·안내 줄·판 정보를 뺀 글."""
    draft = parse_draft(text)
    out = [f"# 자기소개서 · {draft['company']}" if draft["company"] else "# 자기소개서", ""]
    for q in draft["questions"]:
        out += [f"## 문항 {q['no']}. {q['title']}".rstrip(), ""]
        for p in q["paras"]:
            lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in plain(p).split("\n")]
            para = "\n".join(ln for ln in lines if ln)
            if para:
                out += [para, ""]
    if draft["short"]:
        out += ["## 짧은 칸", ""]
        out += [f"- {s['name']}: {s['content']}" for s in draft["short"]]
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def _issue(issues: list, level: str, code: str, where: str, text: str, message: str) -> None:
    issues.append({"level": level, "code": code, "where": where, "text": text, "message": message})


def _evidence(exps: dict, ids: list[str]) -> tuple[str, str]:
    found = [exps[i] for i in ids if i in exps]
    return "\n".join(e["evidence"] for e in found), "\n".join(e["all_text"] for e in found)


def _fact_checks(issues, where, s, exps, posting_body, research_text):
    """한 문장(또는 짧은 칸)의 숫자·직함·기간·지표·시점·설계안 대조."""
    text = s["text"]
    ids = [i for i in s["ids"] if i in exps]
    if ids:
        evidence, everything = _evidence(exps, ids)
        have = {n["value"] for n in numbers(evidence, strict=False)}
        have_all = {n["value"] for n in numbers(everything, strict=False)}
        for n in numbers(text):
            if n["value"] in have:
                continue
            what = "기간·시점" if n["kind"] == "기간" else "숫자"
            if n["value"] in have_all:
                _issue(issues, "error", "unconfirmed_ledger", where, text,
                       f"{n['raw']}{n['unit']}는 장부의 '(AI 정리, 확인 전)' 칸에만 있습니다. 장부를 먼저 확인해 주세요.")
            else:
                _issue(issues, "error", "period_not_in_ledger" if n["kind"] == "기간" else "number_not_in_ledger",
                       where, text, f"{what} {n['raw']}{n['unit']}가 장부 {', '.join(ids)}에 없습니다.")
        for title in titles_in(text):
            if title in evidence:
                continue
            if title in everything:
                _issue(issues, "error", "unconfirmed_ledger", where, text,
                       f"직함 '{title}'은 장부의 '(AI 정리, 확인 전)' 칸에만 있습니다.")
            else:
                _issue(issues, "error", "title_not_in_ledger", where, text, f"직함 '{title}'이 장부 {', '.join(ids)}에 없습니다.")
        for word in CHANGE:
            if word in text and word not in evidence:
                _issue(issues, "warn", "change_unsupported", where, text,
                       f"시점·변화 표현 '{word}'의 근거가 장부 {', '.join(ids)}에 없습니다.")
        # 지표 이름·시점: 문장의 숫자가 장부 수치 칸의 값이면 그 지표 이름과 시점을 맞춥니다.
        metrics = [mt for i in ids for mt in exps[i]["metrics"] if mt["confirmed"]]
        checked = set()
        for n in numbers(text):
            for mt in metrics:
                values = " ".join(mt.get(k, "") for k in METRIC_VALUES)
                if (n["value"], n["unit"]) not in {(x["value"], x["unit"]) for x in numbers(values, strict=False)}:
                    continue
                name = mt.get("지표", "")
                if id(mt) in checked or not name:
                    break
                checked.add(id(mt))
                head = name.split()[-1]
                if head not in text:
                    _issue(issues, "error", "metric_name_mismatch", where, text,
                           f"{n['raw']}{n['unit']}는 장부에서 '{name}'의 값입니다. 문장에 지표 이름 '{head}'가 없습니다.")
                for per in PER_UNIT.findall(text):
                    if per not in name:
                        _issue(issues, "error", "metric_unit_mismatch", where, text,
                               f"문장의 '{per}'가 장부 지표 '{name}'와 다릅니다.")
                when = mt.get("시점", "") + " " + mt.get("기간", "")
                for t in YEAR.findall(text) + HALF.findall(text):
                    if t not in when:
                        _issue(issues, "error", "metric_time_mismatch", where, text,
                               f"'{t}'가 장부 지표 '{name}'의 시점({mt.get('시점', '')})과 다릅니다.")
                break
        # 설계안·계획을 한 일처럼 쓴 문장
        if is_past(text) and not any(h in text for h in HEDGE):
            sb = bigrams(text)
            best, best_ratio = None, -1
            for i in ids:
                for a in exps[i]["actions"]:
                    ab = bigrams(a["text"])
                    if not ab:
                        continue
                    common = len(sb & ab)
                    if common * 1000 // len(ab) > best_ratio:
                        best, best_ratio = a, common * 1000 // len(ab)
            if best and best["tag"] != "한 일" and best_ratio >= 400:
                _issue(issues, "error", "plan_as_done", where, text,
                       f"장부에서 [{best['tag']}]인 행동을 과거형 성과로 썼습니다: {best['text']}")
    if "공고" in s["sources"] and posting_body:
        have = {n["value"] for n in numbers(posting_body, strict=False)}
        for n in numbers(text):
            if n["value"] not in have:
                _issue(issues, "error", "number_not_in_posting", where, text, f"{n['raw']}{n['unit']}가 공고 원문에 없습니다.")
    if "조사" in s["sources"] and research_text:
        have = {n["value"] for n in numbers(research_text, strict=False)}
        for n in numbers(text):
            if n["value"] not in have:
                _issue(issues, "error", "number_not_in_research", where, text, f"{n['raw']}{n['unit']}가 회사 조사 칸에 없습니다.")


def _company_checks(issues, where, text, current, companies, mine):
    for c in companies:
        name = c["name"]
        if not name or (current and (name.lower() in current.lower() or current.lower() in name.lower())):
            continue
        if find_name(text, name) != -1:
            if c["from"] == "folder" or name in mine:
                _issue(issues, "error", "other_company", where, text, f"지금 회사({current or '미정'})가 아닌 지원 회사 이름 '{name}'이 있습니다.")
            else:
                _issue(issues, "warn", "other_company", where, text,
                       f"다른 회사·브랜드 이름 '{name}'이 있습니다. 쓴 도구 이름이면 그대로 둬도 됩니다.")


def _style_checks(issues, where, text, style, sentence=True):
    for word in style["banned"]:
        if word in text:
            _issue(issues, "warn", "style_banned", where, text, f"표기 규칙: '{word}'를 쓰지 않습니다.")
    for a, b in style["replace"]:
        if a in text:
            _issue(issues, "warn", "style_replace", where, text, f"표기 규칙: '{a}' 대신 '{b}'를 씁니다.")
    if sentence and style["max_sentence"] and len(text) > style["max_sentence"]:
        _issue(issues, "warn", "style_length", where, text,
               f"표기 규칙: 문장이 {len(text)}자로 {style['max_sentence']}자보다 깁니다.")
    if sentence and style["tone"] and not _tone_ok(text, style["tone"]):
        _issue(issues, "warn", "style_tone", where, text, f"표기 규칙: '{style['tone']}' 말투로 끝내 주세요.")


def _term_checks(issues, where, text, terms):
    if not terms:
        return
    entries = terms.get("terms", [])
    by_name = _term_index(terms)
    for entry in entries:
        for name in _term_names(entry):
            i = find_name(text, name)
            if i == -1:
                continue
            rest = text[i + len(name):]
            gloss = ""
            m = re.match(r"^\s*\(([^)]*)\)", rest)
            if m:
                gloss = m.group(1)
            else:
                m = re.match(r"^(?:이란|란|은|는|이|가)?\s*,?\s*(?:즉|곧)\s+([^,.]*)", rest)
                if m:
                    gloss = m.group(1)
            if not gloss:
                continue
            for c in entry.get("confusable", []):
                other = by_name.get(c["term"].lower())
                names = _term_names(other) if other else [c["term"]]
                if any(find_name(gloss, n) != -1 for n in names):
                    _issue(issues, "warn", "term_confused", where, text,
                           f"'{name}'를 '{c['term']}'의 뜻으로 썼을 수 있습니다(17번 사전: {c['difference']})")
                    return
            break


# 쓰기 규칙(사용자 원문): 마크다운이나 대화 복사 흔적, 전문용어 남발, 동어반복을 기계로 잡습니다.
# 핵심 요점과 논리 판단은 AI 점검이 맡습니다(skills/review/SKILL.md).
MD_BULLET = re.compile(r"^\s*[-*+]\s")
MD_HEAD = re.compile(r"(?:^|\s)#{1,6}\s")
MD_LINK = re.compile(r"\[[^\]]+\]\([^)]*\)")
CHAT_OPEN = ("물론입니다", "아래는 ", "요청하신 ")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z0-9]+")
# 연락처의 이메일과 주소는 용어가 아니므로 세기 전에 지웁니다.
LINKISH = re.compile(r"https?://\S+|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+|[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+(?:/\S*)?")
JARGON_MAX = 2
REPEAT_DICE = 70


def md_residue(text: str, doc: bool = False) -> str:
    """제출 칸에 그대로 보일 마크다운, 대화 복사 흔적. 문서(doc)는 표, 링크, 굵은 글씨를 HTML로 바꾸므로 그것은 빼고 봅니다."""
    s = plain(text).strip()
    if "(AI 정리" in s:
        return "(AI 정리, 확인 전)"
    if not doc and MD_BULLET.match(s):
        return "목록 기호"
    if MD_HEAD.search(s):
        return "#"
    for mark in ("`", "*", "__", "~~"):
        if mark in s:
            return mark
    if not doc and MD_LINK.search(s):
        return "링크 문법"
    if not doc and "|" in s:
        return "|"
    for w in CHAT_OPEN:
        if s.startswith(w):
            return w.strip(" ,")
    return ""


def jargon(text: str, posting_body: str) -> list[str]:
    """공고에 없는 영문 용어(두 글자 이상). 같은 말은 한 번만 셉니다."""
    low = (posting_body or "").lower()
    out = []
    for m in LATIN_WORD.finditer(LINKISH.sub(" ", plain(text))):
        w = m.group(0)
        if w.lower() not in low and w.lower() not in [o.lower() for o in out]:
            out.append(w)
    return out


def _writing_checks(issues, where, text, posting_body, doc=False):
    mark = md_residue(text, doc)
    if mark:
        _issue(issues, "warn", "md_residue", where, text,
               f"마크다운이나 대화 복사 흔적({mark})이 남았습니다. 제출하면 그대로 보이니 지워 주세요.")
    words = jargon(text, posting_body)
    if len(words) > JARGON_MAX:
        _issue(issues, "warn", "jargon", where, text,
               f"공고에 없는 영문 용어가 한 곳에 {len(words)}개({', '.join(words)}) 있습니다. 읽는 사람이 아는 말로 풀어 쓰거나 꼭 필요한 하나만 남겨 주세요.")


def _near(ka: str, kb: str, dice: int) -> bool:
    if ka == kb:
        return True
    ba, bb = bigrams(ka), bigrams(kb)
    return 200 * len(ba & bb) >= dice * (len(ba) + len(bb))


def check(draft_text: str, ledger_text: str, analysis_text: str = "", posting_text: str = "", style_text: str = "",
          companies: list | None = None, terms: dict | None = None, previous_text: str = "") -> dict:
    """자기소개서 초안 검사. companies는 [{"name", "from": "folder"|"dictionary"}]."""
    issues: list[dict] = []
    draft = parse_draft(draft_text)
    ledger = parse_ledger(ledger_text or "")
    exps = {e["id"]: e for e in ledger["experiences"]}
    analysis = parse_analysis(analysis_text or "")
    posting = parse_posting(posting_text or "")
    style = parse_style(style_text)
    current = draft["company"]
    companies = companies or []
    mine = [c["name"] for c in companies if c["from"] == "folder"]
    research_none = bool(analysis_text) and analysis["research_status"] in ("", "자료 없음", "조사 안 됨")
    for li in ledger["issues"]:
        if li["code"] == "ledger_empty":
            _issue(issues, "error", "ledger_empty", "장부", "", li["message"])
    if not current:
        _issue(issues, "error", "draft_meta", "머리", "", "'- 회사: 회사이름'이 없습니다.")
    questions = []
    for q in draft["questions"]:
        where = f"문항 {q['no']}"
        body = body_text(q["paras"])
        counted = count(body)
        f = fit(counted, q["limit"], q["basis"])
        if q["type"] not in TYPES:
            _issue(issues, "error", "question_meta", where, "", f"'- 유형:'은 {', '.join(TYPES)} 중 하나여야 합니다.")
        if not q["meta"].get("제한"):
            _issue(issues, "error", "question_meta", where, "", "'- 제한: 500자(공백 포함)'이 없습니다. 제한이 없으면 '없음'으로 적어 주세요.")
        elif f["fit"] == "over":
            _issue(issues, "error", "length_over", where, "", f"{f['value']}자로 제한 {q['limit']}자를 넘습니다({f['ratio']}%).")
        elif f["fit"] == "short":
            _issue(issues, "error", "length_short", where, "", f"{f['value']}자로 제한 {q['limit']}자의 90%에 못 미칩니다({f['ratio']}%).")
        elif f["fit"] == "no-limit":
            _issue(issues, "warn", "no_limit", where, "", "글자 수 제한이 없습니다.")
        if not q["version"]:
            _issue(issues, "error", "question_meta", where, "", "'- 판: v1 · 바꾼 점 한 줄'이 없습니다.")
        ids, sents = [], []
        placeholders = 0
        for para in q["paras"]:
            sents += sentences(para)
            for line in para.split("\n"):
                mark = md_residue(line)
                if mark:
                    _issue(issues, "warn", "md_residue", where, plain(line).strip(),
                           f"마크다운이나 대화 복사 흔적({mark})이 남았습니다. 제출하면 그대로 보이니 지워 주세요.")
        for s in sents:
            text = s["text"]
            for i in s["ids"]:
                if i not in ids:
                    ids.append(i)
            if NEED in text:
                placeholders += 1
                _issue(issues, "error", "placeholder", where, text, "장부에 근거가 없어 남긴 칸입니다. 장부에 경험을 더하거나 문장을 빼 주세요.")
                continue
            for u in s["unknown"]:
                _issue(issues, "warn", "unknown_tag", where, text, f"모르는 주석 '{u}'입니다. E01·공고·조사·의견·상황·과제·행동·결과·연결만 씁니다.")
            for i in s["ids"]:
                if i not in exps:
                    _issue(issues, "error", "unknown_id", where, text, f"장부에 {i}가 없습니다.")
                elif exps[i]["unconfirmed"]:
                    _issue(issues, "warn", "unconfirmed_ledger", where, text,
                           f"{i}에 확인 전 칸({', '.join(exps[i]['unconfirmed'])})이 있습니다. 확인한 칸만 근거가 됩니다.")
            factual = bool(numbers(text)) or is_past(text) or (bool(titles_in(text)) and not is_future(text))
            if factual and not s["ids"] and not s["sources"]:
                _issue(issues, "error", "no_id", where, text, "사실 문장에 근거 ID가 없습니다. 문장 뒤에 <!-- E01 -->처럼 달아 주세요.")
            if "조사" in s["sources"] and research_none:
                _issue(issues, "error", "research_none_cited", where, text, "분석의 회사 조사가 '자료 없음'인데 조사를 근거로 썼습니다.")
            if "의견" not in s["sources"]:
                _fact_checks(issues, where, s, exps, posting["body"], analysis["research_text"])
            if any(w in text for w in ABSTRACT) and not re.search(r"[0-9]", text):
                _issue(issues, "warn", "para_abstract", where, text, "근거 없는 추상 성과입니다. 수치·기간·규모·전후 변화로 바꿔 주세요.")
            _company_checks(issues, where, text, current, companies, mine)
            _style_checks(issues, where, text, style)
            _term_checks(issues, where, text, terms)
            words = jargon(text, posting["body"])
            if len(words) > JARGON_MAX:
                _issue(issues, "warn", "jargon", where, text,
                       f"공고에 없는 영문 용어가 한 곳에 {len(words)}개({', '.join(words)}) 있습니다. 읽는 사람이 아는 말로 풀어 쓰거나 꼭 필요한 하나만 남겨 주세요.")
        # 같은 문항 안 동어반복(분량 부풀리기)
        keys = [squash(s["text"]) for s in sents]
        for b in range(len(sents)):
            if len(keys[b]) < 15 or NEED in sents[b]["text"]:
                continue
            if any(len(keys[a]) >= 15 and _near(keys[a], keys[b], REPEAT_DICE) for a in range(b)):
                _issue(issues, "warn", "repeat_in_question", where, sents[b]["text"],
                       "같은 문항 안에서 앞 문장과 거의 같은 말을 되풀이합니다. 분량을 채우는 문장이면 지우고 새 사실이나 판단 이유로 바꿔 주세요.")
        # 경험 문단 원칙(4.1절 10번): STAR 칸 표시가 있는 문항, 또는 경험형 문항
        labeled = [s for s in sents if s["labels"]]
        if q["type"] == "경험형" and not labeled and sents:
            _issue(issues, "warn", "para_no_star", where, "", "경험형 문항인데 STAR 칸 표시(<!-- E01 행동 --> 등)가 없습니다.")
        if labeled:
            def size(*labels):
                return sum(len(s["text"]) for s in sents if any(lb in s["labels"] for lb in labels))
            situation, action = size("상황", "과제"), size("행동")
            if situation > action:
                _issue(issues, "warn", "para_situation_long", where, "",
                       f"상황·과제({situation}자)가 내 행동({action}자)보다 깁니다. 상황은 짧게, 행동은 길게 씁니다.")
            results = [s for s in sents if "결과" in s["labels"]]
            if any(any(t in s["text"] for t in TEAM) for s in results) and \
                    not any(any(w in s["text"] for w in SELF) for s in sents):
                _issue(issues, "warn", "para_team_only", where, "", "성과의 주어가 팀뿐입니다. 그 안에서 내가 한 일을 밝혀 주세요.")
            if any("행동" in s["labels"] for s in sents) and not any(any(w in s["text"] for w in REASON) for s in sents):
                _issue(issues, "warn", "para_no_reason", where, "", "행동에 판단 이유가 없습니다. 왜 그렇게 했는지 써 주세요.")
            last = sents[-1]["text"] if sents else ""
            linked = any("연결" in s["labels"] for s in sents) or any(w in last for w in LINK) or \
                (current and current in last)
            if not linked:
                _issue(issues, "warn", "para_no_link", where, "", "지원 직무에서 이 경험을 어떻게 쓸지로 끝내 주세요.")
        questions.append({"no": q["no"], "title": q["title"], "type": q["type"], "type_guess": guess_type(q["title"]),
                          "version": q["version"], "change": q["change"], "confirmed": q["confirmed"],
                          "limit": q["limit"], "basis": q["basis"], "count": counted, "ratio": f["ratio"],
                          "fit": f["fit"], "ids": ids, "links": q["links"], "placeholders": placeholders,
                          "_sents": sents, "_body": body})
    # 짧은 칸
    short_rows = []
    for sf in draft["short"]:
        where = f"짧은 칸: {sf['name']}"
        counted = count(sf["content"])
        f = fit(counted, sf["limit"], "with_spaces")
        if f["fit"] == "over":
            _issue(issues, "error", "length_over", where, sf["content"], f"{f['value']}자로 제한 {sf['limit']}자를 넘습니다.")
        if NEED in sf["content"]:
            _issue(issues, "error", "placeholder", where, sf["content"], "장부에 근거가 없어 남긴 칸입니다.")
        elif not sf["ids"]:
            _issue(issues, "error", "short_no_id", where, sf["content"], "짧은 칸에도 근거 ID(<!-- E01 -->)를 달아 주세요.")
        for i in sf["ids"]:
            if i not in exps:
                _issue(issues, "error", "unknown_id", where, sf["content"], f"장부에 {i}가 없습니다.")
        s = {"text": sf["content"], "ids": sf["ids"], "labels": [], "sources": sf["sources"], "unknown": []}
        if NEED not in sf["content"]:
            _fact_checks(issues, where, s, exps, posting["body"], analysis["research_text"])
        _company_checks(issues, where, sf["content"], current, companies, mine)
        _style_checks(issues, where, sf["content"], style, sentence=False)
        _writing_checks(issues, where, sf["content"], posting["body"])
        short_rows.append({"name": sf["name"], "limit": sf["limit"], "count": counted, "ratio": f["ratio"],
                           "fit": f["fit"], "ids": sf["ids"]})
    # 문항 사이 중복
    used = {}
    for q in questions:
        for i in q["ids"]:
            used.setdefault(i, [])
            if q["no"] not in used[i]:
                used[i].append(q["no"])
    for i, nos in used.items():
        if len(nos) > 1:
            _issue(issues, "warn", "dup_experience", "전체", i, f"{i} 경험이 문항 {', '.join(str(n) for n in nos)}에 겹칩니다.")
    for a in range(len(questions)):
        for b in range(a + 1, len(questions)):
            for sa in questions[a]["_sents"]:
                ka = squash(sa["text"])
                if len(ka) < 10 or NEED in sa["text"]:
                    continue
                for sb in questions[b]["_sents"]:
                    kb = squash(sb["text"])
                    if len(kb) < 10:
                        continue
                    same = ka == kb
                    if not same and len(ka) >= 20 and len(kb) >= 20:
                        ba, bb = bigrams(ka), bigrams(kb)
                        same = 200 * len(ba & bb) >= 85 * (len(ba) + len(bb))
                    if same:
                        _issue(issues, "warn", "dup_sentence", f"문항 {questions[a]['no']}, {questions[b]['no']}", sb["text"],
                               "같거나 거의 같은 문장이 두 문항에 있습니다.")
    seen_num = {}
    for q in questions:
        for s in q["_sents"]:
            for n in numbers(s["text"]):
                if not n["unit"] or n["unit"] in PERIOD_UNITS:
                    continue
                key = n["value"] + n["unit"]
                seen_num.setdefault(key, [])
                if q["no"] not in seen_num[key]:
                    seen_num[key].append(q["no"])
    for key, nos in seen_num.items():
        if len(nos) > 1:
            _issue(issues, "warn", "dup_number", "전체", key, f"수치 {key}가 문항 {', '.join(str(n) for n in nos)}에 되풀이됩니다.")
    # 역량·세부 업무 커버리지
    coverage = []
    if not analysis_text:
        _issue(issues, "warn", "no_analysis", "전체", "", "analysis.md가 없어 역량 커버리지를 보지 못했습니다.")
    names = [it["item"] for it in analysis["items"]]
    for it in analysis["items"]:
        nos = [q["no"] for q in questions if it["item"] in q["links"] or it["item"].lower() in q["_body"].lower()]
        coverage.append({"item": it["item"], "kind": it["kind"], "questions": nos})
        if not nos:
            _issue(issues, "warn", "coverage_missing", "전체", it["item"],
                   f"공고의 {it['kind'] or '역량'} '{it['item']}'이 어느 문항에도 없습니다.")
    if analysis_text:
        for q in questions:
            for link in q["links"]:
                if link not in names:
                    _issue(issues, "warn", "coverage_unknown", f"문항 {q['no']}", link, f"'연결'의 '{link}'가 분석의 역량·세부 업무에 없습니다.")
    # 확정 문항 보호
    if previous_text:
        before = {q["no"]: q for q in parse_draft(previous_text)["questions"]}
        for q in draft["questions"]:
            old = before.get(q["no"])
            if old and old["confirmed"] and (old["raw"] != q["raw"] or old["title"] != q["title"] or not q["confirmed"]):
                _issue(issues, "error", "confirmed_changed", f"문항 {q['no']}", "", "확정한 문항이 바뀌었습니다. 확정 문항은 다시 쓰지 않습니다.")
    for q in questions:
        del q["_sents"], q["_body"]
    errors = sum(1 for i in issues if i["level"] == "error")
    confirmed_all = bool(questions) and all(q["confirmed"] for q in questions)
    return {"company": current, "mode": draft["mode"], "questions": questions, "short_fields": short_rows,
            "coverage": coverage, "issues": issues,
            "summary": {"errors": errors, "warnings": len(issues) - errors, "ready": errors == 0,
                        "confirmed_all": confirmed_all, "submittable": errors == 0 and confirmed_all}}


# ---------- 이력서·포트폴리오 (PRD 5.7절) ----------

DOC_KINDS = {"resume": "이력서", "portfolio": "포트폴리오"}
DOC_PAGES = {"resume": (1, 2), "portfolio": (3, 5)}
DOC_CARDS = {"resume": ("숫자 카드", 4), "portfolio": ("프로젝트 카드", 3)}
DOC_META = ("회사", "직무", "판", "상태")
# 머리에 함께 두는 연락처 줄. 제출본에는 남기되 머리 칸 읽기를 끝내지 않습니다.
HEAD_CONTACT = ("연락처", "이메일", "전화", "포트폴리오", "깃허브", "블로그")
WEAK = ["참여했습니다", "공부했습니다", "노력했습니다", "기초", "수료 예정", "활용 가능", "관심"]
FREE_SECTIONS = ["자격", "교육", "학력", "도구", "연락"]
DESIGN_WORDS = ["가상", "설계", "가정"]
DESIGN_MARK = ["가상", "설계안", "가정"]
PHOTO = ["사진", "photo", "profile", "증명"]
BIRTH = ["생년월일", "출생", "년생"]
CLAIM_HEAD = {"자격증": "자격", "프로젝트": "프로젝트", "수상": "수상"}
CONTACT = [
    ("전화번호", re.compile(r"(?<![0-9])01[016789][-. \t]?[0-9]{3,4}[-. \t]?[0-9]{4}(?![0-9])")),
    ("이메일", re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+")),
]
IMAGE = re.compile(r"!\[([^\]]*)\]\(([^)\s]*)[^)]*\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_ITEM = re.compile(r"^(?:[-*]|[0-9]+\.)\s+")
RULE_CELL = re.compile(r"^:?-{2,}:?$")
PAGE_RULE = re.compile(r"([0-9]+)\s*(?:쪽|페이지|장)\s*(?:이내|이하)")
COUNT_CLAIM = re.compile(r"(자격증|프로젝트|수상)\s*([0-9]+)\s*(?:개|건|종)")
ADDRESS = re.compile(r"[가-힣]+(?:시|도) [가-힣]+(?:구|군|시) [가-힣0-9]+(?:로|길|동)(?![가-힣])")
YM = re.compile(r"(20[0-9]{2})\s*(\.|-|/|년)\s*([0-9]{1,2})(?![0-9])")
YM_DOT = re.compile(r"(20[0-9]{2})\.([0-9]{1,2})(?![0-9])")
YM_RANGE = re.compile(r"(20[0-9]{2})\s*(?:\.|-|/|년)\s*([0-9]{1,2})\s*월?\s*~\s*(20[0-9]{2})\s*(?:\.|-|/|년)\s*([0-9]{1,2})(?![0-9])")


def doc_kind(text: str, name: str = "") -> str:
    """이력서(resume), 포트폴리오(portfolio), 그 밖("")을 첫 제목이나 파일 이름으로 가립니다."""
    for line in (text or "").replace("\r\n", "\n").split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            for kind, word in DOC_KINDS.items():
                if title.startswith(word):
                    return kind
            break
    for kind in DOC_KINDS:
        if name.startswith(kind + "-"):
            return kind
    return ""


def _strip_md(line: str) -> str:
    s = IMAGE.sub("", plain(line)).strip()
    s = LIST_ITEM.sub("", s)
    return s.replace("**", "").strip()


def _tags(line: str) -> dict:
    tag = {"ids": [], "labels": [], "sources": [], "unknown": []}
    for raw in COMMENT_SPLIT.findall(line):
        t = _parse_tag(raw)
        for key in tag:
            tag[key] += [v for v in t[key] if v not in tag[key]]
    return tag


def parse_doc(text: str, name: str = "") -> dict:
    """머리 칸, 쪽(`---` 줄), 절(##, ###), 내용 줄(제목, 표 행, 글 줄), 이미지를 나눕니다."""
    doc = {"kind": doc_kind(text, name), "meta": {}, "pages": [], "lines": [], "sections": [], "images": []}
    page, section, in_table, started = 1, "", False, False
    content_pages = set()
    for raw in (text or "").replace("\r\n", "\n").split("\n"):
        s = raw.strip()
        if not s:
            in_table = False
            continue
        if s == "---":
            page += 1
            in_table = False
            continue
        if s.startswith(">"):
            continue
        h = HEADING.match(s)
        if h and len(h.group(1)) == 1:
            continue
        f = FIELD.match(s)
        if not started and not h and f and f.group(1).strip() in DOC_META:
            doc["meta"].setdefault(f.group(1).strip(), f.group(2).strip())
            continue
        if not (not h and _head_contact(f, s)):
            started = True
        kind = "line"
        if h:
            section = plain(h.group(2)).strip()
            doc["sections"].append({"title": section, "page": page, "items": 0, "lines": 0})
            kind = "heading"
            body = _strip_md(h.group(2))
            in_table = False
        elif s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if not in_table:
                in_table = True
                continue
            if all(RULE_CELL.match(c) for c in cells if c):
                continue
            kind = "row"
            body = " | ".join(_strip_md(c) for c in cells)
        else:
            in_table = False
            body = _strip_md(s)
        for m in IMAGE.finditer(plain(s)):
            doc["images"].append({"page": page, "alt": m.group(1).strip(), "src": m.group(2)})
        if kind != "heading" and doc["sections"]:
            sec = doc["sections"][-1]
            if kind == "row" or LIST_ITEM.match(s):
                sec["items"] += 1
            if body:
                sec["lines"] += 1
        if body or IMAGE.search(s):
            content_pages.add(page)
        line = {"page": page, "section": section, "kind": kind, "text": body, "raw": s}
        line.update(_tags(s))
        doc["lines"].append(line)
    doc["pages"] = sorted(content_pages)
    return doc


def _head_contact(f, s: str) -> bool:
    return bool(f) and (f.group(1).strip() in HEAD_CONTACT or bool(_contacts(s)))


def doc_submission(text: str) -> str:
    """제출용 본문: 첫 제목, 머리 칸, 안내 줄(>), 장부 ID 주석을 빼고 제목, 표, 쪽 나눔은 남깁니다."""
    out, started = [], False
    for raw in (text or "").replace("\r\n", "\n").split("\n"):
        s = raw.strip()
        if s.startswith("# ") or s.startswith(">"):
            continue
        f = FIELD.match(s)
        if not started and f and f.group(1).strip() in DOC_META:
            continue
        if s and not _head_contact(f, s):
            started = True
        line = re.sub(r"[ \t]+", " ", plain(raw)).rstrip()
        if not line.strip() and (not out or not out[-1].strip()):
            continue
        out.append(line)
    return "\n".join(out).strip() + "\n"


def _ym(text: str) -> tuple[set, set]:
    """연월('2025-03' 꼴로 맞춤)과 쓴 표기('.', '-', '/', '년')."""
    found, styles = set(), set()
    for m in YM.finditer(text):
        found.add(f"{m.group(1)}-{int(m.group(3)):02d}")
        styles.add(m.group(2))
    return found, styles


def _contacts(text: str) -> set:
    out = set()
    for kind, pattern in CONTACT:
        for m in pattern.finditer(plain(text)):
            v = m.group(0)
            out.add(re.sub(r"[^0-9]", "", v) if kind == "전화번호" else v.lower())
    return out


def _id_facts(text: str) -> dict:
    """줄마다 단 장부 ID별로 그 줄의 기간(시작~끝)과 직함을 모읍니다(문서 사이 비교용)."""
    out = {}
    for raw in (text or "").replace("\r\n", "\n").split("\n"):
        ids = _tags(raw)["ids"]
        if not ids:
            continue
        body = plain(raw)
        ranges = {f"{m.group(1)}-{int(m.group(2)):02d}~{m.group(3)}-{int(m.group(4)):02d}" for m in YM_RANGE.finditer(body)}
        titles = set(titles_in(body))
        for i in ids:
            slot = out.setdefault(i, {"periods": set(), "titles": set()})
            slot["periods"] |= ranges
            slot["titles"] |= titles
    return out


def _design_numbers(exp: dict) -> set:
    """설계안, 가상 데이터 수치: 출처나 지표에 가상, 설계, 가정이 있는 수치 칸의 값과 [한 일]이 아닌 행동에만 있는 숫자."""
    out = set()
    for mt in exp["metrics"]:
        if any(w in mt.get("출처", "") + mt.get("지표", "") for w in DESIGN_WORDS):
            for k in METRIC_VALUES:
                out |= {n["value"] for n in numbers(mt.get(k, ""), strict=False)}
    plan = "\n".join(a["text"] for a in exp["actions"] if a["tag"] != "한 일")
    rest = "\n".join([exp["title"], *exp["fields"].values(), *(a["text"] for a in exp["actions"] if a["tag"] == "한 일"),
                      *(mt["raw"] for mt in exp["metrics"])])
    have = {n["value"] for n in numbers(rest, strict=False)}
    out |= {n["value"] for n in numbers(plan, strict=False) if n["value"] not in have}
    return out


def check_doc(text: str, ledger_text: str, analysis_text: str = "", posting_text: str = "", style_text: str = "",
              companies: list | None = None, terms: dict | None = None, others: list | None = None,
              name: str = "") -> dict:
    """이력서, 포트폴리오 검사. others는 같은 회사 폴더의 다른 문서 [{"name", "kind", "text"}]."""
    issues: list[dict] = []
    doc = parse_doc(text, name)
    kind = doc["kind"] or "resume"
    label = DOC_KINDS[kind]
    ledger = parse_ledger(ledger_text or "")
    exps = {e["id"]: e for e in ledger["experiences"]}
    analysis = parse_analysis(analysis_text or "")
    posting = parse_posting(posting_text or "")
    style = parse_style(style_text)
    meta = doc["meta"]
    current = meta.get("회사", "")
    companies = companies or []
    mine = [c["name"] for c in companies if c["from"] == "folder"]
    asked = posting["body"]
    research_none = bool(analysis_text) and analysis["research_status"] in ("", "자료 없음", "조사 안 됨")
    for li in ledger["issues"]:
        if li["code"] == "ledger_empty":
            _issue(issues, "error", "ledger_empty", "장부", "", li["message"])
    if not current:
        _issue(issues, "error", "doc_meta", "머리", "", "'- 회사: 회사이름'이 없습니다.")
    ver = VERSION.match(meta.get("판", ""))
    if not ver:
        _issue(issues, "error", "doc_meta", "머리", "", "'- 판: v1 · 바꾼 점 한 줄'이 없습니다.")
    if not meta.get("직무"):
        _issue(issues, "warn", "doc_meta", "머리", "", "'- 직무:'가 없습니다. 첫 화면에 지원 직무가 읽혀야 합니다.")
    card_head, card_need = DOC_CARDS[kind]
    cards = [ln for ln in doc["lines"] if ln["kind"] == "row" and card_head in ln["section"]]
    all_text = "\n".join(ln["text"] for ln in doc["lines"])
    for ln in doc["lines"]:
        where = f"{ln['page']}쪽 {ln['section'] or '머리'}"
        t = ln["text"]
        if not t:
            continue
        if NEED in t:
            _issue(issues, "error", "placeholder", where, t, "장부에 근거가 없어 남긴 칸입니다. 장부에 경험을 더하거나 줄을 빼 주세요.")
            continue
        if _contacts(t):
            continue  # 연락처 줄은 사실 주장이 아니라 근거 ID를 묻지 않습니다(같은지 여부는 문서 사이 비교가 봅니다).
        for u in ln["unknown"]:
            _issue(issues, "warn", "unknown_tag", where, t, f"모르는 주석 '{u}'입니다. E01, 공고, 조사, 의견만 씁니다.")
        for i in ln["ids"]:
            if i not in exps:
                _issue(issues, "error", "unknown_id", where, t, f"장부에 {i}가 없습니다.")
            elif exps[i]["unconfirmed"]:
                _issue(issues, "warn", "unconfirmed_ledger", where, t,
                       f"{i}에 확인 전 칸({', '.join(exps[i]['unconfirmed'])})이 있습니다. 확인한 칸만 근거가 됩니다.")
        free = any(w in ln["section"] for w in FREE_SECTIONS)
        fact = YM_DOT.sub(r"\1-\2", t)
        factual = bool(numbers(fact)) or is_past(fact) or (bool(titles_in(fact)) and not is_future(fact))
        if factual and not free and not ln["ids"] and not ln["sources"]:
            _issue(issues, "error", "no_id", where, t, "사실 줄에 근거 ID가 없습니다. 줄 끝에 <!-- E01 -->처럼 달아 주세요.")
        if "조사" in ln["sources"] and research_none:
            _issue(issues, "error", "research_none_cited", where, t, "분석의 회사 조사가 '자료 없음'인데 조사를 근거로 썼습니다.")
        if "의견" not in ln["sources"]:
            s = {"text": fact, "ids": ln["ids"], "labels": [], "sources": ln["sources"], "unknown": []}
            _fact_checks(issues, where, s, exps, asked, analysis["research_text"])
        if any(w in t for w in ABSTRACT) and not re.search(r"[0-9]", t):
            _issue(issues, "warn", "para_abstract", where, t, "근거 없는 추상 성과입니다. 수치, 기간, 규모, 전후 변화로 바꿔 주세요.")
        for w in WEAK:
            if w in t:
                _issue(issues, "warn", "weak_word", where, t, f"약한 표현 '{w}'입니다. 한 일과 결과로 바꿔 주세요.")
        if ln["kind"] == "heading" or any(ln is c for c in cards):
            design = set()
            for i in ln["ids"]:
                if i in exps:
                    design |= _design_numbers(exps[i])
            hits = [n for n in numbers(fact) if n["value"] in design]
            if hits and not any(m in t for m in DESIGN_MARK):
                _issue(issues, "error", "design_number_unmarked", where, t,
                       f"{hits[0]['raw']}{hits[0]['unit']}는 장부에서 설계안이나 가상 데이터 수치입니다. "
                       "숫자 바로 옆에 '가상 데이터'나 '설계안'을 적어 주세요.")
        if "생년월일" not in asked and any(w in t for w in BIRTH):
            _issue(issues, "error", "birth", where, t, "공고가 생년월일을 요구하지 않았습니다. 빼 주세요.")
        if "주소" not in asked and ADDRESS.search(t):
            _issue(issues, "error", "address", where, t, "공고가 주소를 요구하지 않았습니다. 빼 주세요.")
        _company_checks(issues, where, t, current, companies, mine)
        _style_checks(issues, where, t, style, sentence=False)
        _term_checks(issues, where, t, terms)
        if not free:
            _writing_checks(issues, where, t, asked, doc=True)
    # 동어반복(분량 부풀리기): 제목을 뺀 줄끼리
    body_lines = [(ln, squash(ln["text"])) for ln in doc["lines"] if ln["kind"] != "heading" and NEED not in ln["text"]]
    for b in range(len(body_lines)):
        ln, kb = body_lines[b]
        if len(kb) < 20:
            continue
        if any(len(ka) >= 20 and _near(ka, kb, REPEAT_DICE) for _, ka in body_lines[:b]):
            _issue(issues, "warn", "repeat_line", f"{ln['page']}쪽 {ln['section'] or '머리'}", ln["text"],
                   "앞 줄과 거의 같은 말을 되풀이합니다. 분량을 채우는 줄이면 지우고 새 사실로 바꿔 주세요.")
    for img in doc["images"]:
        where = f"{img['page']}쪽"
        if not any(w in asked for w in PHOTO) and any(w in (img["alt"] + " " + img["src"]).lower() for w in PHOTO):
            _issue(issues, "error", "photo", where, img["src"], "공고가 사진을 요구하지 않았습니다. 사진을 빼 주세요.")
        if not img["alt"]:
            _issue(issues, "warn", "image_no_caption", where, img["src"], "이미지가 무엇을 보여 주는지 대체 글 한 줄을 붙여 주세요.")
    # 첫 카드와 카드 수
    items = [it for it in analysis["items"] if it["kind"] in ("필수", "우대")]
    if cards and items and cards[0]["ids"]:
        comps = [c for i in cards[0]["ids"] if i in exps for c in exps[i]["competencies"]]
        if comps and not any(c in it["item"] or it["item"] in c for c in comps for it in items):
            _issue(issues, "warn", "first_card_off_role", f"{cards[0]['page']}쪽 {card_head}", cards[0]["text"],
                   f"첫 카드 경험의 역량({', '.join(comps)})이 공고의 필수, 우대 역량과 겹치지 않습니다. 직무와 이어지는 수치를 앞에 두세요.")
    if len(cards) != card_need:
        _issue(issues, "warn", "card_count", card_head, "",
               f"{card_head}가 {len(cards)}개입니다. {label}은 {card_need}개로 씁니다." if cards else
               f"'{card_head}' 절의 표가 없습니다.")
    # 개수 주장과 실제 목록
    for ln in doc["lines"]:
        for m in COUNT_CLAIM.finditer(ln["text"]):
            head = CLAIM_HEAD[m.group(1)]
            sec = next((s for s in doc["sections"] if head in s["title"] and s["items"]), None)
            if sec and sec["items"] != int(m.group(2)):
                _issue(issues, "error", "count_claim", f"{ln['page']}쪽 {ln['section'] or '머리'}", ln["text"],
                       f"'{m.group(0)}'라고 썼는데 '{sec['title']}' 목록은 {sec['items']}개입니다.")
    # 공고 키워드
    low = all_text.lower()
    keywords = [{"item": it["item"], "kind": it["kind"], "found": it["item"].lower() in low} for it in items]
    for k in analysis["keywords"]:
        word = re.split(r"[:：]", k["text"], maxsplit=1)[0].strip()
        if word:
            keywords.append({"item": word, "kind": "숨은 키워드", "found": word.lower() in low})
    for k in keywords:
        if not k["found"]:
            _issue(issues, "warn", "keyword_missing", "전체", k["item"], f"공고의 {k['kind']} '{k['item']}'이 문서에 없습니다.")
    if not analysis_text:
        _issue(issues, "warn", "no_analysis", "전체", "", "analysis.md가 없어 키워드와 첫 카드를 보지 못했습니다.")
    # 분량과 형식
    low_page, high_page = DOC_PAGES[kind]
    rule = PAGE_RULE.search(asked)
    if rule:
        low_page, high_page = 1, int(rule.group(1))
    pages = len(doc["pages"])
    if pages > high_page or pages < low_page:
        _issue(issues, "error", "page_count", "전체", "",
               f"{pages}쪽입니다. {label}은 {low_page}~{high_page}쪽으로 씁니다('---' 줄이 쪽 나눔).")
    page_text = {p: squash("".join(ln["text"] for ln in doc["lines"] if ln["page"] == p)) for p in doc["pages"]}
    for p in sorted({img["page"] for img in doc["images"]}):
        body = squash("".join(ln["text"] for ln in doc["lines"] if ln["page"] == p and ln["kind"] != "heading"))
        if len(body) < 10:
            _issue(issues, "warn", "image_only_page", f"{p}쪽", "", "글 없이 이미지만 있는 쪽입니다. 무엇을 보여 주는지 글로 적어 주세요.")
    plist = doc["pages"]
    for a in range(len(plist)):
        for b in range(a + 1, len(plist)):
            ka, kb = page_text[plist[a]], page_text[plist[b]]
            if len(ka) < 20 or len(kb) < 20:
                continue
            ba, bb = bigrams(ka), bigrams(kb)
            if 200 * len(ba & bb) >= 85 * (len(ba) + len(bb)):
                _issue(issues, "warn", "page_repeat", f"{plist[a]}쪽, {plist[b]}쪽", "", "거의 같은 내용의 쪽이 되풀이됩니다.")
    if kind == "portfolio":
        limits = [s for s in doc["sections"] if "한계" in s["title"]]
        if not limits:
            _issue(issues, "error", "limit_empty", "전체", "", "프로젝트마다 '한계' 칸을 두고 비워 두지 않습니다.")
        for s in limits:
            if not s["lines"]:
                _issue(issues, "error", "limit_empty", f"{s['page']}쪽 {s['title']}", "", "'한계' 칸이 비었습니다.")
    # 문서 사이 불일치
    my_contacts, my_facts = _contacts(text), _id_facts(text)
    _, my_styles = _ym(all_text)
    for other in others or []:
        where = f"{other['name']}과 비교"
        theirs = _contacts(other["text"])
        if my_contacts and theirs and my_contacts != theirs:
            _issue(issues, "error", "doc_mismatch", where, "", "연락처가 다릅니다.")
        facts = _id_facts(other["text"])
        for i in sorted(set(my_facts) & set(facts)):
            a, b = my_facts[i], facts[i]
            if a["periods"] and b["periods"] and not a["periods"] & b["periods"]:
                _issue(issues, "error", "doc_mismatch", where, i,
                       f"{i}의 기간이 다릅니다({', '.join(sorted(a['periods']))} / {', '.join(sorted(b['periods']))}).")
            if a["titles"] and b["titles"] and not a["titles"] & b["titles"]:
                _issue(issues, "error", "doc_mismatch", where, i,
                       f"{i}의 직함이 다릅니다({', '.join(sorted(a['titles']))} / {', '.join(sorted(b['titles']))}).")
        if other["kind"] in DOC_KINDS and other["kind"] != kind:
            _, styles = _ym("\n".join(ln["text"] for ln in parse_doc(other["text"])["lines"]))
            if my_styles and styles and not my_styles & styles:
                _issue(issues, "error", "doc_mismatch", where, "",
                       f"날짜 표기가 다릅니다('{' '.join(sorted(my_styles))}' / '{' '.join(sorted(styles))}').")
    errors = sum(1 for i in issues if i["level"] == "error")
    confirmed = meta.get("상태", "").strip() == "확정"
    return {"kind": kind, "company": current, "role": meta.get("직무", ""),
            "version": f"v{ver.group(1)}" if ver else "", "change": ver.group(2).strip() if ver else "",
            "pages": pages, "cards": len(cards), "keywords": keywords, "issues": issues,
            "summary": {"errors": errors, "warnings": len(issues) - errors, "ready": errors == 0,
                        "confirmed": confirmed, "submittable": errors == 0 and confirmed}}


# ---------- HTML 출력 ----------

HTML_STYLE = ("@page{size:A4;margin:16mm}"
              "body{font-family:'Pretendard','Noto Sans KR','Malgun Gothic',sans-serif;font-size:10.5pt;line-height:1.55;"
              "color:#111;background:#fff;max-width:178mm;margin:0 auto;padding:8mm 0}"
              "h1,h2,h3{line-height:1.3;margin:1.1em 0 .4em}h2{font-size:13pt;border-bottom:1px solid #999;padding-bottom:2px}"
              "h3{font-size:11pt}table{border-collapse:collapse;width:100%;margin:.4em 0}"
              "th,td{border:1px solid #bbb;padding:3px 6px;text-align:left;vertical-align:top}th{background:#f2f2f2}"
              "img{max-width:100%}figure{margin:.6em 0}figcaption{font-size:9pt;color:#444}ul,ol{padding-left:1.3em;margin:.3em 0}"
              "p{margin:.35em 0}.page-break{break-after:page;height:0}"
              "@media screen{.page-break{border-top:1px dashed #bbb;margin:8mm 0}}")


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _inline(text: str) -> str:
    s = _esc(text)
    s = re.sub(r"!\[([^\]]*)\]\(([^)\s]*)[^)]*\)", r'<img src="\2" alt="\1">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r'<a href="\2">\1</a>', s)
    return re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)


def to_html(text: str, title: str = "") -> str:
    """한 단 HTML. 글은 글자로 두고 위에서 아래로 읽히게 씁니다. PDF는 브라우저 인쇄로 만듭니다."""
    out, para, items, table = [], [], [], []
    state = {"list": ""}

    def flush():
        if para:
            out.append("<p>" + " ".join(_inline(p) for p in para) + "</p>")
            para.clear()
        if items:
            tag = state["list"]
            out.append(f"<{tag}>" + "".join(f"<li>{_inline(i)}</li>" for i in items) + f"</{tag}>")
            items.clear()
        if table:
            rows = [r for r in table if not all(RULE_CELL.match(c) for c in r if c)]
            html = "".join("<tr>" + "".join(f"<{'th' if k == 0 else 'td'}>{_inline(c)}</{'th' if k == 0 else 'td'}>"
                                             for c in cells) + "</tr>" for k, cells in enumerate(rows))
            out.append(f"<table>{html}</table>")
            table.clear()

    for raw in plain(text or "").replace("\r\n", "\n").split("\n"):
        s = raw.strip()
        if not s:
            flush()
            continue
        if s == "---":
            flush()
            out.append('<div class="page-break"></div>')
            continue
        h = HEADING.match(s)
        if h:
            flush()
            n = len(h.group(1))
            out.append(f"<h{n}>{_inline(h.group(2).strip())}</h{n}>")
            continue
        if s.startswith("|"):
            if para or items:
                flush()
            table.append([c.strip() for c in s.strip("|").split("|")])
            continue
        m = re.match(r"^([-*]|[0-9]+\.)\s+(.*)$", s)
        if m:
            tag = "ul" if m.group(1) in ("-", "*") else "ol"
            if para or table or (items and state["list"] != tag):
                flush()
            state["list"] = tag
            items.append(m.group(2))
            continue
        img = re.match(r"^!\[([^\]]*)\]\(([^)\s]*)[^)]*\)$", s)
        if img:
            flush()
            cap = f"<figcaption>{_esc(img.group(1))}</figcaption>" if img.group(1) else ""
            out.append(f"<figure>{_inline(s)}{cap}</figure>")
            continue
        if items or table:
            flush()
        para.append(s)
    flush()
    return ("<!doctype html>\n<html lang=\"ko\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{_esc(title)}</title>\n<style>{HTML_STYLE}</style>\n</head>\n<body>\n"
            + "\n".join(out) + "\n</body>\n</html>\n")
