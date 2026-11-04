/** Focused screen regressions against the installed viewer and real exporter. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url=args.get('--url'),reportPath=args.get('--report'),origin=new URL(url).origin;
assert.ok(['127.0.0.1','localhost'].includes(new URL(url).hostname));
const report={status:'FAIL',scope:'INSTALLED_NATIVE_UI_ENGINEERING_NOT_PRIVATE_HOST_PARITY',checks:[],errors:[],external_requests:[]};
const check=name=>report.checks.push(name);
let browser,failure;
try{
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  await context.route('**/*',async route=>{const url=route.request().url();if(/^https?:/.test(url)&&new URL(url).origin!==origin){report.external_requests.push(url);await route.abort();}else await route.continue();});
  const page=await context.newPage();page.on('pageerror',error=>report.errors.push(error.message));
  await page.goto(url,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='2');
  await page.getByRole('treeitem',{name:'Execução',exact:true}).click();
  await page.locator('#native-detail-body').getByRole('button',{name:/^run_id → Registro longo/}).click();
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/declared-run-alias/);
  assert.match(await page.locator('[data-testid="native-context-links"]').innerText(),/UNRESOLVED/);
  await page.getByText(/^Referências recebidas/).click();
  await page.locator('#native-detail-body').getByRole('button',{name:/^Tabela extensa.*record_id/}).click();
  await page.getByText(/^Referências recebidas/).click();
  await page.locator('#native-detail-body').getByRole('button',{name:/^Row-ID-Only.*table_uid/}).click();
  await page.getByText('Evidência e origem declaradas · evidence',{exact:true}).click();
  const evidence=await page.locator('[data-testid="native-evidence"]').innerText();
  assert.match(evidence,/Invented literal evidence/);assert.match(evidence,/9007199254740993/);
  for(const expected of ['table · result_tables','record · records','node · lineage_graph.nodes']){
    await page.locator('[data-testid="native-context-back"]').click();
    assert.ok((await page.locator('#native-detail-body').innerText()).includes(expected));
  }
  assert.equal(await page.locator('.graph-node[aria-selected="true"][aria-label="Execução"]').count(),1);
  check('declared_alias_journey_node_record_table_row_exact_evidence_and_return');
  await page.locator('#native-source').selectOption('source-2');
  assert.ok(await page.locator('#native-detail').isHidden());assert.equal(await page.locator('[data-testid="native-context-back"]').count(),0);
  await page.locator('[data-pane="records"]').click();await page.locator('#native-content tbody tr').first().getByRole('button').click();
  assert.match(await page.locator('#native-detail-body').innerText(),/INVENTED_P02_OTHER_SNAPSHOT/);
  assert.ok(!(await page.locator('[data-testid="native-context-links"]').innerText()).includes('Tabela extensa'));
  await page.locator('#native-source').selectOption('source-1');
  check('source_switch_invalidates_navigation_history_and_alias_context');
  await page.locator('[data-pane="relations"]').click();
  await page.locator('#native-content tbody').getByRole('button',{name:'Composite-key-proof',exact:true}).click();
  const relationLinks=page.locator('[data-testid="native-context-links"]');
  assert.match(await relationLinks.innerText(),/from_key: \["not-interpreted"\].*não interpretado/);
  assert.equal(await relationLinks.getByRole('button',{name:/^from →/}).count(),0);
  check('explicit_composite_endpoint_key_is_not_interpreted_or_fallen_back');
  await page.locator('[data-pane="tables"]').click();
  await page.locator('#native-search').fill('  Row-ID-Only  ');
  assert.equal(await page.locator('#native-content [data-row-id]').count(),1,'Table search must trim and search row identifiers outside cells');
  check('table_search_includes_row_identifiers_and_trims_query');
  await page.locator('#native-clear').click();
  await page.locator('#native-search').fill('Table-B-Only');
  assert.equal(await page.locator('#native-table-select option').count(),1,'Global search must reach metadata of any table');
  assert.equal(await page.locator('#native-table-select option:checked').innerText(),'Outra tabela');
  assert.equal(await page.locator('#native-content [data-row-id]').count(),1);
  check('table_metadata_search_reaches_other_tables_and_preserves_rows');
  await page.locator('#native-clear').click();
  await page.locator('#native-status').selectOption('HOLD');
  assert.equal(await page.locator('#native-table-select option').count(),1,'Status filter must apply to tables');
  assert.equal(await page.locator('#native-content [data-row-id]').count(),2,'Rows without their own facets remain in their declared table context');
  await page.locator('#native-family').selectOption('G');
  assert.equal(await page.locator('#native-table-select').count(),0,'Incompatible facets must produce an honest empty selection');
  assert.match(await page.locator('#native-content').innerText(),/Nenhuma tabela/);
  check('table_family_status_filters_use_declared_context_and_empty_selection');
  await page.locator('#native-clear').click();
  await page.getByRole('button',{name:'Detalhes da tabela',exact:true}).click();
  const tableRaw=await page.locator('[data-testid="native-raw"]').innerText();
  assert.ok(tableRaw.includes('9007199254740993'));assert.equal(JSON.parse(tableRaw).rows.length,2);
  assert.equal(createHash('sha256').update(tableRaw).digest('hex'),args.get('--expected-table-digest'));
  let waiting=page.waitForEvent('download');await page.getByRole('button',{name:'JSON das linhas selecionadas',exact:true}).click();
  let download=await waiting,bytes=await fs.readFile(await download.path());
  assert.ok(bytes.toString().includes('9007199254740993'));assert.equal(JSON.parse(bytes).length,2);
  waiting=page.waitForEvent('download');await page.getByRole('button',{name:'CSV protegido',exact:true}).click();download=await waiting;bytes=await fs.readFile(await download.path());
  assert.ok(bytes.toString().includes("'=1+1"));
  check('filtered_table_exact_json_and_formula_safe_csv_preserved');
  await page.locator('[data-pane="assets"]').click();await page.locator('#native-family').selectOption('Recurso');
  assert.equal(await page.getByRole('button',{name:'Ver referência e detalhes'}).count(),1);
  check('filters_include_declared_resource_facets');
  await page.locator('#native-clear').click();await page.locator('[data-pane="coverage"]').click();
  await page.getByText('Valores globais da projeção',{exact:true}).click();
  const coverage=await page.locator('#native-content').innerText();
  assert.ok(coverage.includes('unknown_empty'));assert.ok(coverage.includes('unknown_null'));assert.ok(coverage.includes('9007199254740993'));
  check('empty_collections_and_exact_global_scalars_are_consultable');
  waiting=page.waitForEvent('download');await page.locator('#native-download').click();download=await waiting;bytes=await fs.readFile(await download.path());
  assert.equal(createHash('sha256').update(bytes).digest('hex'),args.get('--expected-digest'));
  check('full_projection_export_matches_original_bytes');
  for(const width of [1440,390,320]){
    await page.setViewportSize({width,height:1000});
    for(const pane of ['records','tables','relations','assets','timeline','coverage']){
      await page.locator('[data-pane="'+pane+'"]').click();
      assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),`${pane} overflows at ${width}px`);
    }
    check('all_screens_long_values_reflow_'+width);
  }
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);
  report.status='PASS_SCOPED';
}catch(error){failure=error;report.error=error.stack||error.message;}
finally{
  if(browser)await browser.close();
  await fs.mkdir(path.dirname(reportPath),{recursive:true});await fs.writeFile(reportPath,JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
}
if(failure)process.exitCode=1;
