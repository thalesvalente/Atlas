# AP04 — análise de conformidade F4, bloqueios e soluções pesquisadas

**Data:** 2026-10-31. **Estado:** ANALYSIS_COMPLETE / EXECUTION_CHANGE_PROPOSED_NOT_APPROVED.
**Natureza:** análise de coordenação e pesquisa técnica; não é nova revisão independente de código, execução de testes, qualificação de host ou autorização de implementação.
**Plano de referência:** AP04-POR-v1.0-draft. Nenhum documento normativo, prompt histórico, manifesto, guard, branch de produto, PR ou fonte científica é alterado por esta publicação.

## 1. Identidades consultadas

| Frente | PR | Commit | Árvore | Resultado declarado e escopo |
|---|---|---|---|---|
| F4-C0 | #19 | d498504cd2c4d230088f86e04e55624bbe32df79 | 4f0c6360d429507af1946a094c27b790c9894477 | Contrato sucessor revisado; nenhuma implementação |
| F4-C1 | #16 | 4764eb0ebb38cd272b1a5e5fafbb103e72b8e105 | 1ba41dd01b118a008ca33061131e9181a2600548 | Grafo sintético 2911 nós/1595 relações qualificado |
| F4-C2 | #18 | 258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7 | f268d4cf450cf5baa73c5d51e34fc0d6fba3a59f | Mecanismos sintéticos qualificados; aquisição operacional bloqueada |

Baseline comum F2: 54bb16d350f7bc34fafb95438bd64a2397d58bf3.
Pacote arquitetural aprovado: c3ea1e82938fd61cc5a22fee973352715a5bb527; aprovação humana APPROVED_SCOPED na PR #15, comentário 6539419419.
Prompts e dependências da onda F4: c4f1204d75222c1a72678d22f1a4b23f1a33ab8f.

Foram lidos metadados das PRs, contratos, guardrails F2, código de aquisição/parser C2 e registros focais. A API de jobs confirmou 4/4 success em C2 run 41213548641 e C1 run 41214242548. As contagens detalhadas de testes e os pareceres independentes são atribuídos aos respectivos recibos; esta análise não reexecutou suites, não recontou todos os logs e não inspecionou manualmente pixels/ZIPs.

## 2. Veredito de conformidade

**A direção arquitetural permanece preservada no escopo das fontes consultadas; a F4 não está concluída.**

- C0 implementou a obrigação documental de precedência do reader003 apenas para a apresentação opcional O3. O contrato histórico, Catalog, SDK e via Caderno permanecem separados.
- C1 resolveu o bloqueio imediato de tamanho com modelo completo e janela SVG. Não é prova de consumo do corpus privado nem do teto combinado de 10000 nós/100000 relações.
- C2 terminou corretamente BLOCKED_EXACT: a aquisição operacional não está disponível, apesar de CI focal verde sobre formatos inventados.
- Sem evidência de migração do acervo, alteração do R4, promoção científica ou abertura de nova superfície no runtime nesses três resultados. Isso é uma conclusão documental/por código lido, não auditoria de todas as operações locais.
- G4 exige aquisição real e isolamento no ambiente autorizado; G5 exige composição/CI global; G6 exige demonstração local em navegador. Nenhum pode ser promovido pelos resultados focais.
- RO-Crate, Process Run e Caderno continuam a via padronizada. HL7/FHIR permanece capacidade futura por domínio, sem implementação/conformidade anunciada.

**Problema do planejamento operacional:** a decomposição C2/L1 contém uma circularidade agora evidenciada. Ela foi introduzida na preparação dos prompts, não por um desvio silencioso dos agentes executores. Deve ser corrigida de forma explícita e aprovada.

## 3. Achados e consequências

### F4-AUD-01 — circularidade de dependências (prioridade alta)

DEPENDENCIES.json exige C2 pronta antes de L1. O contrato/recibo C2 envia para L1 a necessidade de schema estrutural observado e perfil de isolamento, sem os quais C2 não fica pronta. Resultado: C2 espera uma atividade LOCAL que o próprio sequenciamento impede de começar.

**Não é solução:** declarar C2 pronta, executar --synthetic-fixture sobre fonte real, dispensar isolamento, ou mandar L1 executar aquisição ainda desabilitada.

**Proposta:** um precursor restrito LOCAL de recuperação de evidência estrutural existente e preflight de capacidades, sem executar a aquisição C2 e sem conceder G4. Depois, C2 completa engenharia e qualificação em fixtures; L1 continua responsável pela prova no host e fonte autorizados.

### F4-AUD-02 — formato de ensaio não é formato observado (prioridade alta)

