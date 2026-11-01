# AP04-F4-C4-GLOBAL-CI-CHAT-02 — qualificação global da integração real por SHA

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub e GitHub Actions, com escrita efetiva. **Raciocínio recomendado: Extra High**, manualmente selecionado pelo operador.
**Repositório:** `thalesvalente/Atlas`. **Branch existente, compartilhada SEQUENCIALMENTE com C3:** `integrate/atlas-parity04-f4-composition-20261031`. Começar **somente quando C3 publicar e congelar SHA**, sem writer C3 simultâneo. Não criar novas worktrees/clones, branches/PRs por conveniência.
**Estado-alvo:** `F4_G5_INTEGRATION_CI_QUALIFIED_HOST_GATE_DEFERRED` somente com CI global terminal, controprovas e revisão independente do SHA final; G4 LOCAL e G6 permanecem gates separados.

## 1. Preflight Git e dependências exatas

- F2/PR #15 SHA `54bb16d350f7bc34fafb95438bd64a2397d58bf3` (tree `1372dd532b2323fc1ebaa5c2f00b6d537c636dc9`), 223 IDs distintos nos testes herdados, 37 jobs qualificados naquele SHA, sem atribuir esses PASSES automaticamente ao candidato F4.
- C0/reader003 SHA `d498504cd2c4d230088f86e04e55624bbe32df79`, tree `4f0c6360d429507af1946a094c27b790c9894477`.
- C1 grafo escalável SHA `4764eb0ebb38cd272b1a5e5fafbb103e72b8e105`, tree `1ba41dd01b118a008ca33061131e9181a2600548`.
- F3B tabelas SHA `72118073cc72b4d3cdca21fcc64c18cf742ae384`, tree `ac3dec6de49bf55dc25115bfb35dd364b1a2f690`.
- C2 original PR #18 SHA `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`, seu manifesto histórico; sucessor leitor real v5 inicial `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, **C2-D final** a resolver do handoff por SHA/tree/parent, com C2-B blob provenance e decisão de identidade se houver.
- C3 real-v5 candidato integrado: **SHA FINAL e todos os pais exatos**, código/contratos e CI focal aprovados. Sem C3 congelada/sem revisão, não alterar guard; entregar `F4_C4_INPUT_BLOCKED_EXACT`.
- F1 G1 sanitizada `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, F2 ADR técnica `c3ea1e82938fd61cc5a22fee973352715a5bb527` `APPROVED_SCOPED` via comentário 6539419419 e plano AP04-POR-v1.0-draft G4/G5/G6.

Avaliar topologia sem assumir que diferentes branches têm um único ancestral linear. C3 pode ter importado blobs por SHA ou feito merge técnico dentro da integração; verificar honestamente parentage/ancestry por fonte e objetos, sem alegar Git parent que não existe. Não fazer merge em main, force-push, rebase ou apagar histórico para silenciar testes.

## 2. Ownership exclusivo C4

**Pode alterar somente**:
- scripts/checkers/dispatchers de CI necessários e justificados sob `scripts/qa/`, com novos testes prefixados `atlas_parity04_f4_c4_`;
- workflows existentes só quando indispensável à qualificação de sucessão exata, sempre mantendo suas proteções e todos os triggers relevantes;
- workflow adicional dedicado `atlas-parity04-f4-global.yml` se necessário;
- documentos e recibos novos `docs/missions/atlas-parity-04/f4-c4-ci/`.

**Não alterar:** código do leitor C2/parser/sandbox, componentes F3A/F3B, shell C3, Catalog/SDK/servidor funcional, protocolo, schema reader003 histórico ou adendo C0, ADR/plan/GATES, manifestos originais C1/C2/C3/C4/AP04/F1/F2/F3A/F3B/C0/C2-D e fonte R4. Só os guardas/CI necessários com novos testes adversariais. Um arquivo inesperado requer ownership formalizado ANTES da escrita.

A/QA Git-ancestry e guard, B workflows/testes/instalação, C revisão independente somente leitura no SHA terminal, até três subagentes nativos REAIS quando disponíveis, coordenador único writer. Se não houver subagentes, realizar engenharia sequencial e registrar revisão independente pendente sem simulação.

## 3. Guard fail-closed de sucessão F3/F4

Modelar epochs C4 → AP04 → F1 → F2 → F3A/C1 + F3B + C0 + C2-A/B/D → C3 integrado → C4 reparo, sempre fixando SHAs, trees, parent(s), OIDs, caminhos exatos e modos. Não inferir autorização pela branch, prefixo ou extensão do path. Em cada commit intermediário verificar alterações efetivas, inclusive alterações indevidas revertidas depois, não apenas árvore final.

- Preservar auditor histórico P06 `scripts/qa/atlas_parity02_p06_audit.py` com sua negação original da ADR-0003 histórica e todos os demais paths protegidos. A exceção documental AP04 fica limitada ao blob/path autorizado, nunca `docs/architecture`.
- `scripts/qa/atlas_parity04_doc_ci.py` e os guards C4/P03/Spec Kit continuam detectando alterações indevidas de `INPUTS`, `COMPOSITION`, `P03_C4_ADAPTERS`, `ASSETS`, Caderno/reader003 e manifests. Novos componentes só entram por autorização complementar **exata por arquivo, blob, dono e epoch**, sem manifesto rehashado para permitir mutar o guard.
- Manter checks de SDK/wheel independente R4, Code/Spec Kit 1.2.3 e runners instalados fora do checkout, Caderno sem O1, novas ferramentas externas fora do viewer, sem criar endpoints File API no servidor.
- Triggers CI não podem ser filtrados para evitar falha. Proibidos `paths-ignore`, `continue-on-error`, `|| true`, `if: false`, desativação/silenciamento de suites, pin mutado para verde, branch-name dispatch (`github.head_ref`/`github.ref_name`) como autorização de mudanças.
- Se o C2-D incluiu um merge de controle não previsto, exigir contract/versionado e provas adversariais antes de admiti-lo; não aceitar "porque a branch se chama integrate".

## 4. Testes adversariais indispensáveis

Em repositórios sintéticos temporários:
1. PASS da composição real SHA-bound e da coleção de paths declarados (Caderno + O1 externo + O3 opcional); atributos/modes/parents verdadeiros.
2. RED de documento ou módulo extra não autorizado, symlink, rename, modificação transitória revertida, manifesto antigo adulterado, guard semanticamente relaxado e overlay recalculado.
3. RED da alteração de ADR 0001/0002/0003, reader003 histórico, adendo C0, Caderno schema/contexto, ASM/P03 adapters, assets, workflow pins, `AGENTS.md`, constituição, datasets e source credentials.
4. RED de pass por nome parecido da branch, ref/parent falso, runtime R4 importado no wheel, endpoint HTTP legado, URL/HTML executado, File API enviando payload à rede.
5. RED de perda de 223 identidades herdadas da F2, regressões F3A (22 antigos, 30 finais), F3B (24 testes com 380 IDs de recibo por célula) e suites C2/C3; **não somar 380 IDs de controle como se fossem 380 métodos pytest independentes**.
6. RED de source_key inferido como native_id, binding_gap transformado em RESOLVED, 28 RF não admitidas promovidas, tabelas desvinculadas perdidas, File promovido a Product ou UNKNOWN_UPSTREAM virando denominação global.
7. RED de limite 600.000 valores escondendo payload permitido, quota depth20/32MiB/10k nós/100k relações, TTL expirada ainda navegável e parser aceitando chaves duplicadas.
8. No caso de ação incompatível com a autorização ARC-09, encerrar bloqueio exato sem ajustar contrato anterior.

Testar Python normal e `-O` sem assert de segurança removível; browser real Windows/Ubuntu com 1440/390/320 CSS px, pan/zoom/teclado, tree v5 2911/1595, 5 tabelas/152 linhas de valores INVENTADOS, export, session expiry, CSP e Caderno baseline. Nenhum dado privado/RF literal real no CI público.

## 5. Evidência terminal, revisão e estados

Exigir seis workflows globais qualificados F2 por SHA **no mesmo HEAD terminal novo**:
`ATLAS021 candidate verification`, `ATLAS-PARITY-02 P06 frozen-boundary QA`, `ATLAS-PARITY03 P03 isolated qualification`, `ATLAS-PARITY-03 C4 full composition`, `ATLAS003 Spec Kit contract checks`, `ATLAS-PARITY-04 documentation successor`;
mais workflows F3A/F3B/C2-D/C3/C4 aplicáveis. Todos executados, não omitidos, com Windows/Ubuntu e normal/-O conforme contratos; zero erros/falhas, skips explicitamente por plataforma quando aceitáveis. Preservar os 223 IDs herdados e conjuntos novos sem omissão; checar logs, JSON/JUnit/artifacts/screenshots e SHA por API.

CI global **não** prova hard budget da máquina LOCAL nem que um RF real foi exibido; G4 depende do L1 com autorização de fonte e OS, G6 da F5 (autorização própria). O estado `F4_G5_INTEGRATION_CI_QUALIFIED_HOST_GATE_DEFERRED` é técnico, não uma aprovação científica ou release.

Revisão independente real sem autoria deve cobrir SHA final, todos os workflows/jobs, bytes/manifests, oráculos negativos, inexistência de bypass e efeitos no viewer. Se um commit posterior adiciona recibos, repetir CI e revisão do HEAD final. Persistir código de guard/QA e `RESULT.md`, `INPUT-SHAS.json`, `SUCCESSION-CONTRACT.md`, `REPAIR-OWNERSHIP.json`, `NEGATIVE-TESTS.json`, `CI-EVIDENCE.json`, `INDEPENDENT-REVIEW.md`, `HANDOFF.json`, `MANIFEST.sha256` sob F4-C4 com SHAs/trees/parents.

Se faltarem jobs/gates, `F4_C4_CI_BLOCKED_EXACT` com workflow/job/SHA/finding e menor ato seguro. Não finalizar com recomendações se código e tests seguros forem executáveis. Não alterar R4, acervo privado, AP04-POR, regras ARC-09, release, deploy, promoção, migração, merge main, limpeza ou iniciar F5/F6.

**END-OF-AP04-F4-C4-PROMPT — COMPLETE**
