# ATLAS-PARITY-03-C3 — gate de contratos P01

**Estado na autoria do commit:** C3_GATE_IMPLEMENTED_CI_NOT_YET_OBSERVED; C3_CONTRACT_GATE_READY não reivindicado.

## Identidade

Origem técnica: `3a308ee78e185912959920d85a97cd511a70a764` (tree `03894a33271c030a72ccb7b016aeed943b11f525`). Origem documental: `2cd0e4686fb7456cb7c114bd778bb32a6bd9fad7` (tree `e27541f68039dc09b3e29198be937f50978752a2`). Manifesto P01 SHA-256 `88f64b8ab62d60e4355a3f29553173638f4d7e3844ce0e8126dc1484713c353c`. A conferência inicial leu o manifesto (82 linhas), o handoff (83 paths) e confirmou 51 blobs do pacote técnico idênticos. O runner revalida os 82 hashes no SHA da execução.

## O que foi implementado

- `docs/contracts/atlas-parity-02/p01/run_contract_gate.py`: runner fail-closed para os 46 casos explícitos (11 positivos, 35 negativos), nove probes do leitor real, 11 regressões de referências e auditoria arquitetural aplicável. Executa separadamente normal e `-O`, compara os dois relatórios normalizados e recusa qualquer skip. Emite JSON e JUnit por modo e recibo JSON geral.
- `.github/workflows/atlas-parity03-contracts.yml`: workflow independente Windows/Ubuntu, Python 3.12, checkout do SHA efetivo com histórico, instalações públicas e upload de evidências por SHA; nenhum produtor privado. Não modifica os três workflows globais reservados a C1.
- Matriz P01 28/28 com status e owner históricos imutáveis e correspondências candidatas P02/P03 (isoladas, não presentes no tree C3). Testes de composição P06/C1/C2 **não verificados nesta missão**.

## Limites e bloqueios de aceite

A execução automática e seus resultados dependem de run terminal do GitHub Actions no HEAD final da PR C3. O revisor nativo independente não está disponível neste ambiente; `INDEPENDENT-REVIEW.md` é declaração transparente de indisponibilidade e revisão de autoria própria, não um parecer independente aprovado. Sem ambas as provas, usar `C3_BLOCKED_EXACT`. Os 28 itens são jornadas P01, **não** as do estudo C ausente. Paridade integral e perdas upstream continuam `UNKNOWN_UPSTREAM`. Não há novo esquema, aprovação científica, autenticação, merge, promoção ou release.

O recibo de execução de CI deve ser lido no próprio run e atrelado a `github.sha`, sem substituir o resultado de um SHA por outro.
