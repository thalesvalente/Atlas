(function () {
  "use strict";
  const SCHEMA = {"$schema":"https://json-schema.org/draft/2020-12/schema","$id":"urn:atlas:proposal:legacy-presentation:0.2.0","type":"object","additionalProperties":false,"required":["format","version","authority","synthetic","source","snapshot","validation","policy","nodes","tables","relations","assets","unmapped_fields","coverage","gaps"],"properties":{"format":{"const":"atlas-legacy-presentation"},"version":{"const":"0.2.0"},"authority":{"const":"LEGACY_DERIVED"},"synthetic":{"type":"boolean"},"source":{"$ref":"#/$defs/source"},"snapshot":{"$ref":"#/$defs/snapshot"},"validation":{"$ref":"#/$defs/validation"},"policy":{"$ref":"#/$defs/policy"},"nodes":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/node"}},"tables":{"type":"array","maxItems":128,"items":{"$ref":"#/$defs/table"}},"relations":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/relation"}},"assets":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/asset"}},"unmapped_fields":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/unmapped"}},"coverage":{"$ref":"#/$defs/coverage"},"gaps":{"type":"array","maxItems":10000,"items":{"$ref":"#/$defs/gap"}}},"allOf":[{"if":{"properties":{"synthetic":{"const":false}}},"then":{"properties":{"snapshot":{"properties":{"binding_basis":{"const":"OBSERVED_BYTES_AND_POLICY"},"digest_status":{"const":"OBSERVED_BYTES"},"bytes_sha256":{"type":"string","pattern":"^[0-9a-f]{64}$"}}}}}}],"$defs":{"text":{"type":"string","maxLength":65536},"nullable_text":{"type":["string","null"],"maxLength":65536},"navigation_id":{"type":"string","pattern":"^nav:[A-Za-z0-9._:-]+$","maxLength":512},"source":{"type":"object","additionalProperties":false,"required":["source_id","scope","original_format","original_profile_declared","availability","access_policy_id","declared_scientific_review"],"properties":{"source_id":{"type":"string","minLength":1,"maxLength":512},"scope":{"$ref":"#/$defs/text"},"original_format":{"type":"string","minLength":1,"maxLength":256},"original_profile_declared":{"$ref":"#/$defs/nullable_text"},"availability":{"enum":["OBSERVED_AVAILABLE","UNAVAILABLE","UNKNOWN","CHANGED","EXPIRED"]},"access_policy_id":{"type":"string","minLength":1,"maxLength":512},"declared_scientific_review":{"$ref":"#/$defs/nullable_text"}}},"snapshot":{"type":"object","additionalProperties":false,"required":["snapshot_id","binding_basis","bytes_sha256","digest_status","observed_at","scientific_at","generated_at","expires_at","freshness"],"properties":{"snapshot_id":{"type":"string","minLength":1,"maxLength":512},"binding_basis":{"enum":["OBSERVED_BYTES_AND_POLICY","SYNTHETIC_FIXTURE"]},"bytes_sha256":{"type":["string","null"],"pattern":"^[0-9a-f]{64}$"},"digest_status":{"enum":["OBSERVED_BYTES","NOT_COMPUTED"]},"observed_at":{"type":"string","format":"date-time"},"scientific_at":{"type":["string","null"],"format":"date-time"},"generated_at":{"type":"string","format":"date-time"},"expires_at":{"type":"string","format":"date-time"},"freshness":{"const":"OBSERVED_SNAPSHOT_ONLY"}}},"validation":{"type":"object","additionalProperties":false,"required":["descriptor_schema","descriptor_semantics","literal_comparison","source_profile_assessment","authenticity","scientific_approval"],"properties":{"descriptor_schema":{"enum":["NOT_RUN","PASS","FAIL"]},"descriptor_semantics":{"enum":["NOT_RUN","PASS","FAIL"]},"literal_comparison":{"enum":["NOT_PERFORMED","SOURCE_FIELD_COMPARED","SOURCE_ROW_COMPARED"]},"source_profile_assessment":{"const":"NOT_ASSERTED"},"authenticity":{"const":"NOT_VERIFIED"},"scientific_approval":{"const":"NOT_EVALUATED"}}},"policy":{"type":"object","additionalProperties":false,"required":["source_access","max_descriptor_bytes","ttl_max_seconds","browser_persistence","automatic_uri_access"],"properties":{"source_access":{"const":"EXTERNAL_EXACT_ALLOWLIST_ONLY"},"max_descriptor_bytes":{"const":33554432},"ttl_max_seconds":{"const":3600},"browser_persistence":{"const":"MEMORY_ONLY"},"automatic_uri_access":{"const":false}}},"identity":{"type":"object","additionalProperties":false,"required":["native_id","navigation_id","navigation_id_kind","occurrence","locator"],"properties":{"native_id":{"type":["string","null"],"minLength":1,"maxLength":4096},"navigation_id":{"$ref":"#/$defs/navigation_id"},"navigation_id_kind":{"const":"DERIVED_FOR_PRESENTATION"},"occurrence":{"type":"integer","minimum":0},"locator":{"type":"string","maxLength":8192}}},"reference":{"type":"object","additionalProperties":false,"required":["source_id","snapshot_id","declared_id","target_navigation_id","resolution","evidence_locator"],"properties":{"source_id":{"type":["string","null"],"maxLength":512},"snapshot_id":{"type":["string","null"],"maxLength":512},"declared_id":{"type":["string","null"],"maxLength":4096},"target_navigation_id":{"anyOf":[{"$ref":"#/$defs/navigation_id"},{"type":"null"}]},"resolution":{"enum":["RESOLVED","NULL_ENDPOINT","UNRESOLVED","COLLISION","EXTERNAL_DECLARED"]},"evidence_locator":{"type":["string","null"],"maxLength":8192}}},"cell":{"type":"object","additionalProperties":false,"required":["type","literal","lexeme","unit","precision","absence"],"properties":{"type":{"enum":["string","integer","decimal","boolean","null","missing","array","object"]},"literal":{"$ref":"#/$defs/nullable_text"},"lexeme":{"type":["string","null"],"maxLength":131072},"unit":{"type":["string","null"],"maxLength":256},"precision":{"type":["string","null"],"maxLength":128},"absence":{"enum":[null,"NULL","MISSING"]}},"allOf":[{"if":{"properties":{"type":{"enum":["string","integer","decimal","boolean","array","object"]}}},"then":{"properties":{"literal":{"type":"string"},"lexeme":{"type":"string"},"absence":{"const":null}}}},{"if":{"properties":{"type":{"const":"integer"}}},"then":{"properties":{"literal":{"pattern":"^-?(0|[1-9][0-9]*)$"}}}},{"if":{"properties":{"type":{"const":"decimal"}}},"then":{"properties":{"literal":{"pattern":"^-?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?$"}}}},{"if":{"properties":{"type":{"const":"boolean"}}},"then":{"properties":{"literal":{"enum":["true","false"]}}}},{"if":{"properties":{"type":{"const":"null"}}},"then":{"properties":{"literal":{"const":null},"lexeme":{"const":"null"},"absence":{"const":"NULL"}}}},{"if":{"properties":{"type":{"const":"missing"}}},"then":{"properties":{"literal":{"const":null},"lexeme":{"const":null},"absence":{"const":"MISSING"}}}}]},"node":{"type":"object","additionalProperties":false,"required":["identity","kind","original_type","entity_status","label_literal","family_literal","parent_key_literal","parent","tree_state","external_reference","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind":{"enum":["Project","Family","Experiment","Run","Other","Unknown"]},"original_type":{"$ref":"#/$defs/nullable_text"},"entity_status":{"enum":["SOURCE_ENTITY","DECLARED_EXTERNAL_REFERENCE"]},"label_literal":{"$ref":"#/$defs/text"},"family_literal":{"$ref":"#/$defs/nullable_text"},"parent_key_literal":{"$ref":"#/$defs/nullable_text"},"parent":{"$ref":"#/$defs/reference"},"tree_state":{"enum":["ROOT_DECLARED","PARENT_RESOLVED","ORPHAN","PARENT_UNKNOWN","RUN_EXTERNAL_ISOLATED"]},"external_reference":{"anyOf":[{"$ref":"#/$defs/reference"},{"type":"null"}]},"binding_gap":{"type":"boolean"}},"allOf":[{"if":{"properties":{"entity_status":{"const":"DECLARED_EXTERNAL_REFERENCE"}}},"then":{"properties":{"identity":{"properties":{"native_id":{"const":null}}},"tree_state":{"const":"RUN_EXTERNAL_ISOLATED"},"binding_gap":{"const":true},"external_reference":{"$ref":"#/$defs/reference"}}}}]},"column":{"type":"object","additionalProperties":false,"required":["ordinal","native_key","header_literal"],"properties":{"ordinal":{"type":"integer","minimum":0,"maximum":255},"native_key":{"$ref":"#/$defs/nullable_text"},"header_literal":{"$ref":"#/$defs/text"}}},"column_index":{"type":["integer","null"],"minimum":0,"maximum":255},"requirement_fields":{"type":"object","additionalProperties":false,"required":["id","module","title","description","acceptance_criteria","category"],"properties":{"id":{"$ref":"#/$defs/column_index"},"module":{"$ref":"#/$defs/column_index"},"title":{"$ref":"#/$defs/column_index"},"description":{"$ref":"#/$defs/column_index"},"acceptance_criteria":{"$ref":"#/$defs/column_index"},"category":{"$ref":"#/$defs/column_index"}}},"requirement":{"type":"object","additionalProperties":false,"required":["kind","native_id","admission","admission_evidence_locator","fields","category_status"],"properties":{"kind":{"enum":["RF","RNF","RES"]},"native_id":{"type":["string","null"],"minLength":1,"maxLength":4096},"admission":{"enum":["ADMITTED_NATIVE_RF","UNADMITTED_NATIVE_RF","NOT_EVALUATED","NOT_APPLICABLE"]},"admission_evidence_locator":{"type":["string","null"],"maxLength":8192},"fields":{"$ref":"#/$defs/requirement_fields"},"category_status":{"enum":["MISSING","PRESENT","UNKNOWN"]}},"allOf":[{"if":{"properties":{"admission":{"const":"UNADMITTED_NATIVE_RF"}}},"then":{"properties":{"kind":{"const":"RF"},"native_id":{"const":null}}}},{"if":{"properties":{"admission":{"const":"ADMITTED_NATIVE_RF"}}},"then":{"properties":{"kind":{"const":"RF"},"native_id":{"type":"string","minLength":1},"admission_evidence_locator":{"type":"string","minLength":1}}}}]},"row":{"type":"object","additionalProperties":false,"required":["identity","ordinal","cells","requirement","run_binding","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"ordinal":{"type":"integer","minimum":0},"cells":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/cell"}},"requirement":{"anyOf":[{"$ref":"#/$defs/requirement"},{"type":"null"}]},"run_binding":{"$ref":"#/$defs/reference"},"binding_gap":{"type":"boolean"}}},"table":{"type":"object","additionalProperties":false,"required":["identity","title_literal","domain","domain_origin","record_binding","columns","rows"],"properties":{"identity":{"$ref":"#/$defs/identity"},"title_literal":{"$ref":"#/$defs/text"},"domain":{"enum":["RF","RNF","RES","UNKNOWN","OTHER"]},"domain_origin":{"enum":["DECLARED","UNKNOWN"]},"record_binding":{"$ref":"#/$defs/reference"},"columns":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/column"}},"rows":{"type":"array","maxItems":100000,"items":{"$ref":"#/$defs/row"}}}},"relation":{"type":"object","additionalProperties":false,"required":["identity","kind_literal","semantics","direction","from","to","evidence_locator","issues","repeat_group","repeat_occurrence","binding_gap"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind_literal":{"$ref":"#/$defs/nullable_text"},"semantics":{"enum":["ORGANIZATIONAL_MEMBERSHIP","DECLARED_LINEAGE","DECLARED_BINDING","NEUTRAL_MENTION","UNKNOWN"]},"direction":{"enum":["FROM_TO","UNDIRECTED","UNKNOWN"]},"from":{"$ref":"#/$defs/reference"},"to":{"$ref":"#/$defs/reference"},"evidence_locator":{"type":["string","null"],"maxLength":8192},"issues":{"type":"array","maxItems":32,"items":{"type":"string","maxLength":256}},"repeat_group":{"type":["string","null"],"maxLength":512},"repeat_occurrence":{"type":"integer","minimum":1},"binding_gap":{"type":"boolean"}}},"asset":{"type":"object","additionalProperties":false,"required":["identity","kind","original_type","label_literal","declared_product_role","declared_binding","media_type_literal","uri_literal","availability","opened"],"properties":{"identity":{"$ref":"#/$defs/identity"},"kind":{"enum":["File","Product","ProductGroup","ResourceDocument","DossierAssessment","DossierPackage","Other","Unknown"]},"original_type":{"$ref":"#/$defs/nullable_text"},"label_literal":{"$ref":"#/$defs/text"},"declared_product_role":{"$ref":"#/$defs/nullable_text"},"declared_binding":{"$ref":"#/$defs/reference"},"media_type_literal":{"type":["string","null"],"maxLength":256},"uri_literal":{"$ref":"#/$defs/nullable_text"},"availability":{"enum":["OBSERVED_AVAILABLE","DECLARED_ONLY","UNVERIFIED","MISSING","EXTERNAL_UNRESOLVED","UNKNOWN","INTEGRITY_MISMATCH"]},"opened":{"const":false}}},"unmapped":{"type":"object","additionalProperties":false,"required":["owner_navigation_id","locator","source_key_literal","value"],"properties":{"owner_navigation_id":{"anyOf":[{"$ref":"#/$defs/navigation_id"},{"type":"null"}]},"locator":{"type":"string","maxLength":8192},"source_key_literal":{"$ref":"#/$defs/text"},"value":{"$ref":"#/$defs/cell"}}},"count":{"type":"object","additionalProperties":false,"required":["unit","selected","loaded","visible","unavailable","unknown_reason"],"properties":{"unit":{"type":"string","minLength":1,"maxLength":256},"selected":{"type":["integer","null"],"minimum":0},"loaded":{"type":"integer","minimum":0},"visible":{"type":["integer","null"],"minimum":0},"unavailable":{"type":["integer","null"],"minimum":0},"unknown_reason":{"$ref":"#/$defs/nullable_text"}}},"coverage":{"type":"object","additionalProperties":false,"required":["population","global_archive","global_history","global_total","global_percentage","snapshot_overlap","counts"],"properties":{"population":{"enum":["SELECTED_QUALIFYING_PAYLOAD","SYNTHETIC_FIXTURE"]},"global_archive":{"const":"UNKNOWN_UPSTREAM"},"global_history":{"const":"GLOBAL_UNPROVEN"},"global_total":{"const":null},"global_percentage":{"const":null},"snapshot_overlap":{"enum":["NOT_SUMMED","UNKNOWN"]},"counts":{"type":"array","maxItems":256,"items":{"$ref":"#/$defs/count"}}}},"gap":{"type":"object","additionalProperties":false,"required":["code","scope","count","unit","note"],"properties":{"code":{"type":"string","minLength":1,"maxLength":256},"scope":{"$ref":"#/$defs/text"},"count":{"type":["integer","null"],"minimum":0},"unit":{"type":"string","minLength":1,"maxLength":256},"note":{"$ref":"#/$defs/text"}}}}};
  const TYPES = ["string", "integer", "decimal", "boolean"];
  let instanceCounter = 0;
  const copy = value => JSON.parse(JSON.stringify(value));
  const fail = reason => { throw new Error(reason); };
  const ok = (condition, reason) => { if (!condition) fail(reason); };
  const byteLength = text => new TextEncoder().encode(text).length;
  const equal = (a,b) => JSON.stringify(a) === JSON.stringify(b);
  const own = (value,key) => Object.prototype.hasOwnProperty.call(value,key);

  // Reject accessors, class instances, cycles and depth before serialization.
  // Input is already in memory: this is not a File API/host importer.
  function preflight(value, depth = 0, ancestors = new Set(), budget = {bytes:0}) {
    ok(depth <= 20, "QUOTA_DEPTH: maximum 20");
    if (value === null || ["string","boolean","number"].includes(typeof value)) {
      if (typeof value === "number") ok(Number.isFinite(value), "NON_FINITE_NUMBER");
      if (typeof value === "string") ok(value.length <= 33554432, "QUOTA_DESCRIPTOR_BYTES");
      budget.bytes += byteLength(JSON.stringify(value));
      ok(budget.bytes <= 33554432,"QUOTA_DESCRIPTOR_BYTES");
      return;
    }
    ok(typeof value === "object", "JSON_DATA_ONLY");
    const prototype = Object.getPrototypeOf(value);
    ok(prototype === Object.prototype || prototype === Array.prototype || prototype === null, "JSON_DATA_ONLY");
    ok(!ancestors.has(value), "CYCLIC_DATA");
    ancestors.add(value);
    budget.bytes += 2;
    const keys = Reflect.ownKeys(value);
    if (Array.isArray(value)) ok(keys.length === value.length + 1, "DENSE_JSON_ARRAY_REQUIRED");
    let entryCount = 0;
    for (const key of keys) {
      ok(typeof key === "string", "JSON_DATA_ONLY");
      if (Array.isArray(value) && key === "length") continue;
      const property = Object.getOwnPropertyDescriptor(value,key);
      ok(property && own(property,"value") && property.enumerable, "JSON_DATA_ONLY");
      budget.bytes += (entryCount++ ? 1 : 0) + (Array.isArray(value) ? 0 : byteLength(JSON.stringify(key)) + 1);
      ok(budget.bytes <= 33554432,"QUOTA_DESCRIPTOR_BYTES");
      preflight(property.value, depth + 1, ancestors,budget);
    }
    ancestors.delete(value);
  }
  // Implements only the keywords used by the frozen embedded F2 schema.
  // This does not claim a general JSON Schema engine or scientific validation.
  function schemaCheck(value, rule, path = "$") {
    if (rule.$ref) return schemaCheck(value, SCHEMA.$defs[rule.$ref.split("/").pop()],path);
    if (rule.const !== undefined) ok(equal(value,rule.const), "SCHEMA_CONST " + path);
    if (rule.enum) ok(rule.enum.some(item => equal(value,item)), "SCHEMA_ENUM " + path);
    if (rule.type) {
      const types = Array.isArray(rule.type) ? rule.type : [rule.type];
      ok(types.some(type => type === "null" ? value === null :
        type === "array" ? Array.isArray(value) :
        type === "object" ? value !== null && typeof value === "object" && !Array.isArray(value) :
        type === "integer" ? Number.isSafeInteger(value) : typeof value === type), "SCHEMA_TYPE " + path);
    }
    if (typeof value === "string") {
      const length = Array.from(value).length;
      if (rule.minLength !== undefined) ok(length >= rule.minLength,"SCHEMA_MIN_LENGTH " + path);
      if (rule.maxLength !== undefined) ok(length <= rule.maxLength,"SCHEMA_MAX_LENGTH " + path);
      if (rule.pattern) ok(new RegExp(rule.pattern).test(value),"SCHEMA_PATTERN " + path);
      if (rule.format === "date-time") ok(/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(value) && Number.isFinite(Date.parse(value)),"SCHEMA_DATE " + path);
    }
    if (typeof value === "number") {
      if (rule.minimum !== undefined) ok(value >= rule.minimum,"SCHEMA_MINIMUM " + path);
      if (rule.maximum !== undefined) ok(value <= rule.maximum,"SCHEMA_MAXIMUM " + path);
    }
    if (Array.isArray(value)) {
      if (rule.maxItems !== undefined) ok(value.length <= rule.maxItems,"SCHEMA_MAX_ITEMS " + path);
      if (rule.items) value.forEach((item,index) => schemaCheck(item,rule.items,path + "/" + index));
    } else if (value !== null && typeof value === "object") {
      if (rule.required) for (const key of rule.required) ok(own(value,key),"SCHEMA_REQUIRED " + path + "/" + key);
      if (rule.additionalProperties === false) for (const key of Object.keys(value)) ok(own(rule.properties || {},key),"SCHEMA_EXTRA_PROPERTY " + path + "/" + key);
      if (rule.properties) for (const key of Object.keys(rule.properties)) if (own(value,key)) schemaCheck(value[key],rule.properties[key],path + "/" + key);
    }
    if (rule.anyOf) {
      let passed = false;
      for (const candidate of rule.anyOf) {
        try { schemaCheck(value,candidate,path); passed = true; break; } catch (_) { /* try next schema */ }
      }
      ok(passed,"SCHEMA_ANYOF " + path);
    }
    if (rule.allOf) for (const candidate of rule.allOf) schemaCheck(value,candidate,path);
    if (rule.if) {
      let matches = true;
      try { schemaCheck(value,rule.if,path); } catch (_) { matches = false; }
      if (matches && rule.then) schemaCheck(value,rule.then,path);
    }
  }
  // Compare inert JSON tokens without converting any numeric token to Number.
  // Whitespace and equivalent string escapes may differ; numeric spellings and
  // array/object member order must agree. Both original texts remain untouched.
  function jsonTokenIdentity(text) {
    return text.replace(/"(?:\\[\s\S]|[^"\\])*"|[ \t\r\n]+/g, token =>
      token[0] === '"' ? JSON.stringify(JSON.parse(token)) : "");
  }
  function checkJSONDepth(value, depth = 0) {
    ok(depth <= 20,"QUOTA_DEPTH: maximum 20");
    if (value !== null && typeof value === "object")
      for (const child of Object.values(value)) checkJSONDepth(child,depth + 1);
  }
  function checkCell(cell) {
    ok(byteLength(cell.literal || "") <= 65536 && byteLength(cell.lexeme || "") <= 131072,"QUOTA_CELL_BYTES");
    if (cell.type === "string") {
      let parsed; try { parsed = JSON.parse(cell.lexeme); } catch (_) { fail("CELL_STRING_LEXEME"); }
      ok(parsed === cell.literal,"CELL_STRING_LEXEME");
    } else if (["integer","decimal","boolean"].includes(cell.type)) {
      ok(cell.literal === cell.lexeme,"CELL_TYPED_LEXEME");
    } else if (cell.type === "array" || cell.type === "object") {
      for (const text of [cell.literal,cell.lexeme]) {
        let parsed; try { parsed = JSON.parse(text); } catch (_) { fail("CELL_JSON_LITERAL"); }
        ok(cell.type === "array" ? Array.isArray(parsed) : parsed !== null && typeof parsed === "object" && !Array.isArray(parsed),"CELL_JSON_TYPE");
        checkJSONDepth(parsed);
      }
      ok(jsonTokenIdentity(cell.literal) === jsonTokenIdentity(cell.lexeme),"CELL_JSON_LEXEME");
    }
  }
  function validateDescriptor(input, now) {
    preflight(input);
    const serialized = JSON.stringify(input);
    ok(byteLength(serialized) <= 33554432,"QUOTA_DESCRIPTOR_BYTES");
    const data = JSON.parse(serialized);
    schemaCheck(data,SCHEMA);
    ok(data.validation.descriptor_schema === "PASS" && data.validation.descriptor_semantics === "PASS","DESCRIPTOR_VALIDATION_NOT_PASS");
    ok(data.source.availability === "OBSERVED_AVAILABLE","SOURCE_NOT_AVAILABLE");
    const observed = Date.parse(data.snapshot.observed_at), generated = Date.parse(data.snapshot.generated_at), expires = Date.parse(data.snapshot.expires_at);
    ok(observed <= generated && generated < expires && expires - generated <= 3600000,"SNAPSHOT_TIME_ORDER_OR_TTL");
    ok(generated <= now && now < expires,"SNAPSHOT_NOT_CURRENT");
    const identities = new Map(), nativeCounts = new Map(), references = [];
    const collect = (entity, original = true) => {
      const id = entity.identity;
      ok(!identities.has(id.navigation_id),"DUPLICATE_NAVIGATION_ID");
      identities.set(id.navigation_id,{identity:id,original});
      if (original && id.native_id !== null) nativeCounts.set(id.native_id,(nativeCounts.get(id.native_id) || 0) + 1);
    };
    for (const node of data.nodes) {
      const original = node.entity_status === "SOURCE_ENTITY";
      collect(node,original);
      if (!original) ok(node.identity.native_id === null && node.binding_gap && node.tree_state === "RUN_EXTERNAL_ISOLATED","EXTERNAL_STUB_IDENTITY");
      references.push(node.parent);
      if (node.external_reference) references.push(node.external_reference);
    }
    let rowCount = 0;
    for (const table of data.tables) {
      collect(table);
      references.push(table.record_binding);
      ok(table.domain_origin !== "UNKNOWN" || table.domain === "UNKNOWN","DOMAIN_NOT_DECLARED");
      table.columns.forEach((column,index) => ok(column.ordinal === index,"COLUMN_ORDINAL"));
      for (const [index,row] of table.rows.entries()) {
        collect(row);
        rowCount++;
        ok(rowCount <= 100000,"QUOTA_AGGREGATE_ROWS");
        ok(row.ordinal === index && row.cells.length === table.columns.length,"ROW_SHAPE_OR_ORDINAL");
        row.cells.forEach(checkCell);
        references.push(row.run_binding);
        const requirement = row.requirement;
        if (requirement !== null) {
          for (const column of Object.values(requirement.fields)) ok(column === null || column < table.columns.length,"REQUIREMENT_FIELD_COLUMN");
          if (requirement.admission === "UNADMITTED_NATIVE_RF") ok(requirement.native_id === null && row.identity.native_id === null,"UNADMITTED_NATIVE_ID");
          if (requirement.admission === "ADMITTED_NATIVE_RF" && requirement.fields.id !== null) {
            const cell = row.cells[requirement.fields.id];
            ok(cell.type === "string" && cell.literal === requirement.native_id,"ADMITTED_ID_CELL");
          }
          if (requirement.category_status === "MISSING" && requirement.fields.category !== null) ok(["missing","null"].includes(row.cells[requirement.fields.category].type),"MISSING_CATEGORY_CELL");
        }
      }
    }
    for (const relation of data.relations) { collect(relation); references.push(relation.from,relation.to); }
    for (const asset of data.assets) {
      collect(asset);
      references.push(asset.declared_binding);
      if (asset.original_type === "File") ok(asset.kind === "File","FILE_RECLASSIFIED");
    }
    for (const item of identities.values()) ok(item.identity.native_id === null || !identities.has(item.identity.native_id),"NAVIGATION_ID_PROMOTED");
    for (const table of data.tables) for (const row of table.rows) if (row.requirement && row.requirement.native_id !== null) ok(!identities.has(row.requirement.native_id),"NAVIGATION_ID_PROMOTED");
    for (const field of data.unmapped_fields) { ok(field.owner_navigation_id === null || identities.has(field.owner_navigation_id),"UNMAPPED_OWNER"); checkCell(field.value); }
    for (const reference of references) {
      if (reference.resolution === "NULL_ENDPOINT") ok(reference.declared_id === null && reference.target_navigation_id === null,"NULL_ENDPOINT_TARGET");
      if (["UNRESOLVED","COLLISION"].includes(reference.resolution)) ok(reference.target_navigation_id === null,"UNRESOLVED_TARGET");
      if (reference.resolution === "RESOLVED") {
        const target = identities.get(reference.target_navigation_id);
        ok(reference.source_id === data.source.source_id && reference.snapshot_id === data.snapshot.snapshot_id &&
          target && target.original && target.identity.native_id !== null &&
          target.identity.native_id === reference.declared_id && nativeCounts.get(reference.declared_id) === 1,"RESOLVED_REFERENCE_NOT_UNIQUE");
      }
      if (reference.resolution === "EXTERNAL_DECLARED" && reference.target_navigation_id !== null) {
        const target = identities.get(reference.target_navigation_id);
        ok(target && !target.original,"EXTERNAL_REFERENCE_NOT_STUB");
      }
    }
    const counts = {
      presentation_node_occurrences:data.nodes.length, source_nodes:data.nodes.filter(n => n.entity_status === "SOURCE_ENTITY").length,
      external_reference_stubs:data.nodes.filter(n => n.entity_status === "DECLARED_EXTERNAL_REFERENCE").length,
      tables:data.tables.length, rows:rowCount, relations:data.relations.length, assets:data.assets.length
    };
    for (const count of data.coverage.counts) if (own(counts,count.unit)) ok(count.loaded === counts[count.unit],"COVERAGE_LOADED_COUNT");
    return data;
  }
  function numericParts(text) {
    const match = /^(-?)(\d+)(?:\.(\d+))?(?:[eE]([+-]?\d+))?$/.exec(text);
    const fraction = match[3] || "";
    let digits = (match[2] + fraction).replace(/^0+/,"");
    if (!digits) return {sign:0,digits:"0",position:0n};
    return {sign:match[1] ? -1 : 1,digits,position:BigInt(digits.length) + BigInt(match[4] || "0") - BigInt(fraction.length)};
  }
  function compareNumeric(left,right) {
    const a = numericParts(left), b = numericParts(right);
    if (a.sign !== b.sign) return a.sign < b.sign ? -1 : 1;
    if (!a.sign) return 0;
    if (a.position !== b.position) return (a.position < b.position ? -1 : 1) * a.sign;
    const size = Math.max(a.digits.length,b.digits.length);
    const first = a.digits.padEnd(size,"0"), second = b.digits.padEnd(size,"0");
    return (first === second ? 0 : first < second ? -1 : 1) * a.sign;
  }
  function csvCell(value) {
    const text = String(value);
    const dangerous = /^[\s\u0000-\u001f\u007f-\u009f\ufeff]*[=+\-@]/u.test(text);
    const escaped = text.replace(/[\u0000-\u001f\u007f-\u009f\ufeff]/g, character =>
      "\\u" + character.charCodeAt(0).toString(16).padStart(4,"0"));
    return '"' + ((dangerous ? "'" : "") + escaped).replace(/"/g,'""') + '"';
  }
  const cellText = cell => cell.type === "missing" ? "MISSING" : cell.type === "null" ? "null" : cell.type === "string" && cell.literal === "" ? '"" (string vazia)' : cell.literal;
  const admissionText = row => row.requirement ? row.requirement.admission + (row.requirement.admission === "UNADMITTED_NATIVE_RF" ? " — não admitida" : "") + "; categoria " + row.requirement.category_status : "Requisito não declarado";
  const bindingText = reference => reference.resolution === "RESOLVED" ? "vínculo declarado resolvido" : "não vinculada — " + reference.resolution;

  function mount(root, descriptor, options = {}) {
    ok(root && typeof root.appendChild === "function","MOUNT_ROOT_REQUIRED");
    const doc = root.ownerDocument;
    const instance = "atlas-f3b-" + (++instanceCounter);
    const now = typeof options.now === "function" ? options.now : () => Date.now();
    const sortTypes = copy(options.sortTypes || {});
    let data = null, session = null, revision = 0, selected = null, expired = false, disposed = false, error = "", timer = null;
    let tableNav = null, search = "", admission = "", sort = null, page = 0;
    let pageSize = options.pageSize === undefined ? 10 : options.pageSize;
    ok(Number.isInteger(pageSize) && pageSize >= 1 && pageSize <= 100,"PAGE_SIZE");
    const element = (tag,text,attributes = {}) => {
      const node = doc.createElement(tag);
      if (text !== undefined && text !== null) node.textContent = text;
      for (const [key,value] of Object.entries(attributes)) node.setAttribute(key,String(value));
      return node;
    };
    const wrapper = element("section",null,{class:"atlas-f3b","aria-label":"Tabelas derivadas de apresentação legada"});
    wrapper.append(element("h2","Tabelas — LEGACY_DERIVED"));
    const notice = element("p",null,{"data-f3b":"context"});
    const errorNode = element("p","",{role:"alert","data-f3b":"error",class:"f3b-error"});
    const controls = element("div",null,{class:"f3b-controls"});
    const labelled = (text,node,key) => {
      const id = instance + "-" + key;
      node.id = id; node.setAttribute("data-f3b",key);
      const label = element("label",text,{"for":id});
      label.append(node); controls.append(label); return node;
    };
    const tableSelect = labelled("Tabela / ocorrência",element("select"),"tables");
    const searchInput = labelled("Buscar texto, identidade ou estado",element("input",null,{type:"search"}),"search");
    const admissionSelect = labelled("Admissão declarada",element("select"),"admission");
    for (const [value,label] of [["","Todas"],["UNADMITTED_NATIVE_RF","UNADMITTED_NATIVE_RF — não admitida"],["ADMITTED_NATIVE_RF","ADMITTED_NATIVE_RF"],["NOT_EVALUATED","NOT_EVALUATED"],["NOT_APPLICABLE","NOT_APPLICABLE"]]) admissionSelect.append(element("option",label,{value}));
    const sortSelect = labelled("Ordenar coluna com tipo declarado",element("select"),"sort");
    const directionSelect = labelled("Direção da ordenação",element("select"),"direction");
    directionSelect.append(element("option","Ascendente",{value:"asc"}),element("option","Descendente",{value:"desc"}));
    const summary = element("p","",{"data-f3b":"summary","aria-live":"polite"});
    const viewport = element("div",null,{class:"f3b-viewport",tabindex:"0","aria-label":"Tabela com rolagem horizontal e vertical; conteúdo integral disponível"});
    const pager = element("div",null,{class:"f3b-actions"});
    const button = (label,key,handler) => {
      const node = element("button",label,{type:"button","data-f3b":key});
      node.addEventListener("click",handler); return node;
    };
    const previous = button("Página anterior","prev",() => query({page:page - 1}));
    const next = button("Próxima página","next",() => query({page:page + 1}));
    const detail = element("pre","Selecione uma linha para consultar todos os campos.",{"data-f3b":"detail",tabindex:"-1","aria-label":"Detalhe literal da linha"});
    const exportLabel = element("label","Exportação em memória — JSON literal fiel; CSV neutraliza fórmulas e representa controles como \\uXXXX.",{"for":instance + "-export"});
    const output = element("textarea","",{id:instance + "-export",readonly:"readonly","data-f3b":"export-output",rows:"6"});
    const jsonButton = button("Exportar JSON literal","export-json",() => { const text = exportJSON(); if (text !== null) { output.value = text; output.focus(); } });
    const csvButton = button("Exportar CSV seguro","export-csv",() => { const text = exportCSV(tableNav); if (text !== null) { output.value = text; output.focus(); } });
    pager.append(previous,next,jsonButton,csvButton);
    exportLabel.append(output);
    wrapper.append(notice,errorNode,controls,summary,viewport,pager,detail,exportLabel);
    root.append(wrapper);

    const current = () => data && data.tables.find(table => table.identity.navigation_id === tableNav);
    const report = reason => { error = String(reason instanceof Error ? reason.message : reason); errorNode.textContent = error; return false; };
    const clearError = () => { error = ""; errorNode.textContent = ""; };
    function live() {
      if (disposed) return false;
      if (data && now() >= Date.parse(data.snapshot.expires_at)) {
        data = null; session = null; selected = null; tableNav = null; expired = true;
        clearTimeout(timer); timer = null; output.value = "";
        error = "SNAPSHOT_EXPIRED: seleção e links invalidados";
        render(true);
      }
      return data !== null;
    }
    function armTimer() {
      clearTimeout(timer);
      if (!data || disposed) return;
      timer = setTimeout(() => { if (live()) armTimer(); },Math.max(1,Math.min(3600000,Date.parse(data.snapshot.expires_at) - now())));
    }
    function declaration(table,column) {
      const declared = sortTypes[table.identity.navigation_id] && sortTypes[table.identity.navigation_id][column];
      if (!declared || !TYPES.includes(declared.type) || !own(declared,"unit")) return null;
      return declared;
    }
    function validateSort(table,candidate) {
      ok(candidate && Number.isInteger(candidate.column) && candidate.column >= 0 && candidate.column < table.columns.length &&
        ["asc","desc"].includes(candidate.direction),"SORT_ARGUMENT");
      const declared = declaration(table,candidate.column);
      ok(declared,"SORT_TYPE_NOT_DECLARED");
      for (const row of table.rows) {
        const cell = row.cells[candidate.column];
        if (cell.type === "missing" || cell.type === "null") continue;
        ok(cell.type === declared.type && cell.unit === declared.unit,"SORT_INCOMPATIBLE_TYPE_OR_UNIT");
      }
    }
    function rowsFor(table) {
      if (!table) return [];
      const needle = search.toLowerCase();
      const rows = table.rows.map((row,index) => ({row,index})).filter(item => {
        const row = item.row;
        return (!admission || row.requirement && row.requirement.admission === admission) &&
          (!needle || (JSON.stringify(row) + " " + admissionText(row)).toLowerCase().includes(needle));
      });
      if (sort) {
        const type = declaration(table,sort.column).type;
        rows.sort((a,b) => {
          const first = a.row.cells[sort.column], second = b.row.cells[sort.column];
          const firstAbsent = first.type === "missing" || first.type === "null";
          const secondAbsent = second.type === "missing" || second.type === "null";
          if (firstAbsent || secondAbsent) return firstAbsent === secondAbsent ? a.index - b.index : firstAbsent ? 1 : -1;
          const compared = type === "integer" || type === "decimal" ? compareNumeric(first.literal,second.literal) :
            first.literal === second.literal ? 0 : first.literal < second.literal ? -1 : 1;
          return (sort.direction === "desc" ? -compared : compared) || a.index - b.index;
        });
      }
      return rows.map(item => item.row);
    }
    function render(refreshControls = false) {
      if (disposed) return;
      errorNode.textContent = error;
      const table = current(), rows = rowsFor(table);
      page = Math.max(0,Math.min(page,Math.max(0,Math.ceil(rows.length / pageSize) - 1)));
      if (refreshControls) {
        tableSelect.replaceChildren();
        if (data) for (const item of data.tables) {
          const identity = item.identity;
          const domain = item.domain_origin === "DECLARED" ? item.domain : "UNKNOWN";
          tableSelect.append(element("option",item.title_literal + " | " + domain + " | ocorrência " + identity.occurrence + " | " + bindingText(item.record_binding),{value:identity.navigation_id,"data-table-nav":identity.navigation_id}));
        }
        sortSelect.replaceChildren(element("option","Ordem original",{value:""}));
        if (table) table.columns.forEach((column,index) => {
          const declared = declaration(table,index);
          if (declared) sortSelect.append(element("option",column.header_literal + " [" + declared.type + "; unidade " + String(declared.unit) + "]",{value:index}));
        });
      }
      tableSelect.value = tableNav || ""; searchInput.value = search; admissionSelect.value = admission;
      sortSelect.value = sort ? String(sort.column) : ""; directionSelect.value = sort ? sort.direction : "asc";
      for (const control of [tableSelect,searchInput,admissionSelect,sortSelect,directionSelect,jsonButton,csvButton]) control.disabled = !data;
      previous.disabled = !data || page === 0; next.disabled = !data || (page + 1) * pageSize >= rows.length;
      if (!data) {
        notice.textContent = expired ? "Snapshot expirado; nova importação em memória necessária." : "Nenhuma tabela carregada.";
        summary.textContent = "Carregadas 0; filtradas 0; visíveis 0. Total global UNKNOWN_UPSTREAM / GLOBAL_UNPROVEN.";
        viewport.replaceChildren(element("p","Sem dados disponíveis."));
        detail.textContent = "Sem seleção.";
        return;
      }
      notice.textContent = "Fonte " + data.source.source_id + " | snapshot " + data.snapshot.snapshot_id +
        " | OBSERVED_SNAPSHOT_ONLY | expira " + data.snapshot.expires_at +
        " | schema " + data.validation.descriptor_schema + " / semântica " + data.validation.descriptor_semantics +
        " | NOT_VERIFIED (autenticidade) / NOT_EVALUATED (ciência). " +
        data.gaps.map(gap => gap.code + ": " + gap.note).join(" | ");
      const visible = rows.slice(page * pageSize,(page + 1) * pageSize);
      summary.textContent = "Tabelas " + data.tables.length + "; carregadas " + (table ? table.rows.length : 0) +
        "; filtradas " + rows.length + "; visíveis " + visible.length + "; página " + (page + 1) + "/" +
        Math.max(1,Math.ceil(rows.length / pageSize)) + ". Unidade: ocorrências de linha no snapshot selecionado. Total global UNKNOWN_UPSTREAM / GLOBAL_UNPROVEN; snapshots não somados.";
      if (!table) {
        viewport.replaceChildren(element("p","Descriptor sem tabelas. Disponibilidade de outros domínios UNKNOWN."));
        detail.textContent = "Sem seleção."; return;
      }
      const htmlTable = element("table");
      htmlTable.append(element("caption",table.title_literal + " | " + bindingText(table.record_binding) + " | native_id " +
        (table.identity.native_id === null ? "null" : table.identity.native_id) + " | " + table.identity.navigation_id +
        " | ocorrência " + table.identity.occurrence + " | " + data.source.source_id + "/" + data.snapshot.snapshot_id));
      const head = element("thead"), headerRow = element("tr");
      table.columns.forEach((column,index) => headerRow.append(element("th",column.header_literal,{id:instance + "-col-" + index,scope:"col"})));
      headerRow.append(element("th","Navegação derivada",{id:instance + "-navigation",scope:"col"})); head.append(headerRow);
      const body = element("tbody");
      for (const row of visible) {
        const tr = element("tr",null,{"data-row-nav":row.identity.navigation_id});
        if (selected && selected.row_navigation_id === row.identity.navigation_id) tr.setAttribute("aria-selected","true");
        row.cells.forEach((cell,index) => {
          const td = element("td",null,{headers:instance + "-col-" + index});
          td.append(element("span",cellText(cell),{class:"f3b-literal"}),element("small",
            "tipo=" + cell.type + "; unidade=" + String(cell.unit) + "; precisão=" + String(cell.precision) + "; ausência=" + String(cell.absence),
            {class:"f3b-cell-meta"})); tr.append(td);
        });
        const actions = element("td",null,{headers:instance + "-navigation"});
        const rowButton = button("Detalhe da linha " + row.ordinal,"row-detail",() => select(token(tableNav,row.identity.navigation_id)));
        rowButton.setAttribute("data-row-nav",row.identity.navigation_id);
        actions.append(rowButton,element("small",admissionText(row) + " | native_id=" + String(row.identity.native_id) +
          " | binding_gap=" + row.binding_gap + " | Run " + row.run_binding.resolution,{class:"f3b-cell-meta"}));
        tr.append(actions); body.append(tr);
      }
      htmlTable.append(head,body);
      viewport.replaceChildren(htmlTable);
      if (!visible.length) viewport.append(element("p",table.rows.length ? "Nenhuma linha corresponde aos filtros." : "Tabela conhecida vazia; não prova ausência upstream."));
      const row = selected && selected.row_navigation_id ? table.rows.find(item => item.identity.navigation_id === selected.row_navigation_id) : null;
      detail.textContent = row ? JSON.stringify(row,null,2) : "Selecione uma linha. " + JSON.stringify({identity:table.identity,domain:table.domain,domain_origin:table.domain_origin,record_binding:table.record_binding},null,2);
    }
    function setTables(input) {
      if (disposed) return false;
      live();
      let nextData;
      try { nextData = validateDescriptor(input,now()); } catch (reason) { return report(reason); }
      data = nextData; session = instance + "-import-" + (++revision); selected = null; expired = false;
      tableNav = data.tables.length ? data.tables[0].identity.navigation_id : null;
      search = ""; admission = ""; sort = null; page = 0; output.value = ""; clearError();
      render(true); armTimer(); return true;
    }
    function token(tableNavigation,rowNavigation = null) {
      if (!live()) return null;
      const table = data.tables.find(item => item.identity.navigation_id === tableNavigation);
      if (!table) return null;
      const row = rowNavigation === null ? null : table.rows.find(item => item.identity.navigation_id === rowNavigation);
      if (rowNavigation !== null && !row) return null;
      return {session_id:session,source_id:data.source.source_id,snapshot_id:data.snapshot.snapshot_id,
        table_navigation_id:table.identity.navigation_id,table_occurrence:table.identity.occurrence,
        row_navigation_id:row ? row.identity.navigation_id : null,row_occurrence:row ? row.identity.occurrence : null};
    }
    function select(selection) {
      if (!live()) return report("STALE_SELECTION: snapshot indisponível");
      const expected = selection && token(selection.table_navigation_id,selection.row_navigation_id);
      if (!expected || Object.keys(selection).length !== Object.keys(expected).length || !Object.keys(expected).every(key => selection[key] === expected[key])) return report("STALE_OR_UNKNOWN_SELECTION");
      tableNav = selection.table_navigation_id; selected = copy(selection);
      search = ""; admission = ""; sort = null;
      const table = current(), index = selection.row_navigation_id === null ? 0 : table.rows.findIndex(row => row.identity.navigation_id === selection.row_navigation_id);
      page = Math.floor(Math.max(0,index) / pageSize); clearError(); render(true); detail.focus();
      const EventClass = doc.defaultView.CustomEvent;
      wrapper.dispatchEvent(new EventClass("atlas-f3b-select",{bubbles:true,detail:copy(selected)}));
      return true;
    }
    function query(change = {}) {
      if (!live()) return report("SNAPSHOT_UNAVAILABLE");
      const nextTableNav = own(change,"table") ? change.table : tableNav;
      const table = data.tables.find(item => item.identity.navigation_id === nextTableNav);
      const nextSearch = own(change,"search") ? change.search : search;
      const nextAdmission = own(change,"admission") ? change.admission : admission;
      const changedTable = nextTableNav !== tableNav;
      const nextSort = own(change,"sort") ? change.sort : changedTable ? null : sort;
      const nextSize = own(change,"pageSize") ? change.pageSize : pageSize;
      const nextPage = own(change,"page") ? change.page : 0;
      try {
        ok(table,"UNKNOWN_TABLE"); ok(typeof nextSearch === "string" && nextSearch.length <= 65536,"SEARCH_ARGUMENT");
        ok(["","UNADMITTED_NATIVE_RF","ADMITTED_NATIVE_RF","NOT_EVALUATED","NOT_APPLICABLE"].includes(nextAdmission),"ADMISSION_ARGUMENT");
        ok(Number.isInteger(nextSize) && nextSize >= 1 && nextSize <= 100,"PAGE_SIZE");
        ok(Number.isInteger(nextPage) && nextPage >= 0,"PAGE_ARGUMENT");
        if (nextSort !== null) validateSort(table,nextSort);
      } catch (reason) { return report(reason); }
      tableNav = nextTableNav; search = nextSearch; admission = nextAdmission; sort = nextSort === null ? null : copy(nextSort);
      pageSize = nextSize; page = nextPage;
      if (changedTable) selected = null;
      clearError(); render(changedTable); return true;
    }
    function getState() {
      live();
      const table = current(), rows = rowsFor(table), visible = rows.slice(page * pageSize,(page + 1) * pageSize);
      return {loaded:table ? table.rows.length : 0,filtered:rows.length,visible:visible.length,page,pageSize,
        table_navigation_id:tableNav,selection:copy(selected),session_id:session,error,expired,
        tableCount:data ? data.tables.length : 0,global_total:null,rows:copy(visible)};
    }
    function exportJSON() {
      if (!live()) { report("SNAPSHOT_UNAVAILABLE"); return null; }
      clearError(); return JSON.stringify(data,null,2);
    }
    function exportCSV(navigation = tableNav) {
      if (!live()) { report("SNAPSHOT_UNAVAILABLE"); return null; }
      const table = data.tables.find(item => item.identity.navigation_id === navigation);
      if (!table) { report("UNKNOWN_TABLE"); return null; }
      clearError();
      const rows = [table.columns.map(column => column.header_literal),...table.rows.map(row => row.cells.map(cell => cell.type === "missing" ? "MISSING" : cell.type === "null" ? "null" : cell.literal))];
      return rows.map(row => row.map(csvCell).join(",")).join("\r\n") + "\r\n";
    }
    function dispose() {
      if (disposed) return;
      disposed = true; clearTimeout(timer); data = null; selected = null; session = null;
      output.value = ""; detail.textContent = ""; wrapper.remove();
    }
    tableSelect.addEventListener("change",() => query({table:tableSelect.value}));
    searchInput.addEventListener("input",() => query({search:searchInput.value}));
    admissionSelect.addEventListener("change",() => query({admission:admissionSelect.value}));
    sortSelect.addEventListener("change",() => query({sort:sortSelect.value === "" ? null : {column:Number(sortSelect.value),direction:directionSelect.value}}));
    directionSelect.addEventListener("change",() => { if (sortSelect.value !== "") query({sort:{column:Number(sortSelect.value),direction:directionSelect.value}}); });
    const api = Object.freeze({setTables,select,query,token,getState,exportJSON,exportCSV,dispose});
    render(true);
    if (descriptor !== undefined) setTables(descriptor);
    return api;
  }
  globalThis.AtlasF3BTables = Object.freeze({mount});
})();
