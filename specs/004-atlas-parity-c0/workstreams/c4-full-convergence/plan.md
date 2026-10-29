# Plano C4R

## Technical Context

Python biblioteca padrão e módulos ES existentes; protocolo é dependência pública independente. Renderers P03 permanecem congelados. Node 24/Playwright somente QA; Spec Kit 1.2.3 em ambiente Actions isolado.

## Constitution Check

ARC-01–09 e ADR-0001 preservados. Direção ADR-0002 previamente aceita continua registrada sem promover implementação/ciência. Sem produtor privado, P04 publicado, chamadas pagas ou operação do host.

## Desenho e ownership

Coordenador: leitura dos inputs por SHA, composição Git com três pais, documentação, manifests, PR e conciliação terminal.
Subagente runtime_p03: catalog/server/shell, módulo de composição e seus testes específicos.
Subagente ci_contracts: workflows, runners/auditores, browser integrado e negativos de fronteira.
Subagente independent_review: somente leitura e parecer, sem autoria.

O catálogo deriva project_metadata de fontes já validadas. O app importa renderers explicitamente e monta uma região semântica. O usuário escolhe propriedades; valores numéricos/string usam display_value e booleanos usam bool real. Contexto inclui fonte, snapshot e ID. A desmontagem acompanha expiração do snapshot.

## Verificação

Composição pura C1+C2+C3 sem conflitos por comparação de trees contra main. Preservar manifestos históricos, registrar desvios C4 de arquivos C1/C2 separadamente e validar origem de cada blob. C3 permanece byte-idêntico. Default dos auditores continua estrito; opt-in C4 limitado a paths e hashes finais.

Actions executa Windows/Ubuntu normal/-O com zero skips, isolamento/wheels, P01/C3, P03 focal e browser integrado. Não executar instalação/teste/HTTP/browser no host local. CI de entrada permanece evidência dos inputs, sem transferência ao C4.

## Encerramento

Os documentos versionados apontam o SHA técnico efetivamente testado. O commit documental requer CI e revisão próprias. O recibo externo da PR fixa seu SHA final e evita referência circular; qualquer mudança posterior reabre gates.
