"""Real CPython regressions for the v0.3 input lifecycle.

The production 30/300-second defaults are checked and a genuine >30-second
user wait is exercised. Short constructor budgets cover expiry without waiting
five minutes; they never change production defaults or release files.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import traceback

parser=argparse.ArgumentParser(description=__doc__)
root=Path(__file__).resolve().parents[2]
source=root
parser.add_argument('--python',type=Path,default=Path(sys.executable),help='Python executable; pass the bundled interpreter for release acceptance')
parser.add_argument('--report',type=Path,default=root/'test-reports/windows-input-v030.json')
args=parser.parse_args()
spec=importlib.util.spec_from_file_location('pyslate_input_runtime',source/'runtime/server.py')
runtime=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
work=root/'work'
work.mkdir(parents=True,exist_ok=True)
workspace=Path(tempfile.mkdtemp(prefix='windows-input-v030-',dir=work))
runs=[]
results=[]

def launch(code,**limits):
    directory=workspace/str(len(runs)+1)
    directory.mkdir()
    entry=directory/'main.py'
    entry.write_text(code,'utf-8')
    run=runtime.Run(args.python.resolve(),source/'runtime/worker.py',directory,entry,**limits)
    runs.append(run)
    return run

def until(run,predicate,timeout=4):
    began=time.monotonic()
    while time.monotonic()-began<timeout:
        snapshot=run.poll(0)
        if predicate(snapshot):
            return snapshot
        time.sleep(.01)
    raise AssertionError('condition not reached: '+repr(run.poll(0)))

def waiting(run,after=0):
    return until(run,lambda s:s['waiting'] and s['inputRequestId']>after)

def finish(run,timeout=5):
    assert run.done.wait(timeout), run.poll(0)
    snapshot=run.poll(0)
    assert not snapshot['running'] and not snapshot['waiting'] and snapshot['inputRequestId'] is None
    assert sum(e['type']=='exit' for e in snapshot['events'])==1
    return snapshot

def stdout(run):
    return ''.join(e['text'] for e in run.poll(0)['events'] if e['type']=='stdout').replace('\r\n','\n')

def rejects(operation):
    try:
        operation()
    except ValueError as error:
        return str(error)
    raise AssertionError('stale/duplicate/invalid submission accepted')

def test(name,operation):
    began=time.monotonic()
    try:
        detail=operation()
        results.append({'name':name,'passed':True,'seconds':round(time.monotonic()-began,3),'detail':detail})
        print('PASS',name,flush=True)
    except Exception:
        results.append({'name':name,'passed':False,'seconds':round(time.monotonic()-began,3),'error':traceback.format_exc()})
        print('FAIL',name,traceback.format_exc(),flush=True)
    finally:
        for run in runs:
            if run.running:
                run.stop('输入回归用例结束，清理测试进程。')
                run.done.wait(3)

def production_limits():
    assert runtime.VERSION=='0.3.0' and runtime.RUN_TIMEOUT==30 and runtime.INPUT_WAIT_TIMEOUT==300
    return {'executionSeconds':runtime.RUN_TIMEOUT,'perInputWaitSeconds':runtime.INPUT_WAIT_TIMEOUT}

def snapshot_and_empty():
    run=launch("a=input('第一项：')\nb=input('第二项：')\nprint(repr(a),repr(b))\n")
    first=waiting(run)
    assert first['inputRequestId']==1
    same=run.poll(first['cursor'])
    assert same['events']==[] and same['waiting'] and same['inputRequestId']==1
    accepted=run.send_input('',request_id=1)
    assert accepted['ok'] and accepted['acceptedRequestId']==1 and not accepted['waiting']
    second=waiting(run,1)
    assert second['inputRequestId']==2
    stale=rejects(lambda:run.send_input('stale',request_id=1))
    run.send_input('中文第二项',request_id=2)
    end=finish(run)
    assert stdout(run)=="第一项：第二项：'' '中文第二项'\n" and run.process.returncode==0
    assert [e['requestId'] for e in end['events'] if e['type']=='input_end']==[1,2]
    return {'stdout':stdout(run),'staleError':stale,'requestIds':[1,2]}

def duplicate_and_multiline():
    run=launch("import time\na=input()\ntime.sleep(.15)\nb=input()\nprint(a,b)\n")
    first=waiting(run)
    rejects(lambda:run.send_input('a\nb',request_id=first['inputRequestId']))
    run.send_input('A',request_id=first['inputRequestId'])
    duplicate=rejects(lambda:run.send_input('WRONG',request_id=first['inputRequestId']))
    second=waiting(run,first['inputRequestId'])
    rejects(lambda:run.send_input('WRONG',request_id=first['inputRequestId']))
    assert run.poll(0)['inputRequestId']==second['inputRequestId']
    run.send_input('B',request_id=second['inputRequestId'])
    finish(run)
    assert stdout(run)=='A B\n'
    return {'duplicateError':duplicate,'stdout':stdout(run)}

def paused_budget():
    run=launch("import time\ntime.sleep(.1)\na=input()\ntime.sleep(.1)\nprint(a)\n",timeout=.8,input_timeout=3)
    request=waiting(run)
    time.sleep(1.0)
    assert run.poll(0)['waiting'] and run.running
    run.send_input('wait excluded',request_id=request['inputRequestId'])
    finish(run)
    assert run.process.returncode==0 and stdout(run)=='wait excluded\n' and run.active_seconds<.8
    return {'executionSeconds':round(run.active_seconds,3),'userWaitSeconds':1.0}

def cumulative_budget():
    run=launch("import time\ntime.sleep(.25)\ninput()\ntime.sleep(1.0)\n",timeout=1.0,input_timeout=3)
    request=waiting(run)
    time.sleep(1.1)
    resumed=time.monotonic()
    run.send_input('',request_id=request['inputRequestId'])
    finish(run)
    elapsed=time.monotonic()-resumed
    assert '累计执行超过 1 秒' in run.reason and run.process.returncode!=0 and elapsed<.9
    return {'secondsAfterReply':round(elapsed,3),'executionSeconds':round(run.active_seconds,3),'reason':run.reason}

def wait_deadline():
    run=launch('input()\n',timeout=3,input_timeout=.3)
    waiting(run)
    finish(run)
    assert '等待输入超过 0.3 秒' in run.reason and run.process.returncode!=0
    return {'reason':run.reason,'snapshot':run.poll(run.poll(0)['cursor'])}

def stop_waiting():
    run=launch('input()\n')
    request=waiting(run)
    began=time.monotonic()
    run.stop()
    finish(run)
    assert time.monotonic()-began<1.5
    error=rejects(lambda:run.send_input('late',request_id=request['inputRequestId']))
    return {'lateError':error}

def eof():
    run=launch("try:\n    input('EOF测试：')\nexcept EOFError:\n    print('EOF received')\n")
    request=waiting(run)
    run.send_input(request_id=request['inputRequestId'])
    finish(run)
    assert run.process.returncode==0 and stdout(run)=='EOF测试：EOF received\n'
    return {'stdout':stdout(run)}

def stream_zero_and_partial():
    run=launch("import sys\nprint(repr(sys.stdin.readline(0)),repr(sys.stdin.read(0)))\nprint(repr(sys.stdin.readline(2)))\nprint(repr(sys.stdin.readline()))\n")
    request=waiting(run)
    assert request['inputRequestId']==1
    run.send_input('abcd',request_id=1)
    finish(run)
    assert stdout(run)=="'' ''\n'ab'\n'cd\\n'\n"
    return {'stdout':stdout(run),'requestCount':run.input_count}

def raw_read_until_eof():
    run=launch("import sys\nprint(repr(sys.stdin.read()))\n")
    first=waiting(run)
    run.send_input('第一行',request_id=first['inputRequestId'])
    second=waiting(run,first['inputRequestId'])
    run.send_input(request_id=second['inputRequestId'])
    finish(run)
    assert run.process.returncode==0 and stdout(run)=="'第一行\\n'\n"
    return {'stdout':stdout(run)}

def many_inputs():
    run=launch("for i in range(30):\n    assert input()==str(i)\nprint('30 inputs verified')\n")
    previous=0
    for value in range(30):
        request=waiting(run,previous)
        assert request['inputRequestId']==value+1
        previous=request['inputRequestId']
        run.send_input(str(value),request_id=previous)
    finish(run)
    assert stdout(run)=='30 inputs verified\n'
    return {'requests':previous,'stdout':stdout(run)}

def exit_race():
    run=launch("import os,threading,time\ndef exit_soon():\n    time.sleep(.2)\n    os._exit(0)\nthreading.Thread(target=exit_soon,daemon=True).start()\ninput()\n")
    request=waiting(run)
    end=finish(run)
    error=rejects(lambda:run.send_input('late',request_id=request['inputRequestId']))
    assert not end['waiting'] and end['events'][-1]['type']=='exit'
    return {'lateError':error,'exitCode':run.process.returncode}

def redirected_stdin():
    run=launch("import io,sys\nsys.stdin=io.StringIO('a\\nb\\n')\nprint(input(),input())\n")
    finish(run)
    assert stdout(run)=='a b\n' and not any(e['type']=='input' for e in run.events) and run.input_count==2
    return {'inputCallCount':run.input_count,'visibleWaitRequests':0}

def store_protocol():
    store=runtime.Store(source,workspace/'StoreData',args.python.resolve())
    try:
        project=store.dispatch({'action':'project.create','name':'request-id bridge'})['project']['id']
        store.dispatch({'action':'state.patch','patch':{'trusted':True}})
        store.dispatch({'action':'file.write','id':project,'path':'main.py','content':'print(input())\n'})
        run_id=store.dispatch({'action':'run','id':project})['runId']
        run=store.runs[run_id]
        runs.append(run)
        request=waiting(run)
        accepted=store.dispatch({'action':'input','runId':run_id,'requestId':request['inputRequestId'],'text':'桥接输入'})
        finish(run)
        end=store.dispatch({'action':'events','runId':run_id,'cursor':0})
        assert accepted['ok'] and not end['waiting'] and stdout(run)=='桥接输入\n'
        return {'accepted':accepted,'stdout':stdout(run)}
    finally:
        store.close()

def wait_longer_than_old_timeout():
    run=launch("name=input('请慢慢想：')\nprint('收到：'+name)\n")
    request=waiting(run)
    began=time.monotonic()
    time.sleep(31.2)
    before=run.poll(request['cursor'])
    assert before['running'] and before['waiting'] and before['inputRequestId']==request['inputRequestId']
    run.send_input('30秒后仍可输入',request_id=request['inputRequestId'])
    finish(run)
    assert run.process.returncode==0 and stdout(run)=='请慢慢想：收到：30秒后仍可输入\n'
    return {'userWaitSeconds':round(time.monotonic()-began,3),'stdout':stdout(run),'executionSeconds':round(run.active_seconds,3)}

for name,operation in [
 ('production execution/input budgets remain 30/300 seconds',production_limits),
 ('empty line, consecutive Unicode input and cursor-safe waiting snapshots',snapshot_and_empty),
 ('duplicate, stale and multiline requests cannot answer the next prompt',duplicate_and_multiline),
 ('user thinking time is excluded from execution budget',paused_budget),
 ('execution time remains cumulative across input waits',cumulative_budget),
 ('per-input waiting deadline terminates and clears waiting state',wait_deadline),
 ('stop while waiting is responsive and rejects late input',stop_waiting),
 ('EOF ends the exact pending input request',eof),
 ('read/readline size zero never waits and partial lines retain newlines',stream_zero_and_partial),
 ('text stdin read can collect lines until explicit EOF',raw_read_until_eof),
 ('30 rapid consecutive input requests preserve identity and order',many_inputs),
 ('natural process exit cannot leave a phantom waiting request',exit_race),
 ('StringIO input remains noninteractive and counted',redirected_stdin),
 ('Store input API forwards request IDs and authoritative state',store_protocol),
 ('real production input remains usable after 31 seconds',wait_longer_than_old_timeout),
]:
    test(name,operation)

report={'version':runtime.VERSION,'python':str(args.python.resolve()),'runtimeSHA256':{name:hashlib.sha256((source/'runtime'/name).read_bytes()).hexdigest() for name in ['server.py','worker.py']},'testData':str(workspace),'passed':sum(r['passed'] for r in results),'failed':sum(not r['passed'] for r in results),'results':results,'limitations':['No release package was rebuilt; runtime sources run with the selected Python executable recorded above.','The 300-second production input deadline is tested with shortened constructor-only budgets; a genuine >30-second wait is tested separately.','Binary stdin.buffer and sys.__stdin__ reads do not emit text-input waiting events.']}
args.report.parent.mkdir(parents=True,exist_ok=True)
args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
raise SystemExit(bool(report['failed']))
