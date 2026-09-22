"""Create the non-destructive Episode 02 cardboard-box Blender file.

  blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend \
    --python build_episode02.py

The source .blend is never overwritten. Run prepare_episode02_sprites.py first.
Run this script again on the Episode 02 output to check idempotency; an already
configured file is audited and left unchanged.
"""

import csv
import json
import math
import os
from pathlib import Path
import sys

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dage_neck_patch import (
    MARK_VERSION,
    mark_version_is_supported,
    require_front_neck_patch,
)

SEED = json.loads((ROOT / "episode02_seed.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / SEED["sprite_manifest"]).read_text(encoding="utf-8"))
with (ROOT / SEED["shotlist"]).open(newline="", encoding="utf-8") as handle:
    SHOTS = list(csv.DictReader(handle))
FPS = SEED["fps"]
OUTPUT = ROOT / "Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend"
SETUP_VERSION = "EP02_CardboardBox_v1"
BOX_CENTER = Vector((-1.0, -0.25, 0.0))


def collection(name, parent=None):
    found = bpy.data.collections.get(name)
    if found:
        return found
    found = bpy.data.collections.new(name)
    (parent or bpy.context.scene.collection).children.link(found)
    return found


def color_material(name, color, roughness=0.85):
    found = bpy.data.materials.get(name)
    if found:
        return found
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*color, 1.0)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return material


def cuboid(name, loc, scale, material, target_collection, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = name
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    target_collection.objects.link(obj)
    obj.parent = parent
    obj.location = loc
    obj.scale = scale
    obj.data.materials.append(material)
    return obj


def key(obj, path, frame, value):
    if path == "location":
        obj.location = value
    elif path == "rotation_euler":
        obj.rotation_euler = value
    else:
        raise ValueError(path)
    obj.keyframe_insert(data_path=path, frame=frame)


def make_box():
    box_collection = collection(SEED["discovery_collection"])
    root = bpy.data.objects.new(SEED["discovery_prop"], None)
    box_collection.objects.link(root)
    root.location = BOX_CENTER
    root["role"] = "Episode 02 open cardboard study box"
    cardboard = color_material("MAT_EP02_Cardboard", (0.55, 0.32, 0.14))
    edge = color_material("MAT_EP02_Cardboard_Edge", (0.38, 0.20, 0.075))
    inside = color_material("MAT_EP02_Box_Interior", (0.25, 0.14, 0.065))
    cuboid("EP02_Box_Bottom", (0, 0, 0.04), (0.85, 0.68, 0.04), cardboard, box_collection, root)
    cuboid("EP02_Box_Interior", (0, 0, 0.09), (0.80, 0.62, 0.015), inside, box_collection, root)
    cuboid("EP02_Box_Back", (0, 0.65, 0.37), (0.85, 0.035, 0.34), cardboard, box_collection, root)
    cuboid("EP02_Box_Left", (-0.82, 0, 0.37), (0.035, 0.65, 0.34), cardboard, box_collection, root)
    cuboid("EP02_Box_Right", (0.82, 0, 0.37), (0.035, 0.65, 0.34), cardboard, box_collection, root)
    cuboid("EP02_Box_Front_Low", (0, -0.65, 0.18), (0.85, 0.035, 0.15), cardboard, box_collection, root)
    for side in (-1, 1):
        cuboid(f"EP02_Box_Rim_{side}", (side * 0.82, 0, 0.71),
               (0.05, 0.67, 0.025), edge, box_collection, root)
    flap_pivot = bpy.data.objects.new("EP02_Box_Front_Flap_Pivot", None)
    box_collection.objects.link(flap_pivot)
    flap_pivot.parent = root
    flap_pivot.location = (0, -0.67, 0.31)
    cuboid("EP02_Box_Front_Flap", (0, -0.25, 0),
           (0.82, 0.25, 0.025), cardboard, box_collection, flap_pivot)
    # Dage's paw makes the flap move, then the boundary settles back.
    flap_keys = [(0, -0.35), (180 * FPS, -0.35), (195 * FPS, -0.83),
                 (216 * FPS, -0.53), (235 * FPS, -0.35),
                 (738 * FPS, -0.35), (751 * FPS, -0.55),
                 (768 * FPS, -0.35), (1020 * FPS, -0.35)]
    for frame, angle in flap_keys:
        key(flap_pivot, "rotation_euler", frame, (math.radians(angle * 35), 0, 0))
    old_box = bpy.data.objects.get("PROP_Cardboard_Box")
    if old_box:
        old_box.hide_render = True
        old_box.hide_set(True)
    return root, flap_pivot


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_cameras():
    poses = {
        "CAM_CatEye_A": ((0.0, -5.0, 1.55), (-0.6, -0.2, 0.85), 28),
        "CAM_CondoPeek": ((1.9, -2.8, 1.35), (-0.9, -0.2, 0.85), 50),
        "CAM_HeroPortrait_Dage": ((0.45, -2.7, 1.30), (-0.65, -0.15, 1.08), 62),
        "CAM_HeroPortrait_Dixon": ((2.65, -2.5, 1.35), (1.25, -0.05, 1.15), 62),
        "CAM_HeroPortrait_Cila": ((-3.6, -2.6, 1.40), (-1.9, -0.45, 0.95), 50),
        "CAM_WindowReport": ((1.5, -4.0, 1.6), (0.5, 0.0, 0.9), 36),
        "CAM_PorchWide": ((-2.6, -4.8, 2.6), (-1.0, -0.3, 0.75), 28),
        "CAM_Insert_Paws": ((0.8, -2.9, 1.15), (-0.6, -0.25, 0.6), 45),
        "CAM_Insert_Eyes": ((0.2, -2.0, 1.35), (-0.8, -0.2, 1.1), 78),
    }
    for name, (position, target, lens) in poses.items():
        camera = bpy.data.objects.get(name)
        if camera is None or camera.type != "CAMERA":
            raise RuntimeError(f"Missing template camera {name}")
        if camera.animation_data and camera.animation_data.action:
            camera.animation_data.action.use_fake_user = True
            camera.animation_data_clear()
        camera.location = position
        look_at(camera, target)
        camera.data.lens = lens
        camera["ep02_target"] = target
    # The Dixon portrait camera is reused before and after he approaches the
    # box. Keep its existing name and give it two Episode 02 compositions.
    dixon_portrait = bpy.data.objects["CAM_HeroPortrait_Dixon"]
    for seconds, position, target in (
        (0, (3.85, -1.7, 1.5), (2.9, 1.4, 1.2)),
        (72, (3.85, -1.7, 1.5), (2.9, 1.4, 1.2)),
        (390, (2.65, -2.5, 1.35), (1.25, -0.05, 1.15)),
        (1020, (2.65, -2.5, 1.35), (1.25, -0.05, 1.15)),
    ):
        dixon_portrait.location = position
        look_at(dixon_portrait, target)
        dixon_portrait.keyframe_insert(data_path="location", frame=seconds * FPS)
        dixon_portrait.keyframe_insert(data_path="rotation_euler", frame=seconds * FPS)
    if dixon_portrait.animation_data and dixon_portrait.animation_data.action:
        dixon_portrait.animation_data.action.name = "ACT_EP02_CAM_Dixon_Portrait"
        dixon_portrait.animation_data.action.use_fake_user = True
    scene = bpy.context.scene
    scene.camera = bpy.data.objects["CAM_CatEye_A"]
    return poses


def math_node(nodes, operation, a=None, b=None):
    node = nodes.new("ShaderNodeMath")
    node.operation = operation
    if a is not None:
        node.inputs[0].default_value = a
    if b is not None:
        node.inputs[1].default_value = b
    return node


def sprite_material(name, image, sprite):
    material = bpy.data.materials.new(f"MAT_EP02_{name}_Sprite")
    material.use_nodes = True
    material.use_backface_culling = False
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    output = nodes.new("ShaderNodeOutputMaterial")
    uv = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uv.outputs["UV"], separate.inputs[0])
    frame = nodes.new("ShaderNodeValue")
    frame.label = "Driven by sprite_frame on SPRITE_" + name
    frame.outputs[0].default_value = 0
    driver = frame.outputs[0].driver_add("default_value").driver
    driver.type = "SCRIPTED"
    variable = driver.variables.new()
    variable.name = "sprite_index"
    variable.type = "SINGLE_PROP"
    variable.targets[0].id = sprite
    variable.targets[0].data_path = '["sprite_frame"]'
    driver.expression = "sprite_index"

    u_scale = math_node(nodes, "MULTIPLY", b=1.0 / 7.0)
    column = math_node(nodes, "MODULO", b=7.0)
    column_scale = math_node(nodes, "MULTIPLY", b=1.0 / 7.0)
    u_add = math_node(nodes, "ADD")
    links.new(separate.outputs["X"], u_scale.inputs[0])
    links.new(frame.outputs[0], column.inputs[0])
    links.new(column.outputs[0], column_scale.inputs[0])
    links.new(u_scale.outputs[0], u_add.inputs[0])
    links.new(column_scale.outputs[0], u_add.inputs[1])

    v_scale = math_node(nodes, "MULTIPLY", b=1.0 / 10.0)
    row_divide = math_node(nodes, "DIVIDE", b=7.0)
    row_floor = math_node(nodes, "FLOOR")
    row_reverse = math_node(nodes, "SUBTRACT", a=9.0)
    row_scale = math_node(nodes, "MULTIPLY", b=1.0 / 10.0)
    v_add = math_node(nodes, "ADD")
    links.new(separate.outputs["Y"], v_scale.inputs[0])
    links.new(frame.outputs[0], row_divide.inputs[0])
    links.new(row_divide.outputs[0], row_floor.inputs[0])
    links.new(row_floor.outputs[0], row_reverse.inputs[1])
    links.new(row_reverse.outputs[0], row_scale.inputs[0])
    links.new(v_scale.outputs[0], v_add.inputs[0])
    links.new(row_scale.outputs[0], v_add.inputs[1])

    combine = nodes.new("ShaderNodeCombineXYZ")
    links.new(u_add.outputs[0], combine.inputs["X"])
    links.new(v_add.outputs[0], combine.inputs["Y"])
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Closest"
    texture.extension = "CLIP"
    links.new(combine.outputs[0], texture.inputs["Vector"])
    emission = nodes.new("ShaderNodeEmission")
    transparent = nodes.new("ShaderNodeBsdfTransparent")
    mix = nodes.new("ShaderNodeMixShader")
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    links.new(texture.outputs["Alpha"], mix.inputs[0])
    links.new(transparent.outputs[0], mix.inputs[1])
    links.new(emission.outputs[0], mix.inputs[2])
    links.new(mix.outputs[0], output.inputs["Surface"])
    return material


def create_sprite(name, camera_target):
    info = MANIFEST["characters"][name]
    atlas_path = ROOT / info["atlas"]
    if not atlas_path.is_file():
        raise FileNotFoundError(atlas_path)
    character_collection = bpy.data.collections.get(f"CHAR_{name}")
    if character_collection is None:
        raise RuntimeError(f"Missing CHAR_{name}")
    for obj in character_collection.objects:
        if obj.type == "MESH":
            obj.hide_render = True
            obj.hide_set(True)
    controller = bpy.data.objects.new(f"EP02_{name}_Sprite_CTRL", None)
    character_collection.objects.link(controller)
    controller.empty_display_type = "ARROWS"
    controller.empty_display_size = 0.25
    controller["episode_role"] = "Sprite movement; original 3D rig remains a reference"
    height = {"Cila": 1.83, "Dixon": 1.82, "Dage": 1.96}[name]
    mesh = bpy.data.meshes.new(f"SPRITE_{name}_Mesh")
    mesh.from_pydata([(-height / 2, 0, 0), (height / 2, 0, 0),
                      (height / 2, 0, height), (-height / 2, 0, height)],
                     [], [(0, 1, 2, 3)])
    mesh.update()
    uv = mesh.uv_layers.new(name="SpriteCellUV")
    points = ((1, 0), (0, 0), (0, 1), (1, 1)) if name in ("Dixon", "Dage") else (
        (0, 0), (1, 0), (1, 1), (0, 1))
    for loop, point in zip(mesh.polygons[0].loop_indices, points):
        uv.data[loop].uv = point
    sprite = bpy.data.objects.new(f"SPRITE_{name}", mesh)
    character_collection.objects.link(sprite)
    sprite.parent = controller
    sprite.location = (0, 0, -0.04)
    sprite["sprite_frame"] = info["frame_map"]["idle"]
    if name == "Dage":
        require_front_neck_patch(info["frame_map"]["idle"])
        sprite["dage_front_neck_patch_art"] = MARK_VERSION
    sprite["sprite_valid_frames"] = info["valid_frames"]
    sprite["source_sheet"] = info["source"]
    sprite["atlas_grid"] = "7x10, 192px cells, top-left row-major"
    image = bpy.data.images.load(str(atlas_path), check_existing=True)
    image.filepath = bpy.path.relpath(str(atlas_path))
    image.pack()
    mesh.materials.append(sprite_material(name, image, sprite))
    track = sprite.constraints.new("TRACK_TO")
    track.target = camera_target
    track.track_axis = "TRACK_NEGATIVE_Y"
    track.up_axis = "UP_Z"
    return sprite, controller


def set_constant(action):
    # Blender 5.x stores curves in layered Action channel bags.
    for layer in action.layers:
        for strip in layer.strips:
            for slot in action.slots:
                bag = strip.channelbag(slot)
                if bag:
                    for curve in bag.fcurves:
                        for point in curve.keyframe_points:
                            point.interpolation = "CONSTANT"


def create_sprite_actions(sprite, name, frame_map):
    sequences = {pose.upper(): [(0, frame), (1, frame)]
                 for pose, frame in frame_map.items()}
    if name == "Dage":
        sequences["ENTER_BOX"] = [(0, 9), (6, 10), (12, 11),
                                  (18, 12), (24, 13)]
    if name == "Cila":
        sequences["APPROACH"] = [(0, 14), (6, 15), (12, 16),
                                 (18, 17), (24, 18)]
    actions = {}
    sprite.animation_data_create()
    for pose, keys in sequences.items():
        sprite.animation_data.action = None
        for frame, index in keys:
            sprite["sprite_frame"] = index
            sprite.keyframe_insert(data_path='["sprite_frame"]', frame=frame,
                                   group="Sprite Frame")
            if name == "Dage":
                require_front_neck_patch(index)
        action = sprite.animation_data.action
        action.name = f"ACT_{name}_{pose}"
        action.use_fake_user = True
        action["episode"] = 2
        action["pose"] = pose
        set_constant(action)
        actions[pose] = action
    sprite.animation_data.action = None
    sprite["sprite_frame"] = frame_map["idle"]
    return actions


def add_sprite_nla(sprite, name, actions):
    nla = sprite.animation_data.nla_tracks.new()
    nla.name = f"EP02_{name}_SPRITE_ACTIONS"
    for shot in SHOTS:
        pose = shot[f"{name.lower()}_action"]
        action = actions[pose]
        start = int(shot["start_seconds"]) * FPS
        duration = int(shot["duration_seconds"]) * FPS
        strip = nla.strips.new(f"EP02_{shot['shot']}_{name}_{pose}", start, action)
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]
        first, last = action.frame_range
        strip.action_frame_start = first
        strip.action_frame_end = max(first + 1, last)
        # NLA frame_end is inclusive. End one frame before the next shot so
        # the incoming sprite pose takes effect on its camera-cut frame.
        strip.scale = (duration - 1) / (strip.action_frame_end - strip.action_frame_start)
        strip.blend_type = "REPLACE"
    return nla


