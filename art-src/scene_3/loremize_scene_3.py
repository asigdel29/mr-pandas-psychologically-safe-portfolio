"""Replace the Scene Three job cards (scene_3 atlas) with lorem ipsum.

Boxes come from the REAL GLB (Draco) UVs of the card nodes, decoded with
DracoPy -- NOT the Blender .blend UVs, which do not match the exported GLB.
Confirmed by reading the actual atlas pixels:

  * Human  (node Plane.124, u0.423-0.547 v0.391-0.509) -> NF box, UPRIGHT.
  * Senior (node Plane.125, u0.296-0.415 v0.384-0.509) -> NF box, but the card
    is baked ROTATED 90 deg CCW (text runs bottom-to-top), so we letter onto a
    rotated tile.

IMPORTANT: unlike the scene_4 publication cards, these scene_3 cards are NOT
opaque paper -- they are transparent planes carrying only dark ink strokes (the
notebook wall shows through behind them; measured alpha mean ~35, ~0% light
"paper" pixels). So they are kind="floating": wipe the box alpha to delete the
old strokes (wall shows through, exactly like the original card look) and draw
new lorem ink. Using kind="card" here leaves a grey ghost because there is no
paper colour to flood with.

    python3 ../ktx_tools.py decode ../../public/textures/scene_3.ktx2 s3_base.png
    python3 loremize_scene_3.py s3_base.png s3_painted.png
    python3 ../ktx_tools.py encode s3_painted.png ../../public/textures/scene_3.ktx2
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from text_tools import Region, apply  # noqa: E402

_L = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit sed do "
      "eiusmod tempor incididunt ut labore.")

# Wipe the FULL GLB card box (incl. border + bear icon) so no original stroke
# ghosts, then float lorem. A couple px margin avoids touching the neighbour.
REGIONS = [
    # Human card -- upright. GLB NF box (1732,1601,2240,2084).
    Region(box=(1730, 1599, 2242, 2086), kind="floating", text=_L,
           pad=26, name="human"),
    # Senior card -- baked rotated 90 CCW. GLB NF box (1212,1572,1699,2084).
    Region(box=(1210, 1570, 1701, 2086), kind="floating", text=_L,
           rotate=90, pad=26, name="senior"),
]


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 loremize_scene_3.py <in.png> <out.png>")
        return 2
    apply(argv[1], argv[2], REGIONS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
