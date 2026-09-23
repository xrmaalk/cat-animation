"""Split the mascot concept lineup into three transparent character textures.

Run with normal Python: ``python pipeline/prepare_mascot_sprites.py``.
Requires Pillow. The split columns match the checked concept PNG, so update
SPLITS if the lineup artwork is regenerated.
"""

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "references" / "Purrcilla_Dixon_Dage_MAALTECH_Sprite_Concept.png"
OUTPUT = ROOT / "references" / "mascot_sprites"
SPLITS = {
    "Cila": (0, 570),
    "Dixon": (570, 1114),
    "Dage": (1114, 1774),
}
PADDING = 8


def main():
    with Image.open(SOURCE) as source:
        image = source.convert("RGBA")
    if image.size != (1774, 887):
        raise ValueError(f"Expected the reviewed 1774x887 concept, found {image.size}")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    for name, (left, right) in SPLITS.items():
        region = image.crop((left, 0, right, image.height))
        # Ignore near-transparent antialias specks when computing the crop.
        opaque = region.getchannel("A").point(lambda alpha: 255 if alpha >= 8 else 0)
        box = opaque.getbbox()
        if box is None:
            raise ValueError(f"No visible pixels in the {name} region")
        x0, y0, x1, y1 = box
        x0, y0 = max(0, x0 - PADDING), max(0, y0 - PADDING)
        x1 = min(region.width, x1 + PADDING)
        y1 = min(region.height, y1 + PADDING)
        sprite = region.crop((x0, y0, x1, y1))
        destination = OUTPUT / f"{name}_Mascot_Idle.png"
        sprite.save(destination)
        print(f"SAVED {destination} {sprite.width}x{sprite.height}")


if __name__ == "__main__":
    main()
