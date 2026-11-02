# Rain Clock · one proportion change: a taller foreground window

## Recommendation

**This is the strongest of the tested virtual concepts for keeping the quiet warm-window character while removing the long rotating braces.** It is not a finished mechanism. Accept that the window becomes a foreground element and deliberately hides part of the rain field. If seeing all 19 beads is essential, prefer an honestly visible hub/support instead of continuing to hide it with complicated geometry.

Only one candidate was developed: move a moderately taller window facade in front of the rings, and place each independent hub and its downward spokes directly in its ring plane. Earlier studies remain unchanged.

## Demonstrable geometric improvement

| Quantity | Rear-hub / original-window alternative | Taller foreground-window candidate |
|---|---:|---:|
| Rotating forward links | 97 / 144 mm | **0 / 0 mm** |
| Bead-plane offset from hub plane | 111 / 158 mm | **14 / 14 mm** |
| Hub center Y | +47 / +64 mm | −50 / −80 mm, matching rings |
| Window body height | 135 mm | 154.5 mm |
| Canopy top Z | 221.5 mm | 241 mm |
| Base depth | 220 mm | 210 mm |

These are coordinate differences, not force or stiffness results. Shortening the rotating lever arms is real in the model; bearing capacity and shaft deflection remain unknown.

The common stationary shaft spans 76 mm, with support envelopes near Y=−99 and −28 mm. Both hubs lie between those supports. The front support belongs to the fixed window frame/back cross-member—not the luminous pane. No shaft, bearing, collar or fastener dimensions are recommended for fabrication.

## What the facade changes

- Window body bounds: X=±56 mm, Y=−112…−102 mm, Z=77.5…232 mm.
- The top rises **19.5 mm**, while the overall circular frame stays unchanged.
- Two small fixed legs connect the window-frame envelope to the base.
- The warm four-pane appearance is restored. The rendered panel is opaque/frosted-looking, not transparent glass; real translucent materials may reveal internal silhouettes and have not been evaluated.
- Outer spokes stay narrowly downward (±3°); inner spokes narrow from ±45° to ±18° because their connections no longer have to reach around the original window body.
- Existing ring radii, 19 bead objects and right-side manual tabs remain. There is no motor, timing mechanism or phase linkage.

## Visual cost, not hidden in the recommendation

The lower rings now pass **behind** the foreground window. A conservative frontal bounding-box test at 17 sampled angles per ring found:

- Inner bead #6 completely hidden at every sampled pose.
- Inner bead #5 completely hidden at some sampled poses.
- No outer bead bounding box entirely hidden by the body, though parts of outer beads/arcs are occluded.

Both hub sample sets were hidden in frontal and three-quarter ray tests (144/144 sampled hub points per ring/view at nominal pose). All sampled inner spoke centerline points were hidden in both views. A short outer spoke portion below the window remains visible frontally. These counts are not image-area percentages or a continuous visibility proof.

The two rendered views were visually inspected. They show the actual trade: cleaner support concealment and no long side braces, but fewer visible lower beads and a more prominent window.

## Geometry checks and limits

- **71 valid named solids**, saved and reopened.
- 17 sampled angles per ring over the earlier ±8.59° / ±10.89° motion ranges.
- **3,536 moving-part/window bounding-box pairs** checked. Disjoint boxes excluded impossible intersections; **17 overlapping-box cases** used exact BRep solid intersections. No intersections were found.
- This includes moving tracks, beads, pins, tabs, spokes, hubs and bearing envelopes against the fixed shelter/pane/canopy/sill. It is not a complete all-part, simultaneous-phase or continuous swept-volume proof.
- Nominal inner-bead/facade-body axial separation is 3.4 mm. That is a model gap, not a validated fabrication tolerance or global minimum clearance.
- Mullion shapes are fused to avoid coplanar overlapping render surfaces.

No forces, bearing ratings, frame stiffness, shaft deflection, drag, balancing, collar retention, assembly method, wear, tip stability or safe hand operation were validated. The window frame would now participate in the support load path; its thin visual envelope is not a structural specification. Prior rim-guide capture results do not certify this different architecture.

## Stop here for the architecture decision

Prefer this foreground-window concept **if occluding one or two lower beads is acceptable**. Otherwise keep a visibly supported hub as an intentional aesthetic feature. Do not add more concealed linkages merely to preserve every original projection. A later authorized engineering prototype would need explicit materials, supported bearings, retention and testing; none is implied by these local illustrations.

## Files / reproduce

- `front_facade_axle.FCStd`: editable named solids.
- `build_concept.py`: run with `/usr/bin/python3`; reads the unchanged parent `rain_clock_manual.FCStd`.
- `geometry_comparison.json`: sampled collision and visibility evidence.
- `render_views.py`: after rebuilding, run `blender -b -t 2 --python render_views.py`.
- `front_facade_front.png`, `front_facade_quarter.png`: visually checked previews.

Temporary mesh exchange is regenerated by the build. No fabrication, purchases, uploads or publication occurred.
