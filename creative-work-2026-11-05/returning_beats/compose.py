"""Returning Beats: original deterministic 5:3 miniature. No samples or external assets."""
from pathlib import Path
import json, subprocess
import numpy as np
from scipy.io import wavfile
P=Path(__file__).resolve().parent
SR=48000; DURATION=33
mix=np.zeros((SR*DURATION,2),np.float64); events=[]
def note(start,midi,velocity,pan,voice):
    n=int(SR*4.8); t=np.arange(n)/SR; f=440*2**((midi-69)/12)
    if voice=='glass':
        ratios=[1,2.002,3.01,4.17]; levels=[1,.27,.10,.035]; decays=[1.6,.7,.35,.18]
    else:
        ratios=[1,2,3]; levels=[1,.24,.08]; decays=[1.9,.65,.23]
    s=sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/d) for r,a,d in zip(ratios,levels,decays))
    s*= (1-np.exp(-t/.007))*velocity
    # Linear 250 ms tail prevents truncated tails; equal-power stereo placement.
    s*=np.minimum(1,np.maximum(0,(4.8-t)/.25))
    gains=np.array([np.cos((pan+1)*np.pi/4),np.sin((pan+1)*np.pi/4)])
    at=round(start*SR); end=min(len(mix),at+n); mix[at:end]+=s[:end-at,None]*gains
    events.append({'seconds':round(start,3),'midi':midi,'velocity':velocity,'pan':pan,'voice':voice})
# The opening 3-second cycle is glass alone; the next seven pair five glass notes with three low notes.
# Harmonic route: Dm(add9), Bbmaj9, Fadd9, Cadd9, Gm9, Bbmaj9, A7sus4, Dm(add9).
upper=[[74,69,76,77,81],[74,69,77,81,72],[72,69,77,79,81],[72,67,74,76,79],
       [74,70,77,81,79],[74,69,77,81,72],[74,69,76,79,81],[74,69,76,77,81]]
lower=[[50,57,64],[46,53,57],[41,48,55],[48,55,62],[43,50,57],[46,53,57],[45,52,62],[50,57,65]]
for c in range(8):
    start=.6+c*3
    for j,m in enumerate(upper[c]):
        note(start+j*.6,m,(.19 if j==0 else .14)*(1-.025*c),-.48,'glass')
    if c>0:
        for j,m in enumerate(lower[c]):note(start+j,m,.18 if j==0 else .12,.42,'wood')
# A broken closing figure leaves space; the two voices meet on D at 27.6 s.
for at,m in [(24.6,77),(25.8,76),(27.6,74)]:note(at,m,.135,-.35,'glass')
note(24.6,57,.12,.38,'wood'); note(27.6,50,.18,.25,'wood')
# Short, quiet stereo room reflections. Feed only dry signal, not recursive echoes.
dry=mix.copy()
for delay,gain in [(.071,.10),(.113,.075),(.179,.055),(.263,.035),(.389,.02)]:
    off=round(delay*SR); mix[off:]+=dry[:-off,::-1]*gain
mix[:int(SR*.02)]*=np.linspace(0,1,int(SR*.02))[:,None]
mix[-SR:]*=np.linspace(1,0,SR)[:,None]
peak=np.max(np.abs(mix)); mix*=10**(-2/20)/peak
wavfile.write(P/'Returning-Beats.wav',SR,(mix*32767).round().astype(np.int16))
(P/'score.json').write_text(json.dumps({'title':'다시 만나는 박자','duration':DURATION,'cycle_seconds':3,'polyrhythm':'5:3','events':events},ensure_ascii=False,indent=2)+'\n')
subprocess.run(['ffmpeg','-v','error','-y','-threads','2','-i',str(P/'Returning-Beats.wav'),'-map_metadata','-1','-c:a','libmp3lame','-b:a','192k',str(P/'Returning-Beats.mp3')],check=True)
print(f'Wrote {len(events)} notes, {DURATION}s, 48kHz stereo.')
