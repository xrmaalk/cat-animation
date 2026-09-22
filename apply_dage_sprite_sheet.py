"""Pack the revised Dage atlas into an existing mascot short or Episode 02.

blender --background INPUT.blend --python apply_dage_sprite_sheet.py

The revised sheet contains Dage's natural black front-neck fur patch. This
removes the earlier procedural bowtie/chin overlay and its action keys, then
saves the file.
"""

from hashlib import sha256
import json
from pathlib import Path
import sys

import bpy


ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from dage_neck_patch import MARK_VERSION

MANIFEST = json.loads((ROOT / "references" / "mascot_sprites" /
                       "episode02_atlases" / "episode02_sprite_manifest.json")
                      .read_text(encoding="utf-8"))
ATLAS_PATH = ROOT / MANIFEST["characters"]["Dage"]["atlas"]


def remove_old_mark_nodes(material):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    texture = next(node for node in nodes if node.type == "TEX_IMAGE")
    emission = next(node for node in nodes if node.type == "EMISSION")
    overlay = nodes.get("Dage Black Chin Spot")
    if overlay:
        removable = set()

        def collect(node):
            if node in removable or node == texture or node.type == "SEPXYZ":
                return
            removable.add(node)
            for socket in node.inputs:
                for link in socket.links:
                    collect(link.from_node)

        collect(overlay)
        for node in removable:
            if node.type == "VALUE" and node.name.startswith("Dage Chin Spot"):
                node.outputs[0].driver_remove("default_value")
        for node in removable:
            nodes.remove(node)
    for link in list(emission.inputs["Color"].links):
        links.remove(link)
    links.new(texture.outputs["Color"], emission.inputs["Color"])
    if "dage_chin_mark" in material:
        del material["dage_chin_mark"]
    return texture


def remove_old_action_keys(sprite):
    if not sprite.animation_data:
        return
    for action in bpy.data.actions:
        if not (action.name.startswith("ACT_Dage_") or
                action.name == "ACT_MASCOT_SHORT_Dage_FRAMES"):
            continue
        for layer in action.layers:
            for strip in layer.strips:
                for slot in action.slots:
                    bag = strip.channelbag(slot)
                    if bag:
                        for curve in list(bag.fcurves):
                            if curve.data_path in ('["chin_spot_u"]', '["chin_spot_v"]'):
                                bag.fcurves.remove(curve)
    for prop in ("chin_spot_u", "chin_spot_v"):
        if prop in sprite:
            del sprite[prop]


def main():
    if not bpy.data.filepath:
        raise RuntimeError("Open a saved mascot short or Episode 02 .blend")
    if sha256((ROOT / MANIFEST["characters"]["Dage"]["source"]).read_bytes()).hexdigest() != \
            MANIFEST["characters"]["Dage"]["source_sha256"]:
        raise RuntimeError("Rebuild the sprite atlas manifest before upgrading")
    sprite = bpy.data.objects.get("SPRITE_Dage") or bpy.data.objects.get("Dage")
    if sprite is None or sprite.get("sprite_frame") is None:
        raise RuntimeError("Dage atlas sprite was not found")
    material = sprite.active_material
    texture = remove_old_mark_nodes(material)
    old_image = texture.image
    image = bpy.data.images.load(str(ATLAS_PATH), check_existing=False)
    texture.image = image
    if old_image and old_image.users == 0:
        bpy.data.images.remove(old_image)
    image.name = "Dage_EP02_Atlas.png"
    image.filepath = bpy.path.relpath(str(ATLAS_PATH))
    image.pack()
    remove_old_action_keys(sprite)
    if "dage_chin_art" in sprite:
        del sprite["dage_chin_art"]
    sprite["dage_front_neck_patch_art"] = MARK_VERSION
    bpy.context.scene.frame_set(bpy.context.scene.frame_current)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath)
    print("DAGE_REVISED_SHEET_PACKED", bpy.data.filepath, flush=True)


if __name__ == "__main__":
    main()
