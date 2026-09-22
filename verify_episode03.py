"""Audit Episode 03 and write its machine-readable verification report.

blender --background Purrcilla_Dixon_Dage_EP03_Purr.blend \
  --python verify_episode03.py
"""

import csv
from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dage_neck_patch import (
    FRONT_NECK_PATCH_CENTERS,
    mark_version_is_supported,
)

EPISODE_DIR = ROOT / "episodes" / "3-episode"
SEED = json.loads(
    (EPISODE_DIR / "episode03_seed.json").read_text(encoding="utf-8")
)
MANIFEST = json.loads(
    (ROOT / SEED["sprite_manifest"]).read_text(encoding="utf-8")
)
with (EPISODE_DIR / SEED["shotlist"]).open(
    newline="", encoding="utf-8"
) as handle:
    SHOTS = list(csv.DictReader(handle))

scene = bpy.context.scene
checks = {}


def check(label, condition):
    checks[label] = bool(condition)
    if not condition:
        print("EP03_CHECK_FAILED", label, flush=True)


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


check("separate_ep03_scene", scene.name == "EP03_Purr")
check(
    "episode_seed_properties",
    all(
        scene.get(key) == SEED[key]
        for key in (
            "episode_number",
            "episode_title",
            "episode_seed",
            "discovery_prop",
            "discovery_collection",
            "lead_character",
        )
    ),
)
check("timing_preserved", scene.frame_end == 24480 and scene.render.fps == 24)
check(
    "lap_study_and_prop",
    bpy.data.collections.get("SET_LapStudy") is not None
    and bpy.data.objects.get("PROP_Lap") is not None
    and bpy.data.objects.get("EP03_Cushion") is not None
    and bpy.data.objects.get("EP03_Blanket") is not None,
)

holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
tracks = {
    track.name: track
    for track in holder.animation_data.nla_tracks
} if holder and holder.animation_data else {}
check(
    "ep01_editorial_preserved",
    "EP01_BEATS" in tracks
    and len(tracks["EP01_BEATS"].strips) == 26
    and tracks["EP01_BEATS"].mute,
)
check(
    "ep03_editorial_modular",
    "EP03_BEATS" in tracks and len(tracks["EP03_BEATS"].strips) == 26,
)
check(
    "ep01_actions_preserved",
    sum(action.name.startswith("ACT_S") for action in bpy.data.actions) >= 26,
)
check(
    "ep03_shot_data",
    len(SHOTS) == 26
    and int(SHOTS[-1]["start_seconds"])
    + int(SHOTS[-1]["duration_seconds"]) == 1020,
)

markers = [
    marker
    for marker in scene.timeline_markers
    if marker.name.startswith("EP03_")
]
check("camera_markers", len(markers) == 26 and all(marker.camera for marker in markers))
for shot in SHOTS:
    scene.frame_set(int(shot["start_seconds"]) * scene.render.fps)
    check(
        "camera_" + shot["shot"],
        scene.camera is not None and scene.camera.name == shot["camera"],
    )

for path in MANIFEST.get("dage_visual_references", []):
    check("dage_reference_" + Path(path).stem, (ROOT / path).is_file())

materials = []
images = []
for name in ("Cila", "Dixon", "Dage"):
    sprite = bpy.data.objects.get("SPRITE_" + name)
    group = bpy.data.collections.get("CHAR_" + name)
    info = MANIFEST["characters"][name]
    check(
        "sprite_" + name,
        sprite is not None and group is not None and sprite.name in group.objects,
    )
    if sprite is None:
        continue
    check(
        "sprite_property_" + name,
        sprite.get("sprite_frame") is not None
        and sprite.get("sprite_valid_frames") == info["valid_frames"],
    )
    check(
        "source_hash_" + name,
        sha256((ROOT / info["source"]).read_bytes()).hexdigest()
        == info["source_sha256"],
    )
    check(
        "source_grid_" + name,
        info["source_grid"]["columns"] == 7
        and info["source_grid"]["rows"] == (9 if name == "Dixon" else 10),
    )
    check(
        "normalized_grid_" + name,
        info["atlas_size"] == [1344, 1920]
        and info["atlas_grid"]["cell"] == 192,
    )
    plane_height = max(vertex.co.z for vertex in sprite.data.vertices)
    anchor_offset = sprite.location.z + plane_height * (
        192 - info["foot_pixel_range"][1]
    ) / 192
    check("floor_anchor_" + name, abs(anchor_offset) < 0.02)

    image = bpy.data.images.get(Path(info["atlas"]).name)
    check(
        "packed_image_" + name,
        image is not None and image.packed_file is not None,
    )
    if image is not None:
        images.append(image.name)
    if name == "Dage" and image is not None and image.packed_file is not None:
        check(
            "dage_packed_atlas_matches_sheet",
            sha256(image.packed_file.data).hexdigest()
            == sha256((ROOT / info["atlas"]).read_bytes()).hexdigest(),
        )

    material = sprite.data.materials[0]
    materials.append(material.name)
    drivers = material.node_tree.animation_data.drivers
    driver_paths = {
        variable.targets[0].data_path
        for curve in drivers
        for variable in curve.driver.variables
        if variable.targets[0].id == sprite
    }
    expected_paths = {'["sprite_frame"]'}
    check(
        "frame_driver_" + name,
        len(drivers) == len(expected_paths) and driver_paths == expected_paths,
    )
    nla = sprite.animation_data.nla_tracks
    check("sprite_nla_" + name, len(nla) == 1 and len(nla[0].strips) == 26)
    actions = [
        action
        for action in bpy.data.actions
        if action.name.startswith("ACT_" + name + "_")
    ]
    check("sprite_actions_" + name, len(actions) >= len(info["frame_map"]))
    check(
        "constant_frames_" + name,
        all(
            point.interpolation == "CONSTANT"
            for action in actions
            for curve in curves(action)
            for point in curve.keyframe_points
        ),
    )
    if name == "Dage":
        patch_version = (
            sprite.get("dage_front_neck_patch_art")
            or sprite.get("dage_chin_art")
        )
        check(
            "dage_baked_front_neck_art",
            mark_version_is_supported(patch_version)
            and material.node_tree.nodes.get("Dage Black Chin Spot") is None,
        )
        check(
            "dage_front_neck_art_all_actions",
            all(
                {curve.data_path for curve in curves(action)} == expected_paths
                and all(
                    round(point.co.y) in FRONT_NECK_PATCH_CENTERS
                    for curve in curves(action)
                    for point in curve.keyframe_points
                )
                for action in actions
            ),
        )
    check(
        "proxy_rig_preserved_" + name,
        bpy.data.objects.get(name + "_CTRL_RIG") is not None
        and bpy.data.objects.get(name + "_PROXY_ROOT") is not None,
    )

