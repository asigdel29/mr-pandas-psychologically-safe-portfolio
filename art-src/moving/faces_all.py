"""Repaint anu's bearded face onto all five mascot costume atlases.

Reproducible driver: pulls each costume's CLEAN texture from git (commit
``CLEAN_REF``, before any face edits), decodes it, paints the bearded face via
face_to_person.paint_face, and re-encodes it back into public/textures.

    python3 faces_all.py

Run from art-src/moving. Requires basisu on PATH + a clean git work tree for
the referenced blob (only reads, never writes git).
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import ktx_tools  # noqa: E402
from face_to_person import COSTUMES, paint_face  # noqa: E402

CLEAN_REF = "b99508d"  # parent of the first face edit -- all costumes pristine
TEX_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "public", "textures"))
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _clean_ktx2(costume: str, dst: str) -> None:
    """Extract the pristine costume atlas from git into ``dst``."""
    blob = subprocess.check_output(
        ["git", "show", f"{CLEAN_REF}:public/textures/{costume}.ktx2"], cwd=REPO)
    with open(dst, "wb") as fh:
        fh.write(blob)


def main() -> int:
    for costume in COSTUMES:
        with tempfile.TemporaryDirectory(prefix=f"face_{costume}_") as tmp:
            clean = os.path.join(tmp, "clean.ktx2")
            base = os.path.join(tmp, "base.png")
            painted = os.path.join(tmp, "painted.png")
            _clean_ktx2(costume, clean)
            ktx_tools.decode(clean, base)
            paint_face(costume, base, painted)
            ktx_tools.encode(painted, os.path.join(TEX_DIR, f"{costume}.ktx2"))
    print("repainted faces:", ", ".join(COSTUMES))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
