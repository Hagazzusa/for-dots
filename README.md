# for-dots · 작은 세계와 실험

직접 플레이할 수 있는 비 오는 밤의 장면, 독창적인 절차적 아트, 범위를 한정한 기하·빛 실험을 모았습니다.
각 프로젝트를 독립적으로 다시 열 수 있도록 소스, 편집 가능한 장면, 미리보기와 검증 자료를 함께 보관합니다.

**[작품 갤러리 · 이미지와 짧은 영상으로 둘러보기](GALLERY.md)**

| 프로젝트 | 시작 안내 | 실행 환경 |
|---|---|---|
| **두 잔의 자리 · The Second Cup** — 빵을 기다리는 집 안의 작은 준비 | [제작·검증](second-cup/README.md) · [실제 렌더](second-cup/renders/the_second_cup_final.png) · [생성 콘셉트](second-cup/reference/gpt_image_concept.png) | Blender **4.3.2**, 기본 검증은 Python 표준 라이브러리. 독립적인 도기·금속 정물의 실제 Cycles 렌더이며 유체·열·제품 안전 검증이 아닙니다. |
| **Mended Corner · 수선이 남긴 자리** — 고친 벤치 끝의 조용한 정물 | [작품·제작 소스](mended-corner/README.md) · [실제 렌더](mended-corner/renders/mended_corner_final.png) · [생성 콘셉트](mended-corner/reference/gpt_image_concept.png) | Blender **4.3.2**, Python 표준 라이브러리. 절차적 재질과 모델로 만든 실제 Cycles 렌더이며 실물 수선·전기 안전 검증이 아닙니다. |
| **After the Rain** — 조용한 버스 정류장, 따뜻한 코코아, 유리 쉼터와 선택적인 동네 만남 | [게임 안내](after-the-rain/README.md) · [재구성 현황](after-the-rain/RECOVERY.md) | Godot **4.6.x Standard**. `after-the-rain/project.godot`을 열고 F5를 누릅니다. 플레이에 Blender는 필요하지 않습니다. |
| **Rain Clock** — 가상 키네틱 조각 | [소스·렌더 안내](rain-clock/README.md) · [정지 이미지](rain-clock/rain_clock_still.png) · [반복 영상](rain-clock/rain_clock_loop.mp4) | Blender **4.3.2**. 다시 생성한 프레임을 인코딩하려면 ffmpeg가 필요합니다. |
| **Rain Clock 기구 실험** — 기하학적 대안과 측정된 한계 | [실험 목록](rain-clock/STUDY_INDEX.md) · [수동 기구](rain-clock/mechanism/README.md) | `.FCStd`에는 FreeCAD, 절차적 미리보기에는 Blender가 필요합니다. 각 실험에 스크립트와 가정을 기록했습니다. |
| **Garden of Light** — 세 가지 색 필터 사이로 움직이는 빛 | [안내](garden-of-light/README.md) · [정지 이미지](garden-of-light/Garden-of-Light.png) · [반복 영상](garden-of-light/Garden-of-Light-loop.mp4) | Blender **4.3+**. 영상에는 ffmpeg, 픽셀·영상 품질 검사에는 Pillow, numpy, ffprobe가 필요합니다. |
| **When two filters overlap** — 조건을 통제한 장면 선형 RGB 실험 | [결과·재현](filter-overlap-study/README.md) · [비교](filter-overlap-study/Filter-Overlap-Comparison.png) | Blender **4.3+**(내장 numpy). 비교 이미지에는 Pillow가 설치된 Python이 필요합니다. 선형 EXR 6개에 측정 근거를 보존했습니다. |
| **Three heights, one light** — 부드러운 그림자 작품과 조건을 통제한 반그림자 실험 | [실험·재현](soft-shadow-study/README.md) · [작품](soft-shadow-study/Three-Heights-One-Light.png) · [검증 자료](soft-shadow-study/Penumbra-Evidence.png) · [해상도 검사](soft-shadow-study/Resolution-Check.png) | Blender **4.3+**(내장 numpy). 도표에는 matplotlib/numpy가 설치된 Python이 필요합니다. 선형 EXR 10개에 측정값을 보존했습니다. 두 해상도 비교는 정밀도의 한계를 살피는 것이며 수렴을 입증하지 않습니다. |
| **Fading Shore** — 위로 솟는 청록색 띠와 부드러워지는 색 그림자 | [작품·재생성](fading-shore/README.md) · [정지 이미지](fading-shore/Fading-Shore.png) | Blender **4.3+**, 4.3.2에서 테스트했습니다. 독창적인 가상 조각이며 보정된 측정이나 제작 제안이 아닙니다. |
| **Window Rhythms** — 38초 절차적 빗소리 소품 | [소스·청취 참고](window-rhythms/README.md) · [MP3 미리듣기](window-rhythms/window_rhythms_preview.mp3) · [파형](window-rhythms/waveform.svg) | Python **3.10+**, NumPy/SciPy, libmp3lame을 포함한 FFmpeg. 수치 검사만 했으며 실제로 들어 확인하지 않았습니다. 디지털 레벨은 안전한 재생 음량을 보장하지 않습니다. |
| **Road into Evening** — 지형을 따르는 절차적 풍경 | [소스·한계](quiet-road/README.md) · [정지 이미지](quiet-road/road_into_evening.png) | Blender **4.3.2**. 편집 가능한 압축 장면, 소스, 유한한 메시 검사를 포함합니다. 가상 풍경 실험이며 주행 가능한 프로토타입이나 토목 설계가 아닙니다. |
| **도로 종단 대안** — 범위를 한정한 경사·지형 절충 실험 | [방법·한계](quiet-road-profile-study/README.md) · [비교](quiet-road-profile-study/profile_comparison.png) · [6% 대안](quiet-road-profile-study/road_into_evening.png) | Blender **4.3.2**, 최적화에는 NumPy/SciPy/Matplotlib. 종단 검증에는 표준 Python을 사용합니다. 끝점은 자유롭게 두고 절토·성토 깊이는 표본으로 측정했습니다. 토목 도로 기준 충족을 뜻하지 않습니다. |
| **Beside You** — 허구의 주차된 차 안을 표현한 대안 오디오 | [소스·청취 참고](beside-you/README.md) · [MP3 미리듣기](beside-you/beside_you_preview.mp3) · [파형](beside-you/waveform.svg) | Python **3.10+**, NumPy/SciPy, libmp3lame을 포함한 FFmpeg. 시드 기반의 독립적인 합성입니다. 목소리나 녹음은 없으며 실제 청취 검사나 청취 안전성을 주장하지 않습니다. |
| **Seeded Roadscapes** — 열두 지형, 세 장의 엽서 | [생성기·한정된 검사](seeded-roadscapes/README.md) · [세 장 비교](seeded-roadscapes/postcard_triptych.png) | Blender **4.3.2**. 피팅에는 NumPy/SciPy, 배치에는 Matplotlib을 사용합니다. 고정된 평면 도로와 실제로 시드에 따라 달라지는 지형입니다. 세 사례만 렌더·BVH 검사를 했으며 열두 개의 네이티브 장면을 만든 것은 아닙니다. |
| **A Place to Pause** — 사람 크기를 기준으로 한 길가 작품 | [작품 방향·한계](a-place-to-pause/README.md) · [정지 이미지](a-place-to-pause/a_place_to_pause.png) | Blender **4.3.2**. 저장된 seed1107 종단을 사용하며 SciPy는 필요하지 않습니다. 별도의 벤치 받침과 수정된 조명을 적용했습니다. 가상 기하 검사이며 공공 벤치나 도로의 안전 인증이 아닙니다. |
| **Folded Path** — 종이 경첩 형태의 키네틱 작품 | [소스·운동학적 한계](folded-path/README.md) · [정지 이미지](folded-path/folded_path.png) · [반복 영상](folded-path/folded_path.mp4) | Blender **4.3+**, 인코딩에는 FFmpeg. 두께가 없는 강체 면 6개와 키프레임 경첩을 사용합니다. 용접된 한 장의 판, 실제 종이 시뮬레이션, 제작 가능성의 증명이 아닙니다. |
| **Glass Refuge** — 생성 콘셉트에서 편집 가능한 Blender 재구성으로 | [모델·추정 치수](glass-refuge/README.md) · [콘셉트 원본](glass-refuge/reference/gpt_image_concept.png) · [실제 렌더](glass-refuge/renders/05_final.png) · [구조 둘러보기](glass-refuge/renders/06_structural_inspection.mp4) | Blender **4.3+**. 참고 이미지가 내장되어 있고 독립적인 절차적 소스가 있습니다. 단일 이미지의 해석이며 정확한 CAD 복원이나 시공 검증이 아닙니다. |
| **Glass Refuge 뷰어** — 직접 돌려보는 건축 모델 | [열기·조작](glass-refuge-viewer/README.md) · [Godot 프로젝트](glass-refuge-viewer/project.godot) | Godot **4.6.x Standard**. 화살표로 회전, +/−로 확대·축소, L로 조명, G로 유리, R로 초기화합니다. 독립적으로 사용할 수 있는 파생 GLB입니다. 실시간 재질은 근사치이며 식물 풍경이나 Cycles와의 동등한 표현은 제공하지 않습니다. |
| **Glass Refuge 목재 전이** — 범위를 한정한 512/1024 알베도 비교 | [방법·한계](glass-refuge-wood-transfer/README.md) · [네이티브 512](glass-refuge-wood-transfer/qa/native_close_512.jpg) · [Godot 실험](glass-refuge-wood-transfer/project.godot) | Blender **4.3.2**, Godot **4.6.3**, 검증에는 Python/Pillow. 독창적인 참나무 색상만 전이합니다. 기하는 바꾸지 않았고 PBR은 근사치이며 FPS나 자동 게임 통합을 주장하지 않습니다. |

