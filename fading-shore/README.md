# 사라지는 해안 · Fading Shore

A single teal ribbon lifts slowly away from a warm paper surface. Its nearby
shadow begins with a defined edge; farther along the rising curve, the boundary
opens into a quiet wash of color. The space around it is intentionally empty.

This is an original **digital sculpture**. The unsupported ribbon is deliberately
virtual—not a real-object fabrication proposal.

## The image

- `Fading-Shore.png` — 1000 × 800 gallery still.
- `Fading-Shore.blend` — editable scene, camera, light and materials.
- `build.py` — all original geometry and procedural material source.
- `validation.json` — geometry and camera-framing checks.

No external assets, image textures, compositor effects, or post-process blur.
The colored shadow and its softened boundary come from Cycles lighting through
the filter approximation. One finite disk emitter illuminates the composition;
the small world fill and diffuse material component are part of the artwork.
This image is not a calibrated experiment or a quantitative measurement of
penumbra width. The adjacent [soft-shadow study](../soft-shadow-study/README.md) contains that separate work.

The material combines 89% colored non-refracting transparency and 11% diffuse
surface shading. It is not physical spectral glass or a caustics simulation.
All displayed color is view-transformed through AgX. Fine path-tracing noise
is retained; denoising is disabled for the tested Blender build.

## Geometry

An S-shaped strip uses 220 longitudinal segments, with height strictly increasing
from 0.045 to 1.745 scene units. Each cross-section has constant height and nonzero
width. Disjoint longitudinal segments occupy disjoint height intervals, so the
strip does not fold into or intersect itself. A hairline teal perimeter clarifies
the shape without an opaque supporting frame.

## Rebuild

```sh
blender -b -t 2 --python build.py
```

Tested with Blender 4.3.2, Cycles CPU, two threads, 64 samples. The script resolves
outputs relative to itself; the saved blend uses a relative render path. No loop
is included: the still already expresses the transition without adding motion
for its own sake. The original Garden of Light and controlled study are unchanged.

## Verification

Final still inspected at actual output resolution: the entire ribbon and its
soft shadow are framed, with intentional negative space above and around them.
The mesh has 442 vertices and 220 nonzero-area faces, strictly increasing section
heights, and no self-folding. Saved blend reopened with five scene objects,
relative render output, and no external image dependencies. Renderer text/EXIF
metadata is stripped from the PNG without changing its image/color chunks;
decoded pixel equality was independently verified.
