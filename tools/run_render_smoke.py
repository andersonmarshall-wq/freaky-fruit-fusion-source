#!/usr/bin/env python3
"""Render the real game and click it at a tall phone's physical resolution.
Requires Xvfb, ImageMagick import, libX11, and the graphics dmengine (not headless).
The isolated save and fixture never modify the game or the player's save.
"""
import argparse,ctypes as C,json,os,shutil,subprocess,tempfile,time,uuid
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('--bob',required=True);p.add_argument('--java',required=True)
p.add_argument('--engine',required=True);p.add_argument('--xvfb',default='Xvfb')
p.add_argument('--output',required=True)
p.add_argument('--recovery-test',action='store_true',help='Exercise a real saved crash dump and the recovery buttons before play')
a=p.parse_args();root=Path(__file__).resolve().parents[1]
output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=True)
java,bob,engine=(str(Path(v).resolve()) for v in [a.java,a.bob,a.engine])

class Button(C.Structure):
    _fields_=[('type',C.c_int),('serial',C.c_ulong),('send_event',C.c_int),
        ('display',C.c_void_p),('window',C.c_ulong),('root',C.c_ulong),
        ('subwindow',C.c_ulong),('time',C.c_ulong),('x',C.c_int),('y',C.c_int),
        ('x_root',C.c_int),('y_root',C.c_int),('state',C.c_uint),
        ('button',C.c_uint),('same_screen',C.c_int)]
class Event(C.Union): _fields_=[('button',Button),('pad',C.c_long*24)]

