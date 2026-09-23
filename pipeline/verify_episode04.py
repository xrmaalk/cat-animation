"""Verify Episode 04 structure, current Dage art, previews, and master."""

from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.episode_plan import episode_directory, load_episode_plan, pacing_flags
from pipeline.sprite_manifest import (
    assert_current_dage_source,
    frame_available,
    grid_geometry,
    load_manifest,
)


EPISODE_DIR = episode_directory(4, ROOT)
SEED, SHOTS = load_episode_plan(4, ROOT)
MANIFEST = load_manifest(SEED["sprite_manifest"], ROOT)
scene = bpy.context.scene
checks = {}


def check(label, condition):
    checks[label] = bool(condition)
    if not condition:
        print("EP04_CHECK_FAILED", label, flush=True)


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


try:
    assert_current_dage_source(MANIFEST, ROOT)
    current_source_valid = True
except (OSError, ValueError):
    current_source_valid = False
check("current_dage_source_hash", current_source_valid)
check("separate_ep04_scene", scene.name == "EP04_Sunbeam")
check(
    "episode_seed_properties",
    all(scene.get(key) == SEED[key] for key in (
        "episode_number", "episode_title", "episode_seed", "discovery_prop",
        "discovery_collection", "lead_character", "sprite_manifest",
    )),
)
runtime = int(SEED["runtime_seconds"])
check(
    "short_runtime_and_timing",
    60 <= runtime <= 120 and runtime == 88 and scene.render.fps == 24
    and scene.frame_end == runtime * scene.render.fps,
)
check("smooth_pacing_plan", len(SHOTS) == 18 and not pacing_flags(SHOTS))
check(
    "sunbeam_study",
    bpy.data.collections.get("SET_SunbeamStudy") is not None
    and bpy.data.objects.get("PROP_Sunbeam") is not None
    and all(bpy.data.objects.get(f"EP04_Beam_Marker_{i}") is not None for i in range(1, 4))
    and bpy.data.objects.get("EP04_Purrcilla_Shadow") is not None,
)

holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
tracks = {
    track.name: track for track in holder.animation_data.nla_tracks
} if holder and holder.animation_data else {}
check(
    "ep01_editorial_preserved",
    "EP01_BEATS" in tracks and len(tracks["EP01_BEATS"].strips) == 26
    and tracks["EP01_BEATS"].mute,
)
check("ep04_editorial_modular", "EP04_BEATS" in tracks and len(tracks["EP04_BEATS"].strips) == 18)
if "EP04_BEATS" in tracks:
    strips = sorted(tracks["EP04_BEATS"].strips, key=lambda item: item.frame_start)
    check(
        "ep04_editorial_timing",
        all(
            round(strip.frame_start) == int(shot["start_seconds"]) * 24
            and round(strip.frame_end) == (
                int(shot["start_seconds"]) + int(shot["duration_seconds"])
            ) * 24 - 1
            for strip, shot in zip(strips, SHOTS)
        ),
    )

markers = [m for m in scene.timeline_markers if m.name.startswith("EP04_")]
check("camera_markers", len(markers) == 18 and all(marker.camera for marker in markers))
for shot in SHOTS:
    scene.frame_set(int(shot["start_seconds"]) * 24)
    check("camera_" + shot["shot"], scene.camera and scene.camera.name == shot["camera"])

materials = []
images = []
for name in ("Cila", "Dixon", "Dage"):
    info = MANIFEST["characters"][name]
    sprite = bpy.data.objects.get(f"SPRITE_{name}")
    group = bpy.data.collections.get(f"CHAR_{name}")
    check("sprite_" + name, sprite is not None and group is not None and sprite.name in group.objects)
    if sprite is None:
        continue
    check(
        "sprite_metadata_" + name,
        sprite.get("sprite_valid_frames") == info["valid_frames"]
        and sprite.get("source_sheet") == info["source"],
    )
    material = sprite.data.materials[0]
    image = next((node.image for node in material.node_tree.nodes if node.type == "TEX_IMAGE"), None)
    check("packed_image_" + name, image is not None and image.packed_file is not None)
    materials.append(material.name)
    images.append(image.name if image else "")
    drivers = material.node_tree.animation_data.drivers
    driver_paths = {
        variable.targets[0].data_path
        for curve in drivers for variable in curve.driver.variables
        if variable.targets[0].id == sprite
    }
    check("frame_driver_" + name, driver_paths == {'["sprite_frame"]'})
    nla = sprite.animation_data.nla_tracks
    check(
        "continuous_sprite_nla_" + name,
        len(nla) == 1 and nla[0].name == f"EP04_{name}_SPRITE_ACTIONS"
        and len(nla[0].strips) == 1,
    )
    action = nla[0].strips[0].action
    paths = {curve.data_path for curve in curves(action)}
    check("animated_pose_and_breathing_" + name, '["sprite_frame"]' in paths and "scale" in paths)
    if name == "Dage":
        values = [
            round(point.co.y)
            for curve in curves(action) if curve.data_path == '["sprite_frame"]'
            for point in curve.keyframe_points
        ]
        check("dage_uses_only_occupied_cells", values and all(frame_available(info, value) for value in values))
        check(
            "dage_current_grid_and_source_truth",
            grid_geometry(info) == (8, 11, 192, 208)
            and sprite.get("source_of_truth") == "approved_current_8x11_pet_spritesheet"
            and sprite.get("source_sha256") == info["source_sha256"],
        )
        if image and image.packed_file:
            check(
                "dage_packed_sheet_matches_source",
                sha256(image.packed_file.data).hexdigest()
                == sha256((ROOT / info["source"]).read_bytes()).hexdigest(),
            )
