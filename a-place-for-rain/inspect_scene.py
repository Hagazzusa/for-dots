"""Reopen the saved scene in a separate background Blender; write only QA JSON."""
import bpy,bmesh,json,math,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
source=ROOT/'A_Place_for_Rain.blend';before=hashlib.sha256(source.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene
assert s.render.filepath=='//renders/a_place_for_rain_final.png'
assert s.render.threads==2 and s.cycles.device=='CPU'
assert s.render.resolution_x==P['render']['final_width'] and s.render.resolution_y==P['render']['final_height']
assert s.cycles.samples==P['render']['final_samples'] and not s.cycles.use_denoising
assert all(abs(a-b)<1e-6 for a,b in zip(s.camera.location,P['camera']['position']))
assert abs(s.camera.data.lens-P['camera']['lens_mm'])<1e-6
assert s['ParametersSha256']==hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()
assert s['BuildSourceSha256']==hashlib.sha256((ROOT/'build.py').read_bytes()).hexdigest()
external=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file]+[lib.filepath for lib in bpy.data.libraries]
assert not external and not s.use_nodes
tray=bpy.data.objects['Empty prepared umbrella drip tray'];bm=bmesh.new();bm.from_mesh(tray.data)
assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=False);assert volume>0;bm.free()
pivot=bpy.data.objects['Door hinge pivot — partly open'];leaf=bpy.data.objects['Plain pale-oak door leaf']
assert leaf.parent==pivot and abs(pivot.rotation_euler.z-math.radians(P['door']['open_angle_degrees']))<1e-6
hinges=[o for o in s.objects if o.name.startswith('Simple hinge')]
assert len(hinges)==3 and all(o.parent==pivot and abs(o.location.x)<1e-8 and abs(o.location.y)<1e-8 for o in hinges)
cups=[o for o in s.objects if o.name.startswith('Far cup') and o.name.endswith('bowl')];assert len(cups)==2
from mathutils import Vector
counter=bpy.data.objects['Modest interior console top']
counter_corners=[counter.matrix_world@Vector(v) for v in counter.bound_box]
limits={a:(min(getattr(v,a) for v in counter_corners),max(getattr(v,a) for v in counter_corners)) for a in ('x','y','z')}
cup_contacts=[]
for ob in cups:
 points=[ob.matrix_world@v.co for v in ob.data.vertices]
 gap=min(v.z for v in points)-limits['z'][1]
 assert abs(gap)<1e-7
 assert all(limits[a][0]<getattr(v,a)<limits[a][1] for v in points for a in ('x','y'))
 bm=bmesh.new();bm.from_mesh(ob.data)
 assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=False)>0;bm.free()
 cup_contacts.append({'name':ob.name,'counter_gap_m':gap,'bowl_footprint_inside_counter':True,'closed_manifold_positive_volume':True})
all_hardware=[o for o in s.objects if o.name.startswith(('Handle ','Plain round brass knob','Simple hinge'))]
assert all(o.parent==pivot for o in all_hardware)
for ob in s.objects:
 if ob.type=='MESH':assert all(math.isfinite(c) for v in ob.data.vertices for c in v.co)
result={'reopened':True,'input_blend_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==before,
        'external_dependencies':external,'relative_render_path':s.render.filepath,'objects':len(s.objects),
        'tray_closed_manifold':True,'tray_volume_m3':volume,'cups':len(cups),
        'cup_contacts':cup_contacts,
        'door_leaf_and_hardware_share_pivot':True,'three_hinge_axes_coincide_with_pivot':True,
        'door_open_angle_degrees':P['door']['open_angle_degrees'],'parameters_hash_matches':True,'build_hash_matches':True,
        'cpu_threads':2,'native_gui_tested':False,
        'final_render_settings':{'width':s.render.resolution_x,'height':s.render.resolution_y,'max_samples':s.cycles.samples,'denoising':s.cycles.use_denoising},
        'camera_position_and_lens_match_parameters':True,
        'limitations':'Background native reopen/geometry checks only. No real architectural, drainage, door-mechanism, electrical or safety validation.'}
assert result['input_blend_unchanged']
(ROOT/'reopen_validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
