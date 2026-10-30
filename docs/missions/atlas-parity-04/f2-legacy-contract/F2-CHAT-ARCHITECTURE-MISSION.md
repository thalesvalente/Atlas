# AP04-F2-CHAT-LEGACY-COMPAT-CONTRACT-01 — contrato efêmero e decisão ARC-09

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub/GitHub Actions. Sem acesso ao host, drives ou corpus privado.  
**Raciocínio que o operador seleciona:** **Extra High** (ou esforço superior efetivamente disponível); não presumir nem registrar escolha não observada.  
**Git único:** `thalesvalente/Atlas`; branch exclusiva **já existente** `docs/atlas-parity04-f2-legacy-contract-20261030`, sem worktrees/clones adicionais.  
**Objetivo:** `F2_ARCHITECTURE_DECISION_READY_FOR_HUMAN_REVIEW`. Isto NÃO significa aprovação de ADR-0003, G4 PASS ou implementação de compatibilidade.  
**Natureza:** **documentação e desenho técnico, não implementação**. Somente novos documentos em `docs/missions/atlas-parity-04/f2-legacy-contract/`. Todos os arquivos do produto, protocolo, workflows, testes, planos e ADRs anteriores são somente leitura.

## I. Baseline obrigatória

Antes do trabalho, reconcilie os objetos Git por SHA e árvore:

- AP04-POR-v1.0-draft, PR #14 qualificada, HEAD `47c94d27aeb7717eebb30804f01cd2cd33507c8a`, Draft.
- F1 `F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED`: `a237f446e54927eeeda8ed5e8e9daa83ee09dcb7`, tree `e0626cd274948a9303774593e20ca05fc1d32d62`, parent `e140d973fd4cbc4547046f25fd620166662c5004`.
- C4: `72d9b94e613a57c82a5afd309796f44b271e2185`.
- Missão F2: use o commit exato desta branch, sem alterar ou rebasear as origens.

Leia integralmente, por SHA:

- `.specify/memory/constitution.md` ARC-01–09, `docs/architecture/ADR-0001-atlas-protocol-producers-storage.md` e `ADR-0002-protocol-candidate.md`. ADR-0002 recebeu aceite posterior **como direção de estabilização**, não como release.
- `docs/architecture/ADR-0003-legacy-compatibility-proposed.md`: `PROPOSED_NOT_APPROVED`.
- `docs/missions/atlas-parity-04/ACTION-PLAN.md` F2/G4, `DECISION-REGISTER.md` D-001–D-020, `PARITY-MATRIX.csv`, `GATES.json`, `RESULT-REVIEW-TEMPLATE.md` e `INTEROPERABILITY-GUARDRAILS.md`.
- F1: `f1-legacy-inventory/SANITIZED-HANDOFF.json`, `SANITIZED-HANDOFF.md`, `RESULT-REVIEW.sanitized.md`. Não solicitar os recibos privados quando o sanitizado for suficiente.
- Contrato **atual** `specs/003-producer-selective-preview/contracts/reader.md`: Atlas aceita **exclusivamente snapshots Caderno 0.1.0a1**.
- C4: `packages/atlas/src/atlas_viewer/catalog.py`, `server.py`; Caderno: `packages/protocol/src/caderno_protocol/read_model.py` e `docs/protocol/0.1.0a1.md`, todos em leitura.

A nova via legada **não é** automaticamente compatível com o contrato 003. Quem propõe abrir entrada adicional no viewer deve registrar desvio potencial e o gate de ARC-09, não usar o consentimento funcional do usuário como aprovação arquitetural.

## II. Evidência F1 que não pode ser reinterpretada

F1 verificou em três fontes preexistentes autorizadas uma projeção histórica, com leitura inerte, sem alteração de bytes, tamanho ou mtime. **Fonte qualificante:** 159 records; cinco result_tables com 39, 85, 28, 0 e 0 linhas (152 no total); UMA RF real comparada literalmente, com ID, núcleo/módulo, título, descrição e critérios de aceite; categoria originalmente ausente.

