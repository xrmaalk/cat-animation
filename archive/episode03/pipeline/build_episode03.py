"""Create the non-destructive Episode 03 purr-and-lap Blender animatic.

  blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend \
    --python pipeline/build_episode03.py

The source .blend is never overwritten. This historical builder uses the
existing 7x10 atlas; do not run it against Dage's current 8x11 sheet.
Run this script again on the Episode 03 output to check idempotency; an already
configured file is audited and left unchanged.
"""

import json
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from pipeline.dage_neck_patch import (
    MARK_VERSION,
    mark_version_is_supported,
    require_front_neck_patch,
)
from pipeline.blender_sprite import (
    atlas_grid_label,
    sprite_material as build_sprite_material,
    sprite_plane_width,
)
from pipeline.episode_plan import episode_directory, load_episode_plan

EPISODE_DIR = episode_directory(3, ROOT)
SEED, SHOTS = load_episode_plan(3, ROOT)
MANIFEST = json.loads(
    (ROOT / SEED["sprite_manifest"]).read_text(encoding="utf-8"))
FPS = SEED["fps"]
SHOT_BY_BEAT = {shot["beat"]: shot for shot in SHOTS}
OUTPUT = ROOT / "Purrcilla_Dixon_Dage_EP03_Purr.blend"
SETUP_VERSION = "EP03_Purr_v2_4min"
LAP_CENTER = Vector((-1.0, -0.25, 0.0))


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


