# Rain Clock · rear axle versus rim guides

## Decision from this bounded concept pass

**A rear axle preserves the calm frontal composition better than the visible rim guides, but it is not an invisible or mechanically validated replacement.** Both hubs hide head-on. The inner spokes emerge beside the window, the inner hub peeks above the roof from three-quarter view, and long forward braces become visible.

Keep this as an alternative visual/load-path baseline. Do not continue refining rim-guide escape grids just because they were inconclusive, and do not call this axle design manufacture-ready. The next design choice is whether the visible side braces and rear depth are acceptable—and whether the hubs can be brought closer to the moving rings without changing the window's identity.

## What changed / what stayed

The prior FreeCAD study supplies the fixed window, frame, 19 beads, ring radii, front ring planes and manual tabs. No earlier files were edited.

- Replace six rim rollers, their posts and follower logic with **two independently rotating hub envelopes on one stationary shaft**.
- Outer hub center Y=47 mm; inner Y=64 mm. No coupled shaft or automatic phase linkage is implied.
- Two narrow downward spokes per hub: outer ±3°, inner ±45° relative to downward vertical.
- Forward links connect spokes to the existing front rings: **97 mm outer / 144 mm inner**.
- Two short bearing/bushing envelopes per hub, plus front/rear collar envelopes. These are not selected bearings, fits, fastening methods or load ratings.
- Rear base depth grows from the rim study's 210 to **220 mm**; original artistic scale is still an invented 100 mm per Blender unit.

The original very thin artistic ring wire is not restored here: the current 8×4 mm nominal tracks are retained so the comparison isolates support architecture.

## Why the inner spokes cannot be completely hidden

The ring axis is at Z=210 mm, close to the top of the fixed window. The canopy hides a rear hub in frontal projection, but not from every elevated side view.

The outer ring's low attachment points can pass **below** the window through the original oscillation range. For the smaller inner ring, narrow downward attachment points sit inside the window's body. Forward links there would pass through the window. Spreading its spokes to ±45° moves the links to the sides, avoiding the body but exposing short diagonal segments. No invisible connection was assumed.

## Evidence

- **71 valid solids**, saved in `rear_axle_alternative.FCStd` and reopened.
- **680 exact support/window intersection and distance checks**: 17 angles per ring over ±8.59° outer / ±10.89° inner. Tested spokes, forward links and hubs against the fixed shelter/pane/canopy/sill. No intersections; smallest tested distance **1.664 mm**, outer forward link to shelter. Sampled checks are not a complete all-pair or continuous swept-volume proof.
- Nominal-pose window-occlusion ray samples: both hub samples fully hidden frontally (144/144 each). Three-quarter samples hide 127/144 outer and 88/144 inner. These are **sampled points against window bounding boxes, not percentages of image area**.
- Front spoke-centerline samples hidden: 96/102 outer and 72/102 inner. Long links can project end-on as small features frontally but become prominent from the side; point counts alone are not an aesthetic score.
- `rear_axle_front.png` and `rear_axle_quarter.png` were visually inspected. Both views retain the open upper rings and warm window; the quarter view honestly exposes the braces and hub cap. Render cost: **20.69 seconds total**, two CPU threads, two 900×800 images, 16 samples each.

## Practical comparison

| Question | Rim-guided study | Rear-axle alternative |
|---|---|---|
| Frontal appearance | Six wheels and guide hardware visible | Hubs hidden; two small diagonal spoke segments remain |
| Three-quarter appearance | Guide posts and depth stack visible | Long braces and inner hub cap visible |
| Constraint architecture | Ring form, guide alignment, follower return and flange capture interact | Two fixed-axis revolute hub concepts; no rim-running contact |
| Axial retention | Rim-flange escape/capture unresolved | Retention concentrated at hub collars, but fastening/strength still unspecified |
| Out-of-round decorative ring | Directly changes guide contact | No longer a running surface; still changes clearance and balance |
| Weight/moment concern | Beads are 14 mm ahead of the running track | Beads are **111 / 158 mm ahead of hubs**; long forward links are not stiffness-validated |
| Manual operation | Existing front tabs; independent rings | Same tabs and independence; hand torque and balance unknown |
| Access | Exposed guides easy to inspect | Rear assembly/service access required; fixed window hides hubs |

**The axle's load leverage is a serious trade-off.** The 111/158 mm figures are bead-component lever arms, not the full assembly's COM or a calculated force. Hub/spoke/link/track masses are unknown. No stiffness, shaft deflection, bearing life, drag, torque, axial retention capacity or safe hand operation was established. The thin modeled spokes and 6 mm shaft diameter are visual envelopes—not recommended hardware sizes.

The general concepts of radial support and axial location are distinguished in [SKF's bearing-arrangement guidance](https://www.skf.com/binaries/pub12/Images/0901d1968013be94-SKF-bearing-maintenance-handbook---10001_1-EN%281%29_tcm_12-463040.pdf). No SKF bearing or rating is selected or implied here. Our geometry and trade-off judgments remain original virtual-design work.

## Files / reproduction

- `rear_axle_alternative.FCStd`: editable named solids.
- `build_alternative.py`: rebuild through `/usr/bin/python3`; reads the unchanged parent `rain_clock_manual.FCStd`.
- `geometry_comparison.json`: checks, dimensions and occlusion samples.
- `render_views.py`: after building, run `blender -b -t 2 --python render_views.py`.
- `rear_axle_front.png`, `rear_axle_quarter.png`: verified local previews.

`preview_mesh.json` is temporary and regenerated by the build. No purchases, physical fabrication, uploads or publication occurred.
