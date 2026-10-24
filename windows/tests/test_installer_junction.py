"""Check that an installer cannot write through a junction inside its target."""
import argparse
import _winapi
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
workspace=root/('work/windows-installer-link-'+str(time.time_ns()))
target,outside=workspace/'Application',workspace/'OutsideFixture'
target.mkdir(parents=True);outside.mkdir()
(target/'pyslate.install').write_text('PySlate 0.2','utf-8')
(target/'VERSION.txt').write_text('previous-version-preserve','utf-8')
(outside/'app.js').write_text('outside-file-preserve','utf-8')
_winapi.CreateJunction(str(outside),str(target/'web'))
before={p.relative_to(outside).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in outside.rglob('*') if p.is_file()}
completed=subprocess.run([str(args.installer.resolve()),'--silent','--target',str(target),'--no-shortcuts','--portable-test','--accept-webview2-license','--report',str(workspace/'installer-error.txt')],timeout=180)
after={p.relative_to(outside).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in outside.rglob('*') if p.is_file()}
protected=completed.returncode!=0 and before==after and (target/'VERSION.txt').read_text('utf-8')=='previous-version-preserve'
report={'installer':str(args.installer.resolve()),'installerSHA256':hashlib.sha256(args.installer.read_bytes()).hexdigest(),'exitCode':completed.returncode,'outsideUnchanged':before==after,'outsideAddedFiles':len(set(after)-set(before)),'beforeTargetChangesRejected':protected,'testDirectory':str(workspace),'bugReproduced':before!=after,'scope':'Actual EXE, junction connects two fixtures wholly within this workspace; no real user project or system directory'}
report['passed']=protected if args.expect_protection else report['bugReproduced']
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(not report['passed'])
