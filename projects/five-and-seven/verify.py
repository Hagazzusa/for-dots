"""읽기 전용 파일·음표·오디오 구조 검사. 청취 검토를 대체하지 않는다."""
from pathlib import Path
import hashlib,json,math,struct,wave,sys
import numpy as np
ROOT=Path(__file__).resolve().parent
spec=json.loads((ROOT/'output/events.json').read_text()); events=spec['events']
assert len(events)==38
for cycle in (1,2,3):
 for voice,count,gap in [('A',7,5),('B',5,7)]:
  steps=[e['step'] for e in events if e['cycle']==cycle and e['voice']==voice]
  assert len(steps)==count and all(b-a==gap for a,b in zip(steps,steps[1:]))
assert [e['step'] for e in events if e['cycle']==4]==[105,105]
with wave.open(str(ROOT/'output/Five-and-Seven.wav'),'rb') as w:
 assert (w.getnchannels(),w.getsampwidth(),w.getframerate(),w.getnframes())==(2,2,48000,1603200)
 samples=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').reshape(-1,2).astype(float)/32767
assert np.isfinite(samples).all() and np.max(np.abs(samples))<.701
assert not np.count_nonzero(np.abs(samples)>=1)
assert np.max(np.abs(np.mean(samples,axis=0)))<.001
assert np.max(np.abs(samples[[0,-1]]))==0
# 편집용 MIDI를 제작 함수와 독립적으로 읽는다.
data=(ROOT/'output/Five-and-Seven.mid').read_bytes()
assert data[:14]==b'MThd'+struct.pack('>IHHH',6,0,1,480)
assert data[14:18]==b'MTrk' and int.from_bytes(data[18:22],'big')==len(data)-22
p=22; tick=0; ons=[]; active={}; tempo=None
while p<len(data):
 delta=0
 while True:
  c=data[p];p+=1;delta=(delta<<7)|(c&127)
  if c<128:break
 tick+=delta; status=data[p];p+=1
 if status==255:
  kind=data[p];length=data[p+1];p+=2;payload=data[p:p+length];p+=length
  if kind==81:tempo=int.from_bytes(payload,'big')
  if kind==47:break
 elif status&240==192:p+=1
 elif status&240 in (128,144):
  note,vel=data[p:p+2];p+=2;key=(status&15,note)
  if status&240==144 and vel:
   assert key not in active;active[key]=tick;ons.append((tick,key[0],note))
  else:assert key in active;del active[key]
 else:raise AssertionError(status)
assert not active and tempo==280000
expected=[(e['step']*480,0 if e['voice']=='A' else 1,e['midi']) for e in events]
assert sorted(ons)==sorted(expected)
if (ROOT/'manifest.json').exists():
 for name,rec in json.loads((ROOT/'manifest.json').read_text())['files'].items():
  f=ROOT/name;assert f.stat().st_size==rec['bytes'] and hashlib.sha256(f.read_bytes()).hexdigest()==rec['sha256'],name
out={'duration_seconds':len(samples)/48000,'channels':2,'sample_rate':48000,'pcm_bits':16,'peak_dbfs':20*math.log10(float(np.max(np.abs(samples)))),'rms_dbfs':20*math.log10(float(np.sqrt(np.mean(samples*samples)))),'clipped_samples':0,'event_count':len(events),'midi_notes_match':True,'first_last_samples_zero':True,'listened':False}
if '--report' in sys.argv:
 Path(sys.argv[sys.argv.index('--report')+1]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
