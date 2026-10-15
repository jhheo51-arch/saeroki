"""새록이 묘목 성장 상태를 계산하고 픽셀 아트 SVG로 그립니다.

성장 점수 = 순방문자 + 스타 x 10 + 작업량
- 순방문자: GitHub traffic API의 날짜별 순방문자(uniques) 합. 한 사람은 하루에 1점까지만 셉니다.
- 스타: 저장소 주인을 뺀 스타 1개당 10점.
- 작업량: 사람이 한 커밋마다 1점 + 바뀐 줄 50줄마다 1점(커밋당 최대 4점) + 작업한 날마다 3점.
  봇 커밋과 자동 생성 그림(assets/), 성장 기록(data/growth.json)은 세지 않습니다.
레벨은 1부터 100까지이며, 레벨이 오를수록 필요한 점수가 점점 커집니다(Lv.100 약 9,800점).
생김새는 레벨 숫자로 정해지는 절차적 픽셀 아트라서 레벨마다 모두 다르고, 후반에는 세계수처럼 층층이 자랍니다.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MAX_LEVEL = 100
GRID_W = 48
GRID_H = 62
CENTER = GRID_W / 2  # 몸통과 잎 덩어리의 가운데 x 좌표

STAR_POINTS = 10
DAY_POINTS = 3
LINES_PER_POINT = 50
MAX_SIZE_POINTS = 4
BOT_AUTHORS = ("saeroki-bot", "github-actions[bot]")
IGNORED_PATHS = ("assets/", "data/growth.json")

COLORS = {
    "L": "#ECF39E",  # 연두 잎
    "G": "#90A955",  # 잎
    "D": "#40916C",  # 짙은 잎
    "K": "#31572C",  # 가장 짙은 잎, 줄기, 가지
    "M": "#C7F9CC",  # 빛나는 잎
    "B": "#B07A4F",  # 몸통(나무껍질)
    "b": "#8A5A36",  # 몸통 그림자, 뿌리
    "E": "#1F2A1F",  # 새록이 눈
    "e": "#1F2A1F",  # 새 눈
    "O": "#D97757",  # 열매(클로드 주황)
    "W": "#FAF9F6",  # 꽃, 빛 씨앗 가운데
    "P": "#F2B5C4",  # 꽃 가운데
    "U": "#6C9BC9",  # 나무에 깃든 새
    "Y": "#F2C14E",  # 금빛 열매와 빛 씨앗
}
LEAF = "LGDKM"

# (시작 레벨, 이름). 10레벨마다 새 특징이 하나씩 생깁니다.
TIERS = (
    (1, "새싹"),
    (10, "묘목"),
    (20, "어린 나무"),
    (30, "가지 뻗는 나무"),
    (40, "꽃 피는 나무"),
    (50, "열매 맺는 나무"),
    (60, "새가 쉬는 나무"),
    (70, "층층이 자라는 나무"),
    (80, "덩굴 드리운 고목"),
    (90, "빛을 품은 나무"),
    (100, "세계수"),
)


@dataclass(frozen=True)
class Level:
    level: int
    name: str
    threshold: int


def threshold_for(level: int) -> int:
    """레벨에 도달하는 데 필요한 누적 점수. Lv.1 0점, Lv.10 130점, Lv.50 약 2,760점, Lv.100 약 9,800점."""
    return round(2.5 * (level - 1) ** 1.8)


def tier_name(level: int) -> str:
    name = TIERS[0][1]
    for start, tier in TIERS:
        if level >= start:
            name = tier
    return name


LEVELS = tuple(Level(n, tier_name(n), threshold_for(n)) for n in range(1, MAX_LEVEL + 1))


def level_for_score(score: int) -> Level:
    current = LEVELS[0]
    for level in LEVELS:
        if score >= level.threshold:
            current = level
    return current


def next_level(level: Level) -> Level | None:
    return LEVELS[level.level] if level.level < MAX_LEVEL else None


# ---------- 픽셀 아트 생성 ----------

def _noise(x: int, y: int, seed: int) -> float:
    """좌표와 레벨로 정해지는 0~1 사이 값. 같은 레벨은 언제나 같은 모습이 됩니다."""
    n = (x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)
    n = (n ^ (n >> 13)) * 1274126177
    return ((n ^ (n >> 16)) & 0xFFFF) / 0xFFFF


class Canvas:
    def __init__(self) -> None:
        self.cells = [[" "] * GRID_W for _ in range(GRID_H)]

    def put(self, x: int, y: int, c: str) -> None:
        if 0 <= x < GRID_W and 0 <= y < GRID_H:
            self.cells[y][x] = c

    def get(self, x: int, y: int) -> str:
        return self.cells[y][x] if 0 <= x < GRID_W and 0 <= y < GRID_H else " "

    def rows(self) -> tuple[str, ...]:
        return tuple("".join(row) for row in self.cells)


def _body_size(level: int) -> tuple[int, int]:
    t = (level - 1) / (MAX_LEVEL - 1)
    width = 8 + 2 * round(2 * t)  # 8, 10, 12
    height = 5 + round(5 * t)  # 5 ~ 10
    return width, height


def _draw_body(cv: Canvas, level: int) -> tuple[int, int, int]:
    """클로드 캐릭터처럼 네모난 몸통, 세로 눈, 양팔과 네 다리. (왼쪽 x, 윗줄 y, 너비)를 돌려줍니다."""
    width, height = _body_size(level)
    left = int(CENTER) - width // 2
    top = GRID_H - 1 - height
    for y in range(top, GRID_H - 1):
        for x in range(left, left + width):
            cv.put(x, y, "b" if x == left + width - 1 else "B")
    inset = 1 + (width - 8) // 4
    for y in (top + 1, top + 2):
        cv.put(left + inset, y, "E")
        cv.put(left + width - 2 - inset, y, "E")
    cv.put(left - 1, top + 3, "B")
    cv.put(left + width, top + 3, "b")
    for x in (left, left + 2, left + width - 3, left + width - 1):
        cv.put(x, GRID_H - 1, "b")
    return left, top, width


def _leaf(cv: Canvas, x: int, y: int, length: int, direction: int) -> None:
    """줄기에서 바깥쪽으로 뻗는 두 줄짜리 잎. direction은 -1(왼쪽) 또는 1(오른쪽)."""
    for i in range(length):
        tip = i == length - 1
        cv.put(x + direction * i, y, "L" if tip else "G")
        if not tip:
            cv.put(x + direction * i, y + 1, "D" if i == 0 else "G")


def _draw_sprout(cv: Canvas, level: int, top: int) -> None:
    """1~19레벨: 줄기가 자라고 잎이 늘어납니다."""
    c0, c1 = int(CENTER) - 1, int(CENTER)
    if level < 10:
        stem = 1 + (level - 1) // 3
        leaf = 2 + (level - 1) % 3
        pairs = 1
    else:
        stem = 4 + (level - 10)
        leaf = 2 + (level - 10) // 4
        pairs = 2 + (level - 10) // 2
    tip = top - stem
    for y in range(tip, top):
        cv.put(c0, y, "K")
        cv.put(c1, y, "D")
    _leaf(cv, c0 - 1, tip - 1, leaf, -1)
    _leaf(cv, c1 + 1, tip - 1, leaf, 1)
    if level >= 4:
        cv.put(c0, tip - 1, "G")
        cv.put(c1, tip - 1, "L")
    if level >= 7:
        cv.put(c0, tip - 2, "L")
    for i in range(1, pairs):
        y = tip + 1 + (i - 1) * 2
        if y >= top - 1:
            break
        side = -1 if i % 2 else 1
        start = c0 - 1 if side < 0 else c1 + 1
        _leaf(cv, start, y, max(2, leaf - 1 + (i == 1)), side)


def _blobs(level: int, salt: int, cx: float, cy: float, r: float, lobes: int) -> list[tuple[float, float, float]]:
    blobs = [(cx, cy, r)]
    for i in range(lobes):
        angle = math.pi * (0.12 + 0.76 * (i + 0.5) / lobes)
        jitter = (_noise(i, 7 + salt, level) - 0.5) * 0.3
        blobs.append((
            cx - math.cos(angle) * r * (0.72 + jitter),
            cy - math.sin(angle) * r * 0.5 + r * 0.18,
            r * (0.52 + 0.12 * _noise(i, 3 + salt, level)),
        ))
    return blobs


def _paint_canopy(cv: Canvas, level: int, salt: int, blobs, cy: float, r: float, squash: float, floor_y: float,
                  ledge: bool = False) -> None:
    """잎 덩어리를 칠합니다. 왼쪽 위가 밝고 오른쪽 아래가 어두우며, 아랫단은 그림자로 층을 나눕니다."""
    for y in range(GRID_H):
        py = y + 0.5
        if py > floor_y:
            continue
        for x in range(GRID_W):
            px = x + 0.5
            edge = (_noise(x, y, level * 7 + salt) - 0.5) * 1.1
            if not any((px - bx) ** 2 + ((py - by) / squash) ** 2 <= (br + edge) ** 2 for bx, by, br in blobs):
                continue
            shade = (px - CENTER) / (r * 1.6) + (py - cy) / (r * squash * 1.4)
            shade += (_noise(y, x, level + 101 + salt) - 0.5) * 0.45
            if ledge and py > cy + r * squash * 0.45:
                shade += 0.55  # 층 아랫단 그림자
            color = "L" if shade < -0.8 else "G" if shade < 0.15 else "D" if shade < 0.7 else "K"
            cv.put(x, y, color)


def _draw_trunk(cv: Canvas, level: int, body_top: int) -> int:
    """몸통 위 줄기. 60레벨부터 굵어지고 껍질 무늬가 생깁니다. 줄기 꼭대기 y를 돌려줍니다."""
    if level < 60:
        width, height = 2, 1 + (level - 20) // 25
    else:
        width, height = (4 if level < 80 else 6), 2 + (level - 60) // 8
    left = int(CENTER) - width // 2
    for y in range(body_top - height, body_top):
        for x in range(left, left + width):
            bark = x == left + width - 1 or (width > 2 and _noise(x, y, level) > 0.8)
            cv.put(x, y, "b" if bark else "B")
    return body_top - height


def _draw_canopy(cv: Canvas, level: int, trunk_top: int) -> float:
    """20레벨부터 둥근 잎 덩어리, 70레벨부터 세계수처럼 층층이 쌓인 잎. 기준 반지름을 돌려줍니다."""
    r = 4.0 + (level - 20) * 0.115
    if level < 70:
        squash = 0.8
        cy = trunk_top - r * squash + 0.5
        lobes = min(6, 1 + (level - 20) // 12)
        _paint_canopy(cv, level, 0, _blobs(level, 0, CENTER, cy, r, lobes), cy, r, squash, trunk_top + 0.5)
        return r
    squash = 0.6
    count = 2 if level < 90 else 3
    sizes = [r * 1.2, r * 0.88, r * 0.6][:count]
    centers = []
    cy = trunk_top + 1 - sizes[0] * squash
    for i, size in enumerate(sizes):
        centers.append(cy)
        if i + 1 < count:
            cy -= size * squash * 1.15
    # 아래층부터 칠하고, 위층 아랫단의 그림자가 아래층 위에 드리워 층이 보이게 합니다.
    for i in range(count):
        size, cy = sizes[i], centers[i]
        lobes = 2 + count - i
        floor_y = cy + size * squash + 1 if i else trunk_top + 1.5
        _paint_canopy(cv, level, i * 13, _blobs(level, i * 13, CENTER, cy, size, lobes), cy, size, squash, floor_y, ledge=i > 0)
    return r


def _cells(cv: Canvas, colors: str) -> list[tuple[int, int]]:
    return [(x, y) for y in range(GRID_H) for x in range(GRID_W) if cv.get(x, y) in colors]


def _scatter(cv: Canvas, level: int, salt: int, count: int, colors: str, paint) -> None:
    cells = sorted(_cells(cv, colors), key=lambda p: _noise(p[0], p[1], level * 31 + salt))
    placed: list[tuple[int, int]] = []
    for x, y in cells:
        if len(placed) >= count:
            break
        if all(abs(x - px) + abs(y - py) > 3 for px, py in placed):
            paint(x, y)
            placed.append((x, y))


def _draw_branches(cv: Canvas, level: int, trunk_top: int, r: float) -> None:
    length = min(int(r * 0.8), 2 + (level - 30) // 6)
    c0, c1 = int(CENTER) - 1, int(CENTER)
    for i in range(length):
        cv.put(c0 - 1 - i, trunk_top - 1 - i, "K")
        cv.put(c1 + 1 + i, trunk_top - 1 - i, "K")
    for y in range(trunk_top - min(length + 1, int(r * 0.6)), trunk_top):
        cv.put(c0, y, "K")
        cv.put(c1, y, "K")


def _draw_bird(cv: Canvas, level: int) -> None:
    column = int(CENTER + 3 + (level % 5))
    top = next((y for y in range(GRID_H) if cv.get(column, y) in LEAF), None)
    if top is None:
        return
    for dx, dy, c in ((0, -2, "U"), (1, -2, "e"), (2, -2, "O"), (-1, -1, "U"), (0, -1, "U"), (1, -1, "U")):
        cv.put(column + dx, top + dy, c)


def _draw_roots(cv: Canvas, level: int, left: int, width: int) -> None:
    """땅을 따라 넓게 퍼지는 뿌리."""
    spread = 2 + (level - 70) // 4
    for i in range(spread):
        cv.put(left - 1 - i, GRID_H - 1, "b")
        cv.put(left + width + i, GRID_H - 1, "b")
        if i < spread // 2:
            cv.put(left - 1 - i, GRID_H - 2, "B")
            cv.put(left + width + i, GRID_H - 2, "b")
    cv.put(left - 1, GRID_H - 3, "B")
    cv.put(left + width, GRID_H - 3, "b")


def _draw_vines(cv: Canvas, level: int) -> None:
    """잎 덩어리 아래로 늘어진 덩굴."""
    edges = [(x, y) for x, y in _cells(cv, LEAF) if cv.get(x, y + 1) == " " and abs(x + 0.5 - CENTER) > 5]
    edges.sort(key=lambda p: _noise(p[0], p[1], level * 17))
    used: list[int] = []
    for x, y in edges:
        if len(used) >= 2 + (level - 80) // 3:
            break
        if any(abs(x - u) < 3 for u in used):
            continue
        length = 2 + int(_noise(x, y, level) * 4)
        for i in range(1, length + 1):
            cv.put(x, y + i, "D" if i % 2 else "G")
        cv.put(x, y + length + 1, "L")
        used.append(x)


def _draw_moss(cv: Canvas, level: int, left: int, top: int, width: int) -> None:
    for i in range(1 + (level - 80) // 4):
        x = left + int(_noise(i, 11, level) * width)
        y = top + 4 + int(_noise(i, 9, level) * 2)
        if cv.get(x, y) in "Bb":
            cv.put(x, y, "G" if i % 2 else "D")


def _draw_little_sprouts(cv: Canvas, level: int, left: int, width: int) -> None:
    count = 1 + (level - 90) // 4
    for x in [left - 7, left + width + 5, left - 11, left + width + 9][:count]:
        cv.put(x, GRID_H - 1, "K")
        cv.put(x, GRID_H - 2, "K")
        cv.put(x - 1, GRID_H - 3, "L")
        cv.put(x + 1, GRID_H - 3, "M")


def _draw_seed_of_light(cv: Canvas) -> None:
    """Lv.100: 꼭대기 위에 떠 있는 빛의 씨앗."""
    top = next(y for y in range(GRID_H) if any(cv.get(x, y) != " " for x in range(GRID_W)))
    cx, cy = int(CENTER), top - 4
    for dx, dy, c in ((0, -2, "Y"), (-1, -1, "Y"), (0, -1, "W"), (1, -1, "Y"), (-2, 0, "Y"), (-1, 0, "W"),
                      (0, 0, "W"), (1, 0, "W"), (2, 0, "Y"), (-1, 1, "Y"), (0, 1, "W"), (1, 1, "Y"), (0, 2, "Y")):
        cv.put(cx + dx, cy + dy, c)


def sprite_for(level: int) -> tuple[str, ...]:
    cv = Canvas()
    left, top, width = _draw_body(cv, level)
    if level < 20:
        _draw_sprout(cv, level, top)
        return cv.rows()
    trunk_top = _draw_trunk(cv, level, top)
    r = _draw_canopy(cv, level, trunk_top)
    if 30 <= level < 70:
        _draw_branches(cv, level, trunk_top, r)
    if level >= 80:
        _draw_vines(cv, level)
    if level >= 40:
        def flower(x: int, y: int) -> None:
            cv.put(x, y, "P")
            for dx, dy in ((1, 0), (-1, 0), (0, -1)):
                if cv.get(x + dx, y + dy) in "LGD":
                    cv.put(x + dx, y + dy, "W")
        _scatter(cv, level, 1, 2 + (level - 40) // 6, "LG", flower)
    if level >= 50:
        fruit = "Y" if level == MAX_LEVEL else "O"
        _scatter(cv, level, 2, 2 + (level - 50) // 5, "GD", lambda x, y: cv.put(x, y, fruit))
    if level >= 90:
        _scatter(cv, level, 3, 3 + (level - 90), "GD", lambda x, y: cv.put(x, y, "M"))
    if level >= 60:
        _draw_bird(cv, level)
    if level >= 70:
        _draw_roots(cv, level, left, width)
    if level >= 80:
        _draw_moss(cv, level, left, top, width)
    if level >= 90:
        _draw_little_sprouts(cv, level, left, width)
    if level == MAX_LEVEL:
        _draw_seed_of_light(cv)
    return cv.rows()


# ---------- SVG ----------

def sprite_rects(sprite: tuple[str, ...], pixel: float, keep=lambda c: True) -> str:
    """같은 색이 가로로 이어진 칸은 하나의 사각형으로 합쳐 파일을 가볍게 만듭니다."""
    rects = []
    for y, row in enumerate(sprite):
        x = 0
        while x < len(row):
            c = row[x]
            run = 1
            while x + run < len(row) and row[x + run] == c:
                run += 1
            if c in COLORS and keep(c):
                rects.append(
                    f'<rect x="{x * pixel:g}" y="{y * pixel:g}" width="{run * pixel:g}" height="{pixel:g}" fill="{COLORS[c]}"/>'
                )
            x += run
    return "".join(rects)


def _canopy_box(sprite: tuple[str, ...]) -> tuple[float, float, float] | None:
    cells = [(x, y) for y, row in enumerate(sprite) for x, c in enumerate(row) if c in LEAF]
    if not cells:
        return None
    xs, ys = [x for x, _ in cells], [y for _, y in cells]
    return (min(xs) + max(xs) + 1) / 2, (min(ys) + max(ys) + 1) / 2, max(max(xs) - min(xs), max(ys) - min(ys)) / 2


def render_effects(level: int, sprite: tuple[str, ...], pixel: float, uid: str) -> tuple[str, str]:
    """세계수 빛 연출. (그림 뒤 후광, 그림 앞 빛 입자)를 돌려줍니다."""
    box = _canopy_box(sprite)
    if box is None or level < 50:
        return "", ""
    cx, cy, radius = box[0] * pixel, box[1] * pixel, box[2] * pixel
    behind = front = ""
    if level >= 75:
        color = "#F2C14E" if level == MAX_LEVEL else "#C7F9CC"
        opacity = 0.35 + 0.5 * (level - 75) / 25
        behind += (
            f'<defs><radialGradient id="halo-{uid}"><stop offset="0" stop-color="{color}" stop-opacity="{opacity:.2f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<circle class="glow" cx="{cx:g}" cy="{cy:g}" r="{radius * 1.45:g}" fill="url(#halo-{uid})"/>'
        )
    if level == MAX_LEVEL:
        top = next(y for y, row in enumerate(sprite) if row.strip()) + 2
        ox, oy = (int(CENTER) + 0.5) * pixel, (top + 0.5) * pixel
        rays = "".join(
            f'<polygon points="{ox:g},{oy:g} {ox + math.cos(a - 0.06) * radius * 0.85:g},{oy + math.sin(a - 0.06) * radius * 0.85:g} '
            f'{ox + math.cos(a + 0.06) * radius * 0.85:g},{oy + math.sin(a + 0.06) * radius * 0.85:g}"/>'
            for a in (i * math.pi / 6 for i in range(12))
        )
        behind += f'<g class="rays" fill="#F2C14E" opacity="0.18" style="transform-origin:{ox:g}px {oy:g}px">{rays}</g>'
    count = min(14, 2 + (level - 50) // 4)
    dots = []
    for i in range(count):
        x = cx + (_noise(i, 1, level) - 0.5) * radius * 1.8
        y = cy + (_noise(i, 2, level) - 0.3) * radius * 1.2
        color = "#F2C14E" if level == MAX_LEVEL or i % 2 else "#C7F9CC"
        size = pixel * (0.8 if i % 3 else 1.2)
        dots.append(
            f'<rect class="spark" x="{x:.1f}" y="{y:.1f}" width="{size:g}" height="{size:g}" fill="{color}" '
            f'style="animation-delay:-{_noise(i, 3, level) * 5:.1f}s;animation-duration:{4 + _noise(i, 4, level) * 3:.1f}s"/>'
        )
    front = "".join(dots)
    return behind, front


FONT = "Pretendard, Apple SD Gothic Neo, Noto Sans KR, sans-serif"


def _background(level: int) -> tuple[str, dict]:
    if level == MAX_LEVEL:
        stars = "".join(
            f'<rect x="{40 + _noise(i, 5, 7) * 1120:.0f}" y="{20 + _noise(i, 6, 7) * 200:.0f}" width="3" height="3" fill="#FAF9F6" opacity="{0.4 + 0.6 * _noise(i, 8, 7):.2f}"/>'
            for i in range(40)
        )
        bg = (
            '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14292A"/>'
            '<stop offset="1" stop-color="#2D5A4F"/></linearGradient></defs>'
            f'<rect width="1200" height="320" rx="28" fill="url(#sky)"/>{stars}'
            '<circle cx="1110" cy="70" r="36" fill="#F2C14E" opacity="0.9"/>'
            '<path d="M0 292c180-22 320 18 520 2s380 14 680 0v26H0z" fill="#40916C"/>'
        )
        return bg, {"title": "#FAF9F6", "name": "#F2C14E", "track": "#31572C", "bar": "#F2C14E", "line": "#C7F9CC", "sub": "#90A955"}
    if level >= 80:
        bg = (
            '<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E3F2E6"/>'
            '<stop offset="1" stop-color="#FAF9F6"/></linearGradient></defs>'
            '<rect width="1200" height="320" rx="28" fill="url(#sky)"/>'
            '<circle cx="1110" cy="70" r="40" fill="#ECF39E"/>'
            '<path d="M0 292c180-22 320 18 520 2s380 14 680 0v26H0z" fill="#90A955"/>'
        )
    else:
        bg = (
            '<rect width="1200" height="320" rx="28" fill="#FAF9F6"/>'
            '<circle cx="1110" cy="70" r="40" fill="#ECF39E"/>'
            '<path d="M0 292c180-22 320 18 520 2s380 14 680 0v26H0z" fill="#90A955"/>'
        )
    return bg, {"title": "#31572C", "name": "#31572C", "track": "#ECF39E", "bar": "#40916C", "line": "#40916C", "sub": "#90A955"}


def _fmt(value) -> str:
    return f"{value:,}" if isinstance(value, int) else "확인 전"


def render_current_svg(state: dict) -> str:
    level = level_for_score(state["score"])
    upcoming = next_level(level)
    sprite = sprite_for(level.level)
    used = [y for y, row in enumerate(sprite) if row.strip()]
    # 작은 레벨도 잘 보이도록 실제 그림 높이에 맞춰 픽셀 크기를 정합니다.
    pixel = max(4, min(10, 270 // (GRID_H - used[0])))
    sprite_w, sprite_h = GRID_W * pixel, GRID_H * pixel
    sx, sy = 300 - sprite_w // 2, 300 - sprite_h + pixel // 2
    if upcoming:
        span = upcoming.threshold - level.threshold
        progress = min(1.0, (state["score"] - level.threshold) / span)
        goal = f"Lv.{upcoming.level}까지 {upcoming.threshold - state['score']:,}점"
    else:
        progress = 1.0
        goal = "가장 높은 레벨에 닿았어요"
    bg, ink = _background(level.level)
    behind, front = render_effects(level.level, sprite, pixel, "main")
    work = state.get("work", {})
    bar_w = 520
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc">
  <title id="title">자라는 새록이</title>
  <desc id="desc">새록이가 Lv.{level.level} {level.name}까지 자랐습니다. 성장 점수 {state['score']}점.</desc>
  <style>
    #sway {{ animation: sway 3.2s ease-in-out infinite; transform-origin: {sprite_w // 2}px {sprite_h}px; }}
    #eyes {{ animation: blink 4s infinite; transform-box: fill-box; transform-origin: center; }}
    .glow {{ animation: glow 4s ease-in-out infinite; }}
    .rays {{ animation: spin 40s linear infinite; }}
    .spark {{ animation-name: rise; animation-iteration-count: infinite; animation-timing-function: ease-in-out; opacity: 0; }}
    @keyframes sway {{ 0%, 100% {{ transform: rotate(-1.2deg); }} 50% {{ transform: rotate(1.2deg); }} }}
    @keyframes blink {{ 0%, 92%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(0.1); }} }}
    @keyframes glow {{ 0%, 100% {{ opacity: 0.75; }} 50% {{ opacity: 1; }} }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes rise {{ 0% {{ transform: translateY(0); opacity: 0; }} 30% {{ opacity: 1; }} 100% {{ transform: translateY(-36px); opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ #sway, #eyes, .glow, .rays {{ animation: none; }} .spark {{ animation: none; opacity: 0.8; }} }}
  </style>
  {bg}
  <g transform="translate({sx} {sy})">
    {behind}
    <g id="sway" shape-rendering="crispEdges">
      {sprite_rects(sprite, pixel, lambda c: c != "E")}
      <g id="eyes">{sprite_rects(sprite, pixel, lambda c: c == "E")}</g>
    </g>
    {front}
  </g>
  <text x="520" y="88" fill="{ink['title']}" font-size="22" font-weight="700" font-family="{FONT}">새록이 Lv.{level.level} / {MAX_LEVEL}</text>
  <text x="520" y="148" fill="{ink['name']}" font-size="54" font-weight="800" font-family="{FONT}">{level.name}</text>
  <rect x="520" y="176" width="{bar_w}" height="18" rx="9" fill="{ink['track']}"/>
  <rect x="520" y="176" width="{max(18, round(bar_w * progress))}" height="18" rx="9" fill="{ink['bar']}"/>
  <text x="520" y="228" fill="{ink['line']}" font-size="20" font-weight="600" font-family="{FONT}">성장 점수 {state['score']:,}점 · {goal}</text>
  <text x="520" y="260" fill="{ink['sub']}" font-size="17" font-weight="500" font-family="{FONT}">순방문자 {_fmt(state.get('visitors_total'))} · 스타 {_fmt(state.get('stars'))} · 작업량 {_fmt(work.get('points'))} · {state['updated_at'][:10]} 기준</text>
</svg>
"""


