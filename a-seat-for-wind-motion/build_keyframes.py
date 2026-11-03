#!/usr/bin/env python3
"""Original SVG stays immutable. Make three restrained, rod-anchored breeze studies."""
import math
import re
import subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / 'a-seat-for-wind' / 'a_seat_for_wind.svg'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
COUNTS = {'M':2, 'L':2, 'H':1, 'V':1, 'C':6, 'Q':4, 'Z':0}


def deform_path(d, amount, top=212, bottom=740):
    tokens = re.findall(r'[MLHVCQZ]|[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?', d)
    out=[]
    index=0
    x=y=0
    def p(x,y):
        # The height weight has zero value/derivative at the rod.
        # Control-point deformation fixes endpoints, not the curve tangent.
        s=max(0.0,min(1.0,(y-top)/(bottom-top)))
        w=s*s*(3-2*s)
        return x+amount*w,y
    while index<len(tokens):
        cmd=tokens[index]; index+=1
        n=COUNTS[cmd]
        values=list(map(float,tokens[index:index+n])); index+=n
        if cmd=='Z': out.append('Z'); continue
        if cmd=='H': x=values[0]; values=[x,y]; cmd='L'
        elif cmd=='V': y=values[0]; values=[x,y]; cmd='L'
        else: x,y=values[-2:]
        pairs=[p(*values[i:i+2]) for i in range(0,len(values),2)]
        out.append(cmd+' '.join(f'{v:.4f}' for pair in pairs for v in pair))
    return ' '.join(out)


def main():
    for number,t in enumerate((0,4,8),1):
        tree=ET.parse(SOURCE)
        left=11*math.sin(2*math.pi*t/12)
        right=7*math.sin(2*math.pi*t/12-0.65)
        for group in tree.getroot().findall(f'{{{NS}}}g'):
            group_id=group.get('id','')
            if group_id.startswith('left-curtain') or group_id.startswith('right-curtain'):
                amount=left if group_id.startswith('left') else right
                for path in group.findall(f'{{{NS}}}path'):
                    path.set('d',deform_path(path.get('d'),amount))
        output=ROOT/f'keyframe_{number:02d}.svg'
        tree.write(output,encoding='utf-8',xml_declaration=True)
        subprocess.run(['inkscape',str(output),'--export-type=png',f'--export-filename={output.with_suffix(".png")}','--export-width=1600'],check=True,capture_output=True)
        print(f'{output.name}: t={t}s, left={left:.3f}px, right={right:.3f}px')

if __name__=='__main__': main()
