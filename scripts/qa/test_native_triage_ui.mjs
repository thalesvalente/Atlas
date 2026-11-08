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
const {makePresentation,groupRequirementRows}=await import(new URL('native_legacy_model.js',staticRoot));
const views=await import(new URL('native_legacy_views.js',staticRoot));
const {renderCatalog}=views;
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
  getClientRects(){let node=this;while(node){if(node.hidden)return[];const parent=node.parentNode;if(parent?.localName==='details'&&parent.open===false&&node!==parent.children.find(child=>child.localName==='summary'))return[];node=parent;}return this.isConnected?[this.getBoundingClientRect()]:[];}
  getBoundingClientRect(){return {left:0,top:0,right:100,bottom:40,width:100,height:40};}
  setCustomValidity(value){this.validationMessage=value;}
  reportValidity(){return !this.validationMessage;}
}

const CONTROL_IDS=['native-family','native-kind','native-execution','native-status','native-publication','native-admission',
  'native-review','native-documentary','native-baseline','native-evidence','native-search','native-from','native-to',
  'native-filter-chips','native-filter-count','native-clear','native-selection','native-batch-summary','native-batch-bar',
  'native-select-visible','native-select-filtered','native-compare','native-retention','native-batch-details',
  'native-copy-references','native-batch-links','native-dossier','native-clear-batch'];
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

test('UX-UI-05 clear selection is exposed beside select-visible and select-filtered without a disclosure',()=>{
  const html=readFileSync(new URL('native_notebook.html',staticRoot),'utf8');
  const selectionActions=html.match(/<div class="triage-select-actions">([\s\S]*?)<\/div>/)?.[1];
  assert(selectionActions,'Selection action group must exist');
  assert.match(selectionActions,/id="native-select-visible"/);
  assert.match(selectionActions,/id="native-select-filtered"/);
  assert.match(selectionActions,/id="native-clear-batch"/,'Deselect-all must be discoverable next to the two selection controls');
  assert.doesNotMatch(selectionActions,/<details\b/,'Clearing the batch must not require opening More actions');
  assert.equal([...html.matchAll(/id="native-clear-batch"/g)].length,1,'The existing clear control stays unique');
});

test('UX-UI-05 deselect-all exposes the current count and clears hidden selections without losing session annotations',()=>withUI({pane:'search',select:false},({ui,doc,a,b})=>{
  const clear=doc.getElementById('native-clear-batch');
  assert.equal(clear.disabled,true,'Empty selection has an inactive, visible clear action');
  assert.equal(clear.textContent,'Desmarcar todos (0)');
  ui.ledger.selectMany([a,b]);ui.ledger.setIntent(a,'KEEP_ESSENTIALS');
  ui.ledger.annotateBaseline(a,'Annotation independent from selection');ui.syncBatch();
  assert.equal(clear.disabled,false);assert.equal(clear.textContent,'Desmarcar todos (2)');
  doc.getElementById('native-search').value='Execução A';ui.syncBatch();
  assert.equal(doc.getElementById('native-batch-summary').dataset.hiddenCount,'1');
  clear.focus();ui.ledger.clear();ui.selectionChanged();
  assert.equal(ui.ledger.size,0);assert.equal(ui.ledger.intents.size,0);
  assert.equal(ui.ledger.annotations.size,1,'Clearing selection does not erase the independent baseline annotation');
  assert.equal(clear.disabled,true);assert.equal(clear.textContent,'Desmarcar todos (0)');
  assert.equal(doc.getElementById('native-batch-summary').dataset.selectedCount,'0');
  assert.equal(doc.getElementById('native-batch-bar').hidden,true);
  assert.equal(doc.activeElement,doc.getElementById('native-select-visible'),'Focus must leave a just-disabled clear button');
  assert.ok(doc.querySelectorAll('[data-batch-uid]').every(node=>!node.checked));
}));

