import bpy, math, os
from mathutils import Vector
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0,rough=.4,emission=0,alpha=1):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,alpha); m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,alpha); p.inputs['Metallic'].default_value=metal; p.inputs['Roughness'].default_value=rough
 if emission: p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
 if alpha<1:
  p.inputs['Alpha'].default_value=alpha
  m.surface_render_method='DITHERED'
 return m
teal=mat('Powder coated petrol steel',(.035,.16,.18),.6,.28)
edge=mat('Roof dark teal edge',(.025,.075,.09),.65,.24)
cream=mat('Warm cream enamel',(.66,.66,.51),.35,.35)
wood=mat('Honey cedar',(.43,.22,.085),0,.38)
wood2=mat('Cedar light grain',(.55,.32,.13),0,.4)
glass=mat('Smoked blue glass',(.10,.24,.28),.1,.18,0,.34)
light=mat('Warm shelter light', (1,.61,.23),0,.3,4)
display=mat('Vending soft cool illumination',(.45,.82,.74),0,.3,2.2)
black=mat('Dark recess',(.014,.025,.03),.15,.5)
orange=mat('Tangerine soda',(.9,.22,.055),.2,.3)
red=mat('Berry soda',(.56,.055,.09),.2,.3)
green=mat('Matcha soda',(.27,.46,.25),.2,.3)
silver=mat('Brushed aluminum',(.5,.58,.58),.8,.3)
def conv(v): return (v[0],-v[2],v[1])
def box(n,p,s,m,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=conv(p)); o=bpy.context.object; o.name=n; o.dimensions=(s[0],s[2],s[1]); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(m)
 if bevel:
  mod=o.modifiers.new('Soft manufactured edges','BEVEL'); mod.width=bevel; mod.segments=2
  o.modifiers.new('Corner normals','WEIGHTED_NORMAL')
 return o
def cyl(n,p,r,h,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=h,location=conv(p));o=bpy.context.object;o.name=n;o.data.materials.append(m);o.modifiers.new('Corner normals','WEIGHTED_NORMAL');return o
# Broad flat roof with rain gutter and warm recessed fixtures.
box('Floating roof cap',(0,3.12,0),(7.1,.18,2.7),edge,.045)
box('Cream soffit',(0,3.01,0),(6.87,.10,2.48),cream,.025)
box('Front gutter',(0,3.10,1.38),(7.18,.19,.09),teal,.02)
for x in [-3.2,3.2]:
 for z in [-1,1]:
  box('Steel column',(x,1.48,z),(.10,2.96,.10),teal,.012)
  box('Column foot',(x,.035,z),(.23,.07,.23),edge,.015)
  for dx in [-.075,.075]:
   cyl('Anchor bolt',(x+dx,.08,z),.017,.015,silver)
for x in [-2.1,0,2.1]:
 box('Ceiling light housing',(x,2.93,0),(1.08,.075,.24),edge,.025)
 box('Warm light diffuser',(x,2.88,0),(1.0,.025,.18),light,.015)
# Back wall split glazing, usable clear shelter front.
for x in [-2.13,0,2.13]:
 box('Rear lower panel',(x,.48,-1.02),(2.05,.78,.055),teal,.015)
 box('Rear glass',(x,1.85,-1.02),(2.05,1.84,.028),glass)
for x in [-3.2,-1.065,1.065,3.2]: box('Rear mullion',(x,1.48,-1.04),(.065,2.9,.075),teal,.01)
box('Rear top rail',(0,2.91,-1.04),(6.5,.07,.075),teal,.01)
box('Rear middle rail',(0,.91,-1.04),(6.5,.065,.075),teal,.01)
# Small protective side glass on left.
box('Left side smoked glass',(-3.2,1.65,-.05),(.025,2.30,1.80),glass)
box('Left side low rail',(-3.2,.48,-.05),(.08,.08,1.9),teal,.01)
# Bench slats and friendly rounded edges.
for x in [-2.25,.25]:
 box('Bench leg',(x,.27,-.43),(.09,.54,.50),teal,.02)
 box('Bench foot',(x,.065,-.43),(.48,.09,.55),edge,.02)
 box('Back support',(x,.84,-.70),(.07,.75,.07),teal,.012)
for i in range(4): box('Cedar seat slat',(-1,.57,-.65+i*.15),(3.3,.095,.125),wood if i%2 else wood2,.022)
for i in range(3): box('Cedar back slat',(-1,.83+i*.145,-.74),(3.3,.115,.07),wood if i%2 else wood2,.018)
for x in [-2.6,.6]:
 box('Armrest riser',(x,.70,-.46),(.06,.25,.06),teal,.018)
 box('Armrest',(x,.83,-.43),(.09,.06,.54),teal,.025)
# Nostalgic vending machine, front faces positive Godot Z.
box('Vending enamel cabinet',(2.2,1.10,-.20),(1.22,2.2,.82),cream,.06)
box('Vending teal fascia',(2.2,1.10,.225),(1.12,2.06,.055),teal,.035)
box('Vending glowing drink window',(2.03,1.40,.267),(.69,1.12,.025),display,.035)
box('Vending header light',(2.2,2.02,.27),(.98,.16,.025),light,.018)
box('Payment recess',(2.65,1.39,.272),(.23,.82,.03),black,.018)
box('Payment small screen',(2.65,1.64,.295),(.16,.10,.02),display,.006)
box('Coin slot',(2.65,1.44,.296),(.08,.018,.012),silver)
for yy in [1.32,1.20]:
 box('Selection button',(2.65,yy,.298),(.105,.055,.02),cream,.01)
box('Collection opening',(2.2,.40,.272),(.88,.27,.04),black,.035)
box('Collection lip',(2.2,.27,.31),(.88,.045,.13),silver,.012)
for yy in [1.05,1.36,1.67]:
 box('Drink shelf',(2.03,yy-.10,.32),(.65,.025,.12),silver,.004)
 for idx,xx in enumerate([1.82,2.03,2.24]):
  cyl('Soda can',(xx,yy,.32),.064,.19,[orange,green,red][idx])
  cyl('Can top',(xx,yy+.098,.32),.061,.01,silver)
  box('Can label',(xx,yy,.384),(.075,.055,.005),cream,.005)
for x in [1.72,2.68]: box('Vending rubber foot',(x,.04,-.2),(.12,.08,.6),black,.01)
# Roof route sign housing (text supplied in engine).
box('Route sign panel',(-1.25,2.66,1.04),(3.45,.35,.10),teal,.025)
box('Route sign cream face',(-1.25,2.66,1.096),(3.31,.25,.014),cream,.012)
# Original asset metadata in Blender.
bpy.context.scene['description']='Original procedural rainy night shelter, cedar bench and illuminated vending machine. Godot axes: Y up, front +Z.'
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'art','shelter.blend'))
bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'assets','shelter.glb'),export_format='GLB',export_yup=True,export_apply=True)
print('ASSET_DONE',os.path.join(ROOT,'assets','shelter.glb'))
