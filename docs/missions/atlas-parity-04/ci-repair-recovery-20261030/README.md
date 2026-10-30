# AP04 — Registro persistente dos artefatos e bloqueio de recuperação

**Estado:** `RECOVERY_PACKAGE_SOURCE_BYTES_MISSING`. Este registro não é o reparo de CI.
**Data de referência:** 2026-10-30.
**Destino Git:** `thalesvalente/Atlas`, branch de evidências separada (sem PR de implementação).
**Base documental verificada:** PR Draft #14, commit `c25d37998dac7174067a2819391f3af1625f96dc`, árvore `e6eacdd02a329f88bc0dd656523b84a8fec9217e`, parent C4 `72d9b94e613a57c82a5afd309796f44b271e2185`.

## Por que existe este registro

O operador executa vários chats em paralelo e não deve depender de baixar arquivos gerados por outro chat. O processo anterior apresentou links em sua conversa original para um patch e ZIP de engenharia, mas os respectivos **bytes não estão acessíveis a esta sessão**. Nenhum arquivo foi recriado e rotulado como original.

O procedimento a partir de agora é: publicar **os artefatos publicáveis e os recibos no Git, por SHA, antes de declarar handoff**; comunicar o commit/branch/PR; não presumir download local pelo operador. Acervos privados não são enviados ao repositório público: apenas hashes e relatórios sanitizados são versionados.

## O que esta branch contém

- `ORIGINAL-ARTIFACTS-STATUS.json`: nomes, hashes declarados, localizadores históricos e `UNAVAILABLE_IN_THIS_SESSION`.
- `CI-AND-REPAIR-STATUS.md`: estado da PR #14, C4, CI falha e engenharia relatada, sem transferir testes entre SHAs.
- `SOURCE-CHAT-DIRECT-PUBLISH.md`: instruções para que **a conversa que ainda tem os arquivos originais** os publique diretamente no Git após verificação dos bytes, evitando download manual.
- `PERSISTENCE-POLICY.md`: regra obrigatória para entregas posteriores.
- `prompts/`: prompts e confronto já disponíveis nesta conversa, copiados com proveniência.
- `RECOVERY-SOURCE-INDEX.json`: referências dos materiais e alcance real de leitura.

## Continuidade segura

1. Consulte os artefatos na conversa de origem e confira os SHA-256.
2. Se existirem, publique-os na branch de evidência indicada, com revisão de dados sensíveis, preservando os bytes originais; **não editar PR #14 só para armazenar arquivos**.
3. Só depois aplique o patch verdadeiro, em `docs/atlas-parity04-plan-of-record-20261030`, validando a baseline e a integridade do patch, sem worktree/clone novo.
4. CI em novo SHA, revisão independente real e fechamento por evidências. Se faltar o original, `BLOCKED_ORIGINAL_ARTIFACTS_UNAVAILABLE`; reconstrução futura recebe novo hash e testes, jamais os recibos antigos.

**Proibido:** alterar manifests/pins congelados, ignorar CI, transformar a ADR-0003 em aprovada, migrar ou excluir dados, fazer merge, deploy, release ou promoção.
