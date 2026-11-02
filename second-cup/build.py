"""The Second Cup — an independently modeled, original kitchen still life.

Blender 4.3.2. CPU / two threads. Generated concept is packed as reference only.
TMPDIR="$PWD/work" blender -b -t 2 --python build.py -- --draft
TMPDIR="$PWD/work" blender -b -t 2 --python build.py
No downloaded models, textures, HDRIs, or image-projected surfaces.
"""
import bpy
import bmesh
import math
import sys
import json
from pathlib import Path
from mathutils import Vector, Matrix

ROOT = Path(__file__).resolve().parent
DRAFT = '--draft' in sys.argv
NO_RENDER = '--no-render' in sys.argv
for name in ('renders', 'work'):
    (ROOT / name).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    bpy.data.collections.remove(c)
COL = {}
for key, name in [('near','01 · Tea already poured'),('far','02 · A cup kept empty'),
                  ('plate_near','03 · The first bread plate'),('plate_far','04 · The second bread plate'),
                  ('kettle','05 · Tea kept ready'),('room','06 · A small kitchen fragment'),
                  ('rig','07 · Camera, light and reference')]:
    c=bpy.data.collections.new(name); bpy.context.scene.collection.children.link(c); COL[key]=c

def put(ob, key):
    for c in list(ob.users_collection): c.objects.unlink(ob)
    COL[key].objects.link(ob); return ob

