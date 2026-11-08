from pathlib import Path
import json, subprocess, csv,io,ast,hashlib
from collections import Counter
P=Path(__file__).parent
R=P.parents[1]/'repo'
OLD=Path('/workspace/scratch/c50b5f701290/atlas-pr19')
M='8f8fe01c3041361aa2607194d66af6a640d834ad'
S='SUPERSEDED_BY_DESIGN';E='EQUIVALENT_IN_MAIN';X='REJECTED_WITH_REASON';T='RETAIN_AND_IMPLEMENT'
def g(*a):return subprocess.check_output(['git',*a],cwd=R)
def save(n,v):(P/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
O=json.loads((P.parents[1]/'O0-CONTRACT.json').read_text());H={r['pr']:r['head_sha'] for r in O['targets']}
# Keep all original IDs, contract classes, and acceptance text.
p='docs/missions/atlas-parity-02/p01-contracts/CAPABILITY-PARITY.csv'
js=list(csv.DictReader(io.StringIO(g('show',H[9]+':'+p).decode())))
notes={
1:(E,'Fontes válidas/inválidas/inacessíveis segregadas; invalid não recebe read_model.','P09 INVALID_SOURCE_NOT_INDEXED; catalog_server'),
2:(E,'Mesmo ID em fontes distintas conserva título e alvo local.','P06 repeated_ids; P09 SOURCE_SCOPED_COLLISION'),
3:(T,'Ordinal source-N muda de alvo na reordenação. P02 exige vínculo verificado de preferências/seleção.','P09 ORDINAL_REORDER_LIMIT; P02 F001–003'),
4:(E,'Busca atual restringe runs por campos declarados; não promete busca integral de payload.','app.js filteredRuns; core browser'),
5:(S,'Exploração, comparação e timeline têm escopos próprios; não adotar filtro global por inferência. NativeView explicita população filtrada e contexto técnico.','spec004 FR013; app.js renderTimeline; P02 native browser'),
6:(E,'Tipo/unidade/identidade separam comparação; não há conversão ou equivalência científica inferida.','P06 typed values; core browser'),
7:(S,'C0 conserva display_value e rejeita decimais fora do suporte; NativeView preserva tokens lexicais.','P06 numeric/decimal tests; native_legacy exact token tests'),
8:(E,'Tempo científico desconhecido não usa indexação, publicação ou filesystem.','P06 time_offsets; P09 UNKNOWN_VALUES_TIMES'),
9:(T,'Corrigir rótulo de indexed_at e distinguir observed_at quando exposto.','catalog.py fields; app.js current mislabel; P00 final regression pending'),
10:(T,'Campo date_published já está no read_model. Exposição compatível deve nomear publicação do snapshot, sem inferir criação/evento.','read_model.py source.date_published; P00 final regression pending'),
11:(E,'Relações declaradas mantêm direção; menções não geram causalidade.','P06 lineage; P09 MENTION_NEUTRAL_ORDER'),
12:(E,'Menções neutras, ordem deduplicada, rótulos e disponibilidade permanecem literais.','related_references suite; P09 MENTION_NEUTRAL_ORDER'),
13:(E,'Missing structural reference invalida grafo; ausência de payload não prova inexistência na origem.','P09 INVALID_SOURCE_NOT_INDEXED; related_references availability'),
14:(X,'Não adotar detalhador arbitrário de todas as entities. Candidato não incorporado; spec001 FR003 trata runs/evidências. NativeView inspeciona os seus registros.','spec001 US1/FR003; spec004 US1; native parity'),
15:(S,'Documento não vira run. Não exigir novo painel genérico para cumprir candidato de apresentação.','P09 DOCUMENT_PRODUCT_NOT_RUNS; NativeView full fields'),
16:(X,'Não usar JSON.stringify de entities arbitrárias e números potencialmente inexatos. Painel candidato não é obrigação; NativeView preserva raw JSON original.','spec004 FR005; native parity all fields'),
17:(E,'Propriedades de execução preservam tipo/unidade/ordem/missing_reason/precision.','P06 typed values; core browser'),
18:(X,'Não introduzir nova semântica científica persistida de grade. A via NativeView em Files atende apresentação.','spec004 FR002/009; plan004; typed CSV tests'),
19:(X,'Não criar tipo de evento documental científico ou promover mtime a execução. Preservar tempos declarados e UNKNOWN.','spec004 FR005; P06 unknown time; native parity'),
20:(S,'Overview mostra populações declaradas com origem/ausência; worksheet/sidecar não é obrigatório.','spec007 FR013; native_legacy overview test'),
21:(S,'Perda upstream exige origem/pin de projeção autorizada. Não declarar cobertura privada por fixture sintética.','native parity wrong pin/self-consistent different package; spec007 FR007'),
22:(S,'Coleções/runs/seleção e contagem de acervo são populações distintas. Documento sem run não equivale a acervo vazio.','native_legacy overview/catalog; spec007 FR013'),
23:(S,'Contagem por fonte/validade/seleção conserva escopo; contador da UI não prova universo completo.','catalog_server invalid/valid sources; native overview'),
24:(E,'Conformidade, digest, origem e ciência continuam separadas.','P06 execution/review/integrity; native parity'),
25:(E,'Dossiê derivado inclui fontes/limites sem certificar autenticidade ou ciência.','catalog_server dossier; core browser'),
26:(E,'Rebuild explícito não escreve fontes. Backend detecta mudança; patch de binding UI é separado.','catalog_server source change; native HTTP explicit reindex; P09 INPUT_BYTES_UNCHANGED'),
27:(T,'Orientação atual registra ADR aceita como direção, sem apagar normativos históricos ou aprovar release.','human #5/6406839421; P00 docs patch pending'),
28:(X,'Não tornar ordinal identidade científica durável. Corrigir sessão/preferências não exige protocolo persistido novo.','P09 ORDINAL_REORDER_LIMIT; spec004 FR004; P02 context regression')}
for r in js:
 i=int(r['capability_id'].split('J')[-1]);d,c,t=notes[i];r.update(disposition=d,current=c,tests=t.split('; '),counterevidence='Classe original conservada: candidato não é requisito aprovado. Evidência limitada à superfície citada.',source_sha=H[9],source_path=p,source_blob=g('rev-parse',H[9]+':'+p).decode().strip())
save('P01-JOURNEY-CROSSWALK.json',js)
# 46 exact cases, without claiming the worksheet format became the NativeView API.
cases=json.loads((P/'sources/9/docs/contracts/atlas-parity-02/p01/examples/cases.json').read_text())['cases']
for c in cases:
 fmt=c['format'];i=c['id']
 if fmt=='CADERNO_CURRENT':
  cur='Perfil atual inalterado; semântica do validador preservada.'; tests=['protocol adversarial current-profile validation','P09 current reader probes'];d=E
 elif 'table' in i:
  cur='Intenção de tipos/ausência/exatidão/ordem é atendida por P03/NativeView; worksheet não é API científica.';tests=['native_legacy typed CSV/literal values/reading order','P03 table protected component'];d=S
 elif 'coverage' in i:
  cur='Populações declaradas por origem; ausência não vira zero, denominadores não são inferidos; sem sidecar obrigatório.';tests=['spec007 FR013/SC007','native_legacy overview test'];d=S
 else:
  cur='Invariantes de referência/contexto/tempo e inércia têm validação SDK/NativeView; DTO documental não adotado como transporte.';tests=['related_references suite','P06 semantics','native parity'];d=S
 c.update(disposition=d,current=cur,tests=tests,execution='HISTORICAL_46_PASS_REUSED_NOT_REEXECUTED',counterevidence='Não atribuir expected_errors do worksheet ao parser NativeView. Correlação por intenção, sem cobertura integral automática.')
save('P01-EXAMPLE-CROSSWALK.json',cases)
# 28 additional C2 files from previous authoritative matrix; not inherited P03.
old=json.loads((OLD/'agents/P01/P01-FILES.json').read_text());c2=[]
for f in old:
 if f['pr']!=10 or f.get('inherited_from'):continue
 path=f['path']
 if path.endswith('build.py'):goal='Instalação isolada de wheels';succ=['scripts/qa/clean_install.py','.github/workflows/atlas021.yml']
 elif path.endswith('http.py'):goal='HTTP real de rotas fixas';succ=['tests/viewer/test_catalog_server.py','tests/viewer/test_native_notebook_http.py']
 elif path.endswith('browser.mjs'):goal='Browser real P03: lexemas/foco/reflow/inércia';succ=['scripts/qa/browser_native_notebook.mjs','scripts/qa/browser_native_graph.mjs']
 elif path.endswith('ci.py'):goal='47 testes exatos/zero skips/pins históricos';succ=['scripts/run_checks.py','.github/workflows/atlas021.yml']
 elif 'harness.' in path:goal='Demonstrador P03 isolado';succ=['spec004 NativeView active composition']
 elif path.startswith('docs/'):goal='Recibo histórico específico '+Path(path).name;succ=['Preserve pinned receipt; O0 main CI is separate new evidence']
 elif path.startswith('specs/'):goal='Plano/contrato/tasks da qualificação C2';succ=['specs/004-native-notebook-experience','specs/007-final-legacy-parity']
 else:goal='Orquestração/dependências da qualificação';succ=['.github/workflows/atlas021.yml']
 c2.append(dict(path=path,sha=H[10],blob=f['head_blob'],goal=goal,successor=succ,disposition=S,counterevidence='Não portar layout antigo, exigência 47/zero-skip ou inatividade P03. Evidência histórica não é CI do produto novo.'))
save('P01-C2-28-FILES.json',c2)
# Unique method IDs by class.
def methods(sha,paths):
 out=[]
 for path in paths:
  tree=ast.parse(g('show',sha+':'+path));blob=g('rev-parse',sha+':'+path).decode().strip()
  for cls in ast.walk(tree):
   if isinstance(cls,ast.ClassDef):
    for fn in cls.body:
     if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_'):out.append(dict(id=path+'::'+cls.name+'::'+fn.name,sha=sha,blob=blob))
 return out
paths=[p for p in g('ls-tree','-r','--name-only',H[7],'tests').decode().splitlines() if 'parity02_p03' in p and p.endswith('.py')]
p03=methods(H[7],paths)
for r in p03:r.update(disposition=S,scope='Historical DTO/harness preserved; same method is not claimed executed against main.',successor=['SDK/read_model/native parity for metadata constraints','current HTTP/browser for harness','P03 protected table for table behavior'])
save('C2-P03-35-TEST-CROSSWALK.json',p03)
k=methods(H[31],['tests/qa/test_atlas_parity04_k_doc_ci.py','tests/qa/test_atlas_parity04_f2_doc_ci.py'])
for r in k:r.update(disposition='PRESERVE_PINNED_HISTORICAL_GUARD_NOT_PORT_MAIN',execution_this_turn='NOT_RUN_REUSE_PRIOR',counterevidence='Historical37jobs green and prior partial33/36K replay are distinct proofs; not a new68 test execution or0.2.1 approval.')
save('K-NEGATIVES-PRESERVED.json',k)
# Six independent AP04 capabilities.
par=[
('005','Produtos/grupos/versões/apresentações','Coleções e estágios/execuções declarados no catálogo nativo; preserva null/empty/unknown.','native_legacy catalog includes classical products; product catalog restores declared execution and stage','Não inferir produto de nome/MIME ou ID científico de agrupamento editorial.'),
('006','Documentos/recursos/dossiês','Campos originais, UID/ID, disponibilidade e JSON integral consultáveis.','native_legacy null/scalars/arrays inspectable; hostile labels; native parity','URI não autoriza download; export não aprova ciência.'),
('007','Grafo/árvore/relações','Resolução nativa exata, colisões visíveis, busca alcança todos os nós; árvore editorial distinta de parentesco técnico.','native_legacy relation endpoints/ambiguous endpoints; native graph browser','Não fabricar aresta para null/unresolved nem causalidade por tema.'),
('008','Histórico/timeline','Tempos declarados e UNKNOWN preservados; observação não substitui evento.','P06 time offsets; P09 unknown values/times; native parity allfields','Não converter mtime/publicação/indexação em tempo científico.'),
('009','Cobertura/perdas/populações','Overview separa source populations, navegação e sessão; preserva ausência/null/zero/exato.','native_legacy overview test; spec007 FR013/SC007; native parity pin tests','Sem universo privado conhecido não inferir completude, denominador ou percentual.'),
('010','Storage observacional','Resumo declarado e notices consultáveis, readonly; não há poder de limpeza ou migração.','native_legacy overview/dataset notice; native_notebook immutable source tests','Não prometer espaço recuperado ou existência de arquivos não observados.')]
save('P01-PAR005-010.json',[dict(id='PAR-'+i,historical=h,current=c,tests=t.split('; '),counterevidence=n,disposition=S,evidence=['spec004 spec/plan','spec007 spec','native_legacy_model.js','P02-CI-EVIDENCE.json'],human_gate='Private OLD/NEW/ChromeWindows exact acceptance remains separate.') for i,h,c,t,n in par])
# N01–24. These are rules of the old optional route, not necessarily implemented APIs in main.
n=[
('Contexto fonte/snapshot/ID','UID/nativeID/source_key separados','native parity; occurrences JS','Não mesclar mesmo ID entre contextos'),
('Colisões','Ocorrências preservadas, typed keys e ambiguidade','native endpoints; numeric identity JS','Não escolher primeiro colidente'),
('UID vs nativeID','Apresentação separada da identidade original','spec004 FR004; native parity','UID não vira ciência'),
('NULL endpoint','NULL literal preservado','native relation presentation JS','Não inventar target'),
('Unresolved','Referência não resolvida não cria travessia','native ambiguous endpoints JS','Sem aresta por rótulo'),
('Contagens sobrepostas','Populações declaradas por camada','native overview JS','Não somar subconjuntos'),
('Tabelas sem vínculo','Coleção completa e exportação mantidas','native parity; native browser','Sem descarte por orfandade'),
('ID não admitido','NativeID ausente/null preservado','native occurrences JS','Não inventar ID científico'),
('Run vs stub','Originais e estados declarados preservados','P09 document_product_not_runs; native parity','File não vira execução'),
('Ausência/null/vazio/zero','Tokens e CSV tipado reversível','typed CSV JS; native parity','Não normalizar valores'),
('Lexemas','Raw tokens/display_value verificados','numeric identity JS; native noncanonical JSON test','Sem roundtrip Number'),
('HTML/JS','TextContent/SVG próprios e CSP','hostile labels JS; native HTTP/browser','Sem execução/rede externa'),
('CSV/JSON','CSV protegido/tipado, JSON integral','typed CSV JS','Neutralização declarada sem mudar JSON'),
('Fronteira de I/O','Bug atual P03: rejeitar módulo fora da raiz ANTES de importar; patch P00 via#18','P03 symlink RED; P00 O3 pending','Não alegar O1 sandbox/Windows hardbudget/TOCTOU completos'),
('URIs','Referências inertes, sem download automático','P06 passive URIs; native browser','URI não é autorização de acesso'),
('Mudança/frescor','Pinsha/revisão,digest e reindex explícito','native parity wrongpin/selfconsistentdifferent; native HTTP','Hash próprio não prova origem/frescor; O1 race não implementado'),
('Versão/cota/falha','NativeView rejeita versão/hash/chunk/limites; protocolo pode permanecer válido','native tests; P02 READY/INVALID15checks','Quotas NativeView diferentes das0.2.0'),
('Sessão/reindex/TTL','Contexto nativo; patch P02 para raiz; TTL manual0.2.0 não ativado','native HTTP; P02 F001–003 pending','Não alegar equivalência de TTL3600'),
('Universo desconhecido','Ausência não zero, denominação por população','native overview JS; spec007 FR013','0/0 não vira100%'),
('Digest e ciência','Dimensões separadas','P06 authority states; native parity','Integridade não aprova ciência'),
('Semântica declarada','Catálogo usa coleções declaradas; sem MIME heurístico','native catalog JS; P09 documents_not_runs','Não inferir produto/admissão científica'),
('Independência','Wheels SDK/viewer sem R4/sidecar obrigatório','clean_install; architecture; native standalone','Produtor permanece externo'),
('Browser/acervo','CI sintética atual separada de aceites privados','main CI; spec007 FR007','HTTP/Chromium não são ChromeWindows humano'),
('Conformidade','Paridade pinada por campo;0.2.1 não instalado','native parity; frozenARC09','Checker documental não é produto0.2.1')]
save('P01-N01-24.json',[dict(id=f'N{i:02d}',historical=h,current=c,tests=t.split('; '),counterevidence=neg,disposition=S,status='PENDING_PATCH_OTHER_OWNER' if i in [14,18] else 'SCOPED_EVIDENCE') for i,(h,c,t,neg) in enumerate(n,1)])
# Sources, including normative exact blob verification.
sources=json.loads((P/'P01-SOURCES.json').read_text())
def src(path,sha=M):
 raw=g('show',sha+':'+path);return dict(path=path,sha=sha,blob=g('rev-parse',sha+':'+path).decode().strip(),sha256=hashlib.sha256(raw).hexdigest(),url='https://github.com/thalesvalente/Atlas/blob/'+sha+'/'+path)
freeze='d5bdc86ef68cad2f5d503945ca788c3a74df4839';frozen=[]
for name in ['COMPATIBILITY-AND-MIGRATION-LESS.md','CURRENT-CONTRACT-COUNTEREXAMPLES.md','DESCRIPTOR-0.2.1-CANDIDATE.md','OPTIONS-AND-RISK.md','SYNTHETIC-IDENTITY-FIXTURES.json']:
 path='docs/missions/atlas-parity-04/f4-c2-key-identity/'+name;r=src(path,freeze);r['same_blob_at_pr21_head']=g('rev-parse',freeze+':'+path)==g('rev-parse',H[21]+':'+path);frozen.append(r)
save('P01-ARC09-FROZEN.json',frozen)
current=['README.md','specs/001-atlas021-protocol-interface/spec.md','specs/004-native-notebook-experience/spec.md','specs/004-native-notebook-experience/plan.md','specs/004-native-notebook-experience/research.md','specs/004-native-notebook-experience/contracts/native-view.md','specs/007-final-legacy-parity/spec.md','packages/atlas/src/atlas_viewer/catalog.py','packages/atlas/src/atlas_viewer/static/app.js','packages/atlas/src/atlas_viewer/static/native_legacy_model.js','packages/atlas/src/atlas_viewer/static/parity02_p03_table.js','packages/atlas/src/atlas_viewer/static/parity02_p03_table.css','packages/protocol/src/caderno_protocol/read_model.py','.github/workflows/atlas021.yml','scripts/run_checks.py','scripts/qa/clean_install.py','scripts/qa/test_native_legacy.mjs','scripts/qa/browser.mjs','scripts/qa/browser_native_notebook.mjs','scripts/qa/browser_native_graph.mjs','tests/viewer/test_catalog_server.py','tests/viewer/test_related_references.py','tests/viewer/test_native_notebook.py','tests/viewer/test_native_notebook_http.py','tests/viewer/test_native_notebook_parity.py','tests/qa/test_architecture_boundaries.py','tests/qa/test_protocol_adversarial.py','packages/protocol/tests/test_sdk.py']
sources += [src(x) for x in current]+frozen
save('P01-ALL-SOURCES.json',sources)
checks=json.loads((P/'P01-CHECKS-PRELIMINARY.json').read_text())+json.loads((P/'P09-READER-PROBES-ON-MAIN.json').read_text())
checks.extend([
 dict(id='P01-MAIN-CI',status='PASS_REUSED_O0_VERIFIED',sha=M,runs=[42429516799,42429516812,42429516868,42429516784,42429516816,42429516778],jobs=19,exit_code=None,evidence='../../evidence/o0/main-checks.json',limitation='Baseline only; final candidate requires own CI'),
 dict(id='P01-ARC09-BLOBS',status='PASS',exit_code=0,command='git rev-parse for five paths at d5bdc86 and PR21HEAD; compare',results=frozen,limitation='Blob identity, not approval'),
 dict(id='P01-HUMAN-RECEIPTS',status='VERIFIED',exit_code=None,evidence='HUMAN-APPROVAL-READBACK.json',receipts=['#5/6406839421','#15/6539419419'],limitation='Direction/scoped0.2.0 only; no0.2.1 release/science'),
 dict(id='P01-HISTORICAL-TESTS',status='REUSED_NOT_REEXECUTED',exit_code=None,evidence=str(OLD/'output/ATLAS-PR19-TECHNICAL-DISPOSITION.md'),limitation='46worksheets/35P03/42table and K/F2 from prior receipt; partial33/36K remains partial'),
 dict(id='P01-FINAL-CANDIDATE-CI',status='PENDING_P00_O3',exit_code=None),
 dict(id='P01-INDEPENDENT-REVIEW',status='PENDING_P03',exit_code=None),
 dict(id='P01-PRIVATE-LOCAL',status='NOT_RUN_NOT_REQUIRED_FOR_SCOPE',exit_code=None,limitation='No private data or hostWindows/GUI/hardbudget proof; public synthetic work does not require CodexLocal')])
save('P01-CHECKS.json',checks)
assert len(js)==28 and len(cases)==46 and len(c2)==28 and len(p03)==35 and len(k)==68 and len(n)==24
assert all(r['same_blob_at_pr21_head'] for r in frozen)
x=json.loads((P/'P01-MATRIX.json').read_text())
for r in x['rows']:r['historical_sha']=H[r['pr']]
x['source_inventory']='P01-ALL-SOURCES.json';x['disposition_counts']=dict(Counter(r['disposition'] for r in x['rows']));x['requirements_count']=sum(len(r['requirements']) for r in x['rows'])
save('P01-MATRIX.json',x)
art={p.name:dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size) for p in sorted(P.iterdir()) if p.is_file() and p.name!='P01-HANDOFF.json'}
save('P01-HANDOFF.json',dict(owner='/root/p01_contracts',phase='O1',status='FROZEN_FOR_P03_REVIEW',baseline_sha=M,baseline_tree=O['baseline_tree'],disposition_count=10,counts={'journeys':28,'cases':46,'c2files':28,'p03methods':35,'par':6,'n':24,'arc09':5,'k_f2':68},new_tests={'P06normal':7,'P06optimized':7,'P09normal':9,'P09optimized':9,'exit_codes':[0,0,0,0]},product_edits=0,remote_mutations=0,local_required=False,independent_review='PENDING_P03',final_candidate_ci='PENDING_P00_O3',artifacts=art))
print(json.dumps({'status':'REVIEW_READY','rows':10,'requirements':x['requirements_count'],'sources':len(sources),'matrix_sha256':hashlib.sha256((P/'P01-MATRIX.json').read_bytes()).hexdigest(),'handoff_sha256':hashlib.sha256((P/'P01-HANDOFF.json').read_bytes()).hexdigest()}))
