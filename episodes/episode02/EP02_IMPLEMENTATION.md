# Episode 02 — Dage Discovers Why a Cardboard Box Feels Safe

Open `Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend` in Blender 5.2. Its `EP02_Cardboard_Box` scene is a 17-minute, 24 fps test episode with 26 modular editorial blocks. `EP02_BEATS` is the active NLA track; the copied `EP01_BEATS` track and original actions remain in the file as muted reference data. The Episode 01 template and animated short on disk were not modified.

## Files created

| File | Purpose |
| --- | --- |
| `episodes/episode02/episode02_seed.json` | Episode title, seed, fact, narration, prop, collection, and manifest paths. |
| `episodes/episode02/episode02_shotlist.csv` | 26 shots, preserving Episode 01 start times and durations, with Episode 02 notes, cameras, and sprite actions. |
| `pipeline/prepare_episode02_sprites.py` | Validates the supplied sheets and creates clean, equal-cell atlases without changing the source PNGs. |
| `references/mascot_sprites/episode02_atlases/` | Three normalized atlases and `episode02_sprite_manifest.json`. |
| `pipeline/build_episode02.py` | Imports the atlases into the existing `CHAR_*` collections, adds the box, cameras, actions, NLA tracks, text, and scene properties. |
| `pipeline/render_episode02_preview.py` | Renders the main visual beats and an optional fact-label check. |
| `pipeline/make_episode02_contact_sheet.py` | Makes `preview_frames/episode02_box/EP02_storyboard_preview.png`. |
| `pipeline/verify_episode02.py` | Runs structural and asset checks, writing `episodes/episode02/EP02_VERIFICATION.json`. |

The new prop is `PROP_CardboardBox` in `SET_BoxStudy`. Its front flap has a keyed response to Dage's paw test. The fact label and optional narration are in `NARRATION_TEXT_OFF`; the collection stays disabled by default. When enabled, Episode 01 lower thirds remain individually hidden. The optional narration object also remains individually hidden until chosen for a narration pass.

## Sprite layout and frame control

The supplied sheets are **not 8×8**. Cila and Dage each contain 7 columns × 10 rows (70 cells); Dixon contains 7 columns × 9 rows (63 cells). All have RGBA transparency, though the original generated art has a few small colored edge specks. The preparation script detects the transparent row gutters and per-row column gaps, then repacks the original pixels into separate 7×10 atlases with 192×192 transparent cells. Dixon's tenth atlas row is blank. Each character material uses its own atlas; the three materials and textures are distinct.

`SPRITE_Cila`, `SPRITE_Dixon`, and `SPRITE_Dage` live in their existing `CHAR_*` collections. Each has a `sprite_frame` property. A material driver and centralized shader math select the atlas cell with `column = sprite_frame % 7` and `row = floor(sprite_frame / 7)`, counting source rows from the top. Nearest interpolation keeps frame edges crisp. Sprite action keys use constant interpolation. The normalized cells share a bottom anchor so the feet stay on the floor; Dage's controller rises slightly when he is inside the box.

| Character | Curated frame map, zero-based source index |
| --- | --- |
| Cila | idle 0; curious 5; approach 17; investigate 31; lap loaf 40; shared idle 0 |
| Dixon | idle 0; curious 3; observe 43; window report 6; look back 55; shared idle 0 |
| Dage | idle 0; curious 6; sniff 37; paw test 3; enter box 11; curl in box 26; look back 55; shared idle 42 |

`ACT_Dage_ENTER_BOX` cycles through source frames 9–13; `ACT_Cila_APPROACH` cycles through 14–18. The complete map, source dimensions and hashes, detected cell boundaries, and atlas paths are in `episode02_sprite_manifest.json`.

Dage's irregular black front-neck patch is painted into the revised source spritesheet, with a natural fur edge inside the white ruff; his muzzle and chin remain white. `Dage_Mascot_Idle.png` and `Dage_Sprite_Sheet.jpg` are the authoritative visual references. Blender reads those pixels directly instead of adding a geometric shader mark. `pipeline/dage_neck_patch.py` defines inspection sites for all Dage frames currently used by Episode 02 and the animated short; sprite preparation checks for dark front-neck fur and surrounding light ruff at each site. When adding a new Dage pose, inspect its neck/ruff artwork and add a check site first. To update a saved Episode 02 file without rebuilding it, run `--python pipeline/apply_dage_sprite_sheet.py` with that file open in Blender.

The sprites **replace proxy meshes for Episode 02 rendering**. The original 3D rigs, proxy roots, and their actions remain in the new file as hidden references. Sprite planes use their own NLA actions and camera-facing target; bone actions do not drive the planes.

## Rebuild and review

From the project directory, with Pillow and NumPy available to normal Python and Blender 5.2 available:

```powershell
python pipeline/prepare_episode02_sprites.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python pipeline/build_episode02.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python pipeline/render_episode02_preview.py
python pipeline/make_episode02_contact_sheet.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python pipeline/verify_episode02.py
```

The builder refuses to overwrite an existing Episode 02 file unless `-- --overwrite` is passed. Running it on an already configured Episode 02 file performs an idempotent audit and adds nothing. In Blender, use the timeline markers to move among the 26 shots; bound markers switch the active camera.

## Next episode

Reuse the source template and prepared cat atlases. Copy the seed JSON, shot list, and builder under a new episode number. Update the seed, fact, prop and collection names, shot descriptions and cameras, and per-shot sprite actions. Replace the prop-specific geometry, experiment keys, and controller movement functions in the copied builder. The home set, character collections, rigs, atlas material method, and editorial timing library can be reused.
