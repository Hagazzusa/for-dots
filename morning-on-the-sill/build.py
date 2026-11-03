"""Original image-first ceramic-cat/leaf study. Run in a new Blender 4.3.2 process.
No original project is opened. All geometry and textures are authored here.
"""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent;P=json.loads((ROOT/'parameters.json').read_text());DRAFT='--draft' in sys.argv
OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.scale_length=1
s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=2
s.cycles.samples=P['render']['draft_samples' if DRAFT else 'final_samples'];s.cycles.use_denoising=False
s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.02 if DRAFT else .012;s.cycles.adaptive_min_samples=0 if DRAFT else 32
s.cycles.max_bounces=8;s.cycles.diffuse_bounces=4;s.cycles.glossy_bounces=4;s.cycles.seed=47
s.render.resolution_x=P['render']['draft_width' if DRAFT else 'final_width'];s.render.resolution_y=P['render']['draft_height' if DRAFT else 'final_height'];s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.render.image_settings.color_depth='8';s.render.use_stamp=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=0;s.view_settings.gamma=1
s.world.use_nodes=True;bg=s.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(*P['world']['color'],1);bg.inputs['Strength'].default_value=P['world']['strength']
main=bpy.context.collection
sources=bpy.data.collections.new('Editable cat construction sources — hidden');s.collection.children.link(sources)

def material(name,color,rough=.6):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 n=m.node_tree.nodes['Principled BSDF'];n.inputs['Base Color'].default_value=(*color,1);n.inputs['Roughness'].default_value=rough
 return m

def textured(name,c0,c1,scale,rough,bump=0,stretch=None):
 m=material(name,c0,rough);n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF']
 g=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
 if stretch:
  v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=stretch;l.new(g.outputs['Position'],v.inputs[0]);l.new(v.outputs[0],noise.inputs['Vector'])
 else:l.new(g.outputs['Position'],noise.inputs['Vector'])
 ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[0].color=(*c0,1);ramp.color_ramp.elements[1].position=.85;ramp.color_ramp.elements[1].color=(*c1,1)
 l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
 if bump:
  b=n.new('ShaderNodeBump');b.inputs['Distance'].default_value=bump;b.inputs['Strength'].default_value=.22;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 return m

clay=textured('Blue-grey matte stoneware',(.245,.325,.350),(.325,.405,.425),1500,.64,.00012)
# Small fired-clay speckles, authored procedurally rather than an image texture.
n=clay.node_tree.nodes;l=clay.node_tree.links;p=n['Principled BSDF'];base_link=p.inputs['Base Color'].links[0];base=base_link.from_socket;l.remove(base_link)
g=n.new('ShaderNodeNewGeometry');v=n.new('ShaderNodeTexVoronoi');v.inputs['Scale'].default_value=2200;l.new(g.outputs['Position'],v.inputs['Vector'])
r=n.new('ShaderNodeMath');r.operation='LESS_THAN';r.inputs[1].default_value=.085;l.new(v.outputs['Distance'],r.inputs[0])
mix=n.new('ShaderNodeMixRGB');l.new(r.outputs[0],mix.inputs[0]);l.new(base,mix.inputs[1]);mix.inputs[2].default_value=(.19,.145,.09,1);l.new(mix.outputs[0],p.inputs['Base Color'])
face_mat=material('Quiet clay face marks',(.12,.17,.18),.72)
paint=textured('Pale worn painted wood',(.52,.54,.49),(.72,.73,.67),5,.66,.00016,(1,85,55))
framepaint=textured('Off-white open window frame',(.58,.57,.50),(.77,.75,.66),7,.64,.00012,(3,30,3))
backdrop=textured('Defocused sage exterior — procedural backdrop',(.19,.27,.17),(.47,.55,.35),4,.85,0)
yellow=textured('Drying ochre ginkgo',(.30,.18,.025),(.58,.40,.075),90,.62,.000035)
green=textured('Drying olive ginkgo',(.12,.17,.035),(.29,.34,.09),100,.66,.000035)
vein_y=material('Subtle ochre veins',(.28,.18,.035),.72);vein_g=material('Subtle olive veins',(.12,.17,.04),.74)
for m in (yellow,green):
 n=m.node_tree.nodes;l=m.node_tree.links;p=n['Principled BSDF'];out=n['Material Output'];tr=n.new('ShaderNodeBsdfTranslucent');tr.inputs['Color'].default_value=m.diffuse_color
 ms=n.new('ShaderNodeMixShader');ms.inputs[0].default_value=.10;l.new(p.outputs[0],ms.inputs[1]);l.new(tr.outputs[0],ms.inputs[2]);l.new(ms.outputs[0],out.inputs['Surface'])

