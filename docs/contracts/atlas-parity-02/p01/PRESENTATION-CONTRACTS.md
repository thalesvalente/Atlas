# P01 — Contratos candidatos de apresentação e fidelidade

**Missão:** ATLAS-PARITY-02-P01. **Estado:** CANDIDATE; documentação para implementação compatível e classificação de evolução futura. **Baseline:** `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, árvore `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`. **Autoria semântica:** agente nativo `/root/semantics`; a revisão independente não é atribuída a este autor.

Este documento não altera o perfil Caderno 0.1.0a1, sua serialização, SDK, schemas ou ADR. As obrigações de apresentação abaixo são candidatas desta frente; não são normas aprovadas por outra frente. C0 pode usar o contrato vigente enquanto propostas de evolução são avaliadas. Os estudos A/B/C/D integrais não estavam disponíveis; nenhuma exigência denominada C-UX ou reconstrução das alegadas 12 jornadas é derivada de seu resumo.

## 1. Precedência e classes de decisão

A constituição ARC-01–09 separa interface, protocolo, produtores e armazenamento. O recibo posterior da [PR #5, comentário 6406839421](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421) aceita ADR-0002 v1.0 no HEAD `e985ea3124b7a3cd241ee2dbc88b5ad50688373c` **como direção de estabilização**. Textos históricos `PENDING_HUMAN` são preservados; não anulam esse recibo. O aceite não concede release estável, promoção canônica, ciência, migração ou extensão nova. Fontes E003–E006 do registro de evidências.

| Classe | Significado nesta entrega | Ação permitida aos owners |
|---|---|---|
| `VIGENTE` | Campo, relação ou comportamento sustentado pelo contrato e código fixados | Consumir sem reinterpretar nem alterar bytes do protocolo |
| `C0_CANDIDATE` | Decisão compatível de apresentação, em memória, sobre dados já expostos | Implementar no escopo próprio e demonstrar os critérios; não pressupor implementação ou aprovação alheia |
| `EVOLUTION_REQUIRED` | Nova garantia persistida, vocabulário obrigatório, inferência sem fonte ou semântica ausente | Registrar proposta versionada; requer decisão própria e, se houver desvio arquitetural, ADR sucessora conforme ARC-09 antes de implementar |

`VIGENTE` descreve a versão efetivamente consumida, não uma declaração de estabilidade científica. O [contrato 003](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/contracts/reader.md) mantém aquisição no produtor, conversão explícita e leitura exclusiva do Caderno. P01 não transfere ao viewer a interpretação de um carrier privado. E009.

Na gramática restrita dos worksheets, as três classes correspondem, respectivamente, a `CURRENT_CONTRACT`, `COMPATIBLE_PRESENTATION_CANDIDATE` e `PERSISTED_EVOLUTION_REQUIRED`. A [VALIDATION.md](VALIDATION.md) registra os campos exatos e o alcance de cada negativa; este texto define sua interpretação.

## 2. Mapa real do que já chega à interface

O [read model público](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/read_model.py#L40-L81) expõe `projects`, `experiments`, `runs`, `artifacts`, `relations` e uma cópia de **todas as entidades** em `entities`. `runs` seleciona apenas `CreateAction`; `artifacts` seleciona `File`. Assim, ausência de uma tela própria de documento não prova perda no pacote nem no grafo derivado. E010.

| Conceito | Apoio vigente | Limite que a apresentação deve tornar visível |
|---|---|---|
| Fonte | Catálogo com ID, relatório, digest, status e read model | Apenas fontes explicitamente declaradas; não é inventário do acervo |
| Execução | `CreateAction` → `runs`; estados, tempos, parâmetros, métricas e vínculos | Representa uma atividade declarada, não a mera presença de um arquivo |
| Documento/produto | Entidade pública em `entities`; `File` também em `artifacts` | Tipo documental especializado ou papel de produto pode não estar declarado; payload não é conteúdo textual entregue à UI |
| Referência | `mentions` → `related_references`, com nome/ID, tipos, descrição e observação | Não declara entrada, saída, derivação ou comprovação científica |
| Tabela de propriedades | `PropertyValue` → métricas/parâmetros, com tipo, unidade, precisão e ausência | Não define um modelo geral de planilha, linhas/colunas ou tabelas de documentos |
| Relação | `object`, `result`, `prov:wasDerivedFrom` → relações tipadas | Relações de outro vocabulário conservadas em `entities` não ganham significado novo |
| Marco documental | Pode haver documento e data declarada preservados em `entities` | Não há contrato vigente de evento documental tipado nem permissão para fabricar `CreateAction` |

A UI já implementa busca textual, filtros por projeto/experimento/estado, comparação, timeline, linhagem e referências relacionadas. A evolução deve tratar lacunas de alcance e fidelidade, não declarar essas capacidades inexistentes. [Implementação pública](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/static/app.js#L23-L109), E013.

## 3. Identidade e escopo de fonte

### PC-ID-01 — identidade contextual (`VIGENTE`)

A chave de consulta é **fonte/pacote + ID declarado**. Dentro do pacote, `@id` duplicado ou referência estrutural inexistente é erro de validação. Entre fontes, IDs iguais permanecem entidades distintas; não há merge por nome, digest ou ID isolado. O nome é rótulo; sua ausência permite o ID como fallback. A UI usa `JSON.stringify([source, id])`, não concatenação ambígua. E011–E013.

### PC-ID-02 — validade dos links (`C0_CANDIDATE`)

O [catálogo atual](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/catalog.py#L62-L71) atribui `source-1`, `source-2`, etc. pela ordem dos argumentos. Esses IDs valem para aquele catálogo. Uma reordenação em outra inicialização pode atribuir `source-1` a outro pacote. `generation` incrementa na instância e não é identificador global. O digest dos metadados identifica bytes observados, não o nome estável da fonte nem a autoria. E012.

Até P02 propor e testar outra solução, qualquer nova navegação C0 conserva o contexto do catálogo corrente e não promete bookmarks estáveis após reordenação/reabertura. Uma preferência antiga não pode resolver silenciosamente para outra fonte: precisa ser invalidada ou vinculada a evidência suficiente do mesmo contexto. A correspondência entre dois catálogos é **não estabelecida** quando só há IDs ordinais. Inventar `package_id` estável ou usar digest como identidade científica seria `EVOLUTION_REQUIRED`.

**Aceite:** dois pacotes com o mesmo `@id` e títulos distintos abrem seus próprios detalhes; depois da reordenação não se declara continuidade do link por igualdade de `source-N`. O teste documenta o âmbito em que a identidade foi preservada. Owner P02; revisão P06.

## 4. Execução, marco, produto e documento

### PC-KIND-01 — não fabricar atividade (`VIGENTE` + `C0_CANDIDATE`)

Uma execução resulta de `CreateAction` validada, com experimento, agente, instrumento, estado de execução, revisão, síntese e origem temporal próprios. Documento, produto e tabela não recebem `CreateAction`, status `COMPLETED` ou experimento artificial para caber no catálogo de runs. [Validação de atividades](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/model.py#L316-L360), E011.

C0 pode apresentar um navegador de entidades já expostas, conservando tipos declarados e seus nomes. `File` pode ser mostrado como **arquivo/artefato**; só o rótulo “documento” ou “produto” necessita suporte explícito na entidade ou mapeamento de apresentação rastreável, nunca apenas extensão de arquivo, nome do projeto ou expectativa do domínio. Sem esse suporte, usar entidade/arquivo e informar papel desconhecido. Um produto pode ter vários documentos, e um documento pode ser resultado de uma execução; essas relações precisam ser declaradas separadamente.

### PC-KIND-02 — marco documental (`C0_CANDIDATE` / `EVOLUTION_REQUIRED`)

Uma data de publicação de snapshot ou data de criação declarada em documento pode ser exibida com **seu papel literal**. C0 não a transforma em início/fim experimental ou em “aprovação”. Uma coleção visual de observações documentais, se proposta, deve conservar esse rótulo e separar sua legenda das execuções. Definir tipos persistidos de evento, cadeia de revisões, autoria autenticada ou causalidade documental exige evolução explícita; não é inferida de datas ou da ordenação de arquivos.

**Aceite:** um pacote válido com documento não ligado a run permite inspecionar seus metadados por `entities` sem aumentar a contagem de execuções. Um documento sem papel especializado permanece genérico. Owner P03 para componente; P02 para integração; P06 para prova.

## 5. Referências e relações

### PC-REL-01 — preservar predicado e orientação (`VIGENTE`)

| Declaração na fonte pública | Projeção legítima | O que não pode ser concluído |
|---|---|---|
| `run.mentions → entidade` | Referência relacionada neutra; primeira ocorrência preservada | Uso como input, produção, derivação, causalidade ou aceite |
| `run.object → entidade` | Entidade → execução, relação `input` | Que o consumidor reproduziu a execução ou verificou o conteúdo |
| `run.result → entidade` | Execução → entidade, relação `output` | Validade científica do resultado |
| `entidade.prov:wasDerivedFrom → anterior` | Entidade → anterior, relação `derived_from` | Método causal comprovado, reprodução ou aprovação |
| Relação não interpretada em `entities` | Predicado literal com origem explícita | Conversão automática para uma das relações acima |

O [mapeamento real](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/read_model.py#L27-L74) mantém menções fora da lista de relações de linhagem. Um alvo pode ser simultaneamente mencionado e ter vínculo de input/output explicitamente declarado; não se apaga um papel por causa do outro. A deduplicação da seção de menções preserva a primeira ordem e não deduplica relações diferentes. E009–E010.

No worksheet, `source` e `target` designam sujeito e objeto da declaração original. Para `object`, portanto, o sujeito é a execução e o alvo é a entrada; a orientação visual legítima é alvo → execução. O validador não pode tratar essa inversão apenas visual como inversão da alegação de origem. A semântica do predicado e a chave fonte/ID de ambas as pontas permanecem explícitas.

### PC-REF-01 — metadados e payload não se confundem (`VIGENTE`)

Exibir separadamente digest declarado, digest calculado, disponibilidade declarada e resultado observado. `MISSING` significa ausente **no pacote observado**; `EXTERNAL_UNRESOLVED` significa não acessado; `UNVERIFIED` não significa inválido ou inexistente. Uma URI e texto HTML são dados inertes. Navegação interna mantém fonte/ID; ausência de alvo não autoriza procurar outro pacote, rede ou path privado. Fonte inválida continua sem read model. E009, E012–E013.

**Aceite:** converter uma menção em `input`, inverter uma relação ou resolver alvo em outra fonte deve falhar na validação do exemplo/ensaio correspondente. O caso positivo de menção permanece neutro e não acrescenta aresta experimental. Owner P03/P02; QA P06.

## 6. Tempo, precisão e observação

### PC-TIME-01 — conservar o papel de cada data (`VIGENTE` + `C0_CANDIDATE`)

| Papel temporal | Fonte real disponível | Rótulo e tratamento |
|---|---|---|
| Evento de execução | `startTime`, `endTime`, `cp:timestampOrigin` | Início/fim declarados; ausência explícita; nunca hora de conversão |
| Publicação do snapshot | Root `datePublished` → `source.date_published` | Publicação deste snapshot; pode ter precisão de data; não é evento científico |
| Criação do arquivo/documento | Somente se declarada em campo preservado e compreendido | Criação declarada; não obter de `mtime` nem substituir pelo tempo observado |
| Indexação | `catalog.indexed_at`, `generation` | Quando o índice foi reconstruído |
| Observação do catálogo | `catalog.observed_at`, `changed` | Quando o estado foi observado; mudança não atualiza silenciosamente o snapshot exibido |
| Geração de dossiê | `generated_at` | Geração de uma apresentação derivada |

`startTime`/`endTime` conhecidos exigem timezone no perfil; não inserir horário, fuso ou segundos ausentes. A precisão lexical observada não é uma precisão científica declarada. Conservar o literal e, quando explicitamente fornecida, sua precisão; desconhecimento é `UNKNOWN`/null com motivo no documento derivado. Não transformar uma data diária em meia-noite para ordenar eventos. [Perfil, seção 4](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/protocol/0.1.0a1.md#L119-L147), E016.

A timeline vigente usa todas as runs carregadas, ordenadas por início; as runs sem início permanecem sem data. Os filtros de Explorar não são aplicados a ela. C0 deve explicitar esse alcance ou implementar sincronização testada. A ordem visual não prova causalidade. [UI, linhas 42 e 94](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/static/app.js#L42-L94), E013.

**Aceite:** evento desconhecido + publicação conhecida + observação conhecida produz três papéis distintos; o evento permanece desconhecido. Se `CHANGED`, contagens e detalhes continuam vinculados ao `indexed_at` anterior até reconstrução. Owner P02/P03; QA P06.

## 7. Tabelas, valores e comparação

### PC-TABLE-01 — não perder tipo ou ausência (`VIGENTE`)

Métricas/parâmetros usam `PropertyValue`, `propertyID`, tipo `integer`/`number`/`string`/`boolean`, unidade numérica explícita, precisão declarada opcional e motivo de ausência. Booleano não é inteiro; valor ausente não é zero; unidade desconhecida não é adimensional. A ordem declarada das listas deve sobreviver. O catálogo acrescenta `display_value` textual para preservar inteiros além de 2^53 no navegador; esse texto não substitui o valor tipado no servidor. [Perfil](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/protocol/0.1.0a1.md#L119-L141), [projeção](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/catalog.py#L39-L50), E012/E016.

### PC-TABLE-02 — tabelas gerais (`C0_CANDIDATE` / `EVOLUTION_REQUIRED`)

O contrato atual preserva arquivos tabelares como `File`, mas não entrega payloads como linhas/colunas tipadas no read model. C0 já pode mostrar metadados, disponibilidade e referências de uma tabela. Uma visualização literal adicional depende de acesso explicitamente permitido e de uma implementação separada do contrato vigente; este documento não autoriza novo endpoint, leitura privada ou parser do produtor.

Para um componente derivado de tabela, exigir lista ordenada de colunas, identificadores estáveis **dentro da tabela**, tipo declarado, unidade/precisão quando conhecidas, linhas ordenadas e cells com valores e ausências conservados. Strings `"001"`, `"false"` e `"1.00"` não viram número/booleano por conveniência. Se a representação lexical exata importa, preservar também o literal (`raw`) com origem; não reconstruir zeros finais pelo número binário. Null precisa de motivo; tipo ou unidade sem declaração permanece desconhecido e desabilita comparação quantitativa. Não atribuir chaves de coluna ou unicidade de linha à origem quando forem índices derivados.

Um formato interoperável obrigatório de tabelas, unidades convertíveis, revisão documental ou precisão temporal é `EVOLUTION_REQUIRED`. Os exemplos sintéticos de P01 são worksheets de obrigações; não são novo schema Caderno nem API que o produto já consome.

### PC-COMP-01 — compatibilidade explícita (`VIGENTE` + `C0_CANDIDATE`)

A UI atual agrupa métricas por `property_id || name`, tipo e unidade, limita seleção a quatro execuções e separa unidades/tipos incompatíveis. Não calcula diferenças nem converte unidades. Esse agrupamento não prova equivalência semântica entre produtores, especialmente quando o identificador é local ou há fallback por nome. [Comparação](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/atlas/src/atlas_viewer/static/app.js#L91-L92), E013.

Para comparações quantitativas futuras, exigir mesma identidade semântica demonstrada, tipo numérico compatível, unidade literal igual (ou conversão explicitamente especificada e testada), ausência resolvida e escopo conhecido. C0 pode manter apresentação lado a lado com escopos e avisos; não rotular nomes semelhantes como a mesma medida. Preservar múltiplos valores em vez de escolher silenciosamente um. Revisão `ACCEPTED` declarada pelo produtor não é aprovação da comparação.

**Aceite:** ensaios com inteiro grande, booleano, string com zero inicial, valor ausente, precisão declarada, linhas/colunas ordenadas e unidades diferentes preservam valores e recusam comparação indevida. Owner P03 para componentes; P02 para fonte/modelo permitido; P06 para QA.

## 8. Entrega entre owners e limites de validação

P02 integra navegação contextual, escopo dos contadores/filtros e linguagem de estado; P03 implementa componentes isolados sobre dados públicos existentes; P04 fornece somente resumos autorizados de observações locais; P05 verifica percurso em navegador no próprio escopo; P06 agrega e revisa. P01 entrega contratos e exemplos, sem executar essas implementações.

Os worksheets JSON deste diretório são exemplos sintéticos derivados, nos kinds `ATLAS_P01_PRESENTATION_EXAMPLE`, `ATLAS_P01_TABLE_EXAMPLE` e `ATLAS_P01_COVERAGE_EXAMPLE`; o validador acompanha o pacote documental. Uma fixture Caderno separada exercita o leitor vigente e não deve ser confundida com esses envelopes. Um worksheet negativo esperado não é um pacote científico inválido executado no host; sua rejeição demonstra somente a obrigação correspondente do worksheet. Conformidade documental não substitui teste do SDK, teste do navegador, paridade com acervo real nem aprovação humana. Ver [COVERAGE-CONTRACT.md](COVERAGE-CONTRACT.md), [VALIDATION.md](VALIDATION.md) e o registro de evidências da missão para o alcance e a atribuição exata dos ensaios.
