"""Render seven Episode 03 story beats and one optional fact-text check.

blender --background Purrcilla_Dixon_Dage_EP03_Purr.blend \
  --python pipeline/render_episode03_preview.py
"""

from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.episode_plan import load_episode_plan
SEED, SHOTS = load_episode_plan(3, ROOT)
SHOT_BY_BEAT = {shot["beat"]: shot for shot in SHOTS}
OUT = ROOT / "preview_frames" / "episode03_purr"
OUT.mkdir(parents=True, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only = set(args[args.index("--only") + 1].split(",")
           ) if "--only" in args else set()
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 32
scene.render.image_settings.file_format = "PNG"

def frame_for(beat, fraction=0.55):
    shot = SHOT_BY_BEAT[beat]
    start = int(shot["start_seconds"])
    duration = int(shot["duration_seconds"])
    seconds = start + min(max(1.0, duration * fraction), duration - 1.0)
    return max(1, round(seconds * scene.render.fps))


frames = [
    ("cila_restless", "CILA_FEELS_RESTLESS"),
    ("cila_settles", "CILA_SETTLES"),
    ("first_purr", "FIRST_PURR"),
    ("cila_relaxes", "CILA_RELAXES"),
    ("dixon_listens", "DIXON_LISTENS"),
    ("shared_listening", "SHARED_LISTENING"),
    ("shared_final", "SHARED_FINAL_FRAME"),
]
for label, beat in frames:
    if only and label not in only:
        continue
    scene.frame_set(frame_for(beat))
    scene.render.filepath = str(OUT / (label + ".png"))
    bpy.ops.render.render(write_still=True)
    print("EP03_PREVIEW", label, scene.camera.name,
          scene.render.filepath, flush=True)

if not only or "fact_label_optional" in only:
    text_group = bpy.data.collections["NARRATION_TEXT_OFF"]
    text_group.hide_render = False
    text_group.hide_viewport = False
    scene.frame_set(frame_for("FACT_LABEL"))
    scene.render.filepath = str(OUT / "fact_label_optional.png")
    bpy.ops.render.render(write_still=True)
    print("EP03_PREVIEW", "fact_label_optional", scene.camera.name,
          scene.render.filepath, flush=True)
    text_group.hide_render = True
    text_group.hide_viewport = True
