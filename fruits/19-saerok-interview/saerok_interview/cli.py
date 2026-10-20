"""사용: saerok-interview                       면접 화면을 브라우저로 엽니다(= saerok-interview web). Claude는 내 구독으로 부릅니다
      saerok-interview web [--port 8750] [--no-open] [--api]
      saerok-interview init
      saerok-interview docs [--company 회사]
      saerok-interview new [자기소개서] [--posting 공고] [--resume 이력서] [--portfolio 포트폴리오] [--company 회사] [--industry 산업 --role 직무]
      saerok-interview scan <파일...>
      saerok-interview rubric
      saerok-interview terms --industry platform --role pm [--limit 20]
      saerok-interview record <세션 폴더> document|answer|real   (JSON을 표준 입력으로)
      saerok-interview report <세션 폴더>
      saerok-interview next <세션 폴더> [--who pressure,numbers]
      saerok-interview compare [세션 폴더...] [--last 3] [--json]"""

import argparse
import json
import sys
from pathlib import Path

from . import compare, docs, rubric, session, store, terms, web


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _folder(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() or p.exists() else session.home() / path


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-interview", description="새록 면접관: 모의 면접 세션을 만들고 점수를 기록·비교합니다.")
    sub = parser.add_subparsers(dest="command")

    w = sub.add_parser("web", help="면접 화면을 내 PC에서 열고 브라우저를 띄웁니다(명령 없이 실행해도 같음).")
    w.add_argument("--port", type=int, default=web.DEFAULT_PORT)
    w.add_argument("--no-open", action="store_true", help="브라우저를 띄우지 않고 주소만 알립니다.")
    w.add_argument("--api", action="store_true", help="구독 대신 API 키로 Claude를 부릅니다(크레딧 차감).")

    n = sub.add_parser("new", help="면접 폴더에 세션을 만들고 입력 사본을 둡니다.")
    n.add_argument("resume_letter", nargs="?", help="자기소개서(.md·.txt). 비우면 면접 폴더의 '서류' 폴더에서 고릅니다.")
    n.add_argument("--posting", help="채용 공고(.md·.txt)")
    n.add_argument("--resume", help="이력서(.md·.txt)")
    n.add_argument("--portfolio", help="포트폴리오 요약(.md·.txt)")
    n.add_argument("--company", default="", help="회사 이름(세션 폴더 이름에 씀)")
    n.add_argument("--industry", default="", help="17번 새록 사전 산업 id(ecommerce·platform·finance)")
    n.add_argument("--role", default="", help="17번 새록 사전 직무 id(pm·data·marketing·cx)")
    n.add_argument("--date", help="세션 날짜(기본 오늘, YYYY-MM-DD)")
    n.add_argument("--allow-git", action="store_true", help="면접 폴더가 git 저장소 안이어도 만듭니다(권하지 않음).")

    sub.add_parser("init", help="면접 폴더에 '서류' 폴더와 자기소개서·공고 양식을 만듭니다.")
    d = sub.add_parser("docs", help="'서류' 폴더에서 이번에 쓸 자기소개서·공고·이력서·포트폴리오를 고릅니다.")
    d.add_argument("--company", default="", help="회사 이름(파일 이름 '공고-회사이름'의 회사이름)")

    s = sub.add_parser("scan", help="주민번호·전화번호·이메일 꼴을 찾습니다.")
    s.add_argument("files", nargs="+")

    sub.add_parser("rubric", help="면접관 5명의 기준 항목을 JSON으로 출력합니다.")
    sub.add_parser("home", help="면접 폴더 위치를 출력합니다.")

    t = sub.add_parser("terms", help="17번 새록 사전에서 산업·직무 핵심 용어를 고릅니다.")
    t.add_argument("--industry", required=True)
    t.add_argument("--role", required=True)
    t.add_argument("--limit", type=int, default=20)

    r = sub.add_parser("record", help="면접관 결과·답변·실제 면접 질문을 score.json에 기록합니다.")
    r.add_argument("folder")
    r.add_argument("kind", choices=["document", "answer", "real"])
    r.add_argument("--file", help="JSON 파일. 없으면 표준 입력에서 읽습니다.")

    p = sub.add_parser("report", help="score.json으로 verdict.md를 만듭니다.")
    p.add_argument("folder")

    x = sub.add_parser("next", help="다음에 물을 질문(서류 점수가 낮은 면접관부터)을 출력합니다.")
    x.add_argument("folder")
    x.add_argument("--who", help="이 면접관 질문만(쉼표로 여러 명: pressure,numbers)")

    c = sub.add_parser("compare", help="세션 여러 개의 점수 변화를 비교합니다.")
    c.add_argument("folders", nargs="*")
    c.add_argument("--last", type=int, help="면접 폴더의 최근 세션 N개")
    c.add_argument("--json", action="store_true")

    args = parser.parse_args(argv)
    try:
        return _run(args)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2


def _run(args) -> int:
    if args.command in (None, "web"):
        return web.serve(port=getattr(args, "port", web.DEFAULT_PORT), open_browser=not getattr(args, "no_open", False),
                         use_api=getattr(args, "api", False))
    if args.command == "new":
        files = {}
        if not args.resume_letter:  # 경로가 없으면 서류 폴더에서 고르고, 직접 준 옵션이 이깁니다.
            found = docs.pick(args.company)
            if found["pick"] is None:
                raise ValueError(f"회사가 여러 곳입니다. --company로 하나를 골라 주세요: {', '.join(found['choices'])}")
            files = dict(found["pick"])
            args.company = args.company or found["company"]
        else:
            files["resume_letter"] = args.resume_letter
        for key in ("posting", "resume", "portfolio"):
            if getattr(args, key):
                files[key] = getattr(args, key)
        if bool(args.industry) != bool(args.role):
            raise ValueError("산업과 직무는 함께 넘겨 주세요(--industry, --role).")
        if args.industry:
            terms.pick(args.industry, args.role, limit=1)  # 잘못된 id를 먼저 막습니다.
        _print(session.create(files, company=args.company, industry=args.industry, role=args.role,
                              date=args.date, allow_git=args.allow_git))
    elif args.command == "init":
        _print(docs.init())
    elif args.command == "docs":
        _print(docs.pick(args.company))
    elif args.command == "scan":
        out = {}
        for f in args.files:
            path = Path(f)
            if not path.is_file():
                raise ValueError(f"파일을 찾지 못했습니다: {path}")
            out[f] = session.scan(session.read(path))
        _print(out)
    elif args.command == "rubric":
        _print({"interviewers": rubric.INTERVIEWERS, "levels": rubric.LEVELS, "notice": rubric.NOTICE})
    elif args.command == "home":
        print(session.home())
    elif args.command == "terms":
        _print(terms.pick(args.industry, args.role, args.limit))
    elif args.command == "record":
        raw = Path(args.file).read_text(encoding="utf-8-sig") if args.file else sys.stdin.buffer.read().decode("utf-8-sig")
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON을 읽지 못했습니다: {e}")
        folder = _folder(args.folder)
        fn = {"document": store.record_document, "answer": store.record_answer, "real": store.record_real}[args.kind]
        _print(fn(folder, data))
    elif args.command == "report":
        print(store.write_report(_folder(args.folder)))
    elif args.command == "next":
        _print(store.next_question(_folder(args.folder), [w.strip() for w in args.who.split(",") if w.strip()] if args.who else None))
    elif args.command == "compare":
        folders = [_folder(f) for f in args.folders] or session.sessions()
        if args.last:
            folders = folders[-args.last:]
        if not folders:
            raise ValueError(f"비교할 세션이 없습니다. 면접 폴더: {session.home()}")
        result = compare.compare([session.load(f) for f in folders])
        if args.json:
            _print(result)
        else:
            print(compare.render(result), end="")
    return 0