def mesh(name,verts,faces,mat,smooth=False,collection=None):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(name,me);(collection or main).objects.link(ob);me.materials.append(mat)
 for f in me.polygons:f.use_smooth=smooth
 return ob

def cube(name,loc,size,mat,bevel=0,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(mat)
 if bevel:b=ob.modifiers.new('Soft worn edges','BEVEL');b.width=bevel;b.segments=3;ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if parent:ob.parent=parent
 return ob

def curve(name,points,radius,mat):
 cu=bpy.data.curves.new(name+'_curve','CURVE');cu.dimensions='3D';cu.resolution_u=12;cu.bevel_depth=radius;cu.bevel_resolution=3;cu.use_fill_caps=True
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for bp,co in zip(sp.bezier_points,points):bp.co=co;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);main.objects.link(ob);cu.materials.append(mat);return ob

cat_origin=Vector(P['cat_center']);parts=[]
def cat_part(name,loc,scale,pear=False):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=32,location=cat_origin+Vector(loc));o=bpy.context.object;o.name=name
 for v in o.data.vertices:
  if pear:
   factor=1-.20*(v.co.z+1)/2;v.co.x*=factor;v.co.y*=factor
 o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(clay)
 for c in list(o.users_collection):c.objects.unlink(o)
 sources.objects.link(o);parts.append(o);return o
# One continuous pear-to-neck profile avoids a stack of separate round forms.
profile=[(0,.026,.020),(.006,.034,.027),(.026,.041,.032),(.049,.038,.030),(.069,.031,.026),(.086,.025,.022),(.103,.024,.022),(.119,.020,.019),(.129,.006,.005)]
def catmull(a,b,c,d,t):return .5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)
body_rings=[]
for i in range(len(profile)-1):
 for j in range(6):
  t=j/6;z=profile[i][0]*(1-t)+profile[i+1][0]*t
  rx=catmull(profile[max(0,i-1)][1],profile[i][1],profile[i+1][1],profile[min(len(profile)-1,i+2)][1],t)
  ry=catmull(profile[max(0,i-1)][2],profile[i][2],profile[i+1][2],profile[min(len(profile)-1,i+2)][2],t)
  body_rings.append((z,rx,ry))
body_rings.append(profile[-1]);vs=[];fs=[];ns=64
for z,rx,ry in body_rings:
 for j in range(ns):
  a=2*math.pi*j/ns;vs.append(tuple(cat_origin+Vector((rx*math.cos(a),.005-.007*z/.129+ry*math.sin(a),z))))
for i in range(len(body_rings)-1):
 for j in range(ns):k=(j+1)%ns;fs.append((i*ns+j,i*ns+k,(i+1)*ns+k,(i+1)*ns+j))
fs.extend([tuple(range(ns-1,-1,-1)),tuple(range((len(body_rings)-1)*ns,len(body_rings)*ns))])
parts.append(mesh('Source continuous torso and neck',vs,fs,clay,True,sources))
cat_part('Source head',(0,-.006,.113),(.029,.025,.025))
cat_part('Source restrained muzzle',(0,-.029,.106),(.012,.006,.008))
cat_part('Source left forepaw',(-.014,-.021,.023),(.010,.014,.023))
cat_part('Source right forepaw',(.011,-.023,.023),(.010,.014,.023))
for side in (-1,1):
 x=side*.019;tipx=side*.025;ztip=.148 if side<0 else .147
 verts=[(x-.009,y,.126) for y in (-.016,.004)]+[(x+.009,y,.126) for y in (-.016,.004)]+[(tipx,y,ztip) for y in (-.008,.001)]
 verts=[tuple(cat_origin+Vector(v)) for v in verts]
 o=mesh('Source rounded ear '+str(side),verts,[(0,2,4),(1,5,3),(0,1,3,2),(2,3,5,4),(4,5,1,0)],clay,collection=sources)
 b=o.modifiers.new('Soft ear tips','BEVEL');b.width=.0032;b.segments=3;parts.append(o)
