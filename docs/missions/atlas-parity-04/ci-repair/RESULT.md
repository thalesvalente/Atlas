# Resultado — reparo de CI documental AP04

**Missão:** ATLAS-PARITY04-DOC-CI-PUBLISH-REVIEW-03. **Plano:** AP04-POR-v1.0-draft.
**REASONING_EFFECTIVE:** UNVERIFIED.

## Checkpoint versionado e fechamento externo

O reparo técnico `54ffea9e8fe2ed5cde071a8ec52fbcbff857df60`, tree `417d29e1cf051644ce6e1edead7fed3315147286`, foi publicado por fast-forward na mesma branch da PR Draft #14. Sua CI terminal passou: seis workflows, 33 jobs, tentativa 1.

Este recibo registra esse predecessor testado. O commit que contém os recibos ainda exige CI e revisão próprias. Até esse fechamento, o checkpoint é `AP04_DOC_CI_BLOCKED_EXACT`, pendente somente dos gates do commit documental final. A conclusão terminal será publicada na conversa/descrição da PR #14 com SHA, tree, runs, artefatos e parecer, conforme a seção 9 da retomada -02. Não se tenta embutir o SHA do próprio commit.

## Origem, executor e preservação

Os originais foram recuperados por bytes Git do commit de evidências `e5e6e5370e463d626e095906f53c4ef18640aef0`. Patch e ZIP coincidem com seus SHA-256 e blob OIDs; ZIP com 48 entradas, CRC válido, sem traversal, symlink ou conflitos e patch interno idêntico. Os 34 checksums internos passaram. O patch original permanece preservado na branch de evidências; os bytes derivados são identificados separadamente em INPUT-SHAS.json.

A limitação da execução REPAIR-01 permanece registrada como fato histórico. A retomada reutilizou apenas o checkout existente e o ambiente atlas-poc/Python 3.12.15 para Git e QA. Nenhuma aplicação/Serve local, fonte privada, instalação de avaliação ou unidade H foi usada. Não houve novo clone/worktree; criou-se somente o acompanhamento local da branch remota existente da PR #14.

Inventário do reparo: 19 paths (5M/14A), disjuntos dos nove documentos; delta C4 acumulado: 28 paths, blobs 100644. Os nove documentos, todos os manifestos/handoffs históricos, pins existentes, runtime, protocolo e fixtures científicas permanecem intactos.

## Engenharia e contraprovas

P06 histórico permanece estrito. A exceção é exclusivamente a ADR-0003 original por path/blob/ancestry, depois da validação completa do overlay. A autoria C4 termina em seu SHA congelado; AP04 usa manifesto suplementar. P03/C4 é roteado por objetos e bytes.

A revisão independente encontrou dois bypasses no patch original: corpo C4 retornando sucesso e condição de workflow pulando o guard real, ambos aceitos com manifesto recalculado. O coordenador reproduziu os dois. A correção limita-se ao guard/testes: pins independentes dos bytes completos C4/workflows; AST executável do guard fixado pelos testes; guard fixa os testes. Revisão adicional exigiu tabela exclusivamente literal, preflight antes de executar a fonte, codec UTF-8 e execução do mesmo texto validado sem releitura pelo loader. Seis IDs novos cobrem essas proteções.

## Provas do SHA técnico

- Original recebido: 17/17 PASS Windows normal e 17/17 PASS Windows -O, antes da derivação.
- Derivação final: 23/23 PASS Windows normal e 23/23 PASS Windows -O, sem skips, com hashes de fonte em NEGATIVE-TESTS.json; compile, cinco YAMLs e JSONs válidos.
- Actions: seis workflows/33 jobs success no SHA técnico, incluindo AP04, P06, P03, C4, ATLAS021 e Spec Kit.
- Instalação em quatro células Ubuntu/Windows × normal/-O: exatamente 168 IDs herdados C4 + 23 novos = 191 IDs distintos, todos executados, sem perdas, extras, skips, falhas, erros ou loader errors. Não são 764 identidades distintas.
- Browsers reais C4: 31 checks por célula e quatro screenshots; P03: 19 checks nas duas plataformas; P06: 14; ATLAS021: grupos legados 20/24/23 e P02 23. Consumidor instalado isolado e fixtures públicas preservadas.
- Oito jobs Spec Kit com CLI 1.2.3, sem managed files ausentes/modificados ou findings. Estado de feature não persistido.
- Grafo histórico real: nove documentos, 19 paths/18 hashes do reparo e P06 FAIL exatamente para a ADR proposta; guard AP04 PASS, sem enfraquecer a proteção.
- 28 artefatos têm SHA e digests conferidos contra uploads. Dois ZIPs foram materializados e conferidos por digest/CRC; recibos internos vinculam SHA/tree corretos. A prova integral dos 191 IDs vem dos JSONs dos logs. Não se alega inspeção visual dos PNGs.
- P01/C3 não gerou run próprio pelos filtros aplicáveis; C4 confere seus 95 blobs/manifestos herdados. Nenhum sucesso histórico foi transferido.

CI-EVIDENCE.json persiste IDs completos dos conjuntos, hashes, runs/jobs, artefatos e limites. A revisão nativa sem autoria cobre código e derivação; o parecer final inclui obrigatoriamente o novo commit dos recibos e sua CI.

## Limite local observado

O guard real local falhou em normal/-O, e C4 inputs também falhou. Cinco JSONs Spec Kit preexistentes no worktree estavam em CRLF, distintos dos blobs LF apesar de equivalência JSON; P06 apontou esses cinco BYTES_CHANGED mais a ADR esperada. Git estava limpo. Não se normalizaram esses arquivos nem se relaxou o auditor. Nos checkouts novos dos Actions a fronteira exata passou em Ubuntu e Windows. Esta missão não qualifica operacionalmente o host local.

## Autoridade e próximo ato mínimo

Nenhuma mudança de plano: ARC-01–09, D-001–D-020, PAR-001–PAR-015 e G0–G9 mantêm seus critérios. ADR-0003 continua PROPOSED_NOT_APPROVED. HL7/FHIR permanece capacidade futura sem implementação alegada. A missão não inicia F1–F6 nem autoriza merge, release, deploy, promoção, migração, limpeza ou ciência.

Publicar este delta somente de recibos/manifesto na mesma branch; obter CI terminal e revisão independente do SHA resultante; registrar a conclusão terminal externamente na PR #14. Nenhum commit adicional apenas para inserir identidade.
