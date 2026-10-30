# P01 — Contrato candidato de cobertura e perdas

**Estado:** `CANDIDATE`, evidência derivada opcional; não é extensão persistida aprovada do Caderno. **Baseline:** `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, árvore `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`. **Autoria semântica:** agente nativo `/root/semantics`.

## 1. Pergunta que cada número deve responder

Toda contagem informa **o que foi contado, em qual universo, por qual critério, em qual camada, quando e com qual evidência**. O número de runs carregadas não estima o tamanho do acervo. Um denominador desconhecido permanece desconhecido. Zero só representa uma medição de conjunto vazio, não falha de acesso, ausência de estudo ou seleção que não foi executada.

O [contrato 003](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/contracts/reader.md#L3-L9) separa aquisição de transformação. Seu [modelo de dados](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/data-model.md#L1-L16) exige registrar dados fora do recorte como contagem/lacuna, sem fabricar registros. Essas obrigações justificam um relatório derivado de cobertura; não tornam esse relatório entrada obrigatória do viewer. E009/E015.

## 2. Camadas e unidades que não podem ser somadas

| Camada | Universo observável | Unidade possível | O que a baseline autoriza afirmar |
|---|---|---|---|
| `source` / fonte | Acervo ou entrada efetivamente autorizado e observado pelo produtor | Registros nativos, arquivos ou outra unidade declarada | O viewer não inventaria esse universo; sem recibo, `UNKNOWN` |
| `projection` / projeção | Resultado já produzido pelo pipeline autorizado | Entidades/execuções projetadas, identificadas por tipo | Quantidade depende da evidência da projeção; não é a contagem da fonte |
| `selection` / seleção | Subconjunto escolhido com critério e IDs explícitos | Mesma unidade da projeção quando o mapeamento for 1:1 | Informar seleção exata, exclusões e vínculos cortados; seleção não comprova aquisição |
| `conversion` / conversão | Entradas tentadas, convertidas, recusadas ou não representadas | Registros de entrada e entidades de saída, separadamente | Conversão pode dividir/agrupar; não subtrair unidades diferentes |
| `package` / pacote | Grafo e payloads do snapshot publicado | Entidades por tipo; arquivos declarados; payloads observados | `@graph` inclui descritor/perfis/agentes além de dados; isso não é número de runs |
| `read_model` | Projeção aceita pelo leitor | `projects`, `experiments`, `runs`, `artifacts`, `relations`, `entities` | `entities` conserva todo o grafo; categorias sobrepõem-se e não devem ser somadas |
| `interface` | Registros elegíveis e exibidos numa vista/filtro | Runs visíveis, referências únicas, linhas de uma tabela | A contagem depende da vista e filtros; não prova perda no pacote |

Fonte factual para as três últimas camadas: [read_model.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/read_model.py#L18-L81), [catalog.py](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/catalog.py#L73-L138) e [app.js](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/static/app.js#L23-L45), E010/E012/E013.

**CC-UNIT-01:** cada medida declara unidade. Um pacote não equivale a uma execução; entidades do grafo não equivalem a documentos; menções repetidas não equivalem a referências únicas. Um total de relações inclui seu critério de identidade, direção e deduplicação.

**CC-OVERLAP-01:** não somar etapas de um mesmo fluxo, categorias que contêm os mesmos itens, snapshots sobrepostos ou seleções repetidas. Só agregar fontes disjuntas quando a disjunção e a chave de deduplicação forem demonstradas. Mesmo ID em pacotes distintos continua ocorrência distinta no catálogo; não prova objetos científicos distintos nem permite deduplicação global.

## 3. Campos mínimos de uma medida derivada

Os nomes abaixo descrevem obrigações do relatório e dos exemplos P01. Não são propriedades novas de `ro-crate-metadata.json` nem de `/api/catalog`.

| Campo lógico | Obrigação candidata |
|---|---|
| Identidade do escopo | Fonte/pacote, digest dos bytes pertinentes quando disponível, revisão da projeção/recibo e catálogo/generation quando aplicável |
| Camada e unidade | Uma das sete camadas acima e unidade explícita, sem alternar unidade dentro da mesma série |
| Valor e estado | Inteiro não negativo conhecido, ou null + `UNKNOWN` e motivo; nunca `false` como zero |
| Critério | Filtro, seleção de IDs, deduplicação, tipos incluídos/excluídos e tratamento de inválidos |
| Evidência | Origem observável, caminho público/recibo permitido e digest/revisão; separada de sua interpretação |
| Instante da observação | Tempo do ato de medição com fuso, ou desconhecido; não substitui tempos científicos |
| Denominador | Outra medida identificada, com unidade, escopo e critério compatíveis, ou desconhecido |
| Mapeamento entre camadas | Correspondência que permite calcular retenção/perda; 1:1, divisão, agregação ou desconhecida |
| Perda/limitação | Camada de origem e destino, classe, quantidade quando conhecida, motivo e responsável |

O worksheet `ATLAS_P01_COVERAGE_EXAMPLE` usa `known: false` com `count: null` para o estado desconhecido e associa os motivos a perdas/limitações do mesmo cenário, conforme [VALIDATION.md](VALIDATION.md). Não exige a string literal `UNKNOWN` em um campo numérico. Seu booleano `collection_total_inferred_from_loaded_runs: false` proíbe apenas essa inferência indevida: um total medido diretamente na fonte continua admissível com evidência, unidade e escopo próprios. `derived: true` e `caderno_required: false` conservam a natureza opcional e derivada do exemplo.

IDs `source-N` são locais ao catálogo ordenado. `generation` é local à instância. Digest não confere autenticidade nem estabilidade de identidade entre reordenações. Um relatório que compara catálogos precisa de mapa explícito ou marca a correspondência desconhecida. Ver PC-ID-01/02 em [PRESENTATION-CONTRACTS.md](PRESENTATION-CONTRACTS.md).

## 4. Denominadores e razões

**CC-DEN-01:** para exibir uma razão `n/d`, registrar a pergunta, o numerador e o denominador. É permitido, por exemplo, “2 de 5 execuções carregadas aparecem em Explorar com este filtro”, se os cinco registros são o conjunto elegível da mesma geração do índice e os dois são seu subconjunto. Não é permitido “40% do acervo recuperado” a partir desses mesmos números.

**CC-DEN-02:** uma taxa só pode ser calculada quando os valores forem conhecidos, o denominador for maior que zero, a unidade for idêntica, o numerador for um subconjunto demonstrado do denominador e o escopo/critério/observação forem compatíveis. Quando necessário, a relação de subconjunto pode cruzar camadas mediante mapa explicitamente declarado; a mera igualdade numérica não basta. `n > d` é erro para uma taxa de retenção de subconjunto, mas não prova erro em uma transformação 1:N: nesse caso a fórmula é inaplicável.

**CC-DEN-03:** `0/0` não é 100% nem 0%; exibir “não aplicável: universo medido vazio”. `n/UNKNOWN` não tem percentual. Uma contagem exata de saída pode coexistir com denominador desconhecido, sem bloquear sua apresentação.

**CC-DEN-04:** o tipo, unidade e escopo do denominador ficam legíveis ao usuário, não apenas no JSON. Percentuais arredondados não apagam os inteiros exatos nem pretendem precisão maior que a evidência.

### Exemplo de leitura correta, sem total histórico presumido

Um pacote sintético pode conter quatro `CreateAction`, o read model pode expor as mesmas quatro runs e o filtro pode mostrar duas. Isso comprova `4/4` para a projeção das execuções **daquele pacote** e `2/4` para a seleção visual, se o ensaio declarar esses conjuntos. A fonte histórica, a projeção anterior e o total de documentos podem continuar `UNKNOWN`. As contagens 4 + 4 + 2 não formam dez registros únicos.

## 5. Classificação de perdas e lacunas

| Classe de lacuna | Significado | Prova mínima |
|---|---|---|
| `NOT_OBSERVED` | Camada não acessada/medida ou evidência indisponível | Etapa não executada e motivo; quantidade desconhecida |
| `OUT_OF_SELECTION` | Registro conhecido excluído pelo critério explícito | Universo/seleção comparáveis e identificação ou contagem permitida |
| `CUT_REFERENCE` | Relação declarada cuja outra ponta ficou fora do recorte | Mapeamento de relação e motivo; não inventar alvo nem mudar sua semântica |
| `NOT_REPRESENTABLE` | Semântica não coberta pelo contrato vigente | Campo/relação de origem comprovado, contrato confrontado e decisão de evolução |
| `CONVERSION_REJECTED` | Entrada tentou conversão e foi recusada | Recibo/erro real da conversão; não afirmar que houve aquisição adicional |
| `PRESERVED_NOT_PRESENTED` | Dado ainda está no pacote/read model e a vista não o exibe | Campo/entidade/ID demonstrável e lacuna de componente/navegação |
| `PAYLOAD_NOT_OBSERVED` | Metadados existem, mas conteúdo não foi lido/verificado | Estado do leitor, distinto de ausência na origem |
| `INVALID_OR_UNAVAILABLE` | Leitor recusou ou não pôde acessar a fonte | Relatório de validação/acesso; nenhuma estimativa dos seus registros |

**CC-LOSS-01:** “perda” só é quantitativa quando duas medidas comparáveis e o mapa correspondente foram observados. Se a cadeia for desconhecida, registrar lacuna, não diferença calculada. Nunca inferir perdas históricas do número baixo de runs.

**CC-LOSS-02:** uma referência externa não resolvida, uma tabela sem preview e uma fonte inválida são problemas diferentes. Metadados preservados sem apresentação não viram conteúdo inexistente. Ausência de arquivo no pacote não prova que o produtor nunca o criou. E009/E010/E016.

**CC-LOSS-03:** `NOT_REPRESENTABLE` não pode ser atribuído apenas porque `runs` não contém o dado. Conferir `entities`, `artifacts`, relações e a preservação do payload antes de classificar. Sem os estudos A/B/C/D e sem fonte histórica autorizada observada, não há afirmação de paridade integral nem de perda integral do legado.

## 6. Tempo e consistência do snapshot

**CC-TIME-01:** toda medida é vinculada à observação que a sustenta. `indexed_at` é o instante do índice; `observed_at` é o instante da consulta/verificação do catálogo; `datePublished` é publicação do pacote; criação de arquivo e evento são dimensões separadas. Uma medição posterior não autentica retrospectivamente a data declarada do evento.

O catálogo marca `CHANGED` ao detectar diferença e continua exibindo o snapshot anterior até `rebuild()`. Portanto o relatório de cobertura mantém as contagens daquela geração e informa a mudança; não combina contagens antigas com payloads recém-observados como se fossem uma só fotografia consistente. [Comportamento fixado](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/catalog.py#L99-L138), E012.

**CC-TIME-02:** comparações longitudinais preservam revisões/snapshots, datas de observação e critério de seleção. Não misturar seleção de ontem e universo de hoje para calcular retenção sem uma regra demonstrada. Datas sem precisão suficiente permanecem assim; não acrescentar fuso ou horário fictício.

## 7. Contrato vigente, C0 delegado e evolução

| Faixa | Entrega admissível | Limite |
|---|---|---|
| `VIGENTE` | Contar fontes declaradas/válidas/inválidas separadamente, runs/artefatos/entidades do read model e resultados de filtro | Contagens descrevem o snapshot aceito e a vista; não totalizam o acervo |
| `C0_CANDIDATE` | Rotular escopo e denominador; exibir desconhecidos/perdas; consumir um resumo derivado autorizado como informação adicional | Relatório opcional, reconstruível; sua ausência não invalida Caderno válido nem exige nova fonte |
| `EVOLUTION_REQUIRED` | Tornar sidecar obrigatório, normalizar metadados persistidos de cobertura, alterar perfil ou obrigar identidade global | Proposta versionada e decisão própria; ADR sucessora quando houver desvio ARC-09; fora de P01/C0 vigente |

O sidecar não ganha autoridade científica por acompanhar um pacote, conter SHA-256 ou passar no validador. O viewer não varre o acervo para preencher campos. Não copiar IDs, paths ou recibos privados para este repositório. Resumos locais de P04/P05 só são reaproveitados após recebimento autorizado, com escopo e proveniência observáveis.

## 8. Critérios de aceite e handoff

1. **P02 — escopo dos números:** separar fontes declaradas, válidas, inválidas/inacessíveis e alteradas; rotular runs carregadas e runs visíveis; não inferir total do acervo. A timeline atual tem escopo de todas as runs e deve ser rotulada ou sincronizada mediante teste.
2. **P03 — componentes:** mostrar `UNKNOWN`/null com motivo, unidades e denominadores; uma ausência não vira zero; a legibilidade do escopo permanece em layout estreito.
3. **P04 — observações de coorte:** quando autorizado em sua frente, fornecer contagens por camada, seleção e limites como resumo sanitizado; lacunas desconhecidas continuam desconhecidas. P01 não declara essa execução realizada.
4. **P05 — prova operacional:** verificar no navegador os mesmos conjuntos do recibo, sem contar HTTP 200 como paridade visual nem publicar screenshots privados.
5. **P06 — QA/convergência:** confrontar fonte→projeção→seleção→conversão→pacote→read model→interface usando somente objetos recebidos; recusar unidades/escopos incompatíveis, overlap e observações de revisões distintas. Não somar reruns/OS/modos como casos únicos.

O pacote de exemplos deve incluir casos positivos com denominador conhecido e desconhecido, além de negativas para null convertido em zero, falta de motivo, razão incompatível, contagem negativa/fracionária, `n > d` em subconjunto e sidecar declarado obrigatório. O resultado desses exemplos mede apenas a consistência do contrato candidato; não certifica cobertura real, dados privados, navegador ou execução das outras frentes.
