"""사용: saerok-idea new --line "아이디어 한 줄" [--what ..] [--who ..] [--money ..] [--why-now ..]
      saerok-idea new --from <verdict.md> [--direction 2]
      saerok-idea record <기록 폴더> judge|assumptions|competitors|panel|money|directions --file 결과.json
      saerok-idea decide <기록 폴더>
      saerok-idea report <기록 폴더>
      saerok-idea compare <아이디어 폴더 또는 기록 폴더> [--json]
      saerok-idea breakeven --price 9900 --unit-cost 1500 --fixed-cost 300000
      saerok-idea rubric | home"""

import argparse
import json
import sys
from pathlib import Path

from . import money, rubric, store


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-idea", description="새록 심사단: 아이디어 심사 결과를 검증·판정·기록합니다.")
    sub = parser.add_subparsers(dest="command", required=True)

    n = sub.add_parser("new", help="기록 폴더(~/.saerok/idea/<아이디어>/<날짜>/)를 만듭니다.")
    n.add_argument("--line", help="아이디어 한 줄")
    for key in ("what", "who", "money", "why-now"):
        n.add_argument(f"--{key}", default="", help=f"{rubric.FIELDS[key.replace('-', '_')]}(비우면 미정)")
    n.add_argument("--from", dest="origin", help="이전 verdict.md. 같은 아이디어 폴더에 새 날짜 기록을 만듭니다.")
    n.add_argument("--direction", type=int, help="--from 기록의 방향 번호. 그 방향의 입력으로 다시 심사합니다.")
    n.add_argument("--date", help="기록 날짜(기본 오늘, YYYY-MM-DD)")
    n.add_argument("--allow-git", action="store_true", help="기록 폴더가 git 저장소 안이어도 만듭니다(권하지 않음).")

    r = sub.add_parser("record", help="한 단계의 결과 JSON을 검사해 result.json에 기록합니다.")
    r.add_argument("folder")
    r.add_argument("part", choices=store.PARTS)
    r.add_argument("--file", help="JSON 파일. 없으면 표준 입력에서 읽습니다.")

    d = sub.add_parser("decide", help="투표와 가정 검증으로 판정을 냅니다.")
    d.add_argument("folder")
    p = sub.add_parser("report", help="verdict.md를 만듭니다.")
    p.add_argument("folder")

    c = sub.add_parser("compare", help="같은 아이디어의 날짜별 판정을 비교합니다.")
    c.add_argument("folder")
    c.add_argument("--json", action="store_true")

    b = sub.add_parser("breakeven", help="사용자 값으로 손익분기 월 고객 수를 계산합니다.")
    b.add_argument("--price", type=float)
    b.add_argument("--unit-cost", type=float)
    b.add_argument("--fixed-cost", type=float)

    sub.add_parser("rubric", help="심사위원 기준표·가정·판정 값을 JSON으로 출력합니다.")
    sub.add_parser("home", help="기록 폴더 위치를 출력합니다.")

    args = parser.parse_args(argv)
    try:
        return _run(args)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2


def _read_json(file: str | None) -> dict:
    raw = Path(file).read_text(encoding="utf-8-sig") if file else sys.stdin.buffer.read().decode("utf-8-sig")
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON을 읽지 못했습니다: {e}")


def _run(args) -> int:
    if args.command == "new":
        if args.origin:
            prev = store.run_of(args.origin)
            old = store.load(prev)
            idea = store.direction(prev, args.direction)["idea"] if args.direction else old["idea"]
            origin = {"verdict": str(prev / "verdict.md"), "direction": args.direction}
            _print(store.create(idea, date=args.date, allow_git=args.allow_git, name=prev.parent.name,
                                base=prev.parent.parent, origin=origin))
        else:
            if args.direction:
                raise ValueError("--direction은 --from과 함께 씁니다.")
            idea = {"line": args.line, "what": args.what, "who": args.who, "money": args.money, "why_now": args.why_now}
            _print(store.create(idea, date=args.date, allow_git=args.allow_git))
    elif args.command == "record":
        _print(store.record(store.run_of(args.folder), args.part, _read_json(args.file)))
    elif args.command == "decide":
        _print(store.decide(store.run_of(args.folder)))
    elif args.command == "report":
        print(store.write_report(store.run_of(args.folder)))
    elif args.command == "compare":
        folder = store.run_of(args.folder)
        if (folder / "result.json").is_file():
            folder = folder.parent
        rows = store.compare(folder)
        if not rows:
            raise ValueError(f"비교할 기록이 없습니다: {folder}")
        if args.json:
            _print(rows)
        else:
            print(_render_compare(rows), end="")
    elif args.command == "breakeven":
        values = {k: {"value": v, "source": "사용자 입력"} for k, v in
                  (("price", args.price), ("unit_cost", args.unit_cost), ("fixed_cost", args.fixed_cost)) if v is not None}
        _print(money.breakeven(values))
    elif args.command == "rubric":
        _print({"judges": rubric.JUDGES, "scores": rubric.SCORES, "votes": rubric.VOTES,
                "assumptions": rubric.ASSUMPTIONS, "statuses": rubric.STATUSES, "fields": rubric.FIELDS,
                "core_fields": rubric.CORE_FIELDS, "panel_sizes": rubric.PANEL_SIZES, "notice": rubric.NOTICE})
    elif args.command == "home":
        print(store.home())
    return 0


def _render_compare(rows: list[dict]) -> str:
    head = ["기록", "판정"] + [rubric.JUDGES[k]["name"] for k in rubric.ORDER] + list(rubric.ASSUMPTIONS.values()) + ["한 줄"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for r in rows:
        scores = [str(r["scores"][k] or "-") for k in rubric.ORDER]
        checks = [r["assumptions"].get(k, "-") for k in rubric.ASSUMPTIONS]
        lines.append("| " + " | ".join([r["run"], r["verdict"], *scores, *checks, r["line"]]) + " |")
    return "\n".join(lines) + "\n"
