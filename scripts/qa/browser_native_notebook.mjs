import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const url=args.get('--url'),reportPath=args.get('--report'),origin=new URL(url).origin;
assert.ok(['127.0.0.1','localhost'].includes(new URL(url).hostname));
const report={status:'FAIL',checks:[],errors:[],external_requests:[]},check=name=>report.checks.push(name);
let browser,failure;
try{
  browser=await chromium.launch({headless:true});
  const context=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
  await context.route('**/*',async route=>{const u=route.request().url();if(/^https?:/.test(u)&&new URL(u).origin!==origin){report.external_requests.push(u);await route.abort();}else await route.continue();});
  const page=await context.newPage();page.on('pageerror',e=>report.errors.push(e.message));
  await page.goto(url,{waitUntil:'networkidle'});await page.getByTestId('native-notebook-nav').click();
  await page.waitForFunction(()=>document.getElementById('native-record-count')?.textContent==='2');
  assert.equal(await page.locator('iframe').count(),0);
  assert.match(await page.locator('#native-revision').innerText(),/test-invented-revision/);
  assert.equal(await page.locator('#native-node-count').innerText(),'1202');
  assert.equal(await page.locator('#native-table-count').innerText(),'1 / 127');
  // The historical R4 renderer is now an optional native view, not an
  // imported HTML page. Verify semantic grouping and return to the complete
  // structural tree before the existing 1202-node regression.
  await page.getByRole('button',{name:'Mapa por temas e famílias (R4)'}).click();
  assert.equal(await page.locator('.r4-map').count(),1);
  assert.ok(await page.locator('.r4-map-root').isVisible());
  await page.getByRole('combobox',{name:'Organização do mapa'}).selectOption('native');
  const family=page.locator('.r4-map-family').first();
  assert.ok(await family.isVisible());
  // Duplicate source IDs and an explicitly null endpoint must NOT turn into
  // a false relation, even if filters leave only one candidate visible.
  await page.getByRole('checkbox',{name:'Mostrar relações declaradas'}).check();
  assert.equal(await page.locator('.r4-map-svg path[stroke="#278f97"]').count(),0);
  await family.focus();
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('data-r4-id')),
    await family.getAttribute('data-r4-id'),'Keyboard focus must survive family redraw');
  const expandedRecords=page.locator('.r4-map-record');
  assert.equal(await expandedRecords.count(),2);
  // Choose the exact declared record, not the first item sorted by title
  // (the second synthetic record contains hostile HTML-looking text).
  await page.locator('.r4-map-record[aria-label="Registro A"]').click();
  assert.match(await page.locator('#native-detail-body').innerText(),/Registro A/);
  assert.equal(await page.evaluate(()=>window.nativeInjected),undefined);
  await page.locator('#native-close-detail').click();
  await page.getByRole('button',{name:'Nós estruturais do Caderno'}).click();
  assert.equal(await page.locator('.r4-map').count(),0);
  check('r4_visual_renderer_port_native_themes_and_reversible_structural_switch');
  const initialGraph=await page.locator('.graph-meta').innerText();
  assert.match(initialGraph,/1202 nós carregados/);
  assert.match(initialGraph,/25 no foco atual/);
  assert.ok(await page.locator('.graph-node').count()<=25,'First view must not render all 1202 nodes');
  const initialRoot=page.getByRole('treeitem',{name:'Família',exact:true});
  assert.ok(await initialRoot.isVisible());
  const geometry=await initialRoot.boundingBox();
  assert.ok(geometry.width>=170&&geometry.height>=40,'Large tree must open with readable nodes, not 0.5 percent fit');
  check('exporter_output_reaches_installed_native_ui_with_readable_tree_without_iframe');
  await page.getByRole('button',{name:'Mostrar mais nós +24'}).click();
  assert.match(await page.locator('.graph-meta').innerText(),/49 no foco atual/);
  check('large_tree_initial_focus_progressively_reveals_siblings');
  const search=page.getByRole('searchbox',{name:'Localizar nó na árvore'});
  await search.fill('Família');await page.getByRole('button',{name:'Localizar / próximo',exact:true}).click();
  const rootNode=page.getByRole('treeitem',{name:'Família',exact:true});
  await rootNode.dblclick();assert.equal(await rootNode.getAttribute('aria-expanded'),'false');
  await rootNode.dblclick();assert.equal(await rootNode.getAttribute('aria-expanded'),'true');
  await rootNode.focus();await page.keyboard.press('Space');assert.equal(await rootNode.getAttribute('aria-expanded'),'false');
  await page.keyboard.press('Space');assert.equal(await rootNode.getAttribute('aria-expanded'),'true');
  check('double_click_and_keyboard_toggle_preserve_node_target_and_focus');
  await search.fill('Último nó da coleção');await page.getByRole('button',{name:'Localizar / próximo',exact:true}).click();
  assert.match(await page.locator('#native-detail-body').innerText(),/native-1199/);
  assert.equal(await page.locator('.graph-node[aria-selected="true"][aria-label="Último nó da coleção"]').count(),1);
  check('search_reaches_last_node_beyond_initial_24_siblings');
  const transform=await page.locator('.graph-svg > g').getAttribute('transform');
  await page.getByRole('button',{name:'Ampliar +',exact:true}).click();assert.notEqual(await page.locator('.graph-svg > g').getAttribute('transform'),transform);
  assert.ok(await page.locator('.graph-mini').isVisible());
  for(let i=0;i<6;i++){await page.getByRole('button',{name:'Reduzir −',exact:true}).click();await page.getByRole('button',{name:'Ampliar +',exact:true}).click();}
  check('all_1202_nodes_searchable_with_zoom_and_minimap');
  const labelGeometry=await page.evaluate(async()=>{
    const {mountGraph}=await import('/native_graph.js'),host=document.createElement('div');
    host.style.width='600px';document.body.append(host);
    const node={uid:'wide-label-test',title:'W'.repeat(100)+' 🧪',native_id:null,source_key:'source-key/'.repeat(50)};
    let selected;const graph=mountGraph(host,[node],value=>{selected=value;});
    try{
      graph.locate(node.uid);const item=host.querySelector('.graph-node'),title=item.querySelector('.node-title'),identity=item.querySelector('.meta');
      return {titleWidth:title.getComputedTextLength(),identityWidth:identity.getComputedTextLength(),titleTooltip:title.querySelector('title').textContent,identityTooltip:identity.querySelector('title').textContent,accessibleName:item.getAttribute('aria-label'),sameOccurrence:selected===node,nativeId:selected.native_id};
    }finally{graph.destroy();host.remove();}
  });
  assert.ok(labelGeometry.titleWidth<=234&&labelGeometry.identityWidth<=234,'Visual labels must fit inside the card');
  assert.equal(labelGeometry.titleTooltip,'W'.repeat(100)+' 🧪');assert.equal(labelGeometry.accessibleName,labelGeometry.titleTooltip);
  assert.equal(labelGeometry.identityTooltip,'source-key/'.repeat(50));assert.equal(labelGeometry.sameOccurrence,true);assert.equal(labelGeometry.nativeId,null);
  check('wide_titles_and_long_keys_fit_cards_without_changing_original_identity');
  await page.locator('[data-pane="records"]').click();await page.locator('#native-status').selectOption('HOLD');
  assert.equal(await page.locator('#native-content tbody tr').count(),1);await page.locator('#native-clear').click();
  assert.equal(await page.locator('#native-content tbody tr').count(),2);assert.equal(await page.locator('#native-content img').count(),0);
  assert.equal(await page.evaluate(()=>window.nativeInjected),undefined);
  await page.locator('#native-content tbody tr').first().getByRole('button').click();assert.match(await page.getByTestId('native-raw').innerText(),/"id":"same"/);
  check('duplicate_ids_preserved_status_filter_and_text_only_details');
  await page.locator('[data-pane="tables"]').click();const table=page.locator('[data-component="parity02-p03-table"]');
  assert.ok(await table.isVisible());assert.equal(await table.locator('tbody tr').count(),100);
  const tableText=await table.innerText();assert.ok(tableText.includes('9007199254740993'));
  assert.ok(tableText.includes('NULL — valor declarado'));assert.ok(tableText.includes('MISSING — chave ausente'));
  await page.getByRole('button',{name:'Próxima →',exact:true}).click();assert.equal(await table.locator('tbody tr').count(),27);
  check('reused_p03_exact_numbers_null_missing_and_all_pages');
  await page.getByRole('button',{name:'Detalhes da tabela',exact:true}).click();
  const tableRaw=await page.getByTestId('native-raw').innerText();
  assert.ok(tableRaw.includes('"Inteiro":9007199254740993'));
  assert.equal(JSON.parse(tableRaw).rows.length,127);
  let tableDownloadPromise=page.waitForEvent('download');
  await page.getByRole('button',{name:'Exportar esta ocorrência',exact:true}).click();
  const tableDownload=await tableDownloadPromise;
  const tableBytes=await fs.readFile(await tableDownload.path());
  assert.equal(createHash('sha256').update(tableBytes).digest('hex'),args.get('--expected-table-digest'));
  assert.equal(JSON.parse(tableBytes).rows.length,127);
  check('table_detail_and_occurrence_export_contain_all_rows_exactly_without_rounding');
  let waiting=page.waitForEvent('download');await page.getByRole('button',{name:'JSON das linhas selecionadas',exact:true}).click();
  let download=await waiting;let bytes=await fs.readFile(await download.path());assert.ok(bytes.toString().includes('9007199254740993'));assert.equal(JSON.parse(bytes).length,127);
  waiting=page.waitForEvent('download');await page.getByRole('button',{name:'CSV protegido',exact:true}).click();download=await waiting;bytes=await fs.readFile(await download.path());
  assert.ok(bytes.toString().includes("'=1+1"));check('json_rows_not_rounded_and_csv_formula_neutralized');
  await page.locator('[data-pane="assets"]').click();await page.getByRole('button',{name:'Ver referência e detalhes'}).first().click();assert.match(await page.getByTestId('native-raw').innerText(),/private\/never-opened/);
  await page.locator('[data-pane="timeline"]').click();assert.match(await page.locator('#native-content').innerText(),/2026-01-01T12:00:00Z/);assert.match(await page.locator('#native-content').innerText(),/Data não declarada/);
  await page.locator('[data-pane="coverage"]').click();assert.match(await page.locator('#native-content').innerText(),/unknown_nested/);
  await page.locator('[data-pane="relations"]').click();assert.equal(await page.locator('#native-content tbody tr').count(),1);check('resources_relations_timeline_and_unknown_collections_available');
  await page.locator('#native-source').selectOption('source-2');assert.match(await page.locator('#native-revision').innerText(),/separate-invented-source/);assert.equal(await page.locator('#native-table-count').innerText(),'1 / 2');assert.ok(await page.locator('#native-detail').isHidden());
  await page.locator('#native-source').selectOption('source-1');waiting=page.waitForEvent('download');await page.locator('#native-download').click();download=await waiting;bytes=await fs.readFile(await download.path());
  assert.equal(createHash('sha256').update(bytes).digest('hex'),args.get('--expected-digest'));check('source_switch_clears_selection_and_full_export_matches_original_projection');
  const rebuilt=page.waitForResponse(r=>r.url()===origin+'/api/reindex'&&r.request().method()==='POST');
  const reloaded=page.waitForEvent('load');
  await page.locator('#native-rebuild').click();assert.equal((await rebuilt).status(),200);await reloaded;
  await page.waitForFunction(()=>document.getElementById('native-node-count')?.textContent==='1202');
  check('explicit_update_button_rebuilds_fixed_source_catalog');
  await page.locator('[data-pane="tree"]').click();await fs.mkdir(path.dirname(reportPath),{recursive:true});
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:reportPath.replace('.json','-desktop.png'),fullPage:true});
  await page.locator('[data-pane="tables"]').click();
  if(await page.locator('#native-close-detail').isVisible())await page.locator('#native-close-detail').click();
  await page.evaluate(()=>window.scrollTo(0,0));
  await page.screenshot({path:reportPath.replace('.json','-tables.png'),fullPage:false});
  await page.setViewportSize({width:390,height:844});await page.locator('[data-pane="records"]').click();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await page.screenshot({path:reportPath.replace('.json','-mobile.png'),fullPage:true});
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);check('mobile_reflow_no_page_errors_and_no_external_requests');
  report.status='PASS_SCOPED';
}catch(e){failure=e;report.error=e.stack||e.message;}
finally{if(browser)await browser.close();await fs.mkdir(path.dirname(reportPath),{recursive:true});await fs.writeFile(reportPath,JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));}
if(failure)process.exitCode=1;
