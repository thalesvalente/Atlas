# Alternativas arquiteturais — AP04-F2

Versão: 0.2-candidate; 2026-10-30. RECOMMENDED_PROPOSED / ARC09_APPROVAL_REQUIRED.
Proposta de A (/root/architecture_a), integrada pelo coordenador. Desenho documental, não implementado ou ensaiado nesta F2. Plano AP04-POR-v1.0-draft preservado.

## Candidata única e limite de autoridade

Recomenda-se UMA composição: O1→O3, leitura externa explícita isolada e importação do descriptor neutro atlas-legacy-presentation 0.2.0 em área segregada do navegador Atlas. O1 define aquisição/saída; O3 define consumidor. São componentes da mesma candidata, não escolhas arquiteturais concorrentes.

reader003 recebe exclusivamente Caderno0.1.0a1, e ADR-0001 determina consumo pelo contrato público. Uma nova entrada no navegador amplia a fronteira mesmo sem endpoint. File API/isolamento não demonstram compatibilidade automática. ARC09_APPROVAL_REQUIRED antes da implementação; nova entrada não existe no C4, nem é autorizada pela preferência funcional/ADR0.1, publicação, agentes ou CI.

F1 a237f446e54927eeeda8ed5e8e9daa83ee09dcb7 fornece disponibilidade no recorte e uma RF literal, sem UI recuperada. Quatro tabelas sem record ligado,28RF não admitidas,Run externo isolado/binding_gap,22endpoints null,75relações pendentes,50colisões,40grupos repetidos/41excedentes e UNKNOWN_UPSTREAM/GLOBAL_UNPROVEN impedem modelagem por preenchimento inventado. Inventário integral em RESULT/IDENTITY-AND-LOSS-POLICY.

## O1–O5

Custos relativos ao objetivo temporário, sem horas inventadas.

| Opção | Vantagens/limites | Riscos/padrões | Custo/complexidade | Rollback | Aprovação/disposição |
|---|---|---|---|---|---|
| O1 leitura externa explícita | Parsing/acesso fora do Atlas; origem intacta. Sozinha não define consumo C4 | Perdas/identidade/privacidade devem ser modeladas; descriptor não é Caderno conforme | Médio: ferramenta isolada,validador,snapshot/cache/recibos | Encerrar externo e descartar seus derivados próprios | Componente produtor O1→O3; consumo adicional exige ARC09 |
| O2 pacote temporário Caderno/RO-Crate conforme | Pode usar reader existente se pacote realmente conforme; sem mover/reformatar origem | Órfãos/referências/Run sem experimento não podem ser «corrigidos» por invenção; extensões podem não ser exibidas no C4. Necessário manifesto de perdas e todas validações relevantes | Alto: semântica,literais,validadores/extensões e prova de utilidade; sem promessa de conversão sem perdas | Abandonar pacote/conversor temporários, preservar origem e manifesto | Alternativa não escolhida. «Conforme» só após provas de schema,SDK,semântica,base RO-Crate e requisitos ProcessRun anunciados. Extensão incompatível exige decisão própria |
| O3 entrada opcional UI | Renderer neutro independente de SDK/produtor; sozinha não define aquisição | Amplia reader003/ADR1; risco de segundo modelo permanente e exposição de dados aos scripts da página | Médio no conjunto:parser/validador,renderer,contexto,regressão | Desativar consumidor/assets e invalidar estado | Componente consumidor O1→O3; ARC09_APPROVAL_REQUIRED |
| O4 viewer legado separado | Contingência mantém produto anterior | Não recupera AtlasC4/jornada unificada; contexto/contagens não se misturam. Composição/iframe requer desenho próprio e políticas de origem/CSP de ambas páginas | Menor para consulta se acesso/ambiente já autorizados; maior para integrar depois | Fechar consulta separada, conservar referência provisória | CONTINGENCY_ONLY; sem paridade/G4/G5,execução local com gate próprio |
| O5 migração agora ou cópia de leitor/código privado | Não elegível nesta missão | D014/015,ARC04/07,direitos,privacidade,independência e risco acervo; proibido reconstruir leitor Windows suspenso | Muito alto/inadequado | Oneroso/incerto se originais alterados | OUT_OF_SCOPE_NOT_AUTHORIZED; sem implementação/fallback |

