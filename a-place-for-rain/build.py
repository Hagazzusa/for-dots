"""Original miniature entryway. Image-first concept, independently built geometry.
Blender 4.3.2: blender -b -t 2 --python-exit-code 1 --python build.py -- --draft
No source scene is opened, appended or overwritten; no external texture is used.
"""
import bpy,bmesh,math,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parent
P=json.loads((ROOT/'parameters.json').read_text());DRAFT='--draft' in sys.argv
OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.unit_settings.scale_length=1
S.render.engine='CYCLES';S.cycles.device='CPU';S.render.threads_mode='FIXED';S.render.threads=2
S.cycles.samples=P['render']['draft_samples' if DRAFT else 'final_samples'];S.cycles.use_denoising=False
S.cycles.use_adaptive_sampling=True;S.cycles.adaptive_threshold=.02 if DRAFT else .012
S.cycles.adaptive_min_samples=0 if DRAFT else 32;S.cycles.max_bounces=8;S.cycles.diffuse_bounces=4
S.cycles.glossy_bounces=4;S.cycles.transmission_bounces=4;S.cycles.seed=37
S.render.resolution_x=P['render']['draft_width' if DRAFT else 'final_width']
S.render.resolution_y=P['render']['draft_height' if DRAFT else 'final_height'];S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.image_settings.color_depth='8'
S.render.film_transparent=False;S.render.use_stamp=False
S.view_settings.view_transform='AgX';S.view_settings.look='AgX - Medium High Contrast';S.view_settings.exposure=0;S.view_settings.gamma=1
S.world.use_nodes=True;bg=S.world.node_tree.nodes['Background'];bg.inputs['Color'].default_value=(.29,.38,.53,1);bg.inputs['Strength'].default_value=.055

def mat(name,color,roughness=.5,metallic=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;m.diffuse_color=(*color,1)
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=roughness;p.inputs['Metallic'].default_value=metallic
 return m

def noise_mat(name,c0,c1,scale,roughness,bump_dist=0,bump_strength=.15,stretch=None):
 m=mat(name,c0,roughness);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF')
 g=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.66
 if stretch:
  v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=stretch;l.new(g.outputs['Position'],v.inputs[0]);l.new(v.outputs[0],noise.inputs['Vector'])
 else:l.new(g.outputs['Position'],noise.inputs['Vector'])
 r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(*c0,1);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(*c1,1)
 l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs['Color'],p.inputs['Base Color'])
 if bump_dist:
  b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump_strength;b.inputs['Distance'].default_value=bump_dist;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 return m

plaster=noise_mat('Warm cared-for plaster',(.31,.285,.245),(.42,.385,.33),65,.86,.0015,.20)
paint=mat('Soft off-white jamb paint',(.67,.65,.59),.58)
slate=noise_mat('Cool grey slate — damp sheen, not puddles',(.053,.064,.078),(.115,.125,.135),13,.42,.0011,.22)
n=slate.node_tree.nodes;l=slate.node_tree.links;g=n.new('ShaderNodeNewGeometry');wet=n.new('ShaderNodeTexNoise');wet.inputs['Scale'].default_value=1.7;wet.inputs['Detail'].default_value=2;l.new(g.outputs['Position'],wet.inputs['Vector'])
rr=n.new('ShaderNodeMapRange');rr.inputs['From Min'].default_value=.25;rr.inputs['From Max'].default_value=.75;rr.inputs['To Min'].default_value=.30;rr.inputs['To Max'].default_value=.56;l.new(wet.outputs['Fac'],rr.inputs['Value']);l.new(rr.outputs['Result'],n.get('Principled BSDF').inputs['Roughness'])
grout=mat('Quiet dark grout',(.047,.052,.058),.9)
doorwood=noise_mat('Pale cared-for oak door',(.26,.155,.072),(.49,.325,.165),5,.47,.00035,.12,(9,9,.32))
woodfloor=noise_mat('Warm interior wood floor',(.13,.065,.027),(.29,.16,.065),4,.46,.0003,.12,(.45,8,5))
consolewood=noise_mat('Simple warm console',(.11,.052,.020),(.25,.135,.052),5,.47,.00025,.10,(1,10,4))
traymat=noise_mat('Charcoal empty drip tray',(.035,.040,.044),(.063,.068,.073),32,.45,.0004,.16)
brass=mat('Quiet aged brass',(.33,.235,.105),.35,.76)
ceramic=mat('Ivory cup glaze',(.66,.60,.47),.27)
tea=mat('One quiet cup of tea',(.085,.027,.006),.18)

