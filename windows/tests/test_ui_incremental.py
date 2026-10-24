"""Native WebView2 regression checks for ZIP entry selection and async UI races."""
import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import subprocess
import time
import zipfile


def archive(files):
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
        for name,content in files:
            z.writestr(name,content)
    return base64.b64encode(buffer.getvalue()).decode('ascii')


def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=root.parent/'windows/PySlate')
    parser.add_argument('--report',type=Path,default=root/'test-reports/windows-ui-incremental.json')
    args=parser.parse_args()
    package=args.package.resolve()
    report=args.report.resolve()
    report.parent.mkdir(parents=True,exist_ok=True)
    workspace=root/('work/windows-ui-incremental-'+str(time.time_ns()))
    workspace.mkdir(parents=True)
    data=workspace/'Data'
    fixtures={
        'nested-main':archive([('000.bin',b'\x89\xff\x00'),('src/helper.py','def message():\n    return "真实嵌套入口运行成功"\n'),('src/main.py','from helper import message\n# 真实嵌套入口\nprint(message())\n')]),
        'text-only':archive([('000.bin',b'\x89\xff\x00'),('notes.txt','中文资源可正常阅读\n')]),
        'binary-only':archive([('image.png',b'\x89PNG\r\n\x1a\n\x00\xff')]),
    }
    script=workspace/'incremental.js'
    script.write_text(Path(__file__).with_name('ui-incremental.js').read_text('utf-8').replace('__FIXTURES__',json.dumps(fixtures)), 'utf-8')
    capture=report.with_suffix('.png')
    startup=subprocess.STARTUPINFO()
    startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=1
    process=subprocess.Popen([str(package/'PySlate.exe'),'--data',str(data),'--capture',str(capture),'--capture-script',str(script),'--capture-script-wait','6500'],startupinfo=startup)
    try:
        process.wait(timeout=45)
        state=json.loads((data/'catalog.json').read_text('utf-8'))['state']
        results=state.get('windowsUiIncremental',[])
        metadata=json.loads(capture.with_name(capture.name+'.json').read_text('utf-8-sig'))
        log=capture.with_name(capture.name+'.log').read_text('utf-8-sig')
        results.append({'name':'real native viewport and close flush','passed':capture.stat().st_size>10000 and not metadata['overflow'] and not metadata['brokenImages'] and 'close flush confirmed=True' in log,'detail':{'width':metadata['width'],'height':metadata['height'],'capture':capture.name}})
    except Exception as error:
        if process.poll() is None:
            process.kill()
            process.wait()
        results=[{'name':'native regression completes','passed':False,'detail':str(error)}]
    result={'package':str(package),'nativeHostSHA256':hashlib.sha256((package/'PySlate.exe').read_bytes()).hexdigest(),'uiSHA256':hashlib.sha256((package/'web/app.js').read_bytes()).hexdigest(),'testData':str(data),'results':results,'passed':sum(item['passed'] for item in results),'failed':sum(not item['passed'] for item in results)}
    report.write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf-8')
    for item in results:
        print(('PASS' if item['passed'] else 'FAIL')+' '+item['name'],flush=True)
    return 0 if result['passed']==7 and not result['failed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
