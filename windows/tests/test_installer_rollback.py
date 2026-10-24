"""Inject a locked destination into an isolated actual installer update."""
import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
from pathlib import Path
import subprocess
import time

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--installer',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--expect-protection',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
workspace=root/('work/windows-installer-rollback-'+str(time.time_ns()))
target=workspace/'Application'
(target/'web').mkdir(parents=True)
(target/'pyslate.install').write_text('PySlate 0.2','utf-8')
(target/'VERSION.txt').write_text('previous-version-preserve','utf-8')
(target/'web/app.js').write_text('previous-app-preserve','utf-8')
(target/'user-note.txt').write_text('unlisted-user-file','utf-8')
before={p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()}
kernel=ctypes.WinDLL('kernel32',use_last_error=True)
kernel.CreateFileW.argtypes=[wintypes.LPCWSTR,wintypes.DWORD,wintypes.DWORD,ctypes.c_void_p,wintypes.DWORD,wintypes.DWORD,wintypes.HANDLE]
kernel.CreateFileW.restype=wintypes.HANDLE
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
handle=kernel.CreateFileW(str(target/'web/app.js'),0x80000000,1,None,3,0,None)
if handle in (None,ctypes.c_void_p(-1).value):raise ctypes.WinError(ctypes.get_last_error())
try:
    completed=subprocess.run([str(args.installer.resolve()),'--silent','--target',str(target),'--no-shortcuts','--portable-test','--accept-webview2-license','--report',str(workspace/'installer-error.txt')],timeout=180)
finally:
    kernel.CloseHandle(handle)
after={p.relative_to(target).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in target.rglob('*') if p.is_file()}
unchanged=all(after.get(k)==v for k,v in before.items())
extra=sorted(set(after)-set(before))
report={'installer':str(args.installer.resolve()),'installerSHA256':hashlib.sha256(args.installer.read_bytes()).hexdigest(),'exitCode':completed.returncode,'originalFilesUnchanged':unchanged,'newFilesAfterFailedInstall':extra,'directoryExactlyRestored':before==after,'testDirectory':str(workspace),'bugReproduced':completed.returncode!=0 and before!=after,'scope':'Actual EXE update to isolated marked workspace, one destination held read-only, no shortcuts or registration'}
report['passed']=completed.returncode!=0 and before==after if args.expect_protection else report['bugReproduced']
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='newFilesAfterFailedInstall'},ensure_ascii=False,indent=2))
raise SystemExit(not report['passed'])
