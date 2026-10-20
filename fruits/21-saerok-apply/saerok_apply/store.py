"""지원 폴더(`~/.saerok/apply/`, 환경 변수 SAEROK_APPLY_HOME): 장부·표기 규칙·회사별 공고·분석·초안.
git 저장소 안이면 경고하고, 주민번호·전화번호·이메일 꼴을 점검합니다. 제출본은 19번 서류 폴더로 넘깁니다."""

import json
import os
import re
import time
from pathlib import Path

from . import core, terms

HOME_ENV = "SAEROK_APPLY_HOME"
INTERVIEW_ENV = "SAEROK_INTERVIEW_HOME"
LEDGER, STYLE = "ledger.md", "style.md"
COMPANY_FILES = ("posting.md", "analysis.md")
DRAFT = re.compile(r"^draft-[0-9]{4}-[0-9]{2}-[0-9]{2}(?:-[0-9]+)?\.md$")

# web/apply-core.js와 같은 결과를 내도록 `\d`·`\w`·`\s` 대신 ASCII 문자 묶음을 씁니다.
PATTERNS = [
    ("주민등록번호", re.compile(r"(?<![0-9])[0-9]{6}[ \t]?-[ \t]?[1-4][0-9]{6}(?![0-9])")),
    ("전화번호", re.compile(r"(?<![0-9])01[016789][-. \t]?[0-9]{3,4}[-. \t]?[0-9]{4}(?![0-9])")),
    ("이메일", re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9_-]+(\.[A-Za-z0-9_-]+)+")),
]

# 장부·표기 규칙 양식. 웹 화면(app.js)도 같은 파일을 읽습니다.
TEMPLATES = json.loads((Path(__file__).resolve().parent.parent / "data" / "templates.json").read_text(encoding="utf-8"))


def home() -> Path:
    return Path(os.environ.get(HOME_ENV) or Path.home() / ".saerok" / "apply").expanduser().resolve()


def interview_docs() -> Path:
    base = os.environ.get(INTERVIEW_ENV) or Path.home() / ".saerok" / "interview"
    return Path(base).expanduser().resolve() / "서류"


def git_root(path: Path) -> Path | None:
    for folder in [path, *path.parents]:
        if (folder / ".git").exists():
            return folder
    return None


def git_warning(path: Path | None = None) -> str:
    repo = git_root((path or home()).resolve())
    if not repo:
        return ""
    return f"지원 폴더가 git 저장소({repo}) 안에 있습니다. 장부와 자기소개서가 커밋되지 않게 {HOME_ENV}를 저장소 밖으로 옮겨 주세요."


def _mask(text: str) -> str:
    return text[:3] + "*" * max(len(text) - 3, 0)


def scan(text: str) -> list[dict]:
    """주민번호·전화번호·이메일 꼴. 찾은 값은 앞 세 글자만 보여 줍니다."""
    found = []
    for no, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            for m in pattern.finditer(line):
                found.append({"line": no, "kind": kind, "masked": _mask(m.group())})
    return found


def read(path: Path) -> str:
    path = Path(path)
    return path.read_text(encoding="utf-8-sig") if path.is_file() else ""


def slug(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\s]+", "-", name.strip()).strip("-.")
    return name[:40]


def company_dir(company: str) -> Path:
    name = slug(company)
    if not name:
        raise ValueError("회사 이름이 비었습니다.")
    return home() / name


def companies_here() -> list[str]:
    """지원 폴더 안의 회사 폴더 이름(posting.md나 draft가 있는 폴더)."""
    base = home()
    if not base.is_dir():
        return []
    out = []
    for p in sorted(base.iterdir()):
        if p.is_dir() and not p.name.startswith(".") and (
                any((p / f).is_file() for f in COMPANY_FILES) or any(DRAFT.match(f.name) for f in p.iterdir())):
            out.append(p.name)
    return out


def company_names(current: str = "", data: dict | None = None) -> list[dict]:
    """다른 회사 이름 검사용 목록: 지원 폴더 이름(from=folder)과 17번 사전 기업명(from=dictionary)."""
    out, seen = [], set()
    for name in companies_here():
        if name.lower() not in seen:
            seen.add(name.lower())
            out.append({"name": name, "from": "folder"})
    try:
        names = (data or terms.load()).get("companies", [])
    except OSError:
        names = []
    for name in names:
        if name.lower() not in seen:
            seen.add(name.lower())
            out.append({"name": name, "from": "dictionary"})
    return out


def drafts(company: str) -> list[Path]:
    folder = company_dir(company)
    return sorted(p for p in folder.iterdir() if DRAFT.match(p.name)) if folder.is_dir() else []


