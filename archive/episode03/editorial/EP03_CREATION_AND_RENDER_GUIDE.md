# Episode 3 creation and rendering guide

Episode 3 is a four-minute, 24 fps editorial animatic titled **Purrcilla Discovers Why a Cat's Purr is So Relaxing**. Its 26 modular shots run from 0 to 240 seconds, and the Blender scene ends at frame 5,760.

The project is an animatic/look-development pipeline. It contains camera cuts, selected sprite poses, controller motion, a lap/cushion prop, and optional title/fact cards. It does not yet include final character animation, dialogue, sound design, or a licensed purr recording.

All episodes from Episode 03 forward must run 3–5 minutes (180–300 seconds), with the exact runtime chosen to fit the script. The build, verification, and video-render scripts reject timing outside that range.

## 1. Open PowerShell in the project directory

```powershell
Set-Location 'D:\Projects\Python\Purrcilla-Dixon-Dage-Blender'

$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$Ffmpeg = 'C:\Program Files\Storyboarder\resources\app.asar.unpacked\node_modules\@ffmpeg-installer\win32-x64\ffmpeg.exe'

Test-Path -LiteralPath $Blender
Test-Path -LiteralPath $Ffmpeg
```

Both checks should return `True`.

## 2. Review the Episode 3 inputs

The current production inputs are:

- `episodes/episode03/episode03_seed.json` — title, fact, runtime, FPS, and manifest path.
- `episodes/episode03/episode03_shotlist.csv` — 26 contiguous shot blocks totaling 240 seconds.
- `references/mascot_sprites/episode02_atlases/episode02_sprite_manifest.json` — reusable prepared character atlases.
- `references/mascot_sprites/Dage_Mascot_Idle.png` and `references/mascot_sprites/Dage_Sprite_Sheet.jpg` — authoritative Dage references.

The original Dage sheet named in this episode's historical manifest is currently absent. Dage's approved 8×11 sheet is preserved as `references/mascot_sprites/Dage_SpriteSheet.png`, while this completed Episode 3 scene packs the older 7×10 atlas. The older atlas remains at `references/mascot_sprites/episode02_atlases/1.png`. Use `references/mascot_sprites/current_sprite_manifest.json` for a new episode; do not interpret the old frame numbers against the new sheet.

Purrcilla is named `Cila` in Blender objects and sprite data. Keep `Purrcilla` in viewer-facing text, but use identifiers such as `CHAR_Cila`, `SPRITE_Cila`, and `cila_action` in project data.

Dage's irregular black fur patch belongs on the front of his neck within the white ruff. His muzzle and chin remain white. Do not add a black chin spot.

## 3. Check or retime the shot plan

The CSV column order must remain:

```text
shot,beat,start_seconds,duration_seconds,camera,description,dage_action,dixon_action,cila_action
```

For every row:

1. `start_seconds` must equal the end of the previous row.
2. `duration_seconds` must be a positive whole number.
3. Each camera must exist in the template.
4. Each action must exist in that character's manifest frame map or be created by the builder.
5. The last start plus duration must equal `runtime_seconds` in the seed.
6. Total runtime must remain between 180 and 300 seconds.

The current last row ends at exactly four minutes:

```text
217 + 23 = 240 seconds
240 seconds × 24 fps = 5,760 frames
```

If a future script cannot fit cleanly inside five minutes, split it into multiple episodes instead of stretching the holds.

## 4. Build or rebuild the Episode 3 scene

For a first build:

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend' `
  --python 'pipeline/build_episode03.py'
```

To deliberately replace an existing Episode 3 build after changing the seed, shot list, or builder:

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend' `
  --python 'pipeline/build_episode03.py' -- --overwrite
```

Expected output:

```text
Purrcilla_Dixon_Dage_EP03_Purr.blend
```

The builder never saves over the Episode 01 template. It preserves and mutes `EP01_BEATS`, creates a retimed `EP03_BEATS` track, binds 26 camera markers, and sets the scene range from the seed.

## 5. Review the scene in Blender

Open `Purrcilla_Dixon_Dage_EP03_Purr.blend` in Blender 5.2 and check:

1. The scene name is `EP03_Purr`.
2. The end frame is 5,760 at 24 fps.
3. Numpad 0 enters the active camera.
4. Every `EP03_` timeline marker changes to the expected camera.
5. Purrcilla has no white mittens.
6. Dage's black patch stays on the front of his neck, while his muzzle and chin stay white.
7. The cushion/lap prop does not visibly intersect the sprites.
8. Pose changes land on shot boundaries.
9. `NARRATION_TEXT_OFF` is hidden by default.
10. The final shared composition holds through the end.

## 6. Render inspection stills and the contact sheet

Run these commands in order:

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_EP03_Purr.blend' `
  --python 'pipeline/render_episode03_preview.py'

