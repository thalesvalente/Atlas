# Rastreabilidade — AP04-POR-v1.0-draft

Pacote AP04-F2-v0.2; desenho documental, não implementação. As decisões e a matriz upstream são preservadas por blob; esta avaliação não substitui estados históricos.

## Confronto D-001–D-020

| Decisão | Tratamento nesta proposta |
|---|---|
| D-001 | Interface/contrato/armazenamento separados; descriptor derivado não é autoridade |
| D-002 | Sem r4.* ou RF/RNF/RES obrigatórios no núcleo; SDK independente |
| D-003 | Validade, bytes, origem, autenticação e ciência em eixos separados |
| D-004 | Aquisição e compatibilidade do host em processo externo; sem poderes de manutenção |
| D-005 | CA-01 continua referência provisória; publicação não promove Atlas nem retira fonte |
| D-006 | ARC09_APPROVAL_REQUIRED, ADR v0.2, revisão independente e decisão por SHA antes de implementar |
| D-007 | Aceite da ADR-0002 somente direção RO-Crate1.3/ProcessRun0.6/Caderno0.1.0a1; sem release |
| D-008 | C0/C4 não representam paridade total; lacunas legadas mantidas |
| D-009 | Evidência C4 é histórica e não é CI, browser ou RF literal desta F2 |
| D-010 | Nenhuma retenção física/limpeza autorizada; cache próprio não concede G9 |
| D-011 | BIM/IFC/IDS/SHACL ficam no roadmap, sem alegação de implementação |
| D-012 | Continua campanha AP04 a partir de C4 e F1; não reinicia |
| D-013 | Contratos futuros de árvore e tabela literal, produtos/documentos/linhagem preservados |
| D-014 | Sem conversão persistida em massa, reorganização ou documentação histórica nova |
| D-015 | Leitura externa explícita, temporária e inerte; origem intacta |
| D-016 | HL7/FHIR futuro por domínio, sem conformidade por rótulo |
| D-017 | Evolução R4 pertence a F6, não executada |
| D-018 | Branch F2 existente; nenhum clone/worktree novo |
| D-019 | Este confronto inclui matriz, gates, evidência e pendências |
| D-020 | Sem apagar/mover experimentos ou históricos para melhorar UI |

## Matriz antes/depois

A coluna «antes» é o literal da matriz AP04. Nenhum item recebe RECOVERED_VERIFIED nesta F2. Código/dado novo: nenhum; apenas desenho e exemplos sintéticos originais.

| PAR | Antes literal AP04 | Critério preservado / contribuição documental F2 | Depois nesta missão / lacuna |
|---|---|---|---|
| PAR-001 | NOT_RECOVERED | Nós projeto/experimento/execução; expandir, selecionar, zoom/pan, minimapa, teclado; hierarquia vs causalidade. Contrato F3A | NOT_RECOVERED; browser e caminho completo não provados |
| PAR-002 | NOT_RECOVERED | ID/núcleo/nome/descrição/critério; filtros/detalhe/exportação; prova de linhas reais. Contrato F3B | NOT_RECOVERED; F1 comparou uma RF, UI não executada |
| PAR-003 | INPUT_AVAILABILITY_UNKNOWN | Mesmo renderer para linhas existentes, sem inventar ausentes | INPUT_AVAILABILITY_UNKNOWN; RNF/RES não comprovadas |
| PAR-004 | PARTIAL_NOT_EQUIVALENT | Seleção contextual persistida por fonte/snapshot/ID e retorno | PARTIAL_NOT_EQUIVALENT; binding_gap e Run isolado mantidos |
| PAR-005 | NOT_RECOVERED | Catálogo navegável ligado a execução sem deduzir produto por MIME | NOT_RECOVERED; papel/vínculo exigidos |
| PAR-006 | PARTIAL_NOT_EQUIVALENT | Metadados, disponibilidade, links verificáveis e consulta segura | PARTIAL_NOT_EQUIVALENT; URI inerte e disponibilidade separada |
| PAR-007 | PARTIAL_NOT_EQUIVALENT | Grafo navegável com relações declaradas e menções neutras | PARTIAL_NOT_EQUIVALENT; tipos/direções/ocorrências preservados |
| PAR-008 | PARTIAL_NOT_EQUIVALENT | Datas declaradas/UNKNOWN e revisões independentes; sem fabricar evento | PARTIAL_NOT_EQUIVALENT; observado separado de científico |
| PAR-009 | PARTIAL_NOT_EQUIVALENT | Contagens base/seleção/carga/visível com denominadores ou UNKNOWN | PARTIAL_NOT_EQUIVALENT; GLOBAL_UNPROVEN/UNKNOWN_UPSTREAM |
| PAR-010 | NOT_RECOVERED | Observações originais, vínculo, nenhum comando de limpeza | NOT_RECOVERED; armazenamento somente consultivo futuro |
| PAR-011 | CONTRACT_DECISION_PENDING | Leitor externo em fontes existentes, índice efêmero, zero escrita na fonte | CONTRACT_DECISION_PENDING; ARC09_APPROVAL_REQUIRED |
| PAR-012 | BASELINE_VERIFIED | SDK independente, viewer sem R4, protocolo intacto e CI no novo SHA | PARTIAL_NOT_EQUIVALENT; CI C4 histórica, regressão futura G5 |
| PAR-013 | ARCHITECTURE_REQUIREMENT_ONLY | Extensibilidade por domínio, sem fake FHIR PASS, versão/perfis a definir | CONTRACT_DECISION_PENDING; nenhuma implementação |
| PAR-014 | OBSERVED_PARTIAL | Árvore e uma tabela RF real, testes com SHA e recibos locais privados | PARTIAL_NOT_EQUIVALENT; F5/browser NOT_RUN |
| PAR-015 | BASELINE_VERIFIED_SCOPE | Bytes originais iguais antes/depois e estados/links sem promoção silenciosa | PARTIAL_NOT_EQUIVALENT; preservação F1 é evidência escopada anterior |

