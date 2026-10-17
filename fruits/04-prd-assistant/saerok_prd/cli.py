"""사용: saerok-prd check <PRD 파일 | -> [--json]"""

import argparse
import json
import sys
from pathlib import Path

from .check import check, render


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-prd", description="PRD를 기준표로 검사합니다.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("check", help="PRD 파일 하나를 검사합니다.")
    p.add_argument("path", help="Markdown PRD 파일 경로. -면 표준 입력에서 읽습니다.")
    p.add_argument("--json", action="store_true", help="결과를 JSON으로 출력합니다.")
    args = parser.parse_args(argv)

    if args.path == "-":
        text = sys.stdin.buffer.read().decode("utf-8-sig")
    else:
        path = Path(args.path)
        if not path.is_file():
            print(f"파일을 찾지 못했습니다: {path}", file=sys.stderr)
            return 2
        text = path.read_text(encoding="utf-8-sig")
    result = check(text)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else render(result))
    return 0
