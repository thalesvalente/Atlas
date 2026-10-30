# Modelo documental P01

O modelo não altera APIs nem serialização do Caderno.

| Entidade documental | Chave / informação | Regra |
|---|---|---|
| Fonte de evidência | ID E/I/S, SHA/path ou hash, escopo de leitura | atribuição explícita; bytes ausentes não verificados |
| Capacidade/jornada | P01-Jxx | identificação própria, não suposta jornada C-UX |
| Referência contextual | catálogo corrente + source_id + id | separação de colisões; sem estabilidade prometida |
| Observação temporal | valor, origem, precisão | publicação/indexação/observação/evento/criação distintos |
| Medição de cobertura | camada, unidade, escopo, seleção, contagem e denominador | desconhecido é null, não zero |
| Regra de apresentação | CURRENT_CONTRACT / COMPATIBLE_PRESENTATION_CANDIDATE / PERSISTED_EVOLUTION_REQUIRED | não ratifica proposta persistida |
| Exemplo | documento sintético + resultado esperado | worksheet fora do wire format; SDK verifica Caderno vigente |
| Handoff | base, payload testado, testes, revisão, próximo ato | sem autorreferência ao SHA do commit que o contém |

A gramática executável limitada dos exemplos consta em `VALIDATION.md`, sob a raiz
de contratos. Ela serve a estes ensaios e não adiciona novos campos ao schema público.
