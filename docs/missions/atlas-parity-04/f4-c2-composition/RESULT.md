# AP04-F4-C2-D — composição executada, qualificação bloqueada

**Estado: C2_D_BLOCKED_EXACT.** Código composto e testado; não é um leitor operacional de acervo real, não satisfaz a dependência C3 e não autoriza G4/G5/G6. Subestados: C2_D_CODE_COMPOSED_HOST_GATE_UNVERIFIED e C2_D_SOURCE_KEY_DECISION_PENDING.

## ANALYZE → PLAN → IMPLEMENT → REVIEW

Missão: `315f7dbeffc80822e96068eed6b4af3193d1b6a7:docs/missions/atlas-parity-04/f4-direct-reuse-next-20261101/05-C2-D-COMPOSE-REVIEW-CHAT.md`. Único destino: PR Draft #18, branch `feat/atlas-parity04-f4-external-reader-20261031`. Os handoffs A/B/K foram lidos e seus objetos congelados conferidos. Sem clone, worktree, nova branch, rebase, force ou merge.

A auditoria de pré-composição passou no run 41274537073. O sucessor verifica cada commit dos intervalos original, v5 inicial, A, B e D, incluindo caminhos transitórios, pais, árvores, modos e blobs. O manifesto histórico de 22 entradas continua intacto e é verificado no SHA original. O manifesto desta composição cobre todos os bytes atuais alterados desde F2, exceto ele próprio.

Cinco módulos B foram importados por OID exato em commit de um pai. **B não é ancestral Git da PR18: isto é composição por blobs, não merge.** Parser, mapper A e schema 0.2.0 foram preservados. `reader.prepare` chama o bloqueio real B antes de avaliar caminhos, allowlist ou abrir bytes. Retorno indevido de guards e exceções inesperadas continuam bloqueados. `__main__` não cria scratch antecipadamente nem permite que `--synthetic-fixture` autorize leitura de caminhos fornecidos pelo operador.

A conversão v5 de A existe e é exercitada com fixtures inventadas, inclusive escala 2911/1595, cinco tabelas e diferenças missing/null. Porém B só fornece probes sintéticos; não existe nesta entrega um worker de aquisição real que rode esse mapper sob política OS qualificada. Os códigos HARD_BUDGET_UNVERIFIED/OS_ISOLATION_UNVERIFIED são falhas intencionais anteriores ao acesso, não implementação de aquisição bem-sucedida.

## Evidência executada

SHA técnico `51d814d1955883d152124a530cbff75a6928fabb`, tree `0693cd47482ab00f38c052439ccb0001b24cc747`, run 41275470747/1: quatro jobs SUCCESS. Por modo normal/-O: Ubuntu 79 PASS + 1 skip na suíte original/A/D e 18 PASS + 6 skips em B; Windows 80 PASS e 22 PASS + 2 skips em B. Total matricial: 416 execuções coletadas, 398 PASS, 18 skips de plataforma, zero falhas. Não são 416 casos distintos nem zero skip global. B mantém pytest sem otimização e otimiza apenas o worker; A/D são testados também sob -O. Wheels independentes PASS nos quatro jobs, sem incluir a ferramenta externa.

O primeiro run composto 41274954746 falhou na coleta B em Windows: checkout D: e scratch C: fizeram pytest alcançar diretório protegido. O commit e1af7e00 corrigiu somente o harness D com diretório/configuração de coleta explícitos e contraprova; 252b85c8 preservou os asserts B. A falha histórica não foi apagada. O commit 51d814d1 acrescentou inventário de bytes, quatro contraprovas de manifesto e reconciliação dos recibos pelo mesmo HEAD.

Este recibo registra resultados já observados no SHA técnico. O commit que contém estes documentos exige nova CI e revisão. Os objetos finais, run/attempt, jobs, hashes dos artefatos e parecer observado serão vinculados externamente na conversa da PR18, sem assinatura circular do próprio commit e sem herdar PASS de SHA anterior.

## Bloqueios e atos mínimos

1. **Owner B:** implementar contrato real supervisor/worker; confinamento Windows de filesystem/rede está ausente. Job Object de 256 MiB/30 s não é sandbox de filesystem/rede. Probes Linux não qualificam o parser real nem o host privado.
2. **Owner B + revisor distinto:** findings 4434473937 (Administrators ACE aceita) e 4434473948 (entrada direta do worker sem vínculo não forjável à fixture do supervisor), review 5726563249 no SHA 94e757d1. Foram lidos e confirmados estaticamente no código; não houve reprodução dinâmica nova desses ataques. Corrigir em sucessor B autorizado, acrescentar contraprovas e revisar antes de nova importação. Nenhum blob B foi editado ou declarado seguro por omissão desses testes.
3. **Decisão humana ARC-09/K:** proposta 0.2.1 de `ab22a78e` não aprovada. Sem mudança de schema, native_id fabricado ou afirmação de árvore estrutural integral. Gaps do 0.2.0 permanecem explícitos.
4. **Revisão final/host:** review distinto real existe, mas é COMMENTED/Changes recommended, não aprovação final. Nenhuma ferramenta nativa de subagentes esteve disponível; nenhum revisor foi simulado. L0/arquivos Windows reais não foram inspecionados; HOST_UNVERIFIED. Eventual prova LOCAL depende das autorizações próprias e não é solicitada como transferência de corpus ao CHAT.
5. **F4-C4:** gates globais observados vermelhos foram preservados. A sucessão desses guards não pertence a D. CI focal verde não aprova a PR inteira nem libera C3/C4/F5.

## Uso e limites

O comando histórico de README com `--synthetic-fixture` **não é mais executável para aquisição via CLI**; retorna IO_UNVERIFIED/exit 2, sem abrir a fonte. O modo interno de fixture é exclusivo do harness e não prova que bytes arbitrários sejam públicos. Não usar esse modo com acervo real. Findings históricos de semântica, evidência não sintética e corrida check/unlink continuam sujeitos a revisão dos owners; nenhuma alegação de segurança operacional os dispensa.

Sem alterações em R4, Caderno, SDK, Catalog, servidor, shell, F1/F2, outros PRs ou guards globais. Sem reprocessamento, migração, fontes privadas, G4 LOCAL, F4-C3/C4/F5, merge main, release, deploy, promoção ou limpeza de acervo. A remoção automática de fixtures inventadas pelo harness não é limpeza de fontes.
