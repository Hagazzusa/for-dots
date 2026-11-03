# 재질 미리보기 최소 샌드박스

두 판짜리 독자 GLB와 두 인스턴스만 사용한 Godot 4.6.3 연구다. 게임 자산을 참조하지 않으며 제품 적용은 보류했다. 새 라이선스를 부여하지 않는다.

## 확인한 범위

- `@tool`의 최초 편집기 로드에서 네 판의 복제 재질이 보였다.
- 실제 편집기에서 amber 리소스를 PairA에 드래그하자 A의 두 판만 주황색, B는 파란색으로 남았다. Clear 후 A만 기본 회색으로 복귀했다.
- 그 상태를 실제 Save & Close로 저장했다. `main.tscn`에는 A의 `preview_material = null`이 저장됐고, 임시 `material_override`나 복제 StandardMaterial3D는 직렬화되지 않았다. 에디터가 추가한 UID/unique_id/정규화된 transform 표기는 별개다.
- headless 15검사는 명시적 `emit_changed()` 계약, pane별 복제, 공유 원본의 의도된 양쪽 갱신, 교체/null, 중복 연결 방지, detach/reattach, pack/save/reopen/free를 검사한다. 이 결과는 실제 Inspector undo 검증이 아니다.

## 발견한 실패와 수정

처음 `_ready()`에만 연결했을 때 같은 노드의 detach→reattach 후 changed 신호 구독이 끊겼다. `_enter_tree()` 재연결, `_exit_tree()` 해제 및 이전 deferred 작업을 무효화하는 epoch로 수정했다. 실험에서 remove_child가 owner를 지우므로 테스트는 원래 owner를 명시적으로 복원한다. 제품 코드는 변경하지 않았다.

이 엔진의 headless 직접 `StandardMaterial3D.albedo_color` 대입은 자동 changed 알림을 관찰하지 못했다(refresh 증가 0). 명시적 신호를 넣은 통과 결과로 이를 덮지 않는다. 공유 템플릿 편집이 두 인스턴스에 반영되는 것과, 복제된 pane 상태가 서로 독립인 것은 다른 계약이다. 얕은 duplicate는 향후 중첩 Resource까지 분리한다는 보장이 아니다.

## 미검증과 결론

초기 실험에서는 실제 Inspector 색상 값 편집, undo/redo, 편집기 재개방 및 재import의 신뢰할 만한 완료 증거를 확보하지 못했다. 이후 [한 건의 재질 참조 Undo/Redo 후속 관찰](undo-observation/README.md)에서 참조 교체와 되돌리기·다시 실행 및 각 단계 저장만 확인했다. 색상 값 편집·편집기 재개방·재import 및 일반적인 undo 안전성은 여전히 미검증이다. 창별 캡처에서 popup이 누락되고 입력 결과 확인이 지연되는 문제가 있어, 시도 자체를 성공이나 Godot 결함으로 판정하지 않는다. 저장 한 번에서 오염이 없었다는 결과를 모든 편집 작업의 안전성으로 확대하지 않는다. 복잡한 플러그인이나 제품 변경으로 우회하지 않는다.

따라서 현재 결과는 작은 수명/신호 실험으로만 보존한다. 편집기 조작 전체 gate가 충족되지 않아 게임의 @tool 적용 근거는 부족하다. 성능/일반적 undo 안전성도 주장하지 않는다.

## 재현

Godot 4.6.3에서 project.godot를 열면 저장된 PairA는 null, PairB는 파랑이다. 이는 마지막 UI 저장 증거이며 headless 테스트는 실행 사본의 두 입력을 파랑으로 초기화한다.

`godot --headless --path . --script res://tests/preview_test.gd -- /absolute/writable/output.tscn`

마지막 경로는 테스트가 쓰고 다시 읽는 별도 사본이다. 기존 파일을 선택하면 덮어쓰므로 새로운 경로를 사용한다. 쓰기 가능한 XDG 데이터/캐시/설정 및 임시 디렉터리가 필요하다. 기본 환경 실행 한 번은 캐시/사용자 경로 문제로 중단됐고, 쓰기 가능한 디렉터리로 설정한 최종 실행은 15/0이었다. 원본 재질/GLB에는 쓰지 않는다. 편집기에서 Save는 샌드박스 씬/리소스를 변경할 수 있다.

## 근거

- [Godot 4.6: 편집기에서 코드 실행](https://docs.godotengine.org/en/4.6/tutorials/plugins/running_code_in_the_editor.html)
- [Godot 4.6 Resource](https://docs.godotengine.org/en/4.6/classes/class_resource.html)

UI 관찰과 headless 결과는 구분하며, 제품 자산·게임 동작은 이 연구에 포함하지 않는다.
