/** Pure-state behavioral tests. These do not substitute for a browser run. */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const args = Object.fromEntries(process.argv.slice(2).reduce((pairs, value, index, array) => {
  if (index % 2 === 0) pairs.push([value.replace(/^--/, ''), array[index + 1]]);
  return pairs;
}, []));
if (!args.asset || !args.catalog) throw new Error('Usage: node atlas_parity02_p02_state_tests.mjs --asset PATH --catalog PATH [--report PATH]');
const catalog = JSON.parse(readFileSync(args.catalog, 'utf8'));
const sandbox = {URLSearchParams, URL, console};
runInNewContext(readFileSync(args.asset, 'utf8'), sandbox, {filename: 'parity02_p02_state.js'});
const api = sandbox.AtlasParity02State;
assert.ok(api, 'The packaged asset must expose AtlasParity02State');
const checks = [];
function check(name, action) {
  try {action(); checks.push({name, status: 'PASS'});}
  catch (error) {checks.push({name, status: 'FAIL', message: error.message});}
}
const flat = api.flatten(catalog);
const filter = overrides => ({...api.defaults().filters, ...overrides});
const ids = values => [...values].map(run => run._key);
const by = (source, number) => flat.find(r => r._sourceId === source && r.id.endsWith('run:' + number));
const first = by('source-1', '00'), second = by('source-2', '00');
assert.ok(first && second, 'Use the public P02 fixture (two sources, 28 runs)');
const encode = route => api.stringify(route, catalog);
const decode = hash => api.parse(hash, catalog);
const defaultHash = encode(api.defaults());
const paramsFor = hash => new URLSearchParams(hash.replace(/^#/, ''));
const modify = (hash, field, value) => {const p = paramsFor(hash); p.set(field, value); return '#' + p.toString();};

check('fixture_source_scoped_28_runs', () => {
  assert.equal(flat.length, 28);
  assert.equal(new Set(ids(flat)).size, 28);
  assert.notEqual(first._key, second._key);
});
check('default_hash_is_snapshot_bound', () => {
  assert.equal(paramsFor(defaultHash).get('scope'), catalog.snapshot_id);
  assert.equal(decode(defaultHash).rejected, false);
});
check('roundtrip_detail_selection_and_view', () => {
  const r = {...api.defaults(), view: 'compare', detail: first._key, selected: [first._key, second._key]};
  const parsed = decode(encode(r));
  assert.equal(parsed.rejected, false);
  assert.equal(parsed.route.view, 'compare');
  assert.equal(parsed.route.detail, first._key);
  assert.equal(JSON.stringify(parsed.route.selected), JSON.stringify(r.selected));
});
check('roundtrip_filters_unicode_and_source', () => {
  const r = {...api.defaults(), filters: filter({query: 'Ação 日本語 🧪', source: 'source-1', status: 'COMPLETED', review: 'UNKNOWN', metrics: 'yes', references: 'yes', sort: 'time-desc'})};
  const parsed = decode(encode(r));
  assert.equal(parsed.rejected, false);
  for (const [key, value] of Object.entries(r.filters)) assert.equal(parsed.route.filters[key], value, key);
});
check('roundtrip_project_and_experiment_source_keys', () => {
  const r = {...api.defaults(), filters: filter({project: api.key(first._sourceId, first.project_id), experiment: api.key(first._sourceId, first.experiment_id)})};
  const parsed = decode(encode(r));
  assert.equal(parsed.rejected, false);
  assert.equal(parsed.route.filters.project, r.filters.project);
  assert.equal(parsed.route.filters.experiment, r.filters.experiment);
});
check('selection_survives_filters_that_hide_every_selected_run', () => {
  const r = {...api.defaults(), selected: [first._key, second._key], filters: filter({query: 'no-synthetic-match-exists'})};
  const parsed = decode(encode(r));
  assert.equal(parsed.route.selected.length, 2);
  assert.equal(api.filterRuns(flat, parsed.route.filters).length, 0);
});
check('all_sort_modes_deterministic_on_reordered_input', () => {
  for (const sort of ['title', 'id', 'source', 'status', 'review', 'time-asc', 'time-desc']) {
    assert.equal(JSON.stringify(ids(api.filterRuns(flat, filter({sort})))),
                 JSON.stringify(ids(api.filterRuns([...flat].reverse(), filter({sort})))), sort);
  }
});
check('source_filter_preserves_colliding_ids', () => {
  assert.equal(api.filterRuns(flat, filter({source: 'source-2'})).length, 14);
  assert.ok(api.filterRuns(flat, filter({source: 'source-2'})).every(r => r._sourceId === 'source-2'));
});
check('search_finds_source_name_id_and_unicode_title', () => {
  assert.equal(api.filterRuns(flat, filter({query: 'fonte B'})).length, 14);
  assert.equal(api.filterRuns(flat, filter({query: 'run:08'})).length, 2);
  assert.equal(api.filterRuns(flat, filter({query: '日本語'})).length, 2);
});
check('review_and_execution_filters_are_independent', () => {
  const results = api.filterRuns(flat, filter({status: 'COMPLETED', review: 'HOLD'}));
  assert.ok(results.length > 0);
  assert.ok(results.every(r => r.status === 'COMPLETED' && r.review_status === 'HOLD'));
});
check('metric_presence_does_not_conflate_missing_value_with_missing_metric', () => {
  const positive = api.filterRuns(flat, filter({metrics: 'yes'}));
  const negative = api.filterRuns(flat, filter({metrics: 'no'}));
  assert.equal(positive.length + negative.length, 28);
  assert.ok(positive.some(r => r.id.endsWith('run:04')));
  assert.ok(negative.some(r => r.id.endsWith('run:08')));
});
check('reference_presence_is_independent_of_lineage', () => {
  const positive = api.filterRuns(flat, filter({references: 'yes'}));
  const negative = api.filterRuns(flat, filter({references: 'no'}));
  assert.equal(positive.length + negative.length, 28);
  assert.ok(positive.every(r => r.related_references.length));
  assert.ok(negative.every(r => !r.related_references.length));
});
check('unknown_dates_remain_reachable_in_time_sort', () => {
  const results = api.filterRuns(flat, filter({sort: 'time-asc'}));
  assert.equal(results.length, 28);
  assert.ok(results.some(r => r.id.endsWith('run:08') && r.started_at === null));
});
check('stale_snapshot_rejects_detail_selection_and_source_filter', () => {
  const r = {...api.defaults(), detail: first._key, selected: [first._key], filters: filter({source: first._sourceId})};
  const result = decode(modify(encode(r), 'scope', '0'.repeat(64)));
  assert.ok(result.rejected);
  assert.equal(result.route.detail, null);
  assert.equal(result.route.selected.length, 0);
  assert.equal(result.route.filters.source, '');
  assert.ok(result.warnings.length);
});
check('scope_missing_never_resolves_source_number_entity', () => {
  const p = paramsFor(encode({...api.defaults(), detail: first._key, selected: [first._key]}));
  p.delete('scope');
  const result = decode('#' + p.toString());
  assert.ok(result.rejected);
  assert.equal(result.route.detail, null);
  assert.equal(result.route.selected.length, 0);
});
check('legacy_links_without_version_or_scope_cannot_retarget_source_number', () => {
  const legacy = new URLSearchParams({view: 'explore', run: first._key, source: 'source-1'});
  const result = decode('#' + legacy.toString());
  assert.ok(result.rejected);
  assert.equal(result.reason, 'UNBOUND_ROUTE');
  assert.equal(result.route.detail, null);
  assert.equal(result.route.filters.source, '');
});
check('unknown_run_never_opens_another_entity', () => {
  const result = decode(modify(defaultHash, 'run', api.key('source-1', 'urn:synthetic:nonexistent')));
  assert.equal(result.route.detail, null);
  assert.ok(result.warnings.length || result.rejected);
});
check('invalid_duplicate_and_unknown_parameters_are_rejected', () => {
  for (const hash of [defaultHash + '&view=timeline', defaultHash + '&unsafe=1', defaultHash + '&q=%ZZ']) {
    assert.ok(decode(hash).rejected, hash);
  }
});
check('invalid_enum_values_do_not_select_an_unintended_view_or_filter', () => {
  for (const [field, value] of [['view', 'unapproved-view'], ['metrics', 'maybe'], ['sort', 'rank'], ['review', 'CERTIFIED'], ['status', 'SUCCESS']]) {
    const result = decode(modify(defaultHash, field, value));
    assert.ok(result.rejected || result.warnings.length, field);
    assert.notEqual(result.route.view, 'unapproved-view');
  }
});
check('unknown_source_and_collection_never_fall_through_to_another_entity', () => {
  for (const [field, value] of [['source', 'source-999'], ['project', api.key('source-2', 'urn:missing-project')], ['experiment', 'not-json']]) {
    const result = decode(modify(defaultHash, field, value));
    assert.ok(result.rejected || result.warnings.length, field);
    assert.equal(result.route.filters[field], '');
  }
});
check('adversarial_query_stays_plain_query_text', () => {
  const query = '<img src=https://example.invalid onerror=alert(1)> & # 日本語';
  const result = decode(encode({...api.defaults(), filters: filter({query})}));
  assert.equal(result.route.filters.query, query);
});
check('route_navigation_does_not_modify_source_projection', () => {
  const original = JSON.stringify(catalog);
  api.filterRuns(flat, filter({sort: 'time-desc', query: 'run'}));
  decode(encode({...api.defaults(), detail: second._key}));
  assert.equal(JSON.stringify(catalog), original);
});

const report = {kind: 'ATLAS_PARITY02_P02_STATE_TESTS', status: checks.every(x => x.status === 'PASS') ? 'PASS' : 'FAIL',
  browser_executed: false, checks, total: checks.length};
if (args.report) writeFileSync(args.report, JSON.stringify(report, null, 2) + '\n');
process.stdout.write(JSON.stringify(report, null, 2) + '\n');
if (report.status !== 'PASS') process.exitCode = 1;
