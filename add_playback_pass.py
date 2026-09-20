"""Add visible placeholder playback animation to an existing template .blend.

Run from the template folder:
    blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend \
        --python add_playback_pass.py
"""

import os
import sys
import bpy


ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import build_template as template


def main():
    scene = bpy.context.scene
    template.build_playback_animation({}, scene)
    output = bpy.data.filepath or os.path.join(
        ROOT, "Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend"
    )
    bpy.ops.wm.save_as_mainfile(filepath=output)
    print("Playback animation added and saved:", output)


if __name__ == "__main__":
    main()

