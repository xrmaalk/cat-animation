"""Build the role-aware Episode 05 condensation scene without rendering it."""

from pathlib import Path
import json
import math
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
from pipeline.sprite_manifest import assert_current_dage_source, grid_geometry, load_manifest


EPISODE_DIR = episode_directory(5, ROOT)
SEED, SHOTS = load_episode_plan(5, ROOT)
CONTRACT = json.loads(
    (EPISODE_DIR / SEED["performance_contract"]).read_text(encoding="utf-8")
)
MANIFEST = load_manifest(SEED["sprite_manifest"], ROOT)
FPS = int(SEED["fps"])
OUTPUT = ROOT / "Purrcilla_Dixon_Dage_EP05_Condensation.blend"
SETUP_VERSION = "EP05_Condensation_role_aware_v1"


def collection(name, parent=None):
    found = bpy.data.collections.get(name)
    if found:
        return found
    found = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(found)
    return found


def relink(obj, target):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target.objects.link(obj)
    return obj


def material(name, color, roughness=0.75, alpha=1.0, emission=0.0):
    found = bpy.data.materials.get(name)
    if found:
        return found
    found = bpy.data.materials.new(name)
    found.diffuse_color = (*color, alpha)
    found.use_nodes = True
    bsdf = found.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        if "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission
        elif "Emission" in bsdf.inputs:
            bsdf.inputs["Emission"].default_value = (*color, 1.0)
            bsdf.inputs["Emission Strength"].default_value = emission
    if alpha < 1.0 and hasattr(found, "surface_render_method"):
        found.surface_render_method = "DITHERED"
    return found


def cuboid(name, location, scale, mat, target, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=2, location=location)
    obj = relink(bpy.context.object, target)
    obj.name = name
    obj.scale = scale
    obj.parent = parent
    obj.data.materials.append(mat)
    return obj


def vertical_disc(name, location, scale, mat, target, vertices=48):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=1.0, depth=0.018, location=location
    )
    obj = relink(bpy.context.object, target)
    obj.name = name
    obj.rotation_euler.x = math.radians(90)
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def curves(action):
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    yield from bag.fcurves


def set_linear(action):
    for curve in curves(action):
        for point in curve.keyframe_points:
            point.interpolation = "LINEAR"


def set_sprite_interpolation(action):
    for curve in curves(action):
        mode = "CONSTANT" if curve.data_path == '["sprite_frame"]' else "BEZIER"
        for point in curve.keyframe_points:
            point.interpolation = mode


def key_location(obj, seconds, value):
    obj.location = value
    obj.keyframe_insert(data_path="location", frame=seconds * FPS)


def key_scale(obj, seconds, value):
    obj.scale = value
    obj.keyframe_insert(data_path="scale", frame=seconds * FPS)


