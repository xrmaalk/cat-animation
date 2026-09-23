# Episode 5 pre-render guide

Episode 5 is an 86-second Dixon-led condensation story. This guide deliberately stops before preview or video rendering.

## Seed and performance plan

1. `episode05_seed.json` states the one-line discovery, true audience fact, lead, supporting cast, runtime, current sprite manifest, and local performance contract.
2. `episode05_shotlist.csv` divides the story into 17 contiguous shots and assigns an action plus narrative role to every character in every shot.
3. `episode05_performance_contract.json` maps those actions to character-specific multi-frame sequences and limits them to suitable roles.

## Preflight

```powershell
python pipeline/asset_audit.py
python pipeline/director.py check --episode 5
python pipeline/validate_episode05_performance.py
```

All three commands must pass before the scene is built.

## Build

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background 'Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend' `
  --python 'pipeline/build_episode05.py'
```

The builder writes `Purrcilla_Dixon_Dage_EP05_Condensation.blend` and does not modify the template or Episode 4. Use `-- --overwrite` only for an intentional Episode 5 rebuild.

## Structural verification

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' `
  --background 'Purrcilla_Dixon_Dage_EP05_Condensation.blend' `
  --python 'pipeline/verify_episode05.py'
```

This pre-render verifier checks scene structure, current Dage artwork, performance roles, sprite sequences, camera markers, condensation-prop animation, and text availability. It does not require preview images or an MP4.

Stop after the verifier reports zero failures. Rendering is a separate later approval gate.
