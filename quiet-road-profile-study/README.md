# Road into Evening — virtual grade/profile research

A separate, bounded experiment on the frozen `quiet_road` scene. The planar centerline, original natural terrain, seed 1102, road width, 40 m earthwork transition, lighting and camera are unchanged. Only the road's height profile changes. **No civil-road engineering or safety compliance is claimed.** The 4/6/8% caps are aesthetic research parameters, not standards.

## Results

| Profile | Maximum virtual grade | Maximum cut | Maximum fill | RMS centerline displacement |
|---|---:|---:|---:|---:|
| Natural follow | 11.545% | 2.013 m | 1.802 m | 0 m |
| 4% cap | 4.000% | 4.633 m | 5.632 m | 2.716 m |
| 6% cap | 6.000% | 3.334 m | 3.530 m | 1.634 m |
| 8% cap | 8.000% | 2.014 m | 2.166 m | 0.812 m |

Lower grade is not automatically better: it requires moving the road away from the natural surface. The 8% option preserves terrain most closely; 6% provides a larger grade reduction with moderate additional earthwork; 4% creates considerably more cut/fill. Only the 6% candidate was rebuilt/rendered. `profile_comparison.png` plots height, signed grade and centerline displacement. Cut/fill extrema in the table cover the whole sampled earthwork cross-section, not only its centerline; asphalt's ~4.5 cm anti-z-fighting offset is excluded.

## Method and reproducibility

`analyze.py` uses NumPy, SciPy 1.17.0 and Matplotlib. A 211-node quadratic height objective balances closeness to the original terrain against squared second differences (weight 25). SciPy SLSQP solves it under linear adjacent-height bounds. Endpoint heights are **free**, not connected to existing roads. Using y-distance for the bounds is conservative relative to horizontal centerline arc length. Fits took approximately 1.4–1.5 s each on this machine; timing is not a benchmark guarantee.

A positive normalized Gaussian convolution of the reconstructed slopes (sigma 3 virtual metres of y-distance), followed by mean-height recentering, softens knot transitions while preserving the grade bound. The final profile is stored every 0.75 m in `profile_6pct.json` and reconstructed piecewise-linearly. It is not an analytic C2 curve; numerical grade-change measurements and finite sampling have limits. The final smoothed curve is a postprocessed constrained fit, not claimed to be the exact optimum of the initial objective.

```sh
OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 python analyze.py
blender -b -t 2 --python build.py
blender -b road_into_evening.blend -t 2 --python check_mesh.py
```

Commands operate within this study only. The Blender build consumes the JSON profile with Python's standard library; SciPy is needed only to regenerate optimization data. It writes one 900×600, 64-sample Cycles CPU still with two threads and a native-compressed editable blend. `metrics.json` contains all optimization comparisons; `validation.json` contains the rendered mesh's independent checks.

Official API reference: [SciPy SLSQP](https://docs.scipy.org/doc/scipy/reference/optimize.minimize-slsqp.html). Solver success and explicit constraint residuals are checked rather than inferred from a plotted curve.

## Exact sampling, units and provenance

All distances are virtual metres: **1 Blender unit = 1 virtual metre**. Grade is `100 × vertical change / horizontal distance`; the final reported grade uses planar centerline chord lengths. The optimization cap instead uses y-distance, so it is conservative relative to that chord-based measure. This is a **user-adjustable aesthetic parameter**; 6% is this experiment's selected example, not a user mandate or an engineering standard.

- Fit: **211** height nodes, y = −130…500 m, 3 m spacing.
- Delivered profile: **841** heights and **840** intervals, 0.75 m y-spacing.
- Earthwork: **84,941** signed final-minus-natural samples = 841 rows × 101 lateral offsets (`u = −50…50`); maximum cut is the magnitude of the most negative sample, maximum fill the most positive. `u` is nominal road-normal distance; rows remain at constant y and are mapped to x with the local slope factor.
- Mesh verification: **840** road faces, **all** terrain faces checked for upward normals; **4,200** vertical raycasts at road face centers and inset corners. Zero misses/intersections. Asphalt clearance **0.044960…0.045029 m**, excluded from earthwork comparisons.
- Independent profile verification: every stored height finite, y strictly increasing, maximum conservative y-grade **6.000000000035%** (floating-point residual), maximum chord-based grade **5.999986903208%**. Tolerance is explicit in `verify_profile.py`.

`baseline_provenance.json` records the unchanged frozen baseline file hashes. `checksums.json` records per-file research hashes. The baseline remains the canonical artwork; this folder is a separate profile alternative, not its replacement. The compressed Blender file was reopened for saved-mesh verification. `verify_profile.py` can run with standard Python independently of SciPy or Blender.

## Independent review

Independent verification reproduced baseline and 6% cut/fill and RMS values, checked the unchanged-baseline hashes, and confirmed the conservative y-grade bound survives positive-kernel slope smoothing and linear reconstruction. Its naming clarification is applied: sampled chord length is not exact integrated arc length. Dense analytic-XY checks reach approximately 6.00000000001%, within floating-point tolerance. Endpoint height offsets versus the natural terrain are approximately **+1.65664 m at the start** and **+0.02952 m at the end**; free endpoints remain a deliberate limitation. No rerender or geometry change was needed after review.

The cap is verified only on the delivered road-profile domain **y = −130…500 m** (all 840 piecewise-linear intervals). The Blender terrain extension outside that interval follows the natural terrain with an endpoint offset and is **not** claimed to satisfy the cap. Reported finite chord grades are segment averages; they are not exact continuous arc-length derivatives. Cut/fill values are sampled maximum vertical depths, **not earthwork volumes**.

## Portable checkpoint

This folder is a separate alternative to [the canonical artwork](../quiet-road/README.md). PNG text metadata is omitted with decoded pixels unchanged; saved Blender browser/render paths are relative. Logs and caches are excluded. `checksums.json` covers the publication copies. In `baseline_provenance.json`, `baseline_files` retains the original research-input hashes before publication metadata normalization; `published_baseline_files` identifies the canonical repository copies. Geometry and numerical results are unchanged.
