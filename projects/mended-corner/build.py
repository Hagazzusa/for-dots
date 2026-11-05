"""Mended Corner — original procedural still life from a preserved GPT Image concept.

Blender 4.3.2, CPU only, two threads. No downloaded assets or texture dependencies.
Run from this directory: TMPDIR="$PWD/work" blender -b -t 2 --python build.py -- --draft
Final: TMPDIR="$PWD/work" blender -b -t 2 --python build.py
This is an artistic interpretation, not exact reconstruction or a fabrication plan.
"""
import bpy
import math
import random
import sys
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parent
RNG = random.Random(73)
DRAFT = '--draft' in sys.argv
NO_RENDER = '--no-render' in sys.argv
for directory in ('renders', 'work'):
    (ROOT / directory).mkdir(exist_ok=True)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for collection in list(bpy.data.collections):
    bpy.data.collections.remove(collection)
C = {}
for key, label in (
    ('bench', '01 · An old household bench, repaired'),
    ('tool', '02 · Wooden plane & short pencil'),
    ('cloth', '03 · A neighbour’s folded throw'),
    ('glass', '04 · Reused greenhouse glass & rain'),
    ('frame', '05 · A small fragment of shelter'),
    ('lamp', '06 · Workshop light left on'),
    ('outside', '07 · Blue evening, no real location'),
    ('light', '08 · Light rig'),
    ('camera', '09 · Camera & reference'),
):
    c = bpy.data.collections.new(label)
    bpy.context.scene.collection.children.link(c)
    C[key] = c

def put(obj, key):
    for collection in list(obj.users_collection):
        collection.objects.unlink(obj)
    C[key].objects.link(obj)
    return obj

def material(name, color, roughness=.5, metallic=0):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Roughness'].default_value = roughness
    p.inputs['Metallic'].default_value = metallic
    return m

def wood_material(name, dark, light, axis=(2.6, 125, 34), roughness=.54):
    m = material(name, light, roughness)
    n, links = m.node_tree.nodes, m.node_tree.links
    p = n.get('Principled BSDF')
    geo = n.new('ShaderNodeNewGeometry')
    scale = n.new('ShaderNodeVectorMath'); scale.operation = 'MULTIPLY'
    scale.inputs[1].default_value = axis
    links.new(geo.outputs['Position'], scale.inputs[0])
    grain = n.new('ShaderNodeTexNoise')
    grain.inputs['Scale'].default_value = 1
    grain.inputs['Detail'].default_value = 3.3
    grain.inputs['Roughness'].default_value = .72
    links.new(scale.outputs['Vector'], grain.inputs['Vector'])
    ramp = n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = .23
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].position = .77
    ramp.color_ramp.elements[1].color = (*light, 1)
    links.new(grain.outputs['Fac'], ramp.inputs[0])
    links.new(ramp.outputs['Color'], p.inputs['Base Color'])
    bump = n.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .21
    bump.inputs['Distance'].default_value = .0006
    links.new(grain.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], p.inputs['Normal'])
    rough = n.new('ShaderNodeMapRange')
    rough.inputs['From Min'].default_value = .15
    rough.inputs['From Max'].default_value = .85
    rough.inputs['To Min'].default_value = roughness - .12
    rough.inputs['To Max'].default_value = roughness + .16
    links.new(grain.outputs['Fac'], rough.inputs['Value'])
    links.new(rough.outputs['Result'], p.inputs['Roughness'])
    return m