check("distinct_sprite_materials", len(set(materials)) == 3)
check("distinct_sprite_images", len(set(images)) == 3)

expected_frames = {
    108: {"Cila": 5},
    132: {"Cila": 14},
    156: {"Cila": 40},
    180: {"Cila": 40},
    336: {"Dixon": 43},
    390: {"Dixon": 43},
    438: {"Dage": 6},
    690: {"Dage": 42, "Dixon": 0, "Cila": 40},
    894: {"Dage": 42, "Dixon": 0, "Cila": 0},
}
for seconds, pairs in expected_frames.items():
    scene.frame_set(seconds * scene.render.fps)
    for name, index in pairs.items():
        check(
            f"frame_{seconds}_{name}",
            bpy.data.objects["SPRITE_" + name]["sprite_frame"] == index,
        )

expected_positions = {
    156: {"Cila": (-1.05, -0.25, 0.17)},
    528: {"Dage": (0.45, -0.05, 0.0)},
    690: {"Dixon": (2.0, 0.05, 0.0)},
}
for seconds, pairs in expected_positions.items():
    scene.frame_set(seconds * scene.render.fps)
    for name, expected in pairs.items():
        actual = bpy.data.objects[f"EP03_{name}_Sprite_CTRL"].location
        check(
            f"position_{seconds}_{name}",
            all(abs(actual[index] - expected[index]) < 0.01 for index in range(3)),
        )

text_collection = bpy.data.collections.get("NARRATION_TEXT_OFF")
check(
    "text_off_by_default",
    text_collection is not None
    and text_collection.hide_render
    and text_collection.hide_viewport,
)
check(
    "title_available",
    bpy.data.objects.get("EP03_TITLE_CARD") is not None
    and bpy.data.objects["EP03_TITLE_CARD"].hide_render,
)
check(
    "fact_label_available",
    bpy.data.objects.get("EP03_FACT_LABEL") is not None
    and bpy.data.objects["EP03_FACT_LABEL"].data.body == SEED["fact_label"]
    and not bpy.data.objects["EP03_FACT_LABEL"].hide_render,
)
check(
    "narration_optional",
    bpy.data.objects.get("EP03_OPTIONAL_NARRATION") is not None
    and bpy.data.objects["EP03_OPTIONAL_NARRATION"].hide_render,
)
check(
    "ep01_text_preserved_and_hidden",
    text_collection is not None
    and all(
        obj.hide_render
        for obj in text_collection.objects
        if obj.name.startswith("LOWER_THIRD_")
    ),
)

preview_dir = ROOT / "preview_frames" / "episode03_purr"
preview_labels = (
    "cila_restless",
    "cila_settles",
    "first_purr",
    "cila_relaxes",
    "dixon_listens",
    "shared_listening",
    "shared_final",
    "fact_label_optional",
)
for label in preview_labels:
    path = preview_dir / (label + ".png")
    check("preview_" + label, path.is_file() and path.stat().st_size > 10000)
check(
    "storyboard_contact_sheet",
    (preview_dir / "EP03_storyboard_preview.png").is_file(),
)

missing_external_images = [
    image.name
    for image in bpy.data.images
    if image.source == "FILE"
    and image.packed_file is None
    and not Path(bpy.path.abspath(image.filepath)).is_file()
]

passed = sum(checks.values())
failed = len(checks) - passed
report = {
    "passed": passed,
    "failed": failed,
    "checks": checks,
    "warnings": {
        "missing_nonpacked_template_images": missing_external_images,
    },
    "counts": {
        "collections": len(bpy.data.collections),
        "objects": len(bpy.data.objects),
        "actions": len(bpy.data.actions),
        "materials": len(bpy.data.materials),
    },
}
path = EPISODE_DIR / "EP03_VERIFICATION.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("EP03_VERIFIED", passed, "passed", failed, "failed", path, flush=True)
if failed:
    raise AssertionError(
        f"Episode 03 has {failed} failed checks: "
        + ", ".join(label for label, okay in checks.items() if not okay)
    )
