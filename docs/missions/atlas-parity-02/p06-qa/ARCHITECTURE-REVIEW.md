# ATLAS-PARITY-02-P06 — revisão de compatibilidade e arquitetura

Data: 27/10/2026 (America/Fortaleza). Emissor: subagente nativo de compatibilidade, com responsabilidade exclusiva sobre este documento. Reasoning efetivo: UNVERIFIED, sem telemetria disponível.

## Escopo e identidade da revisão

Revisão estática por leitura do conector GitHub, exclusivamente em `thalesvalente/Atlas`.

- Baseline: `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5`.
- Árvore: `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59`.
- Candidata histórica testada com a mesma árvore: `e985ea3124b7a3cd241ee2dbc88b5ad50688373c`.
- O tree recursivo consultado retornou `truncated=false`; não contém `docs/missions/atlas-parity-02` nem implementações P01/P02/P03 identificadas como tal.
- Não houve shell, acesso ao host, instalação, navegador, teste de runtime, produtor, worktree, branch, commit, ref ou PR por este subagente. A única escrita é o blob deste documento, para integração exclusiva pelo coordenador.

Esta revisão da baseline não substitui a revisão independente do delta final. O coordenador deve fixar SHA/árvore da composição; outro revisor deve avaliar os bytes resultantes antes de encerrar o gate de revisão.

## Contratos lidos e interpretação atual

Foram lidos AGENTS.md, constituição, ADR-0001/0002, AB-CONTRACT-1.0, política de publicação, especificações/contratos e convergências pertinentes das features 001, 002 e 003. Também foram lidos os pyprojects, catálogo, servidor, CLI, modelo de leitura, auditoria arquitetural e testes dessa auditoria.

ARC-01–09 continuam vinculantes. A direção é produtor → protocolo interoperável → armazenamento substituível → Atlas genérico. O Atlas consulta fontes declaradas, compara e apresenta estados e representações derivadas. Aquisição, interpretação de formatos nativos e normalização permanecem no produtor. O núcleo público não recebe módulos privados, leitor legado, descoberta de acervo, executor científico ou poderes de migração/retirada.

