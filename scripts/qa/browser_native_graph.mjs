/* Isolated, local-only graph acceptance harness. All displayed data is invented.
 * Usage: node scripts/qa/browser_native_graph.mjs --report-dir <directory>
 * Optional: --static-root <static directory> --playwright-path <absolute package>
 *           --baseline-ref <git revision> (captures/measurements only)
 */
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';

const require = createRequire(import.meta.url);
const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) args.set(process.argv[i], process.argv[i + 1]);
const repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const staticRoot = path.resolve(args.get('--static-root') || path.join(repo, 'packages/atlas/src/atlas_viewer/static'));
assert.ok(args.get('--report-dir'), '--report-dir is required');
const reportDir = path.resolve(args.get('--report-dir'));
const baselineRef = args.get('--baseline-ref');
const prefix = baselineRef ? 'before' : 'after';
const {chromium} = require(args.get('--playwright-path') || 'playwright');
const report = {status:'FAIL', scope:'ISOLATED_NATIVE_GRAPH_SYNTHETIC_ONLY', tested_sha:null,
  baseline_ref:baselineRef || null, checks:[], metrics:{}, errors:[], external_requests:[], screenshots:[],
  performance_guidance_ms:{mount:1000,interaction_p95:100,product_sla:false},
  timing_scope:'Synchronous graph handlers plus forced SVG layout; browser startup, network and asynchronous paint excluded',performance_observations:[]};
const check = name => report.checks.push(name);
await fs.mkdir(reportDir, {recursive:true});
try { report.tested_sha = execFileSync('git', ['rev-parse', 'HEAD'], {cwd:repo, encoding:'utf8'}).trim(); }
catch { report.tested_sha = 'UNAVAILABLE'; }
const sourceAt = (name) => baselineRef
  ? Promise.resolve(execFileSync('git', ['show', `${baselineRef}:packages/atlas/src/atlas_viewer/static/${name}`], {cwd:repo, encoding:'utf8'}))
  : fs.readFile(path.join(staticRoot, name), 'utf8');
const [graphSource, graphCSS] = await Promise.all([sourceAt('native_graph.js'), sourceAt('native_notebook.css')]);
report.source_sha256 = {native_graph_js:createHash('sha256').update(graphSource).digest('hex'),
  native_notebook_css:createHash('sha256').update(graphCSS).digest('hex')};
if (!baselineRef) {
  try { report.tested_files_dirty = execFileSync('git', ['status','--porcelain','--','packages/atlas/src/atlas_viewer/static/native_graph.js','packages/atlas/src/atlas_viewer/static/native_notebook.css'], {cwd:repo,encoding:'utf8'}).trim().length>0; }
  catch { report.tested_files_dirty = null; }
}