def make_lap():
    """Cushion / blanket stand-in for Episode 03 quiet lap + purr study.
    No human character is created.
    """
    lap_collection = collection("SET_LapStudy")

    root = bpy.data.objects.new("PROP_Lap", None)
    lap_collection.objects.link(root)
    root.location = LAP_CENTER
    root["role"] = "Episode 03 quiet lap and purr study"

    # The template keeps its earlier discovery prop as reusable data. Hide it
    # so the Episode 01 cardboard box cannot block Episode 03 compositions.
    for old_name in ("PROP_Cardboard_Box", "PROP_CardboardBox"):
        old_prop = bpy.data.objects.get(old_name)
        if old_prop:
            old_prop.hide_render = True
            old_prop.hide_set(True)

    def _fabric_material(name, kind="plush"):
        """Procedural fabric. kind: 'plush', 'weave', or 'silk'."""
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
        nt = mat.node_tree
        nodes, links = nt.nodes, nt.links
        nodes.clear()

        out = nodes.new("ShaderNodeOutputMaterial")
        out.location = (1180, 40)

        principled = nodes.new("ShaderNodeBsdfPrincipled")
        principled.location = (640, 160)

        texcoord = nodes.new("ShaderNodeTexCoord")
        texcoord.location = (-860, 80)

        mapping = nodes.new("ShaderNodeMapping")
        mapping.location = (-640, 80)
        mapping.inputs["Scale"].default_value = (18.0, 18.0, 18.0)
        links.new(texcoord.outputs["Object"], mapping.inputs["Vector"])

        tangent = nodes.new("ShaderNodeTangent")
        tangent.location = (-640, -200)
        tangent.direction_type = "UV_MAP"

        if kind == "weave":
            wave_u = nodes.new("ShaderNodeTexWave")
            wave_u.location = (-400, 240)
            wave_u.wave_type = "BANDS"
            wave_u.bands_direction = "X"
            wave_u.inputs["Scale"].default_value = 12.0
            wave_u.inputs["Distortion"].default_value = 1.4
            links.new(mapping.outputs["Vector"], wave_u.inputs["Vector"])

            wave_v = nodes.new("ShaderNodeTexWave")
            wave_v.location = (-400, 20)
            wave_v.wave_type = "BANDS"
            wave_v.bands_direction = "Y"
            wave_v.inputs["Scale"].default_value = 12.0
            wave_v.inputs["Distortion"].default_value = 1.4
            links.new(mapping.outputs["Vector"], wave_v.inputs["Vector"])

            mix_pat = nodes.new("ShaderNodeMix")
            mix_pat.location = (-140, 120)
            mix_pat.data_type = "FLOAT"
            mix_pat.blend_type = "MULTIPLY"
            mix_pat.inputs["Factor"].default_value = 1.0
            links.new(wave_u.outputs["Fac"], mix_pat.inputs["A"])
            links.new(wave_v.outputs["Fac"], mix_pat.inputs["B"])
            pattern_out = mix_pat.outputs["Result"]
            base_color = (0.22, 0.18, 0.28, 1.0)
            roughness = (0.55, 0.88)
            bump_strength = 0.12
            sheen_weight = 0.55
        elif kind == "silk":
            # fine warp threads + slow color drift for moiré / shot-silk
            wave_u = nodes.new("ShaderNodeTexWave")
            wave_u.location = (-400, 240)
            wave_u.wave_type = "BANDS"
            wave_u.bands_direction = "X"
            wave_u.wave_profile = "SIN"
            wave_u.inputs["Scale"].default_value = 42.0
            wave_u.inputs["Distortion"].default_value = 0.35
            links.new(mapping.outputs["Vector"], wave_u.inputs["Vector"])

            noise = nodes.new("ShaderNodeTexNoise")
            noise.location = (-400, -20)
            noise.noise_dimensions = "3D"
            noise.inputs["Scale"].default_value = 7.5
            noise.inputs["Detail"].default_value = 6.0
            noise.inputs["Roughness"].default_value = 0.4
            links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

            mix_pat = nodes.new("ShaderNodeMix")
            mix_pat.location = (-140, 120)
            mix_pat.data_type = "FLOAT"
            mix_pat.blend_type = "OVERLAY"
            mix_pat.inputs["Factor"].default_value = 0.25
            links.new(wave_u.outputs["Fac"], mix_pat.inputs["A"])
            links.new(noise.outputs["Fac"], mix_pat.inputs["B"])
            pattern_out = mix_pat.outputs["Result"]
            base_color = (0.62, 0.48, 0.58, 1.0)  # dusty rose silk
            roughness = (0.08, 0.22)
            bump_strength = 0.04
            sheen_weight = 1.0
        else:
            noise = nodes.new("ShaderNodeTexNoise")
            noise.location = (-400, 200)
            noise.noise_dimensions = "3D"
            noise.inputs["Scale"].default_value = 55.0
            noise.inputs["Detail"].default_value = 8.0
            noise.inputs["Roughness"].default_value = 0.55
            links.new(mapping.outputs["Vector"], noise.inputs["Vector"])

            detail_noise = nodes.new("ShaderNodeTexNoise")
            detail_noise.location = (-400, -40)
            detail_noise.noise_dimensions = "3D"
            detail_noise.inputs["Scale"].default_value = 9.0
            detail_noise.inputs["Detail"].default_value = 4.0
            detail_noise.inputs["Roughness"].default_value = 0.65
            links.new(mapping.outputs["Vector"], detail_noise.inputs["Vector"])

            mix_pat = nodes.new("ShaderNodeMix")
            mix_pat.location = (-140, 80)
            mix_pat.data_type = "FLOAT"
            mix_pat.blend_type = "OVERLAY"
            mix_pat.inputs["Factor"].default_value = 0.45
            links.new(noise.outputs["Fac"], mix_pat.inputs["A"])
            links.new(detail_noise.outputs["Fac"], mix_pat.inputs["B"])
            pattern_out = mix_pat.outputs["Result"]
            base_color = (0.27, 0.18, 0.36, 1.0)  # muted plum cushion
            roughness = (0.55, 0.88)
            bump_strength = 0.18
            sheen_weight = 0.85

        ramp = nodes.new("ShaderNodeValToRGB")
        ramp.location = (120, 240)
        ramp.color_ramp.elements[0].position = 0.35
        ramp.color_ramp.elements[0].color = (
            base_color[0] * 0.72,
            base_color[1] * 0.72,
            base_color[2] * 0.72,
            1.0,
        )
        ramp.color_ramp.elements[1].color = base_color
        if kind == "silk":
            # shot-silk: second stop shifts cooler so glancing light changes hue
            if len(ramp.color_ramp.elements) < 3:
                ramp.color_ramp.elements.new(0.72)
            ramp.color_ramp.elements[2].color = (0.45, 0.52, 0.68, 1.0)
        links.new(pattern_out, ramp.inputs["Fac"])
        links.new(ramp.outputs["Color"], principled.inputs["Base Color"])

        rough = nodes.new("ShaderNodeMapRange")
        rough.location = (120, 40)
        rough.inputs["From Min"].default_value = 0.2
        rough.inputs["From Max"].default_value = 0.8
        rough.inputs["To Min"].default_value = roughness[0]
        rough.inputs["To Max"].default_value = roughness[1]
        links.new(pattern_out, rough.inputs["Value"])
        links.new(rough.outputs["Result"], principled.inputs["Roughness"])

        bump = nodes.new("ShaderNodeBump")
        bump.location = (360, -120)
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.03
        links.new(pattern_out, bump.inputs["Height"])
        links.new(bump.outputs["Normal"], principled.inputs["Normal"])

        if "Sheen Weight" in principled.inputs:
            principled.inputs["Sheen Weight"].default_value = sheen_weight
        elif "SheenWeight" in principled.inputs:
            principled.inputs["SheenWeight"].default_value = sheen_weight
        if "Sheen Roughness" in principled.inputs:
            principled.inputs["Sheen Roughness"].default_value = (
                0.12 if kind == "silk" else 0.28
            )
        elif "SheenRoughness" in principled.inputs:
            principled.inputs["SheenRoughness"].default_value = (
                0.12 if kind == "silk" else 0.28
            )
        if "SheenTint" in principled.inputs:
            principled.inputs["SheenTint"].default_value = (
                (0.95, 0.88, 0.92, 1.0) if kind == "silk" else (
                    0.85, 0.78, 0.72, 1.0)
            )

        # Anisotropy on Principled when the socket exists (3.x / some 4.x builds)
        if "Anisotropic" in principled.inputs:
            principled.inputs["Anisotropic"].default_value = 0.85 if kind == "silk" else 0.0
            if "Anisotropic Rotation" in principled.inputs:
                # thread-aligned highlight; pattern drives slight rotation jitter
                rot_map = nodes.new("ShaderNodeMapRange")
                rot_map.location = (360, 40)
                rot_map.inputs["To Min"].default_value = 0.22
                rot_map.inputs["To Max"].default_value = 0.28
                links.new(pattern_out, rot_map.inputs["Value"])
                links.new(rot_map.outputs["Result"],
                          principled.inputs["Anisotropic Rotation"])
            if "Tangent" in principled.inputs:
                links.new(tangent.outputs["Tangent"],
                          principled.inputs["Tangent"])

        links.new(principled.outputs["BSDF"], out.inputs["Surface"])
        return mat

    def _soft_cuboid(name, size, location, parent, bevel_width=0.04, fabric="plush"):
        mesh = bpy.data.meshes.new(name + "_Mesh")
        obj = bpy.data.objects.new(name, mesh)
        lap_collection.objects.link(obj)
        obj.parent = parent
        obj.location = location

        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        bm.to_mesh(mesh)
        bm.free()
        obj.scale = size

        bevel = obj.modifiers.new(name="EP03_Bevel", type="BEVEL")
        bevel.width = bevel_width
        bevel.segments = 4
        bevel.limit_method = "ANGLE"
        bevel.angle_limit = 1.047
        bevel.miter_outer = "MITER_ARC"

        sub = obj.modifiers.new(name="EP03_Subsurf", type="SUBSURF")
        sub.levels = 2
        sub.render_levels = 2
        sub.subdivision_type = "CATMULL_CLARK"

        smooth = obj.modifiers.new(name="EP03_Smooth", type="SMOOTH")
        smooth.factor = 0.35
        smooth.iterations = 3

        for poly in obj.data.polygons:
            poly.use_smooth = True

        mat = _fabric_material(name + "_Fabric", kind=fabric)
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)

        obj.display_type = "SOLID"
        return obj

    _soft_cuboid(
        "EP03_Cushion",
        size=(0.55, 0.42, 0.10),
        location=(0.0, 0.0, 0.05),
        parent=root,
        bevel_width=0.05,
        fabric="plush",
    )
    _soft_cuboid(
        "EP03_Blanket",
        size=(0.62, 0.38, 0.04),
        location=(0.02, -0.03, 0.12),
        parent=root,
        bevel_width=0.025,
        fabric="silk",
    )

    return root, lap_collection


