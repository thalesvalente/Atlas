# Confronto F1 com AP04-POR-v1.0-draft

## Identificação e escopo

- Missão: AP04-F1-LOCAL-LEGACY-SOURCE-INVENTORY-01, 2026-10-30, ambiente LOCAL Windows.
- Registro AP04: 47c94d27aeb7717eebb30804f01cd2cd33507c8a.
- Prompt F1: e140d973fd4cbc4547046f25fd620166662c5004.
- C4: 72d9b94e613a57c82a5afd309796f44b271e2185.
- Código novo: nenhum. Documentos novos: somente o trio sanitizado; SHA/tree são os do commit que os contém, com parent F1 verificado externamente.
- Três subagentes nativos reais: A seleção/integridade, B semântica, C revisão adversarial independente sem autoria. Coordenador único escritor.
- Nenhuma PR nova criada; nenhuma alteração na PR #14.

## Requisitos e resultado

**G1 = F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED.** Uma fonte legada preexistente autorizada contém hierarquia ligável por relações explícitas e uma RF literal com identidade vinculada à fonte/execução. Isso satisfaz a prova de entrada F1; o percurso contínuo da árvore até a RF continua uma lacuna.

As fontes eram privadas locais autorizadas; nenhum conteúdo literal, path, URI, ID privado ou digest de fonte integra este documento. Foram lidos três arquivos, com dois payloads JSON inertes. No payload qualificante há 159 records, cinco tabelas e 152 linhas; somente uma linha foi comparada literalmente para a amostra G1. Os snapshots não foram somados como entidades únicas globais.

## Matriz

A coluna F1 descreve somente a contribuição observada nesta missão. Ela não rebaixa, revalida nem substitui os estados históricos upstream, e a matriz AP04 original não foi editada.

| ID | Baseline literal AP04 | Resultado específico F1 | Evidência e lacuna |
|---|---|---|---|
| PAR-001 | NOT_RECOVERED | NOT_RECOVERED | Hierarquia nativa observável; 858 parent keys resolvidos. UI e cadeia completa de tipos Project/Experiment não demonstradas. F3A e demonstração integrada. |
| PAR-002 | NOT_RECOVERED | PARTIAL_NOT_EQUIVALENT | Uma linha RF original comparada literalmente, com todos os campos requeridos presentes; 152 linhas observadas no payload. Interface, filtros, detalhe e exportação não executados; 28 linhas permanecem não admitidas. |
| PAR-003 | INPUT_AVAILABILITY_UNKNOWN | INPUT_AVAILABILITY_UNKNOWN | Disponibilidade de RNF/RES não inferida de RF, tokens ou nomes. Verificação futura delimitada quando houver fonte declarada. |
| PAR-004 | PARTIAL_NOT_EQUIVALENT | PARTIAL_NOT_EQUIVALENT | A RF amostrada liga explicitamente fonte, registro e execução externa; o Run está isolado no grafo e conserva binding_gap. Caminho contínuo árvore→execução→RF→evidência e navegação não demonstrados. |
| PAR-011 | CONTRACT_DECISION_PENDING | CONTRACT_DECISION_PENDING | Leitura F1 inerte e preservação observadas; nenhum leitor de runtime ou adaptador implementado. F2: contrato e decisão ARC-09 aplicável antes de implementação. |
| PAR-012 | BASELINE_VERIFIED | PARTIAL_NOT_EQUIVALENT | Código/protocolo preservados no escopo observado. CI anterior é referência histórica; nenhum teste de engenharia/CI/browser F1 executado. Validação de código sucessor pertence à fase que o alterar. |
| PAR-013 | ARCHITECTURE_REQUIREMENT_ONLY | CONTRACT_DECISION_PENDING | Capacidade futura preservada; nenhuma implementação ou conformidade HL7/FHIR alegada. Caso de uso, versão e perfis continuam abertos. |
| PAR-015 | BASELINE_VERIFIED_SCOPE | PARTIAL_NOT_EQUIVALENT | SHA-256, tamanho e mtime iguais para as três fontes selecionadas; sete caminhos de prova comparados (seis arquivos com bytes iguais e um permaneceu ausente); negativos mantidos. Acervo global e fontes brutas upstream não medidos. |

Critérios originais preservados:

