# Atlas

**Interface local para explorar registros científicos de produtores independentes.**
A candidata `0.1.0a1` abre pacotes, consulta projetos/experimentos/execuções, compara
métricas com unidades, apresenta timeline/linhagem e exporta dossiês derivados.

Status: **PR Draft / candidata de avaliação**. A direção arquitetural foi definida
pelo operador; a escolha do perfil em ADR-0002 aguarda aceite humano. Não há release,
promoção canônica, autenticação científica ou autorização de migração/retirada.

## Separação de responsabilidades

| Unidade | Responsabilidade | Dependências em runtime |
|---|---|---|
| `packages/protocol` — caderno-protocol | Perfil, validação estrutural/semântica e leitura de snapshots | Python stdlib |
| `packages/atlas` — atlas-viewer | Interface de consulta e índice derivado | caderno-protocol |
| `examples/environmental` | Produtor ambiental explicitamente sintético | Especificação/SDK público |
| Outros produtores | Exportação aditiva e mapeamentos próprios | Contrato público; fora da interface |

Atlas não importa produtor legado, descobre worktrees, executa experimentos, aprova
ciência ou modifica acervos. Fontes e payloads são somente leitura. Índice em memória
é descartável; preferências ficam no navegador. Veja [ADR-0001](docs/architecture/ADR-0001-atlas-protocol-producers-storage.md)
e [contrato A/B](docs/coordination/AB-CONTRACT.md).

## Instalar e abrir a candidata

Requisitos: Python 3.11+ e navegador. Os comandos seguintes partem desta branch.
Crie e ative um ambiente virtual próprio (`python -m venv .venv`), então:

```sh
python -m pip install ./packages/protocol ./packages/atlas
python examples/environmental/export.py demo-ambiental
atlas serve --source demo-ambiental
```

Abra `http://127.0.0.1:8765`. O corpus ambiental é inventado: dois projetos, três
experimentos e quatro execuções com estados completo, parcial, falho e desconhecido.
O exportador recusa sobrescrever diretórios existentes. A instalação pode baixar as
ferramentas públicas de build fixadas; a consulta dos registros funciona offline.

Também é possível usar a fixture versionada sem gerar outra:

```sh
atlas serve --source examples/environmental/sample
atlas inspect examples/environmental/sample
atlas dossier --source examples/environmental/sample
caderno-validate examples/environmental/sample
```

`--source` é repetível (até 16 fontes); IDs são escopados por fonte. O servidor é
somente loopback. A interface não recebe paths de requisições do navegador. `inspect`
retorna código 2 para fonte inválida; `dossier` escreve JSON derivado no stdout.
Para testar o SDK sozinho, instale apenas `./packages/protocol`.

### Demonstração reproduzível instalada

O [roteiro da PoC](docs/poc-reproducible.md) reutiliza o produtor ambiental público
e a instalação limpa já verificada. Ele fornece o comando para construir/instalar
wheels em ambientes vazios, abrir a interface, percorrer os cenários e inspecionar
os recibos. Funciona sem repositório privado. A prova R4 → Caderno → Atlas usa a
mesma interface de snapshots, com exportação e evidências mantidas no produtor.
O harness de browser confere detalhes de todas as execuções, ausências, relações
e pares de métricas compatíveis por fonte, sem nomes de domínio embutidos.

## Contrato de dados candidato

A recomendação é um perfil restrito sobre **RO-Crate 1.3 + Process Run Crate 0.6**.
O grafo JSON-LD é o intercâmbio; o read model da interface é apenas uma projeção.
Consulte [pesquisa](research/protocol-options.md), [ADR-0002](docs/architecture/ADR-0002-protocol-candidate.md)
e [perfil 0.1.0a1](docs/protocol/0.1.0a1.md). A versão exata é obrigatória.

O leitor aceita diretório expandido, documento de metadados e ZIP limitado sem extração.
A extensão `.eln` por si só não certifica conformidade ELN; o perfil ELN estudado usa
RO-Crate 1.2 e está fora do perfil nativo desta candidata. JSON-LD arbitrário não é
aceito: o contexto é catalogado localmente e a forma suportada é explícita.

Metadados têm limite de 2 MiB; payload individual, 8 MiB; payload agregado, 32 MiB;
ZIP comprimido, 64 MiB; arquivo, 4096 membros; grafo, 10000 entidades; profundidade,
20; razão de compressão, 200. URLs externas não são baixadas. Symlinks, traversal,
colisões de nomes, arquivos especiais, JSON duplicado/NaN e versões desconhecidas
são rejeitados ou apresentados com erro conforme o contrato.

Digest verifica igualdade de bytes, não autoria ou data. `UNKNOWN`, `HOLD`, parcial,
falha, dado ausente e origem declarada permanecem visíveis. Autenticidade não foi
verificada. Qualquer resultado sintético continua identificado como tal.

## Verificação reproduzível

```sh
python -m pip install build==1.3.0 setuptools==80.9.0 wheel==0.45.1 jsonschema==4.25.1
python scripts/run_checks.py
python -O scripts/run_checks.py
python scripts/qa/clean_install.py --repo . --work .ci-clean
npm install --no-save playwright@1.62.1
npx playwright install chromium
python scripts/ci/run_browser.py --work .ci-clean
```

O runner de instalação constrói wheels de cópias, instala SDK e interface em ambientes
vazios separados, usa `-I` fora da árvore e verifica ausência de dependências privadas,
reconstrução e bytes intactos. O browser verifica a aplicação instalada, não mock.
O diretório `--work` deve ser novo. A CI cobre Windows/Ubuntu, normal/`-O`, browser
real e o validador de referência no escopo declarado em [conformidade](docs/protocol/conformance.md).

O ambiente de engenharia usa Spec Kit **1.2.3**, instalado com `uv tool` em
ambiente isolado persistente. Scripts Python, templates e as 10 skills oficiais
Codex estão versionados. Consulte a [configuração de um clone novo](docs/engineering/speckit-setup.md)
e o [registro de validação desta instalação](docs/verification/SPECKIT-SETUP01.md).
O [registro do ciclo anterior](specs/001-atlas021-protocol-interface/execution-log.md)
permanece preservado como evidência histórica.

## Limites da candidata

O perfil exige aceite antes de estabilização ou aplicação ao acervo real. O validador
externo disponível cobre base RO-Crate 1.3; o perfil Process Run 0.6 também é verificado
por regras explícitas e revisão, sem alegação de certificação externa inexistente.
A leitura local não certifica segurança de um host adversarial. A avaliação de paridade
com ferramentas legadas e a preservação física permanecem operações distintas.

Nenhuma licença de software do produto foi escolhida. A divulgação desta candidata
não concede licença open source. Referências e materiais públicos redistribuídos
mantêm seus avisos próprios, conforme [avisos de terceiros](THIRD_PARTY_NOTICES.md).
