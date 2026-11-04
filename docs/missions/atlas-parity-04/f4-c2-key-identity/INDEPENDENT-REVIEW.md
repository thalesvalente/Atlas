# Revisão independente não comprovada — disposições autorais

**Estado:** INDEPENDENT_REVIEW_NOT_PROVEN; ARC09_HUMAN_DECISION_PENDING; C2_K_REVIEW_BLOCKED_EXACT. NATIVE_SUBAGENTS_NOT_AVAILABLE. Este executor é autor dos reparos, não revisor independente. Request de Codex não equivale a aceite nem execução; o recibo final da PR registra o estado real.

Foram lidos os quatro reviews Copilot de 2026-11-01 (03:48, 22:57, 23:02, 23:18 UTC) e os 15 findings distintos; seis threads estavam abertas no HEAD 508ccb257a44dc66da13d1edfec7f00ef5231d09. Não limitar a revisão ao primeiro parecer e não confundir thread resolvido com blob corrigido.

## Disposição autoral a reavaliar no novo SHA

| Finding | Reparo/verificação nos artefatos |
|---|---|
| r4434300170 | F1 identificada como baseline sanitizada/selecionada, não sintética/global |
| r4434300181 | Code spans fechados; nomes de campos legíveis |
| r4434300187 | Parent e parent_key_literal já requeridos em 0.2.0, limite 65.536; não aplicar sugestão incompatível de opcionalidade/2048 |
| r4434300194 | Grafia órfãos corrigida |
| r4434300198 | technical_conclusion idêntico em RESULT/OPTIONS/HANDOFF |
| r4437713479 | Exemplo A conserva native-A como o fixture original |
| r4437713496 | Commit objeto de ARC-09 distinto do HEAD do recibo; SHA/tree e cinco blobs imutáveis no HANDOFF/DECISION final, sem branch móvel |
| r4437713512 | ABSENT/EXPLICIT_NULL/PRESENT, parent obrigatório, raiz com prova e tabela total |
| r4437713526 | Referência até 65.536, key indexável até 2048; L conserva 3000, sem truncamento |
| r4437713544 | Condições allOf/if/then para bases exclusivas preservadas; fragmento não instalado |
| r4437713562 | 14 entradas JSON: 10 principais A/B/C1/C2/D/E/F/G/H/I e 4 suplementares J/K/L/M; matriz PKEY separada |
| r4437778583 | Vazio, número, booleano, objeto, array e excesso rejeitam atomicamente; tabela e PKEY sem coerção |
| r4437778600 | Suíte futura numerada exatamente 1–12 |
| r4437778617 | NULL_ENDPOINT: declared_id=null, declared_key_literal=null, target_navigation_id=null |
| r4437778629 | Quatro campos novos completos em descriptor/RESULT/OPTIONS/HANDOFF/PR, incluindo node.parent_key_presence |

Achados autorais adicionais: matriz F alinhada a dup-F; TREE_CYCLE explicitado como gap com contagem dos membros, não enum de tree_state; root contraditório rejeita; estados de revisão histórica não reaproveitados como aprovação do novo commit. Todas as disposições acima são autorais, sujeitas à contestação independente.

## Limites e gates

O0 é refutado por A/B/C/D sem adulterar native IDs. E/F impedem keys fabricadas/duplicadas; G distingue órfão válido de input inválido; H conserva ciclo; I não promove navegação a causalidade; J/K/L/M cobrem presença, null, limites e bases. Nenhuma fixture prova paridade do corpus F1/R4 ou execução do produto.

C4_AP04_F2_GUARD_SUCCESSION_REQUIRED_FOR_NEW_K_DOC_PATHS: run 41361052428 no SHA inicial falhou nas quatro combinações Ubuntu/Windows e O0/O1. Log Ubuntu 125011293907 mostra GuardError: Repair history contains unauthorized paths para os 11 paths K. Não mudar guard/pins/allowlist, ocultar erro ou repetir CI antiga; P02/C4 é owner do reparo. CI do novo SHA deve ser lida separadamente e registrada na PR.

Revisor externo: conferir o SHA publicado, seu parent único, a cadeia linear desde 508ccb2, escopo exclusivamente K, manifesto completo, os cinco blobs normativos congelados e INPUT-SHAS; contestar identidade, contextos, ausência, ciclos, quotas/TTL, privacidade e ARC-09. Publicar autoria/linhagem verificável, severidade e findings reproduzíveis. G4/G5/G6 e aprovação humana continuam gates separados.

