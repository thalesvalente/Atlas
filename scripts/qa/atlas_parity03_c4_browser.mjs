/** Main-app C0+P03 proof: installed server, explicit choices and isolated identities. */
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import path from 'node:path';

const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const args = Object.fromEntries(process.argv.slice(2).reduce((items, value, index, all) => {
  if (index % 2 === 0) items.push([value.slice(2), all[index + 1]]);
  return items;
}, []));
for (const name of ['url', 'report', 'metadata', 'replacement', 'screenshots']) {
  if (!args[name]) throw new Error('Missing argument: ' + name);
}
const origin = new URL(args.url).origin;
const receipt = {status: 'FAIL', scope: 'C4_INSTALLED_MAIN_APP_C0_PLUS_P03',
  checks: [], screenshots: [], external_requests: [], page_errors: [], console_errors: [], skips: 0,
  test_data: 'NEW_PUBLIC_SYNTHETIC_COPIES', rich_demonstrators_active: false,
  host_operation: 'NOT_RUN', native_browser_zoom_200: 'NOT_MEASURED',
  reflow_scope: '1440, 390 and 320 CSS-pixel browser viewports; no CSS zoom'};
let browser, context, page;
const check = (name, condition) => {
  receipt.checks.push({name, status: condition ? 'PASS' : 'FAIL'});
  assert.ok(condition, name);
};
const sourceKey = source => JSON.stringify([source.id, source.snapshot_id]);
const key = (source, run) => JSON.stringify([source.id, run.id]);
const runControl = (kind, source, run) => page.locator(
  '[data-testid=' + JSON.stringify(kind) + '][data-run-key=' + JSON.stringify(key(source, run)) + ']');
const property = (kind, id) => page.locator(
  '#detail [data-p03-property-key][data-property-kind=' + JSON.stringify(kind) +
  '][data-property-id=' + JSON.stringify(id) + ']');
