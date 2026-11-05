# 대답 앞에서

첫 월급으로 산 구두 이야기를 삼 분짜리 녹음으로 만들려는 자녀와 어머니의 짧은 소설입니다. 두 사람이 같은 녹음을 들으면서 남기고 싶은 부분이 달라집니다.

[읽기용 PDF](output/pdf/Before-the-Answer.pdf) · [텍스트](output/text/Before-the-Answer.txt) · [편집 원고](story.txt)

## 파일

- `story.txt`: 제목과 부제를 포함한 최종 원고.
- `output/pdf/Before-the-Answer.pdf`: 글꼴을 포함한 읽기용 PDF.
- `output/text/Before-the-Answer.txt`: 원고와 바이트가 같은 전달용 텍스트.
- `build_pdf.py`: 원고에서 PDF와 전달용 텍스트를 만드는 코드.
- `verify.py`, `qa.json`: 텍스트 일치와 페이지 경계 검사 및 결과.
- `manifest.json`: 공개 보존 대상의 크기와 SHA-256.

## 재현

Python, fontTools, ReportLab, pdfplumber, pypdf가 필요합니다. 페이지 미리보기에는 Poppler를 사용했습니다. 글꼴은 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`의 한국어 Noto Serif CJK이며 SIL Open Font License 1.1에 따라 PDF에 부분집합을 포함합니다.

기존 결과물을 덮어쓰지 않도록 이 폴더의 별도 사본에서 실행합니다.

```sh
python3 build_pdf.py
python3 verify.py
mkdir -p tmp/pdfs/pages
pdftoppm -scale-to 1200 -png output/pdf/Before-the-Answer.pdf tmp/pdfs/pages/page
```

## 검토 범위

인물의 요구가 작가의 해설로 바뀌는 대목과 녹음·편집의 시간 관계를 읽고 고쳤습니다. 허구의 인물과 상황이며 실제 도서관 사업이나 녹음 현장의 관행을 설명하는 글은 아닙니다.

PDF의 모든 페이지를 이미지로 확인하고 원고와 추출 글자열, 글자 경계, 전달용 텍스트를 검사했습니다. 별도 사본에서 재생성 결과도 비교했습니다. 독자 대상 평가나 음성 낭독은 진행하지 않았습니다.
