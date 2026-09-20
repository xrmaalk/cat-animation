# Purrcilla, Dixon & Dage: Curious Together

This Blender 5.x project is a reusable production scaffold for short educational cat stories. It combines a shared home set, cameras, character collections and proxy rigs, editorial timing blocks, reference photos, and transparent mascot sprites. The current work is an **animatic and look-development pipeline**: shots and selected sprite poses are staged, while final character performance and a full-length rendered episode remain future work.

Purrcilla is named **Cila** in Blender objects and sprite data. Dixon and Dage keep their names throughout.

## Current project files

| File | Role |
| --- | --- |
| `Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend` | Reusable 17-minute Episode 01 master scene, home, cameras, proxy cats, and editorial structure. |
| `Purrcilla_Dixon_Dage_Animated_Short.blend` | 12-second Episode 01 proof of concept using the proxy characters. |
| `Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend` | Short-form mascot lookdev using one camera-facing idle cutout per cat. |
| `Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend` | Separate 17-minute Episode 02 test animatic with frame-driven sprites and an animated box prop. |
| `preview_frames/episode02_box/EP02_storyboard_preview.png` | Contact sheet of Episode 02 story beats and the optional fact label. |

The Episode 01 and Episode 02 timelines each contain 26 modular shots at 24 fps. Their 17-minute duration is an editorial plan with key actions and holds, rather than 17 minutes of continuous finished animation. The separate 12-second short can be rendered to a playable MP4 using the workflow below.

## Animated short

`Purrcilla_Dixon_Dage_Animated_Short.blend` is a 12-second, 24 fps editable proof of concept for Episode 01. Dixon notices and paws at the blinds, the slats turn, floor stripes move, and Cila and Dage join the final view. It uses the template's proxy characters, so the acting and meshes are still suitable for an animatic rather than a finished character performance. The short is a separate file from the 17-minute template.

Open the animated file in Blender, switch to camera view with Numpad 0, return to frame 1, and press Play. Timeline markers label the main beats. `Purrcilla_Dixon_Dage_Animated_Short_preview.webp` is a quick 12 fps Workbench preview.

## Single-cutout mascot lookdev

The transparent concept lineup is in `references/Purrcilla_Dixon_Dage_MAALTECH_Sprite_Concept.png`, with its design notes in `references/MAALTECH_sprite_concept.md`. A Python pass splits it into three character textures and places camera-facing cutouts over the animated cat roots. The cutouts inherit the existing root motion, so the scene can be reviewed without changing the original production file.

Run these from the project directory with Pillow available to the normal Python interpreter and Blender 5.x on your PATH:

```bash
python prepare_mascot_sprites.py
blender --background Purrcilla_Dixon_Dage_Animated_Short.blend --python add_mascot_sprites.py
blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend --python render_mascot_preview.py
```

The second command saves `Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend`; it leaves the animated short and template untouched. The texture images are packed into the new `.blend`. The inspection renders land in `preview_frames/mascot_sprites/` at frames 1, 132, and 258. `add_mascot_sprites.py` accepts `-- --output path/to/file.blend` for another output path and `--overwrite` if you intentionally want to replace that output.

This is a 2.5D lookdev pass with one idle cutout per cat. The scene's camera and root movement remain animated; individual paws, blinks, and body poses do not change within these cutouts. Episode 02 uses the separate multi-frame sheets described below. Use Eevee for the transparent image materials; the existing Workbench preview script does not display them as intended.

### Export a playable video

The Blender 5.2 installation used for this project has no FFmpeg output option. `render_mascot_video.py` renders Eevee PNG frames and calls a local FFmpeg executable to encode H.264 MP4 with `yuv420p` for broad playback support. It writes a temporary MP4 and names the final file only after encoding completes. If Blender stops during rendering, rerun the same command; completed frames are reused.

```bash
blender --background Purrcilla_Dixon_Dage_Animated_Short_Mascot_Sprites.blend --python render_mascot_video.py
```

The 288-frame, 24 fps, 1280×720 result is `renders/Purrcilla_Dixon_Dage_Mascot_Sprites.mp4`. For a one-second playback check, append `-- --sample`. If FFmpeg is not on PATH or in the Storyboarder installation detected by the script, pass `-- --ffmpeg C:/path/to/ffmpeg.exe`.

To rebuild the short from the template:

```bash
blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python animate_short.py
```

To regenerate the proxy short preview, render the sequence with `render_preview.py -- --sequence`, then run `python encode_preview.py` with Pillow installed.

