# ATLAS-PARITY-03-C3 — gate de contratos P01

**Spec Kit 1.2.3 — workstream P01 (C3)**. Este complemento não escreve ponteiro global nem declara execução da CLI oficial. O diretório P01 de Spec Kit 1.2.3 já foi produzido na PR #9; esta extensão aplica o fluxo specify → clarify → plan → tasks → analyze ao gate de CI, com revisão de limites. Helpers da CLI na sessão C3: **NOT_RUN**.

## Specify / clarify

Necessidade: tornar o corpus de P01 um gate executável sem alterar produto ou os workflows de C1. Não há permissão para preencher lacunas de estudos A/B/C/D. Exercícios devem ser sintéticos, offline, sem produtor privado, com proveniência por SHA.

## Plan / tasks

1. Preservar 82 hashes originais, 83 paths e 51 blobs técnicos.
2. Executar 46 casos e nove probes em normal e `-O` nas duas plataformas.
3. Repetir 11 regressões focalizadas, executar auditoria arquitetural e exigir zero skips.
4. Comparar relatórios canônicos, publicar JSON/JUnit por SHA.
5. Validar matriz de 28 IDs contra a CSV original, com estados/imputações idênticos.
6. Reconciliar CI terminal e obter QA independente sem autoria do delta.

## Analyze / gates

No desenho, ARC-01–09 permanecem invariantes: leitor público, Caderno independente, sem R4/importação, proibição de protocolo/runtime/host/release, sem mascarar UNKNOWN e sem aprovar ciência. A geração desses documentos não prova execução dos helpers, revisão independente ou terminal CI; seus gates são verificados separadamente. Nenhum global feature pointer é alterado.
