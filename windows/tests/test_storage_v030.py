"""Fault-injection regressions for catalog transactions and non-destructive create."""
import argparse
import base64
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import traceback
from unittest import mock
import zipfile

root = Path(__file__).resolve().parents[2]
source = root
parser = argparse.ArgumentParser()
parser.add_argument('--report', type=Path, required=True)
parser.add_argument('--python', type=Path, default=Path(sys.executable), help='Python executable; pass the bundled interpreter for release acceptance')
args = parser.parse_args()
spec = importlib.util.spec_from_file_location('pyslate_store_v030', source / 'runtime/server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
work = root / 'work'
work.mkdir(parents=True, exist_ok=True)
workspace = Path(tempfile.mkdtemp(prefix='windows-store-v030-', dir=work))
results = []

def make_store():
    return module.Store(source, workspace / str(len(results)), executable=args.python.resolve())

def reject(operation, expected=Exception):
    try:
        operation()
    except expected:
        return
    raise AssertionError('operation should fail')

def consistent(store, before):
    assert store.catalog == before, 'failed mutation leaked into live catalog'
    assert json.loads(store.catalog_file.read_text('utf-8')) == before, 'disk catalog changed'
    assert module.Store(source, store.data).catalog == before, 'restarted catalog changed'

def test(name, operation):
    try:
        operation()
        results.append({'name':name,'passed':True})
    except Exception:
        results.append({'name':name,'passed':False,'error':traceback.format_exc()})

def state_failure():
    store = make_store()
    before = copy.deepcopy(store.catalog)
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'state.patch','patch':{'trusted':True,'progress':{'l01':True}}}))
    consistent(store, before)

def invalid_update():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'original'})['project']
    before = copy.deepcopy(store.catalog)
    reject(lambda:store.dispatch({'action':'project.update','id':project['id'],'name':'changed','category':'bad\ncategory'}), ValueError)
    consistent(store, before)

def update_failure():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'original'})['project']
    before = copy.deepcopy(store.catalog)
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'project.update','id':project['id'],'name':'changed','category':'new-category'}))
    consistent(store, before)

def category_failure():
    store = make_store()
    before = copy.deepcopy(store.catalog)
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'category.create','name':'not-saved'}))
    consistent(store, before)

def create_failure():
    store = make_store()
    before = copy.deepcopy(store.catalog)
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'project.create','name':'not-saved','category':'new-category'}))
    consistent(store, before)
    assert list(store.projects_dir.iterdir()) == [], 'orphan new directory'

def duplicate_failure():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'original'})['project']
    before = copy.deepcopy(store.catalog)
    directories = set(store.projects_dir.iterdir())
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'project.duplicate','id':project['id']}))
    consistent(store, before)
    assert set(store.projects_dir.iterdir()) == directories, 'orphan duplicate directory'

def import_failure():
    store = make_store()
    before = copy.deepcopy(store.catalog)
    memory = io.BytesIO()
    with zipfile.ZipFile(memory,'w') as archive:
        archive.writestr('main.py','print(42)\n')
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch({'action':'project.import','filename':'example.zip','base64':base64.b64encode(memory.getvalue()).decode()}))
    consistent(store, before)
    assert list(store.projects_dir.iterdir()) == [], 'orphan import directory'
    assert not list(store.data.glob('import-*')), 'orphan import stage'

def run_failure():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'run-test'})['project']
    store.dispatch({'action':'state.patch','patch':{'trusted':True}})
    before = copy.deepcopy(store.catalog)
    with mock.patch.object(store,'save',side_effect=PermissionError('injected index failure')), mock.patch.object(module,'Run') as constructor:
        reject(lambda:store.dispatch({'action':'run','id':project['id']}))
        assert not constructor.called, 'process started despite failed catalog save'
    consistent(store,before)
    assert not store.runs, 'orphan run'

