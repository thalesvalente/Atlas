# ATLAS021 — pesquisa e prova de protocolo

**Consulta:** 24/10/2026. **Autoria:** A1, frente de protocolo; revisão independente
é registrada pela frente QA. **Decisão proposta:** RO-Crate 1.3 + Process Run 0.6,
perfil mínimo Caderno 0.1.0a1, snapshot offline. **Estado:** PENDING_HUMAN.
Esta é uma escolha compatível com ARC-01–09, não uma mudança arquitetural.

## Recomendação e limite da afirmação

Recomenda-se o modelo de pacote e grafo existente em RO-Crate, restringindo sua
serialização e usando Process Run para atividades computacionais. A proposta
reutiliza tipos, relações e convenções publicadas; as extensões `cp` cobrem
distinções exigidas pela missão que não são estados universais desses padrões.
Não é necessário criar um JSON universal paralelo, um banco obrigatório, um
executor ou um serviço de eventos. O read-model do viewer é derivado.

A recomendação usa versões compatíveis **explicitamente**: Process Run 0.6
estende RO-Crate 1.3. O formato `.eln` pesquisado fixa 1.2. Portanto não se afirma
conformidade simultânea das mesmas declarações com `.eln` e Process Run 0.6.
A evidência de protótipo mostra que a alternativa ELN também conserva os campos
testados mediante extensões, mas exige outro alvo de versão e não oferece a
convenção de execução escolhida sem adaptação. Fontes: [Process Run 0.6][PR],
[ELN fixado][ELN], [perfis RO-Crate][PROFILES].

## Versões, maturidade, licença e implementações verificadas

| Referência | Versão/ref fixada | Papel e maturidade observada | Licença/implementação e limite |
|---|---|---|---|
| RO-Crate | release `1.3.0`, 22/06/2026; commit `22fbd7e098ccd2839c80967e363a2201528a2efe` | Recomendação da comunidade para pacotes e metadados; não é protocolo de transporte/rede | Apache-2.0. Contexto público incorporado com licença e SHA; base validada por roc-validator 0.13.0. [release][ROREL] |
| Process / Workflow / Provenance Run | coleção `0.6.0`, 07/09/2026; commit `3c5b530c3d2784169e461d3273855a6b3a57246e` | Perfis publicados com granularidade crescente; Process não exige workflow formal | Apache-2.0. Process escolhido; os dois outros não são dependências do núcleo. [coleção][WFR] |
| `.eln` | release `1.2+20260923`; commit `2379f5131d543cd8a771a06403de9fb427039a91` | ZIP com pasta raiz única, RO-Crate 1.2; há implementações de import/export em vários ELNs | MIT para especificação/tools. Quatro checks oficiais executados; base 1.2 verificada separadamente. [spec][ELN] |
| PROV-DM / PROV-O | Recomendações W3C, 30/04/2013 | Modelo/ontologia de entidade, atividade, agente e derivação; não empacota acervo | Termos documentais W3C; nenhuma cópia integral incorporada. Reutiliza-se `prov:wasDerivedFrom`; não se afirma conformance PROV completa. [DM][PROVDM], [O][PROVO] |
| OpenLineage | release de software `1.54.0`, 13/10/2026; schema `$id` `https://openlineage.io/spec/2-0-2/OpenLineage.json` | Eventos de Run/Job/Dataset e facets; observabilidade de pipelines em execução | Apache-2.0. Clientes/integradores oficiais; não foi instalado porque não há requisito de transporte de eventos. [modelo][OL], [schema][OLSCHEMA] |
| ISA / ISA-JSON | modelo/serializações 1.0, release `v1.1` de correção; commit `53c474c9cbe04e32ee040eb2cbbe53db0667a384` | Investigation/Study/Assay e processos/amostras; foco experimental rico, com ferramentas existentes | Especificação CC BY-SA 4.0. Nenhuma fonte copiada; adoção integral imporia conceitos desnecessários a produtores de software. [modelo][ISA], [termos][ISATERMS] |
| ISA RO-Crate / ARC | perfil exibido `0.1`, sem permalink anunciado; commit consultado `a320269d17baaf00d845e7f4931209aaa42648df` | Perfil em evolução; LabProcess/Bioschemas ainda inclui termos draft | MIT, DataPLANT. Há mapeamento `arc-to-rocrate`; promessa de reversibilidade não é prova de round-trip para nosso domínio. [perfil][ISARC] |
| JSON Schema | dialeto 2020-12, documentos atualizados em 16/06/2022 | Validação estrutural de JSON; não define um caderno científico | Nenhum texto normativo copiado. Schema do candidato próprio; teste com jsonschema 4.25.1. Termos da especificação permanecem os publicados. [dialeto][JS] |
| SHACL | Recomendação W3C, 20/07/2017 | Restrições de grafos RDF | Não adicionado ao runtime. É usado indiretamente pelo validador externo; será justificável se houver suporte a JSON-LD/RDF arbitrário. [norma][SHACL] |
| Validador de referência | `roc-validator==0.13.0`, release 21/10/2026; commit `8dd0c74dc211c8a0bdd0293d8a8512e6e94deeb6` | Implementação em desenvolvimento, suporta RO-Crate 1.3 | Apache-2.0. Seu perfil Process Run disponível ainda é 0.5; não equivale à validação externa de Process Run 0.6. [fonte][VALIDATOR] |

