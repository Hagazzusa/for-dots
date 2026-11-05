# 맨 앞

홍보 영상 촬영에서 줄의 맨 앞을 맡은 지완의 하루를 다룬 짧은 소설. 기다리는 동작을 연기하는 사람들 사이로 실제 손님이 들어온다.

인물과 사건은 허구다. 실제 업체나 촬영 사례를 재현하지 않았다.

## 완성본

- `output/pdf/Front-of-the-Line.pdf`: 6쪽 읽기용 PDF.
- `output/text/Front-of-the-Line.txt`: 같은 원고의 UTF-8 텍스트.
- `story.txt`: 편집용 원문.

시간의 흐름, 등장인원, 문을 통과하는 동작, 소품과 정산 순서를 검토했다. 해설을 덧붙이기보다 인물이 실제로 하는 마지막 행동을 완결하는 쪽으로 결말을 다듬었다.

## 재현과 검사

Python 3, ReportLab, fontTools, PyMuPDF와 시스템 Noto Serif CJK 글꼴이 필요하다. 페이지 이미지는 Poppler로 만든다.

```sh
mkdir -p tmp/pdfs output/pdf output/text
python3 build_pdf.py
cp story.txt output/text/Front-of-the-Line.txt
python3 verify.py
pdftoppm -png -scale-to 1200 output/pdf/Front-of-the-Line.pdf tmp/pdfs/page
```

PDF에는 한글 글꼴을 부분 포함했다. 검사 스크립트는 PDF에서 추출한 본문이 원문과 공백을 제외하고 같은지, 텍스트 파일이 원문과 바이트 단위로 같은지, 본문이 지면의 여백 안에 들어가는지 확인한다. 재생성한 문서의 시각 검토는 별도로 해야 한다.

이번 완성본은 여섯 페이지를 모두 이미지로 확인했다. `qa.json`에 검사 범위와 완성 파일의 해시를, `manifest.json`에 소스와 결과물의 해시를 보존했다.
