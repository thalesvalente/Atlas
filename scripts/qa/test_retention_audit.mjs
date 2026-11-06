/** N02 contract, adversarial inputs and read-only filesystem boundaries.
 * Every document/file is invented. This suite performs no cleanup or deletion.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdir, writeFile, symlink, link, realpath} from 'node:fs/promises';
import {spawnSync} from 'node:child_process';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {auditRetention, RetentionError} from '../../tools/atlas_retention_audit.mjs';
import {makeFixture, encodeFixture, materializeCorpus, fixtureTree, jsonBytes, sha256} from './retention_audit_fixture.mjs';

const CLI = fileURLToPath(new URL('../../tools/atlas_retention_audit.mjs', import.meta.url));
const CONTRADICTION = 'CONTRADICTORY_IDENTITY_OR_INTENT';

async function rejected(options, expected, label = 'contract rejection') {
  const codes = Array.isArray(expected) ? expected : [expected];
  await assert.rejects(() => auditRetention(options), error => {
    assert(error instanceof RetentionError, `${label}: typed RetentionError required, got ${error?.constructor?.name}`);
    assert(codes.includes(error.code), `${label}: ${error.code} not in ${codes.join(', ')}`);
    return true;
  });
}

function assertProtected(report, fixture) {
  assert.equal(report.schema, 'atlas-retention-review/1');
  assert.equal(report.status, 'PROPOSAL_ONLY');
  assert.equal(report.runtime_import, 'VERIFIED_SCOPED');
  assert.equal(report.validation_status, 'PARTIAL');
  assert.equal(report.DELETE_AUTHORIZED, 'NO');
  assert.equal(report.removal_authorized, false);
  assert.equal(report.recoverable_space, 'RECOVERABLE_SPACE_UNKNOWN');
  assert.deepEqual(report.items.map(item => item.identity), fixture.plan.items.map(item => item.identity));
  assert.deepEqual(report.items.map(item => item.intent), fixture.plan.items.map(item => item.intent));
  assert.deepEqual(report.items.map(item => item.type), fixture.plan.items.map(item => item.type));
  for (const item of report.items) {
    assert.equal(item.protection.status, 'PROTECTED');
    assert.equal(item.protection.removal_authorized, false);
    assert(item.protection.reasons.length > 0);
  }
}

/** Re-anchor deliberately altered bytes, so semantics, not hash mismatch, is tested. */
function rawInput(options, name, bytes) {
  const result = {...options, [name]: bytes};
  if (name === 'snapshotBytes') result.expectedSnapshotSha256 = sha256(bytes);
  if (name === 'inventoryBytes') result.expectedInventorySha256 = sha256(bytes);
  if (name === 'planBytes') {
    const inventory = JSON.parse(options.inventoryBytes);
    inventory.plan_sha256 = sha256(bytes);
    result.inventoryBytes = jsonBytes(inventory);
    result.expectedInventorySha256 = sha256(result.inventoryBytes);
  }
  return result;
}

async function withCorpus(fixture, exercise) {
  const corpus = await materializeCorpus(fixture);
  await exercise(corpus);
}

test('N02 imports the real F005 export without requiring private files', async () => {
  const fixture = makeFixture(), options = encodeFixture(fixture);
  const before = [options.planBytes, options.inventoryBytes, options.snapshotBytes].map(sha256);
  const report = await auditRetention(options);
  assertProtected(report, fixture);
  assert.equal(report.file_verification.length, 2);
  assert(report.file_verification.every(file => file.status === 'NOT_VERIFIED' && file.reason === 'LOCAL_BINDING_MISSING'));
  assert.deepEqual([options.planBytes, options.inventoryBytes, options.snapshotBytes].map(sha256), before);
});