old = wood_material('Old elm · lengthwise grain / softened by use', (.018,.007,.003), (.17,.071,.024), roughness=.65)
old_dark = wood_material('Old elm · darker apron and legs', (.014,.006,.003), (.11,.047,.018), roughness=.61)
repair = wood_material('New repair wood · quiet pale heartwood', (.085,.036,.009), (.37,.215,.069), axis=(3.0,62,25), roughness=.59)
framewood = wood_material('Reclaimed frame · vertical grain', (.016,.020,.016), (.105,.118,.078), (65,85,2.4), .71)
toolwood = wood_material('Plane · worn oiled pearwood', (.035,.011,.004), (.25,.10,.028), roughness=.36)
handlewood = wood_material('Plane · polished dark grip', (.018,.005,.002), (.13,.044,.011), roughness=.31)
endgrain = wood_material('Small endgrain dowels', (.035,.017,.008), (.16,.075,.031), (65,50,15), .62)
shavingmat = wood_material('Two thin curls of pale shaving', (.27,.135,.036), (.56,.34,.14), (2,80,30), .75)
bronze = material('Lamp · aged blackened bronze', (.05,.034,.016), .34, .78)
brass = material('Lamp · quietly worn brass edges', (.24,.13,.042), .32, .76)
steel = material('Plane · recessed iron / not a visible cutting edge', (.033,.039,.043), .3, .78)
holemat = material('Old nail recesses', (.007,.004,.002), .95)
red = material('Pencil · worn oxblood paint', (.21,.035,.015), .54)
graphite = material('Pencil · graphite', (.009,.012,.016), .34, .22)
fabric = material('Throw · sage wool with a small-scale woven relief', (.105,.145,.104), .96)
p = fabric.node_tree.nodes.get('Principled BSDF')
p.inputs['Sheen Weight'].default_value = .38
p.inputs['Sheen Roughness'].default_value = .7
n, links = fabric.node_tree.nodes, fabric.node_tree.links
geo = n.new('ShaderNodeTexCoord')
noise = n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 340; noise.inputs['Detail'].default_value = 2.4
links.new(geo.outputs['Object'], noise.inputs['Vector'])
base = n.new('ShaderNodeValToRGB')
base.color_ramp.elements[0].color = (.022,.053,.026,1)
base.color_ramp.elements[1].color = (.12,.19,.087,1)
links.new(noise.outputs['Fac'], base.inputs[0]); links.new(base.outputs['Color'], p.inputs['Base Color'])
bump = n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .32; bump.inputs['Distance'].default_value = .0017
links.new(noise.outputs['Fac'], bump.inputs['Height']); links.new(bump.outputs['Normal'], p.inputs['Normal'])
threadmats = [material('Wool yarn · '+str(i), color, .94) for i,color in enumerate([(.066,.125,.06),(.115,.18,.09),(.045,.09,.044)])]
for m in threadmats:
    m.node_tree.nodes.get('Principled BSDF').inputs['Sheen Weight'].default_value = .32

glass = material('Salvaged greenhouse glass · softly irregular', (.83,.92,.97), .065)
p = glass.node_tree.nodes.get('Principled BSDF')
p.inputs['Transmission Weight'].default_value = 1
p.inputs['IOR'].default_value = 1.45
n, links = glass.node_tree.nodes, glass.node_tree.links
noise = n.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 90; noise.inputs['Detail'].default_value = 2
tex = n.new('ShaderNodeTexCoord'); links.new(tex.outputs['Object'],noise.inputs['Vector'])
bump = n.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.12; bump.inputs['Distance'].default_value=.0007
links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],p.inputs['Normal'])
water = material('Rain · restrained glass-clear droplets', (.84,.94,1), .045)
p = water.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=1;p.inputs['IOR'].default_value=1.333
lampglass = material('Lamp · lightly frosted protective globe', (.93,.73,.40), .19)
p=lampglass.node_tree.nodes.get('Principled BSDF');p.inputs['Transmission Weight'].default_value=.8;p.inputs['IOR'].default_value=1.45
bulbmat=material('Lamp · warm visible bulb', (1,.53,.16), .4)
p=bulbmat.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(1,.47,.105,1);p.inputs['Emission Strength'].default_value=5

def mesh(name, verts, faces, mat, key):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    ob=bpy.data.objects.new(name,me);C[key].objects.link(ob)
    ob.data.materials.append(mat)
    return ob

def bevel(ob, width=.003, segments=3):
    modifier=ob.modifiers.new('Small softened edges','BEVEL');modifier.width=width;modifier.segments=segments
    modifier=ob.modifiers.new('Weighted face normals','WEIGHTED_NORMAL')
    return ob

def cube(name, loc, dimensions, mat, key, radius=.002):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.dimensions=dimensions
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    ob.data.materials.append(mat);put(ob,key)
    if radius:bevel(ob,radius)
    return ob

def sphere(name, loc, scale, mat, key, segments=20, rings=12):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=rings,radius=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(mat);put(ob,key)
    for f in ob.data.polygons:f.use_smooth=True
    return ob

def cylinder(name, a,b,r,mat,key,vertices=24):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=v.length,location=(a+b)/2)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat);put(ob,key)
    bevel(ob,min(.001,r*.15),2)
    return ob