def look_at(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_cameras():
    """Episode 03 camera set: Purrcilla is the hero, lap study stays readable."""
    poses = {
        # primary portrait — Cila on the lap / cushion
        "CAM_HeroPortrait_Cila": ((-1.35, -4.05, 1.45), (-1.35, -0.35, 0.88), 52),
        # face + slow blink
        "CAM_Insert_Eyes": ((-1.05, -3.25, 1.5), (-1.05, -0.25, 1.31), 65),
        # chest, front paws, and cushion
        "CAM_Insert_Paws": ((-1.05, -2.85, 0.82), (-1.05, -0.25, 0.48), 62),
        # supporting / leftover coverage
        "CAM_CatEye_A": ((0.15, -5.8, 1.72), (0.25, -0.05, 0.78), 28),
        "CAM_CondoPeek": ((-4.5, -3.1, 1.4), (-4.5, 0.7, 1.0), 48),
        "CAM_HeroPortrait_Dage": ((-4.5, -3.6, 1.4), (-4.5, 0.7, 1.02), 52),
        "CAM_HeroPortrait_Dixon": ((2.2, -4.2, 1.42), (2.0, 0.45, 1.02), 52),
        "CAM_WindowReport": ((1.6, -4.4, 1.7), (0.35, 0.05, 0.95), 34),
        # wide: lap study in frame, room on the sides for Dixon and Dage
        "CAM_PorchWide": ((0.2, -6.4, 2.45), (LAP_CENTER[0] + 0.4, LAP_CENTER[1], LAP_CENTER[2] + 0.25), 24),
    }

    for name, (position, target, lens) in poses.items():
        camera = bpy.data.objects.get(name)
        if camera is None or camera.type != "CAMERA":
            raise RuntimeError(f"Missing template camera {name}")
        # drop copied Episode 02 Dixon / box animation instead of preserving it
        if camera.animation_data:
            if camera.animation_data.action:
                camera.animation_data.action.use_fake_user = False
            camera.animation_data_clear()
        camera.location = position
        look_at(camera, target)
        camera.data.lens = lens
        camera["ep03_target"] = target
        camera["ep03_role"] = {
            "CAM_HeroPortrait_Cila": "primary Purrcilla portrait",
            "CAM_Insert_Eyes": "Purrcilla face and slow blink",
            "CAM_Insert_Paws": "chest, front paws, and lap cushion",
            "CAM_PorchWide": "lap study wide with room for Dixon and Dage",
            "CAM_CatEye_A": "lap study establishing",
            "CAM_HeroPortrait_Dage": "Dage coverage, not hero",
            "CAM_HeroPortrait_Dixon": "Dixon coverage, not box approach",
        }.get(name, "supporting")

    scene = bpy.context.scene
    scene.camera = bpy.data.objects["CAM_HeroPortrait_Cila"]
    return poses


def sprite_material(name, image, sprite):
    return build_sprite_material(
        f"MAT_EP03_{name}_Sprite", image, sprite,
        MANIFEST["characters"][name],
    )


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
    controller = bpy.data.objects.new(f"EP03_{name}_Sprite_CTRL", None)
    character_collection.objects.link(controller)
    controller.empty_display_type = "ARROWS"
    controller.empty_display_size = 0.25
    controller["episode_role"] = "Sprite movement; original 3D rig remains a reference"
    height = {"Cila": 1.83, "Dixon": 1.82, "Dage": 1.96}[name]
    width = sprite_plane_width(height, info)
    mesh = bpy.data.meshes.new(f"SPRITE_{name}_Mesh")
    mesh.from_pydata([(-width / 2, 0, 0), (width / 2, 0, 0),
                      (width / 2, 0, height), (-width / 2, 0, height)],
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
    sprite["atlas_grid"] = atlas_grid_label(info)
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
        action["episode"] = 3
        action["pose"] = pose
        set_constant(action)
        actions[pose] = action
    sprite.animation_data.action = None
    sprite["sprite_frame"] = frame_map["idle"]
    return actions


def add_sprite_nla(sprite, name, actions):
    nla = sprite.animation_data.nla_tracks.new()
    nla.name = f"EP03_{name}_SPRITE_ACTIONS"
    for shot in SHOTS:
        pose = shot[f"{name.lower()}_action"]
        action = actions[pose]
        start = int(shot["start_seconds"]) * FPS
        duration = int(shot["duration_seconds"]) * FPS
        strip = nla.strips.new(
            f"EP03_{shot['shot']}_{name}_{pose}", start, action)
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]
        first, last = action.frame_range
        strip.action_frame_start = first
        strip.action_frame_end = max(first + 1, last)
        # NLA frame_end is inclusive. End one frame before the next shot so
        # the incoming sprite pose takes effect on its camera-cut frame.
        strip.scale = (duration - 1) / \
            (strip.action_frame_end - strip.action_frame_start)
        strip.blend_type = "REPLACE"
    return nla


def animate_controllers(controllers):
    start = lambda beat: int(SHOT_BY_BEAT[beat]["start_seconds"])
    end = int(SEED["runtime_seconds"])
    paths = {
        "Dage": [(0, (-4.5, 0.7, 0)),
                 (start("DAGE_NOTICES"), (-4.5, 0.7, 0)),
                 (start("DAGE_APPROACHES"), (1.35, 0.05, 0)),
                 (start("SHARED_LISTENING"), (0.45, -0.05, 0)),
                 (end, (0.45, -0.05, 0))],
        "Dixon": [(0, (2.9, 1.4, 0)),
                  (start("DIXON_NOTICES"), (2.9, 1.4, 0)),
                  (start("DIXON_LISTENS"), (1.6, -0.05, 0)),
                  (start("SHARED_QUIET"), (2.0, 0.05, 0)),
                  (end, (2.0, 0.05, 0))],
        "Cila": [(0, (-1.8, -0.52, 0)),
                 (start("CILA_FEELS_RESTLESS"), (-1.8, -0.52, 0)),
                 (start("CILA_APPROACHES_LAP"), (-1.65, -0.45, 0)),
                 (start("CILA_SETTLES"), (-1.05, -0.25, 0.17)),
                 (end, (-1.05, -0.25, 0.17))],
    }
    for name, points in paths.items():
        controller = controllers[name]
        for seconds, position in points:
            key(controller, "location", seconds * FPS, position)
        if controller.animation_data and controller.animation_data.action:
            controller.animation_data.action.name = f"ACT_EP03_{name}_ROOT_MOTION"
            controller.animation_data.action.use_fake_user = True


def editorial_nla():
    holder = bpy.data.objects.get("EDITORIAL_MASTER_NLA")
    if holder is None or not holder.animation_data:
        raise RuntimeError("Missing editorial NLA holder")

    source_track = next(
        (
            track
            for track in holder.animation_data.nla_tracks
            if track.name == "EP01_BEATS"
        ),
        None,
    )
    if source_track is None:
        raise RuntimeError("Missing source EP01_BEATS track")

    if any(
        track.name == "EP03_BEATS"
        for track in holder.animation_data.nla_tracks
    ):
        raise RuntimeError("EP03_BEATS already exists")

    source_strips = sorted(source_track.strips,
                           key=lambda strip: strip.frame_start)
    if len(source_strips) != len(SHOTS):
        raise RuntimeError(
            "Episode 01 NLA layout does not match the 26-shot Episode 03 plan"
        )

    source_track.mute = True

    episode_track = holder.animation_data.nla_tracks.new()
    episode_track.name = "EP03_BEATS"

    for shot, source_strip in zip(SHOTS, source_strips):
        action = source_strip.action.copy()
        action.name = f"ACT_EP03_{shot['shot']}_{shot['beat']}"
        action.use_fake_user = True
        action["episode"] = 3
        action["beat"] = shot["beat"]
        action["camera"] = shot["camera"]
        action["note"] = shot["description"]

        strip = episode_track.strips.new(
            f"EP03_{shot['shot']}_{shot['beat']}",
            int(shot["start_seconds"]) * FPS,
            action,
        )
        if hasattr(strip, "action_slot") and action.slots:
            strip.action_slot = action.slots[0]

        strip.action_frame_start = source_strip.action_frame_start
        strip.action_frame_end = max(
            strip.action_frame_start + 1,
            source_strip.action_frame_end,
        )
        duration = int(shot["duration_seconds"]) * FPS
        strip.scale = (duration - 1) / (
            strip.action_frame_end - strip.action_frame_start
        )
        strip.blend_type = "REPLACE"

    holder["episode03_editorial"] = (
        f"26 modular blocks retimed to {SEED['runtime_seconds']} seconds"
    )


def configure_markers_and_notes(camera_poses):
    scene = bpy.context.scene
    edit = bpy.data.collections["EDIT_NLA"]
    target = bpy.data.objects.new("EP03_SPRITE_CAMERA_TARGET", None)
    edit.objects.link(target)
    target.empty_display_type = "SPHERE"
    target.empty_display_size = 0.12
    for shot in SHOTS:
        frame = int(shot["start_seconds"]) * FPS
        camera = bpy.data.objects[shot["camera"]]
        scene.frame_set(frame)
        marker = scene.timeline_markers.new(
            f"EP03_{shot['shot']}_{shot['beat']}", frame=frame)
        marker.camera = camera
        key(target, "location", frame, camera.matrix_world.translation.copy())
        card = bpy.data.objects.new(f"EP03_CARD_{shot['shot']}", None)
        edit.objects.link(card)
        card.hide_render = True
        card["beat"] = shot["beat"]
        card["camera"] = shot["camera"]
        card["note"] = shot["description"]
        card["duration_seconds"] = int(shot["duration_seconds"])
    if target.animation_data and target.animation_data.action:
        target.animation_data.action.name = "ACT_EP03_SPRITE_CAMERA_TARGET"
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
    # Keep the Episode 01 labels as datablocks, but let the EP03 fact pass be
    # enabled without revealing unrelated words about blinds and sunlight.
    for obj in group.objects:
        if obj.name.startswith("LOWER_THIRD_"):
            obj.hide_render = True
            obj.hide_set(True)
    camera = bpy.data.objects["CAM_CatEye_A"]
    title_body = "Purrcilla Discovers\nWhy a Cat's Purr Is So Relaxing"
    for name, body, loc, size in (
        ("EP03_TITLE_CARD", title_body, (0, 0.62, -3.0), 0.065),
        ("EP03_FACT_LABEL", SEED["fact_label"], (0, 0.72, -3.0), 0.09),
        ("EP03_OPTIONAL_NARRATION", SEED["optional_narration"],
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
        text["episode"] = 3
        text.hide_render = False
        if name in ("EP03_TITLE_CARD", "EP03_OPTIONAL_NARRATION"):
            text.hide_render = True
    backdrop = cuboid("EP03_FACT_BACKDROP", (0, 0.75, -3.03),
                      (1.64, 0.18, 0.005),
                      color_material("MAT_EP03_Fact_Backdrop",
                                     (0.035, 0.025, 0.05)),
                      group, camera)
    backdrop["episode"] = 3
    group.hide_render = True
    group.hide_viewport = True
    beat_sheet = bpy.data.texts.new("EP03_BEAT_SHEET_README")
    beat_sheet.write(SEED["episode_title"] + "\n\n")
    for shot in SHOTS:
        beat_sheet.write(f"{shot['shot']} | {shot['beat']} | {shot['start_seconds']}s | "
                         f"{shot['duration_seconds']}s | {shot['camera']} | {shot['description']}\n")
    beat_sheet.write(
        "\nNarration and fact label OFF by default. Preserve quiet holds and slow blinks.\n")


def audit():
    scene = bpy.context.scene
    expected = ["SET_LapStudy", "CHAR_Cila", "CHAR_Dixon", "CHAR_Dage",
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
            raise RuntimeError(
                "Dage sheet needs upgrading; run apply_dage_sprite_sheet.py")
    holder = bpy.data.objects["EDITORIAL_MASTER_NLA"]
    tracks = {track.name: len(track.strips)
              for track in holder.animation_data.nla_tracks}
    if tracks.get("EP01_BEATS") != 26 or tracks.get("EP03_BEATS") != 26:
        raise RuntimeError(
            f"Expected 26 editorial strips per episode: {tracks}")
    counts = {"scenes": len(bpy.data.scenes), "collections": len(bpy.data.collections),
              "objects": len(bpy.data.objects), "actions": len(bpy.data.actions),
              "materials": len(bpy.data.materials), "editorial_tracks": tracks}
    print("EP03_AUDIT", json.dumps(counts, sort_keys=True), flush=True)
    return counts


def main():
    scene = bpy.context.scene
    if scene.get("episode03_setup_version") == SETUP_VERSION:
        print("EP03_ALREADY_CONFIGURED; no objects or actions added", flush=True)
        audit()
        return
    if scene.name != "CT_MASTER_EP01_TEMPLATE":
        raise RuntimeError("Start from the existing Episode 01 template blend")
    if OUTPUT.exists() and "--overwrite" not in sys.argv:
        raise FileExistsError(f"Output exists: {OUTPUT}")
    runtime = int(SEED["runtime_seconds"])
    if len(SHOTS) != 26:
        raise RuntimeError(
            "Episode 03 must contain its 26 planned blocks"
        )
    for name in ("Cila", "Dixon", "Dage"):
        if (ROOT / MANIFEST["characters"][name]["atlas"]).is_file() is False:
            raise FileNotFoundError(f"Missing prepared atlas for {name}")

    scene.frame_set(0)
    source_blend = Path(bpy.data.filepath).name
    make_lap()
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
    scene.name = "EP03_Purr"
    scene["episode_number"] = SEED["episode_number"]
    scene["episode_title"] = SEED["episode_title"]
    scene["episode_seed"] = SEED["episode_seed"]
    scene["audience_fact"] = SEED["audience_fact"]
    scene["fact_label"] = SEED["fact_label"]
    scene["optional_narration"] = SEED["optional_narration"]
    scene["discovery_prop"] = SEED["discovery_prop"]
    scene["discovery_collection"] = SEED["discovery_collection"]
    scene["lead_character"] = SEED["lead_character"]
    scene["runtime_seconds"] = runtime
    scene["sprite_manifest"] = SEED["sprite_manifest"]
    scene["episode01_source_blend"] = source_blend
    scene["episode03_setup_version"] = SETUP_VERSION
    scene["sprite_rig_policy"] = "EP03 sprite planes use their own actions; 3D rigs remain as hidden references"
    scene.frame_end = runtime * FPS
    scene.frame_set(int(SHOT_BY_BEAT["CILA_FEELS_RESTLESS"]["start_seconds"]) * FPS)
    audit()
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT))
    print("EP03_SAVED", OUTPUT, flush=True)


if __name__ == "__main__":
    main()