check("distinct_sprite_materials", len(set(materials)) == 3)
check("distinct_sprite_images", len(set(images)) == 3)

expected_frames = {
    0: {"Dage": 48}, 5: {"Dage": 0}, 24: {"Dage": 56},
    29: {"Dage": 72, "Dixon": 6}, 34: {"Cila": 17},
    64: {"Dage": 80, "Cila": 31}, 74: {"Dage": 24},
    79: {"Dage": 0, "Dixon": 0, "Cila": 0},
}
for seconds, pairs in expected_frames.items():
    scene.frame_set(seconds * 24)
    for name, expected in pairs.items():
        check(f"pose_{seconds}_{name}", bpy.data.objects[f"SPRITE_{name}"]["sprite_frame"] == expected)

beam = bpy.data.objects.get("PROP_Sunbeam")
if beam:
    scene.frame_set(0)
    start_x = beam.location.x
    scene.frame_set(44 * 24)
    middle_x = beam.location.x
    scene.frame_set(88 * 24)
    end_x = beam.location.x
    check("sunbeam_moves_continuously", start_x < middle_x < end_x and end_x - start_x > 3.0)
for index, seconds in enumerate((24, 39, 50), start=1):
    marker = bpy.data.objects.get(f"EP04_Beam_Marker_{index}")
    scene.frame_set(seconds * 24)
    check(f"marker_{index}_reveals", marker is not None and marker.scale.x > 0.1)

text_group = bpy.data.collections.get("NARRATION_TEXT_OFF")
check("text_off_by_default", text_group and text_group.hide_render and text_group.hide_viewport)
check(
    "title_and_fact_available",
    bpy.data.objects.get("EP04_TITLE_CARD") is not None
    and bpy.data.objects.get("EP04_FACT_LABEL") is not None
    and bpy.data.objects["EP04_FACT_LABEL"].data.body == SEED["fact_label"],
)
check(
    "optional_narration_available",
    bpy.data.objects.get("EP04_OPTIONAL_NARRATION") is not None
    and bpy.data.objects["EP04_OPTIONAL_NARRATION"].data.body == SEED["optional_narration"],
)

preview_dir = ROOT / "preview_frames" / "episode04_sunbeam"
preview_labels = (
    "dage_finds_sunbeam", "sunbeam_slips", "dage_first_marker",
    "dixon_checks_window", "purrcilla_brings_marker", "dage_compares",
    "purrcilla_shadow_test", "shared_sunbeam", "fact_label_optional",
)
for label in preview_labels:
    path = preview_dir / (label + ".png")
    check("preview_" + label, path.is_file() and path.stat().st_size > 10000)
check("storyboard_contact_sheet", (preview_dir / "EP04_storyboard_preview.png").is_file())
video = ROOT / "renders" / "Purrcilla_Dixon_Dage_EP04_Sunbeam_Animatic.mp4"
check("continuous_video_master", video.is_file() and video.stat().st_size > 100000)

missing_external_images = [
    image.name for image in bpy.data.images
    if image.source == "FILE" and image.packed_file is None
    and not Path(bpy.path.abspath(image.filepath)).is_file()
]
passed = sum(checks.values())
failed = len(checks) - passed
report = {
    "passed": passed, "failed": failed, "checks": checks,
    "warnings": {"missing_nonpacked_template_images": missing_external_images},
    "counts": {
        "shots": len(SHOTS), "objects": len(bpy.data.objects),
        "actions": len(bpy.data.actions), "materials": len(bpy.data.materials),
    },
}
path = EPISODE_DIR / "EP04_VERIFICATION.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("EP04_VERIFIED", passed, "passed", failed, "failed", path, flush=True)
if failed:
    raise AssertionError(
        f"Episode 04 has {failed} failed checks: "
        + ", ".join(label for label, okay in checks.items() if not okay)
    )
