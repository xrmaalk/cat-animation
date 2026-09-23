# Episode 4 creation and rendering guide

Episode 4 is an 88-second, 24 fps continuous animatic titled **Dage Discovers Why the Sunbeam Moves**. Dage is the lead; Dixon and Purrcilla support his simple observation experiment.

The episode uses `references/mascot_sprites/current_sprite_manifest.json`. Dage is loaded directly from the approved 8x11 `Dage_SpriteSheet.png`; the historical 7x10 Dage atlas is not used.

## Build and verify

Run from the project root with Blender 5.2:

```powershell
$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'

python pipeline/director.py check --episode 4
& $Blender --background Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend --python pipeline/build_episode04.py
& $Blender --background Purrcilla_Dixon_Dage_EP04_Sunbeam.blend --python pipeline/render_episode04_preview.py
python pipeline/make_episode04_contact_sheet.py
& $Blender --background Purrcilla_Dixon_Dage_EP04_Sunbeam.blend --python pipeline/verify_episode04.py
```

The builder writes a separate `.blend`; it never overwrites the template. Add `-- --overwrite` only when deliberately rebuilding the Episode 4 output.

## Render the continuous animatic

```powershell
& $Blender --background Purrcilla_Dixon_Dage_EP04_Sunbeam.blend --python pipeline/render_episode04_video.py -- --overwrite
```

The renderer samples the continuously animated 24 fps scene every two frames and encodes a 24 fps H.264 review master. This preserves the complete 88-second timing while keeping the practical animatic render lightweight. Existing frames are reused when the `.blend` hash is unchanged.

Expected output:

```text
renders/Purrcilla_Dixon_Dage_EP04_Sunbeam_Animatic.mp4
```

Run the verifier again after the MP4 exists. Completion requires zero failed checks and a clean FFmpeg decode.
