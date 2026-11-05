"""같은 고양이의 조명 세 안을 재현한다. 원본 native는 저장하지 않는다.
Blender 4.3.2, CPU 2 threads. 기본 출력은 새 reproduced/ 폴더이다.
--check-only는 프레임을 렌더하지 않고 재개봉·설정·불변 검사를 기록한다.
"""
import bpy,json,hashlib,math,time,argparse,sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text())
ap=argparse.ArgumentParser();ap.add_argument('--check-only',action='store_true');ap.add_argument('--output',type=Path,default=ROOT/'reproduced')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
SOURCE=(ROOT/P['source_native']).resolve();EXPECTED=P['source_sha256']
assert SOURCE.is_file(),'상위 폴더의 원본 native가 필요합니다'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED,'원본 native 해시가 기록과 다릅니다'
bpy.ops.wm.open_mainfile(filepath=str(SOURCE));s=bpy.context.scene;sun=bpy.data.objects['Clear morning sun'];bg=s.world.node_tree.nodes['Background']
s.render.resolution_x,s.render.resolution_y=P['resolution'];s.render.resolution_percentage=100
s.cycles.samples=P['samples'];s.cycles.adaptive_min_samples=P['adaptive_min_samples'];s.cycles.adaptive_threshold=P['adaptive_threshold'];s.cycles.use_denoising=P['denoising']
s.render.threads_mode='FIXED';s.render.threads=P['threads'];s.cycles.device='CPU'
F=P['fixed_render_settings']
assert s.render.engine==F['engine'] and s.cycles.seed==F['cycles_seed']
assert s.view_settings.view_transform==F['view_transform'] and s.view_settings.look==F['look']
assert s.view_settings.exposure==F['exposure'] and s.view_settings.gamma==F['gamma']
assert s.render.image_settings.color_mode==F['color_mode'] and s.render.image_settings.color_depth==F['color_depth']
args.output.mkdir(parents=True,exist_ok=True)
def digest(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def static_signature():
 # Captures evaluated meshes/curves and transforms, material socket values/links,
 # plus the camera. Lighting/world are the intentional comparison variables.
 bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();objects=[]
 for ob in sorted(s.objects,key=lambda x:x.name):
  if ob.type=='LIGHT':continue
  item={'name':ob.name,'type':ob.type,'matrix':[list(r) for r in ob.matrix_world],'hide_render':ob.hide_render}
  if ob.type in ('MESH','CURVE'):
   ev=ob.evaluated_get(dep);me=ev.to_mesh();item['geometry']=digest({'vertices':[list(v.co) for v in me.vertices],'faces':[(list(p.vertices),p.material_index,p.use_smooth) for p in me.polygons]});item['materials']=[m.name if m else None for m in ob.data.materials];ev.to_mesh_clear()
  objects.append(item)
 mats=[]
 for m in sorted(bpy.data.materials,key=lambda x:x.name):
  if not m.use_nodes:continue
  nodes=[]
  for n in sorted(m.node_tree.nodes,key=lambda x:x.name):
   sockets=[]
   for sock in n.inputs:
    if not hasattr(sock,'default_value'):continue
    v=sock.default_value
    try:v=list(v)
    except TypeError:pass
    sockets.append([sock.identifier,v])
   nodes.append([n.name,n.bl_idname,sockets])
  mats.append([m.name,nodes,sorted((x.from_node.name,x.from_socket.identifier,x.to_node.name,x.to_socket.identifier) for x in m.node_tree.links)])
 return digest({'objects':objects,'materials':mats,'camera':{'lens':s.camera.data.lens,'focus':s.camera.data.dof.focus_distance,'fstop':s.camera.data.dof.aperture_fstop}})
baseline=static_signature();assert baseline==P['expected_static_signature'],'정의된 기하·재질·카메라 검사 해시가 다릅니다'
records=[]
for v in P['variants']:
 sun.rotation_euler=(-Vector(v['from_direction'])).to_track_quat('-Z','Y').to_euler();sun.data.energy=v['sun_energy'];sun.data.color=v['sun_color'];sun.data.angle=math.radians(P['sun_angle_degrees'])
 bg.inputs['Color'].default_value=(*v['world_color'],1);bg.inputs['Strength'].default_value=v['world_strength'];bpy.context.view_layer.update()
 assert static_signature()==baseline
 elev=math.degrees(math.atan2(v['from_direction'][2],math.hypot(*v['from_direction'][:2])))
 record={**v,'sun_elevation_degrees':elev if v['sun_energy'] else None,'static_geometry_material_camera_signature_matches':True}
 if not args.check_only:
  out=args.output/(v['name']+'.png');assert not out.exists(),'기존 비교 이미지를 덮어쓰지 않습니다. 새 출력 폴더를 지정하세요'
  s.render.filepath=str(out);started=time.monotonic();bpy.ops.render.render(write_still=True)
  record.update(file=out.name,elapsed_seconds=round(time.monotonic()-started,2))
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
 records.append(record)
report={'scope':P['scope'],'source_reference':P['source_native'],'source_native_sha256':EXPECTED,'source_unchanged':True,'static_geometry_material_camera_signature':baseline,'resolution':P['resolution'],'max_samples':P['samples'],'threads':P['threads'],'denoising':P['denoising'],'check_only':args.check_only,'frames_rendered':0 if args.check_only else len(records),'no_geographic_or_measured_weather_claim':True,'variants':records}
name='reproduction_check.json' if args.check_only else 'study_report.json'
(args.output/name).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print('조명 비교 검사 완료' if args.check_only else '세 가지 조명 렌더 완료')
