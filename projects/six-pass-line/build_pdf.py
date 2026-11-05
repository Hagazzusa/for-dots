#!/usr/bin/env python3
"""Build the one-page pencil score from score.json without changing the source.

Requires reportlab and fonttools. Noto Serif CJK KR is embedded as a converted
TrueType subset. Font conversion is self-contained, adapted from the original
project opposite-steps. The generated PDF is byte-reproducible.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
from pathlib import Path
import tempfile
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as SourceFont
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parent
FONT_NAME = "SixPassesNotoSerifKR"
DEFAULT_FONT = Path("/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc")
EXTRA_TEXT = "준비와 연주 시간표 한 칸 한 박 이동 머묾 구절 연주 자리 시작 왼쪽 반대 끝 오른쪽 검은 막대는 이동 시간 빈 원은 끝점에 연필을 댄 채 머묾 손의 실제 경로가 아닙니다. 여섯 번 이동 세 번 왕복 약 48초 60 bpm 6cm → ← 0123456789 · / % ="


def register_font(font_path: Path, characters: str, work_dir: Path) -> None:
    """Convert the KR face's used CFF glyphs to embeddable TrueType curves."""
    source = SourceFont(font_path, fontNumber=1, lazy=True)
    try:
        cmap = source.getBestCmap()
        missing = sorted({c for c in characters if not c.isspace() and ord(c) not in cmap})
        if missing:
            raise ValueError(f"Missing font characters: {''.join(missing)!r}")
        options = subset.Options()
        options.recalc_timestamp = False
        subsetter = subset.Subsetter(options=options)
        subsetter.populate(text=characters)
        subsetter.subset(source)
        order, glyph_set = source.getGlyphOrder(), source.getGlyphSet()
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
            "familyName": FONT_NAME, "styleName": "Regular",
            "uniqueFontIdentifier": FONT_NAME, "fullName": FONT_NAME,
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


class Sheet:
    def __init__(self, buffer, score, layout):
        self.score, self.layout = score, layout
        self.w, self.h = [v * mm for v in layout["page_mm"]]
        self.c = Canvas(buffer, pagesize=(self.w, self.h), invariant=1, pageCompression=1)
        self.c.setTitle(score["title"])
        self.c.setAuthor("닷돌이")
        self.c.setSubject(score["subtitle"])
        self.c.setCreator("Six Passes One Line deterministic score builder")
        self.records = []

    def text(self, value, x, y, size=10.2, align="left", gray=0, role="text"):
        self.c.setFillGray(gray)
        self.c.setFont(FONT_NAME, size)
        width = pdfmetrics.stringWidth(value, FONT_NAME, size)
        left = x*mm - (width/2 if align == "center" else width if align == "right" else 0)
        self.c.drawString(left, self.h-y*mm, value)
        self.records.append({"kind": "text", "role": role, "text": value, "font_size_pt": size,
            "bbox_pt": [left, y*mm-pdfmetrics.getAscent(FONT_NAME,size),
                        left+width, y*mm-pdfmetrics.getDescent(FONT_NAME,size)]})

    def paragraph(self, value, x, y, width, size, leading, role="text"):
        """Word-wrap with a character fallback, preserving source punctuation."""
        words = value.split(" ")
        lines, line = [], ""
        for word in words:
            trial = f"{line} {word}" if line else word
            if pdfmetrics.stringWidth(trial,FONT_NAME,size) <= width*mm:
                line = trial
            else:
                if line: lines.append(line)
                line = word
                while pdfmetrics.stringWidth(line,FONT_NAME,size) > width*mm:
                    i = 1
                    while i < len(line) and pdfmetrics.stringWidth(line[:i+1],FONT_NAME,size) <= width*mm:
                        i += 1
                    lines.append(line[:i]); line = line[i:]
        if line: lines.append(line)
        for value in lines:
            self.text(value,x,y,size,role=role)
            y += leading
        return y

    def line(self,x1,y1,x2,y2,gray=.75,width=.35):
        self.c.setStrokeGray(gray); self.c.setLineWidth(width)
        self.c.line(x1*mm,self.h-y1*mm,x2*mm,self.h-y2*mm)

    def rect(self,x,y,w,h,role="bar", **info):
        self.c.setFillGray(0)
        self.c.rect(x*mm,self.h-(y+h)*mm,w*mm,h*mm,stroke=0,fill=1)
        self.records.append({"kind":role,"bbox_mm":[x,y,x+w,y+h],**info})

    def circle(self,x,y,r,filled=False,gray=0,role="hold",**info):
        self.c.setStrokeGray(gray); self.c.setFillGray(gray)
        self.c.setLineWidth(.65)
        self.c.circle(x*mm,self.h-y*mm,r*mm,stroke=not filled,fill=filled)
        self.records.append({"kind":role,"center_mm":[x,y],"radius_mm":r,"filled":filled,**info})


