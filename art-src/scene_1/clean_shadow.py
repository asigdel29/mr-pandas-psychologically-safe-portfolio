"""Remove the orphaned dragon drop-shadow baked into scene_1_bg.

The diorama bakes soft grey drop-shadows onto the lined-paper BACK WALL. The
Chinese dragon is gone (its mesh is hidden), but its shadow lives in a different
atlas -- scene_1_bg -- so hiding the mesh left the shadow floating in the sky.

scene_1_bg is a tightly UV-packed sheet of WALL (light-blue lined paper) + GROUND
(muted green) panels. We must clear the shadow WITHOUT damaging the green ground.

Method (spec REBRAND_SPEC.md sec 5, option 1):
  * Classify shadow = greyish (low saturation), mid luminance, opaque, and NOT
    green. The wall is light-blue (B >= R); the ground is green (G > R and G > B)
    and is explicitly excluded.
  * Replace each shadow pixel with the PER-ROW MEDIAN of the bright clean wall
    paper in that same row. Ruling lines run horizontally, so the per-row paper
    tone is the right local fill; at worst a ruling line gets a hairline gap
    where a shadow crossed it -- invisible vs a grey blob.

Reproducible / idempotent: re-running on an already-clean atlas is a no-op
(there are no shadow pixels left to fill).

    TMPDIR=/private/tmp python3 clean_shadow.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

TEX = os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures",
                   "scene_1_bg.ktx2")

WALL_FALLBACK = (214, 226, 246)  # light-blue lined paper, if a row has no bright px


def _classify(arr):
    rgb = arr[..., :3].astype(int)
    a = arr[..., 3]
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lum = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    green = (G - R > 10) & (G - B > 10)              # ground panels -> protect
    shadow = (a > 120) & (lum >= 120) & (lum <= 205) & (sat < 40) & (~green)
    bright_wall = (a > 120) & (lum > 210) & (B >= R) & (~green)
    return shadow, green, bright_wall


def main() -> int:
    # Always start from the PRISTINE atlas so re-runs don't stack re-encodes.
    out = "/private/tmp/_bg.png"
    import subprocess
    repo = os.path.join(os.path.dirname(__file__), "..", "..")
    pristine = subprocess.check_output(
        ["git", "show", "b99508d:public/textures/scene_1_bg.ktx2"], cwd=repo)
    src_ktx = "/private/tmp/_bg_pristine.ktx2"
    with open(src_ktx, "wb") as fh:
        fh.write(pristine)
    ktx_tools.decode(src_ktx, out)
    os.remove(src_ktx)
    arr = np.array(Image.open(out).convert("RGBA"))

    shadow0, green, _ = _classify(arr)
    green_before = int(green.sum())
    shadow_before = int(shadow0.sum())

    rgb = arr[..., :3]
    H = arr.shape[0]
    # Iterate the per-row paper-median fill in-memory until no shadow remains
    # (filled pixels can re-classify as shadow if a row's median is dim; a few
    # passes converge). Encode ONCE at the end.
    for _ in range(8):
        shadow, _g, bright = _classify(arr)
        if not shadow.any():
            break
        rows = np.where(shadow.any(axis=1))[0]
        for y in rows:
            srow = shadow[y]
            brow = bright[y]
            if brow.sum() >= 8:
                med = np.median(rgb[y][brow], axis=0).astype(np.uint8)
                # guarantee the fill is bright enough to not re-classify as shadow
                if med.mean() < 208:
                    med = np.array(WALL_FALLBACK, np.uint8)
            else:
                med = np.array(WALL_FALLBACK, np.uint8)
            rgb[y][srow] = med

    Image.fromarray(arr, "RGBA").save(out)
    ktx_tools.encode(out, TEX)

    # --- numeric verification (image-Read is unreliable; trust the stats) ---
    chk = np.array(Image.open(out).convert("RGBA"))  # re-read the PNG we encoded
    shadow_after, green_after, _ = _classify(chk)
    os.remove(out)
    print(f"shadow_before={shadow_before} shadow_after={int(shadow_after.sum())}")
    print(f"green_before={green_before} green_after={int(green_after.sum())} "
          f"(must be ~equal -> ground untouched)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
