# Resultado — AP04-F4-C2-A-REAL-V5-MAPPING-CHAT-02

**Estado: C2_A_BLOCKED_EXACT**. Subestado semântico: `C2_A_SOURCE_KEY_DECISION_REQUIRED`. O código C2-A está implementado e verificado focalmente, mas não existe aprovação para paridade integral, aquisição real, integração F4-C3 ou gate G4.

PR Draft #18; branch `feat/atlas-parity04-f4-external-reader-20261031`. Código: `dcd219bf592f47590413424adfdf6513a0daa18f`, árvore `aad819d8d7bc8dc40544aa850bb73831fa5b7fb0`, parent `228d1e1a10ea17874f0078f491e4418c56cf5969`. CI focal código: [41269925191](https://github.com/thalesvalente/Atlas/actions/runs/41269925191), 4/4 SUCCESS; Windows 60/60 (normal/-O), Ubuntu 59 PASS/1 SKIP ACL cada. Wheels independentes PASS. Manifesto C2 original e seus 22 blobs verificados por SHA em `258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7`.

Entrega concreta: parser HTML v5 inerte, mapeador com separação records/lineage, proteção contra colisão entre namespace, RF literal em mapa de células, valores/lexemas e ausências, File/Product sem promoção, sidecars conservados, contraprovas inventadas e JSON Schema Draft2020-12 com semântica e quota. Nenhum dado privado original foi lido no CHAT ou publicado.

**Bloqueios:** 1. SOURCE_KEY_CONTRACT_MISMATCH precisa decisão K/ARC-09. 2. C2_V5_UNAUTHORIZED_HISTORY_PATH: checker focal `scripts/qa/atlas_parity04_f4_c2_v5_evidence.py` fixa oito caminhos permitidos e rejeitará este diretório novo de recibos, necessário por prompt e fora do ownership de alteração do checker. Não manipular checker/guards/pins para fingir verde. 3. NATIVE_INDEPENDENT_REVIEW_NOT_AVAILABLE: nenhum subagente nativo real ou revisor distinto do autor para o SHA novo. 4. OS_ISOLATION_UNVERIFIED, HARD_BUDGET_UNVERIFIED, REAL_SOURCE_BYTES_NOT_ACCESSED.

**Distinção de SHA:** o PASS 4/4 é estritamente do **commit de código** `dcd219bf592f47590413424adfdf6513a0daa18f`; o commit documental sucessor não herda o PASS e sua própria CI deve ser reportada separadamente. O SHA terminal exato é obtido da PR Draft #18 depois do commit que contém estes recibos. Sem merge, release, deploy, migração, chamadas pagas, R4 alterado, clone/worktree, confiança ativada ou F4-C3.
