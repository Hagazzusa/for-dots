"""Original quiet-neighborhood scene. Blender 4.3+, procedural geometry only."""
import bpy, math, sys, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
PREVIEW='--preview' in sys.argv
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=24 if PREVIEW else 64; s.cycles.use_denoising=False; s.cycles.max_bounces=6
s.render.threads_mode='FIXED'; s.render.threads=2; s.render.resolution_x=640 if PREVIEW else 1100; s.render.resolution_y=520 if PREVIEW else 900; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.view_settings.view_transform='AgX'; s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.38,.51,.72,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35

def mat(name,col,rough=.65,metal=0,emit=0):
 m=bpy.data.materials.new(name); m.use_nodes=True; bs=m.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(*col,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
 if emit: bs.inputs['Emission Color'].default_value=(*col,1); bs.inputs['Emission Strength'].default_value=emit
 return m
plaster=mat('Warm chalk plaster',(.49,.45,.36)); trim=mat('Faded forest green paint',(.075,.18,.16)); cream=mat('Porcelain enamel',(.76,.76,.67),.3); dark=mat('Dark rubber',(.024,.037,.04),.5); drum=mat('Steel drum',(.16,.23,.25),.24,.65); glass=mat('Dark washer porthole',(.035,.09,.11),.13,.3); wood=mat('Weathered honey wood',(.32,.19,.085)); pavement=mat('Stone sidewalk',(.3,.32,.31),.9); asphalt=mat('Muted asphalt',(.11,.14,.16),.92); grout=mat('Floor tiles',(.39,.4,.36)); warm=mat('Warm lamp diffuser',(1,.66,.28),.4,emit=3); textmat=mat('Painted lettering',(.86,.81,.63)); terracotta=mat('Clay pot',(.36,.16,.08)); leaf=mat('Rubber plant leaves',(.075,.16,.07)); towel=mat('Folded blue towel',(.23,.38,.42)); roof=mat('Grey metal roof',(.13,.19,.2),.6,.25)
def box(name,loc,dim,ma,bevel=.025):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); ob=bpy.context.object; ob.name=name; ob.dimensions=dim; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); ob.data.materials.append(ma)
 if bevel: mo=ob.modifiers.new('Soft edges','BEVEL'); mo.width=bevel; mo.segments=3; ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return ob

def cyl(name,loc,r,depth,ma,rot=(math.pi/2,0,0),verts=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=verts,radius=r,depth=depth,location=loc,rotation=rot); ob=bpy.context.object; ob.name=name; ob.data.materials.append(ma); mo=ob.modifiers.new('Edge rounding','BEVEL'); mo.width=.01; mo.segments=3; ob.modifiers.new('Normals','WEIGHTED_NORMAL'); return ob

