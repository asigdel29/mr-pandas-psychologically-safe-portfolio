"""Erase the orphaned dragon drop-shadow baked into the scene_1_bg wall.

The diorama bakes soft grey drop-shadows onto the lined-paper back wall. With the
Chinese dragon removed, its large shadow is left floating. We replace the shadow
pixels (grey, darker than the pale wall, but not the dark ruling lines/marker)
with each row's base wall colour -- since the ruling lines run horizontally, the
per-row base preserves them, leaving no visible patch. Cloud shadows outside the
band are kept (their clouds still exist).

    python3 ../ktx_tools.py decode ../../public/textures/scene_1_bg.ktx2 bg.png
    python3 clean_shadow.py bg.png bg_clean.png
    python3 ../ktx_tools.py encode bg_clean.png ../../public/textures/scene_1_bg.ktx2
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

# atlas band holding the dragon shadow (clear of the cloud shadow above y560)
BAND = (150, 560, 2090, 1360)


def clean(in_png: str, out_png: str) -> None:
    arr = np.array(Image.open(in_png).convert("RGBA"))
    x0, y0, x1, y1 = BAND
    sub = arr[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.float32)
    a = sub[..., 3]
    lum = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    shadow = (lum < 206) & (lum > 110) & (sat < 46) & (a > 120)
    bright = (lum >= 200) & (a > 120)
    for j in range(sub.shape[0]):
        br = bright[j]
        base = (np.median(sub[j, :, :3][br], axis=0)
                if br.sum() > 20 else np.array([214, 226, 246]))
        sh = shadow[j]
        for c in range(3):
            sub[j, :, c][sh] = base[c]
    arr[y0:y1, x0:x1] = sub
    Image.fromarray(arr, "RGBA").save(out_png)
    print(f"cleaned dragon shadow: {in_png} -> {out_png} "
          f"({int(shadow.sum())} px)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 clean_shadow.py <in.png> <out.png>")
        return 2
    clean(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
