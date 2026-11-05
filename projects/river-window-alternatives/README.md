# 창밖 강변 판독 · 세 독립 대안

**세 후보 모두 게임 통합 보류.** [앞선 독립 공간 연구](../river-window-study/README.md)의 같은 기준 씬에서 한 범주씩 바꿨다. 세 효과를 섞지 않았고 [실제 게임](../after-the-rain/README.md)의 원본·분기·8초 결말은 변경하지 않았다. 24초/40m는 연구 값이지 실제 게임 경로·시간표가 아니다.

## 무엇을 바꿨나

1. **먼 강둑 윤곽** (`bank.tscn`): 원래 FarBank의 직선 위쪽만 낮고 넓은 세 봉우리로 바꿨다. x=-30…100m, z=-82.5…-79.5m, 아래쪽y=-0.8m와 bank 재질은 유지했다. 기존 top1.2m에 약0…1.2m를 더한 완만한 윤곽이다. 1m 간격의 단일 OBJ(524정점/1,044삼각형)가 기존 box12삼각형을 대체한다. 가림이 풀린 뒤 윤곽 차이는 보이지만, 수면의 강 인지를 충분히 개선하지 못했다. 관찰한 화면에는 두드러진 톱니나 다리 가림은 없었다.
2. **수면의 넓은 명도 무늬** (`water-tone.tscn`): 원래 직선 강둑과 단색수면 형상을 유지하고 River 재질만 변경했다. 월드 XZ의13m·28m value noise를 혼합한다. 0.78/1.0/1.16은 명도 목표값이며 **smoothstep으로 연속 보간하므로 세 가지 이산 단계가 아니다.** 고정 base_color 입력과 roughness0.95를 사용하나 StandardMaterial→ShaderMaterial이므로 전체 렌더 경로의 비트 동일성을 주장하지 않는다. 먼 쪽으로 압축되는 무늬가 수평면 단서를 주었지만, 물인지 흐린 바닥인지 여전히 불확실했다. 화면에 붙인 무늬·유체·물리 반사가 아니며 시간에 따라 무늬 자체가 움직이지 않는다.
3. **적고 넓은 빛 조각** (`light-fragment.tscn`): 원래12개 작은 box표식만6개의 불규칙 평면7각형으로 바꿨다. 원래 warm 재질과 emission 설정을 유지하고 새 광원은 추가하지 않았다. y=-0.075m로 수면 윗면(-0.09m)보다15mm 위다. **양식화된 빛 표식이지 광학 반사가 아니다.** 정상 관찰각에서는 여전히 가는 황금 조각으로 보였고, 작은 부유물과 반사 사이 의미가 모호했다. 더 키워 성공처럼 만들지 않았다.

카메라·수면 위치/크기·난간·다리·조명·시간·나머지 원래 재질은 각 후보의 명시한 범위 밖에서 고정했다. 두 번째의 셰이더 연산, 첫 번째의 삼각형 수는 늘었다. FPS·GPU 시간·draw call은 측정하지 않았으며 개선을 주장하지 않는다. 외부 이미지/모델/폰트나 벡터 그림을 배경으로 쓰지 않았다. 직접 작성한 원시 기하·코드이며 새 포괄 라이선스를 부여하지 않는다.

## 실제 화면과 관찰 범위

[evidence](evidence/)에는 기준과 각 후보의 **0·12·19·24초 실제1180×812 JPEG 16개**를 원본 바이트 그대로 보존했다. 예: [기준24초](evidence/baseline-24.jpg), [강둑24초](evidence/bank-24.jpg), [명도24초](evidence/water-tone-24.jpg), [빛조각24초](evidence/light-fragment-24.jpg). 정지 시점은 검토 키로 직접 이동했다. 확대 캡처나 합성 이미지를 정상 화면 판독 성공의 근거로 삼지 않았다.

