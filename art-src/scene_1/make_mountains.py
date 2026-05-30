"""Draw a panoramic Himalayan range texture for the Scene One backdrop.

Overlapping snow-capped peaks in the flat paper-cutout doodle style (dark wobbly
outline, white snow, blue-grey rock). Transparent sky above; the lower strip is
opaque rock so the range reads as rising from behind the ground. Sits on a wide
plane behind the scenery in SceneOne.jsx.

    python3 make_mountains.py mountains.png
    python3 ../ktx_tools.py encode mountains.png ../../public/textures/mountains.ktx2
"""

from __future__ import annotations

import math
import sys

from PIL import Image, ImageDraw

W, H = 4096, 1024
INK = (70, 74, 84)
ROCK_HI = (150, 166, 188)
ROCK_LO = (112, 128, 152)
SNOW = (242, 246, 252)
SNOW_SHADE = (214, 224, 238)

# (centre x-fraction, peak height-fraction from top, half-width-fraction)
PEAKS = [
    (0.07, 0.46, 0.16), (0.20, 0.30, 0.18), (0.34, 0.52, 0.15),
    (0.46, 0.22, 0.20), (0.60, 0.40, 0.17), (0.72, 0.30, 0.19),
    (0.85, 0.48, 0.16), (0.96, 0.34, 0.15),
]


def make(out_png: str) -> None:
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    base = H  # peaks sit on the bottom edge

    # back-to-front so nearer peaks overlap farther ones
    order = sorted(PEAKS, key=lambda p: -p[1])
    for cx_f, peak_f, hw_f in order:
        cx = cx_f * W
        peak_y = peak_f * H
        hw = hw_f * W
        rock = ROCK_LO if peak_f > 0.4 else ROCK_HI
        # mountain body (triangle to the base)
        d.polygon([(cx - hw, base), (cx, peak_y), (cx + hw, base)],
                  fill=rock, outline=INK)
        # snow cap: a smaller triangle near the summit with a jagged lower edge
        snow_h = peak_y + (base - peak_y) * 0.32
        sl = cx - hw * 0.34
        sr = cx + hw * 0.34
        jag = [(cx, peak_y)]
        steps = 7
        for k in range(steps + 1):
            t = k / steps
            x = sl + (sr - sl) * t
            wob = 18 * math.sin(t * math.pi * 3)
            jag.append((x, snow_h + wob))
        d.polygon(jag + [(cx, peak_y)], fill=SNOW)
        # a soft shade line down one flank of the snow
        d.line([(cx, peak_y), (cx + hw * 0.12, snow_h)], fill=SNOW_SHADE,
               width=6)
        # re-stroke the summit outline for the doodle look
        d.line([(cx - hw, base), (cx, peak_y), (cx + hw, base)], fill=INK,
               width=6, joint="curve")

    img.save(out_png)
    print(f"mountains -> {out_png} ({len(PEAKS)} peaks)")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python3 make_mountains.py <out.png>")
        return 2
    make(argv[1])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
