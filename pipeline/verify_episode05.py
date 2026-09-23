"""Pre-render structural verification for Episode 05."""

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


EPISODE_DIR = episode_directory(5, ROOT)
SEED, SHOTS = load_episode_plan(5, ROOT)
CONTRACT = json.loads(
    (EPISODE_DIR / SEED["performance_contract"]).read_text(encoding="utf-8")
)
MANIFEST = load_manifest(SEED["sprite_manifest"], ROOT)
scene = bpy.context.scene
checks = {}


def check(label, condition):
    checks[label] = bool(condition)
    if not condition:
        print("EP05_CHECK_FAILED", label, flush=True)


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


try:
    assert_current_dage_source(MANIFEST, ROOT)
    source_valid = True
except (OSError, ValueError):
    source_valid = False
check("current_dage_source_hash", source_valid)
check("separate_ep05_scene", scene.name == "EP05_Condensation")
check(
    "episode_seed_properties",
    all(scene.get(key) == SEED[key] for key in (
        "episode_number", "episode_title", "episode_seed", "discovery_prop",
        "discovery_collection", "lead_character", "sprite_manifest",
        "performance_contract",
    )),
)
check(
    "runtime_and_pacing",
    int(SEED["runtime_seconds"]) == 86 and 60 <= int(SEED["runtime_seconds"]) <= 120
    and scene.frame_end == 86 * 24 and scene.render.fps == 24
    and len(SHOTS) == 17 and not pacing_flags(SHOTS),
)
check(
    "isolated_from_episode04",
    scene.get("episode05_setup_version") is not None
    and scene.get("render_status") == "NOT_RENDERED_BY_DESIGN"
    and not any(track.name == "EP04_BEATS" for track in bpy.data.objects["EDITORIAL_MASTER_NLA"].animation_data.nla_tracks),
)

required_props = (
    "PROP_CondensationWindow", "EP05_Cold_Window_Pane",
    "EP05_Condensation_Patch", "EP05_Paw_Clear_Trace",
    "EP05_Warm_Clear_Corner", "PROP_EP05_Warm_Cloth",
    "PROP_EP05_Cold_Coaster",
)
check("condensation_study_props", all(bpy.data.objects.get(name) is not None for name in required_props))
check("droplet_count", sum(name.startswith("EP05_Droplet_") for name in bpy.data.objects.keys()) == 5)

holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
tracks = {track.name: track for track in holder.animation_data.nla_tracks}
check(
    "ep01_editorial_preserved",
    "EP01_BEATS" in tracks and len(tracks["EP01_BEATS"].strips) == 26 and tracks["EP01_BEATS"].mute,
)
check("ep05_editorial_modular", "EP05_BEATS" in tracks and len(tracks["EP05_BEATS"].strips) == 17)
if "EP05_BEATS" in tracks:
    strips = sorted(tracks["EP05_BEATS"].strips, key=lambda item: item.frame_start)
    check(
        "ep05_editorial_timing",
        all(
            round(strip.frame_start) == int(shot["start_seconds"]) * 24
            and round(strip.frame_end) == (
                int(shot["start_seconds"]) + int(shot["duration_seconds"])
            ) * 24 - 1
            for strip, shot in zip(strips, SHOTS)
        ),
    )

