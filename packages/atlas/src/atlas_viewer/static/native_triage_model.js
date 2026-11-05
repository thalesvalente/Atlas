/** Read-only, snapshot-scoped triage over verified Native View DTOs.
 * Derived facets are presentation, never scientific approval or file authority.
 */
import {nativeFragments,buildNativeNavigation} from './native_navigation.js';
import {literalValue,literalText,objectData,familyIdentity,makePresentation,norm,
  EXECUTION_STATE_FIELDS,recordExecutionState,recordExecutionPresentation} from './native_legacy_model.js';

const own=(o,k)=>o!==null&&o!==undefined&&Object.prototype.hasOwnProperty.call(o,k);
const rawCache=new WeakMap(),dataCache=new WeakMap();
const parts=e=>{if(!rawCache.has(e))rawCache.set(e,nativeFragments(e.raw_json,{all:true}));return rawCache.get(e);};
const data=e=>{if(!dataCache.has(e))dataCache.set(e,objectData(literalValue(e.raw_json)));return dataCache.get(e);};
const first=(fields,names)=>names.find(name=>fields.has(name));
const safeGet=(map,key)=>map instanceof Map?map.get(key):undefined;
const TYPE_LABELS=Object.freeze(Object.assign(Object.create(null),{
  record:'Registro',experiment:'Experimento',execution:'Execução',run:'Execução (run)',attempt:'Tentativa',
  mission:'Missão',milestone:'Marco',baseline:'Baseline (tipo declarado)',product:'Produto',artifact:'Artefato',
  resource:'Recurso',document:'Documento',investigation:'Investigação',recovery:'Recuperação',
  presentation:'Apresentação',observation:'Observação',table:'Tabela',row:'Linha de tabela',
  node:'Objeto estrutural',relation:'Relação',collection:'Coleção',asset:'Recurso ou documento',
}));
const ASSET_TYPES=Object.freeze(Object.assign(Object.create(null),{
  resources:'resource',documents:'document',product_items:'product',product_groups:'product',
  presentation_items:'presentation',presentations:'presentation',artifacts:'artifact',
}));
const ALIASES=Object.freeze({
  publication:['publication','publication_status'],admission:['admission','technical_admission','admission_status'],
  review:['human_review','review','review_state','review_status'],result_group:['result_group'],
  date:['started_at','startTime','timestamp','date','scientific_at'],
});
export const TRIAGE_DIMENSIONS=Object.freeze([
  ['execution','Estado de execução'],['result_group','Grupo do resultado'],['publication','Publicação'],
  ['admission','Admissão'],['review','Revisão documental'],['documentary','Estado documental'],
  ['family','Família'],['kind','Tipo de registro'],['baseline','Designação de baseline'],
  ['evidence','Evidência e artefatos'],
].map(([id,label])=>Object.freeze({id,label})));
export const RETENTION_INTENTS=Object.freeze(['KEEP_FULL','KEEP_ESSENTIALS','REVIEW_FOR_REMOVAL','UNDECIDED']);

/** Type follows DTO kind and declared kind; names and status have no role. */
export function entryType(entry){
  const value=data(entry),declared=own(value,'kind');
  if(entry.kind==='record'){
    const kind=declared&&typeof value.kind==='string'&&own(TYPE_LABELS,value.kind)&&
      !['table','row','node','relation','collection','asset'].includes(value.kind)?value.kind:'record';
    return {key:kind,label:TYPE_LABELS[kind],declared,raw:parts(entry).get('kind')};
  }
  const subtype=entry.kind==='asset'?(declared&&typeof value.kind==='string'&&
    ['product','artifact','resource','document','presentation'].includes(value.kind)?value.kind:ASSET_TYPES[entry.group]||'asset'):entry.kind;
  return {key:subtype,label:TYPE_LABELS[subtype]||'Ocorrência',declared:true,raw:JSON.stringify(subtype)};
}

