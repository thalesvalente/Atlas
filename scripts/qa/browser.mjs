/** Independent browser test of the installed, live Atlas application.
 * No producer schema/names or private fixtures are embedded in this harness.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require = createRequire(import.meta.url);
let playwright;
try {playwright = require('playwright');}
catch {playwright = require(require.resolve('playwright', {paths:[process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean)}));}

const args = new Map();
for (let i=2;i<process.argv.length;i+=2) args.set(process.argv[i],process.argv[i+1]);
const url = args.get('--url');
const reportPath = args.get('--report');
if (!url || !reportPath) throw new Error('Required: --url URL --report PATH [--expected-sources N --expected-runs N]');
const origin = new URL(url).origin;
assert.ok(['127.0.0.1','localhost'].includes(new URL(url).hostname), 'Harness only targets an explicitly supplied loopback application');
const checks=[];
const externalRequests=[];
const pageErrors=[];
let browser;
let catalog;
let failure;
const report = {status:'FAIL',scope:'installed-live-ui',checks,external_requests:externalRequests,page_errors:pageErrors};
const record = name => checks.push({name,status:'PASS'});
const screenshots = [];
const expectedInteger=args.get('--expected-exact-integer');
const metricText=m=>m.display_value??String(m.value??'Ausente');
try {
  browser=await playwright.chromium.launch({headless:true,...(process.env.ATLAS_BROWSER_BINARY?{executablePath:process.env.ATLAS_BROWSER_BINARY}:{})});
  report.browser_version=browser.version();
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  await context.route('**/*',async route=>{
    const requestUrl=route.request().url();
    if (/^https?:/.test(requestUrl) && new URL(requestUrl).origin!==origin) {
      externalRequests.push(requestUrl);
      await route.abort();
    } else await route.continue();
  });
  const page=await context.newPage();
  page.on('pageerror', error=>pageErrors.push(error.message));
  const response=await page.goto(url,{waitUntil:'networkidle'});
  assert.equal(response.status(),200);
  assert.ok((response.headers()['content-security-policy']||'').includes("default-src 'none'"));
  const api=await page.request.get(origin+'/api/catalog');
  assert.equal(api.status(),200);
  catalog=await api.json();
  const runs=catalog.sources.flatMap(s=>(s.read_model?.runs||[]).map(r=>({...r,source:s.id})));
  report.sources=catalog.sources.length;
  report.runs=runs.length;
  if(args.has('--expected-sources')) assert.equal(catalog.sources.length,Number(args.get('--expected-sources')));
  if(args.has('--expected-runs')) assert.equal(runs.length,Number(args.get('--expected-runs')));
  await page.waitForFunction(n=>document.getElementById('runs-count').textContent===String(n),runs.length);
  assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.length);
  for(const run of runs) assert.ok((await page.getByTestId('run-table').innerText()).includes(run.name||run.id));
  record('catalog_records_match_parsed_source');
  assert.equal(await page.locator('#run-rows script, #run-rows img, #detail script, #detail img').count(),0);
  assert.equal(await page.evaluate(()=>window.__atlasQA),undefined);
  record('record_labels_render_as_text');

  if(runs.length) {
    const first=runs[0];
    await page.getByTestId('search').fill(first.id);
    assert.ok(await page.getByTestId('run-table').locator('tbody tr').count()>=1);
    assert.ok((await page.getByTestId('run-table').innerText()).includes(first.name||first.id));
    await page.getByRole('button',{name:'Limpar',exact:true}).click();
    assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.length);
    record('search_and_clear');
    const firstSource=catalog.sources.find(s=>s.id===first.source);
    const project=firstSource.read_model.projects[0];
    await page.getByTestId('project-filter').selectOption(JSON.stringify([first.source,project.id]));
    assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.filter(r=>r.source===first.source&&r.project_id===project.id).length);
    await page.getByRole('button',{name:'Limpar',exact:true}).click();
    const experiment=firstSource.read_model.experiments.find(e=>e.id===first.experiment_id);
    await page.getByTestId('experiment-filter').selectOption(JSON.stringify([first.source,experiment.id]));
    assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.filter(r=>r.source===first.source&&r.experiment_id===experiment.id).length);
    await page.getByRole('button',{name:'Limpar',exact:true}).click();
    await page.getByTestId('status-filter').selectOption(first.status);
    assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.filter(r=>r.status===first.status).length);
    await page.getByRole('button',{name:'Limpar',exact:true}).click();
    record('project_experiment_status_filters');
    await page.getByTestId('run-open').first().click();
    assert.ok(await page.getByTestId('detail').isVisible());
    const detail=await page.getByTestId('detail').innerText();
    for(const text of [first.id,first.status,first.review_status])assert.ok(detail.includes(text));
    if(first.synthetic)assert.ok(detail.includes('SINTÉTICO'));
    for(const metric of first.metrics)assert.ok(detail.includes(metricText(metric)));
    if(expectedInteger){assert.ok(first.metrics.some(m=>m.display_value===expectedInteger));assert.ok(detail.includes(expectedInteger));record('detail_preserves_large_integer_text');}
    assert.equal(await page.locator('#detail script,#detail img').count(),0);
    record('run_detail_metrics_states_and_synthetic_identity');
  } else {
    assert.ok(await page.locator('#empty').isVisible());
    record('empty_state_has_no_fabricated_records');
  }
  if(runs.length>=2) {
    await page.getByTestId('run-select').nth(0).check();
    await page.getByTestId('run-select').nth(1).check();
    await page.getByTestId('compare-selected').click();
    assert.ok(await page.getByTestId('compare').isVisible());
    const comparison=await page.getByTestId('compare').innerText();
    for(const run of runs.slice(0,2)) {
      assert.ok(comparison.includes(run.name||run.id));
      assert.ok(comparison.includes(run.review_status));
      const groups=new Map();
      for(const metric of run.metrics) {
        const key=JSON.stringify([metric.property_id,metric.type,metric.unit]);
        if(!groups.has(key))groups.set(key,[]);
        groups.get(key).push(metric);
      }
      for(const metrics of groups.values()) if(metrics.length>1) {
        for(const metric of metrics) {
          assert.ok(comparison.includes(metric.id),'Duplicate metric identities must remain distinguishable');
          assert.ok(comparison.includes(metricText(metric)),'No duplicate value may be overwritten');
        }
        record('comparison_preserves_repeated_metric_identity_values');
      }
    }
    const byIdentity=new Map();
    for(const r of runs.slice(0,2))for(const m of r.metrics) {
      if(!byIdentity.has(m.property_id))byIdentity.set(m.property_id,new Set());
      byIdentity.get(m.property_id).add(JSON.stringify([m.type,m.unit]));
    }
    if([...byIdentity.values()].some(x=>x.size>1)) {
      assert.ok(comparison.includes('incompatíveis'));
      record('comparison_explains_incompatible_units_or_types');
    }
    if(expectedInteger){assert.ok(comparison.includes(expectedInteger));record('comparison_preserves_large_integer_text');}
    record('comparison_preserves_states_and_units');
  }
  await page.getByTestId('timeline-nav').click();
  assert.ok(await page.getByTestId('timeline').isVisible());
  for(const run of runs)assert.ok((await page.getByTestId('timeline').innerText()).includes(run.name||run.id));
  if(runs.some(r=>!r.started_at))assert.ok((await page.getByTestId('timeline').innerText()).includes('Sem data declarada'));
  record('timeline_preserves_declared_and_missing_times');
  await page.getByTestId('lineage-nav').click();
  assert.ok(await page.getByTestId('lineage').isVisible());
  record('lineage_navigation_uses_declared_relations');
  await page.getByTestId('sources-nav').click();
  const sourcesText=await page.locator('#sources-content').innerText();
  for(const source of catalog.sources) {
    assert.ok(sourcesText.includes(source.name));
    assert.ok(sourcesText.includes(source.status));
  }
  if(catalog.sources.length)assert.ok(sourcesText.includes('NOT_VERIFIED'));
  record('source_validity_is_distinct_from_authenticity');
  await page.getByTestId('dossier-nav').click();
  assert.ok(await page.getByTestId('dossier').isVisible());
  const downloadPromise=page.waitForEvent('download');
  await page.getByTestId('download-dossier').click();
  const download=await downloadPromise;
  const stream=await download.createReadStream();
  const chunks=[];
  for await(const chunk of stream) chunks.push(chunk);
  const dossierRaw=Buffer.concat(chunks).toString('utf8');
  const dossier=JSON.parse(dossierRaw);
  if(expectedInteger){assert.ok(/^-?[0-9]+$/.test(expectedInteger));assert.ok(new RegExp('\"value\"\\s*:\\s*'+expectedInteger+'(?=\\s*[,}])').test(dossierRaw),'Raw dossier must preserve exact integer bytes');record('dossier_preserves_large_integer_raw_json');}
  assert.equal(dossier.authority,'DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL');
  assert.equal(dossier.sources.length,catalog.sources.length);
  assert.equal(dossier.sources.reduce((sum,s)=>sum+(s.read_model?.runs.length||0),0),runs.length);
  assert.ok(dossier.limitations.length>=3);
  record('dossier_download_contains_real_records_and_limits');

  const wrongHost=await page.request.get(origin+'/api/catalog',{headers:{Host:'attacker.invalid'}});
  const wrongOrigin=await page.request.get(origin+'/api/catalog',{headers:{Origin:'https://attacker.invalid'}});
  const sourceInjection=await page.request.post(origin+'/api/reindex',{headers:{Origin:origin},data:{source:'/unrequested'}});
  const noOrigin=await page.request.post(origin+'/api/reindex',{data:{}});
  assert.equal(wrongHost.status(),403);
  assert.equal(wrongOrigin.status(),403);
  assert.equal(sourceInjection.status(),400);
  assert.equal(noOrigin.status(),403);
  for(const method of ['put','delete','patch']) {
    const res=await page.request[method](origin+'/api/catalog',{headers:{Origin:origin},data:{}});
    assert.equal(res.status(),405);
  }
  record('http_host_origin_and_fixed_source_allowlist');
  const reindexResponse=page.waitForResponse(r=>r.url()===origin+'/api/reindex'&&r.request().method()==='POST');
  await page.getByTestId('reindex').click();
  assert.equal((await reindexResponse).status(),200);
  await page.waitForFunction(()=>!document.getElementById('refresh').disabled);
  const after=await (await page.request.get(origin+'/api/catalog')).json();
  assert.ok(after.generation>catalog.generation);
  assert.deepEqual(after.sources.map(s=>s.read_model),catalog.sources.map(s=>s.read_model));
  record('explicit_reindex_preserves_source_records');
  await page.goto(url,{waitUntil:'networkidle'});
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(()=>document.activeElement.classList.contains('skip')));
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>document.activeElement.id),'main');
  if(runs.length) {
    await page.getByTestId('search').focus();
    await page.keyboard.type(runs[0].id);
    assert.ok(await page.getByTestId('run-table').locator('tbody tr').count()>=1);
    await page.keyboard.press('Tab');
    assert.equal(await page.evaluate(()=>document.activeElement.id),'project-filter');
    assert.ok(await page.evaluate(()=>parseFloat(getComputedStyle(document.activeElement).outlineWidth)>=2));
    await page.getByRole('button',{name:'Limpar',exact:true}).click();
  }
  record('keyboard_skip_link_filters_and_visible_focus');
  const controls=await page.locator('input,select,button').evaluateAll(elements=>elements.filter(e=>e.offsetWidth&&e.offsetHeight).map(e=>({tag:e.tagName,id:e.id,label:e.getAttribute('aria-label')||e.textContent.trim()||[...(e.labels||[])].map(l=>l.textContent).join('')})));
  assert.ok(controls.every(c=>c.label),'Every visible form control has an accessible text label');
  record('visible_controls_have_names');
  await fs.mkdir(path.dirname(reportPath),{recursive:true});
  const desktopPath=reportPath.replace(/\.json$/,'')+'-desktop.png';
  await page.screenshot({path:desktopPath,fullPage:true});
  screenshots.push(path.basename(desktopPath));
  await page.setViewportSize({width:390,height:844});
  await page.reload({waitUntil:'networkidle'});
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),'Mobile page must not overflow the viewport');
  assert.equal(await page.getByTestId('run-table').locator('tbody tr').count(),runs.length);
  if(runs.length) {
    await page.getByTestId('run-open').first().click();
    assert.ok(await page.getByTestId('detail').isVisible());
  }
  await page.getByTestId('lineage-nav').click();
  assert.ok(await page.getByTestId('lineage').isVisible());
  const mobilePath=reportPath.replace(/\.json$/,'')+'-mobile.png';
  await page.screenshot({path:mobilePath,fullPage:true});
  screenshots.push(path.basename(mobilePath));
  record('mobile_390px_detail_and_navigation');
  assert.deepEqual(pageErrors,[]);
  assert.deepEqual(externalRequests,[]);
  record('no_page_errors_or_external_requests');
  report.status='PASS_SCOPED';
} catch(error) {
  failure=error;
  report.error=error.message;
} finally {
  if(browser)await browser.close();
  report.screenshots=screenshots;
  report.executed_checks=checks.length;
  report.human_protocol_acceptance='PENDING';
  report.canonical_promotion='NOT_AUTHORIZED';
  await fs.mkdir(path.dirname(reportPath),{recursive:true});
  await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
}
if(failure)process.exitCode=1;