def curve(name, points, radius, mat, key, res=2):
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=res
    spl=cu.splines.new('POLY');spl.points.add(len(points)-1)
    for co,point in zip(points,spl.points):point.co=(*co,1)
    ob=bpy.data.objects.new(name,cu);C[key].objects.link(ob);ob.data.materials.append(mat)
    return ob

def polygon_prism(name, points, low, high, mat, key, edge=.001):
    # Ordered planar concave caps keep their boundary; Blender tessellates them for rendering.
    count=len(points)
    verts=[(x,y,z) for z in (low,high) for x,y in points]
    faces=[tuple(reversed(range(count))),tuple(i+count for i in range(count))]
    for i in range(count):
        j=(i+1)%count;faces.append((i,j,j+count,i+count))
    ob=mesh(name,verts,faces,mat,key)
    # Fix orientation independent of input polygon winding.
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.object.mode_set(mode='OBJECT');ob.select_set(False)
    if edge:bevel(ob,edge,2)
    return ob

def lathe(name, center, profile, mat,key,n=48):
    x,y=center;verts=[]
    for z,r in profile:
        for j in range(n):
            a=2*math.pi*j/n;verts.append((x+r*math.cos(a),y+r*math.sin(a),z))
    faces=[]
    for i in range(len(profile)-1):
        for j in range(n):
            k=(j+1)%n;faces.append((i*n+j,i*n+k,(i+1)*n+k,(i+1)*n+j))
    faces.append(tuple(reversed(tuple(range(n)))));faces.append(tuple((len(profile)-1)*n+j for j in range(n)))
    ob=mesh(name,verts,faces,mat,key)
    for f in ob.data.polygons:f.use_smooth=True
    return ob

# BENCH: a 34 mm slatted seat, not the massive worktop seen in the reference.
TOP=.49
for index,y in enumerate((-.015,.165)):
    cube('Seat slat '+str(index+2)+' | old wood',(0,y,TOP-.017),(2.50,.17,.034),old,'bench',.004)
# Shallow fitted repair, with a stepped outline and a continuous old-wood underside.
front_y0,front_y1=-.28,-.11
cube('Front seat slat | original lower wood',(0,-.195,.466),(2.5,.17,.020),old,'bench',.003)
leftline=[(-.17,front_y0),(-.17,-.226),(-.197,-.226),(-.197,-.165),(-.17,-.165),(-.17,front_y1)]
rightline=[(.10,front_y0),(.10,-.226),(.127,-.226),(.127,-.165),(.10,-.165),(.10,front_y1)]
leftpoly=[(-1.25,front_y0)]+leftline+[(-1.25,front_y1)]
rightpoly=rightline+[(1.25,front_y1),(1.25,front_y0)]
patchpoly=leftline+list(reversed(rightline))
polygon_prism('Front seat slat | old left lip',leftpoly,.476,TOP,old,'bench',.0008)
polygon_prism('Front seat slat | old right lip',rightpoly,.476,TOP,old,'bench',.0008)
polygon_prism('Quiet fitted repair | shallow pale splice',patchpoly,.476,TOP,repair,'bench',.00055)
for x in (-.126,.061):
    cylinder('Repair | small flush wood peg',(x,-.195,TOP-.003),(x,-.195,TOP+.0003),.0042,endgrain,'bench',16)
cube('Bench apron | rounded front rail',(0,-.242,.414),(2.42,.044,.08),old_dark,'bench',.008)
cube('Bench apron | rear rail',(0,.21,.414),(2.42,.044,.08),old_dark,'bench',.007)
for x in (-.88,.91):
    for y in (-.20,.18):
        cube('Bench leg | reused household timber',(x,y,.215),(.068,.07,.43),old_dark,'bench',.009)
    cube('Bench under-seat bearer',(x,-.025,.433),(.082,.53,.046),old_dark,'bench',.004)
    cube('Bench side stretcher',(x,-.015,.165),(.045,.43,.048),old_dark,'bench',.005)
cube('Bench long stretcher',(0,.17,.17),(1.85,.045,.05),old_dark,'bench',.005)
# A few tiny irregular old fixings; no ruin, splinters, or dangerous broken wood.
for x in (-1.0,-.84,-.41,.42,.89,1.1):
    y=-.267+RNG.uniform(-.005,.006)
    cylinder('Old countersunk fixing | top',(x,y,TOP-.001),(x,y,TOP+.0001),RNG.uniform(.0022,.0033),holemat,'bench',12)
