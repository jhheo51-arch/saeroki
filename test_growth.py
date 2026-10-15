import unittest

from growth import STAGES, GRID_W, GRID_H, compute_score, merge_views, render_current_svg, stage_for_score


class GrowthTest(unittest.TestCase):
    def test_stage_grows_with_score(self):
        self.assertEqual(stage_for_score(0).name, "새싹")
        self.assertEqual(stage_for_score(29).name, "새싹")
        self.assertEqual(stage_for_score(30).name, "묘목")
        self.assertEqual(stage_for_score(100).name, "어린 나무")
        self.assertEqual(stage_for_score(300).name, "나무")
        self.assertEqual(stage_for_score(5000).name, "큰 나무")

    def test_sprites_fit_grid_and_have_eyes(self):
        for stage in STAGES:
            self.assertEqual(len(stage.sprite), GRID_H, stage.name)
            self.assertTrue(all(len(row) == GRID_W for row in stage.sprite), stage.name)
            self.assertEqual(sum(row.count("E") for row in stage.sprite), 4, stage.name)

    def test_merge_views_accumulates_beyond_14_days(self):
        state = {"views_by_day": {"2026-09-01": 5}}
        payload = {"views": [
            {"timestamp": "2026-10-01T00:00:00Z", "count": 3},
            {"timestamp": "2026-10-02T00:00:00Z", "count": 4},
        ]}
        merged = merge_views(state, payload)
        self.assertEqual(merged["views_total"], 12)
        again = merge_views(merged, {"views": [{"timestamp": "2026-10-02T00:00:00Z", "count": 6}]})
        self.assertEqual(again["views_total"], 14)

    def test_unknown_views_do_not_count_as_zero_in_text(self):
        state = {"views_total": None, "commits": 35, "updated_at": "2026-10-15T00:00:00+00:00"}
        state["score"] = compute_score(state)
        self.assertEqual(state["score"], 35)
        svg = render_current_svg(state)
        self.assertIn("누적 조회 확인 전", svg)
        self.assertIn("묘목", svg)


if __name__ == "__main__":
    unittest.main()
