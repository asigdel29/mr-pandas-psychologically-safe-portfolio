"""Turn the mascot panda's HEAD into a human face (glasses + beard), body kept.

Only the regular costume (regular.ktx2, 1024x1024) is changed, per the user's
choice. The panda is drawn lying horizontally; its head is the white round on
the right and is rotated 90 deg CW in the atlas (viewing it rotated CCW shows it
upright). So we:

  1. Work in an UPRIGHT frame: rotate the whole texture 90 deg CCW.
  2. In that frame, repaint the face -- skin fill over the white muzzle, erase
     the panda eyes/nose, then draw hair, round glasses, eyes and a full beard
     in the flat paper-cutout doodle style.
  3. Rotate back 90 deg CW and save.

Keeping the black ears + round body untouched preserves the "little character"
read the user asked for.

    python3 ../ktx_tools.py decode ../../public/textures/regular.ktx2 regular_base.png
    python3 face_to_person.py regular_base.png regular_person.png
    python3 ../ktx_tools.py encode regular_person.png ../../public/textures/regular.ktx2
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageDraw

# Doodle palette (flat, matches the hand-drawn cutout look).
INK = (60, 60, 60)
SKIN = (235, 200, 170)
SKIN_SHADOW = (216, 178, 150)
HAIR = (54, 44, 40)
BEARD = (74, 60, 52)
LENS = (250, 250, 250)


def to_upright(img: Image.Image) -> Image.Image:
    return img.rotate(90, expand=True)  # CCW -> head upright


def back(img: Image.Image) -> Image.Image:
    return img.rotate(-90, expand=True)


def person_face(in_png: str, out_png: str) -> None:
    src = Image.open(in_png).convert("RGBA")
    up = to_upright(src)
    arr = np.array(up)
    H, W = arr.shape[:2]
    rgb = arr[..., :3].astype(np.int16)
    a = arr[..., 3]

    # --- locate the head muzzle (big white region in the upright frame) ---
    white = (rgb.min(2) > 180) & (a > 120)
    ys, xs = np.where(white)
    # The head sits in the upper portion of the upright image; restrict to the
    # largest white blob there.
    hx0, hx1 = int(np.percentile(xs, 2)), int(np.percentile(xs, 98))
    hy0, hy1 = int(ys.min()), int(np.percentile(ys, 60))
    cx = (hx0 + hx1) // 2
    cy = (hy0 + hy1) // 2
    fw = hx1 - hx0
    fh = hy1 - hy0

    # --- skin fill: recolour the white muzzle pixels to skin ---
    muzzle = np.zeros((H, W), bool)
    muzzle[hy0:hy1 + int(0.15 * fh), hx0:hx1] = True
    skin_mask = white & muzzle
    arr[..., 0][skin_mask] = SKIN[0]
    arr[..., 1][skin_mask] = SKIN[1]
    arr[..., 2][skin_mask] = SKIN[2]

    # --- erase the panda eyes/nose (dark marks inside the muzzle) ---
    interior = np.zeros((H, W), bool)
    interior[hy0 + int(0.15 * fh):hy1 + int(0.12 * fh),
             hx0 + int(0.12 * fw):hx1 - int(0.12 * fw)] = True
    dark = (rgb.max(2) < 110) & (a > 120) & interior
    for c in range(3):
        arr[..., c][dark] = (SKIN, SKIN, SKIN)[0][c] if False else SKIN[c]

    img = Image.fromarray(arr, "RGBA")
    d = ImageDraw.Draw(img)

    # geometry of the human features, derived from the muzzle box
    eye_y = cy + int(0.02 * fh)
    eye_dx = int(0.20 * fw)
    eye_r = max(10, int(0.085 * fw))
    lx, rx = cx - eye_dx, cx + eye_dx

    # --- hair: a soft doodle cap across the top of the head ---
    hair_top = hy0 - int(0.04 * fh)
    hair_bot = cy - int(0.22 * fh)
    d.rounded_rectangle([hx0 + int(0.02 * fw), hair_top,
                         hx1 - int(0.02 * fw), hair_bot],
                        radius=int(0.18 * fw), fill=HAIR)
    # a couple of fringe strokes
    for i in range(5):
        fx = hx0 + int((0.18 + i * 0.16) * fw)
        d.line([(fx, hair_bot - 6), (fx + 8, hair_bot + int(0.10 * fh))],
               fill=HAIR, width=10)

    # --- round glasses: two lenses + bridge + temples ---
    lw = max(6, int(0.022 * fw))
    for ex in (lx, rx):
        d.ellipse([ex - eye_r - 6, eye_y - eye_r - 6,
                   ex + eye_r + 6, eye_y + eye_r + 6], fill=LENS, outline=INK,
                  width=lw)
    d.line([(lx + eye_r, eye_y), (rx - eye_r, eye_y)], fill=INK, width=lw)
    d.line([(lx - eye_r - 6, eye_y), (hx0, eye_y - int(0.04 * fh))],
           fill=INK, width=lw)
    d.line([(rx + eye_r + 6, eye_y), (hx1, eye_y - int(0.04 * fh))],
           fill=INK, width=lw)
    # eyes (dots behind the lenses)
    for ex in (lx, rx):
        d.ellipse([ex - 7, eye_y - 7, ex + 7, eye_y + 7], fill=INK)

    # --- nose ---
    ny = eye_y + int(0.14 * fh)
    d.line([(cx, eye_y + 10), (cx, ny)], fill=INK, width=max(5, lw - 2))

    # --- full beard: doodle fill around the lower face ---
    beard_top = ny - int(0.02 * fh)
    beard = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(beard)
    bd.pieslice([hx0 - int(0.02 * fw), beard_top - int(0.30 * fh),
                 hx1 + int(0.02 * fw), beard_top + int(0.55 * fh)],
                start=8, end=172, fill=BEARD)
    # mustache hint
    bd.line([(cx - int(0.12 * fw), ny + 6), (cx + int(0.12 * fw), ny + 6)],
            fill=BEARD, width=14)
    # keep beard only where the original head was opaque (don't spill off-face)
    headmask = (np.array(img)[..., 3] > 80)
    ba = np.array(beard)
    ba[..., 3] = np.where(headmask, ba[..., 3], 0)
    # leave a mouth gap: clear a small ellipse
    bd2 = Image.new("L", img.size, 0)
    ImageDraw.Draw(bd2).ellipse([cx - int(0.07 * fw), ny + 4,
                                 cx + int(0.07 * fw), ny + int(0.10 * fh)],
                                fill=255)
    gap = np.array(bd2) > 0
    ba[..., 3] = np.where(gap, 0, ba[..., 3])
    img = Image.alpha_composite(img, Image.fromarray(ba, "RGBA"))

    # smile line in the mouth gap
    d = ImageDraw.Draw(img)
    d.arc([cx - int(0.06 * fw), ny + 2, cx + int(0.06 * fw), ny + int(0.11 * fh)],
          start=20, end=160, fill=INK, width=6)

    out = back(img)
    out.save(out_png)
    print(f"person face: {in_png} -> {out_png} "
          f"(muzzle box x[{hx0},{hx1}] y[{hy0},{hy1}] upright)")


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print("usage: python3 face_to_person.py <in.png> <out.png>")
        return 2
    person_face(argv[1], argv[2])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
