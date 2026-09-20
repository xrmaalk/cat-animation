"""Attach the mascot cutouts to the current Blender character roots.

Example:
  blender --background Purrcilla_Dixon_Dage_Animated_Short.blend \
    --python add_mascot_sprites.py

The script saves a sibling *_Mascot_Sprites.blend. Existing files are left alone.
These are camera-facing idle cutouts for look development; full sprite
animation requires additional frames for each action and expression.
"""

import os
import sys

import bpy


ROOT = os.path.dirname(os.path.abspath(__file__))
SPRITE_DIR = os.path.join(ROOT, "references", "mascot_sprites")
COLLECTION_NAME = "SPRITES_MAALTECH_LOOKDEV"
HEIGHTS = {"Cila": 1.55, "Dixon": 1.70, "Dage": 1.70}


def argument(name, default=None):
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    return args[args.index(name) + 1] if name in args else default


def sprite_material(name, image):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.use_backface_culling = False
    nodes = material.node_tree.nodes
    nodes.clear()
    links = material.node_tree.links
    output = nodes.new("ShaderNodeOutputMaterial")
    texture = nodes.new("ShaderNodeTexImage")
    texture.image = image
    texture.interpolation = "Closest"
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


def sprite_plane(name, image, height, collection, root, camera):
    width = height * image.size[0] / image.size[1]
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
    plane["character_name"] = name.split("_")[0]
    plane["sprite_role"] = "camera_facing_idle_lookdev"
    plane.data.materials.append(sprite_material("MAT_" + name, image))
    tracking = plane.constraints.new("TRACK_TO")
    tracking.target = camera
    tracking.track_axis = "TRACK_NEGATIVE_Y"
    tracking.up_axis = "UP_Z"
    return plane


def main():
    scene = bpy.context.scene
    if scene.camera is None:
        raise RuntimeError("The current scene has no active camera")
    if not bpy.data.filepath:
        raise RuntimeError("Open a .blend before running this script")
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
        path = os.path.join(SPRITE_DIR, f"{name}_Mascot_Idle.png")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Run prepare_mascot_sprites.py first: {path}")
        image = bpy.data.images.load(path, check_existing=True)
        image.filepath = bpy.path.relpath(path)
        image.pack()
        sprite_plane(f"{name}_Mascot_Idle", image, HEIGHTS[name],
                     collection, root, scene.camera)
        # Replace only the renderable proxy pieces. Rigs, roots, animation,
        # controls and the original files remain available for later work.
        for obj in character_collection.objects:
            if obj.type == "MESH" and obj.get("sprite_role") is None:
                obj.hide_render = True
                obj.hide_set(True)

    scene["mascot_sprite_pass"] = "Static camera-facing idle cutouts; follow proxy root animation"
    scene.frame_set(scene.frame_current)
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print("MASCOT_SPRITE_SCENE_SAVED", output)


if __name__ == "__main__":
    main()
