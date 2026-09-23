"""Grid-independent Blender sprite material shared by episode directors.

The manifest, not the episode number, supplies UV layout. This accepts both
the historical square 7x10 cells and Dage's current 192x208 8x11 cells.
"""

import bpy

from pipeline.sprite_manifest import grid_geometry


def sprite_plane_width(height, info):
    _, _, cell_width, cell_height = grid_geometry(info)
    return height * cell_width / cell_height


def atlas_grid_label(info):
    columns, rows, cell_width, cell_height = grid_geometry(info)
    return (f"{columns}x{rows}, {cell_width}x{cell_height}px cells, "
            "top-left row-major")


def _math(nodes, operation, a=None, b=None):
    node = nodes.new("ShaderNodeMath")
    node.operation = operation
    if a is not None:
        node.inputs[0].default_value = a
    if b is not None:
        node.inputs[1].default_value = b
    return node


def sprite_material(material_name, image, sprite, info):
    """Build a frame-driven, alpha-blended material for any uniform atlas."""
    columns, rows, _, _ = grid_geometry(info)
    material = bpy.data.materials.new(material_name)
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
    frame.label = "Driven by sprite_frame on " + sprite.name
    frame.outputs[0].default_value = 0
    driver = frame.outputs[0].driver_add("default_value").driver
    driver.type = "SCRIPTED"
    variable = driver.variables.new()
    variable.name = "sprite_index"
    variable.type = "SINGLE_PROP"
    variable.targets[0].id = sprite
    variable.targets[0].data_path = '["sprite_frame"]'
    driver.expression = "sprite_index"

    u_scale = _math(nodes, "MULTIPLY", b=1.0 / columns)
    column = _math(nodes, "MODULO", b=float(columns))
    column_scale = _math(nodes, "MULTIPLY", b=1.0 / columns)
    u_add = _math(nodes, "ADD")
    links.new(separate.outputs["X"], u_scale.inputs[0])
    links.new(frame.outputs[0], column.inputs[0])
    links.new(column.outputs[0], column_scale.inputs[0])
    links.new(u_scale.outputs[0], u_add.inputs[0])
    links.new(column_scale.outputs[0], u_add.inputs[1])

    v_scale = _math(nodes, "MULTIPLY", b=1.0 / rows)
    row_divide = _math(nodes, "DIVIDE", b=float(columns))
    row_floor = _math(nodes, "FLOOR")
    row_reverse = _math(nodes, "SUBTRACT", a=float(rows - 1))
    row_scale = _math(nodes, "MULTIPLY", b=1.0 / rows)
    v_add = _math(nodes, "ADD")
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