Estrutura observada: 2911 nós de linhagem, 1595 arestas, **858 parent keys explícitos resolvidos**; 162 product_items, dez product_groups, 80 resource_documents, 24 dossier_assessments, quatro dossier_packages.

**Lacunas materiais que o contrato deve preservar:**

- Quatro das cinco tabelas sem `record_id` resolúvel.
- 28 linhas `UNADMITTED_NATIVE_RF` com `native_id=null`; não promover à admissão.
- A RF amostrada tem vínculo declarado com execução externa isolada, mantendo `binding_gap`; **NÃO há caminho contínuo** árvore→execução→RF.
- 22 endpoints nulos, 75 relações declaradas não resolvidas, 50 colisões declaradas, 40 grupos de triplas repetidas (41 ocorrências excedentes).
- População global `UNKNOWN_UPSTREAM` e `GLOBAL_UNPROVEN`; upstream bruto não foi relido. RNF/RES não foram comprovadas.
- O gate G1 aprovou **disponibilidade de dados no escopo selecionado**, não paridade da interface.

Nenhum JSON/HTML, path, nome, ID real, RF literal, digest de fonte privada ou screenshot será copiado da bancada para o Git público.

## III. Coordenação e delegação

Execute PLAN → EXECUTE → REVIEW. Até três subagentes **nativos reais**, se disponíveis:

- **A — arquitetura e alternativas:** analisa fronteira ARC-04/05/07/09, contrato 003, Caderno e as opções de integração; propõe `ARCHITECTURE-OPTIONS.md`.
- **B — modelo e semântica:** elabora contrato neutro efêmero, identidade, órfãos, RF literais e perdas; propõe `EPHEMERAL-PRESENTATION-CONTRACT.md`, `IDENTITY-AND-LOSS-POLICY.md`.
- **C — QA independente:** somente leitura, sem autoria dos deltas; revisa fidelidade ao plano, segurança, proveniência, padrão HL7/FHIR e risco de desvio; emite findings reproduzíveis.

O coordenador é único writer no Git e integra os documentos; agentes não podem alterar mesma worktree. Sem subagentes: análises sequenciais, `NATIVE_SUBAGENTS_NOT_AVAILABLE`, **não declarar revisão nativa independente**.

## IV. Opções arquiteturais obrigatórias

Compare com vantagens, riscos, impacto em padrões, custo relativo/complexidade (sem horas inventadas), rollback e necessidade de aprovação:

1. **O1 — leitura externa explícita** de projeção legada já existente, produzindo *descriptor* de apresentação efêmero para consumo segregado. Especificar exatamente qual processo lê, qual componente recebe, como a UI visualiza e a fronteira ARC-07.
2. **O2 — transformação temporária validada para um pacote Caderno/RO-Crate conforme**, sem mover/reformatar o acervo de origem. Só chamar de Caderno conforme se *todos* os validadores relevantes passarem; listar perdas e custo da semântica.
3. **O3 — novo contrato opcional de entrada na UI** para descriptor neutro de apresentação, mantendo o SDK independente. Tratar como potencial mudança do `reader.md` Caderno-exclusivo e desvio ARC-09.
4. **O4 — viewer legado separado como contingência** e composição visual posterior, sem fingir recuperação no Atlas C4.
5. **O5 — migração completa agora ou cópia do leitor/código privado ao runtime Atlas**: fora do escopo, violação da direção D-014/015 e potencial ARC-04/07; nenhuma implementação.

**Escolha UMA arquitetura candidata** justificada e verificável. É insuficiente escrever apenas "usar um adaptador". Defina pontos de entrada/saída, consumidor, lugar de execução, tipo de artefato temporário, mecanismo de isolamento, compatibilidade com `Catalog`, `server.py`, SDK, caching/expiração, invalidação de snapshot, operação/rollback e vínculo com G4. Classifique explicitamente `RECOMMENDED_PROPOSED`, nunca `APPROVED`.

## V. Contrato efêmero (proposta, não alteração de Caderno)

Elabore a versão candidata de uma **projeção de apresentação opcional**, com schema e 2–3 exemplos **sintéticos** completos, invariantes e matriz de validação futura. Não inventar que esses exemplos vieram da F1.

