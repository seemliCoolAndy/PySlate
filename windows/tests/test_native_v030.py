"""Attach the shared UI learning regression suite to the real WebView2 host."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import socket
import subprocess
import time
import urllib.request


def main():
    root=Path(__file__).resolve().parents[2]
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path,default=root.parent/'windows/PySlate')
    parser.add_argument('--report',type=Path,default=root/'test-reports/windows-native-v030')
    parser.add_argument('--node-modules',type=Path,default=root/'node_modules')
    parser.add_argument('--prepare-only',action='store_true',help='Generate and syntax-check native harness without launching the app')
    args=parser.parse_args()
    package=args.package.resolve()
    output=args.report.resolve()
    output.mkdir(parents=True,exist_ok=True)
    work=root/('work/native-v030-'+str(time.time_ns()))
    work.mkdir(parents=True)
    with socket.socket() as sock:
        sock.bind(('127.0.0.1',0))
        port=sock.getsockname()[1]
    environment=dict(os.environ)
    # Debugging is scoped to this disposable test child, never the installer or normal launch.
    environment['WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS']=f'--remote-debugging-port={port} --remote-debugging-address=127.0.0.1'
    modules=args.node_modules.resolve()
    environment['NODE_PATH']=os.pathsep.join(filter(None,(str(modules),os.environ.get('NODE_PATH',''))))
    source=root/'tools/test_learning_v2.cjs'
    script=source.read_text('utf-8')
    original="browser=await chromium.launch({channel:'msedge',headless:true});page=await browser.newPage({viewport:{width:1200,height:820}});"
    replacement=f"browser=await chromium.connectOverCDP('http://127.0.0.1:{port}');page=browser.contexts()[0].pages().find(p=>p.url().includes('/index.html'));if(!page)throw new Error('native page missing');await page.setViewportSize({{width:1200,height:820}});"
    if original not in script: raise RuntimeError('Shared harness launch signature changed; adapt explicitly.')
    script=script.replace(original,replacement)
    # Include a real hardware-keyboard event check on the final application capture handler.
    insertion='''
 await test('原生CtrlEnter运行且不改动源码',async()=>{
  await page.evaluate(()=>openLesson('l01','advanced'));
  await setCode('print("原生快捷键正确")\\n');
  const before=await page.evaluate(()=>S.editor.state.doc.toString());
  await page.locator('.cm-content').focus();await page.keyboard.press('Control+Enter');
  await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');
  assert.match(await page.locator('#console-output').innerText(),/原生快捷键正确/);
  assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),before);
  await page.screenshot({path:path.join(out,'native-ctrl-enter.png')});
 });
'''
    script=script.replace(" await test('超过原30秒仍可输入中文'",insertion+" await test('超过原30秒仍可输入中文'",1)
    count=re.search(r'results\.length===(\d+)',script)
    if not count: raise RuntimeError('Shared harness expected count not found')
    script=re.sub(r'results\.length===\d+',f'results.length==={int(count.group(1))+1}',script)
    # Preserve a direct DOM snapshot before CDP disconnect. The earlier native
    # run returned null from the host's later ExecuteScriptAsync snapshot.
    script=script.replace(' assert.deepEqual(errors,[]);','''

 const imageDecodes=await page.evaluate(async()=>{
  const paths=S.lessonList.flatMap(l=>(l.tiers||[]).map(t=>t.diagram)),results=[];
  for(const src of paths){const img=new Image();img.src=src;try{await img.decode();results.push({src,passed:img.naturalWidth>=512&&img.naturalHeight>=512,width:img.naturalWidth,height:img.naturalHeight});}catch(error){results.push({src,passed:false,error:String(error)});}finally{img.src='';}}
  return results;
 });
 fs.writeFileSync(path.join(out,'native-image-decode.json'),JSON.stringify(imageDecodes,null,2));
 assert.equal(imageDecodes.length,174);assert.equal(imageDecodes.filter(r=>!r.passed).length,0);
 await page.setViewportSize({width:1200,height:820});
 const nativeDom=await page.evaluate(()=>({title:document.title,width:innerWidth,height:innerHeight,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:[...document.images].filter(i=>i.complete&&!i.naturalWidth).map(i=>i.getAttribute('src'))}));
 fs.writeFileSync(path.join(out,'native-dom.json'),JSON.stringify(nativeDom,null,2));
 await page.screenshot({path:path.join(out,'native-desktop-final.png')});
 assert.equal(nativeDom.overflow,false);assert.deepEqual(nativeDom.brokenImages,[]);
 assert.deepEqual(errors,[]);''')
    harness=work/'native-learning-v2.cjs'
    harness.write_text(script,'utf-8')
    subprocess.run(['node','--check',str(harness)],env=environment,check=True)
    if args.prepare_only: return 0
    startup=subprocess.STARTUPINFO()
    startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow=1
    capture=output/'native-close.png'
    process=subprocess.Popen([str(package/'PySlate.exe'),'--data',str(work/'Data'),'--capture',str(capture),'--capture-delay','85000'],startupinfo=startup,env=environment)
    try:
        endpoint=f'http://127.0.0.1:{port}/json'
        target=None
        for _ in range(120):
            try:
                with urllib.request.urlopen(endpoint,timeout=1) as response:
                    targets=json.load(response)
                target=next((item for item in targets if item['type']=='page' and '/index.html' in item['url']),None)
                if target: break
            except OSError: pass
            time.sleep(.1)
        if not target: raise RuntimeError('Native WebView2 debugging page did not become ready')
        result=subprocess.run(['node',str(harness),target['url'],str(output)],env=environment,timeout=90)
        process.wait(timeout=80)
        report=json.loads((output/'learning-v2.json').read_text('utf-8'))
        host_metadata=json.loads(capture.with_name(capture.name+'.json').read_text('utf-8-sig'))
        metadata=host_metadata or json.loads((output/'native-dom.json').read_text('utf-8'))
        log=capture.with_name(capture.name+'.log').read_text('utf-8-sig')
        image_decodes=json.loads((output/'native-image-decode.json').read_text('utf-8'))
        report['native']={'host':'actual WinForms/WebView2 application; CDP attach, no Edge launch','package':str(package),'data':str(work/'Data'),'version':subprocess.check_output([str(package/'python/python.exe'),'-V'],text=True).strip(),'hashes':{relative:hashlib.sha256((package/relative).read_bytes()).hexdigest() for relative in ['PySlate.exe','web/app.js','web/vendor.js','runtime/server.py','runtime/worker.py','course/course.json']},'harnessSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'driverSHA256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'imagesDecoded':len(image_decodes),'imageDecodeFailures':[item for item in image_decodes if not item['passed']],'captureMetadata':metadata,'captureMetadataSource':'host ExecuteScriptAsync' if host_metadata else 'CDP actual DOM before disconnect','hostCaptureMetadata':host_metadata,'closeFlushConfirmed':'close flush confirmed=True' in log}
        report['passed']=bool(report['passed'] and result.returncode==0 and report['native']['closeFlushConfirmed'] and capture.stat().st_size>10000 and not metadata['overflow'] and not metadata['brokenImages'] and len(image_decodes)==174 and all(item['passed'] for item in image_decodes))
        (output/'windows-native-v030.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf-8')
        return 0 if report['passed'] else 1
    finally:
        if process.poll() is None:
            process.kill()
            process.wait()


if __name__=='__main__':
    raise SystemExit(main())
