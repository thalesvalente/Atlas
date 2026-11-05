/** Feature 005 UI/controller regressions in a small in-memory DOM, NOT browser QA.
 * Product methods, domain model, ledger and exports run unchanged. Only DOM and
 * the controller's documented render/download hooks are supplied by this fixture.
 * Run: node scripts/qa/test_native_triage_ui.mjs
 * Optional comparison: ATLAS_TRIAGE_STATIC_ROOT=/absolute/static/directory node ...
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {resolve,sep} from 'node:path';
import {pathToFileURL} from 'node:url';
import vm from 'node:vm';

const staticRoot=process.env.ATLAS_TRIAGE_STATIC_ROOT?
  pathToFileURL(resolve(process.env.ATLAS_TRIAGE_STATIC_ROOT)+sep):
  new URL('../../packages/atlas/src/atlas_viewer/static/',import.meta.url);
const {NativeTriageUI}=await import(new URL('native_triage_ui.js',staticRoot));
const {createTriageModel,SelectionLedger}=await import(new URL('native_triage_model.js',staticRoot));
const {nativeFragments}=await import(new URL('native_navigation.js',staticRoot));
const controllerText=readFileSync(new URL('native_notebook.js',staticRoot),'utf8');
const matchesStart=controllerText.indexOf('function matches(e,context=null){');
const matchesEnd=controllerText.indexOf('\nfunction message(',matchesStart);
assert(matchesStart>=0&&matchesEnd>matchesStart,'real controller matches() source is required');
const actualMatches=triage=>vm.runInNewContext('('+controllerText.slice(matchesStart,matchesEnd)+')',{triage},
  {filename:new URL('native_notebook.js',staticRoot).pathname,timeout:1000});

const freeze=value=>{
  if(value&&typeof value==='object'&&!Object.isFrozen(value)){Object.values(value).forEach(freeze);Object.freeze(value);}
  return value;
};
function entry(uid,value={},kind='record',extra={}){
  const raw_json=JSON.stringify({id:uid,...value}),fields=[...nativeFragments(raw_json,{all:true})]
    .filter(([,raw])=>!['{','['].includes(raw[0])).map(([name,raw])=>({name,
      type:raw==='null'?'null':raw[0]==='"'?'string':/^(true|false)$/.test(raw)?'boolean':'integer',
      text:raw[0]==='"'?JSON.parse(raw):raw}));
  return freeze({uid,kind,group:kind==='record'?'records':'result_tables',title:value.title||'Item '+uid,
    native_id:uid,source_key:uid,family:null,status:null,date:value.started_at??null,parent_uid:null,fields,raw_json,...extra});
}
const source=entries=>freeze({id:'ui-fixture',revision:'INVENTED-UI-R1',metadata_sha256:'a'.repeat(64),status:'READY',entries});
const dataName=name=>name.slice(5).replace(/-([a-z])/g,(_,x)=>x.toUpperCase());
const descendants=root=>root.childNodes.flatMap(node=>[node,...descendants(node)]);

function selectorMatches(node,selector){
  if(node.nodeType!==1)return false;
  if(selector.includes(':not(:disabled)')){if(node.disabled)return false;selector=selector.replace(':not(:disabled)','');}
  if(selector.startsWith('.'))return node.className.split(/\s+/).includes(selector.slice(1));
  if(selector.startsWith('#'))return node.id===selector.slice(1);
  const parsed=/^([a-z][a-z0-9-]*)?(?:\[([a-z0-9-]+)(?:=(?:"([^"]*)"|'([^']*)'|([^\]]+)))?\])?$/i.exec(selector);
  assert(parsed&&parsed[0],`Unsupported fixture selector: ${selector}`);
  if(parsed[1]&&node.localName!==parsed[1])return false;
  if(parsed[2]){const value=node.getAttribute(parsed[2]),expected=parsed[3]??parsed[4]??parsed[5];
    return value!==null&&(expected===undefined||value===expected);}
  return true;
}

class MemoryNode{
  constructor(tag,doc,text=''){
    this.localName=tag;this.tagName=tag.toUpperCase();this.nodeType=tag==='#text'?3:1;this.ownerDocument=doc;
    this._text=text;this._nodes=[];this._attributes=new Map();this._listeners=new Map();this.dataset=Object.create(null);
    this.parentNode=null;this.className='';this.id='';this.value='';this.hidden=false;this.disabled=false;this.checked=false;
    this.classList={contains:name=>this.className.split(/\s+/).includes(name),
      toggle:(name,force)=>{const active=force??!this.classList.contains(name),names=this.className.split(/\s+/).filter(x=>x&&x!==name);if(active)names.push(name);this.className=names.join(' ');return active;}};
  }
  get childNodes(){return this._nodes;}
  get children(){return this._nodes.filter(x=>x.nodeType===1);}
  get firstElementChild(){return this.children[0]??null;}
  get childElementCount(){return this.children.length;}
  get isConnected(){let node=this;while(node){if(node===this.ownerDocument.body)return true;node=node.parentNode;}return false;}
  get textContent(){return this.nodeType===3?this._text:this._nodes.map(x=>x.textContent).join('');}
  set textContent(value){if(this.nodeType===3)this._text=String(value);else{this.replaceChildren();if(String(value))this.append(String(value));}}
  get options(){return this.children.filter(x=>x.localName==='option');}
  get selectedOptions(){return this.options.filter(x=>x.value===this.value);}
  set innerHTML(_){throw Error('HTML sinks are forbidden');}
  set outerHTML(_){throw Error('HTML sinks are forbidden');}
  contains(node){return node===this||descendants(this).includes(node);}
  append(...values){for(const value of values){const node=value instanceof MemoryNode?value:new MemoryNode('#text',this.ownerDocument,String(value));
    node.remove();node.parentNode=this;this._nodes.push(node);}}
  prepend(...values){const nodes=values.map(value=>value instanceof MemoryNode?value:new MemoryNode('#text',this.ownerDocument,String(value)));
    for(const node of nodes){node.remove();node.parentNode=this;}this._nodes.unshift(...nodes);}
  replaceChildren(...values){for(const node of [...this._nodes])node.remove();this.append(...values);}
  remove(){if(!this.parentNode)return;const parent=this.parentNode;
    if(this.contains(this.ownerDocument.activeElement))this.ownerDocument.activeElement=this.ownerDocument.body;
    parent._nodes.splice(parent._nodes.indexOf(this),1);this.parentNode=null;}
  setAttribute(name,value){const text=String(value);this._attributes.set(name,text);
    if(name==='id')this.id=text;if(name==='class')this.className=text;if(name.startsWith('data-'))this.dataset[dataName(name)]=text;}
  getAttribute(name){if(name==='id')return this.id||null;if(name==='class')return this.className||null;
    if(name.startsWith('data-'))return this.dataset[dataName(name)]??null;
    if(['type','tabindex'].includes(name)){const value=this[name==='tabindex'?'tabIndex':name];if(value!==undefined)return String(value);}
    return this._attributes.get(name)??null;}
  removeAttribute(name){this._attributes.delete(name);if(name.startsWith('data-'))delete this.dataset[dataName(name)];}
  querySelectorAll(selector){const selectors=selector.split(',').map(s=>s.trim());return descendants(this).filter(node=>selectors.some(s=>selectorMatches(node,s)));}
  querySelector(selector){return this.querySelectorAll(selector)[0]??null;}
  addEventListener(name,listener){if(!this._listeners.has(name))this._listeners.set(name,[]);this._listeners.get(name).push(listener);}
  dispatchEvent(event){event.target??=this;event.currentTarget=this;event.stopPropagation??=()=>{};event.preventDefault??=()=>{};
    for(const listener of this._listeners.get(event.type)||[])listener(event);return true;}
  click(){if(this.disabled)return;this.focus();this.dispatchEvent({type:'click'});}
  focus(){if(this.isConnected&&!this.disabled)this.ownerDocument.activeElement=this;}
  getClientRects(){let node=this;while(node){if(node.hidden)return[];node=node.parentNode;}return this.isConnected?[this.getBoundingClientRect()]:[];}
  getBoundingClientRect(){return {left:0,top:0,right:100,bottom:40,width:100,height:40};}
  setCustomValidity(value){this.validationMessage=value;}
  reportValidity(){return !this.validationMessage;}
}

const CONTROL_IDS=['native-family','native-kind','native-execution','native-status','native-publication','native-admission',
  'native-review','native-documentary','native-baseline','native-evidence','native-search','native-from','native-to',
  'native-filter-chips','native-filter-count','native-clear','native-selection','native-batch-summary','native-batch-bar',
  'native-select-visible','native-select-filtered','native-compare','native-retention','native-batch-details',
  'native-copy-references','native-batch-links','native-dossier'];
function withUI({pane='selected',mode='dossier',select=true}={},run){
  const previous=globalThis.document,doc={activeElement:null};doc.body=new MemoryNode('body',doc);doc.activeElement=doc.body;
  doc.createElement=tag=>{assert(!['script','iframe'].includes(tag));return new MemoryNode(tag,doc);};
  doc.createTextNode=text=>new MemoryNode('#text',doc,text);
  doc.getElementById=id=>descendants(doc.body).find(node=>node.id===id)??null;
  doc.querySelectorAll=selector=>doc.body.querySelectorAll(selector);doc.querySelector=selector=>doc.body.querySelector(selector);
  globalThis.document=doc;
  try{
    const host=doc.createElement('section');host.id='native-content';doc.body.append(host);
    const detail=doc.createElement('aside');detail.id='native-detail-body';doc.body.append(detail);
    for(const id of CONTROL_IDS){const node=doc.createElement('select');node.id=id;doc.body.append(node);}
    const a=entry('a',{kind:'run',title:'Execução A'}),b=entry('b',{kind:'experiment',title:'Experimento B'}),s=source([a,b]),before=JSON.stringify(s);
    const ledger=new SelectionLedger(s);if(select)ledger.selectMany([a,b]);
    const ui=Object.create(NativeTriageUI.prototype);Object.assign(ui,{source:s,ledger,model:createTriageModel(s),mode,page:0,filtered:[],downloads:[],messages:[]});
    const refresh=()=>{host.replaceChildren();const rows=ui.renderPane(host,pane);ui.afterRender(rows||[]);};
    Object.assign(ui,{hooks:{pane:()=>pane,refresh,tableFilters:()=>({}),
      download:(name,text)=>ui.downloads.push({name,value:JSON.parse(text)}),message:text=>ui.messages.push(text),
      detail:entry=>{detail.replaceChildren();ui.addDetailControls(detail,entry);},filterChanged:refresh}});
    ui.filterOptions(false);refresh();run({ui,host,detail,doc,a,b,source:s,refresh});
    assert.equal(JSON.stringify(s),before,'source DTOs and scientific values must not change');
  }finally{if(previous===undefined)delete globalThis.document;else globalThis.document=previous;}
}
function uncheck(doc,uid){const input=doc.getElementById('native-content').querySelector(`[data-batch-uid="${uid}"]`);
  assert(input,'selected checkbox must exist');input.focus();input.checked=false;input.dispatchEvent({type:'change'});}

test('UX-UI-01 dossier export and cards follow the current explicit selection',()=>withUI({},({ui,host,doc})=>{
  uncheck(doc,'b');doc.getElementById('native-export-dossier').click();
  assert.deepEqual(ui.downloads.at(-1).value.selection.map(x=>x.uid),['a']);
  assert.deepEqual(host.querySelectorAll('[data-result-uid]').map(node=>node.dataset.resultUid),['a']);
  assert.equal(doc.getElementById('native-batch-summary').dataset.selectedCount,'1');
}));

test('UX-UI-01 dossier callback reads the ledger at click time, not its rendered closure',()=>withUI({},({ui,doc,b})=>{
  const exportButton=doc.getElementById('native-export-dossier');ui.ledger.toggle(b);exportButton.click();
  assert.deepEqual(ui.downloads.at(-1).value.selection.map(x=>x.uid),['a']);
}));

test('UX-UI-01 retention removes stale intention controls and exports the current item count',()=>withUI({pane:'retention',mode:'list'},({ui,host,doc})=>{
  uncheck(doc,'b');const selectors=host.querySelectorAll('[data-intent-uid]');
  assert.doesNotThrow(()=>{for(const select of selectors){select.value='KEEP_ESSENTIALS';select.dispatchEvent({type:'change'});}},
    'every still-reachable intention control must belong to the explicit selection');
  assert.deepEqual(selectors.map(node=>node.dataset.intentUid),['a']);
  assert.match(doc.getElementById('native-export-plan').textContent,/1 itens/);
  doc.getElementById('native-export-plan').click();const plan=ui.downloads.at(-1).value;
  assert.deepEqual(plan.selection.map(x=>x.uid),['a']);assert.equal(plan.items[0].intent,'KEEP_ESSENTIALS');
  assert.equal(plan.DELETE_AUTHORIZED,'NO');assert.equal(plan.items[0].protection.removal_authorized,false);
}));

test('UX-UI-01 removing the final selected item retires export controls and restores connected focus',()=>withUI({},({ui,host,doc})=>{
  uncheck(doc,'b');uncheck(doc,'a');assert.equal(ui.ledger.size,0);
  assert.equal(Boolean(doc.getElementById('native-export-dossier')),false);assert.equal(host.querySelectorAll('[data-batch-uid]').length,0);
  assert.equal(doc.activeElement.tagName,'H2');assert.equal(doc.activeElement.isConnected,true);
}));

test('UX-UI-02 controller accepts the row kind without changing its actual type',()=>{
  const table=entry('table',{started_at:'2026-11-05',rows:[]},'table',{row_count:1}),
    row=entry('row',{cells:{ID:'RF-1'}},'row',{table_uid:'table',ordinal:0}),s=source([table,row]),model=createTriageModel(s),ledger=new SelectionLedger(s);
  let filters={kind:model.facet(row,'kind').key};const matches=actualMatches({model,ledger,filters:()=>filters});
  assert.equal(model.matches(row,filters),true);assert.equal(matches(row,table),true);
  filters={kind:model.facet(table,'kind').key};assert.equal(matches(row,table),true,'table context may scope its rows');
  assert.equal(model.type(row).key,'row');assert.equal(row.kind,'row');
});

test('UX-UI-02 declared NULL or empty row dates cannot inherit a table date',()=>{
  const table=entry('table',{started_at:'2026-11-05',rows:[]},'table',{row_count:3}),
    absent=entry('absent',{cells:{}},'row',{table_uid:'table',ordinal:0}),
    nul=entry('null',{started_at:null,cells:{}},'row',{table_uid:'table',ordinal:1}),
    empty=entry('empty',{started_at:'',cells:{}},'row',{table_uid:'table',ordinal:2}),s=source([table,absent,nul,empty]),before=JSON.stringify(s),
    model=createTriageModel(s),ledger=new SelectionLedger(s),filters={from:'2026-11-05',to:'2026-11-05'},matches=actualMatches({model,ledger,filters:()=>filters});
  assert.equal(matches(absent,table),true,'only actual absence may use table context');
  assert.equal(matches(nul,table),false);assert.equal(matches(empty,table),false);assert.equal(JSON.stringify(s),before);
});

test('UX-UI-03 removing a session baseline annotation reconciles Baselines and select-all population',()=>withUI({pane:'baselines',select:false},({ui,host,detail,doc,a,refresh})=>{
  ui.ledger.annotateBaseline(a,'Designação provisória');refresh();ui.hooks.detail(a);
  assert.deepEqual(ui.filtered.map(e=>e.uid),['a']);
  const remove=detail.querySelectorAll('button').find(node=>node.textContent==='Remover anotação de sessão');assert(remove&&!remove.hidden);remove.click();
  assert.equal(ui.ledger.annotations.size,0);assert.deepEqual(ui.filtered.map(e=>e.uid),[]);
  assert.equal(host.querySelectorAll('[data-result-uid]').length,0);
  ui.ledger.selectMany(ui.filtered);assert.equal(ui.ledger.size,0);
  assert.equal(doc.activeElement.isConnected,true);
}));

test('UX-UI-03 adding an annotation reconciles an active NOT_DECLARED filter',()=>withUI({pane:'search',select:false},({ui,host,detail,doc,a,refresh})=>{
  doc.getElementById('native-baseline').value='NOT_DECLARED';refresh();ui.hooks.detail(a);
  assert.deepEqual(ui.filtered.map(e=>e.uid),['a','b']);
  const note=detail.querySelector('input[type="text"]');note.value='Nota da sessão';
  detail.querySelectorAll('button').find(node=>node.textContent==='Anotar baseline nesta sessão').click();
  assert.equal(ui.ledger.annotations.size,1);assert.deepEqual(ui.filtered.map(e=>e.uid),['b']);
  assert.deepEqual(host.querySelectorAll('[data-result-uid]').map(node=>node.dataset.resultUid),['b']);
  ui.ledger.selectMany(ui.filtered);assert.deepEqual(ui.ledger.entries().map(e=>e.uid),['b']);
}));

test('UX-UI-04 navigation counts use typed populations and current session designations',()=>{
  const run=entry('run',{kind:'run'}),baseline=entry('baseline',{kind:'baseline'}),table=entry('table',{rows:[]},'table',{row_count:0}),
    s=source([run,baseline,table]),before=JSON.stringify(s),ui=Object.create(NativeTriageUI.prototype);
  Object.assign(ui,{source:s,model:createTriageModel(s),ledger:new SelectionLedger(s)});
  assert.deepEqual(ui.navigationCounts(),{search:3,experiments:1,baselines:1,selected:0,retention:0});
  ui.ledger.annotateBaseline(table,'Designação da sessão');ui.ledger.selectMany([run,table]);
  assert.deepEqual(ui.navigationCounts(),{search:3,experiments:1,baselines:2,selected:2,retention:2});
  ui.ledger.removeAnnotation(table);assert.equal(ui.navigationCounts().baselines,1);assert.equal(JSON.stringify(s),before);
});
