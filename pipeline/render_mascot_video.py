"""Render sprite-scene PNG frames in Blender 5.2, then encode a playable MP4.

From the project directory:
  blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend \
    --python pipeline/render_mascot_video.py

Pass ``-- --sample`` for a 24-frame check, ``-- --overwrite`` to replace an
earlier MP4, or ``-- --ffmpeg PATH`` if FFmpeg is not on PATH. Completed PNG
frames are reused when resuming an interrupted render of the same .blend.
The output is written to a temporary MP4 until encoding succeeds.
"""

from hashlib import sha256
from pathlib import Path
import os
import shutil
import subprocess
import sys

import bpy


def argument(name, default=None):
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return args[args.index(name) + 1] if name in args else default


def ffmpeg_executable():
    explicit = argument("--ffmpeg")
    found = explicit or shutil.which("ffmpeg")
    if found and Path(found).is_file():
        return found
    bundled = Path(r"C:\Program Files\Storyboarder\resources\app.asar.unpacked\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe")
    if bundled.is_file():
        return str(bundled)
    raise FileNotFoundError("FFmpeg was not found; pass -- --ffmpeg path/to/ffmpeg.exe")


root = Path(__file__).resolve().parents[1]
output_dir = root / "renders"
output_dir.mkdir(exist_ok=True)
sample = "--sample" in sys.argv
scene = bpy.context.scene
base = ("Purrcilla_Dixon_Dage_Mascot_Sheets"
        if scene.get("mascot_sprite_version") else "Purrcilla_Dixon_Dage_Mascot_Sprites")
label = base + ("_sample" if sample else "")
source_signature = sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()[:12]
frames_dir = output_dir / (label + "_frames_" + source_signature)
frames_dir.mkdir(exist_ok=True)
destination = output_dir / (label + ".mp4")
temporary = output_dir / (label + ".part.mp4")
if destination.exists() and "--overwrite" not in sys.argv:
    raise FileExistsError(f"Output exists: {destination}; pass -- --overwrite to replace it")

scene.render.engine = "BLENDER_EEVEE"
scene.frame_start = 1
scene.frame_end = 24 if sample else 288
scene.render.fps = 24
scene.render.resolution_x = 640 if sample else 1280
scene.render.resolution_y = 360 if sample else 720
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 16
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"

for frame in range(scene.frame_start, scene.frame_end + 1):
    frame_path = frames_dir / f"frame_{frame:04}.png"
    if frame_path.is_file() and frame_path.stat().st_size > 1024:
        continue
    scene.frame_set(frame)
    scene.render.filepath = str(frame_path)
    bpy.ops.render.render(write_still=True)
    print("FRAME_SAVED", frame, frame_path, flush=True)

command = [
    ffmpeg_executable(), "-hide_banner", "-loglevel", "warning", "-y",
    "-framerate", "24", "-start_number", "1",
    "-i", str(frames_dir / "frame_%04d.png"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(temporary),
]
subprocess.run(command, check=True)
if not temporary.is_file() or temporary.stat().st_size < 1024:
    raise RuntimeError("FFmpeg did not produce a complete MP4")
os.replace(temporary, destination)
print("PLAYABLE_VIDEO_SAVED", destination, destination.stat().st_size, flush=True)
