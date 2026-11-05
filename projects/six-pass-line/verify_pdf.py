#!/usr/bin/env python3
"""Verify source text, page bounds, embedded font, actual score vectors and rebuild.

python verify_pdf.py
python verify_pdf.py --compare-root /tmp/six-passes-rebuild/output
python verify_pdf.py --report qa_layout.json

By default this checker is read-only and prints the JSON report to stdout.
Only an explicit --report writes a file. A prior visual review is retained only
when its exact PDF and optional local render can both be verified.
Visual inspection of every rendered page is a separate shipping gate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import pdfplumber
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parent
MM=72/25.4


def normalized(value): return re.sub(r"\s+","",value)
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def scalar(value): return value[0] if isinstance(value,(list,tuple)) and len(value)==1 else value

def inside(obj, box, tolerance=.03):
    return (obj["x0"]>=box[0]-tolerance and obj["x1"]<=box[2]+tolerance and
            obj["top"]>=box[1]-tolerance and obj["bottom"]<=box[3]+tolerance)

def near(a,b): assert abs(a-b)<.03,(a,b)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-root",type=Path,default=ROOT/"output")
    ap.add_argument("--compare-root",type=Path)
    ap.add_argument("--report",type=Path,help="Write the report to this path; omitted means stdout only")
    args=ap.parse_args()
    path=args.output_root/"pdf"/"Six-Passes-One-Line.pdf"
    score=json.loads((ROOT/"score.json").read_text())
    l=json.loads((ROOT/"layout.json").read_text())
    manifest=json.loads((args.output_root/"layout_manifest.json").read_text())
    assert manifest["source_sha256"]==sha(ROOT/"score.json")
    assert manifest["pdf_sha256"]==sha(path)
    assert len(score["phrases"])==6 and score["beats_per_phrase"]==8
    assert [p["move_beats"] for p in score["phrases"]]==[6,4,2,2,4,6]
    assert [p["hold_beats"] for p in score["phrases"]]==[2,4,6,6,4,2]
    assert [p["direction"] for p in score["phrases"]]==["오른쪽","왼쪽"]*3
    assert all(p["move_beats"]+p["hold_beats"]==8 for p in score["phrases"])
    assert sum(p["move_beats"]+p["hold_beats"] for p in score["phrases"])==48
    reader=PdfReader(path); assert len(reader.pages)==1
    embedded=[]
    for ref in reader.pages[0]["/Resources"]["/Font"].values():
        font=ref.get_object()
        if "SixPassesNotoSerifKR" in str(font.get("/BaseFont")):
            assert "/FontFile2" in font["/FontDescriptor"] and "/ToUnicode" in font
            embedded.append(str(font["/BaseFont"]))
    assert embedded
    with pdfplumber.open(path) as pdf:
        page=pdf.pages[0]
        near(page.width,210*MM); near(page.height,297*MM)
        text=page.extract_text(); compact=normalized(text)
        assert "\ufffd" not in text and "\x00" not in text
        assert "6회왕복" not in compact
        for key in ("title","subtitle","closing","print_note"):
            assert normalized(score[key]) in compact,(key,score[key])
        for instruction in score["instructions"]:
            assert normalized(instruction) in compact,instruction
        records=manifest["records"]
        for record in records:
            if record["kind"]=="text":
                assert normalized(record["text"]) in compact,record["text"]
        assert set(ch["fontname"].split("+")[-1] for ch in page.chars)=={"SixPassesNotoSerifKR"}
        assert not page.images
        for obj in page.chars+page.rects+page.curves+page.lines:
            assert inside(obj,[8*MM,8*MM,page.width-8*MM,page.height-8*MM]),obj
        texts=[r for r in records if r["kind"]=="text"]
        for i,a in enumerate(texts):
            for b in texts[i+1:]:
                ax,ay,ar,ab=a["bbox_pt"]; bx,by,br,bb=b["bbox_pt"]
                assert min(ar,br)-max(ax,bx)<=.1 or min(ab,bb)-max(ay,by)<=.1,(a,b)
        gx,gy,cw,ch=[l[k]*MM for k in ("grid_x_mm","grid_y_mm","cell_width_mm","cell_height_mm")]
        box=[gx,gy,gx+8*cw,gy+6*ch]
        gridlines=[v for v in page.lines if inside(v,box)]
        assert len(gridlines)==16,len(gridlines)
        vertical=sorted([v for v in gridlines if abs(v["x1"]-v["x0"])<.01],key=lambda v:v["x0"])
        horizontal=sorted([v for v in gridlines if abs(v["bottom"]-v["top"])<.01],key=lambda v:v["top"])
        assert len(vertical)==9 and len(horizontal)==7
        for i,v in enumerate(vertical):
            near(v["x0"],gx+i*cw); near(v["top"],gy); near(v["bottom"],gy+6*ch)
        for i,v in enumerate(horizontal):
            near(v["top"],gy+i*ch); near(v["x0"],gx); near(v["x1"],gx+8*cw)
        bars=sorted([v for v in page.rects if inside(v,box) and v["fill"]],key=lambda v:v["top"])
        holds=[v for v in page.curves if inside(v,box)]
        assert len(bars)==6 and len(holds)==24
        checked=[]
        for row,(bar,p) in enumerate(zip(bars,score["phrases"])):
            cy=gy+(row+.5)*ch
            near(bar["x0"],gx); near(bar["x1"],gx+p["move_beats"]*cw)
            near((bar["top"]+bar["bottom"])/2,cy)
            near(bar["height"],l["bar_height_mm"]*MM)
            assert scalar(bar["non_stroking_color"])==0 and not bar["stroke"]
            row_holds=sorted([h for h in holds if abs((h["top"]+h["bottom"])/2-cy)<.03],key=lambda v:v["x0"])
            assert len(row_holds)==p["hold_beats"]
            for beat,hold in enumerate(row_holds,p["move_beats"]):
                near((hold["x0"]+hold["x1"])/2,gx+(beat+.5)*cw)
                near(hold["width"],2*l["hold_radius_mm"]*MM)
                near(hold["height"],2*l["hold_radius_mm"]*MM)
                assert not hold["fill"] and hold["stroke"]
                assert scalar(hold["stroking_color"])==0
            checked.append({"phrase":p["number"],"direction":p["direction"],"bar_width_mm":round(bar["width"]/MM,5),
                            "move_beats":p["move_beats"],"hold_circles":len(row_holds),"total_beats":8})
        dots=sorted([v for v in page.curves if v["top"]>l["play_heading_mm"]*MM],key=lambda v:v["x0"])
        assert len(dots)==2
        centers=[((v["x0"]+v["x1"])/2,(v["top"]+v["bottom"])/2) for v in dots]
        near(centers[1][0]-centers[0][0],60*MM); near(centers[0][1],centers[1][1])
        near(centers[0][1],l["play_center_y_mm"]*MM)
        for dot in dots:
            assert dot["fill"] and not dot["stroke"] and scalar(dot["non_stroking_color"])==.62
            near(dot["width"],MM); near(dot["height"],MM)
        # The playing field contains only the two dots, with no pre-drawn line.
        playing_box=[65*MM,239*MM,145*MM,261*MM]
        assert not [v for v in page.lines+page.rects if inside(v,playing_box)]
        assert len([v for v in page.curves if inside(v,playing_box)])==2
        assert not [v for v in page.chars if inside(v,playing_box)]
        # All graphic ink is grayscale, including unobtrusive playing points.
        for obj in page.chars+page.rects+page.curves+page.lines:
            for key in ("stroking_color","non_stroking_color"):
                value=obj.get(key)
                if value is not None: assert isinstance(scalar(value),(float,int)),value
    same=None
    if args.compare_root:
        same=path.read_bytes()==(args.compare_root/"pdf"/path.name).read_bytes()
        assert same
        assert (args.output_root/"layout_manifest.json").read_bytes()==(args.compare_root/"layout_manifest.json").read_bytes()
    report={"status":"passed","pdf":"output/pdf/"+path.name,"sha256":sha(path),"source_sha256":sha(ROOT/"score.json"),
      "pages":1,"page_size_mm":[210,297],"font_embedded":embedded,"text_characters":len(text),
      "all_source_text_preserved":True,"all_authored_text_recoverable":True,"bounds_and_text_overlap_passed":True,
      "actual_vector_grid":{"rows":6,"beats_per_row":8,"total_beats":48,"move_beats":24,"hold_beats":24,"phrases":checked},
      "play_points":{"count":2,"distance_mm":round((centers[1][0]-centers[0][0])/MM,5),"pre_drawn_line":False},
      "separate_rebuild_byte_identical":same,"performance_or_audio_claimed":False}
    if args.report and args.report.exists():
        previous=json.loads(args.report.read_text()).get("visual_review")
        if previous:
            render=ROOT/previous["render"]
            if (previous["pdf_sha256"]==sha(path) and render.is_file()
                    and sha(render)==previous["render_sha256"]):
                report["visual_review"]=previous
    serialized=json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    if args.report:
        args.report.write_text(serialized)
    else:
        print(serialized,end="")
    print("PASS: A4 one page; original text; embedded Korean font; bounds; 6 rows / 48 beats; actual bars and circles; 60mm unlined playing field"+("; byte-identical rebuild" if same else ""),file=sys.stderr)

if __name__=="__main__": main()
