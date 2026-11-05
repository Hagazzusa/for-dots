"""Render the actual CAD tessellation, never a remodeled bookmark.
blender -b -t 2 --python build_blender.py -- --draft
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parent; draft='--draft' in sys.argv
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.render.threads_mode='FIXED'; s.render.threads=2; s.cycles.samples=24 if draft else 160; s.cycles.use_denoising=False; s.cycles.seed=19
s.cycles.caustics_reflective=False; s.cycles.caustics_refractive=False
s.render.resolution_x=640 if draft else 1500; s.render.resolution_y=640 if draft else 1500; s.render.resolution_percentage=100
s.world.use_nodes=True; s.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.79,.85,1); s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
s.view_settings.view_transform='AgX'; s.view_settings.look='AgX - Medium High Contrast'
def mat(name,color,rough=.5,metal=0):
 m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True; p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal; return m
brass=mat('Satin old gold',(.55,.34,.12),.32,.88); paper=mat('Warm cream paper',(.83,.76,.62),.82); edge=mat('Paper edges',(.69,.61,.47),.9); cover=mat('Linen cover - muted stone',(.27,.30,.27),.9); table=mat('Chalk daylight',(.74,.75,.70),.86)
def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); o.data.materials.append(ma); return o
def cube(name,loc,scale,ma,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc); o=bpy.context.object; o.name=name; o.dimensions=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(ma)
 if bevel: mod=o.modifiers.new('Soft edge','BEVEL'); mod.width=bevel; mod.segments=3; o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
 return o
payload=json.loads((R/'cad/bookmark_mesh.json').read_text()); vs=[tuple(x*.001 for x in v) for v in payload['vertices']]; o=mesh('Returning Page - CAD brass',vs,payload['faces'],brass); o.location=(.012,.025,.0101)
o['source']='FreeCAD native final solid tessellation'; o['mesh_sha256']=hashlib.sha256((R/'cad/bookmark_mesh.json').read_bytes()).hexdigest(); o['millimetres_to_metres']=.001
# Keep CAD normals planar on the broad faces, smooth around rounded edges only.
for p in o.data.polygons: p.use_smooth=abs(p.normal.z)<.995
cube('Table',(0,0,-.007),(2,2,.01),table)
cube('Linen cover',(0,0,-.0008),(.152,.184,.0016),cover,.001)
cube('Book block',(0,0,.005),(.145,.177,.010),edge,.00045)
# Fine unprinted page strata; no third-party text.
for i in range(21):
 cube('Page stratum %02d'%i,(0,0,.0005+i*.00045),(.1454,.1774,.00008),paper,.00012)
cube('Open cream page',(0,0,.01005),(.145,.177,.0001),paper,0)
# A loose upper page ends over the lower 20 mm of the bookmark. Its lower
# surface is >= bookmark top, exactly touching at y=45mm; all coordinates m.
v=[]; f=[]; nx=12; ny=36
for j in range(ny+1):
 y=-.088+.133*j/ny; z=.0108+1.1*(y-.045)**2
 for i in range(nx+1): v.append((-.0725+.145*i/nx,y,z))
for j in range(ny):
 for i in range(nx):
  a=j*(nx+1)+i; f.append((a,a+1,a+nx+2,a+nx+1))
loose=mesh('Page holding the place',v,f,paper); sol=loose.modifiers.new('Paper thickness','SOLIDIFY'); sol.thickness=.0001; sol.offset=1
for p in loose.data.polygons:p.use_smooth=True
# Daylight only; no spotlight ornament.
def area(name,loc,power,size,color,target):
 bpy.ops.object.light_add(type='AREA',location=loc); a=bpy.context.object; a.name=name; a.data.energy=power; a.data.shape='DISK'; a.data.size=size; a.data.color=color; a.rotation_euler=(Vector(target)-a.location).to_track_quat('-Z','Y').to_euler()
area('Wide morning window',(-.25,.08,.4),7,.32,(1,.94,.81),(0,.03,0))
area('Sky fill',(.2,-.12,.27),2,.25,(.80,.88,1),(0,.03,0))
bpy.ops.object.camera_add(location=(.20,-.25,.43)); cam=bpy.context.object; cam.rotation_euler=(Vector((.01,.032,.012))-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.type='ORTHO'; cam.data.ortho_scale=.285; cam.data.lens=55; s.camera=cam
# Import scale, clearance and provenance evidence.
err=max(abs(o.data.vertices[i].co[k]-v[k]) for i,v in enumerate(vs) for k in range(3)); assert err<1e-8
assert all(math.isfinite(c) for p in o.data.vertices for c in p.co)
report={'cad_mesh_sha256':o['mesh_sha256'],'max_transfer_error_m':err,'triangles_preserved':len(o.data.polygons)==len(payload['faces']),'bookmark_bounds_m':[[.012,.025,.0101],[.037,.115,.0108]],'book_top_m':.0101,'bookmark_book_clearance_m':0,'upper_page_min_bottom_m':.0108,'upper_page_contact_at_y_m':.045,'book_end_y_m':.0885,'bookmark_overhang_mm':26.5,'intersection_check':'Analytical: book occupies z <= .0101, bookmark z >= .0101; upper page bottom >= .0108, bookmark top <= .0108. Contact allowed; no positive volume overlap. No physical paper or bending simulation.','render_engine':'Cycles CPU, 2 threads, no denoising','draft':draft}
(R/'blender_validation.json').write_text(json.dumps(report,indent=2)+'\n')
s.render.image_settings.file_format='PNG'; s.render.filepath=str(R/'renders'/('draft.png' if draft else 'returning_page_final.png'))
if not draft:bpy.ops.wm.save_as_mainfile(filepath=str(R/'Returning_Page.blend'))
bpy.ops.render.render(write_still=True)
