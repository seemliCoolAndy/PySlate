"""Copy installed dependency license texts with version/source manifest."""
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'licenses'
DEST.mkdir(exist_ok=True)
items=[]
for meta in sorted((ROOT/'node_modules').glob('**/package.json')):
    if 'node_modules' not in meta.parts or meta.parent.name.startswith('.'):
        continue
    try:
        p=json.loads(meta.read_text('utf-8'))
    except (ValueError, OSError):
        continue
    if not p.get('name') or not p.get('version'):
        continue
    name=p['name']; folder=DEST/name.replace('/','__').replace('@','')
    files=[f for f in meta.parent.iterdir() if f.is_file() and f.name.lower().startswith(('license','licence','copying','notice','copyright'))]
    if not files and name.startswith('@esbuild/'):
        # esbuild's architecture package is covered by the upstream MIT text.
        files=list((ROOT/'node_modules/esbuild').glob('LICENSE*'))
    if files:
        folder.mkdir(parents=True,exist_ok=True)
        for f in files:
            shutil.copy2(f,folder/f.name)
    build_only=('esbuild' in name or name in ('sharp','detect-libc','semver') or name.startswith(('@img/','@emnapi/')))
    items.append({'name':name,'version':p['version'],'license':p.get('license'),'repository':p.get('repository'),'licenseFiles':[str((folder/f.name).relative_to(DEST)).replace('\\','/') for f in files],'role':'build-only' if build_only else 'bundled-web'})
(DEST/'npm-dependencies.json').write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(ROOT/'LICENSE',DEST/'PySlate-MIT.txt')
print(f'{len(items)} dependency licenses collected; missing texts: '+', '.join(p['name'] for p in items if not p['licenseFiles']))
