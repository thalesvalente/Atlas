# Identidade, ausência e perdas — proposta 0.2.0

Missão: AP04-F2-CHAT-LEGACY-COMPAT-CONTRACT-01.
Proposta de B (/root/model_b), integrada pelo coordenador.
Estado: RECOMMENDED_PROPOSED / ARC09_APPROVAL_REQUIRED.
Aplica-se ao descriptor atlas-legacy-presentation 0.2.0; não altera contratos vigentes.

## Identidade e contexto

Uma identidade nativa exige evidência literal de origem. A chave contextual é (source_id, snapshot_id, native_id). Source IDs e snapshot IDs são técnicos e não autenticam a fonte. Mesmo texto em fontes ou snapshots distintos permanece separado.

Navigation IDs são sempre DERIVED_FOR_PRESENTATION. Sua chave operacional inclui sessão/importação da UI, fonte, snapshot e ocorrência. São temporários, não publicáveis como identidade científica e nunca promovidos a native ID. Índice ordinal, caminho, filename, título, digest ou texto igual não justificam identidade nativa.

Quando não há ID nativo, native_id=null. A ocorrência continua navegável por navigation ID, locator e ordinal. ID vazio ou inválido permanece como dado literal em célula ou unmapped_fields; não vira ID qualificado válido.

Dois objetos com o mesmo native ID no mesmo contexto continuam duas ocorrências. Marcar COLLISION, conservar localizadores e bloquear resolução automática. Não escolher o primeiro, último, mais recente ou mais completo. Endpoint nulo permanece NULL_ENDPOINT; ID declarado sem alvo único permanece UNRESOLVED/COLLISION.

## Run externo e árvore

Um Run original observado no grafo conserva SOURCE_ENTITY e seu tipo/ID efetivamente comprovados, mesmo quando isolado e externamente vinculado à RF. Sua existência não fecha binding_gap nem prova um caminho contínuo. Não substituir esse Run por stub.

Somente quando um vínculo se refere a execução NÃO carregada, a UI pode representar a referência como stub DECLARED_EXTERNAL_REFERENCE, native ID null e RUN_EXTERNAL_ISOLATED. O ID externo literal fica em declared_id. EXTERNAL_DECLARED não equivale a entidade carregada ou referência resolvida; binding_gap=true permanece. O exemplo A é sintético e ilustra essa situação; não reclassifica o Run observado em F1.

Não criar Project, Experiment, parent link, aresta de linhagem ou caminho contínuo para ligar uma execução à árvore. Família, parent_key e tipo vêm de campos explícitos com prova. Sem tipo comprovado, usar Unknown. Pertencimento organizacional, derivação causal e menção neutra continuam distintos na UI, filtros e exportação.

Órfãos permanecem no inventário e na contagem. Uma seção visual «órfãos» ou «referências externas» é agrupamento de apresentação, não novo pai, projeto ou identidade nativa.

## RF/RNF/RES e admissão

RF/RNF/RES são extensões opcionais de domínio. Classificação exige declaração e conteúdo demonstrado; rótulos, paths, extensões, MIME ou correspondências textuais não criam requisitos.

As 28 linhas F1 UNADMITTED_NATIVE_RF têm native_id=null e devem continuar assim. Navigation IDs e preenchimento de campos não as admitem. Uma evidência futura que mude a admissão exige nova observação/snapshot com proveniência; não reescrever silenciosamente o anterior.

Uma RF nativa reconhecida não é ciência aprovada. Conteúdo, estado técnico, validação de descriptor, integridade, origem declarada, autenticidade e revisão científica continuam eixos distintos.

F1 teve UMA RF literalmente comparada, com ID, núcleo/módulo, título, descrição e critérios. Não atribuir comparação individual às demais 151 linhas. Categoria originalmente ausente permanece MISSING, sem classificação por título ou módulo.

A disponibilidade de RNF/RES continua desconhecida. Não apresentar zero como inexistência comprovada nem criar exemplos como se viessem da F1.

## Conservação de valores e ordem

