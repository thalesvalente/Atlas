/** Feature 005 tasks and adversarial QA. Installed product, real browser, invented data. */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {openNativePane, revealNativeControl} from './browser_native_triage_navigation.mjs';
import {runN03Checks} from './browser_native_triage_n03.mjs';
import {runReadabilityChecks} from './browser_native_triage_readability.mjs';

const require = createRequire(import.meta.url);
const {chromium} = require(process.env.ATLAS_PLAYWRIGHT_MODULE || 'playwright');
const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) args.set(process.argv[index], process.argv[index + 1]);
const url = args.get('--url'), reportPath = args.get('--report'), origin = new URL(url).origin;
assert.ok(['127.0.0.1', 'localhost'].includes(new URL(url).hostname), 'QA uses a loopback server only');
const expected = JSON.parse(await fs.readFile(args.get('--expected'), 'utf8'));
assert.equal(expected.fixture_scope, 'INVENTED_DATA_ONLY');
const report = {status: 'FAIL', scope: 'FEATURE005_SYNTHETIC_BROWSER_TASKS', phase: 'BROWSER_BOOTSTRAP',
  checks: [], errors: [], external_requests: [], requests: [], layout: [], screenshots: [], timings_ms: {},
  contrast: [], focused_results: [], breakpoint_controls: [], visual_readability: []};
const contrastRatio = (foreground, background) => {
  const luminance = color => {
    const match = /^rgba?\(([^)]+)\)$/.exec(color);
    assert.ok(match, 'Contrast probe requires a computed sRGB color: ' + color);
    const channels = match[1].split(',').map(Number);
    assert.ok(channels.length === 3 || (channels.length === 4 && channels[3] === 1),
      'Contrast probe must not treat a translucent color as opaque: ' + color);
    return channels.slice(0, 3).map(value => value / 255)
      .map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4)
      .reduce((sum, value, index) => sum + value * [.2126, .7152, .0722][index], 0);
  };
  const values = [luminance(foreground), luminance(background)].sort((a, b) => a - b);
  return (values[1] + .05) / (values[0] + .05);
};
// Read the actual cascade and the nearest painted surface; never infer a pass
// from the intended CSS token. The current gradients have opaque sRGB stops.
const readContrastSamples = samples => samples.map(sample => {
  const node = document.querySelector(sample.selector);
  if (!node) throw Error('Missing contrast target: ' + sample.selector);
  let surface = sample.background ? document.querySelector(sample.background) : node;
  while (surface) {
    const style = getComputedStyle(surface);
    const stops = style.backgroundImage.match(/rgba?\([^)]+\)/g);
    const solid = style.backgroundColor;
    if (stops?.length || (solid && solid !== 'rgba(0, 0, 0, 0)')) {
      return {...sample, foreground: getComputedStyle(node)[sample.property || 'color'],
        backgrounds: stops || [solid], background_image: style.backgroundImage,
        surface: surface.id || surface.className};
    }
    surface = surface.parentElement;
  }
  throw Error('No painted background for contrast target: ' + sample.selector);
});
const uid = key => expected.uids[key];
const attr = value => JSON.stringify(value);
const result = (page, key) => page.locator('[data-result-uid=' + attr(uid(key)) + ']');
const batchBox = (page, key) => page.locator('#native-content [data-batch-uid=' + attr(uid(key)) + ']').first();
const selectedCount = async page => Number(await page.locator('#native-batch-summary').getAttribute('data-selected-count'));
const navigationCount = async (page, pane) => Number(await page.locator('[data-pane="' + pane + '"] .application-nav-count').textContent());
const clickAction = async (page, id) => {
  const control = await revealNativeControl(page, page.locator('#' + id));
  await control.click();
};
const filteredClear = async page => {
  const clear = page.locator('#native-clear');
  if (await clear.isEnabled()) await clear.click();
};
const showFilters = async page => {
  const disclosure = page.locator('.mobile-filters');
  if (await disclosure.count() && await disclosure.getAttribute('open') === null) {
    await disclosure.locator('summary').first().click();
  }
};
const choose = async (page, control, label) => {
  await showFilters(page);
  await page.locator('#' + control).selectOption({label});
};
const search = async (page, query) => {
  await openNativePane(page, 'search');
  await page.locator('#native-search').fill(query);
};
const check = async (name, fn) => {
  const start = performance.now();
  await fn();
  report.timings_ms[name] = Math.round(performance.now() - start);
  report.checks.push(name);
};
const download = async (page, control, name) => {
  const pending = page.waitForEvent('download');
  await page.locator(control).click();
  const value = await pending;
  const text = await fs.readFile(await value.path(), 'utf8');
  await fs.writeFile(path.join(path.dirname(reportPath), name), text);
  return text;
};

