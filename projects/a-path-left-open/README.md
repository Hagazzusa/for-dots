# 길을 남기는 일

[조각과 1번 문제 PDF](output/pdf/A-Path-Left-Open.pdf) · **[권장 2번: 다른 길을 남기기](output/pdf/A-Path-Left-Open-Replacement.pdf)** · [권장 2번 해답](output/pdf/A-Path-Left-Open-Replacement-Answer.pdf)

네 조각을 놓고, 놓지 않은 아홉 칸으로 길을 만드는 종이 퍼즐. 판을 가득 채우는 대신 통과할 자리를 남기는 일을 목표로 삼았다. 같은 조각으로 1번과 대체 2번을 풉니다. 최초 PDF의 두 해답은 판을 180° 돌리면 같은 조각 배치여서, 새로 풀 때는 별도 대체 2번을 권장합니다.

## 사용

원본 PDF의 1쪽에는 조각이 있고, 2쪽의 위쪽이 1번 문제다. 2번은 [별도 대체 문제 PDF](output/pdf/A-Path-Left-Open-Replacement.pdf)를 인쇄해서 푼다. 원본 2쪽 아래의 최초 2번은 기록으로 남겨 두었다. A4 용지에 **단면, 100%(실제 크기)**로 인쇄한다. 첫 장의 기준선이 50mm인지 확인한 뒤 조각의 바깥 실선만 오린다. 안쪽 점선은 자르지 않는다. 같은 조각 세트를 두 판에 번갈아 쓴다.

네 조각을 모두 격자에 맞춰 놓는다. 겹치거나 판 밖으로 나가면 안 된다. 90도 회전과 뒤집기가 허용된다. 출발, 도착, 작은 점이 있는 칸은 비워 두고, 남은 아홉 칸을 가로·세로로 이어 길을 만든다. 대각선 접촉은 연결로 세지 않는다. 조각의 색은 규칙이 아니므로 뒤집어 뒷면이 보여도 괜찮다.

1번 해답은 [최초 해답 PDF](output/pdf/A-Path-Left-Open-Answers.pdf)의 2쪽 위에 있다. 이 파일에는 최초 2번 해답도 함께 들어 있다. 대체 2번 해답은 [별도 PDF](output/pdf/A-Path-Left-Open-Replacement-Answer.pdf)에 있다.

## 구성과 검증

기존 폴리오미노 형태를 사용하여 조각 조합, 문제의 점 위치, 지면을 설계했다. 새로운 도형이나 최초의 퍼즐 유형을 주장하지 않는다.

- 5×5 판, 한 칸 18mm, 판 한 변 90mm.
- 조각 면적은 3+3+5+5=16칸. 빈칸은 9칸.
- 최초 문제 1번과 2번의 유효한 배치는 각각 4개와 1개다. 대체 2번에는 유효한 배치가 1개 있고, 그 배치는 최초 두 문제의 어떤 해답과도 회전·반사로 일치하지 않는다. 대체 2번의 점 위치(3열 1행, 4열 2행), 보드 한 변 90mm와 기준선 50mm, 별도 해답의 배치를 확인했다.
- 출발과 도착 사이의 최단 거리는 8번 이동이므로, 9개의 빈칸으로 연결되면 모든 빈칸이 경로에 쓰인다. 오른쪽·아래쪽 이동의 70개 순서를 모두 조사했다.
- 별도의 검증기는 조각 배치 29,724개를 열거하고 빈칸의 연결을 탐색했다. 조건 없는 유효 배치 24개와 경로 10개, 선택한 문제의 해답 수가 일치했다.
- 최초 PDF의 벡터 크기, 조각 면적, 글자 범위, 기준선 길이를 검사했다. 최초 네 페이지와 대체 문제·해답 두 페이지를 렌더링하여 레이아웃을 확인했다.

실물 인쇄와 재단, 시간 제한을 둔 플레이 테스트는 하지 않았다. 프린터의 자동 맞춤을 끄고 기준선을 확인해야 한다. 난이도나 예상 풀이 시간은 정하지 않았다.

## 최초 문제 재현

아래 코드는 최초 문제와 해답을 재현한다. 대체 문제와 해답은 공유 당시 PDF를 그대로 보존했으며, 별도 생성 소스는 확인하지 못했다.

Python 3와 reportlab, fontTools, PyMuPDF, 시스템 Noto Sans CJK 글꼴이 필요하다. PNG 점검에는 Poppler를 사용했다.

```sh
mkdir -p tmp/pdfs output/pdf
python3 solve.py
python3 independent_verify.py
python3 build_pdf.py
python3 verify_pdf.py
pdftoppm -png -scale-to 1100 output/pdf/A-Path-Left-Open.pdf tmp/pdfs/puzzle
pdftoppm -png -scale-to 1100 output/pdf/A-Path-Left-Open-Answers.pdf tmp/pdfs/answers
```

검사 스크립트는 자동 검사를 다시 기록한다. 재생성한 PDF의 시각 검토는 별도로 수행해야 한다. `qa.json`은 이번 최종본에 대한 검토 기록이며 `manifest.json`에 완성 파일과 소스의 SHA-256을 보존한다.