기준과 강둑·명도 후보는 각각 정상24초 연속 재생도 확인했다. 캡처 구간은 각각26.137/26.821/26.493초, 각140장 표본이다. 이는 프레임레이트 측정이나 모든 렌더 프레임의 전수 검사와 다르다. 마지막 빛조각 후보는 정지 비교만 했다. 전 각도·전 해상도·장시간 재생 검증이 아니다. 관찰한 시점에서 창틀/난간의 가림은 유지됐지만, 이것만으로 모든 가림 상태를 증명하지 않는다.

판정은 제작 과정의 정성 관찰이다. **설명을 모르는 독립 관찰자 검사, 강 인지 성공률, 통계적 유의성, FPS 검사는 실시하지 않았다.** 무늬의 수평면 단서만 상대적으로 나아 보였으며 세 후보 모두 자연스러운 강변의 충분한 판독 성공으로 채택하지 않았다.

## 실행과 재현

Godot4.6.3 Standard/Compatibility, 실제 화면은 Mesa llvmpipe·CPU2 제한으로 확인했다. 오디오는 없고 Dummy 드라이버를 사용했다.

```sh
godot --editor --path . --import
godot --path . --rendering-method gl_compatibility res://baseline.tscn
godot --path . --rendering-method gl_compatibility res://bank.tscn
godot --path . --rendering-method gl_compatibility res://water-tone.tscn
godot --path . --rendering-method gl_compatibility res://light-fragment.tscn
python3 verify_variants.py
godot --headless --path . --script res://test_study.gd
```

Space 재생/정지, R 초기화, 1=0초/2=12초/4=19초/3=24초 검토 위치, Escape 종료. HUD의1/2/3 안내는 이전 연구 그대로이며4도 지원한다. 검토키는 순간이동하는 QA 기능으로 정상 연속 이동과 구분한다. 24초 위치는 끝점에 고정되며 PLAY 표시는 선택된 재생 상태다.

저장 scene/OBJ/shader 자체가 실행 입력이다. Python 검사는 원본이나 사본을 쓰지 않는다. Godot import/실행은 .godot 캐시·사용자 데이터·로그를 생성할 수 있으므로 별도 작업 사본에서 실행하는 편이 좋다. 엔진 검사는 직접 process/키 핸들러 호출에 의한 상태 검사이지 실제 키 dispatch·GPU·SceneTree pause 검사가 아니다. 공개 사본의 새 import 후 headless 상태 검사24개가 실패0으로 통과했고, Python 변경 범위·전체 산출물 해시 검사도 통과했다. 실제 native에서VSync 변경 미지원 경고가 있었으며, 일부 초기 import의 사용자 데이터/editor settings 저장 오류와 실제 화면 관찰을 구분한다. 모든 환경에서 무경고 실행한다고 주장하지 않는다.

## 공식 문서와 설계 판단의 경계

2026-11-03에 확인한 Godot4.6 문서:
- [Spatial shaders](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html): MODEL_MATRIX로 모델 정점을 월드 공간으로 변환하고 varying으로 fragment에 전달한다. 이 연구의 무늬 좌표는 그 방식으로 계산하며 SCREEN_UV와 TIME을 쓰지 않는다. 기본 깊이 검사와 불투명 경로를 유지한다.
- [Standard Material3D](https://docs.godotengine.org/en/4.6/tutorials/3d/standard_material_3d.html): 노드 material_override의 적용 범위와 기본 불투명 재질을 설명한다. 여기서는 수면 노드만 재질을 대체하고 별도 투명 화면 레이어를 추가하지 않았다.

문서는 엔진 동작의 근거이지 강의 시각적 판독 성공을 보증하지 않는다. 낮은 강둑·넓은 명도 무늬·불규칙 표식이 도움이 될 것이라는 가설과 위의 기각 판단은 이 연구의 관찰이며 공식 문서의 결론이 아니다. 타인 이미지나 긴 인용문을 복제하지 않았다.
