# Análise pré-implementação

Requisitos P02-R01–08 têm origem explícita no prompt e baseline, sem inventar C-UX.
Nenhuma extensão de protocolo necessária. P01/P03 não bloqueiam C0.
Ownership cobre alterações planejadas; CI/auditoria globais permanecem P06.
Comparação de até quatro é limite herdado de interação, não limite do corpus.
Fixtures 28 constituem mínimo de ensaio, não capacidade máxima do produto.

Riscos concretos: source-N posicional (scope), precisão >2^53 (display textual),
ausência interpretada como zero (coverage null), métricas incompatíveis (grupos),
hash inválido/obsoleto (validação), foco perdido ao rerender (render controlado),
asset não servido em wheel (teste instalado), browser/CI indisponível (gate separado).

Método Spec Kit aplicado manualmente às etapas sem dispatch nativo; helpers reais
com NO_PERSIST são registrados no recibo. Não há extensão/hook na base.
