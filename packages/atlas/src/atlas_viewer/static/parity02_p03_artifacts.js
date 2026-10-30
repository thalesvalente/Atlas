/* Opt-in metadata components. No payload readers, navigation or boot hooks. */
export const METADATA_LIMITS = Object.freeze({items: 200, relations: 5000, text: 16384, id: 2048, fields: 100, sections: 100});
const declaredStatuses = new Set(["PRESENT", "MISSING", "EXTERNAL", "UNKNOWN"]);
const observedStatuses = new Set(["UNVERIFIED", "AVAILABLE", "AVAILABLE_UNVERIFIED", "MISSING", "EXTERNAL_UNRESOLVED", "UNAVAILABLE", "INTEGRITY_MISMATCH", "READ_BUDGET_EXCEEDED", "UNSAFE_REFERENCE"]);

export class MetadataError extends Error {
  constructor(code, path) { super(`${code}: ${path}`); this.name = "MetadataError"; this.code = code; this.path = path; }
}
function object(value, path) {
  if (value === null || typeof value !== "object" || Array.isArray(value)) throw new MetadataError("FIELD_TYPE", path);
  return value;
}
function text(value, path, required = false, limit = METADATA_LIMITS.text) {
  if (value == null && !required) return null;
  if (typeof value !== "string" || (required && !value)) throw new MetadataError("FIELD_TYPE", path);
  if (value.length > limit * 2 || [...value].length > limit) throw new MetadataError("LIMIT", path);
  return value;
}
function array(value, path, limit) {
  if (!Array.isArray(value)) throw new MetadataError("FIELD_TYPE", path);
  if (value.length > limit) throw new MetadataError("LIMIT", path);
  return value;
}
function digest(value, path) {
  const result = text(value, path);
  if (result !== null && !/^[0-9a-f]{64}$/.test(result)) throw new MetadataError("DIGEST_FORMAT", path);
  return result;
}
function identity(value, path, sourceKey = null) {
  const input = object(value, path);
  const result = {source_key: text(input.source_key, `${path}.source_key`, true, METADATA_LIMITS.id), id: text(input.id, `${path}.id`, true, METADATA_LIMITS.id)};
  if (sourceKey !== null && result.source_key !== sourceKey) throw new MetadataError("SOURCE_MISMATCH", path);
  return result;
}
function relations(value, path, sourceKey, mention, itemId) {
  return array(value, path, METADATA_LIMITS.relations).map((raw, index) => {
    const r = object(raw, `${path}[${index}]`);
    const kinds = mention ? ["mention"] : ["input", "output", "derived_from"];
    if (!kinds.includes(r.kind)) throw new MetadataError("RELATION_KIND", `${path}[${index}].kind`);
    const source = identity(r.source, `${path}[${index}].source`, sourceKey);
    const target = identity(r.target, `${path}[${index}].target`, sourceKey);
    if (source.id !== itemId && target.id !== itemId) throw new MetadataError("RELATION_IDENTITY", `${path}[${index}]`);
    return {source, target, kind: r.kind};
  });
}

