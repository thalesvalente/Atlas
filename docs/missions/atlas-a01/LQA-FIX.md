# ATLAS-A01-LQA-FIX

## Escopo e reserva

Base da correção `b8fcf441cf41064927631c2eb028029684b376c6`, tree `159f5db7d4da09420630d656042ab6b5df26af5a`, parent `5ce67fe1a658cb7388570ca263d28258958613f4`. A entrega segue pela PR Draft #32 sobre a base #25 `32a0b1aeb33406cf6fbbc6b16946bd203073ced5`. Um writer para os dois reparos.

| Paths | Justificativa |
|---|---|
| `native_legacy_tree.js`, `native_notebook.js`, `native_legacy_integration.css` | Encaixar o mesmo minimapa no cabeçalho dos detalhes durante a seleção. Restaurar sua posição no mapa ao fechar. Reutilizar os controles de câmera por teclado. |
| `native_legacy_model.js`, `native_legacy_views.js` e CSS de integração | Aplicar a política de execução ao cartão, ao índice e aos badges de tabela e detalhe. Preservar a seleção do estado e as declarações originais. |
| `scripts/qa/run_a01_application_ux_browser.py`, `scripts/qa/browser_application_ux_a01.mjs`, `scripts/qa/browser_a01_lqa.mjs` | Acrescentar fixtures inventadas e verificar hit-testing, interação real, estilo computado e contraste no harness instalado. |
| `docs/missions/atlas-a01/REUSE-MANIFEST.json` e este recibo | Conferir hashes e deslocamentos das declarações de destino afetadas. |

O Spec Kit 1.2.3 instalado e o helper `check_prerequisites.py --json --require-tasks --include-tasks` localizaram a Feature 004 com `SPECIFY_FEATURE_NO_PERSIST=1`. A checklist de requisitos tinha 5/5 itens marcados. Constituição, contrato e política de transferência foram usados em leitura. O pacote de protocolo, o DTO e o P03 permanecem vinculados aos mesmos blobs.

## LQA-01

O minimapa ficava no canto do mapa coberto pela área fixa dos detalhes. Agora ocupa um espaço próprio no cabeçalho fixo dentro do painel aberto. Com o painel fechado, retorna ao mapa. O tamanho responsivo anterior foi preservado. O mapa e o minimapa compartilham as teclas de pan, zoom e enquadramento. O painel conserva seu botão de fechamento, rolagem e retorno de foco.

No RED instalado, a fixture reproduziu o bloqueio nas larguras desktop e mobile e 25/25 pontos alcançáveis com o painel fechado. A versão corrigida exigiu 25/25 em cinco estados por viewport e clique ou toque real com mudança do `viewBox`. As larguras exercitadas foram 1440, 1101, 1100, 1024, 800, 721, 720, 390 e 320 px. O teste verificou cartão selecionado inteiro e legível após Focar seleção, rolagem da página e do painel, fechamento por Escape, foco restaurado e reabertura.

## LQA-02

O texto obedecia à precedência e a cor dos badges vinha de `result_group`. A política agora usa o valor selecionado por `recordExecutionState` em todas as superfícies. Tokens conhecidos usam tons de execução por correspondência exata sem diferença entre maiúsculas e minúsculas. `published`, desconhecidos, valores vazios, ausentes, NULL, false, zero e estruturas usam tom neutro de execução. As declarações de publicação, revisão e retenção continuam separadas. Índice, acento, texto e badges usam o mesmo significado visual.

O RED registrou `FAILED` em verde com grupo `published` e `SUCCEEDED` em vermelho com grupo `failed`. A matriz de 23 ocorrências verificou os dois conflitos, cada chave da precedência, fallback, ausentes e falsy, desconhecidos, variantes de texto, estruturas e marcação hostil. O navegador conferiu cor computada, contraste, texto e os campos originais no JSON inspecionado.

## Verificação

- `node --test scripts/qa/test_native_legacy.mjs scripts/qa/test_native_a01_fix.mjs`.
- `python -m unittest discover -s tests/viewer -v`. O host usou `NODE_OPTIONS=--test-reporter=tap` para o formato de saída esperado pelo wrapper.
- `python scripts/qa/run_application_ux_browser.py --work <diretório-de-evidência> --require-graph-cancel` e runner A01 focado. Chrome instalado, fonte exportada sintética e comparação dos assets. Busca, filtros tipados, paginação, retorno, JSON/CSV e layout de catálogo/registros foram exercitados.

A qualificação por SHA usa os runs e o recibo do review da PR #32. Evidências de host privado ficam locais. Para a próxima verificação privada, autenticar o pacote e os cinco assets alterados, repetir F11 com detalhes e minimapa em desktop/mobile, repetir a fixture de cores e fazer smoke de busca, tabela, retorno e exportação. `HUMAN_ACCEPTANCE=PENDING`.
