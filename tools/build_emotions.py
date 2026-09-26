#!/usr/bin/env python3
"""Add talking, pressure and shake expressions by editing the native face SVGs."""
from pathlib import Path
import tempfile,xml.etree.ElementTree as E
from build_kawaii_assets import ROOT,SOURCE,SVG,TIERS,export
T=lambda x:f'{{{SVG}}}{x}'
path=SOURCE/'expressions'
entries=[(n,z,f'ball_{i}') for i,(n,z) in enumerate(TIERS,1)]+[('GoldenWatermelon',330,'ball_11f')]
with tempfile.TemporaryDirectory() as tmp:
 for _,size,stem in entries:
  for expression in ['talk','stress','stress_heavy','panic']:
   root=E.parse(path/f'{stem}_kiss_right.svg').getroot()
   face=root.find(".//*[@id='smooch-face']");transform=face.get('transform')
   for el in list(face):face.remove(el)
   face.set('transform',transform)
   def el(tag,**attrs):return E.SubElement(face,T(tag),{k.replace('_','-'):str(v) for k,v in attrs.items()})
   if expression=='stress_heavy':
    for x,sgn in [(-6,1),(6,-1)]:
     el('path',d=f'M {x-2.5*sgn},-2 L {x+2*sgn},1 L {x-2.5*sgn},3.5',fill='none',stroke='#674634',stroke_width=1.4,stroke_linecap='round',stroke_linejoin='round')
   else:
    for x in [-6,6]:
     el('ellipse',cx=x,cy=1,rx=2.65,ry=3.6 if expression=='panic' else 3.0,fill='#fff8ec')
     el('ellipse',cx=x,cy=1,rx=1.15 if expression=='panic' else 1.7,ry=2.15,fill='#674634')
     el('circle',cx=x-.5,cy=.2,r=.5,fill='#ffffff')
   if expression in ['stress','stress_heavy']:
    el('path',d='M -9,-5 Q -6,-3 -3,-5 M 3,-5 Q 6,-3 9,-5',stroke='#674634',stroke_width=1.2,fill='none',stroke_linecap='round')
    el('rect',x=-4.5,y=6,width=9,height=4,rx=1.5,fill='#fff8ec',stroke='#965664',stroke_width=1.1)
    el('path',d='M -2,6.2 V 9.5 M 1,6.2 V 9.5',stroke='#c08f8d',stroke_width=.5,fill='none')
    el('path',d='M 14,-7 Q 10,-1 14,1 Q 18,-1 14,-7Z',fill='#b6e4ef',stroke='#629eae',stroke_width=.5)
    if expression=='stress_heavy':el('path',d='M -15,-4 Q -18,1 -15,3 Q -12,1 -15,-4Z',fill='#b6e4ef')
   elif expression=='panic':
    el('ellipse',cx=0,cy=8,rx=4,ry=5.5,fill='#884956',stroke='#674634',stroke_width=1)
    el('ellipse',cx=0,cy=10.7,rx=2.8,ry=1.8,fill='#f596b6')
    el('path',d='M -9,-5 Q -6,-8 -3,-5 M 3,-5 Q 6,-8 9,-5',stroke='#674634',stroke_width=1.2,fill='none')
   else:
    el('path',d='M -4,6 Q 0,7 4,6 Q 4,13 0,13 Q -4,13 -4,6Z',fill='#9e5365',stroke='#674634',stroke_width=.8)
    el('ellipse',cx=0,cy=11,rx=2.7,ry=1.4,fill='#f596b6')
   for x in [-11,11]:el('ellipse',cx=x,cy=6,rx=2.4,ry=1.3,fill='#f4a1b7',opacity=.8)
   target=path/f'{stem}_{expression}.svg';root.set('id',target.stem)
   E.ElementTree(root).write(target,encoding='utf-8',xml_declaration=True)
   export(target,ROOT/'images'/f'{target.stem}.png',size,Path(tmp))
# Juice droplets use a native SVG so the gusher is visibly liquid, not confetti.
svg=ROOT/'art/effects/droplet.svg'
svg.write_text(f'<svg xmlns="{SVG}" width="64" height="64" viewBox="0 0 64 64"><path d="M32 3C25 19 8 31 8 43a24 19 0 0048 0C56 31 39 19 32 3Z" fill="#ffffff"/><path d="M22 38q-7 7-3 12" fill="none" stroke="#fff9dc" stroke-width="4" stroke-linecap="round" opacity=".7"/></svg>')
import subprocess
subprocess.run(['inkscape',str(svg),'--export-area-page','--export-background-opacity=0',f'--export-filename={ROOT/"images/droplet.png"}'],capture_output=True,check=True)
atlas=ROOT/'main/main.atlas';s=atlas.read_text()
for p in sorted((ROOT/'images').glob('ball_*.png'))+[ROOT/'images/droplet.png']:
 if p.stem.endswith(('talk','stress','stress_heavy','panic')) or p.stem=='droplet':
  asset='/images/'+p.name
  if asset not in s:s+='\nimages {\n  image: "'+asset+'"\n}\n'
atlas.write_text(s)
print('48 talking/stressed/startled faces and juice droplets exported.')
