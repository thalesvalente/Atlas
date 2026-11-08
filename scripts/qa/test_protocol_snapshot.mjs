/** Behavioral state/ordering regressions of the real protocol app; not browser QA. */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import test from 'node:test';

const root = process.env.ATLAS_TEST_REPO || path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const code = fs.readFileSync(path.join(root, 'packages/atlas/src/atlas_viewer/static/app.js'), 'utf8');
const tick = () => new Promise(resolve => setImmediate(resolve));
const itemKey = JSON.stringify(['source-1', 'run']);
const projectKey = JSON.stringify(['source-1', 'project']);
const experimentKey = JSON.stringify(['source-1', 'experiment']);

function catalog(generation=1, indexedAt='2026-01-01T00:00:00Z', sourceName='Synthetic A') {
  return {generation, indexed_at:indexedAt, observed_at:indexedAt, collisions:[], limitations:[],
    sources:[{id:'source-1', name:sourceName, metadata_sha256:sourceName, changed:false,
      report:{valid:true}, read_model:{projects:[{id:'project', name:'Project'}],
        experiments:[{id:'experiment', name:'Experiment'}],
        runs:[{id:'run', name:sourceName, project_id:'project', experiment_id:'experiment', status:'SUCCESS'}]}}]};
}

function harness(saved=null) {
  const nodes = new Map(), requests=[];
  let preferences=saved;
  class Element {
    constructor(tag='div') {this.tagName=tag;this.textContent='';this.value='';this.hidden=false;
      this.disabled=false;this.children=[];this.dataset={};this.classList={toggle(){},add(){},remove(){}};}
    replaceChildren(...children) {this.children=children;}
    append(...children) {this.children.push(...children);}
    addEventListener() {} setAttribute() {} removeAttribute() {}
    querySelectorAll() {return [];} focus() {} scrollIntoView() {}
  }
  const node = id => {if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const sandbox={document:{getElementById:node,createElement:tag=>new Element(tag),
    querySelectorAll:()=>[],addEventListener(){},body:new Element('body')},
    localStorage:{getItem:()=>preferences,setItem:(_,value)=>{preferences=value;}},
    window:{print(){}},URL,setTimeout,
    fetch:(url,options)=>new Promise((resolve,reject)=>requests.push({url,method:options?.method??'GET',resolve,reject}))};
  vm.createContext(sandbox);
  vm.runInContext(code+`\nfor(const name of ['renderRuns','renderComparison','renderTimeline','renderLineage','renderSources','renderDossier'])globalThis[name]=()=>{};
    showDetail=(run)=>{globalThis.presentedDetail=run.name;};
    globalThis.probe={state,updateCatalog,load,savePreferences,restorePreferences,filteredRuns};`,sandbox);
  const respond = (request,data) => request.resolve({ok:true,json:async()=>structuredClone(data)});
  async function ready(data=catalog()) {await tick();respond(requests[0],data);await tick();}
  return {...sandbox.probe,node,requests,respond,ready,saved:()=>preferences};
}

function choose(h) {
  h.state.selected.add(itemKey);h.state.detail=itemKey;
  h.node('detail').hidden=false;h.node('detail-content').textContent='Previous snapshot';
  h.node('project-filter').value=projectKey;h.node('experiment-filter').value=experimentKey;
  h.node('search').value='Synthetic';h.node('status-filter').value='SUCCESS';
}

test('verification keeps the previous snapshot selection, detail and source filters', async () => {
  const h=harness();await h.ready();choose(h);
  const observed=catalog();observed.observed_at='2026-01-02T00:00:00Z';observed.sources[0].changed=true;
  h.updateCatalog(observed);
  assert.deepEqual([...h.state.selected],[itemKey]);assert.equal(h.state.detail,itemKey);
  assert.equal(h.node('project-filter').value,projectKey);
});

test('explicit new epoch clears old identities even when declared IDs and bytes survive', async () => {
  const h=harness();await h.ready();choose(h);
  h.updateCatalog(catalog(2,'2026-01-02T00:00:00Z'));
  assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);
  assert.equal(h.node('detail').hidden,true);
  assert.equal(h.node('project-filter').value,'');assert.equal(h.node('experiment-filter').value,'');
  assert.equal(h.node('search').value,'Synthetic');assert.equal(h.node('status-filter').value,'SUCCESS');
});

