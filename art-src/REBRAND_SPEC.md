# Paper-Diorama Rebrand — Engineering & Art Spec

A single source of truth for converting the forked "Mr. Panda" R3F paper-cutout
portfolio into **anu's** Nepal-themed site. Read this **before** touching any
asset. It encodes the architecture, the exact edit mechanisms, the failure modes
that have already bitten us, and the verification gates that catch them.

> Voice rule: no AI attribution anywhere — commits, comments, docs, PRs.

---

## 0. TL;DR for the impatient

1. The world is **baked**. Almost nothing is DOM text or vector. Every drawing
   lives in a GPU-compressed **`.ktx2` texture atlas**, painted onto flat
   `<mesh>` "paper cutouts" with an **unlit** material. To change art you either
   **repaint the atlas** or **hide/move the mesh** — pick the right one (§3).
2. **Decide edit mode by what you're changing** (§3 decision table). The #1 bug
   source is using the wrong mode (texture-erase punched a hole in the ocean
   floor; mesh-hide orphaned a baked shadow).
3. **Every object can own a separate baked shadow** in `scene_1_bg`. Hiding the
   object does NOT remove its shadow (§5, the dragon-shadow saga).
4. **Verify by decoding the actual `.ktx2` and looking at the right orientation**
   (atlas is often upside-down / rotated vs render). Then verify in **real
   Chrome** — the scene uses WebGPU and is blank in headless (§6).
5. Bump the `?v=N` cache-bust in the JSX whenever you re-encode a texture, or the
   browser serves the stale one (§4).

---

## 1. Stack & boot path

- Vite + React 19 + `@react-three/fiber` v9 + drei v10 + three r182.
- Renderer: **`THREE.WebGPURenderer`** (`src/Experience/Experience.jsx:111-142`,
  `import * as THREE from "three/webgpu"`). Falls back to WebGL2 where WebGPU is
  absent, but **headless Chromium renders blank** (no adapter). You need real
  Chrome with a GPU to see the diorama. This is why we iterate from the user's
  screenshots.
- Boot: `index.html` → `src/main.jsx` (BrowserRouter) → `src/App.jsx` →
  `<IntroScreen/>` (HTML overlay) + `<Experience/>` (R3F Canvas).
- Motion: `src/Experience/Scene.jsx` drives one `useFrame` loop along a camera
  curve (`components/curve.jsx`); scroll input in `Experience.jsx`.

## 2. Where art actually lives

- **Textures**: `public/textures/*.ktx2` — Basis/ETC1S compressed atlases, mostly
  4096² (costumes 1024², `mountains` 4096×1024, `prayer_flags` 4096×384).
- **Geometry**: `public/models/*.glb` (Draco). Surfaced as hardcoded
  `<mesh geometry={nodes.PlaneNNN.geometry}>` lists in `src/Experience/models/*.jsx`
  (gltfjsx output). GLB node names keep dots (`Plane.125`); the JSX strips them
  (`Plane125`). **Never rename `nodes.*`** — they bind to the GLB.
- **Material**: `src/Experience/utils/ktxLoader.jsx` → `useKTX2Texture(url,
  transparent=true, alphaTest=0.6, side="front")` returns an **unlit
  `MeshBasicMaterial`** (`flat`, alpha-tested). That flat look is the whole
  aesthetic. There is **no lighting** — every "shadow" you see is *painted into a
  texture*, not computed.
- **Scene → chapter map**: SceneOne = Roots/Nepal, SceneTwo = Mind+Machine
  (lakeside/ocean), SceneThree = The Build/NYC, SceneFour = Things I Love.

## 3. The two edit modes — and how to choose (READ THIS)

| You want to… | Mode | Mechanism |
|---|---|---|
| Recolor / re-letter / restyle a drawing in place | **Texture repaint** | decode `.ktx2` → numpy/PIL edit the UV island → re-encode → bump `?v=` |
| Remove a whole object cleanly | **Mesh hide** | add `visible={false}` to its `<mesh>`/`<group>` in `SceneN.jsx` |
| Add a new element (garland, mountains) | **New mesh** | add a `<planeGeometry>` mesh with its own KTX2 texture |
| Move / resize / restack an element | **Mesh transform** | edit `position` / `scale` / `renderOrder` in JSX |

