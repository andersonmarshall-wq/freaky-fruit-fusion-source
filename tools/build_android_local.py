#!/usr/bin/env python3
"""Package privately using a separately compiled, matching OpenGL ES engine.

Always build from source in a fresh directory and validate the finished APK's
texture payloads. Never reuse project build outputs: a truncated cached atlas
can retain a valid-looking header and crash the phone's graphics driver.
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
    temporary=Path(tmp)
    work=temporary/'game'
    shutil.copytree(root,work,ignore=shutil.ignore_patterns(
        '.git','.internal','build','__pycache__','*.zip','*.apk','*.aab'))
    if (root/'.internal/lib').exists():
        shutil.copytree(root/'.internal/lib',work/'.internal/lib',dirs_exist_ok=True)
    settings=temporary/'local.settings'
    settings.write_text('[native_extension]\napp_manifest =\n')
    base=cmd+['--settings',str(settings)]
    verify=[java,'-Dcom.google.protobuf.use_unsafe_pre22_gencode','-cp',bob,
        str(root/'tools/VerifyTexturePayloads.java')]
    bundle_out=temporary/'bundle'
    with (out/'build.log').open('w') as log:
        subprocess.run(base+['build'],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run(verify+['--archive',str(work/'build/default/game')],
            stdout=log,stderr=subprocess.STDOUT,check=True)
        # Bob cleans old engine binaries during the local resource build.
        target=work/'build/arm64-android/libdmengine.so';target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(engine,target)
        subprocess.run(base+['--strip-executable','--bundle-format','apk','--bundle-output',str(bundle_out),
            'bundle'],cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
        built=bundle_out/'FreakyFruitFusion/FreakyFruitFusion.apk'
        subprocess.run(verify+['--apk',str(built)],stdout=log,stderr=subprocess.STDOUT,check=True)
        bundle=out/'FreakyFruitFusion';bundle.mkdir(parents=True,exist_ok=True)
        result=bundle/'FreakyFruitFusion.apk'
        shutil.copy2(built,result)
        # Check the exported bytes too, not just the intermediate package.
        subprocess.run(verify+['--apk',str(result)],stdout=log,stderr=subprocess.STDOUT,check=True)
        shutil.copy2(built.parent/'AndroidManifest.xml',bundle/'AndroidManifest.xml')
    # Preserve a newly generated local debug identity for future updates.
    for name in ['debug.keystore','debug.keystore.pass.txt']:
        if not (root/name).exists() and (work/name).exists():shutil.copy2(work/name,root/name)
    print('APK:',result)
    print('Input engine SHA256:',hashlib.sha256(engine.read_bytes()).hexdigest())
