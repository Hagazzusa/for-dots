#!/usr/bin/env python3
"""Shared original rain synthesis and numerical helpers. Vendored for standalone reproduction."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import wave
import numpy as np
import scipy
from scipy.signal import butter, sosfilt, welch

SR = 48000
SECONDS = 38
SEED = 20261102


def band(x, low, high):
    return sosfilt(butter(2, [low, high], btype='bandpass', fs=SR, output='sos'), x, axis=0)


def ff(*args):
    return subprocess.run(['ffmpeg', '-hide_banner', '-nostdin', '-threads', '1', *map(str, args)],
                          check=True, capture_output=True).stderr.decode()


def write_wav(path, x):
    pcm = np.rint(np.clip(x, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as out:
        out.setnchannels(2)
        out.setsampwidth(2)
        out.setframerate(SR)
        out.writeframes(pcm.tobytes())
    return pcm.astype(np.float64) / 32768


def loudness(path):
    log = ff('-i', path, '-af', 'loudnorm=I=-26:TP=-9:LRA=11:print_format=json', '-f', 'null', '-')
    start = log.rfind('{')
    return json.loads(log[start:log.index('}', start) + 1])


def synth():
    rng = np.random.default_rng(SEED)
    n = SR * SECONDS
    t = np.arange(n) / SR
    # Correlated but not identical stereo: a stationary listener, not wide-panned traffic.
    shared = band(rng.normal(size=n), 170, 1700)
    sides = band(rng.normal(size=(n, 2)), 240, 2200)
    road = (shared[:, None] * .84 + sides * .16)
    road /= np.sqrt(np.mean(road ** 2))
    # Two slow, distant swells; long valleys preserve breathing space.
    wash = .0018 + .010 * np.exp(-.5 * ((t - 11.8) / 3.3) ** 2)
    wash += .008 * np.exp(-.5 * ((t - 28) / 3.8) ** 2)
    road *= wash[:, None]
    droplets = np.zeros((n, 2))
    events = []
    # Irregular clusters deliberately avoid a musical meter; no melody or tonal drone.
    for center, count, spread in [(3.8, 13, 1.2), (8.0, 10, 1.0), (15.8, 15, 1.5),
                                  (24.5, 12, 1.5), (32.5, 16, 1.4)]:
        for onset in sorted(rng.normal(center, spread, count)):
            onset = float(np.clip(onset, 1.3, 36.2))
            duration = float(rng.uniform(.09, .28))
            tt = np.arange(int(SR * duration)) / SR
            freq = float(rng.uniform(1100, 3400))
            noise = band(rng.normal(size=tt.size), 650, 5200)
            noise /= max(np.std(noise), 1e-8)
            # Soft 3–7ms attack, fast body, rounded taper; glass texture, not sharp ticks.
            attack = float(rng.uniform(.003, .007))
            env = (1 - np.exp(-tt / attack)) ** 2 * np.exp(-tt / (duration / 6))
            env *= .5 + .5 * np.cos(np.pi * tt / duration)
            body = (.85 * noise + .15 * np.sin(2 * np.pi * freq * tt)) * env
            amp = float(rng.uniform(.016, .041))
            pan = float(rng.uniform(-.62, .62))
            gains = np.sqrt([(1 - pan) / 2, (1 + pan) / 2])
            i = int(onset * SR)
            droplets[i:i + len(tt)] += amp * body[:, None] * gains
            events.append({'onset_s': round(onset, 4), 'duration_s': round(duration, 4),
                           'pan': round(pan, 4)})
    x = road + droplets
    # Remove DC / deep low frequency energy, then a smooth edge taper.
    x = sosfilt(butter(3, 110, 'highpass', fs=SR, output='sos'), x, axis=0)
    fade = np.minimum(np.clip(t / 2.4, 0, 1), np.clip((SECONDS - t) / 3, 0, 1))
    fade = np.sin(fade * np.pi / 2) ** 2
    x *= fade[:, None]
    x[0] = x[-1] = 0
    return x, sorted(events, key=lambda e: e['onset_s'])


def db(value):
    return float(20 * np.log10(max(float(value), 1e-15)))


def inspect(x):
    freqs, power = welch(x, fs=SR, nperseg=8192, axis=0)
    below = float(power[freqs < 80].sum() / power.sum())
    blocks = x.reshape(SECONDS * 10, SR // 10, 2)
    rms = np.sqrt(np.mean(blocks ** 2, axis=(1, 2)))
    return {'duration_seconds': len(x) / SR, 'sample_rate_hz': SR, 'channels': 2,
            'sample_peak_dbfs': db(np.max(np.abs(x))),
            'rms_dbfs_per_channel': [db(v) for v in np.sqrt(np.mean(x ** 2, axis=0))],
            'dc_mean_per_channel': np.mean(x, axis=0).tolist(),
            'clipped_samples': int(np.count_nonzero(np.abs(x) >= .9999)),
            'first_last_samples': [x[0].tolist(), x[-1].tolist()],
            'max_adjacent_sample_step': float(np.max(np.abs(np.diff(x, axis=0)))),
            'stereo_correlation': float(np.corrcoef(x.T)[0, 1]),
            'power_fraction_below_80hz': below,
            '100ms_rms_dbfs_range': [db(rms.min()), db(rms.max())],
            'all_samples_finite': bool(np.isfinite(x).all())}


def waveform(path, x):
    # Portable vector evidence: signed min/max per channel in 40ms bins.
    width, height = 1000, 330
    bins = x.reshape(950, -1, 2)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<rect width="100%" height="100%" fill="#14212c"/>',
             '<g fill="#dce5e8" font-family="sans-serif"><text x="25" y="26">WINDOW RHYTHMS · 38 seconds · linear full-scale waveform</text></g>']
    for ch, y in [(0, 110), (1, 235)]:
        parts.append(f'<path d="M25 {y}H975" stroke="#3a525f"/>')
        parts.append(f'<text x="25" y="{y-49}" fill="#a6bac5" font-family="sans-serif">{"LEFT" if ch == 0 else "RIGHT"} · ±1.0 FS</text>')
        for i in range(950):
            low, high = bins[i, :, ch].min(), bins[i, :, ch].max()
            parts.append(f'<path d="M{i+25} {y-high*48:.3f}V{y-low*48:.3f}" stroke="#9ac7ce"/>')
    parts.append('<text x="25" y="315" fill="#a6bac5" font-family="sans-serif">0s — numerical inspection only; not evidence of perceptual audition — 38s</text></svg>')
    path.write_text('\n'.join(parts))

