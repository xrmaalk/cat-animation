# Episode 5 manual build lesson

This is the learning route for Episode 5. The goal is not merely to produce a
working `.blend`; it is to make the scene-building pattern repeatable by hand
for Episode 6.

The automated file `Purrcilla_Dixon_Dage_EP05_Condensation.blend` is an answer
key only. Do not overwrite it. Do not run `pipeline/build_episode05.py` while
working through this lesson.

## Learning file

Open `Purrcilla_Dixon_Dage_Curious_Together_TEMPLATE.blend` in Blender 5.2 and
immediately use **File > Save As** to create:

```text
Purrcilla_Dixon_Dage_EP05_Manual_Learning.blend
```

This keeps the template, the automated Episode 5 scene, and the manual learning
scene separate. The template contains the home sets, cameras, lights, and proxy
characters needed for the lesson. The sprites can be added later, after the
episode construction skills are understood.

## How the lesson must be taught

- Work through one checkpoint at a time in Blender's user interface.
- The learner performs the clicks, selections, transforms, and keyframes.
- After each checkpoint, save and confirm the visible result before continuing.
- If a result differs from the checkpoint, diagnose that result rather than
  skipping ahead or replacing it with an automation.
- Scripts and the automated Episode 5 file may be inspected only as references.
- Episode 6 does not begin until the learner can repeat the core pattern without
  step-by-step prompting.

## Checkpoints

### 1. Safe scene and timeline

In **Output Properties**:

- Set the frame rate to **24 fps**.
- Set **Start** to `0`.
- Set **End** to `2064` (86 seconds at 24 fps).

Save the file. Scrub to frame 2064 and confirm that the time display is about
`01:26`.

The template also contains Episode 1 timeline markers. Before adding Episode 5
markers, hover over the Timeline, choose **Marker > Select All**, then
**Marker > Delete Markers**. Episode 5 must begin with a clean editorial marker
track.

Skill learned: converting story duration into a Blender timeline without a
builder script.

### 2. First three story markers

In the Timeline, add and rename these markers:

| Marker                   | Frame | Meaning                                     |
|--------------------------|------:|---------------------------------------------|
| `S01_COLD_WINDOW_HOOK`   |     0 | Dixon breathes on the cool glass            |
| `S02_TITLE`              |   120 | Title beat begins at 5 seconds              |
| `S03_DIXON_NOTICES_MIST` |   216 | Dixon notices the cloudy patch at 9 seconds |

Use the rule `frame = seconds x 24` for a marker that begins at a whole
second. Do not add the other fourteen markers until these three are correct.

Skill learned: translating a shot list into editorial timing.

### 3. Bind the first cameras

The template cameras retain long Episode 1 actions. In the manual learning copy,
select each camera before reusing it, press **F3**, run **Remove Animation**, and
confirm that only that camera is selected. Otherwise, the inherited action will
move the camera during Episode 5 playback and can place it inside the set.

Use the existing cameras in the `CAMERAS` collection:

| Marker                   | Camera                   |
|--------------------------|--------------------------|
| `S01_COLD_WINDOW_HOOK`   | `CAM_WindowReport`       |
| `S02_TITLE`              | `CAM_CatEye_A`           |
| `S03_DIXON_NOTICES_MIST` | `CAM_HeroPortrait_Dixon` |

At each marker, select the camera, hover over the Timeline, and use
**Marker > Bind Camera to Markers**. Scrub in camera view at frames 0, 120, and
216 to confirm that the active camera changes.

Skill learned: making an edit from cameras and markers instead of treating the
whole episode as one unbroken shot.

### 4. Build the cool-window experiment

Create a collection named `SET_CondensationStudy`. In it, build a simple window
from cubes:

- one thin, wide pane;
- top, bottom, left, and right frame pieces;
- one flattened circle in front of the pane for the cloudy patch.

Name the objects clearly before proceeding. The exact dimensions matter less
than a readable silhouette in `CAM_WindowReport`.

Skill learned: constructing a reusable story prop from primitives and keeping
the Outliner organized.

### 5. Animate the condensation cause and effect

On the cloudy patch:

- At frame 0, scale it almost to zero and insert a **Scale** keyframe.
- At frame 48 (2 seconds), enlarge it and insert another **Scale** keyframe.
- At frame 216 (9 seconds), make it slightly larger and insert a third Scale
  keyframe.

Play frames 0-216 in camera view. Dixon's breath should appear to create the
cloudy patch, and the patch should still be present when he notices it.

Skill learned: creating readable cause-and-effect animation with keyframes.

### 6. Animate Dixon's first performance

Use `Dixon_PROXY_ROOT` for the blocking pass. Keyframe small, deliberate changes
in location or rotation so that Dixon:

1. leans toward the glass during the hook;
2. settles during the title beat;
3. turns his attention toward the new cloudy patch in shot 3.

Keep the motion subtle and review it in real-time playback. Do not add Cila or
Dage motion yet; Dixon is the lead.

Skill learned: matching character movement to narrative role rather than moving
every character equally.

### 7. Complete the episode by repeating the pattern

After checkpoints 1-6 have been reviewed, continue through
`episode05_shotlist.csv`. For each remaining shot:

1. add its start marker;
2. bind its listed camera;
3. block the lead action;
4. animate the prop response;
5. add restrained supporting reactions;
6. play the transition from the preceding shot;
7. save.

This repetition is the transferable Episode 6 skill. The finished-sprite pass,
text pass, sound, and final render come only after the blocking edit works.

## Completion test before Episode 6

Episode 5 counts as learned when the learner can, without a build script:

- create a safe episode file from the template;
- convert seconds to frames at 24 fps;
- add and rename shot markers;
- bind a camera to each marker;
- build and organize a story prop;
- animate a visible cause and effect;
- block a lead performance and quieter supporting reactions;
- play through adjacent shots and correct a bad transition;
- explain how the same pattern will be reused for Episode 6.

Passing an automated verifier by itself does not satisfy this learning test.
