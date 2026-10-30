# AP04-F1 — handoff sanitizado

**Resultado: F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED.** Data: 2026-10-30. Plano AP04-POR-v1.0-draft, F1/G1. Estado geral AP04: PARTIAL_PARITY_WITH_GAPS.

Foram considerados e lidos três arquivos preexistentes autorizados, todos dentro da cota de 64 MiB: uma captura JSON, um HTML de redirecionamento e o HTML de dados explicitamente apontado e autorizado pelo operador. Dois payloads JSON foram parseados em modo inerte. Nenhum HTML ou JavaScript foi executado, nem houve geração ou rebuild.

No payload legado qualificante foram observadas cinco tabelas com 152 linhas. Uma linha RF foi comparada literalmente no arquivo original, incluindo identificador original, núcleo/módulo, nome, descrição e critérios de aceite, com vínculo explícito a fonte e execução. Categoria não está preenchida no original; seu marcador de ausência foi preservado. Os recibos privados conservam a linha, seus offsets e JSON Pointers. Das linhas observadas, 28 continuam UNADMITTED_NATIVE_RF; nenhuma foi promovida.

A hierarquia contém 2911 nós, 1595 relações e 858 parent keys explícitos que resolvem. O vínculo da RF amostrada é externo e conserva binding_gap: sua execução está isolada no grafo. Não foi demonstrado um caminho contínuo projeto/experimento/execução→RF, nem a interface navegável.

SHA-256, tamanho e mtime permaneceram iguais nas três fontes selecionadas. Três subagentes nativos reais atuaram em seleção/integridade, semântica e revisão independente; o coordenador foi o único escritor dos recibos. A revisão independente conferiu a fonte, a RF literal, os vínculos e os limites de G1.

Contagens pertencem ao payload selecionado; snapshots possivelmente sobrepostos não foram somados. Fontes brutas referenciadas e seus hashes históricos não foram revalidados. GLOBAL_UNPROVEN e UNKNOWN_UPSTREAM permanecem. Não há aprovação científica.

O confronto dos oito itens exigidos está em RESULT-REVIEW.sanitized.md. O próximo ato mínimo é entregar a evidência sanitizada à responsabilidade F2 já prevista para formalizar o contrato efêmero e resolver ARC-09 quando aplicável. F2–F6 não foram iniciadas nesta missão; ADR-0003 permanece PROPOSED_NOT_APPROVED.

Somente este trio sanitizado pode integrar a branch documental F1 existente. Sua identidade é o commit Git que o contém; parent/tree e igualdade dos blobs são verificados no recibo privado de publicação. PR #14 permanece intocada. Sem merge, release, deploy, promoção, migração ou limpeza.
