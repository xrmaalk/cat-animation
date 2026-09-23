# Codex Prompt CatAnimation Blender project

You are working on my existing Catanimation Blender project.

Your task is to create a new episode using the existing SWAP_EPISODE_SEED.md workflow and integrate the newly generated 64-frame character spritesheets for Cila, Dixon, and Dage.

Do not rebuild the entire project. Preserve the existing template, Episode 01, character identities, cameras, environments, timing structure, and reusable NLA organization.

## Primary objective

Create a new test episode:

Title:
Dage Discovers Why a Cardboard Box Feels Safe

Episode seed:
Dage discovers why a cardboard box feels safe.

Audience fact:
Enclosed spaces can help cats feel protected because they provide predictable boundaries and reduce exposure.

Lead character:
Dage

Supporting characters:
Dixon and Cila

Discovery prop:
PROP_CardboardBox

Discovery collection:
SET_BoxStudy

The new episode should follow the visual lesson from SWAP_EPISODE_SEED.md:

1. A cat notices something.
2. The cat tests it through looking, sniffing, pawing, or entering.
3. The object responds through a visible change in position or use.
4. A second cat approaches from a different angle.
5. All three cats share a quiet final frame confirming the idea.

## Step 1 — Inspect the existing project first

Before changing anything:

1. Inspect the current working tree and preserve all existing user changes.
2. Locate:
   - SWAP_EPISODE_SEED.md
   - the existing Blender .blend file
   - Episode 01 scene or collection
   - Blender Python scripts
   - existing character collections
   - existing NLA actions
   - cameras
   - narration/text collections
   - generated character spritesheets
3. Do not assume attachment paths or filenames.
4. Search the project for all PNG, JPG, and Blender files before making changes.
5. Do not overwrite the original .blend file.
6. If the actual generated spritesheets are not available locally, do not fabricate replacement assets. Report the exact missing files and continue only with safe integration scaffolding.

The current project conventions include collections and cameras similar to:

Collections:

CHAR_Cila
CHAR_Dixon
CHAR_Dage
NARRATION_TEXT_OFF

Cameras:

CAM_CatEye_A
CAM_HeroPortrait_Cila
CAM_HeroPortrait_Dage
CAM_HeroPortrait_Dixon
CAM_WindowReport
CAM_CondoPeek
CAM_PorchWide
CAM_Insert_Paws
CAM_Insert_Eyes

Preserve these names wherever existing actions or scene logic depend on them.

## Step 2 — Create a non-destructive Episode 02

Create a new scene, collection, or duplicated .blend file using a clear name such as:

EP02_Cardboard_Box

Do not modify the visual content or timing of Episode 01.

Keep the existing:

- home environment
- lighting
- render settings
- frame rate
- camera system
- beat timing
- reusable actions
- character collection structure
- narration/text organization

Only change the editorial data required for Episode 02:

- episode_seed
- discovery prop
- discovery collection
- shot notes
- camera assignments
- fact label
- optional narration lines
- experiment animation
- sprite-specific character actions

Add or update scene properties using clear names such as:

episode_number = 2
episode_title = "Dage Discovers Why a Cardboard Box Feels Safe"
episode_seed = "Dage discovers why a cardboard box feels safe."
discovery_prop = "PROP_CardboardBox"
discovery_collection = "SET_BoxStudy"
lead_character = "Dage"

## Step 3 — Integrate the character spritesheets

Use the generated spritesheets as actual character assets where practical.

Expected character assets include sheets for:

- Cila
- Dixon
- Dage

Do not assume that the uploaded reference JPGs are the final runtime assets. Reference images may be used to verify appearance, but the generated transparent PNG spritesheets should be used for animation.

Preserve character identity:

Dixon:

- warm chest coloring
- white mittens
- larger round eyes
- upright/window-reporting presence

Cila:

- cooler compact gray-brown silhouette
- no white mittens
- scout/threshold/lap presence

Dage:

- longhair volume
- black-and-white tuxedo markings
- cubby, box, shelf, or soft-fabric presence

Do not share materials, marking overlays, or textures between Cila and Dixon.

Create or preserve this structure:

CHAR_Cila
└── SPRITE_Cila

CHAR_Dixon
└── SPRITE_Dixon

CHAR_Dage
└── SPRITE_Dage

If the existing scene expects objects or collections named CHAR_Cila, CHAR_Dixon, or CHAR_Dage, do not rename them. Add sprite objects inside the existing structure or create a compatibility layer.

## Step 4 — Validate the spritesheets

Inspect each spritesheet before using it.

Confirm:

- image dimensions
- transparent alpha channel
- consistent canvas size
- consistent character scale
- consistent floor or body anchor
- expected frame grid
- absence of unwanted background pixels

The generated sheets are expected to contain 64 frames arranged in an 8×8 grid.

Do not hardcode this assumption without checking. If the sheet is 8×8, use:

column = frame_index % 8
row = frame_index // 8

For example:

frame 0 = column 0, row 0
frame 8 = column 0, row 1
frame 63 = column 7, row 7

If the actual grid differs, detect and document the real layout.

## Step 5 — Build the sprite material

For each character:

1. Create a transparent plane or equivalent sprite card.
2. Apply the character’s spritesheet as an image texture.
3. Connect the texture alpha to the material alpha.
4. Use nearest/closest texture interpolation so frames remain crisp.
5. Configure the material for transparent rendering.
6. Align the character’s feet or body anchor with the environment floor.
7. Ensure all characters face the camera correctly.
8. Keep the character scale consistent between Cila, Dixon, and Dage.

Use UV mapping, a Mapping node, or an equivalent driver-based system to display one frame from the sheet at a time.

Do not interpolate between unrelated sprite frames.

