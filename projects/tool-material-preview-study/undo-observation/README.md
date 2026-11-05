# 재질 참조 한 건의 Undo/Redo 후속 관찰

Godot 4.6.3의 별도 사본에서 실제 Inspector 입력과 Ctrl+Z/Ctrl+Shift+Z를 사용했다. 코드를 수정하거나 신호를 강제로 보내지 않았다. 시작은 PairA=null, PairB=blue였다.

1. amber.tres를 PairA의 재질 필드에 드래그: A 두 판은 주황색, B 두 판은 파랑. UI로 저장한 결과가 `01-amber-saved.tscn`이다.
2. 실제 Undo: Inspector는 null, A는 기본 회색, B는 파랑으로 복귀. UI 저장 결과 `02-undo-saved.tscn`은 공개 시작 `../scenes/main.tscn`과 바이트 동일하다.
3. 실제 Redo: Inspector는 amber, A는 주황색, B는 파랑. UI 저장 결과 `03-redo-saved.tscn`은 01과 바이트 동일하다.

각 입력 직후 앱 단독 캡처에만 의존하지 않고, 이후 전체 화면에서 팝업이 없는 상태와 미리보기 갱신을 확인했다. 전체 화면에는 다른 앱이 있으므로 이미지는 이 공개 목록에서 제외했다. `result.json`은 저장 사본 해시와 관찰 범위를 기록한다.

세 사본에는 의도한 재질 참조 외 임시 material_override/복제 StandardMaterial3D가 없다. 원본 blue/amber 재질, GLB, preview 스크립트, pair 씬도 바이트 불변이다. 사본의 res:// 경로는 원래 연구 프로젝트 루트를 기준으로 한다. 이 폴더에서 독립 실행하는 씬이 아니며, 보존된 저장 증거이다. 직접 재현하려면 연구 프로젝트를 별도 복사하고 동일한 UI 절차를 수행한다. Save는 그 사본의 main.tscn을 덮어쓴다.

이것은 재질 참조 한 건의 Undo/Redo 및 저장 관찰이다. 색상 값 편집, 재import, 저장 후 실제 편집기 재개방, 일반적인 undo 안전성은 여전히 미검증이다. headless 직접 setter의 자동 changed 미관찰과 명시적 신호 계약은 기존 기록대로 유지한다. 제품 통합은 보류한다. 새 라이선스를 부여하지 않는다.

`INITIAL_STUDY_MANIFEST.json`은 후속 문서 갱신 전 초기 연구의 역사적 해시 목록이다. 현재 README에 대한 검증 목록이 아니며, 현재 전체 목록은 상위 STUDY_MANIFEST.json이다.
