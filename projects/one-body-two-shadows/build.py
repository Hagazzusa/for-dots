"""One connected body, two orthogonal silhouettes. Original profile/intersection study."""
import bpy,bmesh,math,json,sys
from pathlib import Path
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
P=Path(__file__).resolve().parent
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
MODE=args[0] if args else 'probe';FORM=args[1] if len(args)>1 else 'hollow';assert MODE in ['probe','final'] and FORM in ['solid','hollow']
N=192
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32 if MODE=='probe' else 512;s.cycles.use_denoising=False;s.cycles.use_auto_tile=True;s.cycles.tile_size=256;s.cycles.adaptive_threshold=.008;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=3
s.render.resolution_x=960 if MODE=='probe' else 1600;s.render.resolution_y=720 if MODE=='probe' else 1200;s.render.resolution_percentage=100;s.render.threads_mode='FIXED';s.render.threads=6;s.render.image_settings.file_format='PNG';s.render.film_transparent=False
s.view_settings.view_transform='AgX';s.view_settings.look='AgX - Medium High Contrast';s.view_settings.exposure=-.25
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.83,.88,1,1);s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.10

def material(name,color,rough):
 m=bpy.data.materials.new(name);m.use_nodes=True;bs=m.node_tree.nodes['Principled BSDF'];bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Roughness'].default_value=rough;return m
clay=material('Warm red body',(.32,.085,.04),.58)
wallmat=material('Pale matte walls',(.70,.68,.62),.88)
floormat=material('Grey warm floor',(.44,.43,.39),.9)
def clean(o):
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-7);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-8);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if bm.calc_volume(signed=True)<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
def prism(name,points,axis,depth):
 n=len(points);vs=[]
 for v in [-depth,depth]:
  vs.extend([(u,v,z) if axis=='Y' else (v,u,z) for u,z in points])
 fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):fs.append((i,(i+1)%n,n+(i+1)%n,n+i))
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(clay);clean(o);return o
def boolean(a,b,operation):
 bpy.context.view_layer.objects.active=a;a.select_set(True)
 mod=a.modifiers.new(operation,'BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=b;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(b,do_unlink=True);clean(a)
house=prism('Shared body',[(-1,0),(1,0),(1,1.9),(0,2.8),(-1,1.9)],'Y',2.3)
r=.22;xc=-.32;zc=.72;door=[(xc-r,-.2),(xc+r,-.2)]+[(xc+r*math.cos(math.pi*i/64),zc+r*math.sin(math.pi*i/64)) for i in range(65)]
boolean(house,prism('Arch doorway',door,'Y',2.5),'DIFFERENCE')
boolean(house,prism('Square window',[(.27,1.25),(.63,1.25),(.63,1.61),(.27,1.61)],'Y',2.5),'DIFFERENCE')
tree=prism('Tree profile',[(-.18,0),(.18,0),(.18,1.5),(-.18,1.5)],'X',2.3)
ellipses=[(-.35,1.8,.72,.70),(.32,1.95,.69,.85),(0,2.35,.55,.45)]
for k,(cy,cz,ry,rz) in enumerate(ellipses):
 pts=[(cy+ry*math.cos(2*math.pi*i/N),cz+rz*math.sin(2*math.pi*i/N)) for i in range(N)]
 boolean(tree,prism(f'Crown lobe {k}',pts,'X',2.3),'UNION')
if FORM=='hollow':
 tree_copy=tree.copy();tree_copy.data=tree.data.copy();bpy.context.collection.objects.link(tree_copy)
boolean(house,tree,'INTERSECT');house.name='Shared body';clean(house)
if FORM=='hollow':
 cut=house.copy();cut.data=house.data.copy();bpy.context.collection.objects.link(cut);cut.name='Translated interior'
 fill=prism('Recess internal ledge',[(.27,1.25),(.63,1.25),(.63,1.61),(.27,1.61)],'Y',2.3)
 boolean(fill,tree_copy,'INTERSECT')
 boolean(cut,fill,'UNION');cut.location=(-.18,-.18,0)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,2.625));limit=bpy.context.object;limit.name='Preserve lower body';limit.dimensions=(8,8,2.75);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 boolean(cut,limit,'INTERSECT');boolean(house,cut,'DIFFERENCE')
