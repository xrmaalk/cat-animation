"""Build Episode 04 as a separate continuously animated Blender scene.

blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend \
  --python pipeline/build_episode04.py

Dage is loaded directly from the approved current 8x11 source sheet. The
template and all historical episode scenes remain untouched.
"""

from pathlib import Path
import json
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pipeline.blender_sprite import (
    atlas_grid_label,
    sprite_material as build_sprite_material,
    sprite_plane_width,
)
from pipeline.episode_plan import episode_directory, load_episode_plan
from pipeline.sprite_manifest import (
    assert_current_dage_source,
    grid_geometry,
    load_manifest,
)


EPISODE_DIR = episode_directory(4, ROOT)
SEED, SHOTS = load_episode_plan(4, ROOT)
MANIFEST = load_manifest(SEED["sprite_manifest"], ROOT)
FPS = int(SEED["fps"])
SHOT_BY_BEAT = {shot["beat"]: shot for shot in SHOTS}
OUTPUT = ROOT / "Purrcilla_Dixon_Dage_EP04_Sunbeam.blend"
SETUP_VERSION = "EP04_Sunbeam_v1_current_8x11"


def collection(name, parent=None):
    found = bpy.data.collections.get(name)
    if found:
        return found
    found = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(found)
    return found


def color_material(name, color, roughness=0.8, emission=0.0):
    found = bpy.data.materials.get(name)
    if found:
        return found
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission
    return material


