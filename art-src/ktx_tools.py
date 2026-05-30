"""KTX2 <-> PNG round-trip helpers for the portfolio texture pipeline.

The diorama art lives in GPU-compressed ``.ktx2`` atlases under
``public/textures``. To hand-/procedurally repaint them we must decode to a
flat RGBA PNG, edit, and re-encode. This module wraps the ``basisu`` CLI so the
rest of the pipeline never has to know its quirks.

basisu quirks this module hides:
  * ``-unpack`` ignores ``-output_path`` and dumps ~hundreds of files (every
    GPU format x every mip x rgb/alpha) into the *current* directory, so we
    always run it inside a throwaway temp dir.
  * the full-resolution colour island is the ``*_rgb_*level_0*`` PNG and its
    cut-out mask is the matching ``*_a_*level_0*`` PNG; we merge them into one
    RGBA image.

Usage:
    python3 ktx_tools.py decode <input.ktx2> <output.png>
    python3 ktx_tools.py encode <input.png>  <output.ktx2>

Requires: basisu on PATH, Pillow, numpy.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

BASISU = shutil.which("basisu")


def _require_basisu() -> str:
    if BASISU is None:
        raise RuntimeError("basisu not found on PATH (brew install basis_universal)")
    return BASISU


def _pick(patterns: list[str], scratch: str) -> str | None:
    """Return the first decoded PNG in ``scratch`` matching any glob pattern."""
    for pattern in patterns:
        hits = sorted(glob.glob(os.path.join(scratch, pattern)))
        if hits:
            return hits[0]
    return None


def decode(ktx2_path: str, out_png: str) -> None:
    """Decode a KTX2 atlas to a flat RGBA PNG (colour island + alpha mask)."""
    _require_basisu()
    ktx2_path = os.path.abspath(ktx2_path)
    out_png = os.path.abspath(out_png)

    with tempfile.TemporaryDirectory(prefix="ktxdecode_") as scratch:
        local = os.path.join(scratch, os.path.basename(ktx2_path))
        shutil.copyfile(ktx2_path, local)
        subprocess.run(
            [BASISU, "-unpack", "-no_ktx", os.path.basename(local)],
            cwd=scratch,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )

        rgb_png = _pick(
            ["*_rgb_*level_0*.png", "*rgb*0000.png", "*_rgb_*.png"], scratch
        )
        if rgb_png is None:
            produced = "\n".join(sorted(os.listdir(scratch))[:20])
            raise RuntimeError(f"no rgb level_0 PNG produced. saw:\n{produced}")

        colour = Image.open(rgb_png).convert("RGB")

        alpha_png = _pick(
            ["*_a_*level_0*.png", "*alpha*0000.png", "*_a_*.png"], scratch
        )
        if alpha_png is not None:
            mask = Image.open(alpha_png).convert("L").resize(colour.size)
            colour.putalpha(mask)
        else:
            colour = colour.convert("RGBA")

        os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
        colour.save(out_png)
        print(f"decoded {ktx2_path} -> {out_png} ({colour.size[0]}x{colour.size[1]})")


def encode(png_path: str, ktx2_path: str) -> None:
    """Encode an RGBA PNG back to a mipmapped ETC1S KTX2 atlas.

    Matches the originals: ETC1S/BASISLZ (basisu default), full mip chain,
    sRGB colour, alpha preserved from the PNG.
    """
    _require_basisu()
    png_path = os.path.abspath(png_path)
    ktx2_path = os.path.abspath(ktx2_path)
    os.makedirs(os.path.dirname(ktx2_path) or ".", exist_ok=True)
    subprocess.run(
        [BASISU, "-ktx2", "-mipmap", "-file", png_path, "-output_file", ktx2_path],
        check=True,
    )
    print(f"encoded {png_path} -> {ktx2_path}")


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in {"decode", "encode"}:
        print(__doc__)
        return 2
    if argv[1] == "decode":
        decode(argv[2], argv[3])
    else:
        encode(argv[2], argv[3])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
