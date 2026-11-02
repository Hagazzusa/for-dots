#!/usr/bin/env python3
"""Recompute image differences only; never edits any captured image.

Requires Pillow and NumPy. Output is qa/pixel_comparison.json.
This is not an optical correctness or general transparency-ordering test.
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image

root = Path(__file__).resolve().parent
rows = []
for view in ("high", "oblique", "low"):
    for key in ("on", "off"):
        a = np.asarray(Image.open(root / f"qa/opaque_{view}_{key}.png").convert("RGB"), dtype=np.int16)
        b = np.asarray(Image.open(root / f"qa/candidate_{view}_{key}.png").convert("RGB"), dtype=np.int16)
        assert a.shape == b.shape == (640, 720, 3)
        delta = np.max(np.abs(a - b), axis=2)
        delta[:52] = 0  # Material label differs by design.
        delta[-60:] = 0  # Fixed explanatory UI, not part of the scene test.
        yy, xx = np.where(delta > 2)
        rows.append({"view": view, "key": key,
                     "changed_scene_pixels_gt2": int(xx.size),
                     "max_scene_channel_delta": int(delta.max()),
                     "changed_bounds_xy": [int(xx.min()), int(yy.min()), int(xx.max()), int(yy.max())] if xx.size else None})
result = {"threshold_per_channel_8bit": 2, "excluded_ui_rows_top": 52,
          "excluded_ui_rows_bottom": 60, "comparisons": rows,
          "scope": "Pixel differences only; not a physical optical or all-angle proof."}
(root / "qa/pixel_comparison.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2))
