"""Fading Shore / 사라지는 해안 — original digital light sculpture.
Blender 4.3+, no assets, no compositor blur, two CPU render threads.
"""
import bpy, math, json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=64; s.cycles.use_denoising=False; s.cycles.transparent_max_bounces=16; s.cycles.max_bounces=8
s.render.threads_mode='FIXED'; s.render.threads=2; s.render.resolution_x=1000; s.render.resolution_y=800; s.render.resolution_percentage=100; s.render.image_settings.file_format='PNG'; s.render.film_transparent=False
s.use_nodes=False; s.view_settings.view_transform='AgX'; s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.73,.81,.9,1); s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.1

def solid(name,color,rough=.7,metal=0):
 m=bpy.data.materials.new(name); m.use_nodes=True; bs=m.node_tree.nodes['Principled BSDF']; bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal; return m
paper=solid('Quiet warm paper',(.72,.68,.57),.94)
n=paper.node_tree.nodes; l=paper.node_tree.links; noise=n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value=180; bump=n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.08; bump.inputs['Distance'].default_value=.008; l.new(noise.outputs['Fac'],bump.inputs['Height']); l.new(bump.outputs[0],n['Principled BSDF'].inputs['Normal'])
bpy.ops.mesh.primitive_plane_add(size=200); floor=bpy.context.object; floor.name='Endless warm paper receiver'; floor.data.materials.append(paper)
f=bpy.data.materials.new('Quiet teal / thin non-refracting filter'); f.use_nodes=True; n=f.node_tree.nodes; n.clear(); l=f.node_tree.links; t=n.new('ShaderNodeBsdfTransparent'); t.inputs['Color'].default_value=(.18,.74,.64,1); d=n.new('ShaderNodeBsdfDiffuse'); d.inputs['Color'].default_value=(.18,.74,.64,1); d.inputs['Roughness'].default_value=.35; mix=n.new('ShaderNodeMixShader'); mix.inputs[0].default_value=.11; l.new(t.outputs[0],mix.inputs[1]); l.new(d.outputs[0],mix.inputs[2]); out=n.new('ShaderNodeOutputMaterial'); l.new(mix.outputs[0],out.inputs[0])
# An open S-shaped strip: centerline rises continuously, never folds back.
# Every cross-section has constant z, with strictly increasing z along t.
# Disjoint cross-sections therefore cannot intersect in 3D.
N=220; vertices=[]; edges=[[],[]]; heights=[]
for i in range(N+1):
 t=i/N; x=-2.85+5.6*t; y=.72*math.sin(2*math.pi*(t-.13))-.05
 dx=5.6; dy=.72*2*math.pi*math.cos(2*math.pi*(t-.13)); length=math.hypot(dx,dy); nx=-dy/length; ny=dx/length
 z=.045+1.7*t**1.65; heights.append(z)
 # Gently taper each end without making a degenerate triangle.
 width=.40+.24*math.sin(math.pi*t)**.8
 for side in [-1,1]:
  co=(x+side*nx*width/2,y+side*ny*width/2,z); vertices.append(co); edges[(side+1)//2].append(co)
faces=[(2*i,2*i+1,2*i+3,2*i+2) for i in range(N)]
mesh=bpy.data.meshes.new('Continuous rising ribbon mesh'); mesh.from_pydata(vertices,[],faces); mesh.update(); ribbon=bpy.data.objects.new('Fading shore / one continuous teal ribbon',mesh); bpy.context.collection.objects.link(ribbon); ribbon.data.materials.append(f)
for face in mesh.polygons: face.use_smooth=True
rim_mat=solid('Hairline teal perimeter',(.12,.32,.27),.5,.1)
# Fine outlines reveal the virtual strip without giving it an opaque metal frame.
perimeter=edges[0]+list(reversed(edges[1])); curve=bpy.data.curves.new('Unbroken shoreline perimeter','CURVE'); curve.dimensions='3D'; curve.bevel_depth=.006; curve.bevel_resolution=3; sp=curve.splines.new('POLY'); sp.points.add(len(perimeter)-1)
for point,co in zip(sp.points,perimeter): point.co=(*co,1)
sp.use_cyclic_u=True; rim=bpy.data.objects.new('Subtle teal edge',curve); bpy.context.collection.objects.link(rim); rim.data.materials.append(rim_mat)
bpy.ops.object.light_add(type='AREA',location=(-1.5,-3.6,6)); light=bpy.context.object; light.name='One broad afternoon'; light.data.shape='DISK'; light.data.size=1.05; light.data.energy=1700; light.data.color=(1,.94,.84); light.rotation_euler=(Vector((0,.3,0))-light.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(5,-8,9)); camera=bpy.context.object; camera.name='Quiet oblique shore'; camera.rotation_euler=(Vector((.1,.6,.15))-camera.location).to_track_quat('-Z','Y').to_euler(); camera.data.type='ORTHO'; camera.data.ortho_scale=9.8; s.camera=camera
s['description']='Fading Shore / 사라지는 해안. A deliberately floating virtual teal ribbon rises above paper; one finite emitter softly spreads its distant colored shadow. No fabrication, spectral glass or quantitative inference claim.'
s['geometry_note']='Strictly monotonic height, nonzero strip width, original continuous open ribbon. No opaque supports: intentionally digital.'
s.render.filepath='//Fading-Shore.png'; bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'Fading-Shore.blend')); s.render.filepath=str(ROOT/'Fading-Shore.png'); bpy.ops.render.render(write_still=True)
# Strip private renderer text/EXIF metadata without changing PNG image/color chunks.
def strip_render_metadata(path):
 raw=path.read_bytes(); assert raw[:8]==b'\x89PNG\r\n\x1a\n'; output=bytearray(raw[:8]); offset=8
 while offset<len(raw):
  length=int.from_bytes(raw[offset:offset+4],'big'); kind=raw[offset+4:offset+8]; chunk=raw[offset:offset+length+12]
  if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf'}: output.extend(chunk)
  offset+=length+12
 assert offset==len(raw); path.write_bytes(output)
strip_render_metadata(ROOT/'Fading-Shore.png')

# Deterministic geometry invariants plus conservative camera-frustum checks.
from bpy_extras.object_utils import world_to_camera_view
projected=[world_to_camera_view(s,camera,Vector(v)) for v in vertices]
report={'blender':bpy.app.version_string,'vertices':len(vertices),'faces':len(faces),'min_height':min(heights),'max_height':max(heights),'strictly_monotonic_section_height':all(a<b for a,b in zip(heights,heights[1:])),'nonzero_faces':all(p.area>1e-8 for p in mesh.polygons),'ribbon_in_camera_frame':all(0<v.x<1 and 0<v.y<1 and v.z>0 for v in projected),'ribbon_camera_bounds':{'x':[min(v.x for v in projected),max(v.x for v in projected)],'y':[min(v.y for v in projected),max(v.y for v in projected)]},'no_compositor':not s.use_nodes,'render_samples':s.cycles.samples,'threads':s.render.threads}
assert report['strictly_monotonic_section_height'] and report['nonzero_faces'] and report['ribbon_in_camera_frame']; (ROOT/'validation.json').write_text(json.dumps(report,indent=2)); print('SHORE_VALIDATION',report)
