# 도시 외관 에셋 출처

2026-11-01, 공개된 파일 메타데이터를 사용해 공식 Poly Haven 에셋 다운로드 서비스에서 가져왔습니다. 다운로드한 에셋 파일 37개는 모두 예상 바이트 길이와 배포자 MD5 검사를 통과했습니다. 정확한 소스 URL, 바이트 크기, 해시, 소스 상대 경로는 `download_manifest.json`에 있습니다.

## 라이선스
에셋 네 개 모두 **CC0 1.0 Universal**이며, 법률 원문을 `CC0-1.0.txt`로 포함했습니다(https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt).
공식 에셋 라이선스 근거: https://polyhaven.com/license . 이 페이지는 상업적 사용과 재배포(판매 제품에 포함하는 경우도)를 명시적으로 허용하고 출처 표기가 필수가 아니라고 설명합니다. 그래도 다음 원문으로 출처를 밝히는 것이 적절합니다: "Assets from Poly Haven (CC0)". 계정/결제/체크박스 동의나 실행형 플러그인을 사용하지 않았습니다. 외부 코드를 포함하거나 실행하지 않았으며, 에셋 데이터만 사용했습니다. 배포자 페이지의 이미지/로고는 이 에셋 라이선스에 포함되지 않으며 함께 넣지 않았습니다.

## 선택한 에셋(모두 1K)
- **Modular Urban Apartments Facade**: https://polyhaven.com/a/modular_urban_apartments_facade . `modular_urban_apartments_facade/modular_urban_apartments_facade_1k.gltf`, 바이너리 + JPG PBR 텍스처 12개. 개별 이름이 있는 모듈 147개, 재질 5개, 전체 카탈로그 삼각형 270,045개(단일 건물의 수치가 아님). 전체 시연 카탈로그를 인스턴스화하기보다 필요한 소규모 부분집합을 추출하는 편을 권장합니다.
- **Modular Factory Facade**: https://polyhaven.com/a/modular_factory_facade . `modular_factory_facade/modular_factory_facade_1k.gltf`, 바이너리 + JPG PBR 텍스처 15개. 전체 카탈로그 기준 모듈 192개, 재질 6개, 삼각형 175,014개. 벽돌, 문, 창, 몰딩, 차고로 대비되는 오래된 산업 거리 외관을 구성할 수 있습니다.
- **Asphalt 02**: https://polyhaven.com/a/asphalt_02 . `asphalt_02/` 디퓨즈, OpenGL 노멀, 거칠기 JPG. 공식 출처의 실제 반복 폭은 3 m. 제작자 Rob Tuytel.
- **Concrete Wall 007**: https://polyhaven.com/a/concrete_wall_007 . `concrete_wall_007/` 디퓨즈, OpenGL 노멀, 거칠기 JPG. 공식 출처의 실제 반복 폭은 2.2 m. 제작자 Charlotte Baglioni(촬영), Dario Barresi(처리), Rico Cilliers(타일링).

## 통합 참고 사항
- glTF는 Y-up이며, 메시 정점은 미터에 가까운 실제 치수를 사용합니다(문 높이 약 2.3–2.8 m). 노드의 평행 이동은 시연 배치용이므로 건물 배치로 그대로 보존하지 마세요.
- 두 `*_module_inventory.json` 파일은 모든 노드의 이름/인덱스, 로컬 경계, 치수, 원본 배치 평행 이동, 삼각형 수를 기록합니다. 많은 창/문은 원점이 아니라 로컬 X=-1.5 주변을 중심으로 합니다. 필요하면 실제 메시 경계를 기준으로 정규화하세요. 건축 그리드 정렬은 원점이 중앙이라고 가정하지 말고 벽/몰딩 지오메트리를 따라야 합니다.
- 표준 패킹 ARM 텍스처는 R=AO, G=거칠기, B=금속성입니다. `nor_gl`은 Godot이 사용하는 OpenGL 노멀 방향입니다.
- 다운로드한 glTF의 재질 연결은 온전합니다. 비 오는 밤에 맞춰 도로의 어두운 알베도/젖은 거칠기, 절제된 발광 창 삽입 등 미술적 조정이 필요할 수 있습니다. 동적 조명을 많이 추가하지 마세요.
- 이 에셋은 적절한 텍스처 세부 표현을 갖춘 사실적인 모듈 메시입니다. 고해상도 카탈로그 전체를 반복하기보다 제한된 근거리/중거리 외관, 공유 텍스처/재질, 단순화한 어두운 원거리 덩어리를 사용하세요.
- HDRI, 거대한 장면, 실행형 애드온, 계정은 필요하지 않습니다. 검증된 에셋 전체 용량: 36.67 MiB. 원본 파일은 수정 없이 보존했으며, 프로젝트 파생 에셋은 별도로 최적화할 수 있습니다.

## v5에서의 사용
런타임 파생 에셋은 Modular Urban Apartments Facade, Asphalt 02, Concrete Wall 007을 사용합니다. Factory Facade는 대안으로 조사/다운로드했지만 이 장면에 배치하지 않았습니다. 건물 조립과 최적화는 독창적인 로컬 스크립트로 수행했으며, 패킹된 편집 가능 Blender 소스는 텍스처 의존성을 보존합니다. 런타임 에셋과 패킹된 편집 가능 Blender 조립본을 포함합니다. 원본 카탈로그 데이터로 assemble_city.py를 다시 실행하려면 download_manifest.json에 나열된 라이선스 적용 소스 파일을 형제 city_asset_sources 디렉터리에 확보해야 합니다. 이 원본 카탈로그 다운로드는 프로젝트 실행에 필요하지 않습니다.
