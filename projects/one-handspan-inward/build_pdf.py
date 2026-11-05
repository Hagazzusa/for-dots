#!/usr/bin/env python3
"""『한 뼘 안쪽』을 한 쪽 PDF와 원문 바이트 그대로인 TXT로 만든다.

별도 위치에 재생성하기:
    python3 build_pdf.py --output-root /tmp/one-handspan-inward/output

필요한 패키지: reportlab, fonttools.
설치된 Noto Serif CJK Regular TTC의 한국어 글꼴을 부분 내장한다.
다른 프로젝트의 소스나 사전 생성된 글꼴 파일에는 의존하지 않는다.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path
import tempfile

from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.lib.colors import black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas


ROOT = Path(__file__).resolve().parent
TITLE = "한 뼘 안쪽"
SUBTITLE = "시조"
AUTHOR = "닷돌이"
STEM = "One-Handspan-Inward"
FONT_NAME = "OneHandspanNotoSerifKR"
DEFAULT_FONT = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
PAGE_WIDTH = PAGE_HEIGHT = 480
LEFT_MARGIN = RIGHT_MARGIN = 58
# 좌표는 PDF의 아래쪽 기준이다. 각 장을 한 행에 두고 30pt 간격을 준다.
TITLE_BASELINE = 382
SUBTITLE_BASELINE = 353
BODY_BASELINES = (278, 248, 218)
AUTHOR_BASELINE = 146
TITLE_SIZE, SUBTITLE_SIZE, BODY_SIZE, AUTHOR_SIZE = 24, 9, 12.5, 9


def read_source(path: Path) -> tuple[bytes, list[str]]:
    """제목·부제·세 행을 확인하고, 원문의 바이트는 수정하지 않는다."""
    raw = path.read_bytes()
    text = raw.decode("utf-8")
    lines = text.splitlines()
    if lines[:3] != [TITLE, SUBTITLE, ""] or len(lines) != 6:
        raise ValueError("원문은 제목, 부제, 빈 행, 시조 세 행으로 구성되어야 합니다.")
    if not all(lines[3:]):
        raise ValueError("시조의 세 행은 비어 있으면 안 됩니다.")
    if any("\t" in line or line != line.strip() for line in lines):
        raise ValueError("원문의 탭과 행 앞뒤 공백을 확인해 주세요.")
    return raw, lines


def register_reading_font(font_path: Path, characters: str, work_dir: Path) -> None:
    """Noto Serif CJK KR의 필요한 글자를 변환하여 PDF 안에 내장한다."""
    source = SourceFont(font_path, fontNumber=1, lazy=True)
    try:
        family = source["name"].getDebugName(1) or ""
        if family != "Noto Serif CJK KR":
            raise ValueError(f"TTC의 1번 글꼴이 Noto Serif CJK KR이 아닙니다: {family!r}")
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
        builder.font["head"].created = builder.font["head"].modified = 2082844800
        converted = work_dir / f"{FONT_NAME}.ttf"
        builder.save(converted)
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(converted)))
    finally:
        source.close()


def build(source_path: Path, output_root: Path, font_path: Path) -> tuple[Path, Path]:
    raw, lines = read_source(source_path)
    pdf_path = output_root.resolve() / "pdf" / f"{STEM}.pdf"
    text_path = output_root.resolve() / "text" / f"{STEM}.txt"
    with tempfile.TemporaryDirectory(prefix="one-handspan-font-") as temporary:
        register_reading_font(font_path, raw.decode("utf-8") + AUTHOR, Path(temporary))
        elements = [(TITLE, TITLE_SIZE, TITLE_BASELINE),
                    (SUBTITLE, SUBTITLE_SIZE, SUBTITLE_BASELINE)]
        elements.extend((line, BODY_SIZE, y) for line, y in zip(lines[3:], BODY_BASELINES))
        elements.append((AUTHOR, AUTHOR_SIZE, AUTHOR_BASELINE))
        for text, size, _ in elements:
            if pdfmetrics.stringWidth(text, FONT_NAME, size) > PAGE_WIDTH - LEFT_MARGIN - RIGHT_MARGIN:
                raise ValueError(f"한 행에 들어가지 않는 문장이 있습니다: {text!r}")
        buffer = io.BytesIO()
        canvas = Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT),
                        pageCompression=1, invariant=1)
        canvas.setTitle(TITLE)
        canvas.setAuthor(AUTHOR)
        canvas.setSubject(SUBTITLE)
        canvas.setCreator("ReportLab")
        canvas.setFillColor(black)
        for text, size, baseline in elements:
            canvas.setFont(FONT_NAME, size)
            canvas.drawString(LEFT_MARGIN, baseline, text)
        canvas.showPage()
        canvas.save()
        pdf_bytes = buffer.getvalue()
    if source_path.read_bytes() != raw:
        raise RuntimeError("조판 중 원문이 바뀌었습니다. 확정된 원문으로 다시 실행해 주세요.")
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    text_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.write_bytes(pdf_bytes)
    text_path.write_bytes(raw)
    return pdf_path, text_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "poem.txt", help="편집 원문 TXT")
    parser.add_argument("--output-root", type=Path, default=ROOT / "output", help="PDF·TXT 출력 폴더")
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT, help="Noto Serif CJK Regular TTC")
    args = parser.parse_args()
    for path in build(args.source, args.output_root, args.font):
        print(path)


if __name__ == "__main__":
    main()
