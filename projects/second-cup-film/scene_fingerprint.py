"""Blender-side static scene fingerprint. Excludes camera and render settings."""
import bpy
import hashlib
import json

def value(v):
    if isinstance(v, (str, bool, int, float)) or v is None:
        return v
    if isinstance(v, bpy.types.ID):
        return {"id_type": v.bl_rna.identifier, "name": v.name}
    try:
        return [value(x) for x in v]
    except TypeError:
        return str(v)

def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()).hexdigest()

def node_tree(tree):
    if not tree:
        return None
    nodes=[]
    for node in sorted(tree.nodes,key=lambda n:n.name):
        props={}
        for prop in node.bl_rna.properties:
            key=prop.identifier
            if key in ("rna_type","inputs","outputs","internal_links","parent") or prop.type in ("COLLECTION",):
                continue
            if prop.type=="POINTER" and key not in ("image","node_tree"):
                continue
            try: props[key]=value(getattr(node,key))
            except (AttributeError,TypeError): pass
        nodes.append({"name":node.name,"type":node.bl_idname,"props":props,
          "inputs":[{"name":s.name,"identifier":s.identifier,"value":value(s.default_value)} for s in node.inputs if hasattr(s,"default_value")]})
    links=sorted((l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in tree.links)
    return {"nodes":nodes,"links":links}

def fingerprint():
    deps=bpy.context.evaluated_depsgraph_get()
    objects=[]
    for ob in sorted(bpy.context.scene.objects,key=lambda o:o.name):
        if ob.type=="CAMERA":continue
        data={"name":ob.name,"type":ob.type,"matrix_world":[list(r) for r in ob.matrix_world],
          "hide_render":ob.hide_render,"collections":sorted(c.name for c in ob.users_collection),
          "visible_camera":ob.visible_camera,"visible_shadow":ob.visible_shadow,
          "visible_diffuse":ob.visible_diffuse,"visible_glossy":ob.visible_glossy,
          "visible_transmission":ob.visible_transmission}
        if ob.type=="MESH":
            evaluated=ob.evaluated_get(deps);mesh=evaluated.to_mesh()
            data["evaluated_mesh"]={"vertices":[list(v.co) for v in mesh.vertices],
               "polygons":[[list(p.vertices),p.material_index,p.use_smooth] for p in mesh.polygons]}
            data["materials"]=[m.name if m else None for m in ob.data.materials]
            evaluated.to_mesh_clear()
        if ob.type=="LIGHT":
            light=ob.data
            data["light"]={k:value(getattr(light,k)) for k in ("type","color","energy","shape","size","size_y","use_shadow")}
            data["light_nodes"]=node_tree(light.node_tree)
        objects.append({"name":ob.name,"sha256":digest(data)})
    # Blender drops zero-user factory materials on save. Only materials assigned
    # to this scene's objects belong to the rendered artwork; all are hashed.
    used_materials={m.name:m for ob in bpy.context.scene.objects if hasattr(ob.data,"materials") for m in ob.data.materials if m}
    materials=[{"name":m.name,"nodes":node_tree(m.node_tree),"diffuse_color":value(m.diffuse_color),
       "metallic":m.metallic,"roughness":m.roughness,"use_nodes":m.use_nodes} for m in sorted(used_materials.values(),key=lambda m:m.name)]
    packed=[{"name":im.name,"sha256":hashlib.sha256(bytes(im.packed_file.data)).hexdigest()} for im in sorted(bpy.data.images,key=lambda im:im.name) if im.packed_file]
    world=node_tree(bpy.context.scene.world.node_tree)
    result={"non_camera_objects":objects,"materials_sha256":digest(materials),"world_sha256":digest(world),"packed_images":packed}
    result["static_scene_sha256"]=digest(result)
    return result
