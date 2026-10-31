// Isolated real Chromium oracle; synthetic fixtures only. No Atlas shell or R4.
import { chromium } from 'playwright';
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { scaleFixture } from './atlas_parity04_f3a_scale_fixture.mjs';

const root = resolve(process.argv[2] || '.');
const out = resolve(process.argv[3] || '.test-output/atlas-parity04-f3a');
await mkdir(out, { recursive: true });
const git = (...args) => execFileSync('git', args, { cwd: root, encoding: 'utf8' }).trim();
const sha = git('rev-parse', 'HEAD'), tree = git('rev-parse', 'HEAD^{tree}');
if (process.env.F3A_EXPECTED_SHA && sha !== process.env.F3A_EXPECTED_SHA) throw new Error('Tested SHA does not match expected head');
const fixture = JSON.parse(await readFile(join(root, 'tests/fixtures/atlas_parity04_f3a_graph.json'), 'utf8'));
const scale = scaleFixture(fixture), scaleSource = "synthetic-f3a", scaleSnapshot = "synthetic-f3a-v1";
await writeFile(join(out, 'scale-fixture.json'), JSON.stringify(scale));
const js = await readFile(join(root, 'packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.js'));
const css = await readFile(join(root, 'packages/atlas/src/atlas_viewer/static/parity04_f3a_graph.css'));
const generator = await readFile(join(root, 'scripts/qa/atlas_parity04_f3a_scale_fixture.mjs'));
const html = '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><link rel="stylesheet" href="/graph.css"><title>F3A isolated synthetic QA</title></head><body style="margin:0"><main id="root"></main><script type="module">import {mount} from "/graph.js"; import {stressFixture} from "/scale-fixture.js"; window.mountGraph=mount; window.stressFixture=stressFixture;</script></body></html>';
const server = createServer((req, res) => {
  const payload = { '/': [html, 'text/html'], '/graph.js': [js, 'text/javascript'], '/graph.css': [css, 'text/css'], '/scale-fixture.js': [generator, 'text/javascript'] }[req.url];
  if (!payload) { res.writeHead(404); res.end(); return; }
  res.writeHead(200, { 'Content-Type': payload[1] + '; charset=utf-8', 'Cache-Control': 'no-store' });
  res.end(payload[0]);
});
await new Promise(r => server.listen(0, '127.0.0.1', r));
const origin = 'http://127.0.0.1:' + server.address().port;
const report = { schema: 'atlas-f3a-browser-receipt-v1', sha, tree, synthetic: true, browser: null, checks: [], screenshots: [], outside_requests: [], page_errors: [], storage_calls: [] };
let browser;
report.progress = [];
async function checkpoint(stage, detail = {}) {
  const item={stage,at:new Date().toISOString(),...detail}; report.progress.push(item);
  report.active_stage=stage; report.passed=false;
  console.log(JSON.stringify({f3a_checkpoint:item}));
  await writeFile(join(out,'browser-progress.json'),JSON.stringify({sha,tree,progress:report.progress},null,2)+'\n');
  await writeFile(join(out,'browser-receipt.json'),JSON.stringify(report,null,2)+'\n');
}
async function deadline(label, promise, milliseconds) {
  let timer;
  try { return await Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error(label+' exceeded '+milliseconds+'ms')),milliseconds);})]); }
  finally {clearTimeout(timer);}
}
const watchdog=setTimeout(async()=>{
  report.fatal='Harness watchdog exceeded 540000ms at '+report.active_stage;report.passed=false;
  try {await checkpoint('watchdog',{error:report.fatal});} finally {process.exit(1);}
},540000);
watchdog.unref();
function insist(value, message) { if (!value) throw new Error(message); }
function small() {
  const d = structuredClone(fixture);
  d.nodes = d.nodes.filter((n, i) => i < 5 || ['nav:orphan', 'nav:isolated', 'nav:stub', 'nav:hostile'].includes(n.identity.navigation_id));
  d.relations = d.relations.slice(0, 4); d.gaps = [];
  d.nodes.find(n => n.identity.navigation_id === 'nav:hostile').original_type = 'Tipo declarado longo ' + 'T'.repeat(160);
  const counts = { presentation_node_occurrences: d.nodes.length, source_nodes: d.nodes.length - 1, external_reference_stubs: 1, relations: 4, tables: 0, rows: 0, assets: 0 };
  d.coverage.counts.forEach(c => { c.selected = counts[c.unit]; c.loaded = counts[c.unit]; c.visible = null; });
  return d;
}
async function check(name, fn, width = 1440, data = small()) {
  const start = performance.now(); let page, context;
  await checkpoint('journey:start',{name,width});
  try {
    context = await browser.newContext({ viewport: { width, height: 800 }, deviceScaleFactor: 1 });
    await context.addInitScript(() => {
      window.F3A_PWNED = 0; window.f3aStorageCalls = [];
      for (const op of ['getItem','setItem','removeItem','clear','key']) {
        Storage.prototype[op] = function(...args) { window.f3aStorageCalls.push(op); throw new Error('Storage is forbidden in F3A'); };
      }
    });
    await context.route('**/*', route => {
      const u = new URL(route.request().url());
      if (u.origin !== origin || !['/', '/graph.js', '/graph.css', '/scale-fixture.js'].includes(u.pathname)) { report.outside_requests.push(route.request().url()); route.abort(); }
      else route.continue();
    });
    page = await context.newPage();
    page.on('pageerror', e => report.page_errors.push(String(e)));
    await page.goto(origin); await page.waitForFunction(() => typeof window.mountGraph === 'function');
    const ok = await page.evaluate(d => {
      window.fixture = d; window.fixtureNow = Date.parse('2026-10-31T09:05:00Z');
      window.f3aEvents = [];
      document.querySelector('#root').addEventListener('graph-selection', e => window.f3aEvents.push(e.detail));
      window.graph = window.mountGraph(document.querySelector('#root'), d, { now: () => window.fixtureNow });
      return window.graph.getState();
    }, data);
    insist(!ok.error, 'Valid synthetic descriptor was refused: ' + JSON.stringify(ok));
    const detail = await deadline('Journey '+name,fn(page),90000);
    const state = await page.evaluate(() => ({ pwned: window.F3A_PWNED, storage: window.f3aStorageCalls }));
    insist(state.pwned === 0, 'Hostile data executed');
    insist(state.storage.length === 0, 'Component accessed browser storage');
    report.checks.push({ name, passed: true, duration_ms: Math.round(performance.now() - start), detail: detail ?? null });
  } catch (e) {
    report.checks.push({ name, passed: false, duration_ms: Math.round(performance.now() - start), error: String(e.stack || e) });
  } finally {
    if (page) { const storage = await deadline('Storage inspection '+name,page.evaluate(() => window.f3aStorageCalls || []),5000).catch(() => []); report.storage_calls.push(...storage); }
    let cleanupError=null;
    if (context) { try {await deadline('Context close '+name,context.close(),10000);} catch(e) {cleanupError=e;report.fatal=String(e.stack||e);} }
    await checkpoint('journey:end',{name,passed:report.checks.at(-1)?.passed===true,duration_ms:Math.round(performance.now()-start),cleanup_error:cleanupError?String(cleanupError):null});
    if(cleanupError)throw cleanupError;
  }
}
async function state(p) { return p.evaluate(() => window.graph.getState()); }
async function shot(p, name) {
  const path = join(out, name + '.png'); await p.screenshot({ path, fullPage: true });
  const bytes = await readFile(path); report.screenshots.push({ name: name + '.png', bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
}
try {
  browser = await chromium.launch({ headless: true }); report.browser = await browser.version();
  await check('hierarchy_selection_and_event', async p => {
    insist(await p.locator('[data-node-id="nav:run"]').count() === 1, 'Declared Run missing');
    await p.locator('[data-node-id="nav:run"]').click();
    const result = await p.evaluate(() => ({ state: graph.getState(), last: f3aEvents.at(-1) }));
    const s = result.last;
    insist(s?.source_id === fixture.source.source_id && s?.snapshot_id === fixture.snapshot.snapshot_id && s?.nav_id === 'nav:run' && s?.occurrence === 0 && typeof s?.session_id === 'string', 'Neutral selection lost contextual identity');
    insist(result.state.selection?.nav_id === 'nav:run', 'Selection state missing');
    const wrong = await p.evaluate(s => graph.select({ ...s, source_id: 'another-source' }), s);
    insist(wrong === false, 'Cross-source resolution accepted');
    await shot(p, 'desktop'); return s;
  });
  await check('collapse_expand_focus_and_state', async p => {
    await p.locator('[data-node-id="nav:run"]').click();
    const before = await state(p);
    await p.locator('[data-toggle-id="nav:family"]').click();
    let after = await state(p);
    insist(!after.visible_ids.includes('nav:run'), 'Collapse left descendants visible');
    insist(after.selection?.nav_id === 'nav:run', 'Collapse lost contextual selection');
    insist(after.zoom === before.zoom && after.pan.x === before.pan.x && after.pan.y === before.pan.y, 'Collapse reset viewport');
    await p.locator('[data-toggle-id="nav:family"]').click();
    after = await state(p);
    insist(after.visible_ids.includes('nav:run') && after.selection?.nav_id === 'nav:run', 'Expansion did not restore descendants/selection');
    const focus = await p.evaluate(() => document.activeElement?.getAttribute('data-node-id') || document.activeElement?.getAttribute('data-toggle-id'));
    insist(focus === 'nav:family', 'Focus was lost after layout rebuild'); return after.visible_ids;
  });
  await check('keyboard_traversal', async p => {
    const project = p.locator('[data-node-id="nav:project"]'); await project.focus();
    await p.keyboard.press('ArrowRight'); await p.keyboard.press('ArrowDown');
    insist(await p.evaluate(() => document.activeElement?.hasAttribute('data-node-id')), 'Arrow navigation lost tree focus');
    await p.keyboard.press('End');
    const end = await p.evaluate(() => document.activeElement.getAttribute('data-node-id'));
    const ids = (await state(p)).visible_ids; insist(end === ids.at(-1), 'End did not reach last visible node');
    await p.keyboard.press('Home');
    insist(await p.evaluate(() => document.activeElement.getAttribute('data-node-id')) === ids[0], 'Home did not reach first visible node');
    await p.keyboard.press('Enter'); insist((await state(p)).selection?.nav_id === ids[0], 'Enter did not select');
    await p.keyboard.press('Escape'); insist((await state(p)).selection === null, 'Escape did not clear selection');
    await p.locator('[data-node-id="nav:family"]').focus(); await p.keyboard.press('ArrowLeft');
    insist(!(await state(p)).visible_ids.includes('nav:run'), 'ArrowLeft did not collapse family');
    await p.keyboard.press('ArrowRight'); insist((await state(p)).visible_ids.includes('nav:run'), 'ArrowRight did not expand family');
    await p.keyboard.press('Tab');
    insist(await p.evaluate(() => document.activeElement !== document.body), 'Tab lost all focus');
    return { first: ids[0], last: end };
  });
  await check('viewport_controls_reset_fit_and_minimap', async p => {
    const initial = await state(p);
    await p.locator('[data-action="zoom-in"]').click(); const zoomed = await state(p);
    insist(zoomed.zoom > initial.zoom, 'Zoom-in control has no effect');
    await p.locator('[data-action="zoom-out"]').click(); insist((await state(p)).zoom < zoomed.zoom, 'Zoom-out control has no effect');
    for (const action of ['pan-left','pan-right','pan-up','pan-down']) {
      const a = await state(p); await p.locator('[data-action="' + action + '"]').click(); const b = await state(p);
      insist(a.pan.x !== b.pan.x || a.pan.y !== b.pan.y, 'Pan control has no effect: ' + action);
    }
    const map = p.locator('[data-minimap]'); const box = await map.boundingBox(); insist(box && box.width > 0, 'Minimap absent');
    const a = await state(p); await map.click({ position: { x: box.width * .2, y: box.height * .2 } }); const b = await state(p);
    insist(a.pan.x !== b.pan.x || a.pan.y !== b.pan.y, 'Minimap does not navigate');
    await map.focus(); await p.keyboard.press('ArrowRight'); const c = await state(p);
    insist(b.pan.x !== c.pan.x, 'Minimap keyboard navigation has no effect');
    await p.locator('[data-action="reset"]').click(); const reset = await state(p);
    insist(reset.zoom === 1 && reset.pan.x === 20 && reset.pan.y === 20, 'Reset did not restore zoom1 and pan20/20');
    await p.locator('[data-action="fit"]').click(); const fit = await state(p);
    insist(fit.zoom > 0 && Number.isFinite(fit.pan.x), 'Fit invalid viewport'); return { initial, zoomed: zoomed.zoom, reset: reset.zoom, fit: fit.zoom };
  });
  await check('pointer_pan_wheel_zoom_and_pinch', async p => {
    const canvas = p.locator('svg[data-f3a-canvas]'); const box = await canvas.boundingBox(); insist(box, 'Canvas missing');
    const x = box.x + box.width * .8, y = box.y + box.height * .8;
    const a = await state(p); await p.mouse.move(x, y); await p.mouse.down(); await p.mouse.move(x + 35, y + 22, { steps: 5 }); await p.mouse.up(); const b = await state(p);
    insist(a.pan.x !== b.pan.x || a.pan.y !== b.pan.y, 'Pointer drag did not pan');
    await p.mouse.move(x, y); await p.mouse.wheel(0, -120); await p.waitForTimeout(80); const c = await state(p);
    insist(c.zoom > b.zoom, 'Wheel gesture did not zoom');
    // Chromium CDP sends actual touch pointers to the SVG; component receives browser pointer events.
    const session = await p.context().newCDPSession(p);
    await session.send('Emulation.setTouchEmulationEnabled', { enabled: true, maxTouchPoints: 2 });
    await session.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x: Math.round(x-30), y: Math.round(y), id: 1 }, { x: Math.round(x+30), y: Math.round(y), id: 2 }] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchMove', touchPoints: [{ x: Math.round(x-55), y: Math.round(y), id: 1 }, { x: Math.round(x+55), y: Math.round(y), id: 2 }] });
    await session.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
    const d = await state(p); insist(d.zoom > c.zoom, 'Pinch did not zoom');
    return { drag: b.pan, wheel: c.zoom, pinch: d.zoom };
  });
  await check('typed_edges_and_no_fabricated_parent', async p => {
    const rels = await p.locator('[data-relation-id]').evaluateAll(elements => elements.map(e => ({ id: e.getAttribute('data-relation-id'), semantics: e.getAttribute('data-semantics'), direction: e.getAttribute('data-direction'), arrow: e.getAttribute('marker-end'), css: e.getAttribute('class') })));
    for (const sem of ['ORGANIZATIONAL_MEMBERSHIP','DECLARED_LINEAGE','DECLARED_BINDING','NEUTRAL_MENTION']) insist(rels.some(e => e.semantics === sem), 'Typed relation absent: ' + sem);
    for (const e of rels.filter(e => e.direction !== 'FROM_TO')) insist(!e.arrow || e.arrow === 'none', 'Unknown/undirected relation gained causal arrow');
    const relationClasses = new Set(rels.map(e => e.css)); insist(relationClasses.size >= 4, 'Relation styles not distinct');
    const orphan = await p.locator('[data-node-id="nav:orphan"]').getAttribute('aria-label');
    insist(orphan?.includes('ORPHAN'), 'Orphan state hidden');
    const iso = await p.locator('[data-node-id="nav:isolated"]').getAttribute('aria-label');
    insist(iso?.includes('binding_gap') || iso?.includes('lacuna') || iso?.includes('gap'), 'Isolated source Run gap hidden');
    return rels;
  });
  await check('adversarial_occurrences_counts_and_no_mutation', async p => {
    const s = await state(p);
    insist(s.node_count === 109 && s.relation_count === 210 && s.visible_ids.length === 109, 'Occurrence loss or silent truncation');
    insist(s.endpoint_counts.NULL_ENDPOINT === 22 && s.endpoint_counts.UNRESOLVED === 75 && s.endpoint_counts.COLLISION === 50, 'Negative endpoint counts changed');
    insist(await p.locator('[data-node-id="nav:collision-0-a"]').count() === 1 && await p.locator('[data-node-id="nav:collision-0-b"]').count() === 1, 'Native collision merged occurrences');
    const original = JSON.stringify(fixture); insist(await p.evaluate(() => JSON.stringify(window.fixture)) === original, 'Component mutated descriptor');
    await p.locator('[data-action="fit"]').click();
    const fitted = await p.evaluate(() => { const canvas=document.querySelector('svg[data-f3a-canvas]').getBoundingClientRect();return [...document.querySelectorAll('[data-node-id]')].every(el=>{const b=el.getBoundingClientRect();return b.left>=canvas.left-2 && b.top>=canvas.top-2 && b.right<=canvas.right+2 && b.bottom<=canvas.bottom+2;}); });
    insist(fitted, 'Fit did not contain all 109 synthetic occurrences in viewport');
    const text = await p.locator('#root').textContent();
    insist(text.includes('75') && text.includes('22'), 'Unresolved/null counts not visible');
    return { node_count: s.node_count, relation_count: s.relation_count, endpoint_counts: s.endpoint_counts };
  }, 1280, fixture);
  await check('hostile_text_uri_and_zero_io', async p => {
    const t = await p.locator('#root').textContent();
    insist(t.includes('<img') && t.includes('javascript:alert(1)') && t.includes('file:///private'), 'Hostile literal not preserved as text');
    insist(await p.locator('#root img,#root script,#root iframe,#root a[href]').count() === 0, 'Descriptor became active markup/URI');
    insist(await p.evaluate(() => F3A_PWNED) === 0, 'Payload executed');
    return { inert: true, active_elements: 0 };
  });
  await check('stale_context_cross_source_snapshot_and_disposal', async p => {
    await p.locator('[data-node-id="nav:run"]').click(); const old = (await state(p)).selection;
    const result = await p.evaluate(ctx => {
      const before = graph.getState().session_id; const ok = graph.setData(structuredClone(fixture)); const fresh = graph.getState();
      return { ok, before, fresh, stale: graph.select(ctx) };
    }, old);
    insist(result.ok && result.fresh.selection === null && result.fresh.session_id !== result.before && !result.stale, 'Same-snapshot reimport reused stale links');
    const crossed = await p.evaluate(() => {
      const d = structuredClone(fixture); d.source.source_id = 'synthetic-other-source'; d.snapshot.snapshot_id = 'synthetic-other-snapshot';
      const fix = r => { if (r.source_id) r.source_id = d.source.source_id; if (r.snapshot_id) r.snapshot_id = d.snapshot.snapshot_id; };
      d.nodes.forEach(n => { fix(n.parent); if(n.external_reference)fix(n.external_reference); }); d.relations.forEach(r=>{fix(r.from);fix(r.to)});
      const ok = graph.setData(d), s = graph.getState();
      return { ok, selected: graph.select({source_id: 'synthetic-f3a',snapshot_id:'synthetic-f3a-v1',occurrence:0,nav_id:'nav:run',session_id:s.session_id}) };
    });
    insist(crossed.ok && !crossed.selected, 'Cross-source/snapshot nav text resolved');
    await p.reload();await p.waitForFunction(()=>typeof window.mountGraph==='function');
    const reloaded=await p.evaluate(({d,old})=>{
      window.fixture=d;window.fixtureNow=Date.parse('2026-10-31T09:05:00Z');window.f3aEvents=[];
      document.querySelector('#root').addEventListener('graph-selection',e=>f3aEvents.push(e.detail));
      window.graph=window.mountGraph(document.querySelector('#root'),d,{now:()=>fixtureNow});
      return {session:graph.getState().session_id,accepted:graph.select(old)};
    },{d:small(),old});
    insist(reloaded.session!==old.session_id && !reloaded.accepted,'Page reload reused previous session/context');
    await p.evaluate(() => { graph.dispose(); graph.dispose(); });
    insist(await p.locator('#root').textContent() === '', 'dispose left component state in DOM');
    return { reimport_session_changed: true, cross_context_rejected: true };
  });
  await check('expiry_invalidates_selection_and_links', async p => {
    await p.locator('[data-node-id="nav:run"]').click(); const old = (await state(p)).selection;
    const r = await p.evaluate(ctx => { fixtureNow = Date.parse('2026-10-31T10:02:00Z'); const accepted = graph.select(ctx); return {accepted,state:graph.getState(),text:document.querySelector('#root').textContent}; }, old);
    insist(!r.accepted && r.state.selection === null && r.state.error && /expir/i.test(r.text), 'Expiry did not visibly invalidate data/context');
    return r.state.error;
  });
  await check('invalid_descriptors_rejected_atomically', async p => {
    const cases = await p.evaluate(() => {
      const mutations = {
        unknown_version: d => { d.version = '99.0.0'; },
        unknown_property: d => { d.extra = 'unexpected'; },
        duplicate_nav: d => { d.nodes[1].identity.navigation_id = d.nodes[0].identity.navigation_id; },
        duplicate_cross_collection_nav: d => { d.relations[0].identity.navigation_id = d.nodes[0].identity.navigation_id; },
        nav_promoted_native: d => { d.nodes[0].identity.native_id = d.nodes[0].identity.navigation_id; },
        resolved_context_mismatch: d => { d.nodes[1].parent.source_id = 'other'; },
        resolved_stub_target: d => { d.relations[0].to.target_navigation_id='nav:stub';d.relations[0].to.declared_id='SYN-EXTERNAL'; },
        resolved_collision: d => { d.nodes.push(structuredClone(d.nodes[0]));d.nodes.at(-1).identity.navigation_id='nav:project-duplicate'; },
        not_validated: d => { d.validation.descriptor_schema='NOT_RUN'; },
        invalid_ttl: d => { d.snapshot.expires_at='2026-11-01T10:01:00Z'; },
        invalid_calendar: d => { d.snapshot.observed_at='2026-02-30T09:00:00Z'; },
        invalid_clock_24h: d => { d.snapshot.observed_at='2026-10-30T24:00:00Z'; },
        unmapped_literal_lexeme_mismatch: d => { d.unmapped_fields=[{owner_navigation_id:'nav:project',locator:'/synthetic/unmapped',source_key_literal:'synthetic',value:{type:'string',literal:'benign',lexeme:'"different"',unit:null,precision:null,absence:null}}]; },
        unmapped_embedded_json_depth: d => {const s='['.repeat(25)+'0'+']'.repeat(25);d.unmapped_fields=[{owner_navigation_id:'nav:project',locator:'/synthetic/unmapped',source_key_literal:'synthetic',value:{type:'array',literal:s,lexeme:s,unit:null,precision:null,absence:null}}]; },
        depth: d => { let o=d;for(let i=0;i<25;i++){o.deep={};o=o.deep;} },
        nonfinite: d => { d.nodes[0].identity.occurrence=Infinity; }
      };
      return Object.entries(mutations).map(([name,mutate]) => {
        graph.setData(structuredClone(fixture)); const d=structuredClone(fixture);mutate(d);
        const accepted=graph.setData(d);const s=graph.getState();
        return {name,accepted,error:s.error,selection:s.selection,visible:s.visible_ids.length,text:document.querySelector('#root').textContent};
      });
    });
    for(const c of cases) insist(!c.accepted && c.error && c.selection === null && c.visible === 0 && c.text.length > 0, 'Invalid input not visibly/atomically refused: '+JSON.stringify(c));
    return cases.map(({name,error})=>({name,error}));
  });
  await check('hierarchy_cycles_retained_as_anomalies', async p => {
    const r = await p.evaluate(() => {
      const d = structuredClone(fixture); d.nodes=d.nodes.slice(0,5);d.relations=[];d.gaps=[];
      d.nodes[0].parent_key_literal='SYN-R';d.nodes[0].parent={source_id:d.source.source_id,snapshot_id:d.snapshot.snapshot_id,declared_id:'SYN-R',target_navigation_id:'nav:run',resolution:'RESOLVED',evidence_locator:'/synthetic/cycle'};
      d.nodes[0].tree_state='PARENT_RESOLVED';
      const counts={presentation_node_occurrences:5,source_nodes:5,external_reference_stubs:0,relations:0,tables:0,rows:0,assets:0};d.coverage.counts.forEach(c=>{c.selected=counts[c.unit];c.loaded=counts[c.unit]});
      const accepted=graph.setData(d);return {accepted,state:graph.getState(),text:document.querySelector('#root').textContent};
    });
    insist(r.accepted && r.state.visible_ids.length === 5 && /cycl|cicl/i.test(r.text), 'Cycle was dropped or silently treated as valid hierarchy'); return r.state;
  });
  await check('capacity_and_descriptor_extremes', async p => {
    await p.evaluate(() => {
      const d=structuredClone(fixture), seed=structuredClone(d.nodes[0]);d.relations=[];d.gaps=[];
      d.nodes=Array.from({length:1000},(_,i)=>({...structuredClone(seed),identity:{...seed.identity,native_id:'SYN-KBD-'+i,navigation_id:'nav:kbd-'+i,occurrence:i},parent_key_literal:i?'SYN-KBD-'+(i-1):null,tree_state:i?'PARENT_RESOLVED':'ROOT_DECLARED',parent:i?{source_id:d.source.source_id,snapshot_id:d.snapshot.snapshot_id,declared_id:'SYN-KBD-'+(i-1),target_navigation_id:'nav:kbd-'+(i-1),resolution:'RESOLVED',evidence_locator:'/synthetic/kbd/'+i}:structuredClone(seed.parent)}));
      const counts={presentation_node_occurrences:1000,source_nodes:1000,external_reference_stubs:0,relations:0,tables:0,rows:0,assets:0};d.coverage.counts.forEach(c=>{c.selected=counts[c.unit];c.loaded=counts[c.unit]});
      if(!graph.setData(d))throw new Error('Keyboard chain cap1000 refused');
    });
    await p.locator('[data-action="fit"]').click();
    await p.locator('[data-node-id="nav:kbd-0"]').focus();await p.keyboard.press('End');await p.keyboard.press('Enter');
    const focused = await p.locator('[data-node-id="nav:kbd-999"]').boundingBox();
    insist(focused.width >= 115 && (await state(p)).selection?.nav_id === 'nav:kbd-999', 'Keyboard after fit failed legible contextual focus in deep1000 chain');
    const results = await p.evaluate(() => {
      function bigger(nodes, relations) {
        const d=structuredClone(fixture), seed=structuredClone(d.nodes[0]), edge=structuredClone(d.relations[0]);
        d.nodes=Array.from({length:nodes},(_,i)=>({...structuredClone(seed),identity:{...seed.identity,native_id:'SYN-LIMIT-'+i,navigation_id:'nav:limit-'+i,occurrence:i}}));
        d.relations=Array.from({length:relations},(_,i)=>({...structuredClone(edge),identity:{...edge.identity,navigation_id:'nav:limit-rel-'+i},from:{...edge.from,declared_id:'SYN-LIMIT-0',target_navigation_id:'nav:limit-0'},to:{...edge.to,declared_id:'SYN-LIMIT-1',target_navigation_id:'nav:limit-1'}}));
        d.gaps=[];const counts={presentation_node_occurrences:nodes,source_nodes:nodes,external_reference_stubs:0,relations, tables:0,rows:0,assets:0};d.coverage.counts.forEach(c=>{c.selected=counts[c.unit];c.loaded=counts[c.unit]});return d;
      }
      const deep=bigger(1000,0),deepStart=performance.now();
      for(let i=1;i<deep.nodes.length;i++){const n=deep.nodes[i];n.parent_key_literal='SYN-LIMIT-'+(i-1);n.tree_state='PARENT_RESOLVED';n.parent={source_id:deep.source.source_id,snapshot_id:deep.snapshot.snapshot_id,declared_id:n.parent_key_literal,target_navigation_id:'nav:limit-'+(i-1),resolution:'RESOLVED',evidence_locator:'/synthetic/deep/'+i};}
      if(!graph.setData(deep) || graph.getState().visible_ids.length!==1000) throw new Error('Render cap1000 chain was not admitted completely');
      document.querySelector('[data-action="fit"]').click();
      const canvas=document.querySelector('svg[data-f3a-canvas]').getBoundingClientRect();
      if(![...document.querySelectorAll('[data-node-id]')].every(el=>{const b=el.getBoundingClientRect();return b.left>=canvas.left-2 && b.top>=canvas.top-2 && b.right<=canvas.right+2 && b.bottom<=canvas.bottom+2;})) throw new Error('Fit did not contain deep1000 chain');
      const positive=[{nodes:1000,relations:0,duration_ms:performance.now()-deepStart,visible:graph.getState().visible_ids.length}];
      const edges=bigger(2,4000),edgeStart=performance.now();
      if(!graph.setData(edges) || graph.getState().node_count!==2 || graph.getState().relation_count!==4000 || document.querySelectorAll('[data-relation-id]').length!==4000) throw new Error('Render cap4000 relations was not admitted completely');
      positive.push({nodes:2,relations:4000,duration_ms:performance.now()-edgeStart,dom_relations:document.querySelectorAll('[data-relation-id]').length});
      for(const [nodes,relations] of [[1001,0],[10000,0],[2,4001]]) { const d=bigger(nodes,relations),start=performance.now(); if(!graph.setData(d))throw new Error('Within-envelope scale refused: '+nodes+'/'+relations+' '+graph.getState().error);positive.push({nodes,relations,duration_ms:performance.now()-start,rendered_nodes:graph.getState().rendered_node_count,rendered_relations:graph.getState().rendered_relation_count}); }
      const negative=[[10001,0],[2,100001]].map(([nodes,relations])=>{
        const d=bigger(nodes,relations),start=performance.now(),accepted=graph.setData(d),s=graph.getState();
        return {nodes,relations,accepted,error:s.error,visible:s.visible_ids.length,duration_ms:performance.now()-start,text:document.querySelector('#root').textContent};
      });return {positive,negative};
    });
    for(const r of results.negative) insist(!r.accepted && r.error && r.visible===0 && r.text.length>0 && r.duration_ms<30000,'Capacity silent truncation or budget exceeded: '+JSON.stringify(r));
    for(const r of results.positive) insist(r.duration_ms<30000,'Positive capacity exceeded30sec');
    return {positive:results.positive,negative:results.negative.map(({nodes,relations,error,duration_ms})=>({nodes,relations,error,duration_ms}))};
  });
  for(const width of [390,320]) await check('responsive_' + width, async p => {
    const box=await p.locator('#root').boundingBox();
    const sizes=await p.evaluate(()=>({scroll:document.documentElement.scrollWidth,inner:innerWidth}));
    insist(box.width<=width && sizes.scroll<=width,'Horizontal page overflow at '+width+': '+JSON.stringify(sizes));
    for(const action of ['zoom-in','zoom-out','fit','reset']) {
      const b=p.locator('[data-action="'+action+'"]');insist(await b.isVisible(),'Control clipped at '+width+': '+action);await b.focus();
      insist(await b.evaluate(el=>el===document.activeElement),'Control unreachable by focus');
    }
    await p.locator('[data-node-id="nav:project"]').focus();await p.keyboard.press('End');await p.keyboard.press('Enter');
    insist((await state(p)).selection?.nav_id==='nav:hostile','Long/hostile label unreachable');
    const textFits=await p.locator('[data-node-id="nav:hostile"] text').evaluateAll(es=>es.every(el=>{const b=el.getBBox();return b.x>=0 && b.x+b.width<=230;}));
    insist(textFits,'Long original_type or label overflowed node card at '+width);
    const aria=await p.locator('[data-node-id="nav:hostile"]').getAttribute('aria-label');insist(aria.includes('T'.repeat(160)), 'Long type lost full accessible literal');
    await shot(p,'mobile-'+width);return sizes;
  },width);
  await check('reflow_preserves_focus_zoom_and_selection', async p => {
    await p.locator('[data-node-id="nav:run"]').focus();await p.keyboard.press('Enter');
    await p.locator('[data-action="zoom-in"]').click();await p.locator('[data-node-id="nav:run"]').focus();
    const a=await state(p);await p.setViewportSize({width:320,height:800});await p.waitForTimeout(80);const b=await state(p);
    insist(a.zoom===b.zoom && a.pan.x===b.pan.x && a.pan.y===b.pan.y && b.selection?.nav_id==='nav:run','Reflow discarded viewport or selection');
    insist(await p.evaluate(()=>document.activeElement?.getAttribute('data-node-id'))==='nav:run','Reflow lost focus');return {zoom:b.zoom,selection:b.selection};
  });
  await check('authority_validation_gaps_and_expiry_visible', async p => {
    const t=await p.locator('#root').textContent();
    for(const expected of ['LEGACY_DERIVED','OBSERVED_SNAPSHOT_ONLY','NOT_VERIFIED','NOT_EVALUATED','PASS','2026-10-31']) insist(t.includes(expected),'Missing authority/validation/expiry disclosure: '+expected);
    insist(/gap|lacuna/i.test(t),'Binding gaps hidden');
    const ratios=await p.evaluate(()=>{
      function rgb(text){const n=text.match(/[\d.]+/g);return n.slice(0,3).map(Number);}
      function luminance(text){return rgb(text).map(n=>{const c=n/255;return c<=.04045?c/12.92:((c+.055)/1.055)**2.4;}).reduce((sum,n,i)=>sum+n*[.2126,.7152,.0722][i],0);}
      function ratio(a,b){const x=luminance(a),y=luminance(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05);}
      const button=getComputedStyle(document.querySelector('[data-action="fit"]')), label=getComputedStyle(document.querySelector('.f3a-label')), meta=getComputedStyle(document.querySelector('.f3a-node-meta')), card=getComputedStyle(document.querySelector('.f3a-node > rect'));
      return {button:ratio(button.color,button.backgroundColor),label:ratio(label.fill,card.fill),metadata:ratio(meta.fill,card.fill)};
    });
    insist(Object.values(ratios).every(r=>r>=4.5),'Measured control/node text contrast below4.5: '+JSON.stringify(ratios));
    return {authority:'LEGACY_DERIVED',scientific_approval:'NOT_EVALUATED',measured_text_contrast:ratios};
  });

  await check('scale_full_index_and_identity', async p => {
    const before = await state(p);
    insist(before.node_count === 2911 && before.relation_count === 1595, 'Scale fixture records lost');
    insist(before.loaded_node_count === 2911 && before.declared_node_count === 2911, 'Loaded/declared node counts confused with DOM');
    const expectedIds = new Set(scale.nodes.map(n => n.identity.navigation_id));
    insist(before.visible_ids.length === 2911 && new Set(before.visible_ids).size === 2911 && before.visible_ids.every(id => expectedIds.has(id)), 'Initial scale traversal lost or duplicated an occurrence');
    insist(before.operation_ms < 30000, '2911-node admission exceeded operation deadline');
    const metrics = await p.evaluate(() => ({dom_elements:document.querySelectorAll('#root *').length,heap_bytes:performance.memory?.usedJSHeapSize ?? null,operation_ms:graph.getState().operation_ms,draw_ms:graph.getState().draw_ms}));
    insist(before.endpoint_counts.NULL_ENDPOINT === 22 && before.endpoint_counts.UNRESOLVED === 75 && before.endpoint_counts.COLLISION === 50, 'Scale adversarial endpoint counts lost');
    insist(before.rendered_node_count <= 1000 && before.rendered_node_count > 0 && before.rendered_node_count === await p.locator('[data-node-id]').count(), 'Rendered window is not bounded or truthful');
    const selected = [];
    for (const id of ['nav:project', 'nav:scale-1455', 'nav:scale-2910']) {
      const reveal = await p.evaluate(id => { const started=performance.now(),ok=graph.reveal(id); return {ok,elapsed_ms:performance.now()-started,dom_elements:document.querySelectorAll('#root *').length,rendered:graph.getState().rendered_node_count}; }, id);
      insist(reveal.ok && reveal.elapsed_ms < 30000, 'Cannot reveal first/middle/last within deadline: ' + id);
      await p.keyboard.press('Enter'); const current = await state(p);
      insist(current.selection?.nav_id === id, 'Revealed node cannot be selected: ' + id);
      const context = current.selection;
      insist(context.source_id === scaleSource && context.snapshot_id === scaleSnapshot && context.occurrence === 0 && context.session_id === current.session_id, 'Scale selection lost full identity');
      insist(current.rendered_ids.includes(id), 'Selected scale identity absent from drawing');
      selected.push({context,reveal});
    }
    const after = await state(p);
    insist(after.node_count === before.node_count && after.relation_count === before.relation_count, 'Window navigation dropped model records');
    const original = JSON.stringify(scale); insist(await p.evaluate(() => JSON.stringify(window.fixture)) === original, 'Scale descriptor mutated');
    await shot(p, 'scale-desktop'); return { total: before.node_count, loaded: before.loaded_node_count, rendered: after.rendered_node_count, metrics, selected };
  }, 1440, scale);
  await check('scale_collapsed_orphan_isolated_and_occurrences', async p => {
    await p.evaluate(() => { graph.reveal('nav:family'); });
    await p.locator('[data-toggle-id="nav:family"]').click();
    insist(!(await state(p)).visible_ids.includes('nav:scale-2910'), 'Collapsed branch stayed logically expanded');
    insist(await p.evaluate(() => graph.reveal('nav:scale-2910')), 'Reveal cannot expand actual collapsed ancestors');
    insist((await state(p)).visible_ids.includes('nav:scale-2910'), 'Revealed descendant absent');
    const contexts = [];
    for (const id of ['nav:orphan', 'nav:isolated', 'nav:collision-0-a', 'nav:collision-0-b', 'nav:hostile']) {
      insist(await p.evaluate(id => graph.reveal(id), id), 'Scale anomaly inaccessible: ' + id);
      await p.keyboard.press('Enter'); contexts.push((await state(p)).selection);
    }
    insist(contexts[2].nav_id !== contexts[3].nav_id && contexts[2].occurrence === 0 && contexts[3].occurrence === 1, 'Duplicate native identities merged occurrences');
    await p.locator('[data-action="relation-previous"]').click();
    const lastRelation = await p.locator('[aria-label="Detalhe da relação"]').textContent();
    insist(lastRelation.includes('nav:scale-rel-1594') && lastRelation.includes('"native_id": null'), 'Last relation occurrence or null native identity lost outside SVG window');
    insist(await p.locator('#root img,#root script,#root iframe,#root a[href]').count() === 0, 'Scale hostile text activated');
    const invalid = await p.evaluate(() => {
      const d = structuredClone(fixture); d.nodes[1455].identity.navigation_id = d.nodes[1454].identity.navigation_id;
      const accepted = graph.setData(d); return {accepted,state:graph.getState()};
    });
    insist(!invalid.accepted && invalid.state.error && invalid.state.visible_ids.length === 0, 'Scale duplicate nav ID not atomically refused');
    return { contexts, duplicate_rejected: true };
  }, 1440, scale);
  await check('scale_pan_zoom_minimap_keyboard', async p => {
    insist(await p.evaluate(() => graph.reveal('nav:scale-1455')), 'Middle node inaccessible');
    const a = await state(p); await p.locator('[data-action="zoom-in"]').click();
    const b = await state(p); insist(b.zoom > a.zoom, 'Scale zoom failed');
    await p.locator('[data-action="pan-right"]').click(); const c = await state(p); insist(c.pan.x !== b.pan.x, 'Scale pan failed');
    const map = p.locator('[data-minimap]'); await map.scrollIntoViewIfNeeded();
    const geometry = await map.evaluate(el => {
      const area=el.getBoundingClientRect(),marks=[...el.querySelectorAll('.f3a-mini-bin')],vb=el.viewBox.baseVal;
      if(!marks.length)return null;
      const boxes=marks.map(mark=>mark.getBoundingClientRect()),left=Math.min(...boxes.map(b=>b.left)),right=Math.max(...boxes.map(b=>b.right));
      const target=marks[Math.floor(marks.length/2)],box=target.getBoundingClientRect(),b=target.getBBox();
      return {css_width:area.width,plotted_width:right-left,bins:marks.length,sum:marks.reduce((n,m)=>n+Number(m.getAttribute('data-bin-count')),0),
        target:{client_x:box.x+box.width/2,client_y:box.y+box.height/2,world_x:b.x+b.width/2,world_y:b.y+b.height/2},
        bounds:{left:vb.x+20,top:vb.y+20,right:vb.x+vb.width-20,bottom:vb.y+vb.height-20}};
    });
    insist(geometry && geometry.css_width>0 && geometry.plotted_width>geometry.css_width*.5, 'Tall scale minimap marks do not occupy useful CSS width: '+JSON.stringify(geometry));
    insist(geometry.sum===2911 && geometry.bins<=2048, 'Minimap bin counts lost or duplicated node occurrences');
    await p.mouse.click(geometry.target.client_x,geometry.target.client_y); const d = await state(p);
    const center = await p.evaluate(() => {const v=document.querySelector('svg[data-f3a-canvas]').viewBox.baseVal,s=graph.getState();return {x:(v.width/2-s.pan.x)/s.zoom,y:(v.height/2-s.pan.y)/s.zoom};});
    const tolerance={x:Math.max(2,(geometry.bounds.right-geometry.bounds.left)*.01),y:Math.max(2,(geometry.bounds.bottom-geometry.bounds.top)*.01)};
    insist(center.x>=geometry.bounds.left && center.x<=geometry.bounds.right && center.y>=geometry.bounds.top && center.y<=geometry.bounds.bottom, 'Minimap click centered camera outside graph bounds: '+JSON.stringify({center,geometry}));
    insist(Math.abs(center.x-geometry.target.world_x)<=tolerance.x && Math.abs(center.y-geometry.target.world_y)<=tolerance.y, 'Minimap click did not navigate to clicked bin: '+JSON.stringify({center,geometry}));
    insist(d.pan.x !== c.pan.x || d.pan.y !== c.pan.y, 'Scale minimap navigation failed');
    insist(d.minimap_bin_count <= 2048 && d.minimap_node_count === d.visible_ids.length, 'Minimap discarded semantic nodes or drew unbounded bins');
    await p.evaluate(() => graph.reveal('nav:scale-1455')); await p.keyboard.press('Home');
    let k = await state(p); insist(await p.evaluate(() => document.activeElement?.getAttribute('data-node-id')) === k.visible_ids[0], 'Scale Home failed');
    await p.keyboard.press('End'); k = await state(p);
    insist(await p.evaluate(() => document.activeElement?.getAttribute('data-node-id')) === k.visible_ids.at(-1), 'Scale End failed');
    await p.keyboard.press('ArrowUp'); await p.keyboard.press('ArrowDown'); await p.keyboard.press('Enter');
    insist((await state(p)).selection?.nav_id === k.visible_ids.at(-1), 'Scale arrows/Enter failed');
    await p.keyboard.press('Escape'); insist((await state(p)).selection === null, 'Scale Escape failed');
    await p.keyboard.press('Tab'); insist(await p.evaluate(() => document.activeElement !== document.body), 'Scale Tab focus lost');
    await p.locator('[data-action="fit"]').click(); const fitted = await state(p);
    insist(fitted.zoom > 0 && Number.isFinite(fitted.pan.x) && fitted.rendered_node_count <= 1000, 'Scale fit or window budget failed');
    return { zoom: fitted.zoom, rendered: fitted.rendered_node_count, minimap_bins: fitted.minimap_bin_count, minimap_geometry:geometry, click_camera_center:center };
  }, 1440, scale);
  for (const width of [390, 320]) await check('scale_responsive_' + width, async p => {
    const sizes = await p.evaluate(() => ({scroll:document.documentElement.scrollWidth,inner:innerWidth}));
    insist(sizes.scroll <= width, 'Scale layout horizontal overflow at ' + width);
    const finder = p.locator('[data-navigation-index]');
    await finder.fill('nav:scale-2910'); await p.locator('[data-action="locate"]').click();
    insist((await state(p)).rendered_ids.includes('nav:scale-2910'), 'Index cannot reveal last node at ' + width);
    await p.locator('[data-node-id="nav:scale-2910"]').focus(); await p.keyboard.press('Enter');
    const before = await state(p);
    await shot(p, 'scale-mobile-' + width);
    await p.setViewportSize({width:width===320?390:320,height:800}); await p.waitForTimeout(80);
    const after = await state(p);
    insist(after.selection?.nav_id === before.selection.nav_id && after.zoom === before.zoom, 'Scale responsive reflow lost selection/zoom');
    insist(await p.evaluate(() => document.activeElement?.getAttribute('data-node-id')) === 'nav:scale-2910', 'Scale responsive reflow lost focus');
    return { sizes, rendered: after.rendered_node_count, selection: after.selection };
  }, width, scale);
  await check('scale_stale_ttl_snapshot_dispose', async p => {
    await p.evaluate(() => graph.reveal('nav:scale-1455')); await p.keyboard.press('Enter'); const old = (await state(p)).selection;
    const result = await p.evaluate(ctx => {
      const accepted = graph.setData(structuredClone(fixture)), fresh = graph.getState();
      return {accepted,stale:graph.select(ctx),fresh};
    }, old);
    insist(result.accepted && !result.stale && result.fresh.session_id !== old.session_id && result.fresh.selection === null, 'Scale stale session admitted');
    const crossed = await p.evaluate(ctx => {
      const d=structuredClone(fixture); d.source.source_id='synthetic-scale-other-source'; d.snapshot.snapshot_id='synthetic-scale-other-snapshot';
      const fix=r=>{ if(r.source_id)r.source_id=d.source.source_id; if(r.snapshot_id)r.snapshot_id=d.snapshot.snapshot_id; };
      d.nodes.forEach(n=>{fix(n.parent);if(n.external_reference)fix(n.external_reference);});
      d.relations.forEach(r=>{fix(r.from);fix(r.to);});
      const accepted=graph.setData(d),fresh=graph.getState();
      return {accepted,wrong_context:graph.select({...ctx,session_id:fresh.session_id}),session:fresh.session_id};
    }, old);
    insist(crossed.accepted && !crossed.wrong_context, 'Scale cross-source/snapshot textual identity resolved');
    const ttl = await p.evaluate(() => {
      fixtureNow = Date.parse('2026-10-31T10:02:00Z'); graph.reveal('nav:scale-2910');
      return graph.getState();
    });
    insist(ttl.error && ttl.selection === null && ttl.visible_ids.length === 0, 'Scale TTL retained live data');
    await p.evaluate(() => graph.dispose()); insist(await p.locator('#root').textContent() === '', 'Scale dispose left DOM');
    return { stale_rejected:true, cross_source_snapshot_rejected:true, ttl_error:ttl.error, disposed:true };
  }, 1440, scale);

  await check('scale_descriptor_stress_and_metrics', async p => {
    const specifications = [
      {nodes:10000,relations:0,required:true},
      {nodes:10000,relations:100000,required:false},
      {nodes:10001,relations:0,required:false},
      {nodes:2,relations:100001,required:false}
    ];
    const results = [];
    for (const item of specifications) {
      await checkpoint('stress:start',item);
      const result = await deadline('Stress '+item.nodes+'/'+item.relations,p.evaluate(({nodes,relations}) => {
        // Construct one full synthetic descriptor in the renderer. Only counts cross CDP.
        // The pure factory is a fixed local harness module, never imported by the component.
        const constructionStart=performance.now(),descriptor=window.stressFixture(fixture,nodes,relations);
        const descriptor_bytes=new TextEncoder().encode(JSON.stringify(descriptor)).byteLength;
        const construction_ms=performance.now()-constructionStart;
        const heap = () => performance.memory ? performance.memory.usedJSHeapSize : null;
        const beforeHeap=heap(),started=performance.now(),accepted=graph.setData(descriptor),s=graph.getState();
        return {nodes,relations,descriptor_bytes,construction_ms,accepted,error:s.error,duration_ms:performance.now()-started,before_heap_bytes:beforeHeap,after_heap_bytes:heap(),dom_elements:document.querySelectorAll('#root *').length,rendered_nodes:s.rendered_node_count,rendered_relations:s.rendered_relation_count,visible:s.visible_ids.length,node_count:s.node_count,relation_count:s.relation_count,text:document.querySelector('#root').textContent.slice(0,400)};
      }, item),60000);
      results.push(result); await checkpoint('stress:end',result);
      insist(result.duration_ms < 30000, 'Scale stress deadline exceeded');
      if (item.required) insist(result.accepted && result.node_count === item.nodes && result.relation_count === item.relations, 'Required within-envelope node stress refused: '+JSON.stringify(result));
      if (item.nodes > 10000 || item.relations > 100000) insist(!result.accepted && result.error && result.visible===0, 'Descriptor envelope overflow admitted');
      if (!result.accepted) insist(result.error && result.visible===0 && result.text.length>0, 'Stress refusal was not atomic/visible');
      else insist(result.rendered_nodes<=1000 && result.rendered_relations<=4000, 'Scale stress drawing unbounded');
    }
    return { results, memory_scope:'Observed Chromium usedJSHeapSize when exposed; not a hard 256MiB browser heap qualification', deadline_ms:30000, transport:'Counts only via CDP; complete synthetic descriptors constructed sequentially in renderer from fixed local test module' };
  }, 1440, scale);

} catch(e) { report.fatal=String(e.stack||e); }
finally {
  await checkpoint('cleanup:start');
  if(browser) {try {await deadline('Browser close',browser.close(),10000);} catch(e) {report.fatal=(report.fatal?report.fatal+'; ':'')+String(e.stack||e);} }
  server.closeAllConnections();
  try {await deadline('Server close',new Promise(r=>server.close(r)),5000);} catch(e) {report.fatal=(report.fatal?report.fatal+'; ':'')+String(e.stack||e);}
  clearTimeout(watchdog);
  report.active_stage='complete';
  report.passed=!report.fatal && report.checks.length===24 && report.checks.every(c=>c.passed) && report.outside_requests.length===0 && report.page_errors.length===0 && report.storage_calls.length===0;
  await writeFile(join(out,'browser-receipt.json'),JSON.stringify(report,null,2)+'\n');
}
await new Promise(resolve=>process.stdout.write(JSON.stringify(report,null,2)+'\n',resolve));
// Browser/driver crashes may leave handles; terminal status always reflects the complete receipt.
process.exit(report.passed?0:1);