O aceite da ADR-0002 **já foi recebido como direção de estabilização**. O [recibo posterior da PR #5](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421) e a [mensagem do merge](https://github.com/thalesvalente/Atlas/commit/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5) registram a decisão vinculada à ADR-0002 v1.0 presente em `e985ea3124b7a3cd241ee2dbc88b5ad50688373c`: RO-Crate 1.3.0 + Process Run Crate 0.6 + Caderno 0.1.0a1. Os estados PENDING_HUMAN nos arquivos/recibos anteriores descrevem o momento anterior a essa decisão; não se solicita o mesmo aceite outra vez. Release estável, ciência, promoção canônica, dados privados e retirada continuam dimensões separadas.

Perfil: Caderno `0.1.0a1`; SHA-256 do documento de perfil declarado no manifesto: `76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e`. Os hashes de manifesto não foram recalculados por esta revisão estática. Não se propõe alteração de perfil, schema, contexto, ontologia ou versão.

## Compatibilidade disponível para C0

O contrato atual já fornece a fronteira necessária para uma candidata C0 que inclua P02+P06. A ausência de P01 ou de componentes novos P03 não constitui, por si só, bloqueio de arquitetura. É necessário demonstrar que a candidata concreta cabe nesta fronteira:

| Fronteira | Evidência observada na baseline | Condição para a composição |
|---|---|---|
| Dependências | `atlas-viewer` depende somente de `caderno-protocol==0.1.0a1`; o protocolo declara `dependencies=[]` | SDK continua instalável sem viewer/produtor; viewer continua sem produtor |
| Fontes | CLI recebe `--source` explícito; catálogo limita a 16 fontes e mantém estado em memória | Nenhuma descoberta automática, leitura nativa ou novo caminho de acervo |
| HTTP | GET fixo para assets, catálogo e dossiê; servidor ligado a 127.0.0.1 | Conservar loopback, Host/Origin, CSP e ausência de downloads remotos |
| Reconstrução | POST `/api/reindex` aceita apenas objeto vazio, sobre fontes previamente declaradas | Não aceitar paths novos nem escrever nas fontes |
| Identidade | Política `SOURCE_ID_AND_DECLARED_ID`; colisões expostas; modelo por pacote | Seleção/detalhe/comparação não cruzam IDs de fontes distintas |
| Semântica | Estado técnico, revisão, disponibilidade, digest e autenticação separados | UNKNOWN/HOLD/ausências não viram sucesso, zero ou aceite |
| Referências | `mentions` vira `related_references` neutra; primeiro alvo único; resolução no pacote | Não converter menção em input/output/linhagem; texto/URIs inertes |
| Precisão | `display_value` preserva texto numérico na apresentação; dossiê mantém bytes do servidor | Não reencodar dossiê no browser nem perder inteiro maior que 2^53 |
| Autoridade | Índice/dossiê são derivados reconstruíveis; fontes são a autoridade dos registros | Nada de novo Caderno interno ou aprovação científica pela interface |
| Empacotamento | Assets HTML/CSS/JS incluídos no wheel | Provar instalação isolada dos bytes finais, fora do checkout |

A auditoria arquitetural é útil, mas limitada: cobre imports estáticos, imports dinâmicos literais, dependências de distribuição e certas capacidades de execução no viewer. Não prova comportamento de código dinâmico arbitrário nem segurança integral de host. Deve continuar acompanhada da instalação independente e dos testes de runtime aplicáveis.

Não foi encontrada contradição arquitetural material nos arquivos da baseline lidos. Não há candidata P02 identificada por SHA nesta baseline; por isso esta conclusão não concede PASS à composição futura.

## Evidência histórica reutilizável

As APIs Git de ambos os commits foram consultadas nesta revisão: `c2d00fb...` e `e985ea...` retornam a mesma árvore `5c65d3f...`. A igualdade da árvore permite reutilizar evidência histórica dos mesmos bytes dentro de seu escopo declarado. Não cria execução nova no SHA de merge nem no host.

As APIs dos runs [produto 40246678115](https://github.com/thalesvalente/Atlas/actions/runs/40246678115) e [Spec Kit 40246678113](https://github.com/thalesvalente/Atlas/actions/runs/40246678113) foram reconsultadas: ambos `completed/success`, `head_sha=e985ea3124b7a3cd241ee2dbc88b5ad50688373c`.

O [recibo CLOSE01](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6405183504) atribui àqueles bytes:

- Produto: seis jobs, incluindo quatro células Windows/Ubuntu normal/-O; 86 testes por célula, zero skips.
- SDK e consumidor instalados em ambientes independentes, sem R4; bytes sintéticos preservados e índice reconstruído.
- Chromium de engenharia/CI: 19 checks normais, 23 adversariais e 22 de referências; desktop, 390 px, teclado/foco e ampliação CSS de 200%.
- Duas fontes com IDs repetidos, referências duplicadas, estados vazios, navegação interna, precisão e zero erros de página/tráfego externo.
- CLI Spec Kit 1.2.3, helpers e auditoria na CI; revisão Codex e revisão nativa daquela candidata.

Os números e inspeções visuais acima são atribuições ao recibo histórico; esta revisão não reproduziu seus testes nem abriu suas capturas. LOCAL-REAL01 permanece evidência anterior de outra frente. Nada aqui representa atualização, execução ou navegador atual do host. Aceite de protocolo e integração pública histórica também não demonstram paridade funcional completa com CA-01.

## Matriz de aceitação para a frente P06

| Dimensão | Estado sustentado agora | Evidência necessária para um PASS novo |
|---|---|---|
| Pacote | Prova histórica reutilizável da baseline; nova instalação NOT_RUN por este subagente | Wheels/manifesto e imports isolados correspondentes ao SHA/árvore final; executar novamente quando o delta afetar pacote/runtime |
| Componente | Componentes da baseline têm cobertura histórica; componentes P03 não inventariados | Testes materiais dos componentes realmente entregues, com origem e SHA; P03 não é requisito artificial para C0 |
| Composição | Contrato atual é suficiente em princípio; candidata P02 concreta não recebida nesta revisão | Tupla de SHAs, merge-base/árvore/delta, exercício das jornadas aplicáveis e revisão independente dos bytes compostos |
| CI | Runs históricos SUCCESS reconsultados no HEAD exato; CI P06 nova NOT_RUN | Jobs, logs e artefatos do HEAD final quando disparados; verificar checkout efetivo, não somente merge ref ou cor verde |
| Browser de engenharia | Histórico sintético real disponível; nova sessão NOT_RUN | Browser real sobre consumidor instalado e composição final; fluxo, identidade, teclado, largura/zoom e ausência de tráfego/erros conforme o delta |
| Host do operador/P05 | NOT_RUN por esta revisão; recibos antigos não são acesso atual | Frente/ambiente capaz e autorizado, tela real e recibo com identidade da instalação/fontes/processo; startup ou HTTP 200 isolados não bastam |

Se o delta final for somente documental, testes de runtime antigos podem ser reaproveitados por identidade dos arquivos, com a limitação explicitada. O novo delta documental e sua revisão devem ser atribuídos ao novo SHA. Não converter esse reaproveitamento em declaração de UI nova, composição P02 ou paridade completa.

## Dependências e lacunas por frente

- **P01:** contratos documentais novos não estão na baseline. Não bloqueiam C0 quando o contrato vigente já comporta o comportamento entregue. Qualquer mudança incompatível de protocolo exige decisão própria.
- **P02:** shell, catálogo, servidor e empacotamento podem aproveitar o contrato atual. Falta um candidato novo identificado por SHA/árvore; não há bytes de P02 a avaliar nesta revisão.
- **P03:** componentes novos isolados não foram identificados. Prova isolada de componente, quando existir, não demonstra a composição; sua ausência não invalida automaticamente C0.
- **P04:** coorte privada offline permanece fora desta revisão e fora do repositório público. Resultado sanitizado não dispensa o recibo privado nem autoriza publicação de dados.
- **P05:** operação local e browser no host exigem frente capaz; nenhum recibo da PR #5 comprova execução P05 atual.
- **P06:** este relatório fornece baseline e critérios. Testes adicionais, CI e revisão final pertencem aos bytes da candidata concreta.

O inventário da coordenação informa A/B/D completos ausentes e C disponível somente como resumo C0. Sem os bytes dos estudos e seus handoffs, não é possível conferir hashes informados, 12 jornadas completas, equivalência integral ou uma escolha comparativa entre A/B/C/D. Isso limita alegações de paridade/seleção, mas não impede documentação, inspeção estática e preparação de QA sobre o contrato e o produto já disponíveis.

## Testes materiais para o menor próximo incremento

A seleção deve seguir o delta, evitando repetir suites sem causa. Quando P02 ou uma composição concreta estiver disponível:

1. Instalar o wheel final fora do checkout; provar SDK sem UI/produtor e viewer sem produtor. Verificar assets, import paths e hashes pertinentes.
2. Abrir duas fontes sintéticas com IDs iguais e nomes/estados distintos; filtrar, abrir detalhe e navegar por referência mantendo fonte+ID. Repetir após reconstrução e recarregamento.
3. Comparar métricas por identidade/tipo/unidade; cobrir ausência, tipos/unidades incompatíveis e inteiro maior que 2^53 sem conversão implícita.
4. Preservar UNKNOWN/HOLD, referências neutras e estados de disponibilidade; manter pacote inválido diagnosticado ao lado de pacote saudável.
5. Percorrer jornadas que a candidata declara, em browser real: filtros/limpeza, todas as execuções, detalhe, comparação, timeline/linhagem, referências e dossiê; teclado/foco, 390 px e ampliação prevista. Vincular o relatório à instalação e ao SHA final.
6. Conferir hashes das fontes antes/depois de consulta, dossiê e reindex. Validar que o servidor não aceita paths, fontes novas ou escrita no acervo.
7. Verificar o workflow e o checkout efetivamente usado. Separar CI, revisão, browser de engenharia e host, incluindo NOT_RUN explícito onde faltar execução.

Não há autorização derivada deste parecer para merge, release, deploy, promoção, alteração de licença, transferência privada, nova aquisição, execução de produtor/modelo, migração ou retirada física.

## Fontes fixadas

- [Árvore da baseline](https://github.com/thalesvalente/Atlas/tree/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5)
- [AGENTS.md](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/AGENTS.md)
- [Constituição](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/.specify/memory/constitution.md)
- [ADR-0001](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/architecture/ADR-0001-atlas-protocol-producers-storage.md), [ADR-0002](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/architecture/ADR-0002-protocol-candidate.md)
- [Contrato 001](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/001-atlas021-protocol-interface/contracts/interface.md), [contrato 002](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/002-atlas021-poc-r4/contracts/demo.md), [contrato 003](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/specs/003-producer-selective-preview/contracts/reader.md)
- [AB-CONTRACT-1.0](https://github.com/thalesvalente/Atlas/blob/c2d00fb137cac1d62d6b7cb045ddbe055355a4c5/docs/coordination/AB-CONTRACT.md)