Nenhuma linha acima transfere licença de terceiros ao código próprio do Atlas.
A escolha de licença de distribuição do produto continua pendente. Os únicos
conteúdos públicos incorporados são o contexto RO-Crate e metadados do exemplo
oficial, acompanhados de atribuição/licença e sem fontes de repositório privado.

## Cobertura dos requisitos pelo candidato recomendado

As classificações são uma análise de adequação, não selos emitidos pelos padrões.
`NATIVE` significa conceito representável diretamente; `PROFILE_CONSTRAINT`
indica convenção mais estrita; `EXTENSION_REQUIRED` indica vocabulário `cp` ou
semântica adicional; `UNSUPPORTED` significa que o protocolo não resolve a questão.

| Necessidade concreta | Classificação | Representação/limite e fonte |
|---|---|---|
| Múltiplos projetos | EXTENSION_REQUIRED | Dataset + `cp:Project`; não fixar um domínio. [perfis][PROFILES] |
| Experimentos ligados ao projeto | EXTENSION_REQUIRED | Dataset + `cp:Experiment`, `isPartOf`. [RO][RO] |
| Execuções e ferramentas | NATIVE | CreateAction, instrument, SoftwareApplication. [PR][PR] |
| Atividades/agentes | NATIVE | CreateAction, Person/Organization; identidade declarada. [PR][PR], [PROV][PROVDM] |
| Métricas e unidades | PROFILE_CONSTRAINT | PropertyValue, propertyID, value, unitText; unidade sempre explícita. [PR][PR] |
| Tipo, precisão e ausência | EXTENSION_REQUIRED | `cp:valueType`, `cp:precision`, `cp:missingReason`; null não é zero |
| Parâmetros | EXTENSION_REQUIRED | PropertyValue nativo ligado por `cp:parameters`, preservado separadamente dos resultados |
| Artefatos e evidências | NATIVE | File/Dataset, object/result e metadados; papel probatório não é atestado. [RO][RO] |
| Origem e derivação | PROFILE_CONSTRAINT | Relações com alvos declarados; `prov:wasDerivedFrom`, grafo sem ciclos. [PROVO][PROVO] |
| Resultado falho | NATIVE | FailedActionStatus. [PR][PR] |
| Resultado parcial/desconhecido | EXTENSION_REQUIRED | cp preserva estado exato; enum schema.org exige projeção conservadora documentada |
| Revisão/ciência separada da execução | EXTENSION_REQUIRED | `cp:reviewStatus`; nenhuma aprovação concedida pelo SDK |
| Data observada versus declarada | EXTENSION_REQUIRED | `cp:timestampOrigin`; tempo desconhecido permanece ausente |
| Arquivos grandes referenciados | NATIVE | HTTP(S) externo; disponibilidade nunca inferida nem buscada automaticamente. [RO][RO] |
| Transporte offline | PROFILE_CONSTRAINT | Snapshot local/ZIP limitado, contexto local, zero rede no runtime |
| Mutabilidade e publicação de versão | PROFILE_CONSTRAINT | Novo snapshot; origem e bytes anteriores preservados. [proveniência][PROVENANCE] |
| Atualização incremental | PROFILE_CONSTRAINT | Publicar snapshot sucessor e reconstruir índice; streaming/event sourcing não implementados |
| Identidade/deduplicação | PROFILE_CONSTRAINT | IDs namespaced, duplicação/alias rejeitados; sem merge semântico silencioso |
| Compatibilidade de versão | PROFILE_CONSTRAINT | Só contexto/perfis explícitos reconhecidos; sem downgrade |
| Recuperação sem interface | NATIVE | Metadata e payloads permanecem acessíveis como pacote; SDK independente |
| Validação independente | PROFILE_CONSTRAINT | Base RO1.3 por ferramenta externa + schema + verificações de grafo e QA; não há certificação 0.6 externa neste release |
| Segundo produtor | PROFILE_CONSTRAINT | Exportador ambiental usa contrato público e não importa adaptador privado |
| Entrada não confiável | PROFILE_CONSTRAINT | Leitor limitado, referências seguras, sem execução HTML/script e sem extração ZIP |
| Autenticidade histórica | UNSUPPORTED | Digest mede bytes; não autentica autor/data. Exige evidência independente |
| Permissões reais do host | UNSUPPORTED | Formato não confere acesso nem qualifica sandbox |
| Autorização para migração/remoção | UNSUPPORTED | Operações continuam sujeitas a decisão humana/ownership |

