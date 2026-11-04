import assert from 'node:assert/strict';
import {buildNativeNavigation,nativeFragments,declaredSourceAliases} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {buildLineage} from '../../packages/atlas/src/atlas_viewer/static/native_lineage.js';
function entry(uid,kind,data,extra={}){
  return{uid,kind,title:uid,native_id:data.native_id??(kind==='record'?data.id:null),source_key:data.key||data.id||null,parent_uid:null,
    fields:Object.entries(data).filter(([,value])=>value===null||typeof value!=='object').map(([name,value])=>({name,type:value===null?'null':typeof value,text:typeof value==='string'?value:JSON.stringify(value)})),raw_json:JSON.stringify(data),...extra};
}
const record=entry('record','record',{id:'R',source_ids:['run-alias',12],resources:['asset','missing',null]}),
  collisionA=entry('collision-a','record',{id:'A',source_ids:['shared-alias']}),
  collisionB=entry('collision-b','record',{id:'B',source_ids:['shared-alias']}),
  node=entry('node','node',{key:'node-key',run_id:'run-alias',native_id:null}),
  absent=entry('absent','node',{key:'absent-key',run_id:null,native_id:'R'}),
  table=entry('table','table',{id:'T',record_id:'run-alias'}),
  ambiguous=entry('ambiguous','table',{id:'T2',record_id:'shared-alias'}),
  asset=entry('asset','asset',{id:'asset'}),
  row=entry('row','row',{id:'row',evidence:[{quote:'invented'}]},{table_uid:'table'}),
  relation=entry('relation','relation',{from_key:null,from:'R',to_key:'node-key',to:'missing'});
