"""세션 폴더 만들기와 개인정보 꼴 점검. 기록은 내 PC 면접 폴더에만 둡니다."""

import hashlib
import json
import os
import re
import shutil
import time
from pathlib import Path

HOME_ENV = "SAEROK_INTERVIEW_HOME"
DOCS = ["resume_letter", "posting", "resume", "portfolio"]
DOC_NAMES = {"resume_letter": "자기소개서", "posting": "채용 공고", "resume": "이력서", "portfolio": "포트폴리오"}

PATTERNS = [
    ("주민등록번호", re.compile(r"(?<!\d)\d{6}\s?-\s?[1-4]\d{6}(?!\d)")),
    ("전화번호", re.compile(r"(?<!\d)01[016789][-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)")),
    ("이메일", re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")),
]


def home() -> Path:
    return Path(os.environ.get(HOME_ENV) or Path.home() / ".saerok" / "interview").expanduser().resolve()


def git_root(path: Path) -> Path | None:
    for folder in [path, *path.parents]:
        if (folder / ".git").exists():
            return folder
    return None


def _mask(text: str) -> str:
    return text[:3] + "*" * max(len(text) - 3, 0)


def scan(text: str) -> list[dict]:
    """주민번호·전화번호·이메일 꼴을 찾습니다. 찾은 값은 앞 세 글자만 보여 줍니다."""
    found = []
    for no, line in enumerate(text.splitlines(), 1):
        for kind, pattern in PATTERNS:
            for m in pattern.finditer(line):
                found.append({"line": no, "kind": kind, "masked": _mask(m.group())})
    return found


def _slug(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|\s]+", "-", name.strip()).strip("-.")
    return name[:30] or "이름-없음"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def create(files: dict[str, str], *, company: str = "", industry: str = "", role: str = "",
           date: str | None = None, base: Path | None = None, allow_git: bool = False) -> dict:
    """세션 폴더를 만들고 입력 사본과 session.json, 빈 score.json을 둡니다."""
    if "resume_letter" not in files:
        raise ValueError("자기소개서는 꼭 필요합니다.")
    texts = {}
    for key, path in files.items():
        if key not in DOCS:
            raise ValueError(f"모르는 입력입니다: {key}")
        file = Path(path)
        if not file.is_file():
            raise ValueError(f"파일을 찾지 못했습니다: {file}")
        if file.suffix.lower() not in (".md", ".txt"):
            raise ValueError(f"{file.name}: .md·.txt만 읽습니다. 한글·워드·PDF는 본문을 텍스트 파일로 붙여 넣어 주세요.")
        texts[key] = read(file)
    return create_texts(texts, company=company, industry=industry, role=role, date=date, base=base,
                        allow_git=allow_git, sources=files)


def create_texts(texts: dict[str, str], *, company: str = "", industry: str = "", role: str = "",
                 date: str | None = None, base: Path | None = None, allow_git: bool = False,
                 sources: dict[str, str] | None = None) -> dict:
    """본문으로 세션을 만듭니다(화면에서 붙여 넣은 서류). sources가 있으면 그 파일을 그대로 복사합니다."""
    base = (base or home()).resolve()
    repo = git_root(base)
    if repo and not allow_git:
        raise ValueError(f"면접 폴더({base})가 git 저장소({repo}) 안에 있습니다. 자기소개서가 커밋될 수 있어 멈춥니다. "
                         f"{HOME_ENV}를 저장소 밖으로 바꿔 주세요.")
    for key in texts:
        if key not in DOCS:
            raise ValueError(f"모르는 입력입니다: {key}")
    texts = {key: texts[key] for key in DOCS if isinstance(texts.get(key), str) and texts[key].strip()}
    if "resume_letter" not in texts:
        raise ValueError("자기소개서는 꼭 필요합니다.")

    date = date or time.strftime("%Y-%m-%d")
    stem = f"{date}-{_slug(company)}"
    folder, n = base / stem, 2
    while folder.exists():
        folder, n = base / f"{stem}-{n}", n + 1
    (folder / "inputs").mkdir(parents=True)

    inputs = {}
    for key, text in texts.items():
        target = folder / "inputs" / f"{DOC_NAMES[key]}.md"
        if sources and key in sources:
            shutil.copyfile(sources[key], target)
        else:
            target.write_text(text, encoding="utf-8", newline="")
        inputs[key] = {"file": f"inputs/{target.name}", "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}

    meta = {
        "version": 1,
        "session": folder.name,
        "date": date,
        "company": company,
        "industry": industry,
        "role": role,
        "posting": "posting" in texts,
        "inputs": inputs,
    }
    write_json(folder / "session.json", meta)
    write_json(folder / "score.json", {"version": 1, "document": {}, "answers": [], "real": []})
    privacy = {key: hits for key, text in texts.items() if (hits := scan(text))}
    return {"folder": str(folder), **meta, "privacy": privacy}


def inputs(folder: Path, meta: dict) -> dict[str, str]:
    """세션 폴더에 둔 입력 사본의 본문."""
    return {key: read(Path(folder) / info["file"]) for key, info in meta["inputs"].items()}


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load(folder: Path) -> tuple[dict, dict]:
    folder = Path(folder)
    meta_file, score_file = folder / "session.json", folder / "score.json"
    if not meta_file.is_file() or not score_file.is_file():
        raise ValueError(f"세션 폴더가 아닙니다(session.json·score.json 없음): {folder}")
    return json.loads(read(meta_file)), json.loads(read(score_file))


def sessions(base: Path | None = None) -> list[Path]:
    """면접 폴더 안의 세션을 이름(날짜) 순으로."""
    base = base or home()
    if not base.is_dir():
        return []
    return sorted(p for p in base.iterdir() if (p / "session.json").is_file())
