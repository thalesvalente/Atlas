# Feature 004 — Atlas parity C0: composição mínima C1

Missão atual: ATLAS-PARITY-03-C1. Branch exclusiva:
`integrate/atlas-parity03-c1-core-20261027`.
Baseline: `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`, árvore
`5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`.

## Intenção e entradas

Compor exatamente P02 + P06, reparar os gates globais diagnosticados e verificar
os bytes compostos. P02: código `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`,
handoff `db6e8b64c28e756d0a2ff4fd1cd90f404c6c0533`. P06: código
`d21d8a490b89995ae5707a7a53b469685416a383`, handoff
`9b0a500b6612d260a9f9bd8a4c8da1be4841cf48`.
Os workstreams P02/P06 e seus documentos congelados continuam sendo fontes
atribuídas; o estado histórico P06 aguardando input não descreve esta composição.

P01 e P03 não integram C1. P04 privado não é acessado nem necessário. C0 não
declara paridade completa: estudos A/B/C/D integrais e denominador permanecem
ausentes. O aceite ADR-0002 v1.0 como direção de estabilização está registrado
na PR #5 e na baseline; bytes históricos PENDING_HUMAN são preservados, sem
reabertura de aceite nem alegação de release, promoção ou aprovação científica.

## Requisitos verificáveis

- FR-001: preservar byte a byte protocolo, fontes sintéticas e governança;
  rejeitar alteração, remoção e adição protegida. A troca deliberada de pacote
  do driver P06 é comparada ao estado esperado, sem alegação falsa de imutabilidade.
- FR-002: usar APIs reais com fontes de IDs repetidos, pacote inválido/trocado e
  cache obsoleto; a identidade é o par fonte + ID, nunca a posição da linha.
- FR-003: preservar UNKNOWN, revisão, ausência, tipo, unidade, precisão e tempo;
  mentions são neutras. Nome da métrica e seu identificador têm provas distintas.
- FR-004: instalar wheels e executar em raiz externa ao checkout; SDK sem
  viewer/R4 e viewer sem R4; assets iguais ao Git e às respostas HTTP permitidas.
- FR-005: executar suíte integrada em Windows e Ubuntu, Python normal e -O,
  zero skips; publicar IDs da coleção real sem somar focais, OS, modos ou reruns.
- FR-006: auditoria deny-by-default; opt-in P02 só para catalog.py, server.py e
  static/index.html com bytes do código congelado, sem exceção por diretório;
  preservar negativas de protocolo, constituição, ADRs e skills.
- FR-007: preservar ancestry dos heads documentais e dos códigos testados;
  testar SHA composto e obter revisão nativa independente sem autoria.
- FR-008: entregar resultado, inputs, topologia, CI, matriz, parecer, handoff e
  manifesto. Evidências distinguem SHA, ambiente, execução real e limites.
- FR-009: reexecutar os três browsers legados, a troca P06 e C0 P02;
  seletores por data-run-key = JSON.stringify([sourceId, runId]), unicidade,
  valores mapeados pelos cabeçalhos de coluna e th scope=row da métrica.
- FR-010: P02 gera JSON, seis PNGs e recibos com Chromium/Playwright, fontes
  CJK/emoji, reflow, teclado e foco; zero requisições externas/erros de página.
  native_zoom=NOT_RUN, css_zoom_used=false, wcag_certification=false.
- FR-011: os helpers oficiais Spec Kit 1.2.3 validam 003 e 004 sem persistir
  .specify/feature.json; a branch própria e as PRs fonte permanecem separadas.

## Jornadas e aceite

US1: o integrador identifica bytes, proveniência, ambiente e resultado pelo recibo.
US2: uma alteração arbitrária em path protegido permanece RED apesar dos opt-ins.
US3: IDs repetidos em duas fontes selecionam e comparam a execução correta.
US4: uma troca de snapshot invalida detalhe e seleção antigos explicitamente;
o pacote B preservado conserva seus bytes e pode ser selecionado de novo por
ação explícita. Binding global P02 precede resolução de IDs; token não autentica.

SC-001: C1_CORE_CANDIDATE_READY somente após todos os runs globais SUCCESS no
SHA final, browsers exigidos PASS, invariância e revisão sem finding bloqueante.
SC-002: nenhuma operação no host do usuário, pacote privado, mudança de protocolo,
merge em main, release, deploy, force-push ou aprovação científica.
SC-003: C1_BLOCKED_EXACT identifica job/step/path/precondição real; preserva o
incremento e o menor próximo ato, sem baseline substituta ou resultado antecipado.