## Reusable sprite sheets and Episode 02

The three source sheets are `references/mascot_sprites/Purrcilla_MAALTECH_Mascot_Spritesheet.png`, `Dixon_MAALTECH_Mascot_Spritesheet.png`, and `Dage_MAALTECH_Mascot_Spritesheet.png`. They remain the source artwork. `prepare_episode02_sprites.py` validates and repacks them into separate, equal-cell, transparent atlases in `references/mascot_sprites/episode02_atlases/`; the JSON manifest records source hashes, layout, and selected pose names. Cila and Dage each have a 7×10 source grid (70 frames), while Dixon has a 7×9 grid (63 frames). Dixon's normalized 7×10 atlas has one blank padding row.

In Episode 02, `SPRITE_Cila`, `SPRITE_Dixon`, and `SPRITE_Dage` live in their existing `CHAR_*` collections. Each camera-facing plane uses its own packed atlas, a `sprite_frame` property, a material driver, and stepped sprite actions on NLA tracks. The original proxy rigs and actions remain available as hidden references in the Episode 02 file. The house, camera library, character identities, and editorial timing come from the template; the cardboard box, flap response, fact, shot assignments, and sprite actions belong to this episode.

Episode 02, **“Dage Discovers Why a Cardboard Box Feels Safe,”** follows `SWAP_EPISODE_SEED.md`: Dage notices, tests, enters, and rests in a box; Dixon observes; Cila investigates; and all three share the final frame. `episode02_seed.json` and `episode02_shotlist.csv` hold the story data and 26-shot timing. `EP02_BEATS` is the active editorial NLA track in the new file; copied `EP01_BEATS` strips are muted reference data. The optional fact label and narration live in `NARRATION_TEXT_OFF`, which starts disabled.

With Blender 5.2 available as `blender`, and Pillow and NumPy installed for your normal Python interpreter, run these from the project directory:

```powershell
python prepare_episode02_sprites.py
blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python build_episode02.py
blender --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python render_episode02_preview.py
python make_episode02_contact_sheet.py
blender --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python verify_episode02.py
```

The builder writes a separate `.blend` and refuses to replace an existing Episode 02 output unless you pass `-- --overwrite`. The preview commands write stills and a contact sheet under `preview_frames/episode02_box/`; they do not encode a 17-minute video. The verifier writes `EP02_VERIFICATION.json`; the current Episode 02 file passed 96 checks with no missing assets. See `EP02_IMPLEMENTATION.md` for frame mappings and rebuild details and `EP02_VERIFICATION.md` for checks and known limits. The source art has a few colored edge specks, and flat sprite planes only approximate paw contact with the box.

For another episode, reuse the template, source sheets or prepared atlases, and the shot timing pattern. Copy the seed, shot list, and episode builder, then change the discovery prop, cause-and-effect action, cameras, fact, and per-shot sprite poses. `SWAP_EPISODE_SEED.md` is the episode planning guide.

The supplied photos guide character identity; the mascot sheets are stylized artwork for the current 2.5D passes.

## What is included

- `build_template.py` — Blender 5.x builder. It creates the master scene, named collections, lightweight proxy character meshes, control rigs and custom properties, modular home sets, discovery props, cameras, lights, narration toggle collection, reference image empties, timeline markers, and Episode 01 NLA beat strips.
- `episode01_shotlist.csv` — 26-shot / 17-minute animatic plan, within the requested 20–40 shot range.
- `episode01_timing.json` — machine-readable beat timing and shot metadata.
- `SWAP_EPISODE_SEED.md` — procedure for making a new discovery episode without rebuilding the rigs or home.
- `references/` — the five supplied cat reference images used to establish identity and silhouette notes.
- `references/mascot_sprites/` — source mascot sheets, single-cutout lookdev images, and Episode 02 atlases with a frame manifest.
- `episode02_seed.json`, `episode02_shotlist.csv`, and `build_episode02.py` — Episode 02 data and separate Blender builder.
- `prepare_episode02_sprites.py`, `render_episode02_preview.py`, `make_episode02_contact_sheet.py`, and `verify_episode02.py` — repeatable sprite preparation, preview, and verification tools.

## Generate the master `.blend`

Run from a Blender 5.x installation:

```bash
blender --background --python build_template.py
```

The builder saves:

```text
Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend
```

`build_template.py` writes to that fixed filename, so running it again can replace the current template. Work from a copy if you have made changes in Blender. `animate_short.py` likewise writes to its fixed animated-short filename.

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
