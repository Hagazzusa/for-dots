"""Noto CJK의 한국어 글꼴을 필요한 문자만 PDF에 내장한다."""
from pathlib import Path
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT_NAME = "WithoutASlamNotoSerifKR"
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

