/** Actual load/updateCatalog with controlled fetch resolution; no HTTP/browser claim. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
const AREA=path.dirname(fileURLToPath(import.meta.url)),REPO=path.resolve(AREA,'../../repo');
const app=fs.readFileSync(path.join(REPO,'packages/atlas/src/atlas_viewer/static/app.js'),'utf8');
const scenarios=JSON.parse(fs.readFileSync(path.join(AREA,'catalog_scenarios.json'),'utf8'));
const requests=[],nodes=new Map();
class Element {
  constructor(tag='div'){this.tagName=tag;this.textContent='';this.value='';this.children=[];this.dataset={};this.classList={toggle(){},add(){},remove(){}};}
  replaceChildren(...children){this.children=children;}append(...children){this.children.push(...children);}
  addEventListener(){}setAttribute(){}removeAttribute(){}querySelectorAll(){return[];}focus(){}scrollIntoView(){}
}
const node=id=>{if(!nodes.has(id))nodes.set(id,new Element());return nodes.get(id);};
const sandbox={document:{getElementById:node,createElement:tag=>new Element(tag),querySelectorAll:()=>[],addEventListener(){},body:new Element('body')},localStorage:{getItem:()=>null,setItem(){}},window:{print(){}},
  fetch:(url,options)=>new Promise(resolve=>requests.push({url,method:options?.method??'GET',resolve})),URL,setTimeout};
vm.createContext(sandbox);
vm.runInContext(app+`\nfor(const name of ['renderRuns','renderComparison','renderTimeline','renderLineage','renderSources','renderDossier'])globalThis[name]=()=>{};showDetail=()=>{};globalThis.probe={state,load};`,sandbox);
const response=data=>({ok:true,json:async()=>structuredClone(data)});
requests[0].resolve(response(scenarios.initial));await new Promise(resolve=>setImmediate(resolve));
const {state,load}=sandbox.probe;
const rebuild=load(true); // user clicks explicit refresh
const verify=load(false); // visibilitychange can issue this while refresh is disabled
requests[1].resolve(response(scenarios.changed_rebuild));await rebuild;
const afterRebuild={generation:state.catalog.generation,name:state.runs[0].name};
requests[2].resolve(response(scenarios.initial));await verify; // older server read delayed in transit
const afterDelayedVerification={generation:state.catalog.generation,name:state.runs[0].name};
assert.equal(afterRebuild.name,'P02_CHANGED_SAME_ID');
assert.equal(afterDelayedVerification.generation,scenarios.initial.generation);
assert.notEqual(afterDelayedVerification.name,afterRebuild.name);
const result={status:'BASELINE_RACE_REPRODUCED',baseline_sha:'8f8fe01c3041361aa2607194d66af6a640d834ad',scope:'actual app.js load with synthetic delayed fetch; no browser/HTTP timing claim',
  defect:'P02-F002: concurrent visibility verification can overwrite the completed explicit rebuild with an older catalog',requests:requests.map(({url,method})=>({url,method})),afterRebuild,afterDelayedVerification};
fs.writeFileSync(path.join(AREA,'app-race-probe.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
