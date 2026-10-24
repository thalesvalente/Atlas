# Quickstart da verificação

[README](../../README.md) e guia público documentam wheels e ambientes vazios.
Só o controle ambiental público é necessário para repetir a apresentação pública.

```sh
python scripts/run_checks.py
python -O scripts/run_checks.py
python scripts/qa/clean_install.py --repo . --work .ci-clean-poc
python scripts/ci/run_browser.py --work .ci-clean-poc
python scripts/ci/run_browser.py --work .ci-clean-poc --adversarial
```

Ferramentas/Chromium seguem README/workflow. Use destino novo. Esperado: fontes
intactas, SDK sem viewer/produtor, viewer sem produtor, quatro runs ambientais,
reindexação equivalente e checks desktop/móvel sem rede externa.

Operador autorizado executa o guia privado para R4: geração real sintética,
snapshot persistente, importação instalada, equivalência semântica e UI com
ambas as fontes. Locators/recibos dessa prova permanecem privados.
