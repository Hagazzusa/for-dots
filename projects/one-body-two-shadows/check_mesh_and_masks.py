"""Read-back topology and two orthographic, unlit silhouette measurements."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(P/'One-Body-Two-Shadows.blend'));s=bpy.context.scene;body=bpy.data.objects['Shared body'];deps=bpy.context.evaluated_depsgraph_get()
evalobj=body.evaluated_get(deps);me=evalobj.to_mesh();bm=bmesh.new();bm.from_mesh(me);bad=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True);assert bad==0 and vol>0
bmesh.ops.triangulate(bm,faces=list(bm.faces));volume=0.;centroid=Vector()
for f in bm.faces:
 a,b,c=[v.co for v in f.verts];v=a.dot(b.cross(c))/6;volume+=v;centroid+=(a+b+c)*(v/4)
centroid/=volume;base=[v.co for v in bm.verts if abs(v.co.z)<1e-6];assert base
bounds=[min(v.x for v in base),max(v.x for v in base),min(v.y for v in base),max(v.y for v in base)]
assert bounds[0]<centroid.x<bounds[1] and bounds[2]<centroid.y<bounds[3],(list(centroid),bounds)
report={'evaluated_nonmanifold_edges':bad,'evaluated_signed_volume':vol,'uniform_volume_centroid':list(centroid),'flat_base_xy_extents':bounds,'centroid_projection_within_base_extents':True,'limits':'Centroid check is a uniform-density rigid-body criterion, not a material or fabrication assessment.'};bm.free();evalobj.to_mesh_clear()
for o in s.objects:o.hide_render=(o!=body)
s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
m=bpy.data.materials.new('QA white emission');m.use_nodes=True;nt=m.node_tree;nt.nodes.clear();em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=(1,1,1,1);em.inputs['Strength'].default_value=1;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(em.outputs[0],out.inputs['Surface']);s.view_layers[0].material_override=m
s.render.resolution_x=s.render.resolution_y=512;s.render.resolution_percentage=100;s.cycles.samples=8;s.cycles.use_adaptive_sampling=False;s.cycles.max_bounces=0;s.view_settings.view_transform='Standard';s.view_settings.look='None';s.view_settings.exposure=0;s.view_settings.gamma=1;s.render.film_transparent=False
report['mask_cameras']={}
for name,loc,axis in [('house',(0,-8,1.4),(1,0,0)),('tree',(-8,0,1.4),(0,1,0))]:
 target=Vector((0,0,1.4));bpy.ops.object.camera_add(location=loc);cam=bpy.context.object;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.2;s.camera=cam;bpy.context.view_layer.update();p=world_to_camera_view(s,cam,target+Vector(axis));polarity=1 if p.x>.5 else -1
 s.render.filepath=str(P/'tmp'/f'{name}-mask.png');bpy.ops.render.render(write_still=True)
 report['mask_cameras'][name]={'extent':3.2,'center_z':1.4,'resolution':512,'horizontal_polarity':polarity,'reference_axis_projected_x':p.x}
(P/'readback-qa.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
