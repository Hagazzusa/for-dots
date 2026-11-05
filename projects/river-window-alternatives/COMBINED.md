# 명도 무늬와 빛 조각을 함께 놓아 본 비교

**게임 통합 보류.** [세 단독안](README.md)의 실패를 유지한 후, 두 번째 수면 명도 무늬와 세 번째 빛 조각만 합쳐 보았다. 수평면 단서는 생기지만 물과 무늬 있는 바닥의 모호함이 남아, 강이라고 읽히는 데 충분한 개선은 확인하지 못했다. 이 접근의 추가 조정은 여기서 멈춘다.

## 바꾼 것과 고정한 것

`combined.tscn`은 `light-fragment.tscn`에 기존 `water_tone.tres` 참조와 River의 재질 override만 더한 씬이다(load_steps도 1 증가). 스크립트·셰이더·6개 OBJ는 기존 파일을 그대로 참조한다. 별도 모델·텍스처·광원은 추가하지 않았다. 직선 강둑, 카메라, 난간, 수면 위치, 시간과 이동 경로는 기준 그대로다.

World XZ 좌표의 smoothstep 연속 명도 보간과 수면 위 15mm에 놓인 고정된 3D 빛 조각이다. 세 가지 이산 명도 띠나 화면 위 덧그림이 아니며, 빛 조각은 양식화 표식일 뿐 실제 광학 반사·유체가 아니다.

## 실제 관찰 범위

1180×812의 정상 창 크기에서 기준·명도 단독·표식 단독·조합의 0/12/19/24초를 비교했다. 기준과 명도 단독은 앞선 동일 씬·크기의 기록을 사용했다. 조합의 24초 연속 이동은 140개 캡처에 걸친 26.257초 구간에서, 표식 단독의 추가 이동은 140개 캡처에 걸친 25.702초 구간에서 관찰했다. 이는 모든 렌더 프레임 검사나 FPS 측정이 아니다. 이 작은 공개 묶음에는 아래 정지 화면 네 장만 보존한다.

이전 공개 기록에서 표식 단독은 정지 비교였다는 설명은 수정하지 않는다. 그 안의 연속 관찰은 이번 후속 비교에서 새로 수행한 것이다. 관찰 시점의 창·난간 가림은 유지됐지만 전체 시점의 무결성은 보장하지 않는다. 낯선 관찰자 검사, 인지 성공률·통계 분석, 성능 측정은 하지 않았다. 같은 제작자가 본 정성 판정이다.

| 연구 시간 | 조합 실제 화면 | 기존 기준 / 명도 단독 / 표식 단독 |
|---|---|---|
| 0초 | [조합](evidence/combined-0.jpg) | [기준](evidence/baseline-0.jpg) / [명도](evidence/water-tone-0.jpg) / [표식](evidence/light-fragment-0.jpg) |
| 12초 | [조합](evidence/combined-12.jpg) | [기준](evidence/baseline-12.jpg) / [명도](evidence/water-tone-12.jpg) / [표식](evidence/light-fragment-12.jpg) |
| 19초 | [조합](evidence/combined-19.jpg) | [기준](evidence/baseline-19.jpg) / [명도](evidence/water-tone-19.jpg) / [표식](evidence/light-fragment-19.jpg) |
| 24초 | [조합](evidence/combined-24.jpg) | [기준](evidence/baseline-24.jpg) / [명도](evidence/water-tone-24.jpg) / [표식](evidence/light-fragment-24.jpg) |

24초/40m는 이 독립 연구 씬의 값이지 실제 게임 경로가 아니다. 기존 게임의 8초 결말과 잇는 시간·공간 설계도 없으므로 게임에 통합하지 않았다.

## 다시 열기

Godot 4.6 계열에서 이 **전체 river-window-alternatives 폴더**가 필요하다. 조합 씬 한 파일만으로는 독립 실행되지 않는다. 같은 폴더의 공통 자산을 재사용하며, 기존 프로젝트의 기본 씬은 변경하지 않았다.

```sh
godot --path river-window-alternatives res://combined.tscn
```

1/2/4/3 키는 각각 0/12/19/24초, Space는 재생/정지, R은 처음, Escape는 연구 창 종료다. Godot은 가져오기 캐시와 사용자 설정을 생성할 수 있다. 기존 `verify_variants.py`와 테스트는 원래 단독안 범위이며 조합의 지각적 성공을 검증하지 않는다. 실행 시 VSync 미지원 경고가 있었으나 해당 실행에서 script/shader 오류는 발견하지 못했다.

공식 [공간 셰이더 문서](https://docs.godotengine.org/en/4.6/tutorials/shaders/shader_reference/spatial_shader.html)는 좌표/재질 표현의 근거이지 강 인지 성공의 근거가 아니다. 추가 외부 에셋이나 새 라이선스는 포함하지 않는다. `COMBINED_MANIFEST.json`은 이번 추가 6파일의 크기·해시만 기록하며 기존 `ARTIFACT_MANIFEST.json`은 단독안 기록으로 그대로 둔다.
