/* Real Chromium component proof over invented, explicitly typed occurrences.
 * --module-dir can point at the installed wheel's static resource directory.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url),{chromium}=require('playwright');
const args=new Map();for(let i=2;i<process.argv.length;i+=2)args.set(process.argv[i],process.argv[i+1]);
const moduleDir=args.get('--module-dir')||path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../packages/atlas/src/atlas_viewer/static');
const reportPath=args.get('--report');assert.ok(reportPath,'--report is required');
const report={status:'FAIL',scope:'SYNTHETIC_LINEAGE_COMPONENT_NOT_PRIVATE_HOST_ACCEPTANCE',checks:[],errors:[],external_requests:[]},check=name=>report.checks.push(name);
const scalar=(name,type,text)=>({name,type,text});
const occurrence=(uid,kind,group,title,fields=[],extra={})=>({uid,kind,group,title,fields,raw_json:'{}',native_id:null,source_key:null,...extra});
const node=(uid,key,title)=>occurrence(uid,'node','lineage_graph.nodes',title,[scalar('key','string',key)],{source_key:key});
const relation=(uid,fields,group='lineage_graph.edges',raw='{}')=>occurrence(uid,'relation',group,'Relação inventada '+uid,fields,{raw_json:raw});
const entries=[node('a','alpha','Alpha inventado'),node('b','beta','Beta inventado'),node('collision-1','same','Candidato um'),node('collision-2','same','Candidato dois'),
  occurrence('other-group','record','records','Mesmo literal em outro namespace',[scalar('id','string','alpha')],{native_id:'alpha',source_key:'alpha'}),
  occurrence('numeric','record','records','Inteiro exato',[scalar('id','integer','9007199254740993')],{native_id:'9007199254740993'}),
  occurrence('string-number','record','records','Texto semelhante ao inteiro',[scalar('id','string','9007199254740993')],{native_id:'9007199254740993',source_key:'9007199254740993'}),
  occurrence('alias','record','records','Registro com alias declarado',[],{raw_json:'{"source_ids":["declared-alias",9007199254740993]}'})];
entries.push(relation('resolved',[scalar('from_key','string','alpha'),scalar('to_key','string','beta'),scalar('type','string','mentions'),scalar('causal_status','string','UNKNOWN')]));
entries.push(relation('collision',[scalar('from_key','string','same'),scalar('to_key','string','beta'),scalar('type','string','contains')]));
entries.push(relation('null',[scalar('from_key','null','null'),scalar('from','string','alpha'),scalar('to_key','string','beta'),scalar('type','string','declared-null')]));
entries.push(relation('missing',[scalar('from_key','string','not-present'),scalar('type','string','missing-endpoint')]));
entries.push(relation('numeric-ref',[scalar('from','integer','9007199254740993'),scalar('to','string','9007199254740993'),scalar('type','string','literal-reference')],'edges'));
entries.push(relation('alias-ref',[scalar('from','string','declared-alias'),scalar('to','string','not-present'),scalar('type','string','alias-reference')],'edges'));
entries.push(relation('composite',[scalar('from','string','alpha'),scalar('to_key','string','beta'),scalar('type','string','composite-key')],'lineage_graph.edges','{"from":"alpha","from_key":["alpha"],"to_key":"beta","type":"composite-key"}'));
entries.push(relation('collision-alias',[scalar('from','string','alpha'),scalar('to','string','beta'),scalar('type','string','unscoped-reference')],'edges'));
entries.push(relation('self-loop',[scalar('from_key','string','alpha'),scalar('to_key','string','alpha'),scalar('type','string','self-reference')]));
for(let i=0;i<13;i++)entries.push(relation('page-'+i,[scalar('from_key','string','alpha'),scalar('to_key','string','beta'),scalar('type','string',i===12?'last-evidence':'page-reference')]));
entries.push(relation('text-only',[scalar('from_key','string','alpha'),scalar('to_key','string','beta'),scalar('type','string','<img src=x onerror=window.lineageInjected=1>')]));
const assets=new Map([['/native_lineage.js','text/javascript'],['/native_navigation.js','text/javascript'],['/native_notebook.css','text/css']]);
const server=http.createServer(async(req,res)=>{
  if(req.url==='/'){res.writeHead(200,{'Content-Type':'text/html','Content-Security-Policy':"default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self'; base-uri 'none'"});res.end('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="/native_notebook.css"><main><div id="lineage"></div><output id="chosen"></output></main>');return;}
  if(!assets.has(req.url)){res.writeHead(404);res.end();return;}
  try{const bytes=await fs.readFile(path.join(moduleDir,req.url.slice(1)));res.writeHead(200,{'Content-Type':assets.get(req.url)});res.end(bytes);}catch{res.writeHead(404);res.end();}
});
let browser;
try{
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));const origin='http://127.0.0.1:'+server.address().port;
  browser=await chromium.launch({headless:true});const context=await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route('**/*',async route=>{const url=route.request().url();if(/^https?:/.test(url)&&new URL(url).origin!==origin){report.external_requests.push(url);await route.abort();}else await route.continue();});
  const page=await context.newPage();page.on('pageerror',error=>report.errors.push(error.message));await page.goto(origin,{waitUntil:'networkidle'});
  const summary=await page.evaluate(async entries=>{
    const {buildLineage,mountLineage}=await import('/native_lineage.js'),before=JSON.stringify(entries),model=buildLineage(entries);
    window.lineage=mountLineage(document.querySelector('#lineage'),entries,entry=>{window.chosenEntry=entry;document.querySelector('#chosen').textContent=entry.uid;});
    return {unchanged:before===JSON.stringify(entries),model:model.map(item=>({uid:item.relation.uid,type:item.type,from:{status:item.from.status,candidates:item.from.candidates.map(match=>match.entry.uid)},to:{status:item.to.status,candidates:item.to.candidates.map(match=>match.entry.uid)}}))};
  },entries);
  assert.equal(summary.unchanged,true);const byId=new Map(summary.model.map(item=>[item.uid,item]));
  assert.deepEqual(byId.get('resolved').from.candidates,['a']);assert.equal(byId.get('resolved').to.status,'RESOLVED');
  assert.equal(byId.get('collision').from.status,'COLLISION');assert.equal(byId.get('collision').from.candidates.length,2);
  assert.equal(byId.get('null').from.status,'EXPLICIT_NULL');assert.deepEqual(byId.get('null').from.candidates,[]);
  assert.equal(byId.get('missing').from.status,'UNRESOLVED');assert.equal(byId.get('missing').to.status,'NOT_SCALAR_OR_ABSENT');
  assert.equal(byId.get('composite').from.status,'NOT_INTERPRETED');assert.deepEqual(byId.get('composite').from.candidates,[]);
  check('scoped_keys_collisions_null_missing_and_composite_endpoints_stay_distinct');
  assert.deepEqual(byId.get('numeric-ref').from.candidates,['numeric']);assert.deepEqual(byId.get('numeric-ref').to.candidates,['string-number']);
  assert.deepEqual(byId.get('alias-ref').from.candidates,['alias']);assert.equal(byId.get('collision-alias').from.status,'COLLISION');
  check('large_integer_lexemes_string_ids_and_explicit_aliases_never_coerce');
  assert.equal(await page.locator('[data-lineage-relation]').count(),6);assert.match(await page.locator('.graph-meta').innerText(),new RegExp('de '+summary.model.length+' relações'));
  assert.ok(await page.locator('[data-lineage-edges] path').count()>0);assert.equal(await page.locator('iframe').count(),0);
  const lanePositions=await page.locator('[data-lineage-relation] > text').evaluateAll(labels=>labels.map(label=>label.getAttribute('y')));
  assert.equal(new Set(lanePositions).size,lanePositions.length,'Parallel relation labels must have distinct visible lanes');
  await page.locator('[data-lineage-relation="resolved"]').focus();await page.keyboard.press('Enter');assert.equal(await page.locator('#chosen').innerText(),'resolved');
  assert.match(await page.locator('[data-lineage-selection]').innerText(),/UNKNOWN/);
  await page.locator('[data-lineage-endpoint="entry:a"]').focus();await page.keyboard.press('Space');assert.equal(await page.locator('#chosen').innerText(),'a');
  check('typed_svg_edges_and_endpoint_keyboard_selection_reach_original_occurrences');
  await page.evaluate(()=>window.lineage.locate('collision'));await page.getByRole('button',{name:'Candidato dois · lineage_graph.nodes · collision-2',exact:true}).click();assert.equal(await page.locator('#chosen').innerText(),'collision-2');
  check('ambiguous_reference_requires_explicit_candidate_selection');
  await page.getByRole('button',{name:'Próximas relações →',exact:true}).click();assert.match(await page.locator('.graph-meta').innerText(),/página 2\//);
  const search=page.getByRole('searchbox',{name:'Buscar relação ou endpoint'});await search.fill('last-evidence');assert.equal(await page.locator('[data-lineage-relation]').count(),1);await search.press('Enter');assert.equal(await page.locator('#chosen').innerText(),'page-12');
  assert.equal(await page.evaluate(()=>window.lineage.locate('page-12')),true);assert.match(await page.locator('.graph-meta').innerText(),/página 4\//);
  check('pagination_and_integral_search_reach_last_relation_beyond_first_window');
  await page.getByRole('combobox',{name:'Tipo de relação declarada'}).selectOption('mentions');assert.equal(await page.locator('[data-lineage-relation]').count(),1);
  await page.getByRole('button',{name:'Ampliar relações +',exact:true}).click();let transform=await page.locator('.graph-svg > g').getAttribute('transform');await page.locator('.graph-svg').focus();await page.keyboard.press('ArrowRight');assert.notEqual(await page.locator('.graph-svg > g').getAttribute('transform'),transform);
  check('type_filter_zoom_and_keyboard_pan_work');
  await page.getByRole('combobox',{name:'Tipo de relação declarada'}).selectOption('self-reference');assert.equal(await page.locator('[data-lineage-endpoint]').count(),1);assert.equal(await page.locator('[data-lineage-relation]').count(),1);check('self_reference_preserves_one_endpoint_occurrence');
  await page.evaluate(()=>window.lineage.locate('text-only'));assert.equal(await page.locator('[data-lineage-selection] img').count(),0);assert.equal(await page.evaluate(()=>window.lineageInjected),undefined);
  await fs.mkdir(path.dirname(reportPath),{recursive:true});await page.screenshot({path:reportPath.replace('.json','-desktop.png'),fullPage:true});
  for(const width of [390,320]){await page.setViewportSize({width,height:844});await page.getByRole('button',{name:'Centralizar origem',exact:true}).click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.screenshot({path:reportPath.replace('.json','-mobile-'+width+'.png'),fullPage:true});}
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);check('mobile_layout_text_only_types_no_errors_and_no_external_requests');report.status='PASS_SCOPED';
}catch(error){report.error=error.stack||String(error);process.exitCode=1;}
finally{await browser?.close();await new Promise(resolve=>server.close(resolve));await fs.mkdir(path.dirname(reportPath),{recursive:true});await fs.writeFile(reportPath,JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));}
