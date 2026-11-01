# AP04-F4-L0-CODEX-DESKTOP-01 — testemunho limitado no host Windows, sem executar L1

orq.phase@llm-sec,agentic-pac/seai.qa:

**EXECUTE o trabalho local seguro deste prompt; NÃO devolva outro prompt como produto.** Ambiente obrigatório: **Codex LOCAL acessando diretamente um workspace Windows autorizado**. Se a sessão for Codex Cloud, container remoto ou CHAT sem acesso real ao host, encerrar como LOCAL_WORKSPACE_UNAVAILABLE. Recomendação de esforço: High; Extra High opcional apenas para divergências.

## 0. Hierarquia, fronteiras e status

Leia INPUT-PINS.json, o prompt L0 original (blob 3b84f85634ed14a984e067de48b6e6a468e3820c), AGENTS.md aplicável, AP04-POR, constituição ARC-01–09 e o handoff C2-D no SHA fixado. Instruções do operador e permissões efetivas do sistema prevalecem sobre convenções de tags. Se houver conflito impeditivo com AGENTS.md ou skill, informe arquivo, regra e efeito sem contornar a restrição.

**Status vinculante para este trabalho:** C2_D_BLOCKED_EXACT no SHA 86aec49d793d10c1d0b35db58fda747e0febdb23. CI focal Windows/Ubuntu normal/-O passou no SHA, mas **não existe worker operacional de leitura real qualificado** e o Windows não tem confinamento filesystem/rede comprovado. C2-K propôs descriptor 0.2.1 em ab22a78eb22af4ef9651cdd8f652c3cb2755e947, porém não há aprovação humana ARC-09 para implementá-lo. Findings de B sobre ACL Administrators e vinculação da fixture ao worker permanecem abertos. Logo **NÃO iniciar L1, reader.prepare real, --synthetic-fixture sobre dados reais, nem afirmar G4/G5/G6/C3 READY**.

O objetivo exclusivo desta missão é F4-L0: comprovar ou delimitar o formato de uma projeção legada **já existente**, sob autorizações separadas, com preservação do host e recibo privado. Não autorizar por inferência L1, CI global, integração C3, F5 ou ciência.

## 1. ANALYZE — preflight do desktop

1. Identifique o PROJECT_ROOT real aberto no Codex, unidade e permissões efetivas. A sessão DEVE ser local Windows; nunca simular acesso a partir do GitHub.
2. Leia as instruções locais aplicáveis. Identifique se há escritores concorrentes ou árvore de trabalho com mudanças; não mudar branch, não dar checkout/reset/clean, não criar clone/worktree e não alterar código de Atlas ou R4.
3. Localize a raiz PRIVADA de recibos F1 somente mediante path explícito fornecido pelo operador ou configuração/recibo conhecido no workspace já aberto; **não faça busca recursiva, glob, enumeração de Downloads, diretórios irmãos, drives H:/G:/C: ou varredura de worktrees**.
4. Somente numa pasta PRIVADA autorizada e gravável, fora do repositório e do corpus, faça um write probe: crie um arquivo de nome aleatório exclusivo, leia-o e remova apenas esse arquivo. Registre em recibo privado WORKSPACE_WRITE_PROBE=PASS ou WORKSPACE_WRITE_BLOCKED. Não mudar ACL, firewall, política PowerShell ou permissões.
5. Compare os metadados públicos/SHAs dos prompts e da C2-D; se o checkout local diferir do commit fixado, não promover os resultados do outro SHA. Pode continuar o testemunho L0 de estrutura usando somente recibos F1 e contratos imutáveis; não substituir a baseline sem registrar.
6. Se os recibos F1 não estiverem acessíveis por path conhecido, encerre F4_L0_RECEIPT_NOT_FOUND; informe só a categoria do bloqueio, sem revelar paths.

**Acesso aos recibos privados F1 não autoriza abrir os arquivos científicos de origem.** A leitura preliminar limita-se aos recibos F1 já autorizados, sem despejar conteúdo privado em stdout, ferramenta de chat, logs remotos ou respostas ao modelo.

## 2. Gate de autorização para qualquer nova leitura científica