def mat(name, color, roughness=.4, metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=roughness
    p.inputs['Metallic'].default_value=metal
    return m

def microtexture(m, scale, distance, strength=.12):
    n=m.node_tree.nodes; l=m.node_tree.links; p=n.get('Principled BSDF')
    coord=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=scale; noise.inputs['Detail'].default_value=2
    l.new(coord.outputs['Object'],noise.inputs['Vector'])
    b=n.new('ShaderNodeBump'); b.inputs['Distance'].default_value=distance; b.inputs['Strength'].default_value=strength
    l.new(noise.outputs['Fac'],b.inputs['Height']); l.new(b.outputs['Normal'],p.inputs['Normal'])

ivory=mat('Ivory stoneware · quiet glaze',(.68,.61,.49),.19)
ivory.node_tree.nodes.get('Principled BSDF').inputs['Coat Weight'].default_value=.22
ivory.node_tree.nodes.get('Principled BSDF').inputs['Coat Roughness'].default_value=.15
microtexture(ivory,850,.000035,.08)
steel=mat('Kettle · satin stainless steel',(.54,.57,.60),.30,1)
p=steel.node_tree.nodes.get('Principled BSDF'); p.inputs['Anisotropic'].default_value=.08
# Very restrained, object-space roughness variation; no downloaded brushed-metal map.
n=steel.node_tree.nodes; l=steel.node_tree.links
coord=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=260
noise.inputs['Detail'].default_value=2; l.new(coord.outputs['Object'],noise.inputs['Vector'])
rough=n.new('ShaderNodeMapRange'); rough.inputs['To Min'].default_value=.28; rough.inputs['To Max'].default_value=.32
l.new(noise.outputs['Fac'],rough.inputs['Value']); l.new(rough.outputs['Result'],p.inputs['Roughness'])
dark=mat('Heat-dark handle · charcoal resin',(.012,.014,.016),.34)
base=mat('Kettle base ring · dark steel',(.035,.039,.044),.34,.8)
table=mat('Porcelain slab · dusty plum',(.205,.145,.185),.38)
microtexture(table,460,.00009,.13)
tilemats=[mat('Cream tile · '+str(i),c,.31) for i,c in enumerate([(.53,.49,.42),(.58,.535,.46),(.55,.50,.435)])]
grout=mat('Warm-grey fine grout',(.40,.365,.31),.8)
apron=mat('Lower cabinet · muted mushroom enamel',(.11,.095,.105),.53)
tea=mat('Tea · transmissive amber and measured absorption',(.94,.81,.58),.045)
p=tea.node_tree.nodes.get('Principled BSDF'); p.inputs['Transmission Weight'].default_value=1
p.inputs['IOR'].default_value=1.333
n=tea.node_tree.nodes; l=tea.node_tree.links
absorb=n.new('ShaderNodeVolumeAbsorption'); absorb.inputs['Color'].default_value=(.60,.19,.035,1)
absorb.inputs['Density'].default_value=38
l.new(absorb.outputs['Volume'],n.get('Material Output').inputs['Volume'])

def mesh(name, verts, faces, material, key, smooth=True):
    me=bpy.data.meshes.new(name); me.from_pydata(verts,[],faces); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    ob=bpy.data.objects.new(name,me); COL[key].objects.link(ob); ob.data.materials.append(material)
    for f in me.polygons: f.use_smooth=smooth
    return ob

def lathe(name, profile, center, material, key, steps=128, cyclic=False):
    # Profile is radius,z, traversing a complete solid cross-section. Poles are
    # single vertices, not zero-radius rings, so there are no degenerate faces.
    verts=[]; rings=[]
    for r,z in profile:
        if abs(r)<1e-10:
            rings.append([len(verts)]); verts.append((center[0],center[1],z))
        else:
            ring=[]
            for j in range(steps):
                a=2*math.pi*j/steps; ring.append(len(verts)); verts.append((center[0]+r*math.cos(a),center[1]+r*math.sin(a),z))
            rings.append(ring)
    faces=[]
    for i in range(len(rings) if cyclic else len(rings)-1):
        a=rings[i]; b=rings[(i+1)%len(rings)]
        for j in range(steps):
            k=(j+1)%steps
            if len(a)==1: faces.append((a[0],b[k],b[j]))
            elif len(b)==1: faces.append((a[j],a[k],b[0]))
            else: faces.append((a[j],a[k],b[k],b[j]))
    return mesh(name,verts,faces,material,key)

def tube(name, points, radii, material, key, sides=20, wall=None):
    # Closed solid rod, or a closed shell with a genuinely open bore at both ends.
    points=[Vector(p) for p in points]; verts=[]; frames=[]
    for i,p in enumerate(points):
        tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized()
        axis=Vector((0,1,0))
        if abs(tangent.dot(axis))>.95: axis=Vector((1,0,0))
        u=tangent.cross(axis).normalized(); v=tangent.cross(u).normalized(); frames.append((u,v))
    layers=[0] if wall is None else [0,wall]
    for subtract in layers:
        for p,r,(u,v) in zip(points,radii,frames):
            for j in range(sides):
                a=2*math.pi*j/sides; q=p+(r-subtract)*(math.cos(a)*u+math.sin(a)*v); verts.append(tuple(q))
    faces=[]; count=len(points)
    for layer in range(len(layers)):
        start=layer*count*sides
        for i in range(count-1):
            for j in range(sides):
                k=(j+1)%sides; faces.append((start+i*sides+j,start+i*sides+k,start+(i+1)*sides+k,start+(i+1)*sides+j))
    if wall is None:
        faces.append(tuple(reversed(range(sides)))); faces.append(tuple((count-1)*sides+j for j in range(sides)))
    else:
        for i in (0,count-1):
            for j in range(sides):
                k=(j+1)%sides; a=i*sides+j; b=i*sides+k
                faces.append((a,b,count*sides+b,count*sides+a))
    return mesh(name,verts,faces,material,key)

def cube(name, loc, dims, material, key, bevel=.002):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); put(ob,key); ob.data.materials.append(material)
    if bevel:
        mod=ob.modifiers.new('Rounded real edge','BEVEL'); mod.width=bevel; mod.segments=3
        mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

def cylinder(name, a, b, radius, material, key, vertices=64):
    a,b=Vector(a),Vector(b); v=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=v.length,location=(a+b)*.5)
    ob=bpy.context.object; ob.name=name; ob.rotation_euler=v.to_track_quat('Z','Y').to_euler(); put(ob,key); ob.data.materials.append(material)
    mod=ob.modifiers.new('Soft machined edge','BEVEL'); mod.width=.0008; mod.segments=3
    mod=ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

CUP_PROFILE=[(0,.005),(.026,.005),(.028,.003),(.029,.000),(.032,.000),(.034,.001),
 (.0355,.004),(.037,.009),(.040,.017),(.044,.028),(.047,.041),(.049,.055),(.050,.068),
 (.050,.0715),(.0497,.0732),(.049,.0744),(.0481,.0748),(.0472,.0744),(.0465,.0734),
 (.046,.0715),(.046,.068),(.045,.055),(.043,.041),(.040,.028),(.036,.019),
 (.032,.015),(.028,.013),(.020,.012),(0,.012)]
