# 차창 밖의 박자 / Window Rhythms

**38 seconds inside a parked car, while the rain goes on without you.**

An original procedural audio miniature: irregular soft droplets on glass, a narrow stereo field, and two distant road-wash swells. The rain thins out between clusters; nothing arrives that needs an answer. No recordings, speech, borrowed music, external assets, or binaural effects are used. This is an art study, not a therapeutic or sleep product.

## Listen

- `window_rhythms_preview.mp3` — 128 kb/s stereo preview, about 595 KiB.
- `window_rhythms.wav` — 48 kHz, stereo, 16-bit PCM master, about 7 MiB.

Start with your device volume low and adjust comfortably. Restrained digital levels do **not** guarantee a safe physical listening level; the playback device and volume still matter. Nothing autoplays.

## Little score

| Time | Gesture |
|---|---|
| 0–6 s | A slow entrance and the first loose gathering of droplets |
| 6–14 s | Another gathering, then distant tires swelling and receding |
| 14–21 s | A few closer drops; room for the background to fall away |
| 21–30 s | Rain returns; a second road wash passes outside |
| 30–38 s | Final scatter, then a three-second fade to zero |

Each droplet is a seeded, band-limited noise burst with a small decaying glass resonance and a 3–7 ms rounded attack. The road layer combines shared and quieter independent stereo noise, filtered above the deep bass region. A final 110 Hz high-pass filter removes DC/deep low-frequency energy. The whole piece has a 2.4-second fade-in and 3-second fade-out. There is no repeating music grid and no added reverb tail.

## Rebuild

Requires Python 3.10+, NumPy, SciPy, and FFmpeg with `libmp3lame`. No downloads or network calls occur in the builder.

```sh
python -m pip install numpy scipy  # only if absent; requires package access
python build.py
# Or put all generated outputs elsewhere:
python build.py --out /tmp/window-rhythms-check
```

The script fixes the random seed (`20261102`) and limits numerical-library/FFmpeg worker threads. It renders one process at a time, sets linear gain from a measured first pass, writes the master, encodes the preview, decodes and inspects that preview, and regenerates the score, waveform and QA. No limiter or compressor is applied. Exact hashes are reproducible with the same NumPy/SciPy/FFmpeg versions; codecs/library changes can alter the bytes. `requirements.txt` records the tested Python library versions, and `qa.json` records the FFmpeg build.

## Verification

**Numerical review only; this work has not been perceptually auditioned.** A waveform or a loudness measurement cannot verify that synthesized rain sounds convincing, pleasant, or free of perceptually distracting details. The environment's Dummy audio backend is not a listening review.

| Measurement | WAV | Decoded MP3 |
|---|---:|---:|
| Duration | 38.000 s | 38.000 s |
| Integrated loudness | −26.00 LUFS | −26.42 LUFS |
| True peak | −10.06 dBTP | −10.96 dBTP |
| Loudness range | 10.00 LU | 10.00 LU |
| Clipped samples | 0 | 0 |
| L/R correlation | 0.954 | 0.949 |
| Maximum absolute channel DC mean | 5.96e−9 | 3.35e−7 |
| Power below 80 Hz | 0.00232% | 0.00269% |

Both channels begin and end at exact zero. The left/right RMS difference is under 0.1 dB. The correlated stereo image avoids phase-inverted channels and has strong mono compatibility. Every sample is finite. Assertions enforce duration, clipping, DC, deep-bass energy, peak and integrated-loudness bounds.

`qa.json` holds the actual samples/codec measurements and audio SHA-256 hashes; `score.json` holds all 66 drop onsets, durations and pans. `waveform.svg` displays a full-scale min/max waveform (not an autoscaled drawing). `reproducibility.json` records the independent repeated-build comparison.

The `*_ffmpeg_loudnorm` entries retain FFmpeg's complete measurement report. **Only `input_*` describes the delivered audio.** `output_*` describes the analysis filter's discarded output; the delivered files do not use that dynamic normalization.

## Files

- `build.py` — entire procedural instrument and verifier
- `requirements.txt` — tested Python dependency versions
- WAV / MP3 — master and small preview
- `score.json` / `qa.json` / `reproducibility.json` — reproducible event data and numerical evidence
- `waveform.svg` — lightweight stereo waveform overview

No game project was modified. No external asset licenses are needed for this self-generated piece.

### Supplemental playback check

Run `python verify_playback.py` to regenerate `playback_qa.json` without changing the audio. Mono folding changes RMS by only −0.102 dB (WAV) / −0.112 dB (MP3), with no substantial cancellation. FFmpeg gapless MP3 decoding returns exactly 1,824,000 frames, matching the WAV. Both first and last 10 ms windows are exact digital silence in both files (the report's −300 dBFS is a finite logging floor for zero). Gapless behavior in other players is not verified. Low-frequency energy and stereo correlation are already covered in the main QA above. No perceptual listening review was possible.