## 문서 언어

설명은 한국어로 통일합니다. 파일명, API 식별자, 실행 명령, 라이선스·인용·정확한 생성 프롬프트의 원문은 그대로 보존합니다. 과거 생성·공개 시점의 출처 기록에 담긴 해시는 당시 체크포인트를 가리키므로 번역된 문서의 현재 해시와 다를 수 있습니다. 현재 파일 바이트는 루트 SOURCE_MANIFEST.json을 기준으로 검사합니다.

## 범위와 한계

- 게임은 **남아 있던 V7 소스를 바탕으로 새로 재구성한 것**이며, V37 코드나 과거 테스트 결과를 복구한 것이 아닙니다. 현재 조작은 WASD 이동, 마우스·화살표 시점 조절, Space 일시정지·도움말, 상황에 따른 E 상호작용입니다. 오디오 생성은 검사했지만 테스트 컴퓨터의 더미 오디오 드라이버에서는 실제로 들어 확인할 수 없었습니다. 소프트웨어 렌더러의 성능은 실제 하드웨어 성능을 보장하지 않습니다.
- Rain Clock과 Garden of Light는 가상 예술이며 검증된 제품이 아닙니다. CAD 실험은 명시된 공칭 기하 또는 표본 기하만 확인합니다. 고정 유지, 공차, 강도, 제조 가능성은 아직 검증하지 않았습니다. 도표를 설계 권고로 받아들이기 전에 각 한계를 읽어 주세요.
- 필터 측정은 굴절이 없는 **RGB 셰이더 모델**을 검사하며 분광 투과나 실제 유리를 측정하지 않습니다. 표시용 PNG 값은 선형 EXR 측정 데이터가 아닙니다.
- 대부분의 작품은 절차적으로 만들었습니다. Glass Refuge의 콘셉트 참고 이미지는 GPT Image로 생성했다고 명시했습니다. 게임에는 외부 도시 에셋과 글꼴도 포함되어 있으며, 출처와 라이선스 원문은 `after-the-rain/assets/city/licenses/`와 `after-the-rain/assets/fonts/`에 보존했습니다. 이 목록은 저장소 전체에 단일 라이선스를 부여하지 **않습니다**.

