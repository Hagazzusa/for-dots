# 잠깐 멈춘 길 / A Place to Pause

One human-scale art-direction pass on the existing **terrain seed 1107**, separate from the canonical road artwork and seeded numerical study. A warm bench in the lower-left invites a pause; the road recedes through sage ground toward cool blue distance, with open sky and empty ground providing breathing room.

**Road, terrain and all original non-bench geometry remain unchanged.** Camera, lighting, sky and materials were art-directed; the six existing bench parts were moved/rotated together onto one new local stone pad. No extra decorative props were added. No people, vehicles, forest or external assets. The source's simple low-poly geometry remains intentionally visible rather than disguised as a photoreal landscape.

## Deliverable

- `a_place_to_pause.png`: final 900×600 still, Cycles CPU, 128 samples, two threads, no denoising (the installed Blender lacks OpenImageDenoise support).
- `a_place_to_pause.blend`: native-compressed editable scene.
- `build.py`: portable hero build; consumes `landscape.py` and `profiles.json`.
- `build_variant.py`: frozen original seeded geometry generator, retained as the independent comparison fixture—not the hero entry point.
- `check_geometry.py`: reconstructs source seed 1107 in memory, reopens the hero, and compares all mesh-object geometry and transforms.

```sh
blender -b -t 2 --python build.py -- --seed 1107 --save-blend
blender -b -t 2 --python check_geometry.py
```

Tested Blender 4.3.2. No SciPy is required to rebuild this artwork from its stored profile. Output paths resolve beside these scripts. The source profile is the previously verified virtual 6% aesthetic alternative, not a civil-road design; its free endpoints, finite sampling and terrain-extension limitations still apply.

## Art direction and verification

Camera is approximately standing eye-height above the chosen roadbed, near the existing pull-off, using a 32 mm lens. The material changes separate warm wood/gravel from cool charcoal asphalt and distant blue hills. A Nishita sky and low amber sidelight replace the original uniform brown world. No depth-of-field blur hides road geometry. The initial render read as a bench on a continuous asphalt apron. A bounded correction moved the bench off that apron onto a separate pad with a visible grass gap, and turned it outward toward the landscape. Superseded candidates are omitted from this source checkpoint.

Geometry verification checks **165 mesh objects**, retaining all original local vertices/topology. **159** original objects retain geometry/transforms/bevel settings; the **6** bench parts allow only transform changes, and exactly **one** local pad is added. Materials, camera and lighting are deliberately excluded because they are the authorized edits. The saved scene also retains all-face orientation checks and **4,200** road/terrain BVH clearance samples with zero misses/intersections. Sampled cut/fill remains **1.075 / 1.215 virtual m**; this denotes vertical depth, not volume. These checks are not physical-road safety certification.

Official sky API: [Blender 4.3 ShaderNodeTexSky](https://docs.blender.org/api/4.3/bpy.types.ShaderNodeTexSky.html). The analytic geometry and seeded terrain inputs remain local and editable; source provenance and hashes are recorded separately. All earlier study folders remain unchanged.

## Separate pedestrian stop correction

The final bench stands on a **2.4×3.2 m** stone/gravel-colored pad beyond the outer shoulder, facing approximately positive X, away from the road. `verify_stop.py` tests the pad rectangle against **every actual road and shoulder quad in XY** using separating-axis tests, not just distance from the analytic centerline. Minimum pad separation is **2.971 m from asphalt** and **1.959 m from the shoulder**, leaving a visible grass strip. All six bench meshes lie entirely inside that disjoint pad footprint.

Both feet meet the pad top within **0.002 mm** numerical tolerance. At **441** support samples the underside follows the actual terrain with **1.64–2.01 mm** numerical separation; the flat pad top stands **3.50–10.18 cm** above local ground. This thin near-contact tolerance prevents coincident surfaces; it is not a suspended platform. The checks do not prove every unsampled point or certify road/pedestrian safety.

`check_geometry.py` and `verify_stop.py` verify the saved scene. Geometry provenance now reads **road/terrain unchanged, local bench/pad adjusted**. To repeat the independent stop check:

```sh
blender -b a_place_to_pause.blend -t 2 --python verify_stop.py
```

## Portable checkpoint

PNG text metadata is omitted without changing decoded pixels. Saved Blender browser/render paths are relative. Logs, caches and superseded candidates are excluded; `checksums.json` identifies these publication copies. Source fixtures and numerical validation are unchanged. The original [Seeded Roadscapes study](../seeded-roadscapes/README.md) remains separate.
