# Checklist de acessibilidade e segurança — Feature 005

## Acessibilidade — PASS_SCOPED no candidato de produto
- [x] A01 1440×1200: lateral 273,6 px dentro do intervalo 240–280; recolher libera área e preserva navegação.
- [x] A02 1024×900 e 800×1000: compacta, expansão sob demanda, sem oclusão permanente. Prova adicional em 1101×900 com lateral e detalhes abertos.
- [x] A03 390×844 e 320×740: Menu/fechar/Escape, foco confinado e devolvido; sem overflow do shell (WCAG 1.4.10).
- [x] A04 Tab/Enter/Espaço, nomes acessíveis/labels, aria-expanded e aria-current corretos nos fluxos exercitados (2.1.1, 2.4.3, 2.5.3, 4.1.2). Contraprova explícita adicional de Shift+Tab incluída para o gate terminal; resultado vinculado ao seu SHA no handoff.
- [x] A05 Foco visível e não obscurecido; alvos amostrados de pelo menos 24 px, controles mobile projetados para 44 px (2.4.7, 2.4.11, 2.5.8). Cartão focado recebe 25/25 hits nas seis resoluções.
- [x] A06 Filtros ativos removíveis/limpar mesmo recolhidos, contagens/lote em role=status; foco de controles preservado nos fluxos (4.1.3).
- [x] A07 Detalhes, árvore/câmera/minimapa e barra de lote coexistem; minimapa recebe 25/25 hits; LQA-01/LQA-02 PASS no sucessor.
- [x] A08 Texto/estados identificados por rótulo. Cores computadas dos quatro alvos de texto novos: mínimo 4,970245:1; outline do cabeçalho: mínimo 4,763086:1. Cores de execução verificadas pelo LQA-02 (1.4.1, 1.4.3, 1.4.11).

## Segurança/arquitetura
- [x] S01 Conteúdo hostil permanece texto; ausência de eval/HTML dinâmico no produto novo; CSP preservada.
- [x] S02 Seleção/plano não chamam rede externa nem mutam arquivos de fonte: zero HTTP no intervalo de planejamento e quatro hashes idênticos antes/depois.
- [x] S03 Nenhuma API de paths arbitrários, script de shell ou comando de exclusão.
- [x] S04 Plano sempre PROPOSAL_ONLY/DELETE_AUTHORIZED=NO, incluindo baseline/falha/UNKNOWN.
- [x] S05 JSON lexical, missing/NULL, fonte/revisão/UID/tipo preservados; snapshot novo invalida lote/anotações/intenções.
- [x] S06 Protocolo/P03/Feature004/manifestos históricos intactos; roteamento novo somente whitelist estática, com negativos no guard.

Evidência: SHA `3a9e1e3d2727c69175768abb437bdcbc47cfabf0`, tree `23b1c290aedf511c0903eaf9dd016296ec7ebe8b`; [relatórios e telas](../evidence/README.md). As aprovações são limitadas às tarefas, elementos amostrados, Chromium e fixtures declaradas. O HEAD documental posterior exige CI/review próprios, registrados no handoff terminal da PR #33.

Não equivale a auditoria completa/certificação WCAG nem revisão humana independente. Fontes oficiais no plan.md.
