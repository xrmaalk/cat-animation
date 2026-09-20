"""Purrcilla, Dixon & Dage: Curious Together - Blender 5.x template builder.

Run from Blender 5.x:
    blender --background --python build_template.py

The script intentionally builds a reusable production scaffold rather than a
single finished movie. It uses lightweight proxy geometry so the file opens
quickly; replace the proxy mesh inside each CHAR_* collection with a sculpted
or linked production asset later without changing the editorial structure.
"""

import bpy
import math
import os
from mathutils import Vector


FPS = 24
EPISODE_SECONDS = 17 * 60
EPISODE_FRAMES = EPISODE_SECONDS * FPS
ROOT = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(ROOT, "references")


def mat(name, color, roughness=0.55, metallic=0.0, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
        if emission:
            bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
            bsdf.inputs["Emission Strength"].default_value = 0.15
    return m


MATS = {
    "wall": mat("MAT_Wall_Beige", (0.66, 0.58, 0.46)),
    "trim": mat("MAT_Window_Trim", (0.92, 0.91, 0.86), 0.4),
    "carpet": mat("MAT_Berber_Carpet", (0.28, 0.21, 0.14)),
    "mat_black": mat("MAT_Fitness_Mat", (0.025, 0.03, 0.035), 0.8),
    "red": mat("MAT_Logo_Red", (0.55, 0.02, 0.015)),
    "wood": mat("MAT_Raw_Wood", (0.36, 0.21, 0.10)),
    "black": mat("MAT_Black_Metal", (0.012, 0.015, 0.018), 0.34, 0.35),
    "blue": mat("MAT_Bright_Blue_Bin", (0.01, 0.14, 0.85), 0.35),
    "teal": mat("MAT_Teal_Fleece", (0.02, 0.35, 0.38), 0.9),
    "white": mat("MAT_White", (0.9, 0.9, 0.86)),
    "glass": mat("MAT_Soft_Glass", (0.45, 0.72, 0.80), 0.2),
    "cila": mat("MAT_Cila_Cool_Gray_Brown_Tab", (0.25, 0.24, 0.22), 0.72),
    "cila_light": mat("MAT_Cila_Whisker_Pads", (0.55, 0.52, 0.46), 0.78),
    "dixon": mat("MAT_Dixon_Warm_Gray_Tab", (0.33, 0.31, 0.27), 0.72),
    "dixon_cream": mat("MAT_Dixon_Cream_Chest", (0.67, 0.58, 0.46), 0.75),
    "dixon_white": mat("MAT_Dixon_White_Mittens", (0.85, 0.84, 0.77), 0.72),
    "dage_black": mat("MAT_Dage_Black_Coat", (0.015, 0.017, 0.022), 0.85),
    "dage_white": mat("MAT_Dage_White_Ruff", (0.86, 0.85, 0.78), 0.9),
    "eye_cila": mat("MAT_Cila_Sage_Eyes", (0.28, 0.52, 0.34), 0.18, emission=(0.06, 0.12, 0.05)),
    "eye_dixon": mat("MAT_Dixon_Bright_Green_Eyes", (0.25, 0.75, 0.24), 0.15, emission=(0.06, 0.2, 0.04)),
    "eye_dage": mat("MAT_Dage_Light_Green_Eyes", (0.5, 0.78, 0.22), 0.15, emission=(0.08, 0.18, 0.04)),
    "nose": mat("MAT_Pink_Tan_Nose", (0.55, 0.20, 0.16), 0.45),
    "label": mat("MAT_Label_Warm", (0.94, 0.68, 0.22), 0.48, emission=(0.35, 0.18, 0.02)),
}


def rebuild_materials_after_factory_reset():
    """Recreate materials after read_factory_settings clears datablocks."""
    return {
        "wall": mat("MAT_Wall_Beige", (0.66, 0.58, 0.46)),
        "trim": mat("MAT_Window_Trim", (0.92, 0.91, 0.86), 0.4),
        "carpet": mat("MAT_Berber_Carpet", (0.28, 0.21, 0.14)),
        "mat_black": mat("MAT_Fitness_Mat", (0.025, 0.03, 0.035), 0.8),
        "red": mat("MAT_Logo_Red", (0.55, 0.02, 0.015)),
        "wood": mat("MAT_Raw_Wood", (0.36, 0.21, 0.10)),
        "black": mat("MAT_Black_Metal", (0.012, 0.015, 0.018), 0.34, 0.35),
        "blue": mat("MAT_Bright_Blue_Bin", (0.01, 0.14, 0.85), 0.35),
        "teal": mat("MAT_Teal_Fleece", (0.02, 0.35, 0.38), 0.9),
        "white": mat("MAT_White", (0.9, 0.9, 0.86)),
        "glass": mat("MAT_Soft_Glass", (0.45, 0.72, 0.80), 0.2),
        "cila": mat("MAT_Cila_Cool_Gray_Brown_Tab", (0.25, 0.24, 0.22), 0.72),
        "cila_light": mat("MAT_Cila_Whisker_Pads", (0.55, 0.52, 0.46), 0.78),
        "dixon": mat("MAT_Dixon_Warm_Gray_Tab", (0.33, 0.31, 0.27), 0.72),
        "dixon_cream": mat("MAT_Dixon_Cream_Chest", (0.67, 0.58, 0.46), 0.75),
        "dixon_white": mat("MAT_Dixon_White_Mittens", (0.85, 0.84, 0.77), 0.72),
        "dage_black": mat("MAT_Dage_Black_Coat", (0.015, 0.017, 0.022), 0.85),
        "dage_white": mat("MAT_Dage_White_Ruff", (0.86, 0.85, 0.78), 0.9),
        "eye_cila": mat("MAT_Cila_Sage_Eyes", (0.28, 0.52, 0.34), 0.18, emission=(0.06, 0.12, 0.05)),
        "eye_dixon": mat("MAT_Dixon_Bright_Green_Eyes", (0.25, 0.75, 0.24), 0.15, emission=(0.06, 0.2, 0.04)),
        "eye_dage": mat("MAT_Dage_Light_Green_Eyes", (0.5, 0.78, 0.22), 0.15, emission=(0.08, 0.18, 0.04)),
        "nose": mat("MAT_Pink_Tan_Nose", (0.55, 0.20, 0.16), 0.45),
        "label": mat("MAT_Label_Warm", (0.94, 0.68, 0.22), 0.48, emission=(0.35, 0.18, 0.02)),
    }


def collection(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if c.name not in {x.name for x in (parent.children if parent else bpy.context.scene.collection.children)}:
        (parent.children if parent else bpy.context.scene.collection.children).link(c)
    return c


def move_to(obj, c):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    c.objects.link(obj)
    return obj


def cube(name, loc, scale, material, c, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Soft_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
    o.data.materials.append(material)
    return move_to(o, c)


def sphere(name, loc, scale, material, c, segments=24):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments, ring_count=12, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return move_to(o, c)


def cyl(name, loc, radius, depth, material, c, rotation=None):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=24, radius=radius, depth=depth, location=loc, rotation=rotation or (0, 0, 0))
    o = bpy.context.object
    o.name = name
    o.data.materials.append(material)
    return move_to(o, c)


def text_obj(name, body, loc, size, c, material=None, align="CENTER"):
    cu = bpy.data.curves.new(name + "_Curve", "FONT")
    cu.body = body
    cu.align_x = align
    cu.size = size
    cu.extrude = 0.005
    ob = bpy.data.objects.new(name, cu)
    c.objects.link(ob)
    ob.location = loc
    if material:
        cu.materials.append(material)
    return ob


def add_asset(obj, description="Reusable Curious Together asset"):
    obj["asset_description"] = description
    try:
        obj.asset_mark()
    except Exception:
        pass
    return obj


def make_cat(name, spec, c):
    """Make readable proxy geometry plus a named control armature."""
    body_mat = spec["body"]
    # Root and torso: separate pieces keep the proxy easy to replace.
    root = bpy.data.objects.new(name + "_PROXY_ROOT", None)
    c.objects.link(root)
    root.empty_display_type = "PLAIN_AXES"
    root["character_role"] = "replaceable_proxy_root"
    torso = sphere(name + "_Body_PROD_PROXY", (0, 0, 0.62),
                   spec["body_scale"], body_mat, c)
    torso.parent = root
    torso["production_placeholder"] = True
    head = sphere(name + "_Head_PROD_PROXY", (0.0, -0.02, 1.18),
                  spec["head_scale"], body_mat, c)
    head.parent = root
    # Muzzle, chest and ears.
    muzzle = sphere(name + "_Whisker_Pads", (0.0, -0.25, 1.08),
                    (0.28, 0.16, 0.18), spec["light"], c)
    muzzle.parent = root
    if spec.get("chest"):
        chest = sphere(name + "_Chest_Patch", (0.0, -0.08, 0.64),
                       (0.33, 0.18, 0.42), spec["chest"], c)
        chest.parent = root
    for sx in (-1, 1):
        ear = bpy.data.objects.new(
            f"{name}_Ear_{'L' if sx < 0 else 'R'}", None)
        c.objects.link(ear)
        ear.empty_display_type = "CONE"
        ear.empty_display_size = 0.18
        ear.location = (0.18 * sx, -0.01, 1.46)
        ear.rotation_euler[1] = -0.2 * sx
        ear.parent = root
        for eye_mat in (spec["eye"],):
            eye = sphere(f"{name}_Eye_{'L' if sx < 0 else 'R'}", (0.11 *
                         sx, -0.22, 1.21), (0.055, 0.032, 0.07), eye_mat, c, segments=16)
            eye.parent = root
    nose = sphere(name + "_Nose", (0, -0.36, 1.08),
                  (0.06, 0.04, 0.045), MATS["nose"], c, segments=16)
    nose.parent = root
    # Legs and paws.
    for sx in (-1, 1):
        for sy, label in ((-0.16, "Front"), (0.18, "Rear")):
            leg = cyl(f"{name}_{label}_Leg_{'L' if sx < 0 else 'R'}",
                      (0.17 * sx, sy, 0.34), 0.075, 0.42, body_mat, c)
            leg.parent = root
            paw_mat = spec.get(
                "paw", body_mat) if label == "Front" else body_mat
            paw = sphere(f"{name}_{label}_Paw_{'L' if sx < 0 else 'R'}",
                         (0.17 * sx, sy - 0.03, 0.11), (0.11, 0.16, 0.07), paw_mat, c)
            paw.parent = root
    tail = cyl(name + "_Tail_FK_PROXY", (0.40, 0.18, 0.65), 0.075 if not spec.get("longhair")
               else 0.13, 0.90, body_mat, c, rotation=(0, math.radians(65), math.radians(-20)))
    tail.parent = root

    arm = bpy.data.armatures.new(name + "_CTRL_RIG")
    rig = bpy.data.objects.new(name + "_CTRL_RIG", arm)
    c.objects.link(rig)
    rig.show_in_front = True
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bones = {}

    def bone(label, head, tail, parent=None):
        b = arm.edit_bones.new(label)
        b.head, b.tail = head, tail
        b.length = max(b.length, 0.08)
        if parent:
            b.parent = bones[parent]
        bones[label] = b
        return b
    bone("root", (0, 0, 0.1), (0, 0, 0.35))
    bone("spine", (0, 0, 0.35), (0, 0, 0.95), "root")
    bone("neck", (0, 0, 0.95), (0, 0, 1.20), "spine")
    bone("head", (0, 0, 1.20), (0, 0, 1.45), "neck")
    for sx, side in ((-1, "L"), (1, "R")):
        bone(f"front_upper_{side}", (0.14 * sx, -0.15,
             0.68), (0.17 * sx, -0.15, 0.35), "spine")
        bone(f"front_paw_{side}", (0.17 * sx, -0.15, 0.35),
             (0.17 * sx, -0.15, 0.10), f"front_upper_{side}")
        bone(f"rear_upper_{side}", (0.16 * sx, 0.18, 0.65),
             (0.17 * sx, 0.18, 0.35), "spine")
        bone(f"rear_paw_{side}", (0.17 * sx, 0.18, 0.35),
             (0.17 * sx, 0.18, 0.10), f"rear_upper_{side}")
        bone(f"ear_{side}", (0.16 * sx, 0, 1.38), (0.18 * sx, 0, 1.58), "head")
    for i in range(5):
        bone(f"tail_{i:02d}", (0.35 + i * 0.12, 0.15, 0.65 - i * 0.03), (0.47 +
             i * 0.12, 0.15, 0.65 - i * 0.03), "root" if i == 0 else f"tail_{i-1:02d}")
    bpy.ops.object.mode_set(mode="POSE")
    rig.pose.bones["head"].custom_shape_scale_xyz = (0.8, 0.8, 0.8)
    bpy.ops.object.mode_set(mode="OBJECT")
    rig["character_name"] = name
    rig["rig_version"] = "CT_Rig_v1.0_Blender5x"
    rig["controls"] = "look_at_target, tail_curl, loaf_morph, hind_stand, fluff_volume"
    rig["look_at_target"] = "CTRL_LOOK_AT"
    rig["tail_curl"] = 0.0
    rig["loaf_morph"] = 0.0
    rig["hind_stand"] = 0.0
    rig["fluff_volume"] = 1.0 if spec.get("longhair") else 0.0
    # Empty control handles are intentionally named and easy to replace with custom shapes.
    for ctl, loc in (("CTRL_LOOK_AT", (0, -1.0, 1.3)), ("CTRL_TAIL_CURL", (0.7, 0.2, 0.7)), ("CTRL_LOAF_MORPH", (-0.8, 0, 0.6))):
        e = bpy.data.objects.new(name + "_" + ctl, None)
        c.objects.link(e)
        e.empty_display_type = "CIRCLE"
        e.empty_display_size = 0.18
        e.location = loc
        e.parent = rig
        e["controller_for"] = ctl
    add_pose_assets(name, c, spec)
    return rig


def add_pose_assets(name, c, spec):
    poses = [
        ("REST", "Neutral production rest pose"),
        ("UPRIGHT_LOOK", "Upright sit looking upward"),
        ("LOAF", "Quiet loaf / long still hold"),
        ("SNIFF", "Slow sniff before decisive paw"),
        ("SLOW_BLINK", "Hold eyes soft; do not narrate over this"),
        ("GROOM_LOOP", "Gentle grooming loop"),
        ("STRETCH", "Downward-dog stretch"),
        ("JUMP_UP", "Measured jump onto a stable surface"),
        ("JUMP_DOWN", "Measured jump down"),
    ]
    if name == "Dixon":
        poses += [("HIND_STAND_HERO", "Dixon window correspondent hero"),
                  ("PEEK_THROUGH_SLATS", "Dixon peeking through blinds")]
    if name == "Dage":
        poses += [("CURL_IN_CUBBY_HERO", "Dage curled in the condo cubby"),
                  ("CHIN_ON_LIP", "Dage watches from the cubby lip")]
    if name == "Cila":
        poses += [("LAP_LOAF_HERO", "Cila loaf beside a human lap"),
                  ("HEAD_TILT", "Cila scout head tilt")]
    for pose, desc in poses:
        e = bpy.data.objects.new(f"POSE_{name}_{pose}", None)
        c.objects.link(e)
        e.empty_display_type = "ARROWS"
        e.empty_display_size = 0.22
        e["pose_name"] = pose
        e["pose_description"] = desc
        add_asset(e, desc)


def build_sets(cols):
    porch, living, window, nook, condo, props = [cols[x] for x in (
        "SET_Porch", "SET_Living", "SET_Window", "SET_WorkNook", "SET_Condo", "PROPS")]
    # Living room / workout corner.
    cube("Living_Carpet", (0, 0, -0.06),
         (4.6, 3.6, 0.06), MATS["carpet"], living, 0.04)
    cube("Fitness_Mat", (1.5, -0.5, 0.01),
         (1.5, 0.85, 0.02), MATS["mat_black"], living, 0.04)
    cube("Fitness_Mat_Red_Logo", (1.5, 0.1, 0.035),
         (0.55, 0.025, 0.005), MATS["red"], living)
    # Window station.
    cube("Window_Wall", (0, 3.4, 1.8), (4.6, 0.10, 1.9), MATS["wall"], window)
    cube("Window_Sill", (0, 3.12, 1.55),
         (2.4, 0.38, 0.12), MATS["trim"], window, 0.06)
    cube("Window_Trim_Top", (0, 3.03, 3.25),
         (2.7, 0.12, 0.10), MATS["trim"], window)
    cube("Window_Trim_Left", (-2.55, 3.03, 2.3),
         (0.10, 0.12, 0.95), MATS["trim"], window)
    cube("Window_Trim_Right", (2.55, 3.03, 2.3),
         (0.10, 0.12, 0.95), MATS["trim"], window)
    cube("Window_Glass", (0, 3.18, 2.35),
         (2.4, 0.02, 0.82), MATS["glass"], window)
    for i in range(16):
        slat = cube(f"Blind_Slat_{i:02d}", (-2.25 + i * 0.30, 2.99,
                    2.35), (0.11, 0.03, 0.72), MATS["white"], window, 0.025)
        slat.rotation_euler[0] = math.radians(-7)
        slat["discovery_prop"] = "blinds"
    cyl("Blind_Cord_Left", (-2.30, 2.94, 1.50),
        0.018, 1.6, MATS["white"], window)
    # Porch.
    cube("Porch_Floor", (0, -5.1, -0.08),
         (4.4, 2.4, 0.08), MATS["trim"], porch)
    cube("Porch_Back_Screen", (0, -7.45, 1.8),
         (4.4, 0.04, 1.8), MATS["glass"], porch)
    cube("Porch_Railing", (0, -5.0, 1.35),
         (4.4, 0.06, 0.08), MATS["black"], porch)
    cube("Blue_Wheeled_Bin", (2.45, -6.0, 0.62),
         (0.7, 0.62, 0.62), MATS["blue"], porch, 0.10)
    for x in (-1.9, 0.0):
        cube("Folding_Table_Top", (x, -5.8, 1.4),
             (0.9, 0.55, 0.05), MATS["wood"], porch)
        for sx in (-1, 1):
            leg = cube("Folding_Table_Black_XLeg", (x + 0.55 * sx, -
                       5.8, 0.70), (0.04, 0.55, 0.75), MATS["black"], porch)
            leg.rotation_euler[1] = math.radians(-22 * sx)
    # Work / bedroom nook.
    cube("Nook_Wall", (-5.0, 0.0, 1.8), (0.10, 3.0, 1.8), MATS["wall"], nook)
    cube("Nook_Desk", (-4.0, 0.6, 1.0),
         (1.15, 0.55, 0.06), MATS["wood"], nook, 0.04)
    cube("Printer_Enclosure", (-4.0, 0.6, 1.75),
         (0.85, 0.45, 0.75), MATS["black"], nook, 0.05)
    for z, color in ((2.55, MATS["white"]), (2.50, MATS["blue"])):
        cyl("Filament_Spool", (-4.0, 0.12, z), 0.30, 0.12,
            color, nook, rotation=(math.radians(90), 0, 0))
    # Condo.
    cube("Condo_Wood_Cubby", (4.1, 1.6, 1.0),
         (1.25, 1.15, 1.0), MATS["wood"], condo, 0.05)
    cube("Condo_Opening", (4.1, 0.35, 1.0),
         (0.83, 0.04, 0.72), MATS["black"], condo, 0.04)
    cube("Condo_Teal_Pad", (4.1, 0.36, 0.34),
         (0.9, 0.8, 0.10), MATS["teal"], condo, 0.08)
    # Reusable discovery props.
    cube("PROP_Cardboard_Box", (-1.8, 0.0, 0.38),
         (0.75, 0.60, 0.38), MATS["wood"], props, 0.04)
    cube("PROP_Paper_Bag", (0.7, 1.6, 0.55),
         (0.42, 0.30, 0.55), MATS["dixon_cream"], props, 0.06)
    cube("PROP_Empty_Mug", (2.5, -1.4, 0.25),
         (0.22, 0.22, 0.28), MATS["white"], props, 0.08)
    cube("PROP_Feather_Toy", (-2.5, -1.2, 0.06),
         (0.55, 0.05, 0.02), MATS["label"], props)
    cyl("PROP_Heating_Vent", (-0.8, 2.4, 0.04),
        0.35, 0.03, MATS["black"], props)
    cube("PROP_Blue_Storage_Bin", (2.6, 2.0, 0.55),
         (0.65, 0.55, 0.55), MATS["blue"], props, 0.08)
    # Reusable sunbeam plane; animated light stripes are represented by slat geometry.
    beam = cube("FX_Sunbeam_Gobo", (-0.3, 0.6, 1.8),
                (2.0, 0.03, 0.03), MATS["label"], props)
    beam["fx_note"] = "Replace with volume cone or compositor gobo for hero shots"
    add_asset(beam, "Sunbeam gobo placeholder")


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def camera(name, loc, target, lens, c):
    data = bpy.data.cameras.new(name + "_DATA")
    data.lens = lens
    data.sensor_width = 36
    ob = bpy.data.objects.new(name, data)
    c.objects.link(ob)
    ob.location = loc
    look_at(ob, target)
    add_asset(ob, "Reusable camera composition")
    return ob


def build_cameras(c):
    cams = {}
    cams["CAM_CatEye_A"] = camera(
        "CAM_CatEye_A", (0, -2.2, 0.65), (0, 1.3, 0.80), 38, c)
    cams["CAM_HeroPortrait_Cila"] = camera(
        "CAM_HeroPortrait_Cila", (-1.6, -2.6, 1.3), (0, 0, 0.9), 65, c)
    cams["CAM_HeroPortrait_Dage"] = camera(
        "CAM_HeroPortrait_Dage", (3.1, -0.8, 1.4), (4.1, 0.7, 1.1), 65, c)
    cams["CAM_HeroPortrait_Dixon"] = camera(
        "CAM_HeroPortrait_Dixon", (0, 2.0, 1.0), (0, 3.0, 1.8), 58, c)
    cams["CAM_WindowReport"] = camera(
        "CAM_WindowReport", (0.8, 1.2, 0.85), (0.3, 3.0, 1.8), 45, c)
    cams["CAM_CondoPeek"] = camera(
        "CAM_CondoPeek", (5.7, -0.3, 0.9), (4.1, 0.4, 1.0), 52, c)
    cams["CAM_PorchWide"] = camera(
        "CAM_PorchWide", (0, -2.0, 2.6), (0, -5.4, 0.8), 28, c)
    cams["CAM_Insert_Paws"] = camera(
        "CAM_Insert_Paws", (-0.7, 1.1, 0.35), (-0.2, 2.9, 0.9), 70, c)
    cams["CAM_Insert_Eyes"] = camera(
        "CAM_Insert_Eyes", (0.8, 2.0, 1.45), (0, 2.9, 1.65), 85, c)
    return cams


def build_lights(c):
    def area(name, loc, energy, size, color, target):
        data = bpy.data.lights.new(name + "_DATA", "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        data.color = color
        ob = bpy.data.objects.new(name, data)
        c.objects.link(ob)
        ob.location = loc
        look_at(ob, target)
        return ob
    area("KEY_Window_Soft", (-1.5, 2.0, 4.5),
         700, 4.0, (1.0, 0.91, 0.74), (0, 0, 0))
    area("FILL_Overcast_Porch", (0, -6.5, 3.5), 450,
         5.0, (0.70, 0.82, 1.0), (0, -5.5, 0.4))
    area("RIM_Warm_Lamp", (4.0, -1.0, 2.8), 300,
         2.0, (1.0, 0.55, 0.25), (3.5, 0.5, 0.8))


def build_narration(c):
    c.hide_render = True
    c.hide_viewport = True
    c["toggle"] = "Enable this collection when narrator/text pass is approved"
    for label, loc in (("blinds", (-1.0, 2.70, 2.3)), ("sunbeam", (0, 0.4, 1.5)), ("window", (0, 2.7, 3.2)), ("cat window", (0, 2.7, 0.9))):
        t = text_obj("LOWER_THIRD_" + label.replace(" ", "_"),
                     label, loc, 0.18, c, MATS["label"])
        t.rotation_euler = (math.radians(90), 0, 0)


SHOT_LIST = [
    ("S01", "COLD_OPEN", 0, 45, "CAM_WindowReport",
     "Dixon already mid-curiosity at blinds; paw enters frame."),
    ("S02", "TITLE", 45, 15, "CAM_CatEye_A",
     "Title card over quiet window light."),
    ("S03", "NAMES_CILA", 60, 4, "CAM_HeroPortrait_Cila",
     "Cila portrait: upright, looking up and left."),
    ("S04", "NAMES_DAGE", 64, 4, "CAM_HeroPortrait_Dage",
     "Dage portrait: curled in cubby, slow blink."),
    ("S05", "NAMES_DIXON", 68, 4, "CAM_HeroPortrait_Dixon",
     "Dixon portrait: window correspondent pose."),
    ("S06", "MORNING_GEOGRAPHY", 72, 36, "CAM_CatEye_A",
     "Cat-height home geography, gentle pan."),
    ("S07", "HOMEBASE_CILA", 108, 24, "CAM_PorchWide",
     "Cila at porch threshold, checks corners."),
    ("S08", "HOMEBASE_DAGE", 132, 24, "CAM_CondoPeek",
     "Dage in cubby, tail fills foreground."),
    ("S09", "HOMEBASE_DIXON", 156, 24, "CAM_WindowReport",
     "Dixon at sill; outside world beyond slats."),
    ("S10", "THE_NOTICE", 180, 36, "CAM_WindowReport",
     "Dixon bats blind; slats tilt and stripe moves."),
    ("S11", "OTHERS_ARRIVE", 216, 36, "CAM_CatEye_A",
     "Cila slow approach; Dage observes above."),
    ("S12", "FIRST_LOOK", 252, 42, "CAM_Insert_Paws",
     "Paws, cord, slat edge; no rush."),
    ("S13", "FIRST_SNIFF", 294, 42, "CAM_Insert_Eyes",
     "Three reactions: look, sniff, slow blink."),
    ("S14", "EXPLODED_SIMPLE", 336, 54, "CAM_WindowReport",
     "Simple labels: blinds, slats, window, daylight."),
    ("S15", "PAW_EXPERIMENT", 390, 48, "CAM_Insert_Paws",
     "Paw bats slat; stripe travels across carpet."),
    ("S16", "TRUE_FACT", 438, 42, "CAM_WindowReport",
     "Visual fact: slats are many small doors for light."),
    ("S17", "CILA_TRACES", 480, 48, "CAM_CatEye_A",
     "Cila traces the moving light stripe."),
    ("S18", "DAGE_STRIPE", 528, 48, "CAM_CondoPeek",
     "Stripe reaches teal blanket; Dage steps down."),
    ("S19", "SHARED_TEST", 576, 60, "CAM_PorchWide",
     "They take turns leaving one slat open."),
    ("S20", "CAT_WINDOW", 636, 54, "CAM_WindowReport",
     "The trio settle at the small view."),
    ("S21", "QUIET_PLAY", 690, 48, "CAM_CatEye_A",
     "Grooming, tail talk, shared stare."),
    ("S22", "CALLBACK", 738, 48, "CAM_Insert_Paws",
     "Dixon checks the slat once more."),
    ("S23", "RECAP_1", 786, 36, "CAM_WindowReport",
     "Still frame: blinds control light."),
    ("S24", "RECAP_2", 822, 36, "CAM_Insert_Paws",
     "Still frame: light stripes move."),
    ("S25", "RECAP_3", 858, 36, "CAM_CondoPeek",
     "Still frame: one slat can make a cat window."),
    ("S26", "BUTTON_ENDCARD", 894, 126, "CAM_CatEye_A",
     "All three in frame; lights lower; slow blinks."),
]


def add_action_timing(action, owner, duration_frames):
    """Add a minimal timing curve using legacy or layered Action APIs."""
    end_frame = max(1, duration_frames - 1)
    if hasattr(action, "fcurves"):
        # Blender 4.3 and earlier.
        fc = action.fcurves.new(data_path="scale", index=0)
    else:
        # Blender 4.4+ / 5.x layered Actions.
        from bpy_extras import anim_utils
        slot = action.slots.new(id_type="OBJECT", name=owner.name)
        layer = action.layers.new("EP01_TIMING")
        key_strip = layer.strips.new(type="KEYFRAME")
        # channelbag(slot) only looks up an existing bag and may return None.
        # Blender's utility creates the required bag safely.
        channelbag = anim_utils.action_ensure_channelbag_for_slot(action, slot)
        fc = channelbag.fcurves.new(data_path="scale", index=0)
    fc.keyframe_points.insert(0, 1.0)
    fc.keyframe_points.insert(end_frame, 1.0)
    fc.update()
    return action


def build_editorial(c, scene):
    edit = scene.collection.children.get("EDIT_NLA") or c
    # Timeline markers and per-shot metadata.
    for shot, beat, start_s, dur_s, cam, note in SHOT_LIST:
        frame = start_s * FPS
        scene.timeline_markers.new(f"{shot}_{beat}", frame=frame)
        card = text_obj(
            f"CARD_{shot}", f"{shot}  |  {beat}  |  {dur_s}s", (0, 0, 0), 0.1, edit, MATS["label"])
        card.hide_render = True
        card.hide_viewport = True
        card["camera"] = cam
        card["note"] = note
    # NLA beat track: each strip is a reusable editorial block with exact duration.
    holder = bpy.data.objects.new("EDITORIAL_MASTER_NLA", None)
    edit.objects.link(holder)
    holder["template"] = "Beat sheet for Episode 01 - 17:00 total"
    holder.animation_data_create()
    track = holder.animation_data.nla_tracks.new()
    track.name = "EP01_BEATS"
    for shot, beat, start_s, dur_s, cam, note in SHOT_LIST:
        action = bpy.data.actions.new(f"ACT_{shot}_{beat}")
        action["beat"] = beat
        action["duration_seconds"] = dur_s
        action["camera"] = cam
        action["note"] = note
        add_action_timing(action, holder, dur_s * FPS)
        strip = track.strips.new(f"NLA_{shot}_{beat}", start_s * FPS, action)
        if hasattr(strip, "action_slot") and hasattr(action, "slots") and action.slots:
            strip.action_slot = action.slots[0]
        strip.action_frame_start = 0
        strip.action_frame_end = max(1, dur_s * FPS - 1)
        strip.blend_type = "REPLACE"
    # Text data is useful inside Blender's Text Editor for editorial review.
    text = bpy.data.texts.new("EP01_BEAT_SHEET_README")
    text.write("Episode 01 — The Slats That Make Daylight\n\n")
    for row in SHOT_LIST:
        text.write(
            f"{row[0]} | {row[1]} | {row[2]:05d}s | {row[3]:03d}s | {row[4]} | {row[5]}\n")
    text.write(
        "\nNarration is OFF by default. Keep holds quiet around SLOW_BLINK poses.\n")


def import_references(c):
    for fn in ("Dixon-Venting(1).jpg", "Cila-LAP.jpg", "Cila-Curious(1).jpg", "Dixon-Curious.jpg", "Dage-Condo.jpg"):
        path = os.path.join(REF_DIR, fn)
        if not os.path.exists(path):
            continue
        try:
            img = bpy.data.images.load(path, check_existing=True)
            empty = bpy.data.objects.new(
                "REF_" + os.path.splitext(fn)[0], None)
            c.objects.link(empty)
            empty.empty_display_type = "IMAGE"
            empty.data = img
            empty.empty_display_size = 2.0
            empty.hide_render = True
            empty["source_reference"] = fn
        except Exception as exc:
            print("Reference import skipped:", fn, exc)


def key_transform(obj, frame, location=None, rotation=None, scale=None):
    """Insert a Blender-version-stable transform key for animatic playback."""
    if location is not None:
        obj.location = location
        obj.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        obj.rotation_euler = rotation
        obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        obj.scale = scale
        obj.keyframe_insert(data_path="scale", frame=frame)


def build_playback_animation(cols, scene):
    """Add a visible, lightweight placeholder pass for pressing Play.

    This is deliberately not final acting. It proves the timeline, camera
    language, and cause/effect of Episode 01 while leaving hero animation
    replaceable through the character/shot libraries.
    """
    fps = FPS
    cila_root = bpy.data.objects.get("Cila_PROXY_ROOT")
    dage_root = bpy.data.objects.get("Dage_PROXY_ROOT")
    dixon_root = bpy.data.objects.get("Dixon_PROXY_ROOT")

    # Establish the three home bases.
    if cila_root:
        key_transform(cila_root, 0, location=(0.0, -4.0, 0.0))
        key_transform(cila_root, 90 * fps, location=(0.0, -4.0, 0.0))
        key_transform(cila_root, 180 * fps, location=(-1.0, 0.5, 0.0))
        key_transform(cila_root, 360 * fps, location=(0.0, 1.4, 0.0))
        key_transform(cila_root, 780 * fps, location=(-0.8, 1.0, 0.0))
    if dage_root:
        key_transform(dage_root, 0, location=(4.1, 1.0, 0.0))
        key_transform(dage_root, 528 * fps, location=(4.1, 1.0, 0.0))
        key_transform(dage_root, 600 * fps, location=(2.0, 1.0, 0.0))
        key_transform(dage_root, 780 * fps, location=(0.8, 1.0, 0.0))
    if dixon_root:
        key_transform(dixon_root, 0, location=(0.0, 2.2, 0.40))
        key_transform(dixon_root, 180 * fps, location=(0.0, 2.2, 0.40))
        key_transform(dixon_root, 390 * fps, location=(0.0, 2.0, 0.40))
        key_transform(dixon_root, 780 * fps, location=(0.5, 1.0, 0.0))

    # Short readable attention beats during the first minute.
    for name, angles in (
        ("Cila_Head_PROD_PROXY", ((0, 0.0),
         (18 * fps, math.radians(-10)), (30 * fps, 0.0))),
        ("Dixon_Head_PROD_PROXY", ((0, 0.0), (8 * fps, math.radians(8)),
         (16 * fps, 0.0), (32 * fps, math.radians(-6)), (45 * fps, 0.0))),
        ("Dage_Tail_FK_PROXY", ((0, math.radians(-18)), (22 * fps, math.radians(18)),
         (40 * fps, math.radians(-8)), (55 * fps, math.radians(8)))),
    ):
        obj = bpy.data.objects.get(name)
        if obj:
            for frame, angle in angles:
                key_transform(obj, frame, rotation=(0.0, angle, 0.0))

    # Dixon's hero window action: a small paw/attention proxy motion.
    dixon_paw = bpy.data.objects.get("Dixon_Front_Paw_R")
    if dixon_paw:
        for sec, z in ((0, 0.0), (4, 0.10), (6, 0.0), (12, 0.08), (15, 0.0), (28, 0.10), (32, 0.0)):
            key_transform(
                dixon_paw, sec * fps, location=(dixon_paw.location.x, dixon_paw.location.y, z))

    # Blinds visibly tilt, then settle into the one-slat cat window.
    slats = [bpy.data.objects.get(f"Blind_Slat_{i:02d}") for i in range(16)]
    slats = [obj for obj in slats if obj]
    for obj in slats:
        base = obj.rotation_euler.copy()
        key_transform(obj, 0, rotation=base)
        key_transform(obj, 4 * fps, rotation=(base.x +
                      math.radians(18), base.y, base.z))
        key_transform(obj, 8 * fps, rotation=(base.x -
                      math.radians(8), base.y, base.z))
        key_transform(obj, 16 * fps, rotation=(base.x +
                      math.radians(5), base.y, base.z))
        key_transform(obj, 32 * fps, rotation=(base.x, base.y, base.z))
    if slats:
        # Leave one visible slat slightly open as the Episode 01 button.
        obj = slats[len(slats) // 2]
        base = obj.rotation_euler.copy()
        key_transform(obj, 780 * fps, rotation=(base.x +
                      math.radians(12), base.y, base.z))
        key_transform(obj, 1020 * fps, rotation=(base.x +
                      math.radians(12), base.y, base.z))

    # Gentle camera movement makes the play button meaningful in camera view.
    cam = bpy.data.objects.get("CAM_WindowReport")
    if cam:
        camera_keys = (
            (0, (0.8, 1.2, 0.85), (0.3, 3.0, 1.8)),
            (12 * fps, (0.45, 1.7, 0.92), (0.2, 3.0, 1.70)),
            (32 * fps, (0.15, 2.0, 0.80), (0.0, 3.0, 1.65)),
            (90 * fps, (0.8, 1.2, 0.85), (0.3, 3.0, 1.8)),
            (780 * fps, (1.4, -0.4, 1.05), (0.4, 1.0, 0.9)),
            (1020 * fps, (1.4, -0.4, 1.05), (0.4, 1.0, 0.9)),
        )
        for frame, loc, target in camera_keys:
            cam.location = loc
            look_at(cam, target)
            cam.keyframe_insert(data_path="location", frame=frame)
            cam.keyframe_insert(data_path="rotation_euler", frame=frame)
        scene.camera = cam

    scene["playback_pass"] = "Visible placeholder animation: camera, blinds, Dixon paw, head/tail attention, home-base moves"
    scene["playback_instruction"] = "Use Numpad 0 for camera view, press Shift+Left to return to frame 0, then Play"


def setup_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    global MATS
    MATS = rebuild_materials_after_factory_reset()
    scene = bpy.context.scene
    scene.name = "CT_MASTER_EP01_TEMPLATE"
    # Blender 4.x exposed Eevee as BLENDER_EEVEE_NEXT; Blender 5.x exposes
    # the same realtime engine as BLENDER_EEVEE. Use whichever enum exists.
    for engine_name in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scene.render.engine = engine_name
            break
        except TypeError:
            continue
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 50
    scene.render.fps = FPS
    scene.frame_start = 0
    scene.frame_end = EPISODE_FRAMES
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    # Factory settings may leave the scene without a World datablock.
    # Create one explicitly before assigning the viewport background color.
    if scene.world is None:
        scene.world = bpy.data.worlds.new("CT_MASTER_WORLD")
    scene.world.color = (0.055, 0.045, 0.035)
    scene["series_title"] = "Purrcilla, Dixon & Dage: Curious Together"
    scene["template_version"] = "1.0"
    scene["episode_seed"] = "The Slats That Make Daylight"
    scene["episode_runtime_seconds"] = 1020
    scene["visual_style"] = "Stylized realism / illustrated documentary of real cats"
    scene["production_note"] = "Use proxy geometry for animatic; link hero character collections for final shots."
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        pass

    names = ["CHAR_Cila", "CHAR_Dage", "CHAR_Dixon", "SET_Porch", "SET_Living", "SET_Window", "SET_WorkNook",
             "SET_Condo", "PROPS", "CAMERAS", "LIGHTS", "FX_Particles", "EDIT_NLA", "NARRATION_TEXT_OFF", "REFERENCES"]
    cols = {n: collection(n) for n in names}
    # Proxy cats are placed close enough to the modular set for quick preview.
    make_cat("Cila", {"body": MATS["cila"], "light": MATS["cila_light"], "eye": MATS["eye_cila"], "body_scale": (
        0.48, 0.72, 0.46), "head_scale": (0.36, 0.36, 0.36)}, cols["CHAR_Cila"])
    make_cat("Dage", {"body": MATS["dage_black"], "light": MATS["dage_white"], "chest": MATS["dage_white"], "eye": MATS["eye_dage"], "body_scale": (
        0.62, 0.82, 0.55), "head_scale": (0.42, 0.40, 0.42), "longhair": True}, cols["CHAR_Dage"])
    make_cat("Dixon", {"body": MATS["dixon"], "light": MATS["dixon_cream"], "chest": MATS["dixon_cream"], "paw": MATS["dixon_white"],
             "eye": MATS["eye_dixon"], "body_scale": (0.52, 0.82, 0.48), "head_scale": (0.40, 0.40, 0.42)}, cols["CHAR_Dixon"])
    build_sets(cols)
    build_cameras(cols["CAMERAS"])
    build_lights(cols["LIGHTS"])
    build_narration(cols["NARRATION_TEXT_OFF"])
    import_references(cols["REFERENCES"])
    build_editorial(cols["EDIT_NLA"], scene)
    build_playback_animation(cols, scene)

    # Basic render preview camera.
    scene.camera = bpy.data.objects.get("CAM_CatEye_A")
    # Add a small set of custom properties documenting the panel contract.
    scene["rig_ui_contract"] = "N-panel expected controls: look at target | tail curl | loaf morph | hind-stand | fluff volume"
    scene["asset_browser_contract"] = "Pose empties and cameras are asset-marked; replace proxy geometry with linked production collections."
    # Save next to the script.
    out = os.path.join(
        ROOT, "Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out)
    print("Saved:", out)
    return out


if __name__ == "__main__":
    setup_scene()