function identityField(source,key){
  return own(source,key)?[true,source[key]]:[false];
}
export function snapshotKey(source){
  return JSON.stringify(['atlas-snapshot-selection/1',identityField(source,'id'),
    identityField(source,'revision'),identityField(source,'metadata_sha256')]);
}
export function selectionKey(source,entry){
  return JSON.stringify(['atlas-selection/1',snapshotKey(source),entry.uid,entry.kind,
    entry.kind==='record'?(parts(entry).has('kind')?[true,parts(entry).get('kind')]:[false]):[false]]);
}
function verifiedEntries(source){
  if(source?.status!=='READY')return[];
  const entries=Array.isArray(source.entries)?source.entries:[],seen=new Set();
  for(const entry of entries){
    if(typeof entry.uid!=='string'||!entry.uid||seen.has(entry.uid))throw Error('TRIAGE_IDENTITY_COLLISION');
    seen.add(entry.uid);
  }
  return entries;
}
function usableSource(source){
  return source?.status==='READY'&&typeof source.id==='string'&&source.id.length>0&&
    typeof source.metadata_sha256==='string'&&source.metadata_sha256.length>0;
}
function typedFacet(dimension,raw,field=null,extra={}){
  const present=raw!==undefined,value=present?literalValue(raw):undefined,identity=familyIdentity(value,present);
  return Object.freeze({key:JSON.stringify(['atlas-triage-facet/1',dimension,present,identity.type,present?raw:null]),
    present,type:identity.type,raw:present?raw:null,field,label:present?literalText(value):'AUSENTE — campo não declarado',...extra});
}
const BASELINE_LABELS=Object.freeze({SOURCE_DECLARED:'Designação explícita da fonte',
  OPERATOR_SESSION:'Designação do operador nesta sessão',NOT_DECLARED:'Designação não declarada',
  UNCONFIRMED:'Declaração sem confirmação de baseline',CONFLICT:'Declarações de baseline conflitantes'});

function operatorAnnotation(source,entry,annotations){
  const key=selectionKey(source,entry),annotation=safeGet(annotations,key);
  return annotation&&annotation.origin==='OPERATOR_SESSION'&&annotation.selection_key===key&&
    annotation.snapshot_key===snapshotKey(source)&&typeof annotation.note==='string'&&annotation.note.trim()?annotation:null;
}

/** A reference to a baseline does not designate the referring item as one. */
export function baselineDesignation(source,entry,annotations=new Map()){
  const fields=parts(entry),value=data(entry),declarations=[];
  for(const name of ['baseline','is_baseline'])if(fields.has(name))declarations.push({field:name,raw:fields.get(name),value:value[name]});
  if(value.kind==='baseline')declarations.push({field:'kind',raw:fields.get('kind'),value:true});
  const positive=declarations.some(x=>x.value===true),negative=declarations.some(x=>x.value===false),conflict=positive&&negative;
  const sourceConfirmed=positive&&!conflict,annotation=operatorAnnotation(source,entry,annotations);
  const status=conflict?'CONFLICT':sourceConfirmed?'SOURCE_DECLARED':annotation?'OPERATOR_SESSION':declarations.length?'UNCONFIRMED':'NOT_DECLARED';
  const result={status,label:BASELINE_LABELS[status],confirmed:sourceConfirmed||Boolean(annotation)&&!conflict,
    sourceConfirmed,operatorDesignated:Boolean(annotation),conflict,
    declarations:declarations.map(({field,raw})=>({field,raw_json:raw})),
    explanation:sourceConfirmed?'Designação declarada; não comprova execução ou aceite científico.':
      conflict?'Declarações contraditórias; confirmação recusada.':
      annotation?'Anotação explícita do operador; o DTO da fonte permanece intacto.':'Nome, publicação e resultado não são prova de baseline.'};
  if(annotation)result.annotation=annotation;
  if(fields.has('baseline_ref'))result.reference={raw_json:fields.get('baseline_ref'),status:'REFERENCE_ONLY_NOT_A_DESIGNATION'};
  return result;
}

const EVIDENCE_FIELDS=Object.freeze(['evidence','artifacts','artifact_refs','resources','document_ids',
  'result_files','file_refs','source','sources','reference','trace','dossier_ref']);
function evidenceFacet(entry){
  const fields=parts(entry),declared=EVIDENCE_FIELDS.filter(name=>fields.has(name));
  if(!declared.length)return {key:'MISSING',present:false,type:'missing',raw:null,field:null,label:'AUSENTE — referências não declaradas'};
  const values=declared.map(name=>literalValue(fields.get(name))),empty=x=>x===''||Array.isArray(x)&&x.length===0||
    x!==null&&typeof x==='object'&&!Array.isArray(x)&&Object.keys(x).length===0&&Object.getOwnPropertySymbols(x).length===0;
  const meaningful=x=>typeof x==='string'&&x!==''||Array.isArray(x)&&x.length>0||
    x!==null&&typeof x==='object'&&!Array.isArray(x)&&Object.keys(x).length>0;
  const key=values.some(meaningful)?'DECLARED':values.every(x=>x===null)?'NULL':values.every(empty)?'EMPTY':'UNINTERPRETED';
  const labels={DECLARED:'Referências declaradas; presença física não verificada',NULL:'NULL — referências sem valor',
    EMPTY:'Referências vazias — presença não comprovada',UNINTERPRETED:'Declaração não interpretada — presença não verificada'};
  return {key,present:true,type:'evidence-summary',raw:'{'+declared.map(name=>JSON.stringify(name)+':'+fields.get(name)).join(',')+'}',
    field:declared.join(', '),label:labels[key]};
}