Dos recibos F1, identifique PRIVADAMENTE os **mesmos três arquivos exatos** da seleção histórica (captura JSON, HTML ponteiro e HTML alvo). Exiba suas identidades apenas ao operador no canal LOCAL seguro. O HTML ponteiro não autoriza navegar automaticamente ao destino; o alvo tem de constar na allowlist F1 e na nova autorização.

**ANTES de abrir/reabrir fonte real, exija manifestação explícita do operador na sessão local**, delimitando as três identidades exatas, finalidade F4-L0, leitura somente leitura, limites de 64 MiB por arquivo/192 MiB agregados e proibição de publicar bytes privados. A autorização antiga de transferência de código R4 NÃO substitui essa manifestação. Se faltar, encerre F4_L0_SOURCE_NOT_AUTHORIZED, mantendo os originais intocados e registrando apenas evidência privada de metadata F1.

Modelo de pedido ao operador LOCAL (não inserir paths neste Git): "Os três arquivos exatos registrados nos recibos F1 estão identificados localmente. Autoriza RELEITURA somente leitura exclusivamente deles, até 64 MiB por arquivo e 192 MiB no total, para testemunho inerte F4-L0, sem abrir fontes vizinhas nem publicar conteúdo privado? A autorização não inclui L1."

Se a ferramenta Codex não conseguir receber essa confirmação sem transmitir paths/bytes privados para ambiente remoto, NÃO reabra a fonte. Não presuma consentimento a partir da simples habilitação do Codex.

## 3. PLAN → EXECUTE — L0 somente após autorização local comprovada

1. Confirme o mesmo conjunto F1 por identidade de arquivo, path canônico, ancestor chain, ausência de symlink/reparse/hardlink perigoso, limites de bytes e escopo autorizado. Rejeite traversal, ADS, UNC/device paths não explicitamente aprovados e qualquer necessidade de descoberta indireta. Não escrever nas fontes, no R4, nos antigos outputs ou no checkout.
2. Capture em recibo PRIVADO identidade/size/mtime/digest antes de cada leitura, com handle read-only e verificação depois. Se houver drift em relação ao F1 ou mudança durante a leitura, interrompa SOURCE_DRIFT ou SOURCE_CHANGED; não regere, normalize ou edite a projeção.
3. Faça extração **inerte** de JSON preexistente: no HTML, exatamente um script id=data type=application/json; rejeite zero/múltiplos scripts qualificantes. Não executar HTML/JS, seguir URLs ou pointers, chamar atlas.build, notebook, provider, inferência, browser legado ou leitura de arquivos referenciados.
4. Parser local deve rejeitar JSON com chaves duplicadas, NaN/Infinity, UTF-8 inválido, profundidade/tamanho fora do contrato; nunca imprimir o payload. Se não houver ferramenta local que assegure que bytes privados não entrarão no contexto do modelo/saída de ferramentas, interrompa: PRIVATE_PAYLOAD_EXPOSURE_UNVERIFIED.
5. Observe somente estrutura/tipos/contagens: schema r4-experiment-viewer-v5, authority, records e lineage_graph.nodes como coleções independentes, lineage_graph.edges, nodes key/ui_id/native_id/parent_key, from_key/to_key, parent links, conflitos, repeats/gaps, result_tables/rows/cells e estados de ausência. Chaves e IDs científicos literais ficam EXCLUSIVAMENTE em recibos privados.
6. Confronte a MESMA amostra F1 selecionada, sem declarar total global: 159 records; 2.911 lineage nodes; 1.595 lineage edges; cinco tabelas com [39,85,28,0,0] linhas (152); 28 RF não admitidas; 858 parent keys explícitas resolvidas; quatro tabelas sem record_id resolúvel; 22 endpoints null, 75 unresolved, 50 colisões e ocorrências repetidas. Diferenças geram SOURCE_DRIFT ou PROFILE_VARIANT_UNVERIFIED, não adaptação artificial dos números.
7. Compare a única linha RF de F1 em PRIVADO quando seu recibo anterior realmente permitir, por ID/núcleo/nome/descrição/critério/categoria e tipo/posição/valor; não publicar literal, IDs, hashes, paths, nome de cliente, screenshots ou descriptor. MISSING, null, vazio e zero devem permanecer distintos; RF UNADMITTED não recebe native_id inventado.
8. Teste apenas se os campos estruturais da projeção REAL são expressáveis pelo mapper C2-A e descriptor 0.2.0, indicando lacunas. Se parent_key source-key não equivale inequivocamente a native_id, marcar KEY_BRIDGE_CONTRACT_REQUIRED e não fabricar RESOLVED. Não alterar A/descriptor no host; criar contraexemplo sintético original caso necessário.
9. Verifique preservação antes/depois por handle/identity/hash/mtime, ausência de escrita, nenhum acesso indevido e nenhum arquivo público modificado. L0 não pode afirmar garantia OS 256 MiB/30 s; isso é gate operacional L1 separado e hoje bloqueado.

