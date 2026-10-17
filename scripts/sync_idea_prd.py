"""20번 새록 심사단 PRD(docs/PRD-v<버전>-idea.md)의 버전을 4번 새록 검토관 PRD 버전에 맞춥니다(PRD 10장).

사용: python scripts/sync_idea_prd.py           버전이 다르면 이름·제목·머리말·링크를 고칩니다.
      python scripts/sync_idea_prd.py --check   고치지 않고 어긋난 것만 알립니다(어긋나면 종료 코드 1).

본문은 바꾸지 않고, 이름을 맞춘 뒤에는 '내용 다시 보기 전' 표시를 남깁니다."""

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEWER_TITLE = "# 새록이 4번 열매 PRD"
REVIEWER_SKILL = Path("fruits/04-prd-assistant/skills/design/SKILL.md")
NAME = re.compile(r"^PRD-v(\d+)\.(\d+)(-idea)?\.md$")
IDEA_REF = re.compile(r"PRD-v(\d+\.\d+)-idea\.md")
HEADER = re.compile(r"검토관 \[PRD v\d+\.\d+\]\(PRD-v\d+\.\d+\.md\)")
REVIEW_MARK = "- 내용 다시 보기: 검토관 v{v}로 이름만 맞춤, 내용 다시 보기 전"
SKIP_DIRS = {".git", "docs", "node_modules", "__pycache__"}


def reviewer_version(root: Path) -> str:
    found = []
    for path in (root / "docs").glob("PRD-v*.md"):
        m = NAME.match(path.name)
        if not m or m.group(3):
            continue
        first = path.read_text(encoding="utf-8-sig").splitlines()[:1]
        if first and first[0].startswith(REVIEWER_TITLE):
            found.append((int(m.group(1)), int(m.group(2))))
    if not found:
        # 못 찾으면 옛 값으로 대신하지 않고 멈춥니다(AGENT-SPEC 3번).
        raise ValueError(f"검토관 PRD를 찾지 못했습니다: docs/PRD-v*.md 중 첫 줄이 '{REVIEWER_TITLE}'로 시작하는 파일이 없습니다.")
    major, minor = max(found)
    return f"{major}.{minor}"


def idea_file(root: Path) -> Path:
    files = [p for p in (root / "docs").glob("PRD-v*-idea.md") if NAME.match(p.name)]
    if len(files) != 1:
        raise ValueError(f"심사단 PRD(docs/PRD-v*-idea.md)는 하나여야 합니다(찾은 수 {len(files)}).")
    return files[0]


def version_of(path: Path) -> str:
    m = NAME.match(path.name)
    return f"{m.group(1)}.{m.group(2)}"


def link_files(root: Path) -> list[Path]:
    """심사단 PRD를 가리킬 수 있는 문서들. docs/ 안의 옛 PRD 기록은 그대로 둡니다."""
    out = []
    for path in sorted(root.rglob("*.md")):
        rel = path.relative_to(root)
        if not SKIP_DIRS.intersection(rel.parts[:-1]):
            out.append(path)
    return out


def problems(root: Path = ROOT) -> list[str]:
    target, current = reviewer_version(root), idea_file(root)
    out = []
    if version_of(current) != target:
        out.append(f"심사단 PRD가 {current.name}인데 검토관은 v{target}입니다. scripts/sync_idea_prd.py를 실행하세요.")
    else:
        if not HEADER.search(current.read_text(encoding="utf-8")):
            out.append(f"{current.name} 머리말에 '검토관 [PRD v{target}](PRD-v{target}.md)' 줄이 없습니다.")
    for path in link_files(root):
        for old in set(IDEA_REF.findall(path.read_text(encoding="utf-8"))):
            if f"PRD-v{old}-idea.md" != current.name:
                out.append(f"{path.relative_to(root).as_posix()}: 없는 심사단 PRD(PRD-v{old}-idea.md)를 가리킵니다.")
    skill = root / REVIEWER_SKILL
    if not skill.is_file() or "--from" not in skill.read_text(encoding="utf-8"):
        out.append(f"{REVIEWER_SKILL.as_posix()}에 '--from' 안내가 없습니다. 심사단 판정을 검토관에 넘기는 연결이 끊겼습니다.")
    return out


def sync(root: Path = ROOT, use_git: bool = True) -> list[str]:
    """버전이 다르면 고치고, 바꾼 파일 목록을 돌려줍니다."""
    target, current = reviewer_version(root), idea_file(root)
    old = version_of(current)
    if old == target:
        return []
    new = current.with_name(f"PRD-v{target}-idea.md")
    if use_git:
        subprocess.run(["git", "mv", str(current), str(new)], cwd=root, check=True)
    else:
        current.rename(new)
    lines = new.read_text(encoding="utf-8").split("\n")
    lines[0] = lines[0].replace(f"PRD v{old}-idea", f"PRD v{target}-idea")
    text = "\n".join(lines)
    text = HEADER.sub(f"검토관 [PRD v{target}](PRD-v{target}.md)", text, count=1)
    text = re.sub(r"\n- 내용 다시 보기: 검토관 v\d+\.\d+로 이름만 맞춤, 내용 다시 보기 전", "", text)
    mark = REVIEW_MARK.format(v=target)
    head, sep, rest = text.partition("\n- 문서 버전:")
    line_end = rest.find("\n")
    text = head + sep + rest[:line_end] + "\n" + mark + rest[line_end:] if sep else text
    new.write_text(text, encoding="utf-8")
    changed = [new.relative_to(root).as_posix()]
    for path in link_files(root):
        body = path.read_text(encoding="utf-8")
        fixed = body.replace(f"PRD-v{old}-idea.md", new.name).replace(f"PRD v{old}-idea", f"PRD v{target}-idea")
        if fixed != body:
            path.write_text(fixed, encoding="utf-8")
            changed.append(path.relative_to(root).as_posix())
    return changed


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="고치지 않고 어긋난 것만 알립니다.")
    args = parser.parse_args(argv)
    try:
        if args.check:
            found = problems()
            for p in found:
                print(p, file=sys.stderr)
            return 1 if found else 0
        changed = sync()
        print("\n".join(changed) if changed else "변경 없음")
        left = problems()
        for p in left:
            print(p, file=sys.stderr)
        return 1 if left else 0
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
