"""Read-only preflight for the next short episode.

    python pipeline/director.py check
    python pipeline/director.py check --episode NUMBER

Story creation remains a deliberate step after the user chooses an episode
subject. This preflight never creates, deletes, or renders project files.
"""

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.asset_audit import audit
from pipeline.episode_plan import (
    MAX_RUNTIME_SECONDS,
    MIN_RUNTIME_SECONDS,
    TARGET_RUNTIME_SECONDS,
    load_episode_plan,
    pacing_flags,
)
from pipeline.sprite_manifest import CURRENT_MANIFEST, load_manifest


REQUIRED_ASSET_CHECKS = {
    "source_exists",
    "atlas_exists",
    "source_hash_matches",
    "atlas_dimensions_match_manifest",
    "atlas_format_matches_manifest",
    "atlas_grid_valid",
    "mapped_poses_occupied",
    "occupied_cells_match_manifest",
}


def check_project(episode=None):
    assets = audit(CURRENT_MANIFEST)
    failures = [
        f"{character}.{name}"
        for character, checks in assets.items()
        for name, passed in checks.items()
        if name in REQUIRED_ASSET_CHECKS and not passed
    ]
    report = {
        "current_sprite_manifest": CURRENT_MANIFEST,
        "assets_ready": not failures,
        "asset_failures": failures,
        "current_dage_source": load_manifest()["characters"]["Dage"]["source"],
        "next_episode_target_seconds": TARGET_RUNTIME_SECONDS,
        "next_episode_runtime_seconds": [MIN_RUNTIME_SECONDS,
                                         MAX_RUNTIME_SECONDS],
    }
    report["ready"] = report["assets_ready"]
    if episode is not None:
        seed, shots = load_episode_plan(episode)
        uses_current = seed["sprite_manifest"] == CURRENT_MANIFEST
        if (episode >= 4 or seed.get("runtime_policy") == "short") and not uses_current:
            report["ready"] = False
            report["asset_failures"].append(
                "new_episode_must_use_current_sprite_manifest"
            )
        report["episode"] = {
            "number": episode,
            "title": seed["episode_title"],
            "runtime_seconds": int(seed["runtime_seconds"]),
            "shot_count": len(shots),
            "sprite_manifest": seed["sprite_manifest"],
            "uses_current_sprites": uses_current,
            "pacing_review": pacing_flags(shots),
        }
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check"])
    parser.add_argument("--episode", type=int,
                        help="also validate an existing episode's timing")
    args = parser.parse_args()
    try:
        report = check_project(args.episode)
    except (OSError, KeyError, ValueError) as exc:
        print(f"DIRECTOR_PREFLIGHT_ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
