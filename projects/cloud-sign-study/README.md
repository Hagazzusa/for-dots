# 남은 하늘 · 환경 방향 부호 비교

두 실제 저샘플 렌더에서 World 가우스 중심 부호를 비교한 연구다. 완성 작품이나 자연스러운 물 표현의 성공을 주장하지 않는다. `draft.png`는 수정 전, `draft_corrected_sign.png`는 수정 후, `sign_comparison.png`는 두 이미지를 나란히 놓은 관찰 자료다. 각각 600×400, Cycles CPU 2 threads, 고정32 samples, seed59이며 adaptive·denoise는 껐다.

## 첫 초안에서 확인한 결과와 오류

수면의 외곽과 뒤쪽 연석의 어두운 반사는 보이지만, 의도한 밝은 구름 반사는 보이지 않는다. 점 잡음도 강하다. **이번 이미지는 물의 한계를 시험한 유효한 하늘 적용 결과로 해석할 수 없다.**

작성자가 World Texture Coordinate Normal을 바깥으로 진행하는 광선 방향으로 잘못 해석했다. Blender 4.3.2에서 배경 Normal은 −ray_D다. 따라서 Normal Z=+0.43에 둔 밝은 구름 띠는 실제로 지평 아래에 놓였다. 표본의 위쪽 반사 광선에서 실제 구름 가중치는 사실상 0이다. `preflight.json`의 처음 양수 방향 가중치 계산은 잘못된 예측으로 명시했고, 실제 셰이더 부호에 따른 범위를 추가했다. 이 문단은 첫 초안의 오류 기록이며 아래의 두 번째 렌더에서 부호를 수정했다.

두 번째 비교는 샘플을 늘리지 않고 부호 하나만 바꾸었다.

## 실제 구성과 계산

- 원본 `remaining_sky/Remaining_Sky.blend`를 읽고 별도 `Cloud_Study.blend`로 저장했다. 수면·8mm 지면 오목함·연석·낙엽·카메라 변환과 렌즈는 원본 그대로다.
- 수면 IOR 1.333, Transmission 1, roughness .035, 평평한 상단 법선도 그대로다. 수면에 하늘 이미지를 그리거나 발광을 넣지 않았다.
- World 전체에 파랑 (.18,.30,.48)과 구름 (1.5,1.55,1.6) 선형 RGB를 방향 가우스 가중치로 섞었다. 측정된 실제 하늘이 아니라 단순화한 환경이다. 위에서 밝힌 방향 부호 오류가 있다.
- 수면 아래 지면의 기존 명도 배율 .60을 .90으로 완화했다. 노이즈 색 입력 (.16,.17,.17)~(.31,.29,.25)에 적용한 셰이더 입력이며, 픽셀 밝기나 반사율이 아니다.
- Sun energy 1.6→0, 반사용 창틀 두 개 render 숨김, 표시 노출 0→+1, DOF 끔, 기존 adaptive 24→고정 32 samples로 바꾸었다. 다중 변수 탐색이므로 인과 분리를 주장하지 않는다.
- 수면 내부 512개 위치에서 반사 광선을 계산했다. render-hidden 창틀을 메모리에서 제외한 확인에서는 World 476개, 연석 36개였다. World를 향한 고도는 약 21.36~30.51°다. 이 수치는 화면 픽셀 기여율이 아니다. 가장자리 전체나 roughness 분포를 적분한 결과도 아니다.
- 최초 scene.ray_cast에는 render-hidden 기하가 잡혔으므로 이를 별도 읽기 전용 재개봉 계산에서 수정했다. `check_reflections.py`는 native를 다시 저장하지 않는다.

## 보존과 한계

원본 SHA256 전후 동일: `0fdff87d12562c3da3cfa8edd14bcdb706e2d7dd507cd3b63e8e1296c777b8ff`.

공개 사본의 PNG 텍스트 경로를 제거했고 native의 상대 저장 경로를 확인했다. 기준 2×2 실험의 ROI 숫자를 재사용하거나 반사율로 해석하지 않았다. 실제 관객의 물 인지 검사, 유체·수심·광학 정확성 인증도 아니다.

## 오류 확인의 일차 근거

