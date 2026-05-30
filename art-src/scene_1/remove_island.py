"""Remove the pirate palm-tree island (palm + sandy mound + treasure chest +
lock) from the scene_2 atlas by clearing its alpha. The scene_2 meshes are
cut-out planes, so a transparent atlas region makes the island vanish in 3-D.
The pufferfish (x>=3180) and dolphin (x>=3250) are left intact.

    python3 ../ktx_tools.py decode ../../public/textures/scene_2.ktx2 s2.png
    python3 remove_island.py s2.png s2_out.png
    python3 ../ktx_tools.py encode s2_out.png ../../public/textures/scene_2.ktx2
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

ERASE_BOXES = [
    (2540, 120, 3170, 790),    # palm crown + trunk
    (2560, 800, 3245, 1370),   # sandy mound + treasure chest + lock
]


def remove(in_png: str, out_png: str) -> None:
    arr = np.array(Image.open(in_png).convert("RGBA"))
    for x0, y0, x1, y1 in ERASE_BOXES:
        arr[y0:y1, x0:x1, 3] = 0
    Image.fromarray(arr, "RGBA").save(out_png)
    print(f"removed island: {in_png} -> {out_png}")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 remove_island.py <in.png> <out.png>")
        return 2
    remove(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
