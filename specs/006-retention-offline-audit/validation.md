# Validação e crosswalk — N02 + N03

Este documento registra trabalho que pode ser conferido antes da publicação.
O recibo P00_HANDOFF na PR de integração registra o SHA/tree terminal, Actions e
Codex Review após sua execução. PASS de N02 ou N03 individual não qualifica o composto.

## Reuso e recuperação

N02 não foi encontrada nas fontes Git verificadas: 38 branches, 33 PRs e 270 commits;
limite descrito em evidence/recovery.json. Implementação técnica N02 publicada como
`ddf866ffb3eda09f5185a007a4c7a24a31eac57e`, tree `c399c521ea401c14361aa254bfab745034f88878`,
parent F005 `46e18bd5c90b922b78cf6731f83ceedc4c09df85`.

N03 foi verificada em `209b3f1fc9ab478c8d2adb84e0bb61f22106ad79`, tree
`748b906cab917ab2bd1cd5b15ff8d462d6b0de4a`, parent direto F005. Review concluído
sem findings: PR #34, comentário 6677298657. Seus 17 checks / 27 grupos browser foram
consultados, não reexecutados. A01 e T015 conservam seus SHAs e aceites originais;
T015: PR #33, comentário 6676134041. O corpo antigo da PR #33 não foi modificado.

Composição Git real: cherry-pick --no-commit -x de N02 sobre N03, sem conflito;
árvore inicial de composição `05a36c0c8d327b489fd17e7b786eb469617699fc`.
Acrescentamos este fechamento documental e o handoff LOCAL antes da primeira
publicação composta. A publicação pelo conector preserva os autores das entradas,
o parent N03 e a referência explícita ao commit N02. Não houve merge de PR.

## Spec Kit real

Infraestrutura oficial 1.2.3 versionada, sem instalação local. Executados:
create_new_feature.py; setup_plan.py; setup_tasks.py; check_prerequisites.py
(--json --require-spec --require-tasks --include-tasks), feature006 explícita e
SPECIFY_FEATURE_NO_PERSIST=1. O CLI specify está ausente neste executor e seus
comandos locais são NOT_RUN. As skills plan/tasks/analyze/implement/converge são
instruções aplicadas pelo agente, não subcomandos fictícios.

Auditoria inicialmente invocada sem --allow-presentation-delta retornou FAIL por
comparar a aplicação com a baseline anterior à apresentação já aceita. Nenhum
arquivo/guard foi alterado. Reexecutada com a invocação exata do workflow existente,
`python scripts/qa/speckit_audit.py --allow-presentation-delta`: PASS; 95 originais,
28 arquivos gerenciados,10 skills e6 helpers, zero erros. Os deltas históricos admitidos
continuam limitados pelos guards e pins existentes.

Análise de especificação:10 FR / 4 SC,12 tarefas mais3 gates externos. Cobertura10/10 FR;
nenhum requisito de produto sem tarefa; ARC-01–09 conferidas. Convergência de código:
zero trabalho de implementação faltante após correções; gates terminais permanecem
externos até seus resultados verificáveis. Não editar constituição ou tasks F005 para
promover aceite de outro SHA.

| Requisito | Implementação/evidência | Tarefas |
| --- | --- | --- |
| FR-001 recuperação/reuso | recovery.json; importações F005 intactas | T001,T003 |
| FR-002 contrato lexical | validateDocuments; canonical transport F005 | T005,T006 |
| FR-003 inventário/proveniência | anchors externos; exactKeys; hashes de plano e documentos | T005,T006 |
| FR-004 contradições/obsolescência | seleção única; igualdade integral; JSON estrito | T005,T006 |
| FR-005 limites físicos | authorizedMappings, inspectedPath, relativePath | T007,T008 |
| FR-006 arquivos substituídos | readStable, fstat/chain antes dos bytes, hash e estabilidade | T007,T008,T010 |
| FR-007 proteção | parecer invariavelmente protegido/parcial; nenhuma exclusão | T005–T008 |
| FR-008 separação arquitetural | módulo tools; nenhum delta no viewer/protocolo em N02 | T002,T010 |
| FR-009 composição e SHA | Git real, workflow N02, regressões e gates externos | T003,T009–T012,G13,G14 |
| FR-010 LOCAL | contracts/local.md e LOCAL_HANDOFF.md | T002,G15 |

