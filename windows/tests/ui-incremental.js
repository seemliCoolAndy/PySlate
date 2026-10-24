/* Executed by test_ui_incremental.py inside the real packaged WebView2. */
(async function () {
  const fixtures = __FIXTURES__;
  const proof = [];
  const originalApi = api;
  const check = (name, condition, detail) => {
    proof.push({name, passed: !!condition, detail});
    if (!condition) throw new Error(name + ': ' + JSON.stringify(detail));
  };
  const importFixture = async (name) => {
    const bytes = Uint8Array.from(atob(fixtures[name]), c => c.charCodeAt(0));
    const imported = importProject(new File([bytes], name + '.zip', {type:'application/zip'}));
    document.querySelector('#dialog [data-yes]').click();
    await imported;
    return S.project;
  };
  try {
    await patchState({trusted:true});
    await importFixture('nested-main');
    check('ZIP import prefers a nested main.py over the first binary asset', S.path === 'src/main.py' && S.editor.state.doc.toString().includes('真实嵌套入口'), {path:S.path});
    await runCode();
    for (let i=0; i<40 && S.run?.running; i++) await new Promise(resolve=>setTimeout(resolve,50));
    check('imported nested entry executes with its sibling helper', !S.run?.running && document.querySelector('#console-output').textContent.includes('真实嵌套入口运行成功'), document.querySelector('#console-output').textContent);

    await importFixture('text-only');
    check('text-only ZIP opens valid UTF-8 content after skipping binary data', S.editor && S.editor.state.doc.toString() === '中文资源可正常阅读\n', {path:S.path,content:S.editor?.state.doc.toString()});

    await importFixture('binary-only');
    check('binary-only ZIP remains accessible without decoding it as text', S.project && S.files.some(file=>file.path==='image.png') && !S.path && (!S.editor || S.editor.contentDOM.contentEditable==='false'), {path:S.path,files:S.files.map(file=>file.path),editorEditable:S.editor?.contentDOM.contentEditable});

    const {project}=await api('project.create',{name:'UI 保存与事件回归',color:'#3c6955',category:'验收'});
    S.projects.push(project);
    await openProject(project.id);
    const output=document.querySelector('#console-output');
    output.textContent='当前控制台';
    let releaseEvents;
    api=(action,data={})=>action==='events'?new Promise(resolve=>{releaseEvents=resolve;}):originalApi(action,data);
    const oldRun={id:'old-controlled-event',cursor:0,running:true};
    S.run=oldRun;
    const oldPoll=pollRun(oldRun);
    const currentRun={id:'new-current-event',cursor:0,running:false};
    S.run=currentRun;
    releaseEvents({events:[{seq:1,type:'stdout',text:'STALE_EVENT_MUST_NOT_APPEAR'}],cursor:1,running:false});
    await oldPoll;
    api=originalApi;
    check('an old events response cannot alter the new run console', S.run===currentRun && output.textContent==='当前控制台', {text:output.textContent,runId:S.run.id});
    S.run=null;

    let releaseFailure;
    const oldText='print("older pending save")\n';
    const newText='print("最新修订已持久保存")\n';
    api=(action,data={})=>action==='file.write'&&data.content===oldText?new Promise((resolve,reject)=>{releaseFailure=reject;}):originalApi(action,data);
    S.editor.dispatch({changes:{from:0,to:S.editor.state.doc.length,insert:oldText}});
    clearTimeout(S.timer);
    const oldSave=flushSave().catch(()=>{});
    for(let i=0;i<20&&!releaseFailure;i++)await new Promise(resolve=>setTimeout(resolve,10));
    if(!releaseFailure)throw new Error('save failure fixture was not reached');
    S.editor.dispatch({changes:{from:0,to:S.editor.state.doc.length,insert:newText}});
    clearTimeout(S.timer);
    const newSave=flushSave();
    releaseFailure(new Error('controlled earlier save failure'));
    await oldSave;
    await newSave;
    api=originalApi;
    await flushSave();
    const saved=await api('file.read',{id:project.id,path:'main.py'});
    check('a failed older save cannot restore stale text over the latest revision', saved.content===newText && S.editor.state.doc.toString()===newText && !S.pending, {saved:saved.content,pending:S.pending});
  } catch(error) {
    proof.push({name:'incremental test completes',passed:false,detail:String(error.stack||error)});
  } finally {
    api=originalApi;
    await patchState({windowsUiIncremental:proof});
  }
})();
