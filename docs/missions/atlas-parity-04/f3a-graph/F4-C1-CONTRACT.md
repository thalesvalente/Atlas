# Contrato sucessor focal — escala F4 C1

Sucessor de GRAPH-CONTRACT.md, que permanece intacto no SHA histórico f0d39787e3fb93bfd70ad096824505ba298c6881. API e descriptor0.2.0 continuam exclusivamente in-memory; nenhum novo caminho de aquisição ou integração no shell. Este texto não altera schema, protocolo ou autorização científica.

## Modelo integral e desenho por janela

O modelo conserva todos os nós e relações admitidos. Os antigos1.000 nós/4.000 relações passam a ser teto de desenho, não recusa por contagem do modelo. SVG principal desenha até1.000 nós,4.000 relações e4.000 arestas hierárquicas por janela. Nó/foco e seleção expandidos são pinados quando possível. Abaixo de1.001 nós o desenho conserva comportamento integral herdado. Relações fora do desenho continuam disponíveis sequencialmente no painel de ocorrências, inclusive repetições/null/unresolved/collision. Limite de desenho não altera endpoints nem inventa resolução.

getState distingue declared_node_count (descriptor.nodes, não população global), loaded_node_count/node_count (modelo completo), visible_ids (traversal de todos os nós da hierarquia expandida), rendered_ids/rendered_node_count (subconjunto SVG), rendered_relation_count e rendered_parent_edge_count. relation_count é total carregado, selection é contexto atual. Contagens da fonte no descriptor não são reescritas; global_total continua null/UNKNOWN_UPSTREAM.

graph.reveal(nav_id) localiza qualquer nó do índice corrente e expande somente ancestrais explícitos previamente validados; retorna false para identidade ausente, contexto expirado ou falha de desenho. Não seleciona nem admite native_id. O finder localiza nav_id exato ou substring de nav_id/rótulo e percorre resultados sem deduplicar ocorrências. Identidade source_id/snapshot_id/nav_id/occurrence/session_id e invalidações anteriores mantidas. Native_id nulo não recebe identidade nativa por localização.

Pan/zoom/fit/reset atualizam a janela, teclado navega índice completo de nós expandidos e materializa o destino antes do foco DOM. Colapso conserva modelo/seleção e retorna foco a ancestral visível quando necessário. Minimapa grande agrega posições em no máximo32×64 bins geométricos com contagem; bins não são nós/ancestrais/relações científicos. Soma data-bin-count equivale ao índice expandido. Hierarquia e causalidade permanecem distintas.

## Limites reais

Envelope aprovado permanece32MiB/profundidade20/10.000 nós/100.000 relações. Limites simultâneos de bytes e contagem se aplicam: o máximo de contagem não garante que qualquer payload dessa contagem caiba em32MiB. copyJSON preserva limite auxiliar herdado de600.000 valores visitados e131.072 bytes por literal; semanticModel mantém65.536 bytes por célula. Esses limites reais podem recusar dentro dos máximos de contagem e precisam permanecer visíveis ao integrador; não equivalem a suporte integral do teto100.000 relações.

Recusa é atômica e visível, sem seleção/modelo parcial. Prazo30s permanece por operação. operation_ms mede setData com cópia/validação/modelo/layout/desenho; draw_ms mede última janela. Métricas de heap Chromium, quando expostas, são observações do processo de teste, sem certificação de hard heap256MiB. Não há execução/parse externo, rede, storage, abertura de URI, script injetado ou fonte privada.

## Qualificação

Fixture sintética gerada determinística de2911/1595 amplia seed original109/210 preservada:22 endpoint-null,75 unresolved,50 endpoints colidentes,50 IDs nativos com duas ocorrências e40 grupos/41 repetições adicionais. Fonte real F1 não foi publicada nem executada. Testes/CI e revisão do novo SHA decidem qualificação focal; não herdar PASS anterior. G5/G6 e sucessão de controles globais pertencem à composição/C4 conforme contrato histórico.

Revisão geométrica C1: minimapa usa preserveAspectRatio none para distribuir o resumo por toda a área CSS; CTM inversa mantém o clique na posição geométrica correspondente. Isso impede a árvore alta de colapsar numa faixa subpixel. O oráculo mede largura útil dos bins, soma das ocorrências e centralização real da câmera sobre uma marca clicada.