def animate_controllers(controllers):
    paths = {
        "Dage": [(0, (1.45, -0.25, 0)), (108, (1.45, -0.25, 0)),
                 (132, (1.35, -0.3, 0)), (156, (0.65, -0.5, 0)),
                 (180, (0.25, -0.5, 0)), (216, (0.15, -0.45, 0)),
                 (252, (0.15, -0.45, 0)), (294, (-1.0, -0.05, 0.08)),
                 (528, (-1.0, -0.05, 0.08)), (576, (0.15, -0.55, 0)),
                 (636, (-1.0, -0.05, 0.08)), (1020, (-1.0, -0.05, 0.08))],
        "Dixon": [(0, (2.9, 1.4, 0)), (336, (2.9, 1.4, 0)),
                  (390, (1.2, -0.25, 0)), (1020, (1.2, -0.25, 0))],
        "Cila": [(0, (-3.1, -0.65, 0)), (438, (-3.1, -0.65, 0)),
                 (480, (-2.3, -0.65, 0)), (1020, (-2.3, -0.65, 0))],
    }
    for name, points in paths.items():
        controller = controllers[name]
        for seconds, position in points:
            key(controller, "location", seconds * FPS, position)
        if controller.animation_data and controller.animation_data.action:
            controller.animation_data.action.name = f"ACT_EP02_{name}_ROOT_MOTION"
            controller.animation_data.action.use_fake_user = True


