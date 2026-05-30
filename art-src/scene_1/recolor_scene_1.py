"""Procedural cool-blue reskin for the Scene One (Roots / Nepal) atlas.

This is a *colour* reskin only: it recolours pixels inside the existing paper
silhouettes (red Chinese dragon -> turquoise Himalayan "Druk" dragon, warm
cream paper/sky -> cool blue). It cannot change shapes -- turning the dragon
into a yak, or swapping the lantern for a stupa, needs a Blender geometry edit
and a re-bake. The cut-out alpha mask is preserved untouched so geometry/UVs
and all the JSX mesh code stay valid.

Pipeline (see ../ktx_tools.py):
    python3 ../ktx_tools.py decode <atlas>.ktx2 <name>_base.png
    python3 recolor_scene_1.py <name>_base.png <name>_painted.png
    python3 ../ktx_tools.py encode <name>_painted.png <atlas>.ktx2

All knobs are constants below; tweak and re-run after eyeballing in Chrome.
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image

# --- tunables ----------------------------------------------------------------
# PIL "HSV" mode stores H,S,V each as 0..255 (H: 0..255 == 0..360 degrees).

# Warm hues to recolour: reds/oranges/yellows wrap around 0. ~0..45deg + ~330..360deg.
WARM_LOW = 32      # <= ~45 degrees  (red, orange, warm yellow)
WARM_HIGH = 235    # >= ~331 degrees (deep red / magenta-red)

# Only recolour pixels that are actually coloured (not the near-grey linework).
SAT_FLOOR = 45

# Target hue for the recoloured warm pixels: turquoise/teal (~183 degrees).
TEAL_H = 130

# Whole-atlas cooling for the cream paper + warm sky: nudge channels cool.
# Multiplies linear-ish 8-bit RGB; keeps linework/value, shifts the white point.
COOL_R = 0.92
COOL_G = 0.99
COOL_B = 1.08
# -----------------------------------------------------------------------------


def recolor(in_png: str, out_png: str) -> None:
    src = Image.open(in_png).convert("RGBA")
    rgb = src.convert("RGB")
    alpha = np.asarray(src.split()[-1])  # preserve cut-out mask exactly

    hsv = np.asarray(rgb.convert("HSV")).astype(np.int16)
    h, s = hsv[..., 0], hsv[..., 1]

    warm = ((h <= WARM_LOW) | (h >= WARM_HIGH)) & (s >= SAT_FLOOR)
    hsv[..., 0] = np.where(warm, TEAL_H, h)
    hsv = np.clip(hsv, 0, 255).astype(np.uint8)

    cooled = Image.fromarray(hsv, mode="HSV").convert("RGB")
    arr = np.asarray(cooled).astype(np.float32)
    arr[..., 0] *= COOL_R
    arr[..., 1] *= COOL_G
    arr[..., 2] *= COOL_B
    arr = np.clip(arr, 0, 255).astype(np.uint8)

    out = np.dstack([arr, alpha])
    Image.fromarray(out, mode="RGBA").save(out_png)
    pct = 100.0 * float(warm.mean())
    print(f"recoloured {in_png} -> {out_png} (warm pixels remapped: {pct:.1f}%)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 recolor_scene_1.py <in.png> <out.png>")
        return 2
    recolor(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