Defina no mínimo:

- **Envelope:** versão, formato/perfil original declarado, fonte/snapshot com escopo, `LEGACY_DERIVED` (sem ser autoridade científica), status de validação, disponibilidade, data observada separada de data científica; SHA comprova bytes somente.
- **Identidade:** chave fonte+snapshot+ID nativo quando houver; IDs derivados de navegação são temporários, marcados `DERIVED_FOR_PRESENTATION`, nunca transformados em `native_id` ou aceitação. ID de mesmo texto em fontes diferentes não se funde.
- **Árvore:** nós, famílias e `parent_key` declarados; pertencer visualmente não implica derivação causal. Preservar nós órfãos e Run externo isolado; não inventar pais, projetos ou caminhos contínuos.
- **Tabelas:** tabela/linhas vinculadas por IDs originais explícitos, headers e valores literais inertes. Preservar ordem, tipo, precisão, unidade, ausência e categoria `MISSING` quando aplicável. Filtros e exportação futuros não podem perder dados ou executar CSV formula/HTML.
- **RF/RNF/RES:** conteúdo de domínio opcional. RF não admitida com `native_id=null` não ganha ID fictício. RNF/RES desconhecidas não são inferidas por rótulo, filename ou MIME.
- **Relações:** tipos/direção/prova; `binding_gap`, quatro tabelas sem `record_id` ligado, 28 linhas não admitidas, null endpoints, não resolvidas, colisões, repetidos e contagens devem ser representáveis. Duplicatas não fundidas silenciosamente.
- **Produtos e documentos:** File permanece File; produto exige papel/vínculo declarado. Sem abrir URI privada, arquivo arbitrário ou executar HTML ativo.
- **Cobertura:** fonte, população selecionada/carregada/visível, ausências, contagens e unidades; nunca total global inventado ou 0/0 percentual.
- **Segurança:** roots autorizadas/allowlist exata, quotas e limites de parsing, symlinks/reparse/traversal/TOCTOU, cache efêmero e identidade de snapshot, CSP/origin se HTTP for proposto. Nenhuma porta/servidor deve ser iniciado na F2.
- **Padrões:** conservar RO-Crate 1.3, Process Run 0.6 e Caderno 0.1.0a1. HL7/FHIR permanece **capacidade futura por domínio**; não impor recursos clínicos ao núcleo universal nem declarar FHIR implementado.

Defina também contratos de consumo para as fases futuras, **sem implementá-las**: F3A (árvore SVG interativa, expandir/recolher, zoom/pan/minimapa e teclado), F3B (RF literal com filtro, detalhe e exportação), F4 (integração), F5 (browser com fonte privada autorizada). A futura UI deve distinguir pertencimento organizacional, relações de linhagem e menções neutras.

## VI. ARC-09, ADR-0003 e solicitação humana

Produza `ADR-0003-v0.2-CANDIDATE.md` **dentro do workstream F2**, sem tocar o arquivo histórico em `docs/architecture` nem alterar ARC-01–09, ADR-0001/0002, GATES.json ou AP04-POR.

Inclua uma matriz de impacto: contrato 003 Caderno-exclusivo; C4 Catalog/servidor; protocolo/SDK/contexto/schema; isolamento de produtor R4; privacidade/licença; dados privados; interfaces UI; segurança; HL7/FHIR futuro.

Se a alternativa adiciona entrada ao viewer ou move leitura legada para runtime, classifique **`ARC09_APPROVAL_REQUIRED`**, salvo demonstração técnica fundamentada e revisão realmente independente provando compatibilidade com a arquitetura vigente. Registrar exatamente o que seria alterado, o risco, alternativas, rollback, desvio de plano se houver e o que fica inalterado.

O documento `DECISION-REQUEST.md` deve apresentar **uma pergunta objetiva para aprovação humana vinculada à versão e SHA do pacote**. Não inventar aprovação por CI, comentário de agente, silêncio, publicação ou autorização funcional anterior.