**Decision rule (the one that prevents the recurring bugs):**

- **If multiple drawings share one mesh's UV atlas region, NEVER alpha-erase to
  delete one of them.** Erasing pixels can clip a neighbour that samples adjacent
  UVs. Example: erasing the pirate island from `scene_2` punched a transparent
  **hole in the ocean floor** because island + floor share UV bands. ✅ Correct
  fix: restore the pristine atlas (`git show <ref>:path > path`) and
  `visible={false}` the island meshes (`Plane026` palm, `Plane018` mound,
  `treasureChestTopGroupRef`).
- **If an object is its own mesh, prefer mesh-hide over texture-erase.** Cheaper,
  reversible, no atlas surgery.
- **But mesh-hide does NOT remove a baked drop-shadow** (§5). If the thing casts
  a painted shadow on the wall, you must also clear that shadow from
  `scene_1_bg`.
- **Texture repaint is right for recolors and text** (rhododendron, terracotta,
  "Kathmandu Air", Danphe bird) — there's no mesh-level way to do those.

## 4. Texture round-trip — the exact, safe procedure

Tooling: `art-src/ktx_tools.py` (wraps `basisu`), `art-src/text_tools.py`
(lettering). Per-asset scripts live in `art-src/scene_1/` and `art-src/moving/`.

```
TMPDIR=/private/tmp python3 - <<'PY'
import ktx_tools, numpy as np
from PIL import Image
ktx_tools.decode('public/textures/X.ktx2', '/private/tmp/x.png')  # -> RGBA PNG
# ...edit the numpy array / PIL image, IN the correct UV island...
ktx_tools.encode('/private/tmp/x.png', 'public/textures/X.ktx2')
PY
```

Then bump the cache-bust in the mesh's JSX: `useKTX2Texture("/textures/X.ktx2?v=N")`.

