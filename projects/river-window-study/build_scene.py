from pathlib import Path
out=['[gd_scene load_steps=12 format=3]','[ext_resource type="Script" path="res://study.gd" id="1"]']
colors={'wall':(.19,.25,.27),'trim':(.055,.08,.09),'warm':(.65,.43,.18),'river':(.24,.39,.43),'bank':(.075,.105,.12),'glass':(.11,.19,.22),'cream':(.22,.21,.17),'road':(.09,.12,.14)}
for n,c in colors.items():
 out += [f'[sub_resource type="StandardMaterial3D" id="{n}"]',f'albedo_color = Color({c[0]}, {c[1]}, {c[2]}, 1)','roughness = 0.95']
 if n=='warm':out+=['emission_enabled = true','emission = Color(0.75,0.42,0.12,1)','emission_energy_multiplier = 0.6']
out+=['[sub_resource type="BoxMesh" id="box"]','size = Vector3(1,1,1)','[sub_resource type="Environment" id="env"]','background_mode = 1','background_color = Color(0.045,0.075,0.105,1)','ambient_light_source = 2','ambient_light_color = Color(0.65,0.75,0.85,1)','ambient_light_energy = 0.8','tonemap_mode = 0','[node name="RiverWindowStudy" type="Node3D"]','script = ExtResource("1")','[node name="Environment" type="WorldEnvironment" parent="."]','environment = SubResource("env")','[node name="World" type="Node3D" parent="."]']
def box(n,pos,size,mat,parent='World'):
 out.extend([f'[node name="{n}" type="MeshInstance3D" parent="{parent}"]',f'position = Vector3{pos}',f'scale = Vector3{size}','mesh = SubResource("box")',f'material_override = SubResource("{mat}")','cast_shadow = 0'])
box('Road',(20,-.15,0),(100,.2,14),'road')
box('River',(38,-.15,-43),(100,.12,76),'river')
box('FarBank',(35,.2,-81),(130,2,3),'bank')
for i,x in enumerate([-6,2,10]):
 box(f'Shop{i}',(x,3.3,-9),(7.5,6.6,6),'wall')
 box(f'ShopWindow{i}',(x,1.8,-5.94),(5,2,.05),'glass')
 box(f'ShopHeader{i}',(x,3.1,-5.85),(6.2,.2,.2),'trim')
 box(f'ShopLight{i}',(x,3,-5.7),(2,.08,.06),'warm')
box('LastPier',(14.1,2,-6.3),(.7,4,1),'trim')
box('BankTop',(43,.38,-7),(58,.1,.35),'bank')
for i in range(16):box(f'Rail{i}',(15+i*3.7,.22,-7),(.08,.44,.08),'trim')
box('BridgeDeck',(42,1.3,-42),(48,.4,2),'bank')
for i,x in enumerate([22,34,46,58]):
 box(f'BridgePier{i}',(x,.3,-42),(.5,2,1),'bank')
 box(f'LampPost{i}',(x,2.4,-42),(.12,2,.12),'trim')
 box(f'Lamp{i}',(x,3.45,-42),(.8,.16,.35),'warm')
 # Authored broad color strokes, not physical reflection.
 for j in range(3):box(f'WaterMark{i}_{j}',(x,-.075,-38+j*4),(1+j*.45,.025,.22),'warm')
out+=['[node name="RideRig" type="Node3D" parent="."]','[node name="Camera" type="Camera3D" parent="RideRig"]','position = Vector3(0,1.7,2)','current = true','fov = 67.0','near = 0.05']
for n,p,s in [('Left',(-1.15,1.7,1),( .75,1.7,.12)),('Right',(1.15,1.7,1),(.75,1.7,.12)),('Top',(0,2.44,1),(3,.25,.12)),('Bottom',(0,.98,1),(3,.3,.12))]:box(n,p,s,'cream','RideRig')
out+=['[node name="UI" type="CanvasLayer" parent="."]','[node name="Label" type="Label" parent="UI"]','offset_left = 18.0','offset_top = 16.0','theme_override_colors/font_color = Color(1,1,1,1)','theme_override_colors/font_shadow_color = Color(0,0,0,1)','theme_override_constants/shadow_offset_x = 2','theme_override_constants/shadow_offset_y = 2','theme_override_font_sizes/font_size = 19']
Path(__file__).with_name('main.tscn').write_text('\n'.join(out)+'\n')
