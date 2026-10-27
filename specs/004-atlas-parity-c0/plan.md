# Plano agregador 004 — ownership e execução
Constituição ARC-01–09 e contratos 001–003 governam este incremento.
Stack existente: Python >=3.11, unittest, SDK e viewer separados; HTTP loopback,
JavaScript estático e Chromium apenas no runner de engenharia.
Nenhuma dependência de runtime nova, formato persistido novo ou extensão ativada.

## Ownership
| Frente | Responsabilidade exclusiva |
|---|---|
| P01 | workstreams/p01-* e contratos documentais recebidos |
| P02 | workstreams/p02-*, shell/catálogo/servidor/empacotamento |
| P03 | workstreams/p03-* e componentes novos isolados |
| P04 | somente coorte privada offline e recibo sanitizado atribuído |
| P05 | somente operação local/browser do host e recibo atribuído |
| P06 | agregadores 004, workstreams/p06-qa, testes/fixtures/scripts QA próprios e novo workflow |

P06 é único writer potencial do ponteiro ORQ. Nenhuma atualização do
`.specify/feature.json` é necessária: helpers usarão
`SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0` e
`SPECIFY_FEATURE_NO_PERSIST=1` no runner isolado.
Não editar workstreams de outras frentes.

## Etapas e dependências
1. Fixar base/tree e recibo #5; ler contratos e reutilizar evidência dos mesmos bytes.
2. Especificar requisitos P06, checklist de qualidade e tarefas; analisar cobertura.
3. Implementar provas comportamentais e contraprovas antes de alegar execução.
4. Publicar branch QA própria e PR Draft; CI faz instalação/testes reais fora do host.
5. Revisor nativo sem autoria examina delta final; resolver findings dentro de ownership.
6. Fazer consulta final de entradas. Sem P02 concreto, entregar QA útil aguardando
   handoff P02; não criar branch de composição nem aguardar frentes continuamente.
7. Com inputs suficientes, congelar SHAs incluindo código QA P06, compor em
   `integration/atlas-parity02-candidate-20261027`, testar e revisar bytes resultantes.

## Verificação
Harness existente atlas021: suite completa quatro células OS/modo, independência
instalada e três scripts browser explícitos (normal, adversarial e referências).
Novo atlas-parity02: unittest P06 quatro células, invariância por blobs Git,
wheel/assets/HTTP no consumidor isolado; Spec Kit 1.2.3 e helpers em dois OS.
Auditoria `speckit_audit.py --allow-presentation-delta` preservada, com sua
exceção histórica exata; nenhuma auditoria é reduzida para obter verde.

Incremento material P06: cenário Chromium de troca de pacote válido, cache CHANGED,
detalhe/seleção obsoletos e navegação fonte+ID, com mutação atribuída ao driver
sintético e checagem de bytes contra o estado intencional, em job próprio.
