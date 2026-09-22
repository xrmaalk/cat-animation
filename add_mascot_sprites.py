"""Attach animated mascot-sheet cutouts to the short's character roots.

Example:
  blender --background Purrcilla_Dixon_Dage_Animated_Short.blend \
    --python add_mascot_sprites.py

Run prepare_episode02_sprites.py first. The script saves a sibling
*_Mascot_Sprites.blend and refuses to replace it without -- --overwrite.
The source animated short, its root motion, and its camera remain intact.
"""

import json
import os
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dage_neck_patch import MARK_VERSION, require_front_neck_patch

MANIFEST_PATH = ROOT / "references" / "mascot_sprites" / "episode02_atlases" / "episode02_sprite_manifest.json"
COLLECTION_NAME = "SPRITES_MAALTECH_LOOKDEV"
HEIGHTS = {"Cila": 1.55, "Dixon": 1.70, "Dage": 1.70}
FRAME_SEQUENCE = {
    # 12-second short: notice, Dixon's reach, moving light, shared view.
    "Cila": [(1, 0), (72, 5), (90, 0), (188, 5),
             (205, 14), (214, 15), (222, 16), (230, 0),
             (239, 37), (245, 0)],
    "Dixon": [(1, 0), (35, 15), (85, 18), (108, 20),
              (122, 3), (137, 6), (153, 19), (191, 0),
              (239, 43), (252, 1), (257, 0)],
    "Dage": [(1, 0), (170, 6), (191, 0), (215, 9),
             (225, 10), (238, 42), (263, 41), (268, 42)],
}


def argument(name, default=None):
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return args[args.index(name) + 1] if name in args else default


def math_node(nodes, operation, a=None, b=None):
    node = nodes.new("ShaderNodeMath")
    node.operation = operation
    if a is not None:
        node.inputs[0].default_value = a
    if b is not None:
        node.inputs[1].default_value = b
    return node


def sprite_material(name, image, sprite):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.use_backface_culling = False
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    output = nodes.new("ShaderNodeOutputMaterial")
    uv = nodes.new("ShaderNodeTexCoord")
    separate = nodes.new("ShaderNodeSeparateXYZ")
    links.new(uv.outputs["UV"], separate.inputs[0])
    frame = nodes.new("ShaderNodeValue")
    frame.label = "Driven by sprite_frame on " + sprite.name
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
    links.new(v_scale.outputs[0], v_add.inputs[1])
    links.new(row_reverse.outputs[0], row_scale.inputs[0])
    links.new(row_scale.outputs[0], v_add.inputs[0])

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
    if hasattr(material, "surface_render_method"):
        material.surface_render_method = "DITHERED"
    return material


def sprite_plane(name, image, height, collection, root, camera, info):
    width = height  # Normalized atlas cells are square.
    mesh = bpy.data.meshes.new(name + "_Mesh")
    # Local -Y is the visible face; Z stays vertical. Origin is at the feet.
    mesh.from_pydata(
        [(-width / 2, 0, 0), (width / 2, 0, 0),
         (width / 2, 0, height), (-width / 2, 0, height)],
        [], [(0, 1, 2, 3)],
    )
    mesh.update()
    uv = mesh.uv_layers.new(name="Sprite UV")
    for loop, point in zip(mesh.polygons[0].loop_indices,
                           ((0, 0), (1, 0), (1, 1), (0, 1))):
        uv.data[loop].uv = point
    plane = bpy.data.objects.new(name, mesh)
    collection.objects.link(plane)
    plane.parent = root
    plane.location = (0, 0, 0.02)
    plane["character_name"] = name
    plane["sprite_role"] = "camera_facing_animated_atlas"
    plane["sprite_frame"] = 0
    if name == "Dage":
        plane["dage_front_neck_patch_art"] = MARK_VERSION
    plane["sprite_valid_frames"] = info["valid_frames"]
    plane["source_sheet"] = info["source"]
    plane["atlas_grid"] = "7x10, 192px cells, top-left row-major"
    plane.data.materials.append(sprite_material("MAT_MASCOT_SHORT_" + name, image, plane))
    tracking = plane.constraints.new("TRACK_TO")
    tracking.target = camera
    tracking.track_axis = "TRACK_NEGATIVE_Y"
    tracking.up_axis = "UP_Z"
    return plane


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