## Alternativas avaliadas

**RO-Crate simples sem perfil de execução:** oferece o pacote, mas deixa autores
e leitores reinventarem ligações de software e run. A restrição de Process Run
reduz essa variação sem exigir uma linguagem de workflow. Workflow Run e
Provenance Run ficam opcionais para produtores que já possuam workflows e
granularidade por etapa; exigir esses perfis agora aumentaria o custo de entrada.

**ELN como contrato principal:** é uma alternativa de intercâmbio real e o
protótipo funcionou. Seu alvo de RO-Crate é 1.2 e o pacote requer uma pasta raiz.
Ele não elimina as extensões de revisão, incerteza e métricas tipadas; adotá-lo
como núcleo obrigaria manter a convenção de execução sob outra combinação de
versões. Recomenda-se futura ponte explícita, não uma troca automática da base.

**OpenLineage como núcleo:** seu Job/Run/Dataset é adequado a eventos operacionais
e relações em pipelines. Para nossa primeira entrega, faltam requisitos de bus,
backend e streaming que justifiquem essa complexidade; projetos/experimentos,
curadoria e pacote offline precisariam de convenções/facets. Pode alimentar um
produtor futuro, sem se tornar o armazenamento ou a interface inteira.

**ISA/ISA RO-Crate como núcleo:** é útil para estudos com amostras, fatores e
ensaios. O custo de impor esse modelo a qualquer produtor de engenharia é maior
que o benefício demonstrado. A integração de um produtor ISA permanece possível
por extensão ou mapeamento; não se pressupõe que a hierarquia de todos os
experimentos seja Investigation/Study/Assay.

**PROV, JSON Schema e SHACL:** têm papéis complementares, não substituem um pacote
de pesquisa. A forma JSON-LD restrita permite JSON Schema e checagens diretas de
grafo sem a complexidade de inferência RDF no runtime. Validar apenas o schema
seria insuficiente para referência pendente, colisão, ciclo ou metadado adulterado.

## Prova curta com finalistas — execução real

`research/compare_candidates.py OUTPUT` gera o mesmo corpus sintético nos dois
alvos: RO-Crate 1.3/Process 0.6/Caderno e `.eln` 1.2. O protótipo ELN muda contexto
e descritor para 1.2, adiciona os metadados ELN e **remove** a declaração de
conformidade dos perfis dependentes de 1.3. As extensões preservam os fatos; não
se confunde essa equivalência selecionada com igualdade dos grafos completos.

| Ensaio | Resultado observado | Limite |
|---|---|---|
| Projeção dos finalistas | Mesmos 2 projetos, 3 experimentos, 4 runs e 12 relações | Igualdade desses campos; não igualdade RDF ou digest |
| RO-Crate 1.3 próprio | `roc-validator 0.13.0`: 63 checks PASS, 0 FAIL, 3 SKIP | Base REQUIRED; offline; não Process0.6 externo |
| Protótipo ELN base1.2 | `roc-validator 0.13.0`: 63 PASS, 0 FAIL, 3 SKIP | Mesmos limites de disponibilidade |
| ELN checker upstream | 4/4 PASS: estrutura ZIP, parser rocrate0.14.0, metadados obrigatórios, schema | Código `tests/checks.py` do commit ELN fixado |
| Exemplo oficial Process0.6 sem alterações | Base1.3: 58 PASS, 5 FAIL, 3 SKIP; seis mensagens | Fonte serve como negativo documentado, não foi reparada |
| SDK/JSON Schema/round-trip | 11/11 PASS normal e 11/11 PASS `-O` | Inclui recusa de precisão decimal perdida; complementado por QA independente |

Os três skips externos são explícitos: `cite-as` indisponível/não aplicável;
modo detached não aplicável ao pacote attached; disponibilidade web não
verificada no ensaio offline. Os arquivos locais do fixture positivo foram
verificados. `--metadata-only` não é usado no recibo final.

O quinto teste do checker ELN upstream fixa RO-Crate **1.1** e contém adaptações
históricas por produtor. Não foi executado para fingir prova 1.2: em seu lugar,
rodou-se a ferramenta atual explicitamente contra 1.2, offline. Esse desvio de
tooling está registrado e não é uma certificação integral do ecossistema ELN.

O exemplo oficial mantém seus bytes e autores. Faltam `description` e
`datePublished` do root e o tipo Profile; as imagens não foram incorporadas, e o
validador requer `version` do software onde o exemplo usa `softwareVersion`.
A recomendação não depende de declarar esse exemplo conforme. Sua rejeição
também demonstra que o leitor não fabrica valores para aceitar entrada conhecida.

