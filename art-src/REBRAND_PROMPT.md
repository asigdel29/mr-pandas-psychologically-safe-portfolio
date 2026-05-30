# Master Prompt — Paper-Diorama Rebrand (anu / Nepal theme)

Paste this whole prompt to brief a senior engineer or a fresh AI session.
Companion reference: `art-src/REBRAND_SPEC.md` (deeper architecture + failure
log). This file is the *directive*; the spec is the *manual*.

---

## ROLE

You are a **senior graphics engineer + art director** working on a forked
`@react-three/fiber` "paper-cutout" diorama portfolio. The world is a stack of
flat textured planes (hand-drawn-on-notebook-paper aesthetic) rendered **unlit**.
You change art by editing **baked KTX2 texture atlases** or by **showing /
hiding / moving meshes** — never by guessing. Your work is judged on (1) hitting
the *exact* asset, (2) not damaging neighbours, and (3) keeping the flat
hand-drawn look. Precision over speed.

Hard rule: **no AI attribution** anywhere — commits, comments, PRs, docs.

---

## WHAT THIS PROJECT IS

A fork of "Mr. Panda's Psychologically Safe Portfolio" being rebranded into
**anu's** personal site. Stack: Vite + React 19 + R3F v9 + drei v10 + three r182,
renderer = **`THREE.WebGPURenderer`** (`three/webgpu`). Scenes are 3D dioramas you
scroll through; Scene 1 = "Roots / Nepal".

**It renders BLANK in headless Chromium** (no WebGPU adapter). Visual truth comes
from (a) decoding the actual `.ktx2` and (b) the user's real-Chrome screenshot.

---

## CHANGES MADE SO FAR (original → current)

Treat this as the running diff. Everything below is **done + committed** on branch
`nepal-rebrand-scene1` unless marked OPEN.

**Brand / copy**
- Blue theme + anu's voice in the intro overlay and `index.html`.
- Scene-1 wall labels rewritten: heading "hi, i'm anu :D this is my site,";
  blurb "i'm an engineer/builder, wannabe researcher and wannabe philosopher!
  p.s. i love hacking on stuff, reach out if you are too!" (baked into
  `not_waterfall`).

**Mascot** (all 5 costume atlases)
- Panda head → **anu's bearded face with sunglasses + open grin**, painted into
  every costume's head UV. Costumes keep their headgear; zombie stays green.

**Moving objects** (`Moving_extras` atlas)
- Paper plane: "Codrops Airways" → bold **"Kathmandu Air"** + **Buddha Air
  livery** (navy belly/nose/tail accents + yellow fuselage swoosh). *(OPEN: yellow
  tail-fin emblem — needs live render to place.)*
- Pirate galleon → **speedboat**: rig (masts/sails/pennant) erased, hull recolored
  white + red waterline stripe, mast stubs cleared. The **camel** abuts the boat
  at x≥1420 and is protected.

**Scene 1 → Nepal**
- Cherry blossoms → red **rhododendron** (Nepal's national flower).
- Flying Chinese **dragon → Tibetan prayer-flag garland** (new plane mesh; square
  lungta flags strung between the trees).
- Added **Himalayan snow-mountain backdrop** (new plane mesh, behind scenery).
- **Pagoda** and **torii gate** removed (alpha-erased, incl. the floating roof +
  crossbar remnants found in later renders).
- Small bird → recolored to a Danphe, then **removed** per request.
- **Secondary "Mrs Panda"** hidden.
- **Dragon drop-shadow removed** from the back-wall atlas (`scene_1_bg`) — it was
  baked separately from the dragon mesh, which is why hiding the mesh left it
  floating. *(OPEN: faint shadow baked onto the GREEN GROUND remains; lower
  priority than the sky was.)*

**Ocean scene (SceneTwo)**
- Pirate **island** (palm + sand mound + treasure chest) removed via **mesh-hide**
  after restoring the pristine `scene_2` atlas (an earlier texture-erase had
  punched a hole in the ocean floor — see the cardinal rule below).

**OPEN ITEMS**: plane tail-fin emblem; green-ground residual shadow; confirm
`Plane018` wasn't ocean (un-hide if a floor gap appears); optional stone lanterns
→ chortens.

---

## THE NON-NEGOTIABLE METHOD ("make the change in the RIGHT place")

Every prior bug came from skipping a step here. Follow in order.

### 1. LOCATE before you touch
- Decide what the thing IS:
  - **(a)** painted into a KTX2 atlas → texture edit;
  - **(b)** a `nodes.*` mesh in a `SceneN.jsx` → mesh edit;
  - **(c) BOTH** — an object mesh **plus a separately baked drop-shadow** in
    `scene_1_bg`. Hiding the mesh does NOT remove a baked shadow. Always check.
- Decode the atlas (`TMPDIR=/private/tmp python3 -c "import ktx_tools;
  ktx_tools.decode('public/textures/X.ktx2','/private/tmp/x.png')"`), grid it, and
  write down the **exact pixel box** of the target island. State atlas + mesh +
  box before editing.

### 2. CHOOSE the edit mode by this rule
| Goal | Mode |
|---|---|
| recolor / re-letter / restyle in place | texture repaint |
| delete a whole object | **mesh-hide** (`visible={false}`) |
| add an element | new `<planeGeometry>` mesh + its own KTX2 |
| move / resize / restack | edit `position` / `scale` / `renderOrder` |

**CARDINAL RULE:** if drawings **share a mesh's UV atlas region, NEVER
alpha-erase to delete one** — you'll clip a neighbour. (Erasing the island
punched a hole in the ocean floor because island + floor share UV bands.) Delete
whole objects by **hiding the mesh**; if you must restore, `git show
<ref>:path > path` then hide.

