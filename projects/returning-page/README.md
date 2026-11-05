# 돌아올 페이지

집에 돌아와 읽던 책을 펼치면, 작은 정류장 하나가 기다리고 있다.
오늘은 여기까지. 다음 문장은 돌아온 뒤에.

조용한 버스와 집의 이야기를 책 사이의 작은 황동 물건으로 옮겼다. 창 하나, 실을 위한 구멍 하나. 장식과 글자를 덜어내고, 밝은 종이 위에 오래 머무는 색을 골랐다. 실은 달지 않았다. 선택할 수 있는 작은 여백으로 남겼다.

## 형태

- 외곽: 90 × 25 × 0.7 mm, 모서리 반지름 3 mm.
- 평면 가장자리 라운딩: 0.14 mm.
- 정류장 창: 15 × 13 mm, 모서리 반지름 1.5 mm.
- 실 구멍: 지름 2.8 mm.
- 재료 표현: 무광에 가까운 황동. 렌더의 재질이며 실제 합금 사양이 아니다.

이것은 **가상 디자인 연구**다. 제조 도면, 제품 안전 인증, 강도 검증이나 실제 책과의 호환성 시험을 제공하지 않는다. 얇은 금속이 책이나 손에 미치는 영향, 실제 모서리 마감, 가공 공차는 따로 확인해야 한다. 종이는 연출용 메시이며 실제 변형 시뮬레이션이 아니다.

## 파일과 재현

- `concept.svg`: 첫 실루엣 스케치. 최종 CAD의 대체물이 아니다.
- `cad/Returning_Page.FCStd`: FreeCAD 기본 형상, 라운딩, 차집합으로 만든 편집 가능한 원본.
- `cad/Returning_Page.step`: 최종 단일 솔리드 교환 파일.
- `cad/bookmark_mesh.json`: FreeCAD 최종 솔리드의 테셀레이션. Blender에서 이 좌표를 그대로 가져왔다.
- `Returning_Page.blend`: 책과 빛을 포함한 렌더 장면.
- `renders/draft.png`: 최종 렌더 전 실제 CAD 메시로 만든 저비용 초안.
- `renders/returning_page_final.png`: 최종 정물 이미지.
- `cad/validation.json`, `blender_validation.json`: 기하·스케일 검증.

FreeCAD 1.0의 시스템 Python ABI를 사용한다:

```sh
PYTHONPATH=/usr/lib/freecad-python3/lib /usr/bin/python3 build_freecad.py
blender --background --factory-startup --threads 2 --python build_blender.py -- --draft
blender --background --factory-startup --threads 2 --python build_blender.py
```

FreeCAD에서 `Blank`의 Length/Width/Height, 원형 구멍의 Radius, 각 라운딩과 창 형상을 편집할 수 있다. 큰 치수 변경은 창 위치와 라운딩의 재검토가 필요하다. 원본 재개방 후 Width를 90에서 92 mm로 바꿔 유효한 재계산과 부피 증가를 확인했다. 저장본은 90 mm다.

STEP 재개방의 유효 솔리드와 부피를 확인했다. mm→m 변환은 Blender에서 한 번만 적용하며 정점과 삼각형을 대조했다. 책 위와 금속 아래는 z=10.1 mm에서 맞닿는다. 위 종이의 바닥은 금속 윗면 10.8 mm보다 낮지 않아 양의 부피 겹침이 없다. 책 밖으로 나온 26.5 mm 부분은 지지되지 않은 가상 연출이다. 물리 검증을 뜻하지 않는다.

외부 이미지, 텍스처, 글, 브랜드, 개인 정보 없이 코드·기본 도형·절차적 재질로 제작했다. 이미지 생성 모델은 사용하지 않았다. 렌더는 Blender 4.3.2 Cycles CPU, 2스레드, 디노이징 없이 생성했다.

## 검증과 재생성 범위

`python3 verify_bundle.py`는 저장된 해시와 메시의 유한 좌표·닫힌 모서리 연결·부피 오차를 읽기 전용으로 검사합니다. 생성 스크립트는 같은 경로의 CAD·메시·Blender 장면·렌더·검증 보고서를 다시 씁니다. `inspect_blend.py`도 장면을 읽은 뒤 검증 JSON을 기록하므로, 원본을 보존하려면 별도 사본에서 실행하세요. 문서의 재개방·치수 수정 검증은 제작 단계의 자동 검사이며 실제 제조 시험을 뜻하지 않습니다.

공개 사본에서는 Blender의 저장 렌더·파일 탐색 경로를 상대 경로로 정리하고 최종 PNG의 텍스트 메타데이터를 제거했습니다. 저장 시 사용하지 않는 기본 재질 하나가 빠졌지만, 장면의 객체 변환·메시·할당 재질과 유지된 재질 입력의 비교 및 PNG의 압축 이미지 데이터·디코딩 픽셀 비교는 일치했습니다. 원본과 공개 사본의 해시는 `provenance.json`에 구분해 남겼습니다.