# Mesh tube tail with taper, attached behind the haunch and resting beside the paws.
tail_points=[(.030,.018,.027),(.039,.012,.022),(.043,.000,.016),(.043,-.018,.010),(.034,-.033,.009),(.018,-.039,.009),(.002,-.038,.010),(-.006,-.035,.011)]
verts=[];faces=[];rings=16
for i,p0 in enumerate(tail_points):
 p0=Vector(p0);tangent=Vector(tail_points[min(i+1,len(tail_points)-1)])-Vector(tail_points[max(0,i-1)]);tangent.normalize();u=tangent.cross(Vector((0,0,1))).normalized();v=tangent.cross(u).normalized();r=.009*(1-.30*i/(len(tail_points)-1))
 for j in range(rings):a=2*math.pi*j/rings;verts.append(tuple(cat_origin+p0+r*(math.cos(a)*u+math.sin(a)*v)))
for i in range(len(tail_points)-1):
 for j in range(rings):k=(j+1)%rings;faces.append((i*rings+j,i*rings+k,(i+1)*rings+k,(i+1)*rings+j))
faces.extend([tuple(range(rings-1,-1,-1)),tuple(range((len(tail_points)-1)*rings,len(tail_points)*rings))])
parts.append(mesh('Source curled attached tail',verts,faces,clay,True,sources))
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();copies=[]
for ob in parts:
 me=bpy.data.meshes.new_from_object(ob.evaluated_get(deps));du=bpy.data.objects.new('Fuse '+ob.name,me);main.objects.link(du);du.matrix_world=ob.matrix_world.copy();copies.append(du)
bpy.ops.object.select_all(action='DESELECT')
for ob in copies:ob.select_set(True)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();cat=bpy.context.object;cat.name='Cat — unified hand-shaped stoneware'
bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
re=cat.modifiers.new('Fuse original sculptural parts','REMESH');re.mode='VOXEL';re.voxel_size=P['cat_voxel_size'];re.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=re.name)
sm=cat.modifiers.new('Gentle sculpt smoothing','SMOOTH');sm.factor=.40;sm.iterations=8;bpy.ops.object.modifier_apply(modifier=sm.name)
zshift=-min(v.co.z for v in cat.data.vertices)
for v in cat.data.vertices:v.co.z+=zshift
for f in cat.data.polygons:f.use_smooth=True
sources.hide_render=True;sources.hide_viewport=True
# Project understated eye/nose marks onto the actual fused face.
bpy.context.view_layer.update()
def face_point(x,z):
 hit,loc,norm,index=cat.ray_cast(Vector((cat_origin.x+x,cat_origin.y-.12,z+zshift)),Vector((0,1,0)))
 assert hit,'Face projection missed';return tuple(loc+norm*.00018)
for side in (-1,1):
 pts=[face_point(side*.011+dx,.119+(.0007 if dx==0 else 0)) for dx in (-.004,0,.004)]
 curve('Quiet closed eye '+str(side),pts,.00033,face_mat)
mesh('Small quiet nose',[face_point(-.0018,.110),face_point(.0018,.110),face_point(0,.1078)],[(0,1,2)],face_mat)

