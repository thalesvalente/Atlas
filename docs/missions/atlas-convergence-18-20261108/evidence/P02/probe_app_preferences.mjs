/** Real C0 save/restore/filter functions across two synthetic Catalog sessions. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const AREA=path.dirname(fileURLToPath(import.meta.url)),REPO=path.resolve(AREA,'../../repo');
const app=fs.readFileSync(path.join(REPO,'packages/atlas/src/atlas_viewer/static/app.js'),'utf8');
const scenarios=JSON.parse(fs.readFileSync(path.join(AREA,'catalog_scenarios.json'),'utf8'));
const storage=new Map();
class Element {
  constructor(tag='div'){this.tagName=tag;this.textContent='';this.value='';this.children=[];this.dataset={};this.classList={toggle(){},add(){},remove(){}};}
  replaceChildren(...children){this.children=children;}append(...children){this.children.push(...children);}
  addEventListener(){}setAttribute(){}removeAttribute(){}querySelectorAll(){return[];}focus(){}scrollIntoView(){}
}
function session(catalog){
  const nodes=new Map(),node=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
  const sandbox={document:{getElementById:node,createElement:tag=>new Element(tag),querySelectorAll:()=>[],addEventListener(){},body:new Element('body')},
    localStorage:{getItem:key=>storage.get(key)??null,setItem:(key,value)=>storage.set(key,value)},window:{print(){}},fetch:()=>new Promise(()=>{}),URL,setTimeout};
  vm.createContext(sandbox);vm.runInContext(app+`\nfor(const name of ['renderRuns','renderComparison','renderTimeline','renderLineage','renderSources','renderDossier'])globalThis[name]=()=>{};showDetail=()=>{};globalThis.probe={state,updateCatalog,savePreferences,filteredRuns};`,sandbox);
  sandbox.probe.updateCatalog(structuredClone(catalog),true);return{...sandbox.probe,node};
}
const old=session(scenarios.changed_rebuild),oldSource=scenarios.changed_rebuild.sources[0];
const project=JSON.stringify(['source-1',oldSource.read_model.projects[0].id]);
const experiment=JSON.stringify(['source-1',oldSource.read_model.experiments[0].id]);
old.node('project-filter').value=project;old.node('experiment-filter').value=experiment;
old.node('search').value='run';old.node('status-filter').value='';old.savePreferences();
const selectedBefore=old.filteredRuns().map(run=>({source:run._sourceId,id:run.id,name:run.name}));
const next=session(scenarios.reordered_restart);
const selectedAfter=next.filteredRuns().map(run=>({source:run._sourceId,id:run.id,name:run.name}));
assert.equal(next.node('project-filter').value,project);
assert.equal(next.node('experiment-filter').value,experiment);
assert.equal(selectedBefore[0].id,selectedAfter[0].id);
assert.equal(selectedBefore[0].name,'P02_CHANGED_SAME_ID');
assert.notEqual(selectedAfter[0].name,selectedBefore[0].name);
assert.equal(scenarios.changed_rebuild.sources[0].metadata_sha256,scenarios.reordered_restart.sources[1].metadata_sha256);
const result={status:'BASELINE_PREFERENCE_REBIND_REPRODUCED',baseline_sha:'8f8fe01c3041361aa2607194d66af6a640d834ad',scope:'actual app.js savePreferences/restorePreferences/filteredRuns in VM; public synthetic Catalog DTOs; not browser QA',
  defect:'P02-F003: persisted source-N project/experiment filters silently bind to another package after source ordering changes across sessions',
  stored:JSON.parse(storage.get('atlas.preferences.v1')),selectedBefore,selectedAfter,
  expected:'Retain source-agnostic query/status, restore source-scoped filters only under the same catalog epoch; otherwise reset them explicitly.'};
fs.writeFileSync(path.join(AREA,'app-preferences-probe.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
