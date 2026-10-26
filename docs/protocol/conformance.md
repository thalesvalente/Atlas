# Evidência de conformidade da candidata

Data: 24/10/2026. Esta evidência refere-se à candidata `0.1.0a1`, com versão e
digests em [profile-manifest.json](profile-manifest.json). A decisão de protocolo
continua PENDING_HUMAN. Não é certificação geral de RO-Crate, Process Run, ELN ou
validade científica. A [pesquisa](../../research/protocol-options.md) registra
fontes, alternativas, licenças, métodos e limites completos.

## Ensaios executados

| Entrada/método | Resultado | Alcance |
|---|---|---|
| Produtor ambiental → RO-Crate 1.3 | 63 PASS, 0 FAIL, 3 SKIP | `roc-validator==0.13.0`, base REQUIRED |
| Protótipo alternativo ELN → RO-Crate 1.2 | 63 PASS, 0 FAIL, 3 SKIP | Mesma ferramenta, alvo de versão explícito |
| ZIP ELN → quatro checks oficiais | 4 PASS | Estrutura, parser `rocrate==0.14.0`, metadados, schema |
| Projeção comparada RO/ELN | Igualdade de 2 projetos, 3 experimentos, 4 runs, 12 relações | Campos selecionados; não identidade RDF/bytes |
| Exemplo oficial Process Run 0.6 preservado | 58 PASS, 5 FAIL, 3 SKIP | Negativo conhecido da base1.3; seis mensagens |
| SDK e JSON Schema | 12 PASS normal, 12 PASS `-O` | Contrato restrito, transporte, IDs, precisão e preservação da origem |

Os recibos estão em [research/evidence](../../research/evidence). Os positivos
foram verificados com payloads locais. Não foi usado `--metadata-only`.

Os três skips da ferramenta externa são visíveis em cada recibo: verificação de
download `cite-as` desabilitada/não aplicável, contexto detached indisponível
para o pacote attached e disponibilidade web desabilitada no teste offline.
Portanto não se atesta disponibilidade de referências remotas. Digests não
autenticam autoria, data histórica ou aprovação científica.

O catálogo desse release do validador oferece Process Run 0.5, enquanto a
proposta usa 0.6 compatível com RO-Crate1.3. Os checks externos executados aqui
são da base; não se afirma validação externa integral de Process Run0.6. O
quinto checker ELN upstream fixa RO-Crate1.1 e não foi usado. Sua verificação de
base foi substituída pelo alvo1.2 explícito, com esse limite registrado.

No exemplo oficial, faltam descrição/data de publicação do root e tipos de
perfil; duas imagens não foram incorporadas e a ferramenta requer `version`
onde o software usa `softwareVersion`. A fonte permanece inalterada. Seu
resultado negativo esperado é diferente de indisponibilidade da ferramenta.

## Reproduzir

Em ambiente isolado com o SDK e dependências de teste fixadas
`jsonschema==4.25.1`, `roc-validator==0.13.0`:

```bash
python research/compare_candidates.py .ci-compare
python research/validate_reference.py examples/environmental/sample .ci-evidence/ro13.json --cache .ci-cache --warm-cache
python research/validate_reference.py .ci-compare/eln-1.2 .ci-evidence/eln12.json --profile ro-crate-1.2 --cache .ci-cache --warm-cache
python research/validate_reference.py examples/upstream/process-run-0.6 .ci-evidence/upstream.json --cache .ci-cache --expect invalid
python -m unittest discover -s packages/protocol/tests -v
python -O -m unittest discover -s packages/protocol/tests -v
```

`--warm-cache` é uma operação explícita sobre URLs públicas dos padrões. A
validação usa sempre `--offline`, `--no-auto-profile` e
`--skip-availability-check`. Sem aquecimento, um cache previamente preparado é
necessário. O SDK do produto não usa rede nem essas bibliotecas de teste.

Para os quatro checks ELN, seguir o checkout/pins e o comando
`research/check_eln_official.py` documentados na pesquisa. Esse harness usa
apenas o protótipo sintético gerado; o parser upstream de teste extrai arquivos
temporários, enquanto o leitor do SDK lê ZIP sem extração.

O comparador retorna erro se os campos divergirem. A ferramenta de referência
retorna erro se o resultado não atender à expectativa explícita; o negativo
oficial exige `--expect invalid`. Os arquivos de recibo não pertencem à fonte e
não devem ser escritos dentro do snapshot verificado.