O parser publicado aceita explicitamente atlas-legacy-synthetic-source/0.1.0, synthetic=true, e um bloco HTML igualmente identificado como sintético. Esse é um contrato útil de teste, mas não um adaptador qualificado da projeção histórica. reader.prepare recusa a operação quando synthetic_fixture não é True; essa negação é correta enquanto faltarem as condições.

Uma consulta somente leitura a uma versão fixada do produtor legado trouxe pistas verificáveis de projeção JSON inerte e validação de estruturas. Não foram executados geradores nem acessados os arquivos privados do Windows. Esse código de referência é uma fonte candidata de especificação, NÃO prova de que o arquivo local atual foi produzido exatamente por ela. Nenhum trecho, identificador privado, amostra ou schema proprietário desse produtor foi copiado para este relatório público.

**Solução:** obter contrato de entrada observado e sanitizado; selecionar um perfil específico da projeção histórica; implementar parsing original externo, sem importar/copiar R4. Conservar o perfil sintético como teste, sem renomeá-lo para simular uma fonte real.

A amostra mínima deve conter delimitador/formato, chaves/tipos, campos opcionais, estrutura de tabela/linha, referências, origem de identidade e parent keys, unidades/precisão, campos ausentes e casos não admitidos. Valores devem ser inventados e publicados somente após revisão de privacidade/liberação aplicável. Reutilizar primeiro os recibos F1 locais já produzidos; nova leitura de fonte exige autorização específica F4.

Não confundir quantidade de records com quantidade de nós de linhagem: as contagens F1 são de camadas diferentes. O perfil real deve mapear cada camada corretamente e não reduzir a árvore apenas porque um modelo sintético deriva nodes de records.

### F4-AUD-03 — hard budgets não implementados (prioridade alta)

reader.py faz checagem cooperativa de prazo entre etapas e declara ausência de isolamento duro. SECURITY-AND-LIMITS.json mantém HARD_BUDGET_UNVERIFIED para memória e tempo. São lacunas concretas de implementação/qualificação; não apenas metadados que uma sessão LOCAL deve preencher.

**Proposta Windows pesquisada:** supervisor externo mínimo, worker iniciado sob limites antes de processar dados, Job Object com limites de committed memory e encerramento do grupo, prazo de tempo decorrido supervisionado fora do worker. Fixar o contador e o escopo medidos: memória comprometida do processo/job não equivale automaticamente a RSS, working set ou memória total do sistema.

JOB_OBJECT_LIMIT_JOB_TIME é tempo de execução em modo usuário; não é um limite de tempo decorrido para uma leitura bloqueada. Para 30 segundos, usar supervisão monotônica de deadline, encerramento via TerminateJobObject e confirmação de que não ficaram descendentes. KILL_ON_JOB_CLOSE deve cobrir queda do supervisor; herança/breakaway precisam ser controlados e testados. A plataforma deve falhar fechada se não conseguir configurar/verificar essas proteções.

Job Objects não resolvem sozinhos acesso a arquivos/rede. Propostas de implementação precisam de testes reais de alocação acima do limite, espera bloqueada, filho descendente, falha do supervisor, ausência do mecanismo e publicação abortada de descriptor. Não confundir uma exceção simulada em teste com limite imposto pelo SO.

### F4-AUD-04 — isolamento de FS/rede é obrigação distinta (prioridade alta)

Allowlist de strings, scratch privado e ausência de chamadas de rede no código não provam que o processo é impedido pelo SO de escrever na origem ou abrir outros arquivos/rede. O contrato F2 já exige essa separação e recusa quando ela não for provada; não é requisito novo criado por esta análise.

**Proposta técnica a revisar:** AppContainer/LPAC ou perfil nativo equivalente, capabilities mínimas e sem rede, runtime necessário de leitura, acesso à fonte estritamente read-only e saída restrita ao scratch. Um broker/launcher com handles exatos read-only é uma opção a estudar sem modificar ACLs das fontes; a fronteira de confiança do broker e dos descendentes deve estar documentada e coberta. Não afirmar que essa combinação já funciona no host.

Criação de perfil, concessão de capacidades ou ACLs somente poderá ocorrer no escopo explicitamente autorizado, nunca para contornar a sandbox do executor. Não alterar ACLs de originais, firewall global, permissões de drives ou ambiente Conda existente por conveniência. Uma máquina sem capacidade suportada permanece bloqueada.

Ubuntu exige perfil próprio: cgroup v2 pode limitar recursos; restrição de arquivo/rede precisa de controles separados. resource.setrlimit é Unix e não é solução portátil para Windows. Qualificação em runners não prova configuração do computador local.

