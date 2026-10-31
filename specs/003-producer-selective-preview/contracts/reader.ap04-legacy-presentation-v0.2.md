# Contrato 003 — adendo AP04 de apresentação legada v0.2

Owner/writer: coordenador C0 /root. Missão AP04-F4-C0-READER003-CONTRACT-CHAT-01. Data: 2026-10-31.
Natureza: sucessor documental delimitado; nenhuma implementação por C0. Custódia de cada blob, SHA/tree/parent e parecer: [pacote C0](../../../docs/missions/atlas-parity-04/f4-c0-reader003/INPUT-SHAS.json), MANIFEST.sha256, OUTPUT-OBJECTS.json e envelope Git do commit que contém este arquivo.

## 1. Autoridade e precedência delimitada

Fundamento: ARC-01–09 e ADR-0001, AP04-POR-v1.0-draft, ADR-0003 v0.2 e descriptor atlas-legacy-presentation 0.2.0 no pacote técnico [c3ea1e82938fd61cc5a22fee973352715a5bb527](https://github.com/thalesvalente/Atlas/commit/c3ea1e82938fd61cc5a22fee973352715a5bb527), tree 986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c. A [decisão humana 6539419419](https://github.com/thalesvalente/Atlas/pull/15#issuecomment-6539419419) é APPROVED_SCOPED para essa versão/SHA. Cabeçalhos históricos PROPOSED_NOT_APPROVED são anteriores à decisão e ficam intactos.

Este adendo sucede EXCLUSIVAMENTE na superfície opcional O3 o alcance global das cláusulas de reader.md que limitam a entrada do Atlas a snapshots Caderno e proíbem acrescentar caminho de leitura/schema/perfil. A exceção autoriza descrever somente a seleção manual por File API do descriptor já aprovado, produzido por O1 externo. Reconhece-se expressamente uma entrada adicional de apresentação no viewer; não se presume compatibilidade automática por manter Catalog fora.

Na via científica existente, reader.md conserva precedência integral: reader, endpoint, SDK, Catalog e API C4 continuam Caderno-exclusivos. A exceção NÃO cria caminho de acesso à fonte original, endpoint HTTP, novo schema/perfil Caderno ou poderes do host no viewer. Nenhum outro contrato congelado é substituído. Fora de O3, ou diante de entrada ambígua/inválida, recusar; não fazer fallback entre vias.

A publicação/revisão C0 cumpre a dependência documental anterior à integração. Não instala painel, não inicia integração C3, não qualifica aquisição local, G4, G5, G6 ou ciência. Ampliação de superfície, formato, quotas ou plano exige justificativa, alternativas, riscos, diff, revisão e aprovação aplicável ANTES da implementação. Se exigir editar reader.md histórico para precedência válida, parar com F4_C0_ARCHITECTURAL_DECISION_REQUIRED.

## 2. Duas vias independentes

| Via | Entrada e percurso | Estado e autoridade |
|---|---|---|
| Científica existente | snapshot Caderno 0.1.0a1 → SDK → Catalog → API C4 → interface Caderno | Exclusiva no leitor/endpoint existente; comportamento e validação preservados |
| Apresentação legada opcional | O1 LOCAL externo explicitamente invocado → projeção preexistente autorizada somente leitura → JSON privado atlas-legacy-presentation 0.2.0 → seleção explícita de um arquivo por File API → painel segregado O3 | LEGACY_DERIVED; RAM da aba; TTL; nunca fonte científica ou ingestão no SDK/Catalog |

O1 fica fora da distribuição/runtime Atlas, sem r4.*, código privado, leitor Windows suspenso ou reconstrução dele. Aquisição não é transformação: autorização para uma não concede a outra. Só arquivo(s)/root exatos previamente autorizados; autorização F1 não se transfere a F4-L1. O viewer não invoca O1 nem lê caminhos, diretórios, drives ou fontes originais por JavaScript. Não há conexão automática ao processo externo, ingestão no Catalog, load_package/to_read_model, reconciliação automática ou identidade compartilhada entre as vias. Caderno deve funcionar sem descriptor/O1/R4; protocolo e SDK funcionam sem UI.

## 3. Descriptor fixado e validação atômica

Reutilizar SEM ALTERAÇÃO o schema Draft 2020-12 fechado do [EPHEMERAL-PRESENTATION-CONTRACT.md](../../../docs/missions/atlas-parity-04/f2-legacy-contract/EPHEMERAL-PRESENTATION-CONTRACT.md), blob 25d79a11171c157bd3c7e0f98d1449a78237fd9c no pacote aprovado. Este adendo não cria schema novo. Exigir format=atlas-legacy-presentation, version=0.2.0, authority=LEGACY_DERIVED e todos os campos/objetos fechados, além das 11 invariantes semânticas da fonte normativa.

Validar localmente shape e invariantes antes de tornar qualquer dataset utilizável. PASS recebido não substitui validação do consumidor. Rejeitar propriedades extras, schema/versão desconhecidos ou remotos, UTF-8 inválido, chaves duplicadas antes de sobrescrita pelo parser, NaN/Infinity, truncamento e excesso de quota. NOT_RUN/FAIL não disponibiliza snapshot como validado. Falha é atômica, com motivo explícito, sem subconjunto anunciado completo; elimina estado/tokens legados e conserva a via Caderno.

| Limite herdado | Máximo |
|---|---|
| O1: arquivos allowlisted/entrada | 3; 64 MiB por arquivo; 192 MiB agregados; sem recursão/ZIP/extração |
| Descriptor UTF-8/profundidade | 32 MiB / 20 |
| Nós/relações/assets | 10.000 / 100.000 ocorrências / 10.000 |
| Tabelas/colunas/linhas | 128 / 256 por tabela / 100.000 linhas agregadas |
| Literal de célula/lexema | 64 KiB / 128 KiB |
| Leitura/validação e memória | 30 s por abertura; 256 MiB impostos na fronteira real do host |
| TTL desde generated_at | ≤3600 s, sem renovação por acesso |

maxLength conta caracteres; bytes, profundidade, linhas agregadas, contagens, tempo, contexto e referências exigem controles extras antes/durante parsing. Falta de imposição/prova dos hard budgets significa HARD_BUDGET_UNVERIFIED e recusa de execução/qualificação G4, nunca alegação de limite duro por documentação ou observação casual no browser. C3 não pode anunciar heap/tempo garantidos sem imposição medida. Quota nunca autoriza truncamento.

## 4. Invariantes de identidade, literalidade e navegação

1. Cada descriptor representa uma fonte/snapshot e um payload qualificante. source_id/snapshot_id são identidade técnica; bytes_sha256 mede bytes exatos, sem canonização/concatenação implícita, sem autenticar autoria. Instância real exige digest observado e recibo privado de escopo/política. Campos sem evidência ficam UNKNOWN; formatos declarados não são conformidade.
2. Token operacional inclui importação/sessão + fonte + snapshot + ocorrência. Navigation IDs únicos são DERIVED_FOR_PRESENTATION; native_id exige prova literal. Nunca derivar native_id de ordinal, path, hash, título ou navigation ID. Mesmo ID em outra fonte/snapshot não resolve vínculo.
3. Colisões mantêm ocorrências e localizadores. NULL_ENDPOINT conserva declared_id e target null; UNRESOLVED/COLLISION não escolhem alvo. RESOLVED exige original único no contexto e prova do vínculo, nunca stub. EXTERNAL_DECLARED pode navegar visualmente a stub, sem resolução científica.
4. Run original observado mantém SOURCE_ENTITY e ID comprovado, inclusive isolado/binding_gap. Stub DECLARED_EXTERNAL_REFERENCE só representa Run não carregado, native_id=null. Não substituir Run observado por stub; não criar Project, Experiment, ancestrais ou arestas para fabricar percurso contínuo árvore→Run→RF.
5. Quatro tabelas F1 sem record_id resolúvel continuam consultáveis e não vinculadas. As 28 RF UNADMITTED_NATIVE_RF continuam native_id=null; completar campos/navigation ID não concede admissão. RNF/RES permanecem desconhecidas até prova explícita. Categoria MISSING, null, propriedade ausente, string vazia e zero são distintos.
6. Conservar ordem/ordinais originais contíguos, headers/chaves e uma célula por coluna; índices RF apontam células originais. Preservar tipos/literais/lexemas/unidades/precisão e unmapped_fields. Inteiros >2^53/decimais usam texto tipado; string numérica continua string. Sem arredondamento, conversão ou preenchimento silencioso.
7. Direção/tipo/endpoints e prova de relações permanecem declarados. Parent key/pertencimento não vira causalidade. Órfãos, ciclos e repetidos mantêm ocorrências; agrupamento UI não cria pai científico. File permanece File; papel de produto e vínculo exigem declaração.
8. Contagens têm unidade/escopo, selecionado/carregado/filtrado/visível; entidades originais e stubs separadas. Não somar snapshots sobrepostos. Negativos F1 sobrepõem-se, não são partição aditiva. UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN e global_total/global_percentage=null; nunca inferir denominador ou 0/0.
9. observed_at ≤ generated_at < expires_at; expires_at-generated_at ≤3600 s. Datas técnicas não substituem scientific_at desconhecido. Browser mostra OBSERVED_SNAPSHOT_ONLY e fonte não reobservada, sem afirmar freshness contínua.
10. Reimportação, reindexação do contexto, nova sessão/snapshot, troca, erro, expiração ou dispose invalidam tokens/links anteriores; não remapear stale por native ID ou título. Expiração bloqueia navegação/exportação e limpa estado legado. Atualizar exige nova observação externa autorizada e importação explícita.
11. Apresentar LEGACY_DERIVED, validade de shape/semântica, integridade, origem declarada, autenticidade e revisão científica separadamente; preservar UNKNOWN/HOLD. Digest comparado, conformidade sintática ou apresentação válida não implicam autenticidade, ciência aprovada ou paridade.

As contagens sanitizadas F1 são referência histórica selecionada, não nova medição C0 nem total upstream: 159 records; cinco tabelas 39/85/28/0/0, 152 linhas; uma RF comparada literalmente; 2.911 nós/1.595 relações/858 parent keys resolvidos; 22 endpoints null, 75 relações não resolvidas, 50 colisões, 40 grupos repetidos/41 excedentes. Não publicar literais/IDs/paths/digests privados nem generalizar a comparação de uma RF.

## 5. Segurança, ciclo de vida e rollback

Sem upload ao servidor, endpoint adicional, rede externa, telemetria, execução HTML/JS/URI de fonte, eval/innerHTML/iframe, imports dinâmicos de conteúdo, leitura de paths por JS, descoberta de drives ou reconciliação entre vias. Textos/URIs são inertes; DOM via textContent e SVG próprio. Sem localStorage/sessionStorage/IndexedDB/service worker ou persistência do descriptor no viewer. O arquivo selecionado continua privado e não é coletado pelo servidor.

Assets JS/CSS futuros são nomes fixos exatos sob o ownership C3, nunca rota genérica. Preservar CSP/Origin/Host/no-store/nosniff e ausência de CORS; não relaxar connect-src ou política para carregar fonte. O1 sem rede, escrita somente no scratch privado próprio, fora do acervo/repos, allowlist/identidade/handle/TOCTOU verificados. Falta de garantia bloqueia aquisição; nenhuma ACL/sandbox pode ser alterada por conveniência.

JSON tipado é a exportação canônica fiel; CSV para planilha neutraliza fórmulas/controles e faz quoting, com transformação declarada sem substituir literais originais. Exportar somente snapshot/seleção autorizados e ainda válidos.

Rollback futuro: desativar painel, invalidar tokens, descartar RAM e apenas cache próprio identificado pelo processo externo dono. Não tocar Caderno, Catalog, SDK, fontes, R4, originais ou experimentos; não conceder G9/limpeza. Crash pode deixar resíduo, sem promessa de apagamento físico. Em C0 o rollback é apenas retirar o adendo de uma futura composição, conservando história Git.

## 6. Padrões e provas posteriores

Caderno 0.1.0a1, RO-Crate 1.3 e Process Run 0.6 mantêm schema/contexto/pins/versões e direção aceita. Descriptor não recebe rótulo conforme desses padrões. HL7/FHIR continua capacidade opcional por domínio, sem versão, IG, perfis, implementação ou conformidade definidos; decisão futura exige caso de uso, recursos/perfis, terminologias, identificadores, consentimento/privacidade, proveniência e testes próprios.

[SECURITY-AND-ROLLBACK.md](../../../docs/missions/atlas-parity-04/f4-c0-reader003/SECURITY-AND-ROLLBACK.md) fixa N01–N24 e negativos suplementares para C3/C4, todos runtime NOT_RUN em C0. C3 prova File API atômica, segregação, identidade e regressão Caderno; C4 qualifica sucessão CI, ancestry e proteção do adendo no SHA integrado terminal. L1/G4 host e F5/G6 privados exigem autorização/provas próprias. Sem evidência, resultado UNKNOWN; nenhuma aprovação automática.
