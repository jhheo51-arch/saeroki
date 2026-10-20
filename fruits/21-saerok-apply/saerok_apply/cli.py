"""사용: saerok-apply                          지원서 화면을 브라우저로 엽니다(= saerok-apply web). Claude는 내 구독으로 부릅니다
      saerok-apply web [--port 8760] [--no-open] [--api]
      saerok-apply init
      saerok-apply where
      saerok-apply ledger [--ledger 경로] [--json]
      saerok-apply analysis <회사> [--json]
      saerok-apply terms <공고 파일> [--industry 산업 --role 직무]
      saerok-apply check <초안|이력서|포트폴리오> [--company 회사] [--ledger] [--analysis] [--style] [--previous 이전 판] [--json]
      saerok-apply diff <이전 판> <새 판>
      saerok-apply submit <초안|이력서|포트폴리오> [--company 회사] [--dry-run]
      saerok-apply html <이력서|포트폴리오> [--out 경로]
      saerok-apply privacy <파일...>
check와 submit은 파일 첫 제목('# 이력서', '# 포트폴리오')이나 이름(resume-, portfolio-)을 보고
이력서, 포트폴리오 검사(PRD 5.7절)와 자기소개서 검사를 가립니다. 검사에 오류가 있으면 종료 코드 2를 돌려줍니다."""

import argparse
import difflib
import json
import sys
from pathlib import Path

from . import core, store, terms

LEVEL = {"error": "오류", "warn": "경고"}
FIT = {"ok": "적정", "over": "초과", "short": "부족", "no-limit": "제한 없음"}
BASIS = {"with_spaces": "공백 포함", "without_spaces": "공백 제외", "bytes": "바이트"}


def _print(data) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def _issues(issues: list) -> list[str]:
    lines = []
    for i in issues:
        lines.append(f"- [{LEVEL[i['level']]}] {i['where']} · {i['code']}: {i['message']}")
        if i["text"]:
            lines.append(f"    > {i['text']}")
    return lines


def render_check(result: dict) -> str:
    s = result["summary"]
    lines = [f"# 자기소개서 검사 · {result['company'] or '회사 미정'}", "",
             f"오류 {s['errors']}개 · 경고 {s['warnings']}개 · 확정 {'모두' if s['confirmed_all'] else '아직 아님'}"
             f" · 제출 {'가능' if s['submittable'] else '불가'}", "", "## 글자 수", "",
             "| 문항 | 유형 | 판 | 상태 | 기준 | 글자 | 제한 | 비율 | 판정 |", "|---|---|---|---|---|---:|---:|---:|---|"]
    for q in result["questions"]:
        value = q["count"][q["basis"]] if q["limit"] else q["count"]["with_spaces"]
        lines.append(f"| {q['no']}. {q['title']} | {q['type'] or '-'} | {q['version'] or '-'} | "
                     f"{'확정' if q['confirmed'] else '작성 중'} | {BASIS[q['basis']]} | {value} | {q['limit'] or '-'} | "
                     f"{'-' if q['ratio'] is None else str(q['ratio']) + '%'} | {FIT[q['fit']]} |")
    lines += ["", "공백 포함·공백 제외·바이트(한글 3바이트, UTF-8)는 JSON 출력(--json)에 모두 있습니다."]
    if result["short_fields"]:
        lines += ["", "## 짧은 칸", "", "| 칸 | 글자 | 제한 | 비율 |", "|---|---:|---:|---:|"]
        for f in result["short_fields"]:
            lines.append(f"| {f['name']} | {f['count']['with_spaces']} | {f['limit'] or '-'} | "
                         f"{'-' if f['ratio'] is None else str(f['ratio']) + '%'} |")
    if result["coverage"]:
        lines += ["", "## 역량·세부 업무 커버리지", "", "| 항목 | 구분 | 문항 |", "|---|---|---|"]
        for c in result["coverage"]:
            lines.append(f"| {c['item']} | {c['kind']} | {', '.join(str(n) for n in c['questions']) or '빠짐'} |")
    lines += ["", "## 문제", ""] + (_issues(result["issues"]) or ["- 없음"])
    return "\n".join(lines) + "\n"


