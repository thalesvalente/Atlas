/** Real-browser gate for the isolated synthetic harness; never installs tooling. */
import assert from 'node:assert/strict';
import {existsSync, mkdirSync, writeFileSync} from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const output = process.argv[2] ? path.resolve(process.argv[2]) : null;
const report = {scope:'P03_ISOLATED_SYNTHETIC_BROWSER', status:'NOT_RUN', checks:[], errors:[], external_requests:null};
let browser, server;
function finish() {
  const encoded = JSON.stringify(report,null,2)+'\n';
  if (output) { mkdirSync(path.dirname(output),{recursive:true}); writeFileSync(output,encoded); }
  process.stdout.write(encoded);
}
async function main() {
  let playwright;
  try { playwright = require('playwright'); }
  catch {
    const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
    if (modules) { try { playwright = require(path.join(modules,'playwright')); } catch {} }
  }
  if (!playwright) { report.reason='PLAYWRIGHT_NOT_AVAILABLE'; return 2; }
  const executable = process.env.P03_BROWSER_EXECUTABLE || playwright.chromium.executablePath();
  if (!existsSync(executable)) { report.reason='CHROMIUM_EXECUTABLE_NOT_AVAILABLE'; return 2; }
  try {
    // No extra launch flags, downloads, or sandbox/network reconfiguration.
    browser = await playwright.chromium.launch({headless:true, executablePath:executable, chromiumSandbox:true});
    report.browser_version = browser.version();
    server = spawn(process.env.P03_PYTHON || 'python', [path.join(root,'scripts/qa/atlas_parity02_p03_harness.py'),'--port','0','--json'], {cwd:root,stdio:['ignore','pipe','pipe']});
    const lines = createInterface({input:server.stdout});
    const url = await new Promise((resolve,reject)=>{
      const timeout = setTimeout(()=>reject(new Error('HARNESS_START_TIMEOUT')),10000);
      const done = (fn,value)=>{clearTimeout(timeout); lines.close(); fn(value);};
      lines.once('line',line=>{try {done(resolve,JSON.parse(line).url);} catch {done(reject,new Error('INVALID_HARNESS_START'));}});
      server.once('error',()=>done(reject,new Error('HARNESS_PROCESS_ERROR')));
      server.once('exit',code=>{if(code!==null && code!==0)done(reject,new Error('HARNESS_EARLY_EXIT'));});
    });
    const page = await browser.newPage({viewport:{width:1440,height:1000}});
    report.external_requests=[];
    page.on('pageerror',error=>report.errors.push(String(error.message)));
    await page.route('**/*',route=>{
      if (new URL(route.request().url()).origin !== url) {
        report.external_requests.push(route.request().url()); return route.abort();
      }
      return route.continue();
    });
    const check = async(name,body)=>{await body();report.checks.push({name,status:'PASS'});};
    await page.goto(url,{waitUntil:'networkidle'});
    await page.waitForSelector('html[data-p03-ready="true"]');
    await check('exact_lexical_values',async()=>{
      const content=await page.locator('#table-mount').innerText();
      assert.ok(content.includes('9007199254740993'));assert.ok(content.includes('0.123456789012345678901'));assert.ok(content.includes('00042'));
    });
    await check('semantic_headers',async()=>{
      assert.equal(await page.locator('#table-mount th[scope="col"]').count(),6);
      assert.equal(await page.locator('#table-mount th[scope="row"]').count(),4);
      assert.equal(await page.locator('#table-mount caption').count(),1);
    });
    await check('typed_sort_keeps_identity',async()=>{
      await page.selectOption('#order','asc');
      assert.deepEqual(await page.locator('#table-mount tbody tr').evaluateAll(rows=>rows.map(row=>row.dataset.rowId)),['amostra-C','amostra-B','amostra-A','amostra-Ausente']);
    });
    await check('missing_filter',async()=>{
      await page.check('#missing');assert.equal(await page.locator('#table-mount tbody th').innerText(),'amostra-Ausente');await page.uncheck('#missing');
    });
    await check('keyboard_focus_reaches_scroll_region',async()=>{
      await page.locator('#missing').focus();await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(()=>document.activeElement.classList.contains('atlas-p03-table__scroll')),true);
    });
    await check('empty_and_hostile_input',async()=>{
      await page.selectOption('#example','empty');assert.ok((await page.locator('#table-mount').innerText()).includes('Nenhuma linha declarada'));
      await page.selectOption('#example','malicious');
      assert.equal(await page.locator('#table-mount script, #table-mount img, #table-mount iframe, #table-mount a').count(),0);
      assert.equal(await page.locator('#metadata-mount script, #metadata-mount img, #metadata-mount a, #document-mount img').count(),0);
      assert.equal(await page.evaluate(()=>globalThis.P03_ATTACK === true),false);
    });
    await check('current_metadata_and_explicit_candidates',async()=>{
      assert.equal(await page.locator('#metadata-mount [data-entity-id="report.pdf"] .p03-metadata-kind').innerText(),'Artefato declarado (File)');
      assert.equal(await page.locator('#metadata-mount [data-semantic-kind]').count(),0);
      assert.equal(await page.locator('[data-semantic-kind="product"]').count(),1);assert.equal(await page.locator('[data-semantic-kind="document"]').count(),1);
    });
    await page.selectOption('#example','table');await page.selectOption('#order','declared');
    for (const [label,width,zoom] of [['desktop',1440,1],['mobile',390,1],['zoom200',1440,2]]) {
      await page.setViewportSize({width,height:1000});await page.evaluate(value=>{document.documentElement.style.zoom=String(value);},zoom);
      await check(`contained_overflow_${label}`,async()=>{
        const shape=await page.evaluate(()=>{
          const section=document.querySelector('.atlas-p03-table');const scroll=section.querySelector('[role="region"]');
          return {width:window.innerWidth,document:document.documentElement.scrollWidth,region:scroll.getBoundingClientRect().right,overflow:getComputedStyle(scroll).overflowX,tabIndex:scroll.tabIndex};
        });
        assert.ok(shape.document<=shape.width+1);assert.ok(shape.region<=shape.width+1);assert.equal(shape.overflow,'auto');assert.equal(shape.tabIndex,0);
      });
      if(output)await page.screenshot({path:path.join(path.dirname(output),`p03-${label}.png`),fullPage:true});
    }
    await page.evaluate(()=>{document.documentElement.style.zoom='1';});
    await check('maximum_table',async()=>{
      await page.selectOption('#example','large');assert.equal(await page.locator('#table-mount tbody tr').count(),1000);assert.equal(await page.locator('#table-mount tbody td').count(),20000);
    });
    await check('no_external_requests_or_page_errors',async()=>{assert.deepEqual(report.external_requests,[]);assert.deepEqual(report.errors,[]);});
    report.status='PASS_SCOPED';report.visible_in_main_app=false;return 0;
  } catch(error) { report.status='FAIL';report.errors.push(String(error.message));return 1; }
  finally { if(browser)await browser.close();if(server)server.kill('SIGTERM'); }
}
process.exitCode=await main();finish();