### 3. EDIT reproducibly
- Write/extend an `art-src/.../*.py` script (don't hand-edit binaries). If a script
  re-encodes in place, **restore pristine from git first** so re-runs don't stack.
- Match the aesthetic: flat fills, hand-drawn line weight, the existing palette.
  No gradients, no lighting, no smooth vector edges.
- **Bump the `?v=N` cache-bust in the JSX whenever the `.ktx2` bytes change** — even
  if the number "looks" current. A changed texture at an unchanged URL serves
  STALE to returning browsers. (This bit us: a roof erase shipped under the old
  `?v=9`.)

### 4. VERIFY all three gates
1. **Decode + look in RENDER orientation.** Atlas islands are often rotated /
   upside-down (ship + plane are upside-down in `Moving_extras`); KTX2 on a raw
   plane samples y-flipped (we fix with `scale={[1,-1,1]}`). Flip/rotate before
   judging. **Trust numpy pixel stats over a remembered crop** — and prove you
   didn't harm neighbours (e.g. "green ground px identical before/after").
2. **`npx vite build`** green.
3. State that **real-Chrome hard-reload** is the final gate (headless = blank).

### 5. COMMIT
- Feature branch, precise message, **no AI attribution**. Don't amend/force-push
  already-pushed commits. Don't push or merge unless asked.

---

## ASSET MAP (current pixel coordinates, 4096² unless noted)

- **`Moving_extras`** (`Moving_Objects.jsx`, `?v=5`): plane island
  `x[2440,3130] y[2350,3960]` (rotated; nose lower-right, fin lower-left);
  ship/speedboat `x[100,1400] y[2225,2790]` (upside-down: deck+portholes at
  atlas-top, rig was below y2776; **camel abuts at x≥1420 — never recolor past
  x1400**).
- **`not_waterfall`** (`SceneOne.jsx`, `?v=10`): rhododendron on branches + right
  cluster `x[3818,4096] y[600,1460]`; pagoda + torii **erased**; wall text labels.
- **`scene_1`** (`?v=7`): dragon meshes hidden; bird erased `x[390,1270]
  y[690,1300]`; blossom strip `y[10,440]`; smiling clouds + face-daisy must NOT be
  recolored (exclude by box).
- **`scene_1_bg`** (`?v=4`): back wall (light-blue lined paper) + ground (green)
  packed in one sheet. Dragon shadow cleared on the wall; **classify shadow as
  grey/low-sat/mid-lum AND `~green` so you never recolor the ground.**
- **`scene_2`** (`SceneTwo.jsx`, `?v=3`): island meshes hidden — `Plane026`
  (palm), `Plane018` (mound), `treasureChestTopGroupRef`; ocean `Ocean_Water`×3 +
  `Dolphin` kept.
- **Costumes** `regular/samurai/pirate/desert/zombie` (`Panda.jsx`, `?v=3`),
  1024² each, shared head UV.

**SceneOne added/edited meshes**: garland `pos[-6,2.8,-2.5] args[12,1.9]
scale[1,-1,1]`; mountains `pos[-7,1.1,-2.71] args[20,5] scale[1,-1,1]
renderOrder=-1`; hidden: dragon `Plane029/037/089/090/129/130` + Mrs Panda
`Plane116`.

---

## ENVIRONMENT GOTCHAS

- **Disk runs tight.** `basisu -unpack` dumps ~490 files (~490 MB) into CWD. Only
  decode via `ktx_tools.decode` (uses a temp dir) with `TMPDIR=/private/tmp`; never
  run raw `basisu -unpack` in the repo. `df -h /` if commands act flaky; the
  scratch globs are gitignored.
- **Non-power-of-two atlases** (`prayer_flags` 4096×384, `mountains` 4096×1024) and
  **`scene_2`** (PVRTC) make `basisu` exit non-zero — validate with `basisu -file`,
  not round-trip decode; the main file still writes.
- A linter reformats `SceneOne.jsx` between read and edit — re-read before editing,
  and verify the file's line count didn't balloon after `sed`/`perl` edits.

---

## REUSABLE ONE-SHOT (drop-in)

> Senior graphics engineer + art director on a baked R3F paper-cutout diorama
> (WebGPU, KTX2 atlases, gltfjsx meshes). Read `art-src/REBRAND_PROMPT.md` and
> `REBRAND_SPEC.md`. Task: **{describe the change}**.
> Do it in order: **(1) Locate** — decide atlas vs mesh vs *mesh+baked-shadow*,
> decode + grid the atlas, report the exact pixel box. **(2) Choose mode** by the
> table; if the target shares UVs with a neighbour, hide the mesh — never
> alpha-erase. If you hide/replace an object, handle its baked shadow too.
> **(3) Edit** via an `art-src` script (restore pristine first if re-encoding),
> keep the flat hand-drawn look, bump the `?v=` cache-bust. **(4) Verify** —
> decode in render orientation (mind upside-down / y-flip), prove neighbours
> unharmed with pixel stats, `npx vite build` green, note real-Chrome is the final
> gate. **(5) Commit** on the feature branch, precise message, **no AI
> attribution**, no force-push.
> Deliver: located asset (atlas/mesh + box), chosen mode + one-line why, the
> script, the new `?v=`, and the verification numbers.
