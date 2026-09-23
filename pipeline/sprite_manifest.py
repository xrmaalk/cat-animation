"""Load historical or current mascot assets without mixing their frame layouts."""

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HISTORICAL_MANIFEST = (
    "references/mascot_sprites/episode02_atlases/episode02_sprite_manifest.json"
)
CURRENT_MANIFEST = "references/mascot_sprites/current_sprite_manifest.json"


def load_manifest(path=CURRENT_MANIFEST, root=ROOT):
    """Replace whole character entries in an overlay; never inherit stale grid fields."""
    root = Path(root)
    data = json.loads((root / path).read_text(encoding="utf-8"))
    if "base_manifest" not in data:
        return data
    base = load_manifest(data["base_manifest"], root)
    merged = deepcopy(base)
    for key, value in data.items():
        if key not in {"base_manifest", "characters"}:
            merged[key] = value
    for name, info in data.get("characters", {}).items():
        merged["characters"][name] = info
    return merged


def grid_geometry(info):
    """Return (columns, rows, cell_width, cell_height) for a uniform atlas."""
    grid = info["atlas_grid"]
    columns, rows = int(grid["columns"]), int(grid["rows"])
    width, height = map(int, info["atlas_size"])
    if columns <= 0 or rows <= 0 or width % columns or height % rows:
        raise ValueError("Atlas dimensions do not divide evenly into its grid")
    cell_width, cell_height = width // columns, height // rows
    if grid.get("cell", cell_width) != cell_width:
        raise ValueError("Atlas cell size does not match its dimensions")
    if grid.get("cell_width", cell_width) != cell_width:
        raise ValueError("Atlas cell width does not match its dimensions")
    if grid.get("cell_height", cell_height) != cell_height:
        raise ValueError("Atlas cell height does not match its dimensions")
    return columns, rows, cell_width, cell_height


def frame_available(info, index):
    """Check the actual occupied slots, including sparse rows in the v2 sheet."""
    columns, rows, _, _ = grid_geometry(info)
    index = int(index)
    if index < 0 or index >= min(columns * rows,
                                int(info.get("valid_frames", columns * rows))):
        return False
    counts = info.get("row_frame_counts", [columns] * rows)
    if len(counts) != rows or any(count < 0 or count > columns for count in counts):
        raise ValueError("Invalid row-frame counts in sprite manifest")
    return index % columns < counts[index // columns]


def require_pose(info, pose):
    index = info["frame_map"][pose]
    if not frame_available(info, index):
        raise ValueError(f"Pose {pose} selects empty atlas cell {index}")
    return index


def assert_current_dage_source(manifest, root=ROOT):
    """Fail closed if the user-approved source has changed since the manifest."""
    info = manifest["characters"]["Dage"]
    source = Path(root) / info["source"]
    if not source.is_file():
        raise FileNotFoundError(source)
    if sha256(source.read_bytes()).hexdigest() != info["source_sha256"]:
        raise ValueError(f"Dage source changed; review and update {CURRENT_MANIFEST}")
    grid_geometry(info)
    for pose in info["frame_map"]:
        require_pose(info, pose)
