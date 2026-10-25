# Modelo de dados da prévia
| Conceito genérico | Modelo Caderno | Tratamento |
|---|---|---|
| Campanha/projeto | `cp:Project` | Identificador producer-scoped |
| Família/experimento | `cp:Experiment` | Vínculo a projeto declarado |
| Execução | `CreateAction` | Estado e revisão separados |
| Medida operacional | `PropertyValue` | Tipo/unidade explícitos, não alegar resultado científico |
| Referência externa | `File` | Disponibilidade não verificada, sem copiar payload |
| Predecessor selecionado | `prov:wasDerivedFrom` | Somente alvo declarado e incluído |
| Predecessor não selecionado | Limitação do manifesto privado | Não criar execução artificial |

Original e projeção são conceitos distintos; índices não se tornam fontes científicas canônicas. Hash declarado não equivale a autenticação.