def mesh_obj(name,verts,faces,material,smooth=False):
 me=bpy.data.meshes.new(name+'_mesh');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(material)
 for f in me.polygons:f.use_smooth=smooth
 return ob

def cube(name,loc,size,material,bevel=0,parent=None):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);ob=bpy.context.object;ob.name=name;ob.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);ob.data.materials.append(material)
 if bevel:
  b=ob.modifiers.new('Gentle edge wear','BEVEL');b.width=bevel;b.segments=3
  ob.modifiers.new('Stable weighted normals','WEIGHTED_NORMAL')
 if parent:ob.parent=parent
 return ob

def tube(name,points,radius,material,parent=None):
 cu=bpy.data.curves.new(name+'_curve','CURVE');cu.dimensions='3D';cu.resolution_u=16;cu.bevel_depth=radius;cu.bevel_resolution=4;cu.use_fill_caps=True
 sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
 for bp,p in zip(sp.bezier_points,points):bp.co=p;bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(material)
 if parent:ob.parent=parent
 return ob

def cylinder(name,loc,radius,depth,material,rotation=(0,0,0),parent=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc,rotation=rotation);ob=bpy.context.object;ob.name=name;ob.data.materials.append(material)
 b=ob.modifiers.new('Soft cylinder edges','BEVEL');b.width=min(.002,depth*.15);b.segments=3;ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 if parent:ob.parent=parent
 return ob

# Limited architecture: one visible threshold, not a complete home.
cube('Entry grout bed',(-.2,-1.8,-.035),(5.0,4.0,.055),grout)
tile_w=.43;tile_d=.36
for ix in range(12):
 for iy in range(11):
  x=-2.6+(ix+.5)*tile_w;y=-3.96+(iy+.5)*tile_d
  cube('Slate tile %02d %02d'%(ix,iy),(x,y,-.012),(tile_w-.004,tile_d-.004,.024),slate,.0015)
cube('Interior floor backing',(.55,1.25,-.035),(2.8,2.5,.055),consolewood)
for ix in range(8):
 for iy in range(4):
  cube('Interior plank %d %d'%(ix,iy),(-.8+(ix+.5)*.34,(iy+.5)*.61,-.012),(.338,.607,.024),woodfloor,.0008)
cube('Left entry wall',(-1.20,.055,1.25),(2.50,.16,2.50),plaster,.004)
cube('Right entry wall',(1.76,.055,1.25),(1.12,.16,2.50),plaster,.004)
cube('Wall above opening',(.625,.055,2.31),(1.15,.16,.38),plaster,.004)
cube('Slate skirting left',(-1.20,-.041,.068),(2.50,.032,.136),slate,.002)
cube('Slate skirting right',(1.76,-.041,.068),(1.12,.032,.136),slate,.002)
cube('Left door jamb',(.04,-.012,1.06),(.09,.205,2.12),paint,.004)
cube('Right door jamb',(1.22,-.012,1.06),(.09,.205,2.12),paint,.004)
cube('Door header',(.63,-.012,2.13),(1.27,.205,.10),paint,.004)
cube('Simple brass threshold',(.63,.012,.006),(1.10,.065,.012),brass,.002)
cube('Interior back wall',(.55,2.18,1.25),(2.8,.14,2.5),plaster,.004)
cube('Interior left return',(-.82,1.12,1.25),(.12,2.12,2.5),plaster,.004)
cube('Interior right return',(1.92,1.12,1.25),(.12,2.12,2.5),plaster,.004)
cube('Small interior ceiling',(.55,1.12,2.49),(2.8,2.12,.10),paint,.002)