- [Blender 4.3.2 배경 셰이딩 초기화](https://github.com/blender/blender/blob/v4.3.2/intern/cycles/kernel/geom/shader_data.h): shader_setup_from_background에서 N = −ray_D.
- [Blender 4.3.2 Texture Coordinate](https://github.com/blender/blender/blob/v4.3.2/intern/cycles/kernel/svm/tex_coord.h): NODE_TEXCO_NORMAL은 sd->N을 사용한다.


## 부호 수정 비교

- `draft_corrected_sign.png`: 두 번째 실제 초안. `sign_comparison.png`는 원본 픽셀 두 장을 축소 없이 나란히 배치하고 이름만 붙였다.
- World 가우스 중심 하나만 Normal.z +0.43→−0.43으로 바꾸었다. 색·강도·카메라·기하·물 재질·seed·샘플·표시 설정은 유지했다. `verify_pair.py`가 두 native를 재개봉해 기록된 주요 입력의 차이가 World Math 노드 하나임을 확인했다. 파일 전체 상태의 완전성 증명은 아니다.
- 렌더 전에 Normal=−ray_D로 512개 반사 방향의 셰이더 식을 직접 평가했다. 구름 띠 중심은 실제 상공 고도 25.4676°다. 가중치는 수정 전 약 7.79e−64~5.30e−46에서 수정 후 0.36936~0.999999로 바뀐다. 이는 입력 혼합 가중치이지 픽셀 기여율이나 반사율이 아니다.
- 실제 이미지에서는 물 내부의 넓고 밝은 띠와 연석의 어두운 반사가 분명히 나타났다. 원래 파란 패치보다 반사 표면으로 읽히는 단서가 늘었다. 그러나 밝은 형태가 흰 재료를 끼운 듯 보일 가능성이 있고 얕은 가장자리·바닥 투과가 충분히 자연스럽다고 단정할 수 없다. 32 samples의 입자도 보인다.
- World 방향 변경은 지면 조명도 바꾸므로, 화면 변화 전체를 수면 반사 증가로만 설명할 수 없다. 구름은 모든 방위에 같은 띠가 있는 이상화이며 자연 구름 사진이나 관측 하늘이 아니다.
- `pixel_comparison.json`의 사후 선택 영역은 표시 PNG의 공간 평균만 기록한다. 통계적 유의성·선형 방사량·관객 평가로 해석하지 않는다.

수정 전 이미지와 native를 함께 보존했다. 이 공개 정리에서는 추가 렌더를 수행하지 않았다.

## 재현 범위와 파일 쓰기

이 묶음은 **오류가 있던 Cloud_Study.blend를 기준으로 부호만 바꾸는 비교**를 재현한다. 그 이전 장면을 빈 파일부터 구성하는 전체 생성 과정은 포함하지 않는다. 기준 장면은 독자적인 절차형 형상·재질로 만들어졌고 외부 이미지·메시를 포함하지 않는다. 초기 구상의 생성 이미지도 이 렌더의 입력이나 배포 파일이 아니다. 새 공개 라이선스를 부여하지 않는다.

`preflight.json`은 첫 오류와 뒤의 정정 주석이 함께 남은 역사적 기록이다. `world_hit_cloud_mix_range`와 `corrected_cloud_mix_range`는 잘못된 양수 방향 계산이므로 실제 World 가중치로 사용하지 않는다. 실제 부호 수정 전후의 식 평가 근거는 `sign_correction_preflight.json`이다. 잘못된 식을 다시 만드는 옛 `check_reflections.py`와 전체 탐색용 `draft.py`는 최소 공개 범위에서 제외했다.

Blender4.3.2, Python NumPy·Pillow가 필요하다. 먼저 폴더 전체를 새 작업 사본으로 복사한다.

```sh
blender --background --disable-autoexec --threads 2 --python-exit-code 1 --python correct_sign.py
blender --background --disable-autoexec --threads 2 --python-exit-code 1 --python verify_pair.py
python3 measure_pixels.py
```

첫 명령은 기준 native를 읽고 수정 native·수정 PNG·sign_correction_preflight.json을 덮어쓴다. 두 번째는 native를 저장하거나 렌더하지 않지만 pair_validation.json을 덮어쓴다. 세 번째는 고정된 사후 영역의 감마·톤매핑된 표시 RGB 평균을 계산해 pixel_comparison_recomputed.json을 쓰고 보존된 수치와 비교한다. 폴더 전체의 읽기 전용 명령은 아니다. 새로운 렌더가 같은 바이트가 된다고 보장하지 않는다. 비교 그림은 제공된 두 원본 픽셀을 나란히 놓은 보존 자료이며 새 렌더에 자동 갱신되지 않는다.

두 PNG에서 작업 경로 텍스트만 제거했고 IDAT와 디코딩 픽셀은 동일하다. 비교 PNG와 두 native는 원래 바이트를 보존했다. `provenance.json`에 역사적 해시와 공개 사본 해시를 구분했다. 주요 입력 비교는 기하·변환·재질 노드·World 노드와 링크·카메라·Cycles 설정을 대상으로 한 한정 검사이며 전체 `.blend` 상태가 한 비트만 다르다는 뜻은 아니다. 출력 파일명도 서로 다르다.
