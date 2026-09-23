"""Render a 3-5 minute Episode 03 shot-hold animatic and encode it to MP4.

The Episode 03 project is an editorial animatic rather than continuous final
animation. This script renders one representative 1280x720 Eevee frame for
each of the 26 shots, then holds each frame for its CSV duration. Title and
fact cards are enabled only for their corresponding shots.

blender --background Purrcilla_Dixon_Dage_EP03_Purr.blend \
  --python pipeline/render_episode03_video.py

Pass ``-- --overwrite`` to replace an existing MP4 or ``-- --ffmpeg PATH``
when FFmpeg is not available at the detected location.
"""

from hashlib import sha256
from pathlib import Path
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
        return str(found)
    bundled = Path(
        r"C:\Program Files\Storyboarder\resources\app.asar.unpacked\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe"
    )
    if bundled.is_file():
        return str(bundled)
    raise FileNotFoundError(
        "FFmpeg was not found; pass -- --ffmpeg path/to/ffmpeg.exe"
    )


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.episode_plan import load_episode_plan
SEED, SHOTS = load_episode_plan(3, ROOT)

scene = bpy.context.scene
if scene.name != "EP03_Purr" or scene.get("episode_number") != 3:
    raise RuntimeError("Open the built Episode 03 scene before rendering")
if len(SHOTS) != 26:
    raise RuntimeError("Episode 03 requires exactly 26 shots")
runtime = int(SEED["runtime_seconds"])
if scene.render.fps != int(SEED["fps"]):
    raise RuntimeError("Episode 03 scene FPS does not match the seed")
if scene.frame_end != runtime * scene.render.fps:
    raise RuntimeError("Episode 03 scene range does not match the shot plan")

output_dir = ROOT / "renders"
output_dir.mkdir(exist_ok=True)
source_signature = sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()[:12]
frames_dir = output_dir / ("episode03_animatic_frames_" + source_signature)
frames_dir.mkdir(exist_ok=True)
destination = output_dir / "Purrcilla_Dixon_Dage_EP03_Purr_Animatic.mp4"
temporary = output_dir / "Purrcilla_Dixon_Dage_EP03_Purr_Animatic.part.mp4"
if destination.exists() and "--overwrite" not in sys.argv:
    raise FileExistsError(
        f"Output exists: {destination}; pass -- --overwrite to replace it"
    )

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 16
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"

text_group = bpy.data.collections["NARRATION_TEXT_OFF"]
title = bpy.data.objects["EP03_TITLE_CARD"]
fact = bpy.data.objects["EP03_FACT_LABEL"]
narration = bpy.data.objects["EP03_OPTIONAL_NARRATION"]


def configure_text(beat):
    show_title = beat == "TITLE"
    show_fact = beat == "FACT_LABEL"
    text_group.hide_render = not (show_title or show_fact)
    text_group.hide_viewport = not (show_title or show_fact)
    title.hide_render = not show_title
    fact.hide_render = not show_fact
    narration.hide_render = True
    bpy.context.view_layer.update()


frame_paths = []
for index, shot in enumerate(SHOTS, start=1):
    start = int(shot["start_seconds"])
    duration = int(shot["duration_seconds"])
    offset = 1.0 if shot["beat"] == "TITLE" else duration * 0.55
    seconds = start + min(offset, max(1.0, duration - 1.0))
    frame = max(1, round(seconds * scene.render.fps))
    frame_path = frames_dir / f"shot_{index:02d}.png"
    configure_text(shot["beat"])
    scene.frame_set(frame)
    if not frame_path.is_file() or frame_path.stat().st_size < 10000:
        scene.render.filepath = str(frame_path)
        bpy.ops.render.render(write_still=True)
        print(
            "EP03_SHOT_RENDERED",
            index,
            shot["shot"],
            shot["beat"],
            frame,
            scene.camera.name,
            frame_path,
            flush=True,
        )
    else:
        print("EP03_SHOT_REUSED", index, frame_path, flush=True)
    frame_paths.append(frame_path)

configure_text("")

concat_path = frames_dir / "episode03_concat.txt"
concat_lines = []
for shot, frame_path in zip(SHOTS, frame_paths):
    escaped = frame_path.resolve().as_posix().replace("'", "'\\''")
    concat_lines.append(f"file '{escaped}'")
    concat_lines.append(f"duration {int(shot['duration_seconds'])}")
escaped_last = frame_paths[-1].resolve().as_posix().replace("'", "'\\''")
concat_lines.append(f"file '{escaped_last}'")
concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

command = [
    ffmpeg_executable(),
    "-hide_banner",
    "-loglevel",
    "warning",
    "-y",
    "-f",
    "concat",
    "-safe",
    "0",
    "-i",
    str(concat_path),
    "-vf",
    f"fps={SEED['fps']},format=yuv420p",
    "-t",
    str(runtime),
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "20",
    "-movflags",
    "+faststart",
    "-metadata",
    f"title={SEED['episode_title']}",
    str(temporary),
]
subprocess.run(command, check=True)
if not temporary.is_file() or temporary.stat().st_size < 1024:
    raise RuntimeError("FFmpeg did not produce a complete Episode 03 MP4")
temporary.replace(destination)
print("EP03_ANIMATIC_SAVED", destination, destination.stat().st_size, flush=True)
