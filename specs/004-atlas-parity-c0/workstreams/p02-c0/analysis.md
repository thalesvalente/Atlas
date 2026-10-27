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

## Convergência de escopo executada

No CODE_SHA `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`, 27 paths no ownership,
protocolo/governança/controles globais sem delta. 98 testes normais e os mesmos
98 com -O passaram; browser focal 23 checks passou; wheel comparada byte a byte
com Git e instalada fora do checkout sem R4. Revisão independente fechou findings
de enum de estados, retorno de foco e fim sem início, além das correções de precisão.

CI do mesmo SHA: quatro jobs de produto e referência pública passaram; browser
global falhou por estrutura de apresentação antiga; Spec Kit falhou na allowlist
histórica, embora CLI/integração passassem. A candidata permanece
P02_IMPLEMENTED_VERIFICATION_PENDING. Nenhuma alteração fora do ownership foi feita
para tornar a CI verde. A composição P03 não foi recebida ou declarada.
