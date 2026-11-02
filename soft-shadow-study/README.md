# Three heights, one light

An original quiet virtual sculpture and a controlled companion study, prompted
by the observation that the Garden of Light's colored shadows soften with distance.
The original Garden files are unchanged.

## Artwork

`Three-Heights-One-Light.png` / `.blend`: three identical rounded teal filters
on slender brass supports, held 0.4, 0.9 and 1.4 scene units above an ivory paper
plinth. One broad light lets their shadow boundaries become increasingly soft.
All geometry and textures are procedural. No external assets or composited shadows.
This is virtual art, not a physical glass fabrication plan.

The artwork uses a colored transparent/diffuse thin-sheet approximation, a
small world fill and warm light. Its image is **illustrative, not the calibrated
measurement setup** below.

## Why the edge spreads

A finite area emitter reaches the receiver along a range of directions.
Near the projected boundary, only part of the emitter is seen through the
filter; the rest is seen unfiltered. More separation lets those directions
spread over a wider region of the receiving surface. A larger emitter also
widens that region. This is a geometric **penumbra**, not evidence that glass
is diffusing or scattering light.

This behavior is consistent with Blender's official description of
[area lights and soft borders](https://docs.blender.org/manual/en/4.4/render/lights/light_object.html).
The [Transparent BSDF](https://docs.blender.org/manual/en/4.4/render/shader_nodes/shader/transparent.html)
passes light straight through without refraction; the experiment does not use
volumetric scattering or a glass shader.

## Controlled measurements

Fixed source-to-receiver distance L = 4.0 scene units. One horizontal 1.2 × 1.6
filter; three heights h; two square-emitter widths a. Identical matte receiver,
white light power, camera and seed. A separate no-filter control for each emitter
size compensates for its illumination field. Eight renders total.

| Emitter width a | Gap h | Measured 10–90% width | Width in pixels |
|---:|---:|---:|---:|
| 0.3 | 0.5 | 0.0366 | 3.5 |
| 0.3 | 1.0 | 0.0809 | 7.8 |
| 0.3 | 1.5 | 0.1431 | 13.7 |
| 0.9 | 0.5 | 0.1032 | 9.9 |
| 0.9 | 1.0 | 0.2386 | 22.9 |
| 0.9 | 1.5 | 0.4296 | 41.2 |

Both trend assertions pass: width increases with gap at either emitter size;
the wider emitter produces softer edges at every gap.

### Definition and controls

- 384 × 384 Cycles renders; 96 samples; seed 23; two CPU threads; no denoising.
- World light is zero. **Indirect diffuse bounces are disabled.** Pure colored
  transparent filter, with red transmission T = 0.2. Broadening therefore
  occurs without the artwork's diffuse mixture or indirect illumination.
- Filters hidden from camera rays only; still active for light/shadow rays.
  This isolates receiver light rather than looking through the filter twice.
- Read 32-bit EXR float buffers, verified **Linear Rec.709**, not display PNGs.
  See Blender's [linear-buffer color pipeline](https://developer.blender.org/docs/features/render_pipeline/color_management/).
- Normalize every red-channel pixel to the corresponding no-filter control:
  `u = (I_red / I_red_control - 0.2) / 0.8`.
  Thus u=0 is fully filtered; u=1 is unfiltered.
- Average 16 central scanlines. Find the right edge's u=0.1 and u=0.9 crossings
  with adjacent-sample linear interpolation. Width is x90−x10. No blur or
  smoothing is applied to the measured profile.
- Pixel pitch is 4/384 = 0.010417 scene units. The narrowest transition spans
  only 3.5 pixels, so its precision is sampling-limited. Four decimal places
  identify computed outputs, not a claim of physical measurement accuracy.
- Finite samples and pixel filtering also affect the result; no uncertainty
  confidence interval was estimated.

### Projection versus softness

Similar triangles give the full geometric penumbra span `a*h/(L-h)` for this
parallel source/filter/receiver setup. The filter's projected image also grows
by `L/(L-h)`—that is **magnification**, separate from boundary softness.
For an ideal uniformly weighted square source, 10–90% width is approximately
`0.8*a*h/(L-h)`. Rendered area-light angular weighting and pixel sampling mean
this reference is not asserted as an exact equality. The evidence plot compares
all six measured widths with that approximation. Edge-profile curves are
centered on their own measured midpoint so magnification does not masquerade
as a wider transition.

The artwork's tilted illumination and supports introduce additional geometry;
do not transfer calibrated values directly to that composition.

## Files and reproduction

```sh
blender -b -t 2 --python measure.py
python plot.py
blender -b -t 2 --python art.py
```

`measurements.json` records definitions, settings, thresholds and trend checks.
`edge_profiles.csv` retains all 384 profile samples for every condition.
The eight EXRs are linear evidence; eight PNGs are Standard/sRGB previews.
`Penumbra-Evidence.png` is the explanatory scientific figure (matplotlib/numpy).
`Soft-Shadow-Measurement.blend` retains the final calibration condition.
All outputs resolve relative to their source scripts. No animation or external
assets are required. Only the source scripts and deliverable/evidence files
should be versioned, not logs, Blender backups or plotting caches.

## Narrowest-case spatial-resolution check

To close the 3.5-pixel limitation, reran **only** emitter width 0.3 / gap 0.5 at
**768 × 768**, with a matching 768 px unfiltered control. Kept 96 samples,
seed 23 and the same scene. Averaged 32 scanlines at 768 instead of 16 at 384,
preserving the physical vertical averaging span. Same linear EXR normalization
and unsmoothed, adjacent-sample threshold interpolation.

- 384 px width: **0.0365845** scene units.
- 768 px width: **0.0346973** scene units, spanning **6.66 pixels**.
- Absolute difference: **0.0018872**; **5.44%** relative to the higher-resolution value.
- 768 px result is **1.20%** above the 0.0342857 uniform-source approximation.

Therefore the narrowest original value should **not** be presented as precise
to four decimal places, or as an exact physical width. The higher-resolution
result moves closer to the geometric approximation, but two resolutions do
not establish an asymptotic limit, uncertainty interval or exact convergence.
Pixel filtering, Monte Carlo sampling, and emitter angular weighting remain.
The broadening trend is unaffected; this check qualifies numerical precision.

`convergence.py` regenerates these two additional renders after `measure.py`.
`convergence.json`, `convergence_profile.csv`, and the two `convergence_768_*.exr`
files preserve evidence. `plot_convergence.py` produces `Resolution-Check.png`.
Original full-matrix JSON, CSV and measurement blend were SHA-256 checked before
and after and remained unchanged.

## Portable evidence copies

Publication copies omit machine-local path metadata. The two convergence EXRs
replace only the `File` string attribute with a padded `<untitled>` value; every
other header byte, offset table and compressed channel/pixel payload is unchanged.
Original and publication hashes are recorded in `metadata_provenance.json`. The
eight original full-matrix EXRs remain byte-identical. PNG decoded pixels are
unchanged after removing text metadata; saved Blender browser paths are relative.
