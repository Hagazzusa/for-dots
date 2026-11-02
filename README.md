# for-dots · small worlds and studies

Playable rainy-night scenes, original procedural art, and bounded geometric/light studies.
Source, editable scenes, and preview evidence are kept together so each project can be reopened independently.

| Project | Start here | Requirements |
|---|---|---|
| **After the Rain** — a quiet bus stop, warm cocoa, optional neighborhood encounters | [Game instructions](after-the-rain/README.md) · [reconstruction status](after-the-rain/RECOVERY.md) | Godot **4.6.x Standard**; open `after-the-rain/project.godot`, press F5. Blender is not required to play. |
| **Rain Clock** — virtual kinetic sculpture | [Source / render instructions](rain-clock/README.md) · [still](rain-clock/rain_clock_still.png) · [loop](rain-clock/rain_clock_loop.mp4) | Blender **4.3.2**; ffmpeg for encoding regenerated frames. |
| **Rain Clock mechanism studies** — geometric alternatives and measured limitations | [Study index](rain-clock/STUDY_INDEX.md) · [manual mechanism](rain-clock/mechanism/README.md) | FreeCAD for `.FCStd`; Blender for procedural previews. Each study documents its script and assumptions. |
| **Garden of Light** — moving light through three colored filters | [Instructions](garden-of-light/README.md) · [still](garden-of-light/Garden-of-Light.png) · [loop](garden-of-light/Garden-of-Light-loop.mp4) | Blender **4.3+**; ffmpeg for video; Pillow, numpy and ffprobe for pixel/video QA. |
| **When two filters overlap** — controlled scene-linear RGB experiment | [Results / reproduction](filter-overlap-study/README.md) · [comparison](filter-overlap-study/Filter-Overlap-Comparison.png) | Blender **4.3+** (bundled numpy); Python with Pillow for the contact sheet. Six linear EXRs retain measurement evidence. |
| **Three heights, one light** — soft-shadow artwork and controlled penumbra study | [Study / reproduction](soft-shadow-study/README.md) · [artwork](soft-shadow-study/Three-Heights-One-Light.png) · [evidence](soft-shadow-study/Penumbra-Evidence.png) · [resolution check](soft-shadow-study/Resolution-Check.png) | Blender **4.3+** (bundled numpy); Python with matplotlib/numpy for figures. Ten linear EXRs retain measurements; two resolutions qualify precision, not establish convergence. |

## Scope and limits

- The game is a **new reconstruction from surviving V7 source**, not recovered V37 code or historical test results. Its current controls include WASD movement, mouse/arrow-key look, Space pause/help, and contextual E interactions. Audio generation was checked, but perceptual audition was unavailable on the test machine's dummy audio driver. Software-renderer performance is not a hardware performance guarantee.
- Rain Clock and Garden of Light are virtual art, not validated products. The CAD studies establish only their stated nominal or sampled geometry; retention, tolerances, strength and manufacturability remain unvalidated. Read individual caveats before interpreting a diagram as a design recommendation.
- Filter measurements test a non-refracting **RGB shader model**, not spectral transmission or actual glass. Display PNG values are not the linear EXR measurement data.
- Original art is procedural. The game also includes third-party city assets and a font; their provenance and license texts remain in `after-the-rain/assets/city/licenses/` and `after-the-rain/assets/fonts/`. This index does **not** assign one blanket license to the repository.

## Check a downloaded copy without engines or credentials

From the repository root, with Python 3.8+:

```sh
python3 verify_sources.py
```

The read-only check compares every manifest-listed file's size and SHA256 using only Python's standard library. No Git, network, credentials, Godot, Blender or FreeCAD is needed for verification. Unlisted local files (such as caches, renders and editor backups) are ignored. The manifest does not list itself.

This detects missing/changed checkpoint bytes; it does **not** prove correctness, safety, authorship or authenticity against a maliciously replaced manifest. Use trusted Git commit history for provenance. Project-specific validators still test their own scene or numerical behavior.

After intentionally editing source, review and stage the intended files, then update the manifest:

```sh
git add <reviewed-files>
python3 verify_sources.py --refresh
python3 verify_sources.py
git add SOURCE_MANIFEST.json
```

Refresh requires Git and hashes the working bytes of tracked/staged regular files; review your diff before committing. It never includes untracked files automatically, follows no symlinks, and excludes only the manifest itself. Keep private data and generated caches out of the tracked set.
