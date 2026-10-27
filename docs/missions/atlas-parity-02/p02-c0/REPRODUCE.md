# Reprodução no ambiente isolado de engenharia

Usar somente as fontes sintéticas versionadas e um checkout do código
`b443f9eb25f118e6a68c2ad17c8e21ab7aa99990` ou do commit documental que preserve os
mesmos bytes executáveis. Os paths abaixo são parâmetros exemplificativos, não
caminhos do host de um usuário. Não executar instalação ou servidor no host por inferência.

## Wheels, import/CLI e regressão

Com Python 3.12, no checkout:

```bash
ATLAS_P02_REPO="$(pwd)"
ATLAS_P02_WORK="$(mktemp -d)/install"
python -m venv /destino/engenharia-p02
/destino/engenharia-p02/bin/python -m pip install build==1.3.0 setuptools==80.9.0 wheel==0.45.1 jsonschema==4.25.1
/destino/engenharia-p02/bin/python scripts/qa/clean_install.py --repo "$ATLAS_P02_REPO" --work "$ATLAS_P02_WORK"
/destino/engenharia-p02/bin/python -m pip install "$ATLAS_P02_WORK"/wheels/*.whl
cd /destino/fora-do-checkout
/destino/engenharia-p02/bin/python -I "$ATLAS_P02_REPO/scripts/run_checks.py"
/destino/engenharia-p02/bin/python -I -O "$ATLAS_P02_REPO/scripts/run_checks.py"
```

Crie os diretórios exemplificativos no ambiente de engenharia. `--work` deve apontar
para diretório ainda inexistente: o helper recusa sobrescrita. No Windows os
executáveis dos venvs ficam em `Scripts/python.exe`. O runner global descobre os
testes novos diretamente em `tests/viewer`; não foi alterado por esta frente.

O recibo original do helper descreve quatro registros de sua própria fixture
ambiental. A jornada P02 usa separadamente duas fontes/28 registros. Os valores
históricos `browser=NOT_RUN_BY_THIS_SCRIPT`, `windows=NOT_RUN` e
`human_protocol_acceptance=PENDING` devem ser interpretados como escopo daquele
helper, não como resultado de todos os demais recibos ou revogação da PR #5.

## Jornada real de navegador

Disponibilize Playwright 1.62.1 e Chromium funcional no ambiente de engenharia.
O caminho padrão é `npm install --no-save playwright@1.62.1` no checkout seguido de
`npx playwright install chromium`. Se uma instalação existente for usada, a
resolução de módulo deve estar acessível ao harness; o runtime desta missão forneceu
`CODEX_PRIMARY_RUNTIME_NODE_MODULES`. Registre a versão real e o binário utilizado.

```bash
"$ATLAS_P02_WORK/viewer-env/bin/python" -I \
  "$ATLAS_P02_REPO/scripts/qa/atlas_parity02_p02_run_browser.py" \
  --repo "$ATLAS_P02_REPO" \
  --report /destino/evidencias-p02/browser.json \
  --screenshots /destino/evidencias-p02/screenshots \
  --code-sha b443f9eb25f118e6a68c2ad17c8e21ab7aa99990
```

Um binário compatível disponível pode ser selecionado por `ATLAS_BROWSER_BINARY`.
O recibo de ambiente registra a alternativa efetivamente usada nesta missão e a
configuração de fontes. Não usar os argumentos extras de `@sparticuz/chromium` como
se fossem requisito do produto. A prova utilizou os defaults do Playwright.

O wrapper exige SDK/viewer instalados fora do checkout e R4 ausente, valida as duas
fontes, inicia servidor próprio em loopback/porta efêmera, executa a jornada, compara
hashes antes/depois e encerra o servidor. Não depende de serviço do host, não faz
polling remoto e não abre referências externas. Exit0 indica conclusão da jornada;
falha retorna exit1, browser indisponível retorna exit2/NOT_RUN.

As seis imagens são overview 1440, detalhe 390 e páginas completas 1440/390/320 e
320 com text spacing. A altura das páginas completas cresce com o conteúdo. Rolagem
de tabelas em suas regiões não significa overflow horizontal da página. Fontes CJK
e emoji compatíveis são necessárias para confirmar seus glifos visualmente.

## Método e fronteiras

No checkout, sem gravar ponteiro de feature:

```bash
SPECIFY_FEATURE_NO_PERSIST=1 \
SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0/workstreams/p02-c0 \
python .specify/scripts/python/setup_plan.py --json
SPECIFY_FEATURE_NO_PERSIST=1 \
SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0/workstreams/p02-c0 \
python .specify/scripts/python/setup_tasks.py --json
SPECIFY_FEATURE_NO_PERSIST=1 \
SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0/workstreams/p02-c0 \
python .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
python scripts/qa/architecture_audit.py . \
  --protocol packages/protocol/src/caderno_protocol \
  --viewer packages/atlas/src/atlas_viewer --viewer-module atlas_viewer
git diff --check
sha256sum -c docs/missions/atlas-parity-02/p02-c0/MANIFEST.sha256
```

No CODE_SHA, `python scripts/qa/speckit_audit.py --allow-presentation-delta` retorna
exit1 para os três arquivos P02 fora da allowlist histórica. Esse resultado esperado
do estado observado é um **gate real pendente**, não um teste positivo. P06 deve
alterar estritamente o controle e testá-lo. O novo browser também requer conexão
explícita ao workflow por P06.
