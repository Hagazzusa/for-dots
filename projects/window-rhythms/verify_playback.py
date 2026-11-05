#!/usr/bin/env python3
"""Read-only supplemental mono-fold and codec-endpoint measurements."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import json
from pathlib import Path
import subprocess
import numpy as np
from build import SR, SECONDS, db

root = Path(__file__).resolve().parent
results = {}
for name in ['window_rhythms.wav', 'window_rhythms_preview.mp3']:
    run = subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-threads', '1', '-i', str(root / name),
                          '-f', 'f64le', '-acodec', 'pcm_f64le', '-'], capture_output=True, check=True)
    x = np.frombuffer(run.stdout, dtype='<f8').reshape(-1, 2)
    mono = x.mean(axis=1)
    stereo_energy = np.mean(x ** 2)
    edge = int(.01 * SR)
    results[name] = {
        'decoded_sample_frames': len(x),
        'expected_sample_frames': SR * SECONDS,
        'mono_fold_rms_change_db_vs_stereo_mean_power': db(np.sqrt(np.mean(mono ** 2) / stereo_energy)),
        'stereo_correlation': float(np.corrcoef(x.T)[0, 1]),
        'first_10ms_peak_dbfs': db(np.max(np.abs(x[:edge]))),
        'last_10ms_peak_dbfs': db(np.max(np.abs(x[-edge:]))),
        'first_last_sample_peak': float(np.max(np.abs(x[[0, -1]]))),
    }
    assert len(x) == SR * SECONDS
    assert results[name]['mono_fold_rms_change_db_vs_stereo_mean_power'] > -1
    assert results[name]['first_10ms_peak_dbfs'] < -80
    assert results[name]['last_10ms_peak_dbfs'] < -80
(root / 'playback_qa.json').write_text(json.dumps({
    'review_scope': 'Numerical only. No audible quality or physical listening-level assertion.',
    'interpretation': 'FFmpeg gapless decode returns exactly the intended frame count; negligible mono energy loss and near-zero endpoint windows.',
    'results': results}, indent=2) + '\n')
print(json.dumps(results, indent=2))
