# 의자 두 개

이삿날 중고 식탁을 가져가러 온 사람 앞에서, 두 룸메이트가 의자의 주인을 서로 다르게 기억합니다. 다리 하나를 떼어 놓은 식탁부터 다시 세워야 하는 짧은 소설입니다.

- [읽기용 PDF](output/pdf/Two-Chairs.pdf)
- [텍스트](output/text/Two-Chairs.txt)
- [편집 원문](story.txt)

## 원본과 제작

`story.txt`가 편집 원본입니다. `build_pdf.py`는 원문을 읽어 한국어 글꼴을 내장한 PDF와 원문 바이트가 같은 TXT를 만듭니다. 제목·본문은 원문 그대로 두고 읽기용 판형에 조판합니다.

Python, ReportLab, fontTools, pdfplumber, pypdf가 필요합니다. 쪽을 이미지로 확인할 때는 Poppler의 `pdftoppm`을 사용했습니다. 제작 글꼴은 Noto Serif CJK KR이며 기본 경로는 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`입니다. 글꼴은 SIL Open Font License 1.1로 제공되며 사용 글자만 변환·내장합니다.

기존 결과를 덮어쓰지 않도록 별도 사본에서 실행합니다.

```sh
python3 build_pdf.py
python3 verify.py
```

기본 검사는 공개 파일을 바꾸지 않습니다. 검사 기록 저장은 검증기의 명시적 출력 옵션으로만 수행합니다. `qa.json`은 조판 검사 기록이고, `manifest.json`은 보존 파일의 크기와 SHA-256입니다. `tmp/`의 임시 이미지·중간 작업은 보존 대상에서 제외합니다.

## 검토 범위

가격과 소유권에 대한 인물의 기억, 식탁 분해와 의자 운반의 순서, 마지막 교통편 대화의 인과를 읽고 다듬었습니다. 원문과 추출 글자열, TXT 바이트, 글꼴 내장, 글자 경계와 겹침을 검사하고 PDF의 4쪽 모두를 이미지로 확인했습니다. 공개 파일만 담은 별도 사본에서도 검사가 실행되며, 제작 소스만 옮긴 사본에서 다시 만든 PDF·TXT의 바이트와 4쪽 렌더 픽셀이 원본과 일치했습니다. 실제 인쇄물과 모든 뷰어의 표시는 별도 확인 범위입니다.
