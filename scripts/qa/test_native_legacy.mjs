/** Presentation adapter regressions with synthetic data only.
 * Run: node scripts/qa/test_native_legacy.mjs
 * The in-memory DOM checks text, identity and callbacks; it is not visual evidence.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {buildNativeNavigation, nativeFragments} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {literalValue, literalText, makePresentation, recordMatches, presentationColumns, catalogTitle, catalogStatus} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_model.js';
import {ASSET_COLLECTIONS, renderCatalog, renderPresentationDetail, renderReadingTable, renderRecordIndex, renderRecordPresentation, renderRelationPresentation} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_views.js';
import {mountEditorialTree} from '../../packages/atlas/src/atlas_viewer/static/native_legacy_tree.js';

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
  assert.equal(recordMatches(r, {family: 'Família Árvore', kind: 'run', status: NULL}), true);
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
      const persistent = {expanded: new Set(['F1', 'F2']), relations: true};
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
    const tree = mountEditorialTree(host, model, model.records, () => {}, {expanded: new Set(['F']), relations: true});
    assert.equal(tags(host, 'path').filter(path => path.classList.contains('tree-provenance')).length, 0);
    tree.destroy();
  });
  withDOM(host => {
    renderRelationPresentation(host, model.edges, model, () => {});
    assert.ok(host.textContent.includes('AMBIGUOUS (2)'));
    assert.ok(host.textContent.includes(node.uid), 'the technical candidate must remain discoverable');
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
  withDOM(host=>{renderRecordIndex(host,model.records,1,null,()=>{});renderRecordPresentation(host,model.records,()=>{});const tree=mountEditorialTree(host,model,model.records,()=>{},{expanded:new Set(['F'])});tree.destroy();assert.ok(host.textContent.includes('Structured record'));});
});

test('prototype-shaped declared labels do not resolve to inherited dictionary members',()=>{
 const r=entry('prototype-record','record',{id:'p',title:'Declared prototype label',kind:'constructor',result_group:'__proto__',family:'F'}),model=makePresentation([r]);
 withDOM(host=>{renderRecordPresentation(host,model.records,()=>{});assert.ok(host.textContent.includes('constructor'));assert.ok(!host.textContent.includes('[native code]'));assert.ok(!host.textContent.includes('[object Object]'));});
});
