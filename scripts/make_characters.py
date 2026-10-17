"""에이전트별 새록이 캐릭터 그림을 만듭니다.

파수꾼(18번, fruits/18-saerok-watch/saerok_watch/character.py)처럼 지금 레벨의 새록이(growth.py)에
에이전트마다 맞는 소품을 얹은 픽셀 그림입니다. 표준 라이브러리만 씁니다.

    python scripts/make_characters.py            # 지금 레벨로 assets/characters/*.png와 파수꾼 그림 생성
    python scripts/make_characters.py --level 50  # 레벨을 정해서 생성
"""

import argparse
import json
import struct
import sys
import zlib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "assets" / "characters"
sys.path.insert(0, str(REPO))
import growth  # noqa: E402  저장소 루트에 있습니다.

PROP_COLORS = {
    "n": "#1F2A44",  # 넥타이·법복(짙은 남색)
    "w": "#FAF9F6",  # 종이·셔츠 깃
    "i": "#1F2A1F",  # 글씨
    "c": "#7A828A",  # 쇠붙이(집게·안경테·돋보기 테)
    "s": "#3A3F44",  # 쇠붙이 그림자
    "l": "#BFE3F2",  # 유리
    "h": "#5C3A21",  # 짙은 나무(판사봉·클립보드)
    "r": "#B23A3A",  # 빨간 표지
    "y": "#F2C14E",  # 금빛
    "o": "#D97757",  # 클로드 주황
    "q": "#4A7FB5",  # 데이터 원통
    "Q": "#2F5E8C",  # 데이터 원통 그림자
}

# 소품: (기준점, (dx, dy), 픽셀 줄). 기준점 "R"은 오른손, "L"은 왼손, "C"는 몸통 윗줄 가운데이고
# 소품 왼쪽 위를 기준점에서 (dx, dy)만큼 옮긴 곳에 둡니다. 공백은 투명입니다.
# 몸통 너비(레벨마다 8·10·12)를 따라야 하는 소품은 이름만 적고 WORN에서 그립니다.
CHARACTERS = {
    "reviewer": {
        "name": "새록 검토관",
        "fruit": "04",
        "alt": "돋보기로 PRD를 살피는 검토관 새록이",
        "props": [
            ("R", (0, -6), (
                " ccc ",
                "clllc",
                "cllwc",
                "clllc",
                " ccc ",
                "h    ",
                "     ",
            )),
        ],
    },
    "sql": {
        "name": "새록 SQL",
        "fruit": "16",
        "alt": "데이터 원통을 안은 SQL 새록이",
        "props": [
            ("L", (-5, -3), (
                " qqq ",
                "qQQQq",
                "qqqqq",
                "QqqqQ",
                "qqqqq",
                "QqqqQ",
                " QQQ ",
            )),
        ],
    },
    "dictionary": {
        "name": "새록 사전",
        "fruit": "17",
        "alt": "동그란 안경을 쓰고 두꺼운 사전을 낀 새록이",
        "props": [
            ("glasses", None, None),
            ("L", (-4, -3), (
                "rrrw",
                "rywr",
                "rrwr",
                "rrwr",
                "rywr",
                "rrrw",
            )),
        ],
    },
    "interviewer": {
        "name": "새록 면접관",
        "fruit": "19",
        "alt": "넥타이를 매고 클립보드를 든 면접관 새록이",
        "props": [
            ("C", (-2, 3), (
                "wnnw",
                " nn ",
                " nn ",
            )),
            ("L", (-5, -4), (
                " ccc ",
                "hwwwh",
                "hiiwh",
                "hwwwh",
                "hiiih",
                "hwwwh",
                "hhhhh",
            )),
        ],
    },
    "judge": {
        "name": "새록 심사단",
        "fruit": "20",
        "alt": "법복을 입고 판사봉을 든 심사단 새록이",
        "props": [
            ("R", (-1, -5), (
                "hhhhh",
                "hhhhh",
                "  h  ",
                "  h  ",
                " h   ",
            )),
            ("robe", None, None),
        ],
    },
    "curator": {
        "name": "새록 콘텐츠 개인화",
        "fruit": "01",
        "alt": "헤드폰을 쓰고 음표를 띄운 새록이",
        "props": [
            ("headphones", None, None),
            ("R", (2, -9), (
                "  oo",
                "  o ",
                "  o ",
                "ooo ",
                "oo  ",
            )),
        ],
    },
}

