# Rain Clock · rear-cartridge envelope and load-path correction

## Result: travel works in the imposed-contact model; retention is not solved

A geometry-only upper slider can accommodate the tested three-lobe example within a nominal ±1 mm travel envelope. **This is not yet a supported, escape-resistant mechanism.** A failed-return case reduces the existing lip's projected overlap to about **0.248 mm**. Axial pitching, guide friction, retention and hand torque remain unresolved. Do not treat the candidate as build-ready or select fabrication tolerances from it.

The completed sculpture/mechanism and sensitivity files were left unchanged. This directory adds a bounded, independently reviewed mathematical correction and one local CAD envelope—not a larger product design.

## Corrected support layout

Use two lower fixed guides at 210° / 330° and one upper radial follower at 90°. This gives a possible gravity load path, unlike treating clearance alone as support. The top carriage could be gravity-biased, but **its return force and ability to overcome friction are not established**. No spring, bearing, motor or load capacity was selected.

The upper guide's axial groove setting is independent of its radial travel. The CAD retains the original 0.2 mm side gap and 2 mm radial lip overhang; it does not silently enlarge the lip or move ornament pins. The `.4 mm` alternative from the earlier study remains a sensitivity variant, not a selected fit.

## Normalized free-body: why front weight matters

Coordinates: X horizontal; Y rearward; Z upward. Set ring weight **W=1**, with no assumed kilograms or material densities.

- For unspecified top follower preload **P ≥ 0**, ideal symmetric lower radial reactions are **N_left = N_right = 1 + P**. This balances vertical force, but P=0 does not establish follower tracking.
- Beads sit 14 mm ahead of the track; the tab envelope's center is 21 mm ahead. For hypothetical weight fractions f and t, with remaining weight in the track plane, **d = 14f + 21t mm**. Actual masses and COM are unknown.
- Weight at Y=−d creates an overturning moment **+d about X** in normalized units.
- A possible opposing axial reaction pair is top-front **+Q toward the rear**, and each lower-rear **−Q/2 toward the front**. With vertical contact separation h, **Q h = d**.
- For illustration only, axial contacts are placed at mid-overlap radii R_eff=142 / 111 mm, giving **h=1.5 R_eff**. Their real pressure centers are unknown.

The script verifies force and moment sums in this ideal symmetric model to below 2×10⁻¹⁵ numerical residual. This is algebraic equilibrium—not a capacity, stability, wear or safe-operation result.

The front-weight moment means the ring tends to **seat against opposing axial contacts**. “Positive side clearance” must not be described as flange-free running. Sliding flange contact can create drag; a rolling thrust-support design has not been selected.

### Axial seating versus the earlier tilt envelope

If a rigid ring is free to translate axially, top-front y=−g and lower-rear y=+g contact give `tan(|pitch|)=2g/h` and a center translation **+g/3**. At g=0.2 mm, this illustrative seating pitch is ~0.108° outer / 0.138° inner. Increasing g doubles the pitch freedom; it does not remove the load's moment.

These figures are **not** the earlier 0.080° / 0.102° conservative fixed-center, full-circumference envelope thresholds. That earlier envelope was not an actual three-contact onset or supported pose.

The single side tab also creates an unknown horizontal COM offset and in-plane gravity torque about Y. Actual contact normals can generate torque too. The symmetric free-body omits those effects; hand torque may be required even without friction. No full rotation equilibrium is claimed.

## Contact-constrained motion—not the earlier free-gap optimizer

`contact_motion.py` imposes all three radial root contacts, solving ring-center X/Z and upper follower displacement. The hypothetical running surface has 0.25 mm third-harmonic shape amplitude; decorative pins remain on a circular centerline. Each ring is checked at **25 shape phases over its 120° repeat**, using 4,096 polygon segments.

| Sampled quantity | Outer | Inner |
|---|---:|---:|
| Follower displacement | −0.7513…+0.7487 mm | −0.7515…+0.7484 mm |
| Maximum center excursion | 0.5013 mm | 0.5015 mm |
| Minimum circular pin-envelope / lip gap | 0.74997 mm | 0.75000 mm |

All imposed contact-distance residuals are below 1.1×10⁻¹² mm. This is a numerical residual, not physical accuracy. Sampled extrema are **not continuous guarantees**. The solver does not establish actual return motion, equilibrium, friction, stiffness or torque.

The first-order relation is `follower shift = 3s`, `ring-center shift = 2s` toward the upper guide, with s the three contacts' common radial shape error. Therefore the motions are correlated: the 1 mm nominal pin/lip gap becomes approximately `1+s`, not `1 − |follower travel| − |center travel|`.

Additional planar samples retain ~0.751 mm outer-post/frame separation and ~3.250 mm outer-bead-sweep/inner-upper-post separation across independent phase pairs. These do not check all solids or axial pitching.

## The unresolved failed-return / escape case

If the top follower stays at its +1 mm outward stop while the ring requires about −0.752 mm, the root loses contact by about 1.752 mm. The 2 mm lip overhang then retains only **0.2485 mm projected overlap** at the worst tested phase. This is a warning, not proof of either retention or escape: pitch, axial translation and the lip's edge geometry can alter the path.

Do not enlarge the lip or move bead pins from this one calculation alone. The reviewer specifically recommended an explicit return/retention investigation rather than calling the assembly “captive.” The CAD's front keepers retain the **slider carriage envelope**, not the ring.

## What the CAD actually contains

`rear_cartridge_envelope.FCStd` contains 14 valid named solids plus a parameter object:

- Rear mounting plate, rail envelopes, front keeper strips and two stop blocks.
- Sliding carriage with nominal ±1 mm vertical travel.
- Unchanged groove root and front/rear lips, axle/collar envelopes and long rear post.
- Separate axial-gap parameter; no finished shim/fastener arrangement.

Exact local CAD checks show zero carriage/stop overlap at ±1 mm and at sampled required positions; ±1.1 mm produces 15.2 mm³ stop overlap. This only demonstrates a geometric stop envelope. Guide clearances, fasteners and the long cantilever's stiffness are unspecified. The top plate reaches 382 mm in the original sculpture coordinates—slightly beyond the 379.5 mm frame envelope—so even this rear-only candidate has a small silhouette change to resolve.

The front remains free of spokes and new decoration; the 19-bead concept and window are not redesigned. No extra weights, electronics, purchased parts or physical build are specified.

## Independent review incorporated

The independent reviewer checked the free-body signs, guide orientation, contact-normal balance, correlated pin clearance and planar gap formulas. It did **not** certify hardware. Its corrections are incorporated here: allow axial seating translation, distinguish sampled from continuous results, include unknown side-tab torque, and leave ring capture unresolved.

## Files

- `load_path.py`, `.json`, `.png`, `.svg`: normalized free-body and visually reviewed diagram.
- `contact_motion.py`, `.json`: imposed-contact samples and failed-return envelope.
- `build_cartridge.py`, `rear_cartridge_envelope.FCStd`, `cartridge_geometry.json`: source, editable CAD envelope and stop checks.

Use `/usr/bin/python3 build_cartridge.py` for the installed FreeCAD API; other scripts use the normal Python environment with NumPy/SciPy/Matplotlib. This completed virtual-study checkpoint is preserved in the repository; no physical build or external asset inputs are involved.

**Next bounded test:** investigate a continuous 3D escape path with the follower both tracking and stuck at the outward stop, including pitch/axial translation and the side-tab mass offset symbolically. Only then choose a keeper/return architecture. The present study does not satisfy an escape-resistant hardware requirement.
