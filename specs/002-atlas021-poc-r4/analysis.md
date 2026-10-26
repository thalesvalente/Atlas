# Analyze — consistência do delta

**Data:** 2026-10-24. **Autoria:** ORQ-A; revisão independente A4 separada.

| ID | Severidade | Evidência/ação |
|---|---|---|
| D01 | Média, resolvida no desenho | Harness baseline provava só um par global; FR-P04/T008 exigem par por fonte |
| D02 | Média, resolvida no desenho | Corpus R4 baseline não tinha par numérico do mesmo tipo; variante sintética explícita conserva default |
| D03 | Média, resolvida no desenho | TemporaryDirectory eliminava demonstração; FR-P01/T005 exigem saída persistente nova |
| D04 | Baixa, resolvida | Provas explícitas ID/tipo/expansão ZIP faltavam; T011 cobre sem alterar SDK |
| D05 | Controle | Resultado local não se transfere a novo SHA; T014–T016 fecham por recibos append-only |
| D06 | Controle | Constituição/perfil e estados humanos são preservados, sem exceção arquitetural |

Não há contradição entre PoC autorizada e ADR-0002 PENDING_HUMAN. Nenhum terceiro
produtor, dado real ou conteúdo privado entra no público. Tipos, estados e perdas
usam o contrato existente; não há novo schema ou formato concorrente.
Matriz requisito→tarefa→arquivo→evidência em traceability.md.