for x in (-.86,-.43,.39,.88):
    cylinder('Old apron nail | dark head',(x,-.266,.417),(x,-.2645,.417),.0035,bronze,'bench',12)
# Sparse shallow grain scratches on the top; deterministic, no image textures.
for i in range(24):
    y=RNG.uniform(-.263,.23);x=RNG.uniform(-1.1,.95);length=RNG.uniform(.028,.15)
    if y<-.11 and x<.13 and x+length>-.20:continue
    points=[(x+length*t/6,y+.0008*math.sin(t*1.1+i),TOP+.00015) for t in range(7)]
    curve('Fine wear line',points,.00019,old_dark,'bench',1)

# PLANE: all components share an editable parent; it lies on its wooden side.
plane_root=bpy.data.objects.new('PROP · Wooden smoothing plane on its side',None);C['tool'].objects.link(plane_root)
plane_root.location=(-.60,-.07,TOP+.045)
plane_root.rotation_euler=(math.pi/2,0,math.radians(-9))
def plane_part(obj):obj.parent=plane_root;return obj
plane_part(cube('Plane | sole block',(0,0,.012),(.29,.09,.024),toolwood,'tool',.007))
plane_part(cube('Plane | toe',(.105,0,.048),(.08,.09,.072),toolwood,'tool',.009))
plane_part(cube('Plane | heel',(-.10,0,.045),(.09,.09,.066),toolwood,'tool',.008))
for side in (-1,1):plane_part(cube('Plane | cheek '+str(side),(0,side*.038,.045),(.12,.014,.066),toolwood,'tool',.004))
wedge=plane_part(cube('Plane | tapered wooden wedge',(-.003,0,.065),(.048,.061,.064),handlewood,'tool',.005));wedge.rotation_euler.y=-.35
iron=plane_part(cube('Plane | dark recessed iron',(-.029,0,.069),(.006,.050,.067),steel,'tool',.001));iron.rotation_euler.y=-.35
plane_part(sphere('Plane | worn rear palm grip',(-.105,0,.100),(.042,.035,.055),handlewood,'tool',24,16))
plane_part(sphere('Plane | thumb-polished toe',(.102,0,.087),(.034,.030,.018),toolwood,'tool',20,12))
# Two thin curls, not a heap of sawdust. Ribbon strip is modeled explicitly.
for index,(cx,cy,radius) in enumerate([(-.49,-.205,.014),(-.43,-.183,.010)]):
    verts=[];faces=[]
    for j in range(65):
        t=j/64;a=t*math.pi*2.0
        x=cx+.037*(t-.5);z=TOP+radius+radius*math.cos(a)
        y=cy+radius*math.sin(a)
        verts.extend([(x,y-.004,z),(x,y+.004,z)])
    for j in range(64):faces.append((j*2,j*2+1,j*2+3,j*2+2))
    ob=mesh('Wood shaving '+str(index+1)+' | thin ribbon',verts,faces,shavingmat,'tool')
    ob.modifiers.new('Paper-thin shaving','SOLIDIFY').thickness=.00035

# Short hexagonal carpenter pencil, with an actual sharpened wood taper.
pencil_root=bpy.data.objects.new('PROP · Short carpenter pencil',None);C['tool'].objects.link(pencil_root)
pencil_root.location=(-.08,.008,TOP+.0073);pencil_root.rotation_euler.z=math.radians(12)
def pencil_part(obj):obj.parent=pencil_root;return obj
pencil_part(cylinder('Pencil | painted hexagonal barrel',(-.09,0,0),(.061,0,0),.0073,red,'tool',6))
pencil_part(cylinder('Pencil | blunt worn end',(-.094,0,0),(-.090,0,0),.0072,toolwood,'tool',6))
def cone_between(name,a,b,r1,r2,mat,key,vertices=6):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=vertices,radius1=r1,radius2=r2,depth=v.length,location=(a+b)/2)
    ob=bpy.context.object;ob.name=name;ob.rotation_euler=v.to_track_quat('Z','Y').to_euler();ob.data.materials.append(mat);put(ob,key);return ob
pencil_part(cone_between('Pencil | exposed cedar',(.061,0,0),(.084,0,0),.0073,.0017,repair,'tool'))
pencil_part(cone_between('Pencil | small graphite point',(.084,0,0),(.090,0,0),.0017,.0002,graphite,'tool'))

