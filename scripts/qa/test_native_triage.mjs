/** Feature 005: synthetic, read-only domain tests. No browser/physical claims. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {performance} from 'node:perf_hooks';
import {nativeFragments} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {makePresentation,recordExecutionState,recordExecutionPresentation,recordMatches} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';
import {createTriageModel,SelectionLedger,selectionKey,snapshotKey,entryType} from '../../packages/atlas/src/atlas_viewer/static/native_triage_model.js';
import {RETENTION_INTENTS,buildRetentionPlan,buildDossier,copyReferences} from '../../packages/atlas/src/atlas_viewer/static/native_retention.js';

function freeze(value) {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
}
function rawEntry(uid,kind,raw,extra={}) {
  const fields=[...nativeFragments(raw,{all:true})].filter(([,v])=>!['{','['].includes(v[0])).map(([name,raw])=>({
    name,type:raw==='null'?'null':raw[0]==='"'?'string':/^(true|false)$/.test(raw)?'boolean':/[.eE]/.test(raw)?'number':'integer',
    text:raw[0]==='"'?JSON.parse(raw):raw,
  }));
  const string=(...names)=>names.map(n=>fields.find(f=>f.name===n)).find(f=>f?.type==='string')?.text??null;
  return freeze({uid,kind,group:({record:'records',table:'result_tables',row:'result_tables',node:'lineage_graph.nodes',asset:'resources',relation:'edges'})[kind]??'extra',
    title:string('title','label','name','id')??kind,native_id:string('native_id','id'),source_key:string('id','key'),
    family:string('family'),status:string('execution_state','status','result_state','result_group'),date:string('started_at','date'),
    parent_uid:null,fields,raw_json:raw,...extra});
}
const entry=(uid,kind,value,extra)=>rawEntry(uid,kind,JSON.stringify(value),extra);
const source=(entries,overrides={})=>freeze({id:'synthetic-source',name:'Fixture pública inventada',revision:'SYNTHETIC-R1',metadata_sha256:'a'.repeat(64),status:'READY',entries,...overrides});
const ids=hits=>hits.map(hit=>hit.entry.uid);
const keyFor=(model,e,dimension)=>model.facet(e,dimension).key;

test('execution filter follows badge precedence and keeps documentary result separate',()=>{
  const failed=entry('failed','record',{id:'failed',kind:'run',execution_state:'FAILED',result_group:'published',publication:'published'});
  const passed=entry('passed','record',{id:'passed',kind:'run',execution_state:'SUCCEEDED',result_group:'failed',admission:'HOLD'});
  const model=createTriageModel(source([failed,passed])),legacy=makePresentation([failed,passed]).records[0];
  assert.equal(recordExecutionState(legacy),'FAILED');
  assert.equal(recordMatches(legacy,{status:'FAILED'}),false,'baseline result-group filter is documentary, not execution');
  assert.equal(model.facet(failed,'execution').label,'FAILED');
  assert.equal(model.facet(failed,'execution').tone,'failed');
  assert.deepEqual(ids(model.search({execution:keyFor(model,failed,'execution')})),['failed']);
  assert.deepEqual(ids(model.search({result_group:keyFor(model,passed,'result_group')})),['passed']);
  assert.equal(model.facet(passed,'execution').label,'SUCCEEDED');
});

test('documentary publication cannot supply an execution state on a legacy mission',()=>{
  const items=['published','PUBLISHED_PASS_WITH_WARNINGS','NOT_PUBLISHED','SNAPSHOT_PUBLISHED'].map((value,i)=>
    entry('document'+i,'record',{kind:'mission',result_group:value,result:value,publication:'UNKNOWN'}));
  const model=createTriageModel(source(items));
  for(const e of items){
    const raw=JSON.parse(e.raw_json),execution=model.facet(e,'execution');
    assert.equal(execution.present,false);
    assert.equal(execution.raw,null);
    assert.equal(execution.tone,'neutral');
    assert.equal(recordExecutionPresentation(raw).state,undefined);
    assert.deepEqual(ids(model.search({result_group:keyFor(model,e,'result_group')})),[e.uid]);
    assert.equal(model.facet(e,'publication').raw,'"UNKNOWN"');
  }
  assert.equal(model.options('execution').length,1);
  const plan=buildRetentionPlan(source(items),items);
  assert.deepEqual(plan.items.map(item=>item.raw_json),items.map(e=>e.raw_json));
  assert.equal(plan.items[0].declared.results.find(value=>value.field==='result_group').raw_json,'"published"');
});

test('legacy execution tokens still drive badges and filters with their original lexemes',()=>{
  const failed=entry('legacy-failed','record',{kind:'mission',result_group:'failed',result:'PUBLISHED'});
  const resultOnly=entry('legacy-succeeded','record',{kind:'run',result:'SUCCEEDED'});
  const model=createTriageModel(source([failed,resultOnly]));
  assert.equal(model.facet(failed,'execution').raw,'"failed"');
  assert.equal(model.facet(failed,'execution').field,'result_group');
  assert.equal(model.facet(failed,'execution').tone,'failed');
  assert.equal(model.facet(resultOnly,'execution').raw,'"SUCCEEDED"');
  assert.equal(model.facet(resultOnly,'execution').field,'result');
});

test('M1.1 result is a table and a declaration does not create an execution',()=>{
  const table=entry('table','table',{id:'M1.1',label:'M1.1 · RF baseline preservada',baseline:true,rows:[]},{row_count:39});
  const result=createTriageModel(source([table])).search({query:'M1.1'})[0];
  assert.equal(result.type,'table');assert.equal(result.typeLabel,'Tabela');assert.equal(result.entry,table);
  assert(result.reasons.some(reason=>reason.field==='id'||reason.field==='title'));
  assert.equal(result.baseline.sourceConfirmed,true);
  assert.equal(createTriageModel(source([table])).facet(table,'execution').present,false);
});

test('M1, M11, M1.1 are distinct search tokens, including title-only matches',()=>{
  const items=['M1','M11','M1.1'].map((id,i)=>entry('u'+i,'table',{id,label:id+' · título inventado'}));
  const model=createTriageModel(source(items));
  for(let i=0;i<items.length;i++)assert.deepEqual(ids(model.search({query:['M1','M11','M1.1'][i]})),['u'+i]);
  assert.deepEqual(ids(model.search({query:'m1.1 título'})),['u2']);
});

test('search reasons expose the actual matching field and preserve numeric lexemes',()=>{
  const exact=rawEntry('opaque-uid','record','{"id":"R-1","kind":"run","metrics":{"integer":9007199254740993,"ratio":0.123456789012345678901},"mission":"missão-longa"}');
  const model=createTriageModel(source([exact]));
  assert(model.search({query:'9007199254740993'})[0].reasons.some(r=>r.field==='metrics'&&r.value.includes('9007199254740993')));
  assert(model.search({query:'0.123456789012345678901'})[0].reasons.some(r=>r.value.includes('0.123456789012345678901')));
  assert(model.search({query:'opaque-uid'})[0].reasons.some(r=>r.field==='uid'));
  assert(model.search({query:'missao-longa'})[0].reasons.some(r=>r.field==='mission'));
});

test('typed facets distinguish absent, NULL, empty, UNKNOWN and literal missing labels',()=>{
  const values=[{}, {execution_state:null},{execution_state:''},{execution_state:'UNKNOWN'},{execution_state:'AUSENTE — campo não declarado'}];
  const items=values.map((value,i)=>entry('state'+i,'record',{kind:'run',...value}));
  const model=createTriageModel(source(items));
  assert.equal(new Set(items.map(e=>keyFor(model,e,'execution'))).size,5);
  assert.equal(model.options('execution').length,5);
  for(const e of items)assert.deepEqual(ids(model.search({execution:keyFor(model,e,'execution')})),[e.uid]);
});

test('explicit NULL and empty execution values stop precedence',()=>{
  for(const first of [null,'',false,0]){
    const e=entry('null','record',{kind:'run',execution_state:first,status:'SUCCEEDED',result_group:'published'}),model=createTriageModel(source([e]));
    assert.equal(model.facet(e,'execution').raw,JSON.stringify(first));
    assert.equal(model.facet(e,'execution').tone,'neutral');
  }
});

test('family facet retains typed identity independently from displayed labels',()=>{
  const items=[1,'1',null,'NULL — família declarada',[],{}].map((family,i)=>entry('f'+i,'record',{kind:'run',family}));
  const model=createTriageModel(source(items));
  assert.equal(model.options('family').length,items.length);
  for(const e of items)assert.deepEqual(ids(model.search({family:keyFor(model,e,'family')})),[e.uid]);
});

test('declared scientific types remain distinct; a mission is not a run',()=>{
  for(const kind of ['experiment','run','execution','attempt','mission','milestone','baseline','product','artifact','resource','document']){
    assert.equal(entryType(entry(kind,'record',{kind})).key,kind);
  }
  const unknown=entry('unknown','record',{title:'experimento SUCCEEDED baseline published M1'});
  assert.equal(entryType(unknown).key,'record');
  const model=createTriageModel(source([unknown]));assert.equal(model.facet(unknown,'kind').present,false);
});

test('kind NULL, absent and empty are not merged into an invented scientific type',()=>{
  const items=[{},{kind:null},{kind:''}].map((d,i)=>entry('k'+i,'record',d)),model=createTriageModel(source(items));
  assert.equal(model.options('kind').length,3);assert(items.every(e=>model.type(e).key==='record'));
});

test('names, success and publication never designate a baseline',()=>{
  const items=[{title:'M1 baseline published SUCCEEDED'}, {baseline:'true'}, {baseline:null}, {baseline:false}, {baseline_ref:'yes'}, {is_baseline:1}]
    .map((data,i)=>entry('no'+i,'record',{kind:'run',status:'SUCCEEDED',...data}));
  const model=createTriageModel(source(items));
  assert(items.every(e=>!model.baseline(e).sourceConfirmed&&!model.baseline(e).confirmed));
});

test('explicit baseline designation and contradictory declarations are separate',()=>{
  const yes=entry('yes','table',{baseline:true}),also=entry('also','record',{is_baseline:true}),kind=entry('kind','record',{kind:'baseline'}),
    conflict=entry('conflict','record',{baseline:true,is_baseline:false});
  const model=createTriageModel(source([yes,also,kind,conflict]));
  for(const e of [yes,also,kind])assert.equal(model.baseline(e).status,'SOURCE_DECLARED');
  assert.equal(model.baseline(conflict).status,'CONFLICT');assert.equal(model.baseline(conflict).confirmed,false);
});

test('baseline conflict explanation takes precedence while retaining the operator note',()=>{
  const e=entry('conflict-note','record',{kind:'baseline',is_baseline:false}),s=source([e]),ledger=new SelectionLedger(s),model=createTriageModel(s);
  ledger.annotateBaseline(e,'Nota');const baseline=model.baseline(e,ledger.annotations);
  assert.equal(baseline.status,'CONFLICT');assert.equal(baseline.confirmed,false);assert.equal(baseline.sourceConfirmed,false);
  assert.match(baseline.explanation,/contraditórias/);assert.equal(baseline.annotation.note,'Nota');assert.equal(baseline.operatorDesignated,true);
  const item=buildRetentionPlan(s,[e],ledger).items[0];
  assert.equal(item.baseline.explanation,baseline.explanation);
  assert.equal(item.protection.status,'PROTECTED');assert.equal(item.protection.removal_authorized,false);
  assert(item.protection.reasons.includes('BASELINE_DECLARATION_CONFLICT'));
});

test('operator baseline annotation is session-scoped, attributable and never mutates DTO',()=>{
  const e=entry('manual','table',{id:'table',label:'Tabela sem designação'}),s=source([e]),before=e.raw_json,ledger=new SelectionLedger(s),model=createTriageModel(s);
  assert(model.options('baseline').some(x=>x.key==='OPERATOR_SESSION'));
  ledger.annotateBaseline(e,'Designação pessoal para revisão do operador');
  const baseline=model.baseline(e,ledger.annotations);
  assert.equal(baseline.status,'OPERATOR_SESSION');assert.equal(baseline.sourceConfirmed,false);assert.equal(baseline.operatorDesignated,true);
  assert.deepEqual(ids(model.search({baseline:'OPERATOR_SESSION'},ledger.annotations)),['manual']);
  assert.equal(e.raw_json,before);
  assert.throws(()=>ledger.annotateBaseline(e,''),/NOTE_REQUIRED/);
  ledger.bind(source([e],{revision:'R2'}));assert.equal(ledger.annotations.size,0);
});

test('annotations from another revision cannot promote a baseline',()=>{
  const e=entry('a','record',{kind:'run'}),s=source([e]),ledger=new SelectionLedger(s);
  ledger.annotateBaseline(e,'Revisão anterior');
  assert.equal(createTriageModel(source([e],{revision:'R2'})).baseline(e,ledger.annotations).operatorDesignated,false);
});

test('multiple facets combine without conflating publication and admission',()=>{
  const items=[entry('a','record',{kind:'run',family:'F',execution_state:'FAILED',publication:'published',admission:'HOLD'}),
    entry('b','record',{kind:'run',family:'F',execution_state:'FAILED',publication:'draft',admission:'HOLD'})];
  const model=createTriageModel(source(items)),a=items[0],filters=Object.fromEntries(['execution','publication','admission','family'].map(d=>[d,keyFor(model,a,d)]));
  assert.deepEqual(ids(model.search(filters)),['a']);assert.equal(model.search({}).length,2);
  assert.equal(model.diagnose({query:'never-in-this-snapshot'}).status,'NOT_FOUND_IN_SNAPSHOT');
});

test('documentary status is distinct from execution and uses presence precedence',()=>{
  const run=entry('run','record',{kind:'run',status:'FAILED'}),table=entry('table','table',{status:'TABLE_ONLY_STATE'}),
    explicit=entry('explicit','record',{kind:'run',status:'SUCCEEDED',documentary_status:'REVIEW_PENDING'}),
    nul=entry('null','table',{documentary_status:null,status:'TABLE_ONLY_STATE'}),model=createTriageModel(source([run,table,explicit,nul]));
  assert.equal(model.facet(run,'documentary').present,false);
  assert.equal(model.facet(table,'execution').present,false);
  assert.deepEqual(ids(model.search({documentary:keyFor(model,table,'documentary')})),['table']);
  assert.equal(model.facet(nul,'documentary').raw,'null');
  assert.equal(model.facet(explicit,'execution').label,'SUCCEEDED');
  assert.equal(model.facet(explicit,'documentary').label,'REVIEW_PENDING');
});

test('publication, admission and review NULL values stop their declared fallback',()=>{
  const e=entry('null','record',{kind:'run',publication:null,publication_status:'published',admission:'',technical_admission:'ACCEPTED',review:false,review_state:'APPROVED'}),model=createTriageModel(source([e]));
  assert.equal(model.facet(e,'publication').raw,'null');assert.equal(model.facet(e,'admission').raw,'""');assert.equal(model.facet(e,'review').raw,'false');
  assert.equal(model.facet(e,'__proto__').present,false);
});

test('human_review has the A01 detail precedence independently of publication',()=>{
  const reviewed=entry('reviewed','record',{kind:'run',human_review:'PENDING',review:'APPROVED',publication:'published'}),
    absent=entry('absent','record',{kind:'run',publication:'published'}),
    nul=entry('null','record',{kind:'run',human_review:null,review:'APPROVED',publication:'published'}),
    empty=entry('empty','record',{kind:'run',human_review:'',review_state:'APPROVED',publication:'published'}),
    model=createTriageModel(source([reviewed,absent,nul,empty]));
  assert.equal(model.facet(reviewed,'review').field,'human_review');
  assert.equal(model.facet(reviewed,'review').raw,'"PENDING"');
  assert.equal(model.facet(nul,'review').raw,'null');assert.equal(model.facet(empty,'review').raw,'""');
  assert.equal(model.facet(absent,'review').present,false);
  assert.equal(model.options('review').length,4);
  assert.equal(model.options('publication').length,1);
  for(const e of [reviewed,absent,nul,empty])assert.deepEqual(ids(model.search({review:keyFor(model,e,'review')})),[e.uid]);
});

test('dossier exports declared human_review including NULL and preserves alternatives',()=>{
  const e=entry('review','record',{kind:'run',human_review:null,review_status:'APPROVED',publication:'published'}),s=source([e]);
  for(const builder of [buildRetentionPlan,buildDossier]){
    const item=builder(s,[e]).items[0];
    assert.equal(item.declared.review[0].field,'human_review');assert.equal(item.declared.review[0].raw_json,'null');
    assert.equal(item.declared.review[1].field,'review_status');assert.equal(item.declared.review[1].raw_json,'"APPROVED"');
    assert(item.gaps.some(gap=>gap.includes('human_review')&&gap.includes('NULL')));
    assert.equal(item.raw_json,e.raw_json);
  }
});

test('diagnosis distinguishes wrong type and absent requested dimensions',()=>{
  const table=entry('t','table',{id:'M1.1'}),run=entry('r','record',{id:'R',kind:'run',execution_state:'FAILED'}),model=createTriageModel(source([table,run]));
  assert.equal(model.diagnose({query:'M1.1',kind:keyFor(model,run,'kind')}).status,'TYPE_NOT_MATCHING');
  assert.equal(model.diagnose({query:'M1.1',execution:keyFor(model,run,'execution')}).status,'FIELD_ABSENT');
});

test('period filters use declared ISO dates and do not invent missing timestamps',()=>{
  const items=[{started_at:'2026-11-05T23:59:59Z'}, {started_at:'2026-11-06T00:00:00Z'}, {}, {started_at:null}, {started_at:'2026-02-30'}, {started_at:'2026-11-05T19:30:00-03:00'}]
    .map((d,i)=>entry('date'+i,'record',{kind:'run',...d})),model=createTriageModel(source(items));
  assert.deepEqual(ids(model.search({from:'2026-11-05',to:'2026-11-05'})),['date0','date5']);
  assert.deepEqual(model.search({from:'not-a-date'}),[]);
  assert.deepEqual(model.search({from:'2026-11-06',to:'2026-11-05'}),[]);
});

test('evidence filtering distinguishes references, NULL, empty and absent without physical claims',()=>{
  const items=[{}, {evidence:null},{evidence:[]},{evidence:['asset-a']},{evidence:false}].map((d,i)=>entry('ev'+i,'record',{kind:'run',...d})),model=createTriageModel(source(items));
  assert.equal(model.options('evidence').length,5);
  for(const e of items)assert.deepEqual(ids(model.search({evidence:keyFor(model,e,'evidence')})),[e.uid]);
  assert.match(model.facet(items[3],'evidence').label,/não verificada/);
});

test('only declared links are navigable and missing links are not invented from names',()=>{
  const table=entry('table','table',{id:'M1.1',record_id:'run-real'}),run=entry('run','record',{id:'run-real',kind:'run'}),
    unlinked=entry('unlinked','record',{id:'M11',title:'M1.1 similar name',kind:'experiment'}),model=createTriageModel(source([table,run,unlinked]));
  const links=model.links(table);assert.equal(links.status,'DECLARED_REFERENCES');
  assert(links.outgoing.some(link=>link.label==='record_id'&&link.resolution==='UNIQUE'&&link.targets[0]==='run'));
  assert.equal(model.links(unlinked).status,'LINK_NOT_PROVEN');
});

test('selection key includes source, revision, digest, UID and kind, never just title',()=>{
  const a=entry('a','record',{title:'Mesmo título',kind:'run'}),b=entry('b','record',{title:'Mesmo título',kind:'run'}),s=source([a,b]);
  assert.notEqual(selectionKey(s,a),selectionKey(s,b));
  for(const other of [source([a],{id:'other'}),source([a],{revision:'R2'}),source([a],{metadata_sha256:'b'.repeat(64)})])assert.notEqual(selectionKey(s,a),selectionKey(other,a));
  assert.notEqual(selectionKey(s,a),selectionKey(s,entry('a','table',{title:'Mesmo título'})));
  assert.notEqual(snapshotKey({id:'x'}),snapshotKey({id:'x',revision:null}));
});

test('visible selection and all filtered selection are distinct and preserve off-page items',()=>{
  const items=Array.from({length:205},(_,i)=>entry('u'+i,'record',{id:'R-'+i,kind:'run'})),ledger=new SelectionLedger(source(items));
  ledger.selectMany(items.slice(0,100));assert.equal(ledger.entries().length,100);
  ledger.selectMany(items.slice(100,200));assert.equal(ledger.entries().length,200);
  assert.equal(ledger.counts(items.slice(100,200),items).visible,100);
  assert.equal(ledger.counts(items.slice(100,200),items).off_page,100);
  ledger.selectMany(items);assert.equal(ledger.entries().length,205);
  ledger.toggle(items[0]);assert.equal(ledger.has(items[0]),false);assert.equal(ledger.entries().length,204);
});

test('filter changes never mutate selection and hidden counts are explicit',()=>{
  const items=[entry('a','record',{kind:'run',family:'A'}),entry('b','record',{kind:'experiment',family:'B'}),entry('c','table',{label:'Tabela'})],ledger=new SelectionLedger(source(items));
  ledger.selectMany(items);const count=ledger.counts([items[0]],[items[0],items[2]]);
  assert.equal(count.total,3);assert.equal(count.visible,1);assert.equal(count.hidden_by_filter,1);assert.equal(count.off_page,1);
  assert.equal(count.types.run,1);assert.equal(count.types.experiment,1);assert.equal(count.types.table,1);
  assert.equal(ledger.entries().length,3);ledger.clear();assert.equal(ledger.entries().length,0);
});

test('editorial grouping cannot select nonexistent descendants implicitly',()=>{
  const child=entry('child','record',{kind:'run',family:'F'}),ledger=new SelectionLedger(source([child]));
  assert.equal(ledger.toggle({uid:'editorial-family-F',kind:'group',title:'F'}),false);
  assert.equal(ledger.entries().length,0);
});

test('binding the same snapshot preserves selections with refreshed DTO references',()=>{
  const a=entry('a','record',{kind:'run'}),ledger=new SelectionLedger(source([a]));ledger.toggle(a);
  const replacement=entry('a','record',{kind:'run'}),result=ledger.bind(source([replacement]));
  assert.equal(result.invalidated,false);assert.equal(ledger.entries()[0],replacement);
});

test('source, revision or digest change invalidates selections, intentions and annotations',()=>{
  const a=entry('a','record',{kind:'run'}),s=source([a]);
  for(const delta of [{revision:'R2'},{id:'source-two'},{metadata_sha256:'c'.repeat(64)}]){
    const ledger=new SelectionLedger(s);ledger.toggle(a);ledger.setIntent(a,'KEEP_FULL');ledger.annotateBaseline(a,'Nota');
    const result=ledger.bind(source([a],delta));assert.equal(result.invalidated,true);assert.equal(result.removed,1);
    assert.equal(ledger.entries().length,0);assert.equal(ledger.intents.size,0);assert.equal(ledger.annotations.size,0);
  }
});

test('changed payload under a reused snapshot identity fails closed',()=>{
  const a=entry('a','record',{kind:'run',title:'original'}),ledger=new SelectionLedger(source([a]));ledger.toggle(a);
  const changed=entry('a','record',{kind:'run',title:'alterado'});
  assert.equal(ledger.bind(source([changed])).invalidated,true);assert.equal(ledger.entries().length,0);
});

test('unready source cannot be selected or exported',()=>{
  const a=entry('a','record',{kind:'run'}),s=source([a],{status:'CHANGED'}),ledger=new SelectionLedger(s);
  assert.equal(ledger.toggle(a),false);assert.deepEqual(createTriageModel(s).items,[]);
  assert.throws(()=>buildRetentionPlan(s,[a]),/SOURCE_NOT_READY/);
});

test('export preserves exact original JSON and literal-valued metadata',()=>{
  const e=rawEntry('exact','record','{"id":"E","kind":"experiment","execution_state":"FAILED","metrics":{"integer":9007199254740993,"decimal":0.123456789012345678901,"negative_zero":-0.0},"configuration":{"seed":9007199254740995},"code_revision":"abc123","limitations":null,"dependencies":[],"artifacts":["shared.dat"]}'),s=source([e]),ledger=new SelectionLedger(s);
  ledger.toggle(e);ledger.setIntent(e,'REVIEW_FOR_REMOVAL');const plan=buildRetentionPlan(s,ledger.entries(),ledger);
  assert.equal(plan.schema,'atlas-retention-plan/1');assert.equal(plan.version,1);assert.equal(plan.status,'PROPOSAL_ONLY');assert.equal(plan.DELETE_AUTHORIZED,'NO');
  assert.equal(plan.items[0].raw_json,e.raw_json);assert.equal(plan.items[0].intent,'REVIEW_FOR_REMOVAL');
  assert(JSON.stringify(plan.items[0].declared.metrics).includes('9007199254740993'));
  assert(JSON.stringify(plan.items[0].declared.metrics).includes('0.123456789012345678901'));
  assert.equal(plan.selection[0].source_revision,s.revision);assert.equal(plan.selection[0].source_metadata_sha256,s.metadata_sha256);
  assert.equal(plan.selection[0].selection_key,selectionKey(s,e));
  assert.equal(plan.space_estimate.label,'A medir no ambiente LOCAL');assert(!('bytes' in plan.space_estimate));
});

test('missing metadata stays absent while explicit NULL is exported and explained',()=>{
  const missing=entry('missing','record',{kind:'run'}),nul=entry('null','record',{kind:'run',metrics:null}),s=source([missing,nul]);
  const plan=buildRetentionPlan(s,[missing,nul]);
  assert(!Object.hasOwn(plan.items[0].declared,'metrics'));
  assert.equal(plan.items[1].declared.metrics[0].type,'null');assert.equal(plan.items[1].declared.metrics[0].raw_json,'null');
  assert(plan.items[0].gaps.some(x=>x.includes('Métricas')));assert(plan.items[1].gaps.some(x=>x.includes('NULL')));
});

test('table dossier includes complete exact rows without replacing the transport skeleton',()=>{
  const table=entry('t','table',{id:'M1.1',rows:[]},{row_count:2}),
    row0=rawEntry('r0','row','{"id":"RF0","cells":{"value":9007199254740993}}',{table_uid:'t',ordinal:0}),
    row1=rawEntry('r1','row','{"id":"RF1","cells":{"value":0.123456789012345678901}}',{table_uid:'t',ordinal:1}),s=source([table,row0,row1]);
  const item=buildDossier(s,[table]).items[0];assert.equal(item.raw_json,table.raw_json);
  assert.equal(item.table_rows.count,2);assert.deepEqual(item.table_rows.rows.map(row=>row.raw_json),[row0.raw_json,row1.raw_json]);
  assert.throws(()=>buildDossier(source([table,row0]),[table]),/TABLE_ROWS_INCOMPLETE/);
});

test('baseline, failed runs and unknown retention all remain protected even on removal intent',()=>{
  const items=[{baseline:true,kind:'run'},{execution_state:'FAILED',kind:'run'},{kind:'artifact'}].map((data,i)=>entry('p'+i,'record',data)),s=source(items),ledger=new SelectionLedger(s);
  ledger.selectMany(items);for(const e of items)ledger.setIntent(e,'REVIEW_FOR_REMOVAL');
  const plan=buildRetentionPlan(s,ledger.entries(),ledger);
  for(const item of plan.items){assert.equal(item.protection.status,'PROTECTED');assert.equal(item.protection.removal_authorized,false);assert(item.pending_verifications.includes('HUMAN_BATCH_AUTHORIZATION'));}
  assert(plan.items[0].protection.reasons.includes('BASELINE_DESIGNATED'));
  assert(plan.items[1].protection.reasons.includes('BACKUP_NOT_VERIFIED'));
});

test('summary or declared backup does not prove preservation or authorize deletion',()=>{
  const e=entry('summary','record',{kind:'run',summary:'Tudo preservado',backup_verified:true,retention:'delete',delete_authorized:true}),s=source([e]);
  const item=buildRetentionPlan(s,[e]).items[0];
  assert.equal(item.protection.removal_authorized,false);assert(item.protection.reasons.includes('BACKUP_NOT_VERIFIED'));
});

test('dossier and reference copying are deterministic data, with explicit selected identities',()=>{
  const a=entry('a','record',{id:'M1',kind:'mission'}),b=entry('b','table',{id:'M1.1'}),s=source([a,b]);
  const dossier=buildDossier(s,[a,b]);assert.equal(dossier.schema,'atlas-triage-dossier/1');assert.equal(dossier.selection.length,2);
  assert.equal(dossier.items[1].type,'table');assert.equal(dossier.status,'PROPOSAL_ONLY');assert.equal(dossier.DELETE_AUTHORIZED,'NO');
  const refs=copyReferences(s,[a,b]).split('\n').map(JSON.parse);assert.deepEqual(refs.map(x=>x.uid),['a','b']);
  assert.equal(JSON.stringify(dossier),JSON.stringify(buildDossier(s,[a,b])));
});

test('only permitted intentions are accepted, and an intention requires explicit selection',()=>{
  const a=entry('a','record',{kind:'run'}),ledger=new SelectionLedger(source([a]));
  assert.throws(()=>ledger.setIntent(a,'KEEP_FULL'),/SELECTION_REQUIRED/);ledger.toggle(a);
  for(const intent of RETENTION_INTENTS)assert.doesNotThrow(()=>ledger.setIntent(a,intent));
  for(const intent of ['DELETE','rm -rf','__proto__','toString',null])assert.throws(()=>ledger.setIntent(a,intent),/INTENT_INVALID/);
});

test('hostile strings and prototype property names stay inert without shared mutations',()=>{
  const e=rawEntry('hostile','record','{"id":"__proto__","kind":"__proto__","title":"<img src=x onerror=alert(1)>","__proto__":{"polluted":true},"constructor":"payload","metrics":{"toString":"not a function"}}'),s=source([e]),model=createTriageModel(s),before=e.raw_json;
  assert.equal({}.polluted,undefined);assert.equal(model.search({query:'<img'})[0].entry,e);assert.equal(model.type(e).key,'record');
  assert.equal(buildRetentionPlan(s,[e]).items[0].raw_json,before);assert.equal({}.polluted,undefined);
});

test('exports reject forged DTOs, missing snapshot identity and duplicate UID corruption',()=>{
  const e=entry('a','record',{kind:'run'}),s=source([e]);
  assert.throws(()=>buildRetentionPlan(s,[entry('a','record',{kind:'run',title:'forged'})]),/OUTSIDE_SNAPSHOT/);
  assert.throws(()=>buildRetentionPlan(source([e],{metadata_sha256:''}),[e]),/IDENTITY_REQUIRED/);
  assert.throws(()=>createTriageModel(source([e,e])),/IDENTITY_COLLISION/);
});

test('domain operations use no browser, network, storage or filesystem APIs',()=>{
  const oldFetch=globalThis.fetch;let requests=0;globalThis.fetch=()=>{requests++;throw Error('Network forbidden');};
  try{const e=entry('pure','record',{kind:'run',resource_id:'https://example.invalid'}),s=source([e]),ledger=new SelectionLedger(s);ledger.toggle(e);ledger.annotateBaseline(e,'Nota');createTriageModel(s).search({query:'pure'});buildRetentionPlan(s,ledger.entries(),ledger);assert.equal(requests,0);}
  finally{globalThis.fetch=oldFetch;}
});

test('1500 records are complete, selections are not capped and search remains responsive',()=>{
  const start=performance.now(),items=Array.from({length:1500},(_,i)=>entry('bulk-'+i,'record',{id:'RUN-'+i,kind:'run',family:'synthetic',summary:'needle '+i})),s=source(items),model=createTriageModel(s),ledger=new SelectionLedger(s);
  assert.equal(model.search({query:'needle'}).length,1500);assert.equal(model.search({query:'bulk-1499'})[0].entry.uid,'bulk-1499');
  ledger.selectMany(model.search({query:'needle'}).map(h=>h.entry));assert.equal(ledger.entries().length,1500);
  assert.equal(ledger.counts(items.slice(0,100),items).off_page,1400);
  const elapsed=performance.now()-start;assert(elapsed<5000,`domain operations took ${elapsed.toFixed(1)} ms (5 s bound)`);
});
