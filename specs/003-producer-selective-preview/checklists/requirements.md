# Qualidade dos requisitos — REUSE-01

Este checklist avalia o contrato, não a execução dos testes.

- [x] Reaproveitamento de APIs existentes é requisito verificável, não intenção vaga.
- [x] Aquisição, transformação e consumo têm responsabilidades distintas.
- [x] O Caderno interoperável permanece como contrato público.
- [x] Regras de preservação semântica e tratamento de perdas estão explícitas.
- [x] Referência sem direção não autoriza inferir entrada/saída.
- [x] Privacidade e independência do viewer são critérios de aceite.
- [x] Limites do ensaio sintético versus host real estão definidos.
- [x] Aprovação do protocolo, merge, promoção e limpeza não são inferidos.

As tarefas de implementação/CI/revisão permanecem em tasks.md; não foram promovidas pelo checklist.

## Qualidade do delta LOCAL-REAL01
- [x] O requisito define aquisição permitida e comportamento quando configuração/rota está ausente (FR-08).
- [x] A distribuição privada e a independência da instalação pública têm fronteiras explícitas (FR-09).
- [x] Identidade ausente, semântica original e seleção substituta têm tratamento verificável (FR-10).
- [x] O aceite distingue navegador, CLI e startup e prevê ausência de ferramenta (FR-11).
- [x] Destino, privacidade, concorrência, veto e limites estão delimitados (FR-12–13).
- [x] A entrega exige repetição e prova de estabilidade com escopo declarado (FR-13).

## Qualidade dos requisitos CLOSE01

- [x] Semântica neutra e separação de entradas/saídas/linhagem estão definidas (FR-14).
- [x] Identidade por fonte/ID, formas aceitas, ordem e duplicação estão delimitadas (FR-15).
- [x] Alvo ausente, payload ausente, digest declarado e verificação têm regras distintas (FR-16).
- [x] Ausência de menções e modelos anteriores têm estado definido, sem dados inventados (FR-17).
- [x] Conteúdo não confiável e navegação interna/externa têm fronteiras verificáveis (FR-18).
- [x] Teclado, foco, 390 pixels, 200% e quebra de IDs têm critérios observáveis (FR-19/SC-05).
- [x] Compatibilidade, reconstrução e independência do consumidor são mensuráveis (FR-20/SC-06).
- [x] Piloto histórico, prova nova, CI por SHA e decisões humanas estão separados (FR-21/SC-07).

Avaliação do coordenador sobre qualidade textual antes da implementação: 22/22.
Esses marcadores não atestam execução de testes ou aceite científico.
