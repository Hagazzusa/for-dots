# 이리 와

작은방에서 난 소리가 정확히 십 분 뒤에 들립니다. 고양이 만두를 이동장에 넣어야 하는 은서와 동생에게, 조금 전의 소란이 뒤늦게 돌아오는 짧은 환상소설입니다.

- [읽기용 PDF](output/pdf/Come-Here.pdf)
- [텍스트](output/text/Come-Here.txt)
- [편집 원문](story.txt)

## 원본과 제작

`story.txt`가 편집 원본입니다. `build_pdf.py`는 한국어 글꼴을 내장한 PDF와 원문 바이트가 같은 TXT를 만듭니다. Noto Serif CJK KR의 사용 글자만 변환·내장하며, 글꼴은 SIL Open Font License 1.1을 따릅니다.

Python, ReportLab, fontTools, pdfplumber, pypdf가 필요합니다. 기본 글꼴 경로는 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`입니다. PDF를 이미지로 볼 때는 Poppler를 사용합니다.

기존 결과를 덮어쓰지 않도록 별도 사본에서 실행합니다.

```sh
python3 build_pdf.py
python3 verify.py
```

`verify.py`의 기본 실행은 파일을 바꾸지 않습니다. `--report 경로.json`을 지정할 때만 검사 기록을 저장합니다. `qa.json`은 조판 검사 기록이고, `manifest.json`은 보존 파일의 크기와 SHA-256입니다. `studies/`와 `tmp/`의 중간 작업은 정식 보존 범위에서 제외합니다.

## 내용 검토

방 안팎에서 생긴 소리의 차이, 원래 자리에서 한 번만 재생되는 규칙, 사건과 소리 사이의 십 분 간격, 이동장과 인물의 위치를 검토했습니다. 만두가 다시 숨는 목적지와 이동장을 옮기려다 멈추는 행동을 분명하게 다듬었습니다.

## 결과 확인과 한계

완성 PDF는 3쪽입니다. 세 쪽을 모두 이미지로 확인했고, 원문 글자 순서·문단·대화 묶음·내장 글꼴·경계·겹침 검사를 통과했습니다. 공개 입력 세 파일만 복사한 별도 사본에서 PDF와 TXT를 다시 만들어 바이트가 일치했고, 144dpi 전 페이지 렌더 픽셀도 일치했습니다. 같은 설치 환경에서 확인한 결과이며 다른 라이브러리·글꼴 버전의 동일 출력을 보장하지 않습니다. 실제 인쇄·낭독이나 독자 반응은 확인하지 않았습니다.