def make_condensation_study():
    study = collection(SEED["discovery_collection"])
    root = bpy.data.objects.new(SEED["discovery_prop"], None)
    study.objects.link(root)
    root["role"] = "Episode 05 cool-window condensation experiment"

    for old_name in ("PROP_Cardboard_Box", "PROP_CardboardBox"):
        old = bpy.data.objects.get(old_name)
        if old:
            old.hide_render = True
            old.hide_set(True)

    glass = material("MAT_EP05_Cool_Glass", (0.45, 0.72, 0.82), 0.18, 0.18)
    frame = material("MAT_EP05_Window_Frame", (0.86, 0.82, 0.74), 0.55)
    fog_mat = material("MAT_EP05_Condensation", (0.82, 0.92, 0.96), 0.95, 0.48, 0.15)
    clear_mat = material("MAT_EP05_Clear_Trace", (0.30, 0.62, 0.78), 0.25, 0.32)
    cloth_mat = material("MAT_EP05_Warm_Cloth", (0.88, 0.26, 0.18), 0.8)
    coaster_mat = material("MAT_EP05_Cold_Coaster", (0.28, 0.50, 0.68), 0.32)
    droplet_mat = material("MAT_EP05_Droplets", (0.72, 0.90, 1.0), 0.2, 0.7, 0.25)

    pane_center = Vector((1.15, 0.66, 1.18))
    pane = cuboid("EP05_Cold_Window_Pane", pane_center, (1.32, 0.025, 0.88), glass, study, root)
    pane["temperature_role"] = "cool surface"
    for name, location, scale in (
        ("EP05_Window_Frame_Top", (1.15, 0.67, 2.10), (1.45, 0.05, 0.06)),
        ("EP05_Window_Frame_Bottom", (1.15, 0.67, 0.26), (1.45, 0.05, 0.06)),
        ("EP05_Window_Frame_Left", (-0.24, 0.67, 1.18), (0.06, 0.05, 0.98)),
        ("EP05_Window_Frame_Right", (2.54, 0.67, 1.18), (0.06, 0.05, 0.98)),
    ):
        cuboid(name, location, scale, frame, study, root)

    fog = vertical_disc(
        "EP05_Condensation_Patch", (1.12, 0.60, 1.22),
        (0.001, 0.001, 0.001), fog_mat, study,
    )
    fog.parent = root
    key_scale(fog, 0, (0.001, 0.001, 0.001))
    key_scale(fog, 2, (0.38, 0.30, 0.06))
    key_scale(fog, 9, (0.50, 0.40, 0.06))
    key_scale(fog, 14, (0.50, 0.40, 0.06))
    key_scale(fog, 18, (0.72, 0.54, 0.06))
    key_scale(fog, 86, (0.78, 0.58, 0.06))

    trace = cuboid(
        "EP05_Paw_Clear_Trace", (1.10, 0.555, 1.16),
        (0.001, 0.001, 0.001), clear_mat, study, root,
    )
    trace.rotation_euler.y = -0.12
    key_scale(trace, 0, (0.001, 0.001, 0.001))
    key_scale(trace, 19, (0.001, 0.001, 0.001))
    key_scale(trace, 20, (0.72, 0.012, 0.045))

    warm_corner = cuboid(
        "EP05_Warm_Clear_Corner", (1.92, 0.55, 0.77),
        (0.001, 0.001, 0.001), clear_mat, study, root,
    )
    key_scale(warm_corner, 0, (0.001, 0.001, 0.001))
    key_scale(warm_corner, 45, (0.001, 0.001, 0.001))
    key_scale(warm_corner, 46, (0.28, 0.012, 0.22))

    cloth = cuboid(
        "PROP_EP05_Warm_Cloth", (-1.25, -0.12, 0.42),
        (0.22, 0.04, 0.18), cloth_mat, study,
    )
    key_location(cloth, 0, (-1.25, -0.12, 0.42))
    key_location(cloth, 44, (-1.25, -0.12, 0.42))
    key_location(cloth, 46, (1.88, 0.32, 0.78))
    key_location(cloth, 51, (1.88, 0.32, 0.78))
    set_linear(cloth.animation_data.action)

    coaster = vertical_disc(
        "PROP_EP05_Cold_Coaster", (-1.60, -0.10, 0.72),
        (0.22, 0.22, 0.06), coaster_mat, study, vertices=32,
    )
    key_location(coaster, 0, (-1.60, -0.10, 0.72))
    key_location(coaster, 50, (-1.60, -0.10, 0.72))
    key_location(coaster, 51, (-0.25, -0.08, 0.72))
    key_location(coaster, 56, (-0.25, -0.08, 0.72))
    set_linear(coaster.animation_data.action)

    droplet_points = ((0.76, 0.93), (0.98, 1.34), (1.26, 1.02), (1.45, 1.50), (1.67, 1.16))
    droplets = []
    for index, (x_pos, z_pos) in enumerate(droplet_points, start=1):
        drop = vertical_disc(
            f"EP05_Droplet_{index}", (x_pos, 0.535, z_pos),
            (0.001, 0.001, 0.001), droplet_mat, study, vertices=24,
        )
        drop.parent = root
        key_scale(drop, 0, (0.001, 0.001, 0.001))
        key_scale(drop, 55, (0.001, 0.001, 0.001))
        key_scale(drop, 56, (0.045, 0.065, 0.025))
        droplets.append(drop)
    return root, fog, trace, warm_corner, cloth, coaster, droplets


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_cameras():
    poses = {
        "CAM_WindowReport": ((1.05, -4.75, 1.64), (1.08, 0.45, 1.10), 44),
        "CAM_HeroPortrait_Dixon": ((0.70, -4.45, 1.42), (0.78, 0.0, 1.00), 48),
        "CAM_CatEye_A": ((0.05, -6.15, 1.72), (0.25, 0.10, 0.82), 36),
        "CAM_Insert_Paws": ((0.92, -3.42, 0.88), (1.05, 0.40, 0.72), 58),
        "CAM_Insert_Eyes": ((0.88, -3.65, 1.58), (1.02, 0.18, 1.35), 64),
        "CAM_PorchWide": ((0.05, -6.80, 2.52), (0.20, 0.12, 0.82), 28),
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
        camera["ep05_target"] = target
    bpy.context.scene.camera = bpy.data.objects["CAM_WindowReport"]


def configure_markers_and_target():
    scene = bpy.context.scene
    edit = bpy.data.collections.get("EDIT_NLA") or collection("EDIT_NLA")
    target = bpy.data.objects.new("EP05_SPRITE_CAMERA_TARGET", None)
    edit.objects.link(target)
    target.empty_display_type = "SPHERE"
    target.empty_display_size = 0.12
    for shot in SHOTS:
        frame = int(shot["start_seconds"]) * FPS
        camera = bpy.data.objects[shot["camera"]]
        scene.frame_set(frame)
        marker = scene.timeline_markers.new(
            f"EP05_{shot['shot']}_{shot['beat']}", frame=frame
        )
        marker.camera = camera
        target.location = camera.matrix_world.translation.copy()
        target.keyframe_insert(data_path="location", frame=frame)
        card = bpy.data.objects.new(f"EP05_CARD_{shot['shot']}", None)
        edit.objects.link(card)
        card.hide_render = True
        for key in ("beat", "camera", "description", "dage_role", "dixon_role", "cila_role"):
            card[key] = shot[key]
        card["duration_seconds"] = int(shot["duration_seconds"])
    if target.animation_data and target.animation_data.action:
        for curve in curves(target.animation_data.action):
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

    controller = bpy.data.objects.new(f"EP05_{name}_Sprite_CTRL", None)
    group.objects.link(controller)
    controller.empty_display_type = "ARROWS"
    controller.empty_display_size = 0.25

    height = {"Cila": 1.78, "Dixon": 1.84, "Dage": 1.96}[name]
    width = sprite_plane_width(height, info)
    mesh = bpy.data.meshes.new(f"EP05_SPRITE_{name}_Mesh")
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
    sprite.location.z = -height * (cell_height - int(info["foot_pixel_range"][1])) / cell_height
    sprite["sprite_frame"] = int(info["frame_map"]["idle"])
    sprite["sprite_valid_frames"] = int(info["valid_frames"])
    sprite["source_sheet"] = info["source"]
    sprite["atlas_grid"] = atlas_grid_label(info)
    sprite["performance_contract"] = CONTRACT["version"]
    if name == "Dage":
        sprite["source_of_truth"] = "approved_current_8x11_pet_spritesheet"
        sprite["source_sha256"] = info["source_sha256"]

    image = bpy.data.images.load(str(atlas_path), check_existing=True)
    image.filepath = bpy.path.relpath(str(atlas_path))
    image.pack()
    mesh.materials.append(
        build_sprite_material(f"MAT_EP05_{name}_Sprite", image, sprite, info)
    )
    track = sprite.constraints.new("TRACK_TO")
    track.target = camera_target
    track.track_axis = "TRACK_NEGATIVE_Y"
    track.up_axis = "UP_Z"
    return sprite, controller


def create_continuous_performance(sprite, name):
    library = CONTRACT["characters"][name]
    column = name.lower()
    sprite.animation_data_create()
    sprite.animation_data.action = None
    for shot in SHOTS:
        action_name = shot[f"{column}_action"]
        sequence = library[action_name]["frames"]
        start = int(shot["start_seconds"]) * FPS
        end = (int(shot["start_seconds"]) + int(shot["duration_seconds"])) * FPS
        for index, frame in enumerate(range(start, end, 4)):
            sprite["sprite_frame"] = int(sequence[index % len(sequence)])
            sprite.keyframe_insert(
                data_path='["sprite_frame"]', frame=frame, group="Sprite Frame"
            )
        sprite["sprite_frame"] = int(sequence[-1])
        sprite.keyframe_insert(
            data_path='["sprite_frame"]', frame=end - 1, group="Sprite Frame"
        )

    for frame in range(0, int(SEED["runtime_seconds"]) * FPS, 12):
        phase = 1.0 if (frame // 12) % 2 == 0 else -1.0
        sprite.scale = (1.0 + 0.010 * phase, 1.0, 1.0 - 0.004 * phase)
        sprite.keyframe_insert(data_path="scale", frame=frame, group="Breathing")

    action = sprite.animation_data.action
    action.name = f"ACT_EP05_{name}_ROLE_AWARE_PERFORMANCE"
    action.use_fake_user = True
    action["episode"] = 5
    action["contract"] = CONTRACT["version"]
    set_sprite_interpolation(action)
    sprite.animation_data.action = None
    nla = sprite.animation_data.nla_tracks.new()
    nla.name = f"EP05_{name}_SPRITE_PERFORMANCE"
    strip = nla.strips.new(f"EP05_{name}_CONTINUOUS", 0, action)
    if hasattr(strip, "action_slot") and action.slots:
        strip.action_slot = action.slots[0]


def animate_controllers(controllers):
    paths = {
        "Dixon": [
            (0, (0.86, -0.12, 0.0)), (20, (0.92, -0.10, 0.0)),
            (41, (1.02, -0.06, 0.0)), (61, (0.82, -0.10, 0.0)),
            (77, (0.55, -0.16, 0.0)), (86, (0.72, -0.12, 0.0)),
        ],
        "Cila": [
            (0, (-2.15, 0.12, 0.0)), (30, (-2.15, 0.12, 0.0)),
            (35, (-0.55, 0.02, 0.0)), (46, (0.15, -0.02, 0.0)),
            (51, (0.05, -0.02, 0.0)), (77, (-0.20, -0.04, 0.0)),
            (86, (-0.20, -0.04, 0.0)),
        ],
        "Dage": [
            (0, (-2.85, 0.32, 0.0)), (35, (-2.85, 0.32, 0.0)),
            (41, (-1.30, 0.08, 0.0)), (51, (-0.62, 0.02, 0.0)),
            (56, (-0.45, 0.02, 0.0)), (77, (-1.02, -0.02, 0.0)),
            (86, (-1.02, -0.02, 0.0)),
        ],
    }
    for name, points in paths.items():
        controller = controllers[name]
        for seconds, position in points:
            key_location(controller, seconds, position)
        action = controller.animation_data.action
        action.name = f"ACT_EP05_{name}_ROOT_MOTION"
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
    originals = sorted(source.strips, key=lambda item: item.frame_start)
    episode = holder.animation_data.nla_tracks.new()
    episode.name = "EP05_BEATS"
    for index, shot in enumerate(SHOTS):
        action = originals[index % len(originals)].action.copy()
        action.name = f"ACT_EP05_{shot['shot']}_{shot['beat']}"
        action.use_fake_user = True
        action["episode"] = 5
        for key in ("beat", "camera", "description", "dage_role", "dixon_role", "cila_role"):
            action[key] = shot[key]
        start = int(shot["start_seconds"]) * FPS
        duration = int(shot["duration_seconds"]) * FPS
        strip = episode.strips.new(f"EP05_{shot['shot']}_{shot['beat']}", start, action)
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]
        first, last = action.frame_range
        strip.action_frame_start = first
        strip.action_frame_end = max(first + 1, last)
        strip.scale = (duration - 1) / (strip.action_frame_end - first)
        strip.blend_type = "REPLACE"
    holder["episode05_editorial"] = "17 role-aware short-format story beats"


def add_text_cards():
    group = bpy.data.collections.get("NARRATION_TEXT_OFF")
    if group is None:
        raise RuntimeError("Missing NARRATION_TEXT_OFF")
    for obj in group.objects:
        obj.hide_render = True
    camera = bpy.data.objects["CAM_CatEye_A"]
    text_mat = material("MAT_EP05_Text", (0.82, 0.94, 1.0), 0.6, 1.0, 0.6)

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
        obj.data.materials.append(text_mat)
        obj.hide_render = True
        obj["episode"] = 5
        return obj

    make_text(
        "EP05_TITLE_CARD", "Dixon Discovers\nWhy the Window Turns Cloudy",
        (0.0, 0.58, -3.0), 0.062,
    )
    make_text(
        "EP05_FACT_LABEL", SEED["fact_label"],
        (0.0, 0.68, -3.0), 0.068,
    )
    make_text(
        "EP05_OPTIONAL_NARRATION", SEED["optional_narration"],
        (0.0, 0.44, -3.0), 0.036,
    )
    group.hide_render = True
    group.hide_viewport = True

    contract_text = bpy.data.texts.new("EP05_PERFORMANCE_CONTRACT")
    contract_text.write(json.dumps(CONTRACT, indent=2))
    beat_sheet = bpy.data.texts.new("EP05_BEAT_SHEET_README")
    beat_sheet.write(SEED["episode_title"] + "\n\n")
    for shot in SHOTS:
        beat_sheet.write(
            f"{shot['shot']} | {shot['beat']} | {shot['start_seconds']}s | "
            f"{shot['duration_seconds']}s | {shot['camera']} | "
            f"Dage={shot['dage_action']}/{shot['dage_role']} | "
            f"Dixon={shot['dixon_action']}/{shot['dixon_role']} | "
            f"Cila={shot['cila_action']}/{shot['cila_role']}\n"
        )


def audit():
    assert_current_dage_source(MANIFEST, ROOT)
    for name in ("Cila", "Dixon", "Dage"):
        sprite = bpy.data.objects.get(f"SPRITE_{name}")
        if sprite is None or sprite.get("performance_contract") != CONTRACT["version"]:
            raise RuntimeError(f"Missing role-aware sprite {name}")
    dage = bpy.data.objects["SPRITE_Dage"]
    if dage.get("source_sheet") != MANIFEST["characters"]["Dage"]["source"]:
        raise RuntimeError("Dage is not using the current source sheet")
    holder = bpy.data.objects["EDITORIAL_MASTER_NLA"]
    tracks = {track.name: len(track.strips) for track in holder.animation_data.nla_tracks}
    if tracks.get("EP05_BEATS") != len(SHOTS):
        raise RuntimeError(f"Unexpected editorial tracks: {tracks}")
    if bpy.data.objects.get("EP05_Condensation_Patch") is None:
        raise RuntimeError("Missing condensation animation")
    print(
        "EP05_AUDIT",
        json.dumps({
            "shots": len(SHOTS), "runtime_seconds": int(SEED["runtime_seconds"]),
            "contract": CONTRACT["version"], "objects": len(bpy.data.objects),
            "actions": len(bpy.data.actions), "editorial_tracks": tracks,
        }, sort_keys=True),
        flush=True,
    )


def main():
    scene = bpy.context.scene
    if scene.get("episode05_setup_version") == SETUP_VERSION:
        print("EP05_ALREADY_CONFIGURED", flush=True)
        audit()
        return
    if scene.name != "CT_MASTER_EP01_TEMPLATE":
        raise RuntimeError("Start from the Episode 01 template blend")
    if OUTPUT.exists() and "--overwrite" not in sys.argv:
        raise FileExistsError(f"Output exists: {OUTPUT}")
    assert_current_dage_source(MANIFEST, ROOT)

    source_blend = Path(bpy.data.filepath).name
    make_condensation_study()
    configure_cameras()
    target = configure_markers_and_target()
    controllers = {}
    for name in ("Cila", "Dixon", "Dage"):
        sprite, controller = create_sprite(name, target)
        create_continuous_performance(sprite, name)
        controllers[name] = controller
    animate_controllers(controllers)
    editorial_nla()
    add_text_cards()

    scene.name = "EP05_Condensation"
    for key in (
        "episode_number", "episode_title", "episode_seed", "audience_fact",
        "fact_label", "optional_narration", "discovery_prop",
        "discovery_collection", "lead_character", "runtime_seconds",
        "sprite_manifest", "performance_contract",
    ):
        scene[key] = SEED[key]
    scene["supporting_characters"] = ", ".join(SEED["supporting_characters"])
    scene["episode01_source_blend"] = source_blend
    scene["episode05_setup_version"] = SETUP_VERSION
    scene["performance_contract_version"] = CONTRACT["version"]
    scene["render_status"] = "NOT_RENDERED_BY_DESIGN"
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = int(SEED["runtime_seconds"]) * FPS
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene.frame_set(9 * FPS)
    audit()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print("EP05_SAVED_NO_RENDER", OUTPUT, flush=True)


if __name__ == "__main__":
    main()