def editorial_nla():
    holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
    if holder is None or not holder.animation_data:
        raise RuntimeError("Missing Episode 01 editorial NLA holder")
    old_track = next((t for t in holder.animation_data.nla_tracks
                      if t.name == "EP01_BEATS"), None)
    if old_track is None or len(old_track.strips) != len(SHOTS):
        raise RuntimeError("Episode 01 NLA layout does not match the 26-shot Episode 02 plan")
    for shot, old in zip(SHOTS, old_track.strips):
        start = int(shot["start_seconds"]) * FPS
        duration = int(shot["duration_seconds"]) * FPS
        if round(old.frame_start) != start or round(old.frame_end) != start + duration - 1:
            raise RuntimeError(f"Timing mismatch at {shot['shot']}")
    old_track.mute = True
    track = holder.animation_data.nla_tracks.new()
    track.name = "EP02_BEATS"
    for shot, old in zip(SHOTS, old_track.strips):
        action = old.action.copy()
        action.name = f"ACT_EP02_{shot['shot']}_{shot['beat']}"
        action.use_fake_user = True
        for field in ("beat", "camera", "note"):
            action[field] = shot["description"] if field == "note" else shot[field if field != "beat" else "beat"]
        action["episode"] = 2
        strip = track.strips.new(f"EP02_{shot['shot']}_{shot['beat']}",
                                 int(shot["start_seconds"]) * FPS, action)
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]
        strip.action_frame_start = old.action_frame_start
        strip.action_frame_end = old.action_frame_end
        strip.blend_type = "REPLACE"
    holder["episode02_editorial"] = "26 modular blocks, Episode 01 timing retained"


