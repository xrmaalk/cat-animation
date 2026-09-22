# Episode 3 creation and rendering guide

This guide turns the existing Episode 3 seed into a separate Blender animatic without changing the Episode 1 template or Episode 2 file.

Episode 3 already has a seed at `episodes/3-episode/episode03_seed.json`. Its shot list is currently empty, and the repository does not yet contain Episode 3 builder, preview, contact-sheet, verification, or full-video scripts. Complete the steps below before trying to render it.

The current project is an animatic/look-development pipeline. A 17-minute Episode 3 file will contain 26 camera-bound editorial blocks, selected sprite poses, simple movement, and long holds. It will not automatically contain continuous final character animation, dialogue, sound design, or a purr recording.

## 1. Open PowerShell in the project directory

```powershell
Set-Location 'D:\Projects\Python\Purrcilla-Dixon-Dage-Blender'

$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Ffmpeg = 'C:\Program Files\Storyboarder\resources\app.asar.unpacked\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe'

Test-Path -LiteralPath $Blender
Test-Path -LiteralPath $Ffmpeg
python -c "import PIL, numpy; print('Pillow', PIL.__version__, 'NumPy', numpy.__version__)"
```

On the machine where this guide was written, both executable paths exist and Pillow and NumPy import successfully. Both `Test-Path` commands should print `True`.

## 2. Review the Episode 3 seed

Open `episodes/3-episode/episode03_seed.json` and confirm the title, fact, narration, runtime, and lead character.

Important naming rule: the public character name is **Purrcilla**, but her Blender objects, collections, manifest entry, and CSV action column use **Cila**. Keep `lead_character` as `Purrcilla` for display, but use names such as `CHAR_Cila`, `SPRITE_Cila`, and `cila_action` in the production scripts.

The seed currently points to this nonexistent file:

```text
references/mascot_sprites/episode03_atlases/episode03_sprite_manifest.json
```

For the first Episode 3 animatic, reuse the already prepared character atlases by changing `sprite_manifest` to:

```json
"sprite_manifest": "references/mascot_sprites/episode02_atlases/episode02_sprite_manifest.json"
```

This is the simplest option because the atlas images are reusable character assets, even though their filenames contain `EP02`. Create Episode 3-specific atlases only if you need a different curated `frame_map` or revised source artwork.

Before publication, verify the purr claim against a reliable source and word it as a modest relaxation claim, not as medical treatment.

## 3. Fill the empty Episode 3 shot list

Paste the following starter plan into `episodes/3-episode/episode03_shotlist.csv`. It retains the template's exact 26-block, 17-minute timing and uses only pose names already present in the prepared manifest.

