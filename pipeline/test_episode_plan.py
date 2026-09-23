"""Runtime-policy regression tests for short and historical episodes."""

import unittest

from pipeline.episode_plan import (
    TARGET_RUNTIME_SECONDS,
    load_episode_plan,
    pacing_flags,
    runtime_bounds,
)


class EpisodePlanTests(unittest.TestCase):
    def test_new_episodes_target_ninety_seconds(self):
        self.assertEqual(TARGET_RUNTIME_SECONDS, 90)
        self.assertEqual(runtime_bounds(4), (60, 120))
        self.assertEqual(runtime_bounds(3, {"runtime_policy": "short"}),
                         (60, 120))

    def test_historical_episode_two_is_grandfathered(self):
        seed, shots = load_episode_plan(2)
        self.assertEqual(int(seed["runtime_seconds"]), 1020)
        self.assertEqual(len(shots), 26)
        self.assertEqual(runtime_bounds(3), (180, 300))

    def test_episode_four_is_short_contiguous_and_uses_current_art(self):
        seed, shots = load_episode_plan(4)
        self.assertEqual(int(seed["runtime_seconds"]), 88)
        self.assertEqual(seed["lead_character"], "Dage")
        self.assertEqual(
            seed["sprite_manifest"],
            "references/mascot_sprites/current_sprite_manifest.json",
        )
        self.assertEqual(len(shots), 18)
        self.assertEqual(pacing_flags(shots), [])

    def test_episode_five_is_short_role_aware_and_uses_current_art(self):
        seed, shots = load_episode_plan(5)
        self.assertEqual(int(seed["runtime_seconds"]), 86)
        self.assertEqual(seed["lead_character"], "Dixon")
        self.assertEqual(seed["performance_contract"],
                         "episode05_performance_contract.json")
        self.assertEqual(seed["sprite_manifest"],
                         "references/mascot_sprites/current_sprite_manifest.json")
        self.assertEqual(len(shots), 17)
        self.assertTrue(all("dixon_role" in shot for shot in shots))
        self.assertEqual(pacing_flags(shots), [])

    def test_long_shot_is_review_flag_not_automatic_rejection(self):
        shots = [
            {"shot": "S01", "duration_seconds": "8"},
            {"shot": "S02", "duration_seconds": "9"},
        ]
        self.assertEqual(pacing_flags(shots), ["S02 lasts 9 seconds"])


if __name__ == "__main__":
    unittest.main()
