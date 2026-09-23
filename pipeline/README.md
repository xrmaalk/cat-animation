# Production scripts

Run scripts from the repository root, passing their path under `pipeline/` to Blender or Python. Paths inside scripts resolve relative to the repository root.

Run `python pipeline/director.py check` for the read-only current-asset preflight. Add `--episode NUMBER` after a new episode's seed and shot list exist. The director targets 90 seconds, allows 60–120 seconds when the script warrants it, and flags shots over eight seconds for pacing review. It does not create an episode until its subject and script are chosen.

- `episode_plan.py` is the shared timing and continuity gate for new episodes. It preserves legacy timing only for historical plans.
- `asset_audit.py` checks the current source hashes, atlas geometry, and occupied frames before creating a new episode. Run `python pipeline/asset_audit.py` from the project root; `--historical` checks the Episodes 2–3 atlas separately.
- `sprite_manifest.py` loads the current manifest and rejects empty cells. `blender_sprite.py` creates grid-independent sprite materials and correctly proportioned planes for new directors.
- `prepare_episode02_sprites.py` rebuilds only the historical 7×10 atlases when all historical source sheets are available. It does not touch Dage's current 8×11 source.
- The retired Episode 3 builder, preview, verifier, and renderer are under `archive/episode03/pipeline/`. They use old Dage frame numbers and must not be copied unchanged into a new director.
- In particular, the archived video renderer repeats one still per shot; new videos need continuously rendered frames and a playback pacing review.
- `dage_neck_patch.py` validates sampled frames in the historical 7×10 Dage atlas. For the current 8×11 source, visually review selected poses against the approved sheet; `dage_chin_mark.py` only supports older scripts.
- Episode 1, Episode 2, and mascot-short scripts remain here for rebuilding or checking those historical scenes.

Episode story inputs and reports live under `episodes/episodeNN/`; source artwork and atlases live under `references/`; the Blender scenes stay at the project root; encoded video stays under `renders/`.