test('UX-UI-06 catalog selection text remains separate from the document title and preserves its detail callback',()=>withUI({pane:'assets',select:false},({ui,host})=>{
  const asset=entry('document',{title:'Documento sintético'},'asset',{group:'resource_documents'}),s=source([asset]),before=JSON.stringify(s);
  ui.source=s;ui.ledger=new SelectionLedger(s);ui.model=createTriageModel(s);host.replaceChildren();
  let opened=null;renderCatalog(host,[asset],makePresentation([asset]),value=>{opened=value;});ui.decorate();
  const cells=host.querySelector('tr[data-uid]').children,selection=cells[0],name=cells[1],control=selection.querySelector('input'),title=name.querySelector('button');
  assert.equal(cells.length,5,'The catalog has a dedicated narrow selection column');
  assert.equal(selection.textContent,'','Per-row selection text is redundant with the column header');
  assert.equal(name.querySelector('input'),null,'Document identity occupies its own column');
  assert.equal(name.textContent,'Documento sintético');
  assert.equal(title.textContent,'Documento sintético');title.click();assert.equal(opened,asset);
  assert.match(control.getAttribute('aria-label'),/^Selecionar Documento sintético/);
  control.checked=true;control.dispatchEvent({type:'change'});assert.equal(ui.ledger.has(asset),true);
  assert.equal(JSON.stringify(s),before);
}));

test('UX-UI-08 catalog checkbox names remain unique for duplicate document titles without visible labels',()=>withUI({pane:'assets',select:false},({ui,host})=>{
  const items=['one','two'].map(uid=>entry(uid,{title:'Same invented document'},'asset',{group:'resource_documents'})),s=source(items);
  ui.source=s;ui.model=createTriageModel(s);ui.ledger=new SelectionLedger(s);host.replaceChildren();renderCatalog(host,items,makePresentation(items),()=>{});ui.decorate();
  const checks=host.querySelectorAll('input');assert.equal(checks.length,2);
  assert.equal(new Set(checks.map(input=>input.getAttribute('aria-label'))).size,2);
  assert.ok(host.querySelectorAll('.catalog-select-cell').every(cell=>cell.textContent===''));
}));

test('UX-UI-09 nucleus disclosures default open and preserve scoped state without changing selection or visible semantics',()=>withUI({pane:'tables'},({ui,host,a,b})=>{
  assert.equal(typeof views.renderRequirementGroup,'function');
  const open=new Map(),group={key:'source:snapshot:table:nucleus',label:'Declared nucleus',rows:[a,b]},before=JSON.stringify(ui.source);
  const draw=(target,rows)=>rows.forEach(row=>target.append(ui.checkControl(row)));
  let region=views.renderRequirementGroup(host,group,[a,b],draw,open,()=>ui.syncBatch());ui.afterRender([a,b]);
  assert.equal(region.tagName,'DETAILS');assert.equal(region.open,true);assert.match(region.querySelector('summary').textContent,/Declared nucleus/);
  assert.equal(ui.visibleEntries().length,2);region.querySelector('input').focus();region.open=false;region.dispatchEvent({type:'toggle'});
  assert.equal(open.get(group.key),false);assert.equal(ui.visibleEntries().length,0);assert.equal(ui.ledger.size,2);
  assert.equal(document.activeElement,region.querySelector('summary'),'Collapsing focused content restores focus to its visible summary');
  host.replaceChildren();region=views.renderRequirementGroup(host,group,[a],draw,open,()=>ui.syncBatch());
  assert.equal(region.open,false,'Filtering/pagination rerenders retain the group choice');
  const other=views.renderRequirementGroup(host,{...group,key:'other-source:snapshot:table:nucleus'},[b],draw,open);
  assert.equal(other.open,true,'Another source/snapshot/table group does not inherit collapse');
  region.open=true;region.dispatchEvent({type:'toggle'});assert.equal(open.get(group.key),true);
  host.replaceChildren();region.open=false;region.dispatchEvent({type:'toggle'});assert.equal(open.get(group.key),true,'Detached events do not overwrite current disclosure state');
  assert.equal(JSON.stringify(ui.source),before);
}));