const row = id => page.locator('#detail [data-testid="p03-derived-tables"] [data-row-id=' + JSON.stringify(id) + ']');
const tables = () => page.locator('#detail [data-component="parity02-p03-table"]');
const choices = () => page.locator('#detail [data-p03-property-key]');
const model = () => page.evaluate(async () => (await fetch('/api/catalog')).json());
async function open(source, run) {
  await runControl('run-open', source, run).click();
  await page.locator('#detail [data-testid="p03-property-selection"]').waitFor();
  assert.equal(await page.locator('#detail-content > code').textContent(), run.id);
}
async function selectAll() {
  const list = choices();
  for (let index = 0; index < await list.count(); index++) await list.nth(index).check();
}
async function screenshot(name) {
  await mkdir(args.screenshots, {recursive: true});
  const file = name + '.png';
  await page.screenshot({path: path.join(args.screenshots, file), fullPage: true});
  receipt.screenshots.push(file);
}
async function noOverflow() {
  return page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1
    && document.body.scrollWidth <= innerWidth + 1);
}
try {
  browser = await chromium.launch({headless: true,
    ...(process.env.ATLAS_BROWSER_BINARY ? {executablePath: process.env.ATLAS_BROWSER_BINARY} : {}),
    args: ['--disable-background-networking', '--disable-component-update', '--no-first-run']});
  receipt.browser_version = browser.version();
  receipt.playwright_version = require('playwright/package.json').version;
  context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  await context.route('**/*', async route => {
    const target = route.request().url();
    if (/^https?:/.test(target) && new URL(target).origin !== origin) {
      receipt.external_requests.push(target);
      await route.abort();
    } else await route.continue();
  });
  page = await context.newPage();
  page.on('pageerror', error => receipt.page_errors.push(error.message));
  page.on('console', event => {
    if (event.type() === 'error') receipt.console_errors.push(event.text());
  });
  const response = await page.goto(args.url, {waitUntil: 'networkidle'});
  assert.equal(response.status(), 200);
  await page.getByTestId('run-open').first().waitFor();
  const initial = await model();
  const [sourceA, sourceB] = initial.sources;
  const runA = sourceA.read_model.runs.find(run => run.id.endsWith('run:00'));
  const runB = sourceB.read_model.runs.find(run => run.id === runA.id);
  const prefix = runA.id.slice(0, -'run:00'.length);
  const propertyIds = {exact: prefix + 'c4:exact', absent: prefix + 'c4:absent',
    boolean: prefix + 'c4:boolean', metric: prefix + 'metric:00'};
  check('two_valid_sources_keep_repeated_run_and_property_ids_scoped',
    initial.sources.length === 2 && initial.sources.every(source => source.report.valid && source.status === 'READY')
    && runA.id === runB.id && runA.name !== runB.name && sourceA.id !== sourceB.id);
  for (const source of initial.sources) {
    check('metadata_projection_is_bound_to_explicit_source_snapshot_' + source.id,
      source.presentation.errors.length === 0
      && source.presentation.metadata.source.key === sourceKey(source)
      && source.presentation.metadata.source.metadata_sha256 === source.metadata_sha256);
  }
  check('boolean_is_actual_false_and_large_integer_uses_exact_display_text',
    runA.parameters.find(item => item.id === propertyIds.boolean).value === false
    && runA.parameters.find(item => item.id === propertyIds.boolean).display_value === 'false'
    && runA.metrics.find(item => item.id === propertyIds.exact).display_value === '9007199254740993'
    && runA.metrics.find(item => item.id === propertyIds.absent).value === null);
  const routes = ['/parity02_p03_table.js', '/parity02_p03_table.css',
    '/parity02_p03_artifacts.js', '/parity02_p03_artifacts.css', '/parity03_p03_composition.js'];
  for (const route of routes) assert.equal((await page.request.get(origin + route)).status(), 200);
  for (const route of ['/demo-data.js', '/harness.mjs', '/p03-candidate.json',
    '/static/parity02_p03_artifacts.js', '/packages/protocol/pyproject.toml']) {
    assert.equal((await page.request.get(origin + route)).status(), 404);
  }
  check('main_http_routes_allow_only_named_assets_and_keep_focal_demo_paths_inactive', true);
  await open(sourceA, runA);
  check('main_detail_has_metadata_and_lazy_explicit_property_selection',
    await page.locator('#detail [data-testid="p03-metadata"]').count() === 1
    && await choices().count() >= 6 && await choices().evaluateAll(nodes => nodes.every(node => !node.checked))
    && await tables().count() === 0);
  await selectAll();
  check('explicit_selection_builds_separate_category_type_and_unit_tables',
    await tables().count() === 5
    && await row(propertyIds.exact).locator('td').nth(2).textContent() === '9007199254740993'
    && await row(propertyIds.boolean).locator('td').nth(2).textContent() === 'false'
    && (await row(propertyIds.absent).locator('td').nth(2).textContent()).includes('Não informado')
    && (await row(propertyIds.absent).locator('td').nth(2).textContent()).includes('desconhecido não é zero'));
  const bindings = await tables().evaluateAll(nodes => nodes.map(node => ({
    source: node.dataset.sourceId, snapshot: node.dataset.snapshotId, entity: node.dataset.entityId,
    columns: node.querySelectorAll('thead th[scope="col"]').length,
    rows: [...node.querySelectorAll('tbody th')].every(th => th.scope === 'row'),
  })));
  check('semantic_tables_keep_source_snapshot_entity_and_declared_row_identity',
    bindings.every(binding => binding.source === sourceA.id && binding.snapshot === sourceA.snapshot_id
      && binding.entity === runA.id && binding.columns === 7 && binding.rows));
  const chosen = property('parameters', propertyIds.boolean);
  await chosen.focus();
  await page.keyboard.press('Space');
  check('keyboard_toggle_preserves_checkbox_focus_and_updates_only_derived_output',
    !await chosen.isChecked() && await chosen.evaluate(node => node === document.activeElement));
  await page.keyboard.press('Space');
  assert.ok(await chosen.isChecked());
  await chosen.evaluate(node => {window.__c4FocusedProperty = node;});
  await page.locator('#search').evaluate(node => {
    node.value = 'run:00';
    node.dispatchEvent(new Event('input', {bubbles: true}));
  });
  check('filter_render_keeps_same_detail_control_focus_and_explicit_selection',
    await chosen.evaluate(node => node === window.__c4FocusedProperty && node === document.activeElement)
    && await chosen.isChecked() && await tables().count() === 5);
  const deepLinkA = page.url();
  check('deep_link_preserves_C0_source_snapshot_and_run',
    new URL(deepLinkA).hash.includes('run=') && new URLSearchParams(new URL(deepLinkA).hash.slice(1)).get('scope') === initial.snapshot_id);
  await open(sourceB, runB);
  check('same_property_ids_in_source_B_do_not_reuse_source_A_choices',
    await choices().evaluateAll(nodes => nodes.every(node => !node.checked))
    && await tables().count() === 0);
  await selectAll();
  const bValue = await row(propertyIds.metric).locator('td').nth(2).textContent();
  check('source_B_tables_and_metadata_are_bound_to_B_without_cross_source_retargeting',
    bValue === runB.metrics.find(item => item.id === propertyIds.metric).display_value
    && bValue !== runA.metrics.find(item => item.id === propertyIds.metric).display_value
    && await tables().evaluateAll((nodes, id) => nodes.every(node => node.dataset.sourceId === id), sourceB.id)
    && await page.locator('#detail .p03-metadata-card').evaluateAll((nodes, expected) =>
      nodes.every(node => node.dataset.sourceKey === expected), sourceKey(sourceB)));
  const detail = await page.locator('#detail [data-testid="p03-metadata"]').innerText();
  check('File_mentions_and_hostile_text_keep_neutral_declared_semantics',
    detail.includes('Artefato declarado (File)') && detail.includes('Menções neutras')
    && detail.includes('<img') && detail.includes('<script>')
    && await page.locator('#detail [data-testid="p03-metadata"] img,#detail [data-testid="p03-metadata"] script').count() === 0
    && await page.locator('[data-semantic-kind],.p03-metadata-candidate').count() === 0
    && await page.evaluate(() => window.__c4QA === undefined && window.__atlasP02QA === undefined));
  await page.goBack();
  await page.waitForFunction(expected => document.querySelector('#detail-content > h3')?.textContent === expected, runA.name);
  check('back_navigation_restores_source_A_explicit_choices_without_cross_source_state',
    await choices().evaluateAll(nodes => nodes.every(node => node.checked))
    && await tables().evaluateAll((nodes, id) => nodes.every(node => node.dataset.sourceId === id), sourceA.id));
  await page.goForward();
  await page.waitForFunction(expected => document.querySelector('#detail-content > h3')?.textContent === expected, runB.name);
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({width, height: 1000});
    check('document_and_P03_embedding_reflow_at_' + width + '_css_pixels', await noOverflow());
    const scroll = await page.locator('#detail .atlas-p03-table__scroll').evaluateAll(nodes => nodes.map(node => ({
      width: node.clientWidth, scroll: node.scrollWidth, overflow: getComputedStyle(node).overflowX,
      tabindex: node.getAttribute('tabindex'), name: node.getAttribute('aria-label'),
    })));
    check('only_named_keyboard_accessible_table_regions_scroll_at_' + width,
      scroll.length === 5 && scroll.every(item => item.tabindex === '0' && item.name?.length > 0
        && (item.scroll <= item.width + 1 || ['auto', 'scroll'].includes(item.overflow))));
    await screenshot('c4-main-' + width);
  }
  const scrollRegion = page.locator('#detail .atlas-p03-table__scroll').first();
  await scrollRegion.focus();
  const beforeScroll = await scrollRegion.evaluate(node => node.scrollLeft);
  await page.keyboard.press('ArrowRight');
  await page.waitForFunction(previous => document.querySelector('#detail .atlas-p03-table__scroll').scrollLeft > previous, beforeScroll);
  check('table_overflow_is_reachable_with_keyboard_without_losing_focus',
    await scrollRegion.evaluate(node => node === document.activeElement));
  await page.keyboard.press('Escape');
  check('escape_closes_detail_and_restores_visible_C0_opener_focus',
    !await page.locator('#detail').isVisible()
    && await runControl('run-open', sourceB, runB).evaluate(node => node === document.activeElement));
  await page.goto(deepLinkA, {waitUntil: 'networkidle'});
  // A fragment-only goto may stay in the current document; reload explicitly
  // before asserting the initial opt-in state of a newly opened deep link.
  await page.reload({waitUntil: 'networkidle'});
  check('fresh_document_deep_link_opens_correct_source_and_leaves_P03_opt_in',
    await page.locator('#detail').isVisible()
    && (await page.locator('#detail-content > h3').first().textContent()) === runA.name
    && await tables().count() === 0);
  await selectAll();
  await runControl('run-select', sourceA, runA).check();
  const staleURL = page.url();
  await writeFile(args.metadata, await readFile(args.replacement));
  const stale = await model();
  check('valid_package_replacement_marks_changed_but_keeps_old_snapshot_until_reindex',
    stale.sources[0].status === 'CHANGED' && stale.sources[0].read_model.runs[0].id === runA.id
    && stale.sources[1].status === 'READY');
  await Promise.all([
    page.waitForResponse(response => new URL(response.url()).pathname === '/api/reindex'
      && response.request().method() === 'POST' && response.status() === 200),
    page.locator('#refresh').click(),
  ]);
  const fresh = await model();
  // C0 deliberately leaves a rejected old URL visible with an explanation.
  // Wait for the rendered snapshot rather than requiring URL canonicalization.
  await page.waitForFunction(expected => document.querySelector('#snapshot-id')?.textContent === expected, fresh.snapshot_id);
  check('new_snapshot_discards_old_C0_and_P03_detail_selection_with_visible_notice',
    fresh.snapshot_id !== initial.snapshot_id && !await page.locator('#detail').isVisible()
    && await page.locator('#run-rows input:checked').count() === 0
    && (await page.locator('#notice').innerText()).includes('descartados'));
  await page.goto(staleURL, {waitUntil: 'networkidle'});
  check('old_deep_link_never_retargets_repeated_run_in_other_source',
    !await page.locator('#detail').isVisible() && (await page.locator('#notice').innerText()).length > 20);
  await open(fresh.sources[1], fresh.sources[1].read_model.runs.find(run => run.id === runB.id));
  check('reindex_expires_all_prior_P03_choices_in_the_unchanged_other_source',
    await choices().evaluateAll(nodes => nodes.every(node => !node.checked))
    && await tables().count() === 0);
  const replacementRun = fresh.sources[0].read_model.runs.find(run => run.id.endsWith('run:00'));
  await open(fresh.sources[0], replacementRun);
  check('metadata_presentation_error_is_visible_while_protocol_source_remains_READY',
    fresh.sources[0].report.valid === true && fresh.sources[0].status === 'READY'
    && fresh.sources[0].presentation.errors.some(error => error.code === 'LIMIT')
    && (await page.locator('#detail [data-testid="p03-presentation-error"]').innerText()).includes('LIMIT')
    && await choices().count() >= 6);
  await screenshot('c4-visible-presentation-error');
  check('no_external_request_browser_exception_or_console_error',
    receipt.external_requests.length === 0 && receipt.page_errors.length === 0 && receipt.console_errors.length === 0);
  receipt.status = 'PASS';
} catch (error) {
  receipt.error = error.stack || String(error);
} finally {
  if (browser) await browser.close();
  await mkdir(path.dirname(args.report), {recursive: true});
  await writeFile(args.report, JSON.stringify(receipt, null, 2) + '\n');
  process.stdout.write('C4_BROWSER_SUMMARY=' + JSON.stringify(receipt) + '\n');
}
process.exitCode = receipt.status === 'PASS' ? 0 : 1;

