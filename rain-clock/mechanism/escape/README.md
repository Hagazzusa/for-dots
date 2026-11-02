# Rain Clock · bounded 3D track-escape investigation

**Result: INCONCLUSIVE.** No extraction endpoint was found in either reachable sampled component. This does not establish capture, retention, safety or absence of an escape path.

| Case | Reachable grid poses | Grid poses tested | Edge midpoints tested | Collision poses | Travel-limit poses | Wall time |
|---|---:|---:|---:|---:|---:|---:|
| Approximate translation following | 72 | 250 | 71 | 160 | 18 | 85.8 s |
| Outward stuck | 142 | 332 | 141 | 190 | 0 | 127.9 s |

Total: **582 distinct grid tests + 212 admitted-edge midpoint checks**, ~214 s serial computation. No uncertain-volume classifications occurred. No physical test or geometry fix was made.

Both reached axial offsets −0.2…+0.2 mm and vertical lifts 0…1.75 mm. The approximate-following branch reached **no nonzero sampled pitch**, while the stuck branch reached −0.1…+0.1°. The former restriction may reflect the approximate follower rule and graph connectivity; it must not be described as a real follower preventing pitch.

## Question

Does an adverse outer-track pose admit a connected sampled path past the three guide flanges, comparing an idealized translation-following upper guide with a follower stuck at its outward stop?

This deliberately does **not** redesign hardware. The earlier ~0.248 mm projected lip overlap is only a warning; it is not an escape path or a retention proof.

## Actual modeled solids

- Outer track: 4 mm axial extrusion, inner radius 135 mm, outer profile `143 + 0.25 cos(3(theta−phase))` mm, adverse phase 60° with theta measured from +Z.
- Outer profile is a **720-segment polygon**; the inner bore is an analytic circle. The profile is not an exact smooth three-lobe curve. A conservative interpolation deviation bound is approximately 0.0014 mm from the supplied smooth curve (second-derivative bound 147 mm/rad² and segment angle 2π/720).
- Three full grooved roller solids: root radius 9 mm, flange radius 11 mm, overall width 10 mm, 4.4 mm axial groove, 2 mm bore.
- Lower guide centers remain fixed at 210° and 330°. Upper center is nominally at 90°, with the selected radial displacement.
- The initial ring-center and closed-follower positions are solved for the same polygon used by the BRep—not imported from the earlier finer polygon.

`escape_search_solids.FCStd` preserves this subset. It includes **real flange thickness and axial groove volume**, not only projected lip-overlap arithmetic. It is not the full sculpture.

## Finite pose family

Coordinates relative to the solved adverse pose:

- Axial Y translation: −8 to +8 mm, step 0.05 mm.
- Vertical Z lift: −0.5 to +2.5 mm, step 0.25 mm.
- Pitch about X: −6 to +6°, step 0.05°.
- Horizontal X translation, roll about Z and in-plane ring phase remain fixed.

The algorithm explores only the connected collision-free sampled component reached from the initial pose using six axis-adjacent grid neighbors. Each admitted edge also has its midpoint tested. This does **not** certify every point on a continuous edge, and can miss narrow or coordinated paths between grid nodes.

Escape endpoint: the entire track's Y bounds have passed the flange slab with 0.1 mm clearance (`Ymax < −5.1` or `Ymin > +5.1`). This is a track-subset endpoint, not sufficient by itself to establish escape of the decorated assembly.

## Follower assumptions

1. **Approximate translation following:** follower displacement equals its initial closed-contact displacement plus the ring's vertical lift. It is limited to ±1 mm travel. Pitch-dependent tracking, contact loss and forces are not solved. This is a restrictive geometric rule—not a real return mechanism or an exact three-dimensional contact constraint.
2. **Outward stuck:** upper follower is fixed at +1 mm. Lower guides remain fixed.

A no-path result with these assumptions cannot establish that a physical follower prevents escape.

## What is exact and what is approximate

OpenCascade computes BRep solid intersections for each tested pose. Those intersections use the actual finite-width root/flange solids and transformed extruded track. “Exact BRep” means exact intersection operations on the supplied model, subject to kernel/numerical tolerances—not physically exact geometry.

Classification:

- Intersection volume ≤10⁻⁹ mm³: sampled pose treated as free.
- Volume >10⁻⁵ mm³: blocked.
- Intermediate volume: uncertain and excluded from the reachable component.

Excluding uncertain contact poses makes the search conservative against claiming a free path but **can hide a real path**. It cannot support an absence proof.

The search omits beads, pins, tab, posts, frame and rear carriage. A path found here would require full-assembly validation. The omitted solids can obstruct paths, and no model of elasticity, gravity, manual force, friction or breakage is present.

## Outcome interpretation

- Found track-subset path: a candidate sampled counterexample requiring full decorated-assembly and continuous-segment checks, not automatically a physical escape demonstration.
- No endpoint reached: **inconclusive within this finite grid, pose family and follower rule**. Never “escape-proof,” “safe” or “retained under all motion.”

No physical fabrication, purchases, uploads or publication. Completed earlier checkpoints are unchanged.


## Review, deliverables and next decision

The four saved search solids reopened valid. The guide BRep was also compared against the previous nominal FreeCAD guide after translation: equal volumes and bidirectional difference volumes below 10⁻⁶ mm³. The lobed track intentionally differs from the earlier circular track and remains polygonized.

An independent reviewer checked the pose transform, guide dimensions and same-polygon initial solve. A missing phase term in the descriptive JSON metadata was corrected; the computation already used the 60° phase. Classification stops at the first uncertain obstacle, so an uncertainty would be conservative rejection rather than an exhaustive collision diagnosis. There were no such poses in this run.

- `search_escape.py`, `results.json`, `summary.json`: reproducible source, complete results and compact counts.
- `escape_search_solids.FCStd`: actual modeled track and guide BReps.
- `plot_results.py`, `reachable_components.png` / `.svg`: visually reviewed reachable-component projection, explicitly zoomed and inconclusive.

**Most informative omitted motion:** a targeted simultaneous **horizontal translation X + roll about Z**, which breaks the imposed left/right symmetry and can unload one lower guide. This is more informative than simply extending axial range or densifying the same grid. First replace the approximate upper-guide rule with a proper three-dimensional contact/loss-of-contact rule; otherwise a zero-pitch result may be an artifact. Contact forces, friction and follower return would then be needed to assess whether a geometric path is physically accessible.

Do not keep increasing compute solely because no escape was found. A practical design decision is to compare this increasingly constrained rim-guidance concept with a simple supported central axle/spoke concept, making the visual trade-off explicit. No new hardware architecture is selected by this inconclusive search.
