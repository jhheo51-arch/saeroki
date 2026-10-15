import unittest

from growth import (
    GRID_H,
    GRID_W,
    LEVELS,
    MAX_LEVEL,
    compute_score,
    level_for_score,
    merge_visitors,
    render_current_svg,
    sprite_for,
    work_points,
)


class GrowthTest(unittest.TestCase):
    def test_hundred_levels_need_more_points_each_time(self):
        self.assertEqual(len(LEVELS), MAX_LEVEL)
        self.assertEqual(LEVELS[0].threshold, 0)
        gaps = [b.threshold - a.threshold for a, b in zip(LEVELS, LEVELS[1:])]
        self.assertTrue(all(gap > 0 for gap in gaps))
        self.assertEqual(gaps, sorted(gaps))

    def test_level_and_name_follow_score(self):
        self.assertEqual(level_for_score(0).level, 1)
        self.assertEqual(level_for_score(0).name, "새싹")
        self.assertEqual(level_for_score(LEVELS[9].threshold).name, "묘목")
        self.assertEqual(level_for_score(LEVELS[9].threshold - 1).level, 9)
        self.assertEqual(level_for_score(10**9).name, "세계수")

    def test_every_level_looks_different_and_keeps_face(self):
        sprites = [sprite_for(n) for n in range(1, MAX_LEVEL + 1)]
        self.assertEqual(len(set(sprites)), MAX_LEVEL)
        for n, sprite in enumerate(sprites, start=1):
            self.assertEqual(len(sprite), GRID_H, n)
            self.assertTrue(all(len(row) == GRID_W for row in sprite), n)
            self.assertEqual(sum(row.count("E") for row in sprite), 4, n)
            self.assertFalse(sprite[0].strip(), f"Lv.{n} 그림이 위쪽 끝에 닿음")

    def test_visitors_use_daily_uniques_and_accumulate(self):
        state = {"visitors_by_day": {"2026-09-01": 2}}
        payload = {"views": [
            {"timestamp": "2026-10-01T00:00:00Z", "count": 30, "uniques": 1},
            {"timestamp": "2026-10-02T00:00:00Z", "count": 4, "uniques": 3},
        ]}
        merged = merge_visitors(state, payload)
        self.assertEqual(merged["visitors_total"], 6)
        again = merge_visitors(merged, {"views": [{"timestamp": "2026-10-02T00:00:00Z", "count": 9, "uniques": 5}]})
        self.assertEqual(again["visitors_total"], 8)

    def test_work_points_skip_bot_and_cap_large_commits(self):
        commits = [
            {"author": "jhheo51-arch", "date": "2026-10-14", "lines": 20},
            {"author": "jhheo51-arch", "date": "2026-10-14", "lines": 120},
            {"author": "jhheo51-arch", "date": "2026-10-15", "lines": 5000},
            {"author": "saeroki-bot", "date": "2026-10-15", "lines": 300},
        ]
        work = work_points(commits)
        self.assertEqual(work["commits"], 3)
        self.assertEqual(work["active_days"], 2)
        self.assertEqual(work["points"], 3 + (0 + 2 + 4) + 3 * 2)

    def test_score_adds_visitors_stars_and_work(self):
        state = {"visitors_total": 12, "stars": 2, "work": {"points": 79}}
        self.assertEqual(compute_score(state), 12 + 20 + 79)

    def test_unknown_values_do_not_show_as_zero(self):
        state = {"visitors_total": None, "stars": None, "work": {"points": 79}, "updated_at": "2026-10-15T00:00:00+00:00"}
        state["score"] = compute_score(state)
        self.assertEqual(state["score"], 79)
        svg = render_current_svg(state)
        self.assertIn("순방문자 확인 전", svg)
        self.assertIn("스타 확인 전", svg)
        self.assertIn("Lv.7", svg)


if __name__ == "__main__":
    unittest.main()
