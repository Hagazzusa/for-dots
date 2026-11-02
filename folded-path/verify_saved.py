"""Independent geometry checks against the saved editable Blender scene."""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(root/'folded_path.blend'))
s=bpy.context.scene
panels=[bpy.data.objects['Paper panel %02d'%i] for i in range(6)]
closure=length_error=ink_error=0.;minimum=100.
for sample in range(193):
    f=1+sample/4;s.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update()
    bounds=[]
    for i,p in enumerate(panels):
        vs=[p.matrix_world@v.co for v in p.data.vertices]
        assert all(math.isfinite(c) for v in vs for c in v)
        length_error=max(length_error,abs((vs[160]-vs[0]).length-.8))
        bounds.append((min(v.x for v in vs),max(v.x for v in vs)))
        if i<5:
            q=panels[i+1]
            for k in range(4):
                gap=(vs[160+k]-q.matrix_world@q.data.vertices[k].co).length
                closure=max(closure,gap)
                if k in [1,2]:ink_error=max(ink_error,gap)
    for i in range(6):
        for j in range(i+2,6):minimum=min(minimum,bounds[j][0]-bounds[i][1])
assert closure<1e-5 and ink_error<1e-5 and length_error<1e-5 and minimum>0
r={'source':'saved blend evaluated independently','poses_including_quarter_frames_and_loop_seam':193,'maximum_full_hinge_closure_error':closure,'maximum_ink_endpoint_gap':ink_error,'maximum_panel_width_error':length_error,'minimum_nonadjacent_x_gap':minimum,'finite_vertices':True,'limitations':'Idealized zero thickness only; no physical simulation or fabrication validation.'}
(root/'saved_scene_verification.json').write_text(json.dumps(r,indent=2)+'\n')
print(json.dumps(r,indent=2))
