#!/usr/bin/env python3
"""『남은 작업』의 편집 원문을 읽기용 PDF와 바이트 동일 TXT로 만든다.

기존 결과를 덮어쓰지 않는 재현 검사:
    python3 build_reading.py --output-root /tmp/remaining-work-check/output
    python3 verify_reading.py --output-root /tmp/remaining-work-check/output

필요한 패키지: reportlab, fonttools. 원본 글꼴은 Noto Serif CJK KR이다.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import tempfile
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.lib.colors import black
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer


ROOT = Path(__file__).resolve().parent
TITLE = "남은 작업"
SUBTITLE = "짧은 소설"
STEM = "Remaining-Work"
FONT_NAME = "RemainingWorkNotoSerifKR"
DEFAULT_FONT = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
PAGE_WIDTH, PAGE_HEIGHT = 480, 680
LEFT_MARGIN = RIGHT_MARGIN = 48
TOP_MARGIN, BOTTOM_MARGIN = 44, 46
FOOTER_BASELINE = 24


def read_source(path: Path) -> tuple[bytes, list[str]]:
    """제목과 부제를 확인하되, 원본 파일의 공백이나 줄바꿈은 고치지 않는다."""
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    if lines[:2] != [TITLE, SUBTITLE]:
        raise ValueError("원문의 첫 두 줄은 ‘남은 작업’, ‘짧은 소설’이어야 합니다.")
    if not any(line.strip() for line in lines[2:]):
        raise ValueError("소설 본문이 비어 있습니다.")
    if any("\t" in line or line != line.strip() for line in lines):
        raise ValueError("조판 전 원문의 탭과 행 앞뒤 공백을 확인해 주세요.")
    return raw, lines


def register_reading_font(font_path: Path, characters: str, work_dir: Path) -> None:
    """사용한 글자만 변환·내장해 한글 글꼴이 없는 환경에서도 읽게 한다."""
    # Noto Serif CJK TTC에서 1번 글꼴은 한국어 KR이다.
    source = SourceFont(font_path, fontNumber=1, lazy=True)
    try:
        cmap = source.getBestCmap()
        missing = sorted({c for c in characters if not c.isspace() and ord(c) not in cmap})
        if missing:
            raise ValueError(f"글꼴에서 찾을 수 없는 글자: {''.join(missing)!r}")
        options = subset.Options()
        options.recalc_timestamp = False
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=characters)
        subsetter.subset(source)
        order = source.getGlyphOrder()
        glyph_set = source.getGlyphSet()
        glyphs = {}
        for name in order:
            pen = TTGlyphPen(None)
            glyph_set[name].draw(Cu2QuPen(pen, 1.0, reverse_direction=True))
            glyphs[name] = pen.glyph()
        builder = FontBuilder(source["head"].unitsPerEm, isTTF=True)
        builder.setupGlyphOrder(order)
        builder.setupCharacterMap(source.getBestCmap())
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics(dict(source["hmtx"].metrics))
        builder.setupHorizontalHeader(ascent=source["hhea"].ascent, descent=source["hhea"].descent)
        builder.setupNameTable({
            "familyName": FONT_NAME,
            "styleName": "Regular",
            "uniqueFontIdentifier": FONT_NAME,
            "fullName": FONT_NAME,
            "psName": FONT_NAME,
            "copyright": "Noto CJK, SIL Open Font License 1.1. Converted subset for PDF embedding.",
        })
        builder.setupOS2(
            sTypoAscender=source["OS/2"].sTypoAscender,
            sTypoDescender=source["OS/2"].sTypoDescender,
            usWinAscent=source["OS/2"].usWinAscent,
            usWinDescent=source["OS/2"].usWinDescent,
        )
        builder.setupPost()
        builder.setupMaxp()
        # PDF뿐 아니라 임시 글꼴의 시각도 고정해 같은 입력의 재생성을 비교한다.
        builder.font["head"].created = builder.font["head"].modified = 2082844800
        converted = work_dir / f"{FONT_NAME}.ttf"
        builder.save(converted)
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(converted)))
    finally:
        source.close()


def make_flowables(lines: list[str]) -> list:
    common = {"fontName": FONT_NAME, "textColor": black}
    title = ParagraphStyle("제목", fontSize=25, leading=32, spaceAfter=7, **common)
    subtitle = ParagraphStyle("부제", fontSize=10, leading=16, spaceAfter=24, **common)
    body = ParagraphStyle(
        "본문", fontSize=11.5, leading=17.6, firstLineIndent=11.5,
        spaceAfter=1.7, wordWrap="CJK", allowWidows=0, allowOrphans=0,
        splitLongWords=True, **common,
    )
    title.keepWithNext = subtitle.keepWithNext = True
    result = [Paragraph(escape(lines[0]), title), Paragraph(escape(lines[1]), subtitle)]
    # SimpleDocTemplate의 Frame 기본 안쪽 여백은 좌우 각 6pt다.
    frame_width = PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN - 12
    body_lines = lines[2:]
    while body_lines and not body_lines[0]:
        body_lines = body_lines[1:]
    while body_lines and not body_lines[-1]:
        body_lines = body_lines[:-1]
    paragraphs = []
    for index, line in enumerate(body_lines):
        if not line:
            paragraphs.append(Spacer(1, 5))
            continue
        paragraph = Paragraph(escape(line), body)
        paragraph.wrap(frame_width, PAGE_HEIGHT)
        wrapped = paragraph.blPara.lines
        # 문단 끝에 다섯 글자 이하만 남으면 마지막 두 어절을 함께 옮긴다.
        # 원문은 그대로 두고 조판용 줄바꿈만 넣어 외톨이 종결어미를 막는다.
        last_text = "".join(wrapped[-1][1])
        if len(wrapped) > 1 and len(last_text.strip()) <= 5:
            words = line.rsplit(" ", 2)
            if len(words) == 3:
                paragraph = Paragraph(escape(words[0]) + "<br/>" + escape(" ".join(words[1:])), body)
        paragraphs.append(paragraph)
    # 빈 행 없이 이어지는 짧은 대화는 한 묶음으로 유지한다.
    # 서술 문단은 모두 짧으므로 한 쪽에 두어 쪽머리에 조사만 남지 않게 한다.
    index = 0
    while index < len(body_lines):
        line = body_lines[index]
        if line.startswith("“"):
            finish = index + 1
            while finish < len(body_lines) and body_lines[finish].startswith("“"):
                finish += 1
            result.append(KeepTogether(paragraphs[index:finish]))
            index = finish
        else:
            result.append(KeepTogether([paragraphs[index]]) if line else paragraphs[index])
            index += 1
    return result


def draw_footer(canvas: Canvas, document: SimpleDocTemplate) -> None:
    canvas.saveState()
    canvas.setFillColor(black)
    canvas.setFont(FONT_NAME, 8)
    canvas.drawCentredString(PAGE_WIDTH / 2, FOOTER_BASELINE, str(document.page))
    canvas.restoreState()


def build(source_path: Path, output_root: Path, font_path: Path) -> tuple[Path, Path]:
    raw, lines = read_source(source_path)
    output_root = output_root.resolve()
    pdf_path = output_root / "pdf" / f"{STEM}.pdf"
    text_path = output_root / "text" / f"{STEM}.txt"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    # 임시 글꼴은 저장소 밖에서 지우며 재현용 파일로 추적하지 않는다.
    with tempfile.TemporaryDirectory(prefix="remaining-work-font-") as temporary:
        register_reading_font(font_path, raw.decode("utf-8") + "0123456789", Path(temporary))
        buffer = io.BytesIO()
        document = SimpleDocTemplate(
            buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
            leftMargin=LEFT_MARGIN, rightMargin=RIGHT_MARGIN,
            topMargin=TOP_MARGIN, bottomMargin=BOTTOM_MARGIN,
            title=TITLE, author="닷돌이", subject=SUBTITLE,
            pageCompression=1, invariant=1,
        )
        document.build(
            make_flowables(lines), onFirstPage=draw_footer, onLaterPages=draw_footer,
            canvasmaker=Canvas,
        )
        pdf_bytes = buffer.getvalue()
    # 생성 도중 편집된 원고와 서로 다른 산출물이 섞이지 않도록 중단한다.
    if source_path.read_bytes() != raw:
        raise RuntimeError("PDF 제작 중 원문이 바뀌었습니다. 최종 원문으로 다시 실행해 주세요.")
    pdf_path.write_bytes(pdf_bytes)
    text_path.write_bytes(raw)
    return pdf_path, text_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "story.txt", help="편집 원문 TXT")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output", help="PDF·TXT 출력 폴더")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="Noto Serif CJK Regular TTC")
    args = parser.parse_args()
    for path in build(args.source, args.output_root, args.font):
        print(path)


if __name__ == "__main__":
    main()
