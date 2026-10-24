"""Uninstall must preserve unlisted directories and never traverse their links."""
import argparse
import _winapi
import hashlib
import json
from pathlib import Path
import subprocess
import time
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--uninstaller',type=Path,required=True)
parser.add_argument('--report',type=Path,required=True)
parser.add_argument('--expect-protection',action='store_true')
args=parser.parse_args()
root=Path(__file__).resolve().parents[2]
workspace=root/('work/windows-uninstaller-link-'+str(time.time_ns()))
target,outside=workspace/'Application',workspace/'OutsideFixture'
target.mkdir(parents=True);(outside/'empty-child').mkdir(parents=True)
(target/'user-empty-folder').mkdir()
(target/'pyslate.install').write_text('PySlate 0.2','utf-8')
(target/'install-manifest.txt').write_text('app.txt\ninstall-manifest.txt\npyslate.install\n','utf-8')
(target/'app.txt').write_text('app','utf-8')
_winapi.CreateJunction(str(outside),str(target/'unlisted-link'))
completed=subprocess.run([str(args.uninstaller.resolve()),'--remove',str(target),'--portable-test'],timeout=30)
protected=completed.returncode==0 and not (target/'app.txt').exists() and (outside/'empty-child').is_dir() and (target/'user-empty-folder').is_dir() and (target/'unlisted-link').is_dir()
report={'uninstaller':str(args.uninstaller.resolve()),'uninstallerSHA256':hashlib.sha256(args.uninstaller.read_bytes()).hexdigest(),'exitCode':completed.returncode,'listedFileRemoved':not (target/'app.txt').exists(),'outsideEmptyDirectoryPreserved':(outside/'empty-child').is_dir(),'unlistedEmptyDirectoryPreserved':(target/'user-empty-folder').is_dir(),'unlistedJunctionPreserved':(target/'unlisted-link').is_dir(),'testDirectory':str(workspace),'bugReproduced':not (outside/'empty-child').is_dir(),'scope':'Actual uninstaller with explicit workspace target, junction joins only owned fixtures; no shortcuts/registry'}
report['passed']=protected if args.expect_protection else report['bugReproduced']
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(not report['passed'])
