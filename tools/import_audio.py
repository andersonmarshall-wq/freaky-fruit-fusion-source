#!/usr/bin/env python3
"""Rebuild the purchased-pack OGGs from the owner's extracted source packs.
python tools/import_audio.py --sfx /path/to/sfx --music /path/to/music
The public source includes the CC BY music; obtain the six pack effects locally (see ASSETS.md).
"""
import argparse, subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--sfx',type=Path);p.add_argument('--music',type=Path);a=p.parse_args()
def source(folder,name):
    matches=list(folder.rglob(name));assert len(matches)==1,(name,len(matches));return matches[0]
def convert(src,name,filters,limit=None):
    cmd=['ffmpeg','-v','error','-y','-i',str(src),'-af',filters]
    if limit:cmd+=['-t',str(limit)]
    subprocess.run(cmd+['-ar','44100','-c:a','libvorbis','-q:a','4',str(root/'sound'/f'{name}.ogg')],check=True)
if a.sfx:
    for name,file in {'pop':'01_Soft_Bubble_Pop_v2.wav','pap':'04_Jelly_Blob_Tap_v1.wav','chain':'14_Star_Twinkle_v1.wav','golden':'11_Magical_Sparkle_v2.wav','gusher':'08_Water_Droplet_Pop_v3.wav','squelch':'10_Marshmallow_Squish_v2.wav'}.items():
        convert(source(a.sfx,file),name,'silenceremove=start_periods=1:start_threshold=-55dB,loudnorm=I=-25:TP=-8:LRA=7',2)
if a.music:
    for name,file in [('blossom','blossom.wav'),('regrowth','regrowth wip.wav')]:
        convert(source(a.music,file),name,'atempo=0.88,lowpass=f=6400,loudnorm=I=-24:TP=-6:LRA=9')
    subprocess.run(['python3',str(root/'tools/build_sounds.py')],check=True)