def configure_markers_and_notes(camera_poses):
    scene = bpy.context.scene
    edit = bpy.data.collections["EDIT_NLA"]
    target = bpy.data.objects.new("EP02_SPRITE_CAMERA_TARGET", None)
    edit.objects.link(target)
    target.empty_display_type = "SPHERE"
    target.empty_display_size = 0.12
    for shot in SHOTS:
        frame = int(shot["start_seconds"]) * FPS
        camera = bpy.data.objects[shot["camera"]]
        scene.frame_set(frame)
        marker = scene.timeline_markers.new(f"EP02_{shot['shot']}_{shot['beat']}", frame=frame)
        marker.camera = camera
        key(target, "location", frame, camera.matrix_world.translation.copy())
        card = bpy.data.objects.new(f"EP02_CARD_{shot['shot']}", None)
        edit.objects.link(card)
        card.hide_render = True
        card["beat"] = shot["beat"]
        card["camera"] = shot["camera"]
        card["note"] = shot["description"]
        card["duration_seconds"] = int(shot["duration_seconds"])
    if target.animation_data and target.animation_data.action:
        target.animation_data.action.name = "ACT_EP02_SPRITE_CAMERA_TARGET"
        target.animation_data.action.use_fake_user = True
        for layer in target.animation_data.action.layers:
            for strip in layer.strips:
                for slot in target.animation_data.action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in bag.fcurves:
                            for point in curve.keyframe_points:
                                point.interpolation = "CONSTANT"
    return target