```csv
shot,beat,start_seconds,duration_seconds,camera,description,dage_action,dixon_action,cila_action
S01,HOME_INTRODUCTION,0,45,CAM_CatEye_A,"Quiet home geography; the lap cushion waits in the shared room",IDLE,IDLE,IDLE
S02,TITLE,45,15,CAM_CatEye_A,"Title over an unhurried morning",IDLE,IDLE,IDLE
S03,NAMES_CILA,60,4,CAM_HeroPortrait_Cila,"Purrcilla looks alert but slightly unsettled",IDLE,IDLE,CURIOUS
S04,NAMES_DAGE,64,4,CAM_HeroPortrait_Dage,"Dage watches quietly from his familiar place",CURIOUS,IDLE,IDLE
S05,NAMES_DIXON,68,4,CAM_HeroPortrait_Dixon,"Dixon listens from the window",IDLE,WINDOW_REPORT,IDLE
S06,MORNING_GEOGRAPHY,72,36,CAM_PorchWide,"Establish the calm room and the lap cushion",IDLE,IDLE,IDLE
S07,CILA_FEELS_RESTLESS,108,24,CAM_HeroPortrait_Cila,"Purrcilla pauses and checks the room",IDLE,IDLE,CURIOUS
S08,CILA_APPROACHES_LAP,132,24,CAM_CatEye_A,"Purrcilla approaches the lap cushion",IDLE,IDLE,APPROACH
S09,CILA_SETTLES,156,24,CAM_HeroPortrait_Cila,"She circles once and settles into a loaf",IDLE,IDLE,LAP_LOAF
S10,FIRST_PURR,180,36,CAM_Insert_Eyes,"Her eyes soften as a gentle purr begins",IDLE,IDLE,LAP_LOAF
S11,PURR_RHYTHM,216,36,CAM_Insert_Paws,"A close view suggests the small steady rhythm",IDLE,IDLE,LAP_LOAF
S12,CILA_RELAXES,252,42,CAM_HeroPortrait_Cila,"Her posture loosens while the rhythm continues",IDLE,IDLE,LAP_LOAF
S13,QUIET_HOLD,294,42,CAM_HeroPortrait_Cila,"Protect a long quiet hold and slow blink",IDLE,IDLE,LAP_LOAF
S14,DIXON_NOTICES,336,54,CAM_WindowReport,"Dixon turns from the window toward the sound",IDLE,OBSERVE,LAP_LOAF
S15,DIXON_LISTENS,390,48,CAM_HeroPortrait_Dixon,"Dixon listens from a respectful distance",IDLE,LOOK_BACK,LAP_LOAF
S16,DAGE_NOTICES,438,42,CAM_CondoPeek,"Dage lifts his head and notices the shared calm",CURIOUS,OBSERVE,LAP_LOAF
S17,DAGE_APPROACHES,480,48,CAM_CatEye_A,"Dage moves closer without crowding Purrcilla",CURIOUS,OBSERVE,LAP_LOAF
S18,SHARED_LISTENING,528,48,CAM_CatEye_A,"All three settle into the same quiet rhythm",CURIOUS,OBSERVE,LAP_LOAF
S19,SECOND_PURR,576,60,CAM_HeroPortrait_Cila,"The purr returns after a brief pause",IDLE,IDLE,LAP_LOAF
S20,FACT_LABEL,636,54,CAM_CatEye_A,"Quiet visual fact: a cat's purr can be relaxing",IDLE,IDLE,LAP_LOAF
S21,SHARED_QUIET,690,48,CAM_CatEye_A,"All three share the calm space; no narration over the slow blink",SHARED_IDLE,SHARED_IDLE,LAP_LOAF
S22,PURR_CALLBACK,738,48,CAM_Insert_Eyes,"Purrcilla opens her eyes, then settles again",IDLE,LOOK_BACK,LAP_LOAF
S23,RECAP_RHYTHM,786,36,CAM_Insert_Paws,"The sound is soft, steady, and repeated",IDLE,IDLE,LAP_LOAF
S24,RECAP_RELAXATION,822,36,CAM_CatEye_A,"The room has become visibly calmer",IDLE,IDLE,LAP_LOAF
S25,CILA_CHOOSES_LAP,858,36,CAM_HeroPortrait_Cila,"Purrcilla chooses the lap cushion again",IDLE,IDLE,LAP_LOAF
S26,SHARED_FINAL_FRAME,894,126,CAM_CatEye_A,"Purrcilla rests while Dixon and Dage remain nearby in a long final hold",SHARED_IDLE,SHARED_IDLE,SHARED_IDLE
```

The required column order is exact. The last shot must end at 1020 seconds:

```text
894 + 126 = 1020 seconds
1020 seconds × 24 fps = 24,480 frames
```

Every value in an `*_action` column must exist in that character's manifest `frame_map`, or be an extra action created by the builder. The starter CSV deliberately stays within the current maps.

## 4. Copy the Episode 2 pipeline as an Episode 3 starting point

Keep the new scripts at the project root. This lets them resolve the template and shared `references` directory consistently.

```powershell
Copy-Item -LiteralPath 'build_episode02.py' -Destination 'build_episode03.py'
Copy-Item -LiteralPath 'render_episode02_preview.py' -Destination 'render_episode03_preview.py'
Copy-Item -LiteralPath 'make_episode02_contact_sheet.py' -Destination 'make_episode03_contact_sheet.py'
Copy-Item -LiteralPath 'verify_episode02.py' -Destination 'verify_episode03.py'
```

Do not run these copies until the hard-coded Episode 2 behavior has been replaced.

## 5. Convert `build_episode03.py`

Work through this checklist instead of relying on a blind search-and-replace.

### 5.1 Load the nested Episode 3 data

At the top of the script, keep `ROOT` as the project root and add an episode directory:

```python
ROOT = Path(__file__).resolve().parent
EPISODE_DIR = ROOT / "episodes" / "3-episode"
SEED = json.loads((EPISODE_DIR / "episode03_seed.json").read_text(encoding="utf-8"))
MANIFEST = json.loads((ROOT / SEED["sprite_manifest"]).read_text(encoding="utf-8"))
with (EPISODE_DIR / SEED["shotlist"]).open(newline="", encoding="utf-8") as handle:
    SHOTS = list(csv.DictReader(handle))
```

Use these output identifiers:

