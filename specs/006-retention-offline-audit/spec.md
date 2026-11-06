# Feature 006 — N02, auditoria offline de retenção

**Estado:** implementação técnica em qualificação; integração/CI/review são gates separados.
**Missão:** P00 — ATLAS-N02-RECOVERY-AND-N03-INTEGRATION, 2026-11-06.

## Contexto e fontes

O operador autorizou recuperar N02 antes de implementar. A busca em 38 branches,
33 PRs e 270 commits alcançáveis encontrou o exportador F005, mas nenhum consumidor
N02. A evidência negativa é limitada às fontes disponíveis; não afirma inexistência
em um host privado. Reutilizamos F005 em `46e18bd5c90b922b78cf6731f83ceedc4c09df85`.
N03 em `209b3f1fc9ab478c8d2adb84e0bb61f22106ad79` é uma entrada independente já
qualificada, com quatro correções, 17 checks, 27 grupos browser e review sem findings.

O contrato sanitizado `ATLAS_N01_R_N02_SANITIZED/1` foi lido integralmente. Ele
explicita integridade observada por subconjunto, evidência histórica e parcial,
backup/restauração incompletos e N02_RUNTIME_IMPORT=NOT_RUN. Não contém as linhas
científicas privadas. O novo envelope LOCAL é documentado em [local.md](contracts/local.md).

## User Stories

### US1 — Confrontar plano com fonte e inventário (P1)

Como operador LOCAL, quero importar uma proposta F005 e suas referências autorizadas
sem transformar intenção em comando ou evidência parcial em aprovação.
Aceite: plano legítimo exportado por F005 é consumido; source/revision/UID/tipo/lexema,
intenção, tabela ou proveniência contraditórios são recusados; bytes de entrada não mudam.

### US2 — Conferir somente os arquivos autorizados (P1)

Como operador LOCAL, quero verificar arquivos selecionados por bindings explícitos,
sem descobrir caminhos nos dados. Aceite: arquivo regular com tamanho/hash esperado
é conferido; traversal, links, aliases e substituição são recusados; ausência de
binding/hash mantém lacuna. Dependência compartilhada e backup declarado ficam protegidos.

### US3 — Entregar parecer e sucessor qualificado (P1)

Como integrador, quero parecer reproduzível, contrato exato e prova no SHA composto,
preservando N03 e aceites anteriores. Aceite: regressões A01/F005 e browser pertinente,
CI Windows/Ubuntu e review no SHA composto, com handoff para dados mantidos LOCAL.

## Functional Requirements

- **FR-001:** recuperar código/recibos antes de implementar; não duplicar exportador F005 ou N03.
- **FR-002:** conservar atlas-retention-plan/1 e comparar todos os campos transportados com
  o exportador existente sobre um snapshot atual ancorado por hash externo.
- **FR-003:** exigir hash externo do inventário, plan_sha256, inventory_integrity,
  validation_status, evidence_scope e delta_provenance; preservar escopos N01-R.
- **FR-004:** correspondência exata e única entre seleção, itens, bindings, tipo e intenção;
  recusar JSON duplicado, UIDs ambíguos, revisões obsoletas e contradições.
- **FR-005:** resolver arquivos somente por roots/mappings explícitos do operador; recusar
  caminhos nos dados, traversal, links externos, junctions, hardlinks e aliases físicos.
- **FR-006:** leitura por descritor, regularidade/identidade antes de ler, hashes e metadados
  antes/depois; mudança observada recusa a execução sem gravar nas fontes.
- **FR-007:** manter PROPOSAL_ONLY, DELETE_AUTHORIZED=NO, proteção integral, backup não
  comprovado, dependências compartilhadas e RECOVERABLE_SPACE_UNKNOWN.
- **FR-008:** ferramenta separada de runtime/protocolo/R4/Caderno; sem rede, exclusão,
  movimentação, limpeza, inferência de filesystem ou instalação de dependência nova.
- **FR-009:** composição própria após qualificação N02/N03; preservar autoria e PRs #32–#34,
  aceites A01/T015 e testar/revisar o SHA composto sem herdar os PASS individuais.
- **FR-010:** entregar interface LOCAL e limitações explícitas sem solicitar upload do corpus.

## Success Criteria e edge cases

- **SC-001:** testes positivos e negativos sintéticos exercitam FR-002–008 e demonstram
  invariância de bytes antes/depois. JSON lexical com inteiro grande/decimal/escape permanece exato.
- **SC-002:** os cenários não comprovados retornam parecer protegido parcial ou recusa;
  nenhuma combinação de intenção, baseline ou status autoriza exclusão.
- **SC-003:** regressões e browser no composto usam SHA/tree registrados; os gates externos
  CI/review são registrados em recibo posterior sem autodeclarar execução futura.
- **SC-004:** nenhum arquivo de produto F005/protocolo ou de N03 é reescrito para implementar N02.

Limites: a ferramenta verifica o subconjunto explicitamente vinculado e fontes estáveis;
checks portáveis de identidade não equivalem a uma trava contra um filesystem hostil.
Hash não é autenticidade e snapshot fornecido pelo operador não prova atualidade global.
A aceitação privada, fechamento das dependências, backup/restore e espaço marginal continuam LOCAL.
