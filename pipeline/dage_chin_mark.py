"""Compatibility aliases for the corrected Dage front-neck patch API.

New code must import from :mod:`dage_neck_patch`. This module remains so older
episode scripts and saved production notes do not break solely because the
mark was previously misidentified as a chin mark.
"""

from .dage_neck_patch import (  # noqa: F401
    FRONT_NECK_PATCH_CENTERS,
    LEGACY_MARK_VERSIONS,
    MARK_VERSION,
    mark_version_is_supported,
    require_front_neck_patch,
)

CHIN_PATCH_CENTERS = FRONT_NECK_PATCH_CENTERS
require_chin_patch = require_front_neck_patch
