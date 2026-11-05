#!/usr/bin/env python3
"""Direct SVG geometry → Inkscape frames → silent H.264. No raster editing."""
import concurrent.futures
import json
import math
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from build_keyframes import ROOT, SOURCE, NS, deform_path

FPS=15
SECONDS=12
N=FPS*SECONDS


def offset(t,amplitude,phase=0):
    return amplitude*math.sin(2*math.pi*t/SECONDS+phase)


def frame(t,path):
    tree=ET.parse(SOURCE)
    for group in tree.getroot().findall(f'{{{NS}}}g'):
        name=group.get('id','')
        if name.startswith('left-curtain') or name.startswith('right-curtain'):
            amount=offset(t,11) if name.startswith('left') else offset(t,7,-0.65)
            for p in group.findall(f'{{{NS}}}path'):
                p.set('d',deform_path(p.get('d'),amount))
    tree.write(path,encoding='utf-8',xml_declaration=True)
    return tree


def main():
    # Analytic periodicity: sine and its derivative match at t=0 and t=12.
    for amplitude,phase in [(11,0),(7,-0.65)]:
        assert abs(offset(0,amplitude,phase)-offset(SECONDS,amplitude,phase))<1e-12
        velocity=lambda t:amplitude*2*math.pi/SECONDS*math.cos(2*math.pi*t/SECONDS+phase)
        assert abs(velocity(0)-velocity(SECONDS))<1e-12
    baseline={g.get('id'):ET.tostring(g) for g in ET.parse(SOURCE).getroot().findall(f'{{{NS}}}g')}
    allowed={'left-curtain','left-curtain-shadow','right-curtain','right-curtain-shadow'}
    with tempfile.TemporaryDirectory(prefix='wind-svg-frames-') as tmp:
        folder=Path(tmp)
        def render(i):
            svg=folder/f'{i:04d}.svg'
            tree=frame(i/FPS,svg)
            for group in tree.getroot().findall(f'{{{NS}}}g'):
                if group.get('id') not in allowed:
                    assert ET.tostring(group)==baseline[group.get('id')]
            subprocess.run(['inkscape',str(svg),'--export-type=png',f'--export-filename={svg.with_suffix(".png")}','--export-width=960'],check=True,capture_output=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            for i,_ in enumerate(pool.map(render,range(N))):
                if (i+1)%30==0: print(f'{i+1}/{N} frames',flush=True)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate',str(FPS),'-i',str(folder/'%04d.png'),'-an','-c:v','libx264','-crf','18','-preset','slow','-pix_fmt','yuv420p','-movflags','+faststart',str(ROOT/'a_seat_for_wind_motion.mp4')],check=True)
    result=subprocess.run(['ffprobe','-v','error','-count_frames','-show_entries','stream=codec_name,codec_type,width,height,r_frame_rate,nb_read_frames,duration:format=duration,size','-of','json',str(ROOT/'a_seat_for_wind_motion.mp4')],check=True,capture_output=True,text=True)
    info=json.loads(result.stdout)
    assert len(info['streams'])==1
    s=info['streams'][0]
    assert s['codec_type']=='video' and s['nb_read_frames']==str(N)
    assert s['width']==960 and s['height']==720 and abs(float(s['duration'])-SECONDS)<0.001
    subprocess.run(['ffmpeg','-v','error','-i',str(ROOT/'a_seat_for_wind_motion.mp4'),'-f','null','-'],check=True)
    (ROOT/'verification.json').write_text(json.dumps({'geometry_checks':'All 180 frames preserve every non-curtain group byte-for-byte after XML parsing.','periodic_position_and_velocity':'Both analytic sine offsets and cosine derivatives match at 0 and 12 seconds within 1e-12.','decode':'All frames decoded without ffmpeg errors.','probe':info},ensure_ascii=False,indent=2)+'\n')
    print(result.stdout)

if __name__=='__main__': main()
