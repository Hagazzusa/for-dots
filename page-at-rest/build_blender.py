"""Import FreeCAD tessellation once, create original paper and quiet lighting.
Run: blender --background --factory-startup --threads 2 --python build_blender.py -- --draft
"""
import bpy, bmesh, math, json, sys, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from bpy_extras.object_utils import world_to_camera_view

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from geometry import page_point
P=json.loads((ROOT/'parameters.json').read_text())
DRAFT='--draft' in sys.argv
OUT=ROOT/'renders'; OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
S=bpy.context.scene; S.unit_settings.system='METRIC'; S.unit_settings.scale_length=1.0
S.render.engine='CYCLES'; S.cycles.device='CPU'; S.render.threads_mode='FIXED'; S.render.threads=2
S.cycles.samples=P['render']['draft_samples' if DRAFT else 'final_samples']; S.cycles.use_denoising=False
S.cycles.max_bounces=10; S.cycles.diffuse_bounces=5; S.cycles.transmission_bounces=6
S.cycles.seed=21
S.render.resolution_x=P['render']['draft_width' if DRAFT else 'final_width']
S.render.resolution_y=P['render']['draft_height' if DRAFT else 'final_height']
S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG'; S.render.image_settings.color_mode='RGBA'; S.render.image_settings.color_depth='8'
S.render.film_transparent=False; S.render.use_stamp=False
S.view_settings.view_transform='AgX'; S.view_settings.look='AgX - Medium High Contrast'; S.view_settings.exposure=0; S.view_settings.gamma=1
S.world.color=(0.16,0.16,0.16)
S.world.use_nodes=True; S.world.node_tree.nodes['Background'].inputs['Color'].default_value=(0.55,0.59,0.63,1)
S.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.045

def simple_mat(name,color,rough=.5,metal=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m

walnut=simple_mat('Walnut — restrained long grain',(.15,.068,.026),.44)
n=walnut.node_tree.nodes; l=walnut.node_tree.links; p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexCoord'); mapping=n.new('ShaderNodeVectorMath'); mapping.operation='MULTIPLY'; mapping.inputs[1].default_value=(2,32,6)
l.new(tex.outputs['Generated'],mapping.inputs[0]); noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=3.7
noise.inputs['Detail'].default_value=3.2; noise.inputs['Roughness'].default_value=.65; l.new(mapping.outputs[0],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.17; ramp.color_ramp.elements[0].color=(.042,.014,.005,1)
ramp.color_ramp.elements[1].position=.83; ramp.color_ramp.elements[1].color=(.23,.105,.035,1)
l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs['Color'],p.inputs['Base Color'])
bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.11; bump.inputs['Distance'].default_value=.00013
l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],p.inputs['Normal'])
brass=simple_mat('Soft brushed brass',(.42,.27,.105),.31,.76)