# Native mesh checks before aesthetic edge softening.
bm=bmesh.new();bm.from_mesh(house.data);bm.verts.ensure_lookup_table();unseen=set(bm.verts);components=[]
while unseen:
 stack=[unseen.pop()];count=0
 while stack:
  v=stack.pop();count+=1
  for e in v.link_edges:
   u=e.other_vert(v)
   if u in unseen:unseen.remove(u);stack.append(u)
 components.append(count)
nonmanifold=sum(not e.is_manifold for e in bm.edges);vol=bm.calc_volume(signed=True)
assert len(components)==1 and nonmanifold==0 and vol>0,(components,nonmanifold,vol)
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(house.data);bm.free()
# Smooth the curved profile sides while preserving planar and architectural edges.
for poly in house.data.polygons:poly.use_smooth=True
bev=house.modifiers.new('Small edge radii','BEVEL');bev.width=.006;bev.segments=3
weighted=house.modifiers.new('Weighted surface normals','WEIGHTED_NORMAL');weighted.keep_sharp=True;weighted.weight=30
# Room surfaces extend beyond the camera; no decorative frames or painted shadows.
def surface(name,verts,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],[(0,1,2,3)]);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
surface('House receiving wall',[(-10,3,-.01),(3,3,-.01),(3,3,8),(-10,3,8)],wallmat)
surface('Tree receiving wall',[(3,3,-.01),(3,-10,-.01),(3,-10,8),(3,3,8)],wallmat)
surface('Floor',[(-15,-15,0),(15,-15,0),(15,15,0),(-15,15,0)],floormat)
for name,rot,energy,color in [('House direction',(math.pi/2,0,0),2.5,(1,.88,.74)),('Tree direction',(0,-math.pi/2,0),2.0,(.77,.88,1))]:
 bpy.ops.object.light_add(type='SUN');o=bpy.context.object;o.name=name;o.rotation_euler=rot;o.data.energy=energy;o.data.angle=.008;o.data.color=color
bpy.ops.object.camera_add(location=(-7,-9,6.3));cam=bpy.context.object;cam.name='Two shadows camera';target=Vector((.8,.8,1.45));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=9.2;s.camera=cam
bpy.context.view_layer.update();coords=[world_to_camera_view(s,cam,house.matrix_world@v.co) for v in house.data.vertices];margin=min(min(v.x,1-v.x,v.y,1-v.y) for v in coords)
qa={'mode':MODE,'form':FORM,'hollow_offset':[-.18,-.18,0] if FORM=='hollow' else None,'solid_below_z':1.25 if FORM=='hollow' else None,'mesh_vertices':len(house.data.vertices),'mesh_triangles':len(house.data.polygons),'connected_components':len(components),'nonmanifold_edges':nonmanifold,'signed_volume_before_bevel':vol,'body_frame_margin':margin,'base_z_range':[min(v.co.z for v in house.data.vertices),max(v.co.z for v in house.data.vertices)],'bevel_width':.006,'profiles':{'house':{'half_width':1,'wall_top':1.9,'roof_top':2.8,'door_center':xc,'door_radius':r,'door_spring_height':zc,'window':[.27,.63,1.25,1.61]},'tree':{'trunk_half_width':.18,'trunk_top':1.5,'ellipses':ellipses}},'lighting':'Two orthogonal horizontal directional lights; all wall shapes are cast shadows.'}
(P/'geometry-qa.json').write_text(json.dumps(qa,indent=2)+'\n');bpy.ops.wm.save_as_mainfile(filepath=str(P/'One-Body-Two-Shadows.blend'));print(json.dumps(qa,indent=2))
