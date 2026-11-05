# Checklist de acessibilidade e segurança — Feature 005

## Acessibilidade (resultado preencher com evidência)
- [ ] A01 1440×1200: lateral ~260 px, recolher libera área e preserva navegação.
- [ ] A02 1024×900 e 800×1000: compacta, expansão sob demanda, sem oclusão permanente.
- [ ] A03 390×844 e 320×740: Menu/fechar/Escape, foco confinado e devolvido; sem overflow do shell (WCAG 1.4.10).
- [ ] A04 Tab/Shift+Tab/Enter/Espaço, nomes acessíveis/labels, aria-expanded e aria-current corretos (2.1.1, 2.4.3, 2.5.3, 4.1.2).
- [ ] A05 Foco visível e não obscurecido; controles de pelo menos 24 px ou exceção demonstrada, alvo projetado de 44 px no mobile (2.4.7, 2.4.11, 2.5.8).
- [ ] A06 Filtros ativos removíveis/limpar mesmo recolhidos, contagens/lote em role=status; sem deslocar foco ao filtrar (4.1.3).
- [ ] A07 Detalhes, árvore/câmera/minimapa e barra de lote coexistem; reparos LQA-01/LQA-02 preservados.
- [ ] A08 Texto/estados identificados por rótulo, contraste conferido (1.4.1, 1.4.3, 1.4.11).

## Segurança/arquitetura
- [ ] S01 Conteúdo hostil permanece texto; ausência de eval/HTML dinâmico; CSP preservada.
- [ ] S02 Seleção/plano não chamam rede externa nem mutam arquivos de fonte (hashes antes/depois).
- [ ] S03 Nenhuma API de paths arbitrários, script de shell ou comando de exclusão.
- [ ] S04 Plano sempre PROPOSAL_ONLY/DELETE_AUTHORIZED=NO, incluindo baseline/falha/UNKNOWN.
- [ ] S05 JSON lexical, missing/NULL, fonte/revisão/UID/tipo preservados; snapshot novo invalida lote/anotações/intenções.
- [ ] S06 Protocolo/P03/Feature004/manifestos históricos intactos; roteamento novo somente whitelist estática, com negativos no guard.

Não equivale a auditoria completa/certificação WCAG nem revisão humana independente. Fontes oficiais no plan.md.
