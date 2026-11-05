# 고객 역할

**The Customer Role** · 직접 쓴 한국어 단편소설 · 2026-11-05 완성

고장 난 냉장고 때문에 항의하는 고객을 연기하는 배우가, 상담 실습 도중 대본에 없던 손님들을 만들어 낸다. 실습을 다시 시작해도 그 손님들은 사라지지 않는다.

[5쪽 PDF 읽기·내려받기](output/pdf/The-Customer-Role.pdf) · [일반 텍스트 TXT 읽기·내려받기](output/text/The-Customer-Role.txt)

화자는 분노를 연기의 문제로 다룹니다. 즉흥적으로 시작한 항의에는 점차 대본에 없는 결정이 필요해집니다. 이야기는 강사와 숙련된 직원, 화자 각자의 실무적인 고민을 따라가며, 어느 한 사람에게 최종 답을 맡기지 않습니다.

## 최종 파일

- `story.txt`: 제목, 부제, 공백을 포함해 3,827자인 한국어 전체 원문.
- `output/pdf/The-Customer-Role.pdf`: 5쪽 읽기용 판본.
- `output/text/The-Customer-Role.txt`: 원문과 동일한 일반 텍스트 판본.
- `build_pdf.py`: 설치된 Noto Serif CJK 글꼴을 사용하는 독립 실행형 PDF 생성기.
- `verify.py`: 원문·출력의 일치 여부와 배치 경계 검사.
- `qa.json`, `manifest.json`: 검증 결과와 파일 해시.

이전 백업에는 미완성 초고가 들어 있었습니다. 이 디렉터리에는 수정과 검토를 마친 이야기와 최종 읽기용 판본이 들어 있습니다. 초고와 비공개 작업 노트는 Git에서 제외한 `studies/` 디렉터리에, 페이지 렌더와 글꼴 부분집합은 제외한 `tmp/`에 남아 있습니다.

## 수정과 검증

서로 독립적인 두 차례의 편집 검토에서 화자의 목소리, 장면 속 동선과 배치, 유머, 결말을 확인했습니다. 수정 과정에서 의자가 향하는 방향과 참가자 교대 방식을 명확히 하고, 휴게실 대화 뒤의 설명 문단을 삭제했으며, 주변적인 농담을 줄였습니다. 화자가 온전히 듣지 못하는 모습과 미해결 상태로 남는 마지막 문장은 유지했습니다.

최종 PDF 다섯 쪽을 모두 렌더링해 눈으로 확인했습니다. 추출한 본문은 공백을 정규화한 뒤 원문과 일치하며, TXT 판본은 원문의 바이트와 일치합니다. 텍스트 경계, 페이지 크기, 페이지 밀도는 프로그램으로 검사했습니다.

이 작품은 소설입니다. 회사와 교육 상황, 대화는 실제 조직이나 검증된 고객 응대 방침을 나타내지 않습니다. 편집 검토는 독자 반응 시험이 아닙니다.

## 재현

Python, ReportLab, fontTools, PyMuPDF가 필요하며, 생성기에 지정된 경로에 Noto Serif CJK 글꼴 모음이 설치되어 있어야 합니다. PDF에는 변환한 글꼴 부분집합을 내장합니다. Noto CJK는 SIL Open Font License 1.1에 따라 배포됩니다.

```sh
mkdir -p tmp/pdfs output/pdf output/text
python3 build_pdf.py
cp story.txt output/text/The-Customer-Role.txt
python3 verify.py
```