test('restarted Catalog cannot inherit identities just because generation restarts at one', async () => {
  const h=harness();await h.ready();choose(h);
  h.updateCatalog(catalog(1,'2026-01-03T00:00:00Z','Synthetic B'));
  assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);
  assert.equal(h.node('project-filter').value,'');
});

test('a changed source invalidates the complete comparison while another source stays intact', async () => {
  const initial=catalog();
  const other=structuredClone(initial.sources[0]);other.id='source-2';other.name='Synthetic B';
  other.metadata_sha256='unchanged-B';other.read_model.runs[0].name='Synthetic B';
  initial.sources.push(other);
  const h=harness();await h.ready(initial);choose(h);
  h.state.selected.add(JSON.stringify(['source-2','run']));
  const updated=structuredClone(initial);updated.generation=2;updated.indexed_at='2026-01-02T00:00:00Z';
  updated.sources[0].metadata_sha256='changed-A';updated.sources[0].read_model.runs[0].name='New A, same declared ID';
  h.updateCatalog(updated);
  assert.equal(h.state.selected.size,0);assert.equal(h.state.detail,null);
  assert.deepEqual(h.state.catalog.sources[1],other);
  assert.equal(h.state.runs.find(run=>run._sourceId==='source-1').name,'New A, same declared ID');
});

test('a reload of the same epoch can restore source-scoped preferences', async () => {
  const h=harness();await h.ready();choose(h);h.savePreferences();
  const reloaded=harness(h.saved());await reloaded.ready();
  assert.equal(reloaded.node('project-filter').value,projectKey);
  assert.equal(reloaded.node('experiment-filter').value,experimentKey);
});

test('a new epoch restores free filters but never source-ordinal preferences', async () => {
  const h=harness();await h.ready();choose(h);h.savePreferences();
  const next=harness(h.saved());await next.ready(catalog(1,'2026-01-03T00:00:00Z','Synthetic B'));
  assert.equal(next.node('project-filter').value,'');assert.equal(next.node('experiment-filter').value,'');
  assert.equal(next.node('search').value,'Synthetic');assert.equal(next.node('status-filter').value,'SUCCESS');
});

test('legacy preferences without a snapshot binding do not rebind ordinal source IDs', async () => {
  const h=harness(JSON.stringify({query:'Synthetic',status:'SUCCESS',project:projectKey,experiment:experimentKey}));
  await h.ready();assert.equal(h.node('project-filter').value,'');assert.equal(h.node('experiment-filter').value,'');
  assert.equal(h.node('search').value,'Synthetic');
});

test('verification requested during rebuild waits for the completed rebuild', async () => {
  const h=harness();await h.ready();const rebuilt=catalog(2,'2026-01-02T00:00:00Z','Synthetic B');
  const post=h.load(true);await tick();const get=h.load(false);await tick();
  assert.equal(h.requests.length,2,'Only initial GET and active POST may be in flight');
  assert.equal(h.requests[1].method,'POST');assert.equal(h.node('refresh').disabled,true);
  h.respond(h.requests[1],rebuilt);await post;await tick();
  assert.equal(h.requests.length,3);assert.equal(h.requests[2].method,'GET');
  h.respond(h.requests[2],rebuilt);await get;
  assert.equal(h.state.catalog.generation,2);assert.equal(h.state.runs[0].name,'Synthetic B');
  assert.equal(h.node('refresh').disabled,false);
});

test('rebuild requested during a verification is preserved and runs afterward', async () => {
  const h=harness();await h.ready();const get=h.load(false);await tick();const post=h.load(true);await tick();
  assert.equal(h.requests.length,2);assert.equal(h.requests[1].method,'GET');
  h.respond(h.requests[1],catalog());await get;await tick();
  assert.equal(h.requests[2].method,'POST');h.respond(h.requests[2],catalog(2,'2026-01-02T00:00:00Z'));
  await post;assert.equal(h.state.catalog.generation,2);
});

test('failed verification does not strand a queued explicit rebuild', async () => {
  const h=harness();await h.ready();const get=h.load(false);await tick();const post=h.load(true);await tick();
  h.requests[1].reject(new Error('synthetic transport failure'));await get;await tick();
  assert.equal(h.requests[2].method,'POST');h.respond(h.requests[2],catalog(2,'2026-01-02T00:00:00Z'));
  await post;assert.equal(h.state.catalog.generation,2);assert.equal(h.node('refresh').disabled,false);
});
