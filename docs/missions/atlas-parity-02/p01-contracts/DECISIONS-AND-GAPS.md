# P01 — decisões, gaps e handoff para os owners

**Estado:** candidata documental de ATLAS-PARITY-02-P01, 2026-10-27.
**Base fixada:** `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`.

## Decisões já existentes

| Decisão | Evidência | Consequência |
|---|---|---|
| Atlas é interface independente; produtores publicam Caderno | E003/E004, ARC-01–09 | nenhum import de produtor, carrier privado ou executor no viewer |
| ADR-0002 v1.0 aceita como direção de estabilização | E006, PR #5 / 6406839421, HEAD e985ea3124b7a3cd241ee2dbc88b5ad50688373c | não solicitar o mesmo aceite; preservar bytes históricos |
| Caderno vigente é o único formato de entrada | E009/E016 | worksheets/sidecar de P01 não criam novo formato obrigatório |
| Menções são referências neutras | E009/E010/E015 | manter seção separada de entrada/saída/derivação |
| Identidade corrente é fonte/pacote + ID | E010/E012/E013 | IDs colidentes entre fontes não se mesclam |
| Merge, release, ciência, promoção e operação física são gates distintos | E003–E006 e missão | encerramento P01 não os concede |

O texto de `catalog.py` em LIMITATIONS ainda diz que o aceite da direção está pendente.
O recibo posterior resolve a decisão histórica; resta alinhar a linguagem atual da UI
sem declarar release estável. P01 registra o gap, não altera produto ou ADR.

## Decisões compatíveis candidatas desta frente

Navegar entidades preservadas em `entities`, expor tipos literais e escopo do catálogo;
rotular os contadores como registros carregados/visíveis; diferenciar indexação de
observação; informar o escopo da timeline e da comparação; preservar precisão e
desconhecidos. São propostas de apresentação sob ARC-01–08, implementáveis pelo owner
sem novo protocolo quando usam os dados já expostos. Este pacote não declara que outra
frente aceitou ou implementou essas propostas.

## Novas decisões realmente necessárias

| ID | Questão | Disposição e próximo ato mínimo |
|---|---|---|
| P01-F01 | Semântica interoperável de grade tabular e marcos/revisões documentais | classificar requisitos comprovados e propor desenho versionado; não tornar obrigatórios campos de worksheet; decisão própria e ADR quando houver desvio ARC-09 |
| P01-F02 | Identidade durável entre publicações/catálogos | avaliar solução explícita e testes de reorder/duplicação; uma solução derivada local não implica mudar protocolo; garantia persistida nova exige decisão própria |
| G01 | Texto integral de A/B/C/D indisponível | INPUT_MISSING; receber bytes e confirmar hashes antes de incorporar conclusões específicas |
| G02 | Fonte/projeção/seleção/conversão do legado não observadas nesta frente | UNKNOWN_UPSTREAM; aceitar somente recibo sanitizado autorizado de P04/P05 quando efetivamente recebido |
| G03 | Alcance genérico de tabela não contratado | metadados File representáveis; não afirmar leitura de linhas ou precisão lexical perdida no produtor |
| G04 | Paridade visual/operacional ainda não verificada nesta frente | P05/P06 executarão seus próprios ensaios; HTTP 200 e documento não substituem navegador |

P01-F01/F02 são propostas classificadas, não pedidos de ratificação genérica. C0 pode
avançar com o contrato vigente enquanto forem analisadas. G01 não bloqueia a onda.

## Handoff de tarefas propostas — sem execução atribuída

Estado de todas as linhas: `HANDOFF_PROPOSED`. Cada owner verifica sua autorização e
seus paths exclusivos. Estas tarefas não concedem a P01 escrita em outro workstream.

| ID | Owner | Incremento concreto | Critério de aceite | Dependência |
|---|---|---|---|---|
| P02-01 | P02 | escopo fonte/ID e proteção contra remapeamento de preferência/link após reorder | dois pacotes com mesmo ID ficam distintos; reorder não abre fonte errada silenciosamente; solução/limites testados | PC-ID-01/02 |
| P02-02 | P02 | expor/rotular contagens e tempos de catálogo com escopo | fonte válida/inválida/alterada separadas; indexed_at ≠ observed_at; nenhum total de acervo derivado de runs | CC-DEN/CC-TIME |
| P02-03 | P02 | alinhar texto de aceite ADR-0002 ao recibo posterior | direção aceita, estabilidade/promoção/ciência continuam separadas; bytes históricos preservados | E006 |
| P03-01 | P03 | componente isolado de detalhe de entidade pública | documento/produto acessível por contexto/ID sem CreateAction fabricada, sem leitura de payload privado | PC-KIND/PC-REF |
| P03-02 | P03 | explicitar/ampliar alcance de busca e filtros sobre dados já fornecidos | manter comportamento existente; campos e conjunto elegível visíveis; testes de filtro por fonte | matriz P01-Jxx |
| P03-03 | P03 | apresentar eventos e observações com escopo temporal | eventos desconhecidos permanecem desconhecidos; timeline explicita conjunto ou sincroniza com filtro mediante teste | PC-TIME |
| P03-04 | P03 | fidelidade de valores e avisos de comparação | preservar tipo/unidade/precisão/ausência; sem equivalência entre produtores por nome; sem conversão implícita | PC-TABLE/PC-COMP |
| P03-05 | P03 | painel de cobertura compatível e opcional | denominadores/UNKNOWN/escopo legíveis; ausência de sidecar não invalida pacote | COVERAGE-CONTRACT |
| P04-01 | P04 | produzir recibos locais de coorte/seleção/perdas dentro de sua autorização | contagens por camada com unidade, observação e limites; resumo público sem IDs/paths/conteúdo privados | evidência efetivamente obtida por P04 |
| P05-01 | P05 | verificar percurso no navegador local autorizado | navegar fontes/entidades/referências, conferir contagens e UNKNOWN; capturas privadas permanecem privadas | objetos de produto recebidos |
| P06-01 | P06 | agregar contratos/testes e verificar fronteiras no SHA integrado | teste de bytes recebidos, ownership/protocolo imutável, denominadores/reorder/menções cobertos; CI atribuída ao SHA correto | candidatas recebidas, sem espera/polling por P01 |

P02/P03 podem coordenar composição shell/componente respeitando suas raízes. Uma
implementação que necessite mudar `packages/protocol/**` não é autorizada por P01;
deve ser reclassificada e encaminhada antes de executar.

## Decisão de encerramento documental

O pacote pode ser `P01_CONTRACT_PACKET_READY` e simultaneamente
`P01_PARTIAL_INPUTS_EXPLICIT`: está pronto para os itens compatíveis sustentados por
evidência, com A/B/C/D integrais ausentes e evolução persistida separada. Não equivale
a recuperação integral do legado, implementação C0, promoção ou aprovação humana.
