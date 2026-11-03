"""One controlled additional draft: cloud center sign only."""
import bpy,json,math,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
original=R/'Cloud_Study.blend';before=sha(original)
bpy.ops.wm.open_mainfile(filepath=str(original));s=bpy.context.scene
nodes=[n for n in s.world.node_tree.nodes if n.type=='MATH' and n.operation=='SUBTRACT'];assert len(nodes)==1
n=nodes[0];old=n.inputs[1].default_value;assert abs(old-.43)<1e-6;n.inputs[1].default_value=-.43
# Evaluate same expression on mirror directions with Normal = -ray_D.
w=bpy.data.objects['지면과 만나는 평평한 수면'];values=[]
for a in range(1,9):
 for j in range(64):
  e=w.data.vertices[1+j*4].co;p=Vector((e.x*a/10,e.y*a/10,-.0015));v=(s.camera.location-p).normalized();d=Vector((-v.x,-v.y,v.z));normal_z=-d.z
  values.append({'elevation':math.degrees(math.asin(d.z)),'old_weight':math.exp(-.5*((normal_z-old)/.055)**2),'new_weight':math.exp(-.5*((normal_z-n.inputs[1].default_value)/.055)**2)})
report={'only_scene_input_changed':'World Gaussian center Normal.z +0.43 -> -0.43','actual_belt_center_elevation_degrees':math.degrees(math.asin(.43)),'sample_count':len(values),'new_weight_range':[min(x['new_weight'] for x in values),max(x['new_weight'] for x in values)],'old_weight_range':[min(x['old_weight'] for x in values),max(x['old_weight'] for x in values)],'pre_render_check':'Normal=-ray_D; peak is now above horizon at elevation asin(.43), no changes to colors, strength, material, camera, seed, exposure or sample settings','original_native_sha256':before,'render':[s.render.resolution_x,s.render.resolution_y,s.cycles.samples,s.cycles.seed]}
assert report['new_weight_range'][1]>.99 and report['old_weight_range'][1]<1e-20
(R/'sign_correction_preflight.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.filepath='//draft_corrected_sign.png';bpy.ops.wm.save_as_mainfile(filepath=str(R/'Cloud_Study_Corrected_Sign.blend'));s.render.filepath=str(R/'draft_corrected_sign.png');bpy.ops.render.render(write_still=True)
assert sha(original)==before
print('SIGN_CORRECTION_COMPLETE')
