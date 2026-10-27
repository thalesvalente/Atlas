# Reprodução P03

Execute no checkout do SHA de componentes informado no INTEGRATION-CONTRACT.
Requisitos: Python >=3.11 e Node.js24; Playwright/Chromium só para o gate visual.
Não há instalação de ferramenta ou downloads implícitos nos comandos de teste.

## Testes de comportamento

```bash
python -m unittest discover -s tests/viewer -p 'test_atlas_parity02_p03_*.py' -v
node --test-reporter=tap scripts/qa/atlas_parity02_p03_table_test.mjs
node --test-reporter=tap scripts/qa/atlas_parity02_p03_artifacts_test.mjs
node --test-reporter=tap scripts/qa/atlas_parity02_p03_dom_test.mjs
```

Os três wrappers Python reexecutam os mesmos 42+14+6 casos Node. Não somar como casos únicos.
DOM recorder é teste de contrato/estrutura, não navegador. Testes HTTP reais tentam loopback.
Somente após um impedimento efetivamente comprovado, a execução offline pode registrar:

```bash
P03_SKIP_LOOPBACK_REASON=SOCKET_EPERM_OBSERVED python -m unittest discover -s tests/viewer -p 'test_atlas_parity02_p03_*.py' -v
```

Esse modo deixa5 casos HTTP como skip e não comprova socket. Não usar a variável para ocultar
regressão funcional ou alegar suíte integral verde.

## Harness sintético

```bash
python scripts/qa/atlas_parity02_p03_harness.py --port 8766
```

Abrir http://127.0.0.1:8766 em ambiente que permita loopback. Escolher valores exatos,
vazio, conteúdo hostil e tabela máxima; ordenar/filtrar; conferir metadados versus candidatos.
Ctrl+C encerra. Nenhuma instância do aplicativo principal é alterada.

## Gate de navegador real

```bash
node scripts/qa/atlas_parity02_p03_browser.mjs /tmp/p03-browser/report.json
```

Com Playwright e Chromium já disponíveis: testa desktop 1440, largura 390, zoom 200%, cabeçalhos,
teclado/foco, ordenação/filtro, tabela 20000 células e ausência de requisições externas. Salva
relatório e capturas sintéticas no diretório explicitamente informado. Ausência de Chromium
produz NOT_RUN/exit2. Nesta sessão não foi possível abrir sockets e não havia executável
Chromium: não existe prova visual local. O harness não está na rota principal do Atlas.

## Instalação e composição

Os assets imediatos static/*.js/static/*.css já entram no wheel pelo package-data existente.
A rota do servidor é allowlist: empacotar não disponibiliza o asset via HTTP.
O contrato de integração em docs/missions/atlas-parity-02/p03-components descreve alterações
mínimas P06/P02. Não modificar o Caderno nem inventar rótulos produto para File.
