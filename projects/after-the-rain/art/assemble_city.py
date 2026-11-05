"""Original assembly of Poly Haven CC0 modular urban apartment facade.
Source: https://polyhaven.com/a/modular_urban_apartments_facade
License: https://polyhaven.com/license (CC0). No downloaded executable code.
"""
import bpy, os, math, random
from mathutils import Vector, Matrix
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.abspath(os.path.join(ROOT,'../city_asset_sources/modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=SRC)
sources={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
for o in sources.values(): o.hide_render=True;o.hide_set(True)
def simple_mat(name, color, emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.34;p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission;return m
warm=simple_mat('Occupied warm amber window',(.72,.32,.095),1.8)
soft=simple_mat('Occupied pale warm window',(.49,.43,.27),1.2)
dark=simple_mat('Unlit opaque blue window',(.018,.031,.044))
roofmat=simple_mat('Slate roof membrane',(.045,.052,.055))
metal=simple_mat('Roof vent zinc',(.12,.15,.16))
all_models=[]
def build(variant):
 made=[];rng=random.Random(18+variant)
 def instance(name, center, z, rot, width=2.1):
  src=sources[name];o=src.copy();o.data=src.data.copy();bpy.context.collection.objects.link(o);o.name=f'{variant}_{name}';o.hide_render=False;o.hide_set(False)
  # Imported mesh local coords span x -3..0; normalize bay center.
  o.matrix_world=Matrix.Translation(Vector((center[0],center[1],z))) @ Matrix.Rotation(rot,4,'Z') @ Matrix.Diagonal((width/3,1,1,1)) @ Matrix.Translation(Vector((1.5,0,0)))
  for i,m in enumerate(o.data.materials):
   if 'glass' in m.name:o.data.materials[i]=rng.choice([dark,dark,warm,soft])
  made.append(o);return o
 def cube(name,p,s,m):
  bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.dimensions=s;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(m);made.append(o);return o
 W,D=6.3,4.3
 faces=[((0,-D/2),0,W,3),((0,D/2),math.pi,W,3),((W/2,0),math.pi/2,D,2),((-W/2,0),-math.pi/2,D,2)]
 for fi,(origin,rot,length,bays) in enumerate(faces):
  bw=length/bays
  for i in range(bays):
   off=(i+.5)*bw-length/2;center=(origin[0]+math.cos(rot)*off,origin[1]+math.sin(rot)*off)
   for floor in range(3):
    door=(fi==0 and i==1 and floor==0)
    typ='small' if variant==0 else 'large'
    # Large windows retain architectural surrounds but are horizontally fitted.
    suffix=f'centered_{typ}_0{1+(floor+variant)%3}'
    if door:
     instance('wall_door_centered_small_01',center,0,rot,bw);instance('door_centered_small_01',center,0,rot,bw)
    else:
     instance('wall_window_'+suffix,center,floor*3,rot,bw);instance('window_'+suffix,center,floor*3,rot,bw)
    if floor>0:instance('cornice_standard_standard_01',center,floor*3-.10,rot,bw)
   instance('crown_standard_standard_01',center,9,rot,bw)
   if not (fi==0 and i==1):instance('dado_standard_standard_01',center,0,rot,bw)
 # Closed slabs and deliberately inset backing; walls remain textured kit geometry.
 plaster=bpy.data.materials['modular_urban_apartments_facade_plaster']
 cube('Closed internal masonry', (0,0,4.5),(W-.8,D-.8,9),plaster)
 cube('Flat dark roof',(0,0,9.03),(W,D,.10),roofmat)
 cube('Roof access housing',(-1,.5,9.40),(1.20,1.1,.7),plaster)
 cube('Roof access cap',(-1,.5,9.78),(1.35,1.24,.09),metal)
 for x in [1,1.65]:cube('Ventilator',(x,.45,9.28),(.35,.48,.4),metal)
 # Second building plaster is subtly cooler. Preserve original image textures.
 if variant:
  tint=plaster.copy();tint.name='Cool stone plaster variation'
  for o in made:
   for i,m in enumerate(o.data.materials):
    if m==plaster:o.data.materials[i]=tint
  p=tint.node_tree.nodes.get('Principled BSDF'); inp=p.inputs['Base Color']
  if inp.is_linked:
   old=inp.links[0].from_socket;tint.node_tree.links.remove(inp.links[0]);mix=tint.node_tree.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=1;mix.inputs[2].default_value=(.72,.83,.88,1);tint.node_tree.links.new(old,mix.inputs[1]);tint.node_tree.links.new(mix.outputs[0],inp)
 # Material-merge: eight or nine mesh surfaces rather than hundreds of draw nodes.
 bpy.ops.object.select_all(action='DESELECT')
 for o in made:o.select_set(True)
 bpy.context.view_layer.objects.active=made[0];bpy.ops.object.convert(target='MESH');bpy.ops.object.join();obj=bpy.context.object;obj.name='Apartment_A' if not variant else 'Apartment_B'
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 # Join may preserve duplicate slots. Deduplicate them and retain exact per-face assignments.
 unique=[];mapping={}
 for i,m in enumerate(obj.data.materials):
  if m not in unique:unique.append(m)
  mapping[i]=unique.index(m)
 indices=[mapping[p.material_index] for p in obj.data.polygons];obj.data.materials.clear()
 for m in unique:obj.data.materials.append(m)
 for p,idx in zip(obj.data.polygons,indices):p.material_index=idx
 bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'assets/city/apartment_'+('a' if not variant else 'b')+'.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
 pts=[obj.matrix_world@Vector(v) for v in obj.bound_box];print('FINAL_BOUNDS',obj.name,[[round(f(v[i] for v in pts),3) for i in range(3)] for f in [min,max]],'materials',len(unique),'vertices',len(obj.data.vertices))
 all_models.append(obj);obj.hide_set(True);obj.hide_render=True
os.makedirs(os.path.join(ROOT,'assets/city'),exist_ok=True)
build(0);build(1)
# Remove unused kit layout but preserve assembled texture dependencies packed in blend.
for o in sources.values():bpy.data.objects.remove(o,do_unlink=True)
for i,o in enumerate(all_models):o.hide_set(False);o.hide_render=False;o.location.x+=i*9
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'art/city_assembly.blend'))
