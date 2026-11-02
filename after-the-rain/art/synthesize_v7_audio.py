#!/usr/bin/env python3
"""Original deterministic noise/resonator synthesis; stdlib only, no sampled media.
Run from any directory. Writes mono 22.05kHz PCM WAVs to ../assets.
Canopy is a quiet, seamless 6-second periodic sequence of tiny fabric taps;
footsteps are short soft soles with wet/roof noise textures, not recorded Foley.
"""
import math, random, struct, wave
from pathlib import Path
SR=22050
OUT=Path(__file__).resolve().parents[1]/'assets'
def save(name, data):
    peak=max(abs(x) for x in data) or 1
    gain=.62/peak
    with wave.open(str(OUT/name),'wb') as f:
        f.setparams((1,2,SR,0,'NONE','not compressed'))
        f.writeframes(b''.join(struct.pack('<h',int(max(-1,min(1,x*gain))*32767)) for x in data))
rng=random.Random(7307)
data=[0.0]*(SR*6)
for _ in range(106):
    start=rng.randrange(len(data)); gain=rng.uniform(.10,.46); freq=rng.uniform(460,1350)
    smooth=0
    for i in range(int(.09*SR)):
        t=i/SR
        smooth=.68*smooth+.32*rng.uniform(-1,1)
        attack=min(1,t/.0015)
        tap=attack*math.exp(-t*75)*(smooth*.8+math.sin(2*math.pi*freq*t)*.25)
        data[(start+i)%len(data)]+=gain*tap
save('umbrella_taps.wav',data)
for wet in (True,False):
    data=[]; smooth=0
    for i in range(int(.23*SR)):
        t=i/SR; smooth=.78*smooth+.22*rng.uniform(-1,1)
        attack=min(1,t/.007)
        sole=math.sin(2*math.pi*(110-80*t)*t)*math.exp(-t*29)
        texture=smooth*math.exp(-t*(15 if wet else 31))
        water=rng.uniform(-1,1)*math.exp(-((t-.05)/.04)**2)*.13 if wet else 0
        data.append(attack*(sole*.4+texture*.6+water))
    save('footsteps_wet.wav' if wet else 'footsteps_roof.wav',data)
