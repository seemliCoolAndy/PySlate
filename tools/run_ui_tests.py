"""Own a disposable local bridge and run the UI suite, leaving user data alone."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

parser=argparse.ArgumentParser()
parser.add_argument('--python',default=sys.executable)
parser.add_argument('--reports',default=str(Path(__file__).resolve().parents[1]/'test-reports'))
parser.add_argument('--work',default=str(Path(__file__).resolve().parents[1]/'work'))
parser.add_argument('--node-modules',default='')
parser.add_argument('--script',default='test_ui.cjs',help='UI suite filename in tools/')
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
work=Path(args.work).resolve();work.mkdir(exist_ok=True,parents=True)
reports=Path(args.reports).resolve();reports.mkdir(exist_ok=True,parents=True)
with tempfile.TemporaryDirectory(prefix='pyslate-owned-ui-',dir=work) as data:
    with (work/'ui-suite-backend.log').open('w',encoding='utf-8') as error:
        backend=subprocess.Popen([args.python,'-u','-X','utf8',str(root/'runtime/server.py'),'--root',str(root),'--data',data],stdout=subprocess.PIPE,stderr=error,text=True,encoding='utf-8')
        try:
            ready=json.loads(backend.stdout.readline())
            env=dict(os.environ)
            if args.node_modules:env['NODE_PATH']=args.node_modules
            script=(root/'tools'/args.script).resolve()
            if script.parent != (root/'tools').resolve():raise ValueError('UI suite must be in tools/')
            result=subprocess.run([shutil.which('node') or 'node',str(script),ready['url'],str(reports)],env=env)
            code=result.returncode
        finally:
            # This subprocess is created by this test, uses only its TemporaryDirectory,
            # and has no user-owned application window or unsaved user document.
            backend.terminate()
            backend.wait(timeout=10)
sys.exit(code)
