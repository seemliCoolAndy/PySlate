"""Verify local image coverage and optional same-schema content baseline."""
import argparse, hashlib, json, re, xml.etree.ElementTree as ET
from pathlib import Path
parser=argparse.ArgumentParser()
parser.add_argument('--baseline')
parser.add_argument('--report',default=str(Path(__file__).resolve().parents[1]/'test-reports/diagram-coverage-v2.json'))
args=parser.parse_args()
root=Path(__file__).resolve().parents[1]
raw=(root/'course/course.json').read_bytes()
course=json.loads(raw)
def units(data):
    return [u for c in data['chapters'] for t in c['lessons'] for u in t.get('tiers',[t])]
def identity(unit):
    return unit.get('unitId',unit['id'])
topics=[t for c in course['chapters'] for t in c['lessons']]
lessons=units(course);issues=[];rows=[]
old=json.loads(Path(args.baseline).read_text('utf-8')) if args.baseline else None
if old and old['version']!=course['version']:
    raise ValueError('Baseline must use the same course schema')
old_by={identity(u):u for u in units(old)} if old else {}
for u in lessons:
    key=identity(u);name=u.get('diagram','');file=root/'web'/name
    row=dict(id=key,title=u['title'],image=name,exists=bool(re.fullmatch(r'course-assets/[a-zA-Z0-9_.-]+',name)) and file.is_file())
    if not row['exists']:
        issues.append(key+': missing or nonlocal image')
    else:
        data=file.read_bytes();row.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
        if course['version']>=2:
            if not name.endswith('.webp') or data[:4]!=b'RIFF' or data[8:12]!=b'WEBP' or int.from_bytes(data[4:8],'little')+8!=len(data):
                issues.append(key+': invalid WebP container')
            if not u.get('visual',{}).get('alt'):
                issues.append(key+': missing alt text')
        elif file.suffix=='.svg':
            svg=ET.fromstring(data.decode('utf-8-sig'));row['viewBox']=svg.attrib.get('viewBox')
            for node in svg.iter():
                if node.tag.rsplit('}',1)[-1] in ('script','foreignObject'):
                    issues.append(key+': executable SVG')
                if any(v.startswith(('http:','https:','//')) for k,v in node.attrib.items() if k.endswith('href')):
                    issues.append(key+': external dependency')
    if old:
        keep=lambda d:{k:v for k,v in d.items() if k not in ('diagram','visual')}
        row['executableFieldsUnchanged']=key in old_by and keep(old_by[key])==keep(u)
        if not row['executableFieldsUnchanged']:
            issues.append(key+': nonvisual content differs')
    rows.append(row)
if course['version']>=2 and (len(topics)!=58 or len(rows)!=174):
    issues.append('v2 must retain58 topics and174 units')
if len({r['image'] for r in rows})!=len(rows):
    issues.append('reused image paths')
hashes=[r['sha256'] for r in rows if 'sha256' in r]
if len(set(hashes))!=len(hashes):
    issues.append('duplicate image content')
report=dict(courseVersion=course['version'],topics=len(topics),units=len(rows),covered=sum(r['exists'] for r in rows),uniqueImages=len(set(hashes)),courseSHA256=hashlib.sha256(raw).hexdigest(),issues=issues,results=rows,passed=not issues)
Path(args.report).parent.mkdir(parents=True,exist_ok=True)
Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
raise SystemExit(bool(issues))
