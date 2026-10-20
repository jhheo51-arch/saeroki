"""면접 폴더의 '서류' 폴더: 양식을 만들고, 파일 이름으로 자기소개서·공고·이력서·포트폴리오를 고릅니다.
경로를 몰라도 `/saerok-interview:panel` 한 줄로 시작할 수 있게 합니다."""

import re
from pathlib import Path

from .session import HOME_ENV, git_root, home, read

FOLDER = "서류"
MARK = "[새록 면접관 양식]"
KINDS = {"자기소개서": "resume_letter", "자소서": "resume_letter", "공고": "posting", "채용공고": "posting",
         "이력서": "resume", "포트폴리오": "portfolio"}
NAME = re.compile(r"^(" + "|".join(sorted(KINDS, key=len, reverse=True)) + r")(?:[-_ ]+(.+))?$")
TEXT = (".md", ".txt")
OTHER = (".hwp", ".hwpx", ".doc", ".docx", ".pdf")

TEMPLATES = {
    "자기소개서.md": f"""# 자기소개서

> {MARK} '>'로 시작하는 안내 줄을 모두 지우고 내 자기소개서로 바꿔 주세요.
> 한 줄에 한 문장씩 씁니다. 면접관이 질문마다 몇째 줄 문장을 보고 물었는지 달아 줍니다.
> 문항은 '## 제목'으로 나눕니다. 수치는 원래 쓴 그대로 둡니다.
> 전화번호·이메일·주민번호는 넣지 않습니다.
> 한글·워드·PDF 원본은 본문을 복사해 여기에 붙여 넣으면 됩니다.
> 회사마다 자기소개서가 다르면 '자기소개서-회사이름.md'로 따로 둡니다.

## 지원 동기

## 가장 큰 성과

## 협업 경험

## 입사 후 포부
""",
    "공고-회사이름.md": f"""# 채용 공고

> {MARK} 파일 이름의 '회사이름'을 지원할 회사로 바꾸고(예: 공고-골목장터.md), '>'로 시작하는 안내 줄을 지운 뒤 채용 페이지 본문을 그대로 붙여 넣어 주세요.
> 회사가 여러 곳이면 이 파일을 복사해 '공고-회사이름.md'를 회사마다 하나씩 둡니다.
> 공고가 없으면 이 파일을 지워도 됩니다. 실무 '공고 요건 연결', 임원 '회사 이해'만 해당 없음이 됩니다.

## 회사 소개

## 주요 업무

## 자격 요건

## 우대 사항
""",
}


def folder() -> Path:
    return home() / FOLDER


def init() -> dict:
    """서류 폴더와 양식 파일을 만듭니다. 이미 있는 파일은 건드리지 않습니다."""
    base = folder()
    repo = git_root(base.parent)
    if repo:
        raise ValueError(f"면접 폴더({base.parent})가 git 저장소({repo}) 안에 있습니다. 자기소개서가 커밋될 수 있어 멈춥니다. "
                         f"{HOME_ENV}를 저장소 밖으로 바꿔 주세요.")
    base.mkdir(parents=True, exist_ok=True)
    created, kept = [], []
    for name, text in TEMPLATES.items():
        path = base / name
        if path.exists():
            kept.append(name)
            continue
        if name.startswith("공고") and any(_kind(p)[0] == "posting" for p in base.iterdir()):
            continue  # 이미 공고를 넣어 두었으면 양식을 다시 두지 않습니다.
        path.write_text(text, encoding="utf-8")
        created.append(name)
    return {"folder": str(base), "created": created, "kept": kept}


def _kind(path: Path) -> tuple[str | None, str]:
    m = NAME.match(path.stem.strip())
    if not m:
        return None, ""
    return KINDS[m.group(1)], (m.group(2) or "").strip()


def scan() -> dict:
    """서류 폴더의 파일을 종류·회사별로 나눕니다. 양식 그대로인 파일과 읽지 못하는 형식은 따로 알립니다."""
    base = folder()
    out = {"folder": str(base), "exists": base.is_dir(), "files": [], "template": [], "unreadable": [], "unknown": []}
    if not base.is_dir():
        return out
    for path in sorted(p for p in base.iterdir() if p.is_file()):
        suffix = path.suffix.lower()
        if suffix in OTHER:
            out["unreadable"].append(path.name)
            continue
        if suffix not in TEXT:
            continue
        kind, company = _kind(path)
        if not kind:
            out["unknown"].append(path.name)
        elif MARK in read(path):
            out["template"].append(path.name)
        else:
            out["files"].append({"kind": kind, "company": company, "file": str(path)})
    return out


def pick(company: str = "") -> dict:
    """회사 하나에 쓸 파일을 고릅니다. 회사 이름이 붙은 파일(예: 자기소개서-골목장터)이 먼저이고, 없으면 이름 없는 파일을 씁니다.
    공고가 여러 회사인데 회사를 정하지 않았으면 choices만 돌려줍니다. 공고가 없고 이름 없는 자기소개서도 없으면
    회사 이름이 붙은 자기소개서로 회사를 정합니다."""
    found = scan()
    if not found["exists"]:
        raise ValueError(f"서류 폴더가 없습니다: {found['folder']}. `saerok-interview init`으로 만들어 주세요.")
    files = found["files"]
    companies = sorted({f["company"] for f in files if f["company"]})
    if not company:
        posted = sorted({f["company"] for f in files if f["kind"] == "posting" and f["company"]})
        if not posted and not any(f["kind"] == "resume_letter" and not f["company"] for f in files):
            posted = sorted({f["company"] for f in files if f["kind"] == "resume_letter" and f["company"]})
        if len(posted) > 1:
            return {**found, "company": "", "choices": posted, "pick": None}
        company = posted[0] if posted else ""
    elif company not in companies and not any(f["kind"] == "resume_letter" and not f["company"] for f in files):
        raise ValueError(f"'{company}' 파일을 찾지 못했습니다. 서류 폴더의 회사: {', '.join(companies) or '없음'}")
    chosen = {}
    for kind in ("resume_letter", "posting", "resume", "portfolio"):
        mine = [f for f in files if f["kind"] == kind and f["company"] == company]
        common = [f for f in files if f["kind"] == kind and not f["company"]]
        for group in (mine, common):
            if len(group) > 1:
                raise ValueError(f"같은 종류 파일이 여러 개입니다: {', '.join(Path(f['file']).name for f in group)}. 하나만 남겨 주세요.")
        if mine or common:
            chosen[kind] = (mine or common)[0]["file"]
    if "resume_letter" not in chosen:
        hint = "아직 양식 그대로입니다. 안내 줄을 지우고 내용을 채워 주세요" if any(n.startswith(("자기소개서", "자소서")) for n in found["template"]) \
            else "'자기소개서.md'(또는 '자기소개서-회사이름.md')를 넣어 주세요"
        raise ValueError(f"자기소개서가 없습니다: {hint}. 서류 폴더: {found['folder']}")
    return {**found, "company": company, "choices": companies, "pick": chosen}
