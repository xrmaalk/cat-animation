"""Validate and repack the supplied character sheets for Episode 02.

Run with the system Python: ``python prepare_episode02_sprites.py``.
Requires Pillow and NumPy. It reads the supplied PNGs and creates new atlases;
the originals are never modified. The source has seven columns and transparent
row gutters. Cila and Dage have ten rows; Dixon has nine.
"""

from hashlib import sha256
import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "references" / "mascot_sprites"
OUTPUT_DIR = SOURCE_DIR / "episode02_atlases"
CELL = 192
COLUMNS = 7
ATLAS_ROWS = 10
SOURCES = {
    "Cila": "Purrcilla_MAALTECH_Mascot_Spritesheet.png",
    "Dixon": "Dixon_MAALTECH_Mascot_Spritesheet.png",
    "Dage": "Dage_MAALTECH_Mascot_Spritesheet.png",
}

# Curated from the numbered source-sheet inspection, zero-based in source
# row-major order. The same indices apply in the normalized atlas.
FRAME_MAP = {
    "Cila": {"idle": 0, "curious": 5, "approach": 17, "investigate": 31,
             "lap_loaf": 40, "shared_idle": 0},
    "Dixon": {"idle": 0, "curious": 3, "observe": 43,
              "window_report": 6, "look_back": 55, "shared_idle": 0},
    "Dage": {"idle": 0, "curious": 6, "sniff": 37, "paw_test": 3,
             "enter_box": 11, "curl_in_box": 26, "look_back": 55,
             "shared_idle": 42},
}


def runs_where(values, predicate):
    runs = []
    start = None
    for index, value in enumerate(values):
        if predicate(value):
            if start is None:
                start = index
        elif start is not None:
            runs.append((start, index - 1))
            start = None
    if start is not None:
        runs.append((start, len(values) - 1))
    return runs


def row_edges(mask):
    counts = mask.sum(axis=1)
    gutters = [pair for pair in runs_where(counts, lambda n: n <= 3)
               if pair[1] - pair[0] + 1 >= 2]
    internal = [(start + end) // 2 for start, end in gutters
                if start > 20 and end < mask.shape[0] - 20]
    edges = [0, *internal, mask.shape[0]]
    if any(b - a < 80 for a, b in zip(edges, edges[1:])):
        raise ValueError(f"Unexpected narrow row in detected sheet: {edges}")
    return edges


def column_edges(mask, y0, y1):
    width = mask.shape[1]
    counts = mask[y0:y1].sum(axis=0)
    edges = [0]
    for column in range(1, COLUMNS):
        expected = round(column * width / COLUMNS)
        low = max(1, expected - 24)
        high = min(width - 1, expected + 25)
        positions = np.arange(low, high)
        empty = positions[counts[low:high] <= 3]
        if len(empty):
            boundary = int(empty[np.argmin(abs(empty - expected))])
        else:
            boundary = int(positions[np.argmin(counts[low:high])])
        edges.append(boundary)
    edges.append(width)
    if any(b - a < 100 for a, b in zip(edges, edges[1:])):
        raise ValueError(f"Unexpected narrow column in row {y0}:{y1}: {edges}")
    return edges


def process_character(name, filename):
    path = SOURCE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(path)
    with Image.open(path) as opened:
        if opened.mode != "RGBA":
            raise ValueError(f"{path.name} must have a transparent alpha channel")
        image = opened.copy()
    alpha = np.asarray(image.getchannel("A"))
    if int(alpha.min()) != 0 or int(alpha.max()) != 255:
        raise ValueError(f"{path.name} does not have expected transparent and opaque pixels")
    if any(int(alpha[y, x]) > 0 for x, y in
           ((0, 0), (image.width - 1, 0), (0, image.height - 1),
            (image.width - 1, image.height - 1))):
        raise ValueError(f"{path.name} has nontransparent corner pixels")

    mask = alpha >= 16
    y_edges = row_edges(mask)
    rows = len(y_edges) - 1
    if rows not in (9, 10):
        raise ValueError(f"Unexpected grid in {path.name}: {COLUMNS}x{rows}")
    frame_count = COLUMNS * rows
    if max(FRAME_MAP[name].values()) >= frame_count:
        raise ValueError(f"A mapped pose is outside {path.name}'s {frame_count} frames")

    atlas = Image.new("RGBA", (COLUMNS * CELL, ATLAS_ROWS * CELL), (0, 0, 0, 0))
    x_edges_by_row = []
    foot_rows = []
    for row in range(rows):
        y0, y1 = y_edges[row:row + 2]
        x_edges = column_edges(mask, y0, y1)
        x_edges_by_row.append(x_edges)
        for col in range(COLUMNS):
            x0, x1 = x_edges[col:col + 2]
            source_cell = image.crop((x0, y0, x1, y1))
            if source_cell.width > CELL or source_cell.height > CELL - 4:
                raise ValueError(f"Source cell too large: {name} row {row}, col {col}")
            x = col * CELL + (CELL - source_cell.width) // 2
            y = row * CELL + CELL - source_cell.height - 4
            atlas.alpha_composite(source_cell, (x, y))
            bbox = source_cell.getchannel("A").getbbox()
            foot_rows.append(None if bbox is None else y + bbox[3] - row * CELL)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    atlas_path = OUTPUT_DIR / f"{name}_EP02_Atlas.png"
    atlas.save(atlas_path)
    return {
        "source": str(path.relative_to(ROOT)).replace("\\", "/"),
        "source_sha256": sha256(path.read_bytes()).hexdigest(),
        "source_size": list(image.size),
        "source_alpha_range": [int(alpha.min()), int(alpha.max())],
        "source_grid": {"columns": COLUMNS, "rows": rows, "frames": frame_count},
        "source_row_edges": y_edges,
        "source_column_edges_by_row": x_edges_by_row,
        "atlas": str(atlas_path.relative_to(ROOT)).replace("\\", "/"),
        "atlas_size": list(atlas.size),
        "atlas_grid": {"columns": COLUMNS, "rows": ATLAS_ROWS, "cell": CELL},
        "valid_frames": frame_count,
        "foot_pixel_range": [min(x for x in foot_rows if x is not None),
                             max(x for x in foot_rows if x is not None)],
        "frame_map": FRAME_MAP[name],
    }


def main():
    characters = {name: process_character(name, filename)
                  for name, filename in SOURCES.items()}
    manifest = {
        "note": "Normalized 7x10 atlases derived from the supplied artwork. Dixon's final atlas row is transparent padding because the source has 7x9 cells.",
        "characters": characters,
    }
    path = OUTPUT_DIR / "episode02_sprite_manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    for name, info in characters.items():
        print(name, info["source_grid"], info["atlas_size"], info["foot_pixel_range"])
    print("MANIFEST_SAVED", path)


if __name__ == "__main__":
    main()
