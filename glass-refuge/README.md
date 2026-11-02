# Glass Refuge — image → editable spatial study

An original, procedural Blender reconstruction of an original GPT Image concept. This is an architectural **design study**, not a construction or engineering package.

## Provenance

- `reference/gpt_image_concept.png` is the preserved original concept image, generated with the built-in GPT Image tool before modeling. No source pixels were painted over.
- Concept brief (human-readable summary, not a claim to reproduce the exact generation prompt): a small curved timber-and-glass garden refuge on a wet stone terrace, copper-clad ribs, muted sage lower panels, an open entrance, a cozy bench and warm globe pendant, overlooking a blue-hour lake landscape.
- All model geometry, materials, vegetation and background are newly authored procedural work in `build.py`. No downloaded assets, textures, HDRIs or external asset licenses are involved.
- The exact original generation prompt and provenance are preserved in `reference/concept_prompt.txt`. The original image was visually inspected before modeling. This is manual/procedural interpretation, **not automatic image-to-mesh conversion or exact CAD recovery**.

## What is observed / what is inferred

**Observed:** barrel-vault silhouette; repeated timber arches with dark copper weather caps; glazed roof and side walls; asymmetrical front with a narrow left sidelight and a wide open entrance; muted sage vertical boarding; timber bench with light and olive cushions and a draped throw; planted right-side box; suspended round warm light; raised dark stone platform and approach steps; wet evening surfaces.

**Inferred:** a 3.20 × 3.20 m nominal footprint, floor +0.42 m, spring line +2.32 m, roof crown +3.568 m; a shallow elliptical barrel; five regularly spaced ribs; 6 mm nominal glazing; complete rear wall; bench and planter joinery; post shoes and fasteners; glass panel subdivision; unseen contact/support relationships. Dimensions are chosen to make a coherent editable model, not measured from the picture. Perspective, generated-image inconsistencies and hidden surfaces prevent unique reconstruction.

**Deliberately simplified:** geographic landscape, clouds, dense wild plants, water droplets, upholstery wrinkles and weathering. The background is atmospheric scene dressing, not a reconstruction of an actual place.

## Files and use

- `Glass_Refuge.blend` — compressed editable scene, packed concept, named collections, saved camera, original materials.
- `build.py` — standalone deterministic source (Blender 4.3 or compatible).
- `renders/01_blockout.png` — initial small preview retained for comparison.
- `renders/05_final.png` — final 1200 × 800 image.
- `renders/06_structural_inspection.gif` and `.mp4` — **구조 확인용 / structural inspection**, 24 actual Workbench views. Glazing, landscape and light fixtures are intentionally hidden only for this output. This is not a beauty render.
- `inspection_turntable.py` — reproducible Workbench orbit, does not save changes to the model.
- `manifest.json` — SHA-256 hashes of the publication files.
- `audit.py` / `geometry_audit.json` — measured closed-solid, winding and packed-reference validation.
- `checks.json` — generated dimension and configuration checks.

From this directory:

```bash
mkdir -p tmp
TMPDIR="$PWD/tmp" blender -b -t 2 --python build.py -- --preview
TMPDIR="$PWD/tmp" blender -b -t 2 --python build.py
```

The script uses CPU Cycles, two render threads, no unsupported denoiser, 48 samples for later 600 × 400 previews (the first blockout used 24) and 128 samples for the 1200 × 800 final. Re-running replaces the `.blend` and corresponding render; the preview command writes `renders/preview.png` and does not replace the historical blockout. Materials and geometry remain editable; procedural curves are explicit mesh rib solids rather than opaque imported scans. The original concept is packed into the blend and also preserved as a separate PNG.

## Limits

No structural calculations, timber connection design, wind/snow loads, tempered/laminated safety-glass specification, foundation/soil design, water drainage, waterproofing, ventilation, thermal analysis, accessibility or building-code validation has been performed. A large open entry and nominal support contacts are geometric checks only. This is not fabrication-ready and must not be used as construction documentation.

## Comparison and refinement record

The first preview exposed a silhouette that was too tall/narrow and a camera that looked down too steeply. Pixel comparison motivated a lower camera and an elliptical rather than semicircular barrel: the revised eave is 1.90 m above the terrace and the roof rise is 1.248 m. This is a design inference, not recovered survey data.

The next pass corrected inward arch face winding, exposed the lake above the ground, shortened the planter to leave a positive gap before the bench, and reduced exterior amber fill. It replaced a hardcoded post-contact assertion with a vertex-bound measurement. A further check corrected a sky-coordinate sign and shortened the pendant cord after lowering the roof; the round globe itself was kept round. Stone corners and tops now vary rather than forming a perfect tile grid.

Noise control is explicit: Cycles CPU, 128 samples, direct sample clamp 10 and indirect clamp 2; no denoiser. The final clear-glass material uses 0.015 roughness and restrained micro-bump. Reflective/refractive caustics are disabled, another explicit render-time compromise. Clamping trades some highlight energy for fewer fireflies and is not a claim of radiometric fidelity. The scene is an editable reconstruction with recognizable architectural correspondence, **not photographic parity** with the generated image. Fine vegetation, weather, terrain complexity, textiles and random droplets remain substantially simpler.

Geometric checks concern the modeled envelope: nominal entrance width, arch clearance, globe low point, post contacts, closed outward-wound rib/glazing solids and a positive bench–planter gap. They do not verify a safe or buildable structure.

The final saved-file audit measured 1,000 mesh objects, 22 closed outward-wound arch/cap/roof-glass solids, no zero-area base mesh faces and no non-finite coordinates. The reference is confirmed packed. Post-contact testing checks the nominal terrace datum, not exact rough-stone contact or foundation load paths.

The publication package intentionally includes one historical blockout and the final result; intermediate local test renders and machine logs are omitted. The structural GIF uses material colors and simplified Workbench lighting, hides glass so the interior can be inspected, and is generated from the same saved editable model, not from synthesized image views.

## Portable saved copy

The publication copy normalizes the saved browser directory to `//` and render destination to `//renders/05_final.png`; both the image and its nested packed-file path use `//reference/gpt_image_concept.png`, with packed image bytes unchanged. Geometry, materials, camera and render settings are unchanged. A plain-text embedded concept-to-geometry guide records design limitations; it is not an executable script. Rebuilt files should be reviewed again before sharing.

To inspect the saved model or regenerate the simplified structural views:

```sh
blender -b Glass_Refuge.blend -t 2 --python audit.py
blender -b Glass_Refuge.blend -t 2 --python inspection_turntable.py
ffmpeg -y -framerate 8 -i renders/inspection_frames/%03d.png -c:v libx264 -pix_fmt yuv420p -map_metadata -1 renders/06_structural_inspection.mp4
```

The audit writes its JSON report. The inspection script changes only its in-memory scene and generated frames; it does not save those visibility or lighting changes into the delivery blend.
