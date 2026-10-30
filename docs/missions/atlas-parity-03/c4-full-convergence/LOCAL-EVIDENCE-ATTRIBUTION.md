# Atribuição da evidência local

Os dois recibos L2 fornecidos pelo operador foram lidos somente como documentos. Pertencem exclusivamente ao C1 326b92ae27effb6941801ed3e9af5c07aa90fb95, tree 7a9bbc1765bbbf3897760ccc50a0b22aec3ee239. RESULT.md SHA256 96b69a7272edadd7a731232cfad993ef94beaa9f119288cb7d30e945b007af91; HANDOFF.json SHA256 d020ad8486ce09d5bca2b78a23085030f34237bc70f0a35b4f60fe40d279b8d6. Arquivos privados e pacote P04 não foram copiados para a PR.

L2 comprovou aquisição de subset identificado de 65 arquivos, instalação isolada e validação offline normal/-O do C1. Wheels foram construídos localmente de inputs conferidos; não eram wheels baixados de CI. P04 preservado no escopo medido: 41 entradas do manifesto P04 conferidas e 437 arquivos no conjunto de preservação, sem diferenças. O número 2100 do resumo inicial não é comprovado por esses recibos e não é repetido como fato.

HTTP L2 foi impedido antes da execução por guarda herdada da L1: a L1 registrou WinError 10013 no primeiro GET, antes de resposta. L2 não criou servidor nem tentou novo bind/GET; browser não foi executado e métricas não observadas são null. Não foi observada falha HTTP da candidata C1. Instalação/offline aprovados permanecem válidos apenas no seu escopo; WinError não vira PASS nem defeito Atlas presumido.

LOCAL_C1_INSTALLATION=PASS
LOCAL_C1_OFFLINE=PASS
LOCAL_C1_HTTP_BROWSER=BLOCKED_EXTERNAL_WINERROR_10013
LOCAL_C4_INSTALLATION=NOT_RUN
LOCAL_C4_OFFLINE=NOT_RUN
LOCAL_C4_HTTP_BROWSER=NOT_RUN
HOST_OPERATIONAL_READINESS=false

C4 acrescenta runtime P03 e controles de composição; L2 anterior não executou esses bytes. CI em runners comprova engenharia no SHA correspondente, sem fechar o gate operacional deste host.

## Futura missão LOCAL C4

Exigir autorização própria, SHA C4 terminal da PR, manifests/wheels conferidos e instalação isolada fora de qualquer checkout compartilhado. Provar SDK sem viewer/R4, viewer sem R4, assets e fontes sintéticas/autorizadas byte-idênticas. Registrar imports, CLI, validação, catálogo/rebuild/dossiê em normal e -O por SHA; os resultados só então podem alterar os campos LOCAL_C4.

Exemplos de comandos para essa futura missão, com python já resolvido do venv C4 verificado e source explicitamente autorizada:

```powershell
& $C4Python -I -m caderno_protocol $Source
& $C4Python -I -O -m caderno_protocol $Source
& $C4Python -I -m atlas_viewer inspect $Source
& $C4Python -I -O -m atlas_viewer inspect $Source
& $C4Python -I -m atlas_viewer dossier --source $Source
```

Serve e browser exigem evidência independente de executor já autorizado/capaz de loopback e nova missão LOCAL específica. Apenas sob esses requisitos, o comando é `& $C4Python -I -m atlas_viewer serve --source $Source --port $AuthorizedPort`, seguido de HTTP/browser reais por SHA com logs, JSON e capturas. Trocar SHA, venv, porta ou cliente não prova mudança de permissão. Não repetir probes equivalentes nem alterar ACL/firewall/sandbox/SID/políticas por este CHAT.

É proibido declarar prontidão operacional a partir da L2 C1, de CI ou do estado HOST_GATE_DEFERRED.
