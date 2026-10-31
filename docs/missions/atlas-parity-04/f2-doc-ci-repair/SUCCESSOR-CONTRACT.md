# Contrato do sucessor documental F2 — AP04-F2-DOC-CI-REPAIR-01

Plano preservado: AP04-POR-v1.0-draft. Prompt obrigatório: 8abf556c6c39fcc54855391f2eeef3d8a8615985, oito seções e marcador COMPLETE conferidos. O prompt parcial anterior foi desconsiderado após a correção explícita do operador. Nenhuma alteração na branch da PR #15 usou a versão parcial.

## PLAN e ownership fixados antes da edição

O inventário exato está em REPAIR-OWNERSHIP.json: A escreve somente novo guard e novas contraprovas; B escreve cinco workflows e o controle C4; ORQ integra onze recibos públicos. C é revisor nativo real, somente leitura, sem autoria. Nenhuma pasta é autorizada por prefixo. Todas as entradas são blobs 100644. O coordenador publica por Git Data API na branch existente da PR Draft #15, com um pai e lease do HEAD esperado.

## Épocas e autoridade

C4 → AP04 original e reparo → F1 → F2 → novo reparo são épocas distintas. INPUT-SHAS.json fixa SHA/tree/parent de cada commit intermediário. As nove árvores históricas, seus pais e deltas são verificados; um commit ilícito seguido de reversão não pode ser legitimado por árvore final igual. Os cinco documentos F1 e catorze F2 têm path/blob/hash/mode e origem exatos. F1 não tem manifesto público próprio; seus cinco blobs são congelados individualmente.

O guard AP04 e seus 23 testes continuam byte-idênticos. Seus oráculos de delta/histórico são aplicados aos objetos históricos AP04 até 47c94d27aeb7717eebb30804f01cd2cd33507c8a, sem impor a allowlist do reparo antigo retrospectivamente aos documentos F1/F2. O manifesto histórico AP04 é verificado nesses objetos, não reescrito para os controles novos. Manifestações históricas C1/C2/C3/C4/F2 permanecem preservadas.

O novo delta começa estritamente DEPOIS de 04373bb910db2e6215cc8bc4212093b649e48456. Todos os paths da árvore F2 terminal ficam congelados, exceto seis controles B explicitamente revisados. Cada commit posterior é inspecionado por pai/delta/status/mode; nenhum merge, remoção, rename, gitlink, symlink ou alteração transitória fora do inventário é permitida.

## Controle independente do overlay

OVERLAY.json deve ter serialização JSON canônica, inventário/owners/purposes literais e os dezenove documentos congelados. MANIFEST.sha256 é ordenado, completo e sem auto-inclusão: dezenove documentos F1/F2 mais dezoito entradas do reparo, 37 no total. Ele comprova integridade, não concede autorização semântica.

No processo independente de contraprovas, o teste novo inspeciona UTF-8 e AST antes de executar a fonte do guard. O entrypoint das contraprovas é o módulo de testes, não um runner que o guard possa omitir. Isso não afirma que nenhum outro processo de CI tenha executado o guard anteriormente. A tabela de hashes é exclusivamente literal e não pode esconder execução nas linhas excluídas. O teste fixa os demais bytes do guard e duplica os controles aprovados; o guard fixa os bytes dos testes e controles. Assim recalcular somente o manifesto não autoriza trocar fluxo, testes, dispatch ou oráculos. Alterações posteriores precisam de novo diff/contraprovas/revisão, sem herança de aprovação.

## Dispatch e regressão

A seleção real usa ancestralidade da âncora F2. Erros Git abortam; a linhagem anterior conserva chamada real ao dispatcher histórico estrito. Não há autorização por nome de branch. O guard novo reconhece identidades históricas por ref e testa positivamente C4/AP04/F1/F2; isso não é reexecução retroativa de CI nesses commits imutáveis.

O controle C4 continua verificando seus INPUTS, COMPOSITION, COMPOSITION_TREE, P03_C4_ADAPTERS, ASSETS e manifests. O conjunto herdado de 168 IDs C4 e 23 AP04 é conferido como 191 IDs distintos, além dos novos, nunca como mero mínimo de contagem. SDK/viewer permanecem instalados fora do checkout, com browser/HTTP/Chromium e Spec Kit 1.2.3 nos gates existentes.

## Fronteira e fechamento

O auditor P06 permanece inalterado, com FAIL histórico exato para o path/blob ADR-0003 já publicado. Nenhuma liberação de docs/architecture ou outro diretório. GATES/constituição/ADRs/plano/reader003/protocolo/fixtures/fontes permanecem intactos. ADR-0003 v0.2 e descriptor 0.2.0 continuam PROPOSED_NOT_APPROVED; G4 pendente; nenhuma fase F3–F6 é iniciada.

Sucesso exige seis workflows completed/success no mesmo SHA FINAL, zero skips/loader errors/falhas, todos os IDs herdados e revisão C do próprio SHA terminal. Se recibos forem acrescentados depois do SHA técnico, o commit posterior exige nova CI e revisão. A conclusão externa na PR identifica esse SHA sem ciclo de commits para embutir o próprio hash.

## Leitura Git em lote após o primeiro ciclo

O primeiro ciclo 9777 passou nos guards e em cinco workflows, mas ATLAS021 Windows não completou a segunda suíte antes do limite preservado de 15 minutos. A correção agrupa leituras por OID exato usando cat-file --batch, em vez de abrir um processo por objeto. Cada frame valida identidade, tipo, tamanho canônico/limites, payload, LF, conteúdo SHA-1 e ausência de trailing bytes. As árvores/modes e todos os pais/revisões continuam conferidos em cada chamada, sem cache de resultados PASS.

APPROVED_PRIOR_CONTROL_REVISIONS admite somente os dois hashes anteriores de guard/testes publicados no SHA 9777 e revisados independentemente; a nova contraprova reconcilia SHA/tree/blobs/bytes e impede substituir os pins antigos por hashes novos. Alterar/recalcular o overlay não aprova versões de controles. A mudança permanece nos mesmos dezenove paths e não altera AP04-POR, timeouts, pins, IDs herdados ou controles de produto.
