/** Regression of the retired executable-HTML surface and native reference link.
 * A real installed browser verifies the route is inert; this is not a claim
 * that the historical R4 renderer or the private Caderno ran in this job.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
let playwright;
try{playwright=require('playwright');}catch{playwright=require(require.resolve('playwright',{paths:[process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean)}));}
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url=args.get('--url'),reportPath=args.get('--report');
if(!url||!reportPath)throw new Error('--url and --report required');
const origin=new URL(url).origin;
assert.ok(['localhost','127.0.0.1'].includes(new URL(url).hostname));
const report={status:'FAIL',scenario:'original-reference-inert-native-surface',checks:[],sensitive_http_requests:[],errors:[]};
let browser,failure;
try{
  browser=await playwright.chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:900}});
  await context.route('**/*',async route=>{const u=route.request().url();if(/^https?:/.test(u)&&new URL(u).origin!==origin){report.sensitive_http_requests.push(u);await route.abort();}else await route.continue();});
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  const response=await page.goto(origin+'/original',{waitUntil:'networkidle'});
  assert.equal(response.status(),200);
  const csp=response.headers()['content-security-policy']||'';
  assert.ok(csp.includes("default-src 'none'"));
  assert.ok(!csp.includes('unsafe-inline'));assert.ok(!csp.includes('frame-src'));
  assert.equal(await page.locator('iframe,input[type=file],script').count(),0);
  assert.match(await page.locator('#original-status').innerText(),/encerrada/);
  assert.equal((await page.request.get(origin+'/original.js')).status(),404);
  assert.equal((await page.request.get(origin+'/api/legacy-source')).status(),404);
  report.checks.push('no_executable_html_upload_srcdoc_or_original_js_route');
  await page.getByTestId('open-native-from-reference').click();
  await page.locator('#native-content').waitFor();
  assert.equal(await page.locator('iframe').count(),0);
  report.checks.push('reference_routes_to_native_product_without_html_execution');
  await page.goto(origin,{waitUntil:'networkidle'});
  await page.locator('#view-explore').waitFor({state:'visible'});
  for(const testid of ['native-notebook-nav','original-atlas-nav']){
    const link=page.getByTestId(testid);
    assert.ok(!(await link.getAttribute('class')).split(/\s+/).includes('nav-button'));
    const opening=context.waitForEvent('page');
    await link.click({modifiers:['Control']});
    const popup=await opening;await popup.waitForLoadState('domcontentloaded');
    assert.ok(await page.locator('#view-explore').isVisible());
    await popup.close();
  }
  report.checks.push('ctrl_click_route_links_never_blank_the_origin_view');
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.sensitive_http_requests,[]);
  report.status='PASS_SCOPED';
}catch(e){failure=e;report.error=e.stack||e.message;}
finally{if(browser)await browser.close();await fs.mkdir(path.dirname(reportPath),{recursive:true});await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report,null,2));}
if(failure)process.exitCode=1;