Os estados «Depois nesta missão» avaliam apenas a contribuição documental F2. PARTIAL_NOT_EQUIVALENT em PAR-012/014/015 não rebaixa, revalida nem substitui os estados históricos literais da coluna «Antes». Nenhuma baseline foi revalidada por esta F2. O avanço novo é prontidão documental para decisão humana, não recuperação de funcionalidade. PAR-005–010 continuam abertos; P0 não foi retirado.

## Contratos de consumo das fases futuras — não executadas

F3A: componentes genéricos consomem nós/ocorrências/famílias e relações tipadas do modelo proposto por fixture sintética. Árvore SVG interativa com expandir/recolher, seleção contextual e retorno, zoom/pan/minimapa, teclado (Tab, setas, Home/End, Enter/Escape), foco visível, nomes acessíveis e reflow. Órfãos em grupo visual «sem pai resolvido» rotulado como agrupamento UI, nunca nó científico. Run externo isolado permanece isolado. Pertencimento organizacional, linhagem dirigida e menções neutras têm legendas/estilos e ações distintos.

F3B: tabela preserva cabeçalhos, ordem original/índice de ocorrência, ID nativo quando presente, núcleo/módulo, nome, descrição, critérios e categoria MISSING. Filtro/ordenação não mudam os dados; detalhe e exportação preservam literal/tipo/unidade/precisão/ausência e escopo. RF não admitida fica separada, sem ID fabricado. RNF/RES somente quando declaradas e disponíveis; nenhuma inferência por nome/MIME.

F4: integrador futuro liga árvore/tabela/detalhe por fonte+snapshot+ocorrência e somente vínculos explícitos. Gaps exibem destino não resolvido, sem criar caminho contínuo. Entrada opcional via File API depende de decisão ARC-09 versão/SHA, F1 e F3A/B conforme plano. Catalog e SDK não recebem descriptor. Esta documentação não inicia F4.

F5: QA/browser Windows com fonte privada explicitamente autorizada e recibos privados por SHA compara linha literal real, navegação, ausências e imutabilidade. Publica somente síntese sanitizada. Sem fonte privada no CHAT, screenshot público, ou reuso da CI C4 como evidência nova.

## Contraprovas com oracle FUTURO

Todos os casos abaixo: NOT_RUN nesta F2; especificação de testes, sem criação de testes de produto. G4 valida fronteira/derivação/imutabilidade; G5 valida integração e não regressão; G2/G3/G6 são adicionais quando indicados.

