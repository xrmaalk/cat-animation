"""Check current mascot assets before a new episode (or historical assets)."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.sprite_manifest import (
    CURRENT_MANIFEST,
    HISTORICAL_MANIFEST,
    frame_available,
    grid_geometry,
    load_manifest,
)


def image_info(path):
    with path.open("rb") as handle:
        header = handle.read(32)
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        return "PNG", struct.unpack(">II", header[16:24])
    if len(header) >= 25 and header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        if header[12:16] == b"VP8L" and header[20] == 0x2F:
            size_bits = int.from_bytes(header[21:25], "little")
            return "WEBP", ((size_bits & 0x3FFF) + 1,
                            ((size_bits >> 14) & 0x3FFF) + 1)
        if header[12:16] == b"VP8X" and len(header) >= 30:
            return "WEBP", (int.from_bytes(header[24:27], "little") + 1,
                            int.from_bytes(header[27:30], "little") + 1)
    raise ValueError(f"Unsupported image header: {path}")


def occupied_layout_matches(path, info):
    from PIL import Image

    columns, rows, cell_width, cell_height = grid_geometry(info)
    with Image.open(path) as image:
        if image.mode != "RGBA" or image.size != tuple(info["atlas_size"]):
            raise ValueError(f"Unexpected dimensions or alpha mode: {path}")
        alpha = image.getchannel("A")
        return all(
            (alpha.crop((column * cell_width, row * cell_height,
                         (column + 1) * cell_width,
                         (row + 1) * cell_height)).getbbox() is not None)
            == frame_available(info, row * columns + column)
            for row in range(rows)
            for column in range(columns)
        )


def audit(manifest_path=CURRENT_MANIFEST):
    manifest = load_manifest(manifest_path, ROOT)
    results = {}
    for name, info in manifest["characters"].items():
        source = ROOT / info["source"]
        atlas = ROOT / info["atlas"]
        checks = {
            "source_exists": source.is_file(),
            "atlas_exists": atlas.is_file(),
        }
        if source.is_file():
            checks["source_hash_matches"] = (
                sha256(source.read_bytes()).hexdigest() == info["source_sha256"]
            )
        if atlas.is_file():
            image_format, dimensions = image_info(atlas)
            checks["atlas_dimensions_match_manifest"] = (
                tuple(info["atlas_size"]) == dimensions
            )
            checks["atlas_format_matches_manifest"] = (
                image_format == info.get("atlas_format", "PNG")
            )
            columns, rows, cell_width, cell_height = grid_geometry(info)
            checks["atlas_grid_valid"] = (
                columns * cell_width == dimensions[0]
                and rows * cell_height == dimensions[1]
            )
            checks["mapped_poses_occupied"] = all(
                frame_available(info, index)
                for index in info["frame_map"].values()
            )
            if "row_frame_counts" in info:
                checks["occupied_cells_match_manifest"] = occupied_layout_matches(
                    atlas, info
                )
        results[name] = checks
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--historical", action="store_true",
                        help="Audit the Episodes 2–3 legacy atlas instead")
    args = parser.parse_args()
    results = audit(HISTORICAL_MANIFEST if args.historical else CURRENT_MANIFEST)
    print(json.dumps(results, indent=2))
    blocking_checks = {
        "atlas_exists",
        "atlas_dimensions_match_manifest",
        "atlas_format_matches_manifest",
        "atlas_grid_valid",
        "mapped_poses_occupied",
        "occupied_cells_match_manifest",
        "source_hash_matches",
    }
    ready = all(
        value
        for checks in results.values()
        for name, value in checks.items()
        if name in blocking_checks
    )
    print("ATLAS_REUSE_READY" if ready else "ATLAS_REUSE_BLOCKED")
    if not ready:
        sys.exit(1)
