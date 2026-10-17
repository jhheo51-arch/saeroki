"""심사 기록 폴더(~/.saerok/idea/<아이디어>/<날짜>/)를 만들고, 단계별 결과를 검사해 result.json에 쌓고,
verdict.md를 만듭니다. 같은 result.json에서는 언제나 같은 verdict.md가 나옵니다."""

import json
import os
import re
import time
from pathlib import Path

from . import money, rubric, verdict

HOME_ENV = "SAEROK_IDEA_HOME"
PARTS = ["judge", "assumptions", "competitors", "panel", "money", "directions"]
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def home() -> Path:
    return Path(os.environ.get(HOME_ENV) or Path.home() / ".saerok" / "idea").expanduser().resolve()


def git_root(path: Path) -> Path | None:
    for folder in [path, *path.parents]:
        if (folder / ".git").exists():
            return folder
    return None


def slug(text: str) -> str:
    text = re.sub(r"[\\/:*?\"<>|\s]+", "-", text.strip()).strip("-.")
    return text[:30].strip("-.") or "이름-없음"


def clean_idea(idea: dict) -> dict:
    """한 줄은 꼭 필요하고, 4칸은 비어 있으면 미정으로 둡니다."""
    line = (idea.get("line") or "").strip()
    if not line:
        raise ValueError("아이디어 한 줄이 필요합니다.")
    out = {"line": line}
    for key in ("what", "who", "money", "why_now"):
        out[key] = (idea.get(key) or "").strip() or rubric.UNKNOWN
    return out


def create(idea: dict, *, date: str | None = None, base: Path | None = None, allow_git: bool = False,
           name: str | None = None, origin: dict | None = None) -> dict:
    """아이디어 폴더 아래 날짜 폴더를 새로 만듭니다. 같은 날 다시 돌리면 -2, -3을 붙여 덮어쓰지 않습니다."""
    base = (base or home()).resolve()
    repo = git_root(base)
    if repo and not allow_git:
        raise ValueError(f"기록 폴더({base})가 git 저장소({repo}) 안에 있습니다. 아이디어가 커밋될 수 있어 멈춥니다. "
                         f"{HOME_ENV}를 저장소 밖으로 바꿔 주세요.")
    idea = clean_idea(idea)
    date = date or time.strftime("%Y-%m-%d")
    if not DATE.match(date):
        raise ValueError(f"날짜는 YYYY-MM-DD 꼴이어야 합니다(받은 값 {date!r}).")
    folder, n = base / slug(name or idea["line"]) / date, 2
    while folder.exists():
        folder, n = folder.parent / f"{date}-{n}", n + 1
    folder.mkdir(parents=True)
    result = {"version": 1, "date": date, "idea": idea, "from": origin, "judges": {}, "assumptions": None,
              "competitors": None, "panel": None, "money": None, "directions": None, "replaced": []}
    save(folder, result)
    return {"folder": str(folder), "idea": idea}


def load(folder: Path) -> dict:
    path = Path(folder) / "result.json"
    if not path.is_file():
        raise ValueError(f"심사 기록이 아닙니다(result.json 없음): {folder}")
    return json.loads(path.read_text(encoding="utf-8"))


