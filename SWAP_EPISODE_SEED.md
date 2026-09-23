# Swapping in a new episode seed

The template keeps the cats and home stable. Put each new episode's seed, shot list, and guide in `episodes/episodeNN/`, and keep its executable scripts in `pipeline/`. Change the discovery data and shot actions without rebuilding the character rigs.

## 1. Choose the subject

Write a one-line seed such as:

> Dage discovers why a cardboard box feels safe.

Record the audience fact in one sentence. Keep it true, small, and visually demonstrable.

## 2. Choose the lead and home base

- Cila: scout, threshold, porch, work nook, or lap.
- Dixon: window, blinds, sound, outdoor-adjacent view, or direct-to-camera reporting.
- Dage: cubby, box, shelf, soft fabric, vent warmth, or overhead observation.

## 3. Duplicate only editorial blocks

Use the shared `pipeline/episode_plan.py`, `pipeline/sprite_manifest.py`, and `pipeline/blender_sprite.py` modules for the new director. The retired Episode 3 builder under `archive/episode03/pipeline/` shows how the original NLA beats were copied, but its old Dage frame numbers and 26-shot pacing must not be reused unchanged. The new director updates:

- the `episode_seed` scene property;
- the discovery prop name and collection link;
- the relevant shot notes and camera assignments;
- the one fact label and optional narrator lines;
- the cause-and-effect animation in the experiment block.

Target about 90 seconds. Let the script determine the exact duration within 60–120 seconds; do not stretch a short idea to fill the upper limit. Use a quick hook, one clear experiment, a payoff, and a brief ending. Review any shot longer than eight seconds for visible motion, changing expression, sound, or a purposeful dramatic reason. Split an overlong script into more than one episode. A replacement Episode 3 must set `"runtime_policy": "short"` in its seed so the retired four-minute policy does not apply.

The retired Episode 3 renderer held one still frame for each shot. Do not use that shot-hold method for a new episode: render continuous character/camera motion and review playback, not only contact sheets. Plan a visible change or meaningful action every few seconds without forcing a cut during a good performance.

Before building, run `python pipeline/asset_audit.py` and validate the seed and shot list through `pipeline/episode_plan.py`. Every shot must start when the previous one ends; the total must match `runtime_seconds`. Point the new seed's `sprite_manifest` to `references/mascot_sprites/current_sprite_manifest.json`; use `pipeline/sprite_manifest.py` to select occupied Dage cells and `pipeline/blender_sprite.py` for the 8×11 UV layout.

## 4. Preserve cat identity

Do not share materials between Cila and Dixon. Dixon must retain warm chest color, white mittens, larger round eyes, and the vertical window pose. Cila must retain the cooler compact gray-brown silhouette without white mittens. Dage alone gets longhair volume and black-and-white tuxedo markings. His muzzle and chin remain white; his natural irregular black fur patch belongs along the front of the neck within the white ruff. `references/mascot_sprites/Dage_SpriteSheet.png` is the source of truth for new Dage poses; use the idle PNG and supplied JPG as supplementary references. Inspect chosen cells at full resolution. The check sites in `pipeline/dage_neck_patch.py` apply only to the historical 7×10 atlas.

## 5. Add the visual lesson

Use the simplest readable sequence:

1. Cat notices.
2. Cat tests with look/sniff/paw/body.
3. The object changes in response.
4. A second cat tries a different angle.
5. A quiet shared use confirms the idea.

For labels, duplicate items in `NARRATION_TEXT_OFF`, rename the label, and leave the collection hidden until the narration/text pass is approved.

## 6. Review

Check every episode for:

- no unexplained still holds; every beat should advance character, action, or understanding;
- continuous animation in the final video, checked in motion rather than only as stills;
- slow blink protected from narration;
- no slapstick cruelty or dangerous props;
- one clear true fact;
- enough modular shots to tell the script clearly, often around 12–18 for a 90-second episode, without forcing a fixed shot count;
- a final shared frame with all three cats.
