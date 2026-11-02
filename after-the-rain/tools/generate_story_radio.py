#!/usr/bin/env python3
"""Original three-phrase instrumental: deterministic local synthesis, no media inputs.

48 seconds, mono 22050 Hz signed PCM16. Envelope endpoints are silent for
continuous phrase/loop joins. Re-run this script to reproduce the committed WAV.
"""
from __future__ import annotations
import argparse
import io
import math
from pathlib import Path
import struct
import wave

RATE = 22050
PHRASE_SECONDS = 16
PHRASES = (
    ((48, 55, 60), (52, 59, 64), (53, 60, 65), (55, 62, 67)),
    ((45, 52, 57), (48, 55, 60), (50, 57, 62), (52, 59, 64)),
    ((53, 60, 65), (52, 59, 64), (50, 57, 62), (48, 55, 60)),
)
MELODIES = (
    (72, 67, 69, 64, 65, 69, 67, 62),
    (64, 69, 72, 67, 74, 69, 71, 64),
    (77, 72, 71, 67, 69, 65, 64, 60),
)
FRAMES = RATE * PHRASE_SECONDS * len(PHRASES)

def frequency(midi: int) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)

def synthesize_pcm() -> bytes:
    samples: list[float] = []
    tau = math.tau
    phrase_frames = RATE * PHRASE_SECONDS
    for chords, melody in zip(PHRASES, MELODIES):
        chord_freqs = [tuple(frequency(n) for n in chord) for chord in chords]
        melody_freqs = [frequency(n) for n in melody]
        for frame in range(phrase_frames):
            t = frame / RATE
            chord_index = min(3, int(t / 4.0))
            chord_t = t - chord_index * 4.0
            # Both pad and bell envelopes start/end at zero: no cut oscillators.
            pad_env = math.sin(math.pi * chord_t / 4.0) ** 2
            pad = 0.0
            for hz in chord_freqs[chord_index]:
                phase = tau * hz * chord_t
                pad += math.sin(phase) + 0.12 * math.sin(phase * 2.0)
            pad *= pad_env * 0.045
            note_index = min(7, int(t / 2.0))
            note_t = t - note_index * 2.0
            bell_env = min(1.0, note_t / 0.06) * min(1.0, (2.0-note_t) / 0.35)
            bell_env *= math.exp(-note_t * 1.9)
            phase = tau * melody_freqs[note_index] * note_t
            bell = (math.sin(phase) + 0.18*math.sin(2.0*phase) + 0.035*math.sin(3.0*phase)) * bell_env * 0.14
            fade = min(1.0, t / 0.18, (phrase_frames-1-frame) / (RATE*0.18))
            samples.append((pad + bell) * max(0.0, fade))
    gain = 0.62 * 32767 / max(abs(sample) for sample in samples)
    return struct.pack('<' + 'h'*len(samples), *(round(sample*gain) for sample in samples))

def wav_bytes(pcm: bytes) -> bytes:
    output = io.BytesIO()
    with wave.open(output, 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(RATE)
        stream.writeframes(pcm)
    return output.getvalue()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'assets/audio/story_radio.wav')
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(wav_bytes(synthesize_pcm()))
    print(f'Wrote original radio: {FRAMES} frames, {FRAMES/RATE:.0f}s, mono PCM16/{RATE}Hz')

if __name__ == '__main__':
    main()
