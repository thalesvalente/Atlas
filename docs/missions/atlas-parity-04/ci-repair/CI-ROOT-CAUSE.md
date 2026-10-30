# Causa raiz e correção por workflow

## Evidência original — SHA `c25d37998dac7174067a2819391f3af1625f96dc`

| Workflow/run | Job/step representativo | Finding | Classificação | Correção aplicada |
|---|---|---|---|---|
| `ATLAS-PARITY-02 P06 frozen-boundary QA` / `41001137728` | Jobs P06 `123885547585`, `123885547656`, `123885547692`, `123885547745`; step `Preserve frozen protocol, public inputs and governance` | `UNEXPECTED_PROTECTED_FILE` para a ADR-0003 proposta | `FROZEN_BOUNDARY_EXPECTED` | O auditor P06 não é relaxado. `atlas_parity04_doc_ci.py boundary` exige exatamente esse único erro histórico e só o neutraliza após provar blob, path, ancestry, modos, histórico e overlay completos. |
| Mesmo run | Spec Kit jobs `123885547644` e `123885547948`; step `Verify existing managed assets without weakening the audit` | A sucessora não recebe o modo C4 por depender da string da branch | `SUCCESSOR_DISPATCH_BUG` | `atlas_parity04_doc_ci.py speckit` seleciona por identidade/ancestralidade validada. |
| `ATLAS-PARITY03 P03 isolated qualification` / `41001137738` | Jobs portáveis e Chromium; step `Bind frozen inputs and ownership to exact candidate`; Spec Kit step `Check C2 workstream...` | `P03 manifest entry changed: tests/viewer/test_atlas_parity02_p03_harness.py` | `SUCCESSOR_DISPATCH_BUG` | `p03-inputs`/`p03-browser` usam P03 isolada somente na linhagem P03 sem C4; C4/AP04 usam o auditor composto, que reconhece a única adaptação congelada. |
| `ATLAS-PARITY-03 C4 full composition` / `41001137742` | Jobs C4 `123885547518`, `123885547519`, `123885547571`, `123885547767`; step `Bind input manifests...` | `C4 manifest must cover every authored path, with no arbitrary exclusions` | `MANIFEST_SCOPE_MISMATCH` | O manifesto C4 é lido no SHA C4 e comparado apenas com `COMPOSITION..C4_BASELINE`; AP04 é overlay suplementar completo e separado. |
| Mesmo run | Spec Kit jobs `123885547194`, `123885547671`; step `Resolve C4 spec, plan and tasks...` | Falha decorrente da associação de inputs ao HEAD sucessor | `MANIFEST_SCOPE_MISMATCH` | O auditor C4 primeiro fixa a C4 e, quando HEAD é sucessor, exige o guard AP04 completo. |
| `ATLAS021 candidate verification` / `41001137694` | workflow completo | Sem finding no run original | Não aplicável | Requalificação continua obrigatória no SHA publicado; não se transfere o sucesso antigo. |

## Invariantes preservadas

- `scripts/qa/atlas_parity02_p06_audit.py` permanece byte-idêntico e fail-closed.
- `scripts/qa/atlas_parity03_p03_ci.py` permanece byte-idêntico e continua sendo o gate da linhagem P03 isolada.
- Manifestos C1/C2/C3/C4 permanecem byte-idênticos.
- Pins existentes de GitHub Actions são comparados com C4 e não podem mudar no sucessor.
- Não há `paths-ignore`, seleção por nome da branch, `continue-on-error`, `if: false` ou `|| true` nos workflows alterados.

## Ausência de regressão alegada

As falhas originais ocorreram em binding/inputs antes dos testes de produto correspondentes. Isso não prova regressão nem prova ausência de regressão. A execução dos browsers, suites instaladas e 168 IDs C4 deve ocorrer novamente no SHA publicado.

## Findings adicionais reproduzidos na retomada -03

1. Guard original comparava constantes C4, mas permitia corpo de função retornando PASS com manifesto recalculado. Contraprova local: PASS indevido. Correção: pin independente dos bytes completos do auditor revisado.
2. Checagem textual de workflow permitia if-expression falsa no step obrigatório, conservando comandos/pins e manifesto atualizado. Contraprova local: PASS indevido. Correção: pin dos bytes completos dos workflows revisados.

Seis IDs novos verificam corpo C4, condições de workflow, fluxo do guard e âncoras dos controles/testes. Não há modificação funcional do produto ou dos workflows originais recebidos.

## Confirmação no SHA técnico publicado

No SHA `54ffea9e8fe2ed5cde071a8ec52fbcbff857df60`, os runs AP04 `41087116946`, P06 `41087116019`, P03 `41087116351`, C4 `41087116596`, ATLAS021 `41087115963` e Spec Kit 003 `41087116289` encerraram success: 33/33 jobs. Os 168 IDs históricos foram comparados com os logs reais e preservados integralmente nas quatro células, com 23 novos IDs separados. P06 mantém FAIL exatamente para ADR-0003 nos checkouts Actions; a exceção exata AP04 passa. A limitação CRLF do worktree local está registrada sem correção de arquivos congelados em CI-EVIDENCE.json/RESULT.md.

O commit posterior destes recibos exige CI e revisão próprias; esta confirmação não transfere sucesso ao próximo SHA.
