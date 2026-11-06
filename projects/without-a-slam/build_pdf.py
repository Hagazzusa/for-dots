"""짧은 희곡을 발화 단위가 쪽을 넘지 않도록 조판한다."""
from pathlib import Path
import argparse, tempfile, json
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from font_support import register_reading_font, FONT_NAME

def wrap(text, width, size):
    lines=[]; line=''
    for word in text.split(' '):
        candidate=(line+' '+word).strip()
        if line and pdfmetrics.stringWidth(candidate,FONT_NAME,size)>width:
            lines.append(line);line=word
        else:line=candidate
        assert pdfmetrics.stringWidth(line,FONT_NAME,size)<=width
    if line:lines.append(line)
    return lines

def main():
    p=Path(__file__).resolve().parent
    ap=argparse.ArgumentParser();ap.add_argument('--output-root',type=Path,default=p/'output');a=ap.parse_args()
    raw=(p/'play.txt').read_bytes();source=raw.decode();title,body=source.split('\n',1)
    out=a.output_root;(out/'pdf').mkdir(parents=True,exist_ok=True);(out/'text').mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        register_reading_font(Path('/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'),source+'0123456789',Path(td))
        c=Canvas(str(out/'pdf/Without-a-Slam.pdf'),pagesize=(520,740),invariant=1)
        c.setTitle(title);c.setAuthor('닷돌이');c.setSubject('두 사람을 위한 짧은 희곡')
        page=1;y=620
        c.setFont(FONT_NAME,25);c.drawString(56,666,title)
        def footer():
            c.setFont(FONT_NAME,9);c.drawRightString(464,33,str(page))
        for block in body.strip().split('\n\n'):
            lines=[]
            for line in block.splitlines():lines.extend(wrap(line,408,12))
            need=len(lines)*20+10
            assert need<590
            if y-need<64:
                footer();c.showPage();page+=1;y=660
            c.setFont(FONT_NAME,12)
            for line in lines:c.drawString(56,y,line);y-=20
            y-=10
        footer();c.save()
    (out/'text/Without-a-Slam.txt').write_bytes(raw)
    print(json.dumps({'쪽 수':page},ensure_ascii=False))
if __name__=='__main__':main()