def add_text():
    group = bpy.data.collections.get("NARRATION_TEXT_OFF")
    if group is None:
        raise RuntimeError("Missing NARRATION_TEXT_OFF collection")
    source = bpy.data.objects.get("LOWER_THIRD_blinds")
    if source is None:
        raise RuntimeError("Missing narration label template")
    # Keep the Episode 01 labels as datablocks, but let the EP02 fact pass be
    # enabled without revealing unrelated words about blinds and sunlight.
    for obj in group.objects:
        if obj.name.startswith("LOWER_THIRD_"):
            obj.hide_render = True
            obj.hide_set(True)
    camera = bpy.data.objects["CAM_CatEye_A"]
    for name, body, loc, size in (
        ("EP02_FACT_LABEL", SEED["fact_label"], (0, 0.72, -3.0), 0.09),
        ("EP02_OPTIONAL_NARRATION", SEED["optional_narration"],
         (0, 0.48, -3.0), 0.045),
    ):
        text = source.copy()
        text.data = source.data.copy()
        text.name = name
        text.data.body = body
        text.data.size = size
        text.data.align_x = "CENTER"
        text.parent = camera
        text.location = loc
        text.rotation_euler = (0, 0, 0)
        group.objects.link(text)
        text["episode"] = 2
        text.hide_render = False
        if name == "EP02_OPTIONAL_NARRATION":
            text.hide_render = True
    backdrop = cuboid("EP02_FACT_BACKDROP", (0, 0.75, -3.03),
                      (1.64, 0.18, 0.005),
                      color_material("MAT_EP02_Fact_Backdrop", (0.035, 0.025, 0.05)),
                      group, camera)
    backdrop["episode"] = 2
    group.hide_render = True
    group.hide_viewport = True
    beat_sheet = bpy.data.texts.new("EP02_BEAT_SHEET_README")
    beat_sheet.write(SEED["episode_title"] + "\n\n")
    for shot in SHOTS:
        beat_sheet.write(f"{shot['shot']} | {shot['beat']} | {shot['start_seconds']}s | "
                         f"{shot['duration_seconds']}s | {shot['camera']} | {shot['description']}\n")
    beat_sheet.write("\nNarration and fact label OFF by default. Preserve quiet holds and slow blinks.\n")


