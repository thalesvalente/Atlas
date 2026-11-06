# Feature 007 — Binding local de propostas de retenção

**Branch** `feat/atlas-retention-binding-readonly-20261106`
**Criada** 2026-11-06 · **Entrada** P02 / ATLAS-N02
**Base** PR #33, commit `46e18bd5c90b922b78cf6731f83ceedc4c09df85`

## User Scenarios & Testing

### US1 — Conferir a seleção contra o inventário (P1)

O operador fornece o plano exportado e as evidências autenticadas do snapshot atual. Um plano íntegro vincula cada identidade selecionada ao DTO original e aos arquivos inventariados. Revisão divergente, UID duplicado, chave adulterada, identidade incompatível ou vínculo ausente rejeitam a proposta inteira.

### US2 — Inspecionar só os arquivos vinculados (P1)

O operador fornece raízes locais explícitas. A verificação lê o conteúdo dos arquivos vinculados e das cópias apresentadas como evidência. Traversal, aliases ambíguos, reparse points, symlinks, hardlinks, arquivos ausentes e substituição observada durante a leitura são recusados.

### US3 — Interpretar proteção e lacunas (P1)

O operador distingue bytes lógicos verificados, bytes protegidos e espaço potencialmente recuperável. KEEP_FULL, baseline e referências compartilhadas protegem os arquivos envolvidos. Cobertura ou backup insuficiente bloqueiam elegibilidade. Cada resultado conserva `DELETE_AUTHORIZED=NO`.

### Edge Cases

Identidade lexical com inteiros grandes e NULL explícito, linha/tabela com identidade própria, baseline conflitante, execução FAILED, cópia na mesma unidade, dependente fora da seleção, inventário parcial complementado por cadeia autenticada e troca de arquivo por conteúdo idêntico.

## Requirements

- **FR-001** Aceitar o plano `atlas-retention-plan/1` e conferir fonte, revisão, digest, snapshot, seleção, UID, tipo de DTO, identidade original, JSON lexical e intenção.
- **FR-002** Exigir evidência externa para autenticar os bytes do plano e do inventário. Aplicar atualizações incrementais com proveniência e sem sobrescrever evidência consolidada.
- **FR-003** Resolver os arquivos somente por uma referência relativa de inventário dentro de uma raiz concedida pelo operador. Inspecionar arquivos regulares e conferir a identidade e os metadados do objeto aberto.
- **FR-004** Identificar dependentes fora do lote, conflitos de retenção e cópias verificadas. Tratar resultados científicos e referências documentais como dados.
- **FR-005** Distinguir as três medidas de espaço e emitir `RECOVERABLE_SPACE_UNKNOWN` quando o espaço físico estiver indeterminado. Produzir apenas relatório local.
- **FR-006** Qualificar com fixtures sintéticas, RED/GREEN, QA adversarial, Actions autorizadas e Codex Review vinculados ao candidato publicado.

### Key Entities

Proposta Feature 005, identidade Native View, segmento de inventário autenticado, vínculo DTO–arquivo, raiz autorizada e relatório de verificação.

## Success Criteria

- **SC-001** O plano público exportado pela Feature 005 passa sem reescrita.
- **SC-002** Todos os negativos de identidade, integridade e filesystem encerram com erro e mantêm `DELETE_AUTHORIZED=NO`.
- **SC-003** Os relatórios de dependências e contagem deduplicam arquivos compartilhados. Uma lacuna de prova fica visível no relatório.
- **SC-004** Windows e Ubuntu reproduzem a suíte focal normal e otimizada com os mesmos casos de contrato.

## Assumptions

O operador controla as raízes autorizadas e a origem dos digests usados na invocação. A N01-R pode fornecer inventário ou complemento local conforme o contrato. A verificação representa o instante da leitura de cada objeto.
