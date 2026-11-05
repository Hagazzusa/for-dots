"""Read-only scope and published hash checks; not a visual or security certification."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent

def text(name): return (ROOT/name).read_text(encoding='utf-8')
def remove_nodes(s,prefix):
    return re.sub(r'\[node name="'+prefix+r'[^\n]+\n(?:(?!\[node).)*','',s,flags=re.S)
base=text('baseline.tscn')
bank=text('bank.tscn').replace('load_steps=13','load_steps=12').replace('[ext_resource type="ArrayMesh" path="res://bank_contour.obj" id="2"]\n','')
assert remove_nodes(bank,'FarBank') == remove_nodes(base,'FarBank')
water=text('water-tone.tscn').replace('load_steps=13','load_steps=12').replace('[ext_resource type="ShaderMaterial" path="res://water_tone.tres" id="2"]\n','').replace('material_override = ExtResource("2")','material_override = SubResource("river")')
assert water==base
marks=text('light-fragment.tscn').replace('load_steps=18','load_steps=12')
marks=re.sub(r'\[ext_resource type="ArrayMesh" path="res://mark_[^\n]+\n','',marks)
assert remove_nodes(marks,'LightFragment')==remove_nodes(base,'WaterMark')
assert 'TIME' not in text('water_tone.gdshader') and 'SCREEN_UV' not in text('water_tone.gdshader')
for i in range(6):
    vertices=[list(map(float,l.split()[1:])) for l in text(f'mark_{i}.obj').splitlines() if l.startswith('v ')]
    assert len(vertices)==7 and all(v[1]==-.075 for v in vertices)
manifest=json.loads(text('ARTIFACT_MANIFEST.json'))
for item in manifest['files']:
    b=(ROOT/item['path']).read_bytes()
    assert len(b)==item['size'] and hashlib.sha256(b).hexdigest()==item['sha256'],item['path']
print(f"Scope checks and {len(manifest['files'])} artifact hashes passed; no rendering assertion.")
