"""Make a 12-second animated proof of concept from the episode template.

Run with Blender 5.x:
    blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python animate_short.py

The original template remains untouched.  The result is an editable .blend with
24 fps keyframes on the proxy cats, blinds, sun stripes, and camera.
"""

import math
import os

import bpy
from mathutils import Vector


ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(ROOT, "Purrcilla_Dixon_Dage_Animated_Short.blend")
FPS = 24
END = 12 * FPS


def obj(name):
    found = bpy.data.objects.get(name)
    if found is None:
        raise RuntimeError(f"Template object missing: {name}")
    return found


def clear_keys(target):
    if target.animation_data:
        target.animation_data_clear()


def key(target, frame, *, location=None, rotation=None, scale=None):
    if location is not None:
        target.location = location
        target.keyframe_insert(data_path="location", frame=frame)
    if rotation is not None:
        target.rotation_euler = rotation
        target.keyframe_insert(data_path="rotation_euler", frame=frame)
    if scale is not None:
        target.scale = scale
        target.keyframe_insert(data_path="scale", frame=frame)


def material(name, color):
    found = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    found.diffuse_color = (*color, 1)
    found.use_nodes = True
    bsdf = found.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1)
        bsdf.inputs["Roughness"].default_value = 0.72
    return found


def mesh_part(name, kind, collection, parent, location, scale, surface):
    if kind == "CONE":
        bpy.ops.mesh.primitive_cone_add(vertices=16, radius1=1, radius2=0, depth=2)
    elif kind == "SPHERE":
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8)
    else:
        bpy.ops.mesh.primitive_cube_add()
    part = bpy.context.object
    part.name = name
    for old_collection in list(part.users_collection):
        old_collection.objects.unlink(part)
    collection.objects.link(part)
    part.parent = parent
    part.location = location
    part.scale = scale
    part.data.materials.append(surface)
    return part


def improve_proxy(name, coat):
    """Expose the existing eyes/muzzle and give head parts one pivot."""
    root = obj(f"{name}_PROXY_ROOT")
    char_collection = bpy.data.collections[f"CHAR_{name}"]
    head = bpy.data.objects.new(f"{name}_ANIM_HeadPivot", None)
    char_collection.objects.link(head)
    head.parent = root
    head.location = (0, 0, 1.18)

    heads = [
        obj(f"{name}_Head_PROD_PROXY"),
        obj(f"{name}_Whisker_Pads"),
        obj(f"{name}_Nose"),
    ]
    heads += [obj(f"{name}_Eye_{side}") for side in ("L", "R")]
    for part in heads:
        clear_keys(part)
        old_location = part.location.copy()
        part.parent = head
        part.location = old_location - Vector((0, 0, 1.18))

    obj(f"{name}_Whisker_Pads").location.y = -0.40
    obj(f"{name}_Nose").location.y = -0.53
    for side in ("L", "R"):
        eye = obj(f"{name}_Eye_{side}")
        eye.location.y = -0.425
        eye.scale = (1.25, 1.0, 1.1)
        sx = -1 if side == "L" else 1
        mesh_part(
            f"{name}_Pupil_{side}", "SPHERE", char_collection, head,
            (sx * 0.11, -0.473, 0.035), (0.022, 0.013, 0.05),
            material("MAT_ANIM_Pupil", (0.009, 0.012, 0.011)),
        )
        mesh_part(
            f"{name}_Visible_Ear_{side}", "CONE", char_collection, head,
            (sx * 0.23, -0.02, 0.34), (0.16, 0.115, 0.20), coat,
        )

    chest = bpy.data.objects.get(f"{name}_Chest_Patch")
    if chest:
        chest.location.y = -0.69
    return head


