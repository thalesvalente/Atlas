/** Presentation-only adapter. Authorized v6.1 source functions are recorded in
 * docs/missions/atlas-a01/REUSE-MANIFEST.json. No producer runtime or data bundled.
 */
import {nativeFragments,buildNativeNavigation} from './native_navigation.js';
const numberLiteral=Symbol('JSON numeric lexeme');
export const norm=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
// Structured metadata is decoded without converting scientific numeric values.
// Only JSON string tokens pass through JSON.parse; object keys have no prototype.
export function literalValue(raw){
  if(raw===undefined)return undefined;
  raw=raw.trim();if(raw==='null')return null;if(raw==='true')return true;if(raw==='false')return false;
  if(raw[0]==='"')return JSON.parse(raw);
  if(raw[0]==='{'){const out=Object.create(null);for(const[k,v]of nativeFragments(raw,{all:true}))out[k]=literalValue(v);return out;}
  if(raw[0]==='['){const out=[];let start=1,depth=0,quoted=false,escaped=false;
    for(let i=1;i<raw.length;i++){const ch=raw[i];if(quoted){if(escaped)escaped=false;else if(ch==='\\')escaped=true;else if(ch==='"')quoted=false;continue;}if(ch==='"')quoted=true;else if(ch==='['||ch==='{')depth++;else if(ch===']'||ch==='}') {if(depth===0){if(raw.slice(start,i).trim())out.push(literalValue(raw.slice(start,i)));break;}depth--;}else if(ch===','&&depth===0){out.push(literalValue(raw.slice(start,i)));start=i+1;}}
    return out;
  }
  return Object.freeze({[numberLiteral]:raw});
}
export function literalText(value){
  if(value===undefined)return 'Não declarado';if(value===null)return 'NULL — valor declarado';
  if(typeof value==='object'){if(numberLiteral in value)return value[numberLiteral];if(Array.isArray(value))return value.length?value.map(literalText).join(' · '):'[] — lista vazia declarada';const fields=Object.entries(value);return fields.length?fields.map(([k,v])=>k+': '+literalText(v)).join('\n'):'{} — objeto vazio declarado';}
  return value===''?'"" — texto vazio declarado':String(value);
}
// Family identity is independent of its human label. Numeric tokens never pass
// through Number, including values nested inside arrays or object families.
function familyLiteral(value){
  if(value===null)return 'null';
  if(typeof value==='object'){
    if(numberLiteral in value)return value[numberLiteral];
    if(Array.isArray(value))return '['+value.map(familyLiteral).join(',')+']';
    return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+familyLiteral(value[key])).join(',')+'}';
  }
  if(typeof value==='string')return JSON.stringify(value);
  return String(value);
}
export function familyIdentity(value,present=true){
  const numeric=value!==null&&typeof value==='object'&&numberLiteral in value;
  const literal=present?familyLiteral(value):'';
  const type=!present?'missing':value===null?'null':numeric||typeof value==='number'?(/^-?(?:0|[1-9]\d*)$/.test(literal)?'integer':'number'):Array.isArray(value)?'array':typeof value;
  const label=!present?'Família não declarada':value===null?'NULL — família declarada':literalText(value);
  return Object.freeze({key:JSON.stringify(['atlas-family/1',present,type,literal]),label,type,present});
}
export const KIND=Object.freeze(Object.assign(Object.create(null),{milestone:'Marco de engenharia',mission:'Missão / execução do caderno',run:'Run / tentativa registrada',recovery:'Recuperação',experiment:'Experimento registrado',investigation:'Investigação',presentation:'Apresentação',product:'Produto',observation:'Observação'}));
export const COLORS=Object.freeze(Object.assign(Object.create(null),{published:'#147b59',technical:'#326d9c',failed:'#b54353',mixed:'#ae731e',blocked:'#858347',unknown:'#778b9a'}));
export const EDGE=Object.freeze(Object.assign(Object.create(null),{PREDECESSOR:'Predecessor explícito',INPUT_FROM:'Entrada de',DERIVED_FROM:'Derivado de',PRODUCES:'Produz',PRESENTED_BY:'Apresentado por',HISTORICAL_CONTEXT:'Contexto histórico (não causal)',COMPARED_WITH:'Comparado com'}));
export const objectData=value=>value!==null&&typeof value==='object'&&!Array.isArray(value)&&!(numberLiteral in value)?value:Object.create(null);
const has=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
export function makePresentation(entries){
  const cache=new Map(),read=e=>{if(!cache.has(e.uid))cache.set(e.uid,literalValue(e.raw_json));return cache.get(e.uid);};
  const identities=new Map(),families=new Map(),nativeFamilies=new Map();
  const remember=identity=>{if(!identities.has(identity.key))identities.set(identity.key,identity);return identities.get(identity.key);};
  // Decode only family fragments for non-record DTOs; broad filters must share
  // this namespace without decoding every resource body into a domain object.
  for(const entry of entries){
    const fields=nativeFragments(entry.raw_json,{all:true});
    const identity=fields.has('family')?familyIdentity(literalValue(fields.get('family'))):typeof entry.family==='string'?familyIdentity(entry.family):familyIdentity(undefined,false);
    families.set(entry.uid,remember(identity));
    if(entry.kind==='record')nativeFamilies.set(entry.uid,fields.has('native_family')?remember(familyIdentity(literalValue(fields.get('native_family')))):families.get(entry.uid));
  }
  const familyOf=entry=>families.get(entry.uid);
  const labels=new Map(),groups=new Map(),suffix=identity=>({string:'texto',missing:'ausente'})[identity.type]??identity.type;
  for(const identity of identities.values()){if(!groups.has(identity.label))groups.set(identity.label,[]);groups.get(identity.label).push(identity);}
  for(const group of groups.values())for(const identity of group)labels.set(identity.key,group.length===1?identity.label:identity.label+' ['+suffix(identity)+']');
  // Same-type composites can flatten to the same readable text; retain their
  // distinct literal representations rather than using their label as a key.
  const collisions=new Map();for(const[key,label]of labels){if(!collisions.has(label))collisions.set(label,[]);collisions.get(label).push(key);}
  for(const keys of collisions.values())if(keys.length>1)for(const key of keys){const identity=identities.get(key);labels.set(key,identity.label+' ['+suffix(identity)+'; '+JSON.parse(key)[3]+']');}
  const familyLabel=key=>labels.get(key)??'Família não reconhecida nesta revisão';
  const records=entries.filter(e=>e.kind==='record').map(entry=>{const data=objectData(read(entry)),family=familyOf(entry),native=nativeFamilies.get(entry.uid);return {...data,id:entry.uid,original_id:data.id,familyKey:family.key,nativeFamilyKey:native.key,native_family:familyLabel(native.key),family:familyLabel(family.key),filterKind:has(data,'kind')?literalText(data.kind):'',filterStatus:has(data,'result_group')?literalText(data.result_group):entry.status??'',title:entry.title,entry};});
  const byUid=new Map(records.map(r=>[r.id,r])),navigation=buildNativeNavigation(entries);
  const edges=entries.filter(e=>e.kind==='relation'&&e.group==='edges').map(entry=>{const data=objectData(read(entry)),refs=navigation.outgoing.get(entry.uid)||[],find=n=>{const name=has(data,n+'_key')?n+'_key':n,ref=refs.find(r=>r.label===name);return {ref,literal:data[name],candidates:(ref?.targets||[]).map(uid=>navigation.byUid.get(uid)).filter(Boolean)};},from=find('from'),to=find('to');const recordEndpoint=endpoint=>endpoint.ref?.resolution==='UNIQUE'&&endpoint.candidates[0]?.kind==='record'?endpoint.candidates[0].uid:null;return {...data,type:typeof data.type==='string'?data.type:literalText(data.type),entry,from:recordEndpoint(from),to:recordEndpoint(to),fromResolution:from.ref?.resolution??'NOT_DECLARED',toResolution:to.ref?.resolution??'NOT_DECLARED',fromCandidates:from.candidates,toCandidates:to.candidates,originalFrom:from.literal,originalTo:to.literal};});
  const editorial=entries.find(e=>e.group==='editorial_map');
  return {records,byUid,edges,editorial_map:editorial?read(editorial):null,read,familyOf,familyLabel};
}
// Adapted filterRecords: the same declared record population drives index,
// editorial tree, record table, relations and timeline. No hardcoded taxonomy.
// Lazily index the complete validated payload, not a whitelist of fields.
// literalValue decodes strings but retains every numeric token; literalText
// visits arrays/objects without invoking payload-provided coercion methods.
// One weak cache entry per derived record/snapshot, released with that snapshot.
const recordSearchCache=new WeakMap();
function recordSearchText(record){
  if(!recordSearchCache.has(record))recordSearchCache.set(record,norm([
    record.title,record.family,record.entry.native_id??'',record.entry.source_key??'',
    literalText(literalValue(record.entry.raw_json))
  ].join('\n')));
  return recordSearchCache.get(record);
}
export function recordMatches(record,{query='',family='',kind='',status=''}={}){
  const q=norm(query).trim();
  return(!family||record.familyKey===family)&&(!kind||record.filterKind===kind)&&
    (!status||record.filterStatus===status)&&(!q||recordSearchText(record).includes(q));
}
export const recordSort=(a,b)=>String(a.family).localeCompare(String(b.family),'pt-BR')||a.title.localeCompare(b.title,'pt-BR');
// Adapted renderRFTable: readable identification/name/description first; all
// original columns remain available in a reversible order. Exports never use it.
const columnRank=name=>{const n=norm(name);if(n==='id')return 0;if(/n.cleo/.test(n))return 1;if(n==='nome')return 2;if(n.startsWith('descri'))return 3;if(/crit.rio/.test(n)&&n.includes('aceit'))return 4;return 5;};
export function presentationColumns(columns){return columns.map((name,index)=>({name,index,rank:columnRank(name)})).sort((a,b)=>a.rank-b.rank||a.index-b.index).map(x=>x.name);}
export function readingColumns(columns){const ordered=presentationColumns(columns),core=ordered.filter(name=>columnRank(name)<5);return core.length===5?core:ordered;}
// Adapted hcTitle / hcStatus precedence; absent states stay absent.
const firstDeclared=(value,names)=>{const data=objectData(value);for(const name of names)if(has(data,name))return data[name];return undefined;};
export const catalogTitle=x=>firstDeclared(x,['label','title','name','native_id','unit_id','native_path','source_path','id']);
export const catalogStatus=x=>firstDeclared(x,['documentary_status','terminal_status','assessment_after','status','binding_status','technical_admission','availability','publication']);
const EXECUTION_INK=Object.freeze({
  succeeded:'#116b4d',technical:'#285f8a',failed:'#9e3447',mixed:'#87570d',blocked:'#666324',
});
const EXECUTION_STATE_FIELDS=Object.freeze(['execution_state','status','result_state']);
const LEGACY_RESULT_FIELDS=Object.freeze(['result_group','result']);
const PUBLICATION_VALUES=new Set(['published','not_published','snapshot_published','published_pass_with_warnings']);
function recordExecutionField(data){
  // Explicit fields preserve even NULL, empty and unknown values. Legacy
  // result fields can also carry documentary publication instead of execution.
  for(const field of EXECUTION_STATE_FIELDS)if(has(data,field))return field;
  for(const field of LEGACY_RESULT_FIELDS){
    if(!has(data,field))continue;
    const value=data[field];
    if(typeof value!=='string'||!PUBLICATION_VALUES.has(value.toLowerCase()))return field;
  }
  return undefined;
}
export function recordExecutionState(record){
  const data=objectData(record),field=recordExecutionField(data);
  return field===undefined?undefined:data[field];
}
// A publication label alone carries no execution verdict. Only exact state
// tokens, matched case-insensitively, can select a non-neutral presentation.
export function recordExecutionPresentation(record){
  const data=objectData(record),field=recordExecutionField(data);
  const state=field===undefined?undefined:data[field],key=typeof state==='string'?state.toLowerCase():'';
  const tone=has(EXECUTION_INK,key)?key:'neutral';
  return {field,state,tone,ink:EXECUTION_INK[tone]??'#526978',
    accent:COLORS[tone==='succeeded'?'published':tone]??'#7d92a4'};
}