NEAR=(-.17,-.165); FAR=(.155,.12)
for key,center,angle,label in [('near',NEAR,math.radians(182),'Near'),('far',FAR,math.radians(15),'Far')]:
    ob=lathe(label+' cup | continuous 4 mm rim, inner bowl and foot',CUP_PROFILE,center,ivory,key)
    ob['role']='cup_body'; ob['contact_surface_z']=0.; ob['inner_floor_z']=.012; ob['rim_z']=.0748
    ob['rim_radial_thickness_m']=.004; ob['center_xy']=list(center)
    points=[]
    for i in range(57):
        a=math.radians(-115+209*i/56); radial=.049+.026*math.cos(a); z=.042+.025*math.sin(a)
        points.append((center[0]+radial*math.cos(angle),center[1]+radial*math.sin(angle),z))
    ob=tube(label+' cup | solid rounded handle',points,[.0058]*len(points),ivory,key,24)
    ob['intentional_hidden_overlap']='Both ends enter cup body; not a boolean-unioned fabrication mesh.'
    ob['role']='cup_handle'; ob['cup_center_xy']=list(center)

# Liquid follows the actual inner bowl. Top is a horizontal disc with only a
# 0.8 mm wall meniscus; no inverted cone, open surface or painted tea image.
LIQUID_Z=.059
liquid_profile=[(0,.01215),(.020,.01215),(.0279,.01315),(.0319,.01515),(.0359,.01915),
 (.0399,.02815),(.0429,.04115),(.0449,.05515),(.04520,.0598),
 (.04495,.05945),(.0443,.05912),(.0434,LIQUID_Z),(.040,LIQUID_Z),(0,LIQUID_Z)]
liquid=lathe('Tea | closed volume and 0.8 mm wall meniscus',liquid_profile,NEAR,tea,'near',160)
liquid['role']='liquid'; liquid['surface_z']=LIQUID_Z; liquid['meniscus_max_z']=.0598
liquid['optical_approximation']='Tint, absorption and disabled refractive caustics are artistic approximations, not beverage measurements.'
liquid.visible_shadow=False

plate_profile=[(0,.0035),(.037,.0035),(.0385,.0015),(.040,.000),(.045,.000),(.047,.001),
 (.049,.004),(.061,.0065),(.073,.011),(.082,.016),(.085,.019),(.0855,.0205),
 (.085,.0218),(.0838,.0222),(.081,.0207),(.073,.016),(.061,.010),(.047,.0075),(.035,.007),(0,.007)]
for key,center,label in [('plate_near',(.025,-.255),'Near'),('plate_far',(.215,-.075),'Far')]:
    ob=lathe(label+' bread plate | empty shallow dish with real foot',[(r*.88,z*.83) for r,z in plate_profile],center,ivory,key)
    ob['role']='bread_plate'; ob['contact_surface_z']=0.

K=(-.145,.195)
body_profile=[(0,.005),(.09,.005),(.103,.006),(.108,.009),(.111,.016),(.112,.030),
 (.110,.055),(.105,.083),(.096,.111),(.081,.135),(.062,.151),(.048,.159),
 (.046,.161),(.0445,.161),(.0445,.1585),(.061,.149),(.0795,.1335),(.0945,.110),
 (.1035,.082),(.1085,.0545),(.1105,.030),(.1095,.016),(.1065,.0105),(.102,.0075),(.09,.0065),(0,.0065)]
body=lathe('Kettle | spun hollow steel body',body_profile,K,steel,'kettle',160)
body['role']='kettle_body'
foot_profile=[(.091,0),(.107,0),(.110,.002),(.111,.0045),(.110,.007),(.106,.008),(.091,.008)]
foot=lathe('Kettle | continuous grounded base ring',foot_profile,K,base,'kettle',128,True)
foot['role']='kettle_contact'; foot['contact_surface_z']=0.
lid_profile=[(0,.161),(.046,.161),(.051,.162),(.0525,.164),(.052,.166),(.049,.168),(.039,.173),(.024,.176),(0,.177)]
lathe('Kettle | separate shallow steel lid',lid_profile,K,steel,'kettle')
knob_profile=[(0,.176),(.010,.176),(.011,.178),(.011,.185),(.014,.188),(.0145,.191),(.013,.194),(.009,.196),(0,.197)]
lathe('Kettle | charcoal lid knob',knob_profile,K,dark,'kettle',96)

