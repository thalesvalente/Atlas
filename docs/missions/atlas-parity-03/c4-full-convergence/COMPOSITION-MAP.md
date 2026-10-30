# Mapa da composição C4

A candidata parte da tree C1. C2 e C3 acrescentam 180 arquivos sem conflito frente à main fixada; a tree composta contém 464 blobs. O commit c120f8ae9e455e19b4e0bcd35f47ec0fd7a0117c tem os três inputs como pais ordenados. O protocolo e os exemplos/fixtures herdados conservam seus blobs.

BLOB-PROVENANCE.csv enumera cada path diferente da main, seu blob final e a origem C1/C2/C3 ou overlay C4. Os manifestos históricos continuam idênticos; divergências autorizadas posteriores não são escondidas reescrevendo manifestos de origem. MANIFEST.sha256 cobre somente todos os paths de autoria C4, incluindo documentação e esta trilha, exceto seu próprio arquivo. Inputs anteriores são ligados por trees/manifests fixados em INPUT-SHAS.json.

Runtime C4 altera catalog.py, server.py, app.js, index.html e style.css e acrescenta parity03_p03_composition.js e testes específicos. Os quatro assets P03 e parity02_p03_metadata.py permanecem congelados. O app importa explicitamente o módulo de composição, que importa renderMetadata/renderTable; renderCandidate não é chamado. Metadados derivam do read model validado e erros ficam em apresentação, sem alterar report/status/fonte. A tabela depende de seleção explícita, preserva display_value/bool/null e separa tipos/unidades.

CI C4 adapta os gates somente na branch C4 e acrescenta oráculos de integração. Default de auditoria e gates históricos continuam estritos. O gate P01/C3 e seus 95 arquivos permanecem byte-idênticos. Cada ajuste possui blob e origem registrados em BLOB-PROVENANCE.csv.

Aquisição de engenharia: snapshot local de edição parcial, sem .git, construído de blobs públicos conferidos. O clone Git falhou por restrição MSYS; nenhuma remediação do host foi tentada. Composição e publicação usam GitHub API; Actions obtém checkout integral real.

Desvio técnico explícito C2: apenas o teste de isolamento test_existing_app_does_not_load_p03 foi substituído por uma asserção de composição representável no C4. Os 24/25 demais arquivos congelados e 55/56 entradas do manifesto P03 preservam seus bytes; a exceção do teste tem path e SHA256 atuais pinados no gate C4. O manifesto e a branch C2 não foram reescritos. Nenhum teste foi omitido ou marcado skip. O finding C4-R01 é fechado por essa adaptação, sujeita à execução real no SHA C4.

Caveat de leitura de engenharia: a primeira leitura PowerShell carregou o perfil existente, que reportou falhas de Conda e acesso ao registro; as leituras seguintes usaram login:false. Não houve execução de produto/teste/servidor local ou remediação de políticas. Downloads posteriores obtiveram somente evidências públicas de Actions em destino isolado.

A primeira execução C4 (d897a8f82a95ea1d7714dd6236390b64931dc797) terminou RED: 24/31 jobs passaram, sete falharam em três incompatibilidades de harness. CI-EVIDENCE.json fixa runs/causas. Os reparos posteriores restringem seletores ao contexto correto e autorizam o único guard adaptado também no browser focal, sem alterar runtime, valores esperados ou registrar skips. Fresh-document deep link exige reload real, sem assumir que mudar fragmento cria documento. Todas as provas serão reexecutadas no SHA corrigido.

A segunda rodada (3e65ac5175e03ded6cc85765322cc9314a29bfe2) terminou RED27/31: os quatro browsers C4 esperavam reescrita de URL obsoleta. O contrato existente conserva URL rejeitada visível com explicação. O reparo exclusivo do harness observa o snapshot novo no DOM e preserva as asserções de expiração/rejeição/notice; runtime e fontes herdadas não mudam. Os25checks anteriores e bytes de cópias sintéticas eram aprovados, sem equivaler a PASS do gate completo.

O SHA a21bacf35c1a7571af39f7366e8f08457db4a49c passou 31/31 jobs, mas não foi aceito: a revisão independente encontrou C4-R02. A regra global de cabeçalhos convertia unidades/IDs P03 para maiúsculas visualmente. O overlay C4 agora reseta text-transform somente nos th de .atlas-p03-embedding .atlas-p03-table, sem tocar CSS P03 congelado. O browser acrescenta oráculo de computedStyle e igualdade innerText/textContent/data-row-id, com mg/L e µg/L literais. Nova CI e revisão visual do SHA são obrigatórias; verde anterior não fecha o finding.

Fechamento técnico: 54461f7494df7c0e54a176cf7df3f16ee43e2edb, tree 73e53237b1362dcd8b65b120acb4c47dfcdf8ba4; seis workflows, 31/31 jobs e revisão independente PASS. C4-R02 foi fechado por prova de CSS, computedStyle e inspeção dos PNGs próprios. O overlay documental posterior exige seus próprios gates por SHA, sem transferência de prova.