### F4-AUD-05 — limite auxiliar de 600000 valores (risco de composição)

F4-C1-CONTRACT explicita que copyJSON recusa mais de 600000 valores visitados, mesmo quando um payload pode estar abaixo das contagens máximas. O stress 10000/100000 tinha 81008070 bytes e ultrapassava também 32 MiB: sua recusa NÃO qualifica o caso de muitas relações dentro do envelope válido. O teste 10000 nós/zero relações é prova diferente.

**Solução:** medir valor count/bytes/profundidade do descriptor real ou estruturalmente equivalente; incluir testes 599999/600000/600001 e um descriptor válido dentro de 32 MiB que exerça o limite, quando factível. Registrar capacidade sintética comprovada separada da real. Se o limite auxiliar impedir um descriptor permitido pelo contrato aprovado, otimizar representação/cópias ou solicitar alteração versionada do limite; não reduzir silenciosamente a população e não afirmar capacidade universal.

### F4-AUD-06 — memória e localização da saída precisam de integração explícita

O parser conserva texto e lexemas de várias subárvores, além dos objetos; o leitor pode conservar mais de uma cópia de bytes durante as verificações. Isso é risco de amplificação sob 256 MiB, não benchmark já demonstrado. Medir com limites nativos efetivos; preferir hashes em blocos e spans/offsets para evitar cópias desnecessárias, mantendo literalidade.

Distinguir dois destinos privados: recibos podem seguir a raiz .local ignorada autorizada pela missão; o descriptor/cache temporário deve respeitar a exigência F2/C2 de ficar FORA do checkout e do acervo. Mover a ferramenta para mudar artificialmente sua detecção de REPOSITORY não é solução de segurança. Todo destino real precisa de autorização e prova de isolamento apropriadas.

### F4-AUD-07 — interpretação de CI e guards históricos

4/4 jobs C2 verdes provam os mecanismos sintéticos declarados, não aquisição real. O registro C2 discrimina 34 PASS por célula Windows e 33 PASS + 1 skip específico de ACL Windows por célula Ubuntu. Não anunciar zero skips universal nem invalidar automaticamente um caso exclusivo de SO; separar aplicabilidade e cobertura.

Guards globais que recusam novos PLAN.md/fixtures são bloqueios previstos de sucessão por ownership. Preservá-los foi correto. Não abrir outra campanha independente de reparo para cada PR somente para alterar sua cor: a C4 deve qualificar composição e topologia exatas e tooling, depois do SHA C3 conforme a sequência vigente. Nenhum guard deve perder o comportamento negativo histórico ou receber permissão genérica.

## 4. Soluções e retomada recomendadas

### Proposta de revisão operacional F4-EXECUTION-REVISION-01 — ainda não aprovada

**Mudar somente o antecedente operacional que está faltando:** adicionar precursor LOCAL de insumo, denominado L0 nesta proposta, ANTES da conclusão de C2.

- Entrada: autorização explícita de caminhos/recibos e finalidade. Priorizar metadados estruturais já produzidos por F1; não regenerar fontes, escanear discos ou executar o leitor bloqueado.
- Saída privada: localização/versão/fingerprint e estrutura observada. Saída pública somente sanitizada, liberada e versionada: esquema estrutural, exemplo inventado e limites por camada. Nenhum valor RF, path privado, ID ou digest de fonte deve ser publicado.
- Preflight de SO pode usar apenas fixtures temporárias inventadas e capacidades já autorizadas. Não reconfigurar host para contornar restrição e não certificar o processamento de fonte real.
- L0 não aprova G4, não implementa o produtor e não substitui L1.

**Em paralelo, na branch existente C2:** duas áreas de engenharia com ownership separado: (A) adaptador do perfil observado, assim que houver insumo; (B) supervisor/isolamento de SO com testes sintéticos. Uma terceira responsabilidade faz revisão independente sem autoria. Não criar worktrees/clones ou duplicar writer na branch.

**Depois:** C2 com CI e revisão completas pode receber READY_FOR_LOCAL_QUALIFICATION; C3 consome os SHAs C0/C1/C2/F3B; C4 qualifica CI global após C3 congelar; L1 executa a prova LOCAL em fonte explicitamente autorizada; F5 demonstra a jornada com a fonte privada após autorizações próprias. C0 e C1 não devem ser refeitos.

Uma alternativa de começar C3 sem C2 pronta poderia aproveitar fixtures válidas, mas altera a dependência atual de C3; NÃO é a recomendação padrão nem uma autorização concedida aqui.

