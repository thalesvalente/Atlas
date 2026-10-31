# Resultado — AP04-F4-C1-GRAPH-SCALE-CHAT-01

**F4_C1_GRAPH_SCALE_QUALIFIED_FOR_COMPOSITION**, no escopo técnico sintético do SHA `913e4038b817916c9a728e18b8cd780ade36b9f0`, tree `7eabeffd019f206641412c56a29ab705ad15b4d3`. A [CI própria 41213311466](https://github.com/thalesvalente/Atlas/actions/runs/41213311466) passou nas quatro células Windows/Ubuntu × normal/-O: cada célula executou 30 testes e 24 jornadas Chromium reais, com zero falhas, erros, skips ou I/O indevido. Os 22 testes e 17 jornadas herdados foram preservados; somente as expectativas antigas de recusa acima de 1.000 nós/4.000 relações foram substituídas pelas novas admissões. C emitiu revisão independente PASS_SCOPED_FOR_COMPOSITION, sem finding bloqueante aberto.

O commit que contém estes recibos exige CI e revisão próprias antes do fechamento terminal. O fechamento externo no PR #16 identifica seu SHA/tree, jobs e artefatos. A qualificação do SHA técnico não se transfere automaticamente. As rodadas falhas permanecem em F4-C1-CI-EVIDENCE.json.

## Comportamento comprovado

O modelo conserva 2.911 nós e 1.595 relações. O índice inicial contém exatamente os 2.911 IDs, sem duplicação ou perda. As jornadas cobrem primeiro/meio/último nó, ramo recolhido, órfão, Run externo isolado, colisões por ocorrência, endpoints nulos/não resolvidos, texto/URI hostis, seleção e foco DOM, pan/zoom/fit/reset/minimapa, teclado e larguras de 1440/390/320 CSS px. Colapso conserva dados e seleção; reveal expande apenas ancestrais declarados. Hierarquia não vira causalidade.

O contexto source_id/snapshot_id/nav_id/occurrence/session_id permanece íntegro. Reimportação, troca de fonte/snapshot, TTL e dispose invalidam links antigos. Native_id nulo não ganha admissão. A fixture histórica de 109 nós/210 relações permanece intacta; o gerador sintético adiciona 2.802 nós/1.385 relações e conserva 22 endpoints nulos, 75 não resolvidos, 50 endpoints colidentes, 50 IDs nativos com duas ocorrências, 40 grupos repetidos e 41 ocorrências excedentes. A fonte real F1 não entrou no CHAT nem foi executada.

Total declarado/carregado, índice expandido, nós desenhados e seleção atual são contagens distintas na UI/getState. O desenho limita a janela a 1.000 nós, 4.000 relações e 4.000 arestas hierárquicas. Todas as relações continuam disponíveis no painel por ocorrência, inclusive fora do SVG. O minimapa agrega posições: 175 marcas somam 2.911 nós e ocupam 255,32 de 300 CSS px; o clique real centraliza a câmera dentro do grafo. Marcas geométricas não são entidades ou ancestrais científicos.

## Métricas e limites reais

Nas quatro células, setData de 2.911/1.595 levou 442,4–646,4 ms; revelar os três nós amostrados levou 12,4–35,6 ms. A abertura apresentou 635 elementos DOM; a quantidade de nós SVG varia com a janela e o foco/seleção preservados. JSON/JUnit, métricas e seis PNGs por artefato estão no recibo CI. Os quatro ZIPs foram baixados e seus SHA-256 conferidos contra os digests publicados. A captura sintética de 320 px foi inspecionada visualmente após a correção do minimapa. Não houve teste local do componente no checkout.

Stress de 10.000 nós/0 relações, com 5.407.991 bytes: aceito integralmente com desenho limitado. O caso de 10.001 nós, com 5.408.536 bytes, foi recusado atomicamente com `F3A — $.nodes: array quota`. O stress de 10.000/100.000 mede 81.008.070 bytes e foi recusado em 1,3925–2,1144 s pelo limite real de 600.000 valores visitados, sem modelo/SVG parcial; também excede 32 MiB. O caso de 100.001 relações foi igualmente recusado.

Não se afirma aceitação de 100.000 relações válidas dentro de 32 MiB. O envelope descriptor 0.2.0 permanece 10.000 nós/100.000 relações/32 MiB/profundidade 20. O limite auxiliar de 600.000 valores é explícito e segue para composição como REAL_VALUE_CAP_GATE_INTEGRATOR_REQUIRED. Qualquer mudança aplicável de quota, contrato ou plano exige decisão antes de implementar.

Heap exposto pelo Chromium é observação quantizada, sem qualificar memória total ou hard heap de 256 MiB. O prazo de 30 s por operação do produto e o prazo Python de 600 s permaneceram. Duas rodadas falharam no harness ao transferir o grande objeto por CDP e encerrar após o crash. O sucessor constrói cada payload completo sequencialmente no renderer, registra progresso e encerra com falha explícita quando necessário. Não omite stress, cria skips ou altera limites do produto. Ambos os findings foram fechados com nova execução no SHA técnico.

## Confronto com AP04-POR

| Item | Antes pertinente | Resultado C1 e lacuna restante |
|---|---|---|
| PAR-001/G2 | F3A recusava o volume de 2.911 nós | Navegação sintética em escala qualificada no componente; sem fonte real |
| PAR-004 | Contexto F3A preservado; integração pendente | Contexto e foco sob windowing comprovados; fluxo integrado nó→tabela→evidência pendente |
| PAR-007 | Modelo/tipos F3A com limite abaixo do volume F1 | Todas as 1.595 ocorrências preservadas e acessíveis; sem provar linhagem privada |
| PAR-012/G5 | Baseline C4 e históricos escopados | 545 blobs da base preservados; protocolo/SDK/Caderno intocados; G5 global não qualificado |
| PAR-015 | Integridade/estados/identidade escopados | Seed intacta e estado/token/inércia testados; sem leitura/escrita de fonte privada |
| G6/PAR-014 | Prova local privada ausente | Continua não qualificada; exige a frente LOCAL própria |

N01–N24 são confrontados individualmente no recibo CI. N01–06/09/12/15/17–21/23 recebem apenas oráculos do componente sintético. N07/08/10/11/13 (tabelas), N14/16 (aquisição) e N22/24 (integração/conformidade) não são qualificados. “Fora de escopo” não virou skip de teste. PAR-005–010 e demais lacunas continuam abertas; HL7/FHIR permanece capacidade futura, sem conformidade afirmada.

Os gates globais continuam rejeitando autoria/inventário/tooling conforme o contrato histórico de reparo e os novos logs registrados. Não foram relaxados. C4 possui sua sucessão exata após composição; G5/G6 permanecem não qualificados. AP04-POR e ARC-01–09 foram preservados, sem desvio de plano ou aprovação humana inferida.

Três subagentes nativos reais atuaram como A/B/C; C não teve autoria e ORQ foi o único publicador da branch. Branch existente e PR Draft #16 reutilizados, commits em português, parent único e lease. Nenhuma alteração em F3B, shell, reader003, Catalog/server/SDK, protocolo, R4 ou controles históricos; nenhum clone/worktree, nova branch, merge, release, deploy, migração, licença ou limpeza.
