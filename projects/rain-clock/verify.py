import bpy, math, json, os
sc=bpy.context.scene
pivots=[o for o in bpy.data.objects if o.name.startswith('Rain rhythm')]
assert len(pivots)==2
poses={}
for f in (1,25,49,73,97):
 sc.frame_set(f); poses[f]=[tuple(o.rotation_euler) for o in pivots]
assert all(abs(a-b)<1e-6 for a,b in zip(sum(poses[1],()),sum(poses[97],())))
assert poses[1]!=poses[25]
assert len([o for o in bpy.data.objects if o.name.startswith('Rain bead')])==19
assert sc.camera and sc.frame_end==96
assert all(o.type!='MESH' or all(math.isfinite(v) for vert in o.data.vertices for v in vert.co) for o in bpy.data.objects)
result={'objects':len(bpy.data.objects),'rain_beads':19,'animation_seam':'PASS: frame 97 = frame 1','motion':'PASS: interior poses differ','geometry':'PASS: finite mesh vertices','external_images':len(bpy.data.images),'render_verified':False}
print(json.dumps(result,indent=2))
open(os.path.join(os.path.dirname(bpy.data.filepath),'verification.json'),'w').write(json.dumps(result,indent=2))
