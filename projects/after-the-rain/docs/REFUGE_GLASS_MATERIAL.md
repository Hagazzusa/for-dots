# 쉼터 유리 재질을 Inspector에서 설정하기

`scenes/neighborhood_extension.tscn`의 `GlassRefuge` 노드에는 `glass_material`이라는 `StandardMaterial3D` 설정이 있습니다. 기본값은 저장된 `config/refuge_glass.tres`입니다. 이전 스크립트에 고정되어 있던 색·알파·거칠기·금속성·양면 설정을 Resource로 옮겼습니다. 노드 구성, 유리 형상, 게임 규칙이나 기본 외형을 바꾸는 작업이 아닙니다.

기본 색은 `(0.55, 0.74, 0.82, 0.14)`, 알파 투명, 거칠기 0.10, 금속성 0.05, 양면 렌더입니다. 유리 그림자는 이전처럼 꺼 둡니다. 설정을 비우면 기본 Resource로 돌아갑니다.

실행 시 24개 유리판마다 template를 `duplicate()`하여 별도 재질을 적용합니다. 원본 Resource를 수정하지 않으며, 한 유리판이나 한 쉼터 인스턴스의 변경이 다른 판·인스턴스로 번지지 않습니다. 현재는 값만 든 재질입니다. 나중에 texture 같은 하위 Resource를 넣는다면 얕은 복제가 그 하위 Resource까지 독립화한다는 뜻은 아니므로 별도 검토가 필요합니다.

## 확인한 범위

- Godot 4.6.3, Compatibility에서 전체 51개 suite가 통과했습니다.
- `tests/refuge_glass_material.gd`: 201개 검사 통과. 두 인스턴스의 48개 재질 고유성, 기본값, 판/인스턴스 변경 격리, 기본·사용자 설정 template 불변, null fallback, 해제 후 재생성을 확인했습니다.
- 191파일 PCK를 소스 없는 별도 경로에서 실행해 정상/`--test` 양쪽의 입력과 fixture 제외를 확인했습니다. 동일 재질 검사를 외부 검사 스크립트로 PCK에 적용해 201개 검사도 다시 통과했습니다.
- 임시 native 실행에서 게임 진행을 멈추고 같은 카메라 `(7, 1.6, -3.5)`로 기존 코드와 같은 값으로 만든 재질과 새 저장 재질을 번갈아 적용했습니다. 전환 로그와 1180×812 실제 캡처 두 장의 디코딩 픽셀이 같았습니다. 한 고정 시점 비교이며 모든 시점·드라이버에서 같은 결과를 보장하지 않습니다. VSync 미지원 경고는 있었지만 해당 실행에서 script/shader 오류는 발견하지 못했습니다.

이 변화로 Inspector에 설정 Resource가 드러나지만, 실제 imported mesh override는 여전히 `_ready()`에서 적용됩니다. `@tool`을 추가하지 않았으며 **편집기 3D 미리보기가 런타임과 같아졌다고 주장하지 않습니다**. 에디터 UI의 저장/재개방 수동 조작은 이번 검증에 포함하지 않았습니다. 성능 개선을 측정하거나 주장하지 않습니다.

공식 [scene organization](https://docs.godotengine.org/en/4.6/tutorials/best_practices/scene_organization.html)과 [Resource](https://docs.godotengine.org/en/4.6/classes/class_resource.html) 안내에 따른 작은 설정 분리입니다. runtime 생성 자체가 엔진에서 금지된 것은 아니며, 절차적 히터 소리나 꽃집 상태 구조를 불필요하게 분리하지 않았습니다.