O2 continua alternativa legítima somente com conformidade demonstrada, nunca apagando lacunas ou promovendo IDs. O4 não recebe crédito de recuperação. O5 não integra sequência autorizada.

## Topologia e contratos de processo

Projeção legada preexistente autorizada → processo LOCAL externo → JSON privado temporário LEGACY_DERIVED → seleção explícita File API → validador neutro no browser → painel «Apresentação legada (derivada)».

Via Caderno independente: snapshot Caderno → SDK/load_package → Catalog → APIs C4 → UI Caderno.
As vias não compartilham catálogo nem resolvem entidades implicitamente entre si. Composição visual explicita fonte/snapshot/regime de validação.

### Processo externo: entrada/saída e ARC-07

Iniciado explicitamente no LOCAL, fora do processo/distribuição principal Atlas. Entrada só na allowlist exata de projeções preexistentes autorizadas, sem glob, descoberta de discos/worktrees/vizinhos, aquisição upstream, rebuild, experimentos, execução de HTML/JS ou seguir links encontrados.

Parser restrito à representação conhecida e delimitada; estrutura não suportada gera erro. Saída UM JSON UTF-8 de apresentação, sem código e sem pacote Caderno fabricado. IDs/literais/paths/digests privados permanecem locais. A implementação futura deve provar handles de leitura, root/allowlist, rejeição symlink/reparse/traversal/TOCTOU e observações antes/depois. Escrita só no scratch privado próprio. Outra pasta/processo não certifica isolamento de OS/host adversarial. SECURITY detalha obrigações.

### Consumidor: UI, Catalog, server e SDK

Seletor File API no painel futuro; validador antes de expor qualquer componente. Erro de schema/quota/identidade/prazo impede importação atômica; sem fallback para Caderno ou truncamento. UI mostra LEGACY_DERIVED, fonte/snapshot, validação de apresentação, data observada e limitações. Textos/URIs inertes; SVG próprio, sem inserir markup de fonte. Organização,linhagem,menções diferenciadas.

Browser não lê caminhos originais, não abre anexos/URI, não envia descriptor ao servidor nem telemetria. Scripts estáticos da página recebem dados privados; isso exige origem controlada/sem código externo e revisão de segurança. CSP não certifica extensões/browser/host.

C4 Catalog.rebuild chama load_package e to_read_model apenas para pacote válido. Identidade/fingerprint/snapshot_binding pertencem a fontes Caderno declaradas. Descriptor NUNCA entra como Source,Package,read_model ou validação Caderno. Consumidor neutro mantém namespace/seleção próprios no browser.

server.py atual só expõe assets fixos,/api/catalog,/api/dossier,/api/reindex. Candidata preserva APIs e só exigiria assets fixos explicitamente enumerados para UI futura aprovada. Nenhum endpoint legado,HTTP sidecar,porta extra,wildcard de arquivos,CORS,proxy de paths,iframe ou URL de fonte arbitrária. Preservar connect-src self,Host/Origin,no-store,nosniff e políticas atuais no SHA integrado. Nenhum servidor/porta iniciado nesta F2.

SDK,read_model,contexto,schema,versões/validadores não dependem do descriptor/UI/R4. Descriptor não é perfil Caderno nem substituição dos padrões. Testes futuros devem demonstrar SDK sem Atlas/R4 e Atlas C4 sem sidecar/legado; desenho não é prova executada.

## Snapshot, operação, cache e invalidação

Processo externo: scratch privado fora acervo/repos, descriptor com vida máxima60min desde emissão; remoção só dos derivados próprios em encerramento normal/timer. Browser: apenas RAM,sem LocalStorage,SessionStorage,IndexedDB,serviceworker/cache persistente; expira ao fechar,TTL,nova importação/invalidação ou erro.

TTL é expiração lógica; crash pode deixar resíduo, sem promessa de apagamento físico. Operação LOCAL futura deve tratar cache próprio e recibos G4, sem poder sobre acervo/G9.

