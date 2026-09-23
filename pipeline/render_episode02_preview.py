"""Render five Episode 02 story beats and one optional fact-text check.

blender --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend \
  --python pipeline/render_episode02_preview.py
"""

from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "preview_frames" / "episode02_box"
OUT.mkdir(parents=True, exist_ok=True)
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else set()
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 32
scene.render.image_settings.file_format = "PNG"

frames = [
    ("dage_notices", 118),
    ("dage_paw_tests", 195),
    ("box_flap_settles", 220),
    ("dage_enters", 275),
    ("dixon_observes", 360),
    ("cila_investigates", 500),
    ("shared_final", 920),
]
for label, seconds in frames:
    if only and label not in only:
        continue
    scene.frame_set(seconds * scene.render.fps)
    scene.render.filepath = str(OUT / (label + ".png"))
    bpy.ops.render.render(write_still=True)
    print("EP02_PREVIEW", label, scene.camera.name, scene.render.filepath, flush=True)

if not only or "fact_label_optional" in only:
    text_group = bpy.data.collections["NARRATION_TEXT_OFF"]
    text_group.hide_render = False
    text_group.hide_viewport = False
    scene.frame_set(660 * scene.render.fps)
    scene.render.filepath = str(OUT / "fact_label_optional.png")
    bpy.ops.render.render(write_still=True)
    print("EP02_PREVIEW", "fact_label_optional", scene.camera.name,
          scene.render.filepath, flush=True)
    text_group.hide_render = True
    text_group.hide_viewport = True