HERO_W, HERO_H = 1200, 360
HERO_BLOCK = 8  # 배너 배경 픽셀 한 칸 크기
HERO_GROWTH = ((1, 7, 560), (40, 5.5, 730), (100, 4.5, 940))  # (레벨, 픽셀 크기, 왼쪽 x)


def _hero_ground(x: int) -> int:
    """배너 오른쪽으로 갈수록 살짝 올라가는 언덕의 높이(y)를 8px 계단으로 돌려줍니다."""
    y = 318 - 22 * math.sin(x / 260) - 10 * math.sin(x / 90 + 1) - (x / HERO_W) * 18
    return int(y // HERO_BLOCK * HERO_BLOCK)


def render_hero_svg() -> str:
    """README 맨 위 배너. 캐릭터와 같은 픽셀 그림으로 새싹에서 세계수까지 자라는 모습을 보여 줍니다."""
    b = HERO_BLOCK
    stars = "".join(
        f'<rect class="twinkle" x="{int(_noise(i, 1, 3) * 1180) // b * b}" y="{int(_noise(i, 2, 3) * 200) // b * b}" '
        f'width="{b // 2 if i % 3 else b}" height="{b // 2 if i % 3 else b}" fill="#ECF39E" '
        f'style="animation-delay:-{_noise(i, 4, 3) * 4:.1f}s"/>'
        for i in range(28)
    )
    moon = "".join(
        f'<rect x="{560 + dx * b}" y="{32 + dy * b}" width="{b}" height="{b}" fill="{"#ECF39E" if dx + dy < 7 else "#90A955"}"/>'
        for dy in range(9) for dx in range(9)
        if (dx - 4) ** 2 + (dy - 4) ** 2 <= 17
    )
    far = "".join(
        f'<rect x="{x}" y="{_hero_ground(x) - 26}" width="{b}" height="{HERO_H}" fill="#40916C"/>'
        for x in range(0, HERO_W, b)
    )
    near = "".join(
        f'<rect x="{x}" y="{_hero_ground(x + 400) + 8}" width="{b}" height="{HERO_H}" fill="#90A955"/>'
        for x in range(0, HERO_W, b)
    )
    grass = "".join(
        f'<rect x="{x}" y="{_hero_ground(x + 400) + 4}" width="{b // 2}" height="{b // 2}" fill="#ECF39E"/>'
        for x in range(0, HERO_W, b * 3) if _noise(x, 9, 3) > 0.45
    )
    trees, arrows = [], []
    for i, (level, pixel, left) in enumerate(HERO_GROWTH):
        sprite = sprite_for(level)
        behind, front = render_effects(level, sprite, pixel, f"hero{level}")
        center = left + GRID_W * pixel / 2
        ground = _hero_ground(int(center) + 400) + 8
        top = ground - GRID_H * pixel + pixel
        trees.append(
            f'<g transform="translate({left:g} {top:g})">{behind}'
            f'<g shape-rendering="crispEdges">{sprite_rects(sprite, pixel)}</g>{front}</g>'
        )
        if i:
            ax = left - 18
            ay = ground - 40
            arrows.append(
                "".join(f'<rect x="{ax + k * b}" y="{ay}" width="{b // 2}" height="{b // 2}" fill="#ECF39E" opacity="0.7"/>' for k in range(3))
            )
    shadow = "#1F2A1F"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {HERO_W} {HERO_H}" role="img" aria-labelledby="title desc">
  <title id="title">새록이</title>
  <desc id="desc">새로운 발견의 새, 기록의 록. 쓸수록 자라는 나만의 AI 에이전트 나무. 새싹에서 세계수까지 자라는 픽셀 새록이.</desc>
  <style>
    .twinkle {{ animation: twinkle 3.5s ease-in-out infinite; }}
    .glow {{ animation: glow 4s ease-in-out infinite; }}
    .rays {{ animation: spin 40s linear infinite; }}
    .spark {{ animation-name: rise; animation-iteration-count: infinite; animation-timing-function: ease-in-out; opacity: 0; }}
    @keyframes twinkle {{ 0%, 100% {{ opacity: 0.25; }} 50% {{ opacity: 1; }} }}
    @keyframes glow {{ 0%, 100% {{ opacity: 0.75; }} 50% {{ opacity: 1; }} }}
    @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    @keyframes rise {{ 0% {{ transform: translateY(0); opacity: 0; }} 30% {{ opacity: 1; }} 100% {{ transform: translateY(-36px); opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .twinkle, .glow, .rays {{ animation: none; }} .twinkle {{ opacity: 0.7; }} .spark {{ animation: none; opacity: 0.8; }} }}
  </style>
  <clipPath id="frame"><rect width="{HERO_W}" height="{HERO_H}" rx="28"/></clipPath>
  <g clip-path="url(#frame)">
    <rect width="{HERO_W}" height="{HERO_H}" fill="#31572C"/>
    <g shape-rendering="crispEdges">{stars}{moon}{far}{near}{grass}{''.join(arrows)}</g>
    {''.join(trees)}
  </g>
  <g font-family="{FONT}">
    <text x="86" y="152" fill="{shadow}" font-size="80" font-weight="800">새록이</text>
    <text x="80" y="146" fill="#FAF9F6" font-size="80" font-weight="800">새록이</text>
    <text x="84" y="204" fill="{shadow}" font-size="27" font-weight="700">새로운 발견의 새, 기록의 록</text>
    <text x="82" y="202" fill="#ECF39E" font-size="27" font-weight="700">새로운 발견의 새, 기록의 록</text>
    <text x="82" y="250" fill="#FAF9F6" font-size="24" font-weight="600">쓸수록 자라는 나만의 AI 에이전트 나무</text>
  </g>
</svg>
"""


MILESTONES = (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)


def render_stages_svg() -> str:
    pixel = 3.5
    sprite_w, sprite_h = GRID_W * pixel, GRID_H * pixel
    cell_w, cell_h = 190, sprite_h + 64
    per_row = 6
    parts = []
    for i, n in enumerate(MILESTONES):
        row, col = divmod(i, per_row)
        in_row = min(per_row, len(MILESTONES) - row * per_row)
        x = (1180 - in_row * cell_w) / 2 + col * cell_w + (cell_w - sprite_w) / 2
        y = 16 + row * (cell_h + 30)
        level = LEVELS[n - 1]
        sprite = sprite_for(n)
        behind, front = render_effects(n, sprite, pixel, f"m{n}")
        mid = x + sprite_w / 2
        parts.append(
            f'<g transform="translate({x:g} {y:g})">{behind}<g shape-rendering="crispEdges">{sprite_rects(sprite, pixel)}</g>{front}</g>'
            f'<text x="{mid:g}" y="{y + sprite_h + 26:g}" text-anchor="middle" fill="#31572C" '
            f'font-size="16" font-weight="700" font-family="{FONT}">Lv.{n} {level.name}</text>'
            f'<text x="{mid:g}" y="{y + sprite_h + 48:g}" text-anchor="middle" fill="#90A955" '
            f'font-size="14" font-family="{FONT}">{level.threshold:,}점부터</text>'
        )
    height = 46 + 2 * cell_h
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 {height:g}" role="img" aria-labelledby="title desc">
  <title id="title">새록이 성장 단계</title>
  <desc id="desc">새싹에서 세계수까지 100레벨로 자라는 새록이의 10레벨마다 모습</desc>
  <rect width="1180" height="{height:g}" rx="28" fill="#FAF9F6"/>
  {''.join(parts)}
</svg>
"""


def render_all_levels_svg() -> str:
    pixel, per_row = 3, 10
    cell_w, cell_h = GRID_W * pixel + 10, GRID_H * pixel + 26
    parts = []
    for n in range(1, MAX_LEVEL + 1):
        row, col = divmod(n - 1, per_row)
        x, y = 10 + col * cell_w, 10 + row * cell_h
        sprite = sprite_for(n)
        behind, front = render_effects(n, sprite, pixel, f"a{n}")
        parts.append(
            f'<g transform="translate({x} {y})">{behind}<g shape-rendering="crispEdges">{sprite_rects(sprite, pixel)}</g>{front}</g>'
            f'<text x="{x + GRID_W * pixel / 2}" y="{y + GRID_H * pixel + 16}" text-anchor="middle" '
            f'font-size="12" fill="#31572C" font-family="{FONT}">Lv.{n}</text>'
        )
    w, h = 20 + per_row * cell_w, 20 + 10 * cell_h
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#FAF9F6"/>'
            f'{"".join(parts)}</svg>')


# ---------- 점수 계산 ----------

def merge_visitors(state: dict, payload: dict) -> dict:
    """traffic API 응답의 날짜별 순방문자를 기존 기록에 덮어써 14일이 지나도 누적되게 합니다."""
    by_day = dict(state.get("visitors_by_day", {}))
    for item in payload.get("views", []):
        by_day[item["timestamp"][:10]] = int(item["uniques"])
    merged = dict(state)
    merged["visitors_by_day"] = dict(sorted(by_day.items()))
    merged["visitors_total"] = sum(by_day.values())
    return merged


def work_points(commits: list[dict]) -> dict:
    """commits: [{"author", "date", "lines"}]. 봇 커밋은 세지 않습니다."""
    human = [c for c in commits if c["author"] not in BOT_AUTHORS]
    size = sum(min(MAX_SIZE_POINTS, c["lines"] // LINES_PER_POINT) for c in human)
    days = len({c["date"] for c in human})
    return {"commits": len(human), "active_days": days, "points": len(human) + size + DAY_POINTS * days}


def compute_score(state: dict) -> int:
    def known(value) -> int:
        return value if isinstance(value, int) else 0

    work = state.get("work", {})
    return known(state.get("visitors_total")) + STAR_POINTS * known(state.get("stars")) + known(work.get("points"))


def read_commits() -> list[dict]:
    log = subprocess.run(
        ["git", "log", "--no-merges", "--format=@%an|%ad", "--date=short", "--numstat"],
        capture_output=True, text=True, encoding="utf-8", check=True,
    ).stdout
    commits: list[dict] = []
    for line in log.splitlines():
        if line.startswith("@"):
            author, date = line[1:].split("|", 1)
            commits.append({"author": author, "date": date, "lines": 0})
        elif line.strip() and commits:
            added, deleted, path = line.split("\t", 2)
            if added == "-" or path.startswith(IGNORED_PATHS):
                continue
            commits[-1]["lines"] += int(added) + int(deleted)
    return commits


def _get_json(url: str, token: str | None):
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as response:
        return json.load(response)


def fetch_traffic(repo: str, token: str) -> dict:
    return _get_json(f"https://api.github.com/repos/{repo}/traffic/views", token)


def fetch_stars(repo: str, token: str | None) -> int:
    """저장소 주인이 누른 스타는 빼고 셉니다."""
    owner = repo.split("/")[0].lower()
    total, page = 0, 1
    while True:
        users = _get_json(f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page={page}", token)
        total += sum(1 for user in users if user["login"].lower() != owner)
        if len(users) < 100:
            return total
        page += 1


def update(state_path: Path, assets_dir: Path, repo: str | None, traffic_token: str | None, api_token: str | None) -> dict:
    old = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state = {k: v for k, v in old.items() if k in ("visitors_by_day", "visitors_total", "stars")}
    errors = []
    if repo and traffic_token:
        try:
            state = merge_visitors(state, fetch_traffic(repo, traffic_token))
        except Exception as error:  # 실패를 0으로 바꾸지 않고 기존 기록을 유지합니다.
            errors.append(f"traffic: {error}")
    state.setdefault("visitors_total", None)
    if repo:
        try:
            state["stars"] = fetch_stars(repo, api_token)
        except Exception as error:
            errors.append(f"stars: {error}")
    state.setdefault("stars", None)
    state["work"] = work_points(read_commits())
    state["score"] = compute_score(state)
    level = level_for_score(state["score"])
    state["stage"] = {"level": level.level, "name": level.name}
    if errors:
        state["last_error"] = "; ".join(errors)

    # 점수와 기록이 그대로면 갱신 시각도 그대로 두어 봇 커밋이 매일 생기지 않게 합니다.
    # 그림은 그리는 방식이 바뀌었을 수 있으니 항상 다시 그립니다(내용이 같으면 git 변경도 없습니다).
    if {k: v for k, v in old.items() if k != "updated_at"} == state and "updated_at" in old:
        state = old
    else:
        state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (assets_dir / "saeroki-tree.svg").write_text(render_current_svg(state), encoding="utf-8")
    (assets_dir / "saeroki-stages.svg").write_text(render_stages_svg(), encoding="utf-8")
    (assets_dir / "saeroki-hero.svg").write_text(render_hero_svg(), encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="새록이 묘목 성장 상태를 갱신합니다.")
    parser.add_argument("--state", default="data/growth.json")
    parser.add_argument("--assets", default="assets")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--preview", type=Path, help="1~100레벨 전체 모습을 담은 미리보기 SVG를 이 경로에 저장")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if args.preview:
        args.preview.write_text(render_all_levels_svg(), encoding="utf-8")
        print(f"saved {args.preview}")
        return
    state = update(
        Path(args.state), Path(args.assets), args.repo,
        os.environ.get("TRAFFIC_TOKEN"), os.environ.get("GITHUB_TOKEN"),
    )
    print(json.dumps({k: v for k, v in state.items() if k != "visitors_by_day"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