/** Validate/copy an explicit descriptor; this is not a Caderno validator. */
export function validateMetadata(descriptor) {
  const input = object(descriptor, "descriptor");
  if (input.version !== "p03-metadata/1" || input.semantic_status !== "DERIVED_CURRENT_CONTRACT") throw new MetadataError("DESCRIPTOR_VERSION", "descriptor");
  const rawSource = object(input.source, "source");
  const source = {key: text(rawSource.key, "source.key", true, METADATA_LIMITS.id), name: text(rawSource.name, "source.name"), metadata_sha256: digest(rawSource.metadata_sha256, "source.metadata_sha256")};
  const seen = new Set();
  let relationCount = 0;
  const items = array(input.items, "items", METADATA_LIMITS.items).map((raw, index) => {
    const item = object(raw, `items[${index}]`);
    const id = identity(item.identity, `items[${index}].identity`, source.key);
    if (seen.has(id.id)) throw new MetadataError("DUPLICATE_ID", `items[${index}].identity`);
    seen.add(id.id);
    const types = array(item.types, `items[${index}].types`, 64).map((v) => text(v, `items[${index}].types`, true, METADATA_LIMITS.id));
    if (item.kind !== (types.includes("File") ? "artifact" : "entity")) throw new MetadataError("SEMANTIC_KIND", `items[${index}].kind`);
    const availability = object(item.availability, `items[${index}].availability`);
    const declared = text(availability.declared, `items[${index}].availability.declared`);
    if (declared !== null && !declaredStatuses.has(declared)) throw new MetadataError("STATUS_VALUE", `items[${index}].availability.declared`);
    if (!observedStatuses.has(availability.observed)) throw new MetadataError("STATUS_VALUE", `items[${index}].availability.observed`);
    const digests = object(item.digests, `items[${index}].digests`);
    relationCount += array(item.relations, `items[${index}].relations`, METADATA_LIMITS.relations).length;
    relationCount += array(item.mentions, `items[${index}].mentions`, METADATA_LIMITS.relations).length;
    // A graph relation may appear on both endpoint cards, at most twice.
    if (relationCount > METADATA_LIMITS.relations * 2) throw new MetadataError("LIMIT", "relations.total");
    return {identity: id, kind: item.kind, name: text(item.name, `items[${index}].name`, true), types,
      description: text(item.description, `items[${index}].description`), media_type: text(item.media_type, `items[${index}].media_type`),
      availability: {declared, observed: availability.observed},
      digests: {declared_sha256: digest(digests.declared_sha256, `items[${index}].digests.declared_sha256`), calculated_sha256: digest(digests.calculated_sha256, `items[${index}].digests.calculated_sha256`)},
      relations: relations(item.relations, `items[${index}].relations`, source.key, false, id.id),
      mentions: relations(item.mentions, `items[${index}].mentions`, source.key, true, id.id)};
  });
  return {version: input.version, semantic_status: input.semantic_status, source, items};
}

/** Only synthetic, explicitly typed candidates can use the richer renderer. */
export function validateCandidate(descriptor) {
  const input = object(descriptor, "descriptor");
  if (input.version !== "p03-candidate/1" || input.semantic_status !== "CANDIDATE_PRESENTATION") throw new MetadataError("DESCRIPTOR_VERSION", "descriptor");
  if (input.synthetic !== true) throw new MetadataError("SYNTHETIC_REQUIRED", "synthetic");
  if (!["product", "document"].includes(input.semantic_kind)) throw new MetadataError("SEMANTIC_KIND", "semantic_kind");
  const fields = array(input.fields ?? [], "fields", METADATA_LIMITS.fields).map((raw, index) => {
    const field = object(raw, `fields[${index}]`);
    return {label: text(field.label, `fields[${index}].label`, true), value: text(field.value, `fields[${index}].value`)};
  });
  const sections = array(input.sections ?? [], "sections", METADATA_LIMITS.sections).map((raw, index) => {
    const section = object(raw, `sections[${index}]`);
    return {title: text(section.title, `sections[${index}].title`, true), text: text(section.text, `sections[${index}].text`)};
  });
  return {version: input.version, semantic_status: input.semantic_status, synthetic: true, semantic_kind: input.semantic_kind,
    identity: identity(input.identity, "identity"), title: text(input.title, "title", true), description: text(input.description, "description"), fields, sections};
}

function documentObject(doc) {
  if (!doc || typeof doc.createElement !== "function") throw new MetadataError("DOCUMENT_REQUIRED", "document");
}
function node(doc, tag, className, value = null) {
  const element = doc.createElement(tag);
  if (className) element.className = className;
  if (value !== null) element.textContent = value;
  return element;
}
function field(doc, list, label, value) {
  list.append(node(doc, "dt", "", label), node(doc, "dd", "", value === null || value === "" ? "Não declarado" : value));
}
function relationList(doc, parent, title, entries) {
  const section = node(doc, "section", "p03-metadata-relations");
  section.append(node(doc, "h4", "", title));
  if (!entries.length) section.append(node(doc, "p", "p03-metadata-empty", "Nenhuma relação declarada nesta categoria."));
  else {
    const list = node(doc, "ul", "");
    entries.forEach((r) => list.append(node(doc, "li", "", `${r.kind}: ${r.source.id} → ${r.target.id}`)));
    section.append(list);
  }
  parent.append(section);
}