Cada tabela mantém ordem original de colunas e linhas, headers literais e chaves originais. Ordenação ou filtro são visões derivadas; devem permitir retorno à ordem original e informar população carregada, filtrada e visível.

Cada valor conserva tipo, texto literal, lexema original, precisão declarada, unidade e ausência. Strings numéricas continuam strings; booleanos não são números. Inteiros e decimais em texto tipado evitam perda no browser. Não aumentar precisão, converter unidades, arredondar ou preencher ausência com zero.

Null, propriedade ausente, string vazia e zero são distintos. Categoria MISSING não se torna «geral» ou classificação inferida. Um rótulo visual de ausência permanece rótulo de UI, não valor científico.

Campos selecionados fora da UI são conservados em unmapped_fields. Valor impossível, quota excedida ou campo excluído não pode ser descartado silenciosamente: produzir erro ou perda explícita com escopo e motivo antes da apresentação. Excesso de quota recusa a importação e não emite subconjunto como completo. A fonte continua recuperável sem UI; o descriptor não promete conservar o acervo inteiro.

A exportação canônica futura é JSON tipado com ordem e literais preservados. CSV seguro exige quoting, escaping e neutralização de fórmulas. Toda transformação é declarada e não substitui a versão canônica fiel. HTML e JavaScript permanecem texto inerte.

## Relações e ocorrências repetidas

Uma relação preserva tipo literal, direção declarada, endpoints, localizador de prova e semântica. Ausência de direção permanece UNKNOWN ou UNDIRECTED; não vira entrada/saída experimental. Relação sem prova não recebe causalidade.

Duplicatas conservam ocorrências. repeat_group é um agrupamento derivado; repeat_occurrence distingue suas ocorrências, sem criar identidade nativa. Contagens de grupos e ocorrências excedentes são separadas.

Os negativos F1 são declarações sanitizadas no payload qualificante: 22 endpoints nulos, 75 relações declaradas não resolvidas, 50 colisões declaradas, 40 grupos de triplas repetidas e 41 ocorrências excedentes. Essas categorias podem se sobrepor; NÃO somá-las como partição das 1595 arestas. Colisões não são entidades únicas globais; relações pendentes não são arquivos inacessíveis.

Quatro das cinco tabelas não possuem record_id resolúvel no conjunto de records. Permanecem tabelas consultáveis com vínculo não resolvido, sem criar record pelo título ou ordinal. A tabela com vínculo resolúvel não fecha a lacuna externa da execução amostrada.

## Produtos, documentos e evidência

File permanece File, mesmo quando tem papel de produto declarado. Um produto exige papel e vínculo explícitos; MIME, extensão ou presença na lista de recursos não bastam. Recurso referenciado não é automaticamente documento disponível, produto validado ou evidência aceita.

URI, path e digest declarado não autorizam acesso. O descriptor conserva URI como texto; não abre arquivos, monta volumes, segue redirecionamentos, baixa recursos ou executa HTML. Disponibilidade declarada, observada, externa não resolvida e integridade comparada são estados separados.

Recursos, grupos e dossiês não se convertem uns nos outros para atender uma tela. Ausências continuam no inventário com estado e contagem.

## Inventário de conservação e perdas

| Aspecto | Conservar | Proibição / perda explícita |
|---|---|---|
| Fonte/snapshot | Contexto, seleção, observação, política, bytes observados | Source ID não autentica; tempo técnico não substitui científico |
| Identidade | ID comprovado, null, ocorrências, locator | Não fabricar native ID nem fundir fontes |
| Árvore | Tipos, família, parent keys, órfãos; Run original e stub distintos | Não completar árvore ou causalidade |
| Tabelas | Headers, chaves, ordem, células, tipos, precisão, unidade, ausência | Não normalizar silenciosamente nem esconder tabela vazia |
| RF | Literal, campos e admissão | Não admitir 28 linhas sem ID nem generalizar uma comparação |
| RNF/RES | Disponibilidade desconhecida até prova | Não inferir por rótulo, MIME ou nome |
| Relações | Direção, prova, null/unresolved/collision, ocorrências | Não escolher alvo ambíguo nem deduplicar |
| Produtos/Files | Tipo original, papel, vínculo, disponibilidade | Não promover recurso/digest a produto ou aceite |
| Campos fora da UI | Chave, localizador e valor em unmapped_fields | Exclusão precisa de gap ou recusa |
| Cobertura | População, unidade, selecionado/carregado/visível | Não extrapolar, somar snapshots sobrepostos ou calcular 0/0 |
| Segurança | Allowlist, limites, observação e expiração | Não abrir URIs nem transformar cache em acervo |
| Padrões | Declaração original e validação realizada | Não declarar Caderno/RO-Crate/FHIR conforme por rótulo |