Snapshot vincula bytes observados e escopo, não autoria/data científica. Links vinculados à sessão UI+fonte+snapshot+ocorrência; nova importação/reindexação/TTL invalida seleção e links anteriores. native_id igual em fontes distintas não funde. Contexto legado não reutiliza snapshot global Caderno.

Browser declara OBSERVED_SNAPSHOT_ONLY; não consegue reobservar a fonte privada. Não diz «fonte atual»/«sem mudanças». Atualizar exige repetir leitura externa autorizada e importar novo descriptor. Fonte alterada durante leitura impede emissão; não remendar snapshot.

| Recurso | Quota proposta |
|---|---:|
| Arquivos allowlisted | 3 |
| Cada arquivo / total entrada | 64MiB /192MiB |
| Descriptor UTF-8/profundidade | 32MiB /20 |
| Nós/relações | 10000/100000 |
| Tabelas/colunas por tabela |128/256|
| Linhas totais/célula |100000/64KiB|
| TTL |60min desde emissão|

Excesso rejeita sem truncar/omitir. Necessidade futura de limites diferentes exige recorte autorizado ou versão revisada; não altera quotas Caderno.

## Fidelidade e fases futuras

Contratos de F3A/B/F4/F5 em PARITY-TRACEABILITY; schema/exemplos e perdas nos documentos B. Nenhuma fase iniciada. Exigências: native_id null não ganha identidade/admissão; parent_key é organização sem causalidade; órfãos e Run isolado preservados; ocorrências pendentes/nulas/colidentes/repetidas retidas; quatro tabelas consultáveis sem record inventado; headers/ordem/tipos/precisão/unidades/ausências literais; File não vira produto por MIME; denominador global desconhecido e snapshots sobrepostos não somados.

F3A genérica sintética: SVG interativo,expandir/recolher,zoom/pan/minimapa,teclado/foco.
F3B: tabela opcional de domínio,filtro/detalhe/exportação,literais/ausências,não cumpre RF real por fixture.
F4: integração única só após decisão arquitetural aplicável,F1,F3A/B e gates previstos.
F5: comparação LOCAL privada/browser Windows no SHA integrado,recibos públicos sanitizados.

Percurso contínuo até RF F1 não é prometido; gap exibido até nova evidência autorizada, jamais completado por inferência.

## Impactos, padrões e G4

Matriz detalhada em ADR candidata: reader003 ampliado requer aprovação; Catalog/APIs preservados; server só assets; SDK/schema/contexto sem mudança; produtor R4 externo e sem import; ARC05 exige prova futura; ARC07 mantém acesso host fora runtime sem dispensar ARC09; privacidade/licença com gate próprio; segurança parsing/origem/TTL; HL7/FHIR futuro por domínio.

RO-Crate1.3,ProcessRun0.6,Caderno0.1.0a1 conservam direção aceita delimitada e validadores. Descriptor nunca recebe rótulo conforme. FHIR futuro exige caso de uso/versão/IG/perfis/terminologias/identidade/consentimento/proveniência/testes; nome/arquivo/MIME não prova domínio/conformidade.

F2 não declara G4 PASS. Qualificação futura requer aprovação versão/SHA, leitura externa delimitada, zero escrita/alteração fontes, descriptor validado sem promoção, lacunas F1 preservadas, stale links recusados, Atlas sem parser privado/poderes host, cache privado e revisão independente por SHA. G5 exige regressão/isolamento;G6 browser privado real.

Rollback: desativar opção,preservar caminho Caderno,encerrar externo e descartar somente derivados próprios; reversão futura de código remove assets/consumidor com checks. Nada exige mover/converter/reescrever/apagar fonte.

Confronto D001–020 completo em PARITY-TRACEABILITY. Não muda ordem F0–F6,PAR,G0–G9 ou proteções, portanto nenhum desvio de plano solicitado. Introduzir futuramente endpoint,leitura no Atlas,novo servidor,poder host,protocolo ou reordenação requer nova proposta/solicitação aplicável antes de agir.

Pergunta humana em DECISION-REQUEST vinculada ao SHA revisado. Resposta favorável não inicia fase, acesso privado,merge,release,deploy,promoção,ciência ou limpeza.