# BLANKET: one continuous draped quad sheet with folded material on its rear half.
# It is deliberately modeled, not a cloth simulation, and contains no imported fabric.
def cloth_point(u,v):
    length=.895*v
    x=.40+.64*u
    if length<=.55:
        y=.24-length;z=.495
        z+=.0038*(1+math.sin(6*math.pi*u+.5*math.sin(10*v)))
        z+=.004*math.sin(v*5)**2
    elif length<=.55+.035*math.pi/2:
        a=(length-.55)/.035;y=-.31-.035*math.sin(a);z=.46+.035*math.cos(a)
        z+=.004*math.sin(6*math.pi*u+.5)
    else:
        y=-.345;z=.46-(length-.55-.035*math.pi/2)
        y+=.019*math.sin(6*math.pi*u+v*2)+.006*math.sin(15*math.pi*u)
        z+=.010*math.sin(u*2*math.pi+.6)*((v-.67)/.33)
    x+=.004*math.sin(v*16+u*4)
    return Vector((x,y,z))
N,M=50,92
verts=[tuple(cloth_point(i/N,j/M)) for j in range(M+1) for i in range(N+1)]
faces=[]
for j in range(M):
    for i in range(N):
        a=j*(N+1)+i;faces.append((a,a+1,a+N+2,a+N+1))
throw=mesh('PROP · Neighbour’s sage throw | continuous drape',verts,[tuple(reversed(f)) for f in faces],fabric,'cloth')
throw.modifiers.new('Soft textile thickness','SOLIDIFY').thickness=.005
throw.modifiers.new('Gentle cloth subdivision','SUBSURF').levels=1
for p in throw.data.polygons:p.use_smooth=True
# A softly rounded folded volume rests directly on the modeled lower layer.
# Lower vertices follow that layer; thickness is artistic wool loft, not simulation.
verts=[];faces=[];NX,NY=42,36
for layer in (0,1):
    for j in range(NY+1):
        v=j/NY
        for i in range(NX+1):
            u=i/NX;y=.222-.268*v
            body_v=(.24-y)/.895
            body=cloth_point(u,body_v)
            x=body.x+.003*math.sin(v*math.pi)
            lower=body.z+.001
            loft=.007+.027*math.sin(math.pi*v)**.7+.005*math.sin(u*5*math.pi+v)**2
            verts.append((x,y,lower+(loft if layer else 0)))
count=(NX+1)*(NY+1)
for j in range(NY):
    for i in range(NX):
        a=j*(NX+1)+i
        quad=(a,a+1,a+NX+2,a+NX+1)
        faces.append(quad)
        faces.append(tuple(k+count for k in reversed(quad)))
boundary=list(range(NX+1))+[j*(NX+1)+NX for j in range(1,NY+1)]+[NY*(NX+1)+i for i in range(NX-1,-1,-1)]+[j*(NX+1) for j in range(NY-1,0,-1)]
for a,b in zip(boundary,boundary[1:]+boundary[:1]):faces.append((a,b,b+count,a+count))
fold=mesh('Throw | softly rounded folded wool volume',verts,faces,fabric,'cloth')
fold.modifiers.new('Soft folded edges','SUBSURF').levels=1
for p in fold.data.polygons:p.use_smooth=True
# Modest yarn relief follows the actual drape; not a flat picture of a blanket.
for i in range(72):
    u=(i+.5)/72;points=[]
    for j in range(115):
        v=j/114;uu=u+.0018*math.sin(v*math.pi*104)
        p=cloth_point(uu,v)
        if v<.615:p.z+=.0031
        else:p.y-=.0031
        points.append(tuple(p))
    curve('Throw | running wool yarn',points,.00050,threadmats[i%3],'cloth',1)
for j in range(140):
    v=(j+.5)/140;points=[]
    for i in range(70):
        u=i/69;p=cloth_point(u,v+.0008*math.sin(u*math.pi*90))
        if v<.615:p.z+=.0030
        else:p.y-=.0030
        points.append(tuple(p))
    curve('Throw | soft cross-weave',points,.00045,threadmats[(j+1)%3],'cloth',1)
