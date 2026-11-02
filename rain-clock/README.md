# 비를 세는 창 · Rain Clock

A virtual desk-scale kinetic art study: a small amber refuge inside two gentle fields of rain. It counts a feeling, not seconds.

## Design
- Midnight enamel shelter and frame; champagne brass paths; celadon rain beads.
- Two concentric paths rock slowly out of phase around the warm window.
- Eight-second seamless pose cycle, 96 frames at 12 fps. Frame 97 equals frame 1 and is excluded from the loop.
- All geometry is original and generated locally. No external assets.

## Files and reproducibility
- `rain_clock.blend`: editable scene, named geometry, materials, lights, camera and keyframes.
- `build.py`: complete procedural source, Blender 4.3.2.
- Build: `blender -b -t 2 --python build.py`
- Still: append `-- --still` (800 × 800, 24 samples).
- Loop frames: append `-- --loop` (480 × 480, 8 samples, every other frame); encode at 6 fps for eight seconds.

The sculpture is a **virtual design study**, not a functional clock or a proven mechanism. Animation is artistic keyframing, not physics. Bearings, motors, power, clearances, stability and manufacturability have not been designed or tested. No hardware or purchase is required.

The duplicate GIF and intermediate frames/logs are omitted from this source checkpoint. Preview PNG workspace-path metadata is removed without changing image pixels. Saved file-browser/render paths are relative.

## Verified output
- `rain_clock_still.png`: 800 × 800, visually reviewed.
- `rain_clock_loop.mp4`: 480 × 480, 48 frames at 6 fps, eight seconds.
- Opposite-phase animation frames visually reviewed; exact animation endpoint equality tested.
- Still render: 20.25 s; loop render: 114.08 s; two CPU threads.
- Denoising is disabled because this local Blender build lacks OpenImageDenoise; previews retain mild low-sample grain.
- `verification.json`: scene, motion, visual-review and media checks.

## Source verification
Run `blender -b -t 2 rain_clock.blend --python verify.py` for geometry/motion checks. This regenerates `verification.json` with `render_verified: false`; visual review must be recorded separately. No external assets, textures, fonts or music are required.
