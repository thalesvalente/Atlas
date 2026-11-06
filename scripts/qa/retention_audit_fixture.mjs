/** Invented N02 fixtures. Plans come from the unchanged Feature 005 exporter. */
import {createHash} from 'node:crypto';
import {mkdtemp, mkdir, writeFile, readdir, readFile, readlink} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {nativeFragments} from '../../packages/atlas/src/atlas_viewer/static/native_navigation.js';
import {SelectionLedger} from '../../packages/atlas/src/atlas_viewer/static/native_triage_model.js';
import {buildRetentionPlan} from '../../packages/atlas/src/atlas_viewer/static/native_retention.js';

export const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
export const jsonBytes = value => Buffer.from(JSON.stringify(value), 'utf8');

function dto(uid, kind, raw, extra = {}) {
  const fragments = nativeFragments(raw, {all: true});
  const fields = [...fragments].filter(([, v]) => !['{', '['].includes(v[0])).map(([name, value]) => ({
    name, type: value === 'null' ? 'null' : value[0] === '"' ? 'string' : /^(true|false)$/.test(value)
      ? 'boolean' : /[.eE]/.test(value) ? 'number' : 'integer',
    text: value[0] === '"' ? JSON.parse(value) : value,
  }));
  const text = (...names) => names.map(name => fields.find(f => f.name === name))
    .find(field => field?.type === 'string')?.text ?? null;
  return {
    uid, kind, group: {record: 'records', table: 'result_tables', row: 'result_tables', asset: 'resources'}[kind],
    title: text('title', 'label', 'id') ?? kind, native_id: text('native_id', 'id'),
    source_key: text('id'), family: text('family'), status: text('execution_state'), date: null,
    parent_uid: null, fields, raw_json: raw, ...extra,
  };
}

export function makeFixture({omitRevision = false, revision = 'INVENTED-N02-R1', annotate = false,
  intent = 'KEEP_FULL'} = {}) {
  const entries = [
    dto('record-baseline', 'record', '{"id":"baseline-01","kind":"run","baseline":true,"title":"Baseline inventada","execution_state":"FAILED","dependencies":["shared-01"],"backup_verified":true,"metrics":{"integer":9007199254740993,"decimal":0.123456789012345678901,"negative_zero":-0.0}}'),
    dto('record-lexical', 'record', String.raw`{"id":"lexical-01","kind":"r\u0075n","title":"Registro léxico inventado"}`),
    dto('table-01', 'table', '{"id":"RF-SYNTHETIC","label":"Tabela inventada","rows":[]}', {row_count: 2}),
    dto('row-00', 'row', '{"id":"RF-0","cells":{"value":9007199254740993}}', {table_uid: 'table-01', parent_uid: 'table-01', ordinal: 0}),
    dto('row-01', 'row', '{"id":"RF-1","cells":{"value":0.123456789012345678901}}', {table_uid: 'table-01', parent_uid: 'table-01', ordinal: 1}),
    dto('resource-01', 'asset', '{"id":"shared-01","kind":"resource","uri":"https://example.invalid/never-opened","shared":true}'),
  ];
  const snapshot = {id: 'invented-n02-source', name: 'Fixture sintética N02', revision,
    metadata_sha256: sha256('invented source metadata, never a private source'), status: 'READY', entries};
  if (omitRevision) delete snapshot.revision;
  const selected = entries.filter(e => ['record-baseline', 'record-lexical', 'table-01'].includes(e.uid));
  const ledger = new SelectionLedger(snapshot);
  ledger.selectMany(selected);
  for (const entry of selected) ledger.setIntent(entry, intent);
  if (annotate) ledger.annotateBaseline(selected[1], 'Anotação inventada do operador; não altera a fonte.');
  const plan = buildRetentionPlan(snapshot, ledger.entries(), ledger);
  const contents = {
    shared01: Buffer.from('SYNTHETIC_SHARED_ARTIFACT_BYTES\n', 'utf8'),
    table01: Buffer.from('SYNTHETIC_TABLE_RESOURCE_BYTES\n', 'utf8'),
  };
  const inventory = {
    schema: 'atlas-retention-inventory/1', version: 1, contract: 'ATLAS_N01_R_N02_SANITIZED/1',
    source: structuredClone(plan.source), snapshot_key: plan.snapshot_key, plan_sha256: sha256(jsonBytes(plan)),
    inventory_integrity: {status: 'VERIFIED', scope: 'OBSERVED_SUBSET_INTEGRITY'},
    validation_status: 'PARTIAL', evidence_scope: 'SCOPED_READ_ONLY',
    delta_provenance: {origin: 'N01_R_READ_ONLY', base_inventory_sha256: sha256('invented historic inventory'),
      receipt_sha256: sha256('invented N01-R receipt')},
    bindings: plan.items.map((item, index) => ({
      identity: structuredClone(item.identity), type: item.type, intent: item.intent,
      file_ids: [index === 2 ? 'table01' : 'shared01'], validation_status: 'PARTIAL',
      evidence_scope: index === 2 ? 'DOCUMENTARY_TABLE_AND_DOWNSTREAM_RELATION' : 'SCOPED_RECORD_PHYSICAL_BINDING',
      dependency_status: 'UNRESOLVED', backup_status: 'NOT_VERIFIED',
    })),
    files: Object.entries(contents).map(([id, content]) => ({
      id, sha256: sha256(content), size_bytes: content.length,
      category: id === 'shared01' ? 'SHARED_ARTIFACT' : 'DERIVED_RESULT',
      consumers: plan.items.filter((_, index) => id === 'shared01' ? index < 2 : index === 2)
        .map(item => item.identity.selection_key),
      shared: id === 'shared01', backup_status: 'NOT_VERIFIED',
    })),
  };
  return {plan, inventory, snapshot, contents};
}