## Step 6 — Add a reusable sprite_frame property

Each sprite character should have a custom property such as:

sprite_frame = 0

Use that property to control the visible spritesheet frame.

Create a reusable mapping or driver system so that changing sprite_frame changes the displayed cell in the spritesheet.

Use constant interpolation for sprite-frame keyframes.

Do not scatter hardcoded UV offsets throughout individual actions. Keep the frame mapping centralized and reusable.

If necessary, create a Blender text block, JSON data block, or clearly named Python dictionary containing the frame mapping.

Example structure:

SPRITE_FRAME_MAP = {
"idle": 0,
"curious": 8,
"sniff": 16,
"paw_test": 24,
"enter_box": 32,
"curl_in_box": 40,
"look_back": 48,
"shared_idle": 56
}

Do not assume these exact frame numbers represent the correct poses. Inspect the sheets and replace the values with the correct frame indices.

## Step 7 — Create sprite-specific actions

Create reusable actions with clear names, such as:

ACT_Cila_IDLE
ACT_Cila_CURIOUS
ACT_Cila_APPROACH
ACT_Cila_LAP_LOAF

ACT_Dixon_IDLE
ACT_Dixon_CURIOUS
ACT_Dixon_WINDOW_REPORT
ACT_Dixon_LOOK_BACK

ACT_Dage_IDLE
ACT_Dage_CURIOUS
ACT_Dage_SNIFF
ACT_Dage_PAW_TEST
ACT_Dage_ENTER_BOX
ACT_Dage_CURL_IN_BOX

These actions may animate:

- sprite_frame
- position
- rotation
- scale
- visibility
- slight camera-facing movement

If the existing NLA system animates 3D bones, do not silently assume those actions will animate the sprite planes. Either:

1. retain the 3D actions as a reference implementation, or
2. create equivalent sprite-specific actions and use them in the Episode 02 NLA strips.

Make the choice explicit in the implementation notes.

## Step 8 — Build the Episode 02 shot sequence

Use the existing Episode 01 beat structure and timing wherever possible. Do not turn the episode into one continuous take.

Create or duplicate modular shot blocks similar to:

EP02_01_Home_Introduction
EP02_02_Dage_Notices_Box
EP02_03_Dage_Approaches
EP02_04_Dage_Sniffs_Box
EP02_05_Dage_Paw_Test
EP02_06_Dage_Enters_Box
EP02_07_Dage_Rests_Inside
EP02_08_Dixon_Observes
EP02_09_Dixon_Window_Report
EP02_10_Cila_Approaches
EP02_11_Cila_Investigates
EP02_12_Dage_Exits
EP02_13_Dage_Returns
EP02_14_Fact_Label
EP02_15_Shared_Final_Frame

Use the existing camera conventions:

- Dage discovery: CAM_CondoPeek or CAM_HeroPortrait_Dage
- Dixon observation: CAM_WindowReport or CAM_HeroPortrait_Dixon
- Cila approach: CAM_PorchWide or CAM_HeroPortrait_Cila
- paw/sniff detail: CAM_Insert_Paws or CAM_Insert_Eyes
- final group frame: CAM_CatEye_A or the appropriate existing wide camera

Preserve the existing episode pacing. Keep long observational holds and protect slow blinks from narration interruptions.

## Step 9 — Add narration and fact text

Duplicate the appropriate entries in NARRATION_TEXT_OFF.

Add:

Fact label:
"Enclosed spaces can help cats feel protected."

Optional narration:

"Dage is not hiding from the world. He is choosing a space where the world feels easier to understand."

Keep the narration optional and modular. Do not permanently enable text or narration if the existing template keeps those collections hidden during animation review.

## Step 10 — Validate the result

After implementation:

1. Open the resulting .blend file in Blender.
2. Confirm Episode 01 is unchanged.
3. Confirm Episode 02 exists separately.
4. Confirm Cila, Dixon, and Dage sprite assets load correctly.
5. Confirm transparent backgrounds render correctly.
6. Confirm the sprite frame changes play correctly.
7. Confirm sprite-frame actions use constant interpolation.
8. Confirm no unrelated materials or markings were shared.
9. Confirm the characters remain correctly anchored to the floor or scene surfaces.
10. Confirm the cameras frame the sprites correctly.
11. Confirm there are no missing image paths.
12. Confirm the fact label and narration can be enabled or disabled.
13. Render a small preview containing:
    - Dage noticing the box
    - Dage entering the box
    - Dixon observing
    - Cila investigating
    - the final shared frame
14. Run the setup or import script twice, if one is created, and confirm it does not duplicate collections, materials, actions, or objects.

## Safety and preservation requirements

- Do not delete existing scenes, collections, actions, materials, or assets.
- Do not overwrite Episode 01.
- Do not overwrite the original Blender file.
- Do not replace the existing rigs without documenting the decision.
- Do not fabricate missing spritesheets.
- Do not rename existing objects that current actions or scripts reference.
- Do not use destructive cleanup commands.
- Preserve all unrelated user work.
- Keep the implementation reversible and clearly documented.

## Deliverables

Provide:

1. The new Episode 02 Blender scene or .blend file.
2. Any Blender Python setup/import script created.
3. A short implementation README explaining:
   - which files were changed
   - where the spritesheets are referenced
   - the frame-grid layout
   - the sprite-frame mapping
   - how to create the next episode
   - whether spritesheets supplement or replace the 3D rigs
4. A verification report listing:
   - successful checks
   - missing assets, if any
   - known limitations
   - exact commands or Blender steps used for testing

The implementation must remain modular so future episodes can be created by changing the seed, discovery prop, shot actions, labels, narration, and sprite-frame actions without rebuilding the characters or home environment.
