# Segurança, contraprovas e rollback — C0

Owner/writer: coordenador /root, análise B nativa somente leitura. Data: 2026-10-31.
Normas fixadas: ADR-0003 v0.2 e descriptor0.2.0 em c3ea1e82938fd61cc5a22fee973352715a5bb527; INPUT-SHAS.json lista blobs. Custódia: manifesto/OUTPUT-OBJECTS/envelope Git.

## Limites de confiança

O1 externo lê somente projeção preexistente explicitamente autorizada, com root/allowlist exatos e identidade verificada; não descobre fontes/worktrees/drives, não importa r4.*, não executa HTML/JS/gerador, não chama rede/provider. Usa scratch privado próprio fora do acervo/repos. Separação de pastas não prova isolamento de OS.

Antes/durante/depois: validar alvo real e ancestrais, handle/identidade, tamanho/mtime/digest; recusar traversal/percent-decoding, aliases Unicode/casefold, UNC/device/ADS, symlink/reparse, hardlink/especial sem identidade provada e TOCTOU. Fonte alterada ou garantia insuficiente bloqueia snapshot. Autorização F1 não se transfere a L1; C0 não lê acervo nem revalida hash privado.

O3 lê um arquivo selecionado manualmente, valida antes da publicação atômica e mantém apenas RAM segregada. Sem upload/telemetria/storage (localStorage/sessionStorage/IndexedDB/service worker), paths JS, endpoint adicional, URI ativa, DOM de HTML fonte ou reconciliação automática. IDs DOM não reutilizam IDs de conteúdo. Renderização por textContent/SVG próprio, sem eval/innerHTML/iframe/import dinâmico. Schema fechado local: nunca baixar schema/contexto ou recurso.

CSP/Origin/Host/no-store/nosniff e ausência de CORS permanecem. Assets futuros fixos exatos; nenhuma rota genérica, proxy ou arquivo privado servido por URL. Browser não monitora origem: OBSERVED_SNAPSHOT_ONLY; leitura externa/importação novas são explícitas.

## Quotas herdadas e recusa

3 arquivos ×64 MiB, total192 MiB; JSON UTF-8 ≤32 MiB, depth20; 10.000 nós/100.000 relações/10.000 assets; 128 tabelas, 256 colunas por tabela, 100.000 linhas agregadas; literal64 KiB/lexema128 KiB. Limite total prevalece. maxLength não impõe bytes, linhas agregadas nem profundidade. Rejeitar chaves duplicadas antes da sobrescrita, UTF-8 inválido, NaN/Infinity, truncamento, formato/versão desconhecido e propriedade extra. Nenhuma recusa exibe subconjunto como completo.

Host deve impor256 MiB/30 s por abertura/leitura/validação. Sem prova da imposição na fronteira real: HARD_BUDGET_UNVERIFIED; recusar execução/qualificação G4. C3 não pode converter benchmark/heap observado em garantia. Esses controles são requisitos, não medições C0.

TTL≤60 min desde geração, observado≤gerado<expiração, sem renovação por acesso. Reimport/reindex/troca de sessão ou snapshot/erro/TTL/dispose invalidam todos os tokens fonte+snapshot+sessão+ocorrência; exportação/navegação expirada é recusada. Não resolver stale por título/ID textual.

## N01–N24 herdados: oracles futuros, não testes C0

Status de execução de TODAS as linhas: NOT_RUN. Resultado de produto: UNKNOWN. C3 demonstra integração/browser sintéticos; C4 preserva e executa as suítes e negativos aplicáveis no SHA terminal integrado. Aquisição/host/fonte real pertencem a C2/L1, e browser privado a F5/G6; C3/C4 não substituem esses atos.

