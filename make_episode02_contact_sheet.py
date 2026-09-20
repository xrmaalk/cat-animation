"""Assemble the Episode 02 inspection renders into one storyboard preview.

Run after render_episode02_preview.py: ``python make_episode02_contact_sheet.py``.
Requires Pillow.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
FOLDER = ROOT / "preview_frames" / "episode02_box"
ITEMS = [
    ("Dage notices the box", "dage_notices.png"),
    ("Dage tests the flap", "dage_paw_tests.png"),
    ("The flap settles", "box_flap_settles.png"),
    ("Dage enters", "dage_enters.png"),
    ("Dixon observes", "dixon_observes.png"),
    ("Cila investigates", "cila_investigates.png"),
    ("Optional fact label", "fact_label_optional.png"),
    ("Shared final frame", "shared_final.png"),
]
WIDTH, HEIGHT, LABEL_HEIGHT = 640, 360, 32


def main():
    canvas = Image.new("RGB", (2 * WIDTH, 4 * (HEIGHT + LABEL_HEIGHT)), "#1c1c24")
    draw = ImageDraw.Draw(canvas)
    font_path = Path("C:/Windows/Fonts/arial.ttf")
    font = ImageFont.truetype(str(font_path), 20) if font_path.is_file() else ImageFont.load_default()
    for index, (label, filename) in enumerate(ITEMS):
        source = FOLDER / filename
        if not source.is_file():
            raise FileNotFoundError(source)
        with Image.open(source) as opened:
            frame = opened.convert("RGB")
        if frame.size != (WIDTH, HEIGHT):
            raise ValueError(f"Unexpected preview size: {source}: {frame.size}")
        x = (index % 2) * WIDTH
        y = (index // 2) * (HEIGHT + LABEL_HEIGHT)
        draw.text((x + 12, y + 5), label, fill="#f8ecda", font=font)
        canvas.paste(frame, (x, y + LABEL_HEIGHT))
    output = FOLDER / "EP02_storyboard_preview.png"
    canvas.save(output)
    print("STORYBOARD_PREVIEW_SAVED", output)


if __name__ == "__main__":
    main()