export function encodeFixture(fixture, {rebindPlan = false} = {}) {
  const planBytes = jsonBytes(fixture.plan), snapshotBytes = jsonBytes(fixture.snapshot);
  const inventory = structuredClone(fixture.inventory);
  if (rebindPlan) inventory.plan_sha256 = sha256(planBytes);
  const inventoryBytes = jsonBytes(inventory);
  return {planBytes, inventoryBytes, snapshotBytes,
    expectedInventorySha256: sha256(inventoryBytes), expectedSnapshotSha256: sha256(snapshotBytes)};
}

/** Deliberately retain small synthetic directories: no cleanup/deletion command. */
export async function materializeCorpus(fixture) {
  const base = await mkdtemp(path.join(tmpdir(), 'atlas-n02-invented-'));
  const corpus = path.join(base, 'corpus');
  await mkdir(path.join(corpus, 'data'), {recursive: true});
  const files = {}, paths = {};
  for (const [id, bytes] of Object.entries(fixture.contents)) {
    const relative_path = `data/${id}.bin`;
    const destination = path.join(corpus, ...relative_path.split('/'));
    await writeFile(destination, bytes, {flag: 'wx'});
    files[id] = {root_id: 'corpus', relative_path};
    paths[id] = destination;
  }
  return {base, corpus, roots: {corpus}, files, paths};
}

/** No-follow observation of this fixture only, for before/after equality. */
export async function fixtureTree(directory) {
  const result = [];
  async function walk(current, relative) {
    const entries = await readdir(current, {withFileTypes: true});
    entries.sort((a, b) => a.name.localeCompare(b.name));
    for (const entry of entries) {
      const full = path.join(current, entry.name), rel = relative ? `${relative}/${entry.name}` : entry.name;
      if (entry.isSymbolicLink()) result.push({path: rel, kind: 'link', target: await readlink(full)});
      else if (entry.isDirectory()) { result.push({path: rel, kind: 'directory'}); await walk(full, rel); }
      else if (entry.isFile()) result.push({path: rel, kind: 'file', sha256: sha256(await readFile(full))});
      else result.push({path: rel, kind: 'other'});
    }
  }
  await walk(directory, '');
  return result;
}
