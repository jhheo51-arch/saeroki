"""루트에서 `python -m unittest`를 실행하면 fruits/ 아래 열매별 검사도 함께 돌립니다."""

import unittest
from pathlib import Path

FRUITS = Path(__file__).resolve().parent / "fruits"


def load_tests(loader, tests, pattern):
    for folder in sorted(p for p in FRUITS.iterdir() if p.is_dir()):
        if any(folder.glob("test_*.py")):
            tests.addTests(unittest.TestLoader().discover(str(folder), pattern="test_*.py", top_level_dir=str(folder)))
    return tests


class IdeaPrdSyncTest(unittest.TestCase):
    """20번 심사단 PRD가 4번 검토관 PRD 버전을 따르는지(PRD v2.0-idea 10장)."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        path = Path(__file__).resolve().parent / "scripts" / "sync_idea_prd.py"
        spec = importlib.util.spec_from_file_location("sync_idea_prd", path)
        cls.sync = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.sync)

    def make_repo(self, root, reviewers=("2.0",), idea="2.0", skill="`--from <verdict.md>`"):
        docs = root / "docs"
        docs.mkdir()
        for v in reviewers:
            (docs / f"PRD-v{v}.md").write_text(f"# 새록이 4번 열매 PRD v{v}: 새록 검토관\n", encoding="utf-8")
        (docs / "PRD-v2.1.md").write_text("# 새록이 19번 열매 PRD v2.1: 새록 면접관\n", encoding="utf-8")
        (docs / f"PRD-v{idea}-idea.md").write_text(
            f"# 새록이 20번 열매 PRD v{idea}-idea: 새록 심사단\n\n"
            f"- 문서 버전: 4번 새록 검토관 PRD의 짝 문서. 검토관 [PRD v{idea}](PRD-v{idea}.md)을 따름(10장)\n\n본문 v{idea}\n",
            encoding="utf-8")
        (root / "README.md").write_text(f"[PRD v{idea}-idea](docs/PRD-v{idea}-idea.md)\n", encoding="utf-8")
        design = root / "fruits" / "04-prd-assistant" / "skills" / "design"
        design.mkdir(parents=True)
        (design / "SKILL.md").write_text(skill, encoding="utf-8")

    def test_repo_is_in_sync(self):
        self.assertEqual(self.sync.problems(self.sync.ROOT), [])

    def test_sync_renames_and_fixes_links(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root, reviewers=("2.0", "2.2", "2.10"), idea="2.0")
            self.assertTrue(self.sync.problems(root))
            changed = self.sync.sync(root, use_git=False)
            self.assertIn("docs/PRD-v2.10-idea.md", changed)
            self.assertFalse((root / "docs" / "PRD-v2.0-idea.md").exists())
            text = (root / "docs" / "PRD-v2.10-idea.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith("# 새록이 20번 열매 PRD v2.10-idea:"))
            self.assertIn("[PRD v2.10](PRD-v2.10.md)", text)
            self.assertIn("내용 다시 보기 전", text)
            self.assertIn("본문 v2.0", text)  # 본문은 그대로
            self.assertIn("docs/PRD-v2.10-idea.md", (root / "README.md").read_text(encoding="utf-8"))
            self.assertEqual(self.sync.problems(root), [])
            self.assertEqual(self.sync.sync(root, use_git=False), [])

    def test_missing_from_link_fails(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            self.make_repo(Path(tmp), skill="검토관 설계 스킬")
            self.assertTrue(any("--from" in p for p in self.sync.problems(Path(tmp))))

    def test_unknown_reviewer_title_fails_without_change(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root, reviewers=())
            with self.assertRaises(ValueError):
                self.sync.sync(root, use_git=False)
            self.assertTrue((root / "docs" / "PRD-v2.0-idea.md").exists())


class CharacterTest(unittest.TestCase):
    """에이전트별 새록이 그림(scripts/make_characters.py)이 모든 레벨에서 그려지는지."""

    @classmethod
    def setUpClass(cls):
        import importlib.util
        path = Path(__file__).resolve().parent / "scripts" / "make_characters.py"
        spec = importlib.util.spec_from_file_location("make_characters", path)
        cls.chars = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.chars)

    def test_every_character_renders_at_every_body_size(self):
        for key in self.chars.CHARACTERS:
            for level in (1, 13, 26, 50, 100):
                with self.subTest(key=key, level=level):
                    rows, colors = self.chars.sprite(key, level)
                    self.assertTrue(all(c == " " or c in colors for r in rows for c in r))
                    self.assertTrue(self.chars.render_png(key, level).startswith(b"\x89PNG"))

    def test_readme_shows_every_character(self):
        readme = (Path(__file__).resolve().parent / "README.md").read_text(encoding="utf-8")
        for key in self.chars.CHARACTERS:
            with self.subTest(key=key):
                self.assertIn(f"assets/characters/saeroki-{key}.png", readme)
