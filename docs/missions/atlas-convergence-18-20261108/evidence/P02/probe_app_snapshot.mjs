/** Run the real C0 state transition; stub rendering only. This is not browser QA. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';

const AREA=path.dirname(fileURLToPath(import.meta.url));
const REPO=path.resolve(AREA,'../../repo');
const app=fs.readFileSync(path.join(REPO,'packages/atlas/src/atlas_viewer/static/app.js'),'utf8');
const scenarios=JSON.parse(fs.readFileSync(path.join(AREA,'catalog_scenarios.json'),'utf8'));
const nodes=new Map();
class Element {
  constructor(tag='div'){this.tagName=tag.toUpperCase();this.textContent='';this.value='';this.hidden=false;this.disabled=false;this.children=[];this.dataset={};this.classList={toggle(){},add(){},remove(){}};}
  replaceChildren(...children){this.children=children;}
  append(...children){this.children.push(...children);}
  addEventListener(){}
  setAttribute(){}
  removeAttribute(){}
  querySelectorAll(){return[];}
  focus(){}
  scrollIntoView(){}
}
const node=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
const sandbox={document:{getElementById:node,createElement:tag=>new Element(tag),querySelectorAll:()=>[],addEventListener(){},body:new Element('body')},
  localStorage:{getItem:()=>null,setItem(){}},window:{print(){}},fetch:()=>new Promise(()=>{}),URL,setTimeout};
vm.createContext(sandbox);
vm.runInContext(app+`\nfor(const name of ['renderRuns','renderComparison','renderTimeline','renderLineage','renderSources','renderDossier'])globalThis[name]=()=>{};\nshowDetail=(run)=>{globalThis.detailPresented=run.name;};globalThis.probe={state,updateCatalog};`,sandbox);
const {state,updateCatalog}=sandbox.probe;
const firstA=scenarios.initial.sources[0].read_model.runs[0],firstB=scenarios.initial.sources[1].read_model.runs[0];
const selected=[JSON.stringify(['source-1',firstA.id]),JSON.stringify(['source-2',firstB.id])];
const reports=[];
function prime(){updateCatalog(structuredClone(scenarios.initial));state.selected=new Set(selected);state.detail=selected[0];}
function observe(label,catalog){
  prime();updateCatalog(structuredClone(catalog));
  reports.push({name:label,selected:[...state.selected],detail:state.detail,detailPresented:sandbox.detailPresented,notice:node('notice').textContent,
    catalog_generation:state.catalog.generation,source_A_hash:state.catalog.sources[0].metadata_sha256});
}
observe('same_bytes_rebuild',scenarios.unchanged_rebuild);
observe('GET_verification_before_explicit_rebuild',scenarios.verify_changed);
observe('explicit_changed_rebuild_same_source_id_and_run_id',scenarios.changed_rebuild);
observe('fresh_Catalog_session_same_positional_ids',scenarios.restarted);
assert.deepEqual(reports[0].selected,selected);
assert.deepEqual(reports[1].selected,selected);
assert.deepEqual(reports[2].selected,selected);
assert.equal(reports[2].detail,selected[0]);
assert.equal(reports[2].detailPresented,'P02_CHANGED_SAME_ID');
assert.deepEqual(reports[3].selected,selected);
const result={status:'BASELINE_DEFECT_REPRODUCED',scope:'actual app.js updateCatalog in Node VM with presentation-only stubs; NOT browser QA',baseline_sha:'8f8fe01c3041361aa2607194d66af6a640d834ad',
  defect:'P02-F001: explicit snapshot replacement silently carries old source+ID comparison selections and opens replacement detail',
  expected_on_changed_snapshot:{selected:[],detail:null},observations:reports};
fs.writeFileSync(path.join(AREA,'app-snapshot-probe.json'),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify(result,null,2));
