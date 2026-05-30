"""Patch the CURRENT scene_1 / not_waterfall atlases (operates in place).

Two late fixes after a render check:
  * not_waterfall: fully erase the remaining torii post (a tall salmon column
    in the lower-right the earlier boxes only partly caught).
  * scene_1: recolour the WHOLE light-blue bird into a Danphe (Himalayan Monal)
    using bbox-relative colour bands -- the earlier BIRD_BOX was too small so
    most of the bird stayed blue.

Run from art-src/scene_1 (uses /private/tmp for basisu scratch):
    TMPDIR=/private/tmp python3 patch_nepal.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

TEX = os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures")

# torii remnants to fully erase (alpha->0). The big post was already removed;
# these are the leftover dark crossbar + salmon stubs in the upper-left of the
# torii zone (x[2900,3080] y[40,600]) plus the earlier lower post box.
TORII_REMNANTS = [
    (3160, 2620, 3850, 3760),  # lower post (already cleared earlier; harmless)
    (2800, 0, 3120, 680),      # upper-left crossbar + salmon stubs (render #25/#27)
]

# the bird is now REMOVED entirely (user request #26): erase its whole bbox.
BIRD_BOX = (390, 690, 1270, 1300)


def patch_not_waterfall():
    p = os.path.join(TEX, "not_waterfall.ktx2")
    out = "/private/tmp/_nw.png"
    ktx_tools.decode(p, out)
    arr = np.array(Image.open(out).convert("RGBA"))
    for x0, y0, x1, y1 in TORII_REMNANTS:
        arr[y0:y1, x0:x1, 3] = 0
    Image.fromarray(arr, "RGBA").save(out)
    ktx_tools.encode(out, p)
    os.remove(out)
    print("patched not_waterfall: torii remnants erased")


def patch_scene_1():
    p = os.path.join(TEX, "scene_1.ktx2")
    out = "/private/tmp/_s1.png"
    ktx_tools.decode(p, out)
    arr = np.array(Image.open(out).convert("RGBA"))
    x0, y0, x1, y1 = BIRD_BOX
    arr[y0:y1, x0:x1, 3] = 0  # remove the bird entirely
    Image.fromarray(arr, "RGBA").save(out)
    ktx_tools.encode(out, p)
    os.remove(out)
    print("patched scene_1: bird removed")


def main() -> int:
    patch_not_waterfall()
    patch_scene_1()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
