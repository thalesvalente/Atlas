# Atlas — disposições técnicas 18/18

Baseline: `8f8fe01c3041361aa2607194d66af6a640d834ad`; branch de integração: `fix/atlas-convergence18-20261108`. Integrador e writer único: P00 (`/root`).

**18/18 classificadas; 84 requisitos principais e 240 itens de crosswalk individualizados.** Os 324 registros do CSV distinguem requisitos, jornadas, exemplos, artefatos e oráculos; não representam 324 testes novos. A disposição agregada da PR não apaga os estados diferentes de seus subrequisitos.

A qualificação da candidata depende dos recibos reais do SHA publicado. A decisão técnica de não incorporar uma infraestrutura histórica não afirma equivalência, corrige seu histórico ou concede aprovação humana.

## Matriz nominal

| PR | Owner | Disposição | Fundamento e destino |
|---|---|---|---|
| [#6](https://github.com/thalesvalente/Atlas/pull/6) | P01 | `SUPERSEDED_BY_DESIGN` | P06 qualificava uma composição histórica. Sete oráculos semânticos passam sem alteração em main; instalação, HTTP e browser têm suites atuais. Não portar a antiga preservação de seleção B após mudança em A, substituída pela política posterior de invalidação do snapshot. |
| [#7](https://github.com/thalesvalente/Atlas/pull/7) | P01 | `SUPERSEDED_BY_DESIGN` | A tabela P03 foi preservada; a integração aprovada é Native View. Metadados genéricos e cards p03-candidate/1 eram demonstradores isolados, não obrigação de implantar nova UI arbitrária. |
| [#8](https://github.com/thalesvalente/Atlas/pull/8) | P02 | `RETAIN_AND_IMPLEMENT` | Reter a finalidade de invalidar estado dependente de fonte/snapshot na superfície /. Há contraprovas atuais reais. Portar apenas o vínculo e a ordenação segura de consultas, preservando contratos e sem reintroduzir todo o router candidato. |
| [#9](https://github.com/thalesvalente/Atlas/pull/9) | P01 | `RETAIN_AND_IMPLEMENT` | Reutilizar análise e 28 jornadas sem promover candidatos a requisitos. Recuperar apenas comportamento atual demonstrável: identidade/snapshot/preferências via P02; rótulos indexação/observação; publicação do snapshot com origem declarada; orientação ADR aceita como direção e main consolidada. Não criar generic detail nem semântica científica persistida. |
| [#10](https://github.com/thalesvalente/Atlas/pull/10) | P01 | `SUPERSEDED_BY_DESIGN` | Os 28 adicionais C2 qualificavam harness P03 isolado, 47 testes exatos e inatividade na app. A composição NativeView tem instalação/HTTP/browser próprios. Preservar os artefatos, substituir a infraestrutura por objetivos atuais identificados e não fingir equivalência integral de gates. |
| [#11](https://github.com/thalesvalente/Atlas/pull/11) | P02 | `RETAIN_AND_IMPLEMENT` | A composição herdada não deve ser portada em bloco. O comportamento global de snapshot é necessário na / atual e tem RED reproduzido; a correção é compartilhada com #8. |
| [#12](https://github.com/thalesvalente/Atlas/pull/12) | P01 | `SUPERSEDED_BY_DESIGN` | C3 é gate documental preso aos pins técnico/documental históricos e às worksheets. Não transplantar/repinar seu coletor sobre outra árvore. Provas úteis do leitor e arquitetura são reutilizadas ou reexecutadas com escopo nominal. |
| [#13](https://github.com/thalesvalente/Atlas/pull/13) | P02 | `SUPERSEDED_BY_DESIGN` | Metadados tipados são cumpridos nas superfícies atuais com composição diversa. P03 preservado é uma reutilização real; o seletor arbitrário de propriedades e generic entity detail candidatos não são promessas do contrato001. A finalidade de isolamento da apresentação foi testada diretamente. As dependências C1 seguem #8/#11. |
| [#14](https://github.com/thalesvalente/Atlas/pull/14) | P01 | `SUPERSEDED_BY_DESIGN` | O plano AP04 é sucedido por features004/007 e avaliação por capacidade. PAR005–010 têm cada uma destino/prova/contraprova. A decisão não concede retirada, migração nem equivalência privada não observada. |
| [#15](https://github.com/thalesvalente/Atlas/pull/15) | P01 | `SUPERSEDED_BY_DESIGN` | Substituição somente da via de apresentação ativa por NativeView Files conforme feature004. Descriptor0.2.0 continua APPROVED_SCOPED no recibo humano exato; não é revogado, implementado por equivalência ou reescrito. |
| [#16](https://github.com/thalesvalente/Atlas/pull/16) | P02 | `SUPERSEDED_BY_DESIGN` | A incorporação do consumidor gráfico efêmero isolado foi substituída pela via NativeView Files004/005/007. Descriptor0.2.0 permanece aprovado em seu escopo opcional, preservado no histórico; não se alega equivalência de APIs, aquisição, nonce ou TTL. |
| [#17](https://github.com/thalesvalente/Atlas/pull/17) | P02 | `SUPERSEDED_BY_DESIGN` | A rota isolada de tabelas descriptor0.2.0 foi substituída pela leitura NativeView e P03/visualização editorial. Tipagem, estados e exportações atuais foram testados; as diferenças de TTL, quotas e escopo de exportação são explícitas e não revogam descriptor0.2.0. |
| [#18](https://github.com/thalesvalente/Atlas/pull/18) | P03 | `RETAIN_AND_IMPLEMENT` | Retain pre-import source-origin boundary in current external adapter: two reproducible baseline counterexamples. Literal preservation/readonly boundaries are mapped to current implementation; HTML parser/O1/descriptor transport are not imported wholesale. |
| [#19](https://github.com/thalesvalente/Atlas/pull/19) | P01 | `SUPERSEDED_BY_DESIGN` | Adendo de dez documentos O1/O3 sucedido na composição da aplicação pelo NativeView. N01–N24 têm destino individual: invariantes comuns mantidos, exclusivos O1/TTL não atribuídos à via nova. Bug atual de origem pré-execução é tratado via #18/P03. |
| [#20](https://github.com/thalesvalente/Atlas/pull/20) | P03 | `REJECTED_WITH_REASON` | Reject direct incorporation of the O1 synthetic host-isolation subsystem into current producer-trusting Native View architecture. Each OS increment remains retrievable by immutable SHA; no equivalent-hard-budget or production qualification is claimed. Preserve historical succession failure. |
| [#21](https://github.com/thalesvalente/Atlas/pull/21) | P01 | `DEFERRED_HUMAN_DECISION` | Gate normativo humano real: aprovar ou rejeitar proposta0.2.1 vinculada aos cinco blobs d5bdc86. Preservar os onze documentos e14 oráculos; nenhum NativeView/CI K decide isso. |
| [#22](https://github.com/thalesvalente/Atlas/pull/22) | P03 | `REJECTED_WITH_REASON` | Reject importing/reusing the demonstrably inconsistent L0 receipt validator as a gate for the current product, where it has no path or consumer. Historical defects stay recorded, not fixed by declaration; original private L0 witness remains unaccepted. |
| [#31](https://github.com/thalesvalente/Atlas/pull/31) | P01 | `REJECTED_WITH_REASON` | Rejeitar porte do gate genealógico F2/K para main: ele qualifica objeto documental exato, não execuçãoNativeView. Preservar guard terminal,binding,36K+32F2; não repinar,enfraquecer ou atribuir negativos à CI atual. Decisão sobre infraestrutura não rejeita nem aprova0.2.1. |

## Leitura dos estados

- `EQUIVALENT_IN_MAIN`: somente a capacidade expressamente delimitada, com fonte atual e teste indicados. Nenhuma PR inteira recebeu esse rótulo por aparência da interface.
- `SUPERSEDED_BY_DESIGN`: objetivo tratado pela composição aprovada atual, com diferenças de contrato, quotas, ciclo de vida ou exportação registradas e contraprova explícita.
- `RETAIN_AND_IMPLEMENT`: obrigação retida com correção pontual do produto; #8/#11 compartilham o mesmo reparo, sem duplicar implementação.
- `REJECTED_WITH_REASON`: incorporação recusada por critério de produto/segurança; o código e o resultado histórico permanecem recuperáveis.
- `DEFERRED_HUMAN_DECISION`: autoridade humana necessária para o objeto exato; não conta como PASS funcional.

## Reparos retidos e rastreabilidade

| Reparo | Origem | Spec / tarefa | Código / regressão |
|---|---|---|---|
| Snapshot e preferências escopadas | #8/#11 e dependência herdada #13 | 001 FR-007/019/020, C18-T002 | `app.js`; `test_protocol_snapshot.mjs`; `browser.mjs` |
| Ordenação GET/POST sem perder rebuild | #8/#11 | 001 FR-007/020, C18-T003 | fila em `app.js`, ordens opostas e falhas em testes Node |
| Indexação, consulta e publicação declarada; orientação vigente | #9 J09/J10/J27 | 001 FR-005/012/017, C18-T004 | `app.js`, `README.md`, browser instalado |
| Guarda de origem antes de executar produtor | #18 P03-18-01 | 004 FR-001/006, C18-T001; ARC-07 | `tools/export_native_notebook.py`; testes sintéticos normal/-O |

O novo contexto da rota `/` inclui geração, instante de indexação e fontes/digests ordenados. GET de verificação não muda esse contexto. Rebuild invalida o contexto mesmo com bytes iguais, coerente com a rota `/notebook`; essa política substitui explicitamente a conservação histórica de contexto no rebuild byte-idêntico. Query/status permanecem independentes; projeto/experimento só são restaurados no mesmo contexto.

A guarda do adaptador valida a cadeia física inteira antes de inicializadores, verifica specs/cache, carrega exatamente o spec validado e restitui `sys.path`. Os inicializadores e dependências escolhidos continuam confiáveis: não se declara sandbox, bloqueio de todo I/O ou proteção contra TOCTOU adversarial.

P03-18-05 é equivalente somente quanto à separação produtor/viewer e à recusa de caminhos HTTP arbitrários. O guard de produção O1 não foi transplantado; sua ativação permanece em P03-20-05.

## Autoridade, histórico e limites

A [ADR-0002 v1.0](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421) recebeu aceite como direção de estabilização no SHA exato daquele ato. O [descriptor externo 0.2.0](https://github.com/thalesvalente/Atlas/pull/15#issuecomment-6539419419) recebeu aprovação opcional delimitada. Native View Files é outra interface: não implementa nem revoga o descriptor por equivalência.

A proposta 0.2.1/ARC-09 permanece congelada em `d5bdc86ef68cad2f5d503945ca788c3a74df4839`; os cinco blobs foram conferidos. Os controles K/F2 e os 37 jobs históricos da #31 não aprovam esse objeto.

O [aceite restrito da #39](https://github.com/thalesvalente/Atlas/pull/39#issuecomment-6715128638) permanece quitado no seu escopo. Paridade privada OLD/NEW/zoom, aquisição produtiva O1 e testemunho L0 não foram produzidos nem dispensados nesta missão. Os dois defeitos L0 da #22 são históricos e não existem em um consumidor atual na main; o validador inseguro não foi incorporado.

Os 19 pareceres anteriores foram revalidados e reutilizados sem refazer 1.016 entradas/542 paths. #30 mantém sua justificativa histórica. A [PR #40](https://github.com/thalesvalente/Atlas/pull/40#issuecomment-6726430940) continua Draft separada em `7ac3e76d12f6d2e59d235458dc122d85850cf499`: 24 disposições reutilizadas e cinco arquivos intactos; nenhum merge ou nova exclusão.

## Evidências e revisão

- [CSV completo](ATLAS-CONVERGENCE-DECISIONS-18.csv) — 84 requisitos + 240 itens detalhados.
- [Requisitos e fontes estruturados](REQUIREMENTS-84.json).
- Análises congeladas: [P01](evidence/P01/P01-MATRIX.json), [P02](evidence/P02/P02-MATRIX.json), [P03](evidence/P03/P03-MATRIX.json).
- Revisões não autoras: [P01→P02](evidence/P01/P01-REVIEW-P02.json), [P02→P03](evidence/P02/P02-REVIEW-P03.json), [P03→P01](evidence/P03/P03-REVIEW-P01.json).
- [DAG e gates](ATLAS-CONVERGENCE-DAG.md), [portabilidade](ATLAS-CONVERGENCE-PORTABILITY.md) e [handoff](ATLAS-CONVERGENCE-HANDOFF.md).

Recibos O1 descrevem a baseline e permanecem congelados, inclusive seus findings OPEN então. Sua resolução posterior é comprovada pelos testes/reviews O3 e pelo recibo terminal O4/O5, sem reescrever as evidências RED.