## Testes e revisão anteriores ao commit terminal

- RED real inicial: módulo inexistente, ERR_MODULE_NOT_FOUND, exit1; não se alega
  RED comportamental nessa primeira prova.
- N02:35/35 grupos PASS, zero skips, Node 24.22.1; log evidence/n02-domain.tap.
- Na árvore composta, prechecks N02(35), F005 domínio/UI(53), wrapper A01,2 guards
  de escopo e auditoria Spec Kit: PASS. SHA final precisa de qualificação própria.
- Revisão não autora do produto:15 contraprovas contratuais e3 trocas durante open,
  todas PASS; nos três casos de corrida, zero chamadas read e zero bytes externos.
  O ensaio inclui troca por symlink com inode distinto/igual e troca por FIFO.
- A suíte versionada cobre CLI real, bindings ausentes, duplicatas, rawJSON, tabelas,
  shared, backups, traversal, UNC/ADS, symlink/junction, hardlink e arquivos alterados.

### Findings tratados

| ID | Problema reproduzido | Correção/contraprova |
| --- | --- | --- |
| N02-SEC-01 | Maps internos sem protótipo rejeitavam plano JSON legítimo | Comparar transporte JSON do exportador; teste de ordem de chaves e roundtrip |
| N02-SEC-02 | shared:false contradizia múltiplos consumidores/categoria compartilhada | Rejeição explícita; dois testes independentes |
| N02-SEC-03 | Nomes COM/LPT com sobrescritos Windows eram aceitos no Linux | Recusa portátil; seis nomes no negativo de paths |
| N02-DOC-01 | Nome do argumento de hash confundia envelope novo com inventário histórico | HASH_N02_ENVELOPE; hashes históricos preservados em delta_provenance |
| N02-CI-01 | No Windows,11 testes físicos falharam na comparação realpath da raiz temporária, antes da leitura | Canonicalizar somente a raiz sintética recém-criada; teste explícito registra path alocado/canônico; módulo de produto e negativos de links intactos |

Nomes reservados: [documentação Microsoft](https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file).
Os testes de protótipos e shared estavam vermelhos na primeira revisão e foram
reproduzidos/verificados pelo revisor distinto do writer. Os35 testes não são sua
própria revisão independente. A matriz de autoria está em evidence/recovery.json.

### Primeira composição e correção da fixture Windows

O composto `f123ff702efdd63f8c915924145797cac9f0a0e5`, tree
`8675d5192145db8e161c61e1e8a25c67d285eefb`, teve18/19 jobs SUCCESS. O job Windows N02
[127739007717](https://github.com/thalesvalente/Atlas/actions/runs/42171149877/job/127739007717)
teve24/35 grupos PASS e11 FAIL, todos bloqueados por EXTERNAL_LINK ao conferir a raiz
temporária. Esses resultados não qualificam esse SHA para LOCAL. Codex Review desse
SHA foi concluído sem findings (PR35, comentário6678068571; recibo6678100244).

A correção atua somente na preparação do diretório sintético criado pelo próprio
teste. Não afrouxa inspectedPath, não converte paths dos dados e não amplia códigos
aceitos nos negativos. A suíte passa a36 grupos e registra os dois nomes temporários
no runner, para verificar a causa. O contrato LOCAL explicita caminhos canônicos.
O novo SHA precisa de CI e Codex Review próprios; os resultados finais ficam no recibo
P00_HANDOFF. O módulo do produto mantém SHA-256
`478803d3361acbc3832b8d91ce8709d7ad0b9737f456a3c2b42e26e2555d9ffe`.

## Gates terminais e limites

G13: Actions no novo SHA, Ubuntu/Windows, suites existentes e browser N03 pertinentes.
G14: Codex Review solicitado uma vez no SHA terminal, com tratamento de findings.
G15: contrato e recibo LOCAL com as identidades finais. Resultados no P00_HANDOFF da
PR, sem modificar o commit depois da qualificação apenas para atualizar status.

Importação privada N01-R,684 arquivos / 638 hashes, backup/restore e fechamento físico:
NOT_RUN nesta missão. A implementação/integração pronta para QA LOCAL não transfere
aceite humano nem transforma inventário parcial em prova integral. Sem merge,
release, deploy, movimentação, retirada, limpeza de worktrees ou provider.
