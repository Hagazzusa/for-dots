# 통째로

두 손을 위한 짧은 낭독문입니다. 냉장고에 수박 하나를 넣으라는 명령이 이어집니다. 말을 따라갈수록 손에 들거나 내려놓아야 하는 것이 늘어납니다.

[한 쪽 PDF 읽기](Whole-Watermelon.pdf) · [텍스트 읽기](Whole-Watermelon.txt)

## 작품과 수정

모든 문장을 명령형으로 썼습니다. 초고는 선반을 다시 끼우는 동작으로 끝났지만, 마지막을 이미 든 물건을 내려놓기 전에 해야 하는 지시로 바꾸었습니다. 읽는 말과 따라 하는 몸 사이에 생기는 어긋남을 남겼습니다.

## 파일

- [script.txt](script.txt): 행과 연 구분을 포함한 원문.
- [Whole-Watermelon.pdf](Whole-Watermelon.pdf): 글꼴을 포함한 한 쪽짜리 낭독판.
- [Whole-Watermelon.txt](Whole-Watermelon.txt): 원문과 바이트가 같은 텍스트판.
- [build_pdf.py](build_pdf.py): PDF 제작 코드.
- [verify.py](verify.py): 원문·PDF 행·여백 검사.
- `qa.json`, `manifest.json`: 검사 결과와 파일 해시.

초고와 검토용 자료, 임시 글꼴·페이지 이미지는 공개 추적에서 제외합니다.

## 재현

Python, fontTools, ReportLab, PyMuPDF와 Noto Serif CJK 글꼴이 필요합니다. 제작 코드는 설치된 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`의 한국어 글꼴을 사용하고 필요한 글자만 변환해 PDF에 포함합니다. Noto CJK의 라이선스는 SIL Open Font License 1.1입니다.

이 폴더의 별도 사본에서 실행하면 결과물을 다시 만들 수 있습니다.

```sh
python3 build_pdf.py
python3 verify.py
```

## 확인한 범위

문장의 명령형, 물건과 손의 동작 순서, 결말의 시간 구조를 검토했습니다. 최종 PDF 전체를 이미지로 확인했고, 제목·부제·본문의 행 일치와 여백을 검사했습니다. 텍스트판은 원문과 바이트가 같습니다.

완성된 창작 낭독문이며 실용적인 가전제품 안내문은 아닙니다. 낭독 녹음이나 실제 동작 공연은 제작·평가하지 않았습니다.