# The upper fold uses the same yarn relief, so it reads as cloth rather than foam.
def fold_point(u,v):
    y=.222-.268*v;body=cloth_point(u,(.24-y)/.895)
    loft=.007+.027*math.sin(math.pi*v)**.7+.005*math.sin(u*5*math.pi+v)**2
    return Vector((body.x+.003*math.sin(v*math.pi),y,body.z+.001+loft+.0008))
for i in range(72):
    u=(i+.5)/72;points=[]
    for j in range(73):
        v=j/72;points.append(tuple(fold_point(u+.0018*math.sin(v*math.pi*40),v)))
    curve('Throw fold | running wool yarn',points,.00050,threadmats[i%3],'cloth',1)
for j in range(42):
    v=(j+.5)/42;points=[]
    for i in range(88):
        u=i/87;points.append(tuple(fold_point(u,v+.0018*math.sin(u*math.pi*90))))
    curve('Throw fold | soft cross-weave',points,.00045,threadmats[(j+1)%3],'cloth',1)
for i in range(32):
    p=cloth_point((i+.5)/32,1);points=[]
    length=RNG.uniform(.038,.058)
    for j in range(13):
        t=j/12;points.append((p.x+.0025*math.sin(t*math.pi*3+i),p.y-.002+.002*math.cos(t*5+i),p.z-length*t))
    curve('Throw | short soft fringe',points,.00135,threadmats[i%3],'cloth',2)
for i in range(80):
    u=RNG.random();v=RNG.uniform(.80,1);p=cloth_point(u,v);p.y-=.004
    q=p+Vector((RNG.uniform(-.003,.003),-.002,RNG.uniform(-.003,.005)))
    curve('Throw | occasional wool fibre',[tuple(p),tuple((p+q)/2+Vector((0,-.001,0))),tuple(q)],.00014,threadmats[i%3],'cloth',1)

# REUSED GLASS AND A FRAGMENT OF SHELTER, deliberately not the full pavilion.
pane=cube('Greenhouse pane | one reused unbroken sheet',(-.30,.408,1.12),(2.04,.004,1.05),glass,'glass',0)
pane.visible_shadow=False
cube('Window | old lower sill',(-.20,.401,.604),(2.42,.084,.083),old_dark,'frame',.007)
cube('Window | left jamb',(-1.365,.41,1.12),(.105,.11,1.20),framewood,'frame',.007)
cube('Window | right jamb',(.78,.41,1.12),(.12,.13,1.20),framewood,'frame',.008)
cube('Window | top rail',(-.20,.41,1.69),(2.42,.11,.09),framewood,'frame',.006)
for i in range(4):cube('Right return | vertical painted timber',(.915+i*.15,.43,1.00),(.142,.075,1.37),framewood,'frame',.004)
for i in range(5):cube('Sage lower wall board',(-1.3+i*.56,.425,.32),(.55,.04,.49),framewood,'frame',.003)
for x in (-1.34,.78):
    for z in (.67,1.48):cylinder('Old frame screw',(x,.337,z),(x,.346,z),.006,bronze,'frame',16)
for i in range(150):
    x=RNG.uniform(-1.29,.70);z=RNG.uniform(.663,1.63)
    r=RNG.uniform(.0015,.0048)
    sphere('Rain bead | outside glass',(x,.413,z),(r,.0016,r*RNG.uniform(1.0,1.8)),water,'glass',10,8)
for index,(x,z,length) in enumerate([(-.87,1.38,.40),(-.35,1.47,.49),(.32,1.29,.32)]):
    points=[]
    for j in range(34):
        t=j/33;points.append((x+.006*math.sin(t*11+index)+.002*math.sin(t*35),.413,z-length*t))
    curve('Rain trail '+str(index+1)+' | outside pane',points,.0020,water,'glass',2)
    sphere('Rain trail | hanging bead',points[-1],(.0042,.0025,.0075),water,'glass',12,8)

