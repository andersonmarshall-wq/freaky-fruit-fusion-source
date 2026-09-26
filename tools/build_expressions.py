#!/usr/bin/env python3
"""Native SVG adaptations of the purchased fruit, plus vector UI/effect assets."""
from pathlib import Path
import math,re,subprocess,tempfile,xml.etree.ElementTree as E
from build_kawaii_assets import ROOT,SOURCE,SVG,TIERS,export
LABEL='{http://www.inkscape.org/namespaces/inkscape}label'
T=lambda x:f'{{{SVG}}}{x}'

def expressions():
    destination=SOURCE/'expressions';destination.mkdir(exist_ok=True)
    entries=[(n,z,f'ball_{i}') for i,(n,z) in enumerate(TIERS,1)]+[('GoldenWatermelon',330,'ball_11f')]
    with tempfile.TemporaryDirectory() as tmp:
        for name,size,stem in entries:
            source=SOURCE/(name+'.svg')
            rows=subprocess.check_output(['inkscape','--query-all',str(source)],text=True)
            row=next(line for line in rows.splitlines() if line.startswith('circle1,'))
            x,y,w,h=map(float,row.split(',')[1:]);root=E.parse(source).getroot()
            vx,vy,vw,vh=map(float,root.get('viewBox').split());pw=float(root.get('width'));ph=float(root.get('height'))
            cx=vx+(x+w/2)*vw/pw;cy=vy+(y+h/2)*vh/ph;unit=min(w*vw/pw,h*vh/ph)/60
            for direction,(dx,dy) in {'left':(-1,0),'right':(1,0),'up':(0,-1),'down':(0,1)}.items():
                root=E.parse(source).getroot()
                for parent in list(root.iter()):
                    for el in list(parent):
                        if re.search(r'eye|mouth|blush',el.get(LABEL,''),re.I): parent.remove(el)
                face=E.SubElement(root,T('g'),{'id':'smooch-face','transform':f'translate({cx+dx*unit*2},{cy+dy*unit*2}) scale({unit})'})
                for ex in [-6,6]:
                    E.SubElement(face,T('ellipse'),{'cx':str(ex),'cy':'1','rx':'2.65','ry':'3.35','fill':'#fff8ec'})
                    E.SubElement(face,T('ellipse'),{'cx':str(ex+dx*1.05),'cy':str(1+dy*1.15),'rx':'1.7','ry':'2.15','fill':'#674634'})
                    E.SubElement(face,T('circle'),{'cx':str(ex+dx*1.05-.45),'cy':str(.3+dy*1.15),'r':'.52','fill':'#ffffff'})
                for ex in [-11,11]:E.SubElement(face,T('ellipse'),{'cx':str(ex),'cy':'6','rx':'3.25','ry':'1.7','fill':'#f7a6c6','opacity':'.88'})
                lips=E.SubElement(face,T('g'),{'transform':f'translate({dx*3},7)','fill':'none','stroke':'#9d5163','stroke-width':'1.15','stroke-linecap':'round'})
                E.SubElement(lips,T('path'),{'d':'M -1.7,-1.8 C 2.5,-3.5 3.8,-.5 .2,0 C 3.8,.5 2.5,3.5 -1.7,1.8'})
                out=destination/f'{stem}_kiss_{direction}.svg';root.set('id',out.stem)
                E.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True)
                export(out,ROOT/'images'/f'{out.stem}.png',size,Path(tmp))

def vectors():
    out=ROOT/'art'/'effects';out.mkdir(parents=True,exist_ok=True)
    shapes={
    'golden_glow': '<defs><radialGradient id="glow"><stop offset="0" stop-color="#ffd65a" stop-opacity=".48"/><stop offset=".59" stop-color="#ffd65a" stop-opacity=".35"/><stop offset="1" stop-color="#ffd65a" stop-opacity="0"/></radialGradient></defs><circle cx="240" cy="240" r="239" fill="url(#glow)"/><g fill="#fff6bb"><path d="M86 120l5 16 16 5-16 5-5 16-5-16-16-5 16-5Z"/><path d="M366 328l4 12 12 4-12 4-4 12-4-12-12-4 12-4Z"/><path d="M375 128l3 9 9 3-9 3-3 9-3-9-9-3 9-3Z"/></g>',
    'heart': '<path d="M32 55C-15 27 8-3 32 17 56-3 79 27 32 55Z" fill="#f488a7" stroke="#fff4d9" stroke-width="3"/>',
    'sparkle': '<path d="M32 3l8 21 21 8-21 8-8 21-8-21L3 32l21-8Z" fill="#ffdd77" stroke="#fff7df" stroke-width="3"/>',
    'pill': '<rect x="1" y="1" width="238" height="70" rx="24" fill="#fff7e9" stroke="#c58a74" stroke-width="2"/>',
    }
    for name,body in shapes.items():
        w,h=(480,480) if name=='golden_glow' else (240,72) if name=='pill' else (64,64)
        path=out/f'{name}.svg';path.write_text(f'<svg xmlns="{SVG}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>')
        subprocess.run(['inkscape',str(path),'--export-area-page','--export-background-opacity=0',f'--export-filename={ROOT/"images"/(name+".png")}'],capture_output=True,check=True)
    atlas=ROOT/'main/main.atlas';text=atlas.read_text()
    for path in sorted((ROOT/'images').glob('*_kiss_*.png'))+[(ROOT/'images')/(n+'.png') for n in shapes]:
        asset='/images/'+path.name
        if asset not in text:text+='\nimages {\n  image: "'+asset+'"\n}\n'
    atlas.write_text(text)
if __name__=='__main__':
    expressions();vectors();print('48 directional expressions and 4 native vector effects exported.')
