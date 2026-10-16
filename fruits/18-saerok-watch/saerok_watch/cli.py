"""saerok-watch 명령."""

import argparse
import sys

from . import advise, export, hook, scan, server
from .store import load_config


def _man(n: int) -> str:
    return advise._man(n)


def print_status() -> None:
    sessions = scan.scan_all()
    t = scan.totals(sessions)
    total = t["processed"] or 1
    print(f"세션 {t['sessions']}개 · 응답 {t['responses']:,}번 · 처리 {_man(t['processed'])} 토큰 · 기본 부담 중앙값 {_man(t['baseline_median'])}")
    labels = ("10만 미만", "10~30만", "30~60만", "60만 이상")
    for label, amount in zip(labels, t["buckets"]):
        print(f"  {label:<8} {amount / total:5.0%} {'█' * round(amount / total * 40)}")
    print()
    for s in advise.suggestions(sessions, load_config()):
        print(f"[{s['size']}] {s['title']}")
        print(f"     {s['measured']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="saerok-watch", description="새록 파수꾼: Claude Code 토큰 사용량 감시")
    sub = parser.add_subparsers(dest="cmd")
    p = sub.add_parser("serve", help="대시보드 열기(기본)")
    p.add_argument("--port", type=int, default=8718)
    p.add_argument("--no-browser", action="store_true")
    sub.add_parser("status", help="터미널에 요약 출력")
    sub.add_parser("hook", help="Claude Code Stop 훅(직접 실행하지 않음)")
    sub.add_parser("statusline", help="Claude Code 상태줄(직접 실행하지 않음)")
    sub.add_parser("test-alert", help="파수꾼 새록이 Windows 알림 시험")
    e = sub.add_parser("export", help="공개용 날짜별 집계 파일 만들기")
    e.add_argument("--out", default=None)
    args = parser.parse_args(argv)
    if args.cmd not in ("hook", "statusline"):
        # 파이프로 받는 cp949 콘솔에서도 막대 글자 때문에 멈추지 않게 합니다.
        sys.stdout.reconfigure(errors="replace")

    if args.cmd == "hook":
        return hook.main()
    if args.cmd == "statusline":
        from . import statusline
        return statusline.main()
    if args.cmd == "test-alert":
        from . import notify
        ok = notify.toast(*notify.TEST, wait=True)
        print("알림을 보냈습니다. 화면 오른쪽 아래를 확인하세요." if ok else "Windows에서만 알림을 띄울 수 있습니다.")
        return 0
    if args.cmd == "status":
        print_status()
        return 0
    if args.cmd == "export":
        from pathlib import Path
        out = export.export(scan.scan_all(), Path(args.out) if args.out else export.PUBLIC_DAILY)
        print(f"공개 집계를 만들었습니다: {out}")
        print("커밋·push 전에 파일을 확인하세요.")
        return 0
    server.serve(getattr(args, "port", 8718), not getattr(args, "no_browser", False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
