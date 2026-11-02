"""Create runtime LOD from preserved high-detail CC0 building assemblies.
Keeps material boundaries while collapsing sub-pixel architectural detail.
"""
import bpy, os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'art/city_assembly.blend'))
for name,suffix in [('Apartment_A','a'),('Apartment_B','b')]:
 obj=bpy.data.objects[name]
 bpy.ops.object.select_all(action='DESELECT');obj.hide_set(False);obj.hide_render=False;obj.select_set(True);bpy.context.view_layer.objects.active=obj
 # Source B was spaced nine metres right only for the editable assembly overview.
 if suffix=='b':obj.location.x-=9
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 dec=obj.modifiers.new('Runtime silhouette-preserving LOD','DECIMATE');dec.decimate_type='COLLAPSE';dec.ratio=.13;dec.use_collapse_triangulate=True;dec.delimit={'MATERIAL','SEAM','UV'}
 bpy.ops.object.modifier_apply(modifier=dec.name)
 obj.data.calc_loop_triangles();print('OPTIMIZED',name,'triangles',len(obj.data.loop_triangles),'materials',len(obj.data.materials))
 bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT,'assets/city/apartment_'+suffix+'.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True)
# Runtime-only low-poly source separate from immutable high-detail source.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'art/city_runtime_lod.blend'))