```python
OUTPUT = ROOT / "Purrcilla_Dixon_Dage_EP03_Purr.blend"
SETUP_VERSION = "EP03_Purr_v1"
LAP_CENTER = Vector((-1.0, -0.25, 0.0))
```

### 5.2 Replace the cardboard box with the Episode 3 prop

Delete the box walls, box flap, flap keyframes, and old cardboard-box hiding logic from `make_box()`. Replace the function with a simple `make_lap()` or cushion stand-in that:

- creates collection `SET_LapStudy`;
- creates root object `PROP_Lap` at `LAP_CENTER`;
- adds one or more soft cuboids for a cushion or blanket;
- uses new names beginning with `EP03_`;
- records a role such as `Episode 03 quiet lap and purr study`.

The project contains no human character. Treat `PROP_Lap` as a clearly framed cushion/blanket stand-in unless you intentionally add a human lap asset.

To make the purr visually readable in a silent review, add one subtle cue such as a small chest/shoulder motion, a gently pulsing cushion, or restrained purr-wave graphics. Keep the motion quiet; do not make it look like shaking.

### 5.3 Recompose cameras for Purrcilla

Update `configure_cameras()` so that:

- `CAM_HeroPortrait_Cila` is the primary portrait;
- `CAM_Insert_Eyes` frames her face and slow blink;
- `CAM_Insert_Paws` frames her chest/front paws and cushion;
- wide cameras include the lap study and leave room for Dixon and Dage;
- any camera animation copied specifically for Dixon and the box is removed or rewritten.

The CSV can reuse the existing camera names, but their transforms should be keyed for Episode 3 compositions.

### 5.4 Keep the reusable sprite system

Retain `sprite_material()`, `create_sprite()`, constant sprite-frame interpolation, camera-facing constraints, and the Dage front-neck-patch validation. Use `references/mascot_sprites/Dage_Mascot_Idle.png` and `references/mascot_sprites/Dage_Sprite_Sheet.jpg` as the authoritative Dage references. His muzzle and chin remain white; the irregular black patch follows the front of his neck within the white ruff.

For the starter CSV, the existing manifest pose names are enough. If you later add actions named `PURR`, `SLOW_BLINK`, or `RELAX`, add their frame indices to the manifest's `frame_map`, then make sure `create_sprite_actions()` builds those actions. Any newly selected Dage frame also needs a verified entry in `dage_neck_patch.py`.

Rename generated Episode 2 identifiers to Episode 3 identifiers, including:

- controllers, materials, NLA tracks, action metadata, and root-motion actions;
- marker, card, and camera-target prefixes;
- text objects and beat-sheet text block;
- the active editorial track from `EP02_BEATS` to `EP03_BEATS`;
- scene metadata and the idempotency property.

Do not rename the shared `CHAR_Cila`, `CHAR_Dixon`, `CHAR_Dage`, `SPRITE_*`, template camera, or `EP01_BEATS` identifiers.

### 5.5 Rewrite controller motion

In `animate_controllers()`:

- place Cila near the lap at the start, move her onto it around 132–156 seconds, and keep her settled for the purr blocks;
- keep Dixon at the window until his observation block, then move him to a respectful nearby position;
- keep Dage at his home position until his notice/approach blocks;
- key all three into the shared final composition.

The starter CSV does not require special walking sprite sequences. Controller location keys can provide the animatic movement while sprite poses remain stepped.

### 5.6 Rewrite editorial, text, audit, and save logic

Make these required changes:

- create and audit `EP03_BEATS`, while keeping the original `EP01_BEATS` muted and preserved;
- create markers named `EP03_S01_...` through `EP03_S26_...` and bind each marker to its CSV camera;
- create `EP03_FACT_LABEL` and `EP03_OPTIONAL_NARRATION` in `NARRATION_TEXT_OFF`;
- leave `NARRATION_TEXT_OFF` hidden in viewport and render by default;
- require `SET_LapStudy` and `PROP_Lap`, not the box collection and prop;
- set the scene name to `EP03_Purr`;
- write `episode03_setup_version`, Episode 3 scene properties, and `episode_number = 3`;
- call `make_lap()` from `main()`;
- save only to `Purrcilla_Dixon_Dage_EP03_Purr.blend`;
- retain the `--overwrite` guard so an existing output is not replaced accidentally.

The script should still reject a shot list unless it has 26 rows and ends at 1020 seconds.

### 5.7 Search for leftover Episode 2 logic