**Não execute testes adversariais de memória, rede, processos, destruição ou ACL contra o acervo ou host reais.** Se precisar de demonstração sintética, use apenas fixtures inteiramente inventadas, em scratch privado e sem extrapolar o resultado ao corpus.

## 4. REVIEW — recibos e privacidade

Crie somente na raiz PRIVADA autorizada, sem usar git add/push, os arquivos nomeados pelo L0 original: SOURCE-SELECTION.private.json, SOURCE-STRUCTURE.private.json, SOURCE-INTEGRITY.private.json, PROFILE-COUNTEREXAMPLES.private.md, RESULT.private.md, MANIFEST.sha256, e INDEPENDENT-REVIEW.private.md apenas se um revisor realmente distinto atuar. Nunca simular revisor ou aprovação. Registre código de falha, ids técnicos locais e hashes nos arquivos privados, não na resposta ao chat.

Produza, se a fase tiver dados suficientes, HANDOFF.sanitized.json pela estrutura **fechada** HANDOFF-SANITIZED.schema.json (inicie de HANDOFF-SANITIZED.template.json). O validador validate_sanitized.py só lê o arquivo sanitizado indicado explicitamente e não faz upload. Mesmo PASS do validador NÃO autoriza envio GitHub: é preciso revisão independente de privacidade quando disponível e aprovação humana explícita específica para publicação. Se não houver tais autorizações, preserve o handoff somente no host.

Para resposta ao operador, informe **somente**: código de estado, confirmação de workspace local, autorização sim/não, fonte reaberta sim/não, identidade antes/depois igual sim/não/não aferida, comparação F1 PASS/DRIFT/UNVERIFIED, revisão realizada ou PENDING, G4=BLOCKED e menor próximo ato. Não mostrar arquivos, paths, hashes de fonte, JSON bruto, stdout sensível ou RF literal.

## 5. DONE / limites da missão

Estados admissíveis:
- F4_L0_PRECHECK_ONLY — workspace e recibos conferidos sem nova leitura;
- F4_L0_SOURCE_NOT_AUTHORIZED — F1 conhecido, mas falta permissão específica de releitura;
- F4_L0_RECEIPT_NOT_FOUND — recibos privados não identificados de modo seguro;
- F4_L0_REAL_SOURCE_SHAPE_WITNESSED_SCOPED — estrutura realmente aferida, bytes íntegros, privacidade revisada no escopo, sem G4;
- F4_L0_STRUCTURAL_GAP_EXACT ou SOURCE_DRIFT — evidência privada exata e contraexemplo só com valores inventados;
- LOCAL_WORKSPACE_UNAVAILABLE / WORKSPACE_WRITE_BLOCKED / PRIVATE_PAYLOAD_EXPOSURE_UNVERIFIED — limites reais impedem avançar.

**Nunca converter nenhum desses estados em F4_L1_LOCAL_REAL_READER_QUALIFIED_SCOPED, C2_D_REAL_V5_READER_READY_FOR_HOST_PROOF, G4, G5, G6 ou ciência aprovada.** Não executar L1/C3/C4/F5, migração, limpeza, release, deploy, merge, alteração do R4 ou da configuração do sistema. Continue trabalho seguro até concluir L0 ou registrar o bloqueio externo exato, sem criar mais prompts como substituto de execução.

**END-OF-AP04-F4-L0-CODEX-DESKTOP-01**
