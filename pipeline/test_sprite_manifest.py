"""Small regression tests for current versus historical sprite selection."""

import unittest

from pipeline.sprite_manifest import (
    CURRENT_MANIFEST,
    HISTORICAL_MANIFEST,
    assert_current_dage_source,
    frame_available,
    grid_geometry,
    load_manifest,
    require_pose,
)


class SpriteManifestTests(unittest.TestCase):
    def test_current_dage_uses_approved_eight_by_eleven_sheet(self):
        manifest = load_manifest(CURRENT_MANIFEST)
        assert_current_dage_source(manifest)
        dage = manifest["characters"]["Dage"]
        self.assertEqual(grid_geometry(dage), (8, 11, 192, 208))
        self.assertEqual(sum(frame_available(dage, i) for i in range(88)), 74)
        self.assertEqual(require_pose(dage, "look_left"), 84)
        self.assertFalse(frame_available(dage, 7))

    def test_historical_sheet_keeps_old_dage_frames(self):
        dage = load_manifest(HISTORICAL_MANIFEST)["characters"]["Dage"]
        self.assertEqual(grid_geometry(dage), (7, 10, 192, 192))
        self.assertEqual(dage["atlas"],
                         "references/mascot_sprites/episode02_atlases/1.png")
        self.assertEqual(require_pose(dage, "enter_box"), 11)

    def test_historical_dixon_padding_is_not_a_pose(self):
        dixon = load_manifest(HISTORICAL_MANIFEST)["characters"]["Dixon"]
        self.assertFalse(frame_available(dixon, 63))


if __name__ == "__main__":
    unittest.main()