with tempfile.TemporaryDirectory(prefix='fruit-render-test-') as tmp:
    dest=Path(tmp)/'game'
    shutil.copytree(root,dest,ignore=shutil.ignore_patterns('.git','build','__pycache__','*.zip'))
    if (root/'.internal/lib').exists():
        shutil.copytree(root/'.internal/lib',dest/'.internal/lib',dirs_exist_ok=True)
    project=dest/'game.project'
    project.write_text(project.read_text().replace('app_manifest = /main/android-compat.appmanifest',''))
    test_save='freaky_render_'+uuid.uuid4().hex
    save=dest/'logic/module/saver.lua'
    save.write_text(save.read_text().replace('"freaky_fruit_fusion", "savefile"',
        '"'+test_save+'", "savefile"'))
    report=dest/'logic/module/startup_report.lua'
    report.write_text(report.read_text().replace("'freaky_fruit_fusion'",repr(test_save)))
    if a.recovery_test:
        bootstrap=dest/'logic/script/bootstrap.script'
        bootstrap.write_text(bootstrap.read_text().replace('self.loading=false',
            'self.loading=false\n    crash.set_file_path(sys.get_save_file('+json.dumps(test_save)+', "test-crash"))\n    crash.set_user_field(0,"Synthetic recovery test")\n    crash.set_user_field(1,"Loading game assets")\n    crash.write_dump()'))
    component='components {\n id: "test"\n component: "/tests/render_input.script"\n}\n'
    with (dest/'main/main.collection').open('a') as f:
        f.write('\nembedded_instances { id: "render_test" data: '+json.dumps(component)+' }\n')
    with (output/'build.log').open('w') as log:
        subprocess.run([java,'-Dcom.google.protobuf.use_unsafe_pre22_gencode','-jar',bob,
            '--platform','x86_64-linux','--max-cpu-threads','4','build'],cwd=dest,
            stdout=log,stderr=subprocess.STDOUT,check=True)
    env=os.environ.copy();env['DISPLAY']='127.0.0.1:98';env['LIBGL_ALWAYS_SOFTWARE']='1'
    with (output/'xvfb.log').open('w') as xf,(output/'render.log').open('w') as gf:
        x=subprocess.Popen([a.xvfb,':98','-screen','0','1080x2424x24','-nolisten','unix',
            '-nolisten','local','-listen','tcp','-ac'],env=env,stdout=xf,stderr=subprocess.STDOUT)
        game=None;display=None
        try:
            time.sleep(.8)
            game=subprocess.Popen([engine,str(dest/'build/default/game.projectc')],
                cwd=dest,env=env,stdout=gf,stderr=subprocess.STDOUT)
            lib=C.CDLL('libX11.so.6')
            lib.XOpenDisplay.argtypes=[C.c_char_p];lib.XOpenDisplay.restype=C.c_void_p
            lib.XDefaultRootWindow.argtypes=[C.c_void_p];lib.XDefaultRootWindow.restype=C.c_ulong
            lib.XQueryTree.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_ulong),C.POINTER(C.c_ulong),C.POINTER(C.POINTER(C.c_ulong)),C.POINTER(C.c_uint)]
            lib.XFetchName.argtypes=[C.c_void_p,C.c_ulong,C.POINTER(C.c_char_p)]
            lib.XResizeWindow.argtypes=[C.c_void_p,C.c_ulong,C.c_uint,C.c_uint]
            lib.XWarpPointer.argtypes=[C.c_void_p,C.c_ulong,C.c_ulong,C.c_int,C.c_int,C.c_uint,C.c_uint,C.c_int,C.c_int]
            lib.XSendEvent.argtypes=[C.c_void_p,C.c_ulong,C.c_int,C.c_long,C.POINTER(Event)]
            lib.XFlush.argtypes=[C.c_void_p];lib.XCloseDisplay.argtypes=[C.c_void_p]
            display=lib.XOpenDisplay(env['DISPLAY'].encode());assert display,'X display unavailable'
            root_window=lib.XDefaultRootWindow(display);window=None
            for _ in range(50):
                children=C.POINTER(C.c_ulong)();n=C.c_uint();rr=C.c_ulong();parent=C.c_ulong()
                lib.XQueryTree(display,root_window,C.byref(rr),C.byref(parent),C.byref(children),C.byref(n))
                for i in range(n.value):
                    name=C.c_char_p();lib.XFetchName(display,children[i],C.byref(name))
                    if name.value and b'Freaky Fruit Fusion' in name.value:window=children[i]
                    if name:lib.XFree(name)
                if children:lib.XFree(children)
                if window:break
                time.sleep(.1)
            assert window,'Game window did not appear'
            lib.XResizeWindow(display,window,1080,2424);lib.XFlush(display)
            time.sleep(1.25)
            def click(px,py):
                lib.XWarpPointer(display,0,window,0,0,0,0,px,py);lib.XFlush(display);time.sleep(.1)
                for typ,mask,state in [(4,1<<2,0),(5,1<<3,1<<8)]:
                    event=Event();event.button=Button(typ,0,1,display,window,root_window,0,0,px,py,px,py,state,1,1)
                    lib.XSendEvent(display,window,1,mask,C.byref(event));lib.XFlush(display);time.sleep(.1)
            if a.recovery_test:
                subprocess.run(['import','-window',str(window),str(output/'recovery.png')],env=env,check=True)
                click(540,1767)
                time.sleep(.2)
                subprocess.run(['import','-window',str(window),str(output/'crash-details.png')],env=env,check=True)
                click(540,1767)
                click(540,1602)
                time.sleep(1.25)
            subprocess.run(['import','-window',str(window),str(output/'ready.png')],env=env,check=True)
            # 810 physical pixels correspond to world x=540 on this 1.5x-width screen.
            lib.XWarpPointer(display,0,window,0,0,0,0,810,1200);lib.XFlush(display);time.sleep(.1)
            for typ,mask,state in [(4,1<<2,0),(5,1<<3,1<<8)]:
                event=Event();event.button=Button(typ,0,1,display,window,root_window,0,0,810,1200,810,1200,state,1,1)
                lib.XSendEvent(display,window,1,mask,C.byref(event));lib.XFlush(display);time.sleep(.15)
            time.sleep(2.75)
            subprocess.run(['import','-window',str(window),str(output/'after-drop.png')],env=env,check=True)
            # Check the new credits panel visually without following its external links.
            for px,py in [(998,183),(540,1662)]:
                lib.XWarpPointer(display,0,window,0,0,0,0,px,py);lib.XFlush(display);time.sleep(.1)
                for typ,mask,state in [(4,1<<2,0),(5,1<<3,1<<8)]:
                    event=Event();event.button=Button(typ,0,1,display,window,root_window,0,0,px,py,px,py,state,1,1)
                    lib.XSendEvent(display,window,1,mask,C.byref(event));lib.XFlush(display);time.sleep(.1)
            subprocess.run(['import','-window',str(window),str(output/'credits.png')],env=env,check=True)
            code=game.wait(timeout=10)
        finally:
            if display:lib.XCloseDisplay(display)
            if game and game.poll() is None:game.terminate();game.wait(timeout=5)
            x.terminate();x.wait(timeout=5)
    log=(output/'render.log').read_text()
    assert code==0 and 'FRUIT_BOOT: game UI ready' in log and 'RENDER_INPUT_PASS' in log,log[-6000:]
    assert not any(v in log for v in ['ERROR:SCRIPT','ERROR:RESOURCE','ERROR:GAMESYS']),log[-6000:]
    from PIL import Image,ImageChops
    if a.recovery_test:
        recovery=Image.open(output/'recovery.png').convert('RGB')
        details=Image.open(output/'crash-details.png').convert('RGB')
        assert ImageChops.difference(recovery,details).getbbox(),'Crash details button did not open the report'
    ready=Image.open(output/'ready.png').convert('RGB');after=Image.open(output/'after-drop.png').convert('RGB')
    assert len(ready.getcolors(ready.width*ready.height) or [])>100,'Blank startup frame'
    assert ImageChops.difference(ready,after).crop((0,800,1080,2150)).getbbox(),'Drop did not change the playfield'
    print('PASS: real graphics, visible GUI/fruit, startup readiness, and touch aiming at 1080x2424')