def animate_sprite(sprite, name, valid_frames, end_frame):
    keys = FRAME_SEQUENCE[name]
    if keys[0][0] != 1 or keys[-1][0] > end_frame:
        raise ValueError(f"Invalid frame sequence for {name}")
    for frame, index in keys:
        if not 0 <= index < valid_frames:
            raise ValueError(f"{name} sprite frame {index} exceeds {valid_frames} cells")
        sprite["sprite_frame"] = index
        sprite.keyframe_insert(data_path='["sprite_frame"]', frame=frame,
                               group="Sprite Frame")
        if name == "Dage":
            require_front_neck_patch(index)
    action = sprite.animation_data.action
    action.name = f"ACT_MASCOT_SHORT_{name}_FRAMES"
    action.use_fake_user = True
    set_constant(action)
    sprite["sprite_frame"] = keys[0][1]


def main():
    scene = bpy.context.scene
    if scene.camera is None:
        raise RuntimeError("The current scene has no active camera")
    if not bpy.data.filepath:
        raise RuntimeError("Open a .blend before running this script")
    if not MANIFEST_PATH.is_file():
        raise FileNotFoundError(f"Run prepare_episode02_sprites.py first: {MANIFEST_PATH}")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    output = argument("--output")
    if output is None:
        base, ext = os.path.splitext(bpy.data.filepath)
        output = base + "_Mascot_Sprites" + ext
    output = os.path.abspath(output)
    if os.path.exists(output) and "--overwrite" not in sys.argv:
        raise FileExistsError(f"Output already exists: {output}; pass --overwrite to replace it")

    existing = bpy.data.collections.get(COLLECTION_NAME)
    if existing:
        for obj in list(existing.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(existing)
    collection = bpy.data.collections.new(COLLECTION_NAME)
    scene.collection.children.link(collection)

    for name in ("Cila", "Dixon", "Dage"):
        root = bpy.data.objects.get(f"{name}_PROXY_ROOT")
        character_collection = bpy.data.collections.get(f"CHAR_{name}")
        if root is None or character_collection is None:
            raise RuntimeError(f"Missing {name} proxy root or character collection")
        info = manifest["characters"][name]
        if info["atlas_grid"] != {"columns": 7, "rows": 10, "cell": 192}:
            raise ValueError(f"Unexpected atlas grid for {name}")
        path = ROOT / info["atlas"]
        if not path.is_file():
            raise FileNotFoundError(path)
        image = bpy.data.images.load(str(path), check_existing=True)
        image.filepath = bpy.path.relpath(str(path))
        image.pack()
        sprite = sprite_plane(name, image, HEIGHTS[name],
                              collection, root, scene.camera, info)
        animate_sprite(sprite, name, info["valid_frames"], scene.frame_end)
        # Replace only the renderable proxy pieces. Rigs, roots, animation,
        # controls and the original files remain available for later work.
        for obj in character_collection.objects:
            if obj.type == "MESH" and obj.get("sprite_role") is None:
                obj.hide_render = True
                obj.hide_set(True)

    scene["mascot_sprite_pass"] = "Animated 7x10 atlas sprites; follow proxy root motion"
    scene["mascot_sprite_manifest"] = str(MANIFEST_PATH.relative_to(ROOT)).replace("\\", "/")
    scene["mascot_sprite_version"] = "animated_short_atlas_v1"
    scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print("MASCOT_SPRITE_SCENE_SAVED", output)


if __name__ == "__main__":
    main()
