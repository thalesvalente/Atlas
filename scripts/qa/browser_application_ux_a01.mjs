/** A01 functional gates. Real browser; synthetic sources only; no external IO. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.ATLAS_PLAYWRIGHT_MODULE||'playwright');
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url=args.get('--url'),reportPath=args.get('--report'),origin=new URL(url).origin;
assert.ok(['127.0.0.1','localhost'].includes(new URL(url).hostname));
const expected=JSON.parse(await fs.readFile(args.get('--expected'),'utf8'));
const report={status:'FAIL',scope:'A01_SYNTHETIC_APPLICATION_AND_COMPONENT_REGRESSIONS',checks:[],errors:[],external_requests:[],screenshots:[],layout:[]};
let browser,failure;
const check=name=>report.checks.push(name);
try{
  browser=await chromium.launch({headless:true,...(process.env.ATLAS_CHROMIUM_EXECUTABLE?{executablePath:process.env.ATLAS_CHROMIUM_EXECUTABLE}:{})});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  await context.route('**/*',async route=>{
    const request=route.request().url();
    if(/^https?:/.test(request)&&new URL(request).origin!==origin){report.external_requests.push(request);await route.abort();}
    else await route.continue();
  });
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  await page.goto(url,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.getElementById('native-revision')?.textContent.includes('INVENTED_A01_FIX_REVISION'));
  await page.locator('[data-pane="tables"]').click();
  const control=key=>page.locator('#native-table-filter-'+key);
  const choose=async(key,label)=>{
    await control(key).selectOption({label});
    assert.equal(await page.locator(':focus').getAttribute('id'),'native-table-filter-'+key);
  };
  for(const key of ['project','run_id','stage','admission','nucleus_id'])assert.equal(await control(key).count(),1);
  for(const[key,label]of [['project','P'],['run_id','R'],['stage','S'],['admission','HOLD'],['nucleus_id','N']])await choose(key,label);
  assert.match(await page.locator('#native-content').innerText(),/105 linhas selecionadas de 205 carregadas/);
  const filterValues=Object.fromEntries(await Promise.all(['project','run_id','stage','admission','nucleus_id'].map(async key=>[key,await control(key).inputValue()])));
  check('five_declared_filters_combine_and_restore_focus');
  await page.getByRole('button',{name:'Próxima →',exact:true}).click();
  assert.match(await page.locator('.pager').first().innerText(),/Página 2\/2/);
  assert.equal(await page.locator('.literal-reading tbody tr').count(),5);
  const row=page.locator('.literal-reading tr[data-row-id='+JSON.stringify(expected.row_uid)+']');
  await row.focus();await page.keyboard.press('Enter');
  assert.equal(await row.getAttribute('aria-selected'),'true');
  await page.locator('#native-detail .inspection>summary').click();
  await page.locator('[data-testid="native-context-links"]').getByRole('button',{name:/^resource_id →/}).click();
  assert.equal(await page.locator('[data-pane="assets"]').getAttribute('aria-current'),'page');
  await page.locator('[data-testid="native-context-back"]').click();
  assert.equal(await page.locator('[data-pane="tables"]').getAttribute('aria-current'),'page');
  for(const[key,value]of Object.entries(filterValues))assert.equal(await control(key).inputValue(),value);
  assert.match(await page.locator('.pager').first().innerText(),/Página 2\/2/);
  assert.equal(await row.getAttribute('aria-selected'),'true');
  await page.keyboard.press('Escape');
  check('keyboard_row_selection_reference_return_preserves_filters_page_uid');
  const download=async(name)=>{
    const waiting=page.waitForEvent('download');await page.getByRole('button',{name,exact:true}).click();
    return fs.readFile(await(await waiting).path(),'utf8');
  };
  assert.equal(await download('JSON das linhas selecionadas'),expected.selected_json);
  assert.equal(await download('CSV protegido'),expected.selected_csv);
  await page.locator('#native-column-order').selectOption('original');
  assert.equal(await download('JSON das linhas selecionadas'),expected.selected_json);
  assert.equal(await download('CSV protegido'),expected.selected_csv);
  check('filtered_json_csv_all_pages_exact_values_original_order_reversible_columns');
  await choose('run_id','R2');
  assert.match(await page.locator('#native-content').innerText(),/Nenhuma tabela ou linha corresponde/);
  assert.equal(await page.locator('#native-table-clear').isEnabled(),true);
  await page.locator('#native-table-clear').click();
  assert.match(await page.locator('.pager').first().innerText(),/Página 1\//);
  for(const key of Object.keys(filterValues))assert.equal(await control(key).inputValue(),'');
  check('empty_combination_retains_controls_and_clear_resets_pagination');
  await choose('project','NULL — valor declarado');
  assert.equal(await page.locator('#native-table-select option').count(),1);
  assert.equal(await page.locator('#native-table-select option:checked').textContent(),'Tabela NULL');
  await choose('run_id','false');await choose('stage','"" — texto vazio declarado');await choose('admission','0');
  assert.equal(await page.locator('#native-table-select option:checked').textContent(),'Tabela NULL');
  await page.locator('#native-table-clear').click();
  await choose('project','AUSENTE — chave não declarada');
  assert.equal(await page.locator('#native-table-select option:checked').textContent(),'Tabela ausente');
  check('null_missing_empty_false_zero_are_distinct_options_not_fallbacks');
  await page.locator('#native-clear').click();
  assert.equal(await control('project').inputValue(),'');
  await choose('project','P');await page.locator('#native-refresh').click();
  await page.waitForFunction(()=>document.getElementById('native-table-filter-project')?.value==='');
  check('global_clear_and_explicit_snapshot_refresh_reset_table_filters');

  // Component regressions exercise the real presentation modules in Chromium.
  // These DTOs are invented inputs, not claims about validator authenticity.
  const component=await page.evaluate(async()=>{
    const {nativeFragments}=await import('/native_navigation.js');
    const {makePresentation,recordMatches}=await import('/native_legacy_model.js');
    const {renderRecordPresentation}=await import('/native_legacy_views.js');
    const dto=(raw,uid)=>({uid,kind:'record',group:'records',title:uid,native_id:null,source_key:null,family:null,status:null,parent_uid:null,raw_json:raw,
      fields:[...nativeFragments(raw,{all:true})].filter(([,v])=>!['{','['].includes(v[0])).map(([name,v])=>({name,type:v==='null'?'null':v[0]==='"'?'string':/^(true|false)$/.test(v)?'boolean':/[.eE]/.test(v)?'number':'integer',text:v[0]==='"'?JSON.parse(v):v}))});
    const cases=[['{"execution_state":"FAILED"}','FAILED'],['{"result_state":"SUCCEEDED"}','SUCCEEDED'],['{"result_group":"failed"}','failed'],['{"execution_state":null,"status":"FAILED"}','NULL — valor declarado'],['{"execution_state":"","result":"legacy"}','"" — texto vazio declarado'],['{}','Não declarado'],['{"status":"FAILED","result":"legacy"}','FAILED']];
    const host=document.createElement('section');document.getElementById('native-content').append(host);
    const entries=cases.map(([raw],i)=>dto(raw,'state-'+i));renderRecordPresentation(host,makePresentation(entries).records,()=>{});
    const results=[...host.querySelectorAll('tbody tr')].map(row=>row.children[2].textContent);
    const raw='{"metrics":{"model":"marker-zebra-731","integer":9007199254740993,"decimal":0.123456789012345678901,"exponent":1.23e+123,"zero":-0.0},"tags":[{"value":"a\\u00e7\\u00e3o"},"<script>globalThis.__a01Injected=true</script>"]}';
    const record=makePresentation([dto(raw,'nested')]).records[0];
    const queries=['marker-zebra-731','9007199254740993','0.123456789012345678901','1.23e+123','-0.0','ação'];
    const found=queries.map(query=>recordMatches(record,{query}));
    const negative=recordMatches(record,{query:'9007199254740992'});
    const inert=!globalThis.__a01Injected&&host.querySelectorAll('script,iframe,img').length===0;
    host.remove();return {results,expected:cases.map(([,value])=>value),found,negative,inert,unchanged:record.entry.raw_json===raw};
  });
  assert.deepEqual(component.results,component.expected);assert.ok(component.found.every(Boolean));
  assert.equal(component.negative,false);assert.equal(component.inert,true);assert.equal(component.unchanged,true);
  check('chromium_component_state_precedence_nested_search_lexical_security');

  await page.locator('[data-pane="assets"]').click();
  for(const width of [1440,390,320]){
    await page.setViewportSize({width,height:1000});
    const layout=await page.locator('.catalog-reading').evaluate(wrap=>{
      const rows=[...wrap.querySelectorAll('tbody tr')],first=rows[0];
      return {viewport:innerWidth,documentWidth:document.documentElement.scrollWidth,wrapWidth:wrap.clientWidth,tableWidth:wrap.scrollWidth,
        rows:rows.length,rowHeight:first.getBoundingClientRect().height,headers:wrap.querySelectorAll('th').length,
        focusableRegion:wrap.tabIndex===0&&wrap.getAttribute('role')==='region',
        titleVisible:getComputedStyle(first.querySelector('button')).display!=='none',
        actionHeight:first.querySelector('button').getBoundingClientRect().height};
    });
    report.layout.push(layout);
    assert.equal(layout.rows,12);assert.equal(layout.headers,4);assert.equal(layout.focusableRegion,true);assert.equal(layout.titleVisible,true);
    assert.ok(layout.documentWidth<=width+1,'Horizontal overflow must be contained in the table region');
    assert.ok(layout.actionHeight>=24,'Readable compact controls retain a 24px target');
    if(width===1440){assert.ok(layout.tableWidth<=layout.wrapWidth+1,'Normal desktop catalog must fit its work surface');assert.ok(layout.rowHeight<115,'Compact synthetic catalog row');}
    const screenshot=reportPath.replace('.json','-'+width+'.png');await page.screenshot({path:screenshot,fullPage:false});report.screenshots.push(path.basename(screenshot));
    check('compact_catalog_all_data_accessible_reflow_'+width);
    await page.locator('[data-pane="tables"]').click();
    for(const key of Object.keys(filterValues)){
      const box=await control(key).boundingBox();assert.ok(box&&box.width>0&&box.x>=0&&box.x+box.width<=width+1);
    }
    await page.locator('[data-pane="assets"]').click();
  }
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);
  report.status='PASS';
}catch(error){failure=error;report.failure=error.stack||String(error);}
finally{if(browser)await browser.close();await fs.writeFile(reportPath,JSON.stringify(report,null,2)+'\n');}
if(failure)throw failure;
console.log(JSON.stringify({status:report.status,checks:report.checks.length,report:reportPath}));
