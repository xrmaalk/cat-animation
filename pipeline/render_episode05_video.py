"""Render and encode the continuous 88-second Episode 04 animatic.

The scene remains authored at 24 fps. By default every second source frame is
rendered, producing a practical 12 fps animation cadence that FFmpeg packages
as a 24 fps H.264 review master without changing story timing.
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
    raise FileNotFoundError("FFmpeg not found; pass -- --ffmpeg path/to/ffmpeg.exe")


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.episode_plan import load_episode_plan


SEED, SHOTS = load_episode_plan(4, ROOT)
scene = bpy.context.scene
if scene.name != "EP04_Sunbeam" or scene.get("episode_number") != 4:
    raise RuntimeError("Open the built Episode 04 scene before rendering")
if scene.render.fps != int(SEED["fps"]):
    raise RuntimeError("Episode 04 FPS does not match the seed")

step = max(1, int(argument("--step", "2")))
source_fps = int(SEED["fps"])
sample_fps = source_fps / step
runtime = int(SEED["runtime_seconds"])
source_end_exclusive = runtime * source_fps
output_dir = ROOT / "renders"
output_dir.mkdir(exist_ok=True)
signature = sha256(Path(bpy.data.filepath).read_bytes()).hexdigest()[:12]
frames_dir = output_dir / f"episode04_continuous_frames_{signature}_step{step}"
frames_dir.mkdir(exist_ok=True)
destination = output_dir / "Purrcilla_Dixon_Dage_EP04_Sunbeam_Animatic.mp4"
temporary = output_dir / "Purrcilla_Dixon_Dage_EP04_Sunbeam_Animatic.part.mp4"
if destination.exists() and "--overwrite" not in sys.argv:
    raise FileExistsError(f"Output exists: {destination}; pass -- --overwrite")

scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = int(argument("--width", "640"))
scene.render.resolution_y = int(argument("--height", "360"))
scene.render.resolution_percentage = 100
if hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 8
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"

text_group = bpy.data.collections["NARRATION_TEXT_OFF"]
title = bpy.data.objects["EP04_TITLE_CARD"]
fact = bpy.data.objects["EP04_FACT_LABEL"]
narration = bpy.data.objects["EP04_OPTIONAL_NARRATION"]
backdrop = bpy.data.objects["EP04_TEXT_BACKDROP"]


def shot_at(frame):
    seconds = frame / source_fps
    for shot in SHOTS:
        start = int(shot["start_seconds"])
        end = start + int(shot["duration_seconds"])
        if start <= seconds < end:
            return shot
    return SHOTS[-1]


def configure_text(beat):
    show_title = beat == "TITLE"
    show_fact = beat == "FACT_LABEL"
    visible = show_title or show_fact
    text_group.hide_render = not visible
    text_group.hide_viewport = not visible
    title.hide_render = not show_title
    fact.hide_render = not show_fact
    narration.hide_render = True
    backdrop.hide_render = not visible


frame_paths = []
source_frames = list(range(0, source_end_exclusive, step))
for index, frame in enumerate(source_frames):
    frame_path = frames_dir / f"frame_{index:05d}.png"
    scene.frame_set(frame)
    configure_text(shot_at(frame)["beat"])
    if not frame_path.is_file() or frame_path.stat().st_size < 5000:
        scene.render.filepath = str(frame_path)
        bpy.ops.render.render(write_still=True)
    if index % max(1, round(sample_fps * 5)) == 0:
        print(
            "EP04_CONTINUOUS_PROGRESS", index, "of", len(source_frames),
            "source_frame", frame, scene.camera.name, flush=True,
        )
    frame_paths.append(frame_path)

configure_text("")
concat_path = frames_dir / "episode04_continuous.ffconcat"
duration = 1.0 / sample_fps
lines = ["ffconcat version 1.0"]
for frame_path in frame_paths:
    escaped = frame_path.resolve().as_posix().replace("'", "'\\''")
    lines.append(f"file '{escaped}'")
    lines.append(f"duration {duration:.10f}")
escaped_last = frame_paths[-1].resolve().as_posix().replace("'", "'\\''")
lines.append(f"file '{escaped_last}'")
concat_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

command = [
    ffmpeg_executable(), "-hide_banner", "-loglevel", "warning", "-y",
    "-f", "concat", "-safe", "0", "-i", str(concat_path),
    "-vf", f"fps={source_fps},format=yuv420p", "-t", str(runtime),
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-movflags", "+faststart", "-metadata", f"title={SEED['episode_title']}",
    str(temporary),
]
subprocess.run(command, check=True)
if not temporary.is_file() or temporary.stat().st_size < 1024:
    raise RuntimeError("FFmpeg did not produce a complete Episode 04 MP4")
temporary.replace(destination)
print("EP04_ANIMATIC_SAVED", destination, destination.stat().st_size, flush=True)