**Hard-won rules:**
- **Always `TMPDIR=/private/tmp`.** `basisu -unpack` dumps ~490 files (~490 MB)
  of every GPU format × mip. `ktx_tools.decode` uses a TemporaryDirectory and
  cleans up — **never run raw `basisu -unpack` in the repo** (it fills the disk;
  at 100% the shell can't even write output). The user's disk runs tight — check
  `df -h /` and clean `*_transcoded_* *_unpacked_*` if it climbs.
- **Non-power-of-two textures** (`prayer_flags` 4096×384, `mountains` 4096×1024)
  make `basisu -unpack` exit non-zero. Validate those with `basisu -file`, not by
  round-trip decode.
- **`scene_2` is multi-format (incl. PVRTC)** → `basisu` exits non-zero but writes
  the main file first; ignore the exit code, check size > 0.
- **Re-encode is destructive & stacking.** Per-object scripts (`speedboat.py`,
  `plane_livery.py`) edit the *current* atlas in place. To redo cleanly: restore
  pristine from git first, then run the scripts in order.

## 5. Baked shadows — the dragon-shadow case study (DO NOT REPEAT)

**Symptom:** after hiding the flying dragon meshes, large grey blobs remained
across the sky wall.

**Root cause:** the diorama bakes soft **drop-shadows onto the back-wall paper**,
stored in **`scene_1_bg.ktx2`** — a *different atlas* from the object. Hiding the
object's mesh (in `scene_1`) cannot touch a shadow painted into `scene_1_bg`.

**Why blind fixes kept failing:** `scene_1_bg` is a **tightly UV-packed sheet of
wall + ground panels**. A color mask for "greyish, low-saturation, mid-luminance"
also catches the muted-green ground panels and the lined-paper itself, so an
automated erase either misses the shadow or damages the ground. The earlier
`clean_shadow.py` only cleared one band (`x[150,2090] y[560,1360]`) and left the
rest (the wide blobs at atlas cells around `x[2048,3584] y[512,2048]`).

**The correct way to kill a baked wall shadow (choose one):**

1. **Decode the wall mesh's real UVs, then clear only the wall island.** Get the
   UVs for `nodes["First_Scene_-_Bg"]` / `First_Scene_-_Bg001` from the GLB via
   DracoPy (atlas px = `u*4096`, `y = v*4096` or `(1-v)*4096` — disambiguate by
   which band actually holds the shadow). Within *only the wall island's*
   bounding region, replace shadow-grey pixels with the **per-row median of the
   bright lined-paper** (preserves the horizontal ruling lines). Do not touch the
   ground-panel islands.
2. **Or cover it in 3-D**: the mountains plane already hides the lower wall.
   Raise/extend a wall-colored or mountain plane to occlude the shadow band
   (cheap, no atlas surgery), accepting that it also hides whatever wall is
   behind it.

**General principle:** *every removable object may own a separate baked shadow.*
When you hide or replace an object, check `scene_1_bg` for an orphaned shadow and
plan its removal in the same change.

## 6. Verification gates (run all three before claiming done)

1. **Decode-and-look at the right orientation.** Atlas islands are often rotated
   or **upside-down** vs the render (the ship + plane are upside-down in
   `Moving_extras`; KTX2 on a raw `planeGeometry` also samples y-flipped — we
   correct with `scale={[1,-1,1]}`). Decode the changed island, flip/rotate to
   render orientation, and eyeball it. **Trust numpy pixel stats over a
   half-remembered crop.**
2. **`npx vite build`** must stay green after JSX edits.
3. **Real Chrome, hard-reload (Cmd-Shift-R) or Incognito.** Headless = blank
   (WebGPU). The user's screenshot is the final gate; expect 1–2 nudge rounds on
   position/scale/orientation.

## 7. Coordinate & cache reference (current, keep updated)

KTX2 cache versions in JSX (bump on every re-encode):
`scene_1 v7`, `scene_1_bg v3`, `not_waterfall v9`, `prayer_flags v3`,
`mountains v1`, `scene_2 v3`, `Moving_extras v5`, costumes `v3`.

Atlas islands (px, 4096² unless noted):
- `Moving_extras`: **plane** island `x[2440,3130] y[2350,3960]` (drawn rotated;
  nose lower-right, fin lower-left). **ship/speedboat** island `x[100,1400]
  y[2225,2790]` (drawn upside-down: deck/portholes at atlas-top, rig hung below
  y2776; **the camel abuts it at x≥1420 — do not recolor past x1400**).
- `not_waterfall`: torii + pagoda were **erased**; rhododendron blossoms on the
  branches + right cluster `x[3818,4096] y[600,1460]` (keep). **Still present and
  WRONG (to remove): the dark teal pagoda roof + the torii crossbar/salmon
  remnant** — they're cut-outs on the `nodes.not_waterfall` mesh; erase their UV
  regions (find via grid-decode; roof reads dark-slate `B-R>4, lum 40-150`).
- `scene_1`: dragon meshes hidden; Danphe bird `BIRD_BOX (390,690,1270,1300)`;
  blossom strip `y[10,440]`.
- `scene_1_bg`: **dragon drop-shadow still baked** (see §5) — the open item.

SceneOne new/edited meshes:
- prayer-flag garland: `position={[-6,2.8,-2.5]}` `args={[12,1.9]}`
  `scale={[1,-1,1]}`.
- mountains: `position={[-7,1.1,-2.71]}` `args={[20,5]}` `scale={[1,-1,1]}`
  `renderOrder={-1}`.
- dragon meshes (`Plane029/037/089/090/129/130`) + Mrs Panda (`Plane116`):
  `visible={false}`.

## 8. Change log so far (what's done)

**Mascot** (`Panda.jsx`, all 5 costume atlases `v3`): bearded face with
sunglasses + open grin painted into every costume's head UV (`face_to_person.py`
+ `faces_all.py`); costumes keep their headgear; zombie stays green.

