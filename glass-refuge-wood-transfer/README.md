# Glass Refuge — wood-albedo transfer comparison (512 / 1024)

This is a **separate technical proof**, not a replacement for the frozen viewer or current game. The original model and frozen viewer remain unchanged; native A/B observations belong to this separate study.

## Comparison result

The single 1024 refinement uses exactly the accepted normalized UV layout and mapping, with 8-pixel dilation and ~16-pixel island gaps. It took **2.94 seconds** at the same 8 samples / 2 CPU threads. The 1024 PNG is 642,380 bytes; its GLB is 4,294,328 bytes (+437,764 bytes versus 512). Position/normal/UV/index accessor bytes match the 512 GLB exactly. Only the image resolution/payload changes.

Actual atlas pixels show finer grain at 1024. In the identical 640×640 applied-wood view, the improvement is modest: posts/bench sharpen somewhat, while the broad soft/banded arch appearance remains. Higher resolution does not fix the source mapping or add surface relief. This is not grounds for an automatic production promotion.

Current `assets/refuge.glb` is the **1024 proof**, not the 512 baseline. Historical 512 figures below describe the retained comparison. Both atlas PNGs and applied previews are preserved. Native variant QA is recorded below; no production promotion has occurred.

### Historical 512 proof

- One 512 × 512 albedo-only emission bake, 8 samples, 2 CPU threads, measured **2.00 seconds**. No lighting, AO, normal, roughness or metallic map was baked.
- Atlas PNG: `assets/wood_albedo_512.png` (204,619 bytes).
- Actual applied wood-only Workbench inspection: `qa/wood_512_applied.png`. Workbench lighting is diagnostic, not a final beauty render.
- Retained `assets/refuge_512.glb`: **3,856,564 bytes; 33 mesh nodes, 35 surfaces, 78,388 triangles; one embedded texture**. The embedded image matches the atlas pixels exactly.
- Godot 4.6.3 headless import confirms the oak texture is 512² and material emission is disabled. The 42 viewer logic checks still pass. No FPS claim is made. Native appearance was subsequently inspected as described below.

## What was fixed before baking

The original 27 cube-based wood objects reused identical UV nets; five curved ribs had no UVs. An all-smart-project layout produced 212 islands and only 17.66% coverage. Reusing connected cube nets initially failed because selecting mesh faces with UV sync disabled did not select legacy UV loops. Explicit UV selection resolved the overlap bug.

The final layout uses 95 islands. A fractional packing margin of 4/512 per island side produces a measured ~8-pixel gap. Analytic checks find zero positive-area triangle overlaps, zero degenerate UV triangles and all UVs inside the atlas. Coverage is **31.27%**; bake dilation is 4 pixels. Sampled native front, oblique and distant views showed no conspicuous atlas-color bleed; this is not exhaustive mip-level coverage.

Area-average density is about 46.52 texels/metre, but the reused cube-net charts are anisotropic. Broad-face area-weighted directional densities are about 168 texels/metre in the high-resolution direction and 11 in the low-resolution direction. Actual pixels show meaningful long grain on posts and bench; arch texture remains softer/patchier. These measurements do not prove full procedural-shader fidelity.

## Mapping and limits

The source uses Generated coordinates → multiply (5,5,0.23) → Noise → ColorRamp → oak Base Color. Each original object's normalized local bounds were captured as a point attribute **before** bevel evaluation and joining. That explicit attribute drives the original color network during baking. This is a reconstruction of Generated mapping, **not independently proven bit-exact Blender ORCO equivalence**.

Only the oak base color transfers. All other materials retain the frozen viewer's approximate constant PBR values. Surface bump and microscopic detail are absent. The lamp remains dynamic because its illumination was not baked into the wood.

## Reproduce the bounded proofs

From this directory, with Blender 4.3.2, Python 3 and Godot 4.6.3 available:

```sh
blender -b -t 2 --python tools/prepare_wood_atlas.py -- --source ../glass-refuge/Glass_Refuge.blend
python3 tools/validate_wood_uv.py
blender -b -t 2 tmp/wood_prebake.blend --python tools/bake_wood_proof.py
blender -b -t 2 tmp/wood_512_proof.blend --python tools/export_refuge.py -- --output assets/refuge_512.glb
blender -b -t 2 tmp/wood_prebake.blend --python tools/bake_wood_1024.py
blender -b -t 2 tmp/wood_1024_proof.blend --python tools/export_refuge.py
python3 tools/validate_candidate.py # requires Pillow
godot --headless --path . --editor --import
godot --headless --path . --script res://tools/test_wood_texture.gd
godot --headless --path . --script res://tools/test_viewer.gd
```

The preparation and bake save derivative files only under this experiment's `tmp/`. Never save over the source Blender file. The source input hash and protected viewer hash are recorded in the QA reports. A metadata-normalized public copy of the source may have a different container hash without a geometry change.

**Status:** One 512 proof and one 1024 comparison are complete. The 1024 texture import and all 42 viewer logic checks pass. A separate native A/B study was inspected. No additional materials or production integration were performed. Device performance remains unmeasured.

RGBA8-equivalent texture storage with a full mip chain increases from about 1.33 MiB to 5.33 MiB (four times the pixels); actual Godot GPU compression/storage was not measured. No FPS claim is made. Protected original source, final render and frozen viewer hashes remain unchanged.

## Native comparison study

The explicitly labeled study offers **B** (or the Wood button) to swap only the 512/1024 albedo texture on the same mesh, material and camera; **R** restores 1024/front/lamp ON/glass ON. Native close front and oblique A/B showed modest finer post grain at 1024, little practical improvement at ordinary framing, and persistent broad arch softness. Lamp OFF visibly removes warm illumination, confirming dynamic lighting is retained. Keyboard orbit/zoom and glass visibility were exercised. Exact close-view screenshots are in `qa/native_close_512.jpg` and `qa/native_close_1024.jpg`.

Recommendation: retain this as a successful color-transfer proof, not an automatic production upgrade. 512 is defensible for ordinary viewing; 1024 offers a small close-up benefit at four times uncompressed texture storage. Better arch detail needs a more isotropic chart layout or an explicitly approximate trim-sheet, not another resolution increase. No further bake is planned. Both atlases load during A/B, so this study is not a clean memory benchmark.

## Chosen integration candidate: 512

Use **`assets/refuge_512.glb`**, not the 1024 study GLB with an external override. It embeds exactly one 512² image; all geometry, index, normal and UV accessor bytes, mesh/surface structure and nodes match the 1024 proof. Validation: `qa/candidate_512_validation.json`. This is the previously exported 512 proof, preserved without a third bake.

512 is selected for a separately tested world candidate: ordinary-distance grain is meaningful, while 1024 costs another 437,764 GLB bytes and approximately 4 MiB RGBA8-equivalent mipmapped texture storage for a modest close-up gain. Actual GPU memory and FPS were not measured. Arch softness and anisotropic charts remain documented limits. The current game is unchanged.

The reproducible scripts create `tmp/` intermediates locally; these are not publication dependencies. Preparation accepts `--source`, or the public sibling `../glass-refuge/Glass_Refuge.blend` by default. The runtime study is self-contained. `PUBLICATION_MANIFEST.json` is the explicit allowlist; omit `.godot`, `tmp`, import caches, logs, UV raw data, superseded failed-layout reports and unused exporter texture sidecars.
