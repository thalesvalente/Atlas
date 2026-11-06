# Plano — Feature 006 / Atlas N02

## Technical Context

Node 24 e módulos built-in; nenhum pacote novo. Ferramenta `tools/atlas_retention_audit.mjs`
separada do viewer, reutilizando buildRetentionPlan, selectionKey e snapshotKey F005.
Documentos JSON limitados a 64 MiB/profundidade 128; corpus autorizado lido em blocos
64 KiB, nunca varrido. Paths apenas nos argumentos explícitos do operador.

## Constitution Check

ARC-01–09 preservadas: parecer derivado, read-only, protocolo/DTO público inalterado,
nenhum produtor importado, sem ciência aprovada, migração ou retirada. A ferramenta
host fica fora do runtime. Nenhum desvio arquitetural ou aceite ARC-09 é necessário.
Manifestos históricos, aceites A01/T015 e branches originais permanecem intactos.

## DAG, owners e integração

O0 recuperar contrato/código → O1 N02 (root produto/docs || recover_n02 testes ||
verify_n03 workflow; n02_security revisão independente) → O2 composição com N03
por root → O3 testes + review independente + Actions/Codex Review do composto → O4 LOCAL.

- Root: worktree `wt-n02`, branch `feat/atlas-n02-retention-readonly-20261106` a partir
  da Feature005 aceita; único writer do produto e spec006.
- recover_n02: somente `scripts/qa/test_retention_audit.mjs` e fixture correspondente.
- verify_n03: somente novo workflow `.github/workflows/atlas-retention-audit.yml`.
- n02_security: leitura e contraprovas isoladas, sem autoria no produto/testes versionados.
- Root compõe com cherry-pick -x numa branch própria a partir do SHA N03, preservando
  autor e vínculo ao commit N02. Nenhum merge em PR, main ou branch anterior.

A PR composta será empilhada na branch F005, mostrando N03 e N02 sem modificar as
PRs anteriores. Assim os workflows existentes qualificam as mudanças de UI N03 no
novo SHA e o workflow N02 qualifica a ferramenta em Ubuntu/Windows. Não reexecutar
runs da N03 individual, já verificados. Os testes Node não têm modo Python -O;
normal/-O do viewer continuam nos workflows existentes.

## Decisões e modelo de dados

Usar o exportador F005 como oráculo de transporte evita copiar regras de identidade,
tipos, lexemas, proteção e tabelas. Comparar JSON serializado considera mapas internos
sem protótipo; strings raw_json conservam ciência numérica sem conversão.

O contrato sanitizado não é o inventário privado nem especifica sua serialização
completa. Definimos envelope versionado `atlas-retention-inventory/1`, mantendo os
quatro campos N01-R requeridos e vínculo explícito a plano/snapshot. A adaptação das
linhas privadas pertence ao LOCAL, sem rehash/rescan integral presumido.

Não há resolução de paths vindos de conteúdo. CLI recebe roots e mappings por ID;
referências científicas ficam inertes. Um hash externo ancora o inventário; outro
ancora o snapshot. Arquivos são abertos com flags somente leitura/no-follow/nonblock
quando suportadas, com lstat de todos os componentes, fstat antes dos bytes, checagens
antes/depois e hash. Symlinks, junctions, hardlinks e aliases não são admissíveis.
Proteção não depende do sucesso do hash; backup/restore e fechamento integral seguem
não atestados. Não calcular espaço recuperável a partir da soma de tamanhos lógicos.

Contrato e quickstart consolidados em [contracts/local.md](contracts/local.md) para
não duplicar a mesma interface em vários documentos.

## Spec Kit e evidência

Helpers oficiais 1.2.3 versionados: create_new_feature, setup_plan, setup_tasks e
check_prerequisites reais, com SPECIFY_FEATURE_NO_PERSIST=1. Skills plan/tasks/analyze/
implement/converge lidas e aplicadas; analyze/converge são instruções do agente,
não subcomandos inventados. specify CLI ausente, uv tool list vazio: comandos CLI
NOT_RUN; nenhuma instalação. Constituição, seletor global e infraestrutura imutáveis.

RED inicial real: teste falha por módulo ausente, sem afirmar comportamento inexistente.
Revisor reproduziu a diferença de protótipos no roundtrip JSON antes da correção.
Suítes de domínio/CLI/FS adversariais, regressões A01/F005 e browser no composto
compõem a qualificação. O recibo final externo vincula resultados ao SHA imutável.
