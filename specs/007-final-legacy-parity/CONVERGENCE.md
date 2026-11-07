# Análise e convergência do incremento

## Spec Kit efetivamente usado

CLI instalado 1.2.3; integração Codex íntegra (28 assets gerenciados), sem instalar
ferramentas. `check_prerequisites.py` executado para 004/005/007;
`setup_plan.py` e `setup_tasks.py` executados em 007 com seleção explícita e
NO_PERSIST. Plan existente preservado, tasks escritas pelo integrador a partir
dos requisitos. Sem feature.json ou extensão de hooks local.

## Análise anterior à implementação

Cinco requisitos FR e três critérios SC cobertos por sete tasks. ARC-01–09
preservadas. FR-001/002/004→T004/T005; FR-003→T002/T003;
FR-005→T001/T006/T007; SC-001→T002–T005; SC-002→T004/T005;
SC-003→T006/T007. Nenhum conflito arquitetural ou requisito de implementação
sem task identificado. Reutilizados componentes aceitos; nenhuma rota nova,
mudança de protocolo ou importação de código produtor.

## Implementação e verificação

O callback anterior reproduziu colisões de CSV; o formato tipado conserva
tokens, presença, tipos e linha original. O formato anterior continua como opção
de leitura com limite explícito. O teste de browser baixa todas as 127 linhas
sintéticas selecionadas, incluindo as fora da página, e confere o formato novo.

O oráculo exige pins externos de bytes/revisão e compara exportação integral.
Negativos recusam pin/revisão/conteúdo divergentes, pacote adulterado, decimal
não suportado e relatório dentro das fontes. `--summary-only` conserva a
comparação e o índice de campos sem duplicar grandes relatórios.

Em `29380daa17ae97151eb6db5239cc3f0df337f89f`: 130 regressões Node;
128 testes Python por modo normal/-O (126 PASS/2 SKIP em cada modo) em ambiente
instalado sem R4; 19/19 Actions SUCCESS Windows/Ubuntu/Chromium; Codex Review
completed sem findings; revisão de agente não autor com contraprovas próprias.
O manifesto A01 histórico e a política de publicação permanecem byte-idênticos;
somente hashes/âncoras do manifesto sucessor foram reconciliados.

## Convergência

O incremento satisfaz os cinco requisitos e três critérios implementáveis do
spec/plan/tasks. Não há código restante identificado neste recorte nem nova task
de implementação a acrescentar. O sucessor documental necessita atestação/CI e
revisão próprias; o recibo da PR fixa o SHA terminal, evitando referência circular.

Os pareceres privados permanecem separados: paridade parcial exata e retirada
bloqueada antes de substituir consumidores. Chrome Windows real não recebe PASS
da CI Chromium/HTTP. A automação Windows encerrou por política de URL; eventual
relato manual do operador é identificado como tal. Sem resultado manual, o gate
permanece aberto. Snapshots distintos conservam revisões distintas; igualdade
local não prova cobertura global, origem assinada ou aceite científico.

Código válido publicado em branch própria/PR Draft #39. Sem alteração R4,
execução de produtor real, merge, release, deploy ou autorização de retirada.

## Continuação de uso e consumidores

Constituição ARC-01–09 reavaliada sem alteração. Spec/plan/tasks existentes
estendidos para FR-006–011 e SC-004–006; 17 requisitos/critérios cobertos por
T001–T016. Helpers oficiais 1.2.3 executados com seleção explícita de 007 e
NO_PERSIST; setup-plan preservou o plano existente. Auditoria dos 28 assets
gerenciados passou com o escopo de apresentação já autorizado. Sem hooks locais,
nova feature, worktree ou documento redundante.

O relato do operador identificou junção do texto de seleção ao título e ação de
zerar seleção escondida. A correção torna o botão existente Desmarcar todos (N)
visível junto aos seletores, mantém seleção/contagem e preserva anotações e foco.
Três contraprovas iniciais e duas independentes de foco reproduziram RED;
GREEN local 14/14 e regressão Node 135/135. A geometria de catálogo e interação
entram no workflow Chromium sintético existente. Isso não concede Chrome PASS.