Se F2 descobrir necessidade de mudar a ordem F0–F6, os critérios PAR/G0–G9 ou as proteções, produzir `PLAN-DEVIATION-REQUEST.md` com justificativa, opções, riscos e solicitação de aprovação; **NÃO executar a mudança**.

## VII. Contraprovas/documentação de testes futuros

Especificar, sem afirmar execução real de testes:

- colisões `source_id/native_id`; IDs derivados que não podem virar nativos;
- 22 endpoints nulos, 75 arestas declaradas não resolvidas, 50 colisões, duplicatas;
- quatro tabelas sem `record_id`; 28 RF sem `native_id`;
- ausência de categoria, campos nulos, strings numéricas, precisão/unidades;
- HTML/JS hostil, path traversal, symlink/reparse, URI maliciosa, CSV injection;
- fonte alterada após leitura, pacote inválido, snapshot reindexado e stale links;
- `UNKNOWN_UPSTREAM`, GLOBAL_UNPROVEN, ausência de aprovação científica;
- implementação HL7/FHIR não existente; não aceitar conformidade por rótulo;
- C4 funcionando sem sidecar e protocolo independente de R4.

Cada negativa terá **oracle futuro** e vínculo PAR/G4/G5, sem inventar execução no CHAT.

## VIII. Entregáveis e validação

**Escrita permitida exclusivamente no workstream** `docs/missions/atlas-parity-04/f2-legacy-contract/`:

1. `RESULT.md`
2. `INPUT-SHAS.json`
3. `ARCHITECTURE-OPTIONS.md`
4. `EPHEMERAL-PRESENTATION-CONTRACT.md`
5. `IDENTITY-AND-LOSS-POLICY.md`
6. `ADR-0003-v0.2-CANDIDATE.md`
7. `SECURITY-AND-INTEROPERABILITY.md`
8. `PARITY-TRACEABILITY.md`
9. `DECISION-REQUEST.md`
10. `INDEPENDENT-REVIEW.md`
11. `HANDOFF.json`
12. `MANIFEST.sha256` (sem se incluir)

Não escrever no código do Atlas, protocolo, R4, specs/004 compartilhados, workflows, testes ou PR #14. Nenhuma mudança do contrato 003 nesta F2.

Valide: todas as decisões D-001–D-020 confrontadas, PAR-001/002/003/004/005/006/007/011/012/013/015 preservados; exemplos sintéticos; inventário de campos/estados sem perda; nenhuma informação privada; ADR continua PROPOSTA; SHA/tree/parent dos inputs e outputs verificáveis; diff documental e sem caminhos fora de ownership.

Revisão independente deve buscar também a contradição entre **Caderno exclusivo** e **novo descriptor de apresentação**. Se houver findings, corrigir somente a documentação e revalidar no SHA final; não simular parecer.

**Publicação Git-first:** commit normal na **branch F2 existente**, por fast-forward, com SHA/tree/parent e links. O usuário trabalha em vários chats; não exigir download de ZIP. Uma eventual PR Draft de revisão documental deve declarar base e gate, sem alterar PR #14 ou fazer merge. Não alegar CI que não foi executada.

**Sucesso:** `F2_ARCHITECTURE_DECISION_READY_FOR_HUMAN_REVIEW` = contrato, alternativas, riscos, ADR candidata e pergunta objetiva revisados, publicados por SHA. **Não equivale a** `ADR_0003_APPROVED`, G4 aprovado ou autorização de F4.

**Falhas honestas:** `F2_REVIEW_PENDING` (sem revisor independente), `F2_INPUT_BLOCKED_EXACT` ou `F2_CONTRACT_BLOCKED_EXACT` com causa específica e menor ato. Não encerrar só com recomendações quando a produção documental segura estiver disponível.

**Proibido:** iniciar F3A/F3B/F4/F5/F6, implementar adaptador/UI, abrir fonte privada a partir do CHAT, criar clone/worktree, mover dados, alterar R4, Caderno, HL7, pins/manifestos, merge/release/deploy/promoção/limpeza. Continuar todo o trabalho documental compatível com o plano existente.