const model=buildNativeNavigation([record,collisionA,collisionB,node,absent,table,ambiguous,asset,row,relation]);
assert.deepEqual(declaredSourceAliases(record),['run-alias']);
assert.deepEqual(model.outgoing.get('node').find(ref=>ref.label==='run_id').targets,['record']);
assert.deepEqual(model.outgoing.get('table').find(ref=>ref.label==='record_id').targets,['record']);
assert.equal(model.outgoing.get('ambiguous')[0].resolution,'COLLISION');
assert.deepEqual(model.outgoing.get('ambiguous')[0].targets,['collision-a','collision-b']);
assert.equal(model.outgoing.get('absent')[0].resolution,'NOT_DECLARED');
assert.deepEqual(model.outgoing.get('relation').find(ref=>ref.label==='from_key').targets,[]);
assert.ok(!model.outgoing.get('relation').some(ref=>ref.label==='from'));
assert.deepEqual(model.outgoing.get('row').find(ref=>ref.label==='table_uid').targets,['table']);
assert.deepEqual(model.outgoing.get('record').map(ref=>ref.resolution),['UNIQUE','UNRESOLVED','NOT_DECLARED']);
assert.equal(model.incoming.get('record').length,2);
const exact='{"evidence":[{"number":9007199254740993,"text":"quoted \\\"value\\\", comma"}],"nested":{"evidence":[1]},"source_ids":[9007199254740993,"literal-alias"]}';
assert.equal(nativeFragments(exact).get('evidence'),'[{"number":9007199254740993,"text":"quoted \\\"value\\\", comma"}]');
const numeric=entry('numeric','record',{id:'N'});numeric.raw_json=exact;
assert.deepEqual(declaredSourceAliases(numeric),['literal-alias']);
const numericIdentity=entry('numeric-id','record',{}, {native_id:'9007199254740993',source_key:null,raw_json:'{"id":9007199254740993}',fields:[{name:'id',type:'integer',text:'9007199254740993'}]});
const stringReference=entry('string-reference','node',{run_id:'9007199254740993'});
assert.equal(buildNativeNavigation([numericIdentity,stringReference]).outgoing.get('string-reference')[0].resolution,'UNRESOLVED');
const otherSnapshot=buildNativeNavigation([entry('other-node','node',{run_id:'run-alias'})]);
assert.equal(otherSnapshot.outgoing.get('other-node')[0].resolution,'UNRESOLVED');
for(const endpoint of ['from','to'])for(const value of [['not-interpreted'],{key:'not-interpreted'},42,false]){
  const composite=entry('composite','relation',{[endpoint]:'R',[endpoint+'_key']:value});
  const refs=buildNativeNavigation([record,composite]).outgoing.get('composite');
  assert.equal(refs.length,1);
  assert.equal(refs[0].label,endpoint+'_key');
  assert.equal(refs[0].resolution,'NOT_INTERPRETED');
  assert.equal(refs[0].literal,JSON.stringify(value));
  assert.deepEqual(refs[0].targets,[]);
}
const nestedKey=entry('nested-key','relation',{from:'R',nested:{from_key:['not-top-level']}});
assert.deepEqual(buildNativeNavigation([record,nestedKey]).outgoing.get('nested-key')[0].targets,['record']);
const exactKey=entry('numeric-key','relation',{from:'R'}, {raw_json:'{"from":"R","from_key":9007199254740993}',fields:[{name:'from',type:'string',text:'R'},{name:'from_key',type:'integer',text:'9007199254740993'}]});
assert.equal(buildNativeNavigation([record,exactKey]).outgoing.get('numeric-key')[0].literal,'9007199254740993');
for(const endpoint of ['from','to']){
  const explicitNull=entry('null-key','relation',{[endpoint]:'R',[endpoint+'_key']:null}),missingKey=entry('missing-key','relation',{[endpoint]:'R'});
  const explicit=buildNativeNavigation([record,explicitNull]).outgoing.get('null-key')[0];
  assert.equal(explicit.label,endpoint+'_key');assert.equal(explicit.resolution,'NOT_DECLARED');assert.deepEqual(explicit.targets,[]);
  const fallback=buildNativeNavigation([record,missingKey]).outgoing.get('missing-key')[0];
  assert.equal(fallback.label,endpoint);assert.equal(fallback.resolution,'UNIQUE');assert.deepEqual(fallback.targets,['record']);
}
const endpoints=[
  entry('shared-record','record',{id:'same',source_ids:['declared-alias']},{group:'records'}),
  entry('shared-node','node',{key:'same',native_id:'native-only'},{group:'lineage_graph.nodes'}),
  entry('record-only','record',{id:'record-only-key'},{group:'records'}),
  entry('foreign-node','node',{key:'foreign-key'},{group:'other.nodes'}),
  entry('asset-key','asset',{id:'asset-key'},{group:'resources'}),
  entry('table-key','table',{id:'table-key'},{group:'result_tables'}),
  entry('row-key','row',{id:'row-key'},{group:'result_tables'}),
  entry('collection-key','collection',{id:'collection-key'},{group:'other'}),
  entry('numeric-native','node',{}, {group:'lineage_graph.nodes',native_id:'9007199254740993',source_key:null,raw_json:'{"native_id":9007199254740993}',fields:[{name:'native_id',type:'integer',text:'9007199254740993'}]}),
];
const keyCases=[['edges','same',['shared-record','shared-node']],['edges','record-only-key',['record-only']],['lineage_graph.edges','same',['shared-node']],['lineage_graph.edges','foreign-key',[]],['edges','native-only',[]],['edges','declared-alias',[]],['edges','collection-key',[]],...['asset-key','table-key','row-key'].map(key=>['edges',key,[key]])];
for(const endpoint of ['from','to'])for(const[group,value,expected]of keyCases){
  const relation=entry('keyed-relation','relation',{[endpoint+'_key']:value},{group}),all=[...endpoints,relation];
  const navigation=buildNativeNavigation(all).outgoing.get(relation.uid).find(ref=>ref.label===endpoint+'_key'),lineage=buildLineage(all)[0][endpoint];
  assert.deepEqual([...navigation.targets].sort(),[...expected].sort(),`${group} ${endpoint}_key=${value}`);
  assert.deepEqual([...navigation.targets].sort(),lineage.candidates.map(match=>match.entry.uid).sort());
  assert.equal(navigation.resolution,lineage.status==='RESOLVED'?'UNIQUE':lineage.status);
}
for(const endpoint of ['from','to'])for(const[value,expected]of [['same',['shared-record','shared-node']],['declared-alias',['shared-record']],['native-only',['shared-node']],['collection-key',[]],['9007199254740993',[]]]){
  const relation=entry('id-relation','relation',{[endpoint]:value},{group:'edges'}),all=[...endpoints,relation];
  const navigation=buildNativeNavigation(all).outgoing.get(relation.uid)[0],lineage=buildLineage(all)[0][endpoint];
  assert.deepEqual([...navigation.targets].sort(),[...expected].sort());
  assert.deepEqual([...navigation.targets].sort(),lineage.candidates.map(match=>match.entry.uid).sort());
}
for(const endpoint of ['from','to']){
  const relation=entry('numeric-relation','relation',{}, {group:'edges',raw_json:`{"${endpoint}":9007199254740993}`,fields:[{name:endpoint,type:'integer',text:'9007199254740993'}]}),all=[...endpoints,relation];
  const navigation=buildNativeNavigation(all).outgoing.get(relation.uid)[0],lineage=buildLineage(all)[0][endpoint];
  assert.deepEqual(navigation.targets,['numeric-native']);assert.deepEqual(navigation.targets,lineage.candidates.map(match=>match.entry.uid));
}
console.log(JSON.stringify({status:'PASS_SCOPED',checks:['declared_aliases_string_only','unique_context_links','ambiguous_aliases_not_first_match','explicit_null_without_fallback','transport_table_membership','resources_missing_and_null','exact_nested_evidence_lexemes','numeric_identity_not_coerced_to_string_reference','source_snapshot_isolation','explicit_array_object_numeric_keys_never_fall_back','exact_large_numeric_key_retained_without_interpretation','absent_key_only_allows_endpoint_fallback','keyed_navigation_lineage_same_candidates_and_collisions','lineage_collection_scope_excludes_foreign_keys','keyed_references_never_use_native_ids_or_aliases','unkeyed_typed_id_and_declared_alias_policy_matches_lineage']}));
