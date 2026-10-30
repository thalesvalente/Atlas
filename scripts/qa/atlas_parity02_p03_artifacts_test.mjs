import assert from "node:assert/strict";
import {readFile} from "node:fs/promises";
import {test} from "node:test";
import {METADATA_LIMITS, MetadataError, validateMetadata, validateCandidate, renderMetadata, renderCandidate} from "../../packages/atlas/src/atlas_viewer/static/parity02_p03_artifacts.js";

const fixture = (name) => readFile(new URL(`../../tests/fixtures/atlas_parity02/p03/${name}`, import.meta.url), "utf8").then(JSON.parse);
const original = await fixture("artifact-descriptor.json");
const candidate = await fixture("document-candidate.json");
const product = await fixture("artifact-product-candidate.json");
const copy = (v) => structuredClone(v);
const code = (expected) => (error) => error instanceof MetadataError && error.code === expected;

test("metadata preserves File and neutral mention semantics", () => {
  const result = validateMetadata(original);
  const item = result.items.find((i) => i.identity.id === "report.pdf");
  assert.equal(item.kind, "artifact");
  assert.deepEqual(item.types, ["File"]);
  assert.deepEqual(item.relations, []);
  assert.equal(item.mentions[0].kind, "mention");
  assert.equal(item.availability.observed, "UNVERIFIED");
});
test("copy is detached and validation never mutates input", () => {
  const before = copy(original);
  const result = validateMetadata(original);
  result.items[0].types.push("Product");
  result.items[0].relations[0].source.id = "different";
  assert.deepEqual(original, before);
});
test("missing and mismatched digests remain separate without approval", () => {
  const result = validateMetadata(original);
  const missing = result.items.find((i) => i.identity.id === "report.pdf");
  assert.equal(missing.digests.calculated_sha256, null);
  const bad = result.items.find((i) => i.identity.id === "data/tampered.csv");
  assert.equal(bad.digests.declared_sha256, "c".repeat(64));
  assert.equal(bad.digests.calculated_sha256, "d".repeat(64));
  assert.equal(bad.availability.observed, "INTEGRITY_MISMATCH");
  assert.equal("approved" in bad, false);
});
test("HTML, URIs and Unicode remain exact inert data", () => {
  const result = validateMetadata(original);
  const bad = result.items.find((i) => i.identity.id.startsWith("https:"));
  assert.equal(bad.name, '<img src=x onerror="globalThis.P03_ATTACK=true">');
  assert.equal(bad.description, "javascript:globalThis.P03_ATTACK=true");
  assert.equal(result.items.find((i) => i.identity.id === "data/result.csv").name, "Resultado α — água 🌱");
});
test("source scope and duplicate identities cannot be silently merged", () => {
  const value = copy(original);
  value.items[0].identity.source_key = "different";
  assert.throws(() => validateMetadata(value), code("SOURCE_MISMATCH"));
  const duplicate = copy(original);
  duplicate.items.push(copy(duplicate.items[0]));
  assert.throws(() => validateMetadata(duplicate), code("DUPLICATE_ID"));
});
test("File cannot acquire product/document semantic kind", () => {
  for (const kind of ["product", "document", "entity"]) {
    const value = copy(original); value.items[0].kind = kind;
    assert.throws(() => validateMetadata(value), code("SEMANTIC_KIND"));
  }
});
test("mention and output categories are validated separately", () => {
  const value = copy(original);
  value.items.find((i) => i.identity.id === "report.pdf").mentions[0].kind = "output";
  assert.throws(() => validateMetadata(value), code("RELATION_KIND"));
  const unrelated = copy(original);
  unrelated.items[0].relations[0].source.id = "other";
  unrelated.items[0].relations[0].target.id = "another";
  assert.throws(() => validateMetadata(unrelated), code("RELATION_IDENTITY"));
});
test("invalid status/digest/type fail with predictable error codes", () => {
  let value = copy(original); value.items[0].availability.observed = "APPROVED";
  assert.throws(() => validateMetadata(value), code("STATUS_VALUE"));
  value = copy(original); value.items[0].digests.calculated_sha256 = "0";
  assert.throws(() => validateMetadata(value), code("DIGEST_FORMAT"));
  value = copy(original); value.items[0].name = 9007199254740992;
  assert.throws(() => validateMetadata(value), code("FIELD_TYPE"));
});
test("empty descriptor and maximum item/text boundaries", () => {
  const empty = copy(original); empty.items = [];
  assert.deepEqual(validateMetadata(empty).items, []);
  const large = copy(empty);
  large.items = Array.from({length: METADATA_LIMITS.items}, (_, n) => ({...copy(original.items[0]), identity: {source_key: original.source.key, id: `item-${n}`}, name: "🌱".repeat(METADATA_LIMITS.text), relations: [], mentions: []}));
  assert.equal(validateMetadata(large).items.length, METADATA_LIMITS.items);
  large.items.push(copy(large.items[0]));
  assert.throws(() => validateMetadata(large), code("LIMIT"));
  const long = copy(original); long.items[0].name = "x".repeat(METADATA_LIMITS.text + 1);
  assert.throws(() => validateMetadata(long), code("LIMIT"));
});
test("candidate requires explicit synthetic semantics", () => {
  assert.equal(validateCandidate(candidate).semantic_kind, "document");
  assert.equal(validateCandidate(product).semantic_kind, "product");
  const noFlag = copy(candidate); delete noFlag.synthetic;
  assert.throws(() => validateCandidate(noFlag), code("SYNTHETIC_REQUIRED"));
  const noKind = copy(candidate); delete noKind.semantic_kind;
  assert.throws(() => validateCandidate(noKind), code("SEMANTIC_KIND"));
  assert.throws(() => validateCandidate(original), code("DESCRIPTOR_VERSION"));
});
test("aggregate relationship copies are bounded across cards", () => {
  const value = copy(original); value.items = [];
  for (let n = 0; n < 3; n++) {
    const item = copy(original.items[0]);
    item.identity.id = `entity-${n}`;
    item.relations = Array.from({length: METADATA_LIMITS.relations}, () => ({source: copy(item.identity), target: {source_key: value.source.key, id: "target"}, kind: "input"}));
    item.mentions = [];
    value.items.push(item);
  }
  assert.throws(() => validateMetadata(value), code("LIMIT"));
});
test("candidate text is inert and optional content remains missing", () => {
  const value = validateCandidate(candidate);
  assert.equal(value.fields[1].value, null);
  assert.match(value.fields[2].value, /<img/);
  assert.match(value.sections[1].text, /javascript:/);
  const before = copy(candidate); value.fields[0].value = "changed";
  assert.deepEqual(candidate, before);
});
test("candidate numeric values require caller-preserved textual representation", () => {
  const value = copy(candidate); value.fields[0].value = 9007199254740992;
  assert.throws(() => validateCandidate(value), code("FIELD_TYPE"));
  value.fields[0].value = "0009007199254740993123456789";
  assert.equal(validateCandidate(value).fields[0].value, "0009007199254740993123456789");
});
test("candidate collection limits and required document object are enforced", () => {
  const value = copy(candidate); value.sections = Array(METADATA_LIMITS.sections + 1).fill({title: "t", text: "x"});
  assert.throws(() => validateCandidate(value), code("LIMIT"));
  assert.throws(() => renderMetadata(null, original), code("DOCUMENT_REQUIRED"));
  assert.throws(() => renderCandidate(null, candidate), code("DOCUMENT_REQUIRED"));
});