// OLD tables-coverage.js scopes project/run/stage/admission to table metadata,
// and nucleus_id to the original row. No aliases or inferred domain taxonomy.
export const TABLE_FILTER_FIELDS=Object.freeze([
  ['project','Projeto','table'],['run_id','Execução','table'],
  ['stage','Estágio','table'],['admission','Admissão','table'],
  ['nucleus_id','Núcleo','row'],
].map(Object.freeze));
const tableFacetCache=new WeakMap();
export function tableFacet(entry,field){
  if(!tableFacetCache.has(entry))tableFacetCache.set(entry,{parts:nativeFragments(entry.raw_json,{all:true}),facets:new Map()});
  const cache=tableFacetCache.get(entry);
  if(!cache.facets.has(field)){
    const present=cache.parts.has(field),raw=present?cache.parts.get(field):'',value=present?literalValue(raw):undefined;
    const identity=familyIdentity(value,present);
    cache.facets.set(field,Object.freeze({key:JSON.stringify(['atlas-table-filter/1',field,present,identity.type,raw]),present,type:identity.type,raw,label:present?literalText(value):'AUSENTE — chave não declarada'}));
  }
  return cache.facets.get(field);
}
export function tableFilterOptions(entries,field){
  const dimension=TABLE_FILTER_FIELDS.find(([key])=>key===field);if(!dimension)return[];
  const facets=entries.filter(e=>e.kind===dimension[2]).map(e=>tableFacet(e,field));
  if(!facets.some(f=>f.present))return[];
  const unique=[...new Map(facets.map(f=>[f.key,f])).values()],counts=new Map();
  for(const f of unique)counts.set(f.label,(counts.get(f.label)||0)+1);
  return unique.map(f=>({...f,label:counts.get(f.label)>1?f.label+' ['+f.type+'; '+f.raw+']':f.label}))
    .sort((a,b)=>a.label.localeCompare(b.label,'pt-BR')||a.key.localeCompare(b.key));
}
export function tableMatchesFilters(entry,filters={}){
  return TABLE_FILTER_FIELDS.every(([field,,kind])=>entry.kind!==kind||!filters[field]||tableFacet(entry,field).key===filters[field]);
}
