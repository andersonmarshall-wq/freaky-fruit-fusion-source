#!/usr/bin/env python3
"""Small original synthesized game cues; no sampled voices or external effects."""
import math,wave,struct,subprocess,tempfile,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];RATE=44100

def write(name,duration,fn):
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'effect.wav'
        with wave.open(str(p),'wb') as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE)
            data=bytearray()
            for i in range(int(duration*RATE)):
                t=i/RATE;v=max(-.9,min(.9,fn(t,duration)))
                data+=struct.pack('<h',int(v*32767))
            w.writeframes(data)
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(p),'-c:a','libvorbis','-q:a','4',str(ROOT/'sound'/f'{name}.ogg')],check=True)

def bell(t,f,decay=6):
    return math.sin(2*math.pi*f*t)*math.exp(-decay*t)*(1-math.exp(-120*t))

def uwu(t,d):
    # A tiny three-syllable formant-like chirp, not a recording of a person.
    result=0
    for start,pitch,span in [(0,660,.23),(.23,510,.16),(.37,740,.30)]:
        x=t-start
        if 0<x<span:
            env=math.sin(math.pi*x/span)**1.5
            phase=2*math.pi*(pitch*x-90*x*x)
            result+=.24*env*(math.sin(phase)+.28*math.sin(2*phase)+.10*math.sin(4*phase))
    return result
write('uwu',.75,uwu)
write('gameover',1.6,lambda t,d:sum(.10*bell(t-start,f,4) for start,f in [(0,659),(.23,523),(.46,392)] if t>=start))
write('shake',.65,lambda t,d:sum(.12*bell(t-start,f,18) for start,f in [(0,280),(.07,340),(.14,420),(.22,520),(.31,680)] if t>=start))
lengths=[]
for n in ['blossom','regrowth']:
    d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(ROOT/'sound'/f'{n}.ogg')]))
    lengths.append(d)
(ROOT/'logic/module/music_tracks.lua').write_text('return {\n'+''.join(f'    {{name="{n}", duration={d:.4f}}},\n' for n,d in zip(['Blossom','Regrowth'],lengths))+'}\n')
print('Built quiet synthesized cues and measured music durations:',lengths)
