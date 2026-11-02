# Glass Refuge — interactive architectural study

A small standalone Godot 4.6 viewer of the actual editable Glass Refuge model. This is the next step of an original **GPT Image concept → Blender model → realtime interaction** experiment. It is not a game expansion, an image billboard, a reconstruction of a real building, or construction documentation.

## Open / controls

Open `project.godot` in Godot **4.6.3** or a compatible 4.6 release, then run the main scene. Alternatively:

```sh
godot --path /path/to/glass_refuge_viewer --audio-driver Dummy
```

- **Arrow keys:** orbit horizontally / raise or lower the viewpoint.
- **+ / = and −:** zoom in/out, with limits.
- **L:** toggle the real pendant light and its globe emission.
- **G:** hide/show glazing for structural inspection.
- **R:** reset camera, lamp and glazing.
- Optional left-drag / wheel orbit and zoom. Mouse capture is never required.
- Clicking the controls does not steal the arrow-key navigation focus. Drag state clears when the window loses focus. There is no walking mode.

## What is actually included

`assets/refuge.glb` contains **78,388 triangles, 33 mesh nodes, 35 material surfaces and 10 material definitions**, measured from the actual exported GLB, not estimated from the source. Its size is 3,617,000 bytes. It contains curved framing, copper covers and fittings, 24 glass panes, sage boarding, bench/cushions/throw, an empty planter box, the pendant fixture and stone terrace/approach. The 316 selected source mesh objects were converted in a derivative process and merged into 33 nodes. Bounds before and after merging agree within 0.00001 Blender units. Dimensions are interpreted design choices, not survey measurements.

There are no downloaded assets, texture maps, heavyweight bakes, or external plugins. The source Blender scene and final Cycles render were not modified. The existing After-the-Rain project is not referenced or changed.

## Honest visual differences

- The source's procedural wood grain, copper variation, cloth weave, wet stone bump and droplet microdetail are replaced by approximate constant PBR colors/roughness. **This is not Cycles visual parity.**
- All botanical meshes and the distant landscape were omitted. The planter box remains intentionally empty.
- Glass uses restrained alpha blending, not physical transmission/refraction. It may show overlapping-transparency sorting differences; the G toggle exposes the structure clearly.
- Three Cycles area lights and its procedural world do not transfer. The viewer instead uses a saved dusk environment, one directional light and a dynamic pendant OmniLight. No indirect-light bake is claimed.
- Source nominal dimensions, glazing safety, supports, drainage, accessibility and building-code compliance are not validated.

## Saved scene architecture

- `scenes/viewer.tscn` / `scripts/viewer.gd`: visible composition root, environment/UI, explicit child wiring.
- `scenes/refuge.tscn` / `scripts/refuge.gd`: imported derived geometry and per-instance glass state.
- `scenes/view_rig.tscn` / `scripts/view_rig.gd`: camera orbit/zoom/reset only.
- `scenes/pendant.tscn` / `scripts/pendant.gd`: owns lamp state; receives the original globe mesh explicitly from the root.

There are no autoloads, global game-state managers, hidden generated world replacements, physics controllers or changes to the source `.blend`. The GLB hierarchy remains inspectable in the editor. Runtime material overrides are intentional and local to each instance; tests check that one viewer does not alter another's state.

## Reproduce the derivative

The runtime is self-contained. Rebuilding the GLB additionally requires Blender 4.3.2 and the separately preserved source `.blend`:

```sh
blender -b -t 2 --python tools/export_refuge.py -- --source /path/to/Glass_Refuge.blend
godot --headless --path . --editor --import
godot --headless --path . --script res://tools/test_viewer.gd
```

When no source argument or already-open Blender file is supplied, the exporter looks for the public sibling `../glass-refuge/Glass_Refuge.blend` (hyphenated repository folder). The standalone runtime does not need that sibling. The export script reads the source in memory, evaluates modifiers, replaces materials only in that in-memory derivative, merges static opaque groups, preserves separate glass panes/globe, and exports a GLB. It never saves the source Blender file, and checks the source SHA-256 before/after. The recorded source hash is in `qa/export_audit.json`.

## Verification and limits

- Actual GLB topology/material counts: `qa/glb_audit.json`.
- Source hash preservation and pre/post merge bounds: `qa/export_audit.json`.
- Headless logic: **42 checks passed**, including a complete orbit, zoom/pitch limits, lamp/glass/reset key handlers, key-repeat suppression, repeated toggles, independent instances, and free/reinstantiate behavior. `qa/headless_tests.json`.
- Separate native-window inspection passed: actual front/side/rear pixels and a full orbit, vertical arrow navigation, zoom, reset, visibly different lamp on/off illumination, glass visibility, and keyboard navigation after clicking a UI button. The final state is the default front three-quarter view with lamp and glass ON. Logical-key events with `physical_keycode == 0` are supported and tested.
- Remote zero-duration letter taps were unreliable; deliberate 200–250 ms taps worked consistently. This is noted rather than claiming every remote input timing was reliable.
- Native renderer observed: Mesa llvmpipe / OpenGL Compatibility. FPS was not measured. Environment warnings reported unsupported V-Sync switching and no audio device; the silent viewer falls back to dummy audio. The launch command above explicitly selects Dummy audio.
- A fresh copy containing only the 25 publication files imported successfully without an existing `.godot` cache and passed the same 42 headless tests. No sibling source blend is required to run it.
- Renderer: Compatibility. No automatic-instancing performance claim, baked GI, or target-device FPS guarantee is made.

### Source provenance note

The recorded source SHA-256 identifies the original working Blender file used for this derivative. The separately published `glass-refuge/Glass_Refuge.blend` may have a different file hash because publication removes absolute editor/image paths without changing geometry or packed reference pixels. Re-exporting from that normalized public sibling records its own input hash; differing container metadata hashes do not imply a geometry change.
