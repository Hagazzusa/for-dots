# 비를 세는 창 / Rain Clock — research index

A virtual desk sculpture about rhythm, not timekeeping. The original warm window and rain-bead rings developed into several **unvalidated mechanical concepts**. This index closes the current research chain rather than selecting fabrication hardware.

**Current visual preference:** [foreground window](mechanism/front_facade/README.md), provided hiding one or two lower beads is acceptable. It eliminates the long rotating braces while keeping the quiet window character. Otherwise a visibly supported hub is the more honest aesthetic choice. Neither option is manufacture-ready.

## Read in this order

| Study | What it establishes | What it does not establish |
|---|---|---|
| [Original virtual art](README.md) · [still](rain_clock_still.png) · [8-second loop](rain_clock_loop.mp4) | Original editable procedural artwork; named scene and matching animation endpoint poses | Physical supports, a functioning clock or a proven mechanism |
| [Nominal rim guide](mechanism/README.md) · [diagram](mechanism/section_diagram.png) | Valid modeled solids; **invariant** 16 mm Y-interval separation from the shelter under the specified Y rotation; six nominal guide-contact checks | Full collision freedom, useful fabrication tolerances, stiffness or safe capture |
| [Sensitivity](mechanism/sensitivity/README.md) · [plot](mechanism/sensitivity/sensitivity_plot.png) | Deterministic hypothetical error envelopes, first-order recentering model and nonlinear spot checks | Measured manufacturing distributions, actual follower behavior or loaded equilibrium |
| [Cartridge/load path](mechanism/cartridge/README.md) · [free-body](mechanism/cartridge/load_path.png) | Normalized symmetric force/moment algebra; **sampled** contact-constrained travel and local stop envelopes | Selected preload, torque balance, reliable return or ring retention |
| [Bounded escape search](mechanism/escape/README.md) · [plot](mechanism/escape/reachable_components.png) | **Inconclusive** finite-grid investigation using actual finite-width BRep guide/track solids | Absence of a continuous escape path, full-assembly escape or safety |
| [Rear axle / original window](mechanism/axle_comparison/README.md) · [view](mechanism/axle_comparison/rear_axle_quarter.png) | Sampled geometric concealment/collision comparison; independent hub concept | A mechanically superior solution: long 97/144 mm links create unresolved leverage |
| [Foreground facade](mechanism/front_facade/README.md) · [front](mechanism/front_facade/front_facade_front.png) · [quarter](mechanism/front_facade/front_facade_quarter.png) | Zero rotating forward links; 14 mm bead offsets; sampled window clearance and deliberate bead occlusion | Bearing ratings, structural integrity, complete motion proof or fabrication readiness |

## Evidence vocabulary — keep the distinctions

- **Invariant geometry:** the nominal rim study's moving and shelter solids occupy disjoint Y intervals; the specified Y-axis rotation preserves those intervals. This narrow statement applies to that unchanged model. It is not a general mechanical validation.
- **Exact BRep operation:** the geometry kernel intersected the supplied solids. A polygonized lobed profile is still an approximation to a smooth profile; a kernel result is not a physical test.
- **Sampled geometry:** only specified angles, phases, poses and pairs were evaluated. Minima and maxima from those samples are not continuous guarantees.
- **Model equilibrium:** algebra balances an idealized symmetric free-body. The cartridge's side-tab torque, friction, real COM and response remain unresolved.
- **Inconclusive search:** the escape search found no endpoint in 582 grid tests plus 212 midpoint checks. Restricted motion directions, approximate follower response and graph connectivity prevent an absence proof.
- **Unvalidated hardware:** applies to every study, including the preferred visual concept.

Two corrections matter when reading earlier snapshots:

1. The sensitivity study's approximately 0.080° outer tilt value is a conservative fixed-center/full-circumference envelope—not the onset of contact in a loaded three-guide mechanism.
2. Positive clearance is not support. Front-offset weight pitches the ring into axial reactions; a follower stuck outward had only about 0.248 mm projected lip overlap in the tested example. Neither that overlap nor the later no-path search proves retention.

The original bead/sill overlap estimate used a smooth-ellipsoid/unbeveled-box reconstruction, not the exact original Blender mesh.

## Validate this preserved checkpoint without rebuilding or rendering

From the study root:

```sh
python consolidation/validate.py --negative-test
```

The command uses the Python standard library, reads files/results, checks syntax, JSON contracts, PNG CRCs, CAD ZIP/XML integrity and object counts, relative project dependencies, and optional video metadata. It intentionally rejects an unsupported `manufacture_ready` evidence label and a path-traversal fixture.

**It does not rerun CAD, recompute the research, render images, or certify hardware.** The reported evidence is checked for integrity and consistency, not independently proved.

### Reproduce a study only in a working copy

Each study README names its build script. Builders overwrite their generated outputs and may reset evidence files; copy the tree first if preserving this checkpoint. `preview_mesh.json` files are intentionally absent and regenerated by CAD builders. The two local `.blend` caches can also be regenerated and are excluded from the portable backup payload. The duplicate GIF is optional and was intentionally omitted from the public repository; the validator reports that omission without failing. A manifest still requires every file it explicitly lists.

Runtime portability is explicit, not overstated:

- Project-data dependencies use the preserved relative tree.
- Historical CAD scripts target this Linux installation of FreeCAD through its Python API; adapt the interpreter/module locations on another platform. The local `freecadcmd` launcher crashed, while API builds worked.
- Blender 4.3.2 was used, CPU renders capped at two threads; denoising was disabled because this build lacks OpenImageDenoise.
- Numerical/plot scripts require NumPy, SciPy and Matplotlib; their Linux cache directory is a runtime setting.

## Prepare a local backup payload

```sh
python consolidation/prepare_backup.py
```

This creates a **new sibling directory**, refuses to overwrite an existing stage, copies only cataloged deliverables, and removes private path metadata from PNG copies while verifying identical IDAT bytes. Originals and historical results stay unchanged. It excludes bytecode, transient meshes and regenerable `.blend` caches with machine-specific output paths.

The stage contains:

- `BACKUP_MANIFEST.json`: exact relative filenames, byte sizes, SHA-256 hashes and source/transformation provenance for the full local archive.
- `PUBLICATION_DELTA.json`: only the newly completed study folders plus this index/consolidation files; existing published studies are not implicitly overwritten.
- `VALIDATION_REPORT.json`: the lightweight audit result before final manifest hashing.

To verify the staged bytes:

```sh
python consolidation/validate.py --negative-test --manifest BACKUP_MANIFEST.json
```

A backup-ready manifest describes local bytes, not remote repository state. Check the repository commit and file hashes separately.

## Project provenance and validation status

These original geometric studies were completed on 2026-11-02. Earlier READMEs are frozen creation-time snapshots; local-only wording describes the state at creation. The source scripts, result files and CAD remain preserved with their stated limitations.

The index consolidates completed evidence without recomputing CAD or certifying hardware. The bounded escape investigation remains inconclusive; sampled clearances are not continuous guarantees. No fabrication readiness, safe retention or physical performance is established.
