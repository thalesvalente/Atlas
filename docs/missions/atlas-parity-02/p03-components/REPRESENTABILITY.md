# Representabilidade — ATLAS-PARITY-02-P03

**Base:** c2d00fb137cac1d62d6b7cb045ddbe055355a4c5.
**Tree:** 5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59.
**Natureza:** análise do contrato público atual e proposta de apresentação isolada.

## 1. Já representado pelo contrato

| Informação | Fonte primária na baseline | Alcance |
|---|---|---|
| Identidade, nome, descrição, tipo | perfil §3; read_model.entities | Contextualizar por fonte/pacote + @id. |
| Artefato File e formato | perfil §§3/5; read_model.artifacts | Não implica produto, documento rico ou aprovação. |
| Disponibilidade declarada | entities[].cp:availability; perfil §5 | Declaração separada da observação do leitor. |
| Disponibilidade observada | artifacts[].availability; SDK | Inclui desconhecido, externo, ausente e mismatch. |
| SHA-256 declarado/calculado | cp:sha256 e observação SDK | Integridade de bytes não autentica autoria/data. |
| Entrada/saída/derivação | object/result/prov:wasDerivedFrom | Relações declaradas e resolvidas; não execução reproduzida. |
| Menção | mentions/related_references | Referência neutra separada de produção. |
| Métrica/parâmetro | PropertyValue; perfil §4 | Tipo/unidade/precisão/ausência, sem tabela genérica. |

Fontes: [perfil](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/protocol/0.1.0a1.md),
[read model](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/packages/protocol/src/caderno_protocol/read_model.py).
Reter entities não concede significado novo a propriedades desconhecidas.

## 2. Apresentação derivada possível

Cartões/listas podem apresentar campos efetivamente declarados e observados sem abrir o
arquivo. Relações podem exibir direção e fonte. Uma lista tabular de métricas existentes é
possível com escolha explícita de linhas/colunas — decisão da apresentação, não schema genérico.

project_metadata projeta o read model. O renderer tabular recebe descritor candidato;
P03 não publica exportador/adaptador de tabela para o Caderno. Inteiros Python devem cruzar
a fronteira JS sem perda (ex.: string lexical no descritor de apresentação). Inteiros Number
fora da faixa segura são recusados. Perda decimal anterior à entrada não é detectável;
decimais exatos devem chegar como strings. Não há recuperação de bytes perdidos. Precisão não arredonda.

## 3. Exige contrato persistido ou decisão específica

| Capacidade | Definição que falta | Entrega P03 |
|---|---|---|
| Tabela genérica persistida | Schema, tipos/unidades, identidade, proveniência | Renderer candidato, fixtures explícitas. |
| Produto universal | Papel/entidade, versão, atividade, disponibilidade | Cartão sintético candidato; File não promovido. |
| Documento rico | Estrutura/seções, semântica e política de acesso | Seções de texto candidato; nenhum payload aberto. |
| Coverage ledger | Universo, critérios, vínculos e estados | Fora do runtime, sem inferência. |
| Paridade com legado | Estudos íntegros e corpus autorizado comparável | Não alegada nem medida. |

Adoção futura requer proposta versionada, revisão e gates aplicáveis de ARC-09. A API de
apresentação não constitui nova compatibilidade nativa do Caderno.

## Entradas e decisões

A/B/C/D integrais e contrato P01: **INPUT_MISSING** nesta execução.
C-study hash informado: f8d274ffe5ac043005b2c27779286638a86c7c2aff3e30ee64a4497b434b110b.
C-handoff hash informado: e8c7b1b3a8eb0a276d94e98f94b9d1477e555d305ebee62d99ec48ee93f5650e.
Ambos são UNVERIFIED_INPUT_HASH: bytes não recebidos, conteúdo não reconstruído.

[Merge da PR #5](https://github.com/thalesvalente/Atlas/commit/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5)
registra aceite ADR-0002 v1.0 como direção. Histórico preservado; isso não aprova extensão,
release, ciência, migração ou promoção.
