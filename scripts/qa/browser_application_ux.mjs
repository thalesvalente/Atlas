/** Full non-graph application qualification, using only invented local inputs. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url=args.get('--url'),reportPath=args.get('--report'),origin=new URL(url).origin;
assert.ok(['127.0.0.1','localhost'].includes(new URL(url).hostname));
const expected=JSON.parse(await fs.readFile(args.get('--expected'),'utf8'));
const report={status:'FAIL',scope:'INSTALLED_APPLICATION_UX_SYNTHETIC_ONLY',browser_channel:process.env.PLAYWRIGHT_CHANNEL||'chromium',checks:[],errors:[],external_requests:[],screenshots:[]};
const check=name=>report.checks.push(name),sha=bytes=>createHash('sha256').update(bytes).digest('hex');
let browser,failure,originalMetadata;
const metadataPath=args.get('--synthetic-metadata');
try{
  browser=await chromium.launch({headless:true,...(process.env.PLAYWRIGHT_CHANNEL?{channel:process.env.PLAYWRIGHT_CHANNEL}:{})});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  await context.route('**/*',async route=>{const value=route.request().url();if(/^https?:/.test(value)&&new URL(value).origin!==origin){report.external_requests.push(value);await route.abort();}else await route.continue();});
  const page=await context.newPage();page.on('pageerror',error=>report.errors.push(error.message));
  await page.goto(url,{waitUntil:'networkidle'});
  await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='5');
  assert.equal(await page.locator('link[href="/native_application.css"]').count(),1);
  const css=await page.request.get(origin+'/native_application.css');assert.equal(css.status(),200);assert.match(css.headers()['content-type'],/text\/css/);
  assert.equal(await page.locator('iframe').count(),0);
  check('installed_application_css_and_native_text_only_assets');
  const pane=name=>page.locator('[data-pane="'+name+'"]');
  const screenshot=async name=>{const filename=reportPath.replace('.json','-'+name+'.png');await page.screenshot({path:filename,fullPage:name==='desktop'});report.screenshots.push(path.basename(filename));};
  const download=async(label,digest)=>{const waiting=page.waitForEvent('download');await page.getByRole('button',{name:label,exact:true}).click();const item=await waiting,bytes=await fs.readFile(await item.path());assert.equal(sha(bytes),digest,label+' must export the entire exact selection');return bytes;};
  const assertFocus=async selector=>assert.equal(await page.locator(selector).evaluate(node=>document.activeElement===node),true,'Expected focus on '+selector);
  const inViewport=async target=>assert.equal(await target.evaluate(node=>{const rect=node.getBoundingClientRect();return rect.top>=0&&rect.bottom<=innerHeight&&rect.left>=0&&rect.right<=innerWidth;}),true,'Focused content must be visible in the viewport');
  await pane('records').click();
  const record=page.locator('#native-content tbody').getByRole('button',{name:'Registro principal',exact:true});
  await record.focus();await page.keyboard.press('Enter');
  await assertFocus('#native-detail-title');
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"native_id":null/);
  assert.equal(await page.locator('#native-detail-body dt').filter({hasText:/^ID original$/}).locator('xpath=following-sibling::dd[1]').innerText(),'NULL — valor declarado');
  assert.equal(await page.locator('#native-content [aria-selected="true"]').count(),1);
  await page.keyboard.press('Escape');assert.ok(await page.locator('#native-detail').isHidden());
  assert.equal(await record.evaluate(node=>document.activeElement===node),true);
  const noStatus=page.locator('#native-content tbody tr').filter({hasText:'Registro sem estado'});
  assert.equal(await noStatus.locator('td').nth(3).innerText(),'Não declarado','An undeclared state must not become literal UNKNOWN');
  const nullId=page.locator('#native-content tbody tr').filter({hasText:'Registro principal'}),missingId=page.locator('#native-content tbody tr').filter({hasText:'Registro sem ID'}),emptyId=page.locator('#native-content tbody tr').filter({hasText:'Registro com textos vazios'});
  assert.equal(await nullId.locator('td').nth(1).innerText(),'NULL — valor declarado');
  assert.equal(await missingId.locator('td').nth(1).innerText(),'Não declarado');
  assert.equal(await emptyId.locator('td').nth(1).innerText(),'"" — texto vazio declarado');
  assert.equal(await missingId.locator('td').nth(3).innerText(),'NULL — valor declarado');
  assert.equal(await emptyId.locator('td').nth(3).innerText(),'"" — texto vazio declarado');
  assert.equal(await page.locator('#native-content tbody tr').filter({hasText:'Registro UNKNOWN'}).locator('td').nth(3).innerText(),'UNKNOWN');
  check('keyboard_detail_focus_escape_return_selection_and_distinct_null_missing_empty_states');
  await record.click();
  await page.locator('[data-testid="native-context-links"]').getByText(/^Referências recebidas/).click();
  await page.locator('[data-testid="native-context-links"]').getByRole('button',{name:/^Tabela da aplicação.*record_id/}).click();
  assert.equal(await page.locator('#native-table-select').inputValue(),expected.table_uid);
  assert.equal(sha(await page.locator('[data-testid="native-raw"]').innerText()),expected.table_sha256);
  await page.locator('[data-testid="native-context-links"]').getByText(/^Referências recebidas/).click();
  await page.locator('[data-testid="native-context-links"]').getByRole('button',{name:/^row-000.*table_uid/}).click();
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"id":"row-000"/);
  assert.ok((await page.locator('#native-detail-body').innerText()).includes('/result_tables/0/rows/0'));
  await page.locator('[data-testid="native-context-back"]').click();
  await page.locator('[data-testid="native-context-back"]').click();
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"id":"record-root"/);
  check('record_table_row_structural_links_exact_identity_and_context_return');
  await page.keyboard.press('Escape');assert.ok(await page.locator('#native-detail').isHidden());
  assert.equal(await record.evaluate(node=>document.activeElement===node),true,'Context return recreates the record trigger; Escape must recover that occurrence');
  await inViewport(record);
  check('escape_after_two_context_returns_restores_recreated_record_trigger');
  await pane('tables').click();assert.ok(await page.locator('#native-detail').isHidden(),'Pane change clears old detail');
  const component=page.locator('[data-component="parity02-p03-table"]');
  const rowsSeen=new Set(),cellsSeen=new Set();
  for(let rowPage=0;rowPage<3;rowPage++){
    for(let columnPage=0;columnPage<3;columnPage++){
      const actual=await component.locator('tbody tr[data-row-id]').evaluateAll(nodes=>nodes.map(tr=>({uid:tr.getAttribute('data-row-id'),cells:[...tr.querySelectorAll('td')].map(td=>td.textContent)})));
      const rowWindow=expected.rows.slice(rowPage*100,rowPage*100+100),columns=expected.columns.slice(columnPage*32,columnPage*32+32);
      assert.deepEqual(actual.map(row=>row.uid),rowWindow.map(row=>row.uid));
      for(let index=0;index<actual.length;index++){
        rowsSeen.add(actual[index].uid);
        const wanted=columns.map(column=>{const cell=rowWindow[index].cells[column];return !cell?'Não informado — MISSING — chave ausente':cell.type==='null'?'Não informado — NULL — valor declarado':cell.text;});
        assert.deepEqual(actual[index].cells,wanted,'Cells must retain exact lexical values and absence states');
        for(const column of columns)cellsSeen.add(actual[index].uid+'/'+column);
      }
      if(columnPage<2){await page.getByRole('button',{name:'Colunas →',exact:true}).click();assert.equal(await page.getByRole('button',{name:columnPage===0?'Colunas →':'← Colunas',exact:true}).evaluate(node=>document.activeElement===node),true);}
    }
    if(rowPage<2){
      await page.getByRole('button',{name:'← Colunas',exact:true}).click();await page.getByRole('button',{name:'← Colunas',exact:true}).click();
      await page.getByRole('button',{name:'Próxima →',exact:true}).click();
      assert.equal(await page.getByRole('button',{name:rowPage===0?'Próxima →':'← Anterior',exact:true}).evaluate(node=>document.activeElement===node),true);
    }
  }
  assert.equal(rowsSeen.size,205);assert.equal(cellsSeen.size,205*65);
  check('all_nine_row_column_windows_205_rows_65_columns_exact_and_keyboard_focus');
  await download('JSON das linhas selecionadas',expected.rows_sha256);
  const csv=await download('CSV protegido',expected.csv_sha256);assert.ok(csv.toString().includes('9007199254740993'));assert.ok(csv.toString().includes("'=1+1"));
  await page.getByRole('button',{name:'Detalhes da tabela',exact:true}).click();
  await download('Exportar esta ocorrência',expected.table_sha256);
  const fullWaiting=page.waitForEvent('download');await page.locator('#native-download').click();const full=await fullWaiting;assert.equal(sha(await fs.readFile(await full.path())),expected.projection_sha256);
  check('whole_selection_csv_rows_occurrence_projection_downloads_byte_exact');
  await page.locator('#native-search').fill('row-204');
  assert.ok(await page.locator('#native-detail').isHidden(),'Filters clear a stale detail');
  assert.equal(await component.locator('tbody tr[data-row-id]').count(),1);
  assert.equal(await component.locator('tbody tr[data-row-id]').getAttribute('data-row-id'),expected.rows[204].uid);
  await page.locator('#native-clear').click();
  await page.locator('#native-table-select').selectOption({label:'Tabela de texto integral'});
  assert.match(await page.locator('#native-content').innerText(),/sem truncar valores/);
  assert.ok((await page.locator('#native-content').innerText()).includes(expected.long_text));
  await page.getByRole('button',{name:'Detalhes da tabela',exact:true}).click();await download('Exportar esta ocorrência',expected.long_table_sha256);
  check('row_search_beyond_first_page_and_p03_long_value_fallback_without_loss');
  await page.locator('#native-source').selectOption('source-2');
  assert.ok(await page.locator('#native-detail').isHidden());assert.equal(await page.locator('[data-testid="native-context-back"]').count(),0);
  for(const name of ['records','assets','timeline','tables','relations','coverage']){
    await pane(name).click();assert.match(await page.locator('#native-content').innerText(),/Nenhum|Nenhuma|vazi/i,name+' must declare an empty population');
  }
  check('source_switch_clears_scope_and_all_empty_sections_are_explicit');
  await page.locator('#native-source').selectOption('source-3');await pane('tree').click();
  assert.equal(await page.locator('#native-node-count').innerText(),'0');
  const fallbackRoot=page.getByRole('treeitem',{name:'Registro raiz sem nós',exact:true});
  await fallbackRoot.focus();await page.keyboard.press('Enter');
  assert.equal(await fallbackRoot.evaluate(node=>document.activeElement===node),true,'Record fallback must retain graph keyboard ownership');
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"id":"fallback-root"/);
  await page.keyboard.press('ArrowDown');
  const fallbackChild=page.getByRole('treeitem',{name:'Registro filho sem nós',exact:true});
  assert.equal(await fallbackChild.evaluate(node=>document.activeElement===node),true);await page.keyboard.press('Enter');
  assert.equal(await fallbackChild.evaluate(node=>document.activeElement===node),true);
  assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"id":"fallback-child"/);
  check('record_tree_fallback_enter_arrows_preserve_treeitem_focus');
  await page.locator('#native-source').selectOption('source-1');
  for(const width of [1440,390,320]){
    await page.setViewportSize({width,height:1000});
    for(const name of ['records','tables','relations','assets','timeline','coverage']){
      await pane(name).click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),name+' overflows '+width);
    }
    if(width!==1440){
      await pane('records').click();
      const trigger=page.locator('#native-content tbody').getByRole('button',{name:'Registro principal',exact:true});
      await trigger.focus();await page.keyboard.press('Enter');await assertFocus('#native-detail-title');await inViewport(page.locator('#native-detail-title'));
      await page.keyboard.press('Escape');assert.ok(await page.locator('#native-detail').isHidden());assert.equal(await trigger.evaluate(node=>document.activeElement===node),true);await inViewport(trigger);
      await trigger.focus();await page.keyboard.press('Enter');
      await page.locator('[data-testid="native-context-links"]').getByText(/^Referências recebidas/).click();
      await page.locator('[data-testid="native-context-links"]').getByRole('button',{name:/^Tabela da aplicação.*record_id/}).click();
      await assertFocus('#native-detail-title');await inViewport(page.locator('#native-detail-title'));
      await page.locator('[data-testid="native-context-back"]').click();
      assert.match(await page.locator('[data-testid="native-raw"]').innerText(),/"id":"record-root"/);
      if(width===390)await page.keyboard.press('Escape');else await page.locator('#native-close-detail').click();
      assert.ok(await page.locator('#native-detail').isHidden());
      assert.equal(await trigger.evaluate(node=>document.activeElement===node),true,'Closing after context return must focus the recreated mobile record trigger');
      await inViewport(trigger);
      check('mobile_context_return_close_restores_recreated_record_trigger_'+width);
      await pane('tables').click();const tableTrigger=page.getByRole('button',{name:'Detalhes da tabela',exact:true});
      await tableTrigger.focus();await page.keyboard.press('Enter');await assertFocus('#native-detail-title');await inViewport(page.locator('#native-detail-title'));
      await page.keyboard.press('Escape');assert.ok(await page.locator('#native-detail').isHidden());assert.equal(await tableTrigger.evaluate(node=>document.activeElement===node),true);await inViewport(tableTrigger);
      check('mobile_record_table_detail_focus_visible_escape_restores_visible_trigger_'+width);
    }
    await pane(width===1440?'records':'tables').click();await page.evaluate(()=>window.scrollTo(0,0));await screenshot(width===1440?'desktop':'mobile-'+width);
    if(width!==1440){await page.locator('#native-content').scrollIntoViewIfNeeded();await screenshot('mobile-'+width+'-table');}
    check('all_non_graph_sections_reflow_'+width);
  }
  await page.setViewportSize({width:1440,height:1000});
  const failed='**/api/notebook';await page.route(failed,route=>route.fulfill({status:503,contentType:'application/json',body:'{}'}));
  await page.locator('#native-refresh').click();await page.waitForFunction(()=>document.getElementById('native-notice')?.textContent.includes('503'));
  assert.equal(await page.locator('#native-source option').count(),0);assert.equal(await page.locator('#native-record-count').innerText(),'0');
  assert.ok(await page.locator('#native-download').isDisabled());assert.ok(await page.locator('#native-detail').isHidden());
  await page.unroute(failed);await page.locator('#native-refresh').click();
  await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='5');
  check('http_failure_clears_stale_sources_and_recovers_explicitly');
  originalMetadata=await fs.readFile(metadataPath);const changed=JSON.parse(originalMetadata.toString());
  changed['@graph'].find(item=>item['@id']==='./').name='INVENTED_TEMPORARY_METADATA_CHANGE';
  const oldSnapshot=(await (await page.request.get(origin+'/api/notebook')).json()).sources[0].metadata_sha256;
  await fs.writeFile(metadataPath,JSON.stringify(changed));await page.locator('#native-refresh').click();
  await page.waitForFunction(()=>document.getElementById('native-notice')?.textContent.includes('CHANGED'));
  assert.ok(await page.locator('#native-download').isDisabled());assert.ok(await page.locator('#native-detail').isHidden());
  const rejected=await page.request.get(origin+'/api/notebook/export?'+new URLSearchParams({source:'source-1',snapshot:oldSnapshot}));assert.ok(rejected.status()>=400);
  const rebuild=async()=>{const response=page.waitForResponse(value=>value.url()===origin+'/api/reindex'&&value.request().method()==='POST'),load=page.waitForEvent('load');await page.locator('#native-rebuild').click();assert.equal((await response).status(),200);await load;};
  await rebuild();await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='5');
  const renewed=(await (await page.request.get(origin+'/api/notebook')).json()).sources[0];assert.equal(renewed.status,'READY');assert.notEqual(renewed.metadata_sha256,oldSnapshot);
  const renewedExport=await page.request.get(origin+'/api/notebook/export?'+new URLSearchParams({source:'source-1',snapshot:renewed.metadata_sha256}));assert.equal(renewedExport.status(),200);assert.equal(sha(await renewedExport.body()),expected.projection_sha256);
  await fs.writeFile(metadataPath,originalMetadata);originalMetadata=null;await rebuild();
  await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='5');
  check('changed_synthetic_metadata_invalidates_snapshot_explicit_reindex_restores_consistency');
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);check('no_javascript_errors_or_automatic_external_requests');
  report.status='PASS_SCOPED';
}catch(error){failure=error;report.error=error.stack||error.message;}
finally{
  if(originalMetadata)await fs.writeFile(metadataPath,originalMetadata);
  if(browser)await browser.close();
  await fs.mkdir(path.dirname(reportPath),{recursive:true});await fs.writeFile(reportPath,JSON.stringify(report,null,2));
  console.log(JSON.stringify(report,null,2));
}
if(failure)process.exitCode=1;
