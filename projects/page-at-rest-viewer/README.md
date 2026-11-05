# 머무는 페이지 — 독립 3D 뷰어

[원본 조형물](../page-at-rest/README.md)의 실제 메시를 키보드로 관찰하는 Godot 4.6 프로젝트입니다. 생성 콘셉트나 Blender 렌더를 배경 이미지로 붙이지 않습니다. 원본 FreeCAD·STEP·Blender 파일과 기존 게임은 수정하지 않습니다.

## 실행과 조작

Godot 4.6 이상에서 `project.godot`를 열고 실행하거나:

```sh
godot --path .
```

- 방향키: 좌우 회전·위아래 시점
- `+` / `=` / 숫자패드 `+`: 확대, `-` / 숫자패드 `-`: 축소
- `L`: 따뜻한 관찰광 100% → 45% → 0%; 환경광과 보조광은 유지
- `R`: 기본 카메라와 100% 조명 복원
- 창 닫기: 종료. 마우스 캡처·이동은 필요하지 않습니다.

최소 창은 640×480입니다. 기본 1100×800, 좌우 ±1.3 rad·상하 0.1–0.9 rad 안에서 관찰합니다. 명목 줌 범위 0.42–1.2 m보다 물체·안내문을 함께 담는 거리를 우선하므로, 세로로 긴 창에서는 1.2 m를 넘을 수 있습니다. 낮은 시점에서는 단순한 바닥과 배경의 경계가 보입니다. 창 포커스가 없으면 카메라 키 입력을 처리하지 않습니다.

## 장면 책임

- `scenes/viewer.tscn`: 조형·바닥·환경·관찰광·한국어 도움말을 저장한 최상위 구성
- `scenes/page_study.tscn`: GLB 인스턴스와 명시적인 종이 재질 근사. 종이 두 메시만 개별 복제 재질로 덮어씁니다.
- `scenes/view_rig.tscn`: 카메라와 Inspector 설정. 실제 아홉 메시의 72개 AABB 모서리를 이용해 화면 여백을 계산합니다.
- `scripts/viewer.gd`: 조명 단계와 초기화만 연결. 별도 애니메이션·퀘스트·오디오는 없습니다.

GLB는 9메시·199,840삼각형·약 3.63 MB입니다. 자동 LOD 생성은 꺼 두어 얇은 종이 경계가 임의 단순화되지 않게 했습니다. 기존 Noto Sans CJK와 라이선스를 포함합니다. 새 외부 텍스처·플러그인은 없습니다.

## 실시간 재질의 범위

종이는 불투명 shader의 `BACKLIGHT` 근사이며 강도 0.35, alpha·emission을 쓰지 않습니다. 두 종이의 그림자 투사를 끄고, 받침·책·황동 등 다른 물체의 그림자는 유지했습니다. 이는 자기그림자 얼룩을 피하기 위한 단순화로, 실제 종이 투과·산란·접힌 표면 간 차폐를 재현하지 않습니다. 종이의 작은 무늬와 목재의 PBR 색도 원본 Cycles 절차적 재질과 동일하지 않습니다. 조형물과 책의 형상을 관찰하는 용도이지 원본 렌더·조명 성능·실물 전기·제작 안전 검증이 아닙니다.

[자산 출처와 변환 검증](ASSET_README.md)은 원본→GLB 검증과 엔진 수입 이후 검증을 구별합니다.

## 검증과 재현

```sh
python3 verify_asset.py
godot --headless --path . --audio-driver Dummy --script res://tools/test_viewer.gd
# 쓰기 가능한 절대 출력 경로를 지정합니다.
godot --headless --path . --script res://tools/build_pack.gd -- /tmp/page-viewer.pck
godot --headless --main-pack /tmp/page-viewer.pck --audio-driver Dummy --script "$PWD/tools/test_viewer.gd" -- /tmp/page-viewer-pack-tests.json
```

최초 실행 전 Godot 편집기에서 import하거나 `godot --headless --editor --path . --import`를 실행합니다. 검사 스크립트는 JSON 결과를 쓰며, pack 도구는 런타임 의존성만 포함한 PCK와 파일 목록을 씁니다. QA·export 도구·원본 연구 문서·작업 로그는 pack에 넣지 않습니다.

- source와 PCK에서 각각 1,990개 assertion 통과. 1100×800, 640×480, 640×900의 아홉 시점 표본을 검사했습니다. 모든 해상도·GPU를 증명하지는 않습니다.
- 실제 데스크톱에서 논리 방향키 누름/해제, 양쪽 회전·상하 한계, 확대/축소, L 세 단계, R 복원, 작은 창 도움말을 확인했습니다. native 캡처는 `qa/native_preview.png`, `qa/native_small.png`입니다.
- 여러 인스턴스 검사는 카메라/조명/재질 상태의 독립성을 뜻하며, 같은 viewport에서 여러 UI와 카메라를 동시에 조작하는 기능을 뜻하지 않습니다.
- Compatibility/llvmpipe에서 관찰했습니다. FPS 개선이나 다른 GPU와의 시각적 동등성은 측정하지 않았습니다. V-Sync 변경 미지원 경고는 기능 오류와 구분합니다.