| Caso | Entrada adversa ou lacuna | Oracle futuro verificável | Vínculo |
|---|---|---|---|
| N01 | Mesmo native_id em fontes diferentes | Duas identidades e seleções distintas; nunca resolve na fonte vizinha | PAR-004/015,G4/G5 |
| N02 | Mesmo ID na mesma fonte com colisão declarada | Ocorrências separadas, colisão visível; nenhuma deduplicação | PAR-007/015,G4/G5 |
| N03 | nav_id derivado usado como native_id | Rejeição semântica de promoção; native_id original permanece null | PAR-002/011/015,G4/G5 |
| N04 | 22 endpoints nulos | Cada ocorrência retida com endpoint null; UI não fabrica alvo | PAR-007/015,G4/G5 |
| N05 | 75 relações declaradas não resolvidas | Contagens e strings declaradas retidas; navegação não atravessa gap | PAR-004/007,G4/G5 |
| N06 | 50 colisões e 40 grupos repetidos,41 excedentes | Todos representáveis; grupos e ocorrências não fundidos; contagem confere por escopo | PAR-007/015,G4/G5 |
| N07 | Quatro tabelas sem record_id resolúvel | Tabelas permanecem visíveis como não vinculadas; nenhum record inventado | PAR-002/004,G4/G5 |
| N08 | 28 UNADMITTED_NATIVE_RF com native_id null | Nenhuma admissão/ID científico; contagem e ausência preservadas | PAR-002/015,G4/G5 |
| N09 | RF com Run externo isolado e binding_gap | Só vínculo declarado exposto; nenhum ancestral/Project/Experiment artificial | PAR-001/004,G4/G5 |
| N10 | Categoria ausente/null/string vazia | Distinções registradas; marcador MISSING sem preencher por heurística | PAR-002/015,G4/G5 |
| N11 | String numérica,inteiro>2^53,decimal/unidade/precisão | Token/tipo/ordem preservados; sem round ou comparação de unidades diferentes | PAR-002/012/015,G4/G5 |
| N12 | HTML/JS/event handler dentro de célula/título | Texto inerte,zero execução/DOM injetado/rede; export literal separado do CSV seguro | PAR-002/006/015,G4/G5 |
| N13 | CSV =,+,-,@ com controles/quotes/newlines | CSV seguro não executa fórmula; JSON literal retém valor original e transformação informada | PAR-002/015,G4/G5 |
| N14 | Traversal,symlink,reparse,TOCTOU,UNC/ADS | Leitura recusada antes de escapar allowlist; identidade final verificada; fonte intacta | PAR-011/015,G4/G5 |
| N15 | URI file:/javascript:/data:/remota maliciosa | Nenhuma abertura/download; metadado permanece inerte | PAR-006/015,G4/G5 |
| N16 | Fonte muda após leitura | Leitura externa detecta/rejeita corrida; browser declara somente snapshot observado e exige nova importação | PAR-004/011/015,G4/G5 |
| N17 | Descriptor inválido,versão desconhecida,quota excedida | Rejeição atômica com razão; C4 continua utilizável e sem subconjunto silencioso | PAR-011/012,G4/G5 |
| N18 | Reimport/reindex/nova sessão/TTL e link antigo | Link rejeitado como stale; contexto não resolve em outra sessão/snapshot | PAR-004/015,G4/G5 |
| N19 | UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN ou denominador0/unknown | Sem total global/percentual0/0; seleção,carga,visível/unidade explícitos | PAR-009/015,G4/G5 |
| N20 | Hash/validação verde com ciência UNKNOWN/HOLD | Nunca vira autenticidade/aceite científico; eixos independentes | PAR-015,G4/G5 |
| N21 | Nome RF/RNF/RES/FHIR ou MIME arbitrário | Não infere domínio/admissão/produto/conformidade FHIR | PAR-003/005/013,G4/G5 |
| N22 | C4 sem sidecar e sem R4;SDK sem Atlas | Instala/roda C4 e valida protocolo em isolamento;CI sucessora por SHA | PAR-012,G4/G5 |
| N23 | Navegação e RF em browser real | Árvore interativa,teclado,retorno,literal/filtro/detalhe/exportação no SHA integrado; não SVG estático | PAR-001/002/004/014,G4/G5+G2/G3/G6 |
| N24 | O2 rotulado conforme sem todos validadores | Rejeitar rótulo Caderno/RO-Crate/ProcessRun; relatório de perdas e provas relevantes obrigatório | PAR-012/015,G4/G5 |

## Gates e checklist F2

G0 mantém documentação Draft; G1 permanece resultado escopado F1, não nova leitura.
G2/G3/G5/G6/G7 não são executados/qualificados por esta missão.
G4 continua ARCHITECTURAL_DECISION_PENDING; G8/G9 continuam não autorizados.
Nenhuma ordem F0–F6, critério PAR/G0–G9 ou proteção mudou; PLAN-DEVIATION-REQUEST não é necessário para esta candidata documental. Se uma implementação posterior exigir mudar o plano, apresentar solicitação antes de agir.

| Checklist | Evidência no pacote / limite |
|---|---|
| F2-01 | INPUT-SHAS, Git Data API commit/tree/parent e inputs por blob |
| F2-02/03 | ARCHITECTURE-OPTIONS e ADR candidata; reader003 exclusivo confrontado |
| F2-04/05 | Contrato com schema/exemplos sintéticos e nós órfãos |
| F2-06/07/08 | IDENTITY-AND-LOSS-POLICY, invariantes e negativos F1 |
| F2-09/10 | SECURITY-AND-INTEROPERABILITY e oracles, sem teste real de produto |
| F2-11/12 | PROPOSED_NOT_APPROVED,ARC09_APPROVAL_REQUIRED,plano intacto |
| F2-13 | N01–N24 são futuros NOT_RUN |
| F2-14 | INDEPENDENT-REVIEW identifica revisão nativa e escopo por SHA |
| F2-15 | HANDOFF e MANIFEST; Git final verificado externamente |
| F2-16 | Diff somente novos documentos F2; sem F3–F6 |
| F2-17 | DECISION-REQUEST com pergunta única, versão e SHA técnico |