def _glasses(left, top, width, height):
    inset = 1 + (width - 8) // 4  # growth._draw_body의 눈 위치
    eyes = (left + inset, left + width - 2 - inset)
    cells = [(x, y) for ex in eyes for x in (ex - 1, ex + 1) for y in (top + 1, top + 2)]
    cells += [(x, top + 1) for x in range(eyes[0] + 2, eyes[1] - 1)]
    return [(x, y, "c") for x, y in cells]


def _robe(left, top, width, height):
    mid = left + width // 2
    return [(x, y, "w" if x in (mid - 1, mid) and y < top + 5 else "n")
            for y in range(top + 3, top + height) for x in range(left, left + width)]


def _headphones(left, top, width, height):
    cells = [(x, top - 1, "s") for x in range(left, left + width)]
    for x in (left - 1, left + width):
        cells += [(x, top, "s"), (x, top + 1, "o"), (x, top + 2, "o")]
    return cells


WORN = {"glasses": _glasses, "robe": _robe, "headphones": _headphones}

PAD = 8  # 소품이 그림 밖으로 나가지 않도록 둘레에 둘 여백


def current_level() -> int:
    path = REPO / "data" / "growth.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return 1
    return int((state.get("stage") or {}).get("level") or 1)


def sprite(key: str, level: int) -> tuple[list[str], dict]:
    """(잘라 낸 픽셀 줄, 글자→색)을 돌려줍니다."""
    base = growth.sprite_for(level)
    grid = [[" "] * (len(base[0]) + PAD * 2) for _ in range(len(base) + PAD * 2)]
    for y, row in enumerate(base):
        for x, c in enumerate(row):
            grid[y + PAD][x + PAD] = c
    width, height = growth._body_size(level)
    left = int(growth.CENTER) - width // 2 + PAD
    top = growth.GRID_H - 1 - height + PAD
    anchors = {"C": (left + width // 2, top), "L": (left - 1, top + 3), "R": (left + width, top + 3)}
    for anchor, offset, rows in CHARACTERS[key]["props"]:
        if anchor in WORN:
            for x, y, c in WORN[anchor](left, top, width, height):
                grid[y][x] = c
            continue
        (dx, dy), (ax, ay) = offset, anchors[anchor]
        for y, row in enumerate(rows):
            for x, c in enumerate(row):
                if c != " ":
                    grid[ay + dy + y][ax + dx + x] = c
    rows = ["".join(r) for r in grid]
    filled = [y for y, r in enumerate(rows) if r.strip()]
    xs = [x for r in rows for x, c in enumerate(r) if c != " "]
    cropped = [r[min(xs):max(xs) + 1] for r in rows[filled[0]:filled[-1] + 1]]
    return cropped, {**growth.COLORS, **PROP_COLORS}


def render_png(key: str, level: int, pixel: int = 8, pad: int = 2) -> bytes:
    rows, colors = sprite(key, level)
    cols = len(rows[0]) + pad * 2
    rows = [" " * cols] * pad + [" " * pad + r + " " * pad for r in rows] + [" " * cols] * pad
    w, h = cols * pixel, len(rows) * pixel

    def rgba(c):
        return bytes.fromhex(colors[c].lstrip("#")) + b"\xff" if c in colors else b"\x00\x00\x00\x00"

    raw = bytearray()
    for row in rows:
        line = b"".join(rgba(c) * pixel for c in row)
        for _ in range(pixel):
            raw += b"\x00" + line

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--level", type=int, default=None)
    args = parser.parse_args(argv)
    level = args.level or current_level()
    OUT.mkdir(parents=True, exist_ok=True)
    for key, info in CHARACTERS.items():
        path = OUT / f"saeroki-{key}.png"
        path.write_bytes(render_png(key, level))
        print(f"{info['fruit']}번 {info['name']}: {path.relative_to(REPO)}")
    # 18번 파수꾼도 같은 레벨로 다시 그립니다(그림 코드는 파수꾼 폴더에 있습니다).
    sys.path.insert(0, str(REPO / "fruits" / "18-saerok-watch"))
    from saerok_watch import character  # noqa: PLC0415
    path = REPO / "assets" / "saeroki-sentry.png"
    path.write_bytes(character.render_png(level))
    print(f"18번 새록 파수꾼: {path.relative_to(REPO)}")


if __name__ == "__main__":
    main()