# One painted ledge and only enough open frame to establish a window.
cube('Pale painted window ledge',(0,0,-.018),(.85,.36,.036),paint,.0025)
cube('Back ledge lip',(0,.165,.008),(.85,.022,.016),framepaint,.002)
cube('Partial fixed jamb',(-.31,.16,.22),(.038,.04,.44),framepaint,.002)
hinge=bpy.data.objects.new('Open sash pivot — static prop',None);main.objects.link(hinge);hinge.location=(-.29,.15,.025);hinge.rotation_euler.z=math.radians(-25)
cube('Open sash lower rail',(.12,0,.016),(.27,.025,.032),framepaint,.002,hinge)
cube('Open sash far upright',(.245,0,.205),(.026,.025,.41),framepaint,.002,hinge)
cube('Open sash hinge upright',(0,0,.205),(.026,.025,.41),framepaint,.002,hinge)
cube('Open sash upper rail',(.12,0,.395),(.27,.025,.032),framepaint,.002,hinge)
cube('Soft sage background',(0,.9,.35),(2.2,.02,1.4),backdrop,0)

leaf_records=[]
def leaf(name,base,rotation,R,mat,veinmat):
 angle=math.radians(rotation);c=math.cos(angle);sn=math.sin(angle)
 def point(u,theta,raise_z=0):
  edge=R*(1-.11*math.exp(-(theta/.18)**2)+.018*math.sin(theta*13));r=u*edge
  x=r*math.sin(theta);y=r*math.cos(theta);z=.0010+.0060*u*u+.0020*u**3*math.sin(theta*1.5)**2+.0006*u*u*math.sin(theta*5)**2
  return (base[0]+c*x-sn*y,base[1]+sn*x+c*y,z+raise_z)
 nr=14;nt=40;vs=[point(i/nr,-1.40+2.80*j/nt) for i in range(nr+1) for j in range(nt+1)];fs=[]
 for i in range(nr):
  for j in range(nt):k=i*(nt+1)+j;fs.append((k,k+1,k+nt+2,k+nt+1))
 ob=mesh(name+' fan',vs,fs,mat,True);bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=1e-7);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
 sol=ob.modifiers.new('Thin leaf lamina','SOLIDIFY');sol.thickness=.00025;sol.offset=-1
 for j in range(11):
  theta=-1.33+2.66*j/10;curve(name+' vein %02d'%j,[point(u,theta,.00012) for u in (.04,.2,.4,.6,.8,.98)],.00009,veinmat)
 stem=[(base[0]-sn*y,base[1]+c*y,z) for y,z in [(0,.0010),(-.010,.0010),(-.021,.0006)]]
 stem_ob=curve(name+' fine resting stem',stem,.0006,veinmat)
 leaf_records.append({'name':name,'base':base,'radius_m':R,'stem_object':stem_ob.name,'lamina_thickness_m':sol.thickness});return ob
leaves=[leaf('Ochre ginkgo',(-.095,-.070),70,.045,yellow,vein_y),leaf('Olive ginkgo',(-.055,-.028),-20,.038,green,vein_g)]

