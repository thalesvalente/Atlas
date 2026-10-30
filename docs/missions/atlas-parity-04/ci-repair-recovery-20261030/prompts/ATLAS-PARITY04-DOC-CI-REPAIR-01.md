# ATLAS-PARITY04-DOC-CI-REPAIR-01 — correção restrita dos gates de sucessão documental da PR #14

`orq.phase@llm-sec,agentic-pac/seai.qa:`

**Ambiente:** CHAT com GitHub e GitHub Actions conectados, ou Codex com acesso efetivo ao mesmo repositório remoto. Sem acesso ao host Windows ou ao acervo privado.  
**Esforço a selecionar pelo operador na interface:** **Max**; utilizar **Extra High** se Max não estiver disponível. O agente não altera o seletor e registra `REASONING_EFFECTIVE=UNVERIFIED` quando não o observa.  
**Repositório único:** `thalesvalente/Atlas`.  
**PR de destino, já existente:** [Draft #14](https://github.com/thalesvalente/Atlas/pull/14).  
**Branch única para escrita:** `docs/atlas-parity04-plan-of-record-20261030` — não criar branch integradora paralela, worktree, clone ou checkout adicional.  
**Resultado-alvo:** `AP04_DOCUMENTATION_CI_QUALIFIED` (apenas CI documental/engenharia; não aprova ADR-0003, implementação, merge ou promoção).  
**Pode começar agora:** sim; **não** começar a implementar a compatibilidade legada da AP04 nesta missão.

## 1. Contexto e identidades fixadas

- **Baseline C4 intocada:** SHA `72d9b94e613a57c82a5afd309796f44b271e2185`, árvore `0a622663ca40232d6143659f82cfe9ce43702e90`; PR Draft #13. A C4 passou seis workflows, 31/31 jobs e 168 testes por célula Windows/Ubuntu × normal/`-O` no próprio SHA.
- **HEAD documental original da PR #14:** SHA `c25d37998dac7174067a2819391f3af1625f96dc`, árvore `e6eacdd02a329f88bc0dd656523b84a8fec9217e`; parent direto C4, **nove arquivos novos sob `docs/`**, sem código de produto ou protocolo. Conferir esse conjunto por Git, não presumir que a branch continua parada.
- **Plano de referência:** `docs/missions/atlas-parity-04/README.md`, `DECISION-REGISTER.md`, `ACTION-PLAN.md`, `PARITY-MATRIX.csv`, `RESULT-REVIEW-TEMPLATE.md`, `INTEROPERABILITY-GUARDRAILS.md`, `EVIDENCE-REGISTER.md`, `GATES.json`; ADR proposta em `docs/architecture/ADR-0003-legacy-compatibility-proposed.md`.
- **Aceite anterior:** ADR-0002 v1.0 foi aceita como **direção de estabilização** na PR #5; isso não significa release, promoção, ciência ou aprovação da ADR-0003. Constituição **ARC-01–09**, especialmente ARC-04/05/07/09, continua vinculante.
- **Registro do diagnóstico já publicado:** [comentário da PR #14](https://github.com/thalesvalente/Atlas/pull/14#issuecomment-6514775335).

### CI observada no HEAD documental original

| Workflow | Run | Estado | Falha principal |
|---|---|---|---|
| `ATLAS021 candidate verification` | `41001137694` | **SUCCESS** terminal | Nenhuma neste run; não usar como prova dos outros três |
| `ATLAS-PARITY-02 P06 frozen-boundary QA` | `41001137728` | **FAILURE** | `UNEXPECTED_PROTECTED_FILE` para `docs/architecture/ADR-0003-legacy-compatibility-proposed.md` |
| `ATLAS-PARITY03 P03 isolated qualification` | `41001137738` | **FAILURE** | Seleção incorreta do modo por nome da branch; `P03 manifest entry changed: tests/viewer/test_atlas_parity02_p03_harness.py`, além dos checkpoints decorrentes |
| `ATLAS-PARITY-03 C4 full composition` | `41001137742` | **FAILURE** | `C4 manifest must cover every authored path, with no arbitrary exclusions` |

Os runs devem ser reconsultados somente na abertura/fechamento e após eventos relevantes, sem polling contínuo. Não atribuir resultados de um SHA a outro.

## 2. Diagnóstico técnico obrigatório antes de editar

Inspecione integralmente os arquivos reais e a lógica dos controles, em particular:

- `scripts/qa/atlas_parity02_p06_audit.py`: `PROTECTED_PREFIXES` inclui `docs/architecture/`, e uma nova ADR sem autorização exata é recusada como `UNEXPECTED_PROTECTED_FILE`. **Isso é uma proteção correta que precisa continuar funcionando.**
- `scripts/qa/atlas_parity03_c4_ci.py`: função `inputs()` compara `MANIFEST.sha256` C4 com todos os paths de autoria desde o commit de composição `c120f8ae9e455e19b4e0bcd35f47ec0fd7a0117c`. Os nove documentos AP04 são sucessores da C4, não autoria retroativa da C4. O manifesto C4 original não deve ser reescrito para fingir que já cobria esses documentos.
- `scripts/qa/atlas_parity03_p03_ci.py`: seu modo P03 isolado exige igualdade literal com os arquivos congelados e `VISIBLE_IN_MAIN_APP=false`. A C4 adaptou **exatamente um teste** de isolamento P03 para comprovar a composição autorizada; os outros arquivos continuam congelados. A sucessora documental não pode voltar ao contrato de P03 isolada nem permitir adaptações novas não autorizadas.
- `.github/workflows/atlas-parity03-p03-gates.yml`, `.github/workflows/atlas-parity02.yml`, `.github/workflows/atlas021.yml`, `.github/workflows/atlas003-speckit.yml` e `.github/workflows/atlas-parity03-c4.yml`: alguns dispatches escolhem o controle C4 por **igualdade com o nome da branch**, e não por ancestralidade/escopo/bytes. Isso funciona na branch C4, mas não necessariamente em sucessoras documentais.
- `scripts/qa/speckit_audit.py`, `tests/qa/test_atlas_parity03_c4_audit.py`, `tests/qa/test_atlas_parity02_p06_invariance.py` e os testes de auditoria: entender quais negativas devem continuar RED.

Confronte os logs do GitHub por job/step e classifique cada finding como: `FROZEN_BOUNDARY_EXPECTED`, `SUCCESSOR_DISPATCH_BUG`, `MANIFEST_SCOPE_MISMATCH`, `REAL_REGRESSION` ou `UNKNOWN`. Não confundir falha do contrato de validação com autorização para eliminar a validação.

## 3. Política de implementação e ownership

**Único integrador/escritor responsável** pela branch da PR #14. Use até três subagentes nativos reais, se disponíveis, com missões exclusivas e handoffs verificáveis:

1. **Contrato e auditoria:** analisar o P06/Spec Kit, propor/aplicar validação explícita da nova ADR e testes adversariais; propriedade exclusiva dos scripts/testes novos do guard documental.
2. **CI e sucessão:** analisar e corrigir o dispatch P03/C4 e a associação de manifests, com ownership dos workflows sob coordenação do integrador; paths sobrepostos são alterados somente pelo integrador.
3. **Revisão independente:** leitura e contraprovas no SHA de código final, sem autoria no delta; deve buscar bypass, promoção de ADR e confusão de evidências.

Se não houver subagentes reais, execute sequencialmente e declare que **QA nativa independente não foi realizada**; não simule paralelismo ou revisão.

**Alterações autorizadas:** o conjunto mínimo de scripts de auditoria, testes negativos, workflows e recibos próprios necessários ao reparo. Os nove documentos originais AP04 devem permanecer byte-idênticos, a menos que exista erro documental concreto e a alteração seja registrada e justificada na matriz de decisões. Preferir criar um guard de sucessão documental independente, com lista de paths e hashes exatos, a generalizar permissões dos auditores históricos.

**Não alterar:** runtime, `packages/protocol/**`, schemas, contextos, SDK, `packages/atlas/src/**`, fontes/fixtures científicas, `AGENTS.md`, constituição, ADR-0001/0002, objetos ou branches C1/C2/C3/C4, SHA/manifestos históricos, dados do P04, ambiente local ou pipeline R4.

Se for demonstrado que um requisito não pode ser atendido nesse ownership, **pare o ponto específico e registre mudança de plano justificada**, referenciando `AP04-POR-v1.0-draft`, o impacto, alternativas, decisão necessária e revisor. Não faça alteração arquitetural unilateral.

## 4. Correção exigida — sucessor documental verificado, não bypass

### A. Guard documental com escopo exato

Implemente uma comprovação **fail-closed** do delta sobre a baseline C4:

1. `HEAD` é descendente do C4 congelado e a árvore de C4 está íntegra.
2. Os nove documentos originais publicados em `c25d37998dac7174067a2819391f3af1625f96dc` têm **identidade de blob/bytes e caminhos exatos**; a ADR-0003 continua `PROPOSED_NOT_APPROVED`.
3. Cada arquivo adicional introduzido **pela própria correção da CI** tem path, propósito e hash manifestado sob propriedade explícita, sem herdar automaticamente uma exceção genérica para `docs/**`, `.github/**` ou `scripts/**`.
4. Nenhum arquivo antigo de C4, governança, protocolo, testes ou fixtures foi removido, trocado ou adicionado em área protegida fora da autorização específica. A verificação examina o diff completo e também **adição/remoção/modo/symlink**, não só edições de texto.
5. Verificações de Caderno, fonte, semântica, contratos e versão permanecem independentes; uma ADR **proposta** pode ser armazenada e versionada, mas não vira ADR ratificada ou alteração do contrato.
6. O guard registra `tested_sha`, `tested_tree`, `base_sha`, `baseline_doc_sha`, manifesto/entry hashes, paths autorizados e rejeitados, `status`, e limitações em JSON/JUnit.

A exceção para `docs/architecture/ADR-0003-legacy-compatibility-proposed.md` deve ser **exatamente esse path, com conteúdo/identidade pinados e prova de ancestralidade**, sem liberar outras ADRs, todas as ADRs futuras ou qualquer arquivo sob `docs/architecture/`.

### B. Manifestos históricos imutáveis + overlay documental

- Preserve byte a byte os manifests e handoffs originais C1/C2/C3/C4.
- Diferencie **autoria de C4, congelada até `72d9b94e…`**, de **documentação sucessora AP04** (e dos controles específicos de CI desta missão).
- Registre uma trilha suplementar versionada e verificável da documentação nova. A origem deve ser uma baseline concreta, nunca `git diff` contra uma branch que esteja em movimento.
- Corrija `C4 manifest must cover every authored path` por uma classificação documentada de overlays com **completude**, mantendo negativas para arquivo novo arbitrário, exclusão de linha do manifesto, hash divergente, documento antigo alterado e alteração de runtime.
- Não reescreva o manifesto C4 como se os nove documentos tivessem participado dos testes da C4 original.

### C. Dispatch dos gates por identidade real

- A escolha de modo C4/P03 deve decorrer de **ancestralidade e comprovação exata dos inputs congelados e das adaptações já autorizadas**, não apenas da string `github.head_ref` ou de `github.ref_name`.
- Uma sucessora documental **não deve executar o gate isolado P03 como se estivesse na P03 original**, mas deverá comprovar que P03 foi incorporado na C4 e que a única adaptação congelada do teste corresponde ao hash C4 autorizado.
- Para alteração de produto ou de input que não passe o guard, a execução deve ser **RED**, não silently default to success.
- Nenhuma classificação baseada apenas em `docs-only`/nome de branch, ou `paths-ignore` amplo, pode deixar alteração protegida sem auditoria. Se houver roteamento de workflows, mantenha um verificador estrutural obrigatório capaz de detectar mudança indevida em qualquer arquivo protegido ou de runtime.
- As CI de produto e browser, quando executadas no novo HEAD, devem produzir **evidência desse HEAD**, sem transportar resultados da C4 ou da P03.

### D. Contraprovas obrigatórias

Crie testes negativos independentes, preferencialmente em repositório Git temporário **dentro do runner de CI** ou sobre fixtures sintéticas, nunca na worktree real do operador:

- Edição, remoção ou symlink de `ADR-0003` → RED.
- Inclusão de `ADR-0004` ou mudança em `ADR-0001`/`ADR-0002` → RED.
- Mudança ou adição em `packages/protocol/**`, contextos/schemas, `.specify/memory/**`, skills, fixtures de fonte e `AGENTS.md` → RED.
- Mudança indevida no runtime C4, no teste P03 congelado ou no asset allowlist → RED.
- Alteração de documento fora dos nove paths AP04 e fora da lista específica de CI → RED.
- Modificação do manifesto suplementar, exclusão de entrada ou divergência de hash → RED.
- Branch diferente com mesma string parcial ou ancestry sem os bytes corretos → RED.
- Documentação AP04 original intacta, C4 intacta e controles autorizados pinados → PASS.

Não enfraqueça asserções, não use skip/xfail para encerrar os controles, não altere pins de ferramentas para silenciar CI, não use `continue-on-error`, `if: false`, `|| true`, bypass por workflow, nem exija aprovação inexistente da ADR-0003.

## 5. Testes e fechamento por SHA

1. Faça preflight Git e publique a implementação apenas na branch de PR #14, com commits rastreáveis **fast-forward**, sem `force-push`, rebase ou merge em `main`.
2. Execute testes focais do guard e negativos em Linux e Windows, normal e `-O`, sem skips.
3. Reexecute os três workflows que falharam (`41001137728`, `41001137738`, `41001137742`) via novos runs disparados pelo(s) commit(s) novos, **não reruns dos SHAs antigos**. Requalifique também `ATLAS021` no SHA final. Se for relevante ao novo gate, inclua Spec Kit 1.2.3 e o contrato P01/C3.
4. Exija CI terminal `success` nos workflows aplicáveis ao **HEAD exato** da PR #14. Se um workflow legado tiver sido substituído por roteamento seguro, documente equivalência funcional e negativos executados; não declare que um job que não rodou passou.
5. Preserve a regressão do C4: o número observado de casos por célula deve ser registrado e o conjunto original de 168 IDs não pode desaparecer silenciosamente. Executar browsers reais de produto/composição onde exigidos, sem atribuir prova de outro SHA; distinguir documentação, produto e host local.
6. Obtenha parecer independente no SHA final, incluindo o delta dos últimos recibos e a ausência de novas permissões arquiteturais. PR continua **Draft**.
7. Em um único fechamento, reconcilie branch HEAD, árvore, PR, CI, manifests e revisão; sem polling contínuo e sem declarar PASS antes de todos os gates terminarem.

## 6. Entregáveis obrigatórios

Registrar em `docs/missions/atlas-parity-04/ci-repair/` (com seus próprios paths e hashes no overlay, sem contaminar os nove documentos originais):

- `RESULT.md` — causas, alterações mínimas, antes/depois e limitações;
- `INPUT-SHAS.json` — baseline C4, objeto AP04, head final, trees e hashes;
- `CI-ROOT-CAUSE.md` — diagnóstico por workflow/job/step e mudança correspondente;
- `SUCCESSOR-DOC-CONTRACT.md` — regra de autorização por ancestry/paths/hashes, e o que permanece protegido;
- `NEGATIVE-TESTS.json` — enumeração e execução das contraprovas, com resultados por SHA;
- `CI-EVIDENCE.json` — workflow IDs, run IDs, jobs, conclusão e SHA exato;
- `DECISION-COMPLIANCE.md` — confronto explícito com D-001–D-020, ADR-0001/0002, ADR-0003 ainda proposta, HL7/FHIR e os gates G0–G9;
- `INDEPENDENT-REVIEW.md` — revisor sem autoria ou limitação declarada;
- `HANDOFF.json` e `MANIFEST.sha256` — identidade, paths, SHA-256, próximos atos.

Documentar qualquer alteração de plano necessária antes de executá-la, com motivo, impacto em dependências e funcionalidade, alternativas e aprovação aplicável. **Não alterar os critérios de paridade PAR-001–PAR-015 para concluir esta tarefa.**

## 7. Critérios de término

### `AP04_DOCUMENTATION_CI_QUALIFIED`

Somente se: a PR #14 tiver HEAD final identificado, autorização AP04 estrita e verificável, ADR-0003 ainda PROPOSTA, todas as entradas históricas relevantes preservadas, auditorias e contraprovas negativas passando, workflows requeridos `success` no novo SHA, revisão independente efetiva sem findings bloqueantes, documentação de rastreabilidade completa e **nenhuma alteração de produto, protocolo, dados, acervo, aprovação ou destino Git**.

### `AP04_DOC_CI_BLOCKED_EXACT`

Caso persistam falhas, registre o job/step/path, natureza da falha, risco de mudar o contrato, entregas realmente concluídas e o menor ato necessário. Não encerrar com auditoria genérica ou uma lista de planos; corrigir tudo que seja seguro e autorizado nesta missão.

**Não iniciar AP04 F1–F6 após encerrar esta execução.** A próxima fase será autorizada separadamente. Não criar worktrees/clones, operar o host, migrar dados, alterar R4, fazer merge, release, deploy, promoção ou apagar experimentos.