# 두 잔의 자리 · 차 재질 연구실

**결론: 제한적 개선은 있지만 통합은 보류한다.** 기존 작품·GLB·뷰어의 opaque 차는 바꾸지 않았다. 컵 프로파일에 맞춘 alpha/PBR 후보는 높은 시점에서 따뜻한 가장자리와 컵 내부 명암을 보여 주지만, 컵 바닥 식별은 아직 약하다. 실제 굴절·체적 흡수·유체 시뮬레이션이 아니다.

- 자세한 두 방법 비교, 공식 문서, 관찰과 한계: [REPORT.md](REPORT.md)
- 원본 GLB의 동일 바이트 복사 + 실험 shader 1개. 새 외부 텍스처나 화면 투영 없음.
- 검증: Godot 4.6.3 official, GL Compatibility, X11/Mesa llvmpipe. 초기 12장 + alpha 1회 보정 후 12장 + 액체 숨김 진단 1장.
- 공개용 allowlist와 무결성: `manifest.json`, `provenance.json`, `qa/preservation.json`.

## 실행

Godot 4.6.x와 OpenGL 디스플레이가 있는 Linux에서:

```sh
python3 verify_lab.py
bash run_native.sh
```

`B`: opaque/후보 전환 · `V`: 3시점 전환 · `L`: 주광원 on/off · `Esc`: 이 연구실만 종료. 환경광과 fill은 계속 켜져 있다. 기본은 opaque다.

재캡처는 동결된 증거를 덮어쓰므로 **이 폴더의 복사본에서만** 실행한다:

```sh
bash run_native.sh --capture-matrix
python3 analyze_captures.py  # Pillow, NumPy 필요; PNG는 변경하지 않음
```

`run_native.sh`는 이 프로젝트만 import하며 `.godot/`, `work/`는 로컬 캐시다. Blender를 실행하지 않는다. 렌더러·드라이버가 바뀌면 픽셀의 완전 일치는 기대하지 않는다. `verify_lab.py`는 저장된 증거·hash·PNG CRC를 검산할 뿐 native 렌더를 재실행하지 않는다.

`qa/initial/native_matrix.json`의 `qa/*.png` 경로는 첫 실행 당시 위치다. 그 실행 결과는 수정 없이 `qa/initial/`로 옮겨 보존했다. 첫 실행 1180×812와 최종 720×640 사이의 픽셀 차이는 직접 비교하지 않는다.

## 출처와 범위

닷돌이의 허구 정물 **두 잔의 자리**에서 파생한 재질 연구다. 배우자가 차를 준비하고 한 사람이 아직 귀가하지 않은 평범한 기다림이며, 실제 사용자의 사생활을 묘사하지 않는다. 원본 작품이나 기존 뷰어를 대신하는 새 작품으로 취급하지 않는다.

원본 자산: [Hagazzusa/for-dots의 두 잔의 자리](https://github.com/Hagazzusa/for-dots/tree/78f55a389e353819f0c8bb90acc11903382f541e/second-cup), [기존 뷰어](https://github.com/Hagazzusa/for-dots/tree/78f55a389e353819f0c8bb90acc11903382f541e/second-cup-viewer). 자산의 producer `.blend` SHA와 GLB SHA는 `provenance.json`에 기록했다. 원본 이미지·Blender·기존 뷰어는 이 연구실의 실행이나 분석으로 수정되지 않는다.
