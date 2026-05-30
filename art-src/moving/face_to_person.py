"""Turn the mascot panda's HEAD into anu's bearded face across every costume.

The mascot (Mr_Panda004) wears five costumes -- regular / samurai / pirate /
desert / zombie -- each a separate KTX2 atlas mapped to the SAME mesh, so the
head occupies the IDENTICAL UV region in all five. The panda is drawn lying
horizontally; its head is rotated 90 deg CW in the atlas. So we:

  1. Work in an UPRIGHT 1024x1024 frame (rotate the texture 90 deg CCW).
  2. Recolour the muzzle to skin, erase the panda eyes/nose/mouth, then draw the
     bearded face -- dark sunglasses, a big open grin with teeth, a full beard,
     and (only where no headgear covers the crown) a dark hair cap.
  3. Rotate back 90 deg CW and save.

The body + each costume's headgear (samurai helmet, pirate hat, desert wrap) are
left untouched; only the face oval is repainted. Feature coordinates are fixed
(measured once from the original clean panda) because the UVs are shared.

    python3 face_to_person.py <costume> <in.png> <out.png>
        costume in: regular samurai pirate desert zombie

Driver for all five lives in faces_all.py.
"""

from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageDraw

# ---- palette (flat paper-cutout doodle) -------------------------------------
INK = (48, 44, 44)
SKIN = (232, 196, 166)
SKIN_SHADOW = (206, 168, 138)
ZOMBIE_SKIN = (150, 178, 120)
ZOMBIE_SHADOW = (120, 150, 96)
HAIR = (43, 38, 40)
BEARD = (60, 50, 46)
GLASS = (38, 40, 46)
GLASS_HI = (188, 198, 208)
MOUTH_IN = (150, 74, 70)
TEETH = (246, 246, 242)

# ---- fixed face geometry in the upright 1024 frame --------------------------
CX = 612
EYE_Y = 533
EYE_L = (527, EYE_Y)
EYE_R = (672, EYE_Y)
LENS_W, LENS_H, LENS_R = 116, 74, 24
NOSE = (611, 578)
MOUTH = (611, 628)
MOUTH_W, MOUTH_H = 132, 58

COSTUMES = {
    # name: (skin, skin_shadow, draw_hair, face_is_green)
    "regular": (SKIN, SKIN_SHADOW, True, False),
    "samurai": (SKIN, SKIN_SHADOW, False, False),
    "pirate": (SKIN, SKIN_SHADOW, False, False),
    "desert": (SKIN, SKIN_SHADOW, False, False),
    "zombie": (ZOMBIE_SKIN, ZOMBIE_SHADOW, True, True),
}


def to_upright(img: Image.Image) -> Image.Image:
    return img.rotate(90, expand=True)


def back(img: Image.Image) -> Image.Image:
    return img.rotate(-90, expand=True)


