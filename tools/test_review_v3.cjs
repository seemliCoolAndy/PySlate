/* Regression checks use a real bridge with isolated data; injected failures are explicit. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
fs.mkdirSync(out,{recursive:true});const results=[],errors=[];
let browser,page;
async function test(name,fn){try{await fn();results.push({name,passed:true});console.log('PASS',name);}catch(e){results.push({name,passed:false,error:e.stack});console.log('FAIL',name,e.message);}}
const setCode=code=>page.evaluate(code=>S.editor.dispatch({changes:{from:0,to:S.editor.state.doc.length,insert:code}}),code);
(async()=>{try{
 browser=await chromium.launch({channel:'msedge',headless:true});page=await browser.newPage({viewport:{width:1280,height:900}});
 page.on('pageerror',e=>errors.push(String(e)));await page.goto(url);await page.locator('.chapters').waitFor();
 await page.evaluate(async()=>{await patchState({trusted:true});const r=await api('project.create',{name:'审查隔离项目'});S.projects.push(r.project);window.reviewProject=r.project.id;await openProject(r.project.id);});
 await test('保存失败不会留下虚假的学习完成状态',async()=>{
  const result=await page.evaluate(async()=>{const original=api,before={...S.state.progress};api=async(action,data)=>{if(action==='state.patch')throw new Error('模拟磁盘写入失败');return original(action,data);};try{await patchState({progress:{...before,l48:true}});}catch{}finally{api=original;}const after={...S.state.progress};S.state.progress=before;return {before,after};});assert.deepEqual(result.after,result.before);
 });
 await test('手机项目文件切回桌面后编辑器可见',async()=>{
  await page.setViewportSize({width:390,height:844});await page.locator('[data-action=mobile-reader]').click();await page.setViewportSize({width:1280,height:900});assert.equal(await page.locator('.coding-pane').isVisible(),true);await page.evaluate(()=>setMobile('code'));
 });
 await test('停止成功后延迟事件不会复活运行状态',async()=>{
  const result=await page.evaluate(async()=>{const original=api;let release;const run={id:'injected-run',cursor:0,running:true,waiting:false,output:[],status:'运行中',stateRevision:1};S.run=run;api=async(action,data)=>action==='events'?new Promise(r=>{release=r;}):action==='stop'?{ok:true}:original(action,data);const polling=pollRun(run);await stopRun();release({running:true,waiting:true,inputRequestId:1,stateRevision:1,cursor:1,events:[{seq:1,type:'input',requestId:1}]});await polling;const state={running:run.running,waiting:run.waiting,status:run.status,enabled:!document.querySelector('#stdin').disabled};S.run=null;api=original;updateRunButtons(false);return state;});assert.deepEqual(result,{running:false,waiting:false,status:'已停止',enabled:false});
 });
 await test('新建文件不能通过大小写别名覆盖现有代码',async()=>{
  await setCode('print("必须保留的代码")\n');await page.evaluate(()=>flushSave());await page.locator('[data-action=new-file]').click();await page.locator('#dialog input').fill('MAIN.py');await page.locator('#dialog button[type=submit]').click();await page.waitForFunction(()=>!document.querySelector('#dialog').open);await page.waitForTimeout(300);const actual=await page.evaluate(async()=>(await api('file.read',{id:window.reviewProject,path:'main.py'})).content);assert.equal(actual,'print("必须保留的代码")\n');
 });
 await test('完成标记双击按顺序切换，取消后仍显示未完成',async()=>{
  await page.evaluate(()=>openLesson('l01','beginner'));
  const result=await page.evaluate(async()=>{await patchState({progress:{}});await Promise.all([actions.complete(),actions.complete()]);return {state:S.state.progress.l01,stored:(await api('bootstrap')).state.progress.l01};});assert.deepEqual(result,{state:false,stored:false});
 });
 await test('文件重命名提交期间冻结编辑，避免旧路径被自动保存复活',async()=>{
  await page.setViewportSize({width:390,height:844});await page.evaluate(()=>openProject(window.reviewProject));await setCode('print("重命名保留")\n');await page.evaluate(()=>flushSave());
  await page.locator('[data-action=file-menu]').click();await page.locator('[data-rename]').click();await page.locator('#dialog input').fill('renamed.py');
  await page.evaluate(()=>{const original=api;window.renameGate={original};api=async(action,data)=>{const result=await original(action,data);if(action==='file.rename')return new Promise(resolve=>{window.renameGate.release=()=>resolve(result);});return result;};});
  await page.locator('#dialog button[type=submit]').click();await page.waitForFunction(()=>window.renameGate.release);assert.equal(await page.locator('.cm-content').getAttribute('contenteditable'),'false');assert.equal(await page.locator('[data-action=insert][data-text=":"]').isDisabled(),true);await page.evaluate(()=>actions.insert(document.querySelector('[data-action=insert][data-text=":"]')));await page.locator('.cm-content').click();await page.keyboard.type('unexpected');
  await page.evaluate(()=>{window.renameGate.release();api=window.renameGate.original;});await page.waitForFunction(()=>S.path==='renamed.py');await page.evaluate(()=>flushSave());
  const r=await page.evaluate(async()=>({files:(await api('project.files',{id:window.reviewProject})).files.map(x=>x.path),content:(await api('file.read',{id:window.reviewProject,path:'renamed.py'})).content}));assert.deepEqual(r.files,['renamed.py']);assert.equal(r.content,'print("重命名保留")\n');assert.equal(await page.locator('.cm-content').getAttribute('contenteditable'),'true');
 });
 await test('载入答案途中切项目按顺序完成，不污染项目代码',async()=>{
  await page.evaluate(()=>openLesson('l29','intermediate'));
  await page.evaluate(()=>{const original=api;window.loadGate={original};api=async(action,data)=>{if(action==='state.patch'&&data.patch?.lessonSources)return new Promise(resolve=>{window.loadGate.release=async()=>resolve(await original(action,data));});return original(action,data);};window.loadGate.loading=loadLessonCode(true);});
  await page.waitForFunction(()=>window.loadGate.release);await page.evaluate(()=>{window.loadGate.navigation=openProject(window.reviewProject);});assert.equal(await page.evaluate(()=>S.view),'lesson');assert.equal(await page.evaluate(()=>S.editorLocked),true);
  await page.evaluate(async()=>{await window.loadGate.release();await window.loadGate.loading;await window.loadGate.navigation;api=window.loadGate.original;});assert.equal(await page.evaluate(()=>S.view),'project');assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("重命名保留")\n');
  await page.evaluate(()=>openLesson('l29','intermediate'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()===lessonCode(learningUnit(),true)),true);assert.equal(await page.evaluate(()=>lessonSource()),'solution');
 });
 await test('载入答案写入失败时来源和草稿共同保留',async()=>{
  await page.evaluate(()=>openLesson('l29','advanced'));const r=await page.evaluate(async()=>{const before={text:S.editor.state.doc.toString(),source:lessonSource()},original=api;api=async(action,data)=>{if(action==='state.patch'&&data.patch?.lessonSources)throw new Error('模拟来源草稿写入失败');return original(action,data);};let rejected=false;try{await loadLessonCode(true);}catch{rejected=true;}finally{api=original;}return {before,after:{text:S.editor.state.doc.toString(),source:lessonSource()},locked:!!S.editorLocked,rejected};});assert.deepEqual(r.before,r.after);assert.equal(r.locked,false);assert.equal(r.rejected,true);
 });
 }catch(e){errors.push(e.stack);}
 finally{const passed=results.length===8&&results.every(r=>r.passed)&&!errors.length;fs.writeFileSync(path.join(out,'review-v3.json'),JSON.stringify({results,errors,passed},null,2));if(browser)await browser.close();if(!passed)process.exitCode=1;}
})();