```powershell
rg -n 'EP02|episode02|Cardboard|cardboard|Box|box|flap' build_episode03.py
```

Review every match. A leftover comment is harmless, but a leftover object name, verification condition, seed path, track name, or prop animation can make the Episode 3 file inconsistent.

Do not globally replace `Dage`; he remains a supporting character and his front-neck-art checks must remain intact.

## 6. Convert the preview and contact-sheet scripts

In `render_episode03_preview.py`:

- change the output directory to `preview_frames/episode03_purr`;
- rename console labels from `EP02_PREVIEW` to `EP03_PREVIEW`;
- choose representative Episode 3 timestamps, for example 118, 168, 195, 270, 360, 500, and 920 seconds;
- use descriptive filenames such as `cila_restless.png`, `cila_settles.png`, `first_purr.png`, `cila_relaxes.png`, `dixon_listens.png`, `shared_listening.png`, and `shared_final.png`;
- render the optional fact label at approximately 660 seconds;
- keep the 640×360 Eevee settings for fast inspection renders.

In `make_episode03_contact_sheet.py`:

- point `FOLDER` at `preview_frames/episode03_purr`;
- update `ITEMS` to the exact new preview filenames;
- write `EP03_storyboard_preview.png`;
- update the script description and printed messages.

## 7. Convert the verifier

In `verify_episode03.py`, load the seed and shot list through `EPISODE_DIR` just as the builder does. Then update the checks to require:

- scene `EP03_Purr`;
- `SET_LapStudy` and `PROP_Lap`;
- 26 `EP03_BEATS` strips and 26 bound `EP03_` markers;
- frame end 24,480 and 24 fps;
- the Episode 3 scene properties;
- all three sprites, packed atlas images, drivers, constant pose keys, and NLA strips;
- Purrcilla's expected pose at key timestamps;
- `EP03_FACT_LABEL` and `EP03_OPTIONAL_NARRATION`;
- all Episode 3 preview images and `EP03_storyboard_preview.png`.

Remove the Episode 2 flap-response test. Replace it with a check for the Episode 3 visual purr cue if one was added.

When reusing the Episode 2 manifest, find each packed image using its actual atlas filename rather than assuming an Episode 3 filename:

```python
image = bpy.data.images.get(Path(info["atlas"]).name)
```

Write the verification result to `episodes/3-episode/EP03_VERIFICATION.json`.

The template currently has five absent JPG reference paths. Either restore those source photos or report them as a separate known asset warning. Do not mistake that pre-existing reference issue for a missing packed sprite atlas.

## 8. Build Episode 3

On the first build, omit `--overwrite`:

```powershell
& $Blender --background 'Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend' --python 'build_episode03.py'
```

Expected output:

```text
Purrcilla_Dixon_Dage_EP03_Purr.blend
```

If the output already exists and you deliberately want to replace it:

```powershell
& $Blender --background 'Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend' --python 'build_episode03.py' -- --overwrite
```

The builder should never save over `Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend`.

## 9. Review the scene interactively

Open the new `.blend` in Blender 5.2.

1. Confirm the scene is `EP03_Purr`.
2. Press Numpad 0 for camera view.
3. Scrub to each `EP03_` timeline marker and confirm the camera changes.
4. Check Cila's identity, especially that she has no white mittens.
5. Check Dage's black front-neck patch wherever his neck/ruff is visible, and confirm his muzzle and chin remain white.
6. Confirm the cushion/lap does not intersect the sprites.
7. Confirm the purr cue is subtle and readable.
8. Confirm the fact/narration collection is hidden by default.
9. Play the key action sections and check that pose changes happen on shot boundaries.
10. Save only the Episode 3 file.

## 10. Render inspection stills, contact sheet, and verification

Run these in order because the verifier should check the rendered preview files:

```powershell
& $Blender --background 'Purrcilla_Dixon_Dage_EP03_Purr.blend' --python 'render_episode03_preview.py'
python 'make_episode03_contact_sheet.py'
& $Blender --background 'Purrcilla_Dixon_Dage_EP03_Purr.blend' --python 'verify_episode03.py'
```

Do not proceed to the full render until the structural checks pass, all preview images are readable, and the contact sheet tells the intended story without explanation.

## 11. Add the purr sound

The repository currently has no Episode 3 sound file or audio-mixing step. Obtain or record audio you are licensed to use, edit it into a 48 kHz master WAV, and align its purr sections with the shot list.

A practical master filename is:

```text
audio/episode03_mix.wav
```