## Contagens F1 delimitadas

O handoff a237f446e54927eeeda8ed5e8e9daa83ee09dcb7 informa três arquivos considerados, selecionados e lidos, dois payloads JSON inertes e um payload qualificante com:

- 159 records.
- Cinco result_tables com 39, 85, 28, 0 e 0 linhas: 152 observadas.
- Uma linha RF literalmente comparada.
- 2911 nós, 1595 arestas e 858 parent keys explícitos resolvidos.
- 162 product_items, dez product_groups e 80 resource_documents.
- 24 dossier_assessments e quatro dossier_packages.
- 28 linhas não admitidas, quatro tabelas sem record_id resolúvel e os negativos acima.

As contagens não são soma dos três arquivos. Snapshots possivelmente sobrepostos não foram somados. Brutos upstream não foram abertos e hashes históricos upstream não foram revalidados.

UNKNOWN_UPSTREAM e GLOBAL_UNPROVEN permanecem. Não existe denominador global comprovado, recall/exaustividade medidos ou percentual global válido. Tabela conhecida vazia não prova ausência upstream e não produz percentual 0/0.

A igualdade F1 antes/depois de SHA-256, tamanho e mtime nas três fontes, zero escrita e sete caminhos de prova preservados (seis arquivos iguais e um permaneceu ausente) é evidência anterior. Não é nova verificação F2 ou integridade global. G1 aprovou disponibilidade selecionada, não paridade da interface.

## Cache, seleção e privacidade

Arquivo externo em scratch privado próprio, fora do acervo e dos repositórios; browser somente em memória. TTL máximo de 60 minutos. Troca de importação, sessão/snapshot, expiração ou invalidação detectada encerra contexto e links legados.

Caderno continua com contexto independente. Não reutilizar links legados como links Caderno ou IDs nativos. Nova observação exige autorização; stale links não são remapeados por título ou ID textual.

A UI não monitora originais. Durante o TTL, OBSERVED_SNAPSHOT_ONLY; freshness atual é desconhecida até releitura externa. Encerramento normal pode remover somente cache próprio; crash pode deixar resíduo. Não prometer limpeza física ou adquirir poder de exclusão sobre fontes.

Nenhum literal, path, nome, URI, ID, digest privado, JSON/HTML ou screenshot F1 será publicado. Contagens e lacunas sanitizadas bastam; não solicitar recibos privados.

Os dois exemplos são inventados, com synthetic=true, datas de fixture e digest null quando NOT_COMPUTED. Não comprovam execução F1, produto, UI ou aprovação. Checagem documental posterior não altera seus estados de execução.

RO-Crate 1.3, Process Run 0.6 e Caderno 0.1.0a1 são preservados. HL7/FHIR permanece capacidade futura por domínio, sem versão/perfis/IG ou conformidade implementada.

## Revisão e gate

A revisão independente deve tentar refutar a diferença entre entrada nova e reader003 exclusivo; promoção de navigation ID, stub ou domínio a ciência; perda de precisão, ausência, ordem, campos ou ocorrências; generalização de contagens; perda de negativos F1/binding_gap; exfiltração e falsa promessa de cache removido; acoplamento SDK/Catalog ao R4 ou regressão C4.

Aprovação humana ARC-09 exige versão e SHA do pacote. Agente, CI, silêncio, publicação ou consentimento funcional anterior não aprovam. Nenhuma implementação é autorizada por este documento.
