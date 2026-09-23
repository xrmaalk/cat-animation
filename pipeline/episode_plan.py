"""Load and validate a script-driven episode without padding its runtime."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET_RUNTIME_SECONDS = 90
MIN_RUNTIME_SECONDS = 60
MAX_RUNTIME_SECONDS = 120
LEGACY_EPISODE12_SECONDS = 1020
ARCHIVED_EP03_MIN_SECONDS = 180
ARCHIVED_EP03_MAX_SECONDS = 300
PACING_REVIEW_SHOT_SECONDS = 8


def episode_directory(number, root=PROJECT_ROOT):
    return Path(root) / "episodes" / f"episode{int(number):02d}"


def runtime_bounds(number, seed=None):
    """Grandfather old plans; a replacement Episode 3 can opt into short."""
    if (seed or {}).get("runtime_policy") != "short":
        if int(number) <= 2:
            return LEGACY_EPISODE12_SECONDS, LEGACY_EPISODE12_SECONDS
        if int(number) == 3:
            return ARCHIVED_EP03_MIN_SECONDS, ARCHIVED_EP03_MAX_SECONDS
    return MIN_RUNTIME_SECONDS, MAX_RUNTIME_SECONDS


def pacing_flags(shots):
    """Surface long shots for human review; motion can justify a long take."""
    return [
        f"{shot['shot']} lasts {int(shot['duration_seconds'])} seconds"
        for shot in shots
        if int(shot["duration_seconds"]) > PACING_REVIEW_SHOT_SECONDS
    ]


def load_episode_plan(number, root=PROJECT_ROOT):
    """Return the seed and contiguous shots within the episode's policy."""
    folder = episode_directory(number, root)
    seed = json.loads(
        (folder / f"episode{int(number):02d}_seed.json").read_text(
            encoding="utf-8"
        )
    )
    if int(seed["episode_number"]) != int(number):
        raise ValueError(f"Episode number mismatch in {folder}")
    with (folder / seed["shotlist"]).open(
        newline="", encoding="utf-8"
    ) as handle:
        shots = list(csv.DictReader(handle))
    if not shots:
        raise ValueError(f"Episode {number:02d} has no shots")

    runtime = int(seed["runtime_seconds"])
    minimum, maximum = runtime_bounds(number, seed)
    if not minimum <= runtime <= maximum:
        raise ValueError(
            f"Episode {number:02d} must run {minimum}–{maximum} seconds; "
            f"got {runtime} seconds"
        )
    cursor = 0
    seen_shots = set()
    seen_beats = set()
    for shot in shots:
        shot_id = shot["shot"]
        beat = shot["beat"]
        start = int(shot["start_seconds"])
        duration = int(shot["duration_seconds"])
        if shot_id in seen_shots or beat in seen_beats:
            raise ValueError(f"Duplicate shot or beat at {shot_id}")
        if start != cursor or duration <= 0:
            raise ValueError(f"Non-contiguous or empty timing at {shot_id}")
        seen_shots.add(shot_id)
        seen_beats.add(beat)
        cursor += duration
    if cursor != runtime:
        raise ValueError(
            f"Episode {number:02d} shots end at {cursor}, seed says {runtime}"
        )
    return seed, shots