# Blurred abstract night beyond the glass, not an HDRI or a real landscape.
night=material('Outside · softly mottled blue evening',(.037,.074,.12),.95)
n,links=night.node_tree.nodes,night.node_tree.links;p=n.get('Principled BSDF')
tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=2.6;tex.inputs['Detail'].default_value=2
r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.008,.021,.034,1);r.color_ramp.elements[1].color=(.12,.21,.32,1)
links.new(tex.outputs['Fac'],r.inputs[0]);links.new(r.outputs['Color'],p.inputs['Base Color']);links.new(r.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.20
cube('Evening background | abstract plane',(0,1.7,1.25),(5,.06,3),night,'outside',0)
silhouette=material('Outside · distant quiet shapes',(.009,.022,.026),1)
# No large exterior objects: the window remains a soft, anonymous evening.

# WORKSHOP LAMP: a small existing lamp, reused rather than a dramatic spotlight.
LX,LY=.76,.245
lathe('Lamp | dark bell shade',(LX,LY),[(1.095,.112),(1.100,.118),(1.110,.109),(1.143,.061),(1.174,.033),(1.186,.032)],bronze,'lamp')
lathe('Lamp | brass lower lip',(LX,LY),[(1.095,.111),(1.098,.116),(1.103,.113)],brass,'lamp')
lathe('Lamp | socket cap',(LX,LY),[(1.177,.030),(1.207,.030),(1.216,.021)],bronze,'lamp')
bulb=sphere('Lamp | warm bulb',(LX,LY,1.015),(.028,.028,.055),bulbmat,'lamp',28,20)
bulb.visible_shadow=False
globe=lathe('Lamp | protective glass',(LX,LY),[(.932,.030),(.938,.047),(1.079,.047),(1.092,.030)],lampglass,'lamp')
globe.visible_shadow=False
for z in (.939,.990,1.079):
    pts=[(LX+.056*math.cos(j*math.pi/32),LY+.056*math.sin(j*math.pi/32),z) for j in range(65)]
    curve('Lamp | cage ring',pts,.0022,brass,'lamp',2)
for j in range(4):
    a=j*math.pi/2+.18
    pts=[(LX+.055*math.cos(a),LY+.055*math.sin(a),1.088),(LX+.056*math.cos(a),LY+.056*math.sin(a),.95),(LX+.043*math.cos(a),LY+.043*math.sin(a),.927),(LX+.023*math.cos(a),LY+.023*math.sin(a),.921)]
    curve('Lamp | protective cage upright',pts,.0027,bronze,'lamp',2)
curve('Lamp | short wall bracket',[(LX,.337,1.265),(LX,.27,1.265),(LX,LY,1.242),(LX,LY,1.211)],.006,bronze,'lamp',2)
cube('Lamp | wall mounting plate',(LX,.337,1.26),(.045,.016,.095),bronze,'lamp',.006)

# Bring this small lamp nearer to the seat for an intimate still-life crop.
for ob in C['lamp'].objects:ob.location.z-=.18

# LIGHTS / CAMERA. Small neutral fill preserves the plane without flattening the night.
def light(name,typ,loc,energy,color,size,target=None):
    d=bpy.data.lights.new(name,typ);d.energy=energy;d.color=color
    if typ=='AREA':d.shape='DISK';d.size=size
    else:d.shadow_soft_size=size
    ob=bpy.data.objects.new(name,d);C['light'].objects.link(ob);ob.location=loc
    if typ=='AREA':
        ob.visible_camera=False;ob.visible_glossy=False;ob.visible_transmission=False
    if target:ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
    return ob
light('Workshop bulb | warm local pool','POINT',(LX,LY,.83),12,(1,.52,.20),.032)
light('Window | broad blue evening','AREA',(-.35,.95,1.48),60,(.39,.59,1.0),1.8,(0,-.05,.49))
light('Soft reflected window fill','AREA',(-1.0,-1.15,1.4),24,(.61,.72,1),1.5,(0,0,.55))
light('Small warm reflected lamp fill','AREA',(.68,-.03,.88),3,(1,.58,.27),.45,(.07,-.15,.49))
world=bpy.data.worlds.new('Quiet blue night');world.use_nodes=True
world.node_tree.nodes['Background'].inputs['Color'].default_value=(.055,.085,.13,1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value=.22
bpy.context.scene.world=world

camera_data=bpy.data.cameras.new('Natural still life · 52 mm')
camera=bpy.data.objects.new('CAM · Mended Corner',camera_data);C['camera'].objects.link(camera)
camera.location=(-1.20,-2.00,1.50);target=Vector((.05,.0,.58))
camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
camera_data.lens=52
focus=bpy.data.objects.new('Focus · repaired seat & pencil',None);C['camera'].objects.link(focus);focus.location=(-.08,-.11,.51)
camera_data.dof.use_dof=True;camera_data.dof.focus_object=focus;camera_data.dof.aperture_fstop=4.5
scene=bpy.context.scene;scene.camera=camera
scene.render.engine='CYCLES';scene.cycles.device='CPU'
scene.render.threads_mode='FIXED';scene.render.threads=2
scene.cycles.samples=24 if DRAFT else 128
scene.cycles.use_denoising=False
scene.cycles.seed=73;scene.cycles.use_adaptive_sampling=True
scene.cycles.adaptive_threshold=.015;scene.cycles.adaptive_min_samples=16 if DRAFT else 32
scene.cycles.max_bounces=8;scene.cycles.transmission_bounces=6;scene.cycles.transparent_max_bounces=8
scene.cycles.sample_clamp_direct=12;scene.cycles.sample_clamp_indirect=2
scene.cycles.caustics_reflective=False;scene.cycles.caustics_refractive=False
scene.render.resolution_x=1200;scene.render.resolution_y=800
scene.render.resolution_percentage=50 if DRAFT else 100
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
scene.render.image_settings.color_depth='8';scene.render.film_transparent=False
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=.3
scene.render.fps=24;scene.render.use_file_extension=True
scene.render.filepath='//renders/'+('draft.png' if DRAFT else 'mended_corner_final.png')
scene['artwork_title']='Mended Corner · 수선이 남긴 자리'
scene['generation']='Original procedural 3D interpretation; not an image projection or exact reconstruction'
scene['story']='An old household bench repaired by a fictional neighbourhood carpenter; neighbours supplied the throw.'
scene['safety_scope']='Visual art only. No joinery, load, electrical, glazing, or construction validation.'

# Packed reference keeps the concept distinguishable and portable. It is not used in shaders.
reference=bpy.data.images.load(str(ROOT/'reference/gpt_image_concept.png'))
reference.name='REFERENCE ONLY · GPT Image concept';reference.pack();reference.use_fake_user=True
reference.filepath='//reference/gpt_image_concept.png'
for packed in reference.packed_files:packed.filepath='//reference/gpt_image_concept.png'
guide=bpy.data.texts.new('READ ME · Concept is not the render');guide.use_fake_user=True
guide.write('Mended Corner — original, editable Blender still life. The packed GPT Image is a mood/composition reference only and is never projected, composited, or used as a texture. The 34 mm seat and shallow splice deliberately differ from the massive worktop-like reference. Materials and all geometry are procedural originals. No third-party assets. This is an artistic scene, not a woodworking, electrical or construction guide. See README.md, provenance.json, checks.json and audit.py.\n')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':
            area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=30
        elif area.type=='FILE_BROWSER':
            try:area.spaces.active.params.directory=b'//'
            except Exception:pass
bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=None
scene.unit_settings.system='METRIC'
bpy.context.view_layer.update()

checks={
    'artwork':'Mended Corner',
    'draft':DRAFT,
    'reference_used_as_texture':False,
    'original_asset_sources_only':True,
    'prop_groups':['wooden smoothing plane','short carpenter pencil','sage wool throw','small workshop lamp'],
    'geometry_objects':sum(o.type=='MESH' for o in scene.objects),
    'curve_objects':sum(o.type=='CURVE' for o in scene.objects),
    'seat_top_m':TOP,
    'seat_thickness_m':.034,
    'repair_depth_m':.014,
    'lamp_bulb_center_m':[LX,LY,.835],
    'render':{'engine':'Cycles','device':'CPU','threads':2,'samples':scene.cycles.samples,'denoising':False,'width':600 if DRAFT else 1200,'height':400 if DRAFT else 800},
    'limitations':['No physical joinery or electrical validation','Rain is static geometry, not simulation','Blanket is a modeled quad surface, not simulated cloth','Lighting includes two artistic bounce-fill area lights', 'Glazing and bulb shadow visibility are disabled; area-light camera, glossy and transmission visibility are disabled to avoid visible softbox shapes','C2PA generation reference retained byte-for-byte outside blend; final is a real Cycles render'],
}
(ROOT/('draft_checks.json' if DRAFT else 'checks.json')).write_text(json.dumps(checks,ensure_ascii=False,indent=2)+'\n')
blend_name='Mended_Corner_Draft.blend' if DRAFT else 'Mended_Corner.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/blend_name),compress=True)
if not NO_RENDER:
    bpy.ops.render.render(write_still=True)
print('MENDED_CORNER_BUILD_COMPLETE',blend_name,scene.render.filepath)
