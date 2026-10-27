# Feature 004 — Atlas parity C0
Branch P06: `work/atlas-parity02-p06-qa-20261027`.
Base fixada: `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`;
tree `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`.
Reserva 004: livre na árvore e na consulta inicial de branches parity.
Esta especificação agregadora delimita o trabalho P06 recebido; não inventa
requisitos dos estudos A/B/C/D nem tarefas das outras frentes.

## Intenção e clarificações
Entregar QA independente do Atlas sobre o Caderno interoperável vigente.
C0 pode compor P02+P06 sem exigir P01/P03, quando o delta concreto couber no
contrato existente. P02 novo ainda não foi recebido por SHA no preflight.
P01/P03 são opcionais conforme o conjunto escolhido; P04/P05 são evidência
externa atribuída. UNKNOWN não é zero; digest não é autenticidade; CI não é
aprovação científica ou promoção humana.
O aceite ADR-0002 v1.0 como direção de estabilização foi recebido na PR #5,
recibo 6406839421 e merge da base. Preservar os bytes históricos PENDING_HUMAN.

## Requisitos verificáveis do escopo P06
- FR-001: preservar byte a byte todos os arquivos versionados do protocolo,
  entradas públicas e governança; detectar alteração, remoção e adição protegida.
- FR-002: exercer APIs reais com duas fontes de IDs repetidos e conteúdo distinto,
  pacote inválido/trocado e cache obsoleto sem cruzar identidade ou inventar preview.
- FR-003: preservar estado técnico/revisão, UNKNOWN, ausência, precisão e tempo;
  mentions neutras não mudam direção de relações nem provocam leitura/execução.
- FR-004: verificar wheel instalado fora do checkout, SDK sem viewer/R4 e viewer
  sem R4; assets no wheel iguais aos servidos, HTTP limitado à allowlist e origem.
- FR-005: executar testes descobertos pelo runner em Windows/Ubuntu, normal/-O;
  o navegador de engenharia usa explicitamente os três cenários do harness vigente.
- FR-006: manter auditorias anteriores intactas e acrescentar contraprovas.
- FR-007: compor somente SHAs congelados, incluindo P06; testar a composição e
  obter revisor nativo sem autoria antes de declarar candidata verificada.
- FR-008: entregar matriz, decisão, inputs, resultado, handoff e manifesto;
  distinguir todas as dimensões de código, CI, browser, coorte, host e promoção.

## Jornadas e critérios
US1: o integrador lê um recibo e sabe quais bytes, ambiente e prova foram usados.
Aceite: FR-008 lista SHA/tree, execução/reuso e NOT_RUN/PENDING por dimensão.
US2: um delta incompatível não é promovido por suite verde.
Aceite: FR-001/006 rejeitam contraprovas; nenhuma exceção de protocolo é aceita.
US3: a candidata mínima não depende de componente opcional ausente.
Aceite: FR-007 seleciona entradas por necessidade real e lista capacidades ausentes.
SC-001: todos os novos unittest são coletados pelo runner existente, sem asserts
desativáveis por -O; contagens por cenário/modo não são somadas como casos únicos.
SC-002: nenhuma fonte privada, dependência de produtor, versão nova de protocolo,
merge em main, release, deploy ou promoção integra este escopo.

## Limites de evidência
Estudos A/B/D completos: INPUT_MISSING. C integral e handoff: INPUT_MISSING;
apenas resumo com C0/12 jornadas e hashes informados, não verificados sem bytes.
Não há denominador de paridade completa. Não derivar cobertura percentual do
número de cenários sintéticos. Host e coorte reais exigem recibos de suas frentes.
