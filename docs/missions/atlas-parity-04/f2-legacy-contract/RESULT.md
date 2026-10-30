# Resultado AP04-F2 — pacote AP04-F2-v0.2

Estado deste candidato: F2_REVIEW_PENDING. Estado terminal será registrado por commit após revisão independente real. Não é aprovação de ADR, G4, paridade ou implementação.

Missão AP04-F2-CHAT-LEGACY-COMPAT-CONTRACT-01, 2026-10-30.
Owner Git: coordenador /root, único writer. Branch exclusiva existente: docs/atlas-parity04-f2-legacy-contract-20261030.
Plano: AP04-POR-v1.0-draft, SHA 47c94d27aeb7717eebb30804f01cd2cd33507c8a.
Prompt: bc2e10e9a783227294daa4100ccaeb384d0dddd0.
F1: a237f446e54927eeeda8ed5e8e9daa83ee09dcb7; C4: 72d9b94e613a57c82a5afd309796f44b271e2185.
INPUT-SHAS.json contém tree/parent/blobs e links. SHA/tree de saída são os do commit que contém este documento, verificáveis externamente, sem tentar embutir o próprio hash.

## PLAN → EXECUTE → REVIEW

PLAN: ler integralmente missão e inputs públicos fixados; reconciliar quatro commits/tree/parent e branch; preservar ownership exclusivo F2. Leitura preliminar de metadados/AGENTS no checkout foi tentada antes da recuperação do prompt; não foi usada como fonte de evidência nem houve escrita. Todo conteúdo de pesquisa/produção documental usa GitHub público por SHA, sem fontes/drives privados. Não se alega escolha de esforço de raciocínio do operador, que não foi observada.

EXECUTE: A (/root/architecture_a) analisa arquitetura/alternativas; B (/root/model_b) propõe contrato/modelo/identidade; coordenador integra textos e escreve exclusivamente os novos documentos F2 por Git Data API. A/B não escrevem filesystem/Git. C (/root/review_c) é revisor nativo real independente, somente leitura e sem autoria dos deltas. Não há simulação de execução ou aprovação.

REVIEW: revisão do conteúdo publicado por SHA, manifesto e diff; findings serão corrigidos documentalmente e submetidos a nova leitura. Evidência e escopo estão em INDEPENDENT-REVIEW.md. O SHA terminal também deve receber fechamento externo de revisão, sem ciclo de auto-hash.

## Resultado técnico proposto

Uma candidata concreta: O1 externo com consumo O3 segregado no browser por File API. Leitor fora do runtime, arquivo descriptor privado temporário, parser neutro e estado só na aba. Catalog, server atual, SDK e Caderno não recebem novo formato nesta F2. A entrada adicional na UI contradiz a exclusividade do reader003 e exige ARC09_APPROVAL_REQUIRED.

Entregues alternativas O1–O5, contrato descriptor 0.2.0 com schema e exemplos originais sintéticos, política de identidade/perdas, segurança/padrões, ADR-0003 v0.2 PROPOSED_NOT_APPROVED, matriz D/PAR/gates, oracles futuros e pergunta humana versionada. Nenhum plano, contrato atual, produto, protocolo, runtime, R4 ou fase F3–F6 foi alterado/iniciado.

## Confronto obrigatório e limites da evidência

PARITY-TRACEABILITY.md confronta todas D-001–D-020 e PAR-001–015 com antes/depois e lacunas, sem editar matriz histórica. Estado AP04: CONTRACT_DECISION_PENDING. Nenhum item RECOVERED_VERIFIED por F2.

F1_G1_SOURCE_AND_RF_READ_PASS_SCOPED é evidência anterior de três fontes autorizadas, uma RF literal e disponibilidade selecionada. Contagens qualificantes:159 records; cinco tabelas39/85/28/0/0=152linhas;2911nós;1595arestas;858parent keys explícitos resolvidos;162product_items;10product_groups;80resource_documents;24dossier_assessments;4dossier_packages. Lacunas:4tabelas sem record_id resolúvel;28UNADMITTED_NATIVE_RF com native_id=null;Run isolado/binding_gap;22endpoints null;75relações não resolvidas;50colisões;40grupos repetidos/41excedentes. Não somar snapshots sobrepostos.

UNKNOWN_UPSTREAM e GLOBAL_UNPROVEN; bruto upstream não relido e RNF/RES não comprovadas. Nenhum conteúdo literal, path, ID ou hash privado foi importado. Hash comprova bytes, não autoria/ciência. F1 não demonstrou interface ou caminho contínuo.

## Verificações desta missão e testes futuros

Executadas leituras públicas por SHA e reconciliação de commit/tree/parent; os 22 inputs tiveram comprimento UTF-8 e Git blob SHA-1 recalculados em memória, todos idênticos aos objetos Git. Revisão documental/sintaxe dos artefatos, manifesto e diff por paths/blobs são registrados conforme conclusão abaixo e no handoff. Foram parseados os três blocos JSON do contrato (schema e dois exemplos sintéticos) e executadas checagens documentais em memória dos keywords usados e de unicidade, referências/contexto, ordinais/larguras, índices de campos, contagens e TTL: zero erros. Isto é checagem própria limitada, não validador formal Draft2020-12, teste de produto ou comparação com fonte F1. Validação formal JSON Schema permanece NOT_RUN. Detalhes no handoff.
Testes de engenharia, Windows/Ubuntu normal/-O, coleção de testes, CI F2, browser real, fonte privada, RF na UI, teclado/reflow/screenshots e implementação de padrões: NOT_RUN nesta produção documental. Eventual CI automática será identificada separadamente pelo SHA/run, sem reaproveitar evidência antiga nem corrigir proteções fora de ownership.

N01–N24 especificam oracles FUTUROS, não execuções. G4 permanece decisão arquitetural pendente. HL7/FHIR conserva capacidade futura por domínio; nenhuma versão/perfil/IG ou conformidade foi adotada.

## Preservação e próximo ato

Nenhum clone/worktree, migração/reorganização/exclusão, experimento/provider, código privado, fonte privada, R4 ou instalação foi acionado por esta F2. Imutabilidade privada é evidência F1, não foi revalidada aqui. Diff desta missão limitado a novos documentos F2; históricos, plano, reader003, protocolo, workflows e testes preservados por blob.

Não há necessidade de alterar ordem F0–F6, PAR/G0–G9 ou proteções para produzir esta documentação. Nenhum PLAN-DEVIATION-REQUEST necessário neste escopo. Uma necessidade posterior deve ser submetida antes de implementação.

Menor próximo ato: decisão humana objetiva em DECISION-REQUEST.md vinculada à versão/SHA revisada. Aprovação arquitetural, eventual autorização de fase, merge/release/deploy/promoção/ciência/limpeza têm gates separados e continuam não concedidos.
