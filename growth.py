"""새록이 묘목 성장 상태를 계산하고 픽셀 아트 SVG로 그립니다.

성장 점수 = 누적 README(저장소) 조회수 + 커밋 수
조회수는 GitHub traffic API가 최근 14일만 돌려주므로 날짜별로 data/growth.json에 쌓아 둡니다.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

PIXEL = 10
GRID_W = 26
GRID_H = 30

COLORS = {
    "L": "#ECF39E",  # 연두 잎
    "G": "#90A955",  # 잎
    "D": "#40916C",  # 짙은 잎
    "K": "#31572C",  # 가장 짙은 잎, 줄기
    "B": "#B07A4F",  # 몸통(나무껍질)
    "b": "#8A5A36",  # 몸통 그림자, 뿌리 발
    "E": "#1F2A1F",  # 눈
    "O": "#D97757",  # 열매(클로드 주황)
    "W": "#FAF9F6",  # 꽃
}


@dataclass(frozen=True)
class Stage:
    level: int
    name: str
    threshold: int
    sprite: tuple[str, ...]


def _body(width: int, height: int, arms: bool = True) -> list[str]:
    """클로드 캐릭터처럼 네모난 몸통, 세로 눈, 양팔과 네 다리를 가진 몸을 만듭니다."""
    pad = (GRID_W - width) // 2
    rows = []
    eye_left = pad + width // 2 - 3
    eye_right = pad + width // 2 + 2
    for y in range(height):
        row = [" "] * GRID_W
        for x in range(pad, pad + width):
            row[x] = "b" if x == pad + width - 1 else "B"
        if 1 <= y <= 2:
            row[eye_left] = "E"
            row[eye_right] = "E"
        if arms and y == 3:
            row[pad - 1] = "B"
            row[pad + width] = "b"
        rows.append("".join(row))
    legs = [" "] * GRID_W
    for x in (pad, pad + 2, pad + width - 3, pad + width - 1):
        legs[x] = "b"
    rows.append("".join(legs))
    return rows


def _center(lines: list[str]) -> list[str]:
    return [line.center(GRID_W) for line in lines]


SPROUT = _center([
    "LG    GL",
    "LGG  GGL",
    " GGKKGG ",
    "   KK   ",
])

SAPLING = _center([
    "   LG   ",
    "  LGGD  ",
    "   GKD  ",
    "LG  K GD",
    "LGG K GGD",
    " GDDKDDG",
    "    K   ",
])

YOUNG_TREE = _center([
    "   LLGGG  ",
    "  LLGGGGD ",
    " LLGGGGGDD",
    " LGGGGDGGD",
    " GGGGDDGDD",
    "  GGDDDDD ",
    "   DDKKD  ",
    "     KK   ",
])

TREE = _center([
    "     LLGGGG     ",
    "   LLLGGGGGDD   ",
    "  LLGGGGGGGGDD  ",
    " LLGGGGGGGGGGDD ",
    " LGGGGGDDGGGGDD ",
    " GGGGGDDDDGGDDD ",
    "  GGDDDDDDDDDD  ",
    "   DDDDKKDDDD   ",
    "      KKKK      ",
    "       BB       ",
])

GREAT_TREE = _center([
    "       LLLLGGGG       ",
    "     LLLGGGGGOGGD     ",
    "   LLLGGGGGGGGGGGDD   ",
    "  LLGGWGGGGGGGGOGGDD  ",
    " LLGGGGGGGGGGGGGGGDDD ",
    " LGGGGGGOGGDDGGGGWDDD ",
    " LGGWGGGGGDDDDGGGDDDD ",
    " GGGGGGDDDDDDDDOGDDDD ",
    "  GGOGDDDDDDDDDDDDDD  ",
    "   DDDDDDDKKDDDWDDD   ",
    "     DDDDKKKKDDDD     ",
    "         KBBK         ",
    "          BB          ",
])


def _stack(crown: list[str], body: list[str]) -> tuple[str, ...]:
    sprite = crown + body
    return tuple([" " * GRID_W] * (GRID_H - len(sprite)) + sprite)


STAGES = (
    Stage(1, "새싹", 0, _stack(SPROUT, _body(8, 5))),
    Stage(2, "묘목", 30, _stack(SAPLING, _body(8, 6))),
    Stage(3, "어린 나무", 100, _stack(YOUNG_TREE, _body(8, 7))),
    Stage(4, "나무", 300, _stack(TREE, _body(10, 8))),
    Stage(5, "큰 나무", 1000, _stack(GREAT_TREE, _body(10, 9))),
)


def stage_for_score(score: int) -> Stage:
    current = STAGES[0]
    for stage in STAGES:
        if score >= stage.threshold:
            current = stage
    return current


def next_stage(stage: Stage) -> Stage | None:
    return STAGES[stage.level] if stage.level < len(STAGES) else None


def sprite_rects(sprite: tuple[str, ...], x0: int = 0, y0: int = 0) -> str:
    rects = []
    for y, row in enumerate(sprite):
        for x, cell in enumerate(row):
            if cell in COLORS:
                rects.append(
                    f'<rect x="{x0 + x * PIXEL}" y="{y0 + y * PIXEL}" width="{PIXEL}" height="{PIXEL}" fill="{COLORS[cell]}"/>'
                )
    return "".join(rects)


def _eyes_only(sprite: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("".join(c if c == "E" else " " for c in row) for row in sprite)


def _without_eyes(sprite: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(row.replace("E", "B") for row in sprite)


FONT = "Pretendard, Apple SD Gothic Neo, Noto Sans KR, sans-serif"


def render_current_svg(state: dict) -> str:
    stage = stage_for_score(state["score"])
    upcoming = next_stage(stage)
    sprite_w = GRID_W * PIXEL
    sprite_h = GRID_H * PIXEL
    sx, sy = 150, 10
    if upcoming:
        span = upcoming.threshold - stage.threshold
        progress = min(1.0, (state["score"] - stage.threshold) / span)
        goal = f"다음 단계 {upcoming.name}까지 {upcoming.threshold - state['score']}점"
    else:
        progress = 1.0
        goal = "가장 큰 나무로 자랐어요"
    views = state.get("views_total")
    views_text = f"{views:,}" if isinstance(views, int) else "확인 전"
    bar_w = 520
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc">
  <title id="title">자라는 새록이</title>
  <desc id="desc">새록이 묘목이 {stage.level}단계 {stage.name}까지 자랐습니다. 성장 점수 {state['score']}점.</desc>
  <style>
    #sway {{ animation: sway 3.2s ease-in-out infinite; transform-origin: {sx + sprite_w // 2}px {sy + sprite_h}px; }}
    #eyes {{ animation: blink 4s infinite; transform-box: fill-box; transform-origin: center; }}
    @keyframes sway {{ 0%, 100% {{ transform: rotate(-1.5deg); }} 50% {{ transform: rotate(1.5deg); }} }}
    @keyframes blink {{ 0%, 92%, 100% {{ transform: scaleY(1); }} 95% {{ transform: scaleY(0.1); }} }}
    @media (prefers-reduced-motion: reduce) {{ #sway, #eyes {{ animation: none; }} }}
  </style>
  <rect width="1200" height="320" rx="28" fill="#FAF9F6"/>
  <circle cx="1110" cy="70" r="40" fill="#ECF39E"/>
  <path d="M0 292c180-22 320 18 520 2s380 14 680 0v26H0z" fill="#90A955"/>
  <g id="sway" shape-rendering="crispEdges">
    {sprite_rects(_without_eyes(stage.sprite), sx, sy)}
    <g id="eyes">{sprite_rects(_eyes_only(stage.sprite), sx, sy)}</g>
  </g>
  <text x="520" y="88" fill="#31572C" font-size="22" font-weight="700" font-family="{FONT}">새록이 성장 {stage.level} / {len(STAGES)}단계</text>
  <text x="520" y="148" fill="#31572C" font-size="54" font-weight="800" font-family="{FONT}">{stage.name}</text>
  <rect x="520" y="176" width="{bar_w}" height="18" rx="9" fill="#ECF39E"/>
  <rect x="520" y="176" width="{max(18, round(bar_w * progress))}" height="18" rx="9" fill="#40916C"/>
  <text x="520" y="228" fill="#40916C" font-size="20" font-weight="600" font-family="{FONT}">성장 점수 {state['score']:,}점 · {goal}</text>
  <text x="520" y="260" fill="#90A955" font-size="17" font-weight="500" font-family="{FONT}">누적 조회 {views_text} · 커밋 {state['commits']:,} · {state['updated_at'][:10]} 기준</text>
</svg>
"""


