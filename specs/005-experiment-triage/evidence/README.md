# Evidências sintéticas — Feature 005

Estes arquivos foram produzidos por Chromium/Actions sobre **dados inteiramente inventados**, sem R4 ou corpus privado. Candidato de produto testado: `3a9e1e3d2727c69175768abb437bdcbc47cfabf0`, tree `23b1c290aedf511c0903eaf9dd016296ec7ebe8b`. O commit que incorpora estes recibos é documental; CI e Codex Review desse HEAD constam do handoff terminal da [PR #33](https://github.com/thalesvalente/Atlas/pull/33).

## Relatórios originais

| Arquivo | Escopo / resultado |
| --- | --- |
| [browser-native-triage-report.json](browser-native-triage-report.json) | 23 grupos; busca, filtros, lote, baselines, propostas, seis viewports, cores e hit-tests — PASS |
| [browser-application-report.json](browser-application-report.json) | 63 checks de aplicação, incluindo exportações exatas e cancelamento gráfico — PASS_SCOPED |
| [browser-application-a01-report.json](browser-application-a01-report.json) | 12 grupos A01, incluindo LQA-01/LQA-02 — PASS |
| [browser-native-report.json](browser-native-report.json) | 14 checks Native — PASS_SCOPED |
| [browser-p02-report.json](browser-p02-report.json) | 17 checks de contexto, tabelas e navegação — PASS_SCOPED |
| [browser-p01-lineage.json](browser-p01-lineage.json) | 8 checks de relações declaradas — PASS_SCOPED |
| [after-graph-report.json](after-graph-report.json) | 15 checks de grafo, câmera e identidade — PASS_SCOPED |

Os JSONs são cópias integrais dos artefatos. Não substituir seus `tested_sha` pelo SHA documental. Referências a outras capturas dentro dos JSONs apontam para os conjuntos completos nos artefatos abaixo; as sete telas escolhidas para preservação permanente estão nesta pasta.

## Resultado focado e controles

As imagens de tarefa seguem um clique real em **Focar seleção**, com lote e detalhes abertos. Os PNGs mostram a execução sintética e sua ligação declarada à tabela RF; não constituem evidência de resultado científico real.

| Viewport | Imagem |
| --- | --- |
| 1440×1200 | [Desktop](browser-native-triage-report-task-1440.png) |
| 1101×900 | [Ponto de quebra](browser-native-triage-report-task-1101.png) / [busca e exportação acessíveis](browser-native-triage-report-controls-1101.png) |
| 1024×900 | [Intermediário](browser-native-triage-report-task-1024.png) |
| 800×1000 | [Intermediário estreito](browser-native-triage-report-task-800.png) |
| 390×844 | [Mobile](browser-native-triage-report-task-390.png) |
| 320×740 | [Mobile estreito](browser-native-triage-report-task-320.png) |

## Integridade e origem

[manifest.json](manifest.json) registra SHA-256 e tamanho de cada payload preservado. [source-hashes-before.json](source-hashes-before.json) e [source-hashes-after.json](source-hashes-after.json) comprovam bytes idênticos nas quatro fontes inventadas. O [mapa de publicação](implementation-publication-map.json) relaciona os commits locais aos commits publicados com a mesma tree; a publicação pelo conector não é revisão humana nem transferência de CI entre SHAs.

[ci-product-checks.json](ci-product-checks.json) registra os 17 checks concluídos com seus IDs, URLs e SHA. O mapa de publicação cobre os incrementos até esse candidato de produto; o commit de fechamento registra seu próprio recibo na mensagem Git e no handoff terminal.

| Artefato Actions original | SHA-256 do ZIP conferido |
| --- | --- |
| [Triagem — run 42111583734 / artifact 13454112139](https://github.com/thalesvalente/Atlas/actions/runs/42111583734/artifacts/13454112139) | `14fb25a9bce61dbff761234bb456d74f0e2258a98ed2d8ed6f759b9ae096749b` |
| [Aplicação — run 42111583741 / artifact 13455291112](https://github.com/thalesvalente/Atlas/actions/runs/42111583741/artifacts/13455291112) | `5a83b644beeee3d0afed75f378fcf19607ea0c644bd1069edaef3ff7c3c2a89c` |
| [Native — run 42111583767 / artifact 13454592020](https://github.com/thalesvalente/Atlas/actions/runs/42111583767/artifacts/13454592020) | `ad97508d9811b6c75c6ea15a169b3e8746ed0de3aa204149e7db73bbfdd11bd8` |

Os artefatos Actions têm retenção de 14 dias. Os arquivos desta pasta permanecem versionados. Os limites do escopo, revisão não autora e gates futuros estão em [validation.md](../validation.md) e no [checklist](../checklists/accessibility-security.md). Nenhum resultado equivale a certificação WCAG completa ou aceite humano da nova feature.
