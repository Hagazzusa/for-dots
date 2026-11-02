# Rain Clock · deterministic clearance sensitivity

## Decision

**Do not freeze the original 0.2 mm groove-side gap as a fabrication tolerance.** In the ideal model, it disappears at only **0.080° outer-track tilt / 0.102° inner-track tilt**, with no other errors. Reserving 0.05 mm axial offset and 0.05 mm sinusoidal axial waviness reduces the outer threshold to **0.040°**.

The useful next virtual candidate is an **axially adjustable guide cartridge**, leaving the front beads, ring radii and quiet appearance unchanged. Compare 0.2 / 0.4 / 0.6 mm side-gap envelopes; do not declare one a production fit. Adjust axial alignment before simply opening the gap. Keep radial take-up independently adjustable: a wider axial groove cannot cure radial shape interference.

## What was varied—not measured

This is a deterministic what-if grid, **not a manufacturing distribution or estimate of failure probability**. None of these inputs is a known fabrication capability.

- Both track outer contact radii: 143 mm outer / 112 mm inner (different from their 139 / 108 mm centerline radii).
- Nominal side gap: 0.2, 0.4, 0.6 mm.
- Axial offset: 0, 0.05, 0.10, 0.20 mm.
- Sinusoidal axial waviness amplitude: 0, 0.05, 0.10, 0.20 mm. Amplitude means **half peak-to-peak**, not total indicated runout.
- Track tilt: 0, 0.02, 0.05, 0.10, 0.20 degrees.
- Roller axial-alignment error bound: 0, 0.05, 0.10, 0.25 mm.
- Radial examples: a round surface eccentric to a reference, two-lobe ovality, three-lobe shape error, and uniformly oversized radius; amplitudes 0.05, 0.10, 0.25 mm. One roller outward adjustments: 0, 0.10, 0.25 mm.

There are 1,920 axial scenarios and 5,184 first-order radial scenarios. They are inexpensive equations, not thousands of CAD simulations.

## Axial model and failure envelope

With unknown independent phases, a conservative envelope is:

`remaining side gap = nominal side gap − |axial offset| − waviness amplitude − R × tan(tilt) − roller alignment error bound`

This sums worst-case contributions; it is not a claim that all peaks coincide in a real ring. The cross-section projection, elastic deformation, contact forces and wear are omitted.

| Side gap per side | Outer tilt-only zero margin | Inner tilt-only zero margin | Outer zero margin after 0.10 mm reserved for other errors |
|---|---:|---:|---:|
| 0.2 mm | 0.080° | 0.102° | 0.040° |
| 0.4 mm | 0.160° | 0.205° | 0.120° |
| 0.6 mm | 0.240° | 0.307° | 0.200° |

Negative margin means overlapping ideal envelopes. Positive margin means geometric room only—not acceptable wobble, retention, smoothness or safety. More gap trades reduced binding risk for greater possible axial freedom.

## Radial result: do not confuse eccentricity with shape error

A rim-guided ring has no central shaft fixing its center. It may translate. A perfectly round running surface eccentric to a decorative/reference center can therefore recenter; its beads may wobble visually, but eccentricity alone is not proof of radial jamming.

For three equally spaced guide normals `n_i`, and small radial shape errors `s_i` / roller offsets `e_i`, the first-order gap is:

`g_i = e_i − s_i − n_i · c`

Since the three normals sum to zero, free translation can equalize the gaps, and the best minimum first-order gap is `mean(e_i − s_i)`. This model predicts:

- Reference eccentricity: center translation absorbs the first harmonic.
- Two-lobe ovality: translation also absorbs its samples at these three contact positions **to first order**. It still moves the center; it is not globally “perfectly round.”
- Three-lobe error: the three rollers can simultaneously face three outward lobes. Translation cannot remove this common radial demand.
- Uniform oversize: likewise cannot be removed by translation.

At 0.25 mm three-lobe amplitude and adverse phase, best minimum gap is approximately **−0.25 mm** for both ring sizes. Moving just one roller outward by 0.25 mm adds only 0.083 mm to the first-order average gap—not a complete correction. Static adjustment may also trade one phase's interference for another phase's free play.

### Nonlinear spot checks

A separate polygon-to-circle distance model uses 4,096 boundary segments, 9 mm guide-roller root radii, ±1 mm allowed center translation, and a multi-start constrained optimizer. Fourteen cases cover both rings. Key results:

