# Confronto obrigatório de novo resultado com AP04-POR-v1.0-draft

**Cada nova missão deve entregar este confronto preenchido, não apenas informar CI PASS.**

## Identificação

- Missão / data / owner / PR Draft:
- Baseline AP04: SHA Git do registro documental:
- Baseline C4: 72d9b94e613a57c82a5afd309796f44b271e2185
- Código novo SHA / tree:
- Documentos novos SHA / tree:
- Ambiente efetivamente observado: CHAT/CI/LOCAL:
- Subagentes/revisor independentes reais (ou NOT_RUN):

## Requisitos e plano

- IDs afetados da PARITY-MATRIX: PAR-...
- O que a linha exigia? Cite o critério original sem mudá-lo.
- Qual fonte e identidade foram usadas? Público sintético / privado local / Caderno:
- ADR-0003: PROPOSED / APPROVED_WITH_VERSION / NOT_APPLICABLE_WITH_JUSTIFICATION:
- ARC-04/05/07/09: preservados? Provas:
- HL7/FHIR: apenas capacidade futura ou há implementação por caso de uso com versão/perfil validado?

## Antes e depois

| ID | Estado antes | Código/dado novo | Evidência por SHA (CI e/ou local) | Estado depois | Lacuna remanescente |
|---|---|---|---|---|---|
| PAR-... | | | | | |

Estados válidos: RECOVERED_VERIFIED; IMPROVED_VERIFIED; PARTIAL_NOT_EQUIVALENT; INPUT_AVAILABILITY_UNKNOWN; CONTRACT_DECISION_PENDING; NOT_RECOVERED; BLOCKED_EXACT. Não marcar RECOVERED_VERIFIED do legado com apenas fixture sintética.

## Segurança, acervo e testes

- Original alterado? NÃO é obrigatório; hashes antes/depois:
- Houve worktree/clone novo? NÃO é obrigatório:
- Migração/reorganização/exclusão feita? NÃO é obrigatório:
- Algum código privado publicado/importado no Atlas? NÃO é obrigatório:
- R4 pipeline alterado nesta frente? NÃO é obrigatório:
- SDK Caderno sem Atlas/R4 e viewer sem R4:
- CI Windows/Ubuntu normal/-O, coleção real, skips e SHA:
- Browser real, árvore/nós/tabela RF, teclado, reflow, screenshots:
- RF real (ID, descrição, critério) visível? SIM / NÃO / DESCONHECIDO:
- Fonte/cobertura/ausência/estado/revisão provados? Detalhe:
- Rede/HTML hostil/payloads/links seguros? Detalhe:

## Desvios e pendências

- Objetivo foi substituído sem decisão explícita?
- Ficou mais difícil recuperar tabela/árvore apesar da nova CI?
- Foi presumida paridade total por um pacote parcial?
- Uma funcionalidade antiga foi retirada silenciosamente?
- Foi alegada conformidade FHIR/RO-Crate sem validação?
- Uma CI foi atribuída ao SHA errado?
- É necessário ADR sucessora e aprovação humana? Qual versão e motivo?
- Finding independente e correções com recibo por SHA:

## Estado terminal e próximo ato mínimo

Selecione exatamente um: MINIMUM_LEGACY_PARITY_DEMONSTRATED / PARTIAL_PARITY_WITH_GAPS / CONTRACT_DECISION_PENDING / BLOCKED_EXACT / NO_CHANGE_TO_BASELINE.

- Mudanças comprovadas da matriz:
- Pendências com owner:
- Menor próximo ato:
- Gates separados: merge, release, promoção, aprovação científica, limpeza física = NÃO AUTORIZADOS até decisão própria.

Não sobrescrever o registro histórico para esconder diferenças. Criar nova versão por commit e registrar o diff das decisões.
