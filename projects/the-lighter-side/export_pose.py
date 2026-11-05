"""Export the eight-second pose as an ordinary OBJ/MTL, without scene dependencies."""
from pathlib import Path
from mobile import state
P=Path(__file__).resolve().parent
meshes,_=state(8.)
obj=['# The Lighter Side - original mobile, pose at 8 seconds','mtllib The-Lighter-Side.mtl'];mtl=[];offset=1
for i,m in enumerate(meshes):
 name=f'part_{i:02d}';obj.extend([f'o {name}',f'usemtl {name}']);obj.extend('v '+' '.join(f'{v:.9f}' for v in p) for p in m['vertices']);obj.extend('f '+' '.join(str(offset+int(v)) for v in f) for f in m['faces']);offset+=len(m['vertices'])
 mtl.extend([f'newmtl {name}','Kd '+' '.join(f'{c:.6f}' for c in m['color']),'Ka 0.2 0.2 0.2','Ks 0 0 0','d 1','illum 1',''])
(P/'The-Lighter-Side.obj').write_text('\n'.join(obj)+'\n');(P/'The-Lighter-Side.mtl').write_text('\n'.join(mtl)+'\n')
print(f'{len(meshes)} mesh parts, {offset-1} vertices')