| ID | Entrada/risco | Oracle exigido | Prova responsável |
|---|---|---|---|
| N01 | ID igual em fontes/snapshots diferentes | Identidades e seleções separadas, nenhum vínculo cruzado | C3/C4 |
| N02 | ID colidente no mesmo contexto | Ocorrências/localizadores retidos, sem escolher primeiro/último | C3/C4 |
| N03 | Navigation ID promovido a nativo | Rejeição semântica; native_id original null | C2/C3/C4 |
| N04 | 22 endpoints null F1 | Endpoint/declared ID null preservados, nenhum alvo inventado | C2/C3/C4 sintético; L1 real |
| N05 | 75 relações não resolvidas | Strings/contagens retidas; navegação não atravessa gap | C2/C3/C4; L1 real |
| N06 | 50 colisões,40 grupos,41 excedentes | Ocorrências e grupos separados; sobreposição não somada como partição | C2/C3/C4; L1 real |
| N07 | Quatro tabelas sem record resolúvel | Consultáveis como não vinculadas; nenhum record artificial | C2/C3/C4; L1 real |
| N08 | 28 RF não admitidas | native_id=null, sem admissão por campos/nav ID | C2/C3/C4; L1 real |
| N09 | Run original isolado ou referência externa não carregada | SOURCE_ENTITY original ≠ stub; binding_gap; sem caminho contínuo fabricado | C2/C3/C4; L1 real |
| N10 | Missing/null/vazio/zero/categoria ausente | Distinções literais; MISSING sem heurística | C2/C3/C4 |
| N11 | >2^53,decimal,string numérica,unidade/precisão | Tokens/tipos/ordens preservados; sem round/conversão | C2/C3/C4 |
| N12 | HTML/JS/handlers em texto | Texto inerte; zero execução/injeção/rede | C2/C3/C4 browser |
| N13 | CSV =,+,-,@,controles,aspas,newlines | Neutralização/quoting declarados; JSON literal intacto | C3/C4 |
| N14 | Traversal/symlink/reparse/TOCTOU/UNC/ADS | Recusar antes da fuga; identidade final/fonte intacta | C2 sintético; L1 host real; C4 regressão |
| N15 | URI file:/javascript:/data:/remota | Zero abertura/download, apenas texto | C3/C4 |
| N16 | Fonte muda durante/depois da leitura | O1 recusa corrida; browser só snapshot observado, nova leitura/import explícita | C2/C3/C4; L1 real |
| N17 | Descriptor inválido/versão/quota | Recusa atômica, sem dataset parcial; Caderno utilizável | C2/C3/C4 |
| N18 | Token após reimport/reindex/sessão/TTL | Stale recusado; sem remapear em novo contexto | C3/C4 |
| N19 | Global unknown/zero/overlap | global_total/global_percentage null, sem 0/0/soma indevida | C2/C3/C4 |
| N20 | Digest/validação PASS e ciência UNKNOWN/HOLD | Sem promoção a autenticidade/ciência | C3/C4 |
| N21 | Nome/MIME RF/RNF/RES/FHIR/produto | Sem inferir domínio/admissão/produto/conformidade | C2/C3/C4 |
| N22 | Caderno sem sidecar/R4; SDK sem UI | Instalação/funcionamento independente no SHA sucessor | C3/C4 |
| N23 | Árvore/RF/jornada interativa | Browser real, teclado/foco, expandir/zoom/pan/minimapa/retorno, filtro/detalhe/export | C3/C4 sintético; F5/G6 privado |
| N24 | O2 declarado conforme sem validadores | Recusar rótulo Caderno/RO-Crate/ProcessRun sem provas relevantes | C3/C4, se aplicável |

As contagens F1 são sanitizadas e históricas; fixtures futuras serão sintéticas, sem literais/IDs/paths/digests privados. Uma RF F1 comparada não comprova as outras151 linhas. RNF/RES e denominador global seguem desconhecidos.

## Negativos suplementares obrigatórios

| ID | Tentativa | Oracle / owner futuro |
|---|---|---|
| C0-X01 | Upload/fetch/endpoint/conexão sidecar/discovery/paths JS | Zero tráfego/leitura; C3/C4 inspecionam fronteiras reais |
| C0-X02 | Storage/TTL renovado/erro deixa seleção exportável | Zero persistência, RAM/tokens invalidados, export/navegação bloqueados; C3/C4 |
| C0-X03 | Alterar CSP/Origin/Host/no-store/nosniff ou asset genérico | RED e proteção idêntica; C3/C4 |
| C0-X04 | Misturar Catalog/SDK/contextos ou File API automática | RED; Caderno funciona sozinho, importação somente explícita; C3/C4 |
| C0-X05 | Chaves duplicadas/extra/schema remoto/UTF-8 inválido/NaN/depth/bytes/linhas agregadas | Recusa antes de dataset utilizável, inclusive payload com PASS recebido; C2/C3/C4 |
| C0-X06 | Adendo C0 adulterado,manifest rehashado,path/mode extra,symlink/rename | Guard sucessor RED por conteúdo independente do manifesto; C4 |
| C0-X07 | Perder ancestry C0 ou alteração transitória congelada depois revertida | RED na história completa/parents, sem squash ou allowlist genérica; C4 |
| C0-X08 | Hard budget não imposto, campo sem prova marcado PASS | HARD_BUDGET_UNVERIFIED/UNKNOWN, recusa G4; C2/L1/C3/C4 conforme fronteira |
| C0-X09 | Rollback/cache cleanup toca Caderno/fonte/snapshot alheio | Zero escrita fora de derivados próprios identificados; C2/L1/C3/C4 |
| C0-X10 | ADR/guard/G4/G5/FHIR promovidos por revisão/CI documental | RED; estado e autoridade separados, sem falsificar aprovação; C4 |

C3 integra somente depois dos quatro inputs qualificados C0/C1/C2/F3B, por ancestry completa. C4 começa depois de C3 congelado, conserva contrato C0 e documentos históricos e qualifica todos os workflows aplicáveis no MESMO SHA terminal, com testes herdados e novos, sem skips/xfail/continue-on-error/paths-ignore/guards relaxados/pins mudados. Recusa do guard antigo para novos paths C0 é CI_SUCCESSION_TO_QUALIFY_C4; registrar run/job/log exatos, não afrouxar proteção. Sucesso documental C0 não implica CI integrada verde.

## Rollback e residual

Em C0: nenhum runtime mudou. Retirar a dependência C0 de uma futura composição basta; conservar os commits/recibos e contrato histórico. Não executar rollback nesta missão.
Em implementação futura: desativar painel, invalidar todos os tokens, descartar RAM; processo externo dono pode remover apenas cache próprio por path/identidade exatos. Não apagar/mover fontes, Caderno, R4 ou experimentos. Crash pode deixar resíduos; sem promessa de apagamento físico ou autorização G9.
Custos/riscos residuais: dois limites de confiança e validador extra; browser não observa drift da origem, hard budgets host dependem prova, dados privados exigem autorização separada. Quaisquer alterações de plano/superfície exigem decisão prévia.
