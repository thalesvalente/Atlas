# Demonstração reproduzível da candidata Atlas

Este roteiro abre a interface instalada a partir de wheels em ambientes vazios,
usando o **produtor ambiental sintético já existente**. É a parte pública da PoC
[R4 → Caderno → Atlas](https://github.com/thalesvalente/Atlas/issues/2): qualquer
snapshot produzido no estágio anterior entra pela mesma opção `--source`.
O exportador e a prova do produtor R4 permanecem sob sua visibilidade própria;
esta demonstração pública funciona sem acesso ao código ou aos dados desse produtor.

Perfil candidato: **Caderno 0.1.0a1**, RO-Crate 1.3 + Process Run Crate 0.6.
ADR-0002 permanece **PENDING_HUMAN**. Executar este roteiro não aprova a escolha,
estabilização, licença, merge, release, uso de acervo real ou operação física.
BIM, IFC, IDS e SHACL permanecem no roadmap, fora deste roteiro e do runtime.

## 1. Preparar uma instalação nova

Use Python 3.11+ e um checkout do SHA candidato que se deseja avaliar. Registre
o resultado de `git rev-parse HEAD` junto aos recibos. Crie um ambiente separado
para as ferramentas de build:

```sh
python -m venv .venv-poc-build
```

Ative-o com `source .venv-poc-build/bin/activate` no Linux/macOS, ou
`.\.venv-poc-build\Scripts\Activate.ps1` no PowerShell. Na raiz do checkout:

```sh
python -m pip install build==1.3.0 setuptools==80.9.0 wheel==0.45.1
python scripts/qa/clean_install.py --repo . --work .ci-poc-demo
```

O segundo comando é o entrypoint reproduzível de instalação e demonstração CLI.
Ele reutiliza o exportador ambiental e recusa um destino de trabalho existente.
Em uma repetição, escolha outro nome novo para `--work`; não sobrescreva a prova
anterior. A instalação de ferramentas pode acessar os índices públicos de pacotes;
a instalação final dos wheels e a consulta dos snapshots não dependem da rede.

O comando produz:

| Saída em `.ci-poc-demo` | Uso |
|---|---|
| `wheels/` | SDK e viewer construídos de cópias das fontes |
| `sdk-env/` | Ambiente novo com somente o SDK instalado |
| `viewer-env/` | Ambiente novo com SDK + viewer, sem produtor instalado |
| `environmental-crate/` | Snapshot sintético gerado pelo exportador público |
| `outside-source/` | Diretório de execução isolada com Python `-I` |
| `clean-install-report.json` | Hashes de fontes/wheels, isolamento, reconstrução e imutabilidade |

O estado esperado é `PASS_SCOPED`, com quatro execuções, `r4_absent=true`,
`source_bytes_unchanged=true`, `rebuild_same_records=true` e
`generation_advanced=true`. O recibo distingue expressamente os testes de browser
e de outros sistemas operacionais que não foram executados por esse comando.

## 2. Abrir a interface instalada

Linux/macOS, a partir da raiz do checkout:

```sh
cd .ci-poc-demo/outside-source
../viewer-env/bin/python -I -m atlas_viewer serve --source ../environmental-crate --port 8765
```

PowerShell, a partir da raiz do checkout:

```powershell
Set-Location .ci-poc-demo/outside-source
..\viewer-env\Scripts\python.exe -I -m atlas_viewer serve --source ../environmental-crate --port 8765
```

Abra `http://127.0.0.1:8765`. O servidor atende somente loopback; encerre-o com
Ctrl+C. Ele lê o snapshot explicitamente informado e não executa o produtor.

### Roteiro de apresentação

| Passo | Ação na interface | Resultado observável no exemplo público |
|---|---|---|
| Catálogo | Abrir **Explorar** | Dois projetos, três experimentos e quatro execuções sintéticas |
| Filtros | Selecionar projeto, experimento e estado; depois **Limpar** | Somente registros correspondentes, sem perder os demais ao limpar |
| Detalhe | Abrir cada execução | Identidade, revisão `UNKNOWN`/`HOLD`, métricas/unidades, parâmetros e disponibilidade separados |
| Comparação | Selecionar as duas coletas simuladas de temperatura | Valores 24.5 e 24.8, ambos `number`/`degC`, na mesma linha; revisão permanece explícita |
| Ausência | Abrir execução com falha e sensor sem data | Valor ausente com motivo; data desconhecida não recebe o horário de exportação |
| Timeline | Abrir **Linha do tempo** | Datas declaradas preservadas e grupo sem data declarada |
| Linhagem | Abrir **Linhagem** | Doze relações declaradas, com suas origens, destinos e fontes |
| Validade | Abrir **Fontes e validade** | Perfil, validação, digest e autenticidade `NOT_VERIFIED` como informações distintas |
| Dossiê | Baixar o dossiê derivado | Registros e limitações com autoridade `DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL` |
| Reconstrução | Acionar **Reconstruir índice** | Mesmos registros a partir dos mesmos bytes; o índice continua derivado |

Os valores e as quantidades acima descrevem exclusivamente esta fixture pública.
Não são restrições do protocolo nem critérios fixos para outros produtores.

## 3. Repetir a verificação de browser

Volte à raiz do checkout. Instale o tooling de teste e rode os entrypoints que a
CI já utiliza:

```sh
npm install --no-save playwright@1.62.1
npx playwright install chromium
python scripts/ci/run_browser.py --work .ci-poc-demo
python scripts/ci/run_browser.py --work .ci-poc-demo --adversarial
```

O harness inicia o viewer instalado, verifica Chromium desktop de 1440 pixels e
mobile de 390 pixels, encerra somente o processo filho que criou e grava os
relatórios/capturas no diretório de trabalho. Falha de início ou de teste retorna
código diferente de zero. As requisições HTTP externas da página são bloqueadas
e sua ocorrência reprova o teste; URLs de artefatos não são baixadas.

Além dos filtros, teclado e dossiê, o relatório `browser-report.json` contém
`semantic_coverage`: quantidade de detalhes, valores ausentes, artefatos, relações
e comparações compatíveis exercitadas **por fonte**. Isso evita usar a comparação
de um produtor como prova da comparação de outro. Uma fonte sem par compatível
recebe contagem zero; esse resultado não comprova o cenário de comparação.
O ensaio adversarial conserva unidades/tipos incompatíveis, métricas repetidas,
rótulos não confiáveis e precisão de inteiros grandes.

## 4. Consultar outro snapshot já exportado

No ambiente do viewer, acrescente outra opção `--source CAMINHO_DO_SNAPSHOT`
para uma fonte sintética explicitamente autorizada. Não instale o produtor nesse
ambiente. Primeiro valide-a com o SDK instalado:

```sh
python -I -m caderno_protocol CAMINHO_DO_SNAPSHOT
python -I -m atlas_viewer inspect CAMINHO_DO_SNAPSHOT
python -I -m atlas_viewer serve --source CAMINHO_DO_SNAPSHOT --port 8765
```

Aqui `python` deve ser o executável do `viewer-env` criado acima; substitua o
placeholder somente pela fonte escolhida. `--source` também aceita diretório,
documento de metadados e ZIP dentro dos limites do perfil. Referências externas
permanecem não resolvidas. O Atlas não descobre fontes por conta própria.

O recibo integrado do produtor deve vincular seu SHA, o SHA público, o digest do
perfil, a validação real e a cobertura de sua própria fonte. Recibos públicos
contêm somente fontes públicas; quaisquer snapshots, mapas e recibos privados
permanecem privados. Independência do viewer não prova recuperação histórica,
ausência de consumidores externos ou autorização de remoção.
