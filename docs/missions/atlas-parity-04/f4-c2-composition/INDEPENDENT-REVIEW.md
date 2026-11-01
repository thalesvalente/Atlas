# Revisão distinta e limites de aprovação

Nenhum subagente nativo foi disponibilizado; execução do integrador foi sequencial, sem simular revisores. Foi solicitada revisão real ao `copilot-pull-request-reviewer[bot]` pela API da PR18.

Review **5726563249**, publicado em **2026-11-01T05:01:34Z**, SHA **94e757d19ba873f0b437f756ded918a8d843420f**: **COMMENTED / Changes recommended**, 13 issues abertas. É revisão distinta real, de esforço Lite; não é aprovação humana, revisão exaustiva ou aprovação do SHA documental final.

## Findings novos nos blobs B preservados

- **4434473937**, `tools/atlas_legacy_presentation/os_windows_acl.py`: Administrators ACE é aceita além do token user e SYSTEM. Bloqueio de qualificação, com inspeção estática concordante; correção exige owner B, teste negativo Windows e nova revisão. Não alteramos o blob congelado.
- **4434473948**, `tools/atlas_legacy_presentation/os_worker.py`: nomes de arquivos/layout e PID do pai não vinculam o worker à fixture criada pelo supervisor. Chamada direta pode passar bytes arbitrários sob layout sintético. Bloqueio de qualificação; exigir capacidade/handle ou vínculo não forjável antes da leitura, contraprova e sucessor B. Não foi feita reprodução dinâmica nova desse ataque nesta frente.
- **4434473957**, README: comando CLI sintético histórico deixou de funcionar. `RESULT.md` deste sucessor explica a recusa deliberada antes de IO; README histórico não foi reescrito fora do ownership.

## Findings históricos e tratamento D

O review agrega também 4434446313, 4434091679, 4434091665 e 4434091650 sobre manifestos/recibos. D preserva o manifesto original por SHA e introduz manifesto sucessor completo, cobertura exata, digest de bytes atuais e negativas para entrada ausente/extra/duplicada/stale. A validação deste fechamento depende de CI própria, não de autoaprovação.

4434101000 (evidência de aquisição não sintética), 4434091710 (semântica de árvore), 4434091698 (corrida entre check e unlink), 4434091721 (tipos de endpoints) continuam itens para os owners/revisor. D não os declara todos corrigidos; mantém produção fechada e os módulos A/B intactos. 4434101007/4434091733 são esclarecidos: a conversão v5 existe, mas aquisição real e host continuam não qualificados.

O run técnico 41275470747 prova execução das suítes existentes e contraprovas D, não ausência desses riscos. Não foram resolvidas threads alheias, emitida aprovação pelo próprio autor ou transferida a revisão anterior para um SHA posterior.

**Estado: INDEPENDENT_REVIEW_PERFORMED_WITH_FINDINGS_NO_FINAL_APPROVAL.** O SHA documental final precisa de nova solicitação de review. O retorno real, SHA e status são vinculados no recibo externo da PR18 após o commit, sem prometer aprovação ou herdar o parecer de 94e757d1.
