# 비가 지나가는 동안

세 점의 정물과 여섯 문장으로 엮은 작은 오프라인 그림책입니다.
기다리는 식탁에서 문 앞의 여백으로, 그리고 볕이 드는 창턱으로 넘어갑니다.

## 읽기

저장소를 내려받은 뒤 `projects/quiet-storybook/index.html`을 브라우저에서 여세요.
서버, 설치, 계정, 인터넷 연결이 필요하지 않습니다.
`quiet-storybook` 폴더만 따로 받으면 그림이 나오지 않으므로 아래 세 원본 이미지 폴더의 위치를 함께 유지해야 합니다.

- `projects/second-cup/renders/the_second_cup_final.png`
- `projects/a-place-for-rain/renders/a_place_for_rain_final.png`
- `projects/morning-on-the-sill/renders/morning_on_the_sill_final.png`

화면의 이전·다음 버튼 또는 ← → 키로 넘깁니다. 마지막 장의 ‘처음으로’는 첫 장으로 돌아갑니다.
화살표 키는 첫 장과 마지막 장에서 멈춥니다. 자동 넘김이나 소리는 없습니다.
자바스크립트를 끄면 세 장면을 한 페이지에서 순서대로 읽을 수 있습니다.
동작 줄이기 설정에서는 페이지 전환 애니메이션을 사용하지 않습니다.
인쇄할 때는 모든 장면을 표시합니다.

작은 사본만 만들려면 저장소 루트에서 다음 명령을 실행합니다. Python 표준 라이브러리만 사용하며 기존 출력 폴더를 덮어쓰지 않습니다.

```sh
python3 projects/quiet-storybook/package_offline.py --repo . --output storybook-offline
```

생성된 `storybook-offline/quiet-storybook/index.html`을 여세요. 사본에는 그림책 소스·안내·검사 도구와 원본 PNG 세 장만 들어갑니다. PNG를 다시 인코딩하거나 메타데이터를 제거하지 않으며 복사 후 SHA-256 일치를 검사합니다.

## 글과 그림

글·구성은 dot의 독창적인 짧은 이야기입니다. 사진이나 생성 콘셉트 대신, 저장소의 세 작품에서 **실제 Blender Cycles 최종 렌더**를 원본 바이트 그대로 사용합니다.

- 《두 잔의 자리》: 차가 든 잔 하나와 빈 잔 하나. 소보로를 든 승객이 돌아오기 전 배우자가 마련한 식탁입니다.
- 《비를 내려놓을 자리》: 아직 비어 있는 물받이와 훅, 조금 열린 문과 멀리 보이는 두 잔입니다. 우산이나 빵이 이미 도착한 장면이 아닙니다.
- 《볕이 돌아온 창턱》: 살아 있는 동물이 아닌 청회색 도자기 고양이 조각과 양식화된 낙엽 두 장입니다.

이 세 정물을 문학적으로 이어 읽는 독립적인 동반 작품입니다. 같은 장소의 연속 촬영이나 게임의 분기·후일담을 확정하지 않습니다. 실제 사람·집·개인사를 재현하지 않습니다. 각 원작의 제작·출처·한계는 원래 프로젝트 README와 provenance 기록에 남아 있습니다. 이 문서는 저장소 전체의 라이선스를 새로 부여하지 않습니다.

## 파일과 확인

- `index.html`, `style.css`, `story.js`: 빌드 없는 정적 그림책. 외부 글꼴·분석·네트워크 API·저장 기능이 없습니다.
- `package_offline.py`: 새 폴더에 최소 오프라인 사본을 만듭니다.
- `test_story.cjs`: Node 표준 라이브러리로 조작 상태와 접근성 관련 표시 상태를 검사합니다. 실제 브라우저나 스크린 리더 검사와는 별개입니다.
- `QA.md`: 확인한 범위와 한계.

```sh
node projects/quiet-storybook/test_story.cjs
```

## PDF 제작 소스

`build_pdf.py`는 같은 세 원본 PNG와 본문으로 3쪽 PDF를 만듭니다. Python의 reportlab, fontTools, Pillow와 설치된 Noto Serif CJK Regular TTC 글꼴이 필요합니다. 새 소프트웨어를 자동 설치하거나 글꼴을 내려받지 않습니다.

```sh
python3 projects/quiet-storybook/build_pdf.py --repo . --font NotoSerifCJK-Regular.ttc --output pdf-output/While-the-Rain-Passes.pdf
```

`--font`에는 설치된 글꼴의 실제 경로를 지정합니다. 한국어 글꼴 인덱스 기본값은 1이며 다른 TTC 구성은 `--font-index`로 지정합니다. 원본 글꼴은 수정하지 않고 필요한 글자를 임시 TrueType 부분집합 `book-subset.ttf`로 만들어 PDF에 내장합니다. 이 부분집합은 출력 PDF와 같은 폴더에 남습니다. Noto CJK의 원래 라이선스와 저작권은 `FONT_LICENSE.txt`에 보존했습니다.

PDF 생성은 이미지 크기를 낮추거나 JPEG로 손실 압축하지 않습니다. PDF의 이미지 객체에는 원본과 동일한 RGB 픽셀을 넣지만 PNG의 출처 메타데이터까지 복제하는 것은 아닙니다. 원본 PNG는 그대로 유지합니다. PDF는 태그 기반 접근성 구조를 제공하지 않으므로 의미 구조를 이용한 읽기에는 HTML판을 권합니다.
