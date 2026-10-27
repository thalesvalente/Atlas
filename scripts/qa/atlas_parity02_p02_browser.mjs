/** Explicit C0 browser proof over the live installed viewer and public P02 fixtures.
 * This script is NOT connected automatically to CI. P06 owns that integration.
 * No CSS zoom is used; native browser zoom remains a separately reported gap.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';

const args = new Map();
for (let index = 2; index < process.argv.length; index += 2) args.set(process.argv[index], process.argv[index + 1]);
const url = args.get('--url'), reportPath = args.get('--report');
if (!url || !reportPath) throw new Error('Required: --url LOOPBACK_URL --report JSON [--screenshots DIR --code-sha SHA]');
const parsed = new URL(url);
assert.ok(['127.0.0.1', 'localhost'].includes(parsed.hostname) && parsed.protocol === 'http:' && !parsed.username && !parsed.password,
  'Only an explicitly supplied HTTP loopback viewer is supported');
const origin = parsed.origin;
const checks = [], screenshots = [], externalRequests = [], pageErrors = [];
const report = {kind: 'ATLAS_PARITY02_P02_BROWSER', status: 'NOT_RUN', scope: 'public-synthetic-installed-viewer',
  code_sha: args.get('--code-sha') || 'UNSPECIFIED', checks, screenshots, external_requests: externalRequests,
  page_errors: pageErrors, native_zoom: 'NOT_RUN', css_zoom_used: false, wcag_certification: false};
let browser, context, page;
const mark = name => checks.push({name, status: 'PASS'});
const screenshotDir = args.get('--screenshots') || path.join(path.dirname(reportPath), 'p02-screenshots');
async function shot(name, {fullPage = true} = {}) {
  await fs.mkdir(screenshotDir, {recursive: true});
  const filename = name + '.png';
  await page.screenshot({path: path.join(screenshotDir, filename), fullPage});
  screenshots.push(filename);
}
async function countIs(expected) {
  await page.waitForFunction(n => document.querySelectorAll('#run-rows tr').length === n, expected);
  assert.equal(await page.locator('#run-rows tr').count(), expected);
}
async function noPageOverflow() {
  const measurement = await page.evaluate(() => ({width: innerWidth,
    root: document.documentElement.scrollWidth, body: document.body.scrollWidth}));
  assert.ok(measurement.root <= measurement.width + 1, JSON.stringify(measurement));
  assert.ok(measurement.body <= measurement.width + 1, JSON.stringify(measurement));
}
async function clearFilters() {await page.locator('[data-view="explore"]').click(); await page.locator('#clear-filters').click();}
async function openRun(run) {await page.getByRole('button', {name: run.name, exact: true}).first().click();}
function route(catalog, {view = 'explore', run, selected = [], ...filters} = {}) {
  const params = new URLSearchParams({v: '1', scope: catalog.snapshot_id, view, ...filters});
  if (run) params.set('run', JSON.stringify([run._sourceId, run.id]));
  if (selected.length) params.set('selected', JSON.stringify(selected.map(r => JSON.stringify([r._sourceId, r.id]))));
  return '#' + params.toString();
}
try {
  const require = createRequire(import.meta.url);
  let playwright;
  try {playwright = require('playwright');}
  catch {playwright = require(require.resolve('playwright', {paths: [process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES].filter(Boolean)}));}
  try {
    browser = await playwright.chromium.launch({headless: true,
      ...(process.env.ATLAS_BROWSER_BINARY ? {executablePath: process.env.ATLAS_BROWSER_BINARY} : {})});
  } catch (error) {
    report.blocker = /Executable doesn't exist|executable.*not found/i.test(error.message)
      ? 'BROWSER_EXECUTABLE_MISSING' : 'BROWSER_LAUNCH_FAILED';
    throw new Error(report.blocker + ': Chromium não pôde ser iniciado no runtime de engenharia.');
  }
  report.status = 'FAIL';
  report.browser_version = browser.version();
  context = await browser.newContext({viewport: {width: 1440, height: 1000}});
  await context.route('**/*', async request => {
    const target = request.request().url();
    if (/^https?:/.test(target) && new URL(target).origin !== origin) {
      externalRequests.push(target);
      await request.abort();
    } else await request.continue();
  });
  page = await context.newPage();
  page.on('pageerror', error => pageErrors.push(error.message));
  const response = await page.goto(url, {waitUntil: 'networkidle'});
  assert.equal(response.status(), 200);
  assert.ok(response.headers()['content-security-policy'].includes("default-src 'none'"));
  const api = await page.request.get(origin + '/api/catalog');
  assert.equal(api.status(), 200);
  const catalog = await api.json();
  const runs = catalog.sources.flatMap(source => (source.read_model?.runs || []).map(run => ({...run, _sourceId: source.id, _sourceName: source.name})));
  assert.equal(catalog.sources.length, 2);
  assert.equal(runs.length, 28);
  assert.ok(runs.every(run => run.synthetic === true));
  report.source_count = 2; report.run_count = 28;
  const run = (source, suffix) => runs.find(r => r._sourceId === source && r.id.endsWith('run:' + suffix));
  await countIs(28);
  mark('two_public_synthetic_sources_and_28_runs');
  await page.evaluate(() => window.scrollTo(0, 0));
  await shot('c0-overview-1440', {fullPage: false});

  assert.ok((await page.locator('#snapshot-id').textContent()).includes(catalog.snapshot_id));
  assert.ok(/não informad[oa]/.test((await page.locator('#scope-summary').innerText()).toLocaleLowerCase('pt-BR')));
  await page.locator('[data-view="sources"]').click();
  const coverageText = (await page.locator('#sources-content').innerText()).toLocaleLowerCase('pt-BR');
  for (const term of ['elegíve', 'selecionado', 'convertido', 'não informado']) assert.ok(coverageText.includes(term), term);
  mark('loaded_scope_snapshot_and_unknown_coverage_are_separate');
  await clearFilters();

  await page.locator('#source-filter').selectOption('source-2'); await countIs(14);
  await page.locator('#search').fill('run:00'); await countIs(1);
  await openRun(run('source-2', '00'));
  assert.ok(await page.locator('#detail').isVisible());
  assert.ok((await page.locator('#detail').innerText()).includes('Nota da fonte B'));
  assert.ok(!(await page.locator('#detail').innerText()).includes('Nota da fonte A'));
  assert.ok(new URL(page.url()).hash.includes('run='));
  mark('source_scoped_detail_and_hash_keep_duplicate_ids_distinct');
  await page.goBack();
  assert.ok(await page.locator('#detail').isHidden());
  assert.equal(await page.locator('#source-filter').inputValue(), 'source-2');
  assert.equal(await page.locator('#search').inputValue(), 'run:00');
  await page.goForward();
  assert.ok(await page.locator('#detail').isVisible());
  await page.reload({waitUntil: 'networkidle'});
  assert.ok(await page.locator('#detail').isVisible());
  assert.ok((await page.locator('#detail').innerText()).includes('Nota da fonte B'));
  await page.locator('#close-detail').click();
  assert.ok(await page.locator('#detail').isHidden());
  assert.equal(await page.locator('#source-filter').inputValue(), 'source-2');
  assert.equal(await page.locator('#search').inputValue(), 'run:00');
  mark('back_forward_reload_and_close_preserve_context');

  await page.goto(origin + route(catalog, {run: run('source-2', '00')}), {waitUntil: 'networkidle'});
  await page.locator('#detail').getByRole('button', {name: run('source-2', '01').name, exact: true}).click();
  assert.ok((await page.locator('#detail').innerText()).includes(run('source-2', '01').name));
  assert.ok((await page.locator('#detail').innerText()).includes('Coorte sintética — fonte B'));
  await page.goBack();
  assert.ok((await page.locator('#detail').innerText()).includes('Nota da fonte B'));
  assert.ok(!(await page.locator('#detail').innerText()).includes('Nota da fonte A'));
  mark('neutral_reference_navigation_and_back_remain_in_the_same_source');

  await clearFilters();
  await page.locator('#search').fill('fonte B'); await countIs(14);
  await page.locator('#search').fill('日本語'); await countIs(2);
  await page.locator('#clear-filters').click();
  for (const [selector, field, value] of [['#review-filter', 'review_status', 'HOLD'], ['#status-filter', 'status', 'UNKNOWN']]) {
    await page.locator(selector).selectOption(value);
    await countIs(runs.filter(r => r[field] === value).length);
    await page.locator('#clear-filters').click();
  }
  for (const [selector, field] of [['#metrics-filter', 'metrics'], ['#references-filter', 'related_references']]) {
    for (const value of ['yes', 'no']) {
      await page.locator(selector).selectOption(value);
      await countIs(runs.filter(r => value === 'yes' ? r[field].length > 0 : r[field].length === 0).length);
    }
    await page.locator('#clear-filters').click();
  }
  mark('source_review_state_presence_and_unicode_filters');
  for (const order of ['title', 'id', 'source', 'status', 'review', 'time-asc', 'time-desc']) {
    await page.locator('#sort-order').selectOption(order);
    const firstOrder = await page.getByTestId('run-open').allTextContents();
    await page.reload({waitUntil: 'networkidle'});
    assert.deepEqual(await page.getByTestId('run-open').allTextContents(), firstOrder, order);
  }
  mark('all_sort_orders_survive_reload');

  await clearFilters();
  if (await page.locator('#clear-selection').isEnabled()) await page.locator('#clear-selection').click();
  for (const selected of [run('source-1', '00'), run('source-2', '00')]) {
    const row = page.locator('#run-rows tr').filter({has: page.getByRole('button', {name: selected.name, exact: true})});
    await row.locator('input[type="checkbox"]').check();
  }
  await page.locator('#search').fill('not-a-matching-synthetic-record'); await countIs(0);
  assert.ok((await page.locator('#selected-count').innerText()).includes('2'));
  assert.ok(await page.locator('#empty').isVisible());
  assert.ok((await page.locator('#empty-reason').innerText()).length > 20);
  await page.locator('#compare-selected').click();
  for (const selected of [run('source-1', '00'), run('source-2', '00')]) assert.ok((await page.locator('#compare-content').innerText()).includes(selected.name));
  await page.reload({waitUntil: 'networkidle'});
  assert.ok(await page.locator('#view-compare').isVisible());
  assert.ok((await page.locator('#selected-count').innerText()).includes('2'));
  mark('comparison_selection_persists_across_hidden_filters_and_reload');

  await page.goto(origin + route(catalog, {view: 'compare', selected: [run('source-1', '00'), run('source-1', '01'), run('source-1', '02')]}), {waitUntil: 'networkidle'});
  const comparison = await page.locator('#compare-content').innerText();
  assert.ok(comparison.toLowerCase().includes('incompat'));
  for (const term of ['mg/L', 'µg/L', 'number', 'integer']) assert.ok(comparison.includes(term));
  assert.ok(comparison.toLocaleLowerCase('pt-BR').includes('precisão'));
  mark('incompatible_metrics_keep_types_units_and_declared_precision_without_ranking');

  await page.goto(origin + route(catalog, {run: run('source-1', '00')}), {waitUntil: 'networkidle'});
  const detail = await page.locator('#detail').innerText();
  for (const value of ['COMPLETED', 'UNKNOWN', 'data/input.csv', 'data/output.csv', 'DECLARED', 'Referências relacionadas']) assert.ok(detail.includes(value), value);
  assert.ok(detail.toLocaleLowerCase('pt-BR').includes('entrada'));
  assert.ok(detail.toLocaleLowerCase('pt-BR').includes('saída'));
  assert.ok(detail.includes('EXTERNAL_UNRESOLVED') && detail.includes('MISSING'));
  assert.equal(await page.locator('#detail img,#detail script,#run-rows img,#run-rows script').count(), 0);
  assert.equal(await page.evaluate(() => window.__atlasP02QA), undefined);
  assert.equal(await page.locator('a[href^="javascript:"],a[href^="file:"],a[href^="https://example.invalid"]').count(), 0);
  mark('detail_preserves_direction_availability_mentions_and_inert_adversarial_content');
  await page.goto(origin + route(catalog, {run: run('source-1', '12')}), {waitUntil: 'networkidle'});
  assert.ok((await page.locator('#detail').innerText()).includes('9007199254740993'));
  mark('declared_precision_exceeding_js_integer_range_is_exact_text');

  await page.goto(origin + route(catalog, {view: 'timeline'}), {waitUntil: 'networkidle'});
  assert.equal(await page.locator('#timeline-content li').count(), 28);
  assert.ok((await page.locator('#timeline-content').innerText()).includes('OBSERVED'));
  const endOnly = page.locator('#timeline-content li').filter({has: page.getByRole('button', {name: run('source-1', '10').name, exact: true})});
  assert.ok((await endOnly.innerText()).includes('2026-10-11T10:05:00-03:00'));
  assert.ok((await endOnly.innerText()).includes('Sem início declarado'));
  assert.ok(!(await endOnly.innerText()).includes('Sem data declarada'));
  mark('end_only_timestamp_is_visible_without_inventing_start');
  await openRun(run('source-1', '08'));
  assert.ok(await page.locator('#detail').isVisible());
  assert.ok((await page.locator('#detail').innerText()).includes('UNKNOWN'));
  await page.keyboard.press('Escape');
  assert.ok(await page.locator('#detail').isHidden());
  assert.deepEqual(await page.evaluate(() => ({tag: document.activeElement?.tagName,
    name: document.activeElement?.textContent, visible: !!document.activeElement?.getClientRects().length})),
    {tag: 'BUTTON', name: run('source-1', '08').name, visible: true});
  await page.locator('[data-view="lineage"]').click();
  await openRun(run('source-1', '08'));
  assert.ok(await page.locator('#detail').isVisible());
  mark('undated_and_unrelated_runs_remain_reachable_from_time_and_relations');

  const stale = new URLSearchParams(route(catalog, {run: run('source-1', '00'), selected: [run('source-1', '00')], source: 'source-1'}).slice(1));
  stale.set('scope', '0'.repeat(64));
  await page.goto(origin + '/#' + stale, {waitUntil: 'networkidle'});
  assert.ok(await page.locator('#detail').isHidden());
  assert.ok((await page.locator('#notice').innerText()).length > 30);
  assert.equal(await page.locator('#source-filter').inputValue(), '');
  assert.equal(await page.locator('#run-rows input:checked').count(), 0);
  mark('stale_snapshot_never_retargets_entity_or_selection');
  const missing = route(catalog, {run: {...run('source-1', '00'), id: 'urn:synthetic:missing'}});
  await page.goto(origin + '/' + missing, {waitUntil: 'networkidle'});
  assert.ok(await page.locator('#detail').isHidden());
  await page.goto(origin + '/#q=%ZZ', {waitUntil: 'networkidle'});
  assert.ok(await page.locator('#detail').isHidden());
  assert.ok((await page.locator('#notice').innerText()).length > 20);
  mark('missing_entity_and_malformed_url_have_explanatory_safe_fallback');

  await page.goto(origin + route(catalog), {waitUntil: 'networkidle'});
  const contrast = await page.locator('label,.muted,.stats small,.footer,.run-open,.badge,.nav-button,.notice,.button,.text-button').evaluateAll(nodes => {
    const rgba = value => {const values = value.match(/[\d.]+/g)?.map(Number); return values && values.length >= 3 ? [...values.slice(0, 3), values[3] ?? 1] : null;};
    const luminance = rgb => rgb.slice(0, 3).map(c => c / 255).map(c => c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4)
      .reduce((value, c, i) => value + c * [.2126, .7152, .0722][i], 0);
    return nodes.filter(node => node.getClientRects().length && !node.disabled && node.textContent.trim()).map(node => {
      const style = getComputedStyle(node), foreground = rgba(style.color);
      let background = [255, 255, 255, 1], cursor = node;
      while (cursor) {
        const candidate = rgba(getComputedStyle(cursor).backgroundColor);
        if (candidate && candidate[3] === 1) {background = candidate; break;}
        cursor = cursor.parentElement;
      }
      if (!foreground || foreground[3] !== 1) return null;
      const values = [luminance(foreground), luminance(background)].sort((a, b) => b - a);
      const size = parseFloat(style.fontSize), weight = parseInt(style.fontWeight, 10);
      return {selector: node.id ? '#' + node.id : '.' + String(node.className).split(' ').join('.'),
        ratio: (values[0] + .05) / (values[1] + .05), minimum: size >= 24 || size >= 18.66 && weight >= 700 ? 3 : 4.5};
    }).filter(Boolean);
  });
  report.solid_color_contrast_samples = contrast;
  assert.ok(contrast.length > 10);
  const insufficient = contrast.filter(sample => sample.ratio + .001 < sample.minimum);
  assert.equal(insufficient.length, 0, JSON.stringify(insufficient));
  mark('sampled_visible_solid_color_text_meets_contrast_threshold');
  // Hash navigation preserves the browser's sequential-focus starting point.
  // Start the skip-link proof in a new document, as a new keyboard user would.
  await page.close();
  page = await context.newPage();
  page.on('pageerror', error => pageErrors.push(error.message));
  await page.goto(origin + route(catalog), {waitUntil: 'networkidle'});
  await countIs(28);
  await page.keyboard.press('Tab');
  assert.ok(await page.evaluate(() => document.activeElement?.matches('a.skip')),
    'The first Tab in a new document must reach the visible skip link');
  assert.ok(await page.locator('a.skip').isVisible());
  const focus = await page.evaluate(() => {const style = getComputedStyle(document.activeElement); return {outline: style.outlineStyle, width: style.outlineWidth};});
  assert.notEqual(focus.outline, 'none'); assert.notEqual(focus.width, '0px');
  await page.keyboard.press('Enter');
  assert.equal(await page.evaluate(() => document.activeElement?.id), 'main');
  mark('first_tab_reaches_visible_skip_link_and_enter_focuses_main');
  await page.locator('#search').focus(); await page.keyboard.type('run:08'); await countIs(2);
  const keyboardRunName = await page.getByTestId('run-open').first().textContent();
  await page.getByTestId('run-open').first().focus(); await page.keyboard.press('Enter');
  assert.ok(await page.locator('#detail').isVisible());
  await page.locator('#close-detail').focus(); await page.keyboard.press('Enter');
  assert.ok(await page.locator('#detail').isHidden());
  assert.deepEqual(await page.evaluate(() => ({kind: document.activeElement?.dataset.testid,
    name: document.activeElement?.textContent})), {kind: 'run-open', name: keyboardRunName});
  mark('keyboard_navigation_search_open_close_and_visible_focus');

  await page.goto(origin + route(catalog, {run: run('source-1', '06')}), {waitUntil: 'networkidle'});
  for (const width of [1440, 390, 320]) {
    await page.setViewportSize({width, height: 1000});
    await noPageOverflow();
    const regions = await page.locator('.table-wrap').evaluateAll(nodes => nodes.map(n => ({overflow: getComputedStyle(n).overflowX, width: n.clientWidth, scroll: n.scrollWidth})));
    assert.ok(regions.every(r => r.scroll <= r.width + 1 || ['auto', 'scroll'].includes(r.overflow)));
    await shot('c0-' + width);
    if (width === 390) {
      await page.locator('#detail').scrollIntoViewIfNeeded();
      await page.locator('#detail').evaluate(element => element.scrollIntoView({block: 'start'}));
      await shot('c0-detail-390', {fullPage: false});
    }
    mark('document_reflow_and_scoped_tables_' + width + '_css_px');
  }
  // Simulate the standard spacing overrides as a separate narrow-view proof.
  // This is not native zoom and does not assert full WCAG conformance.
  await page.evaluate(() => {
    for (const element of document.querySelectorAll('*')) {
      element.style.setProperty('line-height', '1.5', 'important');
      element.style.setProperty('letter-spacing', '.12em', 'important');
      element.style.setProperty('word-spacing', '.16em', 'important');
      if (element.tagName === 'P') element.style.setProperty('margin-bottom', '2em', 'important');
    }
  });
  await noPageOverflow();
  assert.ok(await page.locator('#close-detail').isVisible());
  await shot('c0-320-text-spacing');
  mark('text_spacing_does_not_overflow_page_or_hide_close_control');
  assert.equal(externalRequests.length, 0, 'No external request attempt is allowed');
  assert.equal(pageErrors.length, 0, 'No browser page errors are allowed');
  mark('no_external_requests_or_browser_errors');
  report.status = 'PASS_SCOPED';
} catch (error) {
  report.error = error.message;
  if (browser) report.status = 'FAIL';
  else report.status = 'NOT_RUN';
} finally {
  if (browser) await browser.close();
  await fs.mkdir(path.dirname(reportPath), {recursive: true});
  await fs.writeFile(reportPath, JSON.stringify(report, null, 2) + '\n');
  process.stdout.write(JSON.stringify({status: report.status, checks: checks.length, screenshots: screenshots.length,
    native_zoom: report.native_zoom, error: report.error || null}) + '\n');
}
if (report.status !== 'PASS_SCOPED') process.exitCode = report.status === 'NOT_RUN' ? 2 : 1;