paper=bpy.data.materials.new('Ivory fibre paper — diffuse plus transmitted light, no emission'); paper.use_nodes=True
n=paper.node_tree.nodes; n.clear(); l=paper.node_tree.links
out=n.new('ShaderNodeOutputMaterial'); diffuse=n.new('ShaderNodeBsdfDiffuse'); trans=n.new('ShaderNodeBsdfTranslucent'); mix=n.new('ShaderNodeMixShader')
mix.inputs[0].default_value=.58; diffuse.inputs['Roughness'].default_value=.25
l.new(diffuse.outputs[0],mix.inputs[1]); l.new(trans.outputs[0],mix.inputs[2]); l.new(mix.outputs[0],out.inputs[0])
tex=n.new('ShaderNodeTexCoord'); noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=340
noise.inputs['Detail'].default_value=3.4; noise.inputs['Roughness'].default_value=.72; l.new(tex.outputs['Object'],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position=.10; ramp.color_ramp.elements[0].color=(.52,.405,.265,1)
ramp.color_ramp.elements[1].position=.88; ramp.color_ramp.elements[1].color=(.91,.82,.65,1)
l.new(noise.outputs['Fac'],ramp.inputs[0]); l.new(ramp.outputs['Color'],diffuse.inputs['Color']); l.new(ramp.outputs['Color'],trans.inputs['Color'])
fine=n.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value=2400; fine.inputs['Detail'].default_value=2
l.new(tex.outputs['Object'],fine.inputs['Vector']); bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.13; bump.inputs['Distance'].default_value=.00006
l.new(fine.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs['Normal'],diffuse.inputs['Normal']); l.new(bump.outputs['Normal'],trans.inputs['Normal'])

def mesh_obj(name,vertices,faces,material):
    me=bpy.data.meshes.new(name+'_Mesh'); me.from_pydata(vertices,[],faces); me.update()
    ob=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(ob); ob.data.materials.append(material)
    for f in me.polygons:f.use_smooth=True
    return ob

payload=json.loads((ROOT/'cad/parts_mesh.json').read_text())
transfer=[]; cad={}
for part in payload['parts']:
    verts=[tuple(x*.001 for x in v) for v in part['vertices']]
    ob=mesh_obj(part['name'],verts,part['faces'],walnut if part['material']=='walnut' else brass); cad[ob.name]=ob
    ob['geometry_source']='FreeCAD native shape tessellation; no remodeling'
    ob['source_units']='mm'; ob['millimetres_to_metres_applied_once']=True
    err=max(abs(ob.data.vertices[i].co[k]-v[k]) for i,v in enumerate(verts) for k in range(3))
    assert err<1e-7 and len(ob.data.polygons)==len(part['faces'])
    transfer.append({'name':ob.name,'max_vertex_transfer_error_m':err,'triangles_unchanged':True,
                     'scale':[float(x) for x in ob.scale]})

pages={}; page_face_v={}
for pg in P['pages']:
    nu=P['paper']['segments_u']; nv=P['paper']['segments_v']; verts=[]; faces=[]; band=[]
    half=P['paper']['thickness']*.5
    for layer in (1,-1):
        for j in range(nv+1):
            v=j/nv
            for i in range(nu+1):
                u=i/nu; point=Vector(page_point(pg,P['paper'],u,v))
                du=Vector(page_point(pg,P['paper'],u+.0001,v))-Vector(page_point(pg,P['paper'],u-.0001,v))
                dv=Vector(page_point(pg,P['paper'],u,v+.0001))-Vector(page_point(pg,P['paper'],u,v-.0001))
                normal=du.cross(dv).normalized()
                if normal.y>0:normal=-normal
                verts.append(tuple((point+normal*half*layer)*.001))
    count=(nu+1)*(nv+1)
    for layer in (0,1):
        off=layer*count
        for j in range(nv):
            for i in range(nu):
                a=off+j*(nu+1)+i; f=[a,a+1,a+nu+2,a+nu+1]
                faces.append(f if layer==0 else f[::-1]); band.append((j+.5)/nv)
    perimeter=list(range(nu+1))+[j*(nu+1)+nu for j in range(1,nv+1)]+[nv*(nu+1)+i for i in range(nu-1,-1,-1)]+[j*(nu+1) for j in range(nv-1,0,-1)]
    for a,b in zip(perimeter,perimeter[1:]+perimeter[:1]):
        faces.append([a,b,b+count,a+count]); band.append(((a//(nu+1))+(b//(nu+1)))/(2*nv))
    ob=mesh_obj(pg['name'],verts,faces,paper)
    bm=bmesh.new(); bm.from_mesh(ob.data); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(ob.data); bm.free()
    ob['thickness_mm']=P['paper']['thickness']; ob['not_emissive']=True
    pages[ob.name]=ob; page_face_v[ob.name]=band

def cube(name,loc,scale,mat,bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name
    ob.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat)
    if bevel:
        m=ob.modifiers.new('Soft edges','BEVEL'); m.width=bevel; m.segments=4
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return ob

desk=simple_mat('Warm grey mineral desktop',(.37,.335,.29),.80)
wall=simple_mat('Quiet warm plaster',(.45,.415,.36),.88)
# One continuous matte cyclorama avoids a distracting floor/wall horizon.
section=[(-1.2,0.0),(.20,0.0)]
section += [(.20+.16*math.sin((math.pi/2)*i/32),.16*(1-math.cos((math.pi/2)*i/32))) for i in range(1,33)]
section += [(.36,1.5)]
cyverts=[(x,y,z) for x in (-1.2,1.2) for y,z in section]
N=len(section); cyfaces=[(i,i+1,N+i+1,N+i) for i in range(N-1)]
mesh_obj('Continuous desk and quiet background',cyverts,cyfaces,desk)
linen=simple_mat('Muted flax linen',(.30,.28,.235),.85)
bookpaper=simple_mat('Book page block',(.55,.48,.37),.88)
bookloc=(-.175,.125)
cube('One small linen book — lower cover',(bookloc[0],bookloc[1],.002),(.105,.070,.004),linen,.001)
cube('One small linen book — pages',(bookloc[0]+.001,bookloc[1]-.001,.015),(.101,.065,.023),bookpaper,.0007)
cube('One small linen book — upper cover',(bookloc[0],bookloc[1],.028),(.105,.070,.004),linen,.001)
cube('One small linen book — spine',(bookloc[0]-.050,bookloc[1],.015),(.005,.070,.026),linen,.001)

def area(name,loc,target,power,color,size,shape='DISK',size_y=None):
    data=bpy.data.lights.new(name,'AREA'); data.energy=power; data.color=color; data.shape=shape; data.size=size
    if size_y is not None:data.size_y=size_y
    ob=bpy.data.objects.new(name,data); bpy.context.collection.objects.link(ob); ob.location=loc
    ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob

# Two sides of one concealed broad optical source, represented as area emitters.
# No emissive page, compositor bloom, painted pool or additive halo is used.
area('Concealed warm area — toward paper',(0,.042,.073),(0,-.01,.093),1.10,(1,.63,.31),.058,'RECTANGLE',.052)
area('Concealed warm area — rear wash',(0,.045,.071),(0,.26,.065),.65,(1,.61,.29),.055,'RECTANGLE',.05)
area('Large quiet window',(-.33,-.42,.56),(0,0,.08),4.0,(.82,.89,1.0),.75)
area('Soft upper reflection',(.33,.12,.52),(0,0,.07),1.4,(1.0,.91,.78),.50)

bpy.ops.object.camera_add(location=(.33,-.74,.315)); cam=bpy.context.object; cam.name='Camera — quiet three-quarter'
target=Vector((.023,.025,.113)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=68
cam.data.dof.use_dof=True; cam.data.dof.focus_distance=(cam.location-Vector((0,.01,.09))).length; cam.data.dof.aperture_fstop=11
S.camera=cam
bpy.context.view_layer.update()
projected=[world_to_camera_view(S,cam,ob.matrix_world@v.co) for ob in list(pages.values())+list(cad.values()) for v in ob.data.vertices]
camera_bounds={'left':min(p.x for p in projected),'right':max(p.x for p in projected),
               'bottom':min(p.y for p in projected),'top':max(p.y for p in projected)}
assert camera_bounds['left']>.05 and camera_bounds['right']<.95 and camera_bounds['bottom']>.05 and camera_bounds['top']<.95

def bvh(ob):
    return BVHTree.FromPolygons([ob.matrix_world@v.co for v in ob.data.vertices],[list(f.vertices) for f in ob.data.polygons],all_triangles=False)

report={'scope':'virtual geometric and file validation only, not manufacturing/electrical/thermal safety',
        'freecad_transfer':transfer,'millimetres_to_metres_factor':.001,'camera_projected_bounds':camera_bounds,'pages':[], 'overlaps':{}}
for name,ob in pages.items():
    bm=bmesh.new(); bm.from_mesh(ob.data)
    finite=all(math.isfinite(x) for v in bm.verts for x in v.co)
    closed=all(e.is_manifold for e in bm.edges); vol=bm.calc_volume(signed=False)
    assert finite and closed and vol>0
    bm.free(); report['pages'].append({'name':name,'finite':finite,'closed_manifold':closed,'volume_m3':vol,'thickness_mm':P['paper']['thickness']})
    other='Left_Brass_Cradle' if name.startswith('Left') else 'Right_Brass_Cradle'
    pairs=bvh(ob).overlap(bvh(cad[other])); max_v=max((page_face_v[name][a] for a,b in pairs),default=None)
    report['overlaps'][name+'_own_cradle']={'intersecting_face_pairs':len(pairs),'max_page_v':max_v,
             'interpretation':'intentional shallow lower-edge seat only'}
    assert pairs and max_v<.035,(name,'missing contact or unintended intrusion',max_v)
    for cname,cob in cad.items():
        if cname==other:continue
        pairs2=bvh(ob).overlap(bvh(cob)); report['overlaps'][name+'_'+cname]=len(pairs2); assert not pairs2
pair=bvh(pages['Left_Page']).overlap(bvh(pages['Right_Page'])); report['overlaps']['page_page']=len(pair); assert not pair
report['paper_emission_nodes']=sum(1 for n in paper.node_tree.nodes if n.type=='EMISSION')
assert report['paper_emission_nodes']==0
report['compositor_enabled']=S.use_nodes; assert not S.use_nodes
report['external_images']=[im.filepath for im in bpy.data.images if im.source=='FILE']; assert not report['external_images']
report['objects']=len(S.objects); report['source_mesh_sha256']=hashlib.sha256((ROOT/'cad/parts_mesh.json').read_bytes()).hexdigest()
report['render']={'width':S.render.resolution_x,'height':S.render.resolution_y,'samples':S.cycles.samples,'threads':S.render.threads,'device':'CPU','denoising':False,'denoising_note':'Installed Blender build has no OpenImageDenoise support; native samples only'}
(ROOT/'blender_validation.json').write_text(json.dumps(report,indent=2)+'\n')
# Factory startup includes a File Browser pointed at a home directory. Set its
# saved location to this portable project, not the workstation user's home.
for screen in bpy.data.screens:
    for area_ui in screen.areas:
        for space in area_ui.spaces:
            if space.type=='FILE_BROWSER' and space.params:
                # Overwrite the entire fixed-size C buffer before the short
                # relative path; otherwise stale startup-directory bytes remain.
                space.params.directory=b'/'*1023
                space.params.directory=b'//'
S.render.filepath='//renders/'+('draft_02.png' if DRAFT else 'a_page_at_rest_final.png')
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'A_Page_at_Rest.blend'))
S.render.filepath=str(OUT/('draft_02.png' if DRAFT else 'a_page_at_rest_final.png'))
if '--no-render' not in sys.argv:
    bpy.ops.render.render(write_still=True)
    print('PAGE_AT_REST_RENDER_COMPLETE',S.render.filepath)