test('lexical record kind, large numbers, decimal and full table rows survive import', async () => {
  const fixture = makeFixture();
  assert(fixture.plan.items[1].identity.selection_key.includes('r\\\\u0075n'));
  assert(fixture.plan.items[0].raw_json.includes('9007199254740993'));
  assert(fixture.plan.items[0].raw_json.includes('0.123456789012345678901'));
  assert.equal(fixture.plan.items[2].table_rows.rows.length, 2);
  const original = jsonBytes(fixture.plan);
  assertProtected(await auditRetention(encodeFixture(fixture)), fixture);
  assert.deepEqual(jsonBytes(fixture.plan), original);
});

test('JSON transport and object-key order do not invalidate the canonical F005 export', async () => {
  const fixture = makeFixture();
  assert.equal(Object.getPrototypeOf(fixture.plan.items[0].declared), null);
  const reverseKeys = value => Array.isArray(value) ? value.map(reverseKeys) : value && typeof value === 'object'
    ? Object.fromEntries(Object.entries(value).reverse().map(([key, child]) => [key, reverseKeys(child)])) : value;
  fixture.plan = reverseKeys(JSON.parse(jsonBytes(fixture.plan)));
  fixture.snapshot = reverseKeys(fixture.snapshot);
  fixture.inventory = reverseKeys(fixture.inventory);
  assertProtected(await auditRetention(encodeFixture(fixture, {rebindPlan: true})), fixture);
});

test('missing and NULL revisions each work and remain distinct identities', async () => {
  const missing = makeFixture({omitRevision: true}), nullRevision = makeFixture({revision: null});
  assert.notEqual(missing.plan.snapshot_key, nullRevision.plan.snapshot_key);
  assertProtected(await auditRetention(encodeFixture(missing)), missing);
  assertProtected(await auditRetention(encodeFixture(nullRevision)), nullRevision);
  missing.snapshot.revision = null;
  await rejected(encodeFixture(missing), 'STALE_SNAPSHOT_OR_REVISION');
});

test('valid operator annotation and all permitted intentions remain protected proposals', async () => {
  for (const intent of ['KEEP_FULL', 'KEEP_ESSENTIALS', 'REVIEW_FOR_REMOVAL', 'UNDECIDED']) {
    const fixture = makeFixture({intent, annotate: true});
    assert.equal(fixture.plan.items[1].baseline.annotation.origin, 'OPERATOR_SESSION');
    assertProtected(await auditRetention(encodeFixture(fixture)), fixture);
  }
});

test('external inventory and snapshot digest anchors are mandatory', async () => {
  for (const anchor of ['expectedInventorySha256', 'expectedSnapshotSha256']) {
    for (const value of [undefined, '', 'f'.repeat(64), 'A'.repeat(64)]) {
      const options = encodeFixture(makeFixture()); options[anchor] = value;
      await rejected(options, ['INVENTORY_INTEGRITY_UNVERIFIED', 'STALE_SNAPSHOT_OR_REVISION', 'MALFORMED'], anchor);
    }
  }
});

test('self-declared inventory integrity cannot compensate for altered bytes or plan digest', async () => {
  const fixture = makeFixture(), options = encodeFixture(fixture);
  const changed = structuredClone(fixture.inventory); changed.validation_status = 'VERIFIED';
  await rejected({...options, inventoryBytes: jsonBytes(changed)}, 'INVENTORY_INTEGRITY_UNVERIFIED');
  fixture.inventory.plan_sha256 = '0'.repeat(64);
  await rejected(encodeFixture(fixture), CONTRADICTION);
});

test('stale source id, revision, metadata digest and snapshot key are rejected', async () => {
  for (const [field, value] of [['id', 'other-source'], ['revision', 'OTHER-REVISION'], ['metadata_sha256', 'f'.repeat(64)]]) {
    const fixture = makeFixture(); fixture.snapshot[field] = value;
    await rejected(encodeFixture(fixture), 'STALE_SNAPSHOT_OR_REVISION', field);
  }
  const fixture = makeFixture(); fixture.plan.snapshot_key = 'stale-snapshot';
  await rejected(encodeFixture(fixture, {rebindPlan: true}), ['STALE_SNAPSHOT_OR_REVISION', CONTRADICTION]);
});

