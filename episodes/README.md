# Episode files

Each episode has its own `episodeNN/` directory for its seed, shot list, instructions, and verification report. Blender scene files stay at the repository root, and encoded videos stay in `renders/`.

| Episode | Directory | Status |
| --- | --- | --- |
| 01 | `episode01/` | Original 17-minute editorial template and timing data. |
| 02 | `episode02/` | Historical 17-minute cardboard-box animatic and source notes. |
| 03 | `../archive/episode03/` | Retired four-minute purr animatic using older Dage artwork; recoverable, not active. |
| 04 | `episode04/` | Active 88-second sunbeam story led by Dage, using the approved 8x11 Dage sheet. |
| 05 | `episode05/` | Pre-render-ready 86-second condensation story led by Dixon, with an isolated role-aware performance contract. |

For subsequent episodes, write the script first, aim for about 90 seconds, and choose contiguous shot durations totaling 60–120 seconds without padding. `pipeline/episode_plan.py` enforces the runtime range. Use `references/mascot_sprites/current_sprite_manifest.json` for new scenes; it makes Dage's updated 8×11 sheet the source of truth. Check assets with `python pipeline/asset_audit.py` before selecting poses. Historical Episode 2 and archived Episode 3 keep their older packed art.
