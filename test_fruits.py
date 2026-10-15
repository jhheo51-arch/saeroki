"""루트에서 `python -m unittest`를 실행하면 fruits/ 아래 열매별 검사도 함께 돌립니다."""

import unittest
from pathlib import Path

FRUITS = Path(__file__).resolve().parent / "fruits"


def load_tests(loader, tests, pattern):
    for folder in sorted(p for p in FRUITS.iterdir() if p.is_dir()):
        if any(folder.glob("test_*.py")):
            tests.addTests(unittest.TestLoader().discover(str(folder), pattern="test_*.py", top_level_dir=str(folder)))
    return tests