def new_draft_path(company: str, date: str | None = None) -> Path:
    """덮어쓰지 않는 새 초안 이름: draft-YYYY-MM-DD.md, 있으면 -2, -3…"""
    date = date or time.strftime("%Y-%m-%d")
    folder = company_dir(company)
    path = folder / f"draft-{date}.md"
    n = 2
    while path.exists():
        path = folder / f"draft-{date}-{n}.md"
        n += 1
    return path


def init(base: Path | None = None) -> dict:
    """지원 폴더와 장부·표기 규칙 양식을 만듭니다. 이미 있는 파일은 건드리지 않습니다."""
    base = (base or home()).resolve()
    base.mkdir(parents=True, exist_ok=True)
    made = []
    for name, text in TEMPLATES.items():
        path = base / name
        if not path.exists():
            path.write_text(text, encoding="utf-8")
            made.append(str(path))
    return {"home": str(base), "made": made, "warning": git_warning(base)}


def context(draft_path: Path, company: str = "", ledger: str = "", analysis: str = "", style: str = "",
            previous: str = "") -> dict:
    """check에 넘길 글들을 모읍니다. 경로를 주지 않으면 지원 폴더의 기본 위치를 씁니다."""
    draft_path = Path(draft_path)
    draft_text = read(draft_path)
    if not draft_text:
        raise ValueError(f"초안을 찾지 못했습니다: {draft_path}")
    company = company or core.parse_draft(draft_text)["company"]
    folder = company_dir(company) if company else draft_path.parent
    return {
        "draft_text": draft_text,
        "ledger_text": read(Path(ledger) if ledger else home() / LEDGER),
        "analysis_text": read(Path(analysis) if analysis else folder / "analysis.md"),
        "posting_text": read(folder / "posting.md"),
        "style_text": read(Path(style) if style else home() / STYLE),
        "previous_text": read(Path(previous)) if previous else "",
        "company": company,
    }


def run_check(draft_path: Path, company: str = "", ledger: str = "", analysis: str = "", style: str = "",
              previous: str = "", data: dict | None = None) -> dict:
    ctx = context(draft_path, company, ledger, analysis, style, previous)
    data = data or terms.load()
    return core.check(ctx["draft_text"], ctx["ledger_text"], ctx["analysis_text"], ctx["posting_text"],
                      ctx["style_text"], company_names(ctx["company"], data), data, ctx["previous_text"])


def _free(path: Path, date: str) -> Path:
    if not path.exists():
        return path
    candidate = path.with_name(f"{path.stem}-{date}{path.suffix}")
    n = 2
    while candidate.exists():
        candidate = path.with_name(f"{path.stem}-{date}-{n}{path.suffix}")
        n += 1
    return candidate


def submit(draft_path: Path, company: str = "", dry_run: bool = False, date: str | None = None,
           result: dict | None = None) -> dict:
    """검사를 통과하고 모든 문항이 확정이면 ID 주석을 뺀 제출본을 19번 서류 폴더에 저장합니다.
    같은 이름이 있으면 덮어쓰지 않고 날짜를 붙입니다."""
    ctx = context(draft_path, company)
    result = result or run_check(draft_path, company)
    if result["summary"]["errors"]:
        raise ValueError(f"검사 오류가 {result['summary']['errors']}개 있습니다. check로 고친 뒤 넘겨 주세요.")
    if not result["summary"]["confirmed_all"]:
        raise ValueError("아직 '상태: 확정'이 아닌 문항이 있습니다. 모든 문항을 확정한 뒤 넘겨 주세요.")
    company = ctx["company"]
    date = date or time.strftime("%Y-%m-%d")
    text = core.submission(ctx["draft_text"])
    found = scan(text)
    if found:
        raise ValueError("제출본에 개인정보 꼴(" + ", ".join(f"{f['line']}줄 {f['kind']}" for f in found) + ")이 있습니다.")
    folder = interview_docs()
    targets = [("자기소개서", text)]
    posting = core.parse_posting(ctx["posting_text"])
    if ctx["posting_text"] and posting["body"] and posting["status"] == "확인함":
        targets.append(("공고", f"# 채용 공고 · {company}\n\n- 출처: {posting['source']}\n- 확인 날짜: {posting['checked_at']}\n\n"
                               f"{posting['body']}\n"))
    out = []
    for kind, body in targets:
        path = _free(folder / f"{kind}-{slug(company)}.md", date)
        out.append({"kind": kind, "path": str(path)})
        if not dry_run:
            folder.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
    return {"saved": not dry_run, "files": out, "warning": git_warning(folder),
            "next": "/saerok-interview:panel 로 서류 심사를 받습니다. 날짜가 붙은 이름이면 --company에 그 이름을 그대로 넣어 주세요."}
