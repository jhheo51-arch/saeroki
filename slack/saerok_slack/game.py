"""끝말잇기. AI를 부르지 않고 단어장(words.txt)으로만 돌아서 Claude 구독이 없어도 됩니다."""

from __future__ import annotations

import random
import re
from pathlib import Path

WORDS_PATH = Path(__file__).resolve().parent / "words.txt"
WORD = re.compile(r"^[가-힣]{2,10}$")
GIVE_UP = {"졌다", "졌어", "졌어요", "항복", "그만", "포기"}
Y_VOWELS = {2, 3, 6, 7, 12, 17, 20}  # ㅑ ㅒ ㅕ ㅖ ㅛ ㅠ ㅣ
NIEUN, RIEUL, IEUNG = 2, 5, 11  # 초성 순번


def load(path: Path = WORDS_PATH) -> list[str]:
    words = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            words += [w for w in line.split() if WORD.match(w)]
    return list(dict.fromkeys(words))


def starts(syllable: str) -> set[str]:
    """그 글자로 이을 수 있는 첫 글자들. 두음법칙(력→역, 라→나, 녀→여)도 받습니다."""
    out = {syllable}
    code = ord(syllable) - 0xAC00
    lead, vowel, tail = code // 588, code % 588 // 28, code % 28
    if lead == RIEUL:
        out.add(chr(0xAC00 + (IEUNG if vowel in Y_VOWELS else NIEUN) * 588 + vowel * 28 + tail))
    elif lead == NIEUN and vowel in Y_VOWELS:
        out.add(chr(0xAC00 + IEUNG * 588 + vowel * 28 + tail))
    return out


def need(record: dict) -> str:
    return "/".join(sorted(starts(record["last"][-1])))


def new(channel: str) -> dict:
    return {"fruit": "word", "channel": channel, "used": [], "last": "", "over": False}


def bot_move(record: dict, words: list[str], rng=random) -> str | None:
    pool = words if not record["last"] else [w for w in words if w[0] in starts(record["last"][-1])]
    pool = [w for w in pool if w not in record["used"]]
    if not pool:
        return None
    word = rng.choice(pool)
    record["used"].append(word)
    record["last"] = word
    return word


def play(record: dict, text: str, words: list[str], rng=random) -> str | None:
    """사람의 한 수를 받아 새록이의 답을 돌려줍니다. 끝난 판이거나 단어가 아닌 글이면 None(답하지 않음)."""
    word = text.strip()
    if record["over"]:
        return None
    fits = WORD.match(word) and (not record["last"] or word[0] in starts(record["last"][-1]))
    if word in GIVE_UP and not fits:
        record["over"] = True
        return f"제가 이겼어요! 🌳 {len(record['used'])}단어를 이었어요. 다시 하려면 `/saerok-word`."
    if not WORD.match(word):
        return None
    if not fits:
        return f"‘{need(record)}’(으)로 시작하는 말이어야 해요. 지금 단어는 *{record['last']}*입니다."
    if word in record["used"]:
        return f"‘{word}’는 이미 나왔어요. 다른 말을 찾아 주세요."
    note = "" if word in words else "_(제 단어장에는 없는 말이지만 믿을게요.)_\n"
    record["used"].append(word)
    record["last"] = word
    mine = bot_move(record, words, rng)
    if mine is None:
        record["over"] = True
        return f"{note}‘{need(record)}’(으)로 시작하는 말이 떠오르지 않아요… 제가 졌어요! 🎉 {len(record['used'])}단어를 이었어요."
    return f"{note}*{mine}*\n다음은 ‘{need(record)}’(으)로 시작하는 말이에요."
