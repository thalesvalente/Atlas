# Convergência — candidata antes da publicação

Data: 2026-10-24. Avaliação por ORQ-A após implementação, verificação local e revisão
independente. O procedimento da skill instalada `speckit-converge` foi aplicado pelo
agente, com o auxiliar oficial `check_prerequisites.py`; não se alega execução nativa
via Codex CLI. Não há hooks de extensão. A fase de convergência acrescentou somente
T026/T027 à lista de tarefas. Este registro é artefato de entrega de T023.

## Inventário avaliado

20 requisitos FR, seis critérios SC, 11 cenários de aceite, nove regras ARC,
25 tarefas anteriores e sete decisões de plano: separação de pacotes; HTTP local;
fontes explícitas; serialização restrita; estado derivado; dois produtores; verificação
independente/portabilidade. A implementação foi inspecionada dentro dos paths do plano.
Caixas de tarefas não foram usadas como prova de comportamento.

| Achado | Tipo | Severidade | Origem | Evidência/ação restante |
|---|---|---|---|---|
| F1 | partial | HIGH | FR-018, SC-006, T021 | Workflows e revisão local existem; CI/Codex do commit remoto ainda dependem da publicação. T026. |
| F2 | partial | MEDIUM | FR-016, SC-006, AB-CONTRACT | Requisitos, mapeamento privado e disposições existem; handoff deve anexar os SHAs/árvores remotos. T027. |

Zero achados `contradicts` ou `unrequested`; nenhum desvio constitucional aberto
no conjunto revisado. Os dois achados não são dispensados por testes locais.
`tasks_appended`: duas tarefas na Phase 7. A implementação continua com publicação,
CI/review e handoff; resultados finais devem ser registrados nos canais reais.

## Evidência local conferida

- 64 testes integrados por execução: 11 SDK, 41 QA independente, 12 catálogo/HTTP.
  Todos passam em Python normal e `-O`, sem skips neste host Linux.
- Wheels construídos de cópias, instalados em ambientes vazios; SDK sem interface
  e produtor legado, viewer sem produtor legado. A4 executou 41 testes independentes
  normais/otimizados no SDK instalado, com `-I`, fora da árvore de fontes.
- Browser real: 21 verificações na fixture adversarial, desktop 1440px/mobile 390px,
  sem erros JavaScript ou tráfego externo. Fonte, precisão, métricas repetidas,
  comparação, dossiê, teclado e reconstrução são verificados.
- Perfil/contexto/schema: quatro hashes do manifesto conferidos contra esta árvore.
  Todos os hashes de fontes do build A4 correspondem aos pacotes integrados.
- Conformidade externa e comparação: escopo e skips em `docs/protocol/conformance.md`.
  Não há certificação externa integral de Process Run 0.6.
- Compatibilidade de dois produtores: recibos, corpus e mapa concreto permanecem
  privados. O workflow privado fixa o SHA público; não existe condicionamento de
  domínio no viewer. A declaração final depende dos recibos do mesmo par de commits.

## Marcos no instante deste registro

| Marco | Estado | Limite |
|---|---|---|
| A0 | PASS | ADR-0001, constituição, contrato e rastreabilidade versionados |
| A1 | PENDING_HUMAN | ADR-0002 proposta, perfil 0.1.0a1; decisão não simulada |
| A2 | PASS_SCOPED | Perfil/SDK positivos e negativos; conformidade restrita explícita |
| A3 | PASS_SCOPED | Produto instalado, browser real e fontes intactas |
| A4 | PASS_SCOPED_LOCAL | Dois produtores sintéticos; detalhes/evidências privados |
| A5 | PENDING_EXTERNAL | T026: CI/review/Codex exatos após publicação |
| A6 | PARTIAL | T027; oito fontes individuais UNKNOWN sem B-INVENTORY |
| A7 | NOT_APPROVED | Sem decisão de produto/release/rollback/migração |

Aceite humano e disponibilidade do inventário não são falhas a esconder. A candidata
pode ser revisada; estabilização, uso real, promoção e retirada mantêm seus gates.
Registros append-only na PR e coordenação privada podem concluir T021/T026/T027 sem
alterar retroativamente os resultados locais deste documento.

## Adendo após CI e review Codex

O CI público 40116249982 passou em seis jobs e o privado 40116391856 em quatro,
nos SHAs registrados na coordenação. O Codex então identificou um P2 real no SDK:
ZIP DEFLATE corrompido escapava como exceção. A investigação independente confirmou
a mesma classe de falha no codec LZMA. O autor corrigiu as duas fronteiras de leitura
com exceções específicas e LZMA opcional, sem captura genérica ou alteração de perfil.

A4 reproduziu quatro falhas no wheel anterior e verificou os quatro subcasos
corrigidos, normal/otimizado, além de fonte saudável no mesmo catálogo. Evidência:
`docs/reviews/A4-decompression-review.json`. O recibo de wheel anterior permanece
histórico; seu hash não é atribuído à revisão corrigida. Commits de autoria citados
no recibo são revisões locais dos agentes; o commit público agregado é registrado
na PR e pode ser conciliado pelo hash de arquivo.

A suíte integrada agora tem **68 testes por modo: 12 SDK + 43 QA + 13 viewer**,
todos PASS normal e `-O`, zero skips neste host. Uma fonte com metadados corrompidos
fica INVALID/SOURCE_INVALID; payload corrompido fica UNAVAILABLE com aviso, mantendo
os registros. Snapshot, dossiê e rebuild preservam a outra fonte e todos os bytes.

FR-001/013 e US1/AC2 recebem essa regressão. T026 continua exigindo nova CI e Codex
no SHA corrigido; o handoff anterior recebeu adendo HOLD em vez de ser sobrescrito.
T027 será atualizado por novo comentário com o par exato após essa convergência.
