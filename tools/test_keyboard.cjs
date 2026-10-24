const {chromium}=require('playwright');
const fs=require('node:fs');
const assert=require('node:assert/strict');
(async()=>{let browser;const result={date:'2026-10-20',environment:'Real Microsoft Edge keyboard input to CodeMirror',passed:false};try{
browser=await chromium.launch({channel:'msedge',headless:true});const page=await browser.newPage();await page.goto(process.argv[2]);await page.locator('.chapters').waitFor();await page.locator('[data-action=lesson]').first().click();await page.locator('.cm-content').waitFor();
await page.locator('.cm-content').click();await page.keyboard.press('ControlOrMeta+a');await page.keyboard.insertText('if True:');await page.keyboard.press('Enter');
const entered=await page.evaluate(()=>S.editor.state.doc.toString());assert.equal(entered,'if True:\n    ');
await page.keyboard.press('Tab');const tabbed=await page.evaluate(()=>S.editor.state.doc.toString());assert.equal(tabbed,'if True:\n        ');
await page.keyboard.press('Shift+Tab');const shifted=await page.evaluate(()=>S.editor.state.doc.toString());assert.equal(shifted,'if True:\n    ');
await page.keyboard.insertText('print("四空格缩进")');await page.evaluate(()=>flushSave());const codeBeforeRun=await page.evaluate(()=>S.editor.state.doc.toString());await page.keyboard.press('ControlOrMeta+Enter');if(await page.locator('[data-yes]').isVisible())await page.locator('[data-yes]').click();await page.waitForFunction(()=>document.querySelector('#run-state')?.textContent==='运行完成');assert.match(await page.locator('#console-output').innerText(),/四空格缩进/);assert.equal(await page.evaluate(()=>S.editor.state.doc.toString()),codeBeforeRun);result.enter=entered;result.tab=tabbed;result.shiftTab=shifted;result.ctrlEnterRunsRealPython=true;result.passed=true;console.log('PASS real Enter/Tab/Shift+Tab: 4 spaces; Ctrl+Enter executes actual Python');
}catch(e){result.error=String(e);process.exitCode=1;console.error(e);}finally{fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2));if(browser)await browser.close();}})();