- PAR-001: Nós projeto/experimento/execução; expandir, selecionar, zoom/pan, minimapa, teclado; hierarquia vs causalidade.
- PAR-002: ID/núcleo/nome/descrição/critério; filtros/detalhe/exportação; prova de linhas reais.
- PAR-003: Mesmo renderer para linhas existentes, sem inventar ausentes.
- PAR-004: Seleção contextual persistida por fonte/snapshot/ID e retorno.
- PAR-011: Leitor externo em fontes existentes, índice efêmero, zero escrita na fonte.
- PAR-012: SDK independente, viewer sem R4, protocolo intacto e CI no novo SHA.
- PAR-013: Extensibilidade por domínio, sem fake FHIR PASS, versão/perfis a definir.
- PAR-015: Bytes originais iguais antes/depois e estados/links sem promoção silenciosa.

PAR-005 a PAR-010 continuam abertas: foram observados itens/grupos, documentos, dossiês e relações, mas suas jornadas de interface, acessibilidade e cobertura global não foram qualificadas. PAR-014/browser não foi executada.

## Preservação, estados e verificações

- Originais: hashes, tamanho e mtime iguais antes/depois para os três arquivos; sete caminhos de prova comparados: seis arquivos com bytes iguais e um caminho permaneceu ausente. Nenhuma alegação de integridade global.
- Sem worktree/clone novo, migração, reorganização, exclusão, importação de código privado ou alteração do produtor/Caderno/instalações.
- ARC-04/05/07/09 preservados: nenhuma mudança de runtime, protocolo, dependência ou arquitetura. ADR-0003 continua PROPOSED_NOT_APPROVED; aprovação de eventual desvio ARC-09 pertence à versão aplicável de F2.
- SDK/viewer e CI Windows/Ubuntu normal/-O: não executados em F1. A qualificação do SHA AP04 anterior serve somente ao pré-requisito de início.
- Browser, árvore clicável, teclado, reflow, screenshots e RF visível na nova UI: NOT_RUN. As verificações reais F1 foram leitura inerte, comparação literal/offsets, resolução de referências e hashes.
- Preservados 22 endpoints null, 75 relações declaradas não resolvidas, 50 colisões de identidade declaradas e 40 grupos de triplas repetidas, com 41 ocorrências extras. Referências string preenchidas e parent keys observados resolvem; nenhuma deduplicação feita.
- Quatro das cinco tabelas não têm record_id resolúvel no conjunto de records. A amostra foi escolhida na tabela com vínculo resolúvel; binding_gap externo permanece.
- As 28 linhas UNADMITTED_NATIVE_RF não têm native_id; não foram apresentadas como RF admitida. Estados históricos e hashes upstream permanecem declarações de origem; fontes brutas não foram abertas.
- Recursos de evidência não foram promovidos automaticamente a produtos, documentos acessíveis ou aprovação científica.
- HTML/JS, scripts de geração, provider e links de recursos não foram executados/abertos; somente o alvo explícito do redirecionamento foi seguido após autorização humana.
- Uma inspeção Git inicial antes da recuperação do prompt excedeu a lista estrita de comandos somente de proveniência, em modo de leitura. A exceção procedural e a tentativa equivalente do revisor estão nos recibos privados; não houve mutação Git ou de fontes nem alteração do plano.
- Revisão independente real: confirmou origem/linha/ponteiros/identidade e o limiar G1; apontou e preservou as lacunas de vínculo e contagem. Revisão de privacidade ocorre antes da publicação do trio.

## Desvios, estado terminal e próximo ato

Objetivo e plano não foram substituídos. Nenhuma funcionalidade foi retirada; não se presumiu paridade pelo recorte; não se atribuiu CI a outro SHA nem conformidade FHIR/RO-Crate a fontes legadas. Não houve implementação que exigisse mudança do plano.

**Estado terminal AP04: PARTIAL_PARITY_WITH_GAPS.** G1 passou somente no escopo de leitura descrito. Nenhum item foi declarado RECOVERED_VERIFIED por esta missão.

Próximo ato mínimo: encaminhar o handoff sanitizado à responsabilidade F2 existente para fechar o contrato de apresentação efêmera, resolver os gaps de identidade sem inferência e obter aprovação versionada ARC-09 se houver desvio. Não iniciar esse trabalho nesta execução.

Merge, release, deploy, promoção, aprovação científica e limpeza física mantêm autorização própria e não foram executados.
