"""다섯 걸음, 일곱 걸음: 5:7 주기 두 성부의 청취 전 소리 연구."""
from pathlib import Path
import math, json, struct, wave
import numpy as np
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'; OUT.mkdir(exist_ok=True)
SR=48000; STEP=.28; CYCLE=35*STEP; DURATION=3*CYCLE+4
A=[[62,65,69,72,69,67,64],[62,65,70,74,72,69,67],[62,64,65,69,67,64,62]]
B=[[50,57,60,55,53],[50,58,62,57,55],[50,57,55,53,50]]
EVENTS=[]
for cycle in range(3):
 for voice,seq,gap in [('A',A[cycle],5),('B',B[cycle],7)]:
  for i,note in enumerate(seq):
   EVENTS.append(dict(voice=voice,cycle=cycle+1,step=cycle*35+i*gap,start=round((cycle*35+i*gap)*STEP,6),midi=note,velocity=round(.76+.12*math.cos(i*1.7),6),duration=1.8 if voice=='A' else 2.8))
# 세 번의 완전한 주기 뒤 같은 시작점에서 끝음을 함께 친다.
for voice,note in [('A',62),('B',50)]:
 EVENTS.append(dict(voice=voice,cycle=4,step=105,start=round(105*STEP,6),midi=note,velocity=.68,duration=3.5))
EVENTS.sort(key=lambda e:(e['start'],e['voice']))
y=np.zeros((round(DURATION*SR),2),dtype=np.float64)
for e in EVENTS:
 t=np.arange(round(e['duration']*SR))/SR; f=440*2**((e['midi']-69)/12)
 if e['voice']=='A':
  ratios=[1,2.76,5.4]; amps=[1,.22,.055]; decays=[.55,.18,.07]; pan=-.48; gain=.24
 else:
  ratios=[1,2,3.01,4.2]; amps=[1,.21,.08,.025]; decays=[1.15,.6,.28,.11]; pan=.48; gain=.22
 tone=sum(a*np.sin(2*np.pi*f*r*t)*np.exp(-t/d) for r,a,d in zip(ratios,amps,decays))
 attack=1-np.exp(-t/.004)
 end=np.minimum(1,(e['duration']-t)/.035).clip(0,1)
 tone*=attack*end*e['velocity']*gain
 left=math.cos((pan+1)*math.pi/4); right=math.sin((pan+1)*math.pi/4)
 pos=round(e['start']*SR); stop=min(len(y),pos+len(tone)); tone=tone[:stop-pos]
 y[pos:stop,0]+=tone*left; y[pos:stop,1]+=tone*right
# 약한 좌우 교차 지연 세 개를 명시적으로 합성한다.
dry=y.copy()
for seconds,gain in [(.137,.11),(.233,.07),(.379,.035)]:
 n=round(seconds*SR); y[n:]+=dry[:-n,::-1]*gain
fade=np.minimum(1,(DURATION-np.arange(len(y))/SR)/.5).clip(0,1); y*=fade[:,None]
scale=.70/np.max(np.abs(y)); y*=scale
pcm=np.round(y*32767).astype('<i2')
with wave.open(str(OUT/'Five-and-Seven.wav'),'wb') as w:
 w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes(pcm.tobytes())
(OUT/'events.json').write_text(json.dumps({'step_seconds':STEP,'cycle_steps':35,'sample_rate':SR,'duration_seconds':DURATION,'events':EVENTS},ensure_ascii=False,indent=2)+'\n')
# MIDI는 음표와 시간의 편집용이며 재생 음색은 WAV의 가산합성과 다르다.
def vlq(n):
 b=[n&127]; n>>=7
 while n: b.insert(0,(n&127)|128);n>>=7
 return bytes(b)
items=[(0,bytes([0xC0,12])),(0,bytes([0xC1,10]))]
for e in EVENTS:
 ch=0 if e['voice']=='A' else 1; start=e['step']*480; dur=360
 items += [(start,bytes([0x90|ch,e['midi'],round(e['velocity']*90)])),(start+dur,bytes([0x80|ch,e['midi'],0]))]
items.sort(key=lambda x:x[0]); track=bytearray(b'\x00\xff\x51\x03'+int(STEP*1e6).to_bytes(3,'big')); last=0
for tick,event in items: track+=vlq(tick-last)+event; last=tick
track+=b'\x00\xff\x2f\x00'
(OUT/'Five-and-Seven.mid').write_bytes(b'MThd'+struct.pack('>IHHH',6,0,1,480)+b'MTrk'+struct.pack('>I',len(track))+track)
# 글꼴이 필요 없는 벡터 리듬 지도. 위가 A, 아래가 B. 각 패널은 35칸이다.
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="750" viewBox="0 0 1400 750">','<rect width="1400" height="750" fill="#f1ebdf"/>']
for c in range(3):
 top=95+c*205
 for i in range(36):
  xx=90+i*34
  svg.append(f'<path d="M{xx} {top-35}v135" stroke="#d9d1c2" stroke-width="{2 if i%5==0 else .7}"/>')
 for v,base,color in [('A',top,'#294d7a'),('B',top+75,'#b35536')]:
  svg.append(f'<path d="M90 {base}h1190" stroke="{color}" stroke-width="1" opacity=".35"/>')
  for e in EVENTS:
   if e['cycle']!=c+1 or e['voice']!=v:continue
   xx=90+(e['step']-c*35)*34; yy=base-(e['midi']-(62 if v=='A' else 50))*2
   svg.append(f'<path d="M{xx} {base}V{yy}" stroke="{color}" stroke-width="2"/>')
   svg.append(f'<circle cx="{xx}" cy="{yy}" r="7" fill="{color}"/>')
svg.append('</svg>'); (OUT/'rhythm-map.svg').write_text('\n'.join(svg)+'\n')
print(json.dumps({'duration':DURATION,'events':len(EVENTS),'peak':float(np.max(np.abs(y))),'rms':float(np.sqrt(np.mean(y*y))),'scale':scale}))
