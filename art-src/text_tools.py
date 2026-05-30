"""Replace baked handwritten text in the diorama atlases with lorem ipsum.

The portfolio's in-world copy (welcome blurb, about paragraph, job cards,
publication cards, sticky notes) is painted directly into the KTX2 texture
atlases, not stored as DOM/canvas text. To re-letter it we decode an atlas to
RGBA (see ktx_tools.py), rewrite each text region here, and re-encode.

Two region kinds, because the originals come in two flavours:

  * FLOATING ink -- handwriting drawn straight on the paper wall on an
    otherwise transparent plane (e.g. the "Welcome to my portfolio" and
    "I am a human researcher" labels). Erase = clear alpha in the box; the new
    letters are opaque dark ink, so only glyph pixels become visible again.

  * CARD ink -- handwriting on an opaque paper card (job/publication cards).
    Erase = repaint the card interior with its own paper colour while keeping
    the alpha (preserves the card silhouette + torn border); then letter on top.

Region pixel boxes come from the real GLB/Blender UVs (x = u*W, y = v*H for the
no-flip atlases; callers pass already-resolved pixel boxes). Glyphs use the
system Bradley Hand Bold to match the original hand-drawn feel.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf"

# Reusable lorem ipsum sentences; callers pick how many lines a region wants.
LOREM = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris. "
    "Duis aute irure dolor in reprehenderit in voluptate velit esse."
)

INK = (74, 74, 74)  # matches the originals' soft graphite, not pure black


@dataclass
class Region:
    """One text area to rewrite, in atlas pixel coordinates."""

    box: tuple[int, int, int, int]  # (x0, y0, x1, y1)
    kind: str = "floating"  # "floating" | "card"
    text: str = LOREM
    font_px: int = 0  # 0 => auto from box height
    rotate: int = 0  # degrees CCW, for sideways cards
    pad: int = 18
    ink: tuple[int, int, int] = INK
    name: str = ""


def _dilate(mask: np.ndarray, radius: int) -> np.ndarray:
    """Grow a boolean mask by ``radius`` px (square), numpy-only (no scipy)."""
    out = mask.copy()
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dy == 0 and dx == 0:
                continue
            shifted = np.zeros_like(mask)
            ys = slice(max(0, dy), mask.shape[0] + min(0, dy))
            xs = slice(max(0, dx), mask.shape[1] + min(0, dx))
            sy = slice(max(0, -dy), mask.shape[0] + min(0, -dy))
            sx = slice(max(0, -dx), mask.shape[1] + min(0, -dx))
            shifted[ys, xs] = mask[sy, sx]
            out |= shifted
    return out


def _paper_colour(rgba: np.ndarray, box: tuple[int, int, int, int]) -> tuple[int, int, int]:
    """Median colour of the light (paper) pixels inside a card box."""
    x0, y0, x1, y1 = box
    sub = rgba[y0:y1, x0:x1]
    rgb = sub[..., :3].astype(np.int16)
    a = sub[..., 3]
    light = (rgb.min(2) > 150) & (a > 120)
    if not light.any():
        return (236, 232, 222)
    px = sub[..., :3][light]
    return tuple(int(v) for v in np.median(px, axis=0))


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur = ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _fit_font(draw, text, max_w, max_h, start_px) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Shrink the font until the wrapped text fits the box height."""
    px = start_px
    while px >= 12:
        font = ImageFont.truetype(FONT_PATH, px)
        lines = _wrap(draw, text, font, max_w)
        line_h = int(px * 1.25)
        if line_h * len(lines) <= max_h:
            return font, lines
        px -= 2
    font = ImageFont.truetype(FONT_PATH, 12)
    return font, _wrap(draw, text, font, max_w)


def apply(in_png: str, out_png: str, regions: list[Region]) -> None:
    """Rewrite every region in an atlas PNG and save the result."""
    img = Image.open(in_png).convert("RGBA")
    arr = np.array(img)

    # --- erase pass (numpy, exact) ---
    for r in regions:
        x0, y0, x1, y1 = r.box
        if r.kind == "floating":
            arr[y0:y1, x0:x1, 3] = 0  # wipe old handwriting
        else:  # card: flood the interior with solid paper, keep silhouette
            paper = _paper_colour(arr, r.box)
            sub = arr[y0:y1, x0:x1]
            a = sub[..., 3]
            # Flat-fill the opaque card body, inset from the torn border so the
            # dark outline survives. A solid fill guarantees zero ink ghost
            # (an ink-only mask leaves a grey halo of the old handwriting).
            inset = max(4, r.pad // 2)
            interior = np.zeros(a.shape, dtype=bool)
            interior[inset:-inset or None, inset:-inset or None] = True
            interior &= a > 120
            sub[..., 0][interior] = paper[0]
            sub[..., 1][interior] = paper[1]
            sub[..., 2][interior] = paper[2]
            arr[y0:y1, x0:x1] = sub

    img = Image.fromarray(arr, "RGBA")

    # --- letter pass (PIL draw, optionally on a rotated tile) ---
    for r in regions:
        x0, y0, x1, y1 = r.box
        bw, bh = x1 - x0, y1 - y0
        tile = Image.new("RGBA", (bw, bh), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        avail_w, avail_h = bw - 2 * r.pad, bh - 2 * r.pad
        if r.rotate in (90, 270):
            avail_w, avail_h = avail_h, avail_w
        start_px = r.font_px or max(14, int(min(avail_h, bh) * 0.16))
        font, lines = _fit_font(td, r.text, avail_w, avail_h, start_px)

        canvas = Image.new("RGBA", (avail_w, avail_h), (0, 0, 0, 0))
        cd = ImageDraw.Draw(canvas)
        line_h = int(font.size * 1.25)
        y = 0
        for ln in lines:
            cd.text((0, y), ln, font=font, fill=(*r.ink, 255))
            y += line_h
        if r.rotate:
            canvas = canvas.rotate(r.rotate, expand=True)
        tile.alpha_composite(canvas, (r.pad, r.pad))
        img.alpha_composite(tile, (x0, y0))

    img.save(out_png)
    print(f"lettered {len(regions)} region(s): {in_png} -> {out_png}")


if __name__ == "__main__":
    print(__doc__)
    sys.exit(0)