The full episode can be rendered silently first and the WAV added during FFmpeg encoding. Keep quiet gaps and avoid running the purr continuously for all 17 minutes.

## 12. Render a short motion test

Create a frame directory and render five seconds around the first purr before committing to all 24,480 frames:

```powershell
$Blend = Join-Path (Get-Location) 'Purrcilla_Dixon_Dage_EP03_Purr.blend'
$TestFrames = Join-Path (Get-Location) 'renders\episode03_test_frames'
New-Item -ItemType Directory -Force -Path $TestFrames | Out-Null

& $Blender --background $Blend `
  --python-expr 'import bpy; s=bpy.context.scene; s.render.engine="BLENDER_EEVEE"; s.render.resolution_x=640; s.render.resolution_y=360; s.render.resolution_percentage=100; s.render.image_settings.file_format="PNG"' `
  -o "$TestFrames\frame_####" -F PNG -s 4320 -e 4439 -a

& $Ffmpeg -hide_banner -loglevel warning -y `
  -framerate 24 -start_number 4320 -i "$TestFrames\frame_%04d.png" `
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart `
  'renders\Purrcilla_Dixon_Dage_EP03_Purr_test.mp4'
```

Frames 4320–4439 cover five seconds beginning at 180 seconds. Watch this test for camera framing, sprite transparency, pose timing, purr cue readability, and flicker.

## 13. Render the full 17-minute animation

PNG sequences are safer than rendering directly to MP4: if Blender stops, completed frames remain usable. A 24,480-frame 1080p PNG sequence can require substantial time and disk space. For the animatic, 1280×720 is usually the more practical first export.

```powershell
$Blend = Join-Path (Get-Location) 'Purrcilla_Dixon_Dage_EP03_Purr.blend'
$FrameDir = Join-Path (Get-Location) 'renders\episode03_frames'
New-Item -ItemType Directory -Force -Path $FrameDir | Out-Null

& $Blender --background $Blend `
  --python-expr 'import bpy; s=bpy.context.scene; s.render.engine="BLENDER_EEVEE"; s.render.resolution_x=1280; s.render.resolution_y=720; s.render.resolution_percentage=100; s.render.image_settings.file_format="PNG"; s.render.image_settings.color_mode="RGB"' `
  -o "$FrameDir\frame_####" -F PNG -s 1 -e 24480 -a
```

For a long job, render frame ranges in chunks by changing `-s` and `-e`, for example 1–6000, 6001–12000, 12001–18000, and 18001–24480. All chunks must use the same output directory and naming pattern.

Check that the last frame exists before encoding:

```powershell
Test-Path -LiteralPath (Join-Path $FrameDir 'frame_24480.png')
```

Encode a silent H.264 MP4:

```powershell
& $Ffmpeg -hide_banner -loglevel warning -y `
  -framerate 24 -start_number 1 -i "$FrameDir\frame_%04d.png" `
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart `
  'renders\Purrcilla_Dixon_Dage_EP03_Purr_silent.mp4'
```

Or encode with the finished audio master:

```powershell
& $Ffmpeg -hide_banner -loglevel warning -y `
  -framerate 24 -start_number 1 -i "$FrameDir\frame_%04d.png" `
  -i 'audio\episode03_mix.wav' `
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -movflags +faststart `
  -c:a aac -b:a 192k -shortest `
  'renders\Purrcilla_Dixon_Dage_EP03_Purr.mp4'
```

Watch the beginning, every camera cut, both purr passages, the fact label, the final hold, and the final seconds. Keep the PNG frames until the MP4 and audio synchronization have been verified.

## Completion checklist

- [ ] Episode 3 seed points to an existing manifest.
- [ ] Shot list has 26 rows, valid actions, and ends at 1020 seconds.
- [ ] Episode 3 has its own builder, preview, contact-sheet, and verifier scripts.
- [ ] Builder starts from the template and saves a separate Episode 3 `.blend`.
- [ ] `EP01_BEATS` remains preserved and muted; `EP03_BEATS` is active.
- [ ] All 26 camera markers are bound.
- [ ] Purrcilla/Cila naming is consistent with the project's object names.
- [ ] Dage's front-neck marking is valid in every selected pose; his muzzle and chin remain white.
- [ ] Fact and narration remain optional and hidden by default.
- [ ] Preview stills and storyboard contact sheet are approved.
- [ ] Verification report has no unexplained failures.
- [ ] A five-second motion test is approved.
- [ ] Licensed purr audio is mixed and synchronized.
- [ ] Frame 24,480 exists and the final MP4 plays through to the end.
