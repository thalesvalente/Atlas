# Handoff técnico — próximos atos exclusivos da P06

Objeto P02: `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`, árvore
`3a6c4f1b486f47e78c1ab26643dc30ddb28d631a`, base `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`.
PR Draft: https://github.com/thalesvalente/Atlas/pull/8.
Referências de linha abaixo conferidas nesse SHA por `/root/navigation_state`,
em tarefa somente leitura. Não há integração P03 declarada.

## 1. Auditoria Spec Kit — gate observado

CI `40526560524`, jobs `122267640808` e `122267641255`: FAIL na preservação histórica.
CLI oficial 1.2.3 e integração passaram; os arquivos gerenciados não foram alterados.

`scripts/qa/speckit_audit.py:12` usa a base antiga
`a6e57c9c6748b4a0d50b554613c93e2b8a785554`. O opt-in de apresentação das linhas 17–27
autoriza seis arquivos históricos e não inclui estes três arquivos autorizados P02:

```text
packages/atlas/src/atlas_viewer/catalog.py
packages/atlas/src/atlas_viewer/server.py
packages/atlas/src/atlas_viewer/static/index.html
```

**Ato mínimo:** representar essa autorização por regra específica e verificável;
manter modo padrão estrito, rejeição de exclusões e testes negativos para protocolo,
constituição, ADRs e skills. Não usar exceção por diretório nem dispensar auditoria.
Os testes pertinentes estão em `tests/qa/test_speckit_presentation_audit.py:44–67`.
Comprovar também protocolo byte a byte contra a base desta missão `c2d00fb…`.

O workflow `.github/workflows/atlas003-speckit.yml:47–55` ainda usa o opt-in histórico
e valida a feature 003. A validação agregada da 004 exige os arquivos agregadores
e eventual ponteiro sob ownership P06. P02 usou apenas seu workstream e NO_PERSIST.

## 2. Harness global — uma falha observada, outros ajustes por inspeção

CI produto `40526560195`, job `122267640802`: falha real após cinco checks.
A célula observada contém `temperature` e a linha secundária
`urn:environmental:quantity:temperature`; o teste esperava somente `temperature`.
Os cenários adversarial e referências relacionados posteriores foram skipped.

### H06-01: escolher execução pela identidade

`scripts/qa/browser.mjs:52` coleta registros na ordem da API. O harness usa posição
nas linhas 86, 106, 184, 210–211 e 259–260. A tabela P02 ordena deterministamente;
a ordem do grafo não identifica a posição do registro na tela.

Localizar controles por `data-run-key`, cujo valor é
`JSON.stringify([sourceId, runId])`, disponível em `app.js:40,77–81`. Escapar o valor
corretamente e conferir unicidade. Não corrigir só reproduzindo o algoritmo de
ordenação no esperado: a prova deve verificar identidade fonte/ID independentemente.

### H06-02: conferir nome e identidade da métrica separadamente

`scripts/qa/browser.mjs:116–121` compara todo o texto da primeira célula com o nome.
`app.js:134–137` apresenta nome e `<small>` com `property_id || id`.
Verificar campo principal e identificador secundário, conservando valor, motivo de
ausência, tipo e unidade. Verificar a quarta célula de precisão, preferindo
`display_precision` quando presente. Um simples `includes(name)` não prova identidade.

### H06-03: respeitar cabeçalhos e precisão das células

`scripts/qa/browser.mjs:262–271` usa qualquer `small` da linha e índices 1/2 de `td`.
`app.js:161–165` usa `<th scope="row">` para a métrica e `td` para os valores; cada
valor também contém `small` de precisão. Restringir a identidade ao cabeçalho da
linha; usar `td` 0/1 para duas execuções ou mapear pelas identidades dos cabeçalhos;
verificar valor, unidade e precisão na execução correta. Preservar ensaio de métricas
repetidas e impedir sobrescrita.

H06-01/03 são incompatibilidades identificadas por inspeção; não se apresentam como
falhas executadas após a primeira asserção interromper a CI. Reexecutar os três
cenários existentes chamados em `.github/workflows/atlas021.yml:67–72`.

## 3. Conectar a prova browser P02 explicitamente