function queryTerms(query){
  return norm(typeof query==='string'?query:'').trim().split(/\s+/u).filter(Boolean).map(term=>{
    // Identifier-like queries use token boundaries: M1 is neither M11 nor M1.1.
    if(/^[\p{L}_-]*\p{L}[\p{L}_-]*\d[\p{L}\p{N}_.-]*$/u.test(term)){
      const escaped=term.replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),pattern=new RegExp('(^|[^\\p{L}\\p{N}_.-])'+escaped+'(?=$|[^\\p{L}\\p{N}_.-])','u');
      return value=>pattern.test(value);
    }
    return value=>value.includes(term);
  });
}
function isoTime(value,endOfDay=false){
  if(typeof value!=='string'||!/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?$/.test(value))return NaN;
  const day=value.slice(0,10),start=Date.parse(day+'T00:00:00Z');
  if(!Number.isFinite(start)||new Date(start).toISOString().slice(0,10)!==day)return NaN;
  return value.length===10?start+(endOfDay?86400000-1:0):Date.parse(value);
}

export function createTriageModel(source,presentation=null){
  const items=verifiedEntries(source),byUid=new Map(items.map(e=>[e.uid,e])),model=presentation||makePresentation(items);
  const facets=new WeakMap(),searchIndex=new WeakMap();let navigation=null;
  const type=entryType,baseline=(entry,annotations)=>baselineDesignation(source,entry,annotations);
  function facet(entry,dimension,annotations=new Map()){
    if(dimension==='baseline'){
      const designation=baseline(entry,annotations);
      return {key:designation.status,label:designation.label,present:designation.status!=='NOT_DECLARED',
        type:'baseline-designation',raw:null,field:'baseline/is_baseline/kind',designation};
    }
    if(!facets.has(entry))facets.set(entry,new Map());const cache=facets.get(entry);
    if(cache.has(dimension))return cache.get(dimension);
    const fields=parts(entry);let value;
    if(dimension==='family'){
      const identity=model.familyOf(entry)||familyIdentity(undefined,false);
      value={...identity,label:model.familyLabel(identity.key),raw:fields.get('family')??null,field:'family'};
    }else if(dimension==='kind'){
      const scientific=entry.kind==='record',raw=scientific?fields.get('kind'):JSON.stringify(type(entry).key);
      value=typedFacet(dimension,raw,scientific?'kind':'DTO kind');
      value={...value,key:JSON.stringify(['atlas-triage-kind/1',entry.kind,value.key])};
      if(raw!==undefined&&(!scientific||type(entry).key!=='record'))value.label=type(entry).label;
    }else if(dimension==='execution'){
      const key=entry.kind==='record'?first(fields,EXECUTION_STATE_FIELDS):undefined;
      const state=entry.kind==='record'?recordExecutionState(data(entry)):undefined;
      value=typedFacet(dimension,key===undefined?undefined:fields.get(key),key??null,
        {tone:entry.kind==='record'?recordExecutionPresentation(data(entry)).tone:'neutral',
          label:key===undefined?'AUSENTE — campo não declarado':literalText(state)});
    }else if(dimension==='evidence')value=evidenceFacet(entry);
    else{
      const names=dimension==='documentary'?(entry.kind==='record'?['documentary_status']:['documentary_status','status','terminal_status']):own(ALIASES,dimension)?ALIASES[dimension]:[];
      const key=first(fields,names);value=typedFacet(dimension,key===undefined?undefined:fields.get(key),key??null);
    }
    cache.set(dimension,Object.freeze(value));return value;
  }
  function options(dimension,annotations=new Map()){
    const list=dimension==='execution'?items.filter(e=>e.kind==='record'):items,unique=new Map();
    for(const e of list){const f=facet(e,dimension,annotations),prior=unique.get(f.key);unique.set(f.key,{...f,count:(prior?.count||0)+1});}
    if(dimension==='baseline')for(const[key,label]of Object.entries(BASELINE_LABELS))if(!unique.has(key))unique.set(key,{key,label,count:0});
    const labels=new Map();for(const value of unique.values())labels.set(value.label,(labels.get(value.label)||0)+1);
    return [...unique.values()].map(value=>({...value,label:labels.get(value.label)>1?`${value.label} [${value.type}; ${value.raw}]`:value.label}))
      .sort((a,b)=>a.label.localeCompare(b.label,'pt-BR')||a.key.localeCompare(b.key));
  }
  function indexed(entry,annotations){
    if(!searchIndex.has(entry)){
      const list=[{field:'title',label:'Título de apresentação',value:entry.title},
        {field:'uid',label:'UID de apresentação',value:entry.uid},{field:'dto_kind',label:'Tipo de ocorrência',value:type(entry).label}];
      if(entry.source_key!==null&&entry.source_key!==undefined)list.push({field:'source_key',label:'Chave declarada',value:entry.source_key});
      for(const[field,raw]of parts(entry))list.push({field,label:'Campo '+field,value:literalText(literalValue(raw))});
      searchIndex.set(entry,list.map(row=>({...row,index:norm(row.field+' '+row.value)})));
    }
    const list=searchIndex.get(entry),annotation=operatorAnnotation(source,entry,annotations);
    return annotation?[...list,{field:'operator_baseline_note',label:'Anotação do operador (sessão)',value:annotation.note,index:norm(annotation.note)}]:list;
  }
  function reasons(entry,terms,annotations){
    if(!terms.length)return[];const rows=indexed(entry,annotations);
    if(!terms.every(term=>rows.some(row=>term(row.index))))return null;
    return rows.filter(row=>terms.some(term=>term(row.index))).map(({field,label,value})=>({field,label,value}));
  }
  function filtersMatch(entry,filters,annotations){
    if(!TRIAGE_DIMENSIONS.every(({id})=>!filters[id]||facet(entry,id,annotations).key===filters[id]))return false;
    if(filters.from||filters.to){
      const f=facet(entry,'date'),declared=f.present?literalValue(f.raw):undefined,time=isoTime(declared),from=filters.from?isoTime(filters.from):-Infinity,to=filters.to?isoTime(filters.to,true):Infinity;
      if(!Number.isFinite(time)||Number.isNaN(from)||Number.isNaN(to)||time<from||time>to)return false;
    }
    return true;
  }
  function search(filters={},annotations=new Map()){
    const terms=queryTerms(filters.query),results=[];
    for(const entry of items){
      if(!filtersMatch(entry,filters,annotations))continue;
      const why=reasons(entry,terms,annotations);if(why===null)continue;
      const kind=type(entry);results.push({entry,type:kind.key,typeLabel:kind.label,reasons:why,baseline:baseline(entry,annotations)});
    }
    return results;
  }
  function matches(entry,filters={},annotations=new Map()){
    return byUid.get(entry.uid)===entry&&filtersMatch(entry,filters,annotations)&&reasons(entry,queryTerms(filters.query),annotations)!==null;
  }
  function diagnose(filters={},annotations=new Map()){
    const matched=search(filters,annotations),queryMatches=search({query:filters.query},annotations),missingFields=[];
    for(const{id}of TRIAGE_DIMENSIONS)if(filters[id]&&queryMatches.length&&queryMatches.every(hit=>!facet(hit.entry,id,annotations).present))missingFields.push(id);
    const wrongType=filters.kind&&queryMatches.length&&queryMatches.every(hit=>facet(hit.entry,'kind').key!==filters.kind);
    const status=matched.length?'MATCHES':!queryMatches.length?'NOT_FOUND_IN_SNAPSHOT':wrongType?'TYPE_NOT_MATCHING':missingFields.length?'FIELD_ABSENT':'FILTERED_OUT';
    return {status,total:items.length,matched:matched.length,query_matches:queryMatches.length,missing_fields:missingFields};
  }
  function links(entry){
    navigation??=buildNativeNavigation(items);const declared=navigation.outgoing.get(entry.uid)||[],incoming=navigation.incoming.get(entry.uid)||[];
    return {status:declared.length||incoming.length?'DECLARED_REFERENCES':'LINK_NOT_PROVEN',outgoing:declared,incoming};
  }
  return {items,byUid,type,facet,options,baseline,search,matches,diagnose,links};
}