## 엔진이나 자격 증명 없이 내려받은 사본 검사하기

저장소 루트에서 Python 3.8+로 실행합니다.

```sh
python3 verify_sources.py
```

이 읽기 전용 검사는 Python 표준 라이브러리만 사용해 매니페스트에 나열된 모든 파일의 크기와 SHA256을 비교합니다. 검증에는 Git, 네트워크, 자격 증명, Godot, Blender, FreeCAD가 필요하지 않습니다. 목록에 없는 로컬 파일(캐시, 렌더, 편집기 백업 등)은 무시하며 매니페스트 자신은 목록에 넣지 않습니다.

누락되거나 변경된 체크포인트 바이트를 찾아내지만, 정확성·안전성·저작자나 악의적으로 교체된 매니페스트에 대한 진위를 입증하지는 **않습니다**. 출처 확인에는 신뢰할 수 있는 Git 커밋 이력을 사용하세요. 프로젝트별 검증기는 별도로 각 장면이나 수치적 동작을 검사합니다.

소스를 의도적으로 수정했다면 해당 파일을 검토하고 스테이징한 뒤 매니페스트를 갱신합니다.

```sh
git add <reviewed-files>
python3 verify_sources.py --refresh
python3 verify_sources.py
git add SOURCE_MANIFEST.json
```

갱신에는 Git이 필요하며 추적·스테이징된 일반 파일의 작업 사본 바이트를 해시합니다. 커밋 전에 차이를 검토하세요. 추적되지 않은 파일은 자동으로 포함하지 않고, 심볼릭 링크를 따라가지 않으며, 매니페스트 자신만 제외합니다. 개인 데이터와 생성된 캐시는 추적 대상에서 빼 두세요.

## 공유 전에 에셋 메타데이터 검토하기

[공개 전 점검 도구](tools/README.md)는 명시적으로 선택한 디렉터리나 Git 추적 파일을 선택적으로 읽기 전용 검사합니다. 범위가 제한된 검사기로, 텍스트와 일부 이미지·CAD 메타데이터에서 흔한 비공개 경로·자격 증명 유사 패턴을 표시합니다. Blender와 지원하지 않는 형식은 수동 검토 대상으로 알립니다. 파일을 업로드하거나 수정하지 않으며, 대상 패턴 검사를 통과해도 보안 인증이나 공개 허가가 **아닙니다**.

```sh
python3 tools/check_public_assets.py --directory garden-of-light
python3 tools/test_check_public_assets.py
```
