"""Assemble Episode 04 inspection renders into a labelled contact sheet."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "preview_frames" / "episode04_sunbeam"
ITEMS = [
    ("Dage finds the sunbeam", "dage_finds_sunbeam.png"),
    ("The light slips away", "sunbeam_slips.png"),
    ("Dage marks position one", "dage_first_marker.png"),
    ("Dixon checks the window", "dixon_checks_window.png"),
    ("Purrcilla helps", "purrcilla_brings_marker.png"),
    ("Dage compares the trail", "dage_compares.png"),
    ("Purrcilla tests a shadow", "purrcilla_shadow_test.png"),
    ("Optional fact label", "fact_label_optional.png"),
    ("All three share the beam", "shared_sunbeam.png"),
]
WIDTH, HEIGHT, LABEL_HEIGHT = 640, 360, 34


def main():
    columns, rows = 3, 3
    canvas = Image.new(
        "RGB", (columns * WIDTH, rows * (HEIGHT + LABEL_HEIGHT)), "#191722"
    )
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
        x = (index % columns) * WIDTH
        y = (index // columns) * (HEIGHT + LABEL_HEIGHT)
        draw.text((x + 12, y + 6), label, fill="#f7e8c7", font=font)
        canvas.paste(frame, (x, y + LABEL_HEIGHT))
    output = FOLDER / "EP04_storyboard_preview.png"
    canvas.save(output)
    print("EP04_STORYBOARD_PREVIEW_SAVED", output)


if __name__ == "__main__":
    main()