def relink(obj, target_collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target_collection.objects.link(obj)
    return obj


def cuboid(name, location, scale, material, target_collection, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    obj = relink(bpy.context.object, target_collection)
    obj.name = name
    obj.scale = scale
    obj.parent = parent
    obj.data.materials.append(material)
    return obj


def disc(name, location, scale, material, target_collection, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=1.0, depth=0.018, location=location
    )
    obj = relink(bpy.context.object, target_collection)
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def set_linear(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if not bag:
                    continue
                for curve in bag.fcurves:
                    for point in curve.keyframe_points:
                        point.interpolation = "LINEAR"


def set_sprite_interpolation(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if not bag:
                    continue
                for curve in bag.fcurves:
                    interpolation = (
                        "CONSTANT" if curve.data_path == '["sprite_frame"]'
                        else "BEZIER"
                    )
                    for point in curve.keyframe_points:
                        point.interpolation = interpolation


def key_location(obj, seconds, location):
    obj.location = location
    obj.keyframe_insert(data_path="location", frame=seconds * FPS)


def key_scale(obj, seconds, scale):
    obj.scale = scale
    obj.keyframe_insert(data_path="scale", frame=seconds * FPS)


def make_sunbeam_study():
    study = collection(SEED["discovery_collection"])
    for old_name in ("PROP_Cardboard_Box", "PROP_CardboardBox"):
        old = bpy.data.objects.get(old_name)
        if old:
            old.hide_render = True
            old.hide_set(True)

    gold = color_material("MAT_EP04_Sunbeam", (1.0, 0.55, 0.08), 0.32, 2.2)
    marker_materials = (
        color_material("MAT_EP04_Marker_A", (0.38, 0.06, 0.72), 0.45, 0.3),
        color_material("MAT_EP04_Marker_B", (0.74, 0.08, 0.92), 0.45, 0.3),
        color_material("MAT_EP04_Marker_C", (0.18, 0.42, 0.92), 0.45, 0.3),
    )
    shadow_material = color_material("MAT_EP04_Shadow", (0.035, 0.025, 0.06), 1.0)

    beam = disc(
        "PROP_Sunbeam", (-1.75, -0.1, 0.035), (1.18, 0.43, 0.45),
        gold, study,
    )
    beam["role"] = "Continuously moving patch of sunlight"
    key_location(beam, 0, (-1.75, -0.1, 0.035))
    key_location(beam, 44, (-0.10, -0.1, 0.035))
    key_location(beam, 88, (1.55, -0.1, 0.035))
    set_linear(beam.animation_data.action)

    marker_times = (24, 39, 50)
    marker_x = (-0.85, -0.29, 0.13)
    markers = []
    for index, (reveal, x_pos, material) in enumerate(
        zip(marker_times, marker_x, marker_materials), start=1
    ):
        marker = disc(
            f"EP04_Beam_Marker_{index}", (x_pos, -0.82, 0.048),
            (0.16, 0.16, 0.20), material, study, vertices=32,
        )
        marker["reveal_seconds"] = reveal
        key_scale(marker, 0, (0.001, 0.001, 0.001))
        key_scale(marker, max(0, reveal - 1), (0.001, 0.001, 0.001))
        key_scale(marker, reveal, (0.16, 0.16, 0.20))
        markers.append(marker)

    shadow = disc(
        "EP04_Purrcilla_Shadow", (-0.45, -0.08, 0.052),
        (0.001, 0.001, 0.001), shadow_material, study,
    )
    key_scale(shadow, 0, (0.001, 0.001, 0.001))
    key_scale(shadow, 63, (0.001, 0.001, 0.001))
    key_scale(shadow, 64, (0.42, 0.18, 0.16))
    key_location(shadow, 64, (-0.45, -0.08, 0.052))
    key_location(shadow, 69, (0.42, -0.08, 0.052))
    key_scale(shadow, 69, (0.001, 0.001, 0.001))

    # Three slim rays make Dixon's window-angle demonstration readable.
    ray_material = color_material("MAT_EP04_Rays", (1.0, 0.72, 0.22), 0.4, 1.0)
    for index, z_pos in enumerate((0.72, 1.02, 1.32), start=1):
        ray = cuboid(
            f"EP04_Window_Ray_{index}", (1.02, 0.64, z_pos),
            (0.78, 0.014, 0.018), ray_material, study,
        )
        ray.rotation_euler.y = -0.36
    return beam, markers, shadow


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_cameras():
    poses = {
        "CAM_CatEye_A": ((0.0, -6.1, 1.72), (0.0, 0.0, 0.78), 36),
        "CAM_Insert_Paws": ((-0.15, -3.75, 0.78), (-0.15, -0.05, 0.28), 58),
        "CAM_HeroPortrait_Dage": ((-0.25, -4.75, 1.46), (-0.15, 0.0, 0.96), 44),
        "CAM_Insert_Eyes": ((0.05, -3.45, 1.55), (0.05, 0.0, 1.28), 64),
        "CAM_WindowReport": ((1.85, -4.65, 1.72), (1.15, 0.48, 1.02), 42),
        "CAM_PorchWide": ((0.05, -6.75, 2.5), (0.05, 0.0, 0.62), 28),
    }
    for name, (position, target, lens) in poses.items():
        camera = bpy.data.objects.get(name)
        if camera is None or camera.type != "CAMERA":
            raise RuntimeError(f"Missing template camera {name}")
        if camera.animation_data:
            camera.animation_data_clear()
        camera.location = position
        look_at(camera, target)
        camera.data.lens = lens
        camera["ep04_target"] = target
    bpy.context.scene.camera = bpy.data.objects["CAM_CatEye_A"]


def configure_markers_and_target():
    scene = bpy.context.scene
    edit = bpy.data.collections.get("EDIT_NLA") or collection("EDIT_NLA")
    target = bpy.data.objects.new("EP04_SPRITE_CAMERA_TARGET", None)
    edit.objects.link(target)
    target.empty_display_type = "SPHERE"
    target.empty_display_size = 0.12
    for shot in SHOTS:
        frame = int(shot["start_seconds"]) * FPS
        camera = bpy.data.objects[shot["camera"]]
        scene.frame_set(frame)
        marker = scene.timeline_markers.new(
            f"EP04_{shot['shot']}_{shot['beat']}", frame=frame
        )
        marker.camera = camera
        target.location = camera.matrix_world.translation.copy()
        target.keyframe_insert(data_path="location", frame=frame)
        card = bpy.data.objects.new(f"EP04_CARD_{shot['shot']}", None)
        edit.objects.link(card)
        card.hide_render = True
        card["beat"] = shot["beat"]
        card["camera"] = shot["camera"]
        card["description"] = shot["description"]
        card["duration_seconds"] = int(shot["duration_seconds"])
    if target.animation_data and target.animation_data.action:
        for layer in target.animation_data.action.layers:
            for strip in layer.strips:
                for slot in target.animation_data.action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for point in curve.keyframe_points:
                                point.interpolation = "CONSTANT"
    return target


def create_sprite(name, camera_target):
    info = MANIFEST["characters"][name]
    atlas_path = ROOT / info["atlas"]
    if not atlas_path.is_file():
        raise FileNotFoundError(atlas_path)
    group = bpy.data.collections.get(f"CHAR_{name}")
    if group is None:
        raise RuntimeError(f"Missing CHAR_{name}")
    for obj in group.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_set(True)

    controller = bpy.data.objects.new(f"EP04_{name}_Sprite_CTRL", None)
    group.objects.link(controller)
    controller.empty_display_type = "ARROWS"
    controller.empty_display_size = 0.25

    height = {"Cila": 1.78, "Dixon": 1.82, "Dage": 1.96}[name]
    width = sprite_plane_width(height, info)
    mesh = bpy.data.meshes.new(f"EP04_SPRITE_{name}_Mesh")
    mesh.from_pydata(
        [(-width / 2, 0, 0), (width / 2, 0, 0),
         (width / 2, 0, height), (-width / 2, 0, height)],
        [], [(0, 1, 2, 3)],
    )
    mesh.update()
    uv = mesh.uv_layers.new(name="SpriteCellUV")
    points = (
        ((1, 0), (0, 0), (0, 1), (1, 1))
        if name in ("Dixon", "Dage")
        else ((0, 0), (1, 0), (1, 1), (0, 1))
    )
    for loop, point in zip(mesh.polygons[0].loop_indices, points):
        uv.data[loop].uv = point

    sprite = bpy.data.objects.new(f"SPRITE_{name}", mesh)
    group.objects.link(sprite)
    sprite.parent = controller
    _, _, _, cell_height = grid_geometry(info)
    foot_bottom = int(info["foot_pixel_range"][1])
    sprite.location.z = -height * (cell_height - foot_bottom) / cell_height
    sprite["sprite_frame"] = int(info["frame_map"]["idle"])
    sprite["sprite_valid_frames"] = int(info["valid_frames"])
    sprite["source_sheet"] = info["source"]
    sprite["atlas_grid"] = atlas_grid_label(info)
    if name == "Dage":
        sprite["source_of_truth"] = "approved_current_8x11_pet_spritesheet"
        sprite["source_sha256"] = info["source_sha256"]

    image = bpy.data.images.load(str(atlas_path), check_existing=True)
    image.filepath = bpy.path.relpath(str(atlas_path))
    image.pack()
    material = build_sprite_material(
        f"MAT_EP04_{name}_Sprite", image, sprite, info
    )
    mesh.materials.append(material)
    track = sprite.constraints.new("TRACK_TO")
    track.target = camera_target
    track.track_axis = "TRACK_NEGATIVE_Y"
    track.up_axis = "UP_Z"
    return sprite, controller


DAGE_SEQUENCES = {
    "IDLE": list(range(0, 7)),
    "SHARED_IDLE": list(range(0, 7)),
    "WAVE": list(range(24, 28)),
    "JUMP": list(range(32, 37)),
    "WAITING": list(range(48, 54)),
    "WORKING": list(range(56, 62)),
    "CURIOUS": list(range(64, 70)),
    "REVIEW": list(range(64, 70)),
    "LOOK_UP": list(range(72, 76)),
    "LOOK_RIGHT": list(range(76, 80)),
    "LOOK_DOWN": list(range(80, 84)),
    "LOOK_LEFT": list(range(84, 88)),
}


def create_continuous_sprite_action(sprite, name):
    info = MANIFEST["characters"][name]
    frame_map = {key.upper(): int(value) for key, value in info["frame_map"].items()}
    sprite.animation_data_create()
    sprite.animation_data.action = None
    for shot in SHOTS:
        pose = shot[f"{name.lower()}_action"]
        start = int(shot["start_seconds"]) * FPS
        end = (int(shot["start_seconds"]) + int(shot["duration_seconds"])) * FPS
        sequence = DAGE_SEQUENCES[pose] if name == "Dage" else [frame_map[pose]]
        step = 4 if len(sequence) > 1 else max(1, end - start - 1)
        frame = start
        index = 0
        while frame < end:
            sprite["sprite_frame"] = sequence[index % len(sequence)]
            sprite.keyframe_insert(
                data_path='["sprite_frame"]', frame=frame, group="Sprite Frame"
            )
            frame += step
            index += 1
        sprite["sprite_frame"] = sequence[(index - 1) % len(sequence)]
        sprite.keyframe_insert(
            data_path='["sprite_frame"]', frame=end - 1, group="Sprite Frame"
        )

    # Gentle breathing keeps held poses alive while the story action continues.
    for frame in range(0, int(SEED["runtime_seconds"]) * FPS, 12):
        phase = 1.0 if (frame // 12) % 2 == 0 else -1.0
        sprite.scale = (1.0 + 0.012 * phase, 1.0, 1.0 - 0.004 * phase)
        sprite.keyframe_insert(data_path="scale", frame=frame, group="Breathing")

    action = sprite.animation_data.action
    action.name = f"ACT_EP04_{name}_CONTINUOUS_SPRITE"
    action.use_fake_user = True
    action["episode"] = 4
    action["continuous_motion"] = True
    set_sprite_interpolation(action)
    sprite.animation_data.action = None
    nla = sprite.animation_data.nla_tracks.new()
    nla.name = f"EP04_{name}_SPRITE_ACTIONS"
    strip = nla.strips.new(f"EP04_{name}_CONTINUOUS", 0, action)
    if hasattr(strip, "action_slot") and action.slots:
        strip.action_slot = action.slots[0]
    return action


def animate_controllers(controllers):
    paths = {
        "Dage": [
            (0, (-1.65, -0.35, 0.0)), (14, (-1.35, -0.35, 0.0)),
            (19, (-0.95, -0.32, 0.0)), (24, (-0.72, -0.30, 0.0)),
            (39, (-0.18, -0.28, 0.0)), (50, (0.22, -0.25, 0.0)),
            (64, (0.72, -0.22, 0.0)), (79, (1.12, -0.20, 0.0)),
            (84, (1.28, -0.18, 0.0)), (88, (1.55, -0.15, 0.0)),
        ],
        "Dixon": [
            (0, (2.55, 0.52, 0.0)), (29, (2.55, 0.52, 0.0)),
            (34, (1.78, 0.28, 0.0)), (59, (1.55, 0.32, 0.0)),
            (79, (1.92, 0.18, 0.0)), (88, (1.92, 0.18, 0.0)),
        ],
        "Cila": [
            (0, (-2.85, 0.38, 0.0)), (34, (-2.85, 0.38, 0.0)),
            (39, (-1.18, 0.08, 0.0)), (64, (-0.62, 0.02, 0.0)),
            (69, (0.18, 0.04, 0.0)), (79, (0.38, 0.08, 0.0)),
            (88, (0.38, 0.08, 0.0)),
        ],
    }
    for name, points in paths.items():
        controller = controllers[name]
        for seconds, position in points:
            key_location(controller, seconds, position)
        action = controller.animation_data.action
        action.name = f"ACT_EP04_{name}_ROOT_MOTION"
        action.use_fake_user = True
        set_linear(action)


def editorial_nla():
    holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
    if holder is None or not holder.animation_data:
        raise RuntimeError("Missing editorial NLA holder")
    source = next(
        (track for track in holder.animation_data.nla_tracks if track.name == "EP01_BEATS"),
        None,
    )
    if source is None:
        raise RuntimeError("Missing EP01_BEATS")
    source.mute = True
    source_strips = sorted(source.strips, key=lambda item: item.frame_start)
    episode = holder.animation_data.nla_tracks.new()
    episode.name = "EP04_BEATS"
    for index, shot in enumerate(SHOTS):
        action = source_strips[index % len(source_strips)].action.copy()
        action.name = f"ACT_EP04_{shot['shot']}_{shot['beat']}"
        action.use_fake_user = True
        action["episode"] = 4
        action["beat"] = shot["beat"]
        action["camera"] = shot["camera"]
        action["description"] = shot["description"]
        start = int(shot["start_seconds"]) * FPS
        duration = int(shot["duration_seconds"]) * FPS
        strip = episode.strips.new(f"EP04_{shot['shot']}_{shot['beat']}", start, action)
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]
        first, last = action.frame_range
        strip.action_frame_start = first
        strip.action_frame_end = max(first + 1, last)
        strip.scale = (duration - 1) / (strip.action_frame_end - first)
        strip.blend_type = "REPLACE"
    holder["episode04_editorial"] = "18 contiguous short-format story beats"


def add_text_cards():
    group = bpy.data.collections.get("NARRATION_TEXT_OFF")
    if group is None:
        raise RuntimeError("Missing NARRATION_TEXT_OFF")
    for obj in group.objects:
        obj.hide_render = True

    camera = bpy.data.objects["CAM_CatEye_A"]
    text_material = color_material("MAT_EP04_Text", (1.0, 0.88, 0.46), 0.65, 1.0)
    backdrop_material = color_material("MAT_EP04_Text_Backdrop", (0.025, 0.018, 0.06), 0.9)

    def make_text(name, body, location, size):
        curve = bpy.data.curves.new(name + "_Curve", type="FONT")
        curve.body = body
        curve.align_x = "CENTER"
        curve.align_y = "CENTER"
        curve.size = size
        curve.extrude = 0.004
        obj = bpy.data.objects.new(name, curve)
        group.objects.link(obj)
        obj.parent = camera
        obj.location = location
        obj.data.materials.append(text_material)
        obj.hide_render = True
        obj["episode"] = 4
        return obj

    make_text(
        "EP04_TITLE_CARD", "Dage Discovers\nWhy the Sunbeam Moves",
        (0.0, 0.58, -3.0), 0.065,
    )
    make_text(
        "EP04_FACT_LABEL", SEED["fact_label"],
        (0.0, 0.70, -3.0), 0.075,
    )
    make_text(
        "EP04_OPTIONAL_NARRATION", SEED["optional_narration"],
        (0.0, 0.45, -3.0), 0.038,
    )
    backdrop = cuboid(
        "EP04_TEXT_BACKDROP", (0.0, 0.72, -3.035), (1.72, 0.24, 0.008),
        backdrop_material, group, camera,
    )
    backdrop.hide_render = True
    group.hide_render = True
    group.hide_viewport = True

    beat_sheet = bpy.data.texts.new("EP04_BEAT_SHEET_README")
    beat_sheet.write(SEED["episode_title"] + "\n\n")
    for shot in SHOTS:
        beat_sheet.write(
            f"{shot['shot']} | {shot['beat']} | {shot['start_seconds']}s | "
            f"{shot['duration_seconds']}s | {shot['camera']} | {shot['description']}\n"
        )
    beat_sheet.write("\nDage uses the approved current 8x11 pet sprite sheet.\n")


def audit():
    assert_current_dage_source(MANIFEST, ROOT)
    scene = bpy.context.scene
    if bpy.data.collections.get(SEED["discovery_collection"]) is None:
        raise RuntimeError("Missing sunbeam study collection")
    if bpy.data.objects.get(SEED["discovery_prop"]) is None:
        raise RuntimeError("Missing sunbeam prop")
    for name in ("Cila", "Dixon", "Dage"):
        sprite = bpy.data.objects.get(f"SPRITE_{name}")
        if sprite is None or sprite.get("sprite_frame") is None:
            raise RuntimeError(f"Missing sprite {name}")
    dage = bpy.data.objects["SPRITE_Dage"]
    if dage.get("source_sheet") != MANIFEST["characters"]["Dage"]["source"]:
        raise RuntimeError("Dage is not using the current source sheet")
    holder = bpy.data.objects["EDITORIAL_MASTER_NLA"]
    tracks = {track.name: len(track.strips) for track in holder.animation_data.nla_tracks}
    if tracks.get("EP04_BEATS") != len(SHOTS):
        raise RuntimeError(f"Unexpected Episode 4 editorial tracks: {tracks}")
    counts = {
        "shots": len(SHOTS), "objects": len(bpy.data.objects),
        "actions": len(bpy.data.actions), "editorial_tracks": tracks,
        "runtime_seconds": int(SEED["runtime_seconds"]),
    }
    print("EP04_AUDIT", json.dumps(counts, sort_keys=True), flush=True)


def main():
    scene = bpy.context.scene
    if scene.get("episode04_setup_version") == SETUP_VERSION:
        print("EP04_ALREADY_CONFIGURED", flush=True)
        audit()
        return
    if scene.name != "CT_MASTER_EP01_TEMPLATE":
        raise RuntimeError("Start from the Episode 01 template blend")
    if OUTPUT.exists() and "--overwrite" not in sys.argv:
        raise FileExistsError(f"Output exists: {OUTPUT}")
    assert_current_dage_source(MANIFEST, ROOT)

    source_blend = Path(bpy.data.filepath).name
    make_sunbeam_study()
    configure_cameras()
    camera_target = configure_markers_and_target()
    controllers = {}
    for name in ("Cila", "Dixon", "Dage"):
        sprite, controller = create_sprite(name, camera_target)
        create_continuous_sprite_action(sprite, name)
        controllers[name] = controller
    animate_controllers(controllers)
    editorial_nla()
    add_text_cards()

    scene.name = "EP04_Sunbeam"
    for key in (
        "episode_number", "episode_title", "episode_seed", "audience_fact",
        "fact_label", "optional_narration", "discovery_prop",
        "discovery_collection", "lead_character", "runtime_seconds",
        "sprite_manifest",
    ):
        scene[key] = SEED[key]
    scene["supporting_characters"] = ", ".join(SEED["supporting_characters"])
    scene["episode01_source_blend"] = source_blend
    scene["episode04_setup_version"] = SETUP_VERSION
    scene["continuous_motion_policy"] = (
        "Sunbeam, character roots, Dage frame loops, breathing, and shadow test animate in motion"
    )
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = int(SEED["runtime_seconds"]) * FPS
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.frame_set(int(SHOT_BY_BEAT["DAGE_FINDS_WARM_SPOT"]["start_seconds"]) * FPS)
    audit()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print("EP04_SAVED", OUTPUT, flush=True)


if __name__ == "__main__":
    main()
