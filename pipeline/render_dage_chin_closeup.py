"""Render a Dage portrait for checking the authored front-neck fur in Episode 02."""

from pathlib import Path

import bpy


scene = bpy.context.scene
scene.frame_set(294 * scene.render.fps)
scene.camera = bpy.data.objects["CAM_HeroPortrait_Dage"]
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 32
scene.render.image_settings.file_format = "PNG"
output = Path(__file__).resolve().parents[1] / "preview_frames" / "dage_front_neck_fur_ep02_curl.png"
scene.render.filepath = str(output)
bpy.ops.render.render(write_still=True)
print("DAGE_FRONT_NECK_FUR_PREVIEW", output, flush=True)
