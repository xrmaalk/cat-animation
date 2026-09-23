"""Check the frame-driven mascot short after rebuilding its .blend.

blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend \
  --python pipeline/verify_mascot_short.py
"""

import json
from hashlib import sha256
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.dage_neck_patch import (
    FRONT_NECK_PATCH_CENTERS,
    mark_version_is_supported,
)

MANIFEST = json.loads((ROOT / "references" / "mascot_sprites" /
                       "episode02_atlases" / "episode02_sprite_manifest.json")
                      .read_text(encoding="utf-8"))
scene = bpy.context.scene
checks = []


def check(condition, message):
    checks.append((bool(condition), message))
    if not condition:
        print("FAIL", message, flush=True)


check(scene.frame_start == 1 and scene.frame_end == 288 and scene.render.fps == 24,
      "12-second, 24 fps scene")
check(scene.camera is not None and scene.camera.name == "CAM_AnimatedShort",
      "original animated camera")
check(scene.get("mascot_sprite_version") == "animated_short_atlas_v1",
      "atlas version marker")
sprite_collection = bpy.data.collections.get("SPRITES_MAALTECH_LOOKDEV")
check(sprite_collection is not None and len(sprite_collection.objects) == 3,
      "exactly three mascot planes")
check(not any(bpy.data.objects.get(f"{name}_Mascot_Idle")
              for name in ("Cila", "Dixon", "Dage")), "old idle planes removed")

for name in ("Cila", "Dixon", "Dage"):
    sprite = bpy.data.objects.get(name)
    info = MANIFEST["characters"][name]
    check(sprite is not None and sprite.parent == bpy.data.objects.get(f"{name}_PROXY_ROOT"),
          f"{name} sprite follows original root")
    if sprite is None:
        continue
    check(sprite.get("sprite_valid_frames") == info["valid_frames"],
          f"{name} valid frame count")
    check(sprite.get("source_sheet") == info["source"],
          f"{name} source sheet metadata")
    image = sprite.active_material.node_tree.nodes.get("Image Texture").image
    check(image is not None and image.packed_file is not None and
          tuple(image.size) == tuple(info["atlas_size"]),
          f"{name} packed atlas")
    if name == "Dage" and image is not None and image.packed_file is not None:
        check(sha256(image.packed_file.data).hexdigest() ==
              sha256((ROOT / info["atlas"]).read_bytes()).hexdigest(),
              "Dage packed atlas matches revised source")
    drivers = sprite.active_material.node_tree.animation_data.drivers
    check(any(variable.targets[0].id == sprite and
              variable.targets[0].data_path == '["sprite_frame"]'
              for curve in drivers for variable in curve.driver.variables),
          f"{name} shader driver")
    if name == "Dage":
        paths = {variable.targets[0].data_path
                 for curve in drivers for variable in curve.driver.variables
                 if variable.targets[0].id == sprite}
        patch_version = (sprite.get("dage_front_neck_patch_art") or
                         sprite.get("dage_chin_art"))
        check(paths == {'["sprite_frame"]'} and
              mark_version_is_supported(patch_version) and
              sprite.active_material.node_tree.nodes.get("Dage Black Chin Spot") is None,
              "Dage uses the baked front-neck fur without a shader mark")
    action = sprite.animation_data.action if sprite.animation_data else None
    check(action is not None and action.name == f"ACT_MASCOT_SHORT_{name}_FRAMES",
          f"{name} keyed sprite action")
    if action:
        points = [point for layer in action.layers for strip in layer.strips
                  for slot in action.slots
                  for bag in [strip.channelbag(slot)] if bag
                  for curve in bag.fcurves for point in curve.keyframe_points]
        check(bool(points) and all(point.interpolation == "CONSTANT" for point in points),
              f"{name} stepped frame interpolation")
        if name == "Dage":
            curves = {curve.data_path: curve for layer in action.layers
                      for strip in layer.strips for slot in action.slots
                      for bag in [strip.channelbag(slot)] if bag
                      for curve in bag.fcurves}
            indices = {round(point.co.y) for point in
                       curves['["sprite_frame"]'].keyframe_points}
            check(set(curves) == {'["sprite_frame"]'} and
                  indices <= set(FRONT_NECK_PATCH_CENTERS),
                  "every Dage short pose has checked front-neck artwork")

for frame, expected in ((1, {"Cila": 0, "Dixon": 0, "Dage": 0}),
                        (132, {"Cila": 0, "Dixon": 3, "Dage": 0}),
                        (210, {"Cila": 14, "Dixon": 0, "Dage": 0}),
                        (258, {"Cila": 0, "Dixon": 0, "Dage": 42})):
    scene.frame_set(frame)
    for name, index in expected.items():
        check(bpy.data.objects[name].get("sprite_frame") == index,
              f"frame {frame}: {name} selects atlas cell {index}")

failed = sum(not passed for passed, _ in checks)
print(f"MASCOT_SHORT_VERIFIED {len(checks) - failed}/{len(checks)} checks", flush=True)
if failed:
    raise RuntimeError(f"{failed} mascot short checks failed")
