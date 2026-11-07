# Feature 007 — Paridade final e prontidão de retirada

Pedido do operador: 2026-11-07. Extensão compatível das Features 004/005,
governada por ARC-01–09. Não concede merge nem retirada do R4.

## Requirements

- FR-001: conferir projeção explicitamente escolhida por hash de bytes e revisão
  esperados antes de comparar o pacote; digest próprio não prova origem ou frescor.
- FR-002: comparar conteúdo, tipos, presença, identidade estrutural e exportação
  integral; separar importação/exportação de pesquisa e teste visual.
- FR-003: oferecer CSV tipado reversível que conserve ausência, NULL, vazio,
  números exatos, IDs homônimos, campos originais de linha e fórmulas inertes.
  Preservar o CSV protegido compatível e o JSON integral.
- FR-004: testar adulteração, revisão obsoleta em relação ao pin e fonte divergente.
  Não escrever em fontes, executar produtor real nem importar código R4.
- FR-005: registrar PAR-001–015, limites de autenticação/cobertura, consumidores,
  Chrome real e retirada separadamente, sem herdar PASS de SHAs anteriores.

## Success Criteria

- SC-001: contraprovas sintéticas RED/GREEN para colisões de CSV e pins inválidos.
- SC-002: o oráculo lê pacote sem runtime R4 e demonstra igualdade de cada campo
  no snapshot declarado, ou falha com motivo verificável.
- SC-003: novas mudanças recebem CI Windows/Ubuntu e revisão próprias; Chrome
  bloqueado recebe BLOCKED, sem promoção a PASS por HTTP ou Chromium sintético.

HL7/FHIR permanece extensibilidade futura. Não altera protocolo ou ciência.
