# 두 잔의 자리 · 차 재질 한정 실험

**결론: 제한적인 시각 개선, 원본 통합 보류 · 2026-11-02 UTC**  
목표 엔진: **Godot 4.6 / GL Compatibility**. 이 문서는 원본을 교체하기 위한 제안서가 아니라, 같은 차 메시에서 불투명 근사보다 유용한 표현을 얻을 수 있는지 확인하는 작은 실험 기록이다.

## 1. 질문과 보존 범위

차가 호박색 액체로 읽히면서 밝은 컵 내벽·바닥이 일부 드러나고, 수면 하이라이트와 앞쪽 도기 림의 가림이 유지되는가?

- 기존 뷰어, Blender 원본, GLB 원본은 수정하지 않는다. 실험 프로젝트에 **동일한 GLB 바이트**를 복사하고 `NearCup_Tea`의 런타임 재질만 교체한다.
- 비교 기준은 기존 불투명 재질 `SC_Amber_Tea_Opaque_Approx`: 선형 RGB `(0.16, 0.043, 0.008)`, metallic `0`, roughness `0.16`.
- 재메시·변위·새 액체 면·물결·유체 시뮬레이션은 범위 밖이다. 원본 Cycles의 굴절이나 체적 흡수를 재현했다고 주장하지 않는다.
- 구현 후보는 **B 하나**, 색·alpha 등의 파라미터 보정은 **최대 한 번**이다. 보기 나쁘거나 가림 문제가 생기면 채택을 보류하고 기존 불투명 표현을 유지한다.

