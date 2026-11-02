# 옆자리 / Beside You

**A heater switch. A little movement in the passenger seat. No one needs to speak.**

One restrained, 38-second alternate to *차창 밖의 박자 / Window Rhythms*. This fictional parked-car scene depicts cold rain, a heater, and the suggestion of a silent companion. It makes no claim about any real person or situation.

## Listen

`beside_you_preview.mp3` is the small 128 kb/s preview; `beside_you.wav` is the 48 kHz stereo 16-bit PCM master. Start playback at a low device volume. File-level measurements do not establish physical listening safety. Nothing autoplays.

| Time | Intended narrative cue |
|---|---|
| 0–5 s | The original exterior rain enters |
| 5.5 s | One muted procedural heater-switch click |
| 5.7–10 s | Soft fan rises while the outside layer settles by 6 dB |
| 13.2–13.9 s | A small filtered-noise cloth/seat movement, slightly right |
| 14–35 s | Fan, rain, and space; no conversational cue |
| 35–38 s | Smooth fade to silence |

The outside attenuation is a creative change in listening perspective, **not** a physical claim that a heater reduces rain volume. No voices, breathing, melody, recordings, or external assets were added. The fan is correlated band-limited noise, not a tonal drone or binaural effect. This is audio art, not a health or sleep product.

The original experiment remains untouched. `rain_source.py` vendors its deterministic instrument and measurement helpers so this folder can rebuild independently; no parent-folder imports or hidden inputs are required. The original source gain is retained. There is no upward loudness normalization, compressor, or limiter in this alternate.

## Rebuild and inspect

Requires Python 3.10+, NumPy/SciPy from `requirements.txt`, and FFmpeg with libmp3lame.

```sh
python build.py
python build.py --out /tmp/beside-you-repeat
```

No network access or asset downloads occur during the build. Random seeds are fixed; worker threads are restricted. Byte-identical output is verified for repeated runs on the installed toolchain; another FFmpeg/library version may produce different bytes.

## Numerical QA — not a listening review

Audio input was unavailable. **No perceptual audition was performed.** The intended fan, cloth, and warmer interior cues are unverified perceptually. These measurements cannot establish pleasantness, audible realism, subjective warmth, or actual masking success.

| Metric | WAV master | Decoded MP3 |
|---|---:|---:|
| Duration | 38.000 s | 38.000 s |
| Integrated loudness | −31.09 LUFS | −31.51 LUFS |
| True peak | −11.97 dBTP | −12.50 dBTP |
| Clipped samples | 0 | 0 |
| Stereo correlation | 0.955 | 0.951 |
| Mono-fold RMS change | −0.100 dB | −0.109 dB |
| Power below 80 Hz | 0.00221% | 0.00256% |
| First / last 10 ms | Exact zero | Exact zero |

Maximum absolute channel DC mean is below 2.7e−7. Both files decode to exactly 1,824,000 stereo sample frames. Other players' gapless behavior is not verified.

**Matching-frame comparison, 10–35 seconds:** exterior RMS is exactly 6.00 dB below the same original frames; fan RMS is 11.70 dB below that exterior layer; the complete mix is 5.72 dB below the original. The fan is not simply piled onto the old mix at its old level. These are energy measurements, not a perceptual masking model. Integrated loudness is approximately 5.1 LU lower than the original master.

`qa.json` contains complete measured results and audio SHA-256 hashes. In the retained FFmpeg loudnorm diagnostics, only **`input_*`** describes the delivered audio; `output_*` is discarded analysis-filter output, not an applied normalization. `reproducibility.json` compares independent rebuilds. `waveform.svg` shows min/max stereo waveforms on a full-scale linear axis, not autoscaled.

The builder asserts no clipping, finite samples, correct duration, low DC/deep-bass energy, restrained true peak and loudness, mono compatibility, low endpoint levels, exact exterior attenuation, and a quieter matching-window mix. These are technical checks, not promises of comfort.
