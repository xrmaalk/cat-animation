# Purrcilla, Dixon & Dage: Curious Together — Blender 5.x reusable template

## Animated short

`Purrcilla_Dixon_Dage_Animated_Short.blend` is a 12-second, 24 fps editable proof of concept for Episode 01. Dixon notices and paws at the blinds, the slats turn, floor stripes move, and Cila and Dage join the final view. It uses the template's proxy characters, so the acting and meshes are still suitable for an animatic rather than a finished character performance. The original 17-minute template file is unchanged.

Open the animated file in Blender, switch to camera view with Numpad 0, return to frame 1, and press Play. Timeline markers label the main beats. `Purrcilla_Dixon_Dage_Animated_Short_preview.webp` is a quick 12 fps Workbench preview.

## MAALTECH-style mascot sprite lookdev

The transparent concept lineup is in `references/Purrcilla_Dixon_Dage_MAALTECH_Sprite_Concept.png`, with its design notes in `references/MAALTECH_sprite_concept.md`. A Python pass splits it into three character textures and places camera-facing cutouts over the animated cat roots. The cutouts inherit the existing root motion, so the scene can be reviewed without changing the original production file.

Run these from the project directory with Pillow available to the normal Python interpreter and Blender 5.x on your PATH:

```bash
python prepare_mascot_sprites.py
blender --background Purrcilla_Dixon_Dage_Animated_Short.blend --python add_mascot_sprites.py
blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend --python render_mascot_preview.py
```

The second command saves `Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend`; it leaves the animated short and template untouched. The texture images are packed into the new `.blend`. The inspection renders land in `preview_frames/mascot_sprites/` at frames 1, 132, and 258. `add_mascot_sprites.py` accepts `-- --output path/to/file.blend` for another output path and `--overwrite` if you intentionally want to replace that output.

This is a 2.5D lookdev pass with one idle cutout per cat. The scene's camera and root movement remain animated; individual paws, blinks, and body poses do not change within these cutouts. For full performance, draw aligned sprite frames for each action or use the concept as a guide for new 3D character meshes and materials. Use Eevee for this pass; the existing Workbench preview script does not display these transparent image materials as intended.

To rebuild the short from the template:

```bash
blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python animate_short.py
```

To regenerate the preview, render the sequence with `render_preview.py -- --sequence`, then run `python encode_preview.py` with Pillow installed.

This package is a production scaffold for a gentle educational adventure series starring the three real household cats in the supplied reference photos. It is intentionally modular: the house, cameras, cat identities, control contract, shot rhythm, and episode beat structure stay reusable while each episode swaps only the discovery subject, prop, investigation animation, fact labels, and narration.

## What is included

- `build_template.py` — Blender 5.x builder. It creates the master scene, named collections, lightweight proxy character meshes, control rigs and custom properties, modular home sets, discovery props, cameras, lights, narration toggle collection, reference image empties, timeline markers, and Episode 01 NLA beat strips.
- `episode01_shotlist.csv` — 26-shot / 17-minute animatic plan, within the requested 20–40 shot range.
- `episode01_timing.json` — machine-readable beat timing and shot metadata.
- `SWAP_EPISODE_SEED.md` — procedure for making a new discovery episode without rebuilding the rigs or home.
- `references/` — the five supplied cat reference images used to establish identity and silhouette notes.

## Generate the master `.blend`

Run from a Blender 5.x installation:

```bash
blender --background --python build_template.py
```

The builder saves:

```text
Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend
```

The script uses Eevee for a responsive animatic file, 1920×1080 output, 24 fps, AgX, and a 17-minute timeline. For final hero shots, link or append the production character collections and switch those shots to Cycles/hero fur only where required.

## Scene architecture

The scene contains the requested collections:

`CHAR_Cila`, `CHAR_Dage`, `CHAR_Dixon`, `SET_Porch`, `SET_Living`, `SET_Window`, `SET_WorkNook`, `SET_Condo`, `PROPS`, `CAMERAS`, `LIGHTS`, `FX_Particles`, and `EDIT_NLA`.

The builder also creates `NARRATION_TEXT_OFF` and `REFERENCES`. Narration and lower-third labels are disabled by default so the observational rhythm remains quiet. Enable the narration collection only for an approved narrator/text pass.

## Character identity guardrails

- **Cila**: cool gray-brown compact tabby, sage-green eyes, no white mittens, scout energy, upright/threshold/lap-loaf poses.
- **Dixon**: warmer gray tabby, cream chest, white front mittens, larger round green eyes, vertical window energy, hind-stand and slat-peek poses.
- **Dage**: only black-and-white semi-longhair, white ruff, plume-tail volume, cubby/loaf/chin-on-lip poses.

The proxy geometry is deliberately lightweight and replaceable. It exists to prove composition and timing, not to replace a final sculpt, groom, or deformation pass.

## Rig and animation contract

Each character collection receives a named control armature with root, spine, neck, head, four leg chains, ear controls, and a five-segment tail chain. Custom properties document the intended N-panel controls:

- `look_at_target`
- `tail_curl`
- `loaf_morph`
- `hind_stand` — Dixon hero control
- `fluff_volume` — Dage hero control

The builder creates reusable pose assets/placeholders for rest, upright look, loaf, sniff, slow blink, groom, stretch, jump up/down, and character-specific hero poses. Replace these with full pose assets once the production rig is linked.

## Episode 01 timing

Episode 01, **“The Slats That Make Daylight,”** is timed to 17:00. The NLA/editorial holder contains one strip per shot, and the timeline has beat markers. The shot plan follows the requested sequence: cold open, title/names, morning geography, notice, first investigation, experiment/fact, shared understanding, quiet callback, recap, and button.

The NLA strips are editorial timing blocks, not 17 minutes of continuous animation. Animate each shot independently and keep the master scene as the assembly/edit reference.

## Lookdev workflow

Use the three hero portrait cameras for one lookdev frame per character:

- `CAM_HeroPortrait_Cila`
- `CAM_HeroPortrait_Dage`
- `CAM_HeroPortrait_Dixon`

The remaining cameras cover cat-eye geography, window reporting, condo observation, porch wide, paw inserts, and eye inserts. The lighting collection contains soft window, cool overcast porch, and warm lamp sources. Dust-in-sunbeam and rain-on-screen FX are left as optional shot-level additions so they do not burden every viewport preview.