test('UX-UI-09 locating a row explicitly opens only its nucleus group in the current snapshot',()=>{
  const rows=[entry('target',{nucleus_id:'A',cells:{Nome:'A'}},'row',{table_uid:'T',ordinal:0}),entry('other',{nucleus_id:'B',cells:{Nome:'B'}},'row',{table_uid:'T',ordinal:1})];
  const source={id:'fixture-source',metadata_sha256:'fixture-snapshot'},groups=groupRequirementRows(rows,{sourceId:source.id,snapshot:source.metadata_sha256});
  const state={source,detail:null,tableGrouping:'nucleus',nucleusOpen:new Map(groups.map(group=>[group.key,false])),history:[]};
  const start=controllerText.indexOf('function openOccurrence(uid){'),end=controllerText.indexOf('\nfunction returnToSelection(',start);let selected;
  const open=vm.runInNewContext('('+controllerText.slice(start,end)+')',{state,entries:()=>rows,navigation:()=>({byUid:new Map(rows.map(row=>[row.uid,row]))}),
    triage:{resetFilters:()=>{}},groupRequirementRows,render:()=>{},detail:entry=>{selected=entry;},$:()=>({scrollIntoView:()=>{}})},{timeout:1000});
  open('target');assert.equal(selected,rows[0]);assert.equal(state.nucleusOpen.get(groups[0].key),true);assert.equal(state.nucleusOpen.get(groups[1].key),false);
});

test('UX-UI-07 overview separates declared source metrics from local selection and annotation state',()=>withUI({pane:'search'},({ui,host,a,b})=>{
  const metadata=entry('structure',{records:[],result_tables:[],product_items:[],storage_observations:[],frontier_catalog:[],coverage:{}},'collection',{group:'$structure'}),
    coverage=entry('coverage',{source_rows:{operational_index:7}},'collection',{group:'coverage',pointer:'/coverage'}),
    product=entry('product',{title:'Invented product'},'asset',{group:'product_items'}),s=source([metadata,coverage,a,b,product]);
  ui.source=s;ui.model=createTriageModel(s);ui.ledger=new SelectionLedger(s);ui.ledger.selectMany([a]);
  ui.ledger.annotateBaseline(b,'Local annotation');host.replaceChildren();ui.renderPane(host,'overview');
  const metrics=host.querySelectorAll('[data-population-id]'),counts=new Map(metrics.map(node=>[node.dataset.populationId,node.querySelector('strong').textContent]));
  assert.equal(counts.get('records'),'2');assert.equal(counts.get('notebook_index'),'7');assert.equal(counts.get('product_items'),'1');
  assert.equal(counts.get('storage_observations'),'0');assert.equal(counts.get('frontier_catalog'),'0');
  assert.match(host.textContent,/Sua sessão de consulta/);assert.match(host.textContent,/Anotações de baseline nesta sessão/);
  assert.equal(host.querySelectorAll('[data-session-count]').find(node=>node.dataset.sessionCount==='selected').querySelector('strong').textContent,'1');
  assert.equal(host.querySelectorAll('[data-session-count]').find(node=>node.dataset.sessionCount==='annotations').querySelector('strong').textContent,'1');
}));

test('UX-UI-07 baseline annotation action names the combined destination without promoting source conflicts',()=>withUI({pane:'search',select:false},({ui,host})=>{
  const declared=entry('source-baseline',{baseline:true}),conflict=entry('conflicting-baseline',{baseline:true,is_baseline:false}),s=source([declared,conflict]),before=JSON.stringify(s);
  ui.source=s;ui.model=createTriageModel(s);ui.ledger=new SelectionLedger(s);
  let destination;ui.hooks.navigate=pane=>{destination=pane;};
  const overview=()=>{host.replaceChildren();ui.renderPane(host,'overview');return host.querySelectorAll('[data-session-count]').find(node=>node.dataset.sessionCount==='annotations');};
  let card=overview();assert.equal(card.querySelector('strong').textContent,'0');
  const action=card.querySelector('button');assert.equal(action.textContent,'Ver baselines da fonte e da sessão');
  assert.match(host.textContent,/inclui designações da fonte e anotações da sessão/);
  action.click();assert.equal(destination,'baselines');
  host.replaceChildren();assert.deepEqual(ui.renderPane(host,'baselines').map(item=>item.uid),['source-baseline']);
  ui.ledger.annotateBaseline(conflict,'Keep the note without overriding the declared conflict');
  card=overview();assert.equal(card.querySelector('strong').textContent,'1','The note exists even when confirmation is refused');
  assert.equal(ui.model.baseline(conflict,ui.ledger.annotations).confirmed,false);
  host.replaceChildren();assert.deepEqual(ui.renderPane(host,'baselines').map(item=>item.uid),['source-baseline']);
  assert.equal(JSON.stringify(s),before);
}));