def render_stages_svg() -> str:
    gap = 230
    scale = 0.8
    parts = []
    for i, stage in enumerate(STAGES):
        x = 20 + i * gap
        parts.append(
            f'<g transform="translate({x} 10) scale({scale})">{sprite_rects(stage.sprite)}</g>'
            f'<text x="{x + GRID_W * PIXEL * scale / 2}" y="290" text-anchor="middle" fill="#31572C" '
            f'font-size="20" font-weight="700" font-family="{FONT}">{stage.level}. {stage.name}</text>'
            f'<text x="{x + GRID_W * PIXEL * scale / 2}" y="314" text-anchor="middle" fill="#90A955" '
            f'font-size="15" font-family="{FONT}">{stage.threshold:,}점부터</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 330" role="img" aria-labelledby="title desc">
  <title id="title">새록이 성장 단계</title>
  <desc id="desc">새싹, 묘목, 어린 나무, 나무, 큰 나무 다섯 단계로 자라는 새록이</desc>
  <rect width="1180" height="330" rx="28" fill="#FAF9F6"/>
  <g shape-rendering="crispEdges">{''.join(parts)}</g>
</svg>
"""


def merge_views(state: dict, payload: dict) -> dict:
    """traffic API 응답의 날짜별 조회수를 기존 기록에 덮어써 누적합니다."""
    by_day = dict(state.get("views_by_day", {}))
    for item in payload.get("views", []):
        by_day[item["timestamp"][:10]] = int(item["count"])
    merged = dict(state)
    merged["views_by_day"] = dict(sorted(by_day.items()))
    merged["views_total"] = sum(by_day.values())
    return merged


def compute_score(state: dict) -> int:
    views = state.get("views_total")
    return (views if isinstance(views, int) else 0) + int(state.get("commits", 0))


def fetch_traffic(repo: str, token: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/traffic/views",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def count_commits() -> int:
    result = subprocess.run(["git", "rev-list", "--count", "HEAD"], capture_output=True, text=True, check=True)
    return int(result.stdout.strip())


def update(state_path: Path, assets_dir: Path, repo: str | None, token: str | None) -> dict:
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    state.pop("last_error", None)
    if repo and token:
        try:
            state = merge_views(state, fetch_traffic(repo, token))
        except Exception as error:  # 실패를 0으로 바꾸지 않고 기존 기록을 유지합니다.
            state["last_error"] = f"traffic: {error}"
    elif "views_total" not in state:
        state["views_total"] = None
    state["commits"] = count_commits()
    state["score"] = compute_score(state)
    stage = stage_for_score(state["score"])
    state["stage"] = {"level": stage.level, "name": stage.name}
    state["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (assets_dir / "saeroki-tree.svg").write_text(render_current_svg(state), encoding="utf-8")
    (assets_dir / "saeroki-stages.svg").write_text(render_stages_svg(), encoding="utf-8")
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description="새록이 묘목 성장 상태를 갱신합니다.")
    parser.add_argument("--state", default="data/growth.json")
    parser.add_argument("--assets", default="assets")
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    state = update(Path(args.state), Path(args.assets), args.repo, os.environ.get("TRAFFIC_TOKEN"))
    print(json.dumps({k: v for k, v in state.items() if k != "views_by_day"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
