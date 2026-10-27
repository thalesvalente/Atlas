# Resultado — ATLAS-PARITY-02-P01

**Data de composição:** 2026-10-27T12:03:16-03:00 (America/Fortaleza). **Destino Git:** `thalesvalente/Atlas`.
**PR:** [#9, aberta e Draft](https://github.com/thalesvalente/Atlas/pull/9).

## Decisão

**P01_CONTRACT_PACKET_READY**, com **P01_PARTIAL_INPUTS_EXPLICIT**.

A frente entregou a base semântica/documental que permite implementar os itens
compatíveis de C0 e classifica separadamente os que exigem evolução persistida.
A/B/C/D integrais não foram identificados; essa lacuna não foi transformada em bloqueio
total. O pacote não declara paridade integral com o legado, implementação de C0,
promoção canônica, release estável ou aceite científico.

## Identidade da entrega

| Objeto | Identidade |
|---|---|
| Baseline e código público de produto testado | `c2d00fb137cac1d62d6b7cb045ddbe055355a4c5` |
| Árvore da baseline | `5c65d3f42b7199250bb6df11c7cd4fbe37e7ee59` |
| Commit do pacote técnico efetivamente executado/revisado | `3a308ee78e185912959920d85a97cd511a70a764` |
| Árvore do pacote técnico | `03894a33271c030a72ccb7b016aeed943b11f525` |
| Branch | `work/atlas-parity02-p01-contracts-20261027` |
| Commit documental deste fechamento | resolver pelo HEAD da PR #9; não é gravado dentro de si mesmo |

O commit documental acrescenta recibos/manifesto e fecha marcações de tarefas. A lógica
do validador, as fixtures, os contratos e a matriz permanecem os bytes verificados do
commit técnico. O produto e `packages/protocol/**` permanecem os bytes da baseline.
A materialização local foi feita pelo conector GitHub depois de falha da conexão do
terminal; 162 blobs, árvore e objetos de commit foram conferidos por hash. É checkout
shallow, não alegação de histórico completo ou acesso ao host do operador.

## Entrega concreta

- [EVIDENCE-REGISTER.md](EVIDENCE-REGISTER.md): baseline, precedência de recibos, fontes lidas e limites.
- [INPUT-INVENTORY.json](INPUT-INVENTORY.json): 26 fontes públicas com path, blob SHA, SHA-256, tamanho e escopo de inspeção; entradas A/B/C/D ausentes.
- [CAPABILITY-PARITY.csv](CAPABILITY-PARITY.csv): 28 jornadas próprias, 18 colunas e as sete camadas exigidas, com gaps, owners e aceite.
- [PRESENTATION-CONTRACTS.md](../../../contracts/atlas-parity-02/p01/PRESENTATION-CONTRACTS.md): identidade, entidades, referências, relações, tempo, valores e comparação.
- [COVERAGE-CONTRACT.md](../../../contracts/atlas-parity-02/p01/COVERAGE-CONTRACT.md): população, denominador, unidade, seleção, perdas, desconhecidos e observação.
- [VALIDATION.md](../../../contracts/atlas-parity-02/p01/VALIDATION.md) e [exemplos](../../../contracts/atlas-parity-02/p01/examples/cases.json): gramática documental restrita, 46 fixtures e programa de validação offline.
- [DECISIONS-AND-GAPS.md](DECISIONS-AND-GAPS.md): decisões existentes, propostas novas e handoff delimitado a P02–P06.
- [Workstream Spec Kit](../../../../specs/004-atlas-parity-c0/workstreams/p01-contracts/spec.md): spec, clarify, plan, research, data model, checklist, tasks, analyze, execução e convergência.
- [INDEPENDENT-REVIEW.md](INDEPENDENT-REVIEW.md), [HANDOFF.json](HANDOFF.json) e [MANIFEST.sha256](MANIFEST.sha256): atribuição, resultados e integridade do pacote.

## Principais conclusões com evidência

A baseline já oferece busca, filtros, comparação, timeline, linhagem e referências
relacionadas. A matriz não reinventa essas capacidades. [Registro, E009–E013](EVIDENCE-REGISTER.md).

| Suporte observado | Jornadas |
|---|---:|
| Existente | 11 |
| Parcialmente preservado/apresentado | 10 |
| Representável, sem apresentação própria | 3 |
| Sem semântica genérica contratada suficiente | 3 |
| Origem anterior não observada | 1 |

São 11 itens de contrato vigente, 14 candidatas compatíveis de apresentação e três
propostas de evolução persistida. As 28 jornadas são próprias desta análise; não são
as doze jornadas atribuídas ao resumo não verificado de C.

**Preservação de entidades:** `entities` conserva o grafo completo; `runs` inclui só
`CreateAction`. A prova sintética reteve 13 entidades e uma execução; documento,
produto e metadados de tabela não viraram runs. O gap de navegação não é ausência de
representação. [E010/E013](EVIDENCE-REGISTER.md), `verification/published-payload.json`.

**Identidade:** fontes são enumeradas por ordem. O ensaio de reordenação confirmou que
`source-1` passa a designar outros bytes. A candidata preserva fonte/pacote + ID e não
promete links duráveis. Solução derivada testada pertence a P02; nova identidade
persistida exige desenho/decisão próprios.

**Referências e tempo:** menção continua neutra e deduplicada em ordem. Evento,
criação de documento, publicação, indexação e observação não são intercambiáveis.
A timeline atual usa todas as runs, enquanto filtros atuam na exploração; seu alcance
precisa ficar legível ou receber sincronização testada pelo owner.

**Tabelas e comparação:** métricas tipadas e proteção de inteiros grandes já existem.
Isso não cria grade tabular universal nem equivalência semântica entre produtores por
nome. Tipo, unidade, precisão, ordem, literal e ausências são conservados; compatibilidade
desconhecida não se torna positiva.

**Cobertura:** as sete camadas têm populações e observações distintas. Runs carregadas
não fornecem total do acervo. Denominador desconhecido continua desconhecido; `0/0`
não produz percentual. Sidecar permanece derivado e opcional.

**ADR-0002:** a direção foi aceita no [recibo posterior da PR #5](https://github.com/thalesvalente/Atlas/pull/5#issuecomment-6406839421).
Os bytes históricos não foram alterados. A frase antiga do catálogo sobre aceite
pendente é um gap de linguagem encaminhado a P02, sem reabrir a decisão já recebida.

## Verificações reais e seus limites

| Verificação | Resultado | Atribuição |
|---|---|---|
| Exemplos documentais/SDK | 46/46: 11 positivos e 35 negativos | código do validador e corpus no commit técnico 3a308ee |
| Probes do leitor público | 9/9 | fixtures sintéticas; leitor/catálogo inalterados |
| Python normal / otimizado | resultados idênticos | rerun dos mesmos casos, não 92 casos únicos |
| Regressões existentes de referências relacionadas | 11 testes, zero falhas/skips | baseline c2d00fb, checkout de fontes Linux/Python 3.12.14 |
| Auditoria arquitetural | PASS_SCOPED, zero findings | auditor existente, sem mudança de produto |
| Helpers Spec Kit | setup_plan, setup_tasks, check_prerequisites e resolve_template executados | workstream explícito e NO_PERSIST; zero escrita de ponteiro |
| Fontes da baseline/ownership | 162 arquivos existentes preservados, incluindo os 12 de packages/protocol | bytes conferidos; somente raízes P01 novas |
| QA independente | PASS_SCOPED; QA-P01-01 CLOSED | agente nativo sem autoria, provas e hashes no parecer |

QA-P01-01 encontrou overflow de `1e999` que podia escapar quando o tipo da coluna era
desconhecido. A leitura passou a recusar o valor antes da validação semântica; uma
negativa específica e a rechecagem independente fecharam o finding. Os logs iniciais
com 45 casos ficam como histórico de outro hash do validador; os resultados finais
são os logs `examples-final-*` e `published-payload.json`.

A execução foi no ambiente Linux de engenharia do CHAT; não foi instalação no host,
navegador ou piloto privado. CI histórica citada no registro pertence a e985ea3 e
não é atribuída a este HEAD. O workflow de produto pode executar automaticamente na
PR, mas os workflows atuais não executam o corpus documental P01. A observação de CI
após o commit de fechamento fica na descrição da PR e na resposta final, por SHA/run,
sem polling ou resultado terminal presumido. Sua integração com a QA de C0 cabe a P06.

## Estudos ausentes e próximo ato mínimo

O inventário delimitado examinou nomes de 10.771 entradas em seis archives e dois
textos fornecidos; nenhum estudo integral foi identificado. Não foi copiado código
privado e não se alegou ausência global. Os hashes de C informados continuam não
verificados sem seus bytes. Fonte/projeção/seleção/conversão do legado não observadas
ficam UNKNOWN_UPSTREAM. [Inventário](INPUT-INVENTORY.json).

**Próximo ato mínimo:** P02/P03 podem consumir as candidatas compatíveis e seus casos
no SHA técnico recebido; P06 pode agregar o pacote e executar a validação sobre os
objetos efetivamente integrados. P04/P05 mantêm a aquisição/observação operacional em
seus próprios limites e só fornecem resumos sanitizados autorizados. A/B/C/D completos,
se recebidos, serão reconciliados por bytes/hash sem interromper o avanço compatível.

**Raciocínio solicitado:** Max, fallback Extra High/xhigh. **REASONING_EFFECTIVE=UNVERIFIED**.
O texto da missão não mudou seletor nem forneceu telemetria. Três agentes nativos reais
foram usados, com ownership exclusivo e revisor sem autoria. Não houve aceite humano,
execução ou acesso simulados.
