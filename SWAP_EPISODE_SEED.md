# Swapping in a new episode seed

The template is intended to keep the cats and home stable. A new episode should change the discovery data and shot actions, not duplicate or rebuild the character rigs.

## 1. Choose the subject

Write a one-line seed such as:

> Dage discovers why a cardboard box feels safe.

Record the audience fact in one sentence. Keep it true, small, and visually demonstrable.

## 2. Choose the lead and home base

- Cila: scout, threshold, porch, work nook, or lap.
- Dixon: window, blinds, sound, outdoor-adjacent view, or direct-to-camera reporting.
- Dage: cubby, box, shelf, soft fabric, vent warmth, or overhead observation.

## 3. Duplicate only editorial blocks

Duplicate the Episode 01 NLA beat actions and update:

- the `episode_seed` scene property;
- the discovery prop name and collection link;
- the relevant shot notes and camera assignments;
- the one fact label and optional narrator lines;
- the cause-and-effect animation in the experiment block.

Set each new episode's total runtime from the script, but keep it between 180 and 300 seconds. The template is built from independent shots, so fit the beat durations to that 3–5 minute window. Split an overlong script into more than one episode instead of stretching the timeline.

## 4. Preserve cat identity

Do not share materials between Cila and Dixon. Dixon must retain warm chest color, white mittens, larger round eyes, and the vertical window pose. Cila must retain the cooler compact gray-brown silhouette without white mittens. Dage alone gets longhair volume and black-and-white tuxedo markings. His muzzle and chin remain white; his natural irregular black fur patch belongs along the front of the neck within the white ruff. Use `references/mascot_sprites/Dage_Mascot_Idle.png` and `references/mascot_sprites/Dage_Sprite_Sheet.jpg` as visual authority. Inspect the painted front-neck patch and add a check site to `dage_neck_patch.py` before selecting a new Dage frame.

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

- long still holds and believable cat timing;
- slow blink protected from narration;
- no slapstick cruelty or dangerous props;
- one clear true fact;
- enough modular shots to tell the script clearly, usually 16–30 for a 3–5 minute episode;
- a final shared frame with all three cats.
