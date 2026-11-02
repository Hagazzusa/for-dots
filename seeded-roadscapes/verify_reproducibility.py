"""Independent standard-library parameter/terrain/profile reproducibility checks."""
from pathlib import Path
import json,hashlib,struct,math
from landscape import parameters,natural,SEEDS
p=Path(__file__).resolve().parent;r=json.loads((p/'seed_report.json').read_text());profiles=json.loads((p/'profiles.json').read_text());hashes=[]
for rec in r['records']:
 seed=rec['seed'];params=parameters(seed);assert params==rec['parameters']==profiles[str(seed)]['parameters']
 values=[natural(x,y,params) for y in range(-100,501,30) for x in range(-150,151,30)]
 fingerprint=hashlib.sha256(b''.join(struct.pack('<d',v) for v in values)).hexdigest();assert fingerprint==rec['terrain_fingerprint_sha256'];hashes.append(fingerprint)
 ys=profiles[str(seed)]['y'];hs=profiles[str(seed)]['height'];assert len(ys)==len(hs)==841 and all(math.isfinite(v) for v in hs)
 assert all(ys[i+1]>ys[i] and abs(hs[i+1]-hs[i])/(ys[i+1]-ys[i])<=.060000001 for i in range(840))
assert len(set(hashes))==len(SEEDS)==12
result={'passed':True,'seed_count':12,'distinct_terrain_fingerprints':12,'terrain_samples_rebuilt_per_seed':231,'profile_samples_per_seed':841,'profile_segments_tested_per_seed':840,'maximum_y_grade_tolerance_fraction':.060000001,'profiles_sha256':hashlib.sha256((p/'profiles.json').read_bytes()).hexdigest(),'scope':'Parameter regeneration and sampled terrain fingerprint repeat exactly; all stored virtual profile segments satisfy cap tolerance. Not physical-road certification.'}
(p/'reproducibility.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