def text(name,body,loc,size,ma):
 cu=bpy.data.curves.new(name,'FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=.001; ob=bpy.data.objects.new(name,cu); bpy.context.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(math.pi/2,0,0); ob.data.materials.append(ma); return ob
# Coherent building shell. Units approximate metres; door is 2.15 high.
box('Street',(0,0,-.13),(200,200,.2),asphalt)
box('Raised sidewalk',(0,.5,.0),(9,6,.18),pavement,.04)
for x in range(-4,5): box('Paving joint',(x,-1.2,.096),(.012,2.5,.003),asphalt,.001)
for y in [-2.1,-1.25,-.4]: box('Paving cross joint',(0,y,.097),(8.9,.012,.003),asphalt,.001)
box('Shop floor',(0,1.6,.15),(6,3.2,.12),grout)
box('Rear wall',(0,3.1,1.75),(6,.18,3.2),plaster)
box('Left wall',(-2.95,1.55,1.75),(.18,3.3,3.2),plaster)
box('Right wall',(2.95,1.55,1.75),(.18,3.3,3.2),plaster)
box('Front left pier',(-2.85,-.01,1.72),(.3,.2,3.15),plaster)
box('Door divider',(.95,-.01,1.4),(.22,.22,2.6),trim)
box('Right door pier',(2.75,-.01,1.72),(.4,.2,3.15),plaster)
box('Window low wall',(-.95,-.01,.29),(3.5,.2,.16),trim)
box('Facade upper band',(0,-.01,2.88),(6,.22,.7),plaster)
# Store window is optically clear/open in this stylized render: no opaque fake glass.
for x in [-2.65,.77]: box('Window side frame',(x,-.15,1.45),(.065,.08,2.12),trim,.008)
for z in [.39,2.51]: box('Window horizontal frame',(-.94,-.15,z),(3.48,.08,.065),trim,.008)
for x in [-1.565,-.435]: box('Window slender mullion',(x,-.15,1.45),(.04,.07,2.12),trim,.008)
for x in [1.15,2.54]: box('Door frame',(x,-.15,1.27),(.08,.08,2.2),trim,.008)
box('Door top',(1.845,-.15,2.37),(1.47,.08,.08),trim,.008)
box('Door lower panel',(1.845,-.13,.58),(1.32,.075,.78),trim,.01)
box('Door upper rail',(1.845,-.13,1.0),(1.32,.07,.05),trim,.008)
box('Door handle',(2.34,-.23,1.23),(.035,.06,.26),textmat,.012)
box('Entry step',(1.85,-.45,.16),(1.7,.68,.14),pavement,.03)
box('Roof slab',(0,1.55,3.38),(6.4,3.65,.16),roof,.035)
box('Roof fascia',(0,-.35,3.24),(6.48,.14,.2),trim,.015)
box('Shop sign',(-.85,-.15,2.88),(3.55,.09,.43),trim,.025); text('Sign lettering','SLOW WASH',(-.85,-.205,2.88),.24,textmat)
# Identically scaled front-load washers: 0.86 wide, 1.05 high, visibly inside window.
for i,x in enumerate([-2.13,-1.0,.13]):
 box(f'Washer {i+1} body',(x,.67,.755),(.88,.82,1.08),cream,.055)
 box('Washer control strip',(x,.235,1.13),(.76,.035,.16),trim,.012)
 cyl('Selector knob',(x+.23,.2,1.14),.045,.025,cream)
 box('Small status light',(x-.24,.208,1.15),(.1,.008,.025),warm,.004)
 cyl('Porthole rubber',(x,.215,.7),.315,.065,dark)
 cyl('Porthole steel rim',(x,.17,.7),.285,.045,drum)
 cyl('Porthole dark centre',(x,.14,.7),.232,.025,glass)
 # A small inner crescent and rim catch give circular doors depth.
 bpy.ops.mesh.primitive_torus_add(major_radius=.237,minor_radius=.014,major_segments=48,minor_segments=10,location=(x,.112,.7),rotation=(math.pi/2,0,0)); bpy.context.object.data.materials.append(cream)
 box('Porthole grip',(x+.235,.085,.72),(.05,.045,.16),dark,.015)
box('Back folding counter',(0,2.4,1.05),(4.8,.65,.10),wood)
for x in [-2,2]: box('Counter legs',(x,2.4,.6),(.08,.5,.9),trim)
for i in range(3): box('Folded towel',(.75,2.4,1.14+i*.055),(.65,.38,.05),towel,.025)
# Side bench: human seat height 0.46, two-person length 1.7, facing the side lane.
for y in [.65,1.95]:
 for x in [3.35,3.73]: box('Bench legs',(x,y,.32),(.065,.065,.45),trim,.01)
for x in [3.3,3.48,3.66]: box('Bench seat slat',(x,1.3,.56),(.15,1.75,.065),wood,.015)
for y in [.65,1.95]: box('Bench back upright',(3.2,y,.76),(.055,.055,.72),trim,.009)
for z in [.85,1.04]: box('Bench back slat',(3.19,1.3,z),(.07,1.75,.14),wood,.015)
# Plant at left storefront, kept below the sign and clear of the doorway.
cyl('Terracotta pot',(-3.35,-.35,.39),.25,.57,terracotta,rot=(0,0,0))
for i in range(7):
 a=i*2.4; z=.7+i*.07; x=-3.35+.21*math.cos(a); y=-.35+.21*math.sin(a)
 bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,location=(x,y,z)); ob=bpy.context.object; ob.name='Simple plant leaf'; ob.scale=(.2,.085,.045); ob.rotation_euler=(.35,0,a); ob.data.materials.append(leaf)