## Checker de documentos, não implementação 0.2.1

Executar o bloco Python abaixo na raiz do checkout fixo, em Python normal e -O, após revisão do código. Ele apenas lê documentos/JSONs, compara expectativas conhecidas e hashes. Não importa código do produto, não cria descriptor, não instala schema, não acessa rede nem escreve arquivos. Para uma preparação local ainda não congelada, a execução exige --staging; o recibo publicado exige execução sem essa opção. A flag não é usada para qualificar o HEAD publicado.

```python
"""Read-only documentary checker. Not a descriptor mapper or validator."""
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

P = Path('docs/missions/atlas-parity-04/f4-c2-key-identity')
FIELDS = ['node.source_key_literal', 'node.parent_key_presence',
          'reference.reference_basis', 'reference.declared_key_literal']
MAIN = ['A', 'B', 'C1', 'C2', 'D', 'E', 'F', 'G', 'H', 'I']
SUPP = ['J', 'K', 'L', 'M']
SUBJECT = {'COMPATIBILITY-AND-MIGRATION-LESS.md',
           'CURRENT-CONTRACT-COUNTEREXAMPLES.md', 'DESCRIPTOR-0.2.1-CANDIDATE.md',
           'OPTIONS-AND-RISK.md', 'SYNTHETIC-IDENTITY-FIXTURES.json'}

def need(condition, message):
    if not condition:
        raise ValueError(message)

def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def inspect_oracles(doc):
    need(doc['synthetic'] is True and doc['private_data'] is False, 'origin flags')
    need([c['id'] for c in doc['cases']] == MAIN, 'main inventory')
    need([c['id'] for c in doc['supplemental_reference_oracles']] == SUPP, 'supp inventory')
    c = {x['id']: x for x in doc['cases']}
    s = {x['id']: x for x in doc['supplemental_reference_oracles']}
    graph = lambda name: c[name]['r4_v5']['lineage_graph']
    expected = lambda name: c[name]['expected_0_2_1']
    for name in ['A', 'B', 'C1', 'C2']:
        nodes = graph(name)['nodes']
        ref = expected(name)['parent_ref']
        need(nodes[1]['parent_key'] == nodes[0]['key'] == ref['declared_key_literal'], name + ': literal')
        need(ref['reference_basis'] == 'SOURCE_STRUCTURAL_KEY' and ref['declared_id'] is None, name + ': basis')
        need(ref['source_id'] == c[name]['source_id'] and ref['snapshot_id'] == c[name]['snapshot_id'], name + ': context')
        need(ref['resolution'] == 'RESOLVED' and ref['target_navigation_id'] == f'nav:fixture:{name}:1', name + ': oracle target')
        need(ref['evidence_locator'] == '/lineage_graph/nodes/1/parent_key', name + ': locator')
    need(graph('A')['nodes'][0]['native_id'] == expected('A')['parent_native_id_unchanged'] == 'native-A', 'A native unchanged')
    need(graph('A')['nodes'][0]['key'] != graph('A')['nodes'][0]['native_id'], 'A namespaces')
    need(graph('B')['nodes'][0]['native_id'] is None and c['B']['r4_v5']['records'][0]['id'] == graph('B')['nodes'][0]['key'], 'B collision text')
    need(expected('B')['record_id_same_literal_not_target'] is True, 'B not record')
    need(c['C1']['snapshot_id'] != c['C2']['snapshot_id'] and graph('C1')['nodes'][0]['key'] == graph('C2')['nodes'][0]['key'], 'C snapshot distinction')
    need(expected('C2')['cross_snapshot_forbidden'] is True, 'C isolation')
    d = graph('D')
    native = Counter(n['native_id'] for n in d['nodes'] if n['native_id'] is not None)
    keys = {n['key'] for n in d['nodes']}
    parents = [n['parent_key'] for n in d['nodes'] if 'parent_key' in n]
    need(len(d['nodes']) == len(keys) == 150 and len(d['edges']) == 50, 'D population')
    need(len(native) == 50 and set(native.values()) == {2}, 'D native collisions')
    need(len(parents) == 50 and all(p in keys for p in parents), 'D explicit parents')
    need(all(e['from_key'] in keys and e['to_key'] in keys for e in d['edges']), 'D edge keys')
    need(expected('D') == {'native_collision_groups': 50, 'native_colliding_nodes': 100, 'unique_structural_keys': 150, 'explicit_structural_parents': 50, 'native_lookup_still': 'COLLISION', 'structural_parent_resolutions': 50}, 'D expected counts')
    need('key' not in graph('E')['nodes'][0] and expected('E')['import'] == 'REJECT_MISSING_STRUCTURAL_KEY_ATOMIC' and expected('E')['no_ui_id_or_label_fallback'] is True, 'E atomic missing')
    need([n['key'] for n in graph('F')['nodes']] == ['dup-F', 'dup-F'] and expected('F')['import'] == 'REJECT_DUPLICATE_STRUCTURAL_KEY_ATOMIC', 'F atomic duplicate')
    g = expected('G')
    need(graph('G')['nodes'][1]['parent_key'] not in {n['key'] for n in graph('G')['nodes']}, 'G absent target')
    need(g['parent_ref']['resolution'] == 'UNRESOLVED' and g['parent_ref']['target_navigation_id'] is None and g['tree_state'] == 'ORPHAN' and g['binding_gap'] is True, 'G oracle')
    h = graph('H')['nodes']
    need(h[0]['parent_key'] == h[1]['key'] and h[1]['parent_key'] == h[0]['key'], 'H cycle bytes')
    need(expected('H') == {'structural_parent_refs_resolved_individually': 2, 'tree_cycle_gap': 'TREE_CYCLE', 'binding_gap': True, 'no_acyclic_claim': True}, 'H cycle oracle')
    i = expected('I')
    need(graph('I')['edges'][0] == {'type': 'MEMBER_OF', 'from_key': 'member-I', 'to_key': 'group-I'}, 'I edge')
    need(i['semantics'] == 'ORGANIZATIONAL_MEMBERSHIP' and i['causal_status'] == 'NON_CAUSAL' and i['scientific_approval'] == 'NOT_EVALUATED', 'I non causal')
    for endpoint, literal in [('from_ref', 'member-I'), ('to_ref', 'group-I')]:
        need(i[endpoint] == {'reference_basis': 'SOURCE_STRUCTURAL_KEY', 'declared_id': None, 'declared_key_literal': literal, 'resolution': 'RESOLVED'}, 'I endpoint')
    for name, presence in [('J', 'ABSENT'), ('K', 'EXPLICIT_NULL')]:
        node = s[name]['input']['node']
        e = s[name]['expected_future']
        need(('parent_key' not in node) if name == 'J' else ('parent_key' in node and node['parent_key'] is None), name + ': source presence')
        need(e['parent_key_presence'] == presence and e['parent_key_literal'] is None and e['tree_state'] == 'PARENT_UNKNOWN', name + ': state')
        need(e['parent_reference'] == {'reference_basis': 'SOURCE_STRUCTURAL_KEY', 'declared_id': None, 'declared_key_literal': None, 'target_navigation_id': None, 'resolution': 'NULL_ENDPOINT'}, name + ': null triple')
    need(s['K']['expected_future']['root_true_with_source_proof'] == 'ROOT_DECLARED', 'K root proof oracle')
    l = s['L']['expected_future']
    need(s['L']['input']['node']['parent_key'] == 'x' * 3000 and l['declared_key_literal_length'] == 3000 and l['parent_key_presence'] == 'PRESENT', 'L long literal')
    need(l['parent_reference']['resolution'] == 'UNRESOLVED' and l['parent_reference']['target_navigation_id'] is None and l['tree_state'] == 'ORPHAN' and l['binding_gap'] is True, 'L orphan')
    need(s['M']['invalid_future_refs'] == [{'reference_basis': 'NATIVE_ID', 'declared_id': 'native-M', 'declared_key_literal': 'key-M'}, {'reference_basis': 'SOURCE_STRUCTURAL_KEY', 'declared_id': 'native-M', 'declared_key_literal': 'key-M'}], 'M mixed examples')
    need(s['M']['expected_future']['json_schema_if_then'] == 'REJECT_ATOMIC', 'M negative oracle')
    return MAIN + SUPP

def main():
    text = {f.name: f.read_text(encoding='utf-8') for f in P.iterdir() if f.is_file()}
    checked = inspect_oracles(json.loads(text['SYNTHETIC-IDENTITY-FIXTURES.json']))
    need(git_blob((P/'SYNTHETIC-IDENTITY-FIXTURES.json').read_bytes()) == '49dc02a5fed21d9f6cca074e8511dd006f6fda2c', 'fixture original bytes')
    need(git_blob((P/'INPUT-SHAS.json').read_bytes()) == 'ed11aa5e13b53e689301f800eae3510e9e7fcddf', 'input pins original bytes')
    for name in ['DESCRIPTOR-0.2.1-CANDIDATE.md', 'OPTIONS-AND-RISK.md', 'RESULT.md', 'COMPATIBILITY-AND-MIGRATION-LESS.md', 'CURRENT-CONTRACT-COUNTEREXAMPLES.md', 'DECISION-REQUEST.md', 'HANDOFF.json']:
        need(all(field in text[name] for field in FIELDS), name + ': complete delta')
    suite = text['COMPATIBILITY-AND-MIGRATION-LESS.md'].split('## Suíte red/green')[1]
    need([int(n) for n in re.findall(r'^(\d+)\. ', suite, flags=re.M)] == list(range(1, 13)), 'suite numbering')
    current = text['CURRENT-CONTRACT-COUNTEREXAMPLES.md']
    rows = [line.split('|')[1:4] for line in current.splitlines() if line.startswith('| PKEY-')]
    need(len(rows) == 12, 'PKEY row count')
    need([x[0].strip() for x in rows] == [f'PKEY-{i:02d}' for i in range(1, 13)], 'PKEY ids')
    need(all('REJECT_ATOMIC' in rows[i-1][2] for i in [3, 4, 5, 6, 7, 10]), 'PKEY invalid expectations')
    descriptor = text['DESCRIPTOR-0.2.1-CANDIDATE.md']
    delta = json.loads(descriptor.split('```json\n', 1)[1].split('\n```', 1)[0])
    defs = delta['$defs']
    need(defs['node']['properties']['parent_key_presence']['enum'] == ['ABSENT', 'EXPLICIT_NULL', 'PRESENT'], 'presence enum')
    need(defs['reference']['properties']['declared_key_literal']['maxLength'] == 65536, 'reference bound')
    need(defs['node']['properties']['source_key_literal']['maxLength'] == 2048, 'index bound')
    for rule, basis, null_field in zip(defs['reference']['allOf'], ['NATIVE_ID', 'SOURCE_STRUCTURAL_KEY'], ['declared_key_literal', 'declared_id']):
        need(rule['if']['properties']['reference_basis']['const'] == basis and rule['then']['properties'][null_field]['type'] == 'null', 'illustrative if/then')
    need(len(defs['reference']['allOf']) == 2, 'two conditions')
    handoff = json.loads(text['HANDOFF.json'])
    need(handoff['new_fields'] == FIELDS and handoff['manifest_entries'] == 10, 'handoff fields/count')
    need(handoff['technical_conclusion'] in text['RESULT.md'] and handoff['technical_conclusion'] in text['OPTIONS-AND-RISK.md'], 'conclusion token')
    need(handoff['human_decision'] == 'ARC09_HUMAN_DECISION_PENDING' and handoff['human_approval'] is False, 'no approval')
    subject = handoff['arc09_subject']
    need({Path(f['path']).name for f in subject['files']} == SUBJECT, 'subject inventory')
    for entry in subject['files']:
        path = Path(entry['path'])
        need(path.parent == P and path.name in SUBJECT, 'subject scope')
        data = path.read_bytes()
        need(git_blob(data) == entry['blob_sha1'] and hashlib.sha256(data).hexdigest() == entry['sha256'], 'subject hash')
    if '--staging' not in sys.argv:
        need(subject['state'] == 'FROZEN_UNAPPROVED', 'subject frozen')
        need(re.fullmatch('[0-9a-f]{40}', subject['commit'] or '') and re.fullmatch('[0-9a-f]{40}', subject['tree'] or ''), 'subject immutable identities')
        need(subject['commit'] in text['DECISION-REQUEST.md'] and subject['tree'] in text['DECISION-REQUEST.md'], 'decision identity')
    entries = [line.split('  ', 1) for line in text['MANIFEST.sha256'].splitlines()]
    need(len(entries) == 10 and len({p for _, p in entries}) == 10, 'manifest inventory')
    need({Path(p).name for _, p in entries} == set(text) - {'MANIFEST.sha256'}, 'manifest complete coverage')
    for digest, path in entries:
        need(Path(path).parent == P and re.fullmatch('[0-9a-f]{64}', digest), 'manifest scope')
        need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, 'manifest hash: ' + path)
    print(json.dumps({'document_check': 'PASS', 'oracle_entries': len(checked), 'ids': checked, 'PKEY_documentary_rows': 12, 'manifest': '10/10', 'optimize': sys.flags.optimize, 'product_0_2_1': 'NOT_RUN', 'independent_review': 'NOT_PROVEN'}, ensure_ascii=False))

if __name__ == '__main__':
    main()
```
