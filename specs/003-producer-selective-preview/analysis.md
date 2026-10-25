# Análise pré-implementação — REUSE-01

FR-01/02 → R002/R005/R006: prova deve usar API real do produtor; parser próprio não comprova reaproveitamento.
FR-03/05 → R007: preservação de campos selecionados, perdas explícitas, referências não reabertas, sem aprovação científica.
FR-04 → barreira público/privado e ensaio do viewer sem produtor instalado.
FR-06 → R005/R007/R008: fixtures sintéticas pelo pipeline original, SDK público e CI por SHA.
FR-07 → R006/R010: pacote pequeno e nenhum clone/worktree no host.

Não há desvio de arquitetura. A direção anterior de ler diretamente o índice por outro parser foi supersedida para esta candidata ainda não integrada. O histórico Git conserva os resultados anteriores; novos testes devem demonstrar a substituição.
