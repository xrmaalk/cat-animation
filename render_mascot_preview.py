"""Render a few Eevee frames from the mascot sprite scene for inspection.

blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend \
  --python render_mascot_preview.py
"""

from pathlib import Path

import bpy


root = Path(__file__).resolve().parent
destination = root / "preview_frames" / "mascot_sprites"
destination.mkdir(parents=True, exist_ok=True)
scene = bpy.context.scene
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for frame in (1, 132, 258):
    scene.frame_set(frame)
    scene.render.filepath = str(destination / f"frame_{frame:03}.png")
    bpy.ops.render.render(write_still=True)
    print("MASCOT_PREVIEW_SAVED", scene.render.filepath)
