"""saerok-memory 명령."""

import argparse
import json
import sys

from . import hook, memory, server, sessions, versions
from .paths import data_home
from .store import LINE_LIMIT, read_json, write_json


def _mb(n: int) -> str:
    return f"{n / 1e6:,.1f}MB"


def status() -> dict:
    mem, ver, ses = memory.scan(), versions.scan(), sessions.scan()
    kinds = {}
    for c in mem["candidates"]:
        kinds[c["kind"]] = kinds.get(c["kind"], 0) + 1
    return {
        "projects": [{k: p[k] for k in ("project", "index_bytes", "longest_line", "long_lines", "files", "over_limit")}
                     for p in mem["projects"]],
        "memory_candidates": kinds,
        "versions": {"candidates": len(ver["candidates"]), "bytes": sum(c["bytes"] for c in ver["candidates"]),
                     "kept": ver["kept"], "guarded": ver["guarded"]},
        "sessions": {"logs": ses["logs"], "bytes": ses["bytes"], "open": ses["open"],
                     "candidates": len(ses["candidates"]), "candidate_bytes": sum(c["bytes"] for c in ses["candidates"])},
    }


def print_status() -> None:
    s = status()
    print("기억 목차(MEMORY.md)")
    for p in s["projects"]:
        mark = " ← 4,000바이트 넘음" if p["over_limit"] else ""
        print(f"  {p['project']}: {p['index_bytes']:,}바이트, 가장 긴 줄 {p['longest_line']:,}자, 150자 넘는 줄 {p['long_lines']}개{mark}")
    names = {"index_line": "긴 목차 줄", "archive": "끝난 기억", "stale": "낡은 경로", "broken": "목차 어긋남", "duplicate": "중복 의심"}
    print("기억 후보: " + (", ".join(f"{names.get(k, k)} {v}" for k, v in s["memory_candidates"].items()) or "없음"))
    v = s["versions"]
    print(f"옛 버전 후보 {v['candidates']}개({_mb(v['bytes'])}), 남기는 최신 두 버전 {v['kept']}개, 보호 {v['guarded']}개")
    ss = s["sessions"]
    print(f"세션 기록 {ss['logs']}개({_mb(ss['bytes'])}), 열린 기록 {ss['open']}개, 후보 {ss['candidates']}개({_mb(ss['candidate_bytes'])})")


def suggest(args) -> int:
    """trim 스킬용. --list는 긴 목차 줄 후보를, --id와 --text는 AI 요약 문장을 저장합니다."""
    path = data_home() / "suggestions.json"
    if args.list:
        rows = [{"id": c["id"], "project": c["project"], "before": c["before"], "proposal": c["proposal"]}
                for c in memory.scan()["candidates"] if c["kind"] == "index_line"]
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return 0
    if not (args.id and args.text):
        print("--list 또는 --id와 --text를 함께 주세요.", file=sys.stderr)
        return 2
    text = args.text.strip()
    if len(text) > LINE_LIMIT or len(memory.parse_index(text)) != 1:
        print(f"제안은 '- [제목](파일) — 설명' 한 줄이고 {LINE_LIMIT}자 안이어야 합니다(지금 {len(text)}자).", file=sys.stderr)
        return 2
    saved = read_json(path, {}) or {}
    saved[args.id] = text
    write_json(path, saved)
    print("저장했습니다. 대시보드 후보 탭에서 원문과 나란히 보고 적용하세요.")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="saerok-memory", description="새록 가지치기: Claude 기억과 옛 파일 정리")
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("serve", help="대시보드 열기(기본)")
    p.add_argument("--port", type=int, default=8738)
    p.add_argument("--no-browser", action="store_true")
    st = sub.add_parser("status", help="터미널에 요약 출력")
    st.add_argument("--json", action="store_true")
    sub.add_parser("hook", help="Claude Code Stop 훅(직접 실행하지 않음)")
    sg = sub.add_parser("suggest", help="목차 줄 요약 제안 저장(trim 스킬용)")
    sg.add_argument("--list", action="store_true")
    sg.add_argument("--id")
    sg.add_argument("--text")
    args = parser.parse_args(argv)

    if args.cmd == "hook":
        return hook.main()
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.cmd == "status":
        if args.json:
            print(json.dumps(status(), ensure_ascii=False, indent=2))
        else:
            print_status()
        return 0
    if args.cmd == "suggest":
        return suggest(args)
    server.serve(getattr(args, "port", 8738), not getattr(args, "no_browser", False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