def render_doc(result: dict) -> str:
    s = result["summary"]
    label = core.DOC_KINDS[result["kind"]]
    lines = [f"# {label} 검사 · {result['company'] or '회사 미정'}", "",
             f"오류 {s['errors']}개 · 경고 {s['warnings']}개 · {result['pages']}쪽 · 카드 {result['cards']}개"
             f" · 판 {result['version'] or '-'} · 확정 {'예' if s['confirmed'] else '아직 아님'}"
             f" · 제출 {'가능' if s['submittable'] else '불가'}", ""]
    if result["keywords"]:
        lines += ["## 공고 키워드", "", "| 항목 | 구분 | 문서에 있나 |", "|---|---|---|"]
        lines += [f"| {k['item']} | {k['kind']} | {'있음' if k['found'] else '없음'} |" for k in result["keywords"]]
        lines.append("")
    lines += ["## 문제", ""] + (_issues(result["issues"]) or ["- 없음"])
    return "\n".join(lines) + "\n"


def render_ledger(report: dict) -> str:
    lines = [f"# 경험 장부 · 경험 {report['summary']['experiences']}개 · 오류 {report['summary']['errors']}개", "",
             "| ID | 경험 | 기간 | 역량 | 한 일·설계안·계획 | 수치 | 확인 전 칸 |", "|---|---|---|---|---|---:|---|"]
    for e in report["experiences"]:
        a = e["actions"]
        lines.append(f"| {e['id']} | {e['title']} | {e['period']} | {', '.join(e['competencies'])} | "
                     f"{a['한 일']}·{a['설계안(도입 가정)']}·{a['계획']} | {e['metrics']} | {', '.join(e['unconfirmed']) or '-'} |")
    lines += ["", "## 문제", ""] + (_issues(report["issues"]) or ["- 없음"])
    return "\n".join(lines) + "\n"


