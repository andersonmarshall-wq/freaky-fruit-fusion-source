#!/usr/bin/env python3
"""Original nonsense phonemes, synthesized with Flite and pitched into tiny elves."""
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
lines=['mipi lulo','bimi nulu','tika lili','wibi nanala','piko lumimi','nini wulu','bubu ti la','limi pupu']
for i,line in enumerate(lines,1):
    voice='slt'
    pitch=1.55+(i%3)*.09
    filt=f'aresample=44100,asetrate={int(44100*pitch)},aresample=44100,atempo=0.92,highpass=f=180,lowpass=f=6800,loudnorm=I=-28:TP=-9:LRA=6,afade=t=in:d=0.015,afade=t=out:st=1.40:d=0.15'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f"flite=text='{line}':voice={voice}",'-af',filt,'-t','1.55','-c:a','libvorbis','-q:a','4',str(ROOT/'sound'/f'chatter_{i}.ogg')],check=True)
for i,line in enumerate(['eeee ah','ai yii','waaaa','eeeee'],1):
    filt=f'aresample=44100,asetrate={int(44100*(1.75+i*.045))},aresample=44100,atempo=0.78,lowpass=f=6200,loudnorm=I=-24:TP=-8:LRA=6,afade=t=in:d=0.015,afade=t=out:st=0.78:d=0.18'
    subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i',f"flite=text='{line}':voice=slt",'-af',filt,'-t','0.96','-c:a','libvorbis','-q:a','4',str(ROOT/'sound'/f'scream_{i}.ogg')],check=True)
print('Built 8 quiet elf-like gibberish voices and 4 short squeals.')
