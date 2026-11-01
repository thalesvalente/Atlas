# AP04-F4-C2-D — execução incremental

Estado desta publicação: `PREFLIGHT_AUDIT_PENDING_ACTIONS`, não composição concluída.

## ANALYZE → PLAN → IMPLEMENT → REVIEW

A fonte desta missão é `315f7dbeffc80822e96068eed6b4af3193d1b6a7:docs/missions/atlas-parity-04/f4-direct-reuse-next-20261101/05-C2-D-COMPOSE-REVIEW-CHAT.md`. Único destino: PR Draft #18, branch `feat/atlas-parity04-f4-external-reader-20261031`.

Entradas congeladas observadas por SHA/tree/parent: F2 `54bb16d350f7bc34fafb95438bd64a2397d58bf3`; C2 original `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`; v5 inicial `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`; A `c52215f73292435a2db3525cd7a8b226f13672d7`; B `bc5b634dd05d822983a8b8d5ec9c247bf47b3e4d`; K `ab22a78eb22af4ef9651cdd8f652c3cb2755e947`.

O sucessor do verificador conserva o manifesto histórico de 22 entradas no SHA original e verifica todos os commits em cinco intervalos separados: original, v5 inicial, A, B e D. A inclusão dos nove recibos A é explícita e limitada ao intervalo A fixado. Não se modifica o verificador anterior nem qualquer guard global. O workflow focal conserva a matriz Windows/Ubuntu × normal/-O, testes A e prova de independência dos wheels. A auditoria B ocorre antes da importação, verificando paths transitórios, linearidade, modes, árvores e blobs.

Neste primeiro commit D nenhum módulo B foi importado, nenhum parser A foi alterado e nenhuma aquisição foi habilitada. Depois de auditoria observada sem violações, somente os cinco módulos `os_*.py` enumerados serão candidatos a importação por OID idêntico, em commit normal de um pai. B não será ancestral Git da PR18. Não há merge, rebase ou force.

Bloqueios já documentados pelos owners: A requer decisão source-key; K propõe 0.2.1 sem aprovação humana ARC-09; B bloqueia produção e não impõe filesystem/rede em Windows; revisão independente final pendente. Nenhuma ferramenta de spawn de subagentes nativos foi disponibilizada nesta sessão: execução sequencial, sem revisores simulados. G4 LOCAL, F4-C3/C4/F5 e navegação global não são liberados.

Sem acesso ao acervo privado, mudanças em R4/Caderno/SDK/servidor/shell, alteração de schema, migração, merge main, release, deploy, promoção ou limpeza. O scratch de autoria local contém apenas arquivos novos da missão, sem clone ou worktree Git.
