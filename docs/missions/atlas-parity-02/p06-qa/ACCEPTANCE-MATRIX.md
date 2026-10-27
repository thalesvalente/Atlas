# Matriz de aceitação P06
Resultado novo pertence ao SHA indicado em CI-EVIDENCE.json. Inspeção não é
execução. PASS_SCOPED limita-se aos cenários exercitados, sem paridade global.
Owners de execução de CI: P06/runner hospedado; owner do produto/shell: P02.

| Requisito | Camada e owner | Prova existente atribuída | Prova adicional P06 | Resultado/limite |
|---|---|---|---|---|
| ARC-05 viewer sem R4 | Pacote; P02 | clean_install histórico e atual | wheel/HTTP fora do checkout, find_spec e import sob sys.prefix | PASS no d21; código final QA verificado |
| ARC-02 SDK sem viewer | Pacote; P01/protocolo preservado | clean_install instala SDK sozinho e executa CLI | reuso do harness real quatro OS/modos | PASS no d21; não é leitura de produtor |
| FR-001 bytes do protocolo/fontes | Contrato/entradas; P06 guarda | blobs da base fixada | 64 arquivos protegidos + contraprovas de mudança/remoção/adição | PASS d21, incluindo read_model.py; 162 blobs originais iguais |
| IDs repetidos entre fontes | Catálogo; P02 | tests/viewer e browser referências | fontes com valores/títulos/mentions distintos, snapshot/dossiê/rebuild | PASS d21; identidade fonte+ID |
| Pacote inválido e preview | Catálogo; P02 | regressões de pacote/ZIP | fontes inseguras/perfil desconhecido/estado ausente ao lado de fonte válida | PASS d21; sem fallback para outra fonte |
| Pacote válido trocado e links antigos | Aplicação baseline; P02 | cache CHANGED no teste existente | browser P06 troca metadata sintética validada; fecha detalhe antigo e mantém somente seleção B | PASS d21: 10 checks no cenário Chromium P06 |
| UNKNOWN/estados/revisão | Modelo público; P01/P02 | validação SDK vigente | combina estados, revisão, integridade, cache e datas ausentes em três projeções | PASS d21; sem promoção científica |
| Precisão/ausência | Modelo e UI; P02 | browser adversarial e SDK | >2^53, zero, false, null, texto, decimal/precision, unidade distinta, perda rejeitada | PASS d21; sem arredondamento silencioso |
| Mentions e direção | Modelo; P01/P02 | related_references vigente | URI/HTML literais, bloqueio socket/urlopen/Popen; relações iguais | PASS d21; Python não qualifica DOM |
| Tempo e linhagem | Modelo/UI; P02 | timeline/lineage do harness vigente | offsets +/-, ordem absoluta inválida, UNKNOWN e arestas exatas | PASS d21; origem declarada preservada |
| Limites de leitura e dados adversariais | SDK; P06 verifica | suite test_protocol_adversarial e storage reais | reexecução pelo runner completo | PASS d21; sem certificação de host adversarial |
| URI/HTML no DOM e rede | Browser engenharia; P02/P06 | browser normal/adversarial/referências | três chamadas explícitas reais no atlas021 | PASS d21 19/23/22 checks por cenário, zero erros/requisições externas |
| CSP/Host/Origin e allowlist | HTTP; P02 | testes HTTP existentes | wheel servido byte-idêntico, paths não publicados 404, origens/host 403 | PASS d21 em quatro células |
| Assets no wheel | Pacote/HTTP; P02 | package-data existente | todos os assets do wheel correspondem à allowlist instalada e bytes HTTP | PASS d21; sem alterar pyproject/servidor |
| Navegação/foco/reflow | Browser engenharia; P02/P06 | 390px, teclado e CSS200 no harness | cenário de troca adiciona foco/Enter e 390 px após troca | Histórico atual d21 PASS; incremento d21 PASS |
| Coleção OS/modo | CI; P06 | runner descobre SDK/QA/viewer | descoberta P06 explícita + runner completo, unittest.assert* sob -O | d21:98 por célula,12 novos incluídos; seleções sobrepostas |
| Helpers oficiais e reserva004 | Governança; P06/ORQ | instalação 1.2.3 existente na baseline | CLI e helpers reais Ubuntu/Windows, NO_PERSIST=1 | d21 PASS; ponteiro compartilhado não alterado |
| Componente novo P03 | Componente isolado; P03 | INPUT_MISSING | nenhuma implementação recebida/revisada | NOT_RECEIVED; opcional para C0 |
| Composição P02+P06 | Aplicação composta; P06 | contrato atual sustenta conjunto mínimo | faltam SHA/tree/handoff P02; nenhuma composição realizada | NOT_COMPOSED; não declarar integração |
| Coorte real P04 | Pacote real; P04 | nenhum recibo atual recebido | fora do Git público e da execução desta frente | INPUT_MISSING |
| Baseline local e browser host P05 | Host; P05 | LOCAL-REAL01/PR #5 é evidência histórica atribuída | nenhuma instalação/operação/browser do usuário testados aqui | NOT_RUN_BY_P06; não inferir estado atual |
| Candidata final no host | Host; P05 | inexistente porque composição ausente | recibo específico exigido futuramente | NOT_RUN |
| Promoção humana | Decisão; operador | ADR0002 aceita só como direção de estabilização | nenhuma autorização de promoção nesta missão | NOT_AUTHORIZED_NOT_RUN |

Cobertura: os denominadores do browser descrevem apenas as fixtures e entidades
do cenário. Estudos completos A/B/C/D não recebidos impedem um denominador de
paridade completa. Não somar quatro OS/modos, seleções focais, checks browser ou
reruns como testes únicos. 98 é o número de unittest do runner por célula no d21;
os 12 P06 já estão dentro desses 98.