test('UX-UI-07 overview session cards update after clear and annotation changes without rerendering source populations',()=>withUI({pane:'overview'},({ui,host,doc,a,b})=>{
  const metadata=entry('structure',{records:[]},'collection',{group:'$structure'}),s=source([metadata,a,b]);
  ui.source=s;ui.model=createTriageModel(s);ui.ledger=new SelectionLedger(s);ui.ledger.selectMany([a]);
  host.replaceChildren();ui.renderPane(host,'overview');ui.afterRender([]);
  const sourceCard=host.querySelector('[data-population-id="records"]'),sourceCount=sourceCard.querySelector('strong');
  const local=id=>host.querySelector(`[data-session-count="${id}"]`).querySelector('strong').textContent;
  assert.equal(local('selected'),'1');assert.equal(sourceCount.textContent,'2');
  doc.getElementById('native-clear-batch').focus();ui.ledger.clear();ui.selectionChanged();
  assert.equal(local('selected'),'0','The visible overview card must follow the actual cleared ledger');
  assert.equal(sourceCount.textContent,'2');assert.equal(host.querySelector('[data-population-id="records"]'),sourceCard,'Updating session cards must not rerender or change declared source populations');
  ui.ledger.annotateBaseline(a,'Local note');ui.syncBatch();assert.equal(local('annotations'),'1');
  ui.ledger.removeAnnotation(a);ui.syncBatch();assert.equal(local('annotations'),'0');
  assert.notEqual(doc.activeElement,doc.getElementById('native-clear-batch'));
}));

test('UX-UI-07 population actions name destination areas while keeping the existing collection context',()=>withUI({pane:'overview',select:false},({ui,host})=>{
  const metadata=entry('shape',{records:[],result_tables:[],product_items:[],resource_documents:[],storage_observations:[],frontier_catalog:[]},'collection',{group:'$structure'}),
    product=entry('product',{title:'Invented product'},'asset',{group:'product_items'}),
    docs=['doc-a','doc-b'].map(uid=>entry(uid,{title:'Invented document'},'asset',{group:'resource_documents'})),s=source([metadata,product,...docs]),before=JSON.stringify(s);
  ui.source=s;ui.model=createTriageModel(s);ui.ledger=new SelectionLedger(s);
  const context={pane:'overview',assetGroup:'resource_documents',page:4,columnPage:2};
  const start=controllerText.indexOf('function navigatePane(pane){'),end=controllerText.indexOf('\nfunction locateEntry(',start);
  assert(start>=0&&end>start,'The actual navigatePane source is required');
  ui.hooks.navigate=vm.runInNewContext('('+controllerText.slice(start,end)+')',{state:context,
    triage:{page:1,afterNavigation:()=>{}},closeDetail:()=>{},render:()=>{}},{timeout:1000});
  host.replaceChildren();ui.renderPane(host,'overview');
  const metric=id=>host.querySelector(`[data-population-id="${id}"]`);
  assert.equal(metric('product_items').querySelector('strong').textContent,'1');
  assert.equal(ui.model.items.filter(item=>item.group===context.assetGroup).length,2,'The remembered document population differs from the source product count');
  const action=metric('product_items').querySelector('button');assert.equal(action.textContent,'Abrir recursos e documentos');action.click();
  assert.equal(context.pane,'assets');assert.equal(context.assetGroup,'resource_documents','Opening the area preserves the current collection, rather than promising the product subset');
  for(const id of ['notebook_index','storage_observations','frontier_catalog']){
    const broad=metric(id).querySelector('button');assert.equal(broad.textContent,'Ver cobertura e origens');broad.click();assert.equal(context.pane,'coverage');
  }
  assert.equal(metric('records').querySelector('button').textContent,'Abrir registros');
  assert.equal(metric('result_tables').querySelector('button').textContent,'Abrir tabelas de resultados');
  assert.equal(JSON.stringify(s),before);
}));

for(const pane of ['selected','retention'])test(`UX-UI-05 clear-all in ${pane} moves focus away from its disabled control`,()=>withUI({pane,mode:'list'},({ui,doc})=>{
  const clear=doc.getElementById('native-clear-batch');clear.focus();
  ui.ledger.clear();ui.selectionChanged();
  assert.equal(clear.disabled,true);assert.equal(ui.ledger.size,0);
  assert.notEqual(doc.activeElement,clear,'A just-disabled clear button must not retain keyboard focus');
  assert.equal(doc.activeElement.isConnected,true);assert.equal(doc.activeElement.disabled,false);
  assert.equal(doc.activeElement.tagName,'H2');
}));