Os testes Python novos estão diretamente em `tests/viewer` e entram na descoberta
do runner existente. A jornada browser nova não é acionada automaticamente.

**Restrição concreta:** `atlas_parity02_p02_run_browser.py:39–44` exige que SDK e
viewer estejam instalados fora da árvore do repositório. A CI atual cria `.ci-clean`
dentro do checkout (`atlas021.yml:58–62`). Criar o work desta prova em `RUNNER_TEMP`
ou outra raiz externa; não enfraquecer o requisito para acomodar o path atual.

Executar com o Python desse consumidor instalado e o SHA real da candidata P06:

```text
INSTALLED_PYTHON -I scripts/qa/atlas_parity02_p02_run_browser.py
  --repo CHECKOUT_ABSOLUTO
  --report EVIDENCE_ROOT/browser-report.json
  --screenshots EVIDENCE_ROOT/screenshots
  --code-sha SHA_REAL_DA_CANDIDATA
```

Preservar fontes CJK/emoji compatíveis no ambiente de prova, quando necessário.
O upload atual cobre apenas `.ci-clean/browser*.json`, `.ci-clean/browser*.png` e
o recibo legado (`atlas021.yml:77–81`); incluir os novos destinos de JSON e seis PNGs.
Registrar versões, hashes e reflow/teclado sem reclassificar CSS px como zoom nativo.
No P02: `native_zoom=NOT_RUN`, `css_zoom_used=false`, `wcag_certification=false`.

## 4. Composição de P03 sobre objetos congelados

| Ponto de ligação | Local no CODE_SHA | Regra de composição |
| --- | --- | --- |
| Ordem dos assets | `static/index.html:8–10` | style.css, parity02_p02_state.js, app.js; scripts defer em ordem |
| Navegação | `static/index.html:21–27` | Seis vistas conhecidas em data-view |
| Montagem | `static/index.html:50–75` | #view-explore, #detail-content, #compare-content, #timeline-content, #lineage-content, #sources-content, #view-dossier |
| Rota/catálogo | `static/app.js:5–36` | Consumir depois de validação; não existe API pública window.state |
| Renderização | `static/app.js:140–199` | Renderizadores limpam os contêineres; montagem única será removida no próximo render |
| Reflow e foco | `static/style.css:9–13` | Conservar quebra, foco e rolagem apenas nas regiões de tabela |
| Assets HTTP | `server.py:11–16,56–68` | Acrescentar somente nomes exatos à ASSETS; não criar servidor genérico de arquivos |
| Wheel | `packages/atlas/pyproject.toml:15–19` | Globs atuais cobrem static/*.html/css/js planos; subdiretórios/extensões exigem tratamento explícito |
| Views aceitas | `static/parity02_p02_state.js:5–13` | Nova view precisa de contrato/parser/controle/testes correspondentes |
| Binding de identidade | `static/parity02_p02_state.js:138–161` | Validar sessão/snapshot antes de resolver source-N/ID; token não autentica |

Receber SHA, árvore, API e assets reais de P03; integrar os objetos congelados na
candidata P06; posicionar dependências e montar no ciclo de renderização; validar
wheel/import/HTTP fora do checkout. Nenhum nome ou assinatura de P03 é presumido.
Não copiar fragmentos de uma branch em movimento. C0 P02 permanece funcional sozinho.

## 5. Próximo ato mínimo e recibo legado

Integrar o objeto P02 congelado na candidata própria; corrigir os controles globais
descritos; conectar e executar as jornadas; registrar resultados pelo **novo SHA**.
Aguardar objeto P03 não é requisito para corrigir esses gates. Não atribuir CI
`b443f9e…` à candidata resultante.

`scripts/qa/clean_install.py` ainda registra `human_protocol_acceptance=PENDING`.
Se P06 atualizar esse recibo, referenciar a PR #5 como aceite da direção ADR-0002
sem sugerir release, ciência ou promoção aprovados. P02 conservou os bytes do helper
e do recibo original, documentando a limitação temporal.

Ownership explica por que esses atos não foram executados pela P02: o prompt
proíbe escrever workflows, runner/auditoria globais, testes de outras frentes e
feature registry. Não se pede novo aceite da ADR nem permissão para trabalho já autorizado.
