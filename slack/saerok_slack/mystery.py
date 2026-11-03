"""숲속 추리 게임. AI를 부르지 않고 사건집(cases.json)으로만 돌아서 Claude 구독이 없어도 됩니다."""

from __future__ import annotations

import json
from pathlib import Path

CASES_PATH = Path(__file__).resolve().parent / "cases.json"
CHANCES = 2  # 범인 지목 기회
GIVE_UP = {"포기", "정답", "정답 보기", "모르겠다", "항복"}
HELP = ("스레드에 답글로\n"
        "• `단서`: 단서를 하나씩 엽니다\n"
        "• 용의자 이름(예: `{name}`): 그 동물의 말을 듣습니다\n"
        "• `용의자`: 용의자 목록\n"
        "• `범인 {name}`: 범인을 지목합니다(기회 {chances}번)\n"
        "• `포기`: 정답을 봅니다")


def eun(name: str) -> str:
    """이름 뒤 은/는."""
    return name + ("은" if (ord(name[-1]) - 0xAC00) % 28 else "는")


def load(path: Path = CASES_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def find(book: dict, case_id: int) -> dict | None:
    return next((c for c in book["cases"] if c["id"] == case_id), None)


def listing(book: dict, solved: set[int] = frozenset()) -> str:
    rows = [f"{'✅' if c['id'] in solved else '🔍'} 제{c['id']}화 {c['title']}" for c in book["cases"]]
    return f"*{book['series']}*\n" + "\n".join(rows) + "\n`/saerok-case 2`처럼 회차를 적으면 그 사건을 엽니다."


def next_case(book: dict, solved: set[int]) -> dict:
    return next((c for c in book["cases"] if c["id"] not in solved), book["cases"][0])


def new(channel: str, case: dict, user: str) -> dict:
    return {"fruit": "case", "channel": channel, "case": case["id"], "user": user,
            "clues": 0, "wrong": 0, "over": False, "solved": False}


def opening(book: dict, case: dict) -> str:
    suspects = "\n".join(f"• *{s['name']}* ({s['who']})" for s in case["suspects"])
    name = case["suspects"][0]["name"]
    return (f"*{book['series']} 제{case['id']}화: {case['title']}*\n\n{case['intro']}\n\n"
            f"*용의자*\n{suspects}\n\n" + HELP.format(name=name, chances=CHANCES))


def suspect_in(case: dict, text: str) -> list[dict]:
    return [s for s in case["suspects"] if any(n in text for n in (s["name"], *s.get("aliases", [])))]


def finish(record: dict, case: dict, solved: bool) -> str:
    record["over"] = True
    record["solved"] = solved
    head = (f"🎉 정답이에요! 범인은 *{case['culprit']}*. 단서 {record['clues']}개로 풀었어요."
            if solved else f"🌙 사건 종료. 범인은 *{case['culprit']}*{'이었' if (ord(case['culprit'][-1]) - 0xAC00) % 28 else '였'}어요.")
    return f"{head}\n\n*새록 탐정의 풀이*\n{case['solution']}\n\n다음 사건은 `/saerok-case`."


def play(record: dict, text: str, book: dict) -> str | None:
    """답글 하나를 받아 답을 돌려줍니다. 끝난 사건이거나 게임 말이 아니면 None(답하지 않음)."""
    case = find(book, record["case"])
    text = " ".join(text.split())
    if record["over"] or not case or not text:
        return None
    if text in GIVE_UP:
        return finish(record, case, False)
    if text in ("도움말", "규칙", "?"):
        return HELP.format(name=case["suspects"][0]["name"], chances=CHANCES)
    if text in ("용의자", "용의자 목록"):
        return "*용의자*\n" + "\n".join(f"• *{s['name']}* ({s['who']})" for s in case["suspects"])
    if text in ("단서", "단서 줘", "다음 단서", "힌트"):
        clues = case["clues"]
        if record["clues"] >= len(clues):
            return "단서를 모두 열었어요. 이제 `범인 이름`으로 지목해 보세요."
        clue = clues[record["clues"]]
        record["clues"] += 1
        left = len(clues) - record["clues"]
        return f"🔎 *단서 {record['clues']}. {clue['name']}*\n{clue['text']}\n_남은 단서 {left}개_"
    found = suspect_in(case, text)
    if "범인" in text:
        if len(found) != 1:
            return "범인으로 지목할 동물을 한 명만 적어 주세요. 예: `범인 " + case["suspects"][0]["name"] + "`"
        if found[0]["name"] == case["culprit"]:
            return finish(record, case, True)
        record["wrong"] += 1
        if record["wrong"] >= CHANCES:
            return f"❌ {eun(found[0]['name'])} 범인이 아니에요.\n" + finish(record, case, False)
        return f"❌ {eun(found[0]['name'])} 범인이 아니에요. 기회가 {CHANCES - record['wrong']}번 남았어요."
    if len(found) == 1 and len(text) <= len(found[0]["name"]) + 6:
        s = found[0]
        return f"🗣️ *{s['name']}* ({s['who']})\n“{s['statement']}”"
    return None
