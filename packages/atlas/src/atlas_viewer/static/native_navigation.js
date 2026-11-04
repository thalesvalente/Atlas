/** Derived links within one already verified native snapshot.
 * References are navigation, never a claim of causal/scientific equivalence.
 */
const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
const scalarReferences=new Set(['record_id','atlas_record_id','run_id','native_run_id','external_run_id','execution_id','source_execution_id','source_run_id','resolved_run_id','table_id','row_id','resource_id','document_id','product_id','group_id','item_id','source_id']);
const listReferences=new Set(['resources','document_ids','product_ids','group_ids','item_ids','rf_refs']);
const evidenceFields=new Set(['evidence','trace','source','sources','reference','dossier_ref']);
const endpointFields=new Set(['from','to','from_key','to_key']);

/** Exact top-level JSON fragments; numbers never pass through JS Number. */
export function nativeFragments(raw){
  const fragments=new Map();if(raw[0]!=='{')return fragments;
  const stringEnd=start=>{let escaped=false;for(let i=start+1;i<raw.length;i++){if(escaped){escaped=false;continue;}if(raw[i]==='\\'){escaped=true;continue;}if(raw[i]==='"')return i+1;}return raw.length;};
  let i=1;
  while(i<raw.length){
    while(/[\s,]/.test(raw[i]||''))i++;
    if(raw[i]!== '"')break;
    const end=stringEnd(i),key=JSON.parse(raw.slice(i,end));i=end;
    while(/\s/.test(raw[i]||''))i++;
    if(raw[i++]!==':')break;
    while(/\s/.test(raw[i]||''))i++;
    const start=i;let depth=0;
    for(;i<raw.length;i++){
      const ch=raw[i];
      if(ch==='"'){i=stringEnd(i)-1;continue;}
      if(ch==='{'||ch==='[')depth++;
      else if(ch==='}'||ch===']'){if(depth===0)break;depth--;}
      else if(ch===','&&depth===0)break;
    }
    if(listReferences.has(key)||evidenceFields.has(key)||endpointFields.has(key)||key==='source_ids')fragments.set(key,raw.slice(start,i).trim());
    if(raw[i]==='}')break;
  }
  return fragments;
}

export function declaredSourceAliases(entry){
  if(entry.kind!=='record')return[];
  const raw=nativeFragments(entry.raw_json).get('source_ids');if(!raw)return[];
  const values=JSON.parse(raw);return Array.isArray(values)?values.filter(value=>typeof value==='string'&&value):[];
}

export function buildNativeNavigation(entries){
  const byUid=new Map(entries.map(e=>[e.uid,e])),index=new Map(),recordIndex=new Map(),keyIndex=new Map(),fragments=new Map(),outgoing=new Map(),incoming=new Map(),evidence=new Map();
  const put=(map,value,uid)=>{if(typeof value!=='string'||!value)return;if(!map.has(value))map.set(value,new Set());map.get(value).add(uid);};
  for(const e of entries){
    const nativeField=e.fields.find(field=>field.name==='native_id')||(e.kind==='record'?e.fields.find(field=>field.name==='id'):null);
    const nativeText=nativeField?.type==='string'&&nativeField.text===e.native_id?e.native_id:null;
    for(const value of [e.source_key,nativeText])put(index,value,e.uid);
    if(e.kind==='node')put(keyIndex,e.source_key,e.uid);
    const parts=nativeFragments(e.raw_json);fragments.set(e.uid,parts);
    if(e.kind==='record'){
      for(const value of [e.source_key,nativeText])put(recordIndex,value,e.uid);
      // source_ids are explicitly declared aliases, not inferred equality.
      if(parts.has('source_ids')){const aliases=JSON.parse(parts.get('source_ids'));if(Array.isArray(aliases))for(const alias of aliases)put(recordIndex,alias,e.uid);}
    }
    evidence.set(e.uid,[...parts].filter(([name])=>evidenceFields.has(name)));
  }
  const reference=(e,label,literal,map=index,direct=null)=>{
    const candidates=direct?[direct].filter(uid=>byUid.has(uid)):
      typeof literal==='string'?[...(map.get(literal)||[])].filter(uid=>uid!==e.uid):[];
    const ref={label,literal,targets:candidates,resolution:literal===null?'NOT_DECLARED':candidates.length===1?'UNIQUE':candidates.length?'COLLISION':'UNRESOLVED'};
    outgoing.get(e.uid).push(ref);
    for(const uid of candidates){if(!incoming.has(uid))incoming.set(uid,[]);incoming.get(uid).push({uid:e.uid,label,resolution:ref.resolution});}
  };
  for(const e of entries){
    outgoing.set(e.uid,[]);
    if(e.parent_uid)reference(e,'parent_uid',e.parent_uid,index,e.parent_uid);
    if(e.kind==='row'&&e.table_uid)reference(e,'table_uid',e.table_uid,index,e.table_uid);
    for(const field of e.fields){
      if(!scalarReferences.has(field.name))continue;
      // Only text/null reference literals are interpreted. Numeric IDs remain
      // exact in fields/raw JSON, without coercion into another namespace.
      if(field.type!=='string'&&field.type!=='null')continue;
      const map=/^(record_id|atlas_record_id|run_id|native_run_id|external_run_id|execution_id|source_execution_id|source_run_id|resolved_run_id)$/.test(field.name)?recordIndex:index;
      reference(e,field.name,field.type==='null'?null:field.text,map);
    }
    if(e.kind==='relation')for(const endpoint of ['from','to']){
      const parts=fragments.get(e.uid),keyed=parts.has(endpoint+'_key'),name=keyed?endpoint+'_key':endpoint;
      if(!parts.has(name))continue;
      const field=e.fields.find(f=>f.name===name);
      if(field&&(field.type==='string'||field.type==='null'))reference(e,name,field.type==='null'?null:field.text,keyed?keyIndex:index);
      // Composite/numeric keys are explicit declarations even though they are
      // omitted from scalar fields. Preserve their exact literal and never
      // reinterpret the other endpoint field as a fallback scientific ID.
      else outgoing.get(e.uid).push({label:name,literal:parts.get(name),targets:[],resolution:'NOT_INTERPRETED'});
    }
    for(const[name,raw]of fragments.get(e.uid)){
      if(!listReferences.has(name))continue;
      const values=JSON.parse(raw);if(!Array.isArray(values))continue;
      for(let n=0;n<values.length;n++){
        const value=values[n];if(typeof value==='string'||value===null)reference(e,`${name}[${n}]`,value);
        else if(value&&typeof value==='object'&&!Array.isArray(value))for(const key of ['id','resource_id','document_id','record_id','source_id'])if(own(value,key)&&(typeof value[key]==='string'||value[key]===null))reference(e,`${name}[${n}].${key}`,value[key],key==='record_id'?recordIndex:index);
      }
    }
  }
  return{byUid,outgoing,incoming,evidence};
}
