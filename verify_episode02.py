"""Audit Episode 02 in Blender and write a machine-readable verification file.

blender --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend \
  --python verify_episode02.py
"""

import csv
from hashlib import sha256
import json
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parent
SEED = json.loads((ROOT / "episode02_seed.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / SEED["sprite_manifest"]).read_text(encoding="utf-8"))
with (ROOT / SEED["shotlist"]).open(newline="", encoding="utf-8") as handle:
    SHOTS = list(csv.DictReader(handle))
scene = bpy.context.scene
checks = {}


def check(label, condition):
    checks[label] = bool(condition)
    if not condition:
        raise AssertionError(label)


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


check("separate_ep02_scene", scene.name == "EP02_Cardboard_Box")
check("episode_seed_properties", all(scene.get(key) == SEED[key] for key in
      ("episode_number", "episode_title", "episode_seed", "discovery_prop",
       "discovery_collection", "lead_character")))
check("timing_preserved", scene.frame_end == 24480 and scene.render.fps == 24)
check("box_study_and_prop", bpy.data.collections.get("SET_BoxStudy") is not None
      and bpy.data.objects.get("PROP_CardboardBox") is not None)

holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
tracks = {track.name: track for track in holder.animation_data.nla_tracks}
check("ep01_editorial_preserved", "EP01_BEATS" in tracks and
      len(tracks["EP01_BEATS"].strips) == 26 and tracks["EP01_BEATS"].mute)
check("ep02_editorial_modular", "EP02_BEATS" in tracks and
      len(tracks["EP02_BEATS"].strips) == 26)
check("ep01_actions_preserved", sum(a.name.startswith("ACT_S") for a in bpy.data.actions) >= 26)
check("ep02_shot_data", len(SHOTS) == 26 and
      int(SHOTS[-1]["start_seconds"]) + int(SHOTS[-1]["duration_seconds"]) == 1020)

markers = [marker for marker in scene.timeline_markers if marker.name.startswith("EP02_")]
check("camera_markers", len(markers) == 26 and all(marker.camera for marker in markers))
for shot in SHOTS:
    scene.frame_set(int(shot["start_seconds"]) * scene.render.fps)
    check("camera_" + shot["shot"], scene.camera.name == shot["camera"])

materials = []
images = []
for name in ("Cila", "Dixon", "Dage"):
    sprite = bpy.data.objects.get("SPRITE_" + name)
    group = bpy.data.collections.get("CHAR_" + name)
    info = MANIFEST["characters"][name]
    check("sprite_" + name, sprite is not None and sprite.name in group.objects)
    check("sprite_property_" + name, sprite.get("sprite_frame") is not None and
          sprite.get("sprite_valid_frames") == info["valid_frames"])
    check("source_hash_" + name,
          sha256((ROOT / info["source"]).read_bytes()).hexdigest() == info["source_sha256"])
    check("source_grid_" + name,
          info["source_grid"]["columns"] == 7 and
          info["source_grid"]["rows"] == (9 if name == "Dixon" else 10))
    check("normalized_grid_" + name,
          info["atlas_size"] == [1344, 1920] and
          info["atlas_grid"]["cell"] == 192)
    plane_height = max(vertex.co.z for vertex in sprite.data.vertices)
    anchor_offset = sprite.location.z + plane_height * (
        192 - info["foot_pixel_range"][1]) / 192
    check("floor_anchor_" + name, abs(anchor_offset) < 0.02)
    image = bpy.data.images.get(name + "_EP02_Atlas.png")
    check("packed_image_" + name, image is not None and image.packed_file is not None)
    images.append(image.name)
    material = sprite.data.materials[0]
    materials.append(material.name)
    drivers = material.node_tree.animation_data.drivers
    check("frame_driver_" + name, len(drivers) == 1 and
          drivers[0].driver.variables[0].targets[0].id == sprite and
          drivers[0].driver.variables[0].targets[0].data_path == '["sprite_frame"]')
    nla = sprite.animation_data.nla_tracks
    check("sprite_nla_" + name, len(nla) == 1 and len(nla[0].strips) == 26)
    actions = [action for action in bpy.data.actions if action.name.startswith("ACT_" + name + "_")]
    check("sprite_actions_" + name, len(actions) >= len(info["frame_map"]))
    check("constant_frames_" + name,
          all(point.interpolation == "CONSTANT" for action in actions
              for curve in curves(action) for point in curve.keyframe_points))
    check("proxy_rig_preserved_" + name,
          bpy.data.objects.get(name + "_CTRL_RIG") is not None and
          bpy.data.objects.get(name + "_PROXY_ROOT") is not None)
check("distinct_sprite_materials", len(set(materials)) == 3)
check("distinct_sprite_images", len(set(images)) == 3)
check("no_missing_image_paths", all(image.packed_file is not None or
      Path(bpy.path.abspath(image.filepath)).is_file()
      for image in bpy.data.images if image.source == "FILE"))

flap = bpy.data.objects["EP02_Box_Front_Flap_Pivot"]
scene.frame_set(180 * scene.render.fps)
flap_before = flap.rotation_euler.x
scene.frame_set(195 * scene.render.fps)
flap_after = flap.rotation_euler.x
check("box_flap_responds", abs(flap_after - flap_before) > 0.1)

expected = {
    108: {"Dage": 6},
    156: {"Dage": 37},
    180: {"Dage": 3},
    252: {"Dage": 9},
    294: {"Dage": 26},
    336: {"Dixon": 43},
    480: {"Cila": 31},
    894: {"Dage": 26},
}
for seconds, pairs in expected.items():
    scene.frame_set(seconds * scene.render.fps)
    for name, index in pairs.items():
        check(f"frame_{seconds}_{name}", bpy.data.objects["SPRITE_" + name]["sprite_frame"] == index)

text_collection = bpy.data.collections["NARRATION_TEXT_OFF"]
check("text_off_by_default", text_collection.hide_render and text_collection.hide_viewport)
check("fact_label_available", bpy.data.objects["EP02_FACT_LABEL"].data.body == SEED["fact_label"]
      and not bpy.data.objects["EP02_FACT_LABEL"].hide_render)
check("narration_optional", bpy.data.objects["EP02_OPTIONAL_NARRATION"].hide_render)
check("ep01_text_preserved_and_hidden", all(obj.hide_render for obj in text_collection.objects
      if obj.name.startswith("LOWER_THIRD_")))

preview_dir = ROOT / "preview_frames" / "episode02_box"
for label in ("dage_notices", "dage_paw_tests", "box_flap_settles",
              "dage_enters", "dixon_observes",
              "cila_investigates", "shared_final", "fact_label_optional"):
    path = preview_dir / (label + ".png")
    check("preview_" + label, path.is_file() and path.stat().st_size > 10000)
check("storyboard_contact_sheet", (preview_dir / "EP02_storyboard_preview.png").is_file())

report = {"passed": len(checks), "failed": 0, "checks": checks,
          "counts": {"collections": len(bpy.data.collections),
                     "objects": len(bpy.data.objects),
                     "actions": len(bpy.data.actions),
                     "materials": len(bpy.data.materials)}}
path = ROOT / "EP02_VERIFICATION.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("EP02_VERIFIED", len(checks), "checks", path, flush=True)
