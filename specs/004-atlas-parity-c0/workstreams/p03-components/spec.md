# Feature Specification — P03: componentes isolados

**Missão:** ATLAS-PARITY-02-P03. **Data:** 2026-10-27 (America/Fortaleza).
**Branch:** `work/atlas-parity02-p03-components-20261027`. **Estado:** candidata isolada.
**Entrada:** instrução do operador; baseline `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`.

## User Scenarios & Testing

### US1 — Ler tabelas sem perda (P1)

Uma pessoa revisora lê colunas e linhas com identidade, tipo, unidade, precisão e ausência.
Strings numéricas mantêm grafia; inteiros longos mantêm todos os algarismos; Number inseguro
falha. Ordenar/filtrar preserva a identidade e a fonte. HTML/URI permanece texto. Tabela vazia
informa o vazio, e excesso do limite gera erro explícito. A região de rolagem é focável,
com tabela semântica e cabeçalhos associados.

### US2 — Conferir metadados representáveis (P1)

Metadados declarados e observações do SDK são apresentados separadamente. Um File, mesmo
com extensão .pdf, permanece artefato. Menção não vira produção. Digest não autentica origem
nem aprova ciência. IDs iguais em pacotes distintos conservam fonte + @id. Relações são
corroboradas nas entidades preservadas; ausências permanecem explícitas.

### US3 — Avaliar candidatos explícitos (P2)

Produto/documento rico só aparece como candidato sintético com semântica declarada no
próprio descritor. Componentes não abrem payload, executam documentos ou ativam o aplicativo.

## Requirements

- **FR-P03-001:** classificar contrato vigente, apresentação derivada e nova semântica.
- **FR-P03-002:** oferecer funções puras, entradas explícitas e erros previsíveis.
- **FR-P03-003:** preservar identidade e strings numéricas; rejeitar inteiro JS inseguro.
- **FR-P03-004:** mostrar tipo/unidade/precisão/ausência sem arredondamento/conversão implícitos.
- **FR-P03-005:** usar tabela semântica, caption, cabeçalhos e overflow contido no componente.
- **FR-P03-006:** apresentar conteúdo hostil como texto inerte, sem I/O nos componentes.
- **FR-P03-007:** projetar apenas metadados/relações efetivamente declarados no read model.
- **FR-P03-008:** restringir produto/documento rico a candidatos sintéticos explícitos.
- **FR-P03-009:** testar casos positivos, negativos, vazios, grandes, Unicode e maliciosos.
- **FR-P03-010:** entregar harness reproduzível e contrato de integração por SHA.
- **FR-P03-011:** conservar protocolo, shell, catálogo, servidor, package-data e workflows.
- **FR-P03-012:** entregar RESULT, HANDOFF, MANIFEST e revisão nativa independente.

## Success Criteria

- **SC-P03-001:** componentes executam sobre fixtures e projeção SDK, sem produtor.
- **SC-P03-002:** valor, identidade, ausência, texto hostil e limites têm testes comportamentais.
- **SC-P03-003:** `VISIBLE_IN_MAIN_APP=false`; nenhuma ativação automática.
- **SC-P03-004:** todos os paths novos pertencem a P03; baseline preservada byte a byte.
- **SC-P03-005:** entrega distingue código, documentação, testes locais, CI e limites visuais.

## Assumptions

Estudos A/B/C/D integrais e contrato P01 não recebidos: INPUT_MISSING. Hash informado não
comprova recebimento. A direção ADR-0002 já foi aceita na PR #5; novas extensões, ciência e
release mantêm gates próprios. P06 compõe em candidata separada, respeitando ownership P02.