O adaptador externo e guardas dos launchers passaram a exigir a API produtora
separada. Três subprocessos sintéticos provaram exportação sem renderer,
recusa de checkout somente legado e propagação de erro sem publicar pacote.
Regressão Python 39 casos por modo normal/-O: 38 PASS e um SKIP POSIX no Windows.
O manifesto A01 histórico permanece intacto; apenas o sucessor de destinos foi
reconciliado contra o commit de implementação desta continuação.

Na candidata R4 separada, o produtor mantém os três corpos AST da main e
atlas.project como alias; launcher/CLI/migração/documentação foram atualizados
e os nove assets preservados. Testes selecionados 125/125 e QA focal não autora
25/25. A integração detectou e corrigiu colisão entre diretórios de projeção e
pacote sem relaxar a guarda do exportador. Cold start, nova revisão/refresh,
pin obsoleto e exportação direta passaram com subprocessos/HTTP e fixtures
científicas inventadas. Produtor no Caderno original permanece NOT_RUN.

A comparação das capturas legadas fornecidas pelo operador foi registrada
somente nos recibos privados. Essa equivalência informacional delimitada não
comprova a UI corrigida nem cobertura global. Coleções ausentes da fonte não
foram inventadas para produzir opções de interface.

T013 fica aberto neste snapshot documental até os recibos terminais de
CI/review por SHA. O handoff privado consolida resultados e gates separados.
O estado de paridade permanece PARTIAL_EXACT até
requalificação visual do operador; a comparação de uso OLD/NEW ainda não foi
realizada. Não há nova tarefa de código conhecida além de eventual finding
material; gates externos permanecem explícitos e não são promovidos a PASS.

A primeira CI da continuação aprovou domínio/escopo nos dois OS, mas a nova
guarda geométrica falhou na largura intermediária após passar em desktop.
O catálogo passou a separar o controle em linha própria com margem vertical;
a guarda de espaço e ausência de overflow foi mantida. Diagnósticos são gravados
antes das asserções. Node 135/135 e QA local 14/14 passaram; o GREEN renderizado
do sucessor depende de CI própria, registrado fora deste snapshot documental.

## Refinamento do reteste: resumo e núcleo

O novo pedido do operador acrescenta FR-012–014 e SC-007/008, mantendo a Feature
007. A análise cobre 22 requisitos/critérios por T001–T020, sem mudança ARC ou de
protocolo. P01 permanece writer único da UI; P03 audita sem escrever no código.

O catálogo agora permite seleção e título na mesma linha com quebra controlada.
A visão geral separa populações declaradas, agregações de navegação e contadores
locais, preservando ausência, zero explícito e tokens numéricos exatos. A leitura
por núcleo usa somente metadados/células declarados, mantém identidade contextual
e oferece ordem original reversível. Exportações continuam usando as linhas
originais filtradas. Localização e retorno de página respeitam a organização.

RED inicial: quatro contraprovas de modelo/DOM; achados de revisão também
reproduziram contador local desatualizado e destino de baselines ambíguo. Todos
foram corrigidos. GREEN focal 60/60 e regressão Node 141/141; QA independente
executou 19 casos de UI/contraprovas, incluindo localização paginada com núcleos
intercalados, preservação de UID/raw e contadores locais sem alterar a fonte.
Nenhuma declaração conflitante foi promovida a baseline confirmada.

Fixtures e novas verificações Chromium usam somente dados inventados, incluindo
invariância de JSON/CSV ao agrupar, contagens de origem/sessão e catálogo compacto.
O gate renderizado requer CI e Codex Review do novo SHA; resultados anteriores
permanecem históricos. Reteste manual e uso OLD/NEW mantêm gates próprios.

A convergência encontrou uma lacuna de rótulo/destino dos indicadores e anexou
T021, elevando a rastreabilidade a 22 requisitos/critérios e 21 tasks. Os botões
agora nomeiam a área ampla que abrem, preservando contexto e contagens. A
contraprova independente de navegação passou; regressão Node 142/142. Não resta
lacuna de código conhecida neste recorte após revisão local; CI/review do SHA
sucessor e prova manual continuam separados do resultado técnico anterior.
