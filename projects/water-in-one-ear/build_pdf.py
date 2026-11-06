"""Noto CJK의 한국어 글꼴을 필요한 문자만 PDF에 내장한다."""
from pathlib import Path
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
FONT_NAME = "WaterInOneEarNotoSerifKR"
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



def main():
    import argparse,tempfile
    from reportlab.pdfgen.canvas import Canvas
    p=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser(description="시 원문을 한 쪽 PDF와 TXT로 조판합니다.")
    ap.add_argument("--output-root",type=Path,default=p/"output")
    a=ap.parse_args()
    raw=(p/"poem.txt").read_bytes();lines=raw.decode("utf-8").splitlines()
    assert lines[0]=="귀에 든 물" and len([x for x in lines[2:] if x])==14
    out=a.output_root; (out/"pdf").mkdir(parents=True,exist_ok=True);(out/"text").mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        register_reading_font(Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc"),raw.decode("utf-8"),Path(td))
        c=Canvas(str(out/"pdf/Water-in-One-Ear.pdf"),pagesize=(480,680),invariant=1)
        c.setTitle(lines[0]);c.setAuthor("닷돌이");c.setSubject("자유시")
        c.setFillColorRGB(0,0,0);c.setFont(FONT_NAME,25);c.drawString(72,591,lines[0])
        c.setFont(FONT_NAME,14);y=526
        for line in lines[2:]:
            if line:
                assert pdfmetrics.stringWidth(line,FONT_NAME,14)<=336
                c.drawString(72,y,line);y-=24
            else:y-=15
        assert y>80
        c.save()
    assert (p/"poem.txt").read_bytes()==raw
    (out/"text/Water-in-One-Ear.txt").write_bytes(raw)
    print(out/"pdf/Water-in-One-Ear.pdf")
if __name__=="__main__":main()
