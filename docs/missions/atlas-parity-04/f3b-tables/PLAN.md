# PLAN — AP04-F3B-CHAT-TABLES-01

Data: 2026-10-31. Plano vinculante AP04-POR-v1.0-draft.
Prompt oficial: 23e776d5b94e1e075275d28e41b5e9214a52cffe, docs/missions/atlas-parity-04/f3-parallel-launch/F3B-CHAT-TABLES-01.md.
Base exclusiva: 54bb16d350f7bc34fafb95438bd64a2397d58bf3; tree1372dd532b2323fc1ebaa5c2f00b6d537c636dc9.
ADR-0003v0.2/descriptor0.2.0: APPROVED_SCOPED no comentário PR15 6539419419, vinculado ao pacote c3ea1e82938fd61cc5a22fee973352715a5bb527. Somente F3B autorizada nesta execução.
REASONING_EFFECTIVE=UNVERIFIED (seleção manual do operador não observada).

## PLAN → EXECUTE → REVIEW

1. PLAN: ler constituição/ADR0001/0002, registro AP04, decisões D001–020, matriz PAR002/003/004/005/006/012/015 e gates G3/G5, ADR0003v0.2, contrato completo/schema/exemplos, identidade/perdas e N01–24.
2. EXECUTE: renderer tabular neutro em memória, API de ciclo de vida/seleção contextual, busca/filtro/ordem declarada/paginação/detalhe, exportações JSON fiel e CSV neutralizado. Nenhuma integração File API, shell, Catalog, SDK ou produtor.
3. QA: fixture inventada com RF/RNF/RES opcionais declaradas, ausências/lexemas/precisão, quatro tabelas não vinculadas, 28 RF sem admissão e ataques. Harness real Chromium, Windows/Ubuntu × Python normal/-O, screenshots1440/390/320, zero skips e zero rede externa. Estados de fixture só PASS após validação real.
4. REVIEW: C somente leitura revisa código/contrato/segurança/CI/integridade no SHA técnico e depois no HEAD terminal. Cada novo commit documental recebe gate e revisão novos. Resultado somente F3B_TABLE_COMPONENT_READY_FOR_F4 se todas as condições focais satisfeitas, ou F3B_BLOCKED_EXACT.

## Ownership nativo real

- ORQ /root: único escritor Git; workflow novo e recibos docs/missions/atlas-parity-04/f3b-tables/.
- A /root/model_a: exclusivamente static/parity04_f3b_tables.js/.css.
- B /root/qa_b: exclusivamente teste focal/auxiliares f3b, fixtures atlas_parity04_f3b_* e harness scripts/qa/atlas_parity04_f3b_*.
- C /root/review_c: independente, sem autoria, somente leitura. Parecer pode ser transcrito por ORQ.

Agentes entregam fontes ao coordenador; não criam blobs/commits/branches. Nenhuma worktree/clone nem troca de checkout. Trabalho remoto por GitHub: ferramentas locais exec e node falharam antes de leitura/escrita/testes. Tentativa inicial de metadados locais não é evidência qualificadora.

## Limites e preservação

Delta permitido somente nos paths exclusivos do prompt. Controles históricos/manifestos/protocolo/reader003/F3A permanecem somente leitura. Gate próprio não afrouxa gates anteriores nem mascara falhas globais. Global G5, RF real, G6, paridade completa, F4–F6, ciência, merge/release/deploy/promoção/migração/limpeza não são concedidos.

F1 a237f446e54927eeeda8ed5e8e9daa83ee09dcb7 é referência sanitizada de lacunas, sem importação de fonte privada. Fixtures não são replay F1. UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN e binding_gap permanecem. RO-Crate1.3, ProcessRun0.6 e Caderno0.1.0a1 preservados; HL7/FHIR futuro por domínio sem conformidade atual.

Sem mudança do plano ou gate proposta.
