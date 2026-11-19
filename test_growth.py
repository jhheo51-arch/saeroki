import unittest
import urllib.error
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from growth import (
    GRID_H,
    GRID_W,
    LEVELS,
    MAX_LEVEL,
    compute_score,
    fetch_owner_commit_shas,
    list_owned_repos,
    level_for_score,
    merge_visitors,
    merge_repo_visitors,
    read_repo_commits,
    update,
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

    def test_account_visitors_preserve_old_days_without_publishing_repo_names(self):
        old = {"visitors_by_day": {"2026-10-01": 2}}
        repos = ["jhheo51-arch/saeroki", "jhheo51-arch/memoive"]
        traffic = {
            "jhheo51-arch/saeroki": {"views": [{"timestamp": "2026-11-19T00:00:00Z", "uniques": 3}]},
            "jhheo51-arch/memoive": {"views": [{"timestamp": "2026-11-19T00:00:00Z", "uniques": 4}]},
        }
        merged = merge_repo_visitors(old, traffic)
        self.assertEqual(merged["2026-10-01"], 2)
        self.assertEqual(merged["2026-11-19"], 7)
        self.assertEqual(sum(merged.values()), 9)

    def test_owned_repo_list_uses_authenticated_account_endpoint(self):
        with patch("growth._get_json", return_value=[
            {"full_name": "jhheo51-arch/public", "owner": {"login": "jhheo51-arch"}, "private": False},
            {"full_name": "jhheo51-arch/private", "owner": {"login": "jhheo51-arch"}, "private": True},
        ]) as get_json:
            self.assertEqual(list_owned_repos("jhheo51-arch", "token"),
                             ["jhheo51-arch/private", "jhheo51-arch/public"])
        self.assertIn("/user/repos?", get_json.call_args.args[0])

    def test_account_commit_parser_skips_other_authors_and_generated_files(self):
        log = ("@aaa|2026-11-19\n10\t5\tsrc/app.py\n50\t0\tassets/saeroki-tree.svg\n"
               "@bbb|2026-11-19\n100\t0\tsrc/other.py\n"
               "@ccc|2026-11-18\n20\t10\tsrc/task.py\n")
        with TemporaryDirectory() as directory, patch("growth.subprocess.run") as run:
            run.side_effect = [type("Result", (), {"stdout": ""})(), type("Result", (), {"stdout": log})()]
            commits = read_repo_commits("jhheo51-arch/saeroki", {"aaa", "ccc"}, Path(directory), "jhheo51-arch", "token")
        self.assertEqual([(item["sha"], item["lines"]) for item in commits], [("aaa", 15), ("ccc", 30)])

    def test_new_empty_public_repository_has_no_work_points(self):
        empty = urllib.error.HTTPError("https://api.github.com", 409, "empty repository", {}, None)
        with patch("growth._get_json", side_effect=empty):
            self.assertEqual(fetch_owner_commit_shas("jhheo51-arch/empty", "jhheo51-arch", "token"), set())

    def test_account_update_uses_all_owned_repos_and_preserves_file_on_failure(self):
        with TemporaryDirectory() as directory:
            state_path = Path(directory) / "growth.json"
            assets_dir = Path(directory) / "assets"
            assets_dir.mkdir()
            state_path.write_text('{"visitors_by_day":{"2026-10-01":2},"score":2}', encoding="utf-8")
            repos = ["jhheo51-arch/saeroki", "jhheo51-arch/private"]
            with (patch("growth.list_owned_repos", return_value=repos),
                  patch("growth.fetch_traffic", side_effect=[{"views": []}, {"views": []}]),
                  patch("growth.fetch_stars", side_effect=[1, 2]),
                  patch("growth.fetch_owner_commit_shas", side_effect=[{"aaa"}, {"bbb"}]),
                  patch("growth.read_repo_commits", side_effect=[
                      [{"sha": "aaa", "author": "jhheo51-arch", "date": "2026-11-19", "lines": 50}],
                      [{"sha": "bbb", "author": "jhheo51-arch", "date": "2026-11-19", "lines": 0}],
                  ])):
                result = update(state_path, assets_dir, repos[0], "traffic-token", "api-token")
            self.assertEqual(result["repo_count"], 2)
            self.assertEqual(result["visitors_total"], 2)
            self.assertEqual(result["work"]["points"], 6)
            self.assertEqual(result["score"], 2 + 30 + 6)
            self.assertNotIn("private", state_path.read_text(encoding="utf-8"))
            before = state_path.read_text(encoding="utf-8")
            with (patch("growth.list_owned_repos", return_value=repos),
                  patch("growth.fetch_traffic", side_effect=PermissionError("token scope"))):
                with self.assertRaises(RuntimeError):
                    update(state_path, assets_dir, repos[0], "traffic-token", "api-token")
            self.assertEqual(state_path.read_text(encoding="utf-8"), before)

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