# Door remains a separable, editable hinged group.
d=P['door'];pivot=bpy.data.objects.new('Door hinge pivot — partly open',None);bpy.context.collection.objects.link(pivot)
pivot.location=d['hinge'];pivot.rotation_euler.z=math.radians(d['open_angle_degrees'])
leaf=cube('Plain pale-oak door leaf',(-d['width']/2,0,d['height']/2),(d['width'],d['thickness'],d['height']),doorwood,.004,pivot)
cube('Door lower rail',(-d['width']/2,-.024,.20),(d['width']-.07,.015,.115),doorwood,.003,pivot)
cube('Door subtle inset panel',(-d['width']/2,-.024,1.11),(d['width']-.15,.009,1.54),doorwood,.005,pivot)
for z in (.28,1.05,1.79):cylinder('Simple hinge %.2f'%z,(0,0,z),.013,.085,brass,parent=pivot)
cylinder('Handle rose',(-d['width']+.12,-.033,1.13),.037,.012,brass,(math.pi/2,0,0),pivot)
cylinder('Handle short stem',(-d['width']+.12,-.064,1.13),.014,.056,brass,(math.pi/2,0,0),pivot)
cylinder('Plain round brass knob',(-d['width']+.12,-.098,1.13),.027,.024,brass,(math.pi/2,0,0),pivot)

# One empty hook, not a departed person's possessions.
cylinder('Empty hook backplate',(-.80,-.047,1.20),.043,.010,brass,(math.pi/2,0,0))
tube('Empty brass wall hook',[(-.80,-.060,1.20),(-.80,-.092,1.16),(-.80,-.145,1.13),(-.80,-.180,1.16),(-.80,-.180,1.195)],.009,brass)
bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=.012,location=(-.80,-.180,1.195));bpy.context.object.name='Hook rounded tip';bpy.context.object.data.materials.append(brass)

def rounded_rect(width,depth,r,n=10):
 pts=[]
 for cx,cy,start in [(width/2-r,depth/2-r,0),(-width/2+r,depth/2-r,90),(-width/2+r,-depth/2+r,180),(width/2-r,-depth/2+r,270)]:
  for i in range(n):
   a=math.radians(start+i*90/n);pts.append((cx+r*math.cos(a),cy+r*math.sin(a)))
 return pts

t=P['tray'];outer=rounded_rect(t['width'],t['depth'],t['corner_radius']);inner=rounded_rect(t['width']-2*t['wall'],t['depth']-2*t['wall'],t['corner_radius']-t['wall']);N=len(outer)
verts=[]
for ring,z in [(outer,0),(outer,t['height']),(inner,t['height']),(inner,t['floor_thickness'])]:
 verts.extend([(x+t['center'][0],y+t['center'][1],z) for x,y in ring])
faces=[]
for layer in range(3):
 for i in range(N):j=(i+1)%N;faces.append([layer*N+i,layer*N+j,(layer+1)*N+j,(layer+1)*N+i])
faces.append(list(range(N))[::-1]);faces.append(list(range(3*N,4*N)))
tray=mesh_obj('Empty prepared umbrella drip tray',verts,faces,traymat)
bm=bmesh.new();bm.from_mesh(tray.data);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(tray.data);bm.free()
be=tray.modifiers.new('Rounded tray rim','BEVEL');be.width=.002;be.segments=3;tray.modifiers.new('Tray weighted normals','WEIGHTED_NORMAL')
for i in range(12):cube('Empty tray raised rib %02d'%i,(t['center'][0]-.286+i*.052,t['center'][1],.018),(.009,.220,.006),traymat,.002)

