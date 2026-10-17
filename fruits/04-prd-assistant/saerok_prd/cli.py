"""사용: saerok-prd check <PRD 파일 | -> [--json] [--config 설정]
      saerok-prd compare <이전 PRD> <이후 PRD> [--json] [--log 기록 파일]
      saerok-prd compare <PRD> --since <커밋> [--json] [--log 기록 파일]"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from . import compare
from .check import check, render

CONFIG_NAME = ".saerok-prd.json"


def _read(path: str) -> str | None:
    if path == "-":
        return sys.stdin.buffer.read().decode("utf-8-sig")
    file = Path(path)
    if not file.is_file():
        print(f"파일을 찾지 못했습니다: {file}", file=sys.stderr)
        return None
    return file.read_text(encoding="utf-8-sig")


def find_config(start: Path) -> Path | None:
    """PRD 폴더에서 위로 올라가며 .saerok-prd.json을 찾습니다. git 저장소 맨 위에서 멈춥니다."""
    for folder in [start, *start.parents]:
        if (folder / CONFIG_NAME).is_file():
            return folder / CONFIG_NAME
        if (folder / ".git").exists():
            return None
    return None


def load_config(explicit: str | None, prd: str) -> tuple[dict | None, str | None]:
    path = Path(explicit) if explicit else find_config((Path.cwd() if prd == "-" else Path(prd).resolve().parent))
    if not path:
        return None, None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), None
    except (OSError, json.JSONDecodeError) as e:
        return None, f"설정 파일을 읽지 못했습니다({path}): {e}"


def git_version(path: str, rev: str) -> str | None:
    file = Path(path).resolve()
    run = subprocess.run(["git", "-C", str(file.parent), "show", f"{rev}:./{file.name}"], capture_output=True)
    if run.returncode:
        print(f"git에서 {rev} 버전을 꺼내지 못했습니다: {run.stderr.decode('utf-8', 'replace').strip()}", file=sys.stderr)
        return None
    return run.stdout.decode("utf-8-sig")


def append_log(log: str, before: str, after: str, summary: dict) -> None:
    row = {"date": time.strftime("%Y-%m-%d"), "before": before, "after": after, **summary}
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-prd", description="PRD를 기준표로 검사합니다.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="PRD 파일 하나를 검사합니다.")
    p.add_argument("path", help="Markdown PRD 파일 경로. -면 표준 입력에서 읽습니다.")
    c = sub.add_parser("compare", help="고치기 전후 PRD를 비교해 고친 비율을 셉니다.")
    c.add_argument("before", help="고치기 전 PRD 파일 경로. --since를 쓰면 지금 PRD 파일 경로")
    c.add_argument("after", nargs="?", help="고친 뒤 PRD 파일 경로. -면 표준 입력에서 읽습니다.")
    c.add_argument("--since", metavar="커밋", help="이 커밋의 버전을 이전으로 보고 지금 파일과 비교합니다(예: HEAD~1).")
    c.add_argument("--log", metavar="파일", help="날짜·파일·고친 비율을 이 파일에 한 줄(JSON)씩 덧붙입니다.")
    for q in (p, c):
        q.add_argument("--json", action="store_true", help="결과를 JSON으로 출력합니다.")
        q.add_argument("--config", metavar="파일", help=f"프로젝트 설정 파일. 없으면 PRD 폴더부터 위로 {CONFIG_NAME}을 찾습니다.")
    args = parser.parse_args(argv)

    if args.command == "compare":
        if args.since:
            if args.after:
                print("--since를 쓸 때는 PRD 파일을 하나만 넘겨 주세요.", file=sys.stderr)
                return 2
            names = (f"{args.before}@{args.since}", args.before)
            now = _read(args.before)
            texts = [git_version(args.before, args.since) if now is not None else None, now]
        elif not args.after or args.before == "-":
            print("이전 PRD 파일과 이후 PRD를 넘기거나, PRD 하나와 --since 커밋을 넘겨 주세요.", file=sys.stderr)
            return 2
        else:
            names = (args.before, args.after)
            texts = [_read(args.before), _read(args.after)]
        if None in texts:
            return 2
        config, error = load_config(args.config, names[1])
        if error:
            print(error, file=sys.stderr)
            return 2
        result = compare.compare(*texts, config)
        if args.log:
            append_log(args.log, *names, result["summary"])
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else compare.render(result))
        return 0

    text = _read(args.path)
    if text is None:
        return 2
    config, error = load_config(args.config, args.path)
    if error:
        print(error, file=sys.stderr)
        return 2
    result = check(text, config)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0
