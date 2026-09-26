#!/usr/bin/env python3
"""Package privately using a separately compiled, matching OpenGL ES engine.

The game build never calls a remote native build service. Supply libdmengine.so
from Defold 1.13.1 / 574678c, ARM64 Android, legacy Box2D, OpenGL ES only.
The ordinary Defold editor can instead use main/android-compat.appmanifest.
"""
import argparse,hashlib,os,shutil,subprocess,tempfile
from pathlib import Path
from urllib.parse import urlparse

p=argparse.ArgumentParser()
p.add_argument('--bob',required=True);p.add_argument('--java',required=True)
p.add_argument('--engine',required=True);p.add_argument('--output',required=True)
a=p.parse_args();root=Path(__file__).resolve().parents[1]
engine=Path(a.engine).resolve();assert engine.is_file(),engine
out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
java=str(Path(a.java).resolve());bob=str(Path(a.bob).resolve())
proxy=urlparse(os.environ.get('HTTPS_PROXY',''))
cmd=[java,'-Dcom.google.protobuf.use_unsafe_pre22_gencode']
if proxy.hostname:
    for protocol in ['http','https']:
        cmd += [f'-D{protocol}.proxyHost={proxy.hostname}',f'-D{protocol}.proxyPort={proxy.port or 80}']
cmd += ['-jar',bob,'--platform','arm64-android','--architectures','arm64-android',
    '--max-cpu-threads','4','--variant','debug','--archive']
with tempfile.TemporaryDirectory(prefix='fruit-local-build-') as tmp:
    settings=Path(tmp)/'local.settings'
    settings.write_text('[native_extension]\napp_manifest =\n')
    base=cmd+['--settings',str(settings)]
    with (out/'build.log').open('w') as log:
        subprocess.run(base+['build'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
        # Bob cleans old engine binaries during the local resource build.
        target=root/'build/arm64-android/libdmengine.so';target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(engine,target)
        bundle=out/'FreakyFruitFusion'
        (bundle/'FreakyFruitFusion.aab').unlink(missing_ok=True)
        subprocess.run(base+['--strip-executable','--bundle-format','apk','--bundle-output',str(out),
            'bundle'],cwd=root,stdout=log,stderr=subprocess.STDOUT,check=True)
    print('APK:',bundle/'FreakyFruitFusion.apk')
    print('Input engine SHA256:',hashlib.sha256(engine.read_bytes()).hexdigest())
