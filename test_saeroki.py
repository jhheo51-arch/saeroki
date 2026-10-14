import tempfile
import unittest
from pathlib import Path

from saeroki import (
    Candidate,
    Preference,
    Profile,
    apply_feedback,
    load_profile,
    prepare_candidates,
    recommend,
    run_discovery,
    save_profile,
)
from source_collector import parse_public_metadata


class SaerokiTest(unittest.TestCase):
    def setUp(self):
        self.preference = Preference(
            interests=["AI", "데이터"],
            excluded=["광고"],
            context=["비"],
            max_popularity=70,
        )
        self.candidates = [
            Candidate("known", "이미 본 글", "https://example.com/known", ["AI"], "예시", "2026-10-14", 20),
            Candidate("ad", "광고 글", "https://example.com/ad", ["AI", "광고"], "예시", "2026-10-14", 10),
            Candidate("popular", "너무 유명한 글", "https://example.com/popular", ["AI"], "예시", "2026-10-14", 90),
            Candidate("rain", "비 오는 날의 데이터", "https://example.com/rain", ["데이터", "비"], "예시", "2026-10-14"),
            Candidate("ai", "작은 AI 연구 기록", "https://example.com/ai", ["AI"], "예시", "2026-10-14", 30),
        ]

    def test_filters_and_ranks_candidates(self):
        result = recommend(self.candidates, self.preference, {"known"})
        self.assertEqual([item.candidate.id for item in result], ["rain", "ai"])

    def test_unknown_popularity_is_not_claimed_as_obscure(self):
        result = recommend(self.candidates, self.preference)
        rain = next(item for item in result if item.candidate.id == "rain")
        self.assertIn("확인이 필요합니다", rain.cautions[0])

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend(self.candidates, self.preference, limit=0)

    def test_duplicate_tracking_urls_are_removed(self):
        duplicate = Candidate(
            "copy",
            "복사본",
            "https://example.com/ai?utm_source=letter",
            ["AI"],
            "다른 예시",
            "2026-10-14",
        )
        prepared, rejected = prepare_candidates([self.candidates[-1], duplicate])
        self.assertEqual([item.id for item in prepared], ["ai"])
        self.assertEqual(len(rejected), 1)

    def test_missing_source_is_rejected(self):
        invalid = Candidate(
            "invalid",
            "출처 없는 글",
            "https://example.com/invalid",
            ["AI"],
            "",
            "2026-10-14",
        )
        prepared, rejected = prepare_candidates([invalid])
        self.assertEqual(prepared, [])
        self.assertIn("출처가 없습니다", rejected[0]["reasons"])

    def test_profile_round_trip_and_feedback(self):
        profile = Profile("나", self.preference)
        apply_feedback(profile, "ai", "known")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            save_profile(profile, path)
            loaded = load_profile(path)
        self.assertEqual(loaded.feedback["ai"], "known")
        self.assertIn("ai", loaded.known_ids)

    def test_discovery_run_reviews_and_hides_rejected_candidates(self):
        profile = Profile("나", self.preference, known_ids=["known"])
        invalid = Candidate(
            "broken",
            "주소 오류",
            "not-a-url",
            ["AI"],
            "예시",
            "2026-10-14",
        )
        run = run_discovery(self.candidates + [invalid], profile, limit=3)
        self.assertEqual([item.candidate.id for item in run.recommendations], ["rain", "ai"])
        self.assertEqual(run.prepared_count, 5)
        self.assertEqual(len(run.rejected), 1)
        self.assertTrue(run.review.passed)

    def test_public_metadata_parser_prefers_open_graph_title(self):
        html = """
        <html><head>
          <title>페이지 제목</title>
          <meta property="og:title" content="공개 콘텐츠 제목">
          <meta property="og:description" content="짧은 설명">
          <meta property="article:published_time" content="2026-10-14">
        </head></html>
        """
        metadata = parse_public_metadata("https://example.com/article", html)
        self.assertEqual(metadata.title, "공개 콘텐츠 제목")
        self.assertEqual(metadata.description, "짧은 설명")
        self.assertEqual(metadata.published_at, "2026-10-14")


if __name__ == "__main__":
    unittest.main()