def aim(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def animate_camera(scene):
    data = bpy.data.cameras.new("CAM_AnimatedShort_DATA")
    data.lens = 37
    camera = bpy.data.objects.new("CAM_AnimatedShort", data)
    bpy.data.collections["CAMERAS"].objects.link(camera)
    shots = [
        (1, (0.0, -6.4, 2.2), (0.0, 1.4, 1.18), 33),
        (84, (-0.25, -6.1, 2.15), (0.0, 1.5, 1.2), 34),
        (85, (-3.6, -0.4, 2.15), (-0.2, 2.3, 1.55), 32),
        (190, (-3.5, -0.3, 2.15), (-0.2, 2.3, 1.55), 33),
        (191, (0.0, -6.1, 2.2), (0.0, 1.3, 1.04), 32),
        (END, (0.0, -5.9, 2.2), (0.0, 1.3, 1.04), 33),
    ]
    for frame, loc, target, lens in shots:
        camera.location = loc
        aim(camera, target)
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)
        data.lens = lens
        data.keyframe_insert(data_path="lens", frame=frame)
    scene.camera = camera


def animate_cats():
    cila = obj("Cila_PROXY_ROOT")
    dixon = obj("Dixon_PROXY_ROOT")
    dage = obj("Dage_PROXY_ROOT")
    for root in (cila, dixon, dage):
        clear_keys(root)

    for frame, loc, angle in [
        (1, (-1.6, -0.25, 0), -0.25),
        (166, (-1.6, -0.25, 0), -0.25),
        (218, (-1.2, 0.4, 0), -0.08),
        (END, (-1.2, 0.4, 0), -0.08),
    ]:
        key(cila, frame, location=loc, rotation=(0, 0, angle))
    for frame, loc, angle in [
        (1, (1.7, -0.15, 0), 0.15),
        (178, (1.7, -0.15, 0), 0.15),
        (238, (1.3, 0.35, 0), 0.0),
        (END, (1.3, 0.35, 0), 0.0),
    ]:
        key(dage, frame, location=loc, rotation=(0, 0, angle))
    for frame, loc, angle in [
        (1, (-0.45, 1.48, 0), math.radians(245)),
        (45, (-0.45, 1.8, 0), math.radians(245)),
        (107, (-0.45, 1.8, 0.0), math.radians(245)),
        (130, (-0.45, 1.8, 0.16), math.radians(245)),
        (152, (-0.45, 1.8, 0.0), math.radians(245)),
        (213, (-0.45, 1.8, 0.0), math.radians(245)),
        (END, (-0.45, 1.8, 0.0), math.radians(315)),
    ]:
        key(dixon, frame, location=loc, rotation=(0, 0, angle))

    # Small, timed looks make the cats feel attentive between the big beats.
    for name, poses in {
        "Cila": [(1, 0, 0), (48, 0, 0), (82, -0.10, -0.18),
                 (146, -0.10, -0.18), (190, 0.08, 0.1), (END, 0, 0)],
        "Dixon": [(1, 0, 0), (35, -0.11, -0.10), (85, -0.11, -0.10),
                  (120, 0.11, 0.13), (157, 0, 0), (END, 0.04, -0.12)],
        "Dage": [(1, 0, 0), (168, 0, 0), (213, 0.06, 0.16),
                 (246, 0.0, 0.0), (END, 0, 0)],
    }.items():
        pivot = obj(f"{name}_ANIM_HeadPivot")
        for frame, pitch, yaw in poses:
            key(pivot, frame, rotation=(pitch, 0, yaw))

    # Dixon reaches, makes contact, and settles. The leg follows as a proxy.
    paw = obj("Dixon_Front_Paw_R")
    leg = obj("Dixon_Front_Leg_R")
    for part in (paw, leg):
        clear_keys(part)
    for frame, paw_loc, leg_loc, leg_rot in [
        (1, (0.17, -0.19, 0.11), (0.17, -0.16, 0.34), 0),
        (103, (0.17, -0.19, 0.11), (0.17, -0.16, 0.34), 0),
        (124, (0.17, -0.78, 1.38), (0.17, -0.47, 0.91), -0.4),
        (137, (0.17, -0.90, 1.64), (0.17, -0.56, 1.05), -0.45),
        (158, (0.17, -0.19, 0.11), (0.17, -0.16, 0.34), 0),
        (END, (0.17, -0.19, 0.11), (0.17, -0.16, 0.34), 0),
    ]:
        key(paw, frame, location=paw_loc)
        key(leg, frame, location=leg_loc, rotation=(leg_rot, 0, 0))

    for name, swing in (("Cila", 0.13), ("Dage", 0.18), ("Dixon", 0.10)):
        tail = obj(f"{name}_Tail_FK_PROXY")
        clear_keys(tail)
        base = tail.rotation_euler.copy()
        for frame, offset in ((1, 0), (58, swing), (105, -swing),
                              (178, swing * 0.6), (250, -swing * 0.5), (END, 0)):
            key(tail, frame, rotation=(base.x, base.y, base.z + offset))

    # A quick eye squash reads as a blink even on the simple proxy mesh.
    for name, center in (("Cila", 239), ("Dage", 263), ("Dixon", 252)):
        for side in ("L", "R"):
            eye = obj(f"{name}_Eye_{side}")
            pupil = obj(f"{name}_Pupil_{side}")
            for part in (eye, pupil):
                normal = part.scale.copy()
                key(part, center - 5, scale=normal)
                key(part, center, scale=(normal.x, normal.y, normal.z * 0.08))
                key(part, center + 5, scale=normal)


