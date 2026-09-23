"""Encode the rendered Workbench image sequence as an animated WebP preview."""

from pathlib import Path

from PIL import Image, features


if not features.check("webp_anim"):
    raise RuntimeError("This Pillow build does not support animated WebP")

root = Path(__file__).resolve().parents[1]
paths = sorted((root / "preview_frames" / "animated_short" / "sequence").glob("frame_*.png"))
if len(paths) != 144:
    raise RuntimeError(f"Expected 144 preview frames, found {len(paths)}")

frames = []
for path in paths:
    with Image.open(path) as source:
        frames.append(source.convert("RGB"))

output = root / "preview_frames" / "animated_short" / "Purrcilla_Dixon_Dage_Animated_Short_preview.webp"
frames[0].save(
    output,
    format="WEBP",
    save_all=True,
    append_images=frames[1:],
    duration=83,
    loop=0,
    quality=82,
    method=4,
)
print("ANIMATED_PREVIEW_SAVED", output)
