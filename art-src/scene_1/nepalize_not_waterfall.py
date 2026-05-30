"""Re-theme the Scene One not_waterfall atlas toward Nepal.

This atlas holds the torii gate, the red pagoda, the cherry-blossom branches and
the stone lanterns (plus anu's text labels, left untouched). We:

  * recolour cherry blossoms -> red rhododendron (Nepal's national flower)
  * erase the torii gate ("the door") and the pagoda ("the temple") -- the
    not_waterfall mesh is a single cut-out plane, so clearing a region's alpha
    makes that element vanish in 3-D. Their baked wall shadows are removed
    separately in scene_1_bg.

Run (input must be the atlas that already carries anu's text):
    python3 nepalize_not_waterfall.py <in.png> <out.png>
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

# Elements to delete (atlas px boxes), alpha -> 0. The torii is a crossbar (kept
# clear of the right-side blossoms, which sit below y~600) plus tall posts.
ERASE_BOXES = [
    (0, 2360, 1300, 4096),    # pagoda
    (3040, 10, 4096, 560),    # torii crossbar (above the blossoms)
    (3040, 560, 3720, 1500),  # torii posts
    (3760, 2850, 4096, 3900),  # torii post island (bottom-right, salmon)
    (3240, 2820, 3800, 3500),  # second torii post island (salmon)
]


def nepalize(in_png: str, out_png: str) -> None:
    img = Image.open(in_png).convert("RGBA")
    arr = np.array(img)

    # --- rhododendron blossoms (petals are the only bright warm opaque pixels) -
    rgb = arr[..., :3].astype(np.int16)
    a = arr[..., 3]
    petal = (a > 150) & (rgb.min(2) > 198) & (rgb[..., 0] >= rgb[..., 2] - 6)
    lum = rgb.mean(2)
    t = np.clip((lum - 198) / 57.0, 0, 1)
    arr[..., 0][petal] = (180 + t * 60).astype(np.uint8)[petal]
    arr[..., 1][petal] = (38 + t * 70).astype(np.uint8)[petal]
    arr[..., 2][petal] = (48 + t * 72).astype(np.uint8)[petal]

    # --- delete the torii gate + pagoda ---
    for x0, y0, x1, y1 in ERASE_BOXES:
        arr[y0:y1, x0:x1, 3] = 0

    Image.fromarray(arr, "RGBA").save(out_png)
    print(f"nepalized not_waterfall (rhododendron + removed gate/temple): "
          f"{in_png} -> {out_png}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 nepalize_not_waterfall.py <in.png> <out.png>")
        return 2
    nepalize(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
