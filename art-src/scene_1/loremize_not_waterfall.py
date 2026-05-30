"""Replace the Scene One baked labels (not_waterfall atlas) with lorem ipsum.

Regions are floating handwriting on the paper wall; pixel boxes come from the
Blender UVs (no-flip atlas: x=u*4096, y=v*4096). Run:

    python3 ../ktx_tools.py decode ../../public/textures/not_waterfall.ktx2 nw_base.png
    python3 loremize_not_waterfall.py nw_base.png nw_painted.png
    python3 ../ktx_tools.py encode nw_painted.png ../../public/textures/not_waterfall.ktx2
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from text_tools import Region, apply  # noqa: E402

# not_waterfall is a FLIP atlas (y = (1 - v) * 4096); these pixel boxes are the
# flipped Blender UVs and hold the real handwriting (confirmed by crop).
REGIONS = [
    # "Welcome to my portfolio!! -Mr. Panda  p.s. I love traveling!!"
    Region(box=(1334, 513, 2734, 1472), kind="floating",
           text="Lorem ipsum dolor sit amet, consectetur adipiscing elit sed.",
           name="welcome"),
    # "I am a human researcher trying to help prevent the extinction..."
    Region(box=(15, 24, 1107, 1099), kind="floating",
           text="Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna "
                "aliqua. Ut enim ad minim veniam, quis nostrud exercitation.",
           name="about"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 loremize_not_waterfall.py <in.png> <out.png>")
        return 2
    apply(argv[1], argv[2], REGIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
