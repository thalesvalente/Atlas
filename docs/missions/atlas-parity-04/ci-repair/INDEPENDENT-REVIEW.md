# Revisão independente — PUBLISH-REVIEW-03

## Revisor e independência

Revisor nativo real: `/root/reviewer`, somente leitura, sem autoria ou escrita no delta. O coordenador `/root` é o único writer. As frentes `/root/provenance` e `/root/ci_diagnostic` forneceram verificações adicionais em leitura; não substituem o parecer independente abaixo. A ausência de revisor na execução REPAIR-01 permanece um fato histórico do recibo original.

## Findings e correções revisadas

1. O guard recebido permitia mudar o fluxo C4 para retornar sucesso e atualizar o manifesto. O coordenador reproduziu PASS indevido; a derivação fixa os bytes completos C4 e os cinco workflows fora do manifesto editável.
2. O workflow recebido podia pular o guard obrigatório com if-expression falsa e manifesto recalculado. O coordenador reproduziu PASS indevido; o pin independente do conteúdo completo rejeita essa mudança.
3. Excluir a tabela do digest AST permitia expressão executável envolvendo seus dados. A derivação exige tuple literal de pares string/string, ast.literal_eval, inventário exato e hashes esperados antes de executar a fonte.
4. O loader podia interpretar codec diferente do texto UTF-8 validado. A derivação exige UTF-8 e executa exatamente o texto já validado, sem segunda leitura.

Os testes independentes fixam o AST executável do guard; o guard fixa os bytes completos dos testes. As seis negativas adicionais, totalizando 23 IDs, cobrem os bypasses e a cadeia de autorização. Os snapshots intermediários de 21/22 casos não são transferidos aos bytes finais.

## Parecer do SHA técnico — PASS

SHA `54ffea9e8fe2ed5cde071a8ec52fbcbff857df60`; tree `417d29e1cf051644ce6e1edead7fed3315147286`. Resultado do revisor: `PASS_FOR_EXACT_TECHNICAL_SHA`, sem findings bloqueantes remanescentes.

O revisor conferiu diretamente os seis runs `41087116946`, `41087115963`, `41087116289`, `41087116019`, `41087116596` e `41087116351`: head_sha exato, tentativa 1, completed/success, 33/33 jobs e etapas com sucesso. Leu os 33 logs pela API.

Comparou o recibo C4 original do job `123810381674` (SHA `72d9b94e613a57c82a5afd309796f44b271e2185`, 168 IDs) com os quatro recibos instalados atuais: os mesmos 168 mais os exatos 23 AP04, total 191 IDs, zero ausências/extras/skips/falhas/erros/loader errors. Consumidor fora do checkout e R4 ausente.

Os quatro recibos P06 mantêm exatamente a única rejeição histórica ADR-0003, nove documentos/28 paths e pins sem relaxar P06. Os quatro audits AP04 e 23 negativas por célula passaram. Os quatro browsers C4 passaram 31 checks por célula, sem requests externas, page errors ou console errors.

Os 28 IDs/digests dos artefatos nos logs coincidem com a API e o SHA correto. O revisor não reivindica baixar os 28 ZIPs ou inspecionar visualmente PNGs. As duas materializações ZIP verificadas pelo coordenador estão separadas em CI-EVIDENCE.json.

A verificação independente de proveniência confirmou 19/19 OIDs, 18/18 hashes, serialização canônica, modos e os nove documentos byte-idênticos. Nenhuma mudança de AP04-POR-v1.0-draft, ARC-01–09, D-001–D-020, PAR-001–PAR-015 ou G0–G9 foi identificada.

## Limites e commit documental final

Este parecer cobre código e CI exclusivamente do SHA técnico acima. Não qualifica o host local: o guard local falhou por cinco cópias CRLF preexistentes, preservadas sem normalização; o Actions passou com checkouts novos. Não aprova arquitetura, ciência, ADR-0003, F1–F6, merge, release, deploy, promoção ou migração.

O novo commit dos recibos exige sua própria CI terminal e revisão independente do delta e da identidade publicada. O fechamento final será registrado externamente na conversa/descrição da PR #14, com SHA/tree/runs/artefatos/parecer desse novo commit, sem commit adicional apenas para inserir o próprio SHA.