python 'pipeline/make_episode03_contact_sheet.py'
```

The stills and contact sheet are written to:

```text
preview_frames/episode03_purr/
```

Open `EP03_storyboard_preview.png` and confirm that the story reads clearly from Purrcilla's restlessness through the shared final frame.

To rerender only one preview after a targeted adjustment:

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_EP03_Purr.blend' `
  --python 'pipeline/render_episode03_preview.py' -- --only shared_final
```

## 7. Run structural verification

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_EP03_Purr.blend' `
  --python 'pipeline/verify_episode03.py'
```

Do not render the master until the command reports zero failed checks. The machine-readable report is written to:

```text
episodes/episode03/EP03_VERIFICATION.json
```

The template may still report five absent, unpacked JPG reference paths as warnings. The packed character atlases are separate and must pass verification.

## 8. Render the practical four-minute animatic

This is the recommended project render. It renders one representative 1280×720 Eevee image for each shot, holds it for the CSV duration, and encodes a silent H.264 MP4.

```powershell
& $Blender --background `
  'Purrcilla_Dixon_Dage_EP03_Purr.blend' `
  --python 'pipeline/render_episode03_video.py' -- `
  --overwrite --ffmpeg $Ffmpeg
```

Expected output:

```text
renders/Purrcilla_Dixon_Dage_EP03_Purr_Animatic.mp4
```

The renderer derives its duration from the seed and shot list; it does not use a hard-coded 17-minute limit.

## 9. Validate the MP4

Check the encoded duration and stream properties:

```powershell
& $Ffmpeg -hide_banner -i `
  'renders\Purrcilla_Dixon_Dage_EP03_Purr_Animatic.mp4'
```

The video should report approximately `00:04:00`, 1280×720, 24 fps, H.264, and `yuv420p`.

Run a full decode check:

```powershell
& $Ffmpeg -v error -i `
  'renders\Purrcilla_Dixon_Dage_EP03_Purr_Animatic.mp4' `
  -f null NUL
```

No output means the decode completed without an error.

## 10. Optional full-frame Blender render

Use this only after the animatic is approved. Rendering all 5,760 scene frames is much slower than the shot-hold renderer.

```powershell
$FrameDir = Join-Path (Get-Location) 'renders\episode03_frames'
New-Item -ItemType Directory -Force -Path $FrameDir | Out-Null

& $Blender --background `
  'Purrcilla_Dixon_Dage_EP03_Purr.blend' `
  --python-expr 'import bpy; s=bpy.context.scene; s.render.engine="BLENDER_EEVEE"; s.render.resolution_x=1280; s.render.resolution_y=720; s.render.resolution_percentage=100; s.render.image_settings.file_format="PNG"; s.render.image_settings.color_mode="RGB"' `
  -o "$FrameDir\frame_####" -F PNG -s 1 -e 5760 -a
```

Verify the last frame before encoding:

```powershell
Test-Path -LiteralPath (Join-Path $FrameDir 'frame_5760.png')
```

## 11. Add audio when available

The repository does not currently include a licensed Episode 3 purr recording or finished mix. A practical master path is:

```text
audio/episode03_mix.wav
```

Use a 48 kHz WAV, keep intentional quiet gaps, and align purr passages with the shot list. The current animatic is intentionally silent.

## Completion checklist

- [ ] Seed runtime is between 180 and 300 seconds.
- [ ] Shot list has 26 contiguous rows and ends at the seed runtime.
- [ ] Episode 3 builds as a separate `.blend` without changing the template.
- [ ] `EP01_BEATS` is preserved and muted; `EP03_BEATS` contains 26 correctly retimed strips.
- [ ] All 26 camera markers are bound.
- [ ] Purrcilla/Cila naming is consistent.
- [ ] Dage's front-neck patch is valid in every selected pose; his muzzle and chin remain white.
- [ ] Preview stills and storyboard contact sheet are approved.
- [ ] Verification reports zero failures.
- [ ] Final MP4 is 3–5 minutes long and decodes without error.
- [ ] Licensed audio is mixed and synchronized if sound is required.