**Plane** (`Moving_extras`): "Codrops Airways" → bold **"Kathmandu Air"**;
Buddha Air livery — navy belly/nose/tail accents + yellow fuselage swoosh
(`age_plane.py`, `plane_livery.py`). Tail-fin emblem deferred (thin diagonal,
needs live render).

**Ship → speedboat** (`Moving_extras`): rig erased, hull recolored white + red
waterline stripe, mast stubs cleared, camel protected (`speedboat.py`).

**Scene 1 → Nepal**:
- Cherry blossoms → red **rhododendron** (`nepalize_scene_1.py`,
  `nepalize_not_waterfall.py`).
- Flying dragon → **Tibetan prayer-flag garland** (new plane + `make_garland.py`);
  square lungta flags; spans between the trees.
- **Himalayan mountains** backdrop (new plane + `make_mountains.py`).
- Removed **pagoda** + **torii** (alpha-erase on `not_waterfall`) — *roof/crossbar
  remnants still visible, OPEN*.
- Small bird → **Danphe** (Himalayan Monal) then **removed** per request
  (`patch_nepal.py`).
- Hid the **secondary panda**.
- Labels rewritten in anu's voice ("hi, i'm anu :D this is my site," + about
  blurb) on `not_waterfall` (`label_not_waterfall.py`).

**Ocean (SceneTwo)**: removed pirate **island** (palm + mound + chest) via
mesh-hide after restoring pristine `scene_2` (fixed the floor hole).

## 9. OPEN ITEMS (the "still incomplete")

1. **Dragon drop-shadow in `scene_1_bg`** — the big grey sky blobs. Fix per §5
   (decode wall UVs + per-row paper median, or occlude in 3-D). **Highest
   priority — it's the most visible defect.**
2. **Pagoda roof + torii crossbar/salmon remnants** on `not_waterfall` — finish
   the erase of those cut-out UV regions.
3. Plane **yellow tail-fin emblem** placement (needs live render).
4. Confirm `Plane018` (hidden as island) wasn't ocean — if a floor gap appears,
   un-hide it.
5. Optional: stone lanterns → chortens/stupas.

---

## 10. The reusable working prompt

> You are a senior graphics engineer + art director working on a baked R3F
> paper-cutout diorama (WebGPU, KTX2 atlases, gltfjsx meshes). **Read
> `art-src/REBRAND_SPEC.md` first.** For the requested change:
>
> 1. **Locate the asset precisely.** Identify whether the thing is (a) painted
>    into a KTX2 atlas, (b) a `nodes.*` mesh in a `SceneN.jsx`, or (c) both
>    (object mesh + a *separate baked shadow* in `scene_1_bg`). Decode the atlas
>    and grid-locate the exact UV island in pixels before editing. State which
>    atlas/mesh and the pixel box.
> 2. **Choose the edit mode by §3's table & decision rule.** Justify it in one
>    line. If the element shares UVs with a neighbour, do NOT alpha-erase — hide
>    the mesh or restore-and-hide. If you hide/replace an object, explicitly
>    check for and handle its baked shadow.
> 3. **Make the change reproducibly** via an `art-src/.../*.py` script (restore
>    pristine from git first if re-encoding), bump the `?v=` cache-bust, and keep
>    the flat hand-drawn aesthetic (no lighting, match line weight & palette).
> 4. **Verify all three gates (§6)**: decode-and-look in the *render orientation*
>    (mind the upside-down/rotated/y-flip), `npx vite build` green, and call out
>    that real-Chrome confirmation is still required. Trust numpy stats over
>    remembered crops.
> 5. **No AI attribution** in any commit/comment/doc. Commit on a feature branch
>    with a precise message; do not push or merge unless asked.
>
> Deliver: the located asset (atlas/mesh + pixel box), the chosen mode + why, the
> script, the new `?v=`, and the verification evidence. If a baked shadow or a
> shared-UV neighbour is involved, say how you protected it.
