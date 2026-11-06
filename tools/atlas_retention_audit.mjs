#!/usr/bin/env node
/** Offline N02 consumer. No runtime routes, writes, discovery, network or deletion.
 * Only caller-supplied roots/file bindings can authorize filesystem reads.
 */
import {constants} from 'node:fs';
import {lstat, open, realpath} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {isDeepStrictEqual} from 'node:util';
import {buildRetentionPlan, RETENTION_INTENTS} from '../packages/atlas/src/atlas_viewer/static/native_retention.js';
import {selectionKey, snapshotKey} from '../packages/atlas/src/atlas_viewer/static/native_triage_model.js';

const MAX_DOCUMENT_BYTES = 64 * 1024 * 1024;
const DIGEST = /^[a-f0-9]{64}$/;
const ID = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const STATES = ['VERIFIED', 'PARTIAL', 'UNRESOLVED', 'NOT_ASSESSED'];
const SCOPES = ['DOCUMENTARY_WITNESS_ONLY', 'DOCUMENTARY_TABLE_AND_DOWNSTREAM_RELATION',
  'SCOPED_RECORD_PHYSICAL_BINDING', 'RESOURCE_REFERENCE_CROSSWALK'];
const CATEGORIES = ['SOURCE_ORIGINAL', 'UPSTREAM_INPUT', 'DERIVED_RESULT', 'SHARED_ARTIFACT',
  'EXCLUSIVE_ARTIFACT', 'CHECKPOINT', 'CACHE', 'BACKUP', 'UNKNOWN_DEPENDENCY'];
const BACKUP = ['NOT_VERIFIED', 'DECLARED'];
const own = (value, key) => Object.prototype.hasOwnProperty.call(value, key);
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const object = value => value !== null && typeof value === 'object' && !Array.isArray(value);

export class RetentionError extends Error {
  constructor(code) { super(code); this.name = 'RetentionError'; this.code = code; }
}
function requireThat(condition, code = 'MALFORMED') { if (!condition) throw new RetentionError(code); }
function exactKeys(value, keys) {
  requireThat(object(value) && isDeepStrictEqual(Object.keys(value).sort(), [...keys].sort()));
}
function nonempty(value) { return typeof value === 'string' && value.length > 0; }
function digest(value) { return typeof value === 'string' && DIGEST.test(value); }

/** Reject duplicate decoded member names before JSON.parse can overwrite them.
 * raw_json strings remain strings; scientific numbers are never reserialized.
 */
