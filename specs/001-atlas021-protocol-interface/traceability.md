# Rastreabilidade arquitetural

| Regra | Requisitos | Tarefas | Evidência requerida |
|---|---|---|---|
| ARC-01 | FR-001–006/014/015 | T009–T014 | UI HTTP/browser; ausência executor |
| ARC-02 | FR-008/009 | T007/T008/T011 | SDK instalado sozinho, schema/grafo/contextos |
| ARC-03 | FR-007/019 | T009/T011/T018 | bytes intactos, reconstrução, colisões |
| ARC-04 | FR-009/010 | T007/T015–T017 | AST sem R4, exportadores distintos |
| ARC-05 | FR-009/010/018 | T011/T017/T019 | wheel limpo, dois produtores, CI |
| ARC-06 | FR-003–006/011/012/020 | T007/T012/T013/T016/T018 | estados/unidades/digests e transformações |
| ARC-07 | FR-009/013/014 | T008/T009/T014 | AST, HTTP local, anexos não executados |
| ARC-08 | FR-011/016 | T016/T022/T025 | handoff sem autorização de retirada |
| ARC-09 | FR-016–018 | T020–T025 | ADR proposta, gates humanos, SHA exato |

Os testes são planejados nesta matriz; resultados reais e limites constarão em convergence.md e docs/verification. Nenhuma linha é autorização operacional.
