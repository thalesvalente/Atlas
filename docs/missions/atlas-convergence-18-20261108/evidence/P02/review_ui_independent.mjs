/** P02 independent regression probes. Actual app functions + real Catalog DTOs.
 * Minimal DOM model (including select option membership), not browser QA.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const area=path.dirname(fileURLToPath(import.meta.url));
const repo=process.env.ATLAS_TEST_REPO||path.resolve(area,'../../repo');
const appPath=path.join(repo,'packages/atlas/src/atlas_viewer/static/app.js');
const app=fs.readFileSync(appPath,'utf8');
const sha256=text=>crypto.createHash('sha256').update(text).digest('hex');
const fixtures=JSON.parse(fs.readFileSync(path.join(area,'catalog_scenarios.json'),'utf8'));
const tick=()=>new Promise(resolve=>setImmediate(resolve));
const clone=value=>structuredClone(value);
class Element {
 constructor(tag='div'){this.tagName=tag;this._text='';this._value='';this.children=[];this.hidden=false;this.disabled=false;this.dataset={};this.classList={toggle(){},add(){},remove(){}};this.attributes={};}
 get textContent(){return this._text+this.children.map(x=>typeof x==='string'?x:x.textContent).join('');}
 set textContent(value){this._text=String(value);this.children=[];}
 get value(){return this._value;}
 set value(value){this._value=this.tagName==='select'&&!this.children.some(x=>x.value===value)?'':value;}
 append(...children){this.children.push(...children);}
 replaceChildren(...children){this._text='';this.children=children;if(this.tagName==='select')this._value='';}
 addEventListener(){}setAttribute(k,v){this.attributes[k]=v;}removeAttribute(k){delete this.attributes[k];}querySelectorAll(){return[];}focus(){this.focused=true;}scrollIntoView(){}
}
function harness(saved=null,{blockedStorage=false}={}){
 const nodes=new Map(),requests=[];let stored=saved,active=0,maxActive=0;
 const node=id=>{if(!nodes.has(id)){const e=new Element(id.endsWith('-filter')?'select':'div');if(id==='status-filter')for(const value of ['', 'COMPLETED','FAILED','UNKNOWN']){const o=new Element('option');o.value=value;e.append(o);}nodes.set(id,e);}return nodes.get(id);};
 const sandbox={document:{getElementById:node,createElement:tag=>new Element(tag),querySelectorAll:()=>[],addEventListener(){},body:new Element('body')},localStorage:{getItem(){if(blockedStorage)throw Error('storage unavailable');return stored;},setItem(_,value){if(blockedStorage)throw Error('storage unavailable');stored=value;}},window:{print(){}},URL,setTimeout,
 fetch:(url,options)=>new Promise((resolve,reject)=>{active++;maxActive=Math.max(maxActive,active);requests.push({url,method:options?.method||'GET',resolve:data=>{active--;resolve(data);},reject:error=>{active--;reject(error);}});})};
 vm.createContext(sandbox);
 vm.runInContext(app+`\nfor(const name of ['renderRuns','renderComparison','renderTimeline','renderLineage'])globalThis[name]=()=>{};globalThis.review={state,updateCatalog,showDetail,savePreferences,restorePreferences,filteredRuns,load};`,sandbox);
 const api=sandbox.review;
 const respond=(i,data)=>requests[i].resolve({ok:true,json:async()=>clone(data)});
 async function ready(data=fixtures.unchanged_rebuild){await tick();respond(0,data);await tick();}
 function choose(){const a=api.state.runs.find(r=>r._sourceId==='source-1'),b=api.state.runs.find(r=>r._sourceId==='source-2');api.state.selected.add(a._key);api.state.selected.add(b._key);api.showDetail(a);node('project-filter').value=JSON.stringify(['source-1',a.project_id]);node('experiment-filter').value=JSON.stringify(['source-1',a.experiment_id]);node('search').value='run';node('status-filter').value='COMPLETED';return{a,b};}
 return {...api,node,ready,respond,requests,choose,saved:()=>stored,maxActive:()=>maxActive};
}
const records=[];
async function check(name,fn){try{await fn();records.push({name,status:'PASS'});}catch(e){records.push({name,status:'FAIL',error:e.stack});}}
await check('actual_GET_verification_preserves_A_B_and_original_detail_with_changed_notice',async()=>{
 const h=harness();await h.ready();const {a,b}=h.choose();h.updateCatalog(clone(fixtures.verify_changed));
 assert.deepEqual([...h.state.selected],[a._key,b._key]);assert.equal(h.state.detail,a._key);assert.equal(h.node('detail').hidden,false);
 assert.ok(h.node('detail-content').textContent.includes(a.name));assert.ok(!h.node('detail-content').textContent.includes('P02_CHANGED_SAME_ID'));
 assert.notEqual(h.node('project-filter').value,'');assert.equal(h.node('change-notice').hidden,false);
 assert.ok(h.node('indexed-at').textContent.includes(fixtures.verify_changed.observed_at));
});
await check('actual_changed_rebuild_same_ID_clears_all_and_persists_new_binding_B_unchanged',async()=>{
 const h=harness();await h.ready();h.choose();h.savePreferences();const oldSaved=JSON.parse(h.saved());
 h.updateCatalog(clone(fixtures.changed_rebuild));assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);assert.equal(h.node('detail').hidden,true);assert.equal(h.node('detail-content').textContent,'');
 assert.equal(h.node('project-filter').value,'');assert.equal(h.node('experiment-filter').value,'');assert.equal(h.node('search').value,'run');assert.equal(h.node('status-filter').value,'COMPLETED');
 assert.equal(h.state.runs[0].name,'P02_CHANGED_SAME_ID');assert.deepEqual(h.state.catalog.sources[1].read_model,fixtures.unchanged_rebuild.sources[1].read_model);
 const saved=JSON.parse(h.saved());assert.notEqual(saved.snapshot,oldSaved.snapshot);assert.equal(saved.project,'');assert.equal(saved.experiment,'');assert.match(h.node('notice').textContent,/Novo snapshot/);
});
await check('same_bytes_explicit_rebuild_and_fresh_process_invalidate_context',async()=>{
 for(const [before,after] of [[fixtures.initial,fixtures.unchanged_rebuild],[fixtures.initial,fixtures.restarted]]){const h=harness();await h.ready(before);h.choose();h.updateCatalog(clone(after));assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);assert.equal(h.node('project-filter').value,'');}
});
await check('ordered_source_digest_binding_detects_reassignment_even_when_epoch_fields_reused',async()=>{
 const h=harness();await h.ready(fixtures.changed_rebuild);h.choose();const next=clone(fixtures.reordered_restart);next.generation=h.state.catalog.generation;next.indexed_at=h.state.catalog.indexed_at;
 h.updateCatalog(next);assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);assert.equal(h.node('project-filter').value,'');assert.equal(h.state.runs[0].name,'Coleta simulada A');
});
await check('real_catalog_preferences_reload_same_epoch_then_restart_cannot_rebind_ordinal',async()=>{
 const h=harness();await h.ready(fixtures.changed_rebuild);h.choose();h.savePreferences();const saved=h.saved();
 const same=harness(saved);await same.ready(fixtures.changed_rebuild);assert.notEqual(same.node('project-filter').value,'');assert.notEqual(same.node('experiment-filter').value,'');assert.equal(same.filteredRuns()[0].name,'P02_CHANGED_SAME_ID');
 const other=harness(saved);await other.ready(fixtures.reordered_restart);assert.equal(other.node('project-filter').value,'');assert.equal(other.node('experiment-filter').value,'');assert.equal(other.node('search').value,'run');assert.equal(other.node('status-filter').value,'COMPLETED');
 assert.equal(new Set(other.filteredRuns().map(r=>r._sourceId)).size,2);
});
await check('legacy_or_blocked_localStorage_never_restores_unbound_source_filters',async()=>{
 const a=fixtures.initial.sources[0].read_model.runs[0];const legacy=JSON.stringify({query:'run',status:'COMPLETED',project:JSON.stringify(['source-1',a.project_id]),experiment:JSON.stringify(['source-1',a.experiment_id])});
 const h=harness(legacy);await h.ready();assert.equal(h.node('project-filter').value,'');assert.equal(h.node('experiment-filter').value,'');assert.equal(h.node('search').value,'run');
 const blocked=harness(legacy,{blockedStorage:true});await blocked.ready();blocked.choose();blocked.savePreferences();blocked.updateCatalog(clone(fixtures.changed_rebuild));assert.equal(blocked.state.selected.size,0);assert.equal(blocked.node('project-filter').value,'');
});
await check('HTTP_and_JSON_failures_do_not_break_serial_queue_or_release_refresh_early',async()=>{
 const h=harness();await h.ready();h.choose();const get=h.load(false),post=h.load(true),verify=h.load(false);await tick();
 assert.equal(h.requests.length,2);h.requests[1].resolve({ok:false,status:503});await get;await tick();assert.equal(h.requests.length,3);assert.equal(h.requests[2].method,'POST');assert.equal(h.node('refresh').disabled,true);
 h.respond(2,fixtures.changed_rebuild);await post;await tick();assert.equal(h.requests.length,4);assert.equal(h.requests[3].method,'GET');assert.equal(h.node('refresh').disabled,true);
 h.requests[3].resolve({ok:true,json:async()=>{throw Error('synthetic malformed JSON');}});await verify;assert.equal(h.state.catalog.generation,fixtures.changed_rebuild.generation);assert.equal(h.state.runs[0].name,'P02_CHANGED_SAME_ID');assert.equal(h.node('refresh').disabled,false);assert.equal(h.maxActive(),1);assert.match(h.node('notice').textContent,/synthetic malformed JSON/);
 const recovered=h.load(false);await tick();h.respond(4,fixtures.changed_rebuild);await recovered;assert.equal(h.node('refresh').disabled,false);assert.ok(!h.node('notice').textContent.includes('synthetic malformed JSON'));
});
await check('initial_request_error_allows_queued_rebuild_to_initialize_and_restore_free_preferences',async()=>{
 const h=harness(JSON.stringify({query:'run',status:'COMPLETED'}));await tick();const post=h.load(true);h.requests[0].reject(new Error('synthetic initial failure'));await tick();assert.equal(h.requests[1].method,'POST');h.respond(1,fixtures.changed_rebuild);await post;
 assert.equal(h.state.catalog.generation,fixtures.changed_rebuild.generation);assert.equal(h.node('search').value,'run');assert.equal(h.node('status-filter').value,'COMPLETED');assert.equal(h.node('refresh').disabled,false);assert.equal(h.maxActive(),1);
});
await check('declared_publication_and_observation_dates_render_separately_without_fabrication',async()=>{
 const h=harness();await h.ready();assert.match(h.node('sources-content').textContent,/Publicação declarada do pacote/);assert.ok(h.node('sources-content').textContent.includes(fixtures.unchanged_rebuild.sources[0].read_model.source.date_published));
 const empty=clone(fixtures.unchanged_rebuild);delete empty.sources[0].read_model.source.date_published;h.updateCatalog(empty);assert.ok(h.node('sources-content').textContent.includes('Publicação declarada do pacoteAusente'));
 assert.ok(h.node('dossier-summary').textContent.includes('índice gerado em '+empty.indexed_at));assert.ok(h.node('dossier-summary').textContent.includes('consulta em '+empty.observed_at));
});
const result={reviewer:'/root/p02_ui',author:'/root',status:records.every(r=>r.status==='PASS')?'PASS_SCOPED':'FAIL',scope:'Real app state/render-detail/source/date functions with actual public synthetic Catalog DTOs and minimal DOM model. Not browser/HTTP/wheel/host certification.',app_sha256:sha256(app),fixtures_sha256:sha256(fs.readFileSync(path.join(area,'catalog_scenarios.json'))),tests:records,code_stable:sha256(fs.readFileSync(appPath))===sha256(app)};
fs.writeFileSync(path.join(area,'P02-UI-INDEPENDENT-CHECKS.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
process.exitCode=result.status==='PASS_SCOPED'&&result.code_stable?0:1;
