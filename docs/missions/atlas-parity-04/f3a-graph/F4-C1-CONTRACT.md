# Contrato sucessor focal — escala F4 C1

Sucessor de GRAPH-CONTRACT.md, preservado no SHA histórico f0d39787e3fb93bfd70ad096824505ba298c6881. API e descriptor 0.2.0 continuam exclusivamente in-memory. Este contrato não acrescenta aquisição, integração no shell, mudança de protocolo ou autorização científica.

## Modelo completo e desenho por janela

Todos os nós e relações admitidos permanecem no modelo. Os antigos 1.000 nós/4.000 relações passam a limitar o desenho, sem recusar o modelo apenas por exceder essas contagens. O SVG principal desenha até 1.000 nós, 4.000 relações e 4.000 arestas hierárquicas por janela. Foco e seleção expandidos são preservados na janela quando possível. Até 1.000 nós, o desenho mantém o comportamento integral herdado.

Relações fora do desenho continuam disponíveis no painel sequencial de ocorrências, incluindo repetições, endpoints nulos, não resolvidos e colidentes. O desenho não altera endpoints ou inventa resolução.

getState distingue:

- declared_node_count: tamanho de descriptor.nodes; não é população global;
- loaded_node_count/node_count: modelo completo;
- visible_ids: traversal de todos os nós da hierarquia expandida;
- rendered_ids/rendered_node_count: subconjunto SVG;
- rendered_relation_count/rendered_parent_edge_count: desenho de relações/hierarquia;
- relation_count: total carregado; selection: contexto atual.

Contagens da fonte não são reescritas; global_total continua null/UNKNOWN_UPSTREAM. Colapso conserva o modelo e a seleção.

## Navegação e minimapa

graph.reveal(nav_id) localiza um nó no índice corrente e expande somente ancestrais explícitos previamente validados. Retorna false para identidade ausente, contexto expirado ou falha de desenho; não seleciona nem admite native_id. O finder localiza nav_id exato ou substring de nav_id/rótulo e percorre resultados sem deduplicar ocorrências.

Identidade source_id/snapshot_id/nav_id/occurrence/session_id e invalidações anteriores permanecem. Native_id nulo continua nulo. Teclado navega o índice expandido e materializa o destino antes de focá-lo no DOM. Pan/zoom/fit/reset atualizam a janela. Colapso retorna o foco a um ancestral visível quando necessário. Hierarquia não vira causalidade.

O minimapa grande agrega posições em até 32×64 marcas geométricas. Sua contagem soma o índice expandido; marcas não são entidades, ancestrais ou relações científicas. PreserveAspectRatio none distribui o resumo por toda a área CSS, e a CTM inversa mapeia cliques para posições do grafo. O oráculo mede largura útil, soma de ocorrências e centralização real da câmera sobre uma marca clicada.

## Limites reais

O envelope aprovado permanece 32 MiB, profundidade 20, 10.000 nós e 100.000 relações. Limites de bytes e contagem se aplicam simultaneamente; o máximo de contagem não garante que qualquer payload dessa contagem caiba em 32 MiB.

copyJSON preserva o limite auxiliar herdado de 600.000 valores visitados e 131.072 bytes por literal; semanticModel mantém 65.536 bytes por célula. Esses limites podem recusar payloads abaixo dos máximos de contagem e precisam continuar explícitos ao integrador. Recusa é atômica e visível, sem modelo/seleção parcial. O prazo de 30 s permanece por operação.

operation_ms mede setData, incluindo cópia, validação, modelo, layout e desenho; draw_ms mede a última janela. Heap Chromium, quando exposto, é observação do teste e não certificação de hard heap de 256 MiB. O componente não lê ou parseia arquivos externos, faz rede/storage, abre URI, injeta script ou recebe fonte privada.

## Qualificação e gate do integrador

A fixture sintética gerada de 2.911 nós/1.595 relações preserva o seed histórico de 109/210, incluindo anomalias e repetições. A fonte real F1 não foi executada ou publicada. Testes e revisão do novo SHA decidem a qualificação focal; não herdar PASS anterior.

No SHA técnico 913e4038, 10.000 nós/0 relações, com 5.407.991 bytes, foram aceitos. 10.001 nós foram recusados integralmente. O stress de 10.000/100.000 mede 81.008.070 bytes e foi recusado por 600.000 valores, além de exceder 32 MiB. Não qualifica 100.000 relações válidas dentro de 32 MiB.

REAL_VALUE_CAP_GATE_INTEGRATOR_REQUIRED conserva essa limitação para composição. Qualquer mudança aplicável de quota, contrato ou plano exige decisão antes de implementar. G5/G6 e hard heap de 256 MiB continuam não qualificados. A sucessão dos controles globais pertence a C4; CI/revisão do HEAD documental são vinculadas externamente no PR #16.
