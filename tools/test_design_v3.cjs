/* Visual and accessibility checks on the real local app, without user data. */
const {chromium}=require('playwright');
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const url=process.argv[2],out=path.resolve(process.argv[3]);fs.mkdirSync(out,{recursive:true});
const results=[],errors=[];let browser,page;
async function test(name,fn){try{await fn();results.push({name,passed:true});console.log('PASS',name);}catch(e){results.push({name,passed:false,error:e.stack});throw e;}}
async function noOverflow(){assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);}
async function shot(name){await page.waitForTimeout(180);await page.screenshot({path:path.join(out,name+'.png')});}
(async()=>{try{
 browser=await chromium.launch({channel:'msedge',headless:true});page=await browser.newPage({viewport:{width:1360,height:900},reducedMotion:'reduce'});page.on('pageerror',e=>errors.push(String(e)));await page.goto(url);await page.locator('.chapters').waitFor();
 await test('目录搜索匹配主题和各层知识点，清空恢复58主题',async()=>{
  assert.equal(await page.locator('.lesson-row').count(),58);await page.locator('#course-search').fill('文件');assert.ok(await page.locator('.lesson-row').count()>0);assert.ok(await page.locator('.lesson-row').count()<58);await page.locator('#course-search').fill('不存在的独特词xyz');assert.equal(await page.locator('.catalog-empty').count(),1);await page.locator('[data-action=clear-course-search]').click();assert.equal(await page.locator('.lesson-row').count(),58);await shot('catalog-desktop-light');
 });
 await test('浅深主题关键文字对比度与背景同步',async()=>{
  for(const theme of ['dark','light']){await page.evaluate(async theme=>{await patchState({theme});renderCatalog();},theme);await noOverflow();await shot('catalog-desktop-'+theme);const ratios=await page.evaluate(()=>{const lum=rgb=>{const c=rgb.match(/[\d.]+/g).slice(0,3).map(x=>+x/255).map(x=>x<=.04045?x/12.92:((x+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2];};return ['.nav-item.active','.study-hero .primary','.chapter-title h3','.catalog-heading p'].map(s=>{const el=document.querySelector(s),fg=getComputedStyle(el).color;let parent=el,bg;while(parent){bg=getComputedStyle(parent).backgroundColor;if(!bg.endsWith(', 0)')&&bg!=='transparent')break;parent=parent.parentElement;}const a=lum(fg),b=lum(bg);return {s,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};});});for(const r of ratios)assert.ok(r.ratio>=4.5,`${theme} ${r.s} contrast ${r.ratio}`);}
 });
 await test('390及320像素目录、课程和代码无横向溢出',async()=>{
  for(const width of [390,320]){await page.setViewportSize({width,height:844});await page.evaluate(()=>navigate('study'));await noOverflow();await shot('catalog-phone-'+width);await page.evaluate(()=>openLesson('l20','advanced'));await noOverflow();await shot('lesson-phone-'+width);await page.locator('[data-action=mobile-code]').click();await noOverflow();await shot('code-phone-'+width);}
 });
 await test('手机项目文件页旋转到平板恢复双栏',async()=>{
  await page.evaluate(async()=>{const {project}=await api('project.create',{name:'视觉验收用项目'});S.projects.push(project);await openProject(project.id);});await page.locator('[data-action=mobile-reader]').click();assert.equal(await page.locator('.files-pane').isVisible(),true);assert.equal(await page.locator('.coding-pane').isVisible(),false);await page.setViewportSize({width:1024,height:768});assert.equal(await page.locator('.coding-pane').isVisible(),true);await noOverflow();await shot('project-tablet');
 });
 await test('深色资料库背景无浅色残留，文件按钮可读',async()=>{
  await page.setViewportSize({width:1360,height:900});await page.evaluate(async()=>{await patchState({theme:'dark'});await navigate('library');});await shot('library-desktop-dark');assert.equal(await page.locator('.new-notebook').evaluate(e=>getComputedStyle(e).backgroundColor),'rgb(30, 44, 37)');
 });
 assert.deepEqual(errors,[]);
 }catch(e){errors.push(String(e.stack));if(page)await page.screenshot({path:path.join(out,'design-failure.png')});process.exitCode=1;}
 finally{fs.writeFileSync(path.join(out,'design-v3.json'),JSON.stringify({results,errors,passed:results.length===5&&results.every(r=>r.passed)&&!errors.length},null,2));if(browser)await browser.close();}
})();