test('source readiness and snapshot UID ambiguity fail closed', async () => {
  const fixture = makeFixture(); fixture.snapshot.status = 'CHANGED';
  await rejected(encodeFixture(fixture), ['STALE_SNAPSHOT_OR_REVISION', 'MALFORMED']);
  const duplicate = makeFixture(); duplicate.snapshot.entries.push(structuredClone(duplicate.snapshot.entries[0]));
  await rejected(encodeFixture(duplicate), [CONTRADICTION, 'MALFORMED']);
});

test('malformed UTF-8, invalid JSON and non-object documents are rejected', async () => {
  for (const name of ['planBytes', 'snapshotBytes', 'inventoryBytes']) {
    for (const bytes of [Buffer.from('{'), Buffer.from('null'), Buffer.from('[]'), Buffer.from([0x7b, 0x22, 0x78, 0x22, 0x3a, 0x22, 0xff, 0x22, 0x7d])]) {
      await rejected(rawInput(encodeFixture(makeFixture()), name, bytes), 'MALFORMED', name);
    }
  }
});

test('duplicate JSON keys are rejected even when anchors match the duplicate bytes', async () => {
  for (const name of ['planBytes', 'snapshotBytes', 'inventoryBytes']) {
    const options = encodeFixture(makeFixture()), original = options[name].toString('utf8');
    const key = name === 'snapshotBytes' ? 'id' : 'schema';
    const bytes = Buffer.from(`{"${key}":"duplicate",${original.slice(1)}`);
    await rejected(rawInput(options, name, bytes), 'MALFORMED', name);
  }
});

test('duplicates hidden in scientific raw JSON are not accepted as unambiguous identity', async () => {
  const fixture = makeFixture();
  fixture.snapshot.entries[0].raw_json = fixture.snapshot.entries[0].raw_json.replace('"kind":"run"', '"kind":"run","kind":"run"');
  await rejected(encodeFixture(fixture), ['MALFORMED', CONTRADICTION]);
});

test('UID, selection key, original lexical identity and type contradictions are rejected', async () => {
  const mutations = [
    f => { f.plan.items[0].identity.uid = 'wrong-uid'; },
    f => { f.plan.items[0].identity.selection_key = 'forged-key'; },
    f => { f.plan.items[0].identity.original_id.raw_json = '"forged"'; },
    f => { f.plan.items[0].identity.dto_kind = 'table'; },
    f => { f.plan.items[0].type = 'table'; },
    f => { f.plan.selection.reverse(); },
  ];
  for (const mutate of mutations) {
    const fixture = makeFixture(); mutate(fixture);
    await rejected(encodeFixture(fixture, {rebindPlan: true}), CONTRADICTION);
  }
});

test('altered lexical content, missing table rows and swapped row order are rejected', async () => {
  const mutations = [
    f => { f.plan.items[0].raw_json = f.plan.items[0].raw_json.replace('9007199254740993', '9007199254740992'); },
    f => { f.plan.items[2].table_rows.rows.pop(); },
    f => { f.plan.items[2].table_rows.rows.reverse(); },
  ];
  for (const mutate of mutations) {
    const fixture = makeFixture(); mutate(fixture);
    await rejected(encodeFixture(fixture, {rebindPlan: true}), CONTRADICTION);
  }
});

test('plan status, schema version, provenance and deletion flags cannot be promoted', async () => {
  const mutations = [
    f => { f.plan.status = 'APPROVED'; }, f => { f.plan.DELETE_AUTHORIZED = 'YES'; },
    f => { f.plan.schema = 'atlas-retention-plan/2'; }, f => { f.plan.version = 2; },
    f => { f.plan.provenance.source_read_only = false; },
    f => { f.plan.provenance.physical_presence_verified = true; },
    f => { f.plan.provenance.operator_intentions_are_commands = true; },
    f => { f.plan.items[0].protection.removal_authorized = true; },
  ];
  for (const mutate of mutations) {
    const fixture = makeFixture(); mutate(fixture);
    await rejected(encodeFixture(fixture, {rebindPlan: true}), ['MALFORMED', CONTRADICTION]);
  }
});

