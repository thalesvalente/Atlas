# P01 — Contratos e fidelidade para paridade C0

**Missão:** ATLAS-PARITY-02-P01. **Data:** 2026-10-27, America/Fortaleza.
**Estado:** candidata documental; não é especificação agregadora aprovada da feature 004.
**Branch:** `work/atlas-parity02-p01-contracts-20261027`.
**Baseline:** `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`;
árvore `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`.

## Intenção e limite

Permitir que os owners de apresentação recuperem informação já representável no
Caderno sem inventar fatos, dependências de produtores ou nova autoridade. A entrega
é um pacote documental com evidências, matriz, contratos candidatos e exemplos
executáveis. Nenhum requisito desta spec autoriza P01 a alterar o produto.

## Histórias e cenários independentes

### US1 — Localizar informação e perdas (P1)

Uma pessoa implementadora distingue fonte não observada de informação preservada no
pacote mas ausente da tela. Dado o mesmo SHA, cada linha da matriz informa as sete
camadas, fonte verificável, suporte atual, perda, owner e aceite verificável. Um estudo
ausente aparece como `INPUT_MISSING`; seu resumo não vira estudo integral.

### US2 — Implementar apresentação fiel (P1)

Uma pessoa implementadora usa regras de identidade, entidade, relação e tempo sem
reescrever o Caderno. IDs iguais em fontes distintas não colidem; uma menção não é
input/output; um documento não vira execução; tempo desconhecido não ganha precisão.
As propostas que demandam evolução persistida ficam separadas do incremento C0.

### US3 — Conferir cobertura e rejeitar alegações falsas (P1)

Uma pessoa revisora reproduz exemplos positivos e negativos em ambiente offline.
Contadores declaram unidade, escopo, seleção, denominador e observação. Ausência não
vira zero; runs carregadas não medem o acervo. Tabelas preservam tipo, unidade, ordem,
precisão e motivos de ausência; comparação sem equivalência conhecida não é aprovada.

### US4 — Receber um handoff reproduzível (P1)

Uma pessoa integradora recebe paths exclusivos, entradas identificadas, evidência de
execução/revisão, SHA testado, commit documental e tarefas para os demais owners.
O fechamento documental não declara implementação, aceite científico ou promoção.

## Requisitos documentais

- **FR-P01-001:** fixar SHA/tree, fontes e precedência entre documentos históricos e recibo PR #5.
- **FR-P01-002:** inventariar A/B/C/D uma vez; distinguir bytes lidos, resumo, hash informado e entrada ausente.
- **FR-P01-003:** mapear fonte → projeção → seleção → conversão → pacote → read model → interface sem inventar resultados upstream.
- **FR-P01-004:** especificar identidade contextual e o limite ordinal atual, sem garantir estabilidade após reorder.
- **FR-P01-005:** separar execução, marco documental, produto, documento, tabela, referência e relação; preservar neutralidade de mentions.
- **FR-P01-006:** distinguir criação de arquivo, evento, publicação, indexação e observação, mantendo ausência/origem/precisão.
- **FR-P01-007:** contratar cobertura por população/unidade/escopo/seleção e declarar perdas e desconhecidos.
- **FR-P01-008:** preservar tabela tipada e condicionar comparação a compatibilidade demonstrada; não declarar grid genérico implementado.
- **FR-P01-009:** separar contrato vigente, candidata de apresentação compatível e proposta que exige evolução persistida/ADR.
- **FR-P01-010:** fornecer exemplos sintéticos mínimos positivos/negativos e validação determinística, incluindo consumo pelo SDK vigente.
- **FR-P01-011:** aplicar ciclo Spec Kit no workstream, registrar helpers reais e QA independente sem autoria.
- **FR-P01-012:** entregar RESULT, HANDOFF e MANIFEST, commits/PR Draft somente no Atlas, com privacidade e ownership comprovados.

## Critérios mensuráveis

- **SC-P01-01:** todas as linhas da matriz têm sete camadas, evidência, classificação, owner e aceite.
- **SC-P01-02:** exemplos aceitos e recusados têm resultados reproduzíveis e erro esperado, sem dependência de rede/modelo.
- **SC-P01-03:** documentos/produtos válidos permanecem entidades e não aparecem como runs na prova do leitor vigente.
- **SC-P01-04:** zero alteração de paths fora das três raízes P01; protocolo e ponteiro global preservados.
- **SC-P01-05:** revisão nativa sem autoria identifica bytes efetivamente revisados e fecha findings materiais, ou explicita bloqueio.
- **SC-P01-06:** handoff diferencia código baseline testado, payload documental validado e commit de publicação.

## Casos de borda e premissas

Estudos ausentes, mesmo ID em duas fontes, reorder, relação sem alvo, menção promovida,
documento tratado como ação, data sem fuso, precisão temporal inventada, bool contado
como inteiro, denominador de outro escopo, tabela reordenada ou de unidades divergentes.
Não se presume acesso ao host nem a conversas paralelas. Só fontes públicas e dados
sintéticos próprios entram no Git; esta spec não concede transferência de anexos privados.
