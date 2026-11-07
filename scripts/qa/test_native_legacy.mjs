/** Presentation adapter regressions with synthetic data only.
 * Run: node scripts/qa/test_native_legacy.mjs
 * The in-memory DOM checks text, identity and callbacks; it is not visual evidence.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {buildNativeNavigation, nativeFragments} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {literalValue, literalText, familyIdentity, makePresentation, recordMatches, presentationColumns, catalogTitle, catalogStatus} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';
import {ASSET_COLLECTIONS, renderCatalog, renderPresentationDetail, renderReadingTable, renderRecordIndex, renderRecordPresentation, renderRelationPresentation, renderDatasetNotice} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_views.js';
import {mountEditorialTree} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_tree.js';
import * as legacyModel from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';

test('overview reads declared source populations separately and preserves absent/null/zero/exact counts',()=>{
  assert.equal(typeof legacyModel.snapshotPopulationMetrics,'function');
  const structure=entry('structure','collection',{records:[],result_tables:[],product_items:[],storage_observations:[],frontier_catalog:[],coverage:{}},{group:'$structure'});
  const coverage=rawEntry('coverage','collection','{"source_rows":{"operational_index":9007199254740993}}',{group:'coverage',pointer:'/coverage'});
  const items=[structure,coverage,entry('r1','record',{}),entry('r2','record',{}),entry('t1','table',{rows:[]},{group:'result_tables'}),
    ...['p1','p2','p3'].map(id=>entry(id,'asset',{}, {group:'product_items'})),entry('s1','collection',{}, {group:'storage_observations'}),
    ...['f1','f2','f3','f4'].map(id=>entry(id,'collection',{}, {group:'frontier_catalog'}))];
  const before=JSON.stringify(items),metrics=legacyModel.snapshotPopulationMetrics(items),byId=new Map(metrics.map(item=>[item.id,item]));
  assert.equal(byId.get('records').value,'2');assert.equal(byId.get('notebook_index').value,'9007199254740993');
  assert.equal(byId.get('product_items').value,'3');assert.equal(byId.get('storage_observations').value,'1');assert.equal(byId.get('frontier_catalog').value,'4');
  assert.equal(byId.get('result_tables').value,'1');assert.equal(byId.get('notebook_index').path,'/coverage/source_rows/operational_index');
  const missing=new Map(legacyModel.snapshotPopulationMetrics([entry('empty','collection',{records:[],product_items:[]},{group:'$structure'})]).map(m=>[m.id,m]));
  assert.equal(missing.get('product_items').value,'0');assert.equal(missing.get('notebook_index').value,'Não declarado');
  assert.equal(missing.get('storage_observations').value,'Não declarado');
  for(const [raw,expected]of [['0','0'],['null','NULL — valor declarado'],['""','"" — texto vazio declarado']]){
    const item=rawEntry('count','collection','{"source_rows":{"operational_index":'+raw+'}}',{group:'coverage',pointer:'/coverage'});
    assert.equal(legacyModel.snapshotPopulationMetrics([structure,item]).find(m=>m.id==='notebook_index').value,expected);
  }
  assert.equal(JSON.stringify(items),before);
});

test('requirements group only by declared nucleus, retain table scope/types and never invent business IDs or cells',()=>{
  assert.equal(typeof legacyModel.groupRequirementRows,'function');
  const rows=[
    entry('a1','row',{id:'RF-A',nucleus_id:'A',cells:{'Núcleo / Módulo':'A — invented module',Nome:'First'}},{table_uid:'T',ordinal:0}),
    entry('b1','row',{id:'RF-B',nucleus_id:'B',cells:{Nome:'Second'}},{table_uid:'T',ordinal:1}),
    entry('a2','row',{native_id:null,nucleus_id:'A',cells:{Nome:'Third'}},{table_uid:'T',ordinal:2}),
    entry('missing','row',{id:'RF-A-not-a-nucleus',cells:{Nome:'No declared nucleus'}},{table_uid:'T',ordinal:3}),
    entry('null','row',{nucleus_id:null,cells:{'Núcleo / Módulo':'Do not override NULL'}},{table_uid:'T',ordinal:4}),
    entry('empty','row',{nucleus_id:'',cells:{}},{table_uid:'T',ordinal:5}),
    rawEntry('number','row','{"nucleus_id":1,"cells":{}}',{table_uid:'T',ordinal:6}),
    entry('string','row',{nucleus_id:'1',cells:{}},{table_uid:'T',ordinal:7}),
    entry('other-table','row',{nucleus_id:'A',cells:{}},{table_uid:'OTHER',ordinal:0})];
  const before=JSON.stringify(rows),groups=legacyModel.groupRequirementRows(rows);
  assert.equal(groups.length,8);assert.deepEqual(groups[0].rows.map(r=>r.uid),['a1','a2']);
  assert.match(groups[0].label,/A — invented module/);
  assert.equal(groups.find(group=>group.rows.some(row=>row.uid==='missing')).label,'Não declarado');
  assert.notEqual(groups.find(g=>g.rows[0].uid==='number').key,groups.find(g=>g.rows[0].uid==='string').key);
  assert.notEqual(groups[0].key,groups.find(g=>g.rows[0].uid==='other-table').key);
  assert.equal(new Set(groups.flatMap(group=>group.rows.map(row=>row.uid))).size,rows.length);
  assert.equal(JSON.stringify(rows),before,'Grouping does not mutate rows or manufacture nucleus cells/native IDs');
  assert.equal(JSON.parse(rows[2].raw_json).cells['Núcleo / Módulo'],undefined);
  assert.equal(JSON.parse(rows[2].raw_json).native_id,null);
});

test('nucleus presentation pages preserve every filtered occurrence and exact export data',()=>{
  const rows=Array.from({length:205},(_,index)=>entry('paged-'+index,'row',{native_id:null,nucleus_id:['INVENTED-A','INVENTED-B','UNKNOWN'][index%3],cells:{Nome:'Invented '+index}},{table_uid:'PAGED',ordinal:index}));
  const before=JSON.stringify(rows),csvBefore=legacyModel.typedTableCsv({uid:'PAGED'},rows,['Nome']);
  const grouped=legacyModel.groupRequirementRows(rows,{sourceId:'fixture-source',snapshot:'fixture-revision'}),ordered=grouped.flatMap(group=>group.rows);
  const pages=[ordered.slice(0,100),ordered.slice(100,200),ordered.slice(200)];
  assert.deepEqual(pages.map(page=>page.length),[100,100,5]);
  assert.equal(new Set(pages.flat().map(row=>row.uid)).size,205);
  assert.ok(grouped.some(group=>group.rows.some(row=>pages[0].includes(row))&&group.rows.some(row=>pages[1].includes(row))),'A declared nucleus may continue on another page');
  assert.ok(grouped.some(group=>group.label==='UNKNOWN'),'Declared UNKNOWN stays distinct from absence');
  assert.equal(JSON.stringify(rows),before);assert.equal(legacyModel.typedTableCsv({uid:'PAGED'},rows,['Nome']),csvBefore);
});

test('typed CSV preserves absent/null/empty/typed numbers/formulas and full row identity', () => {
  const raws = [
    '{"cells":{},"native_id":null}',
    '{"cells":{"x":""},"id":"same"}',
    '{"cells":{"x":null},"id":"same"}',
    '{"cells":{"x":"null"}}',
    '{"cells":{"x":9007199254740993}}',
    '{"cells":{"x":"9007199254740993"}}',
    '{"cells":{"x":"=1+1"}}',
    '{"cells":{"x":"\'=1+1"}}',
    '{"cells":{"x":-1.25e-7,"line\\nquote":"a,\\\"b\\n"}}',
  ];
  const rows = raws.map((raw_json, i) => ({uid:'view:'+i,pointer:'/result_tables/0/rows/'+i,raw_json}));
  const before = JSON.stringify(rows);
  const csv = legacyModel.typedTableCsv({uid:'=hostile-table'}, rows, ['x','line\nquote']);
  // Independent RFC4180 reader, including embedded newlines and quote escapes.
  const records = []; let record=[],field='',quoted=false;
  for(let i=0;i<csv.length;i++){
    const ch=csv[i];
    if(ch==='"'){if(quoted&&csv[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}
    else if(!quoted&&ch===','){record.push(field);field='';}
    else if(!quoted&&ch==='\r'&&csv[i+1]==='\n'){record.push(field);records.push(record);record=[];field='';i++;}
    else field+=ch;
  }
  record.push(field);records.push(record);
  assert.equal(records.length, rows.length+1);
  for(const record of records)for(const cell of record)assert.doesNotMatch(cell,/^[\s\u0000-\u001f]*[=+@-]/);
  const values=records.slice(1).map((record,i)=>{
    assert.equal(record[0],'atlas-table-csv/1');
    assert.equal(JSON.parse(record[1]),'=hostile-table');
    assert.equal(JSON.parse(record[2]),rows[i].uid);
    assert.equal(JSON.parse(record[3]),rows[i].pointer);
    assert.equal(record[4],raws[i]);
    return record[5];
  });
  assert.equal(new Set(values).size,values.length);
  assert.equal(values[0],'{"type":"missing"}');
  assert.equal(values[4],'{"type":"integer","value":9007199254740993}');
  assert.equal(values[8],'{"type":"number","value":-1.25e-7}');
  assert.equal(JSON.parse(values[6]).value,'=1+1');
  assert.equal(JSON.stringify(rows),before);
  assert.ok(legacyModel.typedTableCsv({uid:'T'},[],[]).includes('atlas.row_json'));
});

const NULL = 'NULL — valor declarado';
const freeze = value => {
  if (value && typeof value === 'object' && !Object.isFrozen(value)) {
    for (const child of Object.values(value)) freeze(child);
    Object.freeze(value);
  }
  return value;
};

// Build the verified DTO's scalar fields directly from JSON tokens. No numeric
// fixture passes through JSON.parse or a Number conversion.
function rawEntry(uid, kind, raw, extra = {}) {
  const parts = raw.trim().startsWith('{') ? nativeFragments(raw, {all: true}) : new Map([['value', raw]]);
  const fields = [...parts].filter(([, token]) => token[0] !== '{' && token[0] !== '[').map(([name, token]) => ({
    name,
    type: token === 'null' ? 'null' : token[0] === '"' ? 'string' : /^(true|false)$/.test(token) ? 'boolean' : /[.eE]/.test(token) ? 'number' : 'integer',
    text: token[0] === '"' ? JSON.parse(token) : token,
  }));
  const field = name => fields.find(f => f.name === name);
  const text = (...names) => names.map(field).find(f => f?.type === 'string' && f.text)?.text ?? null;
  const identity = field('native_id') ?? (kind === 'record' ? field('id') : null);
  return freeze({
    uid, kind, group: ({record: 'records', node: 'lineage_graph.nodes', relation: 'edges', asset: 'resources', row: 'result_tables'})[kind] ?? 'misc',
    title: text('title', 'label', 'name', 'id', 'native_id', 'key') ?? kind,
    native_id: !identity || identity.type === 'null' ? null : identity.text,
    source_key: text('key', 'id'), family: text('family'),
    status: text('execution_state', 'status', 'result_state', 'result_group'),
    parent_uid: null, fields, raw_json: raw, ...extra,
  });
}
const entry = (uid, kind, value, extra) => rawEntry(uid, kind, JSON.stringify(value), extra);

// Only APIs used by the presentation modules are implemented. An HTML sink or
// executable element fails immediately instead of silently passing this harness.
class MemoryNode {
  constructor(tag, text = null) {
    this.tagName = tag === '#text' ? '#text' : tag.toUpperCase();
    this.localName = tag;
    this.nodeType = tag === '#text' ? 3 : 1;
    this._text = text ?? '';
    this._nodes = [];
    this._attributes = new Map();
    this._listeners = new Map();
    this.dataset = Object.create(null);
    this.className = '';
    this.parentNode = null;
    this.clientWidth = 1024;
    this.clientHeight = 600;
    this._captures = new Set();
    this.classList = {
      add: (...names) => { this.className = [...new Set([...this.className.split(/\s+/).filter(Boolean), ...names])].join(' '); },
      contains: name => this.className.split(/\s+/).includes(name),
    };
  }
  get childNodes() { return this._nodes; }
  get children() { return this._nodes.filter(n => n.nodeType === 1); }
  get childElementCount() { return this.children.length; }
  get firstElementChild() { return this.children[0] ?? null; }
  get lastChild() { return this._nodes.at(-1) ?? null; }
  get textContent() { return this.nodeType === 3 ? this._text : this._nodes.map(n => n.textContent).join(''); }
  set textContent(value) {
    const text = String(value);
    if (this.nodeType === 3) { this._text = text; return; }
    this.replaceChildren();
    if (text) this.append(new MemoryNode('#text', text));
  }
  set innerHTML(_) { throw Error('HTML sink is forbidden in this presentation test'); }
  set outerHTML(_) { throw Error('HTML sink is forbidden in this presentation test'); }
  append(...nodes) {
    for (const value of nodes) {
      const node = value instanceof MemoryNode ? value : new MemoryNode('#text', String(value));
      if (node.parentNode) node.parentNode._nodes.splice(node.parentNode._nodes.indexOf(node), 1);
      node.parentNode = this;
      this._nodes.push(node);
    }
  }
  appendChild(node) { this.append(node); return node; }
  replaceChildren(...nodes) { for (const node of this._nodes) node.parentNode = null; this._nodes = []; this.append(...nodes); }
  setAttribute(name, value) {
    const text = String(value);
    this._attributes.set(name, text);
    if (name === 'class') this.className = text;
    if (name.startsWith('data-')) this.dataset[name.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase())] = text;
  }
  getAttribute(name) { return name === 'class' ? this.className : this._attributes.get(name) ?? null; }
  addEventListener(type, fn) { if (!this._listeners.has(type)) this._listeners.set(type, []); this._listeners.get(type).push(fn); }
  dispatchEvent(event) {
    event.target ??= this;
    event.preventDefault ??= () => {};
    event.stopPropagation ??= () => {};
    for (const fn of this._listeners.get(event.type) ?? []) fn(event);
  }
  click() { this.dispatchEvent({type: 'click'}); }
  querySelector(selector) { return descendants(this).find(n => selector.startsWith('.') ? n.classList.contains(selector.slice(1)) : n.localName === selector) ?? null; }
  hasPointerCapture(id) { return this._captures.has(id); }
  setPointerCapture(id) { this._captures.add(id); }
  releasePointerCapture(id) { this._captures.delete(id); }
  getBoundingClientRect() { return {left: 0, top: 0, width: this.clientWidth, height: this.clientHeight}; }
}
function descendants(root) { return root.childNodes.flatMap(n => [n, ...descendants(n)]); }
const tags = (root, name) => descendants(root).filter(n => n.localName === name);
function withDOM(fn) {
  const previous = globalThis.document;
  globalThis.document = {
    createElement: tag => { assert.notEqual(tag.toLowerCase(), 'script', 'a renderer must not create scripts'); return new MemoryNode(tag); },
    createElementNS: (_, tag) => { assert.notEqual(tag.toLowerCase(), 'script', 'a renderer must not create SVG scripts'); return new MemoryNode(tag); },
    createTextNode: text => new MemoryNode('#text', String(text)),
  };
  try { return fn(new MemoryNode('main')); }
  finally { if (previous === undefined) delete globalThis.document; else globalThis.document = previous; }
}

test('relation endpoints retain the exact native resolution, key precedence and collisions', () => {
  const a = entry('record-a', 'record', {id: 'A', family: 'F', source_ids: ['alias-a']});
  const b = entry('record-b', 'record', {id: 'B', family: 'F'});
  const sharedNode = entry('node-a', 'node', {key: 'A'});
  const node = entry('node-only', 'node', {key: 'node-only'});
  const duplicate = entry('record-a-again', 'record', {id: 'A', family: 'F'});
  const cases = [
    ['absent key', {from: 'alias-a', to: 'B'}, [], 'UNIQUE', 'record-a'],
    ['key overrides fallback', {from: 'A', from_key: 'B', to: 'B'}, [], 'UNIQUE', 'record-b'],
    ['explicit null key', {from: 'A', from_key: null, to: 'B'}, [], 'NOT_DECLARED', null],
    ['unresolved key', {from: 'A', from_key: 'not-present', to: 'B'}, [], 'UNRESOLVED', null],
    ['record/node collision', {from: 'A', to: 'B'}, [sharedNode], 'COLLISION', null],
    ['duplicate record ID', {from: 'A', to: 'B'}, [duplicate], 'COLLISION', null],
    ['key resolves to technical node', {from: 'A', from_key: 'node-only', to: 'B'}, [node], 'UNIQUE', null],
    ...[42, false, ['A'], {id: 'A'}].map(value => ['composite or nontext key ' + JSON.stringify(value), {from: 'A', from_key: value, to: 'B'}, [], 'NOT_INTERPRETED', null]),
  ];
  for (const [name, data, more, expected, chosen] of cases) {
    for (const testedEndpoint of ['from', 'to']) {
      const value = testedEndpoint === 'from' ? data : Object.fromEntries(Object.entries(data).map(([key, val]) => [key.startsWith('from') ? 'to' + key.slice(4) : key.startsWith('to') ? 'from' + key.slice(2) : key, val]));
      const relation = entry('edge', 'relation', value);
      const entries = freeze([a, b, ...more, relation]);
      const original = JSON.stringify(entries);
      const navigation = buildNativeNavigation(entries);
      const edge = makePresentation(entries).edges[0];
      for (const endpoint of ['from', 'to']) {
        const key = Object.hasOwn(value, endpoint + '_key') ? endpoint + '_key' : endpoint;
        const reference = navigation.outgoing.get(relation.uid).find(ref => ref.label === key);
        assert.equal(edge[endpoint + 'Resolution'], reference.resolution, name + ': native resolution');
        assert.deepEqual(edge[endpoint + 'Candidates'].map(e => e.uid), reference.targets, name + ': all candidates survive');
        assert.equal(edge[endpoint], reference.resolution === 'UNIQUE' && navigation.byUid.get(reference.targets[0]).kind === 'record' ? reference.targets[0] : null, name + ': tree only uses a unique record');
      }
      assert.equal(edge[testedEndpoint + 'Resolution'], expected, name);
      assert.equal(edge[testedEndpoint], chosen, name);
      if (value[testedEndpoint + '_key'] === null) assert.equal(edge['original' + (testedEndpoint === 'from' ? 'From' : 'To')], null);
      assert.equal(JSON.stringify(entries), original, 'resolving a relation must not mutate its verified source');
    }
  }
});

test('numeric identities remain lexical and separate from text identities', () => {
  const numeric = rawEntry('numeric-record', 'record', '{"id":9007199254740993,"native_id":9007199254740993}');
  const text = entry('text-record', 'record', {id: '9007199254740993'});
  const relations = [
    rawEntry('numeric-edge', 'relation', '{"from":9007199254740993,"to":"9007199254740993"}'),
    rawEntry('numeric-key', 'relation', '{"from":"9007199254740993","from_key":9007199254740993}'),
  ];
  const model = makePresentation([numeric, text, ...relations]);
  assert.equal(model.edges[0].from, numeric.uid);
  assert.equal(model.edges[0].to, text.uid);
  assert.equal(model.edges[1].fromResolution, 'NOT_INTERPRETED');
  assert.equal(model.edges[1].from, null);
  assert.equal(literalText(model.edges[0].originalFrom), '9007199254740993');
  assert.equal(literalText(model.records[0].original_id), '9007199254740993');
  assert.equal(numeric.raw_json, '{"id":9007199254740993,"native_id":9007199254740993}');
});

test('record occurrences preserve UID, native ID, structural key and explicit null identity', () => {
  const a = entry('occurrence-a', 'record', {id: 'repeated', native_id: null, title: 'First'});
  const b = entry('occurrence-b', 'record', {id: 'repeated', native_id: 'science-id', title: 'Second'});
  const model = makePresentation([a, b]);
  assert.deepEqual(model.records.map(r => r.id), ['occurrence-a', 'occurrence-b']);
  assert.deepEqual(model.records.map(r => r.original_id), ['repeated', 'repeated']);
  assert.equal(model.byUid.get(a.uid).entry.native_id, null);
  assert.equal(model.byUid.get(a.uid).entry.source_key, 'repeated');
  assert.equal(model.byUid.get(b.uid).entry.native_id, 'science-id');
  withDOM(host => {
    const selected = [];
    renderRecordIndex(host, model.records, 2, b.uid, e => selected.push(e.uid));
    const buttons = tags(host, 'button');
    assert.equal(buttons.length, 2);
    buttons[0].click(); buttons[1].click();
    assert.deepEqual(selected, [a.uid, b.uid]);
    assert.equal(buttons[1].getAttribute('aria-current'), 'true');
  });
});

test('null, scalars and arrays stay inspectable in records and resource catalogs', () => {
  const rawValues = ['null', 'false', '"text value"', '9007199254740993', '0.12345678901234567890', '[]'];
  for (const kind of ['record', 'asset']) {
    const entries = freeze(rawValues.map((raw, index) => rawEntry(kind + index, kind, raw)));
    const model = makePresentation(entries), navigation = buildNativeNavigation(entries);
    assert.equal(model.records.length, kind === 'record' ? rawValues.length : 0);
    for (const e of entries) withDOM(host => {
      renderPresentationDetail(host, e, model, navigation, () => {});
      assert.ok(host.textContent.includes('Valor literal: ' + literalText(model.read(e))), e.raw_json);
      assert.equal(e.raw_json, rawValues[Number(e.uid.slice(kind.length))]);
    });
    withDOM(host => {
      if (kind === 'record') renderRecordPresentation(host, model.records, () => {});
      else renderCatalog(host, entries, model, () => {});
      assert.equal(tags(host, 'tbody')[0].children.length, rawValues.length);
    });
  }
});

test('catalog includes classical products and preserves explicit null/empty/unknown state precedence', () => {
  assert.ok(ASSET_COLLECTIONS.some(([name]) => name === 'products'));
  const declaredNull = literalValue('{"documentary_status":null,"label":null,"status":"PASS","title":"Fallback"}');
  assert.equal(catalogStatus(declaredNull), null);
  assert.equal(catalogTitle(declaredNull), null);
  for (const [raw, expected] of [
    ['{}', undefined],
    ['{"documentary_status":"","status":"PASS"}', ''],
    ['{"documentary_status":"UNKNOWN","status":"PASS"}', 'UNKNOWN'],
    ['{"documentary_status":false,"status":"PASS"}', false],
    ['{"status":"PASS"}', 'PASS'],
  ]) assert.equal(catalogStatus(literalValue(raw)), expected);
  const product = rawEntry('product', 'asset', '{"documentary_status":null,"id":"product","label":null,"status":"PASS","title":"Fallback"}', {group: 'products'});
  const model = makePresentation([product]);
  withDOM(host => {
    let selected;
    renderCatalog(host, [product], model, e => { selected = e; });
    const row = tags(host, 'tbody')[0].children[0];
    assert.equal(row.children[0].textContent, NULL);
    assert.equal(row.children[2].textContent, NULL);
    tags(row, 'button')[0].click();
    assert.equal(selected, product);
  });
});

test('search retains native identifiers, aliases, runs, accent folding and exact numeric fields', () => {
  const e = rawEntry('search-record', 'record', '{"family":"Família Árvore","id":"structural-1","kind":"run","native_id":"run-unique","result_group":null,"run_id":"execution-42","source_ids":["run-alias"],"title":"Ação sintética","value":9007199254740993}');
  const r = makePresentation([e]).records[0];
  for (const query of ['run-unique', 'run-alias', 'execution-42', 'structural-1', 'acao sintetica', 'familia arvore', '9007199254740993']) assert.equal(recordMatches(r, {query}), true, query);
  assert.equal(recordMatches(r, {query: 'does-not-exist'}), false);
  assert.equal(recordMatches(r, {family: familyIdentity('Família Árvore').key, kind: 'run', status: NULL}), true);
  assert.equal(recordMatches(r, {kind: 'product'}), false);
  assert.equal(recordMatches(r, {status: 'PASS'}), false);
});

test('literal decoding preserves nested values, escaped delimiters and all numeric lexemes', () => {
  const raw = '{"array":[null,false,"quoted \\\" ] }, text",9007199254740993,{"number":1.2300e-20}],"decimal":0.12345678901234567890,"empty":"","negativeZero":-0,"prototype":{"__proto__":{"polluted":true}},"unknown":"UNKNOWN"}';
  const data = literalValue(raw);
  assert.equal(literalText(data.decimal), '0.12345678901234567890');
  assert.equal(literalText(data.negativeZero), '-0');
  assert.equal(literalText(data.array[3]), '9007199254740993');
  assert.equal(literalText(data.array[4].number), '1.2300e-20');
  assert.equal(data.array[0], null);
  assert.equal(data.array[1], false);
  assert.equal(data.array[2], 'quoted " ] }, text');
  assert.equal(literalText(data.empty), '"" — texto vazio declarado');
  assert.equal(literalText(data.unknown), 'UNKNOWN');
  assert.equal(literalText(undefined), 'Não declarado');
  assert.equal(Object.getPrototypeOf(data), null);
  assert.equal(Object.getPrototypeOf(data.prototype), null);
  assert.equal(data.prototype.__proto__.polluted, true);
  assert.equal({}.polluted, undefined);
});

test('reading order is reversible and rendering never rewrites cells or numeric source lexemes', () => {
  const columns = freeze(['Métrica', 'Critérios de Aceitação', 'Descrição', 'Nome', 'Núcleo / Módulo', 'ID', 'Empty', 'NULL', 'MISSING', 'UNKNOWN', 'Decimal']);
  const expected = ['ID', 'Núcleo / Módulo', 'Nome', 'Descrição', 'Critérios de Aceitação', 'Métrica', 'Empty', 'NULL', 'MISSING', 'UNKNOWN', 'Decimal'];
  assert.deepEqual(presentationColumns(columns), expected);
  assert.deepEqual(columns, ['Métrica', 'Critérios de Aceitação', 'Descrição', 'Nome', 'Núcleo / Módulo', 'ID', 'Empty', 'NULL', 'MISSING', 'UNKNOWN', 'Decimal']);
  const raw = '{"cells":{"Decimal":0.12345678901234567890,"Empty":"","ID":"RF-01","Métrica":9007199254740993,"NULL":null,"Nome":"Name","UNKNOWN":"UNKNOWN"},"id":"row-original"}';
  const row = rawEntry('row-uid', 'row', raw, {ordinal: 0, table_uid: 'table', cells: {
    Decimal: {text: '0.12345678901234567890', type: 'number'}, Empty: {text: '', type: 'string'}, ID: {text: 'RF-01', type: 'string'},
    Métrica: {text: '9007199254740993', type: 'integer'}, NULL: {text: 'null', type: 'null'}, Nome: {text: 'Name', type: 'string'}, UNKNOWN: {text: 'UNKNOWN', type: 'string'},
  }});
  const before = JSON.stringify(row);
  for (const [order, expectedColumns] of [['presentation', expected.slice(0,5)], ['original', columns]]) withDOM(host => {
    let selected;
    assert.deepEqual(renderReadingTable(host, [row], columns, value => { selected = value; }, {order}), expectedColumns);
    assert.deepEqual(tags(host, 'th').map(th => th.textContent), expectedColumns);
    const cells = tags(host, 'tbody')[0].children[0].children;
    const byColumn = new Map(cells.map(cell => [cell.dataset.column, cell]));
    for (const [name, value] of [['Métrica', '9007199254740993'], ['Decimal', '0.12345678901234567890'], ['Empty', ''], ['NULL', NULL], ['MISSING', 'MISSING — chave ausente'], ['UNKNOWN', 'UNKNOWN']]) if(byColumn.has(name))assert.equal(byColumn.get(name).textContent,value,name);else assert.equal(order,'presentation','Every original column must remain available in original order');
    if(order==='presentation')assert.ok(host.textContent.includes('5 de 11 colunas'));
    else assert.equal(byColumn.size,columns.length);
    tags(cells[0], 'button')[0].click();
    assert.equal(selected, row);
    assert.equal(JSON.stringify(row), before);
    assert.equal(row.raw_json, raw);
  });
});

test('renderers insert hostile labels as text and callbacks keep occurrence identity', () => {
  const hostile = '<img src=x onerror="globalThis.injected=1"><script>throw 1</script>';
  const e = entry('hostile-product', 'asset', {id: 'p', label: hostile, documentary_status: 'UNKNOWN'}, {group: 'products'});
  const model = makePresentation([e]);
  withDOM(host => {
    renderCatalog(host, [e], model, () => {});
    renderPresentationDetail(host, e, model, buildNativeNavigation([e]), () => {});
    assert.ok(host.textContent.includes(hostile));
    assert.equal(tags(host, 'img').length, 0);
    assert.equal(tags(host, 'script').length, 0);
    assert.equal(globalThis.injected, undefined);
  });
});

test('editorial tree tolerates string proofs and null themes while preserving selection and lexical evidence', () => {
  const a = entry('tree-a', 'record', {id: 'A', title: 'Record A', family: 'F1'});
  const b = entry('tree-b', 'record', {id: 'B', title: 'Record B', family: 'F2'});
  const edge = rawEntry('tree-edge', 'relation', '{"from":"A","proofs":"source-ref","reason":9007199254740993,"to":"B","type":"PREDECESSOR"}');
  for (const themes of [null, [null], [null, {id: 'reviewed', title: 'Declared theme', families: ['F1', 'F2']}], [false, 'literal', 7]]) {
    const editorial = entry('editorial-map', 'collection', {schema: 'r4-atlas-editorial-map/1', themes}, {group: 'editorial_map'});
    const model = makePresentation([a, b, edge, editorial]);
    withDOM(host => {
      let selected;
      const persistent = {expanded: new Set(model.records.map(r => r.nativeFamilyKey)), relations: true};
      const tree = mountEditorialTree(host, model, model.records, e => { selected = e; }, persistent);
      const proof = tags(host, 'path').find(path => path.classList.contains('tree-provenance'));
      assert.ok(proof, 'the resolved relation is rendered');
      assert.ok(proof.textContent.includes('source-ref'));
      assert.ok(proof.textContent.includes('9007199254740993'));
      assert.ok(!proof.textContent.includes('[object Object]'));
      assert.equal(tree.locate(b.uid), true);
      assert.equal(selected, b);
      assert.equal(tree.locate('missing'), false);
      assert.ok(tree.camera().every(Number.isFinite));
      tree.destroy();
      assert.equal(persistent.selected, b.uid);
      assert.ok(persistent.box.every(Number.isFinite));
    });
  }
});

test('family values of different JSON types remain separate and navigable', () => {
  const records = freeze([
    entry('family-absent', 'record', {id: 'absent'}),
    entry('family-null', 'record', {id: 'null', family: null, native_family: null}),
    entry('family-empty', 'record', {id: 'empty', family: ''}),
    entry('family-unknown', 'record', {id: 'unknown', family: 'UNKNOWN'}),
    rawEntry('family-number', 'record', '{"family":9007199254740993,"id":"number"}'),
  ]);
  const original = JSON.stringify(records), model = makePresentation(records);
  assert.equal(new Set(model.records.map(r => r.familyKey)).size, records.length);
  assert.equal(new Set(model.records.map(r => r.family)).size, records.length);
  assert.equal(literalText(model.read(records[4]).family), '9007199254740993');
  withDOM(host => {
    const selected = [];
    const tree = mountEditorialTree(host, model, model.records, e => selected.push(e.uid));
    for (const record of records) assert.equal(tree.locate(record.uid), true);
    assert.deepEqual(selected, records.map(e => e.uid));
    tree.destroy();
  });
  assert.equal(JSON.stringify(records), original);
});

test('ambiguous endpoints do not become editorial evidence arrows', () => {
  const a = entry('ambiguous-a', 'record', {id: 'same', family: 'F'});
  const b = entry('ambiguous-b', 'record', {id: 'B', family: 'F'});
  const node = entry('ambiguous-node', 'node', {key: 'same'});
  const edge = entry('ambiguous-edge', 'relation', {from: 'same', to: 'B', type: 'PREDECESSOR'});
  const model = makePresentation([a, b, node, edge]);
  withDOM(host => {
    const tree = mountEditorialTree(host, model, model.records, () => {}, {expanded: new Set(model.records.map(r => r.nativeFamilyKey)), relations: true});
    assert.equal(tags(host, 'path').filter(path => path.classList.contains('tree-provenance')).length, 0);
    tree.destroy();
  });
  withDOM(host => {
    renderRelationPresentation(host, model.edges, model, () => {});
    assert.ok(host.textContent.includes('AMBIGUOUS (2)'));
    assert.ok(host.textContent.includes(node.uid), 'the technical candidate must remain discoverable');
  });
});

test('long unbroken editorial titles wrap without losing the exact accessible title', () => {
  const title='correction-run-'+ 'b9f599d6338e22125b1faaa5'.repeat(3)+'😀';
  const record=entry('long-editorial-title','record',{id:'long',title,family:'F'}),model=makePresentation([record]);
  withDOM(host=>{
    const tree=mountEditorialTree(host,model,model.records,()=>{},{expanded:new Set([model.records[0].nativeFamilyKey])});
    const card=tags(host,'g').find(n=>n.classList.contains('svg-record'));
    const titleLines=tags(card,'text').slice(0,2);
    assert.equal(titleLines.length,2);
    assert.ok(titleLines.every(n=>Array.from(n.textContent).length<=28));
    assert.ok(titleLines[1].textContent.endsWith('…'));
    assert.equal(card.getAttribute('aria-label'),title);
    assert.ok(tags(card,'title')[0].textContent.includes(title));
    tree.destroy();
  });
});

test('relation presentation distinguishes explicit null, uninterpreted key and unresolved reference', () => {
  const record = entry('relation-record', 'record', {id: 'R', family: 'F'});
  for (const [key, expected] of [[null, 'NOT_DECLARED'], [['R'], 'NOT_INTERPRETED'], ['missing', 'UNRESOLVED']]) {
    const edge = entry('state-edge', 'relation', {from: 'R', from_key: key, to: 'R'});
    const model = makePresentation([record, edge]);
    withDOM(host => {
      renderRelationPresentation(host, model.edges, model, () => {});
      const sourceCell = tags(host, 'tbody')[0].children[0].children[0];
      assert.ok(sourceCell.textContent.includes(expected), 'expected ' + expected + '; received ' + sourceCell.textContent);
      if (key === null) assert.ok(sourceCell.textContent.includes(NULL));
      if (expected !== 'UNRESOLVED') assert.ok(!sourceCell.textContent.includes('UNRESOLVED'), 'no invented unresolved state');
    });
  }
});

test('presentation ordering tolerates existing replacement characters without rewriting headers',()=>{
  const original=['Autores','Crit�rios de aceite','Descri��o','ID','Nome','N�cleo / M�dulo'];
  const before=[...original];assert.deepEqual(presentationColumns(original),['ID','N�cleo / M�dulo','Nome','Descri��o','Crit�rios de aceite','Autores']);assert.deepEqual(original,before);
  assert.notEqual(literalText(literalValue('[]')),literalText(literalValue('{}')));
  assert.notEqual(literalText(literalValue('[]')),literalText(literalValue('""')));
});

test('structured kind and state metadata never coerce through object prototypes',()=>{
  const r=entry('structured-record','record',{id:'R',title:'Structured record',kind:{literal:9007199254740991},result_group:{state:null},family:'F'});
  const map=entry('structured-map','collection',{schema:'r4-atlas-editorial-map/1',themes:[{id:'T',title:'Theme',subtitle:{literal:null},families:['F']}]},{group:'editorial_map'});
  const model=makePresentation([r,map]);
  assert.ok(recordMatches(model.records[0],{kind:model.records[0].filterKind}));
  withDOM(host=>{renderRecordIndex(host,model.records,1,null,()=>{});renderRecordPresentation(host,model.records,()=>{});const tree=mountEditorialTree(host,model,model.records,()=>{},{expanded:new Set(model.records.map(r=>r.nativeFamilyKey))});tree.destroy();assert.ok(host.textContent.includes('Structured record'));});
});

test('prototype-shaped declared labels do not resolve to inherited dictionary members',()=>{
 const r=entry('prototype-record','record',{id:'p',title:'Declared prototype label',kind:'constructor',result_group:'__proto__',family:'F'}),model=makePresentation([r]);
 withDOM(host=>{renderRecordPresentation(host,model.records,()=>{});assert.ok(host.textContent.includes('constructor'));assert.ok(!host.textContent.includes('[native code]'));assert.ok(!host.textContent.includes('[object Object]'));});
});

test('family identity retains JSON types, presence and numeric lexemes inside composites', () => {
  const values = ['1', '"1"', '1.0', '-0', '0', 'null', 'false', '"false"', '[]', '{}', '""', '[1]', '["1"]'];
  const identities = values.map(raw => familyIdentity(literalValue(raw)));
  assert.equal(new Set(identities.map(i => i.key)).size, values.length);
  assert.equal(familyIdentity(1).key, familyIdentity(literalValue('1')).key);
  assert.equal(familyIdentity(literalValue('1')).type, 'integer');
  assert.equal(familyIdentity(literalValue('1.0')).type, 'number');
  assert.equal(familyIdentity('1').type, 'string');
  assert.equal(familyIdentity(undefined, false).present, false);
  assert.equal(familyIdentity(null).present, true);
  assert.notEqual(familyIdentity(undefined, false).key, familyIdentity(null).key);
  const raw = '{"decimal":0.12345678901234567890,"integer":9007199254740993,"nested":[-0,1.2300e-20,"9007199254740993"]}';
  const identity = familyIdentity(literalValue(raw));
  assert.equal(identity.type, 'object');
  assert.equal(JSON.parse(identity.key)[3], raw, 'the opaque key contains exact canonical numeric tokens, not rounded values');
  assert.notEqual(identity.key, familyIdentity(literalValue(raw.replace('9007199254740993', '9007199254740992'))).key);
  assert.notEqual(identity.key, familyIdentity(raw).key, 'an object family and a string containing JSON remain different');
});

test('typed family keys isolate homonymous records without changing normal labels or raw exports', () => {
  const records = freeze([
    rawEntry('number-one', 'record', '{"family":1,"id":"number"}'),
    entry('text-one', 'record', {family: '1', id: 'text'}),
    entry('null-family', 'record', {family: null, id: 'null'}),
    entry('null-label-text', 'record', {family: 'NULL — família declarada', id: 'null-label'}),
    entry('missing-family', 'record', {id: 'missing'}),
    entry('missing-label-text', 'record', {family: 'Família não declarada', id: 'missing-label'}),
    entry('normal-family', 'record', {family: 'RNF', id: 'normal'}),
  ]);
  const before = JSON.stringify(records), model = makePresentation(records);
  assert.equal(new Set(model.records.map(r => r.familyKey)).size, records.length);
  assert.equal(new Set(model.records.map(r => r.family)).size, records.length);
  assert.equal(model.byUid.get('number-one').family, '1 [integer]');
  assert.equal(model.byUid.get('text-one').family, '1 [texto]');
  assert.equal(model.byUid.get('normal-family').family, 'RNF');
  for (const r of model.records) {
    assert.equal(model.familyOf(r.entry).key, r.familyKey);
    assert.equal(model.familyLabel(r.familyKey), r.family);
    assert.deepEqual(model.records.filter(candidate => recordMatches(candidate, {family: r.familyKey})).map(candidate => candidate.id), [r.id]);
    assert.equal(r.entry.raw_json, records.find(e => e.uid === r.id).raw_json);
  }
  assert.equal(recordMatches(model.byUid.get('normal-family'), {family: 'RNF'}), false, 'a display label is never interpreted as an identity key');
  assert.equal(JSON.stringify(records), before);
  assert.equal(literalText(model.read(records[0]).family), '1');
  assert.equal(model.read(records[2]).family, null);
  assert.equal(Object.hasOwn(model.read(records[4]), 'family'), false);
});

test('broad DTO family filters use the same typed namespace and only fall back when raw family is absent', () => {
  const entries = freeze([
    rawEntry('asset-number', 'asset', '{"family":1,"id":"number"}'),
    entry('asset-text', 'asset', {family: '1', id: 'text'}),
    entry('asset-fallback', 'asset', {id: 'fallback'}, {family: 'RNF'}),
    entry('asset-raw-null', 'asset', {family: null, id: 'null'}, {family: 'RNF'}),
    entry('asset-missing', 'asset', {id: 'missing'}, {family: null}),
    entry('asset-empty-fallback', 'asset', {id: 'empty'}, {family: ''}),
  ]);
  const before = JSON.stringify(entries), model = makePresentation(entries);
  assert.equal(model.records.length, 0);
  assert.equal(model.familyOf(entries[0]).key, familyIdentity(literalValue('1')).key);
  assert.equal(model.familyOf(entries[1]).key, familyIdentity('1').key);
  assert.equal(model.familyLabel(model.familyOf(entries[0]).key), '1 [integer]');
  assert.equal(model.familyLabel(model.familyOf(entries[1]).key), '1 [texto]');
  assert.equal(model.familyOf(entries[2]).key, familyIdentity('RNF').key);
  assert.equal(model.familyLabel(model.familyOf(entries[2]).key), 'RNF');
  assert.equal(model.familyOf(entries[3]).key, familyIdentity(null).key, 'explicit raw null wins over a DTO string');
  assert.equal(model.familyOf(entries[4]).key, familyIdentity(undefined, false).key);
  assert.equal(model.familyOf(entries[5]).key, familyIdentity('').key);
  assert.equal(JSON.stringify(entries), before);
});

test('native family aliases retain their own typed keys while ordinary family filters remain unchanged', () => {
  const entries = freeze([
    rawEntry('alias-number', 'record', '{"family":"RNF","id":"n","native_family":1}'),
    entry('alias-text', 'record', {family: 'RNF', id: 's', native_family: '1'}),
    entry('alias-null', 'record', {family: 'RNF', id: 'null', native_family: null}),
    entry('alias-null-text', 'record', {family: 'RNF', id: 'text-null', native_family: 'NULL — família declarada'}),
    entry('alias-absent', 'record', {family: 'RNF', id: 'absent'}),
  ]);
  const before = JSON.stringify(entries), model = makePresentation(entries);
  assert.equal(new Set(model.records.map(r => r.familyKey)).size, 1);
  assert.equal(new Set(model.records.map(r => r.nativeFamilyKey)).size, entries.length);
  assert.equal(new Set(model.records.map(r => r.native_family)).size, entries.length);
  assert.equal(model.records[0].nativeFamilyKey, familyIdentity(literalValue('1')).key);
  assert.equal(model.records[1].nativeFamilyKey, familyIdentity('1').key);
  assert.equal(model.records[2].nativeFamilyKey, familyIdentity(null).key);
  assert.equal(model.records[4].nativeFamilyKey, model.records[4].familyKey);
  assert.ok(model.records.every(r => r.family === 'RNF' && recordMatches(r, {family: familyIdentity('RNF').key})));
  assert.equal(literalText(model.read(entries[0]).native_family), '1');
  assert.equal(model.read(entries[2]).native_family, null);
  assert.equal(JSON.stringify(entries), before);
});

test('same-type composite family labels cannot merge different numeric or string values', () => {
  const entries = freeze([
    rawEntry('array-number', 'record', '{"family":[1,2],"id":"a"}'),
    entry('array-text', 'record', {family: ['1', '2'], id: 'b'}),
    rawEntry('object-number', 'record', '{"family":{"a":1},"id":"c"}'),
    entry('object-text', 'record', {family: {a: '1'}, id: 'd'}),
  ]);
  const model = makePresentation(entries);
  assert.equal(new Set(model.records.map(r => r.familyKey)).size, entries.length);
  assert.equal(new Set(model.records.map(r => r.family)).size, entries.length);
  for (const r of model.records) assert.deepEqual(model.records.filter(candidate => recordMatches(candidate, {family: r.familyKey})).map(candidate => candidate.id), [r.id]);
});

test('editorial string membership cannot capture numeric, null or missing homonymous families', () => {
  const records = freeze([
    rawEntry('theme-number', 'record', '{"family":1,"id":"n"}'),
    entry('theme-text', 'record', {family: '1', id: 's'}),
    entry('theme-null', 'record', {family: null, id: 'null'}),
    entry('theme-null-text', 'record', {family: 'NULL — família declarada', id: 'text-null'}),
    entry('theme-missing', 'record', {id: 'missing'}),
    entry('theme-missing-text', 'record', {family: 'Família não declarada', id: 'text-missing'}),
  ]);
  const editorial = entry('typed-editorial', 'collection', {schema: 'r4-atlas-editorial-map/1', themes: [{id: 'text-members', title: 'String members', families: ['1', 'NULL — família declarada', 'Família não declarada']}]}, {group: 'editorial_map'});
  const model = makePresentation([...records, editorial]);
  withDOM(host => {
    const tree = mountEditorialTree(host, model, model.records, () => {}, {expanded: new Set(model.records.map(r => r.nativeFamilyKey))});
    const theme = tags(host, 'g').find(g => g.getAttribute('data-graph-id') === 'theme:text-members');
    assert.ok(theme, 'the declared string-only theme remains visible');
    assert.equal(theme.getAttribute('aria-label'), 'String members: 3 registros');
    for (const r of model.records) assert.ok(tags(host, 'g').some(g => g.getAttribute('data-graph-id') === 'family:' + r.nativeFamilyKey), 'every typed family keeps its own graph identity');
    tree.destroy();
  });
});

test('family relation aggregation uses reversible pairs even with literal NUL',()=>{
 const a=entry('nul-a','record',{id:'A',title:'NUL family record',family:'F\u0000X'}),b=entry('nul-b','record',{id:'B',title:'Other family record',family:'G'}),e=entry('nul-edge','relation',{from:'A',to:'B',type:'PREDECESSOR'});
 const model=makePresentation([a,b,e]);withDOM(host=>{const tree=mountEditorialTree(host,model,model.records,()=>{},{relations:true});assert.equal(tags(host,'path').filter(p=>p.classList.contains('tree-family-evidence')).length,1);assert.equal(tags(host,'g').filter(n=>n.classList.contains('svg-family')).length,2);tree.destroy();});
});

test('small SVG status and ordinal text reaches WCAG 4.5 while accents stay distinct',()=>{
 const rgb=hex=>hex.replace('#','').match(/../g).map(pair=>parseInt(pair,16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4),lum=hex=>{const c=rgb(hex);return .2126*c[0]+.7152*c[1]+.0722*c[2];},contrast=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);};
 for(const group of ['succeeded','technical','failed','mixed','blocked','unknown']){
  const r=entry('ink-'+group,'record',{id:group,title:'Record '+group,family:'F',result:'Status '+group,result_group:group}),model=makePresentation([r]);
  withDOM(host=>{const tree=mountEditorialTree(host,model,model.records,()=>{},{expanded:new Set([model.records[0].nativeFamilyKey])});for(const bg of ['#FFFFFF','#EFFAF8']){const label=tags(host,'text').find(n=>n.textContent===group);assert.ok(label);assert.ok(contrast(label.getAttribute('fill'),bg)>=4.5,group+' status contrast');}const ordinal=tags(host,'text').find(n=>n.textContent==='01');assert.ok(ordinal);for(const bg of ['#5A91E6','#14A8A3','#9B81DE','#5F8BA2','#788D9B'])assert.ok(contrast(ordinal.getAttribute('fill'),bg)>=4.5,'ordinal contrast');tree.destroy();});
 }
});

test('dataset notice keeps explicit states and meaningful warnings without orphan NULL paragraphs',()=>{
 const table=entry('notice-table','table',{id:'T',status:null,source_warning:'Declared warning',reason:'Duplicate explanation',binding_gap:null,rows:[]}),model=makePresentation([table]),before=table.raw_json;
 withDOM(host=>{renderDatasetNotice(host,table,model);assert.deepEqual(tags(host,'p').map(n=>n.textContent),['Declared warning']);assert.ok(host.textContent.includes('Estado'));assert.ok(host.textContent.includes(NULL));assert.equal(table.raw_json,before);});
 const gap=entry('notice-gap','table',{id:'G',binding_gap:'Explicit unresolved binding',rows:[]}),other=makePresentation([gap]);withDOM(host=>{renderDatasetNotice(host,gap,other);assert.ok(host.textContent.includes('Vínculo com o Caderno: Explicit unresolved binding'));});
});

test('product catalog restores declared execution and stage before opaque identities',()=>{
 const e=entry('context-product','asset',{id:'opaque-id',native_id:'RF-001',run_id:null,execution_id:'execution-declared',stage_id:'infer_nuclei',atlas_record_id:'opaque-record',group_id:'opaque-group',status:'LOADED',publication:null,human_review:'NOT_ASSESSED'},{group:'product_items'}),model=makePresentation([e]),before=e.raw_json;
 withDOM(host=>{renderCatalog(host,[e],model,()=>{});const cells=tags(host,'tbody')[0].children[0].children;assert.ok(cells[1].textContent.includes('Execução'));assert.ok(cells[1].textContent.includes('execution-declared'));assert.ok(cells[1].textContent.includes('Estágio'));assert.ok(cells[1].textContent.includes('infer_nuclei'));assert.ok(tags(cells[1],'details').length);assert.ok(cells[1].textContent.includes('opaque-record'));assert.ok(cells[2].textContent.includes('LOADED'));assert.ok(cells[2].textContent.includes(NULL));assert.equal(e.raw_json,before);});
});


    
// CXR-01: exercise the actual SVG card and <title> tooltip, not a mock
// formatter. The same DTO occurrence must agree with the table and detail.
for (const [name, states, selected] of [
  ['execution_state overrides legacy result', {execution_state:'FAILED', result:'SUCCEEDED'}, 'FAILED'],
  ['execution_state alone', {execution_state:'FAILED'}, 'FAILED'],
  ['status overrides result_state and result', {status:'BLOCKED', result_state:'SUCCEEDED', result:'SUCCEEDED'}, 'BLOCKED'],
  ['result_state overrides legacy result', {result_state:'FAILED', result:'SUCCEEDED'}, 'FAILED'],
  ['result_group overrides legacy result', {result_group:'failed', result:'SUCCEEDED'}, 'failed'],
  ['explicit NULL takes precedence', {execution_state:null, result:'SUCCEEDED'}, 'NULL — valor declarado'],
  ['explicit empty text takes precedence', {execution_state:'', result:'SUCCEEDED'}, '"" — texto vazio declarado'],
  ['explicit false takes precedence', {execution_state:false, result:'SUCCEEDED'}, 'false'],
  ['explicit zero takes precedence', {execution_state:0, result:'SUCCEEDED'}, '0'],
  ['all state fields absent', {}, null],
  ['legacy result is the final fallback', {result:'SUCCEEDED'}, 'SUCCEEDED'],
  ['HTML-shaped state remains inert text', {execution_state:'<img src=x onerror=alert(1)>', result:'SUCCEEDED'}, '<img src=x onerror=alert(1)>'],
]) {
  test('CXR-01 tree, table and detail agree: '+name, () => {
    const original = entry('cxr01-record','record',{id:'ORIGINAL-1',title:'CXR01 synthetic',family:'F', ...states});
    const raw = original.raw_json, model = makePresentation([original]), r = model.records[0];
    withDOM(host => {
      let selectedEntry;
      const treeHost = new MemoryNode('section');
      const tableHost = new MemoryNode('section');
      const detailHost = new MemoryNode('section');
      host.append(treeHost, tableHost, detailHost);
      const tree = mountEditorialTree(treeHost,model,model.records,e=>{selectedEntry=e;},{expanded:new Set([r.nativeFamilyKey])});
      const card = tags(treeHost,'g').find(n=>n.getAttribute('data-graph-id')===original.uid);
      assert.ok(card, 'record card must be visible');
      const statusText = tags(card,'text').find(n=>n.getAttribute('y')==='74');
      const tooltip = tags(card,'title')[0];
      assert.ok(statusText, 'SVG status text must exist');
      assert.ok(tooltip, 'SVG tooltip must exist');
      assert.equal(statusText.textContent, selected===null?'':selected.replaceAll('_',' ').slice(0,27), 'SVG card');
      assert.equal(tooltip.textContent, ['CXR01 synthetic',selected,'cxr01-record'].filter(v=>v!==null).join('\n'), 'SVG title');
      renderRecordPresentation(tableHost,model.records,()=>{});
      assert.equal(tags(tableHost,'tbody')[0].children[0].children[2].textContent, selected??'Não declarado', 'record table');
      renderPresentationDetail(detailHost,original,model,buildNativeNavigation([original]),()=>{});
      const badges=tags(detailHost,'span').filter(n=>n.classList.contains('badge'));
      assert.equal(badges[0]?.textContent??null,selected, 'record detail primary state');
      assert.equal(tree.locate(original.uid),true,'navigation');
      assert.equal(selectedEntry,original,'selected occurrence identity');
      assert.equal(card.getAttribute('data-native-node'),original.uid,'SVG native identity');
      assert.equal(tags(host,'script').length,0,'no executable script');
      assert.equal(tags(host,'img').length,0,'no HTML execution');
      if (name==='execution_state overrides legacy result') {
        assert.equal(statusText.getAttribute('fill'),'#9e3447','selected FAILED must not retain a green group ink');
      }
      tree.destroy();
    });
    assert.equal(original.raw_json,raw,'DTO not mutated');
    assert.equal(model.records[0].entry,original,'reference not rewritten');
  });
}
