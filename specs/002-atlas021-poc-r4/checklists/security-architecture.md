# Checklist de requisitos: segurança, arquitetura e evidência da PoC

**Purpose:** avaliar clareza, completude e consistência dos requisitos do delta.
**Created:** 2026-10-24.
**Feature:** [PoC R4 → Caderno → Atlas](../spec.md).
**Review Ownership:** A4, revisor independente dos autores do comando/demo.
**Marker Semantics:** `[x]` significa qualidade do requisito revisada e satisfeita;
não significa implementação concluída, CI verde ou aprovação humana.

Checklist gerada pela aplicação manual da skill oficial `speckit-checklist`
do Spec Kit 1.2.3, com helper oficial de pré-requisitos/template executado.
Não houve dispatch nativo pelo Codex CLI. A geração deixa itens desmarcados;
uma revisão posterior do owner registra sua avaliação.

## Completude e clareza

- [x] CHK001 O requisito de ensaio persistente distingue fonte sintética, destino novo e recusa de sobrescrita? [Completude, Spec US1/FR-P01]
- [x] CHK002 Os campos preservados e o tratamento explícito das perdas estão enumerados sem sugerir recuperação de informações ausentes? [Clareza, Spec FR-P02/05, data-model.md]
- [x] CHK003 A independência do leitor inclui instalação separada, ausência do produtor e ausência de contexto remoto implícito? [Completude, Spec FR-P03]
- [x] CHK004 A comparação tem identidade, tipo e unidade definidos por fonte, sem permitir que outro produtor substitua a evidência obrigatória? [Clareza, Spec US2/FR-P04, contracts/demo.md]

## Consistência arquitetural e privacidade

- [x] CHK005 A preservação de ADR-0001/ARC-01–09 e do perfil candidato é compatível entre spec, plano e tarefas? [Consistência, Spec FR-P10, Plan Constitution Check]
- [x] CHK006 O escopo distingue claramente os dois produtores existentes das extensões de domínio futuras? [Cobertura, Spec FR-P07/10]
- [x] CHK007 A separação entre material público e privado abrange código, corpus, mapas e recibos, e identifica um único publicador? [Completude, Spec FR-P07, Plan Ownership]
- [x] CHK008 As declarações de validade, integridade, disponibilidade e revisão científica têm limites distintos e explícitos? [Clareza, Spec FR-P02/05, data-model.md]

## Cenários e critérios mensuráveis

- [x] CHK009 Os cenários negativos incluem estrutura, tipo/ID, relações, ausência, integridade, limites ZIP, precisão, mutação e referência externa? [Cobertura, Spec FR-P06/SC-P03]
- [x] CHK010 Os critérios de falha impedem sucesso por mera conclusão da coleta e abrangem validação, comparação, processo e navegador? [Clareza, Spec NFR-P04, contracts/demo.md]
- [x] CHK011 As plataformas, modos Python e viewports têm escopo explícito, distinguindo observação local e CI? [Mensurabilidade, Spec NFR-P01/SC-P02]
- [x] CHK012 A imutabilidade e o armazenamento derivado têm critérios objetivos sem criar requisito de host adversarial ou backend novo? [Consistência, Spec FR-P03/NFR-P02, Plan Risk]

## Autoridade, evidência e rastreabilidade

- [x] CHK013 A definição de PoC concluída exige os sete gates técnicos e evidência do par final, preservando provas históricas sob seu escopo? [Completude, Spec FR-P08/SC-P04, Tasks T014–T016]
- [x] CHK014 O handoff separa dependência funcional, disposição histórica desconhecida e decisões humanas específicas, sem atribuir poder físico à PoC? [Consistência, Spec FR-P09/10, contracts/demo.md]

## Notes

`speckit-implement` lê os marcadores; não é owner deles. O arquivo
`requirements.md` tem o ciclo próprio de specify/clarify. Estes itens avaliam
requisitos escritos, não substituem testes, review de código ou CI.

## Avaliação posterior do owner A4

Os 14 critérios foram avaliados após a geração. Resultado: 14/14 satisfeitos
para qualidade dos requisitos, por confronto de spec, plan, tasks, contratos,
data-model e clarifications. O helper oficial confirmou spec/plan/tasks; não
há hooks registrados. Dez FR, quatro NFR e quatro SC têm cobertura por 16 tarefas.
Nenhuma inconsistência constitucional, duplicação material ou ambiguidade
bloqueante foi encontrada. A execução/CI e o aceite humano têm recibos próprios.
