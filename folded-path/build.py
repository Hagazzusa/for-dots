"""Folded Path: original hinged-paper visual study; Blender 4.3+."""
import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
N=6; WIDTHS=[0.8]*N; DEPTH=1.8; FRAMES=48

def angle(frame):
    # Closed hold, smooth opening, open hold, smooth closing; periodic seam.
    t=(frame-1)%48
    if t<4: q=0
    elif t<20: q=(1-math.cos(math.pi*(t-4)/16))/2
    elif t<28:q=1
    elif t<44:q=(1+math.cos(math.pi*(t-28)/16))/2
    else:q=0
    return math.radians(66-44*q)

def pose(frame):
    a=angle(frame); p=[(0.,0.)]
    for i,w in enumerate(WIDTHS):
        s=a*(-1 if i%2 else 1);x,z=p[-1];p.append((x+w*math.cos(s),z+w*math.sin(s)))
    return p

def verify():
    errs=[]; minimum=100
    for f in range(1,49):
        p=pose(f)
        assert all(math.isfinite(v) for t in p for v in t)
        for i,w in enumerate(WIDTHS):
            err=abs(math.dist(p[i],p[i+1])-w);errs.append(err);assert err<1e-12
        # Each panel occupies a disjoint X slab; this is a sufficient nonintersection
        # proof for this extrusion, not a general collision engine.
        assert all(p[i+1][0]>p[i][0] for i in range(N))
        for i in range(N):
            for j in range(i+2,N):
                gap=p[j][0]-p[i+1][0];minimum=min(minimum,gap);assert gap>0
    report={'sampled_frames':48,'panel_widths':WIDTHS,'maximum_length_error':max(errs),'minimum_nonadjacent_x_gap':minimum,'finite_poses':True,'shared_hinge_edges':'analytic endpoint chain, Y edges identical','limits':'Zero-thickness idealized hinged patches; no elasticity, thickness collision or fabrication validation.'}
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    return report

def material(name,color):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=.82
    return m

def aim(o,p):o.rotation_euler=(Vector(p)-o.location).to_track_quat('-Z','Y').to_euler()

def build():
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    for x in list(bpy.data.materials):bpy.data.materials.remove(x)
    paper=material('Warm ivory paper',(.76,.69,.54));ink=material('Muted teal pigment',(.025,.19,.18));ground=material('Oatmeal desk',(.34,.29,.235))
    base=bpy.data.objects.new('Centered accordion',None);bpy.context.collection.objects.link(base);base.location.z=.025
    parent=base; hinges=[]
    for i,w in enumerate(WIDTHS):
        h=bpy.data.objects.new('Hinge %02d'%i,None);bpy.context.collection.objects.link(h);h.parent=parent
        h.location.x=0 if i==0 else WIDTHS[i-1];hinges.append(h);parent=h
        verts=[];faces=[]
        for j in range(41):
            x=w*j/40;s=sum(WIDTHS[:i])+x
            y=.30*math.sin(s*1.55-.8)+.08*math.sin(s*3.2)
            for yy in [-DEPTH/2,y-.028,y+.028,DEPTH/2]:verts.append((x,yy,0))
        for j in range(40):
            for k in range(3):a=j*4+k;faces.append((a,a+4,a+5,a+1))
        mesh=bpy.data.meshes.new('Surface patch %02d'%i);mesh.from_pydata(verts,[],faces);mesh.materials.append(paper);mesh.materials.append(ink)
        obj=bpy.data.objects.new('Paper panel %02d'%i,mesh);bpy.context.collection.objects.link(obj);obj.parent=h
        for j,poly in enumerate(mesh.polygons):poly.material_index=1 if j%3==1 else 0
    for f in range(1,50):
        a=angle(f);base.location.x=-pose(f)[-1][0]/2;base.keyframe_insert('location',frame=f)
        for i,h in enumerate(hinges):
            slope=a*(-1 if i%2 else 1);previous=0 if i==0 else -slope
            h.rotation_euler.y=-(slope-previous);h.keyframe_insert('rotation_euler',frame=f)
    for obj in [base]+hinges:
        for fc in obj.animation_data.action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
    bpy.ops.mesh.primitive_plane_add(size=200);bpy.context.object.name='Infinite warm desk';bpy.context.object.data.materials.append(ground)
    bpy.ops.object.camera_add(location=(5,-7.5,5.2));cam=bpy.context.object;aim(cam,(0,0,.25));cam.data.type='ORTHO';cam.data.ortho_scale=6.45;bpy.context.scene.camera=cam;cam.data.lens=48
    bpy.ops.object.light_add(type='AREA',location=(-3,-4,6));key=bpy.context.object;key.name='Large warm window';key.data.energy=500;key.data.shape='DISK';key.data.size=4;key.data.color=(1,.88,.72);aim(key,(0,0,0))
    scene=bpy.context.scene;scene.world.color=(.23,.23,.23);scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=64;scene.cycles.use_denoising=False
    scene.render.threads_mode='FIXED';scene.render.threads=2;scene.render.resolution_x=800;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.fps=12;scene.frame_start=1;scene.frame_end=48;scene.view_settings.view_transform='AgX'
    scene.render.use_stamp=False;scene.frame_set(24)
    scene['Study']='Folded Path / 접힌 길';scene['Model']='Six zero-thickness rigid patches with coincident full hinge edges; idealized kinematics, not fabrication proof.'
    # Verify evaluated Blender transforms as well as analytic chain.
    closure=0.;normal_error=0.
    for f in range(1,49):
        scene.frame_set(f);bpy.context.view_layer.update()
        for i in range(N-1):
            for y in [-DEPTH/2,DEPTH/2]:
                u=hinges[i].matrix_world@Vector((WIDTHS[i],y,0));v=hinges[i+1].matrix_world@Vector((0,y,0));closure=max(closure,(u-v).length)
    assert closure<1e-5
    report=verify();report['maximum_blender_hinge_closure_error']=closure
    (ROOT/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    scene.render.filepath='//frames/frame_';scene.frame_set(24);bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'folded_path.blend'),compress=True)
    return scene

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    scene=build()
    if '--still' in args:scene.render.filepath=str(ROOT/'folded_path.png');bpy.ops.render.render(write_still=True)
    if '--loop' in args:
        scene.render.resolution_x=480;scene.render.resolution_y=384;scene.cycles.samples=16;scene.render.filepath=str(ROOT/'frames'/'frame_');bpy.ops.render.render(animation=True)
