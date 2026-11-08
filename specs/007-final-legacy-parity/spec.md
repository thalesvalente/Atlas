# Feature 007 — Paridade final e prontidão de retirada

Pedido do operador: 2026-11-07. Extensão compatível das Features 004/005,
governada por ARC-01–09. Não concede merge nem retirada do R4.

## Requirements

- FR-001: conferir projeção explicitamente escolhida por hash de bytes e revisão
  esperados antes de comparar o pacote; digest próprio não prova origem ou frescor.
- FR-002: comparar conteúdo, tipos, presença, identidade estrutural e exportação
  integral; separar importação/exportação de pesquisa e teste visual.
- FR-003: oferecer CSV tipado reversível que conserve ausência, NULL, vazio,
  números exatos, IDs homônimos, campos originais de linha e fórmulas inertes.
  Preservar o CSV protegido compatível e o JSON integral.
- FR-004: testar adulteração, revisão obsoleta em relação ao pin e fonte divergente.
  Não escrever em fontes, executar produtor real nem importar código R4.
- FR-005: registrar PAR-001–015, limites de autenticação/cobertura, consumidores,
  Chrome real e retirada separadamente, sem herdar PASS de SHAs anteriores.

## Success Criteria

- SC-001: contraprovas sintéticas RED/GREEN para colisões de CSV e pins inválidos.
- SC-002: o oráculo lê pacote sem runtime R4 e demonstra igualdade de cada campo
  no snapshot declarado, ou falha com motivo verificável.
- SC-003: novas mudanças recebem CI Windows/Ubuntu e revisão próprias; Chrome
  bloqueado recebe BLOCKED, sem promoção a PASS por HTTP ou Chromium sintético.

HL7/FHIR permanece extensibilidade futura. Não altera protocolo ou ciência.

## Continuação operacional autorizada — 2026-11-07

Reutilizar a PR #39 e PAR-001–015; a frente R4 tem branch/PR próprias.
O operador autoriza a separação mínima de produtor/interface e a substituição
dos consumidores C01–C09, preservando fontes científicas e rollback histórico.

US1: como usuário do Atlas, recuperar informação e concluir tarefas essenciais
pela aplicação nova, com equivalência verificável por capacidade (SC-004).
US2: como operador R4, validar e exportar a ciência para o Atlas independente,
com falhas explícitas e retorno ao histórico preservado (SC-005).

- FR-006: avaliar capacidade e resultado, sem exigir os mesmos controles ou layout.
  Usar EQUIVALENT, SUPERIOR_REPLACEMENT, INTENTIONAL_DIFFERENCE, MATERIAL_GAP
  ou NOT_PROVEN. Superioridade exige mesma necessidade atendida, informação
  essencial, identidade/proveniência/estados, ausência de regressão material e
  benefício demonstrável; ausência de prova nunca equivale a PASS.
- FR-007: comprovar percursos essenciais no Chrome Windows real ou registrar
  WAIT_HUMAN_EXACT. Respeitar interrupção de segurança; HTTP/Chromium sintético
  e comparação de conteúdo não completam esse gate. Não preparar a demonstração
  modificando o Caderno.
- FR-008: manter produção, projeção, validação, ledger, históricos, migração e
  verificadores científicos no R4. Oferecer entrypoint de dados independente do
  renderer; conservar contratos e aliases científicos utilizados legitimamente.
- FR-009: substituir launcher e consumidores operacionais pertinentes C01–C09,
  com argumentos/caminhos, erros e exit codes preservados e rollback explícito.
  Identificar os nove assets legados, sem excluí-los.
- FR-010: qualificar inicialização e refresh, fonte ausente/obsoleta, revisão
  incompatível, pacote inválido, erros/subprocessos e rollback com fixtures
  isoladas. Produtor/migração reais no Caderno original permanecem NOT_RUN.
- FR-011: integrar recibos de owners e QA não autora, CI Windows/Ubuntu e Codex
  Review vinculados aos SHAs finais. Separar aprovação técnica de aceite humano.

- SC-004: PAR-001–015 registram fluxo OLD/NEW, informação, diferença, teste,
  classificação, evidência e resultado, com dimensão Chrome explícita.
- SC-005: C01–C09 têm classificação de responsabilidade, dependências diretas e
  reversas, contrato de substituição/rollback e testes de fronteira verificáveis.
- SC-006: prontidão de retirada só é concedida com P01 e P02 concluídos/revisados;
  nunca autoriza remoção. KEEP_FULL=5, DELETE_AUTHORIZED=NO.

## Refinamento após reteste do operador

As capturas de reteste identificaram densidade excessiva do catálogo e mistura
de populações da fonte com estado local na visão geral. O operador também pediu
agrupamento dos requisitos pelo núcleo informado. A continuação permanece em 007.

- FR-012: manter catálogo compacto em desktop, intermediário e móvel, com seleção
  e título separados de forma legível, sem impor uma linha vazia adicional por
  controle quando há espaço disponível. Preservar foco e área de clique.
- FR-013: distinguir resumo declarado da fonte, agregações da navegação e estado
  da sessão. Expor populações essenciais antes recuperáveis no resumo legado,
  com rótulo, unidade e origem verificáveis. Ausência não pode virar zero; zero
  declarado permanece zero. Não inferir execução ou aceite a partir de contagens.
- FR-014: permitir agrupamento reversível das linhas de requisitos pelo núcleo
  explicitamente declarado. Valores sem núcleo têm grupo identificado, sem
  inferência por título/ID. Preservar campos, identidades, tipos, filtros,
  paginação e exportações integrais em JSON/CSV tipado.
- SC-007: contraprovas sintéticas distinguem resumo da fonte e seleção/baselines
  locais; verificam ausência/zero e agregações com denominadores diferentes.
- SC-008: agrupamento mantém a mesma população e conteúdo exportado, enquanto
  catálogo continua legível e compacto nas larguras qualificadas pela CI.

## Refinamentos finais solicitados pelo operador

O operador confirmou os ajustes anteriores e pediu dois refinamentos delimitados:

- FR-015: oferecer coluna estreita exclusiva para seleção no catálogo, com caixa
  por linha e cabeçalho único. Remover texto visível repetitivo sem perder nome
  acessível, alvo de interação, teclado, seleção ou acesso ao documento.
- FR-016: permitir expandir/recolher cada região de núcleo, preservando a escolha
  na sessão por fonte/revisão/tabela/grupo. Paginação e filtros não alteram os
  dados; localizar uma linha revela seu grupo quando necessário. Recolher uma
  região não modifica seleção, população, identidades ou exportações.
- SC-009: testes cobrem coluna compacta/acessível, alternância de regiões,
  preservação de contexto e exportação integral com grupos recolhidos.