# Simple direct daylight: no deep room, hidden emission, bloom or image plate.
d=bpy.data.lights.new('Clear morning sun','SUN');d.energy=P['sun']['energy'];d.color=P['sun']['color'];d.angle=math.radians(P['sun']['angle_degrees']);o=bpy.data.objects.new('Clear morning sun',d);main.objects.link(o);o.rotation_euler=(-Vector(P['sun']['from_direction'])).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=P['camera']['position']);cam=bpy.context.object;cam.name='Camera — morning after rain';cam.rotation_euler=(Vector(P['camera']['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=P['camera']['lens_mm'];cam.data.clip_start=.01;cam.data.clip_end=100;cam.data.dof.use_dof=True;cam.data.dof.focus_distance=(cam.location-Vector((.075,.0,.085))).length;cam.data.dof.aperture_fstop=P['camera']['f_stop'];s.camera=cam
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
bm=bmesh.new();bm.from_mesh(cat.data);assert all(e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=False);assert volume>0
remaining=set(bm.verts);components=0
while remaining:
 components+=1;todo=[remaining.pop()]
 while todo:
  v=todo.pop()
  for e in v.link_edges:
   w=e.other_vert(v)
   if w in remaining:remaining.remove(w);todo.append(w)
bm.free();assert components==1,components
finite=[]
for ob in s.objects:
 if ob.type not in ('MESH','CURVE'):continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();assert all(math.isfinite(x) for v in me.vertices for x in v.co),ob.name;finite.append(ob.name);ev.to_mesh_clear()
for ob in leaves:
 ev=ob.evaluated_get(deps);me=ev.to_mesh();bm=bmesh.new();bm.from_mesh(me);assert all(e.is_manifold for e in bm.edges),ob.name;bm.free()
 record=next(x for x in leaf_records if ob.name==x['name']+' fan');record['lamina_min_height_m']=min((ob.matrix_world@v.co).z for v in me.vertices);assert record['lamina_min_height_m']>=-1e-6
 leaf_proj=[world_to_camera_view(s,cam,ob.matrix_world@v.co) for v in me.vertices];record['fan_camera_bounds']={'left':min(v.x for v in leaf_proj),'right':max(v.x for v in leaf_proj),'bottom':min(v.y for v in leaf_proj),'top':max(v.y for v in leaf_proj)};assert all(.02<getattr(v,a)<.98 for v in leaf_proj for a in ('x','y')),('Leaf clipped',ob.name,record['fan_camera_bounds'])
 record['fan_inside_frame']=True;ev.to_mesh_clear()
 stem=bpy.data.objects[record['stem_object']];ev=stem.evaluated_get(deps);me=ev.to_mesh();record['stem_floor_contact_gap_m']=min((stem.matrix_world@v.co).z for v in me.vertices);assert abs(record['stem_floor_contact_gap_m'])<.0001;ev.to_mesh_clear()
proj=[world_to_camera_view(s,cam,cat.matrix_world@v.co) for v in cat.data.vertices]
bounds={a:fn(getattr(p,k) for p in proj) for a,k,fn in [('left','x',min),('right','x',max),('bottom','y',min),('top','y',max)]}
assert all(.025<v<.975 for v in bounds.values()),('Cat clipped',bounds)
emissive=[m.name for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='EMISSION' or (n.type=='BSDF_PRINCIPLED' and sum(n.inputs['Emission Color'].default_value[:3])>0 and n.inputs['Emission Strength'].default_value>0)]
assert not emissive and not s.use_nodes;external=[im.filepath for im in bpy.data.images if im.source=='FILE'];assert not external
report={'scope':'Original virtual art geometry, not ceramic production, botanical, architectural or safety validation','cat_closed_manifold':True,'cat_connected_components':components,'cat_volume_m3':volume,'cat_floor_contact_gap_m':min(v.co.z for v in cat.data.vertices),'cat_construction_sources_preserved':len(parts),'cat_camera_bounds':bounds,'leaves':leaf_records,'evaluated_finite_geometry_objects':len(finite),'external_images':external,'emissive_materials':emissive,'compositor_enabled':s.use_nodes,'source_parameters_sha256':hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest(),'build_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'render':{'width':s.render.resolution_x,'height':s.render.resolution_y,'max_samples':s.cycles.samples,'threads':2,'device':'CPU','denoising':False}}
(ROOT/'geometry_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for screen in bpy.data.screens:
 for area in screen.areas:
  for sp in area.spaces:
   if sp.type=='FILE_BROWSER' and sp.params:sp.params.directory=b'/'*1023;sp.params.directory=b'//'
   if sp.type=='VIEW_3D':sp.region_3d.view_perspective='CAMERA';sp.shading.color_type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT');s['Title']=P['title'];s['Scope']='Original fictional windowsill, not a real home or commercial product.';s['ParametersSha256']=report['source_parameters_sha256'];s['BuildSourceSha256']=report['build_source_sha256']
filename='draft_03.png' if DRAFT else 'morning_on_the_sill_final.png';s.render.filepath='//renders/'+filename
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Morning_on_the_Sill.blend'))
if '--no-render' not in sys.argv:s.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True);print('MORNING_RENDER_COMPLETE',filename)
