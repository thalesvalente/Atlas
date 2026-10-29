/** Real Chromium gate for the C2 synthetic P03 harness; no browser downloads. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {existsSync, mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync, spawn} from 'node:child_process';
import {createInterface} from 'node:readline';

const require = createRequire(import.meta.url);
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const argumentsList = process.argv.slice(2);
if (argumentsList.length !== 2 || argumentsList[0] !== '--output-dir') {
  throw new Error('Usage: node scripts/qa/atlas_parity03_p03_browser.mjs --output-dir DIRECTORY');
}
const output = path.resolve(argumentsList[1]);
mkdirSync(output, {recursive:true});
const git = (...args) => execFileSync('git', args, {cwd:root, encoding:'utf8'}).trim();
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const freezePath = 'docs/missions/atlas-parity-02/p03-components/evidence/FREEZE.json';
const frozenFiles = JSON.parse(readFileSync(path.join(root, freezePath), 'utf8')).files;
const hashFrozen = () => Object.fromEntries(frozenFiles.map(entry =>
  [entry.path, sha256(readFileSync(path.join(root, entry.path)))]));
const sourcePaths = [...frozenFiles.map(entry => entry.path),
  'scripts/qa/atlas_parity03_p03_browser.mjs',
  'scripts/qa/atlas_parity03_p03_harness.py',
  'scripts/qa/atlas_parity03_p03_harness.css'];
const report = {
  schema:'atlas-parity03-p03-browser-receipt/1',
  scope:'P03_ISOLATED_SYNTHETIC_HARNESS',
  status:'NOT_RUN',
  tested_head:git('rev-parse', 'HEAD'),
  tested_tree:git('rev-parse', 'HEAD^{tree}'),
  actions_run_id:process.env.GITHUB_RUN_ID || null,
  actions_run_attempt:process.env.GITHUB_RUN_ATTEMPT || null,
  platform:process.platform,
  node_version:process.version,
  visible_in_main_app:false,
  main_server_assets_qualified:false,
  synthetic:true,
  checks:[],
  skipped:0,
  screenshots:[],
  page_errors:[],
  console_errors:[],
  external_requests:[],
  websocket_attempts:[],
  unexpected_local_requests:[],
  requests:[],
  network_observation_scope:'All requests and WebSocket attempts in the Playwright browser context, with service workers blocked. Chromium background process traffic is not measured by this receipt.',
  browser_zoom_200:{
    status:'NOT_RUN',
    reason:'The installed-browser Playwright page API does not expose a verified native browser zoom control. No extension or browser-UI controller is installed by this gate.',
    css_zoom_used:false,
    device_scale_factor_used_as_zoom:false,
    cdp_page_scale_used_as_zoom:false,
    minimum_next_act:'Run a native browser UI/zoom controller on this exact SHA and record the browser zoom setting and the viewport transformation at 200 percent.'
  },
  embedding:{
    stylesheet:'scripts/qa/atlas_parity03_p03_harness.css',
    table_max_block_size:'min(60vh, 28rem)',
    scope:'Explicit focal host constraint; does not qualify the main shell.'
  }
};
let browser;
let server;
let context;
let page;
let serverStderr = '';
let before;

async function check(name, run) {
  const entry = {name, status:'RUNNING'};
  report.checks.push(entry);
  try {
    const evidence = await run();
    if (evidence !== undefined) entry.evidence = evidence;
    entry.status = 'PASS';
  } catch (error) {
    entry.status = 'FAIL';
    entry.error = String(error.message);
    throw error;
  }
}

async function screenshot(name) {
  const filename = `p03-${name}.png`;
  await page.screenshot({path:path.join(output, filename), fullPage:true});
  report.screenshots.push({path:filename, sha256:sha256(readFileSync(path.join(output, filename)))});
}

async function startHarness() {
  server = spawn(process.env.P03_PYTHON || 'python',
    [path.join(root, 'scripts/qa/atlas_parity03_p03_harness.py'), '--port', '0', '--json'],
    {cwd:root, stdio:['ignore','pipe','pipe']});
  server.stderr.on('data', value => { serverStderr = (serverStderr + value.toString()).slice(-8000); });
  const lines = createInterface({input:server.stdout});
  return new Promise((resolve, reject) => {
    const timeout = setTimeout(() => done(new Error('HARNESS_START_TIMEOUT')), 15000);
    let settled = false;
    const done = (error, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timeout);
      lines.close();
      if (error) reject(error); else resolve(value);
    };
    lines.once('line', line => {
      try {
        const value = JSON.parse(line);
        assert.equal(value.synthetic, true);
        assert.equal(value.visible_in_main_app, false);
        const url = new URL(value.url);
        assert.equal(url.protocol, 'http:');
        assert.equal(url.hostname, '127.0.0.1');
        assert.ok(url.port);
        done(null, url.origin);
      } catch (error) { done(error); }
    });
    server.once('error', error => done(error));
    server.once('exit', code => done(new Error(`HARNESS_EARLY_EXIT:${code}`)));
  });
}

async function restoreTable() {
  await page.selectOption('#example', 'table');
  await page.selectOption('#order', 'declared');
  await page.uncheck('#missing');
}

async function geometry() {
  return page.evaluate(() => {
    const region = document.querySelector('#table-mount [role="region"]');
    const bounds = region.getBoundingClientRect();
    const style = getComputedStyle(region);
    return {
      inner_width:innerWidth,
      document_client_width:document.documentElement.clientWidth,
      document_scroll_width:document.documentElement.scrollWidth,
      body_scroll_width:document.body.scrollWidth,
      region_left:bounds.left,
      region_right:bounds.right,
      region_client_width:region.clientWidth,
      region_scroll_width:region.scrollWidth,
      region_client_height:region.clientHeight,
      region_scroll_height:region.scrollHeight,
      overflow_x:style.overflowX,
      overflow_y:style.overflowY,
      tabindex:region.tabIndex,
      css_zoom:getComputedStyle(document.documentElement).zoom,
      outer_horizontal_overflows:[...document.querySelectorAll('body *')]
        .filter(element => !element.closest('#table-mount [role="region"]'))
        .filter(element => element.clientWidth > 0 && element.scrollWidth > element.clientWidth + 2)
        .map(element => ({tag:element.tagName, id:element.id, class_name:element.className,
          client_width:element.clientWidth, scroll_width:element.scrollWidth}))
    };
  });
}

function contained(shape, width) {
  assert.equal(shape.inner_width, width);
  assert.ok(shape.document_scroll_width <= shape.document_client_width + 1, JSON.stringify(shape));
  assert.ok(shape.body_scroll_width <= shape.document_client_width + 1, JSON.stringify(shape));
  assert.ok(shape.region_left >= -1 && shape.region_right <= width + 1, JSON.stringify(shape));
  assert.equal(shape.overflow_x, 'auto');
  assert.equal(shape.overflow_y, 'auto');
  assert.equal(shape.tabindex, 0);
  assert.deepEqual(shape.outer_horizontal_overflows, []);
  assert.ok(['1','normal'].includes(shape.css_zoom));
}

async function main() {
  let playwright;
  try { playwright = require('playwright'); }
  catch {
    const modules = process.env.CODEX_PRIMARY_RUNTIME_NODE_MODULES;
    if (modules) { try { playwright = require(path.join(modules, 'playwright')); } catch {} }
  }
  if (!playwright) { report.reason = 'PLAYWRIGHT_NOT_AVAILABLE'; return 2; }
  const executable = process.env.P03_BROWSER_EXECUTABLE || playwright.chromium.executablePath();
  if (!existsSync(executable)) { report.reason = 'CHROMIUM_EXECUTABLE_NOT_AVAILABLE'; return 2; }
  report.browser_executable = executable;
  try {
    await check('frozen_inputs_and_exact_git_binding', async () => {
      before = hashFrozen();
      assert.equal(frozenFiles.length, 25);
      for (const entry of frozenFiles) assert.equal(before[entry.path], entry.sha256, entry.path);
      report.input_hashes = Object.fromEntries(sourcePaths.map(filename => {
        const bytes = readFileSync(path.join(root, filename));
        assert.deepEqual(bytes, execFileSync('git', ['show', `${report.tested_head}:${filename}`], {cwd:root}), filename);
        return [filename, sha256(bytes)];
      }));
      return {frozen_files:25, exact_git_bytes:true};
    });
    browser = await playwright.chromium.launch({headless:true, executablePath:executable, chromiumSandbox:true});
    report.browser_version = browser.version();
    const origin = await startHarness();
    report.harness_origin = origin;
    context = await browser.newContext({viewport:{width:1440, height:1000}, serviceWorkers:'block'});
    const allowed = new Set(['/', '/harness.mjs', '/harness.css', '/demo-data.js',
      '/parity02_p03_table.js', '/parity02_p03_artifacts.js',
      '/parity02_p03_table.css', '/parity02_p03_artifacts.css']);
    await context.route('**/*', route => {
      const request = route.request();
      const url = new URL(request.url());
      report.requests.push({url:request.url(), method:request.method(), type:request.resourceType()});
      if (url.origin !== origin) {
        report.external_requests.push(request.url());
        return route.abort('blockedbyclient');
      }
      if (!allowed.has(url.pathname) || url.search || request.method() !== 'GET') {
        report.unexpected_local_requests.push(request.url());
        return route.abort('blockedbyclient');
      }
      return route.continue();
    });
    await context.routeWebSocket('**/*', socket => {
      report.websocket_attempts.push(socket.url());
      socket.close();
    });
    page = await context.newPage();
    page.setDefaultTimeout(15000);
    page.on('pageerror', error => report.page_errors.push(String(error.message)));
    page.on('console', message => {
      if (message.type() === 'error') report.console_errors.push(message.text());
    });
    const initialResponse = await page.goto(origin, {waitUntil:'networkidle'});
    report.content_security_policy = initialResponse.headers()['content-security-policy'];
    await page.waitForSelector('html[data-p03-ready="true"]');

    await check('semantic_table_headers_caption_and_row_identity', async () => {
      assert.equal(await page.locator('#table-mount table').count(), 1);
      assert.equal(await page.locator('#table-mount table > caption').count(), 1);
      assert.equal(await page.locator('#table-mount thead th[scope="col"]').count(), 6);
      assert.equal(await page.locator('#table-mount tbody th[scope="row"]').count(), 4);
      const identities = await page.locator('#table-mount tbody tr').evaluateAll(rows =>
        rows.map(row => ({id:row.dataset.rowId, heading:row.querySelector('th').textContent})));
      assert.deepEqual(identities.map(entry => entry.id), ['amostra-A','amostra-B','amostra-C','amostra-Ausente']);
      assert.ok(identities.every(entry => entry.id === entry.heading));
      return identities;
    });
    await check('typed_transport_exact_numeric_strings_and_real_booleans', async () => {
      const transport = await page.evaluate(async () => {
        const {default:data} = await import('/demo-data.js');
        return data.table.rows.map(row => ({id:row.id, cells:row.cells,
          types:Object.fromEntries(Object.entries(row.cells).map(([key,value]) => [key, value === null ? 'null' : typeof value]))}));
      });
      assert.equal(transport[0].types.count, 'string');
      assert.equal(transport[0].cells.count, '9007199254740993');
      assert.equal(transport[0].cells.measure, '0.123456789012345678901');
      assert.equal(transport[0].cells.code, '00042');
      assert.equal(transport[0].types.flag, 'boolean');
      assert.equal(transport[0].cells.flag, false);
      assert.equal(transport[1].cells.flag, true);
      assert.equal(transport[1].cells.count, '09007199254740992');
      assert.equal(transport[1].cells.measure, '+001.2300e+2');
      const rows = await page.locator('#table-mount tbody tr').evaluateAll(items =>
        items.map(row => [...row.querySelectorAll('td')].map(cell => cell.textContent)));
      assert.deepEqual(rows[0], ['São Luís / 水 / 🌱','9007199254740993','0.123456789012345678901','false','00042']);
      assert.deepEqual(rows[1], ['Controle','09007199254740992','+001.2300e+2','true','0007']);
      assert.deepEqual(rows[2], ['Zero preservado','0','-0.000','false','-0']);
      return transport;
    });
    await check('null_omission_missing_reason_and_empty_string_are_distinct', async () => {
      const values = await page.locator('#table-mount [data-row-id="amostra-Ausente"] td').allTextContents();
      assert.deepEqual(values, ['Ausência explícita','Não informado — Não medido',
        'Não informado — Fonte não declarou','Não informado — Sem declaração','']);
      assert.equal(await page.locator('#table-mount [data-row-id="amostra-Ausente"] td.atlas-p03-table__missing').count(), 3);
      return values;
    });
    await check('column_types_units_precision_are_visible_without_rounding', async () => {
      const headers = await page.locator('#table-mount thead th').allTextContents();
      assert.match(headers[2], /Tipo: integer.*Unidade: 1.*Precisão declarada: 0/);
      assert.match(headers[3], /Tipo: decimal.*Unidade: mg\/L.*Precisão declarada: 2/);
      assert.match(headers[4], /Tipo: boolean/);
      assert.ok((await page.locator('#table-mount tbody').innerText()).includes('0.123456789012345678901'));
      return headers;
    });
    await check('typed_sort_control_identity_and_aria_sort', async () => {
      await page.selectOption('#order', 'asc');
      const asc = await page.locator('#table-mount tbody tr').evaluateAll(rows => rows.map(row => row.dataset.rowId));
      assert.deepEqual(asc, ['amostra-C','amostra-B','amostra-A','amostra-Ausente']);
      assert.equal(await page.locator('#table-mount th[aria-sort="ascending"]').count(), 1);
      await page.selectOption('#order', 'desc');
      const desc = await page.locator('#table-mount tbody tr').evaluateAll(rows => rows.map(row => row.dataset.rowId));
      assert.deepEqual(desc, ['amostra-A','amostra-B','amostra-C','amostra-Ausente']);
      assert.equal(await page.locator('#table-mount th[aria-sort="descending"]').count(), 1);
      await page.check('#missing');
      assert.equal(await page.locator('#table-mount tbody th').textContent(), 'amostra-Ausente');
      await restoreTable();
      return {asc, desc};
    });
    await check('typed_filters_stability_and_source_objects_preserved_in_browser', async () => {
      const result = await page.evaluate(async () => {
        const {default:data} = await import('/demo-data.js');
        const {renderTable, filterRows, sortRows} = await import('/parity02_p03_table.js');
        const descriptor = data.table;
        const before = JSON.stringify(descriptor);
        const cases = [
          [{columnId:'count',operator:'gt',value:'9007199254740992'}, ['amostra-A']],
          [{columnId:'measure',operator:'lt',value:'0.1'}, ['amostra-C']],
          [{columnId:'measure',operator:'eq',value:'123'}, ['amostra-B']],
          [{columnId:'flag',operator:'eq',value:false}, ['amostra-A','amostra-C']],
          [{columnId:'flag',operator:'eq',value:true}, ['amostra-B']],
          [{columnId:'code',operator:'eq',value:'00042'}, ['amostra-A']],
          [{columnId:'measure',operator:'is_missing'}, ['amostra-Ausente']],
          [{columnId:'measure',operator:'is_present'}, ['amostra-A','amostra-B','amostra-C']]
        ];
        const results = cases.map(([filter,expected]) => {
          const rows = filterRows(descriptor, filter);
          const rendered = renderTable(document, descriptor, {filter});
          document.getElementById('table-mount').replaceChildren(rendered);
          return {filter, expected, actual:rows.map(row => row.id),
            rendered:[...rendered.querySelectorAll('tbody tr')].map(row => row.dataset.rowId),
            same_objects:rows.every(row => descriptor.rows.includes(row))};
        });
        const boolOrder = sortRows(descriptor, 'flag').map(row => row.id);
        const sameObjects = sortRows(descriptor, 'count').every(row => descriptor.rows.includes(row));
        return {results, bool_order:boolOrder, same_objects:sameObjects, unchanged:JSON.stringify(descriptor) === before};
      });
      for (const item of result.results) {
        assert.deepEqual(item.actual, item.expected);
        assert.deepEqual(item.rendered, item.expected);
        assert.equal(item.same_objects, true);
      }
      assert.deepEqual(result.bool_order, ['amostra-A','amostra-C','amostra-B','amostra-Ausente']);
      assert.equal(result.same_objects, true);
      assert.equal(result.unchanged, true);
      await restoreTable();
      return result;
    });
    await check('unsafe_number_and_string_boolean_fail_closed_in_real_browser', async () => {
      const result = await page.evaluate(async () => {
        const {default:data} = await import('/demo-data.js');
        const {renderTable, filterRows} = await import('/parity02_p03_table.js');
        const failures = [];
        for (const [key,value] of [['count',9007199254740992],['flag','false'],['flag',0]]) {
          const copy = structuredClone(data.table);copy.rows[0].cells[key] = value;
          try { renderTable(document, copy);failures.push('ACCEPTED'); }
          catch (error) { failures.push(error.code); }
        }
        try { filterRows(data.table, {columnId:'flag',operator:'eq',value:'false'});failures.push('ACCEPTED'); }
        catch (error) { failures.push(error.code); }
        return failures;
      });
      assert.deepEqual(result, ['UNSAFE_NUMBER','INVALID_TYPE','INVALID_TYPE','INVALID_TYPE']);
      return result;
    });
    await check('file_remains_file_mentions_are_neutral_and_states_separate', async () => {
      const file = page.locator('#metadata-mount [data-entity-id="report.pdf"]');
      assert.equal(await file.locator('.p03-metadata-kind').textContent(), 'Artefato declarado (File)');
      assert.equal(await file.locator('[data-semantic-kind]').count(), 0);
      const categories = await file.locator('.p03-metadata-relations').allTextContents();
      assert.match(categories[0], /Nenhuma relação declarada nesta categoria/);
      assert.match(categories[1], /Menções neutras · sem inferência de produção/);
      assert.match(categories[1], /mention: urn:synthetic:run → report\.pdf/);
      assert.doesNotMatch(categories[1], /output:|input:|derived_from:/);
      const fields = await file.locator('dt').allTextContents();
      for (const label of ['Disponibilidade declarada','Disponibilidade observada pelo leitor',
        'SHA-256 declarado','SHA-256 calculado informado pelo leitor']) assert.ok(fields.includes(label));
      const metadata = await page.locator('#metadata-mount').innerText();
      assert.ok(metadata.includes('UNKNOWN'));assert.ok(metadata.includes('UNVERIFIED'));
      assert.ok(metadata.includes('integridade não é autenticidade nem aprovação científica'));
      return {categories, fields};
    });
    await check('products_documents_stay_explicitly_synthetic_candidates', async () => {
      for (const kind of ['product','document']) {
        const candidate = page.locator(`#${kind}-mount [data-semantic-kind="${kind}"]`);
        assert.equal(await candidate.count(), 1);
        assert.match(await candidate.locator('.p03-metadata-status').textContent(), /candidato · fixture sintética · sem novo contrato persistido/);
      }
      assert.equal(await page.locator('#metadata-mount [data-semantic-kind]').count(), 0);
      const rejection = await page.evaluate(async () => {
        const {default:data} = await import('/demo-data.js');
        const {renderCandidate} = await import('/parity02_p03_artifacts.js');
        const candidate = structuredClone(data.document);candidate.synthetic=false;
        try { renderCandidate(document, candidate);return 'ACCEPTED'; } catch (error) { return error.code; }
      });
      assert.equal(rejection, 'SYNTHETIC_REQUIRED');
    });
    await check('keyboard_order_focus_visibility_and_no_focus_trap', async () => {
      await page.locator('#example').focus();
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'order');
      await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'missing');
      await page.keyboard.press('Tab');
      const focused = await page.evaluate(() => {
        const element = document.activeElement;const style = getComputedStyle(element);
        return {class_name:element.className, role:element.getAttribute('role'),
          label:element.getAttribute('aria-label'), outline_style:style.outlineStyle,
          outline_width:parseFloat(style.outlineWidth), focus_visible:element.matches(':focus-visible')};
      });
      assert.ok(focused.class_name.includes('atlas-p03-table__scroll'));
      assert.equal(focused.role, 'region');assert.ok(focused.label.includes('Tabela:'));
      assert.equal(focused.focus_visible, true);
      assert.notEqual(focused.outline_style, 'none');assert.ok(focused.outline_width >= 2);
      await page.keyboard.press('Shift+Tab');
      assert.equal(await page.evaluate(() => document.activeElement.id), 'missing');
      return focused;
    });

    for (const width of [1440,390,320]) {
      await page.setViewportSize({width, height:1000});
      await check(`contained_table_reflow_${width}_css_px`, async () => {
        const shape = await geometry();contained(shape, width);
        if (width < 400) assert.ok(shape.region_scroll_width > shape.region_client_width);
        return shape;
      });
      await screenshot(`${width}px`);
    }
    await check('maximum_table_two_dimensional_scroll_contained_and_keyboard_operable', async () => {
      await page.selectOption('#example', 'large');
      assert.equal(await page.locator('#table-mount tbody tr').count(), 1000);
      assert.equal(await page.locator('#table-mount tbody td').count(), 20000);
      const shape = await geometry();contained(shape, 320);
      assert.ok(shape.region_scroll_width > shape.region_client_width);
      assert.ok(shape.region_scroll_height > shape.region_client_height);
      const region = page.locator('#table-mount [role="region"]');
      await region.focus();
      await region.evaluate(element => {element.scrollTop=0;element.scrollLeft=0;});
      await page.keyboard.press('ArrowRight');
      await page.waitForFunction(() => document.querySelector('#table-mount [role="region"]').scrollLeft > 0);
      await page.keyboard.press('ArrowDown');
      await page.waitForFunction(() => document.querySelector('#table-mount [role="region"]').scrollTop > 0);
      const movement = await region.evaluate(element => ({left:element.scrollLeft, top:element.scrollTop,
        document_left:document.documentElement.scrollLeft, active:document.activeElement === element}));
      assert.ok(movement.left > 0 && movement.top > 0);
      assert.equal(movement.document_left, 0);assert.equal(movement.active, true);
      await screenshot('320px-large-table');
      return {shape,movement};
    });
    await restoreTable();
    await check('text_spacing_at_320_css_px_no_loss_or_outer_horizontal_scroll', async () => {
      const textBefore = await page.locator('body').textContent();
      await page.evaluate(() => {
        for (const element of document.querySelectorAll('body, body *')) {
          element.style.lineHeight='1.5';element.style.letterSpacing='0.12em';element.style.wordSpacing='0.16em';
          if (element.tagName === 'P') element.style.marginBottom='2em';
        }
      });
      const shape = await geometry();contained(shape,320);
      assert.equal(await page.locator('body').textContent(), textBefore);
      const measured = await page.locator('#table-mount td').first().evaluate(element => {
        const style=getComputedStyle(element);return {font_size:parseFloat(style.fontSize),
          line_height:parseFloat(style.lineHeight),letter_spacing:parseFloat(style.letterSpacing),
          word_spacing:parseFloat(style.wordSpacing)};
      });
      assert.ok(Math.abs(measured.line_height / measured.font_size - 1.5) < .01);
      assert.ok(Math.abs(measured.letter_spacing / measured.font_size - .12) < .01);
      assert.ok(Math.abs(measured.word_spacing / measured.font_size - .16) < .01);
      const clipped = await page.locator('#table-mount td, #metadata-mount dd, #document-mount p').evaluateAll(elements =>
        elements.filter(element => ['hidden','clip'].includes(getComputedStyle(element).overflowY)
          && element.scrollHeight > element.clientHeight + 1).length);
      assert.equal(clipped,0);
      await page.locator('#missing').focus();await page.keyboard.press('Tab');
      assert.equal(await page.evaluate(() => document.activeElement.classList.contains('atlas-p03-table__scroll')),true);
      await screenshot('320px-text-spacing');
      return {shape,measured,clipped_elements:clipped};
    });
    // Fresh document restores original styles and rechecks the real HTTP/module path.
    await page.reload({waitUntil:'networkidle'});
    await page.waitForSelector('html[data-p03-ready="true"]');
    await check('empty_table_and_hostile_html_uri_identity_are_inert', async () => {
      await page.selectOption('#example','empty');
      assert.ok((await page.locator('#table-mount').innerText()).includes('Nenhuma linha declarada'));
      await page.selectOption('#example','malicious');
      const mounts = '#table-mount, #metadata-mount, #product-mount, #document-mount';
      const state = await page.locator(mounts).evaluateAll(elements => ({
        dangerous_nodes:elements.reduce((count,element) => count + element.querySelectorAll('script,img,iframe,svg,a,object,embed,form,video,audio').length,0),
        event_attributes:elements.reduce((count,element) => count + [...element.querySelectorAll('*')]
          .reduce((sum,node) => sum + [...node.attributes].filter(attribute => /^on/i.test(attribute.name)).length,0),0),
        xss:globalThis.__p03_xss === true,
        attack:globalThis.P03_ATTACK === true
      }));
      assert.deepEqual(state,{dangerous_nodes:0,event_attributes:0,xss:false,attack:false});
      const text = await page.locator('#table-mount').textContent();
      assert.ok(text.includes('<img src="https://example.invalid/no-fetch"'));
      assert.ok(text.includes('javascript:globalThis.__p03_xss=true'));
      assert.ok(text.includes('https://example.invalid/payload.csv?private=synthetic'));
      assert.equal(await page.locator('#table-mount tbody tr').first().getAttribute('data-row-id'),
        'row" autofocus onfocus="globalThis.__p03_xss=true');
      const shape = await geometry();contained(shape,320);
      await screenshot('320px-hostile-data');
      return {state,shape};
    });
    await check('zero_external_requests_websockets_unknown_routes_page_or_console_errors', async () => {
      assert.deepEqual(report.external_requests,[]);
      assert.deepEqual(report.websocket_attempts,[]);
      assert.deepEqual(report.unexpected_local_requests,[]);
      assert.deepEqual(report.page_errors,[]);
      assert.deepEqual(report.console_errors,[]);
      const requested = new Set(report.requests.map(request => new URL(request.url).pathname));
      for (const route of allowed) assert.ok(requested.has(route), `Asset not requested by real browser: ${route}`);
      return {external_requests:0,websocket_attempts:0,page_errors:0,console_errors:0,served_asset_paths:[...requested].sort()};
    });
    await check('sources_fixtures_and_all_25_frozen_bytes_preserved', async () => {
      assert.deepEqual(hashFrozen(),before);
      return {files:25,bytes_preserved:true};
    });
    report.status='PASS_SCOPED';
    report.required_checks_passed=report.checks.length;
    report.required_checks_failed=0;
    return 0;
  } catch (error) {
    report.status='FAIL';report.error=String(error.stack || error.message);
    if (page) {
      try { await screenshot('failure'); } catch {}
    }
    return 1;
  } finally {
    if (context) await context.close();
    if (browser) await browser.close();
    if (server) {
      server.kill('SIGTERM');
      await new Promise(resolve => {
        if (server.exitCode !== null) return resolve();
        const timeout=setTimeout(() => {server.kill('SIGKILL');resolve();},5000);
        server.once('exit', () => {clearTimeout(timeout);resolve();});
      });
    }
    if (serverStderr) report.harness_stderr=serverStderr;
  }
}

process.exitCode=await main();
report.completed_at=new Date().toISOString();
report.collected_checks=report.checks.length;
writeFileSync(path.join(output,'BROWSER-RECEIPT.json'),JSON.stringify(report,null,2)+'\n');
process.stdout.write(JSON.stringify({status:report.status,tested_head:report.tested_head,
  checks:report.collected_checks,skipped:report.skipped,browser_zoom_200:report.browser_zoom_200.status,
  output:path.join(output,'BROWSER-RECEIPT.json'),error:report.error || report.reason || null})+'\n');
