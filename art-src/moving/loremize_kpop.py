"""Replace the "Kpop Demon Hunters is a great movie btw" note (kpop atlas).

The note is a floating handwritten sticky on its own 1024x1024 kpop.ktx2 atlas,
baked UPSIDE-DOWN (rotate 180). kind="floating": wipe the box alpha, then draw
lorem rotated 180 so it reads upright in-world. Box found by ink detection
(Blender has no kpop-textured mesh to query).

    python3 ../ktx_tools.py decode ../../public/textures/kpop.ktx2 kpop_base.png
    python3 loremize_kpop.py kpop_base.png kpop_painted.png
    python3 ../ktx_tools.py encode kpop_painted.png ../../public/textures/kpop.ktx2
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from text_tools import Region, apply  # noqa: E402

REGIONS = [
    Region(box=(40, 540, 600, 960), kind="floating", rotate=180,
           text="Lorem ipsum dolor sit amet consectetur adipiscing elit.",
           pad=24, name="kpop_note"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 loremize_kpop.py <in.png> <out.png>")
        return 2
    apply(argv[1], argv[2], REGIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