const fixtureScript = `import {mountGraph} from '/native_graph.js';
const node=(uid,title,parent_uid=null,extra={})=>({uid,title,parent_uid,native_id:null,source_key:uid,group:'Inventado',...extra});
function fixture(kind){
  if(kind==='star')return [node('root','Família'),node('child','Execução','root',{native_id:'R1'}),
    ...Array.from({length:1200},(_,i)=>node('node-'+i,i===1199?'Último nó da coleção':'Nó sintético '+i,'root',{native_id:'native-'+i}))];
  if(kind==='identity')return [
    node('identity-root','Raiz sem ID'),
    node('duplicate-a','Ocorrência com ID repetido A','identity-root',{native_id:'same',source_key:'source-a'}),
    node('duplicate-b','Ocorrência com ID repetido B','identity-root',{native_id:'same',source_key:'source-b'}),
    node('null','ID nulo preservado','duplicate-a',{source_key:'native:null',native_id:null}),
    node('orphan','Pai ausente preservado','missing-parent'),
    node('cycle-a','Ciclo declarado A','cycle-b'),node('cycle-b','Ciclo declarado B','cycle-a'),
    node('self-cycle','Ciclo próprio declarado','self-cycle')];
  const result=[node('forest','Coleção de engenharia · dados inteiramente sintéticos')];
  for(let b=0;b<10;b++){
    result.push(node('branch-'+b,'Ramo '+(b+1)+' · séries de engenharia','forest',{native_id:'F-'+b}));
    for(let i=0;i<290;i++)result.push(node('leaf-'+b+'-'+i,'Amostra '+(i+1)+' do ramo '+(b+1)+' · descrição sintética legível','branch-'+b,
      {native_id:i%11===0?null:'DUP-'+(i%7),source_key:'source-'+b+'-'+i}));
  }
  return result;
}
window.nodes=fixture(new URL(location.href).searchParams.get('dataset')||'star');
window.inputBefore=JSON.stringify(window.nodes);window.selections=[];window.gestureEvents=[];window.gestureTimes=[];
for(const type of ['click','dblclick'])document.addEventListener(type,event=>{
  if(event.target.closest?.('.graph-node')){window.gestureEvents.push(type+':'+event.detail);window.gestureTimes.push(performance.now());}
},{capture:true});
const mountStart=performance.now();
window.graph=mountGraph(document.querySelector('#graph-host'),window.nodes,n=>{
  window.selections.push(n);document.querySelector('#selected').textContent=n.title;
  window.gestureEvents.push('select');
  if(new URL(location.href).searchParams.has('reflow')&&window.selections.length===1)document.querySelector('#graph-host').style.maxWidth='760px';
});
window.mountDuration=performance.now()-mountStart;
window.ready=true;`;
const harnessCSS = `body{margin:0;background:#f4f7f4;color:#193a3d;font:15px/1.5 system-ui}main{padding:24px;max-width:1440px;margin:auto;width:100%;box-sizing:border-box}h1{margin:0 0 8px;font-size:24px}p{margin:0 0 16px;color:#526b61}#selected{margin-top:12px;overflow-wrap:anywhere;font-size:14px}@media(max-width:720px){main{padding:14px}h1{font-size:20px}}`;
const html = `<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Atlas · teste sintético do grafo</title><link rel="stylesheet" href="/native_notebook.css"><link rel="stylesheet" href="/harness.css"><main><h1>Atlas · árvore estrutural</h1><p>Acervo de engenharia inventado · nenhuma informação científica privada.</p><div id="graph-host"></div><output id="selected" aria-label="Ocorrência selecionada"></output></main><script type="module" src="/harness.js"></script></html>`;
const responses = new Map([
  ['/', ['text/html; charset=utf-8', html]],
  ['/native_graph.js', ['text/javascript; charset=utf-8', graphSource]],
  ['/native_notebook.css', ['text/css; charset=utf-8', graphCSS]],
  ['/harness.js', ['text/javascript; charset=utf-8', fixtureScript]],
  ['/harness.css', ['text/css; charset=utf-8', harnessCSS]],
]);
const server = http.createServer((request,response) => {
  const pathname = new URL(request.url, 'http://127.0.0.1').pathname;
  const resource = responses.get(pathname);
  response.setHeader('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none'");
  response.setHeader('Cache-Control', 'no-store');
  if (!resource) { response.writeHead(404); response.end(); return; }
  response.writeHead(200, {'Content-Type':resource[0]}); response.end(resource[1]);
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
let browser, context, failure;
try {
  browser = await chromium.launch({headless:true});
  context = await browser.newContext({viewport:{width:1440,height:1000}});
  await context.route('**/*', async route => {
    const url = route.request().url();
    if (/^https?:/.test(url) && new URL(url).origin !== origin) {report.external_requests.push(url); await route.abort();}
    else await route.continue();
  });
  const page = await context.newPage();
  page.on('pageerror', error => report.errors.push(error.message));
  const item = uid => page.locator(`[data-native-node="${uid}"]`);
  const selected = () => page.locator('.graph-node[aria-selected="true"]');
  async function open(dataset,viewport={width:1440,height:1000},options={}) {
    await page.setViewportSize(viewport);
    await page.goto(`${origin}/?${new URLSearchParams({dataset,...options})}`, {waitUntil:'networkidle'});
    await page.waitForFunction(() => window.ready);
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  }
  async function capture(name) {
    const filename = `${prefix}-${name}.png`;
    await page.screenshot({path:path.join(reportDir,filename),fullPage:true});
    report.screenshots.push(filename);
  }
  async function geometry() {
    return page.evaluate(() => {
      const cards=[...document.querySelectorAll('.graph-node')].map(n=>{const r=n.getBoundingClientRect();return {width:r.width,height:r.height};});
      return {viewport:{width:innerWidth,height:innerHeight},cards,meta:document.querySelector('.graph-meta')?.textContent,
        focus:document.activeElement?.getAttribute('data-native-node'),overflow:document.documentElement.scrollWidth>innerWidth+1};
    });
  }
  async function locate(uid) {
    await page.evaluate(id => window.graph.locate(id), uid);
    assert.equal(await selected().getAttribute('data-native-node'),uid);
    const r = await item(uid).boundingBox(), view = await page.locator('.graph-svg').boundingBox();
    assert.ok(r&&view&&r.x+r.width>view.x&&r.x<view.x+view.width&&r.y+r.height>view.y&&r.y<view.y+view.height, `Located ${uid} must intersect viewport`);
  }
  async function allReachable(label) {
    const result = await page.evaluate(() => {
      const durations=[], failures=[];
      for (const n of window.nodes) {
        const start=performance.now(); window.graph.locate(n.uid);durations.push(performance.now()-start);
        const selected=document.querySelector('.graph-node[aria-selected="true"]');
        const r=selected?.getBoundingClientRect(),v=document.querySelector('.graph-svg').getBoundingClientRect();
        if(selected?.getAttribute('data-native-node')!==n.uid||!r||r.right<=v.left||r.left>=v.right||r.bottom<=v.top||r.top>=v.bottom)failures.push(n.uid);
      }
      durations.sort((a,b)=>a-b);
      return {total:window.nodes.length,failures,p95_ms:durations[Math.floor(durations.length*.95)],max_ms:durations.at(-1),total_ms:durations.reduce((a,b)=>a+b,0),unchanged:window.inputBefore===JSON.stringify(window.nodes)};
    });
    report.metrics[label] = result;
    assert.deepEqual(result.failures,[], `${label}: every input occurrence is reachable`);
    assert.equal(result.unchanged,true, `${label}: input records must remain unchanged`);
  }
  async function keyFocus(key,expected) {
    await page.keyboard.press(key);
    assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('data-native-node')),expected, `${key} should focus ${expected}`);
  }
  async function measureInteractions(dataset,lastUid) {
    await open(dataset);
    const measurements=await page.evaluate(id=>{
      const before=performance.now();window.graph.locate(id);
      document.querySelector('.graph-svg').getBoundingClientRect();
      return {mount_ms:window.mountDuration,last_locate_ms:performance.now()-before};
    },lastUid);
    // Start expansion from a freshly mounted, progressively collapsed graph.
    await open(dataset);
    Object.assign(measurements,await page.evaluate(()=>{
      const expand=[...document.querySelectorAll('.graph-toolbar button')].find(n=>n.textContent==='Expandir todos');
      let start=performance.now();expand.click();document.querySelector('.graph-svg').getBoundingClientRect();
      const expand_all_ms=performance.now()-start,durations=[],svg=document.querySelector('.graph-svg');
      for(let i=0;i<32;i++){
        start=performance.now();svg.dispatchEvent(new KeyboardEvent('keydown',{key:i%2?'ArrowLeft':'ArrowRight',shiftKey:true,bubbles:true}));
        svg.getBoundingClientRect();durations.push(performance.now()-start);
      }
      durations.sort((a,b)=>a-b);
      return {expand_all_ms,pan_p95_ms:durations[Math.floor(durations.length*.95)],pan_max_ms:durations.at(-1),
        graph_cards_in_dom:document.querySelectorAll('.graph-node').length,mini_nodes:document.querySelectorAll('.graph-mini-node').length};
    }));
    report.metrics[`benchmark_${dataset}`]=measurements;
    if(measurements.mount_ms>1000||measurements.pan_p95_ms>100)
      report.performance_observations.push(`${dataset}: host exceeded engineering guidance; inspect measurements (not a product SLA)`);
    if(!baselineRef){
      assert.ok(measurements.mount_ms<1000,`${dataset}: graph mount exceeded the 1000 ms engineering gate`);
      assert.ok(measurements.pan_p95_ms<100,`${dataset}: pan p95 exceeded the 100 ms engineering gate`);
    }
  }

  await open('star');
  assert.equal(await page.locator('iframe').count(),0);
  report.metrics.star_initial = await geometry();
  await capture('star-desktop');
  assert.match(await page.locator('.graph-meta').innerText(),/1202 nós carregados/);
  assert.match(await page.locator('.graph-meta').innerText(),/25 no foco atual/);
  await page.getByRole('button',{name:'Mostrar mais nós +24',exact:true}).click();
  assert.match(await page.locator('.graph-meta').innerText(),/49 no foco atual/);
  check('pr24_progressive_25_then_49_and_full_population_retained');
  await locate('node-1199');
  assert.equal(await page.evaluate(()=>window.selections.at(-1).native_id),'native-1199');
  check('last_of_1202_locatable_outside_initial_window');

  if (!baselineRef) {
    const root=()=>item('root');
    await locate('root');await root().focus();
    await root().dblclick();assert.equal(await root().getAttribute('aria-expanded'),'false');
    await root().dblclick();assert.equal(await root().getAttribute('aria-expanded'),'true');
    await root().focus();await page.keyboard.press('Space');assert.equal(await root().getAttribute('aria-expanded'),'false');
    await page.keyboard.press('Space');assert.equal(await root().getAttribute('aria-expanded'),'true');
    assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('data-native-node')),'root');
    check('double_click_space_and_stable_focus');
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.evaluate(()=>document.activeElement?.getAttribute('data-native-node')),'child');
    await keyFocus('ArrowDown','node-0');await keyFocus('ArrowUp','child');
    await keyFocus('ArrowLeft','root');await keyFocus('End','node-1199');await keyFocus('Home','root');
    await page.keyboard.press('Enter');assert.equal(await selected().getAttribute('data-native-node'),'root');
    check('tree_keyboard_right_left_up_down_home_end_enter');
    const search = page.getByRole('searchbox',{name:'Localizar nó na árvore'});
    await search.fill('Último nó da coleção');await search.press('Enter');
    assert.equal(await selected().getAttribute('data-native-node'),'node-1199');
    assert.match(await page.locator('.graph-path').innerText(),/Família/);
    assert.match(await page.locator('.graph-path').innerText(),/Último nó da coleção/);
    await search.fill('não existe este nó 12345');await search.press('Enter');
    assert.match(await page.locator('.graph-search-status').innerText(),/nenhum|0.*result|não encontrado/i);
    assert.equal(await selected().getAttribute('data-native-node'),'node-1199');
    check('search_result_ancestral_path_and_empty_search_feedback');
    const transform=()=>page.locator('.graph-svg > g').getAttribute('transform');
    const beforeZoom=await transform();
    await page.getByRole('button',{name:'Ampliar +',exact:true}).click();assert.notEqual(await transform(),beforeZoom);
    const svg=await page.locator('.graph-svg').boundingBox();
    await page.mouse.move(svg.x+svg.width-15,svg.y+svg.height-15);await page.mouse.down();
    const beforePan=await transform();await page.mouse.move(svg.x+svg.width-65,svg.y+svg.height-65,{steps:4});await page.mouse.up();
    assert.notEqual(await transform(),beforePan);
    await page.mouse.wheel(0,-120);assert.notEqual(await transform(),beforePan);
    for(let i=0;i<20;i++)await page.getByRole('button',{name:'Reduzir −',exact:true}).click();
    const minZoom=await page.locator('.graph-svg > g').getAttribute('transform');
    const zoom=Number(minZoom.match(/scale\(([^)]+)\)/)?.[1]);
    report.metrics.desktop_min_zoom=zoom;assert.ok(zoom>=.75,'Desktop zoom must not make cards microscopic');
    await page.getByRole('button',{name:'Ajustar',exact:true}).click();
    assert.ok(await page.locator('.graph-mini-node').count()>0,'Minimap must depict graph nodes');
    const mini=page.locator('.graph-mini');const beforeMini=await transform();await mini.click({position:{x:150,y:60}});
    assert.notEqual(await transform(),beforeMini);
    check('mouse_pan_wheel_zoom_floor_and_minimap_nodes');
    await allReachable('star_all_1202');
    await page.getByRole('button',{name:'Ajustar',exact:true}).click();
    await item('node-1199').focus();
    const focusGeometry=await item('node-1199').boundingBox(),focusViewport=await page.locator('.graph-svg').boundingBox();
    assert.ok(focusGeometry.y+focusGeometry.height>focusViewport.y&&focusGeometry.y<focusViewport.y+focusViewport.height,'A retained keyboard focus target must return to the camera after fit');
    check('focus_of_retained_offscreen_node_recenters_after_fit');
  }
  await open('branches');
  assert.equal(await page.evaluate(()=>window.nodes.length),2911);
  report.metrics.branches_initial=await geometry();await capture('branches-desktop');
  if (!baselineRef) {
    assert.equal(report.metrics.branches_initial.overflow,false);
    assert.ok(report.metrics.branches_initial.cards.every(r=>r.width>=200&&r.height>=52),'Desktop cards must remain comfortably readable');
    await locate('leaf-9-289');
    assert.match(await page.locator('.graph-path').innerText(),/Coleção de engenharia/);
    assert.match(await page.locator('.graph-path').innerText(),/Ramo 10/);
    await capture('branches-selected-desktop');
    await allReachable('branches_all_2911');
    check('all_2911_synthetic_branches_reachable_and_immutable');
  }
  await open('branches',{width:390,height:844});
  report.metrics.mobile_initial=await geometry();await capture('branches-mobile');
  if (!baselineRef) {
    assert.equal(report.metrics.mobile_initial.overflow,false);
    await locate('leaf-9-289');
    for(let i=0;i<20;i++)await page.getByRole('button',{name:'Reduzir −',exact:true}).click();
    const zoom=Number((await page.locator('.graph-svg > g').getAttribute('transform')).match(/scale\(([^)]+)\)/)?.[1]);
    report.metrics.mobile_min_zoom=zoom;assert.ok(zoom>=.85,'Mobile zoom floor must preserve readable card text');
    await locate('leaf-9-289');
    const crumb=await page.locator('.graph-path [aria-current="location"]').boundingBox(),crumbViewport=await page.locator('.graph-path').boundingBox();
    assert.ok(crumb&&crumbViewport&&crumb.x<crumbViewport.x+crumbViewport.width&&crumb.x+crumb.width>crumbViewport.x,'Selected ancestor breadcrumb must be brought into the mobile path window');
    await capture('branches-selected-mobile');
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true);
    check('mobile_390_navigation_zoom_floor_and_no_document_overflow');
  }
  await open('star',{width:390,height:844});await capture('star-mobile');
  if (!baselineRef) {
    await open('identity');await allReachable('identity_cycles_null_collisions');
    await locate('duplicate-a');assert.equal(await page.evaluate(()=>window.selections.at(-1).source_key),'source-a');
    await locate('duplicate-b');assert.equal(await page.evaluate(()=>window.selections.at(-1).source_key),'source-b');
    await locate('null');assert.equal(await page.evaluate(()=>window.selections.at(-1).native_id),null);
    await locate('cycle-a');assert.match(await page.locator('.graph-meta').innerText(),/3 nós em ciclo/);
    assert.equal(await page.evaluate(()=>window.inputBefore===JSON.stringify(window.nodes)),true);
    check('null_ids_colliding_native_ids_orphans_and_declared_cycles_preserved');
    // Opening the notebook detail pane changes graph width. The first click of a
    // double click must not invoke that callback and move the second-click target.
    report.metrics.single_click_callback_latency_ms=[];
    for(const gap of [0,450]){
      await open('star',undefined,{reflow:'1'});
      const initialHostWidth=await page.locator('#graph-host').evaluate(n=>n.getBoundingClientRect().width);
      if(gap===0)await item('root').dblclick();
      else{
        // Locator.dblclick({delay}) delays each down/up as well as the gap,
        // doubling time between click events. Send the intended 450 ms gap.
        const rect=await item('root').boundingBox();await page.mouse.move(rect.x+rect.width/2,rect.y+rect.height/2);
        await page.mouse.down({clickCount:1});await page.mouse.up({clickCount:1});await page.waitForTimeout(gap);
        await page.mouse.down({clickCount:2});await page.mouse.up({clickCount:2});
        const actualGap=await page.evaluate(()=>window.gestureTimes[1]-window.gestureTimes[0]);
        report.metrics.slow_double_click_gap_ms=actualGap;assert.ok(actualGap>=440);
      }
      await page.waitForTimeout(100);
      assert.equal(await item('root').getAttribute('aria-expanded'),'false');
      assert.deepEqual(await page.evaluate(()=>window.gestureEvents),['click:1','click:2','dblclick:2','select'],'Fresh double click must finish before its selection callback opens a detail pane');
      assert.equal(await page.evaluate(()=>window.selections.length),1);
      assert.ok(await page.locator('#graph-host').evaluate(n=>n.getBoundingClientRect().width)<initialHostWidth);
      const callbackStart=Date.now();await item('root').click();
      await page.waitForFunction(()=>window.selections.length===2,null,{timeout:1000});
      const latency=Date.now()-callbackStart;report.metrics.single_click_callback_latency_ms.push(latency);assert.ok(latency<1000,'Single click selection callback must settle within one second');
      assert.equal(await selected().getAttribute('data-native-node'),'root');
      await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>window.selections.length),2,'A single click must select exactly once');
    }
    check('fresh_double_click_survives_detail_callback_reflow_and_single_click_selects_once');
    await page.evaluate(()=>window.graph.destroy());assert.equal(await page.locator('#graph-host > *').count(),0);
    check('destroy_removes_graph_and_listeners');
  }
  await measureInteractions('star','node-1199');
  await measureInteractions('branches','leaf-9-289');
  assert.deepEqual(report.errors,[]);assert.deepEqual(report.external_requests,[]);
  check('no_page_errors_or_external_requests');
  report.status=baselineRef?'BASELINE_CAPTURED':'PASS_SCOPED';
} catch(error) { failure=error;report.error=error.stack||error.message; }
finally {
  if(browser)await browser.close();
  await new Promise(resolve=>server.close(resolve));
  await fs.writeFile(path.join(reportDir,`${prefix}-graph-report.json`),JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify(report,null,2));
}
if(failure)process.exitCode=1;
