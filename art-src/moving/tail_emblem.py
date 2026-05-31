"""Paint a yellow Himalayan-peak emblem on the plane's navy tail fin.

plane_livery.py deferred the tail-fin emblem ("the fin is a thin diagonal that's
hard to place without a live render"). With the plane livery already baked, this
adds JUST the emblem as a small, localised, idempotent edit -- a flat yellow
twin-peak motif (the Kathmandu Air / Himalaya read) clipped to the navy fin so
it can never spill onto the sky or the white fuselage.

This operates IN PLACE on the CURRENT Moving_extras (which already carries the
speedboat + plane livery). It does NOT restore pristine -- doing so would wipe
that baked work. Re-running is safe: the emblem is redrawn in the same spot, and
because it only paints over navy it self-limits.

    TMPDIR=/private/tmp python3 tail_emblem.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

TEX = os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures",
                   "Moving_extras.ktx2")

YELLOW = (240, 196, 40)
NAVY = (32, 52, 120)

# The navy tail fin (upper-left of the plane island). Emblem is centred here and
# hard-clipped to the navy pixels inside this box.
FIN_BOX = (2600, 2330, 2770, 2580)   # x0, y0, x1, y1


def _navy_mask(arr):
    rgb = arr[..., :3].astype(int)
    a = arr[..., 3]
    R, B = rgb[..., 0], rgb[..., 2]
    lum = rgb.mean(2)
    return (a > 120) & (B - R > 30) & (lum < 120) & (lum > 20)


def main() -> int:
    out = "/private/tmp/_emblem.png"
    ktx_tools.decode(TEX, out)
    img = Image.open(out).convert("RGBA")
    arr = np.array(img)

    x0, y0, x1, y1 = FIN_BOX
    navy_before = int(_navy_mask(arr)[y0:y1, x0:x1].sum())

    # Draw the twin-peak emblem on a scratch layer, then composite only where
    # the fin is navy.
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx = (x0 + x1) // 2
    base_y = y1 - 30
    # two overlapping flat triangles (a back peak + a taller front peak)
    d.polygon([(cx - 70, base_y), (cx - 18, base_y - 120), (cx + 26, base_y)],
              fill=(*YELLOW, 255))
    d.polygon([(cx - 20, base_y), (cx + 34, base_y - 150), (cx + 84, base_y)],
              fill=(*YELLOW, 255))
    # a thin snow-cap notch on the taller peak, in navy, for a paper-cutout read
    d.polygon([(cx + 22, base_y - 96), (cx + 34, base_y - 150),
               (cx + 47, base_y - 96)], fill=(*NAVY, 255))

    layer_arr = np.array(layer)
    # clip the emblem to navy fin pixels only (never onto sky / white fuselage)
    clip = np.zeros(arr.shape[:2], bool)
    clip[y0:y1, x0:x1] = _navy_mask(arr)[y0:y1, x0:x1]
    # also allow the snow-cap navy notch (it sits inside the yellow, so re-allow
    # pixels the emblem itself drew) -- simplest: allow emblem where clip OR the
    # pixel is already navy. Since the whole fin under the emblem is navy, clip
    # already covers it.
    layer_arr[..., 3] = np.where(clip, layer_arr[..., 3], 0)

    img = Image.alpha_composite(img, Image.fromarray(layer_arr, "RGBA"))
    img.save(out)
    ktx_tools.encode(out, TEX)

    chk = np.array(Image.open(out).convert("RGBA"))
    rgb = chk[..., :3].astype(int)
    yellow_in_box = int(((np.abs(rgb[y0:y1, x0:x1] - np.array(YELLOW)).sum(2)
                          < 60)).sum())
    os.remove(out)
    print(f"tail emblem: navy_fin_px_before={navy_before}")
    print(f"yellow_emblem_px_in_fin={yellow_in_box} (0 = nothing painted -> "
          f"check FIN_BOX vs the navy fin location)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
