# P01 — ATLAS-AP04-C2-K-CONTRACT-FINAL

**Conclusão técnica:** `O0_INSUFFICIENT_O1_RECOMMENDED_CONDITIONALLY`.
**Resultado:** `C2_K_REVIEW_BLOCKED_EXACT`.
**Gates:** `INDEPENDENT_REVIEW_NOT_PROVEN`, `ARC09_HUMAN_DECISION_PENDING`, `C4_AP04_F2_GUARD_SUCCESSION_REQUIRED_FOR_NEW_K_DOC_PATHS`.

0.2.0 continua contrato aprovado; 0.2.1 é UNAPPROVED_VERSIONED_PROPOSAL. A autoavaliação documental não declara C2_K_CONTRACT_CANDIDATE_REVIEWED, contrato aprovado ou implementação. O objeto imutável de ARC-09 é identificado por SHA/tree e cinco blobs normativos em HANDOFF.json/DECISION-REQUEST.md. HEAD do recibo é distinto e deve ser registrado na PR com CI/review do SHA exato; nunca resolver objeto pela branch móvel.

## Evidências e limites

INPUT-SHAS.json preserva os pins históricos. Código R4 fixado em 5c145615c8a1bd601351badddccaf3acea474ed2 separa key estrutural, ui_id derivado e native_id eventualmente null; parent_key/from_key/to_key são referências estruturais. Apenas código foi consultado, nenhum dado privado foi copiado. Não se executa nem publica esse código nesta K.

Schema 0.2.0 e semantics.py nos blobs e87767710b6eafd32d57fc68d5294610b0038571 e c448663d84507178a8fb463d019a10a1a43f0cde são native-only para RESOLVED. Parent e parent_key_literal já são requeridos. O mapeador C2 fixado conserva key/ui_id em unmapped_fields, mas isso não autoriza resolução estrutural: SOURCE_PARENT_KEY_NOT_NATIVE_REFERENCE e R4_V5_PARENT_SCOPE_UNREPRESENTABLE são lacunas/recusas honestas, não permissão de contornar o validador.

F1 sanitizada a237f446e54927eeeda8ed5e8e9daa83ee09dcb7 registra 2.911 nós, 1.595 relações e 858 parent keys explícitos resolvidos no payload selecionado, não no acervo global nem no descriptor 0.2.0. Seus negativos históricos não são os 50 pares inventados de D.

## Reparos reais

A candidata define parent ausente, null, presente, vazio, inválido e acima de quota; valores inválidos rejeitam atomicamente. NULL_ENDPOINT tem os três campos explicitamente null. UNRESOLVED/ORPHAN conserva referência válida sem alvo; TREE_CYCLE é gap, preservando refs resolvidas, sem enum inventado. Root exige prova literal consistente.

O delta de quatro campos corresponde em todos os documentos aplicáveis: `node.source_key_literal`, `node.parent_key_presence`, `reference.reference_basis`, `reference.declared_key_literal`. O1 permanece tipada e segregada. A numeração de testes futuros é 1–12; a matriz F usa dup-F, como os bytes originais. A tabela completa de 15 findings, incluindo seis abertos no HEAD inicial, está em INDEPENDENT-REVIEW.md; threads não foram resolvidas em nome do revisor.

## Verificação autoral

Checker documental reproduzível em INDEPENDENT-REVIEW.md: inventário e expectativas dos 14 oráculos JSON (10 principais e J/K/L/M), matriz PKEY, contagens de D, JSON ilustrativo parseado como texto, termos e manifesto. Normal e -O verificam os mesmos invariantes; não é implementação de mapper/schema 0.2.1. Os arquivos INPUT-SHAS.json e SYNTHETIC-IDENTITY-FIXTURES.json permanecem byte a byte nos blobs históricos. MANIFEST.sha256 contém dez entradas, exclui a si próprio e cobre todos os demais dez arquivos.

A execução/saída, SHA publicado, tree, parent e hash do manifesto devem constar no recibo append-only da PR depois do readback Git. NÃO executados nesta missão: validate_descriptor 0.2.1, testes de produto 0.2.1, renderer/browser, host Windows e corpus real. G4/G5/G6 permanecem abertos. Spec Kit analyze: NOT_RUN (CLI indisponível nesta sessão; nenhuma instalação); análise equivalente spec/plan/tasks/contrato realizada sem editar artefatos globais.

## Handoff e ordem

P01 corrige e congela somente K. P02/C4 recebe o finding de sucessão e deve implementar sua solução própria, estritamente scoped, com negativos de paths/proteção histórica. P03/P04/QA externo recebem o HEAD exato publicado e devem verificar a igualdade dos cinco blobs normativos com o commit objeto de ARC-09, reavaliar findings e CI, sem usar resoluções de threads como prova. Somente depois dos gates pertinentes cabe decisão humana ARC-09 explícita; implementação posterior permanece outra missão de C2/F3A/F3B. Sem merge/deploy/release/migração ou alteração de produto.