# Open, rising spout. A small exact boolean cuts the shell where the real bore
# enters it. Hidden overlap with the spout wall is an assembly seam, not a leak test.
phi=math.radians(-151); radial=Vector((math.cos(phi),math.sin(phi),0))
def spout_point(t):
    r=.087+.073*t; z=.073+.105*t+.008*math.sin(math.pi*t)
    return Vector((K[0],K[1],0))+radial*r+Vector((0,0,z))
spoints=[spout_point(i/40) for i in range(41)]
spout=tube('Kettle | open tapered spout, 1.6 mm lip',spoints,[.023-.010*i/40 for i in range(41)],steel,'kettle',48,.0016)
spout['role']='spout'; spout['wall_thickness_m']=.0016
start=spout_point(0); axis=(spout_point(.02)-start).normalized()
cutter=cylinder('Temporary spout bore',start-axis*.008,start+axis*.10,.0208,steel,'kettle')
for mod in list(cutter.modifiers): cutter.modifiers.remove(mod)
mod=body.modifiers.new('Actual spout opening through vessel shell','BOOLEAN'); mod.operation='DIFFERENCE'; mod.solver='EXACT'; mod.object=cutter
bpy.context.view_layer.objects.active=body; bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.data.objects.remove(cutter,do_unlink=True)

# Fixed arched handle, metal skeleton plus resin grip; each end is socketed.
arc=[]
for i in range(81):
    a=math.pi*i/80; arc.append((K[0]+.078*math.cos(a),K[1]+.010,.134+.120*math.sin(a)))
tube('Kettle | steel handle skeleton',arc,[.0048]*len(arc),steel,'kettle',20)
grip=arc[8:73]
tube('Kettle | thick arched charcoal grip',grip,[.011]*len(grip),dark,'kettle',24)
for side in (-1,1):
    lug=cube('Kettle | handle lug '+str(side),(K[0]+side*.078,K[1]+.010,.133),(.017,.017,.038),steel,'kettle',.003)
    lug.rotation_euler[1]=side*math.radians(17)
    cylinder('Kettle | hinge pin '+str(side),(K[0]+side*.078,K[1]-.001,.139),(K[0]+side*.078,K[1]+.022,.139),.0056,base,'kettle')

# The concept kettle is interpreted as a small two-person vessel rather than a
# full-size kitchen stock kettle. Uniform scaling keeps the assembled joints.
transform=Matrix.Translation((K[0],K[1],0)) @ Matrix.Scale(.86,4) @ Matrix.Translation((-K[0],-K[1],0))
for ob in COL['kettle'].objects:
    ob.matrix_world=transform @ ob.matrix_world
    ob['uniform_design_scale']=.86
spout['wall_thickness_m']=.0016*.86
spout['mouth_center_world']=list(transform @ spoints[-1])
spout['mouth_axis_world']=list((spoints[-1]-spoints[-2]).normalized())
spout.name='Kettle | open tapered spout, 1.4 mm lip'

# Background architecture, not extra narrative props.
cube('Table | rounded porcelain slab',(0,0,-.016),(1.30,1.04,.032),table,'room',.012)
cube('Table | narrow mushroom-coloured apron',(0,.015,-.11),(1.00,.99,.165),apron,'room',.012)
cube('Wall | warm grout backing',(0,.518,.27),(1.6,.03,.56),grout,'room',.001)
for row in range(5):
    for col in range(8):
        x=-.80+col*.225+(row%2)*.1125
        cube('Backsplash | tile '+str(row)+'-'+str(col),(x,.498,.057+row*.107),(.221,.011,.103),tilemats[(row+col)%3],'room',.002)

def aim(ob, point): ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
def area(name, loc, target, color, power, size, size_y):
    d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.color=color; d.shape='RECTANGLE'; d.size=size; d.size_y=size_y
    ob=bpy.data.objects.new(name,d); COL['rig'].objects.link(ob); ob.location=loc; aim(ob,target); return ob
area('Warm-neutral soft rectangle · long kettle reflection',(-.48,-.21,.68),(-.10,.08,.03),(1,.79,.58),8,.08,.72)
area('Quiet lavender window fill',(.55,.30,.72),(0,.02,.025),(.73,.77,1),2,.52,.60)
area('Small neutral room bounce · cup interiors',(.12,-.56,.62),(.12,.10,.025),(.93,.90,.85),.8,.50,.42)
scene=bpy.context.scene
scene.world.use_nodes=True
scene.world.node_tree.nodes.get('Background').inputs['Color'].default_value=(.45,.40,.36,1)
scene.world.node_tree.nodes.get('Background').inputs['Strength'].default_value=.25
bpy.ops.object.camera_add(location=(.10,-1.02,1.13)); cam=bpy.context.object; cam.name='Camera | a shared table, no absent-person portrait'; put(cam,'rig')
aim(cam,(-.01,.010,.038)); cam.data.lens=80; cam.data.sensor_width=36; scene.camera=cam
cam.data.dof.use_dof=False