markers = [marker for marker in scene.timeline_markers if marker.name.startswith("EP05_")]
check("camera_markers", len(markers) == 17 and all(marker.camera for marker in markers))
for shot in SHOTS:
    scene.frame_set(int(shot["start_seconds"]) * 24)
    check("camera_" + shot["shot"], scene.camera and scene.camera.name == shot["camera"])
    card = bpy.data.objects.get(f"EP05_CARD_{shot['shot']}")
    check(
        "role_card_" + shot["shot"],
        card is not None and all(card.get(key) == shot[key] for key in ("dage_role", "dixon_role", "cila_role")),
    )

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
        "performance_contract_" + name,
        sprite.get("performance_contract") == CONTRACT["version"],
    )
    material_slot = sprite.data.materials[0]
    image = next((node.image for node in material_slot.node_tree.nodes if node.type == "TEX_IMAGE"), None)
    check("packed_image_" + name, image is not None and image.packed_file is not None)
    materials.append(material_slot.name)
    images.append(image.name if image else "")
    nla = sprite.animation_data.nla_tracks
    check(
        "continuous_performance_" + name,
        len(nla) == 1 and nla[0].name == f"EP05_{name}_SPRITE_PERFORMANCE"
        and len(nla[0].strips) == 1,
    )
    action = nla[0].strips[0].action
    paths = {curve.data_path for curve in curves(action)}
    check("pose_and_breathing_" + name, '["sprite_frame"]' in paths and "scale" in paths)
    values = [
        round(point.co.y)
        for curve in curves(action) if curve.data_path == '["sprite_frame"]'
        for point in curve.keyframe_points
    ]
    check("occupied_frames_" + name, values and all(frame_available(info, value) for value in values))
    check(
        "multiframe_library_" + name,
        all(len(entry["frames"]) >= 2 for entry in CONTRACT["characters"][name].values()),
    )
    if name == "Dage":
        check(
            "dage_current_source_truth",
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

expected = {
    0: {"Dixon": 7, "Cila": 0, "Dage": 0},
    9: {"Dixon": 3}, 20: {"Dixon": 14},
    30: {"Cila": 14}, 35: {"Dage": 72},
    46: {"Cila": 28}, 51: {"Dage": 56},
    72: {"Dixon": 35}, 82: {"Dixon": 0, "Cila": 0, "Dage": 0},
}
for seconds, pairs in expected.items():
    scene.frame_set(seconds * 24)
    for name, value in pairs.items():
        check(f"pose_{seconds}_{name}", bpy.data.objects[f"SPRITE_{name}"]["sprite_frame"] == value)

fog = bpy.data.objects.get("EP05_Condensation_Patch")
trace = bpy.data.objects.get("EP05_Paw_Clear_Trace")
warm = bpy.data.objects.get("EP05_Warm_Clear_Corner")
if fog and trace and warm:
    scene.frame_set(0)
    fog_before = fog.scale.x
    trace_before = trace.scale.x
    scene.frame_set(20 * 24)
    fog_after = fog.scale.x
    trace_after = trace.scale.x
    scene.frame_set(46 * 24)
    warm_after = warm.scale.x
    check("fog_appears", fog_before < 0.01 and fog_after > 0.5)
    check("paw_trace_appears", trace_before < 0.01 and trace_after > 0.5)
    check("warm_corner_appears", warm_after > 0.2)

text_group = bpy.data.collections.get("NARRATION_TEXT_OFF")
check("text_off_by_default", text_group and text_group.hide_render and text_group.hide_viewport)
check(
    "title_fact_narration_available",
    bpy.data.objects.get("EP05_TITLE_CARD") is not None
    and bpy.data.objects.get("EP05_FACT_LABEL") is not None
    and bpy.data.objects["EP05_FACT_LABEL"].data.body == SEED["fact_label"]
    and bpy.data.objects.get("EP05_OPTIONAL_NARRATION") is not None,
)
check("contract_embedded", bpy.data.texts.get("EP05_PERFORMANCE_CONTRACT") is not None)

missing_external_images = [
    image.name for image in bpy.data.images
    if image.source == "FILE" and image.packed_file is None
    and not Path(bpy.path.abspath(image.filepath)).is_file()
]
passed = sum(checks.values())
failed = len(checks) - passed
report = {
    "stage": "pre-render",
    "passed": passed,
    "failed": failed,
    "checks": checks,
    "warnings": {"missing_nonpacked_template_images": missing_external_images},
    "render_started": False,
    "counts": {
        "shots": len(SHOTS), "objects": len(bpy.data.objects),
        "actions": len(bpy.data.actions), "materials": len(bpy.data.materials),
    },
}
path = EPISODE_DIR / "EP05_VERIFICATION.json"
path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("EP05_PRE_RENDER_VERIFIED", passed, "passed", failed, "failed", path, flush=True)
if failed:
    raise AssertionError(
        f"Episode 05 has {failed} failed pre-render checks: "
        + ", ".join(label for label, okay in checks.items() if not okay)
    )