- Round reference eccentricity of 0.25 mm: recentering ≈0.25 mm; residual numerical gap near zero.
- Two-lobe 0.25 mm example: best minimum gap ≈+0.0005 to +0.0006 mm; first-order zero is a close approximation, not an exact result.
- Three-lobe 0.25 mm adverse phase: ≈−0.24998 mm.
- Uniform 0.25 mm radial oversize: ≈−0.24998 mm.

Two outer-ring cases were repeated at 8,192 segments; gap changes were below 0.0001 mm. These are local multi-start optimization results, **not a global infeasibility certificate**. Friction, gravity, preload and the ability to actually recenter are absent.

### Original small motion, not full revolutions

The broad phase sweep represents unknown mounting phase, not a claim that the artwork makes full revolutions. Additional cases use the original ±8.59° / ±10.89° motions. With the 0.25 mm three-lobe example:

- Initial phase 0°: overlap throughout either motion band.
- Initial phase 30°: gap changes sign; outer approximately −0.109 to +0.109 mm, inner −0.135 to +0.135 mm.
- Initial phase 60°: positive gap throughout, which can mean loss of three-point contact—not a supported pass.

## Coupled-ring checks: limited but useful

Simple envelope budgets, not full 3D collision sweeps:

| Pair | Nominal gap | Explicit hypothetical allowance | Remaining |
|---|---:|---:|---:|
| Outer beads / inner rollers, axial | 6.4 mm | 0.5 mm moving excursion + 0.5 mm roller reposition | 5.4 mm |
| Outer bead sweep / inner posts, radial | 4.5 mm | 0.5 mm sweep growth + 0.5 mm post outward shift | 3.5 mm |
| Bead pins / same-ring roller lips, radial | 1.0 mm | 0.25 mm center excursion + 0.25 mm inward roller error | 0.5 mm |
| Moving geometry / shelter, axial | 16.0 mm | 0.5 mm rearward excursion | 15.5 mm |

Within **these selected budgets**, guide fit is more restrictive than inter-ring or shelter separation. This is not a complete coupled collision clearance or safety assessment.

## Adjustable geometry without changing the front composition

`groove_variants.FCStd` contains three separate virtual guide coupons. Root radius 9 mm, retaining-lip radius 11 mm, and lip thickness 2.8 mm are held constant. Only the axial groove spacing changes:

| Side gap | Groove width | Total roller width | Nominal bead-back / front-lip gap |
|---|---:|---:|---:|
| 0.2 mm | 4.4 mm | 10.0 mm | 4.4 mm |
| 0.4 mm | 4.8 mm | 10.4 mm | 4.2 mm |
| 0.6 mm | 5.2 mm | 10.8 mm | 4.0 mm |

The additional depth is behind the existing beads; no spokes, larger front ring, new drive or extra ornament are introduced. A spacer/shim-adjusted cartridge is a **proposed architecture**, not a modeled fastener assembly. A later model should separate the functions of radial support, axial retention and compliant take-up instead of demanding three perfectly rigid zero-clearance contacts. Spring rate, preload, adjustment travel and bearing selection remain deliberately unspecified.

## Evidence and limits

[Mitutoyo's official precision-measurement guide](https://www2.mitutoyo.co.jp/eng/useful/E11003/pageindices/index64.html) distinguishes reference-circle evaluation, centering effects and inclination effects. [NIST's roundness measurement guidance](https://itl.nist.gov/div898/handbook/mpc/section3/mpc344.htm) explains why a single trace can mix spindle error and workpiece error. These justify keeping reference eccentricity, form error and alignment separate. The contact models and hypothetical numbers above are our calculations—not manufacturer recommendations.

No physical fabrication, measurement, force/torque estimate, power design or purchase occurred. No material strength, tolerance capability, friction, wear, fatigue, stability, guards or safe hand use has been established. The completed parent study remains unchanged.

## Reproduce / inspect

- `sweep.py`: run `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python sweep.py`.
- `results.json`: full deterministic inputs/results, operating-band and coupled envelopes.
- `summary.json`: thresholds and nonlinear checks.
- `sensitivity_plot.png` / `.svg`: visually reviewed scientific model curves.
- `build_groove_variants.py`: run with `/usr/bin/python3` and the installed FreeCAD API.
- `groove_variants.FCStd` / `.json`: six valid coupon solids and parameters.

**Next bounded virtual test:** model an explicit rear adjustable cartridge with separate axial spacing and radial compliant travel, then test whether it maintains contact across the adverse three-lobe cases without consuming the 1 mm pin/lip clearance. Do not select a motor until the guide architecture makes geometric sense.
