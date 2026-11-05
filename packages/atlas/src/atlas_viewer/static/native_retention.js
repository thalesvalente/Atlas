/** A retention proposal is inert JSON, not a filesystem instruction or approval.
 * No DOM, network, paths API, producer import or persistent state is used here.
 */
import {nativeFragments} from './native_navigation.js';
import {literalValue,literalText,familyIdentity} from './native_legacy_model.js';
import {createTriageModel,selectionKey,snapshotKey,RETENTION_INTENTS} from './native_triage_model.js';
export {RETENTION_INTENTS};

const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const PENDING=Object.freeze(['LOCAL_CURRENT_INVENTORY','DEPENDENCY_GRAPH','DOSSIER_PRESERVATION',
  'BACKUP_OR_APPLICABLE_POLICY','RECOVERABLE_SPACE_ESTIMATE','HUMAN_BATCH_AUTHORIZATION']);
const GROUPS=Object.freeze([
  ['scientific_identity','Identidade original',['native_id','id','experiment_id','run_id','execution_id','mission_id','attempt_id']],
  ['family','Família',['family','native_family']],
  ['configurations','Configurações',['configuration','config','configs','configuration_ref','parameters','settings','hyperparameters','seed']],
  ['code_revisions','Código e revisões',['code_revision','code_revisions','commit','commit_sha','code_ref','git_sha','revision','software','source_revision','code']],
  ['results','Resultados',['results','result','result_state','result_group','outputs']],
  ['metrics','Métricas',['metrics','metric','metric_values','scores','measurements']],
  ['limitations','Limitações',['limitations','limitation','caveats']],
  ['dependencies','Dependências',['dependencies','depends_on','input_refs','inputs','dependency_refs','shared_dependencies']],
  ['artifacts','Artefatos',['artifacts','artifact_refs','resources','resource_ids','document_ids','file_refs','result_files','dossier_ref']],
  ['evidence','Evidência',['evidence','trace','reference','source','sources']],
  ['preservation_declarations','Declarações de preservação',['backup','backup_ref','backup_verified','retention','retention_policy']],
  ['dates','Datas',['started_at','startTime','timestamp','date','scientific_at']],
]);

