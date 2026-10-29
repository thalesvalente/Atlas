import assert from 'node:assert/strict';
import {pathToFileURL} from 'node:url';

const asset = process.argv[process.argv.indexOf('--module') + 1];
const {buildPropertyTables, p03ContextKey, propertyChoiceKey, renderP03Metadata, renderPropertySelection} = await import(pathToFileURL(asset));
const passed = [];
const check = (name, body) => {body(); passed.push(name);};
const property = (id, type, value, unit = null, precision = null) => ({
  id, property_id: id + ':kind', name: id, type, value, unit, precision,
  display_value: value == null ? null : typeof value === 'string' ? value : JSON.stringify(value),
  display_precision: precision == null ? null : String(precision), missing_reason: null,
});
const run = {id: 'urn:run:shared', synthetic: true, inputs: ['report.pdf'], outputs: [], related_references: [], metrics: [
  {...property('large', 'integer', 9007199254740992, '1', 0), display_value: '9007199254740993'},
  property('false', 'boolean', false), property('zero', 'integer', 0, '1', 0),
  {...property('missing', 'number', null, 'mg/L'), missing_reason: 'Não medido'},
  property('empty', 'string', ''),
  {...property('decimal', 'number', '0.1234500', 'mg/L', 9007199254740992), display_precision: '9007199254740993'},
  property('other-unit', 'number', '0.1234500', 'g/L', 7),
], parameters: [property('parameter', 'boolean', true)]};
const source = {id: 'source-1', snapshot_id: 'a'.repeat(64), read_model: {runs: [run]}};
const choose = (...ids) => new Set(ids.map(id => propertyChoiceKey('metrics', id)));
const rows = descriptors => descriptors.flatMap(descriptor => descriptor.rows);

check('explicit_empty_selection_creates_no_inferred_table', () => assert.deepEqual(buildPropertyTables(source, run, new Set()), []));
check('exact_numeric_text_boolean_zero_empty_and_missing_stay_distinct', () => {
  const selected = choose('large', 'false', 'zero', 'missing', 'empty', 'decimal');
  const before = structuredClone(source);
  const result = rows(buildPropertyTables(source, run, selected));
  const byId = Object.fromEntries(result.map(row => [row.id, row]));
  assert.equal(byId.large.cells.value, '9007199254740993');
  assert.equal(byId.false.cells.value, false);
  assert.equal(byId.zero.cells.value, '0');
  assert.equal(byId.empty.cells.value, '');
  assert.equal(byId.missing.cells.value, null);
  assert.equal(byId.missing.missing_reasons.value, 'Não medido');
  assert.equal(byId.decimal.cells.value, '0.1234500');
  assert.equal(byId.decimal.cells.precision, '9007199254740993');
  assert.deepEqual(source, before);
});
check('incompatible_units_and_declared_types_are_separate_tables', () => {
  const tables = buildPropertyTables(source, run, choose('large', 'decimal', 'other-unit'));
  assert.equal(tables.length, 3);
  assert.deepEqual(tables.map(table => table.columns.find(column => column.id === 'value').unit), ['1', 'mg/L', 'g/L']);
  assert.equal(tables[1].columns.find(column => column.id === 'value').type, 'decimal');
  assert.ok(tables.every(table => !Object.hasOwn(table.columns.find(column => column.id === 'value'), 'precision')));
});
check('parameters_require_their_own_explicit_selection', () => {
  const result = rows(buildPropertyTables(source, run, new Set([propertyChoiceKey('parameters', 'parameter')])));
  assert.equal(result.length, 1);
  assert.equal(result[0].cells.value, true);
});
check('unknown_property_and_invalid_boolean_are_visible_presentation_failures', () => {
  assert.throws(() => buildPropertyTables(source, run, choose('absent')), error => error.code === 'UNKNOWN_PROPERTY');
  const changed = structuredClone(source);
  changed.read_model.runs[0].metrics.find(item => item.id === 'false').value = 'false';
  assert.throws(() => buildPropertyTables(changed, run, choose('false')), error => error.code === 'INVALID_TYPE');
});
check('context_qualifies_duplicate_ids_by_source_snapshot_and_catalog', () => {
  const catalog = {snapshot_id: 'session-a'};
  const keys = [p03ContextKey(catalog, source, run), p03ContextKey(catalog, {...source, id: 'source-2'}, run),
    p03ContextKey(catalog, {...source, snapshot_id: 'b'.repeat(64)}, run), p03ContextKey({snapshot_id: 'session-b'}, source, run)];
  assert.equal(new Set(keys).size, 4);
  assert.deepEqual(JSON.parse(keys[0]), [catalog.snapshot_id, source.id, source.snapshot_id, run.id]);
});