def audit():
    scene = bpy.context.scene
    expected = ["SET_BoxStudy", "CHAR_Cila", "CHAR_Dixon", "CHAR_Dage",
                "NARRATION_TEXT_OFF"]
    for name in expected:
        if bpy.data.collections.get(name) is None:
            raise RuntimeError(f"Missing collection {name}")
    for name in ("Cila", "Dixon", "Dage"):
        sprite = bpy.data.objects.get(f"SPRITE_{name}")
        if sprite is None or sprite.get("sprite_frame") is None:
            raise RuntimeError(f"Missing sprite or sprite_frame: {name}")
        if sprite.name not in bpy.data.collections[f"CHAR_{name}"].objects:
            raise RuntimeError(f"Sprite outside CHAR_{name}")
        patch_version = (sprite.get("dage_front_neck_patch_art") or
                         sprite.get("dage_chin_art"))
        if name == "Dage" and not mark_version_is_supported(patch_version):
            raise RuntimeError("Dage sheet needs upgrading; run apply_dage_sprite_sheet.py")
    holder = bpy.data.objects["EDITORIAL_MASTER_NLA"]
    tracks = {track.name: len(track.strips)
              for track in holder.animation_data.nla_tracks}
    if tracks.get("EP01_BEATS") != 26 or tracks.get("EP02_BEATS") != 26:
        raise RuntimeError(f"Expected 26 editorial strips per episode: {tracks}")
    counts = {"scenes": len(bpy.data.scenes), "collections": len(bpy.data.collections),
              "objects": len(bpy.data.objects), "actions": len(bpy.data.actions),
              "materials": len(bpy.data.materials), "editorial_tracks": tracks}
    print("EP02_AUDIT", json.dumps(counts, sort_keys=True), flush=True)
    return counts