function fieldValue(field,raw){
  const value=literalValue(raw),type=familyIdentity(value,true).type;
  return {field,type,raw_json:raw,display:literalText(value)};
}
function sourceIdentity(source){
  const result={};for(const key of ['id','name','revision','metadata_sha256'])if(own(source,key))result[key]=source[key];
  return result;
}
function identity(source,entry){
  const result={selection_key:selectionKey(source,entry),source_id:source.id,uid:entry.uid,dto_kind:entry.kind};
  if(own(source,'revision'))result.source_revision=source.revision;
  if(own(source,'metadata_sha256'))result.source_metadata_sha256=source.metadata_sha256;
  if(typeof entry.source_key==='string')result.source_key=entry.source_key;
  const fields=nativeFragments(entry.raw_json,{all:true}),key=['native_id','id'].find(name=>fields.has(name));
  if(key!==undefined)result.original_id=fieldValue(key,fields.get(key));
  if(entry.kind==='record'&&fields.has('kind'))result.record_kind=fieldValue('kind',fields.get('kind'));
  return result;
}
function selection(source,entries){
  if(source?.status!=='READY')throw Error('RETENTION_SOURCE_NOT_READY');
  if(typeof source.id!=='string'||!source.id||typeof source.metadata_sha256!=='string'||!source.metadata_sha256)
    throw Error('RETENTION_SOURCE_IDENTITY_REQUIRED');
  const model=createTriageModel(source),selected=new Map();
  for(const entry of entries){
    const canonical=model.byUid.get(entry?.uid);
    if(!canonical||canonical.kind!==entry.kind||canonical.raw_json!==entry.raw_json)throw Error('RETENTION_OCCURRENCE_OUTSIDE_SNAPSHOT');
    selected.set(selectionKey(source,canonical),canonical);
  }
  return {model,entries:[...selected.values()]};
}
function declaredContent(entry){
  const fields=nativeFragments(entry.raw_json,{all:true}),declared=Object.create(null),gaps=[];
  for(const[group,label,names]of GROUPS){
    const values=names.filter(name=>fields.has(name)).map(name=>fieldValue(name,fields.get(name)));
    if(!values.length){gaps.push(label+': não declarados nesta ocorrência.');continue;}
    declared[group]=values;
    for(const value of values){
      if(value.type==='null')gaps.push(label+' / '+value.field+': NULL declarado, não substituído.');
      else if(['""','[]','{}'].includes(value.raw_json))gaps.push(label+' / '+value.field+': valor vazio declarado.');
    }
  }
  return {declared,gaps};
}
function protection(entry,baseline,declared){
  const reasons=['SOURCE_PRESERVATION_REQUIRED','LOCAL_INVENTORY_NOT_VERIFIED','DEPENDENCIES_NOT_VERIFIED',
    'DOSSIER_PRESERVATION_NOT_VERIFIED','BACKUP_NOT_VERIFIED','RETENTION_POLICY_NOT_VERIFIED',
    'SPACE_NOT_MEASURED','HUMAN_BATCH_AUTHORIZATION_MISSING'];
  if(baseline.confirmed||baseline.operatorDesignated)reasons.unshift('BASELINE_DESIGNATED');
  if(baseline.conflict)reasons.unshift('BASELINE_DECLARATION_CONFLICT');
  if(entry.kind==='asset'||declared.artifacts)reasons.push('ARTIFACT_UNIQUENESS_NOT_VERIFIED');
  if(declared.configurations)reasons.push('CONFIGURATION_NECESSITY_NOT_VERIFIED');
  if(declared.dependencies)reasons.push('SHARED_DEPENDENCIES_NOT_VERIFIED');
  return {status:'PROTECTED',removal_authorized:false,reasons};
}
function tableRows(source,entry){
  if(entry.kind!=='table'||!Number.isInteger(entry.row_count))return null;
  const rows=source.entries.filter(row=>row.kind==='row'&&row.table_uid===entry.uid).sort((a,b)=>a.ordinal-b.ordinal);
  if(rows.length!==entry.row_count||rows.some((row,i)=>row.ordinal!==i))throw Error('RETENTION_TABLE_ROWS_INCOMPLETE');
  return {status:'COMPLETE_FOR_SNAPSHOT',transport_skeleton:true,count:rows.length,
    rows:rows.map(row=>({uid:row.uid,ordinal:row.ordinal,raw_json:row.raw_json}))};
}

function build(source,requested,{annotations=new Map(),intents=new Map()}={},schema){
  const {model,entries}=selection(source,requested),items=entries.map(entry=>{
    const ref=identity(source,entry),kind=model.type(entry),baseline=model.baseline(entry,annotations),content=declaredContent(entry),
      intent=intents instanceof Map&&intents.has(ref.selection_key)?intents.get(ref.selection_key):'UNDECIDED';
    if(!RETENTION_INTENTS.includes(intent))throw Error('RETENTION_INTENT_INVALID');
    const item={identity:ref,title:entry.title,type:kind.key,type_label:kind.label,raw_json:entry.raw_json,
      baseline,execution:model.facet(entry,'execution'),intent,declared:content.declared,gaps:content.gaps,
      protection:protection(entry,baseline,content.declared),pending_verifications:[...PENDING]};
    const rows=tableRows(source,entry);if(rows)item.table_rows=rows;
    item.gaps.push('Referências físicas, dependências e backups: a verificar no ambiente LOCAL.');
    return item;
  });
  return {schema,version:1,status:'PROPOSAL_ONLY',DELETE_AUTHORIZED:'NO',source:sourceIdentity(source),
    snapshot_key:snapshotKey(source),selection:items.map(item=>item.identity),items,
    pending_verifications:[...PENDING],space_estimate:{status:'NOT_MEASURED',label:'A medir no ambiente LOCAL'},
    provenance:{mode:'DERIVED_SESSION_PROPOSAL',source_read_only:true,physical_presence_verified:false,
      scientific_acceptance:'NOT_ASSERTED',operator_intentions_are_commands:false,
      notes:'Identidades e conteúdo pertencem ao snapshot declarado. Digest não prova autenticidade; resumo não prova preservação.'}};
}

export function buildRetentionPlan(source,entries,options={}){
  return build(source,entries,options,'atlas-retention-plan/1');
}
export function buildDossier(source,entries,options={}){
  return build(source,entries,options,'atlas-triage-dossier/1');
}
export function copyReferences(source,entries){
  return selection(source,entries).entries.map(entry=>JSON.stringify(identity(source,entry))).join('\n');
}
