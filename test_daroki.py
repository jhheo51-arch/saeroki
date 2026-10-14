import unittest

from daroki import Candidate, Preference, recommend


class RecommendTest(unittest.TestCase):
    def setUp(self):
        self.preference = Preference(
            interests=frozenset({"AI", "데이터"}),
            excluded=frozenset({"광고"}),
            context=frozenset({"비"}),
            max_popularity=70,
        )
        self.candidates = [
            Candidate("known", "이미 본 글", "https://example.com/known", ("AI",), "예시", "2026-10-14", 20),
            Candidate("ad", "광고 글", "https://example.com/ad", ("AI", "광고"), "예시", "2026-10-14", 10),
            Candidate("popular", "너무 유명한 글", "https://example.com/popular", ("AI",), "예시", "2026-10-14", 90),
            Candidate("rain", "비 오는 날의 데이터", "https://example.com/rain", ("데이터", "비"), "예시", "2026-10-14"),
            Candidate("ai", "작은 AI 연구 기록", "https://example.com/ai", ("AI",), "예시", "2026-10-14", 30),
        ]

    def test_filters_and_ranks_candidates(self):
        result = recommend(self.preference, self.candidates, frozenset({"known"}))
        self.assertEqual([item.candidate.id for item in result], ["rain", "ai"])

    def test_unknown_popularity_is_not_claimed_as_obscure(self):
        result = recommend(self.preference, self.candidates)
        rain = next(item for item in result if item.candidate.id == "rain")
        self.assertIn("단정하지 않음", rain.discovery_note)

    def test_invalid_limit_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend(self.preference, self.candidates, limit=0)


if __name__ == "__main__":
    unittest.main()
