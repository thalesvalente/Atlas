# Aplicação exata — ATLAS-PARITY04-DOC-CI-REPAIR-01

Este pacote existe porque a sessão que produziu o reparo tinha leitura efetiva do GitHub, mas não expôs operação invocável de commit/push ou dispatch. Ele **não** representa uma publicação na PR #14.

## Pré-condições obrigatórias

Use somente o checkout já existente de `thalesvalente/Atlas`; não crie branch, worktree ou clone novo.

```bash
git switch docs/atlas-parity04-plan-of-record-20261030
test "$(git rev-parse HEAD)" = "c25d37998dac7174067a2819391f3af1625f96dc"
test -z "$(git status --porcelain --untracked-files=normal)"
```

A árvore esperada antes da aplicação é `e6eacdd02a329f88bc0dd656523b84a8fec9217e` e a base C4 é `72d9b94e613a57c82a5afd309796f44b271e2185` / árvore `0a622663ca40232d6143659f82cfe9ce43702e90`.

## Aplicação

Copie `ATLAS-PARITY04-DOC-CI-REPAIR-01.patch` para fora ou para uma área ignorada do checkout. Depois:

```bash
git apply --check --index ATLAS-PARITY04-DOC-CI-REPAIR-01.patch
git apply --index ATLAS-PARITY04-DOC-CI-REPAIR-01.patch
git diff --cached --check
git diff --cached --name-status
```

O diff deve conter exatamente 19 paths: 5 modificados e 14 adicionados. Nenhum dos nove documentos AP04 originais aparece no patch.

## Validação focal antes do commit

```bash
python -m py_compile \
  scripts/qa/atlas_parity04_doc_ci.py \
  scripts/qa/atlas_parity03_c4_ci.py \
  tests/qa/test_atlas_parity04_doc_ci.py

python -m unittest discover \
  -s tests/qa -p 'test_atlas_parity04_doc_ci.py' -v

PYTHONOPTIMIZE=1 python -O -m unittest discover \
  -s tests/qa -p 'test_atlas_parity04_doc_ci.py' -v
```

Resultado esperado em cada suíte: `Ran 17 tests ... OK`.

## Publicação autorizada pela missão

Após revisão do diff e somente na branch existente:

```bash
git commit -m "ci: qualify the AP04 documentation successor"
git push origin HEAD:docs/atlas-parity04-plan-of-record-20261030
```

Não use rebase, force-push, merge para `main`, release, deploy ou promoção.

## Fechamento que ainda exige GitHub

1. Exigir runs novos no SHA publicado, não reruns do SHA `c25d3799…`.
2. Requalificar o workflow AP04, P06, P03, C4 e ATLAS021; incluir Spec Kit quando disparado.
3. Confirmar os 168 IDs C4 e browsers reais no SHA novo; sucesso histórico não é transferível.
4. Obter revisão independente real no SHA final, incluindo qualquer commit posterior de recibos.
5. Atualizar `CI-EVIDENCE.json`, `HANDOFF.json`, `INDEPENDENT-REVIEW.md`, `INPUT-SHAS.json`, `RESULT.md` e `MANIFEST.sha256` com fatos reais. Esse commit de recibos também precisa de CI terminal e revisão do delta.
6. Manter PR #14 Draft até todos os gates convergirem.

## Identidade do patch

SHA-256: `d25540bce2a90dbf099ca38b82528b645ea49c92fd86d04438d5f1b7a58b83b8`.