class Node {
  constructor(tag) {this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {}; this.handlers = {}; this._text = '';}
  set textContent(value) {this._text = String(value); this.children = [];}
  get textContent() {return this._text + this.children.map(child => child.textContent).join('');}
  append(...nodes) {this.children.push(...nodes);}
  replaceChildren(...nodes) {this._text = ''; this.children = nodes;}
  setAttribute(name, value) {this.attributes[name] = String(value);}
  addEventListener(name, handler) {this.handlers[name] = handler;}
}
const document = {createElement: tag => new Node(tag)};
const collect = (node, predicate) => [ ...(predicate(node) ? [node] : []), ...node.children.flatMap(child => collect(child, predicate)) ];

check('selection_updates_only_output_and_removal_does_not_register_global_handlers', () => {
  const selection = new Set();
  const section = renderPropertySelection(document, source, run, selection);
  const controls = collect(section, node => node.tagName === 'input');
  const control = controls.find(node => node.dataset.propertyId === 'false');
  const fieldset = collect(section, node => node.tagName === 'fieldset')[0];
  control.checked = true; control.handlers.change();
  assert.equal(selection.has(propertyChoiceKey('metrics', 'false')), true);
  assert.equal(collect(section, node => node.attributes['data-component'] === 'parity02-p03-table').length, 1);
  assert.equal(collect(section, node => node.tagName === 'fieldset')[0], fieldset);
  assert.equal(collect(section, node => node.dataset.propertyId === 'false')[0], control);
  const rebuilt = renderPropertySelection(document, source, run, selection);
  assert.equal(collect(rebuilt, node => node.dataset.propertyId === 'false')[0].checked, true);
  control.checked = false; control.handlers.change();
  assert.equal(collect(section, node => node.attributes['data-component'] === 'parity02-p03-table').length, 0);
});

const metadata = {
  version: 'p03-metadata/1', semantic_status: 'DERIVED_CURRENT_CONTRACT',
  source: {key: JSON.stringify([source.id, source.snapshot_id]), name: 'Fonte <script>hostil</script>', metadata_sha256: null},
  items: [{identity: {source_key: JSON.stringify([source.id, source.snapshot_id]), id: 'report.pdf'}, kind: 'artifact', name: 'report.pdf',
    types: ['File'], description: '<img src=x>', media_type: 'application/pdf', availability: {declared: 'EXTERNAL', observed: 'EXTERNAL_UNRESOLVED'},
    digests: {declared_sha256: null, calculated_sha256: null}, relations: [], mentions: []}],
};
check('metadata_keeps_file_neutral_and_hostile_strings_in_text_nodes', () => {
  const section = renderP03Metadata(document, {...source, presentation: {metadata, errors: []}}, run);
  assert.ok(section.textContent.includes('Artefato declarado (File)'));
  assert.ok(section.textContent.includes('<script>hostil</script>'));
  assert.ok(section.textContent.includes('<img src=x>'));
  assert.equal(collect(section, node => ['script', 'img', 'a'].includes(node.tagName)).length, 0);
  assert.equal(collect(section, node => node.dataset.semanticKind).length, 0);
});
check('metadata_failure_is_visible_and_independent_of_source_status', () => {
  const result = renderP03Metadata(document, {...source, status: 'READY', presentation: {metadata: null, errors: [{code: 'LIMIT', path: 'items'}]}});
  assert.equal(collect(result, node => node.dataset.testid === 'p03-presentation-error').length, 1);
  assert.ok(result.textContent.includes('LIMIT (items)'));
  const mismatch = structuredClone(metadata); mismatch.source.key = 'another-source';
  const mismatched = renderP03Metadata(document, {...source, presentation: {metadata: mismatch, errors: []}});
  assert.ok(mismatched.textContent.includes('SOURCE_MISMATCH'));
});

process.stdout.write(JSON.stringify({status: 'PASS', cases: passed.length, passed, browser_executed: false}));