# A small, secondary two-cup hint beyond the threshold, before arrival.
top=.825
cube('Modest interior console top',(.76,1.53,top-.019),(.98,.40,.038),consolewood,.008)
cube('Modest console front apron',(.76,1.365,.69),(.88,.035,.23),consolewood,.003)
for x in (.34,1.18):
 for y in (1.40,1.66):cube('Console leg %.2f %.2f'%(x,y),(x,y,.40),(.045,.045,.80),consolewood,.003)

def cup(name,center,with_tea=False):
 # Closed lathed ceramic cross-section: underside -> outer wall -> rim -> inner bowl.
 profile=[(0,.0),(.026,.0),(.029,.003),(.030,.012),(.037,.030),(.044,.066),(.044,.083),(.042,.087),(.039,.086),(.039,.078),(.037,.058),(.030,.024),(.024,.013),(0,.013)]
 steps=64;vs=[];fs=[]
 for r,z in profile:
  for i in range(steps):a=2*math.pi*i/steps;vs.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),top+z))
 for j in range(len(profile)-1):
  for i in range(steps):k=(i+1)%steps;fs.append([j*steps+i,j*steps+k,(j+1)*steps+k,(j+1)*steps+i])
 ob=mesh_obj(name+' bowl',vs,fs,ceramic,True)
 bm=bmesh.new();bm.from_mesh(ob.data);bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=.000001);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(ob.data);bm.free()
 tube(name+' handle',[(center[0]+.040,center[1],top+.068),(center[0]+.066,center[1],top+.072),(center[0]+.073,center[1],top+.048),(center[0]+.055,center[1],top+.030),(center[0]+.036,center[1],top+.033)],.006,ceramic)
 if with_tea:cylinder(name+' still tea surface',(center[0],center[1],top+.064),.037,.002,tea)
 return ob

cup_one=cup('Far cup — waiting tea',(.97,1.39),True);cup_two=cup('Far cup — empty',(1.14,1.39),False)

def area(name,loc,target,energy,color,size):
 data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.color=color;data.shape='DISK';data.size=size
 ob=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();return ob

area('Warm room light — broad source',(.72,.90,2.22),(.55,-.65,.28),115,(1.0,.78,.52),.95)
area('Quiet warm interior fill',(.45,1.98,1.75),(.70,1.2,.65),12,(1.0,.76,.50),.75)
area('Cool rainy fill outside frame',(-2.6,-3.4,2.3),(-.25,.0,.75),145,(.80,.86,1.0),4.0)
area('Soft reflected entry fill',(-1.6,-1.4,1.7),(-.8,-.35,.04),34,(.82,.88,1.0),1.8)

bpy.ops.object.camera_add(location=P['camera']['position']);cam=bpy.context.object;cam.name='Camera — waiting at the threshold';target=Vector(P['camera']['target']);cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=P['camera']['lens_mm'];cam.data.clip_start=.05;cam.data.clip_end=100
cam.data.dof.use_dof=True;cam.data.dof.focus_distance=(cam.location-Vector((-.55,-.25,.45))).length;cam.data.dof.aperture_fstop=7.1;S.camera=cam
bpy.context.view_layer.update()

# Deliberately bounded checks, not a manufacturing/architectural certificate.
emissive_materials=[m.name for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes if n.type=='EMISSION' or (n.type=='BSDF_PRINCIPLED' and sum(n.inputs['Emission Color'].default_value[:3])>0 and n.inputs['Emission Strength'].default_value>0)]
cup_count=len([o for o in S.objects if o.name.startswith('Far cup') and o.name.endswith('bowl')]);assert cup_count==2
report={'scope':'virtual art geometry and file checks; not a survey, architectural, electrical or safety design',
        'story_moment':P['story_moment'],'empty_tray_by_authored_scene':True,'empty_hook_by_authored_scene':True,'cups':cup_count,'people':0,'umbrellas':0,'bread_or_bags':0,
        'external_images':[im.filepath for im in bpy.data.images if im.source=='FILE'],
        'emissive_materials':emissive_materials,'compositor_enabled':S.use_nodes,'mesh_checks':[]}
