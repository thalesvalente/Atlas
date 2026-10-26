# Implementation Plan: Atlas independente e protocolo candidato

**Branch**: `feat/atlas021-interface-protocol` | **Date**: 2026-10-24 | **Spec**: [spec.md](spec.md)

## Summary

Implementação nova, com dois pacotes Python independentes: caderno-protocol e
atlas-viewer. Interface local HTTP, HTML/CSS/JavaScript estáticos, sem CDN. SDK stdlib
valida serialização restrita RO-Crate e semântica referencial. Produtor ambiental
público usa apenas o protocolo; adaptador legado e testes permanecem privados.

## Technical Context

**Language/Version**: Python >=3.11, JavaScript ES2022. Desenvolvimento 3.12.14.
**Primary Dependencies**: runtime UI apenas caderno-protocol==0.1.0a1; SDK stdlib.
Ferramentas isoladas specify-cli1.2.3, build1.3.0, setuptools80.9.0, wheel0.45.1,
jsonschema4.25.1, roc-validator0.13.0; navegador Playwright1.62.1.
**Storage**: pacote local expandido e snapshot de metadados; fontes somente leitura;
índice efêmero em memória, preferências no navegador, reconstrução explícita.
**Testing**: unittest, auditoria AST, instalação wheel em venv vazio, testes HTTP e browser.
**Target Platform**: Windows/Ubuntu, Python normal/-O; browser desktop/mobile viewport.
**Project Type**: SDK/CLI + aplicativo local instalável em wheel.
**Performance Goals**: escopo limitado a fontes locais e corpus de referência, sem SLA de produção.
**Constraints**: sem rede implícita; metadados limitados pelo SDK; sem execução de anexos;
ZIP limitado em memória sem extração; sem autenticação remota; servidor apenas loopback com origem/Host validados.
**Scale/Scope**: candidata limitada por orçamento explícito de metadados/entidades/payload.

## Constitution Check

ARC-01–09 preservados no desenho. Nenhum desvio necessário. ADR-0002 é proposta;
testes não equivalem a aceite humano. Não se transportam fontes privadas ao público.
Gate de estabilização não bloqueia protótipo autorizado. Sem autoridade de migração/retirada.

## Project Structure

- packages/protocol: A1, SDK/schema/validador e serialização pública.
- packages/atlas: ORQ/A2, interface e servidor local somente leitura.
- examples/environmental: A1, exportador de domínio independente.
- packages/protocol/tests: A1; tests/qa e scripts/qa: A4; tests/viewer: A2.
- docs/architecture e docs/coordination: ORQ, exceto ADR-0002 de A1.
- research: A1; docs/reviews: A4; .specify e specs: ORQ.
- Adaptador e testes de legado: A3, em branch privada e namespace exclusivo.

## Research and Design

Ver [research.md](research.md), [data-model.md](data-model.md),
[contracts/interface.md](contracts/interface.md) e [quickstart.md](quickstart.md).
Não adotar um formato próprio concorrente. A1 testa finalistas públicos e documenta
perdas/compatibilidade antes de congelar a candidata. SDK não depende de UI.

## Complexity Tracking

Nenhuma violação constitucional aceita. Runtime HTTP é local e não é serviço multiusuário.
Conformidade completa JSON-LD arbitrária fica fora; serialização suportada é explícita.
