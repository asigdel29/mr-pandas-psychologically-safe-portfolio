"""Rewrite the Scene One baked labels (not_waterfall atlas) in anu's voice.

Two floating handwritten labels on the paper wall -- the welcome greeting and
the about-me blurb. Pixel boxes come from the Blender UVs (not_waterfall is a
FLIP atlas: y = (1 - v) * 4096); confirmed by crop to hold the real handwriting.

    python3 ../ktx_tools.py decode ../../public/textures/not_waterfall.ktx2 nw_base.png
    python3 label_not_waterfall.py nw_base.png nw_painted.png
    python3 ../ktx_tools.py encode nw_painted.png ../../public/textures/not_waterfall.ktx2
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from text_tools import Region, apply  # noqa: E402

REGIONS = [
    # big welcome heading (was "Welcome to my portfolio!! -Mr. Panda ...")
    Region(box=(1334, 513, 2734, 1472), kind="floating",
           text="hi, i'm anu :D this is my site,",
           name="welcome"),
    # about-me blurb (was "I am a human researcher trying to help prevent ...")
    Region(box=(15, 24, 1107, 1099), kind="floating",
           text="i'm an engineer/builder, wannabe researcher and wannabe "
                "philosopher! p.s. i love hacking on stuff, reach out if you "
                "are too!",
           name="about"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 label_not_waterfall.py <in.png> <out.png>")
        return 2
    apply(argv[1], argv[2], REGIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
