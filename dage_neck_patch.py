"""Dage's black front-neck fur patch is part of the authored sprite art.

The authoritative visual references keep Dage's muzzle and chin white. The
irregular black marking begins below the jaw on the forward neck/ruff and
follows the neck fur downward. These cell-local pixel sites cover every Dage
frame selected by the current short and Episode 02 actions so atlas
preparation can detect a missing or washed-out front-neck patch.
"""

MARK_VERSION = "Dage_baked_black_front_neck_fur_v3"
LEGACY_MARK_VERSIONS = frozenset({"Dage_baked_black_chin_fur_v2"})

# Top-left-origin coordinates inside a 192x192 normalized atlas cell.
# The coordinates sample the black front-neck marking inside the white ruff;
# they are not chin coordinates.
FRONT_NECK_PATCH_CENTERS = {
    0: (98, 100),
    3: (85, 101),
    6: (90, 100),
    9: (117, 106),
    10: (121, 113),
    11: (134, 106),
    12: (134, 104),
    13: (104, 107),
    26: (103, 130),
    37: (87, 99),
    41: (90, 97),
    42: (110, 97),
    55: (105, 99),
}


def require_front_neck_patch(index):
    """Reject a newly selected pose until its authored neck mark is inspected."""
    index = int(index)
    if index not in FRONT_NECK_PATCH_CENTERS:
        raise ValueError(
            f"Dage sprite frame {index} needs a front-neck-patch check before use"
        )
    return FRONT_NECK_PATCH_CENTERS[index]


def mark_version_is_supported(value):
    """Accept the corrected marker and existing scenes with the legacy label."""
    return value == MARK_VERSION or value in LEGACY_MARK_VERSIONS
