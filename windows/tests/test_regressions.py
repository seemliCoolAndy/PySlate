"""Windows-specific fault-injection checks, confined to fresh workspace data."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from unittest import mock
import _winapi

parser = argparse.ArgumentParser()
root = Path(__file__).resolve().parents[2]
source = root
parser.add_argument('--python', type=Path, default=Path(sys.executable), help='Python executable; pass the bundled interpreter for release acceptance')
parser.add_argument('--report', type=Path, default=root / 'test-reports/windows-regressions.json')
args = parser.parse_args()
spec = importlib.util.spec_from_file_location('pyslate_server', source / 'runtime/server.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
work = root / 'work'
work.mkdir(parents=True, exist_ok=True)
temporary = Path(tempfile.mkdtemp(prefix='windows-regressions-', dir=work))
store = module.Store(source, temporary / 'Data')
results = []

def test(name, operation):
    try:
        operation()
    except Exception as error:
        results.append({'name':name, 'passed':False, 'error':repr(error)})
    else:
        results.append({'name':name, 'passed':True})

def same_volume_trash():
    project = store.dispatch({'action':'project.create', 'name':'delete-test'})['project']
    assert store.dispatch({'action':'project.delete', 'id':project['id']})['ok']
    assert list(store.trash.glob(project['id'] + '-*'))

def junction_and_failed_rename():
    project = store.dispatch({'action':'project.create', 'name':'junction-test'})['project']
    outside = temporary / 'outside'
    outside.mkdir()
    (outside / 'must-not-copy.txt').write_text('remain outside')
    link = store.directory(project['id']) / 'linked'
    _winapi.CreateJunction(str(outside), str(link))
    for action in ['project.files', 'project.delete']:
        try:
            store.dispatch({'action':action, 'id':project['id']})
        except ValueError:
            pass
        else:
            raise AssertionError('junction accepted: ' + action)
    assert (outside / 'must-not-copy.txt').read_text() == 'remain outside'
    assert not list(store.trash.rglob('must-not-copy.txt'))
    link.rmdir()
    with mock.patch.object(Path, 'rename', side_effect=PermissionError('injected sharing violation')):
        try:
            store.dispatch({'action':'project.delete', 'id':project['id']})
        except ValueError:
            pass
        else:
            raise AssertionError('rename failure should preserve project')
    assert store.directory(project['id']).exists()

def input_flood():
    run_dir = temporary / 'run'
    run_dir.mkdir()
    entry = run_dir / 'main.py'
    entry.write_text('import io, sys\nsys.stdin = io.StringIO("\\n" * 10000)\nfor _ in range(10000):\n    input()\n')
    run = module.Run(args.python.resolve(), source / 'runtime/worker.py', run_dir, entry)
    assert run.done.wait(5)
    assert sum(e['type']=='input' for e in run.events) <= 256
    assert len(run.events) <= 260 and '256' in run.reason

def delete_preserves_filename_and_rolls_back():
    project = store.dispatch({'action':'project.create', 'name':'user-metadata-name'})['project']
    store.dispatch({'action':'file.write', 'id':project['id'], 'path':'pyslate-recovery.json', 'content':'this belongs to the learner'})
    store.dispatch({'action':'project.delete', 'id':project['id']})
    deleted = next(path for path in store.trash.glob(project['id'] + '-*') if path.is_dir())
    assert (deleted / 'pyslate-recovery.json').read_text() == 'this belongs to the learner'
    assert deleted.with_name(deleted.name + '.recovery.json').is_file()
    project = store.dispatch({'action':'project.create', 'name':'failed-index-delete'})['project']
    directory = store.directory(project['id'])
    with mock.patch.object(store, 'save', side_effect=PermissionError('injected index write failure')):
        try:
            store.dispatch({'action':'project.delete', 'id':project['id']})
        except PermissionError:
            pass
        else:
            raise AssertionError('index write failure should reject delete')
    assert directory.is_dir() and (directory / 'main.py').is_file()
    assert store.project(project['id'])['id'] == project['id']
    assert not list(store.trash.glob(project['id'] + '-*'))

test('same-volume project trash rename', same_volume_trash)
test('junction rejected and injected rename failure preserves project', junction_and_failed_rename)
test('synthetic input event flood bounded in parent service', input_flood)
test('delete preserves learner metadata filename and rolls back failed index save', delete_preserves_filename_and_rolls_back)
report = {'platform':'Windows x64', 'results':results, 'passed':sum(r['passed'] for r in results), 'failed':sum(not r['passed'] for r in results), 'testData':str(temporary)}
args.report.parent.mkdir(parents=True, exist_ok=True)
args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(report['failed']))
