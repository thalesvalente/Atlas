# Checklist: contrato, segurança e aceite da feature 008

**Feature**: [spec.md](spec.md) · **Plano**: [plan.md](plan.md) · **Tarefas**: [tasks.md](tasks.md)

## Contrato revisado

- [x] Escopo e três cenários de usuário definidos; decisões do integrador incorporadas.
- [x] Precedência, vazio, relativos, schema, versão, limite, duplicação e erros têm critérios testáveis.
- [x] Arquivo privado e fonte científica têm responsabilidades e destinos separados.
- [x] API compartilhada e ownership P01/P02/P03 definidos antes da composição.
- [x] Compatibilidade explícita e comportamento legado documentados; nenhuma descoberta.
- [x] Scripts Spec Kit executados, CLI ausente distinguida e seletor global preservado.
- [x] Cobertura planejada de FR-001–018 e SC-001–005 conferida; nenhum conflito arquitetural identificado.

## Crosswalk e contraprovas

| Requisitos | Tarefas | Evidência necessária |
|---|---|---|
| FR-001, FR-004 | T005–009, T012 | JSON local, configurar/exibir/limpar, gestão sem servidor |
| FR-002–003, FR-014 | T007, T013–016 | Explicit source vence config malformada; padrão ausente/vazio; filho não herda seleção |
| FR-005–006 | T010–012, T016 | Relativos/CWD/pasta JSON, Unicode/espaços, schema/version/tipos/chaves |
| FR-007–008 | T005, T007, T010–011, T015–016 | Existência/acesso/compatibilidade, 16/17, duplicados, limite com adaptador |
| FR-009 | T005, T011 | Falhas de write/fsync/replace preservam bytes anteriores; temporário limpo |
| FR-010–011 | T005, T007, T010–011 | Leituras não gravam; pacote imutável; links e destinos científicos recusados |
| FR-012–013 | T014–016, T017 | Sem R4/varredura; inspect/CLI explícita/legado compatíveis; smoke cross-process instalado |
| FR-015 | T005–007, T011, T014 | Erro/resumo sem paths; paths somente por opção explícita |
| FR-016–018 | T001–004, T017–021 | Docs, testes reais, revisão não autora, branch/PR Draft/handoff e gates separados |
| SC-001–002 | T007, T011, T014, T016 | Primeira configuração, reutilização, reconfiguração e cardinalidades |
| SC-003–004 | T011, T014–018 | Negativos, integridade, explicit source e ausência R4 |
| SC-005 | T018–021 | Revisão/PR/handoff; Windows somente após recibo |

## Gates de implementação e QA

- [ ] Backend e CLI implementados e testados em ambiente declarado.
- [ ] Launchers integrados e testados, sem serviços nos comandos de gestão.
- [ ] Contraprovas de persistência, precedência, isolamento, dedup e privacidade executadas.
- [ ] Smoke `scripts/qa/portable_source_config_smoke.py` e regressões pertinentes de catálogo/launcher/instalação executados.
- [ ] Revisão independente não autora concluída no snapshot final; findings resolvidos ou explícitos.
- [ ] Branch/commits e PR Draft publicados; base protegida pelo escopo preservada.
- [ ] Actions observadas no SHA correto; Codex Review registrado como executado, pendente ou não disponível.
- [ ] Handoff local inclui SHA exato, testes sintéticos e critérios de aceite.
- [ ] Windows PowerShell 5.1/7 e instalação isolada efetivamente testados: `LOCAL_TEST_NOT_RUN`.

## Limites

Checkbox de contrato indica consistência documental, não teste executado.
A tabela é cobertura planejada, não resultado. CI ou revisão automática não
substituem o teste no host Windows nem autorizam merge, release, deploy, leitura
privada ou retirada de dados. Evidências históricas e seus pins ficam intactos.
