/** P06/P02 composition: real state asset, synthetic catalog, no browser claim. */
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {runInNewContext} from 'node:vm';

const args = new Map();
for(let index=2;index<process.argv.length;index+=2)args.set(process.argv[index],process.argv[index+1]);
const asset=args.get('--asset');
if(!asset)throw new Error('Required: --asset PATH [--report PATH] [--legacy-expectation true]');
const bytes=readFileSync(asset);
const sandbox={URLSearchParams,URL};
runInNewContext(bytes.toString('utf8'),sandbox,{filename:'installed-parity02_p02_state.js'});
const state=sandbox.AtlasParity02State;
const source=(id,name,runId,snapshot)=>({id,name,snapshot_id:snapshot,read_model:{
  runs:[{id:runId,name:name+' execution',project_id:'project',experiment_id:'experiment'}],
  projects:[{id:'project'}],experiments:[{id:'experiment'}]}});
const original={snapshot_id:'a'.repeat(64),sources:[
  source('source-1','Synthetic A','urn:synthetic:shared-run','c'.repeat(64)),
  source('source-2','Synthetic B','urn:synthetic:shared-run','d'.repeat(64))]};
const changed={snapshot_id:'b'.repeat(64),sources:[
  source('source-1','Synthetic A replacement','urn:synthetic:replacement-run','e'.repeat(64)),
  structuredClone(original.sources[1])]};
const beforeB=JSON.stringify(original.sources[1]);
const keyA=state.key('source-1','urn:synthetic:shared-run');
const keyB=state.key('source-2','urn:synthetic:shared-run');
const oldRoute={...state.defaults(),detail:keyA,selected:[keyA,keyB]};
const oldHash=state.stringify(oldRoute,original);
const report={status:'FAIL',scope:'executed pure state asset; synthetic catalogs; NOT a browser run',
  asset_sha256:createHash('sha256').update(bytes).digest('hex'),checks:[]};
const record=name=>report.checks.push({name,status:'PASS'});
try {
  const current=state.parse(oldHash,original);
  assert.equal(current.rejected,false);
  assert.equal(JSON.stringify(current.route.selected),JSON.stringify([keyA,keyB]));
  record('original_snapshot_holds_two_source_scoped_selections');
  const expired=state.parse(oldHash,changed);
  if(args.get('--legacy-expectation')==='true') {
    report.observed={reason:expired.reason,selected:expired.route.selected,detail:expired.route.detail};
    assert.equal(JSON.stringify(expired.route.selected),JSON.stringify([keyB]),
      'Legacy P06 expected selection B to survive the global snapshot change');
    throw new Error('Legacy expectation unexpectedly passed');
  }
  assert.equal(expired.rejected,true);
  assert.equal(expired.reason,'SNAPSHOT_MISMATCH');
  assert.equal(expired.route.detail,null);
  assert.equal(expired.route.selected.length,0);
  assert.ok(expired.warnings.some(text=>text.includes('seleção')&&text.includes('descartados')));
  record('changed_global_snapshot_expires_detail_and_all_stale_selections_with_warning');
  assert.equal(JSON.stringify(changed.sources[1]),beforeB);
  assert.equal(JSON.stringify(original.sources[1]),beforeB);
  record('unaffected_source_B_records_are_byte_equivalent_in_the_catalog');
  const freshHash=state.stringify({...state.defaults(),detail:keyB,selected:[keyB]},changed);
  const fresh=state.parse(freshHash,changed);
  assert.equal(fresh.rejected,false);
  assert.equal(fresh.route.detail,keyB);
  assert.equal(JSON.stringify(fresh.route.selected),JSON.stringify([keyB]));
  assert.equal(new URLSearchParams(freshHash.slice(1)).get('scope'),changed.snapshot_id);
  record('explicit_fresh_B_selection_and_detail_bind_only_to_the_new_snapshot');
  report.status='PASS_SCOPED';
} catch(error) {
  report.error=error.message;
  report.legacy_expectation_red=args.get('--legacy-expectation')==='true';
}
if(args.has('--report'))writeFileSync(args.get('--report'),JSON.stringify(report,null,2)+'\n');
process.stdout.write(JSON.stringify(report,null,2)+'\n');
if(report.status!=='PASS_SCOPED')process.exitCode=1;