assert not emissive_materials
deps=bpy.context.evaluated_depsgraph_get()
for ob in S.objects:
 if ob.type!='MESH':continue
 ev=ob.evaluated_get(deps);me=ev.to_mesh();assert all(math.isfinite(c) for v in me.vertices for c in v.co),ob.name
 report['mesh_checks'].append({'name':ob.name,'vertices':len(me.vertices),'finite':True});ev.to_mesh_clear()
for ob in (tray,cup_one,cup_two):
 bm=bmesh.new();bm.from_mesh(ob.data);assert all(e.is_manifold for e in bm.edges),ob.name;assert bm.calc_volume(signed=False)>0;bm.free()
report['tray_closed_solid']=True;report['cup_bowls_closed_solid']=True
report['door_hinge_consistent']=leaf.parent==pivot and all(o.parent==pivot for o in S.objects if o.name.startswith(('Handle ','Plain round brass knob','Simple hinge')))
report['hinge_axes_coincide_with_pivot']=all(abs(o.location.x)<1e-8 and abs(o.location.y)<1e-8 for o in S.objects if o.name.startswith('Simple hinge'))
assert report['door_hinge_consistent']
assert report['hinge_axes_coincide_with_pivot']
report['door_open_angle_degrees']=d['open_angle_degrees'];report['door_floor_clearance_m']=d['hinge'][2]
report['tray_floor_contact_gap_m']=min(v.co.z for v in tray.data.vertices);assert abs(report['tray_floor_contact_gap_m'])<1e-8
report['cup_counter_contact_gaps_m']=[min(v.co.z for v in ob.data.vertices)-top for ob in (cup_one,cup_two)];assert all(abs(x)<1e-7 for x in report['cup_counter_contact_gaps_m'])
proj=[world_to_camera_view(S,cam,tray.matrix_world@v.co) for v in tray.data.vertices]
report['tray_camera_bounds']={'left':min(v.x for v in proj),'right':max(v.x for v in proj),'bottom':min(v.y for v in proj),'top':max(v.y for v in proj)}
assert all(.015<getattr(p,axis)<.985 for p in proj for axis in ('x','y')),'Tray clipped'
assert not report['external_images'] and not S.use_nodes
report['render']={'width':S.render.resolution_x,'height':S.render.resolution_y,'max_samples':S.cycles.samples,'threads':2,'device':'CPU','denoising':False,'note':'Installed Blender lacks OpenImageDenoise; native sampling only'}
report['object_count']=len(S.objects);report['source_parameters_sha256']=hashlib.sha256((ROOT/'parameters.json').read_bytes()).hexdigest()
report['build_source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(ROOT/'geometry_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
for screen in bpy.data.screens:
 for ar in screen.areas:
  for sp in ar.spaces:
   if sp.type=='FILE_BROWSER' and sp.params:sp.params.directory=b'/'*1023;sp.params.directory=b'//'
   if sp.type=='VIEW_3D':sp.region_3d.view_perspective='CAMERA';sp.shading.color_type='MATERIAL'
bpy.ops.object.select_all(action='DESELECT')
S['Title']='비가 머물 자리 / A Place for Rain';S['Narrative']='Before the fictional passenger arrives; empty prepared tray and hook, no possessions placed here.'
S['Scope']='Independent original vignette; not the game or an existing real home.'
S['ParametersSha256']=report['source_parameters_sha256'];S['BuildSourceSha256']=report['build_source_sha256']
filename='draft_04.png' if DRAFT else 'a_place_for_rain_final.png'
S.render.filepath='//renders/'+filename
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'A_Place_for_Rain.blend'))
if '--no-render' not in sys.argv:
 S.render.filepath=str(OUT/filename);bpy.ops.render.render(write_still=True);print('RENDER_COMPLETE',filename)