test('contradictory or executable intentions in plan and binding are rejected', async () => {
  for (const intent of ['KEEP_ESSENTIALS', 'DELETE', 'rm -rf', null]) {
    const fixture = makeFixture(); fixture.inventory.bindings[0].intent = intent;
    await rejected(encodeFixture(fixture), [CONTRADICTION, 'MALFORMED']);
  }
  const fixture = makeFixture(); fixture.plan.items[0].intent = 'DELETE';
  await rejected(encodeFixture(fixture, {rebindPlan: true}), [CONTRADICTION, 'MALFORMED']);
});

test('inventory row order, identity, duplicate file IDs and unresolved references are validated', async () => {
  const mutations = [
    [f => { f.inventory.bindings.reverse(); }, CONTRADICTION],
    [f => { f.inventory.bindings[0].identity.uid = 'wrong-uid'; }, CONTRADICTION],
    [f => { f.inventory.files.push(structuredClone(f.inventory.files[0])); }, 'FILE_IDENTITY_AMBIGUOUS'],
    [f => { f.inventory.bindings[0].file_ids = ['nonexistent']; }, CONTRADICTION],
    [f => { f.inventory.files[0].consumers = []; }, CONTRADICTION],
    [f => { f.inventory.bindings.push(structuredClone(f.inventory.bindings[0])); }, 'MALFORMED'],
  ];
  for (const [mutate, code] of mutations) {
    const fixture = makeFixture(); mutate(fixture);
    await rejected(encodeFixture(fixture), code);
  }
});

test('a file with multiple consumers cannot declare shared false', async () => {
  const fixture = makeFixture();
  fixture.inventory.files[0].shared = false;
  fixture.inventory.files[0].category = 'EXCLUSIVE_ARTIFACT';
  assert.equal(fixture.inventory.files[0].consumers.length, 2);
  await rejected(encodeFixture(fixture), CONTRADICTION);
});

test('SHARED_ARTIFACT cannot declare shared false even with only one consumer', async () => {
  const fixture = makeFixture();
  fixture.inventory.files[0].shared = false;
  fixture.inventory.files[0].consumers = [fixture.plan.items[0].identity.selection_key];
  fixture.inventory.bindings[1].file_ids = [];
  assert.equal(fixture.inventory.files[0].category, 'SHARED_ARTIFACT');
  await rejected(encodeFixture(fixture), CONTRADICTION);
});

test('unknown inventory fields and forged integrity or backup claims are rejected', async () => {
  const mutations = [
    f => { f.inventory.path = '/not-an-authorized-root'; },
    f => { f.inventory.files[0].url = 'https://example.invalid/never-open'; },
    f => { f.inventory.files[0].path = '../outside'; },
    f => { f.inventory.inventory_integrity.status = 'DECLARED'; },
    f => { f.inventory.files[0].backup_status = 'VERIFIED'; },
    f => { delete f.inventory.delta_provenance.receipt_sha256; },
  ];
  for (const mutate of mutations) {
    const fixture = makeFixture(); mutate(fixture);
    await rejected(encodeFixture(fixture), ['MALFORMED', 'INVENTORY_INTEGRITY_UNVERIFIED']);
  }
});

test('unresolved bindings stay partial without inventing files or physical presence', async () => {
  const fixture = makeFixture(); fixture.inventory.bindings[0].file_ids = [];
  fixture.inventory.bindings[0].validation_status = 'UNRESOLVED';
  const report = await auditRetention(encodeFixture(fixture));
  assertProtected(report, fixture);
  assert.deepEqual(report.items[0].file_ids, []);
  assert.equal(report.items[0].validation_status, 'UNRESOLVED');
});

