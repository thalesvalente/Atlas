/* Atlas F3A: isolated in-memory presentation, original synthetic implementation.
 * Schema copied verbatim as data from approved descriptor 0.2.0 (blob
 * 25d79a11171c157bd3c7e0f98d1449a78237fd9c). No runtime integration.
 */
const SCHEMA = {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:atlas:proposal:legacy-presentation:0.2.0","type":"object","additionalProperties":false,"required":["format","version","authority","synthetic","source","snapshot","validation","policy","nodes","tables","relations","assets","unmapped_fields","coverage","gaps"],"properties":{"format":{"const":"atlas-legacy-presentation"},"version":{"const":"0.2.0"},"authority":{"const":"LEGACY_DERIVED"},"synthetic":{"type":"boolean"},"source":{"$ref":"#/$defs/source"},"snapshot":{"$ref":"#/$defs/snapshot"},"validation":{"$ref":"#/$defs/validation"},"policy":{"$ref":"#/$defs/policy"},"nodes":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/node"}},"tables":{"type":"array","maxItems":128,"items":{"$ref":"#/$defs/table"}},"relations":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/relation"}},"assets":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/asset"}},"unmapped_fields":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/unmapped"}},"coverage":{"$ref":"#/$defs/coverage"},"gaps":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/gap"}}},"allOf":[{"if":{"properties":{"synthetic":{"const":false}}},"then":{"properties":{"snapshot":{"properties":{"binding_basis":{"const":"OBSERVED_BYTES_AND_POLICY"},"digest_status":{"const":"OBSERVED_BYTES"},"bytes_sha256":{"type":"string","pattern":"^[0-9a-f]{64}$"}}}}}}],"$defs":{"text":{"type":"string","maxLength":65536},"nullable_text":{"type":["string","null"],"maxLength":65536},"navigation_id":{"type":"string","pattern":"^nav:[A-Za-z0-9._:-]+$","maxLength":512},"source":{"type":"object","additionalProperties":false,"required":["source_id","scope","original_format","original_profile_declared","availability","access_policy_id","declared_scientific_review"],"properties":{"source_id":{"type":"string","minLength":1,"maxLength":512},"scope":{"$ref":"#/$defs/text"},"original_format":{"type":"string","minLength":1,"maxLength":256},"original_profile_declared":{"$ref":"#/$defs/nullable_text"},"availability":{"enum":["OBSERVED_AVAILABLE","UNAVAILABLE","UNKNOWN","CHANGED","EXPIRED"]},"access_policy_id":{"type":"string","minLength":1,"maxLength":512},"declared_scientific_review":{"$ref":"#/$defs/nullable_text"}}},"snapshot":{"type":"object","additionalProperties":false,"required":["snapshot_id","binding_basis","bytes_sha256","digest_status","observed_at","scientific_at","generated_at","expires_at","freshness"],"properties":{"snapshot_id":{"type":"string","minLength":1,"maxLength":512},"binding_basis":{"enum":["OBSERVED_BYTES_AND_POLICY","SYNTHETIC_FIXTURE"]},"bytes_sha256":{"type":["string","null"],"pattern":"^[0-9a-f]{64}$"},"digest_status":{"enum":["OBSERVED_BYTES","NOT_COMPUTED"]},"observed_at":{"type":"string","format":"date-time"},"scientific_at":{"type":["string","null"],"format":"date-time"},"generated_at":{"type":"string","format":"date-time"},"expires_at":{"type":"string","format":"date-time"},"freshness":{"const":"OBSERVED_SNAPSHOT_ONLY"}}},"validation":{"type":"object","additionalProperties":false,"required":["descriptor_schema","descriptor_semantics","literal_comparison","source_profile_assessment","authenticity","scientific_approval"],"properties":{"descriptor_schema":{"enum":["NOT_RUN","PASS","FAIL"]},"descriptor_semantics":{"enum":["NOT_RUN","PASS","FAIL"]},"literal_comparison":{"enum":["NOT_PERFORMED","SOURCE_FIELD_COMPARED","SOURCE_ROW_COMPARED"]},"source_profile_assessment":{"const":"NOT_ASSERTED"},"authenticity":{"const":"NOT_VERIFIED"},"scientific_approval":{"const":"NOT_EVALUATED"}}},"policy":{"type":"object","additionalProperties":false,"required":["source_access","max_descriptor_bytes","ttl_max_seconds","browser_persistence","automatic_uri_access"],"properties":{"source_access":{"const":"EXTERNAL_EXACT_ALLOWLIST_ONLY"},"max_descriptor_bytes":{"const":33554432},"ttl_max_seconds":{"const":3600},"browser_persistence":{"const":"MEMORY_ONLY"},"automatic_uri_access":{"const":false}}},"identity":{"type":"object","additionalProperties":false,"required":["native_id","navigation_id","navigation_id_kind","occurrence","locator"],"properties":{"native_id":{"type":["string","null"],"minLength":1,"maxLength":4096},"navigation_id":{"$ref":"#/$defs/navigation_id"},"navigation_id_kind":{"const":"DERIVED_FOR_PRESENTATION"},"occurrence":{"type":"integer","minimum":0},"locator":{"type":"string","maxLength":8192}}},"reference":{"type":"object","additionalProperties":false,"required":["source_id","snapshot_id","declared_id","target_navigation_id","resolution","evidence_locator"],"properties":{"source_id":{"type":["string","null"],"maxLength":512},"snapshot_id":{"type":["string","null"],"maxLength":512},"declared_id":{"type":["string","null"],"maxLength":4096},"target_navigation_id":{"anyOf":[{"$ref":"#/$defs/navigation_id"},{"type":"null"}]},"resolution":{"enum":["RESOLVED","NULL_ENDPOINT","UNRESOLVED","COLLISION","EXTERNAL_DECLARED"]},"evidence_locator":{"type":["string","null"],"maxLength":8192}}},"cell":{"type":"object","additionalProperties":false,"required":["type","literal","lexeme","unit","precision","absence"],"properties":{"type":{"enum":["string","integer","decimal","boolean","null","missing","array","object"]},"literal":{"$ref":"#/$defs/nullable_text"},"lexeme":{"type":["string","null"],"maxLength":131072},"unit":{"type":["string","null"],"maxLength":256},"precision":{"type":["string","null"],"maxLength":128},"absence":{"enum":[null,"NULL","MISSING"]}},"allOf":[{"if":{"properties":{"type":{"enum":["string","integer","decimal","boolean","array","object"]}}},"then":{"properties":{"literal":{"type":"string"},"lexeme":{"type":"string"},"absence":{"const":null}}}},{"if":{"properties":{"type":{"const":"integer"}}},"then":{"properties":{"literal":{"pattern":"^-?(0|[1-9][0-9]*)$"}}}},{"if":{"properties":{"type":{"const":"decimal"}}},"then":{"properties":{"literal":{"pattern":"^-?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?$"}}}},{"if":{"properties":{"type":{"const":"boolean"}}},"then":{"properties":{"literal":{"enum":["true","false"]}}}},{"if":{"properties":{"type":{"const":"null"}}},"then":{"properties":{"literal":{"const":null},"lexeme":{"const":"null"},"absence":{"const":"NULL"}}}},{"if":{"properties":{"type":{"const":"missing"}}},"then":{"properties":{"literal":{"const":null},"lexeme":{"const":null},"absence":{"const":"MISSING"}}}}]},"node":{"type":"object","additionalProperties":false,"required":["identity","kind","original_type","entity_status","label_literal","family_literal","parent_key_literal","parent","tree_state","external_reference","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind":{"enum":["Project","Family","Experiment","Run","Other","Unknown"]},"original_type":{"$ref":"#/$defs/nullable_text"},"entity_status":{"enum":["SOURCE_ENTITY","DECLARED_EXTERNAL_REFERENCE"]},"label_literal":{"$ref":"#/$defs/text"},"family_literal":{"$ref":"#/$defs/nullable_text"},"parent_key_literal":{"$ref":"#/$defs/nullable_text"},"parent":{"$ref":"#/$defs/reference"},"tree_state":{"enum":["ROOT_DECLARED","PARENT_RESOLVED","ORPHAN","PARENT_UNKNOWN","RUN_EXTERNAL_ISOLATED"]},"external_reference":{"anyOf":[{"$ref":"#/$defs/reference"},{"type":"null"}]},"binding_gap":{"type":"boolean"}},"allOf":[{"if":{"properties":{"entity_status":{"const":"DECLARED_EXTERNAL_REFERENCE"}}},"then":{"properties":{"identity":{"properties":{"native_id":{"const":null}}},"tree_state":{"const":"RUN_EXTERNAL_ISOLATED"},"binding_gap":{"const":true},"external_reference":{"$ref":"#/$defs/reference"}}}}]},"column":{"type":"object","additionalProperties":false,"required":["ordinal","native_key","header_literal"],"properties":{"ordinal":{"type":"integer","minimum":0,"maximum":255},"native_key":{"$ref":"#/$defs/nullable_text"},"header_literal":{"$ref":"#/$defs/text"}}},"column_index":{"type":["integer","null"],"minimum":0,"maximum":255},"requirement_fields":{"type":"object","additionalProperties":false,"required":["id","module","title","description","acceptance_criteria","category"],"properties":{"id":{"$ref":"#/$defs/column_index"},"module":{"$ref":"#/$defs/column_index"},"title":{"$ref":"#/$defs/column_index"},"description":{"$ref":"#/$defs/column_index"},"acceptance_criteria":{"$ref":"#/$defs/column_index"},"category":{"$ref":"#/$defs/column_index"}}},"requirement":{"type":"object","additionalProperties":false,"required":["kind","native_id","admission","admission_evidence_locator","fields","category_status"],"properties":{"kind":{"enum":["RF","RNF","RES"]},"native_id":{"type":["string","null"],"minLength":1,"maxLength":4096},"admission":{"enum":["ADMITTED_NATIVE_RF","UNADMITTED_NATIVE_RF","NOT_EVALUATED","NOT_APPLICABLE"]},"admission_evidence_locator":{"type":["string","null"],"maxLength":8192},"fields":{"$ref":"#/$defs/requirement_fields"},"category_status":{"enum":["MISSING","PRESENT","UNKNOWN"]}},"allOf":[{"if":{"properties":{"admission":{"const":"UNADMITTED_NATIVE_RF"}}},"then":{"properties":{"kind":{"const":"RF"},"native_id":{"const":null}}}},{"if":{"properties":{"admission":{"const":"ADMITTED_NATIVE_RF"}}},"then":{"properties":{"kind":{"const":"RF"},"native_id":{"type":"string","minLength":1},"admission_evidence_locator":{"type":"string","minLength":1}}}}]},"row":{"type":"object","additionalProperties":false,"required":["identity","ordinal","cells","requirement","run_binding","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"ordinal":{"type":"integer","minimum":0},"cells":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/cell"}},"requirement":{"anyOf":[{"$ref":"#/$defs/requirement"},{"type":"null"}]},"run_binding":{"$ref":"#/$defs/reference"},"binding_gap":{"type":"boolean"}}},"table":{"type":"object","additionalProperties":false,"required":["identity","title_literal","domain","domain_origin","record_binding","columns","rows"],"properties":{"identity":{"$ref":"#/$defs/identity"},"title_literal":{"$ref":"#/$defs/text"},"domain":{"enum":["RF","RNF","RES","UNKNOWN","OTHER"]},"domain_origin":{"enum":["DECLARED","UNKNOWN"]},"record_binding":{"$ref":"#/$defs/reference"},"columns":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/column"}},"rows":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/row"}}}},"relation":{"type":"object","additionalProperties":false,"required":["identity","kind_literal","semantics","direction","from","to","evidence_locator","issues","repeat_group","repeat_occurrence","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind_literal":{"$ref":"#/$defs/nullable_text"},"semantics":{"enum":["ORGANIZATIONAL_MEMBERSHIP","DECLARED_LINEAGE","DECLARED_BINDING","NEUTRAL_MENTION","UNKNOWN"]},"direction":{"enum":["FROM_TO","UNDIRECTED","UNKNOWN"]},"from":{"$ref":"#/$defs/reference"},"to":{"$ref":"#/$defs/reference"},"evidence_locator":{"type":["string","null"],"maxLength":8192},"issues":{"type":"array","maxItems":32,"items":{"type":"string","maxLength":256}},"repeat_group":{"type":["string","null"],"maxLength":512},"repeat_occurrence":{"type":"integer","minimum":1},"binding_gap":{"type":"boolean"}}},"asset":{"type":"object","additionalProperties":false,"required":["identity","kind","original_type","label_literal","declared_product_role","declared_binding","media_type_literal","uri_literal","availability","opened"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind":{"enum":["File","Product","ProductGroup","ResourceDocument","DossierAssessment","DossierPackage","Other","Unknown"]},"original_type":{"$ref":"#/$defs/nullable_text"},"label_literal":{"$ref":"#/$defs/text"},"declared_product_role":{"$ref":"#/$defs/nullable_text"},"declared_binding":{"$ref":"#/$defs/reference"},"media_type_literal":{"type":["string","null"],"maxLength":256},"uri_literal":{"$ref":"#/$defs/nullable_text"},"availability":{"enum":["OBSERVED_AVAILABLE","DECLARED_ONLY","UNVERIFIED","MISSING","EXTERNAL_UNRESOLVED","UNKNOWN","INTEGRITY_MISMATCH"]},"opened":{"const":false}}},"unmapped":{"type":"object","additionalProperties":false,"required":["owner_navigation_id","locator","source_key_literal","value"],"properties":{"owner_navigation_id":{"anyOf":[{"$ref":"#/$defs/navigation_id"},{"type":"null"}]},"locator":{"type":"string","maxLength":8192},"source_key_literal":{"$ref":"#/$defs/text"},"value":{"$ref":"#/$defs/cell"}}},"count":{"type":"object","additionalProperties":false,"required":["unit","selected","loaded","visible","unavailable","unknown_reason"],"properties":{"unit":{"type":"string","minLength":1,"maxLength":256},"selected":{"type":["integer","null"],"minimum":0},"loaded":{"type":"integer","minimum":0},"visible":{"type":["integer","null"],"minimum":0},"unavailable":{"type":["integer","null"],"minimum":0},"unknown_reason":{"$ref":"#/$defs/nullable_text"}}},"coverage":{"type":"object","additionalProperties":false,"required":["population","global_archive","global_history","global_total","global_percentage","snapshot_overlap","counts"],"properties":{"population":{"enum":["SELECTED_QUALIFYING_PAYLOAD","SYNTHETIC_FIXTURE"]},"global_archive":{"const":"UNKNOWN_UPSTREAM"},"global_history":{"const":"GLOBAL_UNPROVEN"},"global_total":{"const":null},"global_percentage":{"const":null},"snapshot_overlap":{"enum":["NOT_SUMMED","UNKNOWN"]},"counts":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/count"}}}},"gap":{"type":"object","additionalProperties":false,"required":["code","scope","count","unit","note"],"properties":{"code":{"type":"string","minLength":1,"maxLength":256},"scope":{"$ref":"#/$defs/text"},"count":{"type":["integer","null"],"minimum":0},"unit":{"type":"string","minLength":1,"maxLength":256},"note":{"$ref":"#/$defs/text"}}}}};
export const LIMITS = Object.freeze({descriptorBytes:33554432, depth:20, nodes:10000,
  relations:100000, renderNodes:1000, renderRelations:4000, operationMs:30000});
const NS = "http://www.w3.org/2000/svg";
const encoder = new TextEncoder();
let mountSerial = 0;
const fail = (message) => { throw new Error(message); };
const own = (v,k) => Object.prototype.hasOwnProperty.call(v,k);
const finite = (v) => typeof v === "number" && Number.isFinite(v);
const isObject = (v) => v !== null && typeof v === "object" && !Array.isArray(v);
const text = (v) => v === null ? "null" : String(v);
function validDateTime(value) {
  const m=/^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(?:\.\d+)?(Z|[+-](\d\d):(\d\d))$/i.exec(value);
  if(!m)return false;
  const year=Number(m[1]),month=Number(m[2]),day=Number(m[3]);
  const leap=year%4===0 && (year%100!==0 || year%400===0);
  const days=[31,leap?29:28,31,30,31,30,31,31,30,31,30,31];
  return month>=1 && month<=12 && day>=1 && day<=days[month-1] &&
    Number(m[4])<=23 && Number(m[5])<=59 && Number(m[6])<=59 &&
    (m[7].toUpperCase()==="Z" || (Number(m[8])<=23 && Number(m[9])<=59)) &&
    Number.isFinite(Date.parse(value));
}
function validateSchema(v, s, path="$") {
  if (s.$ref) return validateSchema(v,SCHEMA.$defs[s.$ref.split("/").pop()],path);
  if (s.type) {
    const matches = t => t === "null" ? v === null : t === "array" ? Array.isArray(v) :
      t === "object" ? isObject(v) : t === "integer" ? Number.isSafeInteger(v) : typeof v === t;
    if (!(Array.isArray(s.type)?s.type:[s.type]).some(matches)) fail(path+": invalid type");
  }
  if (own(s,"const") && v !== s.const) fail(path+": invalid constant");
  if (s.enum && !s.enum.includes(v)) fail(path+": invalid enum");
  if (typeof v === "string") {
    const length = [...v].length;
    if ((own(s,"maxLength") && length>s.maxLength) || (own(s,"minLength") && length<s.minLength))
      fail(path+": string length limit");
    if (s.pattern && !new RegExp(s.pattern).test(v)) fail(path+": invalid pattern");
    if (s.format === "date-time" && !validDateTime(v))
      fail(path+": invalid date-time");
  }
  if (typeof v === "number" && ((own(s,"minimum") && v<s.minimum) || (own(s,"maximum") && v>s.maximum)))
    fail(path+": numeric range");
  if (Array.isArray(v)) {
    if (own(s,"maxItems") && v.length>s.maxItems) fail(path+": array quota");
    if (s.items) v.forEach((x,i)=>validateSchema(x,s.items,path+"["+i+"]"));
  }
  if (isObject(v)) {
    if (s.required) for (const k of s.required) if (!own(v,k)) fail(path+": missing "+k);
    if (s.additionalProperties === false)
      for (const k of Object.keys(v)) if (!own(s.properties||{},k)) fail(path+": extra property "+k);
    if (s.properties) for (const [k,rule] of Object.entries(s.properties))
      if (own(v,k)) validateSchema(v[k],rule,path+"."+k);
  }
  if (s.anyOf) {
    if (!s.anyOf.some(rule=>{try{validateSchema(v,rule,path);return true;}catch{return false;}}))
      fail(path+": no allowed alternative");
  }
  if (s.allOf) s.allOf.forEach(rule=>validateSchema(v,rule,path));
  if (s.if) {
    let matches=true; try {validateSchema(v,s.if,path);} catch {matches=false;}
    if (matches && s.then) validateSchema(v,s.then,path);
  }
}
function copyJSON(input, checkpoint) {
  let budget=0, values=0;
  const active=new Set();
  function visit(v,depth) {
    checkpoint();
    if (++values>600000 || depth>LIMITS.depth) fail("Descriptor depth/value quota exceeded");
    if (v === null || typeof v === "boolean") {budget+=5;return v;}
    if (finite(v)) {budget+=24;return v;}
    if (typeof v === "string") {
      if (v.length>131072 || encoder.encode(v).length>131072) fail("Descriptor literal byte quota exceeded");
      budget+=encoder.encode(JSON.stringify(v)).length+1;
      if (budget>LIMITS.descriptorBytes) fail("Descriptor byte quota exceeded");
      return v;
    }
    if (!v || typeof v !== "object") fail("Descriptor must contain only JSON data");
    if (active.has(v)) fail("Descriptor JSON cycle");
    const proto=Object.getPrototypeOf(v);
    if (proto!==Object.prototype && proto!==Array.prototype && proto!==null) fail("Non-JSON object");
    active.add(v); budget+=2;
    const result=Array.isArray(v)?[]:Object.create(null);
    for (const key of Reflect.ownKeys(v)) {
      if (Array.isArray(v) && key==="length") continue;
      if (typeof key !== "string") fail("Symbol properties are not JSON");
      const prop=Object.getOwnPropertyDescriptor(v,key);
      if (!own(prop,"value") || !prop.enumerable) fail("Descriptor accessors are not JSON data");
      if (Array.isArray(v) && !/^(0|[1-9]\d*)$/.test(key)) fail("Non-JSON array property");
      budget+=encoder.encode(JSON.stringify(key)).length+2;
      result[key]=visit(prop.value,depth+1);
      if (budget>LIMITS.descriptorBytes) fail("Descriptor byte quota exceeded");
    }
    if (Array.isArray(v) && Object.keys(result).length!==v.length) fail("Sparse array is not JSON data");
    active.delete(v); return result;
  }
  const result=visit(input,0);
  if (encoder.encode(JSON.stringify(result)).length>LIMITS.descriptorBytes) fail("Descriptor byte quota exceeded");
  return result;
}
function semanticModel(d, now, checkpoint) {
  function validateCell(c) {
    checkpoint();
    if(c.type==="null" || c.type==="missing")return;
    if(encoder.encode(c.literal).length>65536)fail("Cell literal byte quota");
    if(c.type==="string") {
      let value;try{value=JSON.parse(c.lexeme);}catch{fail("Invalid string lexeme");}
      if(value!==c.literal)fail("String literal/lexeme mismatch");
    } else {
      if(c.lexeme!==c.literal)fail("Typed literal/lexeme mismatch");
      if(c.type==="array" || c.type==="object") {
        let value;try{value=JSON.parse(c.lexeme);}catch{fail("Invalid JSON cell");}
        if(c.type==="array"?!Array.isArray(value):!isObject(value))fail("JSON cell type mismatch");
        copyJSON(value,checkpoint); // Inner JSON is still inert; validate its own depth/byte budget.
      }
    }
  }
  if (d.validation.descriptor_schema!=="PASS" || d.validation.descriptor_semantics!=="PASS")
    fail("Descriptor validation must be PASS; presentation never grants scientific approval");
  if(["CHANGED","EXPIRED"].includes(d.source.availability))fail("Source context invalidated: "+d.source.availability);
  const observed=Date.parse(d.snapshot.observed_at), generated=Date.parse(d.snapshot.generated_at),
    expires=Date.parse(d.snapshot.expires_at);
  if (!(observed<=generated && generated<expires && expires-generated<=3600000))
    fail("Invalid snapshot chronology/TTL");
  if (!finite(now) || now>=expires) fail("EXPIRED snapshot");
  const identities=new Map(), natives=new Map(), refs=[];
  function register(item, type) {
    checkpoint();
    const id=item.identity;
    if (identities.has(id.navigation_id)) fail("Duplicate navigation_id");
    identities.set(id.navigation_id,{item,type});
    if (id.native_id!==null) {
      const list=natives.get(id.native_id)||[]; list.push(item); natives.set(id.native_id,list);
    }
  }
  function ref(r) {refs.push(r);}
  d.nodes.forEach(n=>{register(n,"node");ref(n.parent);if(n.external_reference)ref(n.external_reference);});
  let rows=0;
  d.tables.forEach(t=>{
    register(t,"table");ref(t.record_binding); rows+=t.rows.length;
    t.columns.forEach((c,i)=>{if(c.ordinal!==i)fail("Noncontiguous column ordinals");});
    t.rows.forEach((r,i)=>{
      register(r,"row"); ref(r.run_binding);
      if(r.ordinal!==i || r.cells.length!==t.columns.length) fail("Row ordinal/cell mismatch");
      r.cells.forEach(validateCell);
      if(r.requirement) {
        const q=r.requirement;
        for(const index of Object.values(q.fields)) if(index!==null && index>=t.columns.length)
          fail("Requirement cell index out of range");
        if(q.admission==="UNADMITTED_NATIVE_RF" && (q.native_id!==null || r.identity.native_id!==null))
          fail("Unadmitted RF cannot gain native identity");
        if(q.admission==="ADMITTED_NATIVE_RF") {
          if(!q.native_id || !q.admission_evidence_locator || q.native_id!==r.identity.native_id)
            fail("Admitted RF evidence/identity mismatch");
          if(q.fields.id!==null && r.cells[q.fields.id].literal!==q.native_id)
            fail("RF ID does not match original cell");
        }
      }
    });
  });
  if(rows>100000) fail("Aggregate row quota exceeded");
  d.assets.forEach(a=>{register(a,"asset");ref(a.declared_binding);
    if(a.original_type==="File" && a.kind!=="File")fail("File cannot be promoted to Product");
  });
  d.relations.forEach(r=>{register(r,"relation");ref(r.from);ref(r.to);});
  for(const [native] of natives) if(identities.has(native)) fail("Navigation identity promoted to native_id");
  for(const field of d.unmapped_fields) {
    validateCell(field.value);
    if(field.owner_navigation_id!==null && !identities.has(field.owner_navigation_id))
      fail("Unmapped field owner is absent");
  }
  for(const r of refs) {
    checkpoint();
    const target=r.target_navigation_id===null?null:identities.get(r.target_navigation_id);
    if(r.resolution==="NULL_ENDPOINT" && (r.declared_id!==null || r.target_navigation_id!==null))
      fail("NULL_ENDPOINT must remain null");
    if(["UNRESOLVED","COLLISION"].includes(r.resolution) && r.target_navigation_id!==null)
      fail("Unresolved/colliding reference cannot choose a target");
    if(r.resolution==="RESOLVED") {
      if(r.source_id!==d.source.source_id || r.snapshot_id!==d.snapshot.snapshot_id ||
        !target || target.type==="relation" || target.item.entity_status==="DECLARED_EXTERNAL_REFERENCE" ||
        r.declared_id===null || target.item.identity.native_id!==r.declared_id ||
        natives.get(r.declared_id)?.length!==1 || !r.evidence_locator)
        fail("RESOLVED requires unique original target, identity, context and evidence");
    }
    if(r.resolution==="EXTERNAL_DECLARED" && r.target_navigation_id!==null &&
      (!target || target.type!=="node" || target.item.entity_status!=="DECLARED_EXTERNAL_REFERENCE"))
      fail("External declaration may only navigate to an explicit stub");
  }
  const nodes=new Map(d.nodes.map(n=>[n.identity.navigation_id,n]));
  const parents=new Map(),children=new Map(d.nodes.map(n=>[n.identity.navigation_id,[]]));
  const cycles=new Set(),done=new Set();
  for(const n of d.nodes) {
    const id=n.identity.navigation_id;
    if(n.tree_state==="PARENT_RESOLVED") {
      if(n.parent.resolution!=="RESOLVED" || !nodes.has(n.parent.target_navigation_id) ||
        n.parent_key_literal!==n.parent.declared_id) fail("Parent requires explicit matching parent_key");
      parents.set(id,n.parent.target_navigation_id);
    } else if(n.parent.resolution==="RESOLVED") fail("Resolved parent contradicts tree_state");
    if(n.tree_state==="RUN_EXTERNAL_ISOLATED" && parents.has(id))fail("Isolated Run has parent");
  }
  for(const id of nodes.keys()) {
    if(done.has(id))continue;
    const chain=[], local=new Map();let current=id;
    while(current!==undefined && !done.has(current)) {
      checkpoint();
      if(local.has(current)) {for(const member of chain.slice(local.get(current)))cycles.add(member);break;}
      local.set(current,chain.length);chain.push(current);current=parents.get(current);
    }
    chain.forEach(x=>done.add(x));
  }
  // Retain original cyclic parent data; remove only UI traversal arcs.
  for(const id of cycles)parents.delete(id);
  for(const [id,parent] of parents)children.get(parent).push(id);
  const endpointCounts={RESOLVED:0,NULL_ENDPOINT:0,UNRESOLVED:0,COLLISION:0,EXTERNAL_DECLARED:0};
  for(const r of d.relations){endpointCounts[r.from.resolution]++;endpointCounts[r.to.resolution]++;}
  const knownCounts={presentation_node_occurrences:d.nodes.length,
    source_nodes:d.nodes.filter(n=>n.entity_status==="SOURCE_ENTITY").length,
    external_reference_stubs:d.nodes.filter(n=>n.entity_status==="DECLARED_EXTERNAL_REFERENCE").length,
    tables:d.tables.length,rows,relations:d.relations.length,assets:d.assets.length};
  for(const count of d.coverage.counts)
    if(own(knownCounts,count.unit) && count.loaded!==knownCounts[count.unit])fail("Coverage loaded count mismatch");
  return {d,nodes,parents,children,cycles,natives,endpointCounts,expires};
}
function element(tag, attrs={}, label=null, svg=false) {
  const e=svg?document.createElementNS(NS,tag):document.createElement(tag);
  for(const [key,value] of Object.entries(attrs)) e.setAttribute(key,String(value));
  if(label!==null)e.textContent=label;
  return e;
}
function fitSVGText(e,value,maxWidth) {
  const chars=[...value], candidates=chars.slice(0,256);
  let low=0,high=candidates.length,best="";
  while(low<=high) {
    const mid=Math.floor((low+high)/2);
    const candidate=candidates.slice(0,mid).join("")+(mid<chars.length?"…":"");
    e.textContent=candidate;
    if(e.getComputedTextLength()<=maxWidth) {best=candidate;low=mid+1;} else high=mid-1;
  }
  e.textContent=best;
  if(e.getComputedTextLength()===0 && best.length>20) {
    // Detached hosts cannot measure fonts; keep a bounded glyph box until attached.
    e.setAttribute("textLength",String(maxWidth));e.setAttribute("lengthAdjust","spacingAndGlyphs");
  }
}
function makeButton(action,label) {
  return element("button",{type:"button","data-action":action,"data-f3a-action":action},label);
}
/** Mount into an otherwise empty dedicated host. No IO, storage, or data execution. */
export function mount(host, descriptor, options={}) {
  if(!(host instanceof Element))throw new TypeError("F3A mount requires an Element");
  const now=options.now || (()=>Date.now());
  if(typeof now!=="function")throw new TypeError("now must be a function");
  const instance=++mountSerial,abort=new AbortController(),signal=abort.signal;
  const root=element("section",{class:"f3a-graph","aria-label":"Apresentação legada — grafo derivado"});
  const banner=element("p",{class:"f3a-banner"}),toolbar=element("div",{class:"f3a-toolbar","aria-label":"Controles do grafo"});
  const controls=[
    ["zoom-in","Ampliar +"],["zoom-out","Reduzir −"],["pan-left","Mover ←"],["pan-right","Mover →"],
    ["pan-up","Mover ↑"],["pan-down","Mover ↓"],["reset","Restaurar"],["fit","Ajustar"]];
  controls.forEach(([action,label])=>toolbar.append(makeButton(action,label)));
  const zoomLabel=element("output",{"aria-label":"Escala",class:"f3a-zoom"});
  toolbar.append(zoomLabel);
  const status=element("p",{class:"f3a-status",role:"status","aria-live":"polite"});
  const error=element("p",{class:"f3a-error",role:"alert",hidden:""});
  const viewport=element("div",{class:"f3a-viewport"});
  const svg=element("svg",{class:"f3a-svg",role:"tree","aria-label":"Árvore hierárquica declarada",
    "data-f3a-canvas":"true",tabindex:"0",viewBox:"0 0 1000 440"},null,true);
  const defs=element("defs",{},null,true);
  for(const cls of ["lineage","binding"]){
    const marker=element("marker",{id:"f3a-"+instance+"-"+cls,viewBox:"0 0 10 10",refX:"9",refY:"5",
      markerWidth:"7",markerHeight:"7",orient:"auto-start-reverse"},null,true);
    marker.append(element("path",{d:"M 0 0 L 10 5 L 0 10 z",class:"f3a-arrow-"+cls},null,true));defs.append(marker);
  }
  const world=element("g",{class:"f3a-world"},null,true);svg.append(defs,world);viewport.append(svg);
  const mini=element("svg",{"data-minimap":"true",class:"f3a-minimap",role:"button",tabindex:"0",
    "aria-label":"Minimapa navegável. Clique para centrar; setas movem a vista.",viewBox:"0 0 1000 440"},null,true);
  const legend=element("ul",{class:"f3a-legend","aria-label":"Legenda de relações"});
  [["membership","Pertencimento: parent_key explícito (sem causalidade)"],
    ["lineage","Linhagem declarada: seta somente FROM_TO"],
    ["binding","Input/output ou vínculo declarado: direção literal"],
    ["mention","Menção neutra / direção desconhecida: sem seta"]].forEach(([cls,label])=>
      legend.append(element("li",{class:"f3a-key-"+cls},label)));
  const detail=element("pre",{class:"f3a-detail","aria-label":"Detalhe do nó selecionado",tabindex:"0"});
  const relations=element("section",{class:"f3a-relations","aria-label":"Ocorrências de relações"});
  const relationHeading=element("h3",{},"Relações — ocorrências preservadas");
  const relationControls=element("div",{class:"f3a-toolbar"});
  relationControls.append(makeButton("relation-previous","Relação anterior"),makeButton("relation-next","Próxima relação"));
  const relationDetail=element("pre",{class:"f3a-detail","aria-label":"Detalhe da relação",tabindex:"0"});
  relations.append(relationHeading,relationControls,relationDetail);
  root.append(banner,toolbar,status,error,viewport,mini,legend,detail,relations);
  host.replaceChildren(root);
  let model=null,session=0,sessionId=null,selection=null,focusId=null,expanded=new Set(),
    positions=new Map(),visible=[],zoom=1,pan={x:20,y:20},width=1000,height=440,
    bounds={width:1000,height:440},timer=null,disposed=false,errorMessage=null,relationIndex=0;
  const listen=(e,event,fn,opts={})=>e.addEventListener(event,fn,{...opts,signal});
  const emit=()=>host.dispatchEvent(new CustomEvent("graph-selection",{detail:selection?{...selection}:null,bubbles:true}));
  function clear(message=null) {
    clearTimeout(timer);timer=null; model=null; selection=null;sessionId=null;focusId=null;
    expanded.clear();positions.clear();visible=[];world.replaceChildren();mini.replaceChildren();
    detail.textContent="Nenhum nó selecionado.";relationDetail.textContent="Nenhuma relação carregada.";
    errorMessage=message;error.hidden=!message;error.textContent=message||"";
    banner.textContent="LEGACY_DERIVED · sem snapshot validado · autenticidade NOT_VERIFIED · ciência NOT_EVALUATED";
    status.textContent=message?"Snapshot indisponível; nenhuma apresentação parcial.":"Nenhum snapshot.";
    emit();
  }
  function live() {
    if(disposed)return false;
    if(model && now()>=model.expires)clear("EXPIRED — snapshot expirado; seleção e links invalidados.");
    return !!model;
  }
  function setData(input) {
    if(disposed)return false;
    clear();session++;
    try {
      const started=performance.now();
      const checkpoint=()=>{if(performance.now()-started>LIMITS.operationMs)fail("Operation time quota exceeded");};
      const d=copyJSON(input,checkpoint);
      validateSchema(d,SCHEMA);checkpoint();
      if(d.nodes.length>LIMITS.renderNodes || d.relations.length>LIMITS.renderRelations)
        fail("Render limit exceeded: "+LIMITS.renderNodes+" nodes / "+LIMITS.renderRelations+" relations; no truncation");
      model=semanticModel(d,now(),checkpoint);
      sessionId="f3a-"+instance+"-"+session;
      expanded=new Set(model.nodes.keys());focusId=d.nodes[0]?.identity.navigation_id||null;
      relationIndex=0;zoom=1;pan={x:20,y:20};
      banner.textContent="LEGACY_DERIVED · "+d.source.source_id+" / "+d.snapshot.snapshot_id+
        " · fonte "+d.source.availability+" · descriptor_schema PASS · descriptor_semantics PASS · OBSERVED_SNAPSHOT_ONLY · expira "+
        d.snapshot.expires_at+" · autenticidade NOT_VERIFIED · ciência NOT_EVALUATED";
      error.hidden=true;errorMessage=null;render(null,checkpoint);
      timer=setTimeout(()=>{live();},Math.max(1,model.expires-now()+1));
      return true;
    } catch(e) {clear("F3A — "+e.message);return false;}
  }
  function currentContext(id) {
    const n=model.nodes.get(id);
    return {source_id:model.d.source.source_id,snapshot_id:model.d.snapshot.snapshot_id,
      occurrence:n.identity.occurrence,nav_id:id,session_id:sessionId};
  }
  function showDetail() {
    if(!selection || !model){detail.textContent="Nenhum nó selecionado.";return;}
    const n=model.nodes.get(selection.nav_id);
    detail.textContent=JSON.stringify({context:selection,...n,
      collision_occurrences:n.identity.native_id===null?0:model.natives.get(n.identity.native_id).length,
      presentation_warning:model.cycles.has(selection.nav_id)?"PARENT_CYCLE — somente traversal UI interrompido":null},null,2);
  }
  function select(context) {
    if(!live())return false;
    if(context===null){selection=null;showDetail();paintSelection();emit();return true;}
    if(!isObject(context) || !model.nodes.has(context.nav_id))return false;
    const expected=currentContext(context.nav_id);
    if(Object.keys(expected).some(k=>context[k]!==expected[k]))return false;
    selection=expected;showDetail();paintSelection();emit();return true;
  }
  function paintSelection() {
    for(const node of world.querySelectorAll("[data-node-id]"))
      node.setAttribute("aria-selected",String(selection?.nav_id===node.getAttribute("data-node-id")));
  }
  function updateCamera() {
    world.setAttribute("transform","translate("+pan.x+" "+pan.y+") scale("+zoom+")");
    zoomLabel.textContent=(zoom<.01?(zoom*100).toFixed(3):String(Math.round(zoom*100)))+"%";
    const rect=mini.querySelector("[data-mini-view]");
    if(rect){rect.setAttribute("x",String(-pan.x/zoom));rect.setAttribute("y",String(-pan.y/zoom));
      rect.setAttribute("width",String(width/zoom));rect.setAttribute("height",String(height/zoom));}
  }
  function fitScale() {
    const margin=Math.min(16,width/4,height/4);
    return Math.max(.000001,Math.min(2,(width-margin*2)/bounds.width,(height-margin*2)/bounds.height));
  }
  function zoomAt(next,cx=width/2,cy=height/2) {
    if(!live())return;
    const target=Math.max(Math.min(.1,fitScale()),Math.min(4,next));
    const factor=target/zoom;
    pan={x:cx-(cx-pan.x)*factor,y:cy-(cy-pan.y)*factor};
    zoom=target;updateCamera();
  }
  function reveal(id) {
    const p=positions.get(id);if(!p)return;
    const needsLegibility=zoom<.5;
    if(needsLegibility)zoom=1;
    if(needsLegibility || p.x*zoom+pan.x<0 || (p.x+230)*zoom+pan.x>width ||
      p.y*zoom+pan.y<0 || (p.y+62)*zoom+pan.y>height) {
      pan={x:width/2-(p.x+115)*zoom,y:height/2-(p.y+31)*zoom};updateCamera();
    }
  }
  function focusNode(id,shouldReveal=true) {
    if(!live() || !positions.has(id))return;
    focusId=id;
    for(const node of world.querySelectorAll("[data-node-id]")){
      const active=node.getAttribute("data-node-id")===id;node.setAttribute("tabindex",active?"0":"-1");
      if(active)node.focus({preventScroll:true});
    }
    if(shouldReveal)reveal(id);
  }
  function toggle(id) {
    if(!live() || !model.children.get(id)?.length)return;
    if(expanded.has(id))expanded.delete(id);else expanded.add(id);
    try {render(id);} catch(e) {clear("F3A — "+e.message);}
  }
  function relationText() {
    if(!model)return;
    const r=model.d.relations[relationIndex];
    relationDetail.textContent=r?("Ocorrência "+(relationIndex+1)+" / "+model.d.relations.length+"\n"+
      JSON.stringify(r,null,2)):"Nenhuma relação declarada.";
  }
  function render(fallback=null,check=null) {
    if(!model)return;
    const started=performance.now();
    const checkpoint=check || (()=>{if(performance.now()-started>LIMITS.operationMs)fail("Render time quota exceeded");});
    const hadFocus=world.contains(document.activeElement);
    positions=new Map();visible=[];let row=0,maxDepth=0;
    const roots=[...model.nodes.keys()].filter(id=>!model.parents.has(id));
    // Iterative DFS, bounded by validated input; cycles are retained as annotated roots.
    const stack=roots.map(id=>[id,0]).reverse();
    while(stack.length) {
      checkpoint();
      const [id,depth]=stack.pop();visible.push(id);
      positions.set(id,{x:depth*270,y:row++*86,depth});maxDepth=Math.max(maxDepth,depth);
      if(expanded.has(id))for(const child of [...model.children.get(id)].reverse())stack.push([child,depth+1]);
    }
    bounds={width:Math.max(260,maxDepth*270+260),height:Math.max(100,row*86)};
    if(!positions.has(focusId))focusId=fallback && positions.has(fallback)?fallback:visible[0]||null;
    world.replaceChildren();
    const svgLine=(a,b,cls,attrs={})=>{
      const p=positions.get(a),q=positions.get(b);if(!p || !q)return;
      world.append(element("line",{x1:p.x+230,y1:p.y+31,x2:q.x,y2:q.y+31,
        class:"f3a-edge f3a-"+cls,...attrs},null,true));
    };
    for(const [id,parent] of model.parents)svgLine(parent,id,"membership",{"data-edge":"parent","data-parent-edge":"true","data-parent-id":parent});
    for(const r of model.d.relations) {
      if(r.from.resolution!=="RESOLVED" || r.to.resolution!=="RESOLVED")continue;
      const cls=r.semantics==="DECLARED_LINEAGE"?"lineage":r.semantics==="DECLARED_BINDING"?"binding":
        r.semantics==="ORGANIZATIONAL_MEMBERSHIP"?"membership":"mention";
      const directed=r.direction==="FROM_TO" && ["lineage","binding"].includes(cls);
      svgLine(r.from.target_navigation_id,r.to.target_navigation_id,cls,{
        "data-relation-id":r.identity.navigation_id,"data-semantics":r.semantics,
        "data-direction":r.direction,...(directed?{"marker-end":"url(#f3a-"+instance+"-"+cls+")"}:{})});
    }
    for(const id of visible) {
      checkpoint();
      const n=model.nodes.get(id),p=positions.get(id),hasChildren=model.children.get(id).length>0;
      const collision=n.identity.native_id!==null && model.natives.get(n.identity.native_id).length>1;
      const warning=[n.tree_state,n.binding_gap?"binding_gap":"",collision?"COLLISION":"",
        model.cycles.has(id)?"PARENT_CYCLE":""].filter(Boolean).join(" · ");
      const label=n.label_literal;
      const g=element("g",{"data-node-id":id,"data-nav-id":id,class:"f3a-node",
        transform:"translate("+p.x+" "+p.y+")",role:"treeitem",tabindex:id===focusId?"0":"-1",
        "aria-level":p.depth+1,"aria-selected":selection?.nav_id===id,
        "aria-label":label+" · "+(n.original_type||n.kind)+" · "+warning,
        ...(hasChildren?{"aria-expanded":expanded.has(id)}:{})},null,true);
      g.append(element("title",{},label+"\n"+(n.original_type||n.kind)+"\n"+warning,true));
      g.append(element("rect",{width:"230",height:"62",rx:"7"},null,true));
      const shortLabel=label;
      g.append(element("text",{x:hasChildren?"28":"10",y:"24",class:"f3a-label"},shortLabel,true));
      g.append(element("text",{x:"10",y:"46",class:"f3a-node-meta"},
        (n.original_type||n.kind)+" · "+warning,true));
      if(hasChildren) {
        const btn=element("g",{"data-toggle-id":id,role:"button",tabindex:"-1",
          "aria-label":(expanded.has(id)?"Recolher ":"Expandir ")+label,class:"f3a-toggle"},null,true);
        btn.append(element("rect",{x:"0",y:"0",width:"28",height:"32",class:"f3a-toggle-hit"},null,true));
        btn.append(element("text",{x:"7",y:"24"},expanded.has(id)?"−":"+",true));
        g.append(btn);
      }
      world.append(g);
      fitSVGText(g.querySelector(".f3a-label"),label,hasChildren?190:210);
      fitSVGText(g.querySelector(".f3a-node-meta"),(n.original_type||n.kind)+" · "+warning,210);
    }
    mini.replaceChildren();mini.setAttribute("viewBox","-20 -20 "+(bounds.width+40)+" "+(bounds.height+40));
    for(const id of visible){const p=positions.get(id);mini.append(element("rect",{x:p.x,y:p.y,width:"230",height:"62",
      class:"f3a-mini-node"},null,true));}
    mini.append(element("rect",{"data-mini-view":"true",class:"f3a-mini-view",x:0,y:0,width:100,height:100},null,true));
    status.textContent="Nós carregados "+model.nodes.size+"; visíveis "+visible.length+
      "; relações "+model.d.relations.length+"; endpoints "+JSON.stringify(model.endpointCounts)+
      "; ciclos "+model.cycles.size+"; gaps declarados "+JSON.stringify(model.d.gaps)+
      ". Sem pai resolvido e RUN_EXTERNAL_ISOLATED permanecem raízes isoladas; agrupamento somente UI. "+
      "UNKNOWN_UPSTREAM / GLOBAL_UNPROVEN; sem denominador global.";
    showDetail();relationText();updateCamera();checkpoint();
    if(hadFocus && focusId)focusNode(focusId,false);
  }
  function action(name) {
    if(!live())return;
    if(name==="zoom-in")zoomAt(zoom*1.25);
    else if(name==="zoom-out")zoomAt(zoom/1.25);
    else if(name==="reset"){zoom=1;pan={x:20,y:20};updateCamera();}
    else if(name==="fit"){
      zoom=fitScale();
      pan={x:(width-bounds.width*zoom)/2,y:(height-bounds.height*zoom)/2};updateCamera();
    } else if(name.startsWith("pan-")){
      const delta={"pan-left":[64,0],"pan-right":[-64,0],"pan-up":[0,64],"pan-down":[0,-64]}[name];
      pan={x:pan.x+delta[0],y:pan.y+delta[1]};updateCamera();
    } else if(name.startsWith("relation-") && model.d.relations.length){
      relationIndex=(relationIndex+(name==="relation-next"?1:-1)+model.d.relations.length)%model.d.relations.length;relationText();
    }
  }
  listen(root,"click",event=>{
    const button=event.target.closest("[data-action]");if(button && root.contains(button))action(button.dataset.action);
  });
  listen(svg,"click",event=>{
    if(!live())return;
    const toggleNode=event.target.closest("[data-toggle-id]");
    if(toggleNode){toggle(toggleNode.getAttribute("data-toggle-id"));return;}
    const node=event.target.closest("[data-node-id]");
    if(node){const id=node.getAttribute("data-node-id");focusNode(id);select(currentContext(id));}
  });
  listen(svg,"focusin",event=>{const node=event.target.closest("[data-node-id]");if(node)focusId=node.getAttribute("data-node-id");});
  listen(svg,"keydown",event=>{
    if(!live())return;
    const id=event.target.closest("[data-node-id]")?.getAttribute("data-node-id")||focusId;
    if(!id)return;
    const index=visible.indexOf(id),children=model.children.get(id);
    let target=null;
    if(event.key==="ArrowDown")target=visible[Math.min(index+1,visible.length-1)];
    else if(event.key==="ArrowUp")target=visible[Math.max(0,index-1)];
    else if(event.key==="Home")target=visible[0];
    else if(event.key==="End")target=visible[visible.length-1];
    else if(event.key==="ArrowRight"){
      if(children.length && !expanded.has(id)){toggle(id);target=id;}
      else if(children.length)target=children[0];
    } else if(event.key==="ArrowLeft"){
      if(children.length && expanded.has(id)){toggle(id);target=id;}
      else target=model.parents.get(id);
    } else if(event.key==="Enter")select(currentContext(id));
    else if(event.key==="Escape")select(null);
    else return;
    event.preventDefault();if(target)focusNode(target);
  });
  listen(svg,"wheel",event=>{
    if(!live())return;event.preventDefault();
    const rect=svg.getBoundingClientRect();
    zoomAt(zoom*Math.exp(-event.deltaY*.002),event.clientX-rect.left,event.clientY-rect.top);
  },{passive:false});
  const pointers=new Map();let gesture=null;
  listen(svg,"pointerdown",event=>{
    if(!live() || event.button!==0 || event.target.closest("[data-node-id]"))return;
    svg.setPointerCapture(event.pointerId);pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
    gesture={points:[...pointers.values()],pan:{...pan},zoom};
  });
  listen(svg,"pointermove",event=>{
    if(!pointers.has(event.pointerId) || !live())return;
    pointers.set(event.pointerId,{x:event.clientX,y:event.clientY});
    const points=[...pointers.values()];
    if(points.length===1 && gesture.points.length===1){
      pan={x:gesture.pan.x+points[0].x-gesture.points[0].x,y:gesture.pan.y+points[0].y-gesture.points[0].y};updateCamera();
    } else if(points.length===2 && gesture.points.length===2){
      const distance=p=>Math.hypot(p[0].x-p[1].x,p[0].y-p[1].y);
      const old=distance(gesture.points);
      if(old>0){
        const target=Math.max(Math.min(.1,fitScale()),Math.min(4,gesture.zoom*distance(points)/old));
        const rect=svg.getBoundingClientRect();
        const cx=(points[0].x+points[1].x)/2-rect.left,cy=(points[0].y+points[1].y)/2-rect.top;
        const ox=(gesture.points[0].x+gesture.points[1].x)/2-rect.left,oy=(gesture.points[0].y+gesture.points[1].y)/2-rect.top;
        pan={x:cx-(ox-gesture.pan.x)*target/gesture.zoom,y:cy-(oy-gesture.pan.y)*target/gesture.zoom};zoom=target;updateCamera();
      }
    }
  });
  const pointerEnd=event=>{pointers.delete(event.pointerId);gesture=pointers.size?
    {points:[...pointers.values()],pan:{...pan},zoom}:null;};
  listen(svg,"pointerup",pointerEnd);listen(svg,"pointercancel",pointerEnd);listen(svg,"lostpointercapture",pointerEnd);
  listen(mini,"click",event=>{
    if(!live())return;
    const matrix=mini.getScreenCTM();if(!matrix)return;
    const point=new DOMPoint(event.clientX,event.clientY).matrixTransform(matrix.inverse());
    pan={x:width/2-point.x*zoom,y:height/2-point.y*zoom};updateCamera();
  });
  listen(mini,"keydown",event=>{
    const directions={ArrowLeft:"pan-left",ArrowRight:"pan-right",ArrowUp:"pan-up",ArrowDown:"pan-down"};
    if(directions[event.key]){event.preventDefault();action(directions[event.key]);}
    else if(event.key==="Enter" || event.key==="Home"){event.preventDefault();action("fit");}
    else if(event.key==="Escape"){event.preventDefault();select(null);}
  });
  const resize=new ResizeObserver(()=>{
    const rect=viewport.getBoundingClientRect();
    width=Math.max(1,rect.width);height=Math.max(1,rect.height);
    svg.setAttribute("viewBox","0 0 "+width+" "+height);updateCamera();
  });resize.observe(viewport);
  const api={
    setData,select,
    getState(){
      live();
      return {session_id:sessionId,selection:selection?{...selection}:null,zoom,pan:{...pan},
        expanded:[...expanded],visible_ids:[...visible],focus_id:focusId,node_count:model?.nodes.size||0,
        relation_count:model?.d.relations.length||0,endpoint_counts:model?{...model.endpointCounts}:null,
        cycle_ids:model?[...model.cycles]:[],error:errorMessage,disposed};
    },
    dispose(){
      if(disposed)return;clear();disposed=true;abort.abort();resize.disconnect();root.remove();
    }
  };
  setData(descriptor);return Object.freeze(api);
}