## 5. O que depende de aprovação e o que não depende

**Já cabe à engenharia existente, respeitado o ownership:** implementar controles de recursos/isolamento exigidos, acrescentar contraprovas, desenvolver parser externo original baseado em perfil documentado, preservar fonte e corrigir defeitos dentro do contrato.

**Exige decisão explícita antes de executar:** antecedente L0 no sequenciamento, fonte/recibos privados a acessar nesta finalidade, publicação de qualquer informação derivada privada, configuração nova de sandbox/ACLs no host, ampliação de limite, mudança de formato/precedência, antecipação de C3 ou flexibilização de segurança. O AP04-POR e prompts antigos permanecem inalterados até a revisão aprovada.

**Não autorizado por esta análise:** merge, release, deploy, promoção, migração, limpeza, mudança do R4, fonte privada nova, File API implementada, G4/G5/G6 aprovados ou execução da revisão operacional proposta.

## 6. Matriz objetiva de aceite de C2 e L1

| Predicado | Prova exigida |
|---|---|
| Perfil de origem real | Observação estrutural autorizada + vínculo a produtor/snapshot, sem confundir fonte sintética |
| Literalidade | Uma linha RF real comparada privadamente, todas as linhas selecionadas conservadas e ausências/gaps explícitos |
| Confinamento | Tentativas reais em fixture de escrita na origem, leitura fora da allowlist e rede negadas pelo SO |
| Memória | Configuração consultada + tentativa de ultrapassar 256 MiB recusada/encerrada, métrica e escopo definidos |
| Prazo | Worker bloqueado é terminado pelo supervisor até o deadline com tolerância medida; descendentes não sobrevivem |
| Atomicidade | Falha/timeout/mudança de fonte não publica descriptor utilizável; originais byte-idênticos |
| Independência | Viewer/SDK funcionam sem a ferramenta; tool fora dos wheels e sem import R4 |
| Capacidade conjunta | Descriptor respeita 32 MiB/depth/counts e passa a condição real de 600000 valores, ou alteração aprovada |
| Publicação | Código, testes e recibos públicos no Git por SHA; privados apenas em destino autorizado |

## 7. Fontes primárias públicas e de projeto

### Projeto, por identidade imutável

- PR #18: https://github.com/thalesvalente/Atlas/pull/18 ; reader/parser/READER-CONTRACT/SECURITY-AND-LIMITS no SHA 258eda6153ffe602d3fa8e6b4fe7a2ad74edbbd7.
- PR #16: https://github.com/thalesvalente/Atlas/pull/16 ; F4-C1-CONTRACT no SHA 4764eb0ebb38cd272b1a5e5fafbb103e72b8e105.
- PR #19: https://github.com/thalesvalente/Atlas/pull/19 ; reader.ap04-legacy-presentation-v0.2.md no SHA d498504cd2c4d230088f86e04e55624bbe32df79.
- Dependências da onda: docs/missions/atlas-parity-04/f4-wave-launch/DEPENDENCIES.json no SHA c4f1204d75222c1a72678d22f1a4b23f1a33ab8f.
- Segurança F2: docs/missions/atlas-parity-04/f2-legacy-contract/SECURITY-AND-INTEROPERABILITY.md no SHA c3ea1e82938fd61cc5a22fee973352715a5bb527.

### Pesquisa externa oficial, consultada em 2026-10-31

- Microsoft, Job Objects: https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects
- Microsoft, JOBOBJECT_EXTENDED_LIMIT_INFORMATION: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information
- Microsoft, JOBOBJECT_BASIC_LIMIT_INFORMATION: https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_limit_information
- Microsoft, Launch an AppContainer: https://learn.microsoft.com/en-us/windows/win32/secauthz/implementing-an-appcontainer
- Microsoft, TerminateJobObject: https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-terminatejobobject
- Microsoft, WaitForSingleObject: https://learn.microsoft.com/en-us/windows/win32/api/synchapi/nf-synchapi-waitforsingleobject
- Python 3.12, resource: https://docs.python.org/3.12/library/resource.html
- Python 3.12, subprocess: https://docs.python.org/3.12/library/subprocess.html
- Linux kernel, cgroup v2: https://docs.kernel.org/admin-guide/cgroup-v2.html

As opções pesquisadas são propostas de engenharia, não implementações validadas nesta análise. A disponibilidade de um mecanismo na documentação não prova que esteja acessível/configurado no host do operador.

**END-OF-F4-ANALYSIS — EXECUTION_CHANGE_PROPOSED_NOT_APPROVED**
