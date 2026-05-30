"""Turn the pirate galleon on the Moving_extras atlas into a speedboat.

The ship cutout is drawn UPSIDE-DOWN in the atlas: the brown hull (with
scroll/porthole detailing) sits at the TOP (y~2450-2785), and the two masts +
three white sails + blue masthead pennant hang BELOW it (y~2785-3990). When
rendered the mesh flips so the hull floats on the water with the rig above.

Speedboat = drop the rig, keep a sleek hull:
  1. Erase (alpha 0) everything below the hull deck -> removes masts, sails,
     pennant. The hull silhouette + its dark outline survive.
  2. Recolour the brown hull to a white speedboat body with a bold red
     waterline stripe along its lower edge (keeps the hand-drawn outline +
     porthole scrollwork as dark linework).

Operates in place on public/textures/Moving_extras.ktx2.
    TMPDIR=/private/tmp python3 speedboat.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

TEX = os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures",
                   "Moving_extras.ktx2")

# ship island bounds in the atlas. The pirate galleon is drawn UPSIDE-DOWN: the
# deck/rail is at the atlas TOP (y~2260), the hull body below it, and the rig
# (masts/sails/pennant) hangs from y~2776 down.
SHIP_X = (100, 1400)          # hull ends ~x1380; gap then a separate camel at x1420
HULL_TOP_Y = 2225             # include the full deck rail so no tan strip survives
HULL_BOTTOM_Y = 2776          # below this = rig (masts/sails/pennant) -> erase

# Two mast stubs survive the cut (ETC1S alpha-bleed at the hard edge), at the
# left + right mast columns. Erase those columns a little past the cut.
MAST_STUBS = [(330, 2770, 430, 3000), (1180, 2770, 1380, 3010)]

HULL_WHITE = (238, 240, 240)
STRIPE_RED = (196, 54, 44)


def main() -> int:
    out = "/private/tmp/_speedboat.png"
    ktx_tools.decode(TEX, out)
    arr = np.array(Image.open(out).convert("RGBA"))

    x0, x1 = SHIP_X
    # 1. erase the rig (everything below the hull) + the stray mast stubs
    arr[HULL_BOTTOM_Y:4096, x0:x1, 3] = 0
    for mx0, my0, mx1, my1 in MAST_STUBS:
        arr[my0:my1, mx0:mx1, 3] = 0

    # 2. recolour the hull (brown -> white) within the hull band
    sub = arr[HULL_TOP_Y:HULL_BOTTOM_Y, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = rgb.mean(2)
    # brown/tan fill = warm, opaque; keep the dark outline (lum<90). Ceiling
    # raised to 238 so the bright deck-rail tan is also recoloured.
    brown = (a > 120) & (R - B > 12) & (lum > 90) & (lum < 238)
    for c in range(3):
        sub[..., c][brown] = HULL_WHITE[c]

    # red waterline stripe at a FIXED atlas-Y band (the porthole-scroll row),
    # independent of HULL_TOP_Y so it stays put when the band grows.
    STRIPE_Y0, STRIPE_Y1 = 2620, 2706
    h = sub.shape[0]
    yy = np.mgrid[0:h, 0:sub.shape[1]][0] + HULL_TOP_Y
    band = (yy >= STRIPE_Y0) & (yy < STRIPE_Y1)
    fill = (a > 120) & (lum > 90) & band
    for c in range(3):
        sub[..., c][fill] = STRIPE_RED[c]
    arr[HULL_TOP_Y:HULL_BOTTOM_Y, x0:x1] = sub

    Image.fromarray(arr, "RGBA").save(out)
    ktx_tools.encode(out, TEX)
    os.remove(out)
    print("speedboat: rig erased, hull recoloured white + red stripe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
