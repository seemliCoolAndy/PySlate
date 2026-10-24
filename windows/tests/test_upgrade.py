"""Upgrade previous EXE installation to the current version inside disposable workspace only."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time
import urllib.request


def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--old-installer',type=Path,required=True)
    parser.add_argument('--new-installer',type=Path,required=True)
    parser.add_argument('--old-version',default='0.2.0')
    parser.add_argument('--new-version',default='0.3.0')
    parser.add_argument('--report',type=Path,default=root/'test-reports/windows-upgrade-v030.json')
    args=parser.parse_args()
    workspace=root/('work/windows-upgrade-'+str(time.time_ns()))
    workspace.mkdir(parents=True)
    target,data=workspace/'Application',workspace/'UserData'
    results=[]
    service=None
    endpoint=None

    def check(name,condition,detail=None):
        results.append({'name':name,'passed':bool(condition),'detail':detail})
        print(('PASS ' if condition else 'FAIL ')+name,flush=True)
        if not condition: raise AssertionError(name)

    def install(installer):
        return subprocess.run([str(installer.resolve()),'--silent','--target',str(target),'--no-shortcuts','--portable-test','--accept-webview2-license','--report',str(workspace/'install-error.txt')],timeout=180).returncode

    def start():
        nonlocal service,endpoint
        service=subprocess.Popen([str(target/'python/python.exe'),'-X','utf8','-u',str(target/'runtime/server.py'),'--root',str(target),'--data',str(data)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,encoding='utf-8')
        hello=json.loads(service.stdout.readline())
        endpoint=hello['url'].rsplit('/',1)[0]+'/api'

    def stop():
        nonlocal service
        if service:
            service.kill()
            service.wait(timeout=10)
            service=None

    def api(action,**fields):
        request=urllib.request.Request(endpoint,json.dumps({'action':action,**fields},ensure_ascii=False).encode('utf-8'),{'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=10) as response: return json.load(response)

    try:
        check('actual '+args.old_version+' setup installs to isolated workspace',install(args.old_installer)==0 and (target/'pyslate.install').read_text()=='PySlate '+'.'.join(args.old_version.split('.')[:2]))
        start()
        before=api('bootstrap')
        project=api('project.create',name='升级保留中文项目')['project']
        project_id=project['id']
        fixture='print("升级后真实执行成功")\n'
        api('file.write',id=project_id,path='main.py',content=fixture)
        api('file.write',id=project_id,path='资源/笔记.txt',content='旧版中文资源完整保留\n')
        api('state.patch',patch={'trusted':True,'drafts':{'l01':'print("旧版初级草稿")\n'},'progress':{'l01':True},'practiceIds':{'l01':project_id}})
        check('old application creates real project and beginner records',before['version']==args.old_version and api('file.read',id=project_id,path='main.py')['content']==fixture)
        stop()
        (target/'unlisted-user-note.txt').write_text('keep this unlisted installation-folder file','utf-8')
        check('actual '+args.new_version+' setup accepts existing '+args.old_version+' marker',install(args.new_installer)==0 and (target/'pyslate.install').read_text()=='PySlate '+'.'.join(args.new_version.split('.')[:2]))
        check('upgrade preserves unlisted user file', (target/'unlisted-user-note.txt').read_text('utf-8')=='keep this unlisted installation-folder file')
        start()
        after=api('bootstrap')
        check('upgraded real backend reports '+args.new_version+' and retains project',after['version']==args.new_version and any(row['id']==project_id for row in after['projects']))
        state=after['state']
        check('old beginner drafts progress and practice identity retained',state['drafts']['l01']=='print("旧版初级草稿")\n' and state['progress']['l01'] is True and state['practiceIds']['l01']==project_id)
        check('UTF-8 project code and nested Chinese resource unchanged',api('file.read',id=project_id,path='main.py')['content']==fixture and api('file.read',id=project_id,path='资源/笔记.txt')['content']=='旧版中文资源完整保留\n')
        run=api('run',id=project_id,entry='main.py')
        cursor=0
        events=[]
        deadline=time.monotonic()+10
        while time.monotonic()<deadline:
            response=api('events',runId=run['runId'],cursor=cursor)
            events.extend(response['events'])
            cursor=response['cursor']
            if not response['running']: break
            time.sleep(.05)
        output=''.join(event.get('text','') for event in events if event['type']=='stdout')
        check('upgraded installed embedded Python executes preserved code',output.replace('\r\n','\n')=='升级后真实执行成功\n' and any(event['type']=='exit' and event.get('code')==0 for event in events),output)
        stop()
        result=subprocess.run([str(target/'Uninstall.exe'),'--silent','--portable-test'],timeout=15)
        deadline=time.monotonic()+30
        while (target/'install-manifest.txt').exists() and time.monotonic()<deadline: time.sleep(.1)
        check('upgraded uninstaller preserves independent user data and unlisted file',not (target/'PySlate.exe').exists() and (data/'projects'/project_id/'main.py').read_text('utf-8')==fixture and (target/'unlisted-user-note.txt').exists())
    except Exception as error:
        results.append({'name':'upgrade suite completes','passed':False,'detail':repr(error)})
    finally:
        stop()
        report={'scope':'actual '+args.old_version+' → '+args.new_version+' installers; workspace target, no shortcuts or HKCU registration','workspace':str(workspace),'installers':{str(path.resolve()):hashlib.sha256(path.read_bytes()).hexdigest() for path in (args.old_installer,args.new_installer)},'results':results,'passed':sum(row['passed'] for row in results),'failed':sum(not row['passed'] for row in results)}
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
    return 1 if report['failed'] else 0


if __name__=='__main__':
    raise SystemExit(main())
