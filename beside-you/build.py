#!/usr/bin/env python3
"""Beside You: one restrained procedural variation, without voices or recordings."""
import os
for key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import numpy as np
import scipy
from scipy.signal import butter, sosfilt
from rain_source import SR, SECONDS, synth, band, db, ff, write_wav, loudness, inspect, waveform


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def render():
    rng = np.random.default_rng(2026110213)
    original, events = synth()
    # The original's measured linear gain, retained rather than loudness-normalizing
    # the quieter cabin back up. The outside layer is otherwise identical.
    original *= 10 ** (12.88 / 20)
    t = np.arange(len(original)) / SR
    progress = smoothstep((t - 5.7) / 4.3)
    exterior_gain = 10 ** (-6 * progress / 20)
    exterior = original * exterior_gain[:, None]
    fade = np.sin(np.minimum(np.clip(t / 2.4, 0, 1), np.clip((SECONDS-t)/3, 0, 1)) * np.pi / 2) ** 2
    common = band(rng.normal(size=len(t)), 180, 900)
    independent = band(rng.normal(size=(len(t), 2)), 220, 800)
    fan = common[:, None] * .94 + independent * .06
    fan /= np.sqrt(np.mean(fan ** 2))
    fan *= (.0045 * progress * fade)[:, None]
    cues = np.zeros_like(original)

    def cue(onset, duration, low, high, amplitude, pan, cloth=False):
        tt = np.arange(int(duration * SR)) / SR
        noise = band(rng.normal(size=len(tt)), low, high)
        noise /= np.std(noise)
        if cloth:
            env = np.sin(np.pi * tt / duration) ** 2
            env *= .6 + .4 * np.sin(2 * np.pi * 3.1 * tt + .4) ** 2
        else:
            env = (1 - np.exp(-tt/.008)) ** 2 * np.exp(-tt/.025)
            env *= np.cos(np.pi * tt/(2*duration)) ** 2
        body = noise * env * amplitude
        gains = np.sqrt([(1-pan)/2, (1+pan)/2])
        start = int(onset * SR)
        cues[start:start+len(tt)] += body[:, None] * gains

    cue(5.5, .17, 500, 2200, .022, -.12)
    cue(13.2, .68, 420, 1900, .006, .40, cloth=True)
    cues = sosfilt(butter(3, 110, 'highpass', fs=SR, output='sos'), cues, axis=0)
    fan = sosfilt(butter(3, 110, 'highpass', fs=SR, output='sos'), fan, axis=0)
    x = exterior + fan + cues
    x[0] = x[-1] = 0
    # Compare matching source frames, not different moments of irregular rainfall.
    region = slice(10 * SR, 35 * SR)
    rms = lambda a: float(np.sqrt(np.mean(a ** 2)))
    mask = {
        'comparison_window_seconds': [10, 35],
        'exterior_rms_change_db_vs_identical_original_frames': db(rms(exterior[region])/rms(original[region])),
        'exterior_rms_dbfs': db(rms(exterior[region])),
        'fan_rms_dbfs': db(rms(fan[region])),
        'fan_to_exterior_rms_db': db(rms(fan[region])/rms(exterior[region])),
        'mix_rms_change_db_vs_identical_original_frames': db(rms(x[region])/rms(original[region])),
        'interpretation': 'Signal-level comparison only; not a perceptual masking or comfort test.',
    }
    return x, mask


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, default=Path(__file__).resolve().parent)
    out=ap.parse_args().out
    out.mkdir(parents=True, exist_ok=True)
    x, comparison=render()
    wav=out/'beside_you.wav'
    mp3=out/'beside_you_preview.mp3'
    x=write_wav(wav, x)
    ff('-y','-i',wav,'-map_metadata','-1','-c:a','libmp3lame','-b:a','128k','-threads','1',mp3)
    raw=subprocess.run(['ffmpeg','-hide_banner','-nostdin','-threads','1','-i',str(mp3),'-f','f32le','-acodec','pcm_f32le','-'],check=True,capture_output=True)
    p=np.frombuffer(raw.stdout,dtype='<f4').reshape(-1,2).astype(float)
    report={'title':'옆자리 / Beside You', 'review_scope':'Numerical only; audio input unavailable. No perceptual audition performed.',
            'comparison':comparison,'wav':inspect(x),'mp3_decoded':inspect(p),
            'wav_ffmpeg_loudnorm':loudness(wav),'mp3_ffmpeg_loudnorm':loudness(mp3),
            'numpy':np.__version__,'scipy':scipy.__version__,
            'ffmpeg':subprocess.run(['ffmpeg','-version'],capture_output=True,text=True).stdout.splitlines()[0],
            'sha256':{a.name:hashlib.sha256(a.read_bytes()).hexdigest() for a in [wav,mp3]}}
    for name, a in [('wav',x),('mp3_decoded',p)]:
        mono=a.mean(axis=1)
        report[name]['mono_fold_rms_change_db_vs_stereo_mean_power']=db(np.sqrt(np.mean(mono**2)/np.mean(a**2)))
        report[name]['first_last_10ms_peak']=float(np.max(np.abs(np.concatenate([a[:480],a[-480:]]))))
        q=report[name]
        assert q['all_samples_finite'] and q['clipped_samples']==0
        assert q['sample_peak_dbfs'] < -8 and q['duration_seconds']==38
        assert max(abs(v) for v in q['dc_mean_per_channel'])<.00001
        assert q['power_fraction_below_80hz']<.01
        assert q['mono_fold_rms_change_db_vs_stereo_mean_power'] > -1
        assert q['first_last_10ms_peak'] < .0001
    assert abs(comparison['exterior_rms_change_db_vs_identical_original_frames']+6)<.0001
    assert comparison['mix_rms_change_db_vs_identical_original_frames'] < -4
    for key in ['wav_ffmpeg_loudnorm','mp3_ffmpeg_loudnorm']:
        assert float(report[key]['input_tp']) < -8
        assert -33 < float(report[key]['input_i']) < -25
    (out/'qa.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    waveform(out/'waveform.svg',x)
    svg=(out/'waveform.svg').read_text().replace('WINDOW RHYTHMS','BESIDE YOU')
    (out/'waveform.svg').write_text(svg)
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
