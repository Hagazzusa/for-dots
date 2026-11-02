# Rain Clock · manual mechanism study 01

**Result:** the original sculpture is not a buildable mechanism. This revision gives the two moving rings explicit guide tracks and supports, and removes a nominal bead/sill collision. It is still an untested geometric concept—not fabrication-ready, a timekeeper, a self-running mechanism, or tested safe hardware.

## What the original animation hides

The original Blender scene has two freely floating rings, 11 + 8 decorative beads, and independent sine-angle keyframes. There are no bearings, supports, drive, or physical phase linkage. At frame 25, inner bead #6 intersects the sill in a smooth-ellipsoid/unbeveled-box reconstruction (about 38.0 mm³). This is a nominal-solid audit, not an exact intersection of the original low-poly/beveled Blender mesh.

All dimensions here use an **invented study scale: 1 original Blender unit = 100 mm**. The original did not establish physical dimensions.

## Options considered

1. **Central shaft, hub and spokes:** direct load path; however spokes occupy the window view, and two independently moving concentric rings require separate coaxial bearings/shafts or a linkage. Not selected for the first study.
2. **Three rim-guide rollers per ring — selected:** keeps the center open, avoids a coaxial shaft, and makes support/adjustment visible. Needs round tracks, correct groove fit, alignment, retention and validation of resistance to wobble.
3. **Suspended/flexure-supported arcs:** fewer rolling parts but no longer the original closed-ring motion; flexure fatigue, stiffness and stroke would need a separate study. Not pursued here.

## Selected architecture: manual first

Each decorative ring gains a smooth annular track behind its beads. Three exterior grooved rollers at 0°, 120°, 240° locate the track; their flanges provisionally constrain axial drift. Posts connect the roller axles to rear columns and the base. Rear slotted carriers indicate a need for adjustment; the red carrier is the candidate adjustment point, not a manufactured eccentric bearing.

Each ring has its own front tab. A person would move one ring at a time, slowly through the original approximate amplitudes (±8.6° outer; ±10.9° inner). **This does not reproduce the automatic eight-second, phase-offset loop.** There is no motor, power source, stored-energy drive, gearing or claimed continuous operation. The amber pane is only a visual placeholder: this prototype does not include electronics or working illumination.

Bearing/bushing choice, axle retention, fasteners, adjuster travel and preload are unresolved. The CAD's 4 mm wheel bores and 3.6 mm axle envelopes are placeholders, not recommended fits. No torque, load rating, material strength, service life or hand-force value is assumed.

## Deliberate geometric changes

| Feature | Original nominal mm | Revision mm | Reason / visual effect |
|---|---:|---:|---|
| Outer ring radius | 139 | 139 | Preserved |
| Inner ring radius | 112 | 108 | Clears inner support posts from outer bead sweep; slightly larger gap between rings |
| Decorative bead planes Y | −2, −19 | −64, −94 | Pull beads forward of shelter and guide rollers |
| Track center planes Y | same as beads | −50, −80 | Separate running surfaces from ornaments |
| Running track section | 2.8 mm round wire | 8 radial × 4 axial | Visible wider flat track, not a stiffness-qualified section |
| Fixed outer frame inner radius | 154.5 | 156.5 | Gives rear posts 1.5 mm nominal radial separation |
| Base width × depth | 390 × 125 | 390 × 210 | Accommodates the deeper stack; tipping not analyzed |
| Bead count | 11 + 8 | 11 + 8 | Preserved |

The deeper stack and visible rollers/posts make this less ethereal than the original render. The bead rings still overlap portions of the window in a frontal projection—this is visual occlusion, not solid collision after depth separation. Rear rails are also deliberately visible. The CAD omits the original bevels and fine decoration to expose the mechanism.

## What was actually checked

- FreeCAD 1.0 Python API generated valid solids; saved an editable `.FCStd` with named parts and a reproducible script.
- **All-angle shelter separation:** Y-axis rotation leaves Y extents unchanged. Every moving solid has a disjoint Y interval from every shelter solid. Minimum separating interval: **16 mm**. This proves this narrow geometric condition for all angles, not merely sampled frames.
- Six track/roller pairs: exact CAD intersections have **0 mm³ overlap**, and nominal tangent contact is present.
- Conservative swept-envelope gaps: bead backs to roller fronts **4.4 mm**; pins to roller lips **1 mm**; outer bead sweep to inner support posts **4.5 mm**; rear columns to canopy **12 mm**; outer posts to fixed-frame inner edge **1.5 mm**.
- Groove width 4.4 mm around a 4 mm track leaves **0.2 mm per side** in ideal geometry. **This is not an accepted tolerance**, and may be unusable with real runout, warping, dirt or inaccurate fabrication.
- These checks do not establish all-pair clearance, structural support adequacy, contact stress, friction, noise, balance, safety, dimensional stack-up, life or manufacturability. There is no finite-element or motion-dynamics simulation.

## Evidence, not endorsement

[HepcoMotion's official ring-guide description](https://www.hepcomotion.com/product/curved-rails-and-track-system-components/large-diameter-ring-guides-segments-and-track-systems/) describes internal/external rolling guide edges, open centers, and adjustable eccentric bearings. This supports considering rim guidance as an architecture. Its commercial load/speed claims **do not apply** to this small original study or its simplified U-groove wheels.

[HepcoMotion's official eccentric-adjustment explanation](https://www.hepcomotion.com/videos/animation-gv3-eccentric-adjustment/) confirms that their V-bearing systems use adjustment to restore running condition after wear. Our slotted carrier is only an inferred adjustment concept, not that product's implementation.

## Before any physical trial

Do not treat exposed nip points, removable beads or sharp edges as safe. A physical prototype needs captive parts, guarded roller/track nips, retained axles, travel stops and a stable base before hand operation. None is safety-validated here. No purchase, fabrication order or physical test has occurred.

**Next bounded step:** make a virtual single-ring coupon variant and sweep groove side clearance and radial runout. Find where the 0.2 mm ideal side gap or 1 mm pin clearance first produces interference, then specify what a later authorized bench coupon must measure (starting/running hand force, wobble, rubbing, retention and wear). This is more useful than selecting a motor before the ring guide has demonstrated smooth motion.

## Local files / reproduction

- `rain_clock_manual.FCStd`: named, individually positionable FreeCAD solids. Rebuild dimensions through `build_mechanism.py`; not a constrained manufacturing assembly.
- `build_mechanism.py`: `/usr/bin/python3 build_mechanism.py`; uses the installed FreeCAD Python API via the Linux FreeCAD module path `/usr/lib/freecad/lib`; adapt that import path to your installation if needed.
- `geometry_checks.json`: narrow geometry proof and numeric results.
- `render_mechanism.py`, `mechanism_preview.png`: review preview and reproducible renderer. Run the build first to regenerate `preview_mesh.json`, then `blender -b -t 2 --python render_mechanism.py`. The derived preview `.blend` is not included; the editable mechanism source is the `.FCStd`.
- No original sculpture or game files were changed. All geometry is original; no external assets. This completed study is preserved separately in the repository. Intermediate caches and the derived preview blend are excluded; PNG path metadata was removed without changing pixels.

- `section_diagram.svg` / `.png`: annotated axial-stack and guide-contact explanation, visually reviewed.
- Mechanism preview visually reviewed; 15.50 seconds, two CPU threads, 1000 × 800, 16 samples, no denoiser.
