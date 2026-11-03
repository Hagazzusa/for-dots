# 머무는 페이지 · 실시간 파생 자산

`assets/page_at_rest.glb`는 [원본 작품](../page-at-rest/README.md)의 실제 Blender 메시에서 만든 파생본입니다. 생성 콘셉트나 Cycles 렌더를 평면 배경에 붙인 것이 아닙니다. 원본 CAD·Blender·렌더·C2PA 이미지는 변경하지 않았습니다.

## 원본에서 보존한 것

- 호두나무 받침, 황동 cradle 두 개, **실제 두께가 있는 닫힌 종이 곡면 두 개**, 린넨 책 4부품.
- **9개 메시 / 199,840개 삼각형 / 3,632,556bytes GLB**. 첫 파생본은 리토폴로지·decimation·Draco 손실 압축 없이 원본 평가 메시를 유지합니다.
- 원본 cyclorama, 광원·카메라·애니메이션은 제외했습니다. 이미지·텍스처·외부 버퍼가 없는 self-contained GLB입니다.
- 실행 전후 원본 `.blend`의 SHA-256은 `4d0ee8b68c98381dfb89e68bd77b3b85ef6d29c716d97d6c2e78f7893937a72e`로 같았습니다.

약20만 삼각형은 정확한 최초 이식의 비용입니다. 파일이 작다는 것만으로 모든 하드웨어에서 빠르다고 주장하지 않습니다. 실제 Godot 실행과 조작 검사는 뷰어의 QA 기록에서 구별합니다.

## 좌표와 계약

- 미터, root scale `(1,1,1)`. Blender `(x,y,z)` → glTF/Godot `(x,z,-y)`.
- 원점은 타원 받침 아래의 중심, 책상 접촉면은 `Y=0`입니다.
- 조형물 범위: `(-0.121006, 0, -0.038987)` ~ `(0.114014, 0.207007, 0.038990)`.
- 책 포함 범위: `(-0.227500, 0, -0.160000)` ~ `(0.114014, 0.207007, 0.038990)`.
- 원본 카메라 `(0.33,0.315,0.74)`, target `(0.023,0.113,-0.025)`, 세로 FOV 약20°. 뷰어는 UI와 창 비율에 맞춰 별도로 프레이밍합니다.
- 원본 숨은 면광원의 중심에 대응하는 위치는 `(0,0.073,-0.042)`입니다. Godot의 점광원은 이 면광원과 광학적으로 동등하지 않습니다.

`PageSculpture` 그룹: `WalnutBase`, `LeftBrassCradle`, `RightBrassCradle`, `LeftPage`, `RightPage`.
`LinenBook` 그룹: `BookLowerCover`, `BookPages`, `BookUpperCover`, `BookSpine`.

그룹 변환은 identity이며 꼭짓점은 받침 기준 좌표입니다. 조형물 관찰용이며 각 부품의 CAD 편집 피벗을 따로 제공하지 않습니다. 종이 두께와 얇은 황동을 보호하기 위해 Godot 자동 LOD는 끄는 방향으로 검증합니다.

## 종이는 어떻게 보이는가

GLB의 기본 재질은 모두 **불투명 core metallic/roughness PBR 근사**입니다. 원본 절차적 요철과 광선 추적 재질을 베이크하거나 복원한 것이 아닙니다.

`assets/materials/paper_backlight.tres`는 실제 종이 메시 위에 연결할 별도 Godot shader입니다. 불투명 depth 경로를 유지하고, 약한 절차적 색 결 및 `BACKLIGHT` 항을 사용합니다. **ALPHA나 EMISSION은 쓰지 않습니다.** 따라서 종이 뒤의 사물이 투명하게 비치거나, 실제 두께에 따른 산란·흡수·굴절을 계산하지는 않습니다.

Godot4.6은 BACKLIGHT를 저렴한 subsurface-scattering 근사로 설명합니다. 이 작품에서는 빛의 방향·세기 변화에 반응하는 따뜻한 종이 인상을 얻기 위한 시각적 근사입니다. [Godot4.6 Spatial shader](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html), [BaseMaterial3D backlight](https://docs.godotengine.org/en/4.6/classes/class_basematerial3d.html#class-basematerial3d-property-backlight-enabled)

실제 native draft에서 얇은 닫힌 종이의 자기그림자가 사각 줄무늬를 만들었습니다. 따라서 **종이 두 메시의 cast-shadow를 끄는 단순화를 채택**했습니다. 받침·황동·책은 그대로이며, 실제 투과 그림자를 계산한 것은 아닙니다. 초기 노란 과포화를 낮추기 위해 BACKLIGHT strength는1.0에서0.35로 줄이고 뷰어 조명도 함께 조정했습니다. 최종 화면과 키보드 반응의 범위는 [뷰어 README](README.md)와 QA에 기록합니다. 금속은 diffuse ambient만으로 검어질 수 있어 sky radiance·약한 fill을 유지합니다.

Compatibility는 HDR이 아니며 색 정밀도와 광학 기능이 원본 Cycles와 다릅니다. 이 파생본이 원본 렌더와 동일한 외관이나 물리적 광량을 보장하지 않습니다. [Godot4.6 렌더링 한계](https://docs.godotengine.org/en/4.6/tutorials/3d/3d_rendering_limitations.html)

## 재현과 검증

```sh
mkdir -p work
TMPDIR="$PWD/work" blender -b -t 2 --python-exit-code 1 \
  --python export_from_blender.py -- --source ../page-at-rest/A_Page_at_Rest.blend

# GLB는 바꾸지 않고 원본 평가 메시와 다시 대조합니다.
TMPDIR="$PWD/work" blender -b -t 2 --python-exit-code 1 \
  --python export_from_blender.py -- --source ../page-at-rest/A_Page_at_Rest.blend --verify-only

python3 verify_asset.py
```

Exporter는 원본을 저장하지 않습니다. `--verify-only`도 검사 JSON을 갱신하므로 완전한 읽기 전용 명령은 아닙니다. `verify_asset.py`의 기본 모드는 파일 해시·GLB 구조를 읽기만 하고, `--freeze`일 때만 자산 manifest를 갱신합니다.

실제 GLB 바이너리의 node transform·buffer·index를 읽어 모든 위치 및 **방향을 보존한 삼각형 위치 집합**을 0.1µm 좌표 반올림 기준으로 대조했습니다. 단순히 삼각형 개수가 같다고 이식을 검증한 것은 아닙니다. 양의 부호 체적, 유한한 단위 법선, 재질 다섯 개, 외부 의존성 부재도 확인했습니다. `export_audit.json`은 **GLB까지의 수치 검사**이며 Godot import·shader·실제 창 조작의 성공을 대신하지 않습니다.

원본 생성 콘셉트와 C2PA는 원작 폴더에 그대로 남고 이 GLB에는 이미지 픽셀이 없습니다. 전기·발열·구조·제조·실물 안전 검증 모델이 아닙니다.