def render_analysis(result: dict) -> str:
    p, f = result["posting"], result["flags"]
    lines = [f"# 공고·분석 점검 · {p['company'] or '회사 미정'}", "",
             f"- 공고 상태: {p['status']} · 출처: {p['source'] or '-'} · 확인 날짜: {p['checked_at'] or '-'}",
             f"- 분석 진행: {'멈춤(공고 확인 필요)' if result['blocked'] else '가능'}",
             f"- 공고 읽기 실패: {'예' if f['posting_failed'] else '아니요'} · 이미지 확인 전: {'예' if f['image_unconfirmed'] else '아니요'}"
             f" · 회사 조사 없음: {'예' if f['research_none'] else '아니요'}"
             f" · 사전에 없는 용어: {', '.join(f['terms_missing']) or '없음'}", "", "## 문제", ""]
    lines += _issues(result["issues"]) or ["- 없음"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(prog="saerok-apply", description="새록 지원서: 경험 장부로 자기소개서를 쓰고 검사합니다.")
    sub = parser.add_subparsers(dest="command")

    w = sub.add_parser("web", help="지원서 화면을 내 PC에서 열고 브라우저를 띄웁니다(명령 없이 실행해도 같음).")
    w.add_argument("--port", type=int, default=8760)
    w.add_argument("--no-open", action="store_true")
    w.add_argument("--api", action="store_true", help="구독 대신 API 키로 Claude를 부릅니다(크레딧 차감).")

    sub.add_parser("init", help="지원 폴더와 장부·표기 규칙 양식을 만듭니다.")
    sub.add_parser("where", help="지원 폴더와 19번 서류 폴더 위치를 알립니다.")

    lg = sub.add_parser("ledger", help="경험 장부 형식과 확인 전 칸을 점검합니다.")
    lg.add_argument("--ledger")
    lg.add_argument("--json", action="store_true")

    an = sub.add_parser("analysis", help="회사 폴더의 posting.md·analysis.md를 점검합니다.")
    an.add_argument("company")
    an.add_argument("--json", action="store_true")

    t = sub.add_parser("terms", help="공고 글에 나오는 17번 새록 사전 용어를 찾습니다.")
    t.add_argument("posting")
    t.add_argument("--industry", default="")
    t.add_argument("--role", default="")

    c = sub.add_parser("check", help="자기소개서 초안, 이력서, 포트폴리오를 검사합니다(같은 입력이면 같은 결과).")
    c.add_argument("draft")
    c.add_argument("--company", default="")
    c.add_argument("--ledger", default="")
    c.add_argument("--analysis", default="")
    c.add_argument("--style", default="")
    c.add_argument("--previous", default="", help="이전 판. 확정 문항이 바뀌었는지 봅니다.")
    c.add_argument("--json", action="store_true")

    d = sub.add_parser("diff", help="두 판의 바뀐 줄을 보여 줍니다.")
    d.add_argument("old")
    d.add_argument("new")

    s = sub.add_parser("submit", help="검사를 통과한 확정본을 19번 서류 폴더로 넘깁니다(덮어쓰지 않음).")
    s.add_argument("draft")
    s.add_argument("--company", default="")
    s.add_argument("--dry-run", action="store_true")

    h = sub.add_parser("html", help="이력서, 포트폴리오 제출본을 한 단 HTML로 만듭니다(PDF는 브라우저 인쇄).")
    h.add_argument("file")
    h.add_argument("--out", default="")

    pv = sub.add_parser("privacy", help="주민번호·전화번호·이메일 꼴을 찾습니다.")
    pv.add_argument("files", nargs="+")

    args = parser.parse_args(argv)
    try:
        return _run(args)
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2


def _need(path: Path) -> str:
    text = store.read(path)
    if not text:
        raise ValueError(f"파일을 찾지 못했습니다: {path}")
    return text


def _is_doc(path: Path) -> bool:
    return bool(core.doc_kind(store.read(path), path.name))


def _run(args) -> int:
    if args.command in (None, "web"):
        from . import web
        return web.serve(port=getattr(args, "port", 8760), open_browser=not getattr(args, "no_open", False),
                         use_api=getattr(args, "api", False))
    if args.command == "init":
        _print(store.init())
    elif args.command == "where":
        _print({"home": str(store.home()), "interview_docs": str(store.interview_docs()),
                "companies": store.companies_here(), "warning": store.git_warning()})
    elif args.command == "ledger":
        report = core.ledger_report(_need(Path(args.ledger) if args.ledger else store.home() / store.LEDGER))
        _print(report) if args.json else print(render_ledger(report), end="")
        return 2 if report["summary"]["errors"] else 0
    elif args.command == "analysis":
        folder = store.company_dir(args.company)
        result = core.check_analysis(store.read(folder / "posting.md"), store.read(folder / "analysis.md"), terms.load())
        _print(result) if args.json else print(render_analysis(result), end="")
        return 2 if result["summary"]["errors"] else 0
    elif args.command == "terms":
        posting = core.parse_posting(_need(Path(args.posting)))
        if posting["status"] != "확인함":
            raise ValueError(f"공고 상태가 '{posting['status']}'입니다. 확인한 공고만 분석합니다.")
        _print(core.match_terms(posting["body"], terms.load(), args.industry, args.role))
    elif args.command == "check" and _is_doc(Path(args.draft)):
        result = store.run_doc_check(Path(args.draft), args.company, args.ledger, args.analysis, args.style)
        _print(result) if args.json else print(render_doc(result), end="")
        return 2 if result["summary"]["errors"] else 0
    elif args.command == "check":
        result = store.run_check(Path(args.draft), args.company, args.ledger, args.analysis, args.style, args.previous)
        _print(result) if args.json else print(render_check(result), end="")
        return 2 if result["summary"]["errors"] else 0
    elif args.command == "diff":
        old, new = _need(Path(args.old)).splitlines(), _need(Path(args.new)).splitlines()
        print("\n".join(difflib.unified_diff(old, new, args.old, args.new, lineterm="")) or "바뀐 줄이 없습니다.")
    elif args.command == "submit" and _is_doc(Path(args.draft)):
        _print(store.submit_doc(Path(args.draft), args.company, dry_run=args.dry_run))
    elif args.command == "html":
        path = Path(args.file)
        text = _need(path)
        kind = core.doc_kind(text, path.name)
        if not kind:
            raise ValueError("이력서나 포트폴리오가 아닙니다. 첫 줄을 '# 이력서 · 회사'나 '# 포트폴리오 · 회사'로 써 주세요.")
        company = core.parse_doc(text)["meta"].get("회사", "")
        out = Path(args.out) if args.out else path.with_suffix(".html")
        out.write_text(core.to_html(core.doc_submission(text), f"{core.DOC_KINDS[kind]} {company}".strip()), encoding="utf-8")
        _print({"html": str(out), "next": "브라우저로 열고 인쇄(Ctrl+P)에서 'PDF로 저장'을 고르면 PDF가 됩니다."})
    elif args.command == "submit":
        _print(store.submit(Path(args.draft), args.company, dry_run=args.dry_run))
    elif args.command == "privacy":
        out = {f: store.scan(_need(Path(f))) for f in args.files}
        _print(out)
        return 2 if any(out.values()) else 0
    return 0
