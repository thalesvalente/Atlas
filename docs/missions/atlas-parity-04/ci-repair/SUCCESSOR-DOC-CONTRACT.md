# Contrato do sucessor documental AP04

## Objetivo

Autorizar somente um sucessor documental verificável da C4, sem converter a exceção em permissão para `docs/**`, `docs/architecture/**`, `.github/**`, `scripts/**` ou qualquer futura ADR.

## Âncoras imutáveis

- C4 SHA/tree: `72d9b94e613a57c82a5afd309796f44b271e2185` / `0a622663ca40232d6143659f82cfe9ce43702e90`.
- Baseline documental SHA/tree: `c25d37998dac7174067a2819391f3af1625f96dc` / `e6eacdd02a329f88bc0dd656523b84a8fec9217e`.
- A baseline documental deve ter C4 como pai único e direto.
- Os nove paths publicados nesse SHA devem conservar modo `100644`, tipo blob, OID e bytes.

## Autorização do delta

1. `HEAD` deve descender de C4 e da baseline documental.
2. Cada commit posterior à baseline documental deve ter um único pai, sem merge, e tocar somente paths enumerados no overlay.
3. O diff completo `C4..HEAD` deve conter exatamente os nove documentos e os 19 paths de reparo; nenhum path pode faltar ou sobrar.
4. Os cinco paths existentes devem ter status `M`; os demais devem ter status `A`; todos devem permanecer blobs `100644`.
5. Symlink, remoção, rename implícito, modo executável, submódulo e alteração transitória seguida de reversão são RED.
6. `OVERLAY.json` deve enumerar cada path e propósito exato. `MANIFEST.sha256` deve conter todos os paths de reparo exceto ele próprio, com SHA-256 correto e serialização canônica ordenada.
7. O manifesto C4 no checkout deve ser byte/blob-idêntico ao objeto C4 e cobrir somente a autoria C4.
8. O auditor P06 histórico deve continuar retornando FAIL com exatamente um erro: a ADR-0003 como `UNEXPECTED_PROTECTED_FILE`. Qualquer outro erro é RED.

## ADR-0003

A única exceção documental é o path literal `docs/architecture/ADR-0003-legacy-compatibility-proposed.md`, no blob publicado pela baseline documental. `GATES.json` deve continuar declarando `PROPOSED_NOT_APPROVED`, `DOCUMENTATION_ONLY` e as não autorizações de merge/release/deploy/promotion. ADR-0004, alterações em ADR-0001/0002 ou qualquer outro arquivo de `docs/architecture/` são RED.

## Identidade P03/C4

- A linhagem P03 isolada é reconhecida somente quando contém o input P03 fixado e **não** contém C4.
- C4 exata usa o contrato C4 histórico.
- Um sucessor de `c25d3799…` usa C4 mais este guard AP04.
- Nenhuma outra linhagem recebe fallback permissivo; a classificação falha fechada.
- `INPUTS`, `P03_C4_ADAPTERS`, `ASSETS`, `COMPOSITION` e as declarações de origem do auditor C4 são comparadas semanticamente com o blob C4.

## Workflows

Os quatro workflows existentes conservam integralmente seus pins. O workflow AP04 aceita somente os três actions/pins completos declarados no guard e executa Linux/Windows × normal/`-O`. Tokens de bypass e seleção por nome de branch são rejeitados.

## Evidência

O guard emite JSON e JUnit com `tested_sha`, `tested_tree`, base, baseline documental, documentos, histórico, delta completo, hashes do overlay, boundary P06 e limitações. Esse recibo não substitui run terminal do GitHub, browser real, revisão independente ou decisão humana.

## Correção adversarial PUBLISH-REVIEW-03

O manifesto suplementar verifica integridade/completude, mas não concede autorização semântica. O guard fixa separadamente os bytes completos do auditor C4, cinco workflows e testes. Assim alterações de funções, retornos, call sites, condições, comandos ou pins são RED mesmo quando o manifesto é recalculado.

Os testes fixam o AST executável do guard, excluindo exclusivamente a tabela de hashes, e duplicam as seis âncoras C4/workflows. O guard fixa os bytes completos desses testes. A ordem AST -> testes -> tabela evita a tentativa impossível de embutir o próprio SHA no código. Qualquer revisão conjunta das proteções exige novo diff, justificativa, contraprovas e revisão independente; esses hashes não substituem autorização humana ou parecer.

A região excluída do digest AST deve ser exclusivamente uma tuple literal de pares string/string, avaliada por ast.literal_eval, com os seis hashes congelados e o hash dos testes exatos. A fonte é validada antes de importar o guard; expressões executáveis nessa tabela são RED.

A declaração de codec deve ser UTF-8. Após o preflight, o teste compila e executa exatamente o texto UTF-8 já validado, sem releitura pelo loader; codecs que reinterpretam comentários são rejeitados antes da execução.