def make_score(score, layout):
    b = io.BytesIO(); s = Sheet(b,score,layout); l=layout; m=l["margin_mm"]
    total = sum(p["move_beats"]+p["hold_beats"] for p in score["phrases"])
    s.text(score["title"],m,l["title_baseline_mm"],25,role="title")
    s.text(score["subtitle"],m,l["subtitle_baseline_mm"],10.5,role="subtitle")
    s.text(f"여섯 번 이동 · 세 번 왕복 · {total}박 · 약 {total*score['approx_seconds_per_beat']:.0f}초",m,l["summary_baseline_mm"],9,role="summary")
    s.text("준비와 연주",m,l["instructions_heading_mm"],11.8,role="heading")
    y=l["instructions_baseline_mm"]
    for i, instruction in enumerate(score["instructions"],1):
        s.text(str(i),m,y,l["body_size_pt"],role="instruction_number")
        y=s.paragraph(instruction,m+6,y,210-m*2-6,l["body_size_pt"],l["body_leading_mm"],role="instruction")
        y+=l["instruction_gap_mm"]
    if y > l["score_heading_mm"]-5:
        raise ValueError(f"Instructions overflow: next baseline {y}mm")
    s.text("시간표",m,l["score_heading_mm"],11.8,role="heading")
    s.text("한 칸 = 한 박 · 약 60 bpm",192,l["score_heading_mm"],9,align="right",role="tempo")
    ly=l["legend_baseline_mm"]
    s.rect(m,ly-2.3,8,1.5,role="legend_bar")
    s.text("이동 시간",m+11,ly,9,role="legend")
    s.circle(70,ly-1.05,l["hold_radius_mm"],role="legend_hold")
    s.text("끝점에 연필을 댄 채 머묾",74,ly,9,role="legend")
    s.text("검은 막대는 시간입니다. 손의 실제 경로가 아닙니다.",m,l["time_note_baseline_mm"],9,role="time_note")
    gx,gy,cw,ch=[l[k] for k in ("grid_x_mm","grid_y_mm","cell_width_mm","cell_height_mm")]
    beats=score["beats_per_phrase"]
    s.text("구절과 방향",m,l["beat_labels_baseline_mm"],8.5,role="column_label")
    for beat in range(beats):
        s.text(str(beat+1),gx+(beat+.5)*cw,l["beat_labels_baseline_mm"],9,align="center",role="beat_label")
    for k in range(beats+1): s.line(gx+k*cw,gy,gx+k*cw,gy+len(score["phrases"])*ch)
    for r in range(len(score["phrases"])+1): s.line(gx,gy+r*ch,gx+beats*cw,gy+r*ch)
    for row,p in enumerate(score["phrases"]):
        cy=gy+(row+.5)*ch
        arrow="→" if p["direction"]=="오른쪽" else "←"
        s.text(f"{p['number']}  {arrow}",m,cy+1.3,10.8,role="phrase_direction")
        s.text(f"이동 {p['move_beats']} · 머묾 {p['hold_beats']}",34,cy+1.1,9,role="phrase_summary")
        s.rect(gx,cy-l["bar_height_mm"]/2,p["move_beats"]*cw,l["bar_height_mm"],phrase=p["number"],beats=p["move_beats"])
        for beat in range(p["move_beats"],beats):
            s.circle(gx+(beat+.5)*cw,cy,l["hold_radius_mm"],phrase=p["number"],beat=beat+1)
    s.text("연주 자리",m,l["play_heading_mm"],11.8,role="heading")
    s.text("6cm",192,l["play_heading_mm"],9,align="right",role="distance_label")
    cy=l["play_center_y_mm"]
    for x, label in ((105-score["line_length_mm"]/2,"시작 · 왼쪽"),(105+score["line_length_mm"]/2,"반대 끝 · 오른쪽")):
        s.circle(x,cy,.5,filled=True,gray=.62,role="play_dot")
        s.text(label,x,l["play_label_baseline_mm"],8,align="center",gray=.3,role="play_label")
    s.text(score["closing"],m,l["closing_baseline_mm"],10,role="closing")
    s.paragraph(score["print_note"],m,l["print_note_baseline_mm"],174,l["print_note_size_pt"],4.2,role="print_note")
    s.c.save()
    return b.getvalue(),s.records


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-root",type=Path,default=ROOT/"output")
    ap.add_argument("--font",type=Path,default=DEFAULT_FONT)
    args=ap.parse_args()
    score_path=ROOT/"score.json"
    score=json.loads(score_path.read_text()); layout=json.loads((ROOT/"layout.json").read_text())
    assert len(score["phrases"])==6 and score["beats_per_phrase"]==8
    assert [p["move_beats"] for p in score["phrases"]]==[6,4,2,2,4,6]
    assert all(p["move_beats"]+p["hold_beats"]==8 for p in score["phrases"])
    with tempfile.TemporaryDirectory(prefix="six-passes-font-") as tmp:
        register_font(args.font,json.dumps(score,ensure_ascii=False)+EXTRA_TEXT,Path(tmp))
        data,records=make_score(score,layout)
    out=args.output_root/"pdf"; out.mkdir(parents=True,exist_ok=True)
    pdf=out/"Six-Passes-One-Line.pdf"; pdf.write_bytes(data)
    qa={"pdf":"pdf/"+pdf.name,"page_count":1,"source_sha256":hashlib.sha256(score_path.read_bytes()).hexdigest(),
        "pdf_sha256":hashlib.sha256(data).hexdigest(),"font":"Noto Serif CJK KR Regular embedded subset", "records":records}
    (args.output_root/"layout_manifest.json").write_text(json.dumps(qa,ensure_ascii=False,indent=2)+"\n")
    print(pdf)

if __name__=="__main__": main()
