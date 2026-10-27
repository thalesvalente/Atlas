# Implementation Plan — P03

**Branch:** `work/atlas-parity02-p03-components-20261027` · **Spec:** [spec.md](spec.md).

## Summary

Dois módulos ES sem dependências de runtime e uma projeção Python pura. Renderers retornam
DOM desconectado. Harness próprio monta explicitamente dados sintéticos e serve allowlist
fixa em loopback, sem modificar o servidor principal.

## Technical Context

Python >=3.11, JavaScript ES/BigInt, unittest stdlib e Node assert. Nenhum banco, produtor,
rede ou contrato persistido novo nos componentes. Tabela limitada a 1000 linhas, 32 colunas,
20000 células; limites adicionais no COMPONENT-API. Disponibilidade e digests separados.
Prova visual exige navegador real; DOM de teste não é navegador.

## Constitution Check

ARC-01–09 preservados; apresentação descartável não é protocolo. Fixtures sintéticas,
nenhum executor, aceite, migração ou retirada. Aceite posterior ADR-0002 reconhecido sem
reescrever história. Não há desvio arquitetural necessário. Verificação por hashes/diff e
revisão independente.

## Ownership

| Agente real | Escrita exclusiva |
|---|---|
| `/root/p03_tables` | JS/CSS tabular, testes e fixtures table* |
| `/root/p03_artifacts` | projeção Python, JS/CSS de metadados, seus testes/fixtures |
| `/root/p03_independent_review` | nenhuma escrita no delta; parecer externo ao checkout |
| `/root` | harness, provas transversais, docs/specs P03 e Git/publicação |

## Delivery sequence

1. Snapshot GitHub: conferir 162 blobs, árvore e commit; ler governança.
2. Spec Kit existente com SPECIFY_FEATURE_NO_PERSIST=1 no workstream P03.
3. APIs fixadas, implementações paralelas e harness isolado.
4. Testes focais, regressão, instalação isolada, HTTP e imutabilidade.
5. Revisão independente de bytes congelados e correção de findings.
6. Commit de código; commit documental referenciando SHA anterior; PR Draft sanitizada.
7. Leitura final GitHub única, sem aguardar CI/frentes externas.

## Complexity Tracking

Sem violação constitucional. Composição e semântica persistida ficam fora do plano.
