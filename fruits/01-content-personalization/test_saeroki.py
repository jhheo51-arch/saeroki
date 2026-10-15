import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

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
    schedule_for_time,
    scheduled_recommend,
)
from source_collector import PublicLink, collect_confirmed_sources, parse_public_metadata, parse_rss
from weather import parse_weather_payload, weather_code_label
from music_candidates import load_music_candidates, validate_music_candidate


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

    def test_interest_and_excluded_keywords_are_matched_in_title(self):
        profile = Preference(["기획"], excluded=["광고성"])
        candidates = [
            Candidate("good", "기획 실험 기록", "https://example.com/good", [], "기술 블로그", "2026-10-15"),
            Candidate("bad", "광고성 기획 안내", "https://example.com/bad", [], "기술 블로그", "2026-10-15"),
        ]
        result = recommend(candidates, profile, allow_unmatched=False)
        self.assertEqual([item.candidate.id for item in result], ["good"])

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

    def test_feedback_is_applied_to_the_next_recommendation(self):
        profile = Profile("나", self.preference)
        apply_feedback(profile, "rain", "not_interested")
        run = run_discovery(self.candidates, profile, limit=5)
        self.assertNotIn("rain", [item.candidate.id for item in run.recommendations])
        self.assertEqual(profile.feedback["rain"], "not_interested")

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

    def test_collection_skips_unconfirmed_sources(self):
        records = [
            {
                "name": "공개 예시",
                "url": "https://example.com",
                "category": "기술 블로그",
                "status": "confirmed_public",
            },
            {
                "name": "확인 전 예시",
                "url": "https://example.org",
                "category": "기술 블로그",
                "status": "needs_url",
            },
        ]
        with patch(
            "source_collector.fetch_public_metadata",
            side_effect=OSError("network disabled in test"),
        ):
            candidates, errors = collect_confirmed_sources(records)
        self.assertEqual(candidates, [])
        self.assertEqual(len(errors), 1)

    def test_collection_expands_public_list_links(self):
        records = [
            {
                "name": "공개 목록",
                "url": "https://example.com/list",
                "collection_mode": "public_list",
                "access_status": "confirmed_public",
            }
        ]
        with patch(
            "source_collector.fetch_public_links",
            return_value=[PublicLink("https://example.com/article", "개별 글")],
        ):
            candidates, errors = collect_confirmed_sources(records)
        self.assertEqual(errors, [])
        self.assertEqual(candidates[0].title, "개별 글")
        self.assertEqual(candidates[0].url, "https://example.com/article")

    def test_collection_reads_public_json_articles(self):
        records = [
            {
                "name": "뉴닉 주간 에디터 픽",
                "url": "https://newneek.co/issues/43",
                "api_url": "https://api.newneek.co/product/v1/issues/43/articles?page=1",
                "collection_mode": "json_articles",
                "access_status": "confirmed_public",
            }
        ]
        payload = {
            "articles": [
                {
                    "id": 123,
                    "title": "공개 글",
                    "dtPublished": "2026-10-14T00:00:00+09:00",
                    "meta": {
                        "countReads": 42,
                        "user": {"name": "뉴닉"},
                    },
                }
            ]
        }
        with patch("source_collector.fetch_public_json", return_value=payload):
            candidates, errors = collect_confirmed_sources(records)
        self.assertEqual(errors, [])
        self.assertEqual(candidates[0].id, "newneek-123")
        self.assertEqual(candidates[0].popularity, 42)
        self.assertEqual(candidates[0].published_at, "2026-10-14T00:00:00+09:00")

    def test_schedule_uses_seoul_time_boundaries(self):
        mode, slots = schedule_for_time(datetime.fromisoformat("2026-10-15T07:30:00+09:00"))
        self.assertEqual(mode, "morning_commute")
        self.assertEqual([(slot.content_type, slot.limit) for slot in slots], [
            ("music", 1), ("technology_blog", 1), ("newsletter", 1)
        ])
        mode, slots = schedule_for_time(datetime.fromisoformat("2026-10-15T20:00:00+09:00"))
        self.assertIsNone(mode)
        self.assertEqual(slots, [])

    def test_scheduled_recommendation_selects_by_content_type(self):
        profile = Profile("나", Preference(["기획", "발라드"]))
        candidates = [
            Candidate("music", "숨은 발라드", "https://example.com/music", ["발라드"], "음악", "2026-10-15", content_type="music"),
            Candidate("tech", "기획 기록", "https://example.com/tech", ["기획"], "기술 블로그", "2026-10-15", content_type="technology_blog"),
            Candidate("news", "업무 뉴스레터", "https://example.com/news", ["기획"], "뉴스레터", "2026-10-15", content_type="newsletter"),
        ]
        run = scheduled_recommend(
            candidates,
            profile,
            datetime.fromisoformat("2026-10-15T08:00:00+09:00"),
        )
        self.assertEqual(set(run.recommendations), {"music", "technology_blog", "newsletter"})
        self.assertEqual([item.candidate.id for item in run.recommendations["music"]], ["music"])

    def test_weather_condition_is_added_to_music_reason(self):
        profile = Profile("나", Preference(["발라드"]))
        candidate = Candidate(
            "rain-song", "비 오는 날의 발라드", "https://example.com/rain-song",
            ["발라드", "비"], "음악", "2026-10-15", content_type="music",
        )
        run = scheduled_recommend(
            [candidate], profile, datetime.fromisoformat("2026-10-15T08:00:00+09:00"), "비"
        )
        self.assertIn("서울 날씨: 비", run.recommendations["music"][0].reasons)

    def test_rss_parser_creates_typed_candidates(self):
        xml = "<rss><channel><item><title>기술 글</title><link>https://example.com/post</link><pubDate>2026-10-15</pubDate></item></channel></rss>"
        candidates = parse_rss(xml, "예시 기술 블로그", "기술 블로그", "2026-10-15")
        self.assertEqual(candidates[0].content_type, "technology_blog")
        self.assertEqual(candidates[0].title, "기술 글")

    def test_prepare_candidates_rejects_same_title_from_two_feeds(self):
        first = Candidate("one", "같은 글", "https://one.example/a", ["기술"], "one", "2026-10-15")
        second = Candidate("two", "같은 글!", "https://two.example/b", ["기술"], "two", "2026-10-15")
        prepared, rejected = prepare_candidates([first, second])
        self.assertEqual([item.id for item in prepared], ["one"])
        self.assertIn("같은 제목의 후보가 이미 있습니다", rejected[0]["reasons"])

    def test_weather_payload_maps_open_meteo_code(self):
        observation = parse_weather_payload({
            "current": {
                "weather_code": 61,
                "temperature_2m": 18.5,
                "time": "2026-10-15T08:00",
            }
        })
        self.assertEqual(weather_code_label(61), "비")
        self.assertEqual(observation.condition, "비")
        self.assertEqual(observation.temperature_c, 18.5)

    def test_manual_music_candidate_requires_youtube_link(self):
        candidate = Candidate(
            "song", "숨은 발라드", "https://music.youtube.com/watch?v=abc",
            ["발라드", "비"], "수동 목록", "2026-10-15", content_type="music",
        )
        self.assertEqual(validate_music_candidate(candidate), [])

    def test_manual_music_candidate_rejects_other_sites(self):
        candidate = Candidate(
            "song", "숨은 발라드", "https://example.com/song",
            ["발라드"], "수동 목록", "2026-10-15", content_type="music",
        )
        self.assertIn("YouTube 또는 YouTube Music 주소가 아닙니다", validate_music_candidate(candidate))


if __name__ == "__main__":
    unittest.main()