def save(folder: Path, result: dict) -> None:
    (Path(folder) / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _text(value, what: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{what}이(가) 비어 있습니다.")
    return value.strip()


def _texts(values, what: str, low: int, high: int) -> list[str]:
    items = [v.strip() for v in values or [] if isinstance(v, str) and v.strip()]
    if not low <= len(items) <= high:
        raise ValueError(f"{what}은(는) {low}~{high}개여야 합니다(받은 수 {len(items)}).")
    return items


def _link(item: dict, what: str) -> dict:
    url, checked = (item.get("url") or "").strip(), (item.get("checked") or "").strip()
    if not url.startswith(("http://", "https://")):
        raise ValueError(f"{what}: 링크(url)가 http로 시작해야 합니다. 링크가 없으면 근거로 쓰지 않습니다.")
    if not DATE.match(checked):
        raise ValueError(f"{what}: 확인 날짜(checked)가 YYYY-MM-DD 꼴이어야 합니다.")
    return {"url": url, "checked": checked}


def check_judge(data: dict) -> dict:
    who = data.get("judge")
    if who not in rubric.JUDGES:
        raise ValueError(f"모르는 심사위원입니다: {who!r}. 가능한 값: {', '.join(rubric.ORDER)}")
    score = data.get("score")
    if isinstance(score, bool) or score not in rubric.SCORES:
        raise ValueError(f"{who}: 점수는 1~5 정수여야 합니다(받은 값 {score!r}).")
    if data.get("vote") not in rubric.VOTES:
        raise ValueError(f"{who}: 투표는 {'·'.join(rubric.VOTES)} 중 하나여야 합니다.")
    return {
        "judge": who,
        "score": score,
        "vote": data["vote"],
        "reasons": _texts(data.get("reasons"), f"{who} 이유", 1, 3),
        "concerns": _texts(data.get("concerns"), f"{who} 걸리는 점", 1, 3),
    }


def check_assumptions(data: dict) -> list[dict]:
    items = data.get("assumptions") if isinstance(data, dict) else data
    if not isinstance(items, list) or sorted(a.get("key") for a in items) != sorted(rubric.ASSUMPTIONS):
        raise ValueError(f"가정은 {', '.join(rubric.ASSUMPTIONS)} 세 개가 하나씩 있어야 합니다.")
    out = []
    for key in rubric.ASSUMPTIONS:
        a = next(x for x in items if x["key"] == key)
        status = a.get("status")
        if status not in rubric.STATUSES:
            raise ValueError(f"{key}: 결과는 {'·'.join(rubric.STATUSES)} 중 하나여야 합니다.")
        evidence = []
        for n, e in enumerate(a.get("evidence") or [], 1):
            if e.get("kind") not in rubric.EVIDENCE_KINDS:
                raise ValueError(f"{key} 근거 {n}: kind는 받침·반박 중 하나여야 합니다.")
            evidence.append({"kind": e["kind"], "title": _text(e.get("title"), f"{key} 근거 {n} 제목"),
                             **_link(e, f"{key} 근거 {n}"), "note": (e.get("note") or "").strip()})
        kinds = {e["kind"] for e in evidence}
        if status in rubric.EVIDENCE_KINDS and status not in kinds:
            raise ValueError(f"{key}: '{status}'이면 그 쪽 근거가 하나 이상 있어야 합니다. 없으면 '확인 못 함'입니다.")
        out.append({
            "key": key,
            "statement": _text(a.get("statement"), f"{key} 가정 문장"),
            "status": status,
            "evidence": evidence,
            # 확증 편향을 막으려고, 반박 근거를 어떤 검색어로 먼저 찾았는지 남깁니다.
            "counter_query": _text(a.get("counter_query"), f"{key} 반박 검색어(counter_query)"),
            "user_check": (a.get("user_check") or "").strip(),
        })
    return out


def check_competitors(data: dict) -> dict:
    queries = _texts(data.get("queries"), "검색어", 1, 10)
    if not DATE.match(data.get("checked") or ""):
        raise ValueError("경쟁 조사 날짜(checked)가 YYYY-MM-DD 꼴이어야 합니다.")
    items = []
    for n, c in enumerate(data.get("items") or [], 1):
        items.append({"name": _text(c.get("name"), f"경쟁 {n} 이름"), **_link(c, f"경쟁 {n}"),
                      "diff": _text(c.get("diff"), f"경쟁 {n} 차이"),
                      "source": "사용자 입력" if c.get("user_added") else "확인됨"})
    return {"queries": queries, "checked": data["checked"], "items": items}


def check_panel(data: dict) -> dict:
    size = data.get("size")
    if size not in rubric.PANEL_SIZES.values():
        raise ValueError(f"패널은 {' 또는 '.join(map(str, rubric.PANEL_SIZES.values()))}명이어야 합니다.")
    personas = data.get("personas") or []
    if not 3 <= len(personas) <= 4:
        raise ValueError("페르소나 유형은 3~4개여야 합니다.")
    total = 0
    for p in personas:
        _text(p.get("type"), "페르소나 유형")
        if isinstance(p.get("count"), bool) or not isinstance(p.get("count"), int) or p["count"] < 1:
            raise ValueError("페르소나 count는 1 이상의 정수여야 합니다.")
        total += p["count"]
    if total != size:
        raise ValueError(f"페르소나 count 합({total})이 패널 규모({size})와 같아야 합니다.")
    against = []
    for r in data.get("against") or []:
        against.append({"reason": _text(r.get("reason"), "반대 이유"), "types": [t for t in r.get("types") or [] if t]})
    return {"size": size, "personas": [{"type": p["type"].strip(), "count": p["count"]} for p in personas],
            "against": against, "for": [f.strip() for f in data.get("for") or [] if f.strip()]}


def check_directions(data: dict) -> dict:
    items = data.get("directions") or []
    if not 2 <= len(items) <= 3:
        raise ValueError(f"방향은 2~3개여야 합니다(받은 수 {len(items)}).")
    out = []
    for n, d in enumerate(items, 1):
        out.append({
            "title": _text(d.get("title"), f"방향 {n} 이름"),
            "idea": clean_idea(d.get("idea") or {}),
            "changed": _text(d.get("changed"), f"방향 {n}에서 바꾼 것"),
            "addresses": _texts(d.get("addresses"), f"방향 {n}이 해결하는 지적", 1, 5),
            "user_checks": [c.strip() for c in d.get("user_checks") or [] if c.strip()],
        })
    pick = data.get("recommended")
    if isinstance(pick, bool) or pick not in range(1, len(out) + 1):
        raise ValueError(f"추천(recommended)은 1~{len(out)} 중 하나여야 합니다.")
    return {"items": out, "recommended": pick, "why": _text(data.get("why"), "추천 이유")}


def record(folder: Path, part: str, data: dict) -> dict:
    """한 단계의 결과를 검사해 기록합니다. 같은 단계를 다시 넣으면 옛 값을 replaced에 남기고 바꿔 씁니다."""
    folder = Path(folder)
    result = load(folder)
    if part == "judge":
        clean = check_judge(data)
        old = result["judges"].get(clean["judge"])
        result["judges"][clean["judge"]] = clean
        label = f"judge:{clean['judge']}"
    elif part in ("assumptions", "competitors", "panel", "directions"):
        clean = globals()[f"check_{part}"](data)
        old, result[part], label = result[part], clean, part
    elif part == "money":
        clean = {"values": data, "breakeven": money.breakeven(data)}
        old, result["money"], label = result["money"], clean, "money"
    else:
        raise ValueError(f"모르는 단계입니다: {part}. 가능한 값: {', '.join(PARTS)}")
    if old is not None:
        result["replaced"].append({"part": label, "at": time.strftime("%Y-%m-%d %H:%M"), "old": old})
    save(folder, result)
    return clean


def decide(folder: Path) -> dict:
    result = load(Path(folder))
    missing = [rubric.JUDGES[k]["name"] for k in rubric.ORDER if k not in result["judges"]]
    if missing:
        raise ValueError(f"심사위원 결과가 모자랍니다: {', '.join(missing)}")
    if not result["assumptions"]:
        raise ValueError("가정 검증 결과가 없습니다.")
    return verdict.decide(result["idea"], result["judges"], result["assumptions"])


def direction(folder: Path, number: int) -> dict:
    """고른 방향의 입력 4칸. 다시 심사할 때 새 기록의 입력이 됩니다."""
    result = load(Path(folder))
    items = (result.get("directions") or {}).get("items") or []
    if not 1 <= number <= len(items):
        raise ValueError(f"방향 {number}이(가) 없습니다. 이 기록의 방향 수: {len(items)}")
    return items[number - 1]


def origin(folder: Path, number: int | None = None) -> dict:
    """다시 심사할 때 새 기록에 남길 출처. 이전 입력과 고른 방향을 함께 남겨 아이디어가 바뀐 과정을 보여 줍니다."""
    folder = Path(folder)
    out = {"verdict": str(folder / "verdict.md"), "direction": number, "before": load(folder)["idea"]}
    if number:
        item = direction(folder, number)
        out.update(title=item["title"], changed=item["changed"], addresses=item["addresses"])
    return out


def runs(idea_folder: Path) -> list[Path]:
    return sorted(p for p in Path(idea_folder).iterdir() if (p / "result.json").is_file())


def compare(idea_folder: Path) -> list[dict]:
    """같은 아이디어의 날짜별 기록을 판정·점수·가정 결과로 나란히 봅니다."""
    rows = []
    for folder in runs(idea_folder):
        result = load(folder)
        try:
            decided = decide(folder)["verdict"]
        except ValueError:
            decided = "미완료"
        rows.append({
            "run": folder.name,
            "line": result["idea"]["line"],
            "verdict": decided,
            "scores": {k: result["judges"].get(k, {}).get("score") for k in rubric.ORDER},
            "assumptions": {a["key"]: a["status"] for a in result["assumptions"] or []},
            "from": result.get("from"),
        })
    return rows


def _idea_rows(idea: dict, other: dict | None = None) -> list[str]:
    if other is None:
        return [f"| {rubric.FIELDS[k]} | {idea[k]} |" for k in rubric.FIELDS]
    return [f"| {rubric.FIELDS[k]} | {other[k]} | {idea[k]} |" for k in rubric.FIELDS]


def _change_rows(before: dict, after: dict) -> list[str]:
    return [f"| {rubric.FIELDS[k]} | {before[k]} | {after[k]} |" for k in rubric.FIELDS if before[k] != after[k]]


def _growth(result: dict) -> list[str]:
    """아이디어가 이전 심사에서 이번 입력으로, 이번 입력에서 추천 방향으로 어떻게 바뀌는지 바뀐 칸만 보여 줍니다."""
    idea, f, d = result["idea"], result.get("from") or {}, result.get("directions")
    if not f.get("before") and not d:
        return []
    lines = ["## 아이디어가 이렇게 바뀌었어요", ""]
    if f.get("before"):
        lines += ["### 이전 심사에서 이번 입력으로", ""]
        if f.get("direction"):
            lines += [f"- 고른 방향: 방향 {f['direction']}. {f['title']}", f"- 바꾼 것: {f['changed']}",
                      f"- 해결하려던 지적: {' / '.join(f['addresses'])}"]
        rows = _change_rows(f["before"], idea)
        lines += ["", "| 칸 | 이전 | 이번 |", "|---|---|---|"] + rows if rows else ["- 입력은 이전과 같습니다."]
        lines.append("")
    if d:
        n = d["recommended"]
        item = d["items"][n - 1]
        lines += [f"### 이번 입력에서 추천 방향으로(방향 {n}. {item['title']})", "",
                  f"- 바꾼 것: {item['changed']}", f"- 왜: {' / '.join(item['addresses'])}", f"- 추천 이유: {d['why']}"]
        rows = _change_rows(idea, item["idea"])
        same = [rubric.FIELDS[k] for k in rubric.FIELDS if idea[k] == item["idea"][k]]
        lines += ["", "| 칸 | 지금 | 추천 방향 |", "|---|---|---|"] + rows if rows else ["- 입력 칸은 바꾸지 않았습니다."]
        if rows and same:
            lines += ["", f"그대로 둔 칸: {', '.join(same)}"]
        lines.append("")
    return lines


def render(folder: Path) -> str:
    folder = Path(folder)
    result = load(folder)
    decided = decide(folder)
    idea = result["idea"]
    lines = [f"# 새록 심사단 판정: {idea['line']} ({folder.name})", "", f"> {rubric.NOTICE}", ""]
    if result.get("from"):
        f = result["from"]
        lines += [f"다시 심사: {f['verdict']}" + (f"의 방향 {f['direction']}" if f.get("direction") else ""), ""]
    lines += ["## 판정", "", f"**{decided['verdict']}**", ""] + [f"- {s}" for s in decided["steps"]] + [""]
    lines += _growth(result)
    lines += ["## 입력(사용자 입력)", "", "| 칸 | 내용 |", "|---|---|"] + _idea_rows(idea)

    lines += ["", "## 심사위원(AI 시뮬레이션)", "", "| 심사위원 | 점수 | 투표 | 이유 | 걸리는 점 |", "|---|---:|---|---|---|"]
    for k in rubric.ORDER:
        j = result["judges"][k]
        lines.append(f"| {rubric.JUDGES[k]['name']} | {j['score']}/5 | {j['vote']} | {' / '.join(j['reasons'])} | {' / '.join(j['concerns'])} |")

    lines += ["", "## 핵심 가정 검증", ""]
    for a in result["assumptions"]:
        lines += [f"### {rubric.ASSUMPTIONS[a['key']]}: {a['status']}", "", f"- 가정: {a['statement']}",
                  f"- 반박 근거를 먼저 찾은 검색어: {a['counter_query']}"]
        for e in a["evidence"]:
            note = f": {e['note']}" if e["note"] else ""
            lines.append(f"- {e['kind']}(확인됨, {e['checked']}): [{e['title']}]({e['url']}){note}")
        if not a["evidence"]:
            lines.append("- 근거를 찾지 못했습니다(확인 못 함). 지어내지 않았습니다.")
        if a["user_check"]:
            lines.append(f"- 사용자가 직접 확인할 일: {a['user_check']}")
        lines.append("")

    c = result.get("competitors")
    lines += ["## 경쟁 서비스", ""]
    if c:
        lines += [f"찾은 범위: 검색어 {', '.join(c['queries'])} ({c['checked']})", ""]
        if c["items"]:
            lines += ["| 이름 | 출처 | 차이 |", "|---|---|---|"]
            lines += [f"| [{i['name']}]({i['url']}) | {i['source']}, {i['checked']} | {i['diff']} |" for i in c["items"]]
        else:
            lines.append("이 범위에서는 경쟁 서비스를 찾지 못했습니다. 없다는 뜻은 아닙니다.")
    else:
        lines.append("아직 조사하지 않았습니다.")

    p = result.get("panel")
    lines += ["", "## 가상 사용자 패널(AI 시뮬레이션)", ""]
    if p:
        types = ", ".join(f"{x['type']} {x['count']}명" for x in p["personas"])
        lines += [f"패널 {p['size']}명: {types}. 수요 예측이 아니라 반대 이유 모음이며 판정에 쓰지 않습니다.", ""]
        lines += [f"- 반대: {r['reason']}" + (f" ({', '.join(r['types'])})" if r["types"] else "") for r in p["against"]]
        if not p["against"]:
            lines.append("- 반대 이유가 하나도 나오지 않았습니다. 패널이 한쪽으로 쏠렸을 수 있습니다.")
        lines += [f"- 찬성: {x}" for x in p["for"]]
    else:
        lines.append("아직 돌리지 않았습니다.")

    m = result.get("money")
    lines += ["", "## 손익분기", ""]
    if m and m["breakeven"]["computed"]:
        b = m["breakeven"]
        for key, name in money.NAMES.items():
            v = m["values"][key]
            lines.append(f"- {name}: {v['value']:,} ({v['source']}{', ' + v['url'] if v.get('url') else ''})")
        lines.append(f"- 고객당 남는 돈: {b['margin']:,}원")
        lines.append(f"- 손익분기 월 고객 수: {b['customers']:,}명. {b['note']}" if b["customers"] is not None else f"- {b['note']}")
    elif m:
        lines.append(f"계산하지 않았습니다. 필요한 값: {', '.join(m['breakeven']['needed'])}")
    else:
        lines.append("가격·비용 값이 없어 계산하지 않았습니다.")

    d = result.get("directions")
    lines += ["", "## 다듬은 방향(AI 제안)", ""]
    if d:
        for n, item in enumerate(d["items"], 1):
            mark = " (추천)" if n == d["recommended"] else ""
            lines += [f"### 방향 {n}. {item['title']}{mark}", "", f"- 바꾼 것: {item['changed']}",
                      f"- 해결하는 지적: {' / '.join(item['addresses'])}"]
            lines += [f"- 직접 확인할 일: {x}" for x in item["user_checks"]]
            lines += ["", "| 칸 | 원래 입력 | 이 방향 |", "|---|---|---|"] + _idea_rows(item["idea"], idea) + [""]
        lines += [f"추천 이유: {d['why']}", "", "방향은 제안입니다. 원래 입력은 위 표에 그대로 남아 있습니다.", ""]
    else:
        lines += ["아직 만들지 않았습니다.", ""]

    verdict_path = folder / "verdict.md"
    lines += ["## 다음 단계", ""]
    if d:
        lines.append(f"- 방향 하나를 다시 심사: `/saerok-idea:judge --from \"{verdict_path}\" --direction <번호>`")
    if decided["verdict"] in ("진행", "조건부"):
        lines.append(f"- 기획으로 넘기기: `/saerok-prd:design --from \"{verdict_path}\"`")
    elif decided["verdict"] == verdict.INSUFFICIENT:
        lines.append("- 미정 칸을 채우거나, 가정을 확인할 검색어를 바꿔 다시 심사하세요.")
    return "\n".join(lines).rstrip() + "\n"


def write_report(folder: Path) -> Path:
    path = Path(folder) / "verdict.md"
    path.write_text(render(folder), encoding="utf-8")
    return path


def run_of(path: str) -> Path:
    """verdict.md 경로, 기록 폴더 경로, 또는 기록 폴더 기준 상대 경로를 기록 폴더로 바꿉니다."""
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = home() / path
    if p.name == "verdict.md" or p.name == "result.json":
        p = p.parent
    return p