export function parseJsonStrict(bytes) {
  requireThat(Buffer.isBuffer(bytes) && bytes.length <= MAX_DOCUMENT_BYTES);
  let text;
  try { text = new TextDecoder('utf-8', {fatal: true}).decode(bytes); }
  catch { throw new RetentionError('MALFORMED'); }
  let i = 0;
  const space = () => { while (i < text.length && /[\t\r\n ]/.test(text[i])) i++; };
  const string = () => {
    const start = i++;
    requireThat(text[start] === '"');
    while (i < text.length) {
      if (text[i] === '\\') { i += 2; continue; }
      if (text[i++] === '"') {
        try { return JSON.parse(text.slice(start, i)); }
        catch { throw new RetentionError('MALFORMED'); }
      }
    }
    throw new RetentionError('MALFORMED');
  };
  const value = depth => {
    requireThat(depth <= 128); space();
    if (text[i] === '"') { string(); return; }
    if (text[i] === '{') {
      i++; space(); const seen = new Set();
      if (text[i] === '}') { i++; return; }
      while (true) {
        space(); const key = string(); requireThat(!seen.has(key)); seen.add(key);
        space(); requireThat(text[i++] === ':'); value(depth + 1); space();
        if (text[i] === '}') { i++; return; }
        requireThat(text[i++] === ',');
      }
    }
    if (text[i] === '[') {
      i++; space(); if (text[i] === ']') { i++; return; }
      while (true) {
        value(depth + 1); space(); if (text[i] === ']') { i++; return; }
        requireThat(text[i++] === ',');
      }
    }
    const token = /^(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/.exec(text.slice(i));
    requireThat(token !== null); i += token[0].length;
  };
  try {
    value(0); space(); requireThat(i === text.length);
    return JSON.parse(text);
  } catch (error) {
    if (error instanceof RetentionError) throw error;
    throw new RetentionError('MALFORMED');
  }
}

function validateDocuments(plan, inventory, snapshot, planSha256) {
  requireThat(object(snapshot) && snapshot.status === 'READY' && nonempty(snapshot.id)
    && digest(snapshot.metadata_sha256) && Array.isArray(snapshot.entries));
  requireThat(object(plan) && plan.schema === 'atlas-retention-plan/1' && plan.version === 1);
  requireThat(plan.status === 'PROPOSAL_ONLY' && plan.DELETE_AUTHORIZED === 'NO'
    && Array.isArray(plan.items) && Array.isArray(plan.selection));
  const source = {};
  for (const key of ['id', 'name', 'revision', 'metadata_sha256']) if (own(snapshot, key)) source[key] = snapshot[key];
  requireThat(isDeepStrictEqual(plan.source, source) && plan.snapshot_key === snapshotKey(snapshot),
    'STALE_SNAPSHOT_OR_REVISION');
  const byUid = new Map();
  for (const entry of snapshot.entries) {
    requireThat(object(entry) && nonempty(entry.uid) && nonempty(entry.kind)
      && typeof entry.raw_json === 'string' && Array.isArray(entry.fields));
    requireThat(!byUid.has(entry.uid), 'CONTRADICTORY_IDENTITY_OR_INTENT');
    parseJsonStrict(Buffer.from(entry.raw_json, 'utf8'));
    byUid.set(entry.uid, entry);
  }
  requireThat(plan.items.length === plan.selection.length && plan.items.length > 0,
    'CONTRADICTORY_IDENTITY_OR_INTENT');
  const entries = [], seen = new Set(), intents = new Map(), annotations = new Map();
  for (const [index, item] of plan.items.entries()) {
    requireThat(object(item) && object(item.identity)
      && isDeepStrictEqual(item.identity, plan.selection[index]), 'CONTRADICTORY_IDENTITY_OR_INTENT');
    const entry = byUid.get(item.identity.uid);
    requireThat(entry && !seen.has(entry.uid) && RETENTION_INTENTS.includes(item.intent),
      'CONTRADICTORY_IDENTITY_OR_INTENT');
    const key = selectionKey(snapshot, entry);
    requireThat(item.identity.selection_key === key, 'CONTRADICTORY_IDENTITY_OR_INTENT');
    seen.add(entry.uid); entries.push(entry); intents.set(key, item.intent);
    if (object(item.baseline) && own(item.baseline, 'annotation')) annotations.set(key, item.baseline.annotation);
  }
  let canonical;
  try { canonical = buildRetentionPlan(snapshot, entries, {intents, annotations}); }
  catch { throw new RetentionError('CONTRADICTORY_IDENTITY_OR_INTENT'); }
  // The exporter intentionally uses null-prototype maps internally. Compare its
  // actual JSON transport, not JavaScript object prototypes lost on export.
  // Scientific values remain inside unchanged raw_json strings throughout.
  requireThat(isDeepStrictEqual(plan, JSON.parse(JSON.stringify(canonical))), 'CONTRADICTORY_IDENTITY_OR_INTENT');

  exactKeys(inventory, ['schema', 'version', 'contract', 'source', 'snapshot_key', 'plan_sha256',
    'inventory_integrity', 'validation_status', 'evidence_scope', 'delta_provenance', 'bindings', 'files']);
  requireThat(inventory.schema === 'atlas-retention-inventory/1' && inventory.version === 1
    && inventory.contract === 'ATLAS_N01_R_N02_SANITIZED/1');
  requireThat(isDeepStrictEqual(inventory.source, source) && inventory.snapshot_key === plan.snapshot_key,
    'STALE_SNAPSHOT_OR_REVISION');
  requireThat(digest(inventory.plan_sha256) && inventory.plan_sha256 === planSha256,
    'CONTRADICTORY_IDENTITY_OR_INTENT');
  exactKeys(inventory.inventory_integrity, ['status', 'scope']);
  requireThat(inventory.inventory_integrity.status === 'VERIFIED'
    && inventory.inventory_integrity.scope === 'OBSERVED_SUBSET_INTEGRITY', 'INVENTORY_INTEGRITY_UNVERIFIED');
  requireThat(STATES.includes(inventory.validation_status)
    && ['SCOPED_READ_ONLY', 'HISTORICAL_SCOPED'].includes(inventory.evidence_scope));
  exactKeys(inventory.delta_provenance, ['origin', 'base_inventory_sha256', 'receipt_sha256']);
  requireThat(inventory.delta_provenance.origin === 'N01_R_READ_ONLY'
    && digest(inventory.delta_provenance.base_inventory_sha256) && digest(inventory.delta_provenance.receipt_sha256));
  requireThat(Array.isArray(inventory.files) && Array.isArray(inventory.bindings)
    && inventory.bindings.length === plan.items.length);
  const files = new Map();
  for (const file of inventory.files) {
    exactKeys(file, ['id', 'sha256', 'size_bytes', 'category', 'consumers', 'shared', 'backup_status']);
    requireThat(typeof file.id === 'string' && ID.test(file.id));
    requireThat(!files.has(file.id), 'FILE_IDENTITY_AMBIGUOUS');
    requireThat((file.sha256 === null || digest(file.sha256)) && Number.isSafeInteger(file.size_bytes)
      && file.size_bytes >= 0 && CATEGORIES.includes(file.category) && BACKUP.includes(file.backup_status)
      && [true, false, 'UNKNOWN'].includes(file.shared)
      && Array.isArray(file.consumers) && file.consumers.every(nonempty)
      && new Set(file.consumers).size === file.consumers.length);
    requireThat(!(file.shared === false && (file.consumers.length > 1 || file.category === 'SHARED_ARTIFACT')),
      'CONTRADICTORY_IDENTITY_OR_INTENT');
    files.set(file.id, file);
  }
  for (const [index, binding] of inventory.bindings.entries()) {
    exactKeys(binding, ['identity', 'type', 'intent', 'file_ids', 'validation_status', 'evidence_scope',
      'dependency_status', 'backup_status']);
    const item = plan.items[index];
    requireThat(isDeepStrictEqual(binding.identity, item.identity) && binding.type === item.type
      && binding.intent === item.intent, 'CONTRADICTORY_IDENTITY_OR_INTENT');
    requireThat(STATES.includes(binding.validation_status) && STATES.includes(binding.dependency_status)
      && SCOPES.includes(binding.evidence_scope) && BACKUP.includes(binding.backup_status)
      && Array.isArray(binding.file_ids) && new Set(binding.file_ids).size === binding.file_ids.length);
    for (const id of binding.file_ids) {
      requireThat(files.has(id) && files.get(id).consumers.includes(item.identity.selection_key),
        'CONTRADICTORY_IDENTITY_OR_INTENT');
    }
    requireThat(binding.file_ids.length > 0 || binding.validation_status !== 'VERIFIED',
      'CONTRADICTORY_IDENTITY_OR_INTENT');
  }
  return files;
}

function normalized(value) { return process.platform === 'win32' ? value.toLowerCase() : value; }
function sameStat(a, b) {
  return ['dev', 'ino', 'mode', 'nlink', 'size', 'mtimeNs', 'ctimeNs'].every(key => a[key] === b[key]);
}
function sameObject(a, b) { return a.dev === b.dev && a.ino === b.ino && a.mode === b.mode; }
function childOf(root, target) {
  const relative = path.relative(root, target);
  return relative !== '' && relative !== '..' && !relative.startsWith('..' + path.sep) && !path.isAbsolute(relative);
}

/** Every existing ancestor is checked. Windows junctions are symbolic links to lstat.
 * Portable metadata checks narrow races; they do not claim an adversarial OS lock.
 */
async function inspectedPath(candidate, {directory = false} = {}) {
  const absolute = path.resolve(candidate), parsed = path.parse(absolute);
  requireThat(path.isAbsolute(candidate) && !/^[/\\]{2}/.test(candidate), 'UNSAFE_PATH');
  const segments = absolute.slice(parsed.root.length).split(path.sep).filter(Boolean);
  let current = parsed.root;
  const nodes = [];
  for (const [index, segment] of segments.entries()) {
    current = path.join(current, segment);
    const info = await lstat(current, {bigint: true});
    requireThat(!info.isSymbolicLink(), 'EXTERNAL_LINK');
    const isLast = index === segments.length - 1;
    requireThat(isLast && !directory ? info.isFile() : info.isDirectory(), 'UNSAFE_PATH');
    if (isLast && !directory) requireThat(info.nlink === 1n, 'FILE_IDENTITY_AMBIGUOUS');
    nodes.push({path: current, stat: info});
  }
  requireThat(nodes.length > 0, 'UNSAFE_PATH');
  const canonical = await realpath(absolute);
  requireThat(normalized(canonical) === normalized(absolute), 'EXTERNAL_LINK');
  return {absolute, canonical, nodes, stat: nodes.at(-1).stat};
}
function sameChain(before, after) {
  return before.nodes.length === after.nodes.length && before.nodes.every((node, index) =>
    normalized(node.path) === normalized(after.nodes[index].path) && sameObject(node.stat, after.nodes[index].stat));
}
function relativePath(value) {
  requireThat(nonempty(value) && !/[\\:%\x00-\x1f\x7f<>"|?*]/.test(value)
    && !path.posix.isAbsolute(value) && !path.win32.isAbsolute(value), 'UNSAFE_PATH');
  const parts = value.split('/');
  requireThat(parts.every(part => part && part !== '.' && part !== '..' && !/[. ]$/.test(part)
    && !/^(?:con|prn|aux|nul|com[0-9¹²³]|lpt[0-9¹²³])(?:\.|$)/i.test(part)), 'UNSAFE_PATH');
  return parts;
}

async function readStable(candidate, {collect = false, expected = null, root = null} = {}) {
  let handle;
  try {
    const before = await inspectedPath(candidate);
    if (root) requireThat(childOf(root.canonical, before.canonical), 'UNSAFE_PATH');
    if (collect) requireThat(before.stat.size <= BigInt(MAX_DOCUMENT_BYTES));
    if (expected) requireThat(before.stat.size === BigInt(expected.size_bytes), 'FILE_SUBSTITUTED');
    handle = await open(before.absolute, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0) | (constants.O_NONBLOCK ?? 0));
    const opened = await handle.stat({bigint: true});
    requireThat(opened.isFile() && opened.nlink === 1n && sameStat(before.stat, opened), 'FILE_SUBSTITUTED');
    const afterOpen = await inspectedPath(candidate);
    requireThat(sameChain(before, afterOpen) && sameStat(opened, afterOpen.stat), 'FILE_SUBSTITUTED');
    if (root) {
      const currentRoot = await inspectedPath(root.absolute, {directory: true});
      requireThat(sameChain(root, currentRoot), 'FILE_SUBSTITUTED');
    }
    // Do not read any bytes until the descriptor and every path component agree.
    const digester = createHash('sha256'), chunks = [], buffer = Buffer.alloc(64 * 1024);
    let total = 0;
    while (true) {
      const {bytesRead} = await handle.read(buffer, 0, buffer.length, null);
      if (!bytesRead) break;
      total += bytesRead;
      requireThat(BigInt(total) <= opened.size, 'FILE_SUBSTITUTED');
      const chunk = buffer.subarray(0, bytesRead); digester.update(chunk);
      if (collect) chunks.push(Buffer.from(chunk));
    }
    const finished = await handle.stat({bigint: true}), after = await inspectedPath(candidate);
    requireThat(BigInt(total) === opened.size && sameStat(opened, finished)
      && sameStat(finished, after.stat) && sameChain(before, after), 'FILE_SUBSTITUTED');
    const sha256 = digester.digest('hex');
    if (expected) requireThat(sha256 === expected.sha256, 'FILE_SUBSTITUTED');
    return {bytes: collect ? Buffer.concat(chunks) : undefined, sha256,
      size_bytes: total, physical_id: `${opened.dev}:${opened.ino}`};
  } catch (error) {
    if (error instanceof RetentionError) throw error;
    if (error.code === 'ELOOP') throw new RetentionError('EXTERNAL_LINK');
    throw new RetentionError('INPUT_UNREADABLE');
  } finally { if (handle) await handle.close(); }
}

async function authorizedMappings(roots, bindings, inventoryFiles) {
  requireThat(object(roots) && object(bindings), 'UNSAFE_PATH');
  const rootMap = new Map(), fileMap = new Map(), seenPaths = new Set();
  for (const [id, candidate] of Object.entries(roots)) {
    requireThat(ID.test(id) && typeof candidate === 'string', 'UNSAFE_PATH');
    try { rootMap.set(id, await inspectedPath(candidate, {directory: true})); }
    catch (error) {
      if (error instanceof RetentionError) throw error;
      throw new RetentionError('INPUT_UNREADABLE');
    }
  }
  for (const [id, binding] of Object.entries(bindings)) {
    requireThat(inventoryFiles.has(id), 'CONTRADICTORY_IDENTITY_OR_INTENT');
    exactKeys(binding, ['root_id', 'relative_path']);
    requireThat(rootMap.has(binding.root_id), 'UNSAFE_PATH');
    const root = rootMap.get(binding.root_id), parts = relativePath(binding.relative_path);
    const candidate = path.join(root.absolute, ...parts);
    requireThat(childOf(root.absolute, candidate), 'UNSAFE_PATH');
    const token = normalized(candidate);
    requireThat(!seenPaths.has(token), 'FILE_IDENTITY_AMBIGUOUS'); seenPaths.add(token);
    fileMap.set(id, {root, candidate});
  }
  return fileMap;
}

export async function auditRetention({planBytes, inventoryBytes, snapshotBytes,
  expectedInventorySha256, expectedSnapshotSha256, roots = {}, files = {}}) {
  requireThat(Buffer.isBuffer(planBytes) && Buffer.isBuffer(inventoryBytes) && Buffer.isBuffer(snapshotBytes));
  requireThat(digest(expectedInventorySha256) && hash(inventoryBytes) === expectedInventorySha256,
    'INVENTORY_INTEGRITY_UNVERIFIED');
  requireThat(digest(expectedSnapshotSha256) && hash(snapshotBytes) === expectedSnapshotSha256,
    'STALE_SNAPSHOT_OR_REVISION');
  const plan = parseJsonStrict(planBytes), inventory = parseJsonStrict(inventoryBytes), snapshot = parseJsonStrict(snapshotBytes);
  const planDigest = hash(planBytes), inventoryFiles = validateDocuments(plan, inventory, snapshot, planDigest);
  const mappings = await authorizedMappings(roots, files, inventoryFiles);
  const selectedFiles = new Set(inventory.bindings.flatMap(binding => binding.file_ids));
  const verified = new Map(), physical = new Set();
  for (const id of selectedFiles) {
    const file = inventoryFiles.get(id), mapping = mappings.get(id);
    if (!mapping || file.sha256 === null) {
      verified.set(id, {id, status: 'NOT_VERIFIED', reason: !mapping ? 'LOCAL_BINDING_MISSING' : 'SELECTIVE_DIGEST_MISSING'});
      continue;
    }
    const checked = await readStable(mapping.candidate, {expected: file, root: mapping.root});
    requireThat(!physical.has(checked.physical_id), 'FILE_IDENTITY_AMBIGUOUS'); physical.add(checked.physical_id);
    verified.set(id, {id, status: 'VERIFIED_CURRENT_READ', sha256: checked.sha256, size_bytes: checked.size_bytes});
  }
  const items = plan.items.map((item, index) => {
    const binding = inventory.bindings[index], reasons = new Set(item.protection.reasons);
    reasons.add('BACKUP_NOT_PROVEN'); reasons.add('FULL_DEPENDENCY_CLOSURE_NOT_ATTESTED');
    if (!binding.file_ids.length || binding.file_ids.some(id => verified.get(id).status !== 'VERIFIED_CURRENT_READ'))
      reasons.add('PHYSICAL_BINDING_INCOMPLETE');
    if (binding.validation_status !== 'VERIFIED' || inventory.validation_status !== 'VERIFIED') reasons.add('N01_R_PARTIAL_EVIDENCE');
    if (binding.dependency_status !== 'VERIFIED') reasons.add('DEPENDENCIES_UNRESOLVED');
    if (binding.file_ids.some(id => {
      const file = inventoryFiles.get(id);
      return file.shared !== false || file.category === 'SHARED_ARTIFACT' || file.consumers.length > 1;
    })) reasons.add('SHARED_OR_UNKNOWN_DEPENDENCY');
    return {identity: item.identity, type: item.type, intent: item.intent,
      validation_status: binding.validation_status, evidence_scope: binding.evidence_scope,
      protection: {status: 'PROTECTED', removal_authorized: false, reasons: [...reasons]},
      file_ids: [...binding.file_ids]};
  });
  return {schema: 'atlas-retention-review/1', status: 'PROPOSAL_ONLY', DELETE_AUTHORIZED: 'NO',
    removal_authorized: false, runtime_import: 'VERIFIED_SCOPED', validation_status: 'PARTIAL',
    recoverable_space: 'RECOVERABLE_SPACE_UNKNOWN',
    input_digests: {plan_sha256: planDigest, inventory_sha256: expectedInventorySha256, snapshot_sha256: expectedSnapshotSha256},
    inventory_integrity: {...inventory.inventory_integrity}, evidence_scope: inventory.evidence_scope,
    delta_provenance: {...inventory.delta_provenance},
    file_verification: [...verified.values()], items,
    pending_verifications: ['FULL_DEPENDENCY_CLOSURE', 'BACKUP_COVERAGE_AND_RESTORE',
      'MARGINAL_PHYSICAL_RELEASE', 'HUMAN_BATCH_AUTHORIZATION'],
    provenance: {mode: 'OFFLINE_READ_ONLY_REVIEW', source_read_only: true,
      scientific_acceptance: 'NOT_ASSERTED', inventory_integrity_is_authenticity: false,
      physical_scope: 'ONLY_EXPLICITLY_BOUND_SELECTED_FILES', source_file_bytes_in_report: false}};
}

const HELP = `Atlas N02 — revisão offline somente leitura\n\nnode tools/atlas_retention_audit.mjs --plan FILE --inventory FILE --inventory-sha256 HASH\n  --snapshot FILE --snapshot-sha256 HASH [--root ID=ABS_DIR] [--file ID=ROOT:relative/path]\n\nstdout: parecer JSON. Exit 0: importação protegida. Exit 2: recusa. Nenhuma exclusão ou escrita.\n`;

export async function main(argv = process.argv.slice(2)) {
  if (argv.length === 1 && argv[0] === '--help') { process.stdout.write(HELP); return 0; }
  try {
    const args = Object.create(null), roots = Object.create(null), files = Object.create(null);
    const single = ['--plan', '--inventory', '--inventory-sha256', '--snapshot', '--snapshot-sha256'];
    for (let i = 0; i < argv.length; i += 2) {
      const flag = argv[i], value = argv[i + 1];
      requireThat(nonempty(value) && !value.startsWith('--'));
      if (single.includes(flag)) { requireThat(!own(args, flag)); args[flag] = value; }
      else if (flag === '--root' || flag === '--file') {
        const split = value.indexOf('='), id = value.slice(0, split), rest = value.slice(split + 1);
        requireThat(split > 0 && ID.test(id) && nonempty(rest));
        if (flag === '--root') { requireThat(!own(roots, id)); roots[id] = rest; }
        else {
          const colon = rest.indexOf(':'); requireThat(colon > 0 && !own(files, id));
          files[id] = {root_id: rest.slice(0, colon), relative_path: rest.slice(colon + 1)};
        }
      } else throw new RetentionError('MALFORMED');
    }
    requireThat(single.every(flag => own(args, flag)));
    const plan = await readStable(path.resolve(args['--plan']), {collect: true});
    const inventory = await readStable(path.resolve(args['--inventory']), {collect: true});
    const snapshot = await readStable(path.resolve(args['--snapshot']), {collect: true});
    const report = await auditRetention({planBytes: plan.bytes, inventoryBytes: inventory.bytes, snapshotBytes: snapshot.bytes,
      expectedInventorySha256: args['--inventory-sha256'], expectedSnapshotSha256: args['--snapshot-sha256'], roots, files});
    process.stdout.write(JSON.stringify(report, null, 2) + '\n'); return 0;
  } catch (error) {
    const code = error instanceof RetentionError ? error.code : 'MALFORMED';
    process.stdout.write(JSON.stringify({schema: 'atlas-retention-review/1', status: 'REJECTED',
      DELETE_AUTHORIZED: 'NO', removal_authorized: false, error: {code}}) + '\n'); return 2;
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) process.exitCode = await main();
