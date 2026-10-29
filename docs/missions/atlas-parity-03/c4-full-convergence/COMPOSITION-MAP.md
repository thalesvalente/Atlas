# Mapa da composição C4

A candidata parte da tree C1. C2 e C3 acrescentam 180 arquivos sem conflito frente à main fixada; a tree composta contém 464 blobs. O commit c120f8ae9e455e19b4e0bcd35f47ec0fd7a0117c tem os três inputs como pais ordenados. O protocolo e os exemplos/fixtures herdados conservam seus blobs.

BLOB-PROVENANCE.csv enumera cada path diferente da main, seu blob final e a origem C1/C2/C3 ou overlay C4. Os manifestos históricos continuam idênticos; divergências autorizadas posteriores não são escondidas reescrevendo manifestos de origem. MANIFEST.sha256 cobre somente todos os paths de autoria C4, incluindo documentação e esta trilha, exceto seu próprio arquivo. Inputs anteriores são ligados por trees/manifests fixados em INPUT-SHAS.json.

Runtime C4 altera catalog.py, server.py, app.js, index.html e style.css e acrescenta parity03_p03_composition.js e testes específicos. Os quatro assets P03 e parity02_p03_metadata.py permanecem congelados. O app importa explicitamente o módulo de composição, que importa renderMetadata/renderTable; renderCandidate não é chamado. Metadados derivam do read model validado e erros ficam em apresentação, sem alterar report/status/fonte. A tabela depende de seleção explícita, preserva display_value/bool/null e separa tipos/unidades.

CI C4 adapta os gates somente na branch C4 e acrescenta oráculos de integração. Default de auditoria e gates históricos continuam estritos. O gate P01/C3 e seus 95 arquivos permanecem byte-idênticos. Cada ajuste final terá blob e origem registrados antes de publicar.

Aquisição de engenharia: snapshot local de edição parcial, sem .git, construído de blobs públicos conferidos. O clone Git falhou por restrição MSYS; nenhuma remediação do host foi tentada. Composição e publicação usam GitHub API; Actions obtém checkout integral real.

Desvio técnico explícito C2: apenas o teste de isolamento test_existing_app_does_not_load_p03 foi substituído por uma asserção de composição representável no C4. Os 24/25 demais arquivos congelados e 55/56 entradas do manifesto P03 preservam seus bytes; a exceção do teste tem path e SHA256 atuais pinados no gate C4. O manifesto e a branch C2 não foram reescritos. Nenhum teste foi omitido ou marcado skip. O finding C4-R01 é fechado por essa adaptação, sujeita à execução real no SHA C4.

Caveat de leitura de engenharia: a primeira leitura PowerShell carregou o perfil existente, que reportou falhas de Conda e acesso ao registro; as leituras seguintes usaram login:false. Não houve execução de produto/teste/servidor local ou remediação de políticas. Downloads posteriores obtiveram somente evidências públicas de Actions em destino isolado.
