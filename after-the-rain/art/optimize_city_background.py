"""Background quality: 4-5k triangles, diffuse/emission only; preserves detail tier."""
import bpy,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'art/city_runtime_lod.blend'))
# Simplify expensive textured PBR channels while keeping authored albedo/emission.
for mat in bpy.data.materials:
 if not mat.use_nodes:continue
 p=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not p:continue
 for key in ['Normal','Roughness','Metallic','Coat Weight','Specular IOR Level']:
  inp=p.inputs.get(key)
  if inp:
   for link in list(inp.links):mat.node_tree.links.remove(link)
 p.inputs['Roughness'].default_value=.8;p.inputs['Metallic'].default_value=0
 p.inputs['Coat Weight'].default_value=0;p.inputs['Specular IOR Level'].default_value=.2
 # glTF exporter recognizes glTF Material Output nodes as occlusion; disconnect them.
 for n in list(mat.node_tree.nodes):
  if n.type=='GROUP' and n.node_tree and 'glTF' in n.node_tree.name:
   for inp in n.inputs:
    for link in list(inp.links):mat.node_tree.links.remove(link)
for name,suffix in [('Apartment_A','a'),('Apartment_B','b')]:
 obj=bpy.data.objects[name];bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.hide_render=False;obj.select_set(True);bpy.context.view_layer.objects.active=obj
 dec=obj.modifiers.new('Distant city silhouette LOD','DECIMATE');dec.decimate_type='COLLAPSE';dec.ratio=.235;dec.use_collapse_triangulate=True;dec.delimit={'MATERIAL','SEAM','UV'}
 bpy.ops.object.modifier_apply(modifier=dec.name);obj.data.calc_loop_triangles();print('BACKGROUND',name,'triangles',len(obj.data.loop_triangles),'materials',len(obj.data.materials))
 bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'assets/city/apartment_'+suffix+'.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'art/city_background_lod.blend'))