test('synthetic temporary roots use canonical paths before explicit authorization', async t => {
  const fixture = makeFixture(), corpus = await materializeCorpus(fixture);
  t.diagnostic(JSON.stringify({platform: process.platform,
    allocated_base: corpus.allocatedBase, canonical_base: corpus.base}));
  assert.equal(corpus.base, await realpath(corpus.allocatedBase));
  assert.equal(corpus.corpus, await realpath(corpus.corpus));
  const before = await fixtureTree(corpus.base);
  const report = await auditRetention({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files});
  assertProtected(report, fixture);
  assert(report.file_verification.every(file => file.status === 'VERIFIED_CURRENT_READ'));
  const allocatedRoot = path.join(corpus.allocatedBase, 'corpus');
  const folded = value => process.platform === 'win32' ? value.toLowerCase() : value;
  if (folded(allocatedRoot) !== folded(corpus.corpus)) {
    await rejected({...encodeFixture(fixture), roots: {corpus: allocatedRoot}, files: corpus.files}, 'EXTERNAL_LINK');
  }
  assert.deepEqual(await fixtureTree(corpus.base), before);
});

test('shared consumers and declared backups retain protection after verified reads', async () => {
  const fixture = makeFixture();
  for (const file of fixture.inventory.files) file.backup_status = 'DECLARED';
  for (const binding of fixture.inventory.bindings) binding.backup_status = 'DECLARED';
  await withCorpus(fixture, async corpus => {
    const before = await fixtureTree(corpus.base);
    const report = await auditRetention({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files});
    assertProtected(report, fixture);
    assert(report.file_verification.every(file => file.status === 'VERIFIED_CURRENT_READ'));
    assert(report.items[0].protection.reasons.some(reason => /SHARED|CONSUMER/.test(reason)));
    assert(report.items.every(item => item.protection.reasons.some(reason => /BACKUP/.test(reason))));
    assert(!JSON.stringify(report).includes(corpus.corpus));
    assert(!JSON.stringify(report).includes('SYNTHETIC_SHARED_ARTIFACT_BYTES'));
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('missing selective digest never causes a physical read or a fabricated PASS', async () => {
  const fixture = makeFixture(); fixture.inventory.files[0].sha256 = null;
  await withCorpus(fixture, async corpus => {
    corpus.files.shared01.relative_path = 'not-present-without-hash.bin';
    const before = await fixtureTree(corpus.base);
    const report = await auditRetention({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files});
    assertProtected(report, fixture);
    assert.deepEqual(report.file_verification.find(file => file.id === 'shared01'),
      {id: 'shared01', status: 'NOT_VERIFIED', reason: 'SELECTIVE_DIGEST_MISSING'});
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('unselected files remain unopened even when their authorized locator does not exist', async () => {
  const fixture = makeFixture();
  fixture.inventory.files.push({id: 'unselected01', sha256: sha256('unselected'), size_bytes: 10,
    category: 'CACHE', consumers: ['opaque-unselected-consumer'], shared: 'UNKNOWN', backup_status: 'NOT_VERIFIED'});
  await withCorpus(fixture, async corpus => {
    corpus.files.unselected01 = {root_id: 'corpus', relative_path: 'never-created/unselected.bin'};
    const before = await fixtureTree(corpus.base);
    const report = await auditRetention({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files});
    assertProtected(report, fixture);
    assert(!report.file_verification.some(file => file.id === 'unselected01' && file.status === 'VERIFIED_CURRENT_READ'));
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('operator locators reject traversal, absolute, UNC, ADS, reserved and encoded paths', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    const before = await fixtureTree(corpus.base);
    const unsafe = ['../outside.bin', './data/shared01.bin', 'data//shared01.bin', '/tmp/outside.bin',
      '\\\\server\\share\\file', 'C:/outside.bin', 'data/file:stream', 'data\\shared01.bin',
      'https://example.invalid/file', 'data/%2e%2e/file', 'data/CON', 'data/NUL.txt',
      'data/COM¹.txt', 'data/COM²', 'data/COM³.bin', 'data/LPT¹.txt', 'data/LPT²', 'data/LPT³.bin',
      'data/file.', 'data/file ', 'data/file\u0000.bin'];
    for (const relative_path of unsafe) {
      const files = structuredClone(corpus.files); files.shared01.relative_path = relative_path;
      await rejected({...encodeFixture(fixture), roots: corpus.roots, files}, 'UNSAFE_PATH', JSON.stringify(relative_path));
    }
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('unknown file/root IDs and non-absolute roots have no fallback lookup', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    const before = await fixtureTree(corpus.base);
    const cases = [
      [{roots: {corpus: 'relative'}, files: corpus.files}, 'UNSAFE_PATH'],
      [{roots: corpus.roots, files: {...corpus.files, ghost: {root_id: 'corpus', relative_path: 'data/shared01.bin'}}}, CONTRADICTION],
      [{roots: corpus.roots, files: {...corpus.files, shared01: {root_id: 'unknown', relative_path: 'data/shared01.bin'}}}, 'UNSAFE_PATH'],
    ];
    for (const [maps, code] of cases) await rejected({...encodeFixture(fixture), ...maps}, code);
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('external directory symlink or Windows junction is refused before reading target bytes', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    const outside = path.join(corpus.base, 'outside'); await mkdir(outside);
    await writeFile(path.join(outside, 'secret.bin'), 'INVENTED_EXTERNAL_SENTINEL', {flag: 'wx'});
    await symlink(outside, path.join(corpus.corpus, 'portal'), process.platform === 'win32' ? 'junction' : 'dir');
    corpus.files.shared01.relative_path = 'portal/secret.bin';
    const before = await fixtureTree(corpus.base);
    await rejected({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files}, 'EXTERNAL_LINK');
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('root paths containing a symlink or junction cannot authorize corpus access', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    const alias = path.join(corpus.base, 'root-alias');
    await symlink(corpus.corpus, alias, process.platform === 'win32' ? 'junction' : 'dir');
    const before = await fixtureTree(corpus.base);
    await rejected({...encodeFixture(fixture), roots: {corpus: alias}, files: corpus.files}, 'EXTERNAL_LINK');
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('hardlinked artifacts are rejected even when their bytes and digests match', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    await link(corpus.paths.shared01, path.join(corpus.base, 'second-link.bin'));
    const before = await fixtureTree(corpus.base);
    await rejected({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files}, 'FILE_IDENTITY_AMBIGUOUS');
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('two opaque IDs cannot claim the same physical file under different bindings', async () => {
  const fixture = makeFixture();
  fixture.inventory.files[1].sha256 = fixture.inventory.files[0].sha256;
  fixture.inventory.files[1].size_bytes = fixture.inventory.files[0].size_bytes;
  await withCorpus(fixture, async corpus => {
    corpus.files.table01.relative_path = corpus.files.shared01.relative_path;
    const before = await fixtureTree(corpus.base);
    await rejected({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files}, 'FILE_IDENTITY_AMBIGUOUS');
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('substituted same-size bytes fail digest verification without modifying any file', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    await writeFile(corpus.paths.shared01, Buffer.alloc(fixture.contents.shared01.length, 0x58));
    const before = await fixtureTree(corpus.base);
    await rejected({...encodeFixture(fixture), roots: corpus.roots, files: corpus.files}, 'FILE_SUBSTITUTED');
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

test('missing files and directories are not accepted as verified regular files', async () => {
  const fixture = makeFixture();
  await withCorpus(fixture, async corpus => {
    const before = await fixtureTree(corpus.base);
    for (const relative_path of ['not-created.bin', 'data']) {
      const files = structuredClone(corpus.files); files.shared01.relative_path = relative_path;
      await rejected({...encodeFixture(fixture), roots: corpus.roots, files},
        ['INPUT_UNREADABLE', 'UNSAFE_PATH', 'FILE_SUBSTITUTED', 'FILE_IDENTITY_AMBIGUOUS']);
    }
    assert.deepEqual(await fixtureTree(corpus.base), before);
  });
});

async function cliFixture() {
  const fixture = makeFixture(), corpus = await materializeCorpus(fixture), options = encodeFixture(fixture);
  const inputs = path.join(corpus.base, 'inputs'); await mkdir(inputs);
  const names = {planBytes: 'plan.json', inventoryBytes: 'inventory.json', snapshotBytes: 'snapshot.json'};
  for (const [key, filename] of Object.entries(names)) await writeFile(path.join(inputs, filename), options[key], {flag: 'wx'});
  const args = [CLI, '--plan', path.join(inputs, 'plan.json'), '--inventory', path.join(inputs, 'inventory.json'),
    '--inventory-sha256', options.expectedInventorySha256, '--snapshot', path.join(inputs, 'snapshot.json'),
    '--snapshot-sha256', options.expectedSnapshotSha256, '--root', `corpus=${corpus.corpus}`,
    '--file', 'shared01=corpus:data/shared01.bin', '--file', 'table01=corpus:data/table01.bin'];
  return {fixture, corpus, args};
}

test('CLI reads explicit inputs, writes only stdout and exits 0 with a protected review', async () => {
  const {fixture, corpus, args} = await cliFixture(), before = await fixtureTree(corpus.base);
  const result = spawnSync(process.execPath, args, {encoding: 'utf8', timeout: 10000});
  assert.equal(result.error, undefined);
  assert.equal(result.status, 0, result.stderr);
  assertProtected(JSON.parse(result.stdout), fixture);
  assert.equal(result.stderr, '');
  assert(!result.stdout.includes(corpus.base));
  assert.deepEqual(await fixtureTree(corpus.base), before);
});

test('CLI refuses unknown/destructive, duplicate and valueless options with exit 2', async () => {
  const {corpus, args} = await cliFixture(), before = await fixtureTree(corpus.base);
  for (const extra of [['--delete'], ['--out', 'not-created.json'], ['--plan', 'other.json'],
    ['--root', `corpus=${corpus.corpus}`], ['--file', 'shared01=corpus:data/shared01.bin'], ['--snapshot-sha256']]) {
    const result = spawnSync(process.execPath, [...args, ...extra], {encoding: 'utf8', timeout: 10000});
    assert.equal(result.error, undefined);
    assert.equal(result.status, 2, result.stderr);
    const error = JSON.parse(result.stdout);
    assert.equal(error.status, 'REJECTED'); assert.equal(error.DELETE_AUTHORIZED, 'NO');
    assert.equal(typeof error.error.code, 'string');
    assert(!result.stdout.includes(corpus.base));
  }
  assert.deepEqual(await fixtureTree(corpus.base), before);
});

test('CLI contract rejection is structured and does not disclose a failed input path', async () => {
  const {corpus, args} = await cliFixture(), before = await fixtureTree(corpus.base);
  const changed = [...args], index = changed.indexOf('--inventory-sha256'); changed[index + 1] = '0'.repeat(64);
  const result = spawnSync(process.execPath, changed, {encoding: 'utf8', timeout: 10000});
  assert.equal(result.status, 2);
  const error = JSON.parse(result.stdout);
  assert.equal(error.status, 'REJECTED'); assert.equal(error.DELETE_AUTHORIZED, 'NO');
  assert.equal(error.error.code, 'INVENTORY_INTEGRITY_UNVERIFIED');
  assert(!result.stdout.includes(corpus.base));
  assert.deepEqual(await fixtureTree(corpus.base), before);
});
