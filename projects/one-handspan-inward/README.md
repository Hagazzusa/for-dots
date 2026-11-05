# 한 뼘 안쪽

엘리베이터의 닫힘 버튼과 바깥에서 들어오는 손, 안쪽에서 옮기는 뒤꿈치를 담은 시조 한 수입니다.

- [읽기용 PDF](output/pdf/One-Handspan-Inward.pdf)
- [텍스트](output/text/One-Handspan-Inward.txt)
- [편집 원문](poem.txt)

## 형식

3장 12음보로 구성했습니다. 정한 음보에 따른 표기 음절 수는 초장 3·5·3·4, 중장 3·5·3·4, 종장 3·5·4·3으로, 전체 45음절입니다. 이 수치는 원문의 형식을 확인하기 위한 것이며 작품의 완성도를 뜻하지 않습니다.

`meter.json`에 음보를 구분해 두었고 `verify_meter.py`가 원문과의 일치 및 한글 표기 음절 수를 읽기 전용으로 검사합니다. 읽기용 PDF에는 분절 기호를 넣지 않고 세 행으로 조판했습니다.

## 제작과 보존

`poem.txt`가 편집 원본입니다. `build_pdf.py`는 자체 포함한 글꼴 변환 코드로 Noto Serif CJK KR의 사용 글자를 내장하고, 원문 바이트가 같은 TXT를 함께 만듭니다. 기본 글꼴 경로는 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`이며 SIL Open Font License 1.1을 따릅니다.

기존 결과를 덮어쓰지 않도록 별도 사본에서 실행합니다.

```sh
python3 build_pdf.py
python3 verify.py
python3 verify_meter.py
```

조판과 검사에는 Python, ReportLab, fontTools, pdfplumber, pypdf가 필요합니다. PDF를 이미지로 확인할 때는 Poppler를 사용합니다. 기본 검증은 파일을 바꾸지 않고, `verify.py --report 경로.json`을 지정할 때만 검사 기록을 저장합니다. `qa.json`과 `manifest.json`에 조판 검사 및 보존 파일의 SHA-256을 기록합니다.

## 확인한 범위

원문의 표현과 시조 형식을 검토하고, 표기 음절 45개 및 정한 음보와의 일치를 검사했습니다. PDF 한 쪽을 이미지로 확인했으며 글꼴 내장, 공백을 포함한 본문 행 일치, 글자 경계와 겹침, 세 장의 한 행 유지를 검사했습니다. 실제 인쇄와 낭독은 확인하지 않았습니다.

제작에 필요한 공개 입력 세 파일만 옮긴 사본에서 PDF·TXT의 바이트와 144dpi 렌더 픽셀이 원본과 일치했습니다. 보존 파일만 담은 사본에서도 두 검증기가 입력 파일을 변경하지 않고 실행됩니다.