def animate_blinds_and_light():
    for index in range(16):
        slat = obj(f"Blind_Slat_{index:02d}")
        clear_keys(slat)
        delay = round(abs(index - 7.5) * 0.55)
        for frame, angle in [
            (1, 0), (109, 0), (139 + delay, -37),
            (171 + delay, 17), (205, -10), (END, -10),
        ]:
            key(slat, frame, rotation=(0, 0, math.radians(angle)))

    # Thin golden patches make the changing light legible on the carpet.
    props = bpy.data.collections["PROPS"]
    gold = material("MAT_ANIM_SunStripe", (0.92, 0.67, 0.30))
    for index in range(11):
        x = -2.1 + index * 0.42
        stripe = mesh_part(
            f"ANIM_SunStripe_{index:02d}", "CUBE", props, None,
            (x, 0.55, 0.013), (0.045, 1.18, 0.0025), gold,
        )
        for frame, dx, width in [
            (1, 0, 0.025), (108, 0, 0.025),
            (151, 0.55, 0.065), (186, -0.20, 0.045),
            (225, 0.18, 0.05), (END, 0.18, 0.05),
        ]:
            key(stripe, frame, location=(x + dx, 0.55, 0.013),
                scale=(width, 1.18, 0.0025))

    # Retire the original visual placeholder, which floats in front of the set.
    obj("FX_Sunbeam_Gobo").hide_render = True
    obj("PROP_Cardboard_Box").hide_render = True
    obj("PROP_Paper_Bag").hide_render = True
    obj("PROP_Blue_Storage_Bin").hide_render = True
    obj("Fitness_Mat").hide_render = True
    obj("Fitness_Mat_Red_Logo").hide_render = True
    bpy.data.collections["SET_WorkNook"].hide_render = True
    bpy.data.collections["SET_Condo"].hide_render = True


def main():
    scene = bpy.context.scene
    scene.render.fps = FPS
    scene.frame_start = 1
    scene.frame_end = END
    scene.render.resolution_x = 1280
    scene.render.resolution_y = 720
    scene.render.resolution_percentage = 100
    scene["animated_short"] = "12-second Episode 01 proof of concept"
    scene["animation_notes"] = "Dixon notices blinds, tests one slat, stripes travel, Cila and Dage join. Proxy acting; editable keyframes."
    scene["original_template"] = "Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend"

    for old_marker in list(scene.timeline_markers):
        scene.timeline_markers.remove(old_marker)
    for frame, name in ((1, "NOTICE"), (97, "DIXON_REACH"),
                        (139, "SLATS_TURN"), (192, "LIGHT_TRAVELS"),
                        (239, "SHARED_LOOK")):
        scene.timeline_markers.new(name, frame=frame)

    coats = {
        "Cila": bpy.data.materials["MAT_Cila_Cool_Gray_Brown_Tab"],
        "Dage": bpy.data.materials["MAT_Dage_Black_Coat"],
        "Dixon": bpy.data.materials["MAT_Dixon_Warm_Gray_Tab"],
    }
    for name, coat in coats.items():
        improve_proxy(name, coat)
    animate_cats()
    animate_blinds_and_light()
    animate_camera(scene)

    # Start where the motion is easy to inspect in the camera view.
    scene.frame_set(1)
    for area in bpy.context.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
    print("ANIMATED_SHORT_SAVED", OUTPUT)


if __name__ == "__main__":
    main()