def file_action_failure(action):
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'file-test'})['project']
    directory = store.directory(project['id'])
    previous = (directory/'main.py').read_bytes()
    before = copy.deepcopy(store.catalog)
    request = {'action':action,'id':project['id'],'path':'main.py','newPath':'renamed.py','content':'print("changed")\n'}
    if action == 'file.create': request['path'] = 'new.py'
    with mock.patch.object(store,'save',side_effect=PermissionError('injected index failure')):
        reject(lambda:store.dispatch(request))
    assert (directory/'main.py').read_bytes() == previous, 'file changed despite failed index save'
    assert not (directory/'renamed.py').exists() and not (directory/'new.py').exists()
    consistent(store,before)

def exclusive_create():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'new-file'})['project']
    directory = store.directory(project['id'])
    original = (directory/'main.py').read_bytes()
    for name in ['main.py','MAIN.py','./main.py']:
        reject(lambda:store.dispatch({'action':'file.create','id':project['id'],'path':name,'content':'overwrite'}))
        assert (directory/'main.py').read_bytes() == original, 'create overwrote existing file'
    assert store.dispatch({'action':'file.create','id':project['id'],'path':'sub/new.py','content':'初始内容'})['ok']
    assert (directory/'sub/new.py').read_text('utf-8') == '初始内容'

def racing_create():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'racing-file'})['project']
    destination = store.directory(project['id'])/'new.py'
    # A learner's running code can create the file after the preflight check.
    original_touch = store.touch
    def create_between_check_and_open(project_id):
        original_touch(project_id)
        destination.write_text('created by running code','utf-8')
    with mock.patch.object(store,'touch',side_effect=create_between_check_and_open):
        reject(lambda:store.dispatch({'action':'file.create','id':project['id'],'path':'new.py','content':'overwrite'}),FileExistsError)
    assert destination.read_text('utf-8') == 'created by running code'

def failed_create_flush():
    store = make_store()
    project = store.dispatch({'action':'project.create','name':'create-flush'})['project']
    destination = store.directory(project['id'])/'new.py'
    # Isolate the file flush from the preceding catalog write.
    with mock.patch.object(store,'touch'), mock.patch.object(module.os,'fsync',side_effect=OSError('injected new-file flush failure')):
        reject(lambda:store.dispatch({'action':'file.create','id':project['id'],'path':'new.py','content':'partial write'}),OSError)
    assert not destination.exists(), 'failed create left a partial file'

def real_atomic_save_failure():
    store = make_store()
    before = copy.deepcopy(store.catalog)
    real_write = module.atomic_write
    def fail_catalog(path,data):
        if Path(path) == store.catalog_file: raise PermissionError('injected replacement failure')
        return real_write(path,data)
    with mock.patch.object(module,'atomic_write',side_effect=fail_catalog):
        reject(lambda:store.dispatch({'action':'state.patch','patch':{'lastLesson':'l33'}}))
    consistent(store,before)
    store.dispatch({'action':'state.patch','patch':{'theme':'dark'}})
    assert module.Store(source,store.data).catalog['state']['theme'] == 'dark'
    assert store.catalog['state']['lastLesson'] == 'l01', 'retry accidentally persisted failed mutation'

for name,operation in [('state patch rollback',state_failure),('update validates all fields before mutation',invalid_update),('project update rollback',update_failure),('category create rollback',category_failure),('project create rollback and cleanup',create_failure),('duplicate publish rollback and cleanup',duplicate_failure),('import publish rollback and cleanup',import_failure),('failed run metadata never starts child',run_failure),('exclusive create prevents case-alias overwrite',exclusive_create),('atomic replacement failure and subsequent save recovery',real_atomic_save_failure)]:
    test(name,operation)
for action in ['file.write','file.rename','file.delete','file.create']:
    test(action+' index failure preserves files',lambda action=action:file_action_failure(action))
test('exclusive create resists a file appearing after preflight',racing_create)
test('failed new-file flush removes only the partial new file',failed_create_flush)
report={'version':'0.3.0','python':str(args.python.resolve()),'results':results,'passed':sum(item['passed'] for item in results),'failed':sum(not item['passed'] for item in results),'sourceSha256':hashlib.sha256((source/'runtime/server.py').read_bytes()).hexdigest(),'testData':str(workspace)}
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
raise SystemExit(bool(report['failed']))
