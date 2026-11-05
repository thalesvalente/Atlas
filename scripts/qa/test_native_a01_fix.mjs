/** ATLAS-A01-FIX: adversarial regressions. Synthetic DTOs; no corpus or runtime.
 * Run: node scripts/qa/test_native_a01_fix.mjs
 * Discovered by tests/viewer/test_native_notebook_a01_fix.py in existing CI.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {nativeFragments} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {makePresentation,recordMatches} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';
import {renderRecordPresentation} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_views.js';

// The DTO's scalar fields retain the tokens; scientific numbers never pass
// through JSON.parse, JSON.stringify or Number in this fixture builder.
function dto(raw,uid='synthetic-record') {
  const fields=[...nativeFragments(raw,{all:true})]
    .filter(([,v])=>!['{','['].includes(v[0]))
    .map(([name,v])=>({name,type:v==='null'?'null':v[0]==='"'?'string':/^(true|false)$/.test(v)?'boolean':/[.eE]/.test(v)?'number':'integer',text:v[0]==='"'?JSON.parse(v):v}));
  const first=names=>names.map(name=>fields.find(f=>f.name===name)).find(f=>f?.type==='string'&&f.text)?.text??null;
  return Object.freeze({uid,kind:'record',group:'records',title:'Registro sintético',native_id:null,source_key:null,family:null,status:first(['execution_state','status','result_state','result_group']),parent_uid:null,fields:Object.freeze(fields.map(Object.freeze)),raw_json:raw});
}
const record=raw=>makePresentation([dto(raw)]).records[0];

// Minimal DOM is used only for the table's public text and callback contract.
// Browser layout and accessibility are qualified separately in Chromium.
class Node {
  constructor(tag,text=''){this.tagName=tag;this.nodes=[];this.text=text;this.dataset={};this.attrs={};this.events={};}
  set textContent(value){this.text=String(value);this.nodes=[];}
  get textContent(){return this.text+this.nodes.map(n=>n.textContent).join('');}
  get childElementCount(){return this.nodes.filter(n=>n.tagName!=='#text').length;}
  append(...nodes){this.nodes.push(...nodes);}
  setAttribute(name,value){assert.ok(!/^on/i.test(name));this.attrs[name]=String(value);}
  addEventListener(name,fn){this.events[name]=fn;}
  set innerHTML(_){throw Error('Imported HTML must not execute');}
}
const descendants=(node,tag)=>node.nodes.flatMap(n=>[...(n.tagName===tag?[n]:[]),...descendants(n,tag)]);
function executionCell(raw){
  const previous=globalThis.document;
  globalThis.document={createElement:tag=>{assert.ok(!['script','iframe','object'].includes(tag));return new Node(tag);},createTextNode:text=>new Node('#text',String(text))};
  try{
    const host=new Node('main'),r=record(raw),before=r.entry.raw_json;
    renderRecordPresentation(host,[r],()=>{});
    assert.equal(r.entry.raw_json,before);
    return descendants(host,'tbody')[0].nodes[0].nodes[2].textContent;
  }finally{if(previous===undefined)delete globalThis.document;else globalThis.document=previous;}
}

for(const [name,raw,expected] of [
  ['execution_state','{"execution_state":"FAILED"}','FAILED'],
  ['status positive control','{"status":"FAILED"}','FAILED'],
  ['result_state','{"result_state":"SUCCEEDED"}','SUCCEEDED'],
  ['result_group','{"result_group":"failed"}','failed'],
  ['explicit NULL','{"execution_state":null}','NULL — valor declarado'],
  ['explicit empty text','{"execution_state":""}','"" — texto vazio declarado'],
  ['missing control','{}','Não declarado'],
  ['NULL wins over lower priority','{"execution_state":null,"status":"FAILED"}','NULL — valor declarado'],
  ['empty text wins over lower priority','{"execution_state":"","status":"FAILED"}','"" — texto vazio declarado'],
  ['canonical order','{"execution_state":"FIRST","status":"SECOND","result_state":"THIRD","result_group":"fourth","result":"legacy"}','FIRST'],
  ['status wins over result_state and legacy result','{"status":"SECOND","result_state":"THIRD","result":"legacy"}','SECOND'],
  ['result_state NULL wins over group','{"result_state":null,"result_group":"failed"}','NULL — valor declarado'],
  ['false is declared','{"execution_state":false,"status":"FAILED"}','false'],
  ['zero token is declared','{"execution_state":0,"status":"FAILED"}','0'],
  ['legacy result fallback control','{"result":"LEGACY"}','LEGACY'],
])test('F01 '+name,()=>assert.equal(executionCell(raw),expected));

for(const [name,raw,query] of [
  ['nested metrics','{"metrics":{"model":"marker-zebra-731"}}','marker-zebra-731'],
  ['arbitrary array','{"tags":["marker-zebra-731"]}','marker-zebra-731'],
  ['known notes positive control','{"notes":["marker-zebra-731"]}','marker-zebra-731'],
  ['scalar positive control','{"description":"marker-zebra-731"}','marker-zebra-731'],
  ['mixed nested arrays','{"custom":[{"deeper":[false,null,{"value":"marker-zebra-731"}]}]}','marker-zebra-731'],
  ['decoded escaped Unicode','{"custom":{"text":"a\\u00e7\\u00e3o-pinguim"}}','ação-pinguim'],
  ['large integer exact token','{"metrics":{"n":900719925474099312345}}','900719925474099312345'],
  ['decimal exact token','{"metrics":{"n":0.1234567890123456789012345}}','0.1234567890123456789012345'],
  ['exponent exact token','{"metrics":{"n":1.234567890123456789e+123}}','1.234567890123456789e+123'],
  ['negative zero exact token','{"metrics":{"n":-0.0}}','-0.0'],
  ['prototype-looking keys remain data','{"custom":{"__proto__":{"toString":"marker-zebra-731"},"constructor":null}}','marker-zebra-731'],
  ['HTML and URL remain inert data','{"custom":["<script>marker-zebra-731</script>","javascript:marker-zebra-731"]}','marker-zebra-731'],
])test('F02 '+name,()=>{
  const r=record(raw),original=r.entry.raw_json;
  assert.equal(recordMatches(r,{query}),true);
  assert.equal(r.entry.raw_json,original);
});

test('F02 negative: do not round the numeric payload or invent a hit',()=>{
  const r=record('{"metrics":{"n":9007199254740993},"tags":["needle-original"]}');
  assert.equal(recordMatches(r,{query:'9007199254740992'}),false);
  assert.equal(recordMatches(r,{query:'needle-absent'}),false);
});

test('F02 search still combines with every record filter',()=>{
  const r=record('{"family":"F","kind":"run","result_group":"failed","metrics":{"model":"marker-zebra-731"}}');
  assert.equal(recordMatches(r,{query:'marker-zebra-731',family:r.familyKey,kind:r.filterKind,status:r.filterStatus}),true);
  for(const field of ['family','kind','status'])assert.equal(recordMatches(r,{query:'marker-zebra-731',[field]:'not-present'}),false);
});

// The five dimensions come from the authorized OLD tables-coverage.js, not
// a new taxonomy. Values and missingness are observations of this snapshot.
import * as filters from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';
const tableDto=(uid,raw,kind='table')=>Object.freeze({...dto(raw,uid),kind});
const facetEntries=[
  tableDto('missing','{}'),tableDto('null','{"project":null}'),
  tableDto('empty','{"project":""}'),tableDto('text','{"project":"1"}'),
  tableDto('number','{"project":1}'),tableDto('false','{"project":false}'),
  tableDto('label','{"project":"NULL — valor declarado"}'),
  tableDto('array','{"project":["a","b"]}'),tableDto('array-label','{"project":"a · b"}'),
];
test('F03 typed facet keys distinguish NULL, missing, empty, scalar and composite values',()=>{
  const options=filters.tableFilterOptions(facetEntries,'project');
  assert.equal(options.length,facetEntries.length);
  assert.equal(new Set(options.map(x=>x.key)).size,facetEntries.length);
  assert.equal(new Set(options.map(x=>x.label)).size,facetEntries.length);
  for(const e of facetEntries){
    const key=filters.tableFacet(e,'project').key;
    assert.deepEqual(facetEntries.filter(t=>filters.tableMatchesFilters(t,{project:key})).map(t=>t.uid),[e.uid]);
  }
});
test('F03 undeclared dimensions produce no manufactured filter options',()=>{
  assert.deepEqual(filters.tableFilterOptions([tableDto('only','{}')],'stage'),[]);
  assert.deepEqual(filters.tableFilterOptions(facetEntries,'unknown_dimension'),[]);
});
test('F03 table and row dimensions do not borrow values from each other',()=>{
  const es=[tableDto('t','{"project":"P","nucleus_id":"NOT_A_ROW"}'),tableDto('r','{"project":"NOT_A_TABLE","nucleus_id":"N"}','row')];
  assert.equal(filters.tableFilterOptions(es,'project').length,1);
  assert.equal(filters.tableFilterOptions(es,'nucleus_id').length,1);
  assert.match(filters.tableFilterOptions(es,'nucleus_id')[0].label,/^N$/);
});
test('F03 table dimensions combine without overwriting values or changing original order',()=>{
  const es=[tableDto('second','{"project":"P","run_id":"R","stage":"S","admission":"HOLD"}'),tableDto('first','{"project":"Q","run_id":"R","stage":"S","admission":"HOLD"}'),tableDto('third','{"project":"P","run_id":null,"stage":"S","admission":"HOLD"}')];
  const before=es.map(e=>e.raw_json),selection=Object.fromEntries(['project','run_id','stage','admission'].map(k=>[k,filters.tableFacet(es[0],k).key]));
  assert.deepEqual(es.filter(e=>filters.tableMatchesFilters(e,selection)).map(e=>e.uid),['second']);
  assert.deepEqual(es.filter(e=>filters.tableMatchesFilters(e,{})),es);
  assert.deepEqual(es.map(e=>e.raw_json),before);
});
test('F03 arbitrary precision, exponents and negative zero remain distinct facet tokens',()=>{
  const tokens=['9007199254740993','9007199254740992','1.00','1e+0','-0','0'];
  const es=tokens.map((v,i)=>tableDto('n'+i,'{"run_id":'+v+'}'));
  assert.equal(filters.tableFilterOptions(es,'run_id').length,tokens.length);
  tokens.forEach((v,i)=>assert.equal(filters.tableFacet(es[i],'run_id').label,v));
});
test('F03 nucleus selection preserves explicit absence and null',()=>{
  const es=[tableDto('a','{}','row'),tableDto('b','{"nucleus_id":null}','row'),tableDto('c','{"nucleus_id":""}','row')];
  for(const e of es){const f={nucleus_id:filters.tableFacet(e,'nucleus_id').key};assert.deepEqual(es.filter(x=>filters.tableMatchesFilters(x,f)),[e]);}
});
test('F03 prototype-looking and HTML-bearing facet values remain inert literals',()=>{
  const e=tableDto('t','{"project":{"__proto__":{"toString":"<script>trap</script>"}}}');
  assert.match(filters.tableFacet(e,'project').label,/<script>trap<\/script>/);
  assert.equal(filters.tableMatchesFilters(e,{project:filters.tableFacet(e,'project').key}),true);
});