/** Batch selection is independent of focus/detail/navigation. No DOM or storage. */
export class SelectionLedger{
  constructor(source=null){
    this.source=null;this._snapshot=null;this._catalog=new Map();this._selected=new Map();
    this.annotations=new Map();this.intents=new Map();this.bind(source);
  }
  bind(source){
    const incoming=verifiedEntries(source),catalog=new Map(incoming.map(e=>[e.uid,e])),next=snapshotKey(source);
    const changed=this._snapshot!==null&&this._snapshot!==next;
    const drift=[...this._selected.values()].some(e=>{const target=catalog.get(e.uid);return !target||target.kind!==e.kind||target.raw_json!==e.raw_json;})||
      [...this.annotations.values()].some(a=>{const old=this._catalog.get(a.uid),target=catalog.get(a.uid);return !target||!old||target.raw_json!==old.raw_json||target.kind!==old.kind;});
    const invalidated=changed||drift||this._selected.size>0&&!usableSource(source),removed=invalidated?this._selected.size:0;
    if(invalidated){this._selected.clear();this.annotations.clear();this.intents.clear();}
    else for(const[key,e]of this._selected)this._selected.set(key,catalog.get(e.uid));
    this.source=source;this._snapshot=next;this._catalog=catalog;return {invalidated,removed};
  }
  _entry(entry){
    if(!usableSource(this.source))return null;
    const target=this._catalog.get(typeof entry==='string'?entry:entry?.uid);if(!target)return null;
    if(typeof entry!=='string'&&(target.kind!==entry.kind||target.raw_json!==entry.raw_json))throw Error('TRIAGE_OCCURRENCE_OUTSIDE_SNAPSHOT');
    return target;
  }
  has(entry){const e=this._entry(entry);return Boolean(e&&this._selected.has(selectionKey(this.source,e)));}
  toggle(entry){
    const e=this._entry(entry);if(!e)return false;const key=selectionKey(this.source,e);
    if(this._selected.has(key)){this._selected.delete(key);this.intents.delete(key);return false;}
    this._selected.set(key,e);return true;
  }
  selectMany(entries){for(const entry of entries){const e=this._entry(entry);if(e)this._selected.set(selectionKey(this.source,e),e);}return this._selected.size;}
  clear(){this._selected.clear();this.intents.clear();}
  entries(){return [...this._selected.values()];}
  keys(){return [...this._selected.keys()];}
  get size(){return this._selected.size;}
  counts(visibleEntries=[],filteredEntries=visibleEntries){
    const visible=new Set(visibleEntries.map(e=>e.uid)),filtered=new Set(filteredEntries.map(e=>e.uid));
    let visibleCount=0,filteredCount=0;const types=Object.create(null);
    for(const e of this._selected.values()){
      if(visible.has(e.uid))visibleCount++;if(filtered.has(e.uid))filteredCount++;
      const kind=entryType(e).key;types[kind]=(types[kind]||0)+1;
    }
    return {total:this._selected.size,visible:visibleCount,filtered:filteredCount,
      hidden:this._selected.size-filteredCount,hidden_by_filter:this._selected.size-filteredCount,
      off_page:Math.max(0,filteredCount-visibleCount),types,revision:this.source?.revision,
      source_id:this.source?.id,snapshot:this._snapshot};
  }
  annotateBaseline(entry,note){
    const e=this._entry(entry);if(!e)throw Error('TRIAGE_OCCURRENCE_OUTSIDE_SNAPSHOT');
    if(typeof note!=='string'||!note.trim())throw Error('BASELINE_NOTE_REQUIRED');
    const selection_key=selectionKey(this.source,e),annotation=Object.freeze({schema:'atlas-baseline-annotation/1',
      origin:'OPERATOR_SESSION',selection_key,snapshot_key:this._snapshot,uid:e.uid,dto_kind:e.kind,note:note.trim()});
    this.annotations.set(selection_key,annotation);return annotation;
  }
  removeAnnotation(entry){const e=this._entry(entry);return e?this.annotations.delete(selectionKey(this.source,e)):false;}
  setIntent(entry,intent){
    if(!RETENTION_INTENTS.includes(intent))throw Error('RETENTION_INTENT_INVALID');
    const e=this._entry(entry);if(!e||!this.has(e))throw Error('RETENTION_SELECTION_REQUIRED');
    this.intents.set(selectionKey(this.source,e),intent);return intent;
  }
}
