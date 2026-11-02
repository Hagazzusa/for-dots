# Seeded Roadscapes — twelve terrain seeds, three postcards

A bounded foundation for calm road-trip landscapes, separate from the canonical `quiet_road` artwork and its profile study. **The original study's seed changed only decorative stones; its road and terrain were fixed analytic functions.** This study genuinely seeds terrain wave amplitudes, phases and horizontal scales. Decorative stones also use the seed. The road's planar S-curve, camera, light, palette, road width and profile-fitting method stay fixed to isolate terrain/profile behavior.

## What the seed controls

`landscape.parameters(seed)` uses a private deterministic Python random generator. Three wave amplitudes lie in [3,7], [2,5] and [2,4] virtual m; phases in [−π,π]; x scales in [70,110] and [85,140] m; y scales in [100,160], [120,190] and [150,220] m. These are sinusoid denominator scales, **not full wavelengths**. All parameters are recorded in `seed_report.json` and each profile. There are no external assets, textures or user data.

**1 unit = 1 virtual metre.** The 6% cap is an adjustable aesthetic parameter, not an engineering standard. Each profile uses 211 SLSQP nodes at 3 m y-spacing, closeness + second-difference smoothing (weight 25), then positive normalized y-slope convolution (sigma 3 m), mean recentering and piecewise-linear reconstruction at 0.75 m. Endpoints are free. The cap applies only to y = −130…500 m; the terrain extension beyond that domain is not cap-certified. Final reported grades use horizontal chord-segment lengths; conservative constraints use y-distance.

## Bounded verification

Twelve seeds **1101…1112** were tested, not an unbounded search:

- Every seed: **307,510 terrain quads / 615,020 triangles**, plus **840 road quads / 1,680 triangles**, covered by positive vertical cross-product checks. Because all seeds share the same XY topology, these arrays are computed and checked **once**, and the result applies to all twelve height fields; this is not twelve separate mesh builds. Both triangles of one diagonal triangulation per quad are checked. The non-folding row mapping has a positive horizontal Jacobian independent of terrain height; numerical tests inspect all generated horizontal triangle coordinates, not merely the centerline.
- Every seed: **841** profile samples / **840** segments; conservative y-grade stays ≤6% within floating tolerance. Original natural-following maximum grades range **5.54–9.82%**.
- Every seed: **84,941** signed earthwork-depth samples (841 rows × 101 nominal lateral offsets −50…50). Worst across all twelve: **2.324 m cut**, **3.038 m fill**. These are sampled vertical depths, **not volumes**, and exclude the 4.5 cm asphalt rendering offset.
- Selected rendered seeds: all actual Blender terrain/road polygon normals checked, **4,200 BVH clearance samples each**, zero misses/intersections. This stronger mesh-intersection check applies to the three rendered cases, not the other nine numerical cases.
- Independent standard-library regeneration: **231** terrain-height samples per seed reproduce recorded fingerprints exactly; all **12 fingerprints differ**. Stored profiles pass every segment's grade check.
- The complete twelve-seed optimization was rerun: `profiles.json` reproduced **byte-for-byte**. This is same-environment reproducibility, not a promise of bitwise identity across SciPy/BLAS/platform versions.

## Three selected postcards

The selection uses a fixed 231-position terrain-height fingerprint: farthest pair by RMS height distance, then max-min third. It is selected by terrain, not stones or hand-picked solver outcomes.

| Seed | Maximum cut | Maximum fill |
|---|---:|---:|
| 1105 | 2.148 m | 3.038 m |
| 1107 | 1.075 m | 1.215 m |
| 1111 | 1.126 m | 1.010 m |

`seed_1105.png`, `seed_1107.png`, `seed_1111.png`: three 600×400 Cycles CPU previews, 32 samples, two threads, rendered serially. All actual pixels were inspected; the changed terrain visibly changes the road's vertical presentation and horizon without changing its planar path. `postcard_triptych.png` is a labeled comparison layout. Only **`seed_1105.blend`** is retained, native-compressed with editable geometry; it was reopened and verified. No extra huge scene files are required for the other two seeds.

## Rebuild

Python analysis needs NumPy and SciPy (tested 1.17.0); the comparison layout needs Matplotlib. Blender tested 4.3.2. The Blender generator reads precomputed profiles and uses the standard-library `landscape.py`.

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python analyze_seeds.py
python verify_reproducibility.py
blender -b -t 2 --python build_variant.py -- --seed 1105 --save-blend
blender -b -t 2 --python build_variant.py -- --seed 1107
blender -b -t 2 --python build_variant.py -- --seed 1111
blender -b seed_1105.blend -t 2 --python verify_saved_blend.py
python make_triptych.py
```

Run render commands serially. Output paths are relative to the scripts, with no global CLI/config changes. Mesh validators write their JSON reports. No physical simulation, driving system, road-network connectivity, navigation mesh or civil-road certification is provided. Both prior studies remain unchanged.

Official optimization API reference: [SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html).

## Independent review

Independent verification reproduced all twelve terrain fingerprints, all twelve cut/fill results, the selected seeds, and the shared XY topology counts/positive cross-products. It confirmed the source keeps the planar road, camera, lighting and profile method fixed. Its clarification that topology is checked once for shared XY—not twelve separate mesh builds—is applied above. Review was read-only and did not perform extra renders.

## Portable checkpoint

Publication copies omit PNG text metadata without changing decoded pixels. Saved Blender browser/render paths are relative. Logs and caches are excluded; `checksums.json` identifies the included copies. Original source-study manifest hashes in `provenance.json` identify the research inputs before metadata normalization; added published-source manifest hashes identify the corresponding repository copies. The canonical [landscape](../quiet-road/README.md) and [profile study](../quiet-road-profile-study/README.md) remain unchanged.
