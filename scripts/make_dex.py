"""새록이 도감 데이터(dex/dex-data.js)를 만듭니다.

번호마다 이름·분류·타입·설명과 지금 레벨의 새록이 그림을 담습니다. 상태(🌱·🌸·🍎)는 README 열매 지도에서 읽으므로
README만 고치면 도감도 따라옵니다. 표준 라이브러리만 씁니다.

    python scripts/make_dex.py
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_characters as chars  # noqa: E402

REPO = chars.REPO
OUT = REPO / "dex" / "dex-data.js"
GITHUB = "https://github.com/jhheo51-arch/saeroki/tree/main/"
PAGES = "https://jhheo51-arch.github.io/saeroki/"

# 도감에만 나오는 뿌리 세 개의 소품(make_characters.CHARACTERS와 같은 형식)
DEX_PROPS = {
    "basket": [("L", (-5, -1), (
        " h h ",
        "h   h",
        "yhyhy",
        "hyhyh",
        " hhh ",
    ))],
    "flag": [("R", (0, -8), (
        "hooo",
        "hooo",
        "hoo ",
        "h   ",
        "h   ",
        "h   ",
        "h   ",
        "h   ",
    ))],
    "mirror": [("R", (0, -6), (
        " ccc ",
        "cllwc",
        "clllc",
        "clllc",
        " ccc ",
        "  h  ",
        " h   ",
    ))],
}

# 번호 → 도감 기록. 씨앗(🌱)은 분류와 설명 대신 기획 한 줄만 보여 줍니다.
ENTRIES = {
    1: dict(name="콘텐츠 개인화", kind="추천", art="curator", cls="헤드폰 새록이", folder="fruits/01-content-personalization",
            text="서울의 시간과 날씨에 귀를 기울인다. 공개 출처에서 고른 글과 음악 가운데 1~3개만 이유와 함께 건넨다."),
    2: dict(name="Agno", kind="뿌리", plan="열매들을 실행하는 공통 운영 기반. 아직 들이지 않았다."),
    3: dict(name="마케팅 전략", kind="기획", folder="fruits/03-marketing-strategy", plan="시장 데이터를 분석해 마케팅 전략을 만든다."),
    4: dict(name="새록 검토관", kind="기획", art="reviewer", cls="돋보기 새록이", folder="fruits/04-prd-assistant",
            plugin="saerok-prd",
            text="PRD의 빈칸과 근거 없는 줄을 줄 번호까지 짚어 낸다. 결정은 대신 내리지 않고 스무고개로 하나씩 묻는다."),
    5: dict(name="데이터 시각화", kind="데이터", folder="fruits/05-data-visualization",
            plan="여러 역할이 대화하며 데이터를 분석하고 시각화를 만든다."),
    6: dict(name="레시피", kind="추천", folder="fruits/06-recipe", plan="개인 맞춤형 레시피를 만든다."),
    7: dict(name="금융", kind="조사와 분석", folder="fruits/07-finance", plan="분석가 인사이트와 시장 뉴스를 정리한다."),
    8: dict(name="미디어 트렌드", kind="조사와 분석", folder="fruits/08-media-trend",
            plan="뉴스와 디지털 트렌드를 분석하고 인플루언서를 찾는다."),
    9: dict(name="법률 문서", kind="조사와 분석", folder="fruits/09-legal-document", plan="PDF 법률 문서를 분석한다."),
    10: dict(merged=9),
    11: dict(name="도서", kind="추천", folder="fruits/11-book-recommendation", plan="개인화된 도서를 추천한다."),
    12: dict(name="정보 수집", kind="뿌리", art="basket", cls="바구니 새록이",
             text="공개 출처를 돌아다니며 후보를 바구니에 담는다. 출처를 모르는 열매는 줍지 않는다."),
    13: dict(name="계획 후 실행", kind="뿌리", art="flag", cls="깃발 새록이",
             text="길을 떠나기 전에 단계마다 깃발을 꽂아 둔다. 지나온 단계는 빠짐없이 기록한다."),
    14: dict(name="결과 자기 검토", kind="뿌리", art="mirror", cls="거울 새록이",
             text="일을 마치면 결과를 거울에 비춰 본다. 틀린 곳을 찾으면 스스로 고친다."),
    15: dict(name="심층 연구", kind="조사와 분석", folder="fruits/15-deep-research", plan="주제를 깊게 조사해 리포트를 쓴다."),
    16: dict(name="새록 SQL", kind="데이터", art="sql", cls="원통 새록이", folder="fruits/16-natural-language-sql",
             text="우리말 질문을 SQL로 바꿔 서울 공공 데이터를 캐낸다. 데이터는 읽기만 하고 고치지 않는다."),
    17: dict(name="새록 사전", kind="학습", art="dictionary", cls="안경 새록이", folder="fruits/17-saerok-dictionary",
             web=PAGES, text="산업과 직무의 낯선 말을 출처와 함께 풀어 준다. 두꺼운 사전을 늘 옆구리에 끼고 다닌다."),
    18: dict(name="새록 파수꾼", kind="돌봄", art="sentry", cls="파수꾼 새록이", folder="fruits/18-saerok-watch",
             plugin="saerok-watch",
             text="대화가 20만 토큰을 넘으면 경계 태세에 들어간다. 40만을 넘으면 경고를 울리고 새는 곳을 찾는다."),
    19: dict(name="새록 면접관", kind="학습", art="interviewer", cls="넥타이 새록이", folder="fruits/19-saerok-interview",
             plugin="saerok-interview", web=PAGES + "interview/",
             text="다섯 면접관이 자기소개서를 저마다의 기준으로 심사한다. 질문마다 어느 문장을 보고 물었는지 밝힌다."),
    20: dict(name="새록 심사단", kind="기획", art="judge", cls="판사봉 새록이", folder="fruits/20-saerok-idea",
             plugin="saerok-idea", web=PAGES + "idea/",
             text="아이디어 한 줄을 심사위원 셋이 판정한다. 진행·조건부·보류 가운데 하나와 다듬은 방향을 내놓는다."),
    21: dict(name="새록 지원서", kind="학습", art="apply", cls="연필 새록이", folder="fruits/21-saerok-apply",
             plan="채용 공고를 분석하고 내 경험 장부에 적힌 경험만으로 자기소개서를 쓴다.",
             text="채용 공고를 읽고 내 경험 장부에 적힌 경험만으로 자기소개서를 쓴다. 다 쓴 글은 면접관에게 넘긴다."),
}

STATUS = {"🌱": "seed", "🌸": "flower", "🍎": "fruit"}


def statuses() -> dict[int, str]:
    """README 열매 지도(에이전트 표와 뿌리 표)에서 번호별 상태를 읽습니다."""
    text = (REPO / "README.md").read_text(encoding="utf-8")
    found = {int(n): STATUS[s] for s, n in re.findall(r"(🌱|🌸|🍎) \[(\d+) ", text)}
    found.update({int(n): STATUS[s] for s, n in re.findall(r"^\| (🌱|🌸|🍎) (\d+) ", text, re.M)})
    return found


def art(key: str, level: int) -> tuple[list[str], dict]:
    if key == "sentry":
        sys.path.insert(0, str(REPO / "fruits" / "18-saerok-watch"))
        from saerok_watch import character  # noqa: PLC0415
        return character.sentry_sprite(level)
    if key in DEX_PROPS:
        return chars.draw(DEX_PROPS[key], level)
    return chars.sprite(key, level)


def silhouette(level: int) -> list[str]:
    rows, _ = chars.draw([], level)
    return ["".join("x" if c != " " else " " for c in r) for r in rows]


def build(level: int) -> dict:
    status = statuses()
    entries = []
    for no in range(1, max(ENTRIES) + 1):
        info = ENTRIES[no]
        if "merged" in info:
            entries.append({"no": no, "merged": info["merged"]})
            continue
        item = {"no": no, "name": info["name"], "kind": info["kind"], "status": status.get(no, "seed"),
                "folder": GITHUB + info["folder"] if "folder" in info else None,
                "plugin": info.get("plugin"), "web": info.get("web")}
        if item["status"] == "seed" or "art" not in info:
            item.update(plan=info.get("plan", ""), sprite=silhouette(level))
        else:
            rows, colors = art(info["art"], level)
            used = {c for r in rows for c in r if c != " "}
            item.update(cls=info["cls"], text=info["text"], sprite=rows,
                        colors={c: colors[c] for c in sorted(used)})
        entries.append(item)
    return {"level": level, "entries": entries}


def main() -> None:
    data = build(chars.current_level())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("// scripts/make_dex.py가 만든 파일입니다. 직접 고치지 마세요.\nwindow.SAEROK_DEX = "
                   + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    seen = sum(e.get("status") in ("flower", "fruit") for e in data["entries"])
    fruit = sum(e.get("status") == "fruit" for e in data["entries"])
    print(f"{OUT.relative_to(REPO)}: {len(data['entries'])}번까지, 꽃 이상 {seen} · 열매 {fruit}")


if __name__ == "__main__":
    main()
