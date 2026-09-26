#!/usr/bin/env python3
"""Run the real scripts in an isolated, headless Defold project.
Usage: python3 tools/run_engine_tests.py --bob /path/bob.jar --java /path/java --engine /path/dmengine_headless
"""
import argparse,shutil,tempfile,subprocess,json,uuid
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--bob',required=True);p.add_argument('--java',default='java');p.add_argument('--engine',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='fruit-engine-test-') as tmp:
 dest=Path(tmp)/'game'
 shutil.copytree(root,dest,ignore=shutil.ignore_patterns('.git','build','__pycache__','*.zip'))
 # Retain downloaded dependency ZIPs without editor/session state.
 if (root/'.internal/lib').exists():shutil.copytree(root/'.internal/lib',dest/'.internal/lib',dirs_exist_ok=True)
 # The Android-only graphics manifest has no effect on this Linux test engine.
 project=dest/'game.project'
 project.write_text(project.read_text().replace('app_manifest = /main/android-compat.appmanifest',''))
 save_prefix='freaky_fruit_fusion_test_'+uuid.uuid4().hex
 for relative in ['logic/module/saver.lua','logic/module/startup_report.lua']:
  save=dest/relative;save.write_text(save.read_text().replace('freaky_fruit_fusion',save_prefix))
 col=dest/'main/main.collection';component='components {\n  id: "driver"\n  component: "/tests/integration.script"\n}\n'
 with col.open('a') as f:f.write('\nembedded_instances {\n  id: "test_driver"\n  data: '+json.dumps(component)+'\n}\n')
 r=subprocess.run([str(Path(a.java).resolve()) if '/' in a.java else a.java,'-Dcom.google.protobuf.use_unsafe_pre22_gencode','-jar',str(Path(a.bob).resolve()),'--platform','x86_64-linux','--max-cpu-threads','4','build'],cwd=dest,capture_output=True,text=True)
 if r.returncode:print(r.stdout+r.stderr);raise SystemExit(r.returncode)
 try:
  r=subprocess.run([str(Path(a.engine).resolve()),str(dest/'build/default/game.projectc')],cwd=dest,capture_output=True,text=True,timeout=20)
  log=r.stdout+r.stderr
 except subprocess.TimeoutExpired as e:
  log=(e.stdout or b'').decode(errors='replace')+(e.stderr or b'').decode(errors='replace')
  (root/'tests/engine-test-result.txt').write_text(log)
  print(log[-8000:]);raise
 output=root/'tests/engine-test-result.txt';output.write_text(log)
 for line in log.splitlines():
  if any(w in line for w in ['PRESSURE','ENGINE_INTEGRATION','ERROR:SCRIPT','ERROR:GAMEOBJECT','ERROR:RESOURCE']):print(line)
 assert r.returncode==0 and 'ENGINE_INTEGRATION_PASS' in log and 'ERROR:SCRIPT' not in log,'Headless integration failed; see tests/engine-test-result.txt'
 print('PASS: complete runtime integration')