ref=bpy.data.images.load(str(ROOT/'reference/gpt_image_concept.png'),check_existing=False)
ref.name='REFERENCE ONLY · original GPT Image concept'
ref.filepath='_'*1023  # Clear stale bytes beyond the future shorter path's NUL.
ref.filepath='//reference/gpt_image_concept.png'; ref.pack()
ref.use_fake_user=True
scene['title']='두 잔의 자리 · The Second Cup'
scene['story']='Fictional rainy town: a spouse has prepared tea; the passenger and two soboro buns have not arrived yet. Ordinary waiting, not tragedy.'
scene['reference_use']='Packed reference only. Not attached to any shader, world or compositor; independently authored geometry.'
scene['hero_prop_count']=5
scene['known_approximations']='No fluid or thermal simulation. Liquid shadow rays are disabled, caustics disabled, mild indirect clamp. Separate assembled parts overlap at hidden seams. Not a product, safety or manufacturing design.'
scene.render.engine='CYCLES'; scene.cycles.device='CPU'
scene.render.threads_mode='FIXED'; scene.render.threads=2
scene.cycles.samples=24 if DRAFT else 128
scene.cycles.use_adaptive_sampling=True; scene.cycles.adaptive_threshold=.05 if DRAFT else .018
scene.cycles.use_denoising=False  # This Blender build exposes no denoiser enum.
scene.cycles.max_bounces=10; scene.cycles.diffuse_bounces=4; scene.cycles.glossy_bounces=5; scene.cycles.transmission_bounces=8
scene.cycles.caustics_reflective=False; scene.cycles.caustics_refractive=False
scene.cycles.sample_clamp_direct=0; scene.cycles.sample_clamp_indirect=4
scene.render.resolution_x=600 if DRAFT else 1200; scene.render.resolution_y=scene.render.resolution_x; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.render.image_settings.color_mode='RGB'; scene.render.image_settings.color_depth='8'
scene.render.film_transparent=False
scene.render.use_stamp=False
scene.view_settings.view_transform='AgX'; scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=-.10
scene.render.filepath='//work/draft.png' if DRAFT else '//renders/the_second_cup_final.png'
scene.render.use_file_extension=True
scene.unit_settings.system='METRIC'
# Set a useful camera view when opening the editable file, without using the GUI.
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        if area_ui.type=='VIEW_3D': area_ui.spaces.active.region_3d.view_perspective='CAMERA'
        for space in area_ui.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                # Overwrite the fixed-size browser buffer before shortening it;
                # otherwise stale bytes beyond NUL can retain a machine path.
                space.params.directory=b'/'*1023
                space.params.directory=b'//'
                space.params.filename='_'*255
                space.params.filename=''
filename='The_Second_Cup_Draft.blend' if DRAFT else 'The_Second_Cup.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/filename),relative_remap=True)
settings={'blender_version':bpy.app.version_string,'draft':DRAFT,'hero_props':5,
 'render':{'engine':'CYCLES','device':'CPU','threads':2,'samples':scene.cycles.samples,'resolution':[scene.render.resolution_x,scene.render.resolution_y],'denoising':scene.cycles.use_denoising},
 'cup_inner_floor_m':.012,'cup_rim_height_m':.0748,'tea_surface_height_m':LIQUID_Z,'meniscus_height_m':.0008,
 'no_image_texture_projection':True,'no_downloaded_assets':True,'reference_original_preserved':True,
 'limitations':['Not a product or fabrication design.','No thermal, fluid or mechanical simulation.','Optical absorption, disabled liquid shadows and disabled caustics are artistic approximations.','Assembled handle, body and lugs have intentional hidden overlaps.']}
(ROOT/('work/draft_settings.json' if DRAFT else 'checks.json')).write_text(json.dumps(settings,ensure_ascii=False,indent=2)+'\n')
if not NO_RENDER: bpy.ops.render.render(write_still=True)
print('SECOND_CUP_BUILD_FINISHED',filename)
