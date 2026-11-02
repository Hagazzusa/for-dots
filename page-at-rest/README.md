# 머무는 페이지 · A Page at Rest

두 장의 얇은 곡면이 넓게 벌어지고, 그 뒤의 따뜻한 빛이 책상에 머무는 작은 가상 조형물입니다. 낮은 호두나무 타원 받침과 황동 cradle 두 개, 뒤편의 작은 린넨 책 한 권만 놓았습니다.

이미지 콘셉트의 날개 같은 인상을 독립적인 수학 곡면으로 해석했습니다. 이미지의 정확한 치수·형상 복원이나 실물 제품 설계가 아닙니다.

## 제작 경로

### 초기 source-only 스냅샷 안내

초기 원격 백업에는 생성 스크립트·매개변수·검증 도구·설명·정확한 콘셉트 프롬프트만 포함합니다. 최종 렌더, Blender/CAD/메시 산출물은 아직 포함하지 않습니다. 생성 콘셉트 PNG 원본은 작업 환경의 별도 보존 원본이며 이후 전체 작품 패키지에 C2PA 그대로 포함할 예정입니다. 빌드에 이미지 파일을 텍스처로 읽어들이지 않으므로 이미지 없이도 아래 기하 생성은 실행할 수 있습니다. 반드시 FreeCAD → Blender 순서로 실행하세요.

1. `reference/concept_prompt.txt`의 정확한 프롬프트로 만든 이미지 콘셉트를 눈으로 확인했습니다.
2. `parameters.json`과 `geometry.py`가 mm 단위의 공통 기하 정의입니다.
3. `build_freecad.py`는 **FreeCAD 1.0.0**의 네이티브 Ellipse → Extrusion → Fillet, Circle → Loft → MultiFuse를 사용합니다. **49개 네이티브 parametric 객체**로 만든 FCStd이며 외부 Python proxy를 복원할 필요가 없습니다.
4. 받침과 두 지지부의 실제 FreeCAD shape를 메시 JSON으로 내보냅니다. **Blender 4.3.2**가 해당 정점과 삼각형을 그대로 읽고 mm → m 변환을 **한 번** 적용합니다. Blender에서 받침·지지부를 다시 모델링하지 않습니다.
5. Blender에서 공통 곡면 정의로 두께 있는 종이, 절차적 재질, 카메라, 면광원을 추가합니다. 종이에는 emission이 없고 compositor bloom이나 칠해 넣은 빛무리를 사용하지 않습니다.

## 재현

프로젝트 폴더에서 실행합니다. 이 환경의 FreeCAD 모듈 ABI는 Python 3.13입니다.

```sh
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=2 OMP_NUM_THREADS=2 \
PYTHONPATH=/usr/lib/freecad-python3/lib /usr/bin/python3 -B build_freecad.py
blender --background --factory-startup --threads 2 --python build_blender.py -- --draft
# 최종: --draft 없이 실행 (1200 × 800, 128 samples)
blender --background --factory-startup --threads 2 --python build_blender.py
```

다른 설치 위치·FreeCAD Python ABI에서는 실행 명령의 경로를 조정해야 합니다. 렌더는 CPU 2 threads로 직렬 수행합니다.

두 앱은 실시간 연결이 아닙니다. 공통 매개변수를 바꿨다면 FreeCAD 내보내기와 Blender 가져오기를 순서대로 다시 실행하세요. FCStd의 native 치수·단면은 편집 가능하지만 그 변경이 이미 저장된 Blender 메시를 자동 갱신하지는 않습니다. 설치된 Blender 빌드에는 OpenImageDenoise가 없어 denoising을 사용하지 않습니다.

## 기하 확인 범위

- FreeCAD 최종 부품 3개는 각각 유효한 단일 solid입니다.
- FCStd 재개봉 및 STEP 재독해 후 유효성을 확인합니다.
- 두 황동 부품끼리는 겹치지 않습니다.
- 황동 발은 나무 받침에 0.5mm, 종이 밑단은 cradle에 약 0.12mm 의도적으로 들어갑니다. 이는 가상 장면의 시각적 접촉을 분명히 하기 위한 얕은 자리이며 접합·제조 공차 검증이 아닙니다.
- Blender는 전송 정점 오차, 유한 좌표, 닫힌 종이 메시, 종이와 지지부 접촉이 밑단에만 있는지, 기타 부품 간 간섭을 확인합니다.
- 자세한 수치는 `cad/geometry_validation.json`, `blender_validation.json`에 기록합니다.

**전기·발열·구조·실물 제작·제조 공차·안전 인증을 검증한 설계가 아닙니다.** 면광원은 화면의 빛을 만드는 렌더 요소이며 실제 광원·회로·열 관리 구조를 모델링하지 않았습니다.

## 출처와 보존

모든 모델·스크립트·절차적 재질은 이 작품을 위해 독립 제작했습니다. 생성 이미지와 정확한 프롬프트는 `reference/`에 보존합니다. 원본 이미지의 C2PA `caBX` 청크는 제거하지 않습니다. 외부 텍스처, 상업 제품 CAD, 타인 모델을 사용하지 않았습니다. 상세 이력은 `provenance.json`을 참조하세요.

현재 렌더 단계와 검증 결과는 제작 중 갱신됩니다.

이 초기 사본의 `SOURCE_FREEZE_MANIFEST.json`은 포함된 소스 10파일만 검증하는 목록입니다. 위 기하 결과와 `provenance.json`의 메시 해시는 제작 중 별도 생성물의 기록이며, 이 소스 묶음에 해당 산출물이 들어 있다는 뜻이 아닙니다. `inspect_blend.py`는 Blender 파일 생성 후 실행하며 검사 JSON을 씁니다. `verify_bundle.py`는 Python의 Pillow 패키지와 전체 산출물과 별도 콘셉트 이미지가 준비된 뒤 쓰는 후처리 도구입니다. 렌더 PNG의 특정 텍스트 메타데이터를 정리하고 검사 JSON을 쓰므로 읽기 전용 검사기가 아닙니다. 초기 사본만으로 바로 실행하지 마세요.
