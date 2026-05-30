"""Replace the Scene Four publication cards (scene_4 atlas) with lorem ipsum.

The two "Featured Work" publication cards are opaque paper cards with dark
handwriting -> kind="card". Boxes are FLIP pixels (y = (1 - v) * 4096) from the
Blender UVs of Plane.125 / Plane.126, confirmed by crop: the flipped boxes hold
the readable card text, the no-flip mirror is blank paper.

    python3 ../ktx_tools.py decode ../../public/textures/scene_4.ktx2 s4_base.png
    python3 loremize_scene_4.py s4_base.png s4_painted.png
    python3 ../ktx_tools.py encode s4_painted.png ../../public/textures/scene_4.ktx2
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from text_tools import Region, apply  # noqa: E402

# Boxes are FL pixels from the real GLB (Draco) UVs of nodes Plane125 / Plane126
# (y = (1 - v) * 4096). The FL boxes hold the readable card text; the NF mirror
# is blank paper. Cards render upright in-world, so no rotation.
REGIONS = [
    Region(box=(1240, 243, 2150, 858), kind="card",
           text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore.",
           pad=18, name="pub_left"),
    Region(box=(2203, 243, 3112, 858), kind="card",
           text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna.",
           pad=18, name="pub_right"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 loremize_scene_4.py <in.png> <out.png>")
        return 2
    apply(argv[1], argv[2], REGIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
