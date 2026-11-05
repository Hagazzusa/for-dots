import math, random, struct, wave
from pathlib import Path
rate=22050; length=16; n=rate*length; samples=[0.0]*n
# Original, sparse four-voicing composition; no sampled music or voice.
# Wrapped tails make the 16-second phrase loop continuously.
voicings=[(48,55,62,64),(45,52,59,60),(50,57,60,65),(43,50,57,62)]
for bar, chord in enumerate(voicings):
 for voice, midi in enumerate(chord):
  start=int((bar*4+voice*.42)*rate)
  freq=440*2**((midi-69)/12)
  for i in range(int(5.5*rate)):
   t=i/rate
   env=(1-math.exp(-t/0.018))*math.exp(-t/1.3)
   tone=(math.sin(2*math.pi*freq*t)+.24*math.sin(2*math.pi*freq*2.002*t)+.07*math.sin(2*math.pi*freq*3*t))
   # Soft second detuned oscillator provides a little radio warmth.
   tone+=.12*math.sin(2*math.pi*(freq+.18)*t)
   samples[(start+i)%n]+=.13*env*tone
# Small mono room reflection, deterministic and wrapped.
original=samples[:]
for delay,gain in [(.093,.12),(.173,.08),(.311,.055)]:
 offset=int(delay*rate)
 for i,v in enumerate(original):samples[(i+offset)%n]+=v*gain
peak=max(abs(v) for v in samples)
scale=.64/peak
path=Path('assets/audio/story_radio.wav')
with wave.open(str(path),'wb') as w:
 w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
 w.writeframes(b''.join(struct.pack('<h',round(v*scale*32767)) for v in samples))
print(path,'frames',n,'duration',length,'peak .64; original procedural keys')
