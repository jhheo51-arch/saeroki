"""파수꾼 새록이: 지금 레벨의 새록이(growth.py)가 K-2 소총을 들고 보초를 서는 픽셀 그림.

저장소 루트의 growth.py와 data/growth.json을 읽어, 새록이가 자라면 파수꾼 모습도 함께 자랍니다.
"""

import struct
import sys
import zlib
from pathlib import Path

from .paths import FRUIT_DIR
from .store import read_json

REPO = FRUIT_DIR.parent.parent

# K-2 소총(오른쪽을 겨눈 옆모습). 둘째 줄이 팔 높이에 옵니다.
# f 접철식 개머리판·손잡이, g 총몸·총열, h 가늠자·소염기
RIFLE = (
    "          h      g  ",
    "ffffgggggggggggggggh",
    "f   gggggff         ",
    "      f  gg         ",
    "          g         ",
)
RIFLE_COLORS = {"f": "#1A1C1E", "g": "#3A3F44", "h": "#7A828A"}

# 플러그인으로 설치해 growth.py가 없는 컴퓨터에서 쓰는 레벨 10 파수꾼 새록이
FALLBACK = (
    "         L          ",
    "       LGGLGL       ",
    "        DKDD        ",
    "       LGKD         ",
    "        DKD         ",
    "         KD         ",
    "      BBBBBBBb      ",
    "      BEBBBEBb      ",
    "      BEBBhEBb   g  ",
    "ffffgBggggggggbggggh",
    "f   gggggffBBb      ",
    "      f bggb b      ",
    "          g         ",
)
FALLBACK_COLORS = {"L": "#ECF39E", "G": "#90A955", "D": "#40916C", "K": "#31572C",
                   "B": "#B07A4F", "b": "#8A5A36", "E": "#1F2A1F", **RIFLE_COLORS}


def _growth():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    import growth  # noqa: PLC0415  저장소 루트에 있어 실행 때 불러옵니다.
    return growth


def current_level() -> int:
    state = read_json(REPO / "data" / "growth.json", {}) or {}
    return int((state.get("stage") or {}).get("level") or 1)


def sentry_sprite(level: int | None = None) -> tuple[list[str], dict]:
    """(잘라 낸 픽셀 줄, 글자→색) 을 돌려줍니다."""
    try:
        growth = _growth()
    except ImportError:
        return list(FALLBACK), FALLBACK_COLORS
    level = level or current_level()
    grid = [list(row) for row in growth.sprite_for(level)]
    grid += [[" "] * len(grid[0]) for _ in range(2)]  # 탄창이 발아래로 내려올 자리
    width, height = growth._body_size(level)
    left = int(growth.CENTER) - width // 2
    arm = growth.GRID_H - 1 - height + 3

    start = left - 6
    for dy, row in enumerate(RIFLE):
        y = arm - 1 + dy
        for dx, c in enumerate(row):
            x = start + dx
            if c != " " and 0 <= y < len(grid) and 0 <= x < len(grid[y]):
                grid[y][x] = c
    # 총을 쥔 두 손
    grid[arm][left - 1] = "B"
    grid[arm][left + width] = "b"

    rows = ["".join(r) for r in grid]
    filled = [y for y, r in enumerate(rows) if r.strip()]
    xs = [x for r in rows for x, c in enumerate(r) if c != " "]
    top, bottom = filled[0], filled[-1]
    lo, hi = min(xs), max(xs)
    cropped = [r[lo:hi + 1] for r in rows[top:bottom + 1]]
    return cropped, {**growth.COLORS, **RIFLE_COLORS}


def render_svg(level: int | None = None, pixel: int = 6) -> str:
    rows, colors = sentry_sprite(level)
    w, h = len(rows[0]) * pixel, len(rows) * pixel
    rects = []
    for y, row in enumerate(rows):
        x = 0
        while x < len(row):
            c, run = row[x], 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            if c in colors:
                rects.append(f'<rect x="{x * pixel}" y="{y * pixel}" width="{run * pixel}" height="{pixel}" fill="{colors[c]}"/>')
            x += run
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
            f'shape-rendering="crispEdges" role="img" aria-label="K-2 소총을 든 파수꾼 새록이">{"".join(rects)}</svg>')


def render_png(level: int | None = None, pixel: int = 8, pad: int = 2) -> bytes:
    """Windows 알림 등 SVG를 못 쓰는 곳을 위한 투명 배경 PNG(표준 라이브러리만 사용)."""
    rows, colors = sentry_sprite(level)
    cols = len(rows[0]) + pad * 2
    rows = [" " * cols] * pad + [" " * pad + r + " " * pad for r in rows] + [" " * cols] * pad
    w, h = cols * pixel, len(rows) * pixel

    def rgba(c):
        if c not in colors:
            return b"\x00\x00\x00\x00"
        v = colors[c].lstrip("#")
        return bytes.fromhex(v) + b"\xff"

    raw = bytearray()
    for row in rows:
        line = b"".join(rgba(c) * pixel for c in row)
        for _ in range(pixel):
            raw += b"\x00" + line

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