def _ellipse_mask(shape, cx, cy, rx, ry) -> np.ndarray:
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    return ((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2 <= 1.0


def paint_face(costume: str, in_png: str, out_png: str) -> None:
    skin, shadow, draw_hair, green = COSTUMES[costume]
    src = Image.open(in_png).convert("RGBA")
    up = to_upright(src)
    arr = np.array(up)
    rgb = arr[..., :3].astype(np.int16)
    a = arr[..., 3]

    # --- skin fill: recolour the muzzle (white face, or green for zombie) ----
    # Restrict to a face oval so costume headgear (skull, wrap, helmet) outside
    # the oval is preserved.
    face_oval = _ellipse_mask(a.shape, CX, 528, 196, 188)
    crown = np.zeros(a.shape, bool)
    crown[0:430, :] = True  # headgear zone above the brow; never skin-fill here
    skinnable = face_oval & ~crown & (a > 120)
    if green:
        face_px = (rgb[..., 1] - rgb[..., 0] > 8) & (rgb[..., 1] - rgb[..., 2] > 8)
    else:
        face_px = rgb.min(2) > 178
    fill = skinnable & face_px
    for c in range(3):
        arr[..., c][fill] = skin[c]

    # --- erase old panda eyes / nose / mouth (dark marks inside the face) -----
    inner = _ellipse_mask(a.shape, CX, 552, 150, 132)
    dark = (rgb.max(2) < 96) & (a > 120) & inner
    # for zombie the marks (stitches, red eyes, mouth) are not all dark:
    if green:
        reddish = (rgb[..., 0] - rgb[..., 1] > 12) & (a > 120) & inner
        dark = dark | reddish
    for c in range(3):
        arr[..., c][dark] = skin[c]

    img = Image.fromarray(arr, "RGBA")
    head_alpha = a > 80  # clip everything to the original head silhouette

    # --- hair cap (only when nothing covers the crown) -----------------------
    if draw_hair:
        hair = Image.new("RGBA", img.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hair)
        # short rounded crown -- leaves the forehead visible below the hairline
        hd.rounded_rectangle([478, 360, 748, 452], radius=58, fill=HAIR)
        # a soft side-swept fringe dipping just below the hairline
        hd.polygon([(478, 446), (532, 472), (590, 450), (612, 470),
                    (664, 448), (716, 470), (748, 446)], fill=HAIR)
        # short sideburns connecting hair to beard at the temples
        hd.line([(492, 452), (492, 560)], fill=HAIR, width=22)
        hd.line([(734, 452), (734, 560)], fill=HAIR, width=22)
        ha = np.array(hair)
        ha[..., 3] = np.where(head_alpha, ha[..., 3], 0)
        img = Image.alpha_composite(img, Image.fromarray(ha, "RGBA"))

    # --- beard: framing the jaw/chin, cheeks + mouth left open ---------------
    beard = Image.new("RGBA", img.size, (0, 0, 0, 0))
    bd = ImageDraw.Draw(beard)
    bd.pieslice([454, 548, 770, 722], start=6, end=174, fill=BEARD)
    # thin sideburns climbing toward the glasses (kept narrow so cheeks show)
    bd.polygon([(470, 700), (486, 556), (512, 566), (506, 700)], fill=BEARD)
    bd.polygon([(754, 700), (738, 556), (712, 566), (718, 700)], fill=BEARD)
    ba = np.array(beard)
    ba[..., 3] = np.where(head_alpha, ba[..., 3], 0)
    # carve the mouth opening out of the beard
    hole = Image.new("L", img.size, 0)
    ImageDraw.Draw(hole).ellipse(
        [CX - MOUTH_W // 2 - 8, MOUTH[1] - MOUTH_H // 2 - 6,
         CX + MOUTH_W // 2 + 8, MOUTH[1] + MOUTH_H // 2 + 14], fill=255)
    ba[..., 3] = np.where(np.array(hole) > 0, 0, ba[..., 3])
    img = Image.alpha_composite(img, Image.fromarray(ba, "RGBA"))

    d = ImageDraw.Draw(img)

    # --- nose (subtle) -------------------------------------------------------
    d.line([(CX - 3, NOSE[1] - 30), (CX - 9, NOSE[1])], fill=shadow, width=7)
    d.line([(CX - 9, NOSE[1]), (CX + 9, NOSE[1] + 2)], fill=shadow, width=7)

    # --- big open grin: dark interior, white upper teeth, ink outline --------
    mx0, my0 = CX - MOUTH_W // 2, MOUTH[1] - MOUTH_H // 2
    mx1, my1 = CX + MOUTH_W // 2, MOUTH[1] + MOUTH_H // 2
    d.chord([mx0, my0, mx1, my1 + 10], start=0, end=360, fill=MOUTH_IN, outline=INK, width=8)
    # upper teeth band
    teeth = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(teeth).pieslice([mx0 + 6, my0 + 4, mx1 - 6, my1 + 4],
                                   start=182, end=358, fill=(*TEETH, 255))
    tmask = Image.new("L", img.size, 0)
    ImageDraw.Draw(tmask).rectangle([mx0, my0, mx1, MOUTH[1]], fill=255)
    ta = np.array(teeth)
    ta[..., 3] = np.where(np.array(tmask) > 0, ta[..., 3], 0)
    img = Image.alpha_composite(img, Image.fromarray(ta, "RGBA"))
    d = ImageDraw.Draw(img)
    # tooth gap lines
    for tx in (CX - 28, CX, CX + 28):
        d.line([(tx, my0 + 8), (tx, MOUTH[1] - 2)], fill=(210, 210, 206), width=3)
    # mustache hint just above the grin
    d.line([(CX - 40, my0 - 4), (CX, my0 + 6)], fill=BEARD, width=12)
    d.line([(CX + 40, my0 - 4), (CX, my0 + 6)], fill=BEARD, width=12)

    # --- sunglasses: dark rounded lenses + bridge + temples ------------------
    def lens(c):
        x, y = c
        box = [x - LENS_W // 2, y - LENS_H // 2, x + LENS_W // 2, y + LENS_H // 2]
        d.rounded_rectangle(box, radius=LENS_R, fill=GLASS, outline=INK, width=6)
        # glossy highlight streak
        d.line([(x - LENS_W // 2 + 16, y + LENS_H // 2 - 12),
                (x - LENS_W // 2 + 40, y - LENS_H // 2 + 12)],
               fill=GLASS_HI, width=7)

    lens(EYE_L)
    lens(EYE_R)
    # bridge
    d.line([(EYE_L[0] + LENS_W // 2 - 6, EYE_Y - 8),
            (EYE_R[0] - LENS_W // 2 + 6, EYE_Y - 8)], fill=INK, width=10)
    # temples toward the ears
    d.line([(EYE_L[0] - LENS_W // 2, EYE_Y - LENS_H // 2 + 10),
            (452, EYE_Y - LENS_H // 2 - 6)], fill=INK, width=9)
    d.line([(EYE_R[0] + LENS_W // 2, EYE_Y - LENS_H // 2 + 10),
            (792, EYE_Y - LENS_H // 2 - 6)], fill=INK, width=9)
    # brows above the glasses for a touch of expression
    d.line([(EYE_L[0] - 40, EYE_Y - LENS_H // 2 - 14),
            (EYE_L[0] + 40, EYE_Y - LENS_H // 2 - 20)], fill=HAIR, width=10)
    d.line([(EYE_R[0] - 40, EYE_Y - LENS_H // 2 - 20),
            (EYE_R[0] + 40, EYE_Y - LENS_H // 2 - 14)], fill=HAIR, width=10)

    # clip any overspill back to the head silhouette
    out_arr = np.array(img)
    out_arr[..., 3] = np.where(head_alpha, out_arr[..., 3], a)
    img = Image.fromarray(out_arr, "RGBA")

    back(img).save(out_png)
    print(f"face[{costume}]: {in_png} -> {out_png}")


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in COSTUMES:
        print("usage: python3 face_to_person.py <costume> <in.png> <out.png>")
        print("costume:", ", ".join(COSTUMES))
        return 2
    paint_face(argv[1], argv[2], argv[3])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