# A wall clock and single overhead strip make the interior legible without clutter.
cyl('Interior wall clock',(-1.6,3.0,2.5),.23,.035,cream); box('Clock minute hand',(-1.6,2.97,2.56),(.014,.01,.14),trim,.002); box('Clock hour hand',(-1.54,2.965,2.5),(.13,.01,.014),trim,.002)
box('Ceiling lamp housing',(0,1.3,3.05),(3,.23,.08),trim); box('Ceiling lamp glow',(0,1.3,3.0),(2.9,.19,.025),warm,.01)
bpy.ops.object.light_add(type='AREA',location=(0,1.0,2.9)); light=bpy.context.object; light.name='Warm interior'; light.data.energy=170; light.data.shape='RECTANGLE'; light.data.size=3; light.data.size_y=1.3; light.data.color=(1,.76,.48)
bpy.ops.object.light_add(type='AREA',location=(-3,-5,7)); light=bpy.context.object; light.name='Soft evening sky'; light.data.energy=550; light.data.size=7; light.data.color=(.65,.79,1); light.rotation_euler=(Vector((0,1,1))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.light_add(type='AREA',location=(6,-3,5)); light=bpy.context.object; light.name='Gentle side fill'; light.data.energy=140; light.data.size=5; light.data.color=(.7,.8,1); light.rotation_euler=(Vector((2,1,1))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(7.2,-11.5,4.5)); camera=bpy.context.object; camera.name='Street eye / three quarter'; camera.rotation_euler=(Vector((.15,.7,1.35))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=11.8; camera.location += (camera.location-Vector((.15,.7,1.35))).normalized()*20; camera.data.clip_end=250; s.camera=camera
s['scene_scale']='Approximate metres; entry 2.15 high, washers 1.08 high, bench seat 0.46 above pavement.'
# Clear unused sequencer UI history; this still scene has no strips.
if s.sequence_editor is not None and not s.sequence_editor.sequences_all: s.sequence_editor_clear()
# Clear inherited file-browser directories before saving a public scene.
for screen in bpy.data.screens:
 for area in screen.areas:
  for space in area.spaces:
   if space.type=='FILE_BROWSER' and space.params is not None:
    space.params.directory=b'/'*1023  # Clear stale bytes beyond the C string terminator.
    space.params.directory=b'//'
s.render.filepath='//Quiet-Laundrette.png'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Quiet-Laundrette.blend')); s.render.filepath=str(ROOT/('preview.png' if PREVIEW else 'Quiet-Laundrette.png')); bpy.ops.render.render(write_still=True)
# Remove renderer path/date metadata; preserve PNG pixel/color chunks.
p=Path(s.render.filepath); raw=p.read_bytes(); result=bytearray(raw[:8]); off=8
while off<len(raw):
 length=int.from_bytes(raw[off:off+4],'big'); kind=raw[off+4:off+8]
 if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'oFFs'}: result.extend(raw[off:off+length+12])
 off+=length+12
p.write_bytes(result)
(ROOT/'validation.json').write_text(json.dumps({'blender':bpy.app.version_string,'objects':len(s.objects),'threads':2,'samples':s.cycles.samples,'preview':PREVIEW,'external_images':len([i for i in bpy.data.images if i.filepath]),'camera_orthographic':True},indent=2))