/** Return a detached section. Mounting and lifecycle belong to the caller. */
export function renderMetadata(doc, descriptor) {
  documentObject(doc);
  const input = validateMetadata(descriptor);
  const section = node(doc, "section", "p03-metadata");
  section.setAttribute("aria-label", "Metadados declarados e observações do leitor");
  section.append(node(doc, "h2", "", "Metadados do contrato atual"), node(doc, "p", "p03-metadata-status", "Apresentação derivada · integridade não é autenticidade nem aprovação científica."));
  const source = node(doc, "dl", "p03-metadata-fields");
  field(doc, source, "Fonte", input.source.name);
  field(doc, source, "Identidade da fonte", input.source.key);
  field(doc, source, "SHA-256 dos metadados informado pelo leitor", input.source.metadata_sha256);
  section.append(source);
  if (!input.items.length) section.append(node(doc, "p", "p03-metadata-empty", "Nenhum artefato ou referência selecionado."));
  input.items.forEach((item) => {
    const article = node(doc, "article", "p03-metadata-card");
    article.dataset.entityId = item.identity.id;
    article.dataset.sourceKey = item.identity.source_key;
    article.append(node(doc, "h3", "", item.name), node(doc, "p", "p03-metadata-kind", item.kind === "artifact" ? "Artefato declarado (File)" : "Entidade declarada"));
    const details = node(doc, "dl", "p03-metadata-fields");
    field(doc, details, "Identificador", item.identity.id);
    field(doc, details, "Fonte", item.identity.source_key);
    field(doc, details, "Tipos declarados", item.types.join(", "));
    field(doc, details, "Descrição", item.description);
    field(doc, details, "Formato declarado", item.media_type);
    field(doc, details, "Disponibilidade declarada", item.availability.declared);
    field(doc, details, "Disponibilidade observada pelo leitor", item.availability.observed);
    field(doc, details, "SHA-256 declarado", item.digests.declared_sha256);
    field(doc, details, "SHA-256 calculado informado pelo leitor", item.digests.calculated_sha256);
    article.append(details);
    relationList(doc, article, "Relações declaradas de entrada, saída ou derivação", item.relations);
    relationList(doc, article, "Menções neutras · sem inferência de produção", item.mentions);
    section.append(article);
  });
  return section;
}

/** Candidate semantics come from explicit synthetic input, never a File name. */
export function renderCandidate(doc, descriptor) {
  documentObject(doc);
  const input = validateCandidate(descriptor);
  const section = node(doc, "section", "p03-metadata p03-metadata-candidate");
  section.setAttribute("aria-label", input.semantic_kind === "product" ? "Produto candidato sintético" : "Documento candidato sintético");
  section.dataset.semanticKind = input.semantic_kind;
  section.append(node(doc, "h2", "", input.title), node(doc, "p", "p03-metadata-status", `${input.semantic_kind === "product" ? "Produto" : "Documento"} candidato · fixture sintética · sem novo contrato persistido.`));
  const details = node(doc, "dl", "p03-metadata-fields");
  field(doc, details, "Identificador", input.identity.id);
  field(doc, details, "Fonte", input.identity.source_key);
  field(doc, details, "Descrição", input.description);
  input.fields.forEach((item) => field(doc, details, item.label, item.value));
  section.append(details);
  input.sections.forEach((item) => {
    const part = node(doc, "section", "p03-metadata-text");
    part.append(node(doc, "h3", "", item.title), node(doc, "p", "", item.text === null || item.text === "" ? "Não declarado" : item.text));
    section.append(part);
  });
  return section;
}
