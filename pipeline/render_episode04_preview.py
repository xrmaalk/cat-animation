"""Render representative Episode 04 review frames from the continuous scene."""

from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.episode_plan import load_episode_plan


SEED, SHOTS = load_episode_plan(4, ROOT)
SHOT_BY_BEAT = {shot["beat"]: shot for shot in SHOTS}
OUT = ROOT / "preview_frames" / "episode04_sunbeam"
OUT.mkdir(parents=True, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else set()

scene = bpy.context.scene
if scene.name != "EP04_Sunbeam" or scene.get("episode_number") != 4:
    raise RuntimeError("Open the built Episode 04 scene before rendering")
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
if hasattr(scene.eevee, "taa_render_samples"):
    scene.eevee.taa_render_samples = 24
scene.render.image_settings.file_format = "PNG"


def frame_for(beat, fraction=0.55):
    shot = SHOT_BY_BEAT[beat]
    start = int(shot["start_seconds"])
    duration = int(shot["duration_seconds"])
    seconds = start + min(max(0.5, duration * fraction), duration - 0.25)
    return round(seconds * scene.render.fps)


frames = [
    ("dage_finds_sunbeam", "DAGE_FINDS_WARM_SPOT"),
    ("sunbeam_slips", "SUNBEAM_SLIPS"),
    ("dage_first_marker", "FIRST_MARKER"),
    ("dixon_checks_window", "DIXON_CHECKS_WINDOW"),
    ("purrcilla_brings_marker", "PURRCILLA_BRINGS_MARKER"),
    ("dage_compares", "DAGE_COMPARES"),
    ("purrcilla_shadow_test", "PURRCILLA_TESTS_SHADOW"),
    ("shared_sunbeam", "SHARED_SUNBEAM"),
]
for label, beat in frames:
    if only and label not in only:
        continue
    scene.frame_set(frame_for(beat))
    scene.render.filepath = str(OUT / (label + ".png"))
    bpy.ops.render.render(write_still=True)
    print("EP04_PREVIEW", label, scene.camera.name, scene.render.filepath, flush=True)

if not only or "fact_label_optional" in only:
    group = bpy.data.collections["NARRATION_TEXT_OFF"]
    title = bpy.data.objects["EP04_TITLE_CARD"]
    fact = bpy.data.objects["EP04_FACT_LABEL"]
    narration = bpy.data.objects["EP04_OPTIONAL_NARRATION"]
    backdrop = bpy.data.objects["EP04_TEXT_BACKDROP"]
    group.hide_render = False
    group.hide_viewport = False
    title.hide_render = True
    fact.hide_render = False
    narration.hide_render = True
    backdrop.hide_render = False
    scene.frame_set(frame_for("FACT_LABEL"))
    scene.render.filepath = str(OUT / "fact_label_optional.png")
    bpy.ops.render.render(write_still=True)
    print("EP04_PREVIEW fact_label_optional", scene.camera.name,
          scene.render.filepath, flush=True)
    group.hide_render = True
    group.hide_viewport = True
    fact.hide_render = True
    backdrop.hide_render = True