let browser, failure;
try {
  browser = await chromium.launch({headless: true,
    ...(process.env.ATLAS_CHROMIUM_EXECUTABLE ? {executablePath: process.env.ATLAS_CHROMIUM_EXECUTABLE} : {})});
  report.browser_version = browser.version();
  const context = await browser.newContext({viewport: {width: 1440, height: 1200}, acceptDownloads: true});
  const protectNetwork = async context => {
    await context.route('**/*', async route => {
      const request = route.request(), target = request.url();
      if (/^https?:/.test(target)) {
        report.requests.push({method: request.method(), path: new URL(target).pathname});
        if (new URL(target).origin !== origin) {
          report.external_requests.push(target);
          await route.abort();
          return;
        }
      }
      await route.continue();
    });
  };
  await protectNetwork(context);
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(error.message));
  page.setDefaultTimeout(10000);
  await page.goto(url, {waitUntil: 'networkidle'});
  await page.waitForFunction(revision => document.getElementById('native-revision')?.textContent.includes(revision), expected.revision_a);
  report.phase = 'FEATURE_TASKS';

  await check('G2_navigation_destinations_semantics_and_real_new_controls', async () => {
    // On the accepted baseline these assertions genuinely fail: the new
    // navigation and execution filter do not exist. A launch failure is BLOCKED.
    assert.equal(await page.locator('#native-menu-toggle').count(), 1, 'Responsive navigation control is required');
    assert.equal(await page.locator('#native-sidebar').count(), 1);
    assert.equal(await page.locator('#native-execution').count(), 1, 'Execution must have its own coherent filter');
    for (const pane of ['overview', 'search', 'experiments', 'baselines', 'tree', 'records', 'tables', 'assets', 'relations', 'timeline', 'coverage', 'selected', 'retention']) {
      assert.equal(await page.locator('[data-pane="' + pane + '"]').count(), 1, pane + ' is a unique navigation destination');
    }
    // Search includes every DTO; uids only indexes records, tables and assets.
    // Nine explicit run/experiment/attempt records accompany the bulk runs.
    for (const [pane, count] of Object.entries({search: expected.total_entries,
      experiments: expected.bulk_records + 9, baselines: 2, selected: 0, retention: 0})) {
      assert.equal(await navigationCount(page, pane), count, pane + ' reports the actual synthetic snapshot or batch population');
    }
    assert.equal(await page.getByRole('menu').count(), 0, 'Ordinary navigation is not an ARIA application menu');
    assert.equal(await page.locator('#native-menu-toggle').getAttribute('aria-controls'), 'native-sidebar');
  });

  await check('T01_M1_1_is_a_39_row_table_with_typed_search_reason_not_a_run', async () => {
    await search(page, 'M1.1');
    const table = result(page, 'M1.1');
    assert.equal(await table.count(), 1);
    assert.equal(await table.getAttribute('data-result-type'), 'table');
    const text = await table.innerText();
    assert.match(text, /Tabela/i);
    assert.match(text, /M1\.1 · RF baseline preservada/);
    assert.doesNotMatch(text, /SUCCEEDED/);
    assert.match(text, /título|identificador|\bID\b|label|campo|correspond/i, 'Every hit explains its matching field');
    assert.equal(await result(page, 'M1').count(), 0);
    assert.equal(await result(page, 'M11').count(), 0);
    await openNativePane(page, 'tables');
    assert.match(await page.locator('#native-content').innerText(), /39 linhas/);
    await search(page, 'M1');
    assert.equal(await result(page, 'M1').count(), 1);
    assert.equal(await result(page, 'M11').count(), 0);
    assert.equal(await result(page, 'M1.1').count(), 0);
    await search(page, 'M11');
    assert.equal(await result(page, 'M11').count(), 1);
    assert.equal(await result(page, 'M1').count(), 0);
    assert.equal(await result(page, 'M1.1').count(), 0);
  });

  await check('T02_execution_filter_matches_badges_and_preserves_documentary_dimensions', async () => {
    await filteredClear(page);
    await openNativePane(page, 'experiments');
    await choose(page, 'native-execution', 'SUCCEEDED');
    await choose(page, 'native-status', 'failed');
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 1);
    assert.equal(await batchBox(page, 'run-failed-published').count(), 0);
    assert.equal(await batchBox(page, 'run-blocked-published').count(), 0);
    await filteredClear(page);
    await choose(page, 'native-execution', 'FAILED');
    await choose(page, 'native-publication', 'published');
    assert.equal(await batchBox(page, 'run-failed-published').count(), 1);
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 0);
    await choose(page, 'native-admission', 'HOLD');
    await choose(page, 'native-review', 'PENDING');
    assert.equal(await batchBox(page, 'run-failed-published').count(), 1);
    await filteredClear(page);
    await choose(page, 'native-execution', 'BLOCKED');
    await choose(page, 'native-publication', 'published');
    assert.equal(await batchBox(page, 'run-blocked-published').count(), 1);
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 0);
  });

  await check('G4_NULL_empty_missing_UNKNOWN_remain_four_different_states', async () => {
    await filteredClear(page);
    await openNativePane(page, 'records');
    for (const [label, positive, negatives] of [
      ['NULL — valor declarado', 'state-null', ['state-empty', 'state-missing', 'state-unknown']],
      ['"" — texto vazio declarado', 'state-empty', ['state-null', 'state-missing', 'state-unknown']],
      ['UNKNOWN', 'state-unknown', ['state-null', 'state-empty', 'state-missing']],
    ]) {
      await choose(page, 'native-execution', label);
      assert.equal(await batchBox(page, positive).count(), 1, label);
      for (const negative of negatives) assert.equal(await batchBox(page, negative).count(), 0, label + ' excludes ' + negative);
    }
    await showFilters(page);
    const missingOption = page.locator('#native-execution option').filter({hasText: /AUSENTE|Não declarado|não declarad/i});
    assert.equal(await missingOption.count(), 1);
    await page.locator('#native-execution').selectOption(await missingOption.getAttribute('value'));
    assert.equal(await batchBox(page, 'state-missing').count(), 1);
    assert.equal(await batchBox(page, 'state-null').count(), 0);
    assert.equal(await batchBox(page, 'state-empty').count(), 0);
    await filteredClear(page);
    await search(page, 'state-missing');
    assert.match(await result(page, 'state-missing').innerText(), /Execução: AUSENTE/);
    assert.equal(await page.locator('#native-execution option').filter({hasText: /^published$/i}).count(), 0);
    await choose(page, 'native-status', 'published');
    assert.equal(await result(page, 'state-missing').count(), 1);
  });

  await check('G3_G4_declared_period_evidence_individual_chips_and_search_diagnostics', async () => {
    await filteredClear(page);
    await showFilters(page);
    await page.locator('#native-from').fill('2026-10-01');
    await page.locator('#native-to').fill('2026-10-01');
    await choose(page, 'native-execution', 'SUCCEEDED');
    assert.equal(await page.locator('#native-content [data-batch-uid]').count(), 1);
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 1);
    await page.getByRole('button', {name: /^Remover filtro Estado de execução:/}).click();
    assert.equal(await page.locator('#native-execution').inputValue(), '');
    assert.equal(await page.locator('#native-from').inputValue(), '2026-10-01');
    assert.equal(await page.locator('#native-to').inputValue(), '2026-10-01');
    assert.equal(await page.locator('#native-content [data-batch-uid]').count(), 1);
    await filteredClear(page);
    await choose(page, 'native-evidence', 'Referências declaradas; presença física não verificada');
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 1);
    assert.equal(await batchBox(page, 'state-missing').count(), 0);
    await page.getByRole('button', {name: /^Remover filtro Evidência e artefatos:/}).click();
    assert.equal(await page.locator('#native-evidence').inputValue(), '');

    await search(page, 'M1.1');
    await choose(page, 'native-kind', 'Execução (run)');
    assert.equal(await page.locator('[data-result-uid]').count(), 0);
    await page.getByText('Diagnóstico da busca e campos ausentes', {exact: true}).click();
    assert.match(await page.locator('#native-content').innerText(), /TYPE_NOT_MATCHING/);
    await filteredClear(page);
    await search(page, 'M1.1');
    await choose(page, 'native-execution', 'SUCCEEDED');
    await page.getByText('Diagnóstico da busca e campos ausentes', {exact: true}).click();
    assert.match(await page.locator('#native-content').innerText(), /FIELD_ABSENT/);
    await filteredClear(page);
    await search(page, 'NO-SUCH-ATLAS-ITEM-8465');
    await page.getByText('Diagnóstico da busca e campos ausentes', {exact: true}).click();
    assert.match(await page.locator('#native-content').innerText(), /NOT_FOUND_IN_SNAPSHOT/);
  });

  await check('T03_locate_expands_editorial_groups_and_focuses_exact_result', async () => {
    await filteredClear(page);
    await search(page, 'volume-1199');
    await page.locator('[data-locate-uid=' + attr(uid('volume-1199')) + ']').click();
    assert.equal(await page.locator('[data-pane="tree"]').getAttribute('aria-current'), 'page');
    const selected = page.locator('.editorial-svg .svg-record.selected');
    assert.equal(await selected.getAttribute('data-graph-id'), uid('volume-1199'));
    assert.equal(await selected.evaluate(node => document.activeElement === node || node.contains(document.activeElement)), true);
    assert.equal(await page.locator('#native-detail').isVisible(), true);
    assert.match(await page.locator('#native-detail-body').innerText(), /Execução de volume 1199/);
    await page.keyboard.press('Escape');
  });

  let planningRequestStart;
  await check('T04_visible_batch_is_not_all_filtered_and_survives_pages_views_filters', async () => {
    await filteredClear(page);
    await openNativePane(page, 'records');
    if (await selectedCount(page)) await clickAction(page, 'native-clear-batch');
    const visible = await page.locator('#native-content [data-batch-uid]').count();
    assert.ok(visible > 0 && visible < expected.total_records);
    planningRequestStart = report.requests.length;
    await page.locator('#native-select-visible').click();
    assert.equal(await selectedCount(page), visible);
    assert.equal(Number(await page.locator('#native-batch-summary').getAttribute('data-visible-count')), visible);
    await page.locator('#native-content').getByRole('button', {name: 'Próxima →', exact: true}).click();
    assert.equal(await selectedCount(page), visible);
    assert.equal(Number(await page.locator('#native-batch-summary').getAttribute('data-visible-count')), 0);
    const nextCheckbox = page.locator('#native-content [data-batch-uid]').first();
    await nextCheckbox.check();
    assert.equal(await selectedCount(page), visible + 1);
    await openNativePane(page, 'tree');
    assert.equal(await selectedCount(page), visible + 1);
    await page.getByRole('button', {name: 'Recolher', exact: true}).click();
    assert.equal(await selectedCount(page), visible + 1);
    await openNativePane(page, 'tables');
    assert.equal(await selectedCount(page), visible + 1);
    await openNativePane(page, 'records');
    const filterStart = performance.now();
    await page.locator('#native-search').fill('volume');
    assert.match(await page.locator('#native-select-filtered').innerText(), new RegExp('\\(' + expected.bulk_records + '\\)$'));
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 0);
    assert.ok(await page.locator('#native-content [data-batch-uid]').count() > 0);
    const filterElapsed = Math.round(performance.now() - filterStart);
    report.bulk_filter_ms = filterElapsed;
    assert.ok(filterElapsed <= 2000, 'SC-003: filtering 1,200+ loaded records responds within 2 s (observed ' + filterElapsed + 'ms)');
    await page.locator('#native-search').fill('M11');
    assert.equal(await selectedCount(page), visible + 1);
    assert.ok(Number(await page.locator('#native-batch-summary').getAttribute('data-hidden-count')) >= visible);
    await filteredClear(page);
    const start = performance.now();
    await page.locator('#native-select-filtered').click();
    assert.equal(await selectedCount(page), expected.total_records);
    const elapsed = Math.round(performance.now() - start);
    report.bulk_select_ms = elapsed;
    assert.ok(elapsed <= 2000, 'SC-003: selecting 1,200+ loaded records responds within 2 s (observed ' + elapsed + 'ms)');
    await openNativePane(page, 'selected');
    assert.match(await page.locator('#native-batch-summary').innerText(), new RegExp(String(expected.total_records)));
    await clickAction(page, 'native-clear-batch');
    assert.equal(await selectedCount(page), 0);
    assert.equal(await page.locator('#native-batch-bar').isHidden(), true);
  });

  await check('T05_compare_selected_and_inspect_only_declared_references', async () => {
    await filteredClear(page);
    await openNativePane(page, 'records');
    await page.locator('#native-search').fill('run-rf-proof');
    await batchBox(page, 'run-rf-proof').check();
    await page.locator('#native-search').fill('state-missing');
    await batchBox(page, 'state-missing').check();
    assert.equal(await selectedCount(page), 2);
    await filteredClear(page);
    await page.locator('#native-compare').click();
    const text = await page.locator('#native-content').innerText();
    assert.match(text, /Execução RF comprovada na fixture/);
    assert.match(text, /Registro sem estado nem retenção/);
    assert.match(text, /SUCCEEDED/);
    assert.match(text, /Não declarado|AUSENTE/);
    await clickAction(page, 'native-batch-links');
    assert.match(await page.locator('#native-content').innerText(), /resource-proof|Dossiê sintético declarado/);
    await context.grantPermissions(['clipboard-read', 'clipboard-write'], {origin});
    await clickAction(page, 'native-copy-references');
    const copied = await page.evaluate(() => navigator.clipboard.readText());
    assert.ok(copied.includes(uid('run-rf-proof')) && copied.includes(uid('state-missing')));
    assert.ok(copied.includes(expected.revision_a), 'Copied references include their exact revision');
  });

  await check('T06_T07_T08_retention_export_is_exact_protected_and_non_executable', async () => {
    await openNativePane(page, 'baselines');
    await batchBox(page, 'M1.1').check();
    assert.equal(await selectedCount(page), 3);
    await page.locator('#native-retention').click();
    assert.match(await page.locator('#native-content').innerText(), /A medir no ambiente LOCAL/);
    await page.locator('[data-intent-uid=' + attr(uid('run-rf-proof')) + ']').selectOption('REVIEW_FOR_REMOVAL');
    const serialized = await download(page, '#native-export-plan', 'synthetic-retention-plan.json');
    const plan = JSON.parse(serialized);
    assert.equal(plan.schema, 'atlas-retention-plan/1');
    assert.equal(plan.version, 1);
    assert.equal(plan.status, 'PROPOSAL_ONLY');
    assert.equal(plan.DELETE_AUTHORIZED, 'NO');
    assert.equal(plan.source.revision, expected.revision_a);
    assert.match(plan.source.metadata_sha256, /^[a-f0-9]{64}$/);
    assert.equal(plan.selection.length, 3);
    assert.equal(new Set(plan.selection.map(item => item.selection_key)).size, 3);
    assert.deepEqual(new Set(plan.selection.map(item => item.uid)), new Set([uid('run-rf-proof'), uid('state-missing'), uid('M1.1')]));
    for (const item of plan.selection) {
      assert.equal(item.source_revision, expected.revision_a);
      assert.equal(item.source_metadata_sha256, plan.source.metadata_sha256);
      assert.equal(item.source_id, plan.source.id);
      assert.equal(item.dto_kind, item.uid === uid('M1.1') ? 'table' : 'record');
    }
    const baseline = plan.items.find(item => item.identity.uid === uid('run-rf-proof'));
    const missing = plan.items.find(item => item.identity.uid === uid('state-missing'));
    const table = plan.items.find(item => item.identity.uid === uid('M1.1'));
    assert.equal(baseline.raw_json, expected.raw_json['run-rf-proof']);
    assert.ok(baseline.raw_json.includes('9007199254740993'));
    assert.ok(baseline.raw_json.includes('0.123456789012345678901'));
    assert.equal(baseline.baseline.sourceConfirmed, true);
    assert.equal(baseline.intent, 'REVIEW_FOR_REMOVAL');
    for (const item of plan.items) {
      assert.equal(item.protection.status, 'PROTECTED');
      assert.equal(item.protection.removal_authorized, false);
      assert.ok(item.protection.reasons.length > 0);
      assert.ok(item.pending_verifications.length > 0);
      assert.equal(Object.hasOwn(item, 'command'), false);
      assert.equal(Object.hasOwn(item, 'script'), false);
    }
    assert.equal(missing.raw_json, expected.raw_json['state-missing']);
    assert.equal(missing.intent, 'UNDECIDED');
    assert.equal(missing.execution.present, false);
    assert.ok(missing.gaps.length > 0);
    assert.equal(table.type, 'table');
    assert.equal(table.execution.present, false, 'A requirements table is never classified as an execution');
    assert.equal(table.raw_json, expected.raw_json['M1.1']);
    assert.equal(table.table_rows.status, 'COMPLETE_FOR_SNAPSHOT');
    assert.equal(table.table_rows.count, 39);
    assert.equal(table.table_rows.transport_skeleton, true);
    assert.deepEqual(table.table_rows.rows.map(row => row.raw_json), expected.table_rows_raw_json);
    assert.equal(plan.space_estimate.status, 'NOT_MEASURED');
    assert.equal(plan.space_estimate.label, 'A medir no ambiente LOCAL');
    assert.equal(plan.provenance.source_read_only, true);
    assert.equal(plan.provenance.physical_presence_verified, false);
    assert.ok(plan.pending_verifications.length > 0);
    assert.equal(await page.getByRole('button', {name: /^(Apagar|Excluir|Remover arquivos|Executar descarte)/i}).count(), 0);
    report.retention = {schema: plan.schema, selection: plan.selection.length, status: plan.status,
      DELETE_AUTHORIZED: plan.DELETE_AUTHORIZED, exact_original_json: true, protected: plan.items.length};
  });

  await check('G5_baseline_designation_is_not_inferred_from_name_or_reference', async () => {
    await filteredClear(page);
    await openNativePane(page, 'baselines');
    assert.equal(await batchBox(page, 'run-rf-proof').count(), 1);
    assert.equal(await batchBox(page, 'M1.1').count(), 1);
    assert.equal(await batchBox(page, 'name-only-baseline').count(), 0);
    assert.equal(await batchBox(page, 'baseline-reference-only').count(), 0);
    assert.equal(await batchBox(page, 'M1').count(), 0);
    assert.equal(await batchBox(page, 'M11').count(), 0);
  });

  await check('G5_operator_baseline_annotation_has_source_revision_and_is_exported_without_DTO_mutation', async () => {
    await search(page, 'name-only-baseline');
    await result(page, 'name-only-baseline').getByRole('button', {name: 'Ver detalhes', exact: true}).click();
    const label = 'Motivo da anotação do operador (somente sessão)';
    const note = 'Designação sintética explícita do operador para QA; sem aprovação científica.';
    await page.getByRole('textbox', {name: label, exact: true}).fill(note);
    await page.getByRole('button', {name: 'Anotar baseline nesta sessão', exact: true}).click();
    assert.match(await page.locator('#native-detail-body').innerText(), /Designação do operador nesta sessão/);
    await page.keyboard.press('Escape');
    await openNativePane(page, 'baselines');
    assert.equal(await batchBox(page, 'name-only-baseline').count(), 1);
    await batchBox(page, 'name-only-baseline').check();
    assert.equal(await selectedCount(page), 4);
    await page.locator('#native-retention').click();
    const plan = JSON.parse(await download(page, '#native-export-plan', 'synthetic-retention-with-annotation.json'));
    const annotated = plan.items.find(item => item.identity.uid === uid('name-only-baseline'));
    assert.equal(annotated.baseline.status, 'OPERATOR_SESSION');
    assert.equal(annotated.baseline.sourceConfirmed, false);
    assert.equal(annotated.baseline.operatorDesignated, true);
    assert.equal(annotated.baseline.annotation.origin, 'OPERATOR_SESSION');
    assert.equal(annotated.baseline.annotation.note, note);
    assert.equal(annotated.baseline.annotation.selection_key, annotated.identity.selection_key);
    assert.equal(annotated.baseline.annotation.snapshot_key, plan.snapshot_key);
    assert.equal(annotated.raw_json, expected.raw_json['name-only-baseline']);
    assert.equal(Object.hasOwn(JSON.parse(annotated.raw_json), 'baseline'), false);
    assert.equal(annotated.protection.removal_authorized, false);
  });

  await check('G8_dossier_export_preserves_selection_exact_records_table_rows_and_pending_verifications', async () => {
    await clickAction(page, 'native-dossier');
    assert.match(await page.locator('#native-content').innerText(), /Dossiê dos selecionados/);
    const dossier = JSON.parse(await download(page, '#native-export-dossier', 'synthetic-triage-dossier.json'));
    assert.equal(dossier.schema, 'atlas-triage-dossier/1');
    assert.equal(dossier.status, 'PROPOSAL_ONLY');
    assert.equal(dossier.DELETE_AUTHORIZED, 'NO');
    assert.equal(dossier.selection.length, 4);
    assert.equal(dossier.source.revision, expected.revision_a);
    const run = dossier.items.find(item => item.identity.uid === uid('run-rf-proof'));
    const table = dossier.items.find(item => item.identity.uid === uid('M1.1'));
    assert.equal(run.raw_json, expected.raw_json['run-rf-proof']);
    assert.deepEqual(table.table_rows.rows.map(row => row.raw_json), expected.table_rows_raw_json);
    assert.ok(dossier.pending_verifications.length > 0);
    assert.equal(dossier.provenance.physical_presence_verified, false);
  });

  await check('UX_UI_01_deselection_refreshes_dossier_export_plan_controls_and_intentions', async () => {
    await clickAction(page, 'native-clear-batch');
    for (const key of ['run-rf-proof', 'state-missing']) {
      await search(page, key);
      await batchBox(page, key).check();
    }
    await filteredClear(page);
    await clickAction(page, 'native-dossier');
    assert.equal(await selectedCount(page), 2);
    assert.equal(await navigationCount(page, 'selected'), 2);
    assert.equal(await navigationCount(page, 'retention'), 2);
    assert.equal(await batchBox(page, 'state-missing').isChecked(), true);
    await batchBox(page, 'state-missing').click();
    assert.equal(await selectedCount(page), 1);
    assert.equal(await result(page, 'state-missing').count(), 0, 'Dossier removes a deselected card before any navigation');
    const dossier = JSON.parse(await download(page, '#native-export-dossier', 'synthetic-triage-dossier-current-selection.json'));
    assert.deepEqual(dossier.selection.map(item => item.uid), [uid('run-rf-proof')]);
    assert.deepEqual(dossier.items.map(item => item.identity.uid), [uid('run-rf-proof')]);
    assert.equal(dossier.items[0].raw_json, expected.raw_json['run-rf-proof']);

    await search(page, 'state-missing');
    await batchBox(page, 'state-missing').check();
    await filteredClear(page);
    await page.locator('#native-retention').click();
    await page.locator('[data-intent-uid=' + attr(uid('run-rf-proof')) + ']').selectOption('REVIEW_FOR_REMOVAL');
    await page.locator('[data-intent-uid=' + attr(uid('state-missing')) + ']').selectOption('KEEP_ESSENTIALS');
    assert.equal(await batchBox(page, 'state-missing').isChecked(), true);
    await batchBox(page, 'state-missing').click();
    assert.equal(await selectedCount(page), 1);
    assert.equal(await result(page, 'state-missing').count(), 0);
    assert.equal(await page.locator('[data-intent-uid=' + attr(uid('state-missing')) + ']').count(), 0,
      'An unselected item must not retain an actionable intention control');
    assert.equal(await page.locator('#native-content [data-intent-uid]').count(), 1);
    assert.equal(await navigationCount(page, 'selected'), 1);
    assert.equal(await navigationCount(page, 'retention'), 1);
    const plan = JSON.parse(await download(page, '#native-export-plan', 'synthetic-retention-current-selection.json'));
    assert.deepEqual(plan.selection.map(item => item.uid), [uid('run-rf-proof')]);
    assert.deepEqual(plan.items.map(item => item.identity.uid), [uid('run-rf-proof')]);
    assert.equal(plan.items[0].intent, 'REVIEW_FOR_REMOVAL');
    assert.equal(plan.items[0].protection.removal_authorized, false);

    await search(page, 'state-missing');
    await batchBox(page, 'state-missing').check();
    await page.locator('#native-retention').click();
    assert.equal(await page.locator('[data-intent-uid=' + attr(uid('state-missing')) + ']').inputValue(), 'UNDECIDED',
      'Reselecting an item does not revive the removed intention');
    // Restore the original four-item batch and session annotation for the
    // existing source/revision invalidation task below.
    for (const key of ['M1.1', 'name-only-baseline']) {
      await search(page, key);
      await batchBox(page, key).check();
    }
    await filteredClear(page);
    assert.equal(await selectedCount(page), 4);
  });

  await check('UX_UI_03_04_baseline_annotation_updates_active_list_filtered_total_and_navigation', async () => {
    await openNativePane(page, 'baselines');
    assert.equal(await navigationCount(page, 'baselines'), 3);
    assert.equal(await page.locator('#native-content [data-result-uid]').count(), 3);
    assert.match(await page.locator('#native-select-filtered').innerText(), /\(3\)$/);
    await result(page, 'name-only-baseline').getByRole('button', {name: 'Ver detalhes', exact: true}).click();
    await page.getByRole('button', {name: 'Remover anotação de sessão', exact: true}).click();
    assert.equal(await page.locator('[data-pane="baselines"]').getAttribute('aria-current'), 'page');
    assert.equal(await result(page, 'name-only-baseline').count(), 0, 'The active baseline list refreshes immediately after removal');
    assert.equal(await page.locator('#native-content [data-result-uid]').count(), 2);
    assert.equal(await navigationCount(page, 'baselines'), 2);
    assert.match(await page.locator('#native-select-filtered').innerText(), /\(2\)$/);
    assert.equal(await selectedCount(page), 4, 'Removing a designation does not remove an explicit batch selection');
    await page.getByRole('textbox', {name: 'Motivo da anotação do operador (somente sessão)', exact: true})
      .fill('Designação sintética explícita do operador para QA; sem aprovação científica.');
    await page.getByRole('button', {name: 'Anotar baseline nesta sessão', exact: true}).click();
    assert.equal(await result(page, 'name-only-baseline').count(), 1, 'The active baseline list refreshes immediately after designation');
    assert.match(await result(page, 'name-only-baseline').innerText(), /Designação do operador nesta sessão/);
    assert.equal(await page.locator('#native-content [data-result-uid]').count(), 3);
    assert.equal(await navigationCount(page, 'baselines'), 3);
    assert.match(await page.locator('#native-select-filtered').innerText(), /\(3\)$/);
    assert.equal(await navigationCount(page, 'selected'), 4);
    assert.equal(await navigationCount(page, 'retention'), 4);
    await page.keyboard.press('Escape');
  });

  await check('G13_hostile_labels_URLs_and_prototype_names_remain_inert', async () => {
    await search(page, 'hostile-record');
    const hostile = result(page, 'hostile-record');
    assert.equal(await hostile.count(), 1);
    assert.match(await hostile.innerText(), /<img/);
    assert.equal(await hostile.locator('img,script,iframe,object').count(), 0);
    assert.equal(await page.evaluate(() => Boolean(globalThis.__triageInjected || Object.prototype.polluted)), false);
    assert.deepEqual(report.external_requests, []);
    assert.deepEqual(report.errors, []);
  });

  await check('T10_selection_comparison_planning_make_no_HTTP_or_source_write_requests', async () => {
    const operations = report.requests.slice(planningRequestStart);
    assert.deepEqual(operations, [], 'Selection, comparison, filtering and proposals stay within the loaded snapshot');
    assert.deepEqual(report.external_requests, []);
    assert.equal(report.requests.some(request => !['GET', 'HEAD'].includes(request.method)), false);
    report.selection_planning_http_requests = operations.length;
  });

  await check('G6_switching_source_revision_invalidates_selection_intents_and_session_state', async () => {
    assert.equal(await selectedCount(page), 4);
    await page.locator('#native-source').selectOption('source-2');
    await page.waitForFunction(revision => document.getElementById('native-revision')?.textContent.includes(revision), expected.revision_b);
    assert.equal(await selectedCount(page), 0);
    assert.equal(await page.locator('#native-batch-bar').isHidden(), true);
    await openNativePane(page, 'selected');
    assert.equal(await page.locator('#native-content [data-batch-uid]').count(), 0);
    await openNativePane(page, 'baselines');
    assert.equal(await batchBox(page, 'name-only-baseline').count(), 0, 'Session baseline annotation is invalidated with its source revision');
    await page.locator('#native-source').selectOption('source-1');
    assert.equal(await selectedCount(page), 0, 'Returning to the earlier revision must not silently revive stale selection');
  });

  const viewports = [{width: 1440, height: 1200}, {width: 1101, height: 900}, {width: 1024, height: 900},
    {width: 800, height: 1000}, {width: 390, height: 844}, {width: 320, height: 740}];
  for (const viewport of viewports) {
    await check('G11_responsive_keyboard_touch_focus_and_minimap_' + viewport.width, async () => {
      const touch = viewport.width <= 390;
      const layoutContext = await browser.newContext({viewport, isMobile: touch, hasTouch: touch, acceptDownloads: true});
      await protectNetwork(layoutContext);
      const layoutPage = await layoutContext.newPage();
      layoutPage.on('pageerror', error => report.errors.push(error.message));
      layoutPage.setDefaultTimeout(10000);
      try {
        await layoutPage.goto(url, {waitUntil: 'networkidle'});
        await layoutPage.waitForFunction(() => !document.getElementById('native-download')?.disabled);
        const toggle = layoutPage.locator('#native-menu-toggle'), sidebar = layoutPage.locator('#native-sidebar');
        const initiallyExpanded = await toggle.getAttribute('aria-expanded') === 'true';
        if (viewport.width === 1440) {
          assert.equal(initiallyExpanded, true, 'Wide desktop navigation is initially visible');
          const sidebarBox = await sidebar.boundingBox();
          assert.ok(sidebarBox.width >= 240 && sidebarBox.width <= 280);
          const before = await layoutPage.locator('#native-main').boundingBox();
          await toggle.click();
          const after = await layoutPage.locator('#native-main').boundingBox();
          assert.ok(after.width > before.width, 'Collapsing the rail returns width to the work area');
          await toggle.click();
        } else if (touch) {
          assert.equal(initiallyExpanded, false, 'Mobile navigation is a temporary panel');
          assert.match(await toggle.innerText(), /Menu/);
          await toggle.tap();
          assert.equal(await sidebar.isVisible(), true);
          assert.equal(await sidebar.evaluate(node => node.contains(document.activeElement)), true);
          const focusable = sidebar.locator('button:visible, a:visible, input:visible, select:visible, [tabindex="0"]:visible');
          await focusable.last().focus();
          await layoutPage.keyboard.press('Tab');
          assert.equal(await sidebar.evaluate(node => node.contains(document.activeElement)), true, 'Tab does not escape the temporary modal drawer');
          await focusable.first().focus();
          await layoutPage.keyboard.press('Shift+Tab');
          assert.equal(await focusable.last().evaluate(node => document.activeElement === node), true, 'Shift+Tab wraps to the last control inside the temporary drawer');
          await layoutPage.keyboard.press('Escape');
          assert.equal(await toggle.getAttribute('aria-expanded'), 'false');
          assert.equal(await toggle.evaluate(node => document.activeElement === node), true);
          await layoutPage.keyboard.press('Enter');
          assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
          await layoutPage.locator('#native-nav-close').click();
          assert.equal(await toggle.evaluate(node => document.activeElement === node), true);
          await layoutPage.keyboard.press('Space');
          assert.equal(await toggle.getAttribute('aria-expanded'), 'true');
          await layoutPage.keyboard.press('Escape');
        }
        await search(layoutPage, 'run-rf-proof');
        await batchBox(layoutPage, 'run-rf-proof').check();
        const textSamples = await layoutPage.evaluate(readContrastSamples, [
          {selector: '.triage-query label[for="native-source"]'},
          {selector: '.triage-query label[for="native-search"]'},
          {selector: '.intro p'},
          {selector: '.triage-result[data-batch-selected="true"] .muted'},
        ]);
        for (const sample of textSamples) {
          sample.minimum_ratio = Math.min(...sample.backgrounds.map(background => contrastRatio(sample.foreground, background)));
          report.contrast.push({viewport: viewport.width, kind: 'text', ...sample});
          assert.ok(sample.minimum_ratio >= 4.5, sample.selector + ' requires 4.5:1 text contrast: ' + JSON.stringify(sample));
        }
        await layoutPage.locator('[data-locate-uid=' + attr(uid('run-rf-proof')) + ']').click();
        assert.equal(await selectedCount(layoutPage), 1);
        if (viewport.width === 1101) {
          assert.equal(await toggle.getAttribute('aria-expanded'), 'true', 'The breakpoint probe requires the open sidebar');
          assert.equal(await layoutPage.locator('#native-detail').isVisible(), true);
          for (const id of ['native-source', 'native-search', 'native-search-all', 'native-download']) {
            const control = layoutPage.locator('#' + id);
            await control.scrollIntoViewIfNeeded();
            const probe = await control.evaluate(node => {
              const box = node.getBoundingClientRect(), detail = document.getElementById('native-detail').getBoundingClientRect();
              const points = [.2, .5, .8].flatMap(x => [.2, .5, .8].map(y => [box.x + box.width * x, box.y + box.height * y]));
              return {id: node.id, rect: {x: box.x, y: box.y, width: box.width, height: box.height},
                hit_points: points.filter(([x, y]) => node.contains(document.elementFromPoint(x, y))).length,
                in_viewport: box.left >= 0 && box.top >= 0 && box.right <= innerWidth && box.bottom <= innerHeight,
                intersects_detail: box.left < detail.right && box.right > detail.left && box.top < detail.bottom && box.bottom > detail.top};
            });
            report.breakpoint_controls.push({viewport: viewport.width, ...probe});
            assert.equal(probe.hit_points, 9, id + ' must receive real pointer input with sidebar and details open');
            assert.equal(probe.in_viewport, true, id + ' remains within the viewport');
            assert.equal(probe.intersects_detail, false, id + ' must not overlap the details drawer');
          }
          const screenshot = reportPath.replace('.json', '-controls-1101.png');
          await layoutPage.screenshot({path: screenshot, fullPage: false});
          report.screenshots.push(path.basename(screenshot));
        }
        await layoutPage.getByRole('button', {name: 'Focar seleção', exact: true}).click();
        const focused = await layoutPage.locator('.editorial-svg .svg-record.selected').evaluate(node => {
          const card = node.querySelector('.node-surface').getBoundingClientRect(), map = node.ownerSVGElement.getBoundingClientRect();
          const detail = document.getElementById('native-detail').getBoundingClientRect();
          const title = node.querySelector('text'), scale = title.getScreenCTM();
          const identity = node.getAttribute('data-graph-id');
          const points = [.1, .3, .5, .7, .9].flatMap(x => [.1, .3, .5, .7, .9].map(y => [card.x + card.width * x, card.y + card.height * y]));
          const occluded = points.flatMap(([x, y]) => {
            const hit = document.elementFromPoint(x, y);
            // The batch checkbox is a sibling of the record group. It belongs
            // to this card only when the exact presentation UID agrees.
            if (node.contains(hit) || hit?.closest('.svg-batch')?.getAttribute('data-batch-uid') === identity) return [];
            return [{x, y, tag: hit?.tagName, id: hit?.id,
              batch_bar: Boolean(hit?.closest('#native-batch-bar')), detail: Boolean(hit?.closest('#native-detail'))}];
          });
          return {uid: identity, rect: {x: card.x, y: card.y, width: card.width, height: card.height},
            hit_points: points.length - occluded.length, occluded_points: occluded,
            font_px: parseFloat(getComputedStyle(title).fontSize) * Math.hypot(scale.a, scale.b),
            whole: card.left >= Math.max(0, map.left) - 1 && card.right <= Math.min(innerWidth, map.right) + 1 &&
              card.top >= Math.max(0, map.top) - 1 && card.bottom <= Math.min(innerHeight, map.bottom) + 1,
            intersects_detail: card.left < detail.right && card.right > detail.left && card.top < detail.bottom && card.bottom > detail.top};
        });
        report.focused_results.push({viewport: viewport.width, ...focused});
        assert.equal(focused.uid, uid('run-rf-proof'));
        assert.equal(focused.whole, true, 'The focused result is entirely visible inside its map and viewport');
        assert.equal(focused.intersects_detail, false, 'Details must not obscure the focused result');
        assert.equal(focused.hit_points, 25, 'The focused result or its own batch checkbox receives all 25 pointer samples');
        assert.ok(focused.font_px >= 8, 'The focused result retains the accepted A01 minimum title size');
        const taskScreenshot = reportPath.replace('.json', '-task-' + viewport.width + '.png');
        await layoutPage.screenshot({path: taskScreenshot, fullPage: false});
        report.screenshots.push(path.basename(taskScreenshot));
        const mini = layoutPage.locator('.editorial-minimap');
        await mini.scrollIntoViewIfNeeded();
        const geometry = await mini.evaluate(node => {
          const box = node.getBoundingClientRect();
          const points = [.1, .3, .5, .7, .9].flatMap(x => [.1, .3, .5, .7, .9].map(y => [box.x + box.width * x, box.y + box.height * y]));
          const close = document.getElementById('native-close-detail'), closeBox = close.getBoundingClientRect();
          return {viewport: [innerWidth, innerHeight], mini: {x: box.x, y: box.y, width: box.width, height: box.height},
            hit_points: points.filter(([x, y]) => node.contains(document.elementFromPoint(x, y))).length,
            in_viewport: box.x >= 0 && box.y >= 0 && box.right <= innerWidth && box.bottom <= innerHeight,
            close_reachable: close.contains(document.elementFromPoint(closeBox.x + closeBox.width / 2, closeBox.y + closeBox.height / 2)),
            document_width: document.documentElement.scrollWidth};
        });
        assert.equal(geometry.hit_points, 25, 'Batch bar, menu and details must not occlude the minimap');
        assert.equal(geometry.in_viewport, true);
        assert.equal(geometry.close_reachable, true);
        assert.ok(geometry.document_width <= viewport.width + 1, 'Horizontal overflow remains in dedicated scroll regions');
        const cameraBefore = await layoutPage.locator('.editorial-svg').getAttribute('viewBox');
        const point = {x: geometry.mini.x + geometry.mini.width * .15, y: geometry.mini.y + geometry.mini.height * .15};
        if (touch) await layoutPage.touchscreen.tap(point.x, point.y);
        else await layoutPage.mouse.click(point.x, point.y);
        assert.notEqual(await layoutPage.locator('.editorial-svg').getAttribute('viewBox'), cameraBefore, 'Real pointer input changes the camera');
        await layoutPage.keyboard.press('Escape');
        assert.equal(await selectedCount(layoutPage), 1);
        for (const control of ['native-menu-toggle', 'native-select-visible', 'native-select-filtered']) {
          const node = layoutPage.locator('#' + control);
          await node.scrollIntoViewIfNeeded();
          const bounds = await node.boundingBox();
          assert.ok(bounds && bounds.width >= 24 && bounds.height >= 24, control + ' has a minimum 24px target');
        }
        await toggle.focus();
        await layoutPage.keyboard.press('Tab');
        const focus = await layoutPage.locator(':focus').evaluate(node => {
          const box = node.getBoundingClientRect(), style = getComputedStyle(node);
          return {outline: style.outlineStyle, width: parseFloat(style.outlineWidth),
            visible: box.width > 0 && box.height > 0 && box.top >= 0 && box.bottom <= innerHeight};
        });
        assert.ok(focus.outline !== 'none' && focus.width >= 2 && focus.visible, 'Keyboard focus is visible and not obscured');
        const [focusSample] = await layoutPage.evaluate(readContrastSamples,
          [{selector: ':focus', property: 'outlineColor', background: '.topbar'}]);
        assert.equal(await layoutPage.locator(':focus').evaluate(node => Boolean(node.closest('.topbar'))), true,
          'The focus contrast probe measures a header control against the header background');
        focusSample.minimum_ratio = Math.min(...focusSample.backgrounds.map(background => contrastRatio(focusSample.foreground, background)));
        report.contrast.push({viewport: viewport.width, kind: 'focus', ...focusSample});
        assert.ok(focusSample.minimum_ratio >= 3, 'Header focus requires 3:1 contrast: ' + JSON.stringify(focusSample));
        focus.contrast = focusSample;
        geometry.keyboard_focus = focus;
        geometry.touch = touch;
        report.layout.push(geometry);
        const screenshot = reportPath.replace('.json', '-' + viewport.width + '.png');
        await layoutPage.screenshot({path: screenshot, fullPage: false});
        report.screenshots.push(path.basename(screenshot));
      } catch (error) {
        const screenshot = reportPath.replace('.json', '-failure-' + viewport.width + '.png');
        try {
          await layoutPage.screenshot({path: screenshot, fullPage: false});
          report.screenshots.push(path.basename(screenshot));
        } catch (captureError) { report.failure_capture_error = String(captureError); }
        throw error;
      } finally {
        await layoutContext.close();
      }
    });
  }
  await runN03Checks({browser, check, expected, protectNetwork, report, url});
  await runReadabilityChecks({browser, check, protectNetwork, report, url});
  assert.deepEqual(report.errors, []);
  assert.deepEqual(report.external_requests, []);
  report.status = 'PASS';
  report.phase = 'COMPLETE';
} catch (error) {
  failure = error;
  report.failure = error.stack || String(error);
  if (report.phase === 'BROWSER_BOOTSTRAP') report.status = 'BLOCKED';
} finally {
  if (browser) await browser.close();
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
}
if (failure) throw failure;
console.log(JSON.stringify({status: report.status, checks: report.checks.length, report: reportPath}));