As primeiras rodadas encontraram falhas reais no candidato: tipos dos perfis,
metadados de software e um payload local intencionalmente ausente. Corrigiram-se
as fixtures positivas; o caso de ausência ficou nas negativas. A revisão do
texto normativo também removeu enums de status inventados e substituiu a URI
provisória do perfil por uma página de descrição efetivamente publicável.

### Reproduzir as verificações

Instalar em ambiente de teste isolado `jsonschema==4.25.1`,
`roc-validator==0.13.0` e o SDK candidato. Nenhuma dessas bibliotecas externas
é requisito do runtime do SDK.

```bash
python research/compare_candidates.py .ci-compare
python research/validate_reference.py examples/environmental/sample .ci-evidence/ro13.json --cache .ci-cache --warm-cache
python research/validate_reference.py .ci-compare/eln-1.2 .ci-evidence/eln12.json --profile ro-crate-1.2 --cache .ci-cache --warm-cache
python research/validate_reference.py examples/upstream/process-run-0.6 .ci-evidence/upstream.json --cache .ci-cache --expect invalid
python -m unittest discover -s packages/protocol/tests -v
python -O -m unittest discover -s packages/protocol/tests -v
```

`--warm-cache` busca apenas contextos/páginas públicas do padrão; a validação
continua sempre `--offline`. Sem essa opção, exige cache já preparado. A
comparação falha com exit não zero se houver divergência nos campos. Recibos
sanitizados estão em `research/evidence`; os paths internos foram excluídos.

Para repetir os quatro checks oficiais ELN, instalar adicionalmente
`rocrate==0.14.0` e obter o checkout público
`TheELNConsortium/TheELNFileFormat` no commit
`2379f5131d543cd8a771a06403de9fb427039a91`. O harness verifica SHA-256 de
`tests/checks.py` e `tests/schema.json` antes de importar o código. Execute
`python research/check_eln_official.py CAMINHO_DO_CHECKOUT .ci-compare/synthetic.eln .ci-evidence/eln-official.json`.
Esse ensaio usa apenas o ZIP sintético gerado pelo comparador. O parser de teste
upstream extrai temporariamente o arquivo; não faz parte do leitor do produto.

## Lacunas e critérios para decisão humana

A escolha envolve aceitar um perfil restrito e suas extensões, a projeção
conservadora de PARTIAL/UNKNOWN e o backend inicial de snapshots. O custo atual
é um SDK Python sem dependências de runtime, um viewer separado, produtores
independentes e tooling de teste adicional. O perfil não inclui streaming,
assinatura, autenticação histórica, conversão universal de unidades ou migração
automática de dados reais. Expansões futuras devem partir de requisitos medidos.

**Não congelar nem aplicar a dados reais antes do aceite explícito de ADR-0002,
vinculado ao digest da descrição 0.1.0a1.** CI/review demonstram propriedades
técnicas, não substituem essa decisão nem autorizam remoção de fontes.

[RO]: https://www.researchobject.org/ro-crate/specification/1.3/
[ROREL]: https://github.com/ResearchObject/ro-crate/releases/tag/1.3.0
[PR]: https://www.researchobject.org/workflow-run-crate/profiles/0.6/process_run_crate/
[WFR]: https://github.com/ResearchObject/workflow-run-crate/releases/tag/0.6.0
[ELN]: https://github.com/TheELNConsortium/TheELNFileFormat/blob/2379f5131d543cd8a771a06403de9fb427039a91/SPECIFICATION.md
[PROFILES]: https://www.researchobject.org/ro-crate/specification/1.3/profiles.html
[PROVENANCE]: https://www.researchobject.org/ro-crate/specification/1.3/provenance.html
[PROVDM]: https://www.w3.org/TR/2013/REC-prov-dm-20130430/
[PROVO]: https://www.w3.org/TR/2013/REC-prov-o-20130430/
[OL]: https://openlineage.io/docs/1.54.0/spec/object-model/
[OLSCHEMA]: https://github.com/OpenLineage/OpenLineage/blob/1.54.0/spec/OpenLineage.json
[ISA]: https://isa-specs.readthedocs.io/en/latest/isamodel.html
[ISATERMS]: https://github.com/ISA-tools/isa-specs/blob/53c474c9cbe04e32ee040eb2cbbe53db0667a384/source/index.rst
[ISARC]: https://nfdi4plants.github.io/arc-ro-crate-profile/profiles/isa_ro_crate/
[JS]: https://json-schema.org/draft/2020-12
[SHACL]: https://www.w3.org/TR/2017/REC-shacl-20170720/
[VALIDATOR]: https://github.com/crs4/rocrate-validator/tree/0.13.0
