# Revisão independente por SHA

Revisor nativo real: **`/root/independent_review`**. Autoria do delta: **nenhuma**.
Código examinado: `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`.
Árvore examinada: `3a6c4f1b486f47e78c1ab26643dc30ddb28d631a`.
Este documento é a transcrição atribuída do parecer recebido pelo coordenador;
não representa aprovação humana, merge ou revisão executada por outro serviço.

## Parecer de código recebido

**PASS_SCOPED.** O revisor confirmou HEAD/árvore, 27 paths no ownership, working tree
correspondente ao commit no instante da leitura e ausência de alterações do protocolo,
governança, workflows, runner e auditorias globais. Não identificou defeito de código
aberto no escopo revisado. `git diff --check` passou.

| Finding | Correção conferida no CODE_SHA | Estado |
| --- | --- | --- |
| F01 — estados do seletor rejeitados pelo parser | Removidos PLANNED/CANCELLED; opções compatíveis com o contrato | Fechado |
| F02 — retorno de foco podia encontrar um tr não focável | Busca restrita a button/input, visibilidade/foco conferidos, acionador externo preservado, fallback main | Fechado |
| F04 — fim sem início rotulado como ausência de toda data | “Sem início declarado” e data final preservada; fixture run:10/browser | Fechado |

O revisor confirmou ainda inputs/outputs explícitos, menções neutras, precisão na
comparação e `display_precision` textual, mensagem sobre a direção aceita da
ADR-0002, asset permitido no servidor e proteção contra interação antes do catálogo.

## Conferências diretas e evidências examinadas

O revisor executou a comparação de ownership e de bytes protegidos, conferiu hashes
das fixtures e comparou **9 arquivos de produção viewer e 10 SDK** dentro dos wheels
com o CODE_SHA: zero diferenças. Os dois SHA-256 dos wheels coincidem com o recibo.

Examinou os logs/JSON das execuções realizadas pelo coordenador: 98 testes normais,
os mesmos 98 com `-O`, zero falhas/erros/skips; 23 checks de navegador e seis imagens.
Essas execuções não foram repetidas pelo revisor, e a presente atribuição não as
apresenta como uma segunda execução independente.

A inspeção visual incluiu overview desktop, detalhe 390 px e regiões das imagens
320 px com e sem text spacing. Constatou quebra de textos longos, tabelas em regiões
próprias, badges e relações legíveis. A amostra inicial de contraste teve 147 amostras,
menor razão aproximadamente 4,743 e nenhuma abaixo do limiar calculado. Isso não
constitui certificação WCAG nem verifica zoom nativo.

## ENV-01 — fontes de Unicode no ambiente

Na primeira captura final de 390 px, japonês/emoji apareceram como caixas de glifos
ausentes. O texto do DOM e a busca Unicode estavam preservados; esses checks não
provavam renderização de todos os glifos. O parecer visual inicial foi
**PASS_SCOPED_WITH_ENVIRONMENT_LIMITATION**. O recibo de ambiente preserva a atribuição
da repetição com fontes compatíveis e o parecer complementar, quando executada.
Não se altera o produto para ocultar uma limitação de evidência.

## Limites e handoff ratificados

Auditoria histórica, harness global e conexão explícita de browser são P06.
Composição P03 depende de objetos congelados recebidos e testados na candidata P06.
O campo antigo PENDING de `clean_install.py` não revoga a PR #5.
O revisor exige conservar **P02_IMPLEMENTED_VERIFICATION_PENDING** enquanto faltarem
CI/convergência pertinentes. Zoom nativo permanece NOT_RUN.

O parecer não autoriza release, promoção canônica, operação do host ou aceite científico.

## Complemento final independente — ENV-01 encerrado

Parecer de código **PASS_SCOPED**; parecer visual atualizado **PASS_SCOPED nos
cenários efetivamente ensaiados**. ENV-01: **RESOLVED_SCOPED**. Mesmo CODE_SHA e
mesma árvore; revisor `/root/independent_review`, sem autoria do delta.

O revisor inspecionou as novas capturas de detalhe 390 e overview 1440 produzidas
com fontes compatíveis. Confirmou 日本語, αβγ e 🧪 renderizados sem caixas, título
extenso quebrando dentro do detalhe e botão Fechar detalhe visível. Confirmou
hierarquia e legibilidade dos controles no overview. O ambiente inicial continua
registrado como limitação histórica; a nova evidência não o transforma em PASS retroativo.

Conferiu nove hashes de recibo, proveniência, fontconfig e imagens: zero divergências.
Conferiu localmente SHA-256, objeto Git declarado e tamanho das duas fontes contra
o recibo; não realizou consulta remota neste complemento. Os 23 nomes de checks e
os hashes das fontes sintéticas são idênticos entre as execuções. Produto, scripts
executáveis e fixtures não mudaram. Não repetiu os testes unitários.

SHA-256 do novo browser.json:
`0313dc747b665540d1e5fdf58805ca64c2cdda1f2ca4f29c932686b31ffa1fd7`.
Noto Sans CJK JP 2.004 e Noto Color Emoji 2.057 ficaram limitadas ao ambiente de
evidência; a proveniência está em `receipts/font-provenance.json`.

O revisor também leu criticamente RESULT, ACCEPTANCE-MAP, REPRODUCE, REVIEW e os
recibos CI/método disponíveis, sem nova inconsistência material. Ratificou a separação
de 98 casos/2 modos, 22 checks internos, 23 checks browser, SHA de código/documentação,
autoria/revisão e método manual/helpers. Os gates P06 e zoom nativo NOT_RUN permanecem.
