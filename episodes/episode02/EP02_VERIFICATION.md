# Episode 02 verification

## Successful checks

- Blender 5.2 opened `Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend`. The current `pipeline/verify_episode02.py` audit passed **98 of 99 checks**, including the revised packed Dage atlas and all eight Dage sprite actions. Its one failure concerns missing JPG reference paths listed below. Detailed results are in `episodes/episode02/EP02_VERIFICATION.json`.
- The original template and Episode 01 animated short are unchanged on disk. Git reports neither original `.blend` as modified. Existing user edits to `.gitignore` and `README.md` were preserved.
- Episode 02 has a separate `EP02_Cardboard_Box` scene in a new `.blend`, the expected seed properties, a 17:00 / 24 fps timeline, 26 bound camera markers, and 26 `EP02_BEATS` strips. The copied `EP01_BEATS` track and its actions remain present and muted.
- Cila, Dixon, and Dage each have a named sprite in the existing character collection, their own material and packed atlas, a `sprite_frame` driver, 26 sprite NLA strips, and constant sprite-frame key interpolation. The 3D rigs and proxy roots remain present.
- Source sheet hashes match the manifest. The detected layouts are 7×10 for Cila and Dage, 7×9 for Dixon; all three normalized atlases are 1344×1920 RGBA and packed into the `.blend`.
- Dage's revised sprite sheet contains a natural irregular black fur patch along the front of his neck within the white ruff; his muzzle and chin remain white. The packed atlas matches the revised file, and the obsolete shader mark and coordinate keys are gone. Every current Dage action uses a frame with an inspected front-neck patch site; sprite preparation validates dark fur within the light ruff there.
- The box flap changes angle during the paw experiment; the sprite feet remain aligned to the floor or box interior. The narration collection starts hidden, the Episode 02 fact label can be shown independently of Episode 01 lower thirds, and the optional narration remains separately disabled.
- Rendered previews show Dage noticing, testing the flap, entering and settling in the box; Dixon observing; Cila investigating; and the quiet shared final frame. The fact-label preview shows the optional text pass.
- A second run of `pipeline/build_episode02.py` on the completed Episode 02 file printed `EP02_ALREADY_CONFIGURED` with the same counts: 16 collections, 247 objects, 102 actions, and 30 materials. Nothing was duplicated.

## Missing assets

The three mascot source sheets and packed atlases are present. Five JPG photo references are currently missing from `references/`: `Cila-Curious(1).jpg`, `Cila-LAP.jpg`, `Dage-Condo.jpg`, `Dixon-Curious.jpg`, and `Dixon-Venting(1).jpg`. This is the single failing audit check. The photos are reference images; the Episode 02 sprite renders use packed atlases.

## Known limits

- This is a test animatic with key poses, root movement, camera cuts, and editorial holds across 17 minutes. It is not a fully acted 17-minute animation or a final rendered episode.
- The generated source sheets contain 70, 63, and 70 cells, rather than the anticipated 64 each. A few small colored edge specks remain in the supplied artwork; the repacking preserves them. Manual sprite cleanup would improve final delivery.
- Flat camera-facing sprite planes cannot provide 3D limb articulation or reliable physical contact in every camera angle. The paw test visually pairs a raised-paw pose with flap movement; exact paw-to-flap contact would need a dedicated frame or a separate paw layer.
- Only selected frames have curated semantic labels. Other atlas cells remain available by setting `sprite_frame` directly or expanding the manifest map.

## Commands used

```powershell
python pipeline/prepare_episode02_sprites.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python pipeline/build_episode02.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python pipeline/build_episode02.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python pipeline/render_episode02_preview.py
python pipeline/make_episode02_contact_sheet.py
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --background Purrcilla_Dixon_Dage_EP02_Cardboard_Box.blend --python pipeline/verify_episode02.py
git status --short
```

The final story preview is `preview_frames/episode02_box/EP02_storyboard_preview.png`.
