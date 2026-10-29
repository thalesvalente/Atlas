# Pesquisa delimitada e decisões de desenho

Não é repetição dos estudos ATLAS-PARITY-01. As fontes e os bytes efetivamente lidos
estão no [registro](../../../../docs/missions/atlas-parity-02/p01-contracts/EVIDENCE-REGISTER.md).

| Questão | Decisão candidata | Evidência / alternativa |
|---|---|---|
| Base e autoridade | manter c2d00fb; recibo PR #5 posterior esclarece ADR-0002 | E001–E006; não reescrever histórico |
| Estudos A/B/C/D | INPUT_MISSING para uso integral | inventário delimitado; resumo/hash não substituem texto |
| Entidades fora de runs | aproveitar entities e explicitar UI limitada | E009–E013; não fabricar CreateAction |
| Identidade | contexto catálogo/fonte/ID; reorder precisa guarda/teste próprio | E012–E013; digest não é identidade global |
| Tabelas e marcos | distinguir conservação opaca de semântica genérica contratada | E010–E016; evoluções futuras separadas |
| Cobertura | registrar medições por camada, sem totalizar populações sobrepostas | contexto de seleção obrigatório |
| Validação | SDK real + worksheet documental restrito | não promover worksheet a protocolo |
| Spec Kit | helpers existentes com diretório explícito/no-persist | common.py suporta ambos; sem ponteiro global |

Não se conclui perda no produtor a partir de ausência na UI. Para fonte/projeção/
seleção/conversão privada sem bytes acessíveis, a observação é UNKNOWN_UPSTREAM.
Gaps da baseline têm critérios falsificáveis; futuras decisões não são autorizações.
