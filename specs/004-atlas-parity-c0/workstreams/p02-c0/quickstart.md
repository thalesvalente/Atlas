# Reprodução P02

Todos os comandos usam fontes sintéticas públicas. O servidor aceita somente
fontes declaradas e loopback. Nada aqui autoriza instalação no host do operador.

## Testes no ambiente de engenharia

```bash
python -m pip install build==1.3.0 setuptools==80.9.0 wheel==0.45.1 jsonschema==4.25.1
python -m pip install --no-build-isolation ./packages/protocol ./packages/atlas
python scripts/run_checks.py
python -O scripts/run_checks.py
python scripts/qa/clean_install.py --repo . --work /destino/novo-p02
```

O diretório de instalação deve ser novo; o helper recusa sobrescrita. Confira
`clean-install-report.json`: SDK sem viewer/R4, viewer sem R4, CLI e fontes intactas.
O campo histórico `human_protocol_acceptance=PENDING` desse helper não atualiza a
PR #5; é limitação de recibo antigo, conservado por ownership, a conciliar por P06.

## Explorar a coorte sintética

```bash
/destino/novo-p02/viewer-env/bin/python -I -m atlas_viewer serve \
  --source tests/fixtures/atlas_parity02/p02/source-a \
  --source tests/fixtures/atlas_parity02/p02/source-b --port 8765
```

Abra a URL loopback anunciada. Há 28 execuções e IDs repetidos entre fontes.
Selecione duas, aplique filtros, abra um detalhe, use voltar/avançar, recarregue e
feche o detalhe. A seleção permanece mesmo se um item ficar oculto pelos filtros.
As URLs valem pela sessão/snapshot. Reiniciar o servidor expira referências antigas
com aviso; isso impede que um source-N posicional abra outra entidade silenciosamente.

## Prova de navegador instalada, explícita

```bash
npm install --no-save playwright@1.62.1
npx playwright install chromium
/destino/novo-p02/viewer-env/bin/python -I \
  scripts/qa/atlas_parity02_p02_run_browser.py \
  --repo /checkout/Atlas --report /destino/p02-browser.json \
  --screenshots /destino/p02-screenshots --code-sha SHA_DO_CODIGO
```

No Windows use `viewer-env/Scripts/python.exe`. Um Chromium existente compatível
pode ser fornecido por `ATLAS_BROWSER_BINARY`; registre a versão efetivamente usada.
O wrapper inicia/encerra seu próprio servidor, verifica imports instalados sem R4,
roda jornadas reais e compara os hashes das fontes antes/depois, sem polling.
Capturas: desktop 1440, 390 e 320 CSS px e 320 com text spacing. Não usa CSS zoom;
zoom nativo e certificação WCAG não são alegados. Falha gera exit1; indisponibilidade
real do browser gera exit2/NOT_RUN. O arquivo novo NÃO é acionado pela CI existente.

## Integração P06

Ligar explicitamente o wrapper novo ao job de browser e conservar seus artefatos.
Atualizar o harness global por identidade/semântica (não por posição na lista),
e a allowlist estrita da auditoria para os três arquivos de apresentação P02.
