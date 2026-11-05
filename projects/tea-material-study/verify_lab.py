#!/usr/bin/env python3
"""Read-only verification of the frozen isolated research bundle (stdlib)."""
import hashlib
import json
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parent
GLB_SHA = "e5b3a05b8db4421d1cca41c7f8f30d266ca718533d2602c40a1bad2e34416a7b"
SHADER_SHA = "732eaaee5f8c7b24acb2c24a839f8c16a47262f8ecf9d0ac14f62b9fb0d566cf"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def png_info(path):
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", path
    offset = 8
    dimensions = None
    kinds = []
    while offset < len(data):
        size = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + size]
        crc = struct.unpack_from(">I", data, offset + 8 + size)[0]
        assert zlib.crc32(kind + payload) & 0xffffffff == crc, path
        assert kind not in (b"tEXt", b"iTXt", b"zTXt", b"eXIf"), (path, "unexpected metadata")
        kinds.append(kind.decode("ascii"))
        if kind == b"IHDR":
            dimensions = struct.unpack_from(">II", payload)
        offset += size + 12
        if kind == b"IEND":
            break
    assert offset == len(data) and kinds[-1] == "IEND", path
    return dimensions

manifest = json.loads((ROOT / "manifest.json").read_text())
paths = []
for item in manifest["files"]:
    relative = Path(item["path"])
    assert not relative.is_absolute() and ".." not in relative.parts
    assert relative.parts[0] not in (".godot", "work")
    path = ROOT / relative
    assert not path.is_symlink()
    assert path.stat().st_size == item["size_bytes"], relative
    assert sha(path) == item["sha256"], relative
    paths.append(relative.as_posix())
assert len(paths) == len(set(paths))
assert sha(ROOT / "assets/second_cup_tableau.glb") == GLB_SHA
assert sha(ROOT / "shaders/empirical_tea.gdshader") == SHADER_SHA

data = (ROOT / "assets/second_cup_tableau.glb").read_bytes()
magic, version, size = struct.unpack_from("<4sII", data)
assert magic == b"glTF" and version == 2 and size == len(data)
n, kind = struct.unpack_from("<I4s", data, 12)
assert kind == b"JSON"
gltf = json.loads(data[20:20+n])
assert len(gltf["meshes"]) == 19
triangles = sum(gltf["accessors"][p["indices"]]["count"] // 3 for mesh in gltf["meshes"] for p in mesh["primitives"])
assert triangles == 62072
assert not gltf.get("images") and not gltf.get("textures")
assert "meshes/generate_lods=false" in (ROOT / "assets/second_cup_tableau.glb.import").read_text()

matrix = json.loads((ROOT / "qa/native_matrix.json").read_text())
assert matrix["rendering_method"] == "gl_compatibility"
assert matrix["display_server"] != "headless"
assert matrix["glb_sha256"] == GLB_SHA
assert matrix["candidate_shader_sha256"] == SHADER_SHA
assert matrix["geometry_fingerprint_before"] == matrix["geometry_fingerprint_after"]
assert matrix["view_only_material_override"] and not matrix["source_geometry_modified"]
assert matrix["capture_count"] == len(matrix["captures"]) == 12
assert len({(c["material"],c["view"],c["key_light"]) for c in matrix["captures"]}) == 12
for entry in matrix["captures"]:
    assert png_info(ROOT / entry["file"]) == tuple(entry["resolution"]) == (720,640)
assert png_info(ROOT / matrix["diagnostic_reference"]) == (720,640)
initial = json.loads((ROOT / "qa/initial/native_matrix.json").read_text())
assert initial["candidate_shader_sha256"] == sha(ROOT / "qa/initial/empirical_tea.gdshader")
for entry in initial["captures"]:
    assert png_info(ROOT / "qa/initial" / Path(entry["file"]).name) == tuple(entry["resolution"])
assert len(list((ROOT / "qa").rglob("*.png"))) == 25
for item in json.loads((ROOT / "qa/pixel_comparison.json").read_text())["comparisons"]:
    if item["view"] == "low":
        assert item["changed_scene_pixels_gt2"] == 0

shader = (ROOT / "shaders/empirical_tea.gdshader").read_text()
assert "depth_draw_always" in shader and "cull_back" in shader
assert "texture(" not in shader and "sampler2D" not in shader
assert "void vertex() { model_position = VERTEX; }" in shader
assert not any(token in (ROOT / p).read_text(errors="replace") for p in paths if Path(p).suffix in (".md", ".json", ".gd", ".gdshader", ".tscn", ".godot", ".import", ".sh", ".log") for token in ("/workspace/", "/home/agent/", "file:///"))
print(json.dumps({"status":"pass", "manifest_files":len(paths),
    "native_png_count":25, "png_text_metadata":False,
    "glb_meshes":19, "glb_triangles":triangles,
    "runtime_geometry_fingerprint_equal":True,
    "renderer":matrix["rendering_method"], "source_glb_sha256":GLB_SHA,
    "scope":"Frozen evidence validation; does not rerun the renderer or prove all-angle optical correctness."}, indent=2))
