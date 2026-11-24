"""이상적인 평행 줄무늬와 최종 도안의 PDF 좌표를 검사한다."""
import json
from pathlib import Path
import numpy as np
import pdfplumber
from PIL import Image
from build import PT, W, H, X, Y, WW, WH, FW, FH, SHIFTS

ROOT=Path(__file__).resolve().parent
N=200
x=(np.arange(WW*N)+.5)/N


def envelope(pitch,shift):
    a=(x%2.0)<1.0
    b=((x-shift)%pitch)<pitch/2
    return (~(a|b)).astype(float)


def coefficient(y):
    return np.mean(np.exp(-2j*np.pi*x/42)*y)


fundamental=[coefficient(envelope(2.10,s)) for s in SHIFTS]
motion = [float(-42*np.angle(c/fundamental[0])/(2*np.pi)) for c in fundamental]
assert np.allclose(motion,[0,-10,-20],atol=.025)
assert max(abs(coefficient(envelope(2,s))) for s in SHIFTS)<.001
assert np.array_equal(envelope(2.10,0),envelope(2.10,2.10))


def near(v,w,tol=.001):
    return abs(v-w)<tol


with pdfplumber.open(ROOT/'Shade-Goes-the-Other-Way-Print.pdf') as pdf:
    assert len(pdf.pages)==2
    for i,p in enumerate(pdf.pages):
        assert near(p.width/PT,210) and near(p.height/PT,297)
        cut_size=((W,H),(FW,FH))[i]
        cuts=[r for r in p.rects if near(r['width']/PT,cut_size[0])
              and near(r['height']/PT,cut_size[1]) and r['stroking_color'] is not None]
        assert len(cuts)>=1
        assert any(near(r['x0']/PT,21) and near(r['top']/PT,57)
                   and r['x1']/PT<=190 for r in cuts)
        bars=[l for l in p.lines if near(l['x0']/PT,21) and near(l['x1']/PT,71)
              and near(l['top']/PT,258)]
        assert len(bars)==1
        pitch=(2,2.10)[i]
        stripes=sorted([r['x0']/PT for r in p.rects
                        if near(r['width']/PT,pitch/2) and near(r['height']/PT,WH)])
        assert len(stripes)>=61 and np.allclose(np.diff(stripes),pitch,atol=.001)
        assert near(stripes[0],21+X if i==0 else 21-4+X-2.10)
        assert all(8*PT<ch['x0']<ch['x1']<202*PT and 8*PT<ch['top']<ch['bottom']<289*PT for ch in p.chars)

im=Image.open(ROOT/'Shade-Goes-the-Other-Way.jpg')
im.load()
assert im.size==(980,1648) and not im.getexif()
# 정지한 벤치와 바닥은 겹치는 선이 달라져도 그대로다.
boxes=[np.array(im.crop((90,k+300,870,k+400)),dtype=float) for k in (244,718,1192)]
assert max(np.mean(abs(boxes[0]-b)) for b in boxes[1:])<1.3
print(json.dumps({'shifts_mm':SHIFTS,'measured_envelope_shift_mm':[round(m,3) for m in motion],
 'equal_pitch_has_envelope':False,'period_mm':42,'pdf_pages_a4':2,'scale_bars_mm':[50,50],
 'pitch_mm':[2.0,2.1],'physical_print_and_assembly_tested':False},ensure_ascii=False))
