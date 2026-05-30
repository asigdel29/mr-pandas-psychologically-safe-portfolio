"""Re-theme the Scene One scene_1 atlas toward Nepal: rhododendron blossoms.

scene_1 holds the dragon, the blossom tree, scattered blossoms, grass, clouds
and small lanterns. This first pass recolours the cherry blossoms (the scattered
clusters + the tree canopy) to red rhododendron, leaving the smiling clouds, the
trunk and the dragon untouched. (The dragon transform + lantern->chorten come in
a later pass.)

    python3 nepalize_scene_1.py <in.png> <out.png>
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

# The cherry-blossom 5-petal flowers live in a strip across the top of the atlas
# (the tree + scattered blooms sample these). Everything here sits on identical
# notebook paper, so colour can't separate blossoms from the smiling cloud or
# the cyan face-daisy -- we take the strip and cut out those two regions.
BLOSSOM_STRIP = (80, 10, 2350, 440)
NOT_BLOSSOM = [(1000, 290, 1600, 800),   # top of the centre smiling cloud
               (1950, 40, 2270, 370)]    # the cyan face-daisy


# The light-blue bird -> a Danphe (Himalayan Monal), Nepal's national bird:
# green head/crest, copper back, blue-green wing, dark belly.
BIRD_BOX = (555, 815, 1015, 1170)


def _danphe(arr):
    x0, y0, x1, y1 = BIRD_BOX
    sub = arr[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]
    lum = rgb.mean(2)
    cyan = (a > 120) & (rgb[..., 2] - rgb[..., 0] > 4) & (lum > 120) & (lum < 236)
    h, w = cyan.shape
    yy, xx = np.mgrid[0:h, 0:w]
    ax, ay = xx + x0, yy + y0
    head = (ay < 1015) & (ax < 785)
    wing = ~head & (ax > 835)
    belly = ~head & ~wing & (ay > 1035)
    back = ~head & ~wing & ~belly
    for region, col in [(head, (40, 135, 75)), (back, (196, 100, 40)),
                        (wing, (38, 120, 165)), (belly, (140, 60, 35))]:
        m = region & cyan
        for c in range(3):
            sub[..., c][m] = col[c]
    arr[y0:y1, x0:x1] = sub


def _to_rhododendron(arr, mask):
    rgb = arr[..., :3].astype(np.int16)
    lum = rgb.mean(2)
    t = np.clip((lum - 150) / 105.0, 0, 1)  # dim..bright -> deep..light red
    arr[..., 0][mask] = (176 + t * 62).astype(np.uint8)[mask]
    arr[..., 1][mask] = (40 + t * 64).astype(np.uint8)[mask]
    arr[..., 2][mask] = (50 + t * 60).astype(np.uint8)[mask]


def nepalize(in_png: str, out_png: str) -> None:
    img = Image.open(in_png).convert("RGBA")
    arr = np.array(img)
    rgb = arr[..., :3].astype(np.int16)
    a = arr[..., 3]
    H, W = a.shape

    # blossom strip minus the cloud/daisy cut-outs
    bx0, by0, bx1, by1 = BLOSSOM_STRIP
    region = np.zeros((H, W), bool)
    region[by0:by1, bx0:bx1] = True
    for x0, y0, x1, y1 in NOT_BLOSSOM:
        region[y0:y1, x0:x1] = False
    # light petals (keep the dark outline); a green guard skips grass blades.
    green = (rgb[..., 1] - rgb[..., 0] > 25) & (rgb[..., 1] - rgb[..., 2] > 25)
    petal = region & (a > 150) & (rgb.mean(2) > 150) & ~green

    _to_rhododendron(arr, petal)
    _danphe(arr)
    Image.fromarray(arr, "RGBA").save(out_png)
    print(f"nepalized scene_1 (rhododendron {int(petal.sum())} px): "
          f"{in_png} -> {out_png}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 nepalize_scene_1.py <in.png> <out.png>")
        return 2
    nepalize(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
