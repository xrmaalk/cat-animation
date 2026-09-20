"""Render inspection frames or a sequence for an animated WebP preview.

    blender --background Purrcilla_Dixon_Dage_Animated_Short.blend --python render_preview.py
    blender --background Purrcilla_Dixon_Dage_Animated_Short.blend --python render_preview.py -- --sequence
    python encode_preview.py

The preview uses Workbench shading for quick review; the .blend keeps its
original Eevee lighting and materials.
"""

import os
import sys

import bpy


root = os.path.dirname(os.path.abspath(__file__))
scene = bpy.context.scene
scene.render.engine = "BLENDER_WORKBENCH"
scene.display.shading.color_type = "MATERIAL"
scene.display.shading.light = "STUDIO"
scene.display.shading.show_shadows = True
scene.display.shading.show_cavity = True
scene.display.shading.cavity_type = "BOTH"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100

if "--sequence" in sys.argv:
    out_dir = os.path.join(root, "preview_frames", "sequence")
    os.makedirs(out_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    # A 12 fps preview keeps the file small; the editable .blend is 24 fps.
    for frame in range(scene.frame_start, scene.frame_end + 1, 2):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(out_dir, f"frame_{frame:03}.png")
        bpy.ops.render.render(write_still=True)
    print("PREVIEW_SEQUENCE_SAVED", out_dir)
else:
    out_dir = os.path.join(root, "preview_frames")
    os.makedirs(out_dir, exist_ok=True)
    scene.render.image_settings.file_format = "PNG"
    for frame in (1, 80, 132, 160, 225, 258):
        scene.frame_set(frame)
        scene.render.filepath = os.path.join(out_dir, f"frame_{frame:03}.png")
        bpy.ops.render.render(write_still=True)
        print("PREVIEW_FRAME_SAVED", frame, scene.render.filepath)
