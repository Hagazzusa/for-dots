"""Blender 장면을 읽기 전용으로 점검한다. --report 경로를 쓰면 JSON만 저장한다."""
import bpy, bmesh, json, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
s=bpy.context.scene
meshes=[o for o in s.objects if o.type=='MESH' and o.name!='바닥']
assert len(meshes)==3
assert {o.name for o in meshes}=={'군청 빗살','다홍 빗살','따로 놓인 다홍 이빨'}
reports={}; trees={}
for o in meshes:
 bm=bmesh.new(); bm.from_mesh(o.data)
 assert all(e.is_manifold for e in bm.edges),o.name
 assert bm.calc_volume()>0,o.name
 bm.transform(o.matrix_world); trees[o.name]=BVHTree.FromBMesh(bm)
 reports[o.name]={'vertices':len(bm.verts),'faces':len(bm.faces),'closed_manifold':True,'volume':bm.calc_volume()}
 assert abs(min(v.co.z for v in bm.verts))<1e-6
 bm.free()
blue=trees['군청 빗살']
for name in ('다홍 빗살','따로 놓인 다홍 이빨'):
 assert not blue.overlap(trees[name]),name
assert not trees['다홍 빗살'].overlap(trees['따로 놓인 다홍 이빨'])
assert not [im for im in bpy.data.images if im.source=='FILE']
assert s.render.resolution_x==1600 and s.render.resolution_y==1400
out={'objects':reports,'unbeveled_surface_intersections':0,'all_parts_on_z_zero':True,'external_image_assets':0,'render_engine':s.render.engine,'samples':s.cycles.samples,'blender':bpy.app.version_string,'note':'기본 메시의 닫힘·표면 교차 검사입니다. 실제 제작 공차·내구성·안전 검사가 아닙니다.'}
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
if '--report' in args:
 p=args[args.index('--report')+1]; open(p,'w').write(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(out,ensure_ascii=False))
