# 저녁으로 가는 길 / Road into Evening

A bounded original landscape study: a quiet ribbon road, soft hills, and a small bench at a widened viewpoint. No external assets, people, vehicles, game framework, or generated bitmap textures.

## Rebuild

Tested with Blender 4.3.2. Run from any directory:

```sh
blender -b -t 2 --python /path/to/quiet_road/build.py
blender -b /path/to/quiet_road/road_into_evening.blend -t 2 --python /path/to/quiet_road/check_mesh.py
```

Outputs are written beside the scripts. The build replaces only this study's output files. One still: 900 × 600, Cycles CPU, 64 samples, two threads, denoising disabled because this Blender build lacks OpenImageDenoise. Editable geometry and named materials are retained in `road_into_evening.blend`.

## Parameters and limits

- Seed: **1102**, used for original meadow stones.
- Units: **1 Blender unit = 1 virtual metre**.
- Centerline: `x(y) = 21 sin((y + 25)/46) + 0.07y`; vertical profile in `bed()` follows the original natural terrain centerline.
- Nominal normal road width: 6 m, widening to approximately 10.5 m at the pull-off.
- Roadbed blends into meadow over 40 m; asphalt is lifted only 0.045 m to prevent coincident surfaces, not suspended over unmodified terrain.
- Numerical geometry checks and virtual grade/curvature results are in `validation.json`. They are design diagnostics, **not civil-road engineering or safety standards**.
- `check_mesh.py` independently raycasts the saved road and terrain meshes at face centers and inset corners; finite sampling does not prove all-point clearance.
- This is a visual composition, not a drivable prototype, navigation mesh, physical simulation, or accessibility assessment.

## Visual review

The initial normal-offset terrain folded at large offsets and separate distant sheets overlapped. The final terrain uses a non-folding row mapping and a single continuous distant surface. Its material transitions from sage foreground to lavender distance. A later review found that an independent low road baseline still carved a continuous canal. The corrected road follows the natural centerline terrain rather than hiding the problem with a camera change. Closer framing makes the bench and pull-off readable. Superseded candidates are omitted from this source checkpoint.

Final mesh verification: 840 upward road faces, zero non-upward terrain faces, 4,200 mesh raycast samples with no misses or terrain intersections. Sampled separation is approximately 4.497–4.503 cm. Maximum virtual grade is 11.54%; minimum virtual curvature radius is 101.2 m. These finite tests are not an engineering certification.

Earthwork is measured separately from the asphalt gap: 84,941 signed final-minus-natural terrain samples give maximum cut **2.013 m** and maximum fill **1.802 m**. The 40 m smooth transition flattens the local cross section rather than excavating an independent low route. Terrain-following introduces a maximum virtual grade of 11.54%; this remains a scenic study, not a road design. The final `.blend` uses Blender native compression and was reopened for independent mesh verification, retaining all editable geometry.

## Portable checkpoint

PNG path metadata is omitted without changing decoded pixels. Saved Blender browser and render paths are relative. `checksums.json` records these publication copies, not superseded local candidates. Logs and caches are excluded.
