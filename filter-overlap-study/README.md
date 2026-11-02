# When two filters overlap

A bounded companion experiment to **Garden of Light**. Instead of another
palette variation, this asks whether its colored shadows behave like
subtractive RGB filters, and what changes when a diffuse surface component is added.

## Result

Measured floor-patch RGB divided by the identical unfiltered reference:

| Condition | R | G | B |
|---|---:|---:|---:|
| No filters | 1.000000 | 1.000000 | 1.000000 |
| Cyan, C | 0.200000 | 0.850000 | 0.900000 |
| Yellow, Y | 0.950000 | 0.850000 | 0.200000 |
| Pure overlapping filters | 0.190000 | 0.722500 | 0.180000 |
| Overlap, gallery-style 12% diffuse mix | 0.150503 | 0.587904 | 0.153065 |
| Same gallery mix, indirect diffuse disabled | 0.147136 | 0.559504 | 0.139392 |

Pure transmission matches the channelwise product **C × Y**, within
**3.8 × 10⁻⁸** in normalized RGB. This is floating-point agreement inside this
shader model, not a real-material accuracy rating.

The gallery mixture's direct-path prediction is **0.88² × C × Y**. With diffuse
bounces enabled, measured normalized green is 0.587904 rather than 0.559504.
Disabling indirect diffuse reduces the maximum prediction residual from
**0.028400** to **3.7 × 10⁻⁸**. This controlled ablation supports diffuse
interreflection as the source of the excess in this scene; the noisy residual
is not an exact physical radiometric measurement.

## Controls and limits

- Same matte 0.8 diffuse floor, white area light, camera, exposure, seed, patch
  geometry, and sampling in all six conditions.
- Black world; no colored lights, compositor coloring, or external textures.
- 256 × 256, 64 samples, fixed seed 17, two CPU threads, no denoising.
- Measured the identical central 32 × 32 floor patch from **32-bit float EXR**,
  loaded by Blender as **Linear Rec.709**. Divided each channel by the control.
- PNG previews use Standard / sRGB, exposure 0, gamma 1. Their display values
  are **not** used for calculation. Color-management nonlinearities would make
  multiplying ordinary screenshot RGB values invalid for this test.
- Filters remain active for shadow and indirect rays but are hidden from
  camera rays, isolating the floor rather than viewing it through the filters
  a second time. This is a measurement setup, not a proposed camera trick for
  the original installation.
- Two plane sizes/heights give approximately aligned shadow footprints. Only
  the central patch, safely inside both penumbras, is measured.
- The gallery comparison repeats the original 88% transparent / 12% diffuse
  structure, but changes colors and controlled geometry. It does not claim to
  measure the original gallery scene pixel-for-pixel.
- RGB non-refractive approximations, not spectral transmission, real glass,
  wavelength-dependent scattering, or focused caustics.

## Reproduce

```sh
blender -b -t 2 --python study.py
python compose.py
```

Blender includes numpy for measurement. Contact-sheet composition requires
Pillow (with a default-font fallback). All source paths resolve relative to
the scripts. The saved blend opens at the final, direct-only condition; run
the source to regenerate every controlled variant.

`Filter-Overlap-Comparison.png` is a visually inspected contact sheet of the
actual six floor renders, not recolored illustrative swatches.
`measurements.json` retains unnormalized means, predictions, residuals and
loaded color-space names. The six `.exr` files retain the linear evidence;
`.png` files retain display previews. `Filter-Overlap.blend` is editable.

## Primary technical references

- Blender's [Transparent BSDF documentation](https://docs.blender.org/manual/en/4.4/render/shader_nodes/shader/transparent.html)
  defines straight-through transparency without refraction and colored transmission.
- Blender's [color-management implementation documentation](https://developer.blender.org/docs/features/render_pipeline/color_management/)
  describes scene-linear float image buffers.
- [OpenEXR scene-linear documentation](https://openexr.com/en/latest/SceneLinear.html)
  cautions that an EXR file alone does not guarantee linear-light interpretation;
  this experiment additionally records Blender's loaded color-space designation.
