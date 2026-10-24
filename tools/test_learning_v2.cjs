/* Actual UI + real CPython bridge; only this harness's disposable project data. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);
fs.mkdirSync(out,{recursive:true});const results=[],errors=[];
let browser,page;
async function test(name,fn){const start=Date.now();try{await fn();results.push({name,passed:true,ms:Date.now()-start});console.log('PASS',name);}catch(e){results.push({name,passed:false,error:e.stack});throw e;}}
const waitInput=()=>page.waitForFunction(()=>!document.querySelector('#stdin').disabled&&document.querySelector('#run-state').textContent.startsWith('等待输入'));
const setCode=code=>page.evaluate(code=>{S.editor.dispatch({changes:{from:0,to:S.editor.state.doc.length,insert:code}});},code);
async function run(code){await setCode(code);await page.locator('#run-button').click();}
async function send(text){await waitInput();await page.locator('#stdin').fill(text);await page.locator('#stdin').press('Enter');}
(async()=>{try{
 browser=await chromium.launch({channel:'msedge',headless:true});page=await browser.newPage({viewport:{width:1200,height:820}});page.on('pageerror',e=>errors.push(String(e)));await page.goto(url);await page.locator('.chapters').waitFor();
 await test('v1练习与完成标记继续属于初级',async()=>{
  await page.evaluate(async()=>{await patchState({trusted:true,drafts:{l01:'print("v1保留")\n'},progress:{l01:true}});await openLesson('l01','beginner');});
  assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("v1保留")\n');assert.match(await page.locator('[data-action=complete]').innerText(),/已完成/);
 });
 await test('174单元都有独立内容与图，难度不是代码换名',async()=>{
  const data=await page.evaluate(()=>S.lessonList.map(l=>({id:l.id,tiers:(l.tiers||[]).map(t=>({id:t.id,body:t.body,code:t.code,solution:t.solution,exercise:t.exercise,image:t.diagram}))})));
  assert.equal(data.length,58);for(const l of data){assert.deepEqual(l.tiers.map(t=>t.id),['beginner','intermediate','advanced']);assert.equal(new Set(l.tiers.map(t=>t.code)).size,3,l.id+' examples');assert.equal(new Set(l.tiers.map(t=>t.solution)).size,3,l.id+' answers');for(const t of l.tiers){assert.ok(t.body.length>=150,l.id+'/'+t.id);assert.ok(t.exercise.trim(),l.id+'/'+t.id);assert.equal(t.image,`course-assets/tier-${l.id}-${t.id}.webp`);}}
 });
 await test('初中高代码与进度隔离，重载保留选中层级',async()=>{
  await page.evaluate(()=>switchTier('intermediate'));await setCode('print("中级草稿")\n');await page.locator('[data-action=complete]').click();await page.evaluate(()=>switchTier('advanced'));await setCode('print("高级草稿")\n');await page.evaluate(()=>switchTier('beginner'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("v1保留")\n');
  await page.evaluate(()=>switchTier('intermediate'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("中级草稿")\n');assert.match(await page.locator('[data-action=complete]').innerText(),/已完成/);await page.evaluate(()=>switchTier('advanced'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("高级草稿")\n');assert.doesNotMatch(await page.locator('[data-action=complete]').innerText(),/取消/);await page.evaluate(()=>flushSave());await page.reload();await page.locator('.chapters').waitFor();await page.evaluate(()=>openLesson('l01'));assert.equal(await page.evaluate(()=>S.tier),'advanced');assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("高级草稿")\n');
 });
 await test('快速切换按序保存，不丢最后编辑',async()=>{
  await setCode('print("最后高级编辑")\n');await page.evaluate(()=>Promise.all([switchTier('beginner'),switchTier('intermediate')]));assert.equal(await page.evaluate(()=>S.tier),'intermediate');assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("中级草稿")\n');await page.evaluate(()=>switchTier('advanced'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("最后高级编辑")\n');
 });
 await test('切级或跨课保存尚未返回时，旧编辑仍写入旧层级',async()=>{
  for(const destination of [{topic:'l01',tier:'beginner'},{topic:'l02',tier:'intermediate'}]){
   await page.evaluate(()=>openLesson('l01','advanced'));await setCode('print("切换前")\n');await page.evaluate(destination=>{const original=api;window.levelSaveGate={original,release:null};api=async(action,data)=>{if(action==='state.patch'&&data.patch?.lessonTiers&&!window.levelSaveGate.release)return new Promise(resolve=>{window.levelSaveGate.release=async()=>resolve(await original(action,data));});return original(action,data);};window.levelSaveGate.navigation=destination.topic==='l01'?switchTier(destination.tier):openLesson(destination.topic,destination.tier);},destination);
   await page.waitForFunction(()=>window.levelSaveGate.release);await setCode('print("切换途中仍属高级")\n');await page.evaluate(async()=>{await window.levelSaveGate.release();await window.levelSaveGate.navigation;api=window.levelSaveGate.original;});assert.equal(await page.evaluate(()=>S.tier),destination.tier);assert.notEqual(await page.evaluate(()=>S.editor.state.doc.toString()),'print("切换途中仍属高级")\n');await page.evaluate(()=>openLesson('l01','advanced'));assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),'print("切换途中仍属高级")\n');
  }
 });
 await test('超过原30秒仍可输入中文',async()=>{
  await run('name=input("请慢慢输入：")\nprint("收到="+name)\n');await waitInput();await page.waitForTimeout(31200);assert.equal(await page.locator('#stdin').isEnabled(),true);await send('中文正常');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/收到=中文正常/);
 });
 await test('空行和连续三次input各消费一行',async()=>{
  await run('a=input("一：")\nb=input("二：")\nc=input("三：")\nprint(repr((a,b,c)))\n');await send('');await send('第二');await send('third');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/\('', '第二', 'third'\)/);
 });
 await test('输入法确认候选时不提前发送',async()=>{
  await run('print("值="+input("输入："))\n');await waitInput();await page.locator('#stdin').dispatchEvent('compositionstart');await page.locator('#stdin').fill('拼音候选');await page.locator('#stdin').dispatchEvent('keydown',{key:'Enter',code:'Enter',isComposing:true,bubbles:true});await page.locator('#stdin-form').dispatchEvent('submit');assert.equal(await page.evaluate(()=>S.run.waiting),true);await page.locator('#stdin').dispatchEvent('compositionend');await send('中文已确认');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/值=中文已确认/);
 });
 await test('双击只消费一行，不污染下次input',async()=>{
  await run('a=input("一：")\nb=input("二：")\nprint(a+"|"+b)\n');await waitInput();await page.locator('#stdin').fill('first');await page.evaluate(()=>Promise.all([sendInput(),sendInput()]));await waitInput();assert.equal(await page.locator('#stdin').inputValue(),'');await send('second');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/first\|second/);
 });
 await test('提交后的旧等待快照不会重新开启已消费请求',async()=>{
  await run('a=input("一：")\nb=input("二：")\nprint(a+"|"+b)\n');await waitInput();
  await page.evaluate(()=>{const original=api;window.inputSnapshotGate={captured:false,release:null,original};api=async(action,data)=>{const response=await original(action,data);if(action==='events'&&!window.inputSnapshotGate.captured){window.inputSnapshotGate.captured=true;return new Promise(resolve=>{window.inputSnapshotGate.release=()=>resolve(response);});}return response;};});
  await page.waitForFunction(()=>window.inputSnapshotGate?.release);await page.locator('#stdin').fill('first');await page.locator('#stdin').press('Enter');await page.waitForFunction(()=>S.run.lastSubmittedRequestId===1);
  await page.evaluate(()=>{window.inputSnapshotGate.release();api=window.inputSnapshotGate.original;});await page.waitForTimeout(30);assert.equal(await page.locator('#stdin').isDisabled(),true);await send('second');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/first\|second/);
 });
 await test('换项目文件后待输入和未发文字仍可使用',async()=>{
  await page.evaluate(async()=>{const {project}=await api('project.create',{name:'输入回归隔离项目'});S.projects.push(project);await api('file.write',{id:project.id,path:'other.py',content:'# 另一个文件\n'});await openProject(project.id);});await run('print("之前输出")\na=input("请输入：")\nprint("之后="+a)\n');await waitInput();await page.locator('#stdin').fill('暂存文字');await page.evaluate(()=>switchFile('other.py'));assert.match(await page.locator('#console-output').innerText(),/之前输出/);assert.equal(await page.locator('#stdin').inputValue(),'暂存文字');assert.equal(await page.locator('#stdin').isEnabled(),true);await page.locator('#stdin').press('Enter');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/之后=暂存文字/);await page.screenshot({path:path.join(out,'file-switch-input.png')});
 });
 await test('手机键盘高度下输入框与发送按钮可见',async()=>{
  await page.setViewportSize({width:390,height:470});await run('print(input("手机输入："))\n');await waitInput();const r=await page.locator('#stdin').boundingBox(),b=await page.locator('#send-input').boundingBox();assert.ok(r.y>=0&&r.y+r.height<=470);assert.ok(b.y+b.height<=470);assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.screenshot({path:path.join(out,'phone-keyboard-height.png')});await send('phone');await page.waitForFunction(()=>document.querySelector('#run-state').textContent==='运行完成');
 });
 assert.deepEqual(errors,[]);
 }catch(e){console.error(e.stack);process.exitCode=1;if(page)await page.screenshot({path:path.join(out,'learning-v2-failure.png')}).catch(()=>{});}
 finally{fs.writeFileSync(path.join(out,'learning-v2.json'),JSON.stringify({results,errors,passed:results.length===12&&results.every(r=>r.passed)},null,2));if(browser)await browser.close();}
})();
