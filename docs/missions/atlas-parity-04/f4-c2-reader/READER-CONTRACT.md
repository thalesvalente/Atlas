# Contrato de leitura e limite de qualificação C2

## Estado

F4_C2_BLOCKED_EXACT. Há implementação pública original de mecanismos e testes sintéticos; não há schema observado da projeção legada real nem isolamento/budget duro de host qualificados. Nenhum acervo privado foi aberto. Formato sintético não estabelece compatibilidade R4. A CLI operacional recusa antes de inspecionar qualquer path; não tentar L1 com --synthetic-fixture.

## Input de ensaio explícito, versão0.1.0

JSON UTF-8 estrito, sem BOM, duplicatas, NaN/Infinity ou surrogate solto. Root object: format=atlas-legacy-synthetic-source,version=0.1.0,synthetic=true,source_id,snapshot_id,access_policy_id,scope e arrays obrigatórios records,edges,result_tables,product_items,resource_documents. JSON-LD usa o mesmo envelope sem resolver @context. HTML somente um script inerte com exatamente type=application/json e id=atlas-legacy-synthetic-source. Conteúdo HTML/JS externo ao bloco é ignorado como texto e nunca executado; formatos ambíguos/execução necessária recusados.

records: id opcional comprovado,kind explícito ou Unknown,label obrigatório,original_type,family,parent_id e root opcionais. id nunca deriva de hash/path/ordinal. parent_id só referencia um ID fonte único no mesmo source+snapshot; objeto de referência externa exige {source_id,snapshot_id,id}. Colisões retêm ocorrências; null vs missing permanecem em refs/células/unmapped. Run observado permanece SOURCE_ENTITY isolado sem ancestrais inventados.

edges: from,to,kind,semantics,direction explicitamente declarados; ausência mantém UNKNOWN/UNRESOLVED. Sem causalidade inferida. Repetidos mantêm occurrence/repeat_group. Null endpoints não se tornam nó. result_tables: title,columns=[{key,header}],rows=[{id?,cells:[{present:true,value,unit?,precision?}|{present:false}],requirement?,run_id?}],id?,domain?,record_id?. Ordem vem dos arrays observados e nunca é ordenada por conteúdo. requirement é a estrutura fechada F2 com fields apontando índices originais. Admissão RF deve ser declaração/evidência explícita; UNADMITTED não recebe ID. Product/resource: id?,label,kind explícito ou Unknown,original_type,product_role,binding_id,media_type,uri; File continua File, nenhuma URI é seguida.

Campos selecionados não expostos são preservados em unmapped_fields com lexema. Campo impossível/excesso/forma incompatível recusa, sem truncamento. Números e arrays/objetos são texto tipado lexical; string numérica continua string. Null,missing,vazio,zero e booleano são distintos. Schema fechado 0.2.0 extraído integralmente do primeiro bloco JSON F2; não é alteração do contrato. Draft2020-12 formal + invariantes de referências, contexto, identidade, ordinais, células, estados, tempos e contagens. PASS de descriptor não é fonte autêntica ou ciência aprovada.

## Aquisição e efemeridade

Arquivo absoluto exato + até3 paths absolutos exatos; sem glob/drive scan/recursão/UNC/device/ADS/traversal/%/symlink/reparse/hardlink. Não abrir vizinhos ou links de payload. Até64MiB por arquivo e192MiB allowlist total (uma fonte por operação; não somar snapshots),32MiB descriptor,depth20,10k nós/assets,100k relações/linhas,128 tabelas,256colunas,64KiB literal/128KiB lexema. O orçamento de memória256MiB e30s duro NÃO está imposto; prazo cooperativo é detecção adicional e fica HARD_BUDGET_UNVERIFIED. Separação OS de rede/FS não qualificada. --synthetic-fixture é facilidade de teste e não barreira de segurança ou prova de origem inventada.

Fonte via handle, SHA256/tamanho/mtime/ctime/identidade antes/depois e path/ancestrais rechecados. Só sintéticos nesta execução. Scratch privado criado pelo processo fora de fontes/repositório,POSIX0700/DACL Windows protegida usuário do token atual+SYSTEM,arquivo0600 quando aplicável,publicação atômica sem sobrescrita por hardlink exclusivo e unlink do parcial próprio dentro de diretório privado. Não afirma confinamento host adversarial. TTL até3600s; validar com now real antes de uso. Cleanup remove só identidade derivada conhecida em memória; não há scan,log privado,cleanup após crash ou promessa de apagamento seguro. CLI que encerrou perde receipt de ownership e não oferece limpeza de arquivos arbitrários. Resíduo requer política local aprovada própria.

## Contrato mínimo sanitizado para L1

Fornecer amostra estrutural com valores inventados, preservando chaves/tipos/ordem e sem paths,IDs,digests,literais ou bytes privados: formato/versão/delimiter inerte; paths JSON e cardinalidades de records,edges,result_tables,product_items,resource_documents; chaves de identidade,contextos,endpoints; ordinais,colunas,linhas e distinção missing/null; evidência/ID/admissão RF; local de unit/precision/tokens; relações explicitamente declaradas. Confirmar se precisa executar JS: se sim, formato permanece recusado. Amostra não transfere autorização nem valida compatibilidade real.

L1 também precisa qualificar perfil OS verificável: fontes exatas RO,scratch próprio RW,sem rede/providers,256MiB/30s com mecanismo SO,cancelamento/negativas e receipt por versão/identidade. Nenhum ensaio privado é autorizado por este handoff. G4/G5/G6 não recebem PASS e o plano AP04-POR não muda.
