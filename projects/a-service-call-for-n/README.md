# 받침 출장

황동 이름표에서 ㄴ이 떨어진 밤, 현관문이 커다란 무로 바뀝니다. 부품이 떨어진 수리공과 집주인은 다른 물건에서 받침 하나를 빌려 오기로 합니다.

**완성한 짧은 환상소설입니다.** 물건이 바뀌는 우스운 사건과, 잠시 다른 모양이 된 찻잔을 다루는 행동으로 이야기를 닫았습니다. 기존 게임이나 다른 소설의 확정 설정과 연결하지 않은 독립 작품입니다.

- [읽기용 PDF](output/pdf/A-Service-Call-for-N.pdf), 3쪽
- [읽기용 TXT](output/text/A-Service-Call-for-N.txt)
- [편집 원문](story.txt)

## 원본과 조판

`story.txt`가 편집 원본입니다. `build_pdf.py`는 원문과 바이트가 같은 TXT 및 한글 글꼴을 내장한 PDF를 만듭니다. 이전 「이리 와」의 조판·검사 코드를 이 프로젝트 안에 독립 사본으로 두고 제목과 출력 이름을 바꿨습니다. 이전 프로젝트의 파일이나 결과물을 수정하지 않았습니다.

Python, ReportLab, fontTools, pdfplumber, pypdf가 필요합니다. 기본 글꼴은 `/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc`의 한국어 글꼴입니다. 사용 글자만 변환·내장하며 Noto CJK의 SIL Open Font License 1.1을 따릅니다. 글꼴 원본을 별도 파일로 배포하지 않습니다.

기존 결과를 덮어쓰지 않으려면 출력 폴더를 따로 지정합니다.

```sh
python3 build_pdf.py --output-root /tmp/service-call-check/output
python3 verify.py --output-root /tmp/service-call-check/output
```

## 검토와 확인 범위

문→무, 잔→자의 변환, ㄴ 한 개를 빌려 쓰는 동안 다른 물건을 동시에 복구할 수 없는 조건, 금요일부터 월요일까지의 임시 사용, 인물과 문·매트·찻잔의 위치를 검토했습니다. 낯선 현상을 설명하는 문단은 한 군데로 모으고 이후에는 수리와 차를 대접하는 행동에 집중했습니다.

PDF 세 쪽을 모두 이미지로 확인했습니다. 원문 글자 순서, 배포 TXT 바이트, 문단과 인접 대화의 한 쪽 유지, 글꼴 내장, 글자 경계·행 겹침 검사를 통과했습니다. 결과는 [qa.json](qa.json)에 기록합니다. 원문·제작·검사 소스만 복사한 별도 폴더에서 PDF·TXT 바이트와 1100px 전 페이지 렌더 픽셀이 일치했습니다. 같은 설치 환경에서 확인한 결과입니다. 실제 인쇄·낭독·독자 반응은 확인하지 않았습니다.

`verify.py`는 기본 실행에서 파일을 변경하지 않습니다. `--report 경로.json`을 지정할 때만 검사 기록을 저장합니다. `manifest.json`은 자신을 제외한 보존 파일의 크기와 SHA-256입니다. 렌더된 검사 이미지·임시 글꼴·캐시는 공개 보존 범위에 포함하지 않습니다.