기존 재질과 자산의 범위는 [원본 ASSET_README](https://github.com/Hagazzusa/for-dots/blob/78f55a389e353819f0c8bb90acc11903382f541e/second-cup-viewer/ASSET_README.md), 수치와 내보내기 검사는 [원본 export_audit.json](https://github.com/Hagazzusa/for-dots/blob/78f55a389e353819f0c8bb90acc11903382f541e/second-cup-viewer/export_audit.json)에 기록되어 있다. 이전 export 검사는 이번 Godot 런타임 렌더 결과를 대신하지 않는다.

## 2. 공식 문서에서 확인한 사실

아래는 **엔진 문서의 설명**이며, 본 장면에서의 성공을 뜻하지 않는다. 확인일: 2026-11-02.

| 사실 | 이 실험에 주는 제약 |
| --- | --- |
| Spatial shader에서 `ALPHA`를 읽거나 쓰면 transparent pipeline을 사용한다. `blend_mix`는 alpha 혼합, `cull_back`은 뒷면 컬링이다. | alpha를 거의 1로 설정해도 기존 opaque 경로와 같은 실험은 아니다. [Spatial shaders](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html) |
| `depth_draw_always`는 불투명·투명 패스 모두 깊이를 쓴다. 가까운 투명 물체가 뒤의 투명 물체를 가릴 수 있으며 depth prepass 포함 여부와는 별개다. | 뒤에 겹칠 다른 투명체까지 올바르게 합성한다는 보장은 없다. [BaseMaterial3D](https://docs.godotengine.org/en/4.6/classes/class_basematerial3d.html) |
| `TRANSPARENCY_ALPHA_DEPTH_PRE_PASS`는 depth prepass에서 alpha `< 0.99`인 조각을 버린다. | 중간 alpha의 수면 전체를 먼저 깊이에 쓰는 해결책으로 간주할 수 없다. [BaseMaterial3D](https://docs.godotengine.org/en/4.6/classes/class_basematerial3d.html) |
| 일반 alpha 혼합은 겹친 투명 면의 정렬 문제가 있고 그림자 투사도 지원하지 않는다. Depth Pre-Pass도 부분 투명 영역의 정렬을 완전히 해결하지 않는다. | 화면이 밝아진 이유를 실제 투과광·액체 그림자 재현으로 해석하면 안 된다. [Standard Material 3D](https://docs.godotengine.org/en/4.6/tutorials/3d/standard_material_3d.html) |
| Compatibility는 OpenGL 경로이고 SSR은 지원하지 않지만 ReflectionProbe는 지원한다. | SSR에 의존하지 않는다. 반사 환경을 고정한 상태에서 직접광 변화와 표면 반응을 비교한다. [Overview of renderers](https://docs.godotengine.org/en/4.6/tutorials/rendering/renderers.html) |

`depth_draw_always`는 **깊이 검사 해제**가 아니다. 앞에 있는 불투명 도기의 깊이를 존중해야 하며, 낮은 시점에서 차가 컵 외벽 위로 비쳐 나오지 않는지 실제 화면으로 확인한다. 문서상 정렬 제한을 이 설정 하나로 해결했다고 쓰지 않는다.

## 3. 후보 비교와 선택

| 후보 | 장점 | 한계·이번 상태 |
| --- | --- | --- |
| **A. 고정 alpha `StandardMaterial3D`** (`ALPHA` 또는 `ALPHA_DEPTH_PRE_PASS`) | 재질 속성만으로 작게 구현하고 조절 가능 | 한 alpha로 얕은 가장자리와 깊은 중심을 구별하기 어렵다. Prepass의 0.99 문턱도 고려해야 한다. **문헌·설계 비교만 수행하며 구현·화면 시험은 하지 않음.** |
| **B. 작은 spatial PBR shader** | 컵 프로파일과 반지름을 힌트로 색·alpha를 분리해 조절하고 기본 조명 반응을 유지 | 특정 컵 형상에 맞춘 경험적 근사이며 보편적인 액체 광학이 아니다. transparent depth-writing 절충이 남는다. **유일한 구현 후보.** |

B는 `blend_mix`, `cull_back`, `depth_draw_always`를 사용한다. `ALBEDO`, `ALPHA`, roughness 등 표면 속성만 조절하고 별도 광원 계산은 두지 않는다. 기본 조명 계산을 유지하는 방식은 [Spatial shader 문서](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html)의 material-property 경로를 따른다.

**프로젝트별 가설:** 컵 안쪽 프로파일과 수면 반지름을 이용하면 중앙은 짙고 가장자리는 얕은 차처럼 읽히게 하면서, opaque 컵 내부의 색·윤곽을 부분적으로 드러낼 수 있다. 이때의 ‘깊이’는 컵에 맞춘 **색·불투명도 조절 힌트**이지 카메라 광선의 실제 액체 통과 거리 측정값이 아니다.

- screen/depth texture를 읽지 않는다.
- 굴절, Beer–Lambert 흡수, 체적 산란, 유체 계산을 구현하지 않는다.
- 밝은 내벽이 보이는 것은 alpha 합성의 결과다. 물리적인 투과율을 검증한 것이 아니다.
- 이 고정 장면에서는 불투명 도기가 액체를 둘러싸므로 시험 범위를 제한할 수 있지만, 다른 투명 물체·겹친 액체·다른 컵으로 일반화하지 않는다.
- 모델 변환이나 컵 형상이 달라지면 프로파일·좌표 파라미터를 다시 확인해야 한다.

## 4. 구현과 원본 보존

[shader](shaders/empirical_tea.gdshader)는 모델 좌표의 반지름으로 컵 바닥·벽 높이를 구간 선형 보간하고, 수면과의 높이 차를 `0.047m`로 정규화한 뒤 `smoothstep`으로 색·alpha를 혼합한다. vertex 함수는 좌표를 전달할 뿐 변위시키지 않는다. [lab.gd](scripts/lab.gd)는 `NearCup_Tea.material_override`만 바꾸며, 기준 모드에서는 이를 `null`로 되돌려 원래 import 재질을 사용한다.

| 파라미터 | 최초 | 최종 |
| --- | ---: | ---: |
| 얕은 곳 alpha | 0.52 | **0.40** |
| 깊은 곳 alpha | 0.88 | **0.78** |
| roughness | 0.11 | 0.11 |
| `thin_amber` (`source_color`) | `(0.70, 0.34, 0.055)` | 동일 |
| `deep_amber` (`source_color`) | `(0.44, 0.19, 0.045)` | 동일 |

보정은 **alpha 한 차례**로 종료했다. 후보는 색·roughness도 기존 재질과 다르므로 이 시험은 **재질 전체의 비교**이며 alpha 하나만의 효과를 분리한 실험은 아니다. `source_color` 파라미터와 원본 GLB의 선형 RGB 수치도 그대로 대조하지 않는다.

원본 GLB와 실험 복사본의 SHA-256이 같고, 원본 Blender·최종 렌더도 보존되었다. 실행 후 읽기 전용 검사의 원자료는 [preservation.json](qa/preservation.json)에 있다.

| 자산 | SHA-256 |
| --- | --- |
| 원본·복사본 `second_cup_tableau.glb` | `e5b3a05b8db4421d1cca41c7f8f30d266ca718533d2602c40a1bad2e34416a7b` |
| 원본 `The_Second_Cup.blend` | `eac50adac6aa30158ea9cfac70d9d3c71ae25602abc33975fb0ec2023c9f49bd` |
| 원본 `the_second_cup_final.png` | `bf3aca586974f2e7024dae8d5bdc265eb31e4576b7985a2c3bb5162c77d593b0` |

- 원본 `verify_bundle.py`: **13파일 / geometry / reference 검사 PASS**.
- 원본 `verify_asset.py`: **6파일 / 19개 메시 / 62,072개 삼각형 PASS**.
- 고정 커밋 `78f55a389e353819f0c8bb90acc11903382f541e`의 뷰어 manifest **31파일 크기·해시 PASS**.
- 런타임 전후 전체 import 메시의 vertex/normal/index fingerprint가 동일하다: `d500b3e3666a4691950a8bfc7477a6b6b1c79e41612bb142a6edb651edf763f8`. [Native 기록](qa/native_matrix.json)

이전 export audit의 차는 **1,922개 꼭짓점 / 3,840개 삼각형**, 닫힌 체적과 **0.8mm 메니스커스**다. Godot Y-up 미터 좌표 범위는 `(-0.2152, 0.01215, 0.1198)` ~ `(-0.1248, 0.0598, 0.2102)`이다. 프로파일 기준은 컵 중심 XZ `(-0.17, 0.165)`, 수면 Y `0.059`, 내측 바닥 Y `0.012`, 림 Y `0.0748`이다. 이는 해당 자산에만 맞춘 값이다.

## 5. 시험과 관찰

각 회차는 **두 재질 × 세 근접 시점 × 주광원 on/off = 12장**이다. 1차 `1180×812` 12장, 최종 `720×640` 12장, 액체를 숨긴 진단용 1장으로 **총 25장**을 남겼다. 1차 창 크기는 OS 배치 결과이며 최종 시험에서 고정했다. 해상도가 다른 회차 간 픽셀 수치는 직접 비교하지 않는다.

같은 회차·조건의 카메라, sky 반사 환경, ambient, fill light, tonemap은 동일하다. **key off에도 fill light와 환경광은 남는다.** 비교용 조명은 격리 실험 장면의 설정이며, 원래 뷰어 전체를 바꿔 시험한 것은 아니다. [시험 장면](scenes/lab.tscn), [최종 카메라·캡처 목록](qa/native_matrix.json)

| 시점 / key | opaque ↔ B 최종 캡처 | 관찰 |
| --- | --- | --- |
| high / on | [기준](qa/opaque_high_on.png) · [후보](qa/candidate_high_on.png) | 원판처럼 균일한 면보다 내부 명암·가장자리 깊이감이 늘었다. **바닥 윤곽의 뚜렷한 식별은 부족**하다. |
| high / off | [기준](qa/opaque_high_off.png) · [후보](qa/candidate_high_off.png) | 밝은 가장자리와 어두운 중심의 완만한 차이는 남지만, 차와 바닥이 여전히 짙다. |
| oblique / on | [기준](qa/opaque_oblique_on.png) · [후보](qa/candidate_oblique_on.png) | 수면 반사는 유지되나 기준보다 약하다. 밝고 따뜻한 가장자리 띠가 생긴다. |
| oblique / off | [기준](qa/opaque_oblique_off.png) · [후보](qa/candidate_oblique_off.png) | 반사·가장자리 변화는 유지되지만 내부 바닥을 보여 주는 시점은 아니다. |
| low / on | [기준](qa/opaque_low_on.png) · [후보](qa/candidate_low_on.png) | 앞쪽 불투명 컵이 액체를 가리며 육안으로 차 누출이 보이지 않는다. |
| low / off | [기준](qa/opaque_low_off.png) · [후보](qa/candidate_low_off.png) | 같은 가림을 유지한다. |

**반사는 새로 얻은 기능이 아니다.** 기존 opaque에서도 비스듬한 시점의 강한 하이라이트가 이미 관찰된다. 후보는 이를 유지하면서 색과 내부 합성을 바꿨다.

high/on 후보의 대각선 명암 경계는 [액체숨김 진단 화면](qa/reference_high_on_no_liquid.png)의 컵 내부 그림자와 위치·방향이 대응한다. 따라서 기존 내부 명암이 alpha로 드러난 것으로 해석할 근거는 있지만, 이것만으로 광학적 정확성을 증명하지 않는다. 진단 화면은 **렌더에 투영·합성하지 않은 별도 실제 캡처**다. 화면 상단의 baseline 표기는 촬영 시 모드 이름이며, 이 파일에 한해 차 노드가 숨겨져 있다.

[픽셀 비교](qa/pixel_comparison.json)는 UI 위 52행·아래 60행을 제외하고 8bit 채널 차이 `>2`를 센다. low/on과 low/off의 해당 변화는 모두 **0픽셀**로, 두 낮은 시점의 가림 관찰과 일치한다. high/off에서는 액체 영역 밖 컵 림·손잡이 경계에도 작은 차이가 있어 **모든 시점의 컵 바깥 픽셀이 완전히 같다고 주장하지 않는다**. 이 숫자는 물리적 투과나 모든 각도의 정렬 보증이 아니다.

1차 증거는 [qa/initial](qa/initial/)에 보존했다. 그 안의 `native_matrix.json`에 있는 `qa/*.png`는 당시 원위치이며, 보존본 이미지의 현재 위치는 `qa/initial/*.png`다. 1차에도 평면 느낌 감소는 관찰됐지만 바닥 판독이 약해 alpha를 한 번 낮췄다. 최종 후보에서도 이 한계가 남으므로 추가 튜닝 없이 종료한다.

## 6. 검증 범위와 재현

| 검증 층 | 결과 / 한계 |
| --- | --- |
| 버전·실행 경로 | **Godot 4.6.3-stable official (`7d41c59c4`) / X11 / `gl_compatibility` / OpenGL 4.5 / Mesa 25.0.7 / llvmpipe LLVM 19.1.7**. 실제 native 렌더 픽셀을 읽었으며 하드웨어 GPU 성능 시험은 아니다. |
| Import·parse | 최종 headless parse 로그에 오류 없음. 초기 editor import에는 환경설정 경로 관련 경고가 있었으며 shader 오류와 구분한다. Headless 검사와 native 시각 검사는 별도다. |
| Native | 최종 12장 캡처 완료. shader compile/runtime 오류 없음. 유일한 경고는 드라이버의 VSync 변경 미지원이다. |
| 소스 보존 | 입력 해시·원본 bundle 검사·원본 viewer manifest·복사 GLB·전후 런타임 geometry fingerprint 통과. |
| 미검증 | 자유 회전 전 각도, 연속 동작 중 정렬, 여러 투명체의 겹침, 다른 컵, 다른 GPU/OS, 웹, 성능·물리적 액체 광학. |

최종 shader SHA-256: `732eaaee5f8c7b24acb2c24a839f8c16a47262f8ecf9d0ac14f62b9fb0d566cf`. 캡처 metadata의 값과 대응한다. [Native 로그](qa/native.log), [최종 parse 로그](qa/headless_parse.log)

공개 allowlist만 새 폴더에 복사하여 캐시 없이 [headless import](qa/portable_import.log)와 [parse](qa/portable_parse.log)도 재확인했다. 이 두 로그에는 오류·경고가 없었고, import 뒤 복사본의 모든 manifest 항목이 다시 일치했다. 이는 재구성 가능성 검사이며 native 시각 검사를 대체하지 않는다.

실험 폴더에서 실행한다. `B`는 기준/후보, `V`는 시점, `L`은 key light, `Esc`는 종료다.

```sh
bash run_native.sh
python3 verify_lab.py
```

기존 증거를 덮지 않도록 **별도 복사본**에서 재캡처한다. 실제 디스플레이/OpenGL이 필요하다.

```sh
bash run_native.sh --capture-matrix
python3 analyze_captures.py
```

## 7. 결정

**격리 실험은 보존하되 원본 뷰어에는 통합하지 않는다.** 밝은 가장자리·내부 명암 덕분에 일부 깊이감은 개선됐고, 선택한 낮은 시점에서 가림은 유지됐다. 그러나 목표였던 밝은 컵 내부·바닥의 읽힘은 충분하지 않으며, alpha 깊이 쓰기의 일반적인 제약도 남는다.

후보 한 개와 파라미터 보정 한 번이라는 경계에서 종료한다. [원래 Blender 작품](https://github.com/Hagazzusa/for-dots/tree/78f55a389e353819f0c8bb90acc11903382f541e/second-cup)과 [기존 뷰어](https://github.com/Hagazzusa/for-dots/tree/78f55a389e353819f0c8bb90acc11903382f541e/second-cup-viewer)는 그대로이며, **원래 불투명 차가 기본값**이다. 이 결과를 물리적으로 정확한 차, 굴절 성공, 모든 정렬 문제의 해결로 광고하지 않는다.