def main():
    scene = bpy.context.scene
    if scene.get("episode02_setup_version") == SETUP_VERSION:
        print("EP02_ALREADY_CONFIGURED; no objects or actions added", flush=True)
        audit()
        return
    if scene.name != "CT_MASTER_EP01_TEMPLATE":
        raise RuntimeError("Start from the existing Episode 01 template blend")
    if OUTPUT.exists() and "--overwrite" not in sys.argv:
        raise FileExistsError(f"Output exists: {OUTPUT}")
    if len(SHOTS) != 26 or int(SHOTS[-1]["start_seconds"]) + int(SHOTS[-1]["duration_seconds"]) != 1020:
        raise RuntimeError("Episode 02 shot list must retain 26 blocks and 17:00 runtime")
    for name in ("Cila", "Dixon", "Dage"):
        if (ROOT / MANIFEST["characters"][name]["atlas"]).is_file() is False:
            raise FileNotFoundError(f"Missing prepared atlas for {name}")

    scene.frame_set(0)
    source_blend = Path(bpy.data.filepath).name
    make_box()
    camera_poses = configure_cameras()
    camera_target = configure_markers_and_notes(camera_poses)
    controllers = {}
    for name in ("Cila", "Dixon", "Dage"):
        sprite, controller = create_sprite(name, camera_target)
        actions = create_sprite_actions(sprite, name,
                                        MANIFEST["characters"][name]["frame_map"])
        add_sprite_nla(sprite, name, actions)
        controllers[name] = controller
    animate_controllers(controllers)
    editorial_nla()
    add_text()
    scene.name = "EP02_Cardboard_Box"
    scene["episode_number"] = SEED["episode_number"]
    scene["episode_title"] = SEED["episode_title"]
    scene["episode_seed"] = SEED["episode_seed"]
    scene["audience_fact"] = SEED["audience_fact"]
    scene["fact_label"] = SEED["fact_label"]
    scene["optional_narration"] = SEED["optional_narration"]
    scene["discovery_prop"] = SEED["discovery_prop"]
    scene["discovery_collection"] = SEED["discovery_collection"]
    scene["lead_character"] = SEED["lead_character"]
    scene["sprite_manifest"] = SEED["sprite_manifest"]
    scene["episode01_source_blend"] = source_blend
    scene["episode02_setup_version"] = SETUP_VERSION
    scene["sprite_rig_policy"] = "EP02 sprite planes use their own actions; 3D rigs remain as hidden references"
    scene.frame_set(108 * FPS)
    audit()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print("EP02_SAVED", OUTPUT, flush=True)


if __name__ == "__main__":
    main()
