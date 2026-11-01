# AP04-F4-C2-A — PLAN / EXECUTE / REVIEW

Prompt: Atlas `315f7dbeffc80822e96068eed6b4af3193d1b6a7`; PR Draft #18; ownership exclusivo do mapeador C2-A e novos recibos. HEAD inicial `e349a09d439d292011bca4c0994cf8ab3e3fbf9f`, árvore `1ceb61ad7693862b9fddcd0ee3cd0c3378bd38df`.

PLAN: leitura de `AGENTS.md`, F1 sanitizada, contrato F2, R4 privado apenas por GitHub no SHA autorizado; análise de `records`, `lineage_graph`, `result_tables` e histórico. Proibir alteração de R4, leitor/isolamento owner B, SDK, viewer, protocolo, Caderno, guards globais, manifestos e feature.json. Nenhuma criação de clone ou worktree.

EXECUTE: commits `228d1e1a10ea17874f0078f491e4418c56cf5969` e `dcd219bf592f47590413424adfdf6513a0daa18f`; correção do mapeamento de chaves estruturais, preservação de metadados adicionais e negativos de fonte v5 com valores inventados. JSON extraído inerte de script#data; não executar R4/HTML/JS, URL, links nem provider.

REVIEW: CI focal de código `41269925191`: 4/4 SUCCESS no `dcd219bf592f47590413424adfdf6513a0daa18f`; 60 PASS em cada Windows e 59 PASS/1 SKIP ACL em cada Ubuntu. 22 objetos históricos confirmados por SHA no commit original, wheels SDK/viewer independentes PASS. Sem subagentes nativos disponíveis; a inspeção deste autor não substitui revisão independente. Os caminhos deste diretório não constam do checker de ownership exato C2; o HEAD documental requer reconciliação pelo owner do checker, sem bypass. O descriptor 0.2.0 não suporta todo parent_key estrutural: decisão K/ARC-09 pendente. G4 continua bloqueado.
