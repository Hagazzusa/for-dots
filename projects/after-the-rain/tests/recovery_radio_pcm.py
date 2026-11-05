#!/usr/bin/env python3
"""Objective reproducibility/format/seam checks; does not audition the audio."""
from pathlib import Path
import hashlib
import importlib.util
import io
import math
import struct
import wave

project = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('radio_generator', project/'tools/generate_story_radio.py')
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
first = generator.wav_bytes(generator.synthesize_pcm())
second = generator.wav_bytes(generator.synthesize_pcm())
assert first == second, 'Generator is not byte-deterministic'
assert first == (project/'assets/audio/story_radio.wav').read_bytes(), 'Committed WAV differs from generator'
with wave.open(io.BytesIO(first), 'rb') as audio:
    assert (audio.getnchannels(), audio.getsampwidth(), audio.getframerate(), audio.getnframes()) == (1, 2, 22050, 1058400)
    pcm = audio.readframes(audio.getnframes())
values = struct.unpack('<'+'h'*(len(pcm)//2), pcm)
peak = max(map(abs, values))
assert 16000 <= peak <= 20316, f'Unexpected headroom/peak {peak}'
assert not any(abs(v) >= 32767 for v in values), 'Clipping'
n = 16*22050
phrases = [values[i*n:(i+1)*n] for i in range(3)]
assert len({hashlib.sha256(pcm[i*n*2:(i+1)*n*2]).hexdigest() for i in range(3)}) == 3, 'Phrases repeat identical PCM'
for phrase in phrases:
    rms = math.sqrt(sum(v*v for v in phrase)/len(phrase))/32767
    assert .02 < rms < .3, f'Unexpected phrase RMS {rms}'
    assert phrase[0] == 0 and phrase[-1] == 0, 'Phrase endpoints must join at zero'
for boundary in [0,n,2*n]:
    assert abs(values[boundary] - values[boundary-1]) == 0, 'Discontinuous phrase/loop seam'
    assert max(abs(values[(boundary+i)%len(values)]-values[(boundary+i-1)%len(values)]) for i in range(-16,17)) <= 4, 'Abrupt slope at seam'
print(f'RADIO PCM PASS: deterministic 48s/3 phrases, peak={peak}, seamless endpoints, sha256={hashlib.sha256(first).hexdigest()}')
