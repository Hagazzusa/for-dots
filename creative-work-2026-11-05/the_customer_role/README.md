# 고객 역할

**The Customer Role** · Original Korean short fiction · Completed 2026-11-05

고장 난 냉장고 때문에 항의하는 고객을 연기하는 배우가, 상담 실습 도중 대본에 없던 손님들을 만들어 낸다. 실습을 다시 시작해도 그 손님들은 사라지지 않는다.

The narrator treats anger as a performance problem. His improvised complaint begins to require decisions that the script does not contain. The story keeps the instructor, experienced worker and narrator within their separate practical concerns rather than assigning one of them the final answer.

## Final files

- `story.txt`: complete Korean source, 3,827 characters including title, subtitle and whitespace.
- `output/pdf/The-Customer-Role.pdf`: five-page reading edition.
- `output/text/The-Customer-Role.txt`: identical plain-text edition.
- `build_pdf.py`: self-contained PDF builder using the installed Noto Serif CJK font.
- `verify.py`: source/output equivalence and layout-bound checks.
- `qa.json`, `manifest.json`: verification results and file hashes.

The earlier backup contained an unfinished draft. This directory now contains the revised, reviewed story and its final reading editions. Drafts and private working notes remain in the ignored `studies/` directory; page renders and font subsets remain in ignored `tmp/`.

## Revision and verification

Two independent editorial reads checked the narrator's voice, scene logistics, humor and ending. Revision clarified the chairs' orientation and participant rotation, removed an explanatory passage after the break-room exchange, and reduced peripheral jokes. The narrator's imperfect listening and the unresolved final line were retained.

All five final PDF pages were rendered and inspected. Extracted body text matches the source after whitespace normalization; the TXT edition matches its bytes. Text bounds, page sizes and page density were checked programmatically.

This is fiction. The company, training scenario and dialogue do not represent a real organization or a verified customer-service policy. Editorial review is not audience testing.

## Reproduce

Requires Python, ReportLab, fontTools, PyMuPDF, and an installed Noto Serif CJK collection at the path used in the builder. The PDF embeds a converted font subset. Noto CJK is distributed under the SIL Open Font License 1.1.

```sh
mkdir -p tmp/pdfs output/pdf output/text
python3 build_pdf.py
cp story.txt output/text/The-Customer-Role.txt
python3 verify.py
```
