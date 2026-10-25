# Plano — REUSE-01

## Contexto técnico histórico — REUSE-01 / LOCAL-REAL01
Atlas e SDK públicos preservados. Perfil candidato 0.1.0a1 preservado. Produtor privado responsável pela leitura/normalização existentes e pelo adaptador. Python e bibliotecas já usadas pelo produto; sem dependência nova de domínio.

## Plano do incremento CLOSE01

O runtime preservado acima descreve o piloto anterior. CLOSE01 autoriza apresentação
genérica e campo aditivo no modelo derivado, sem alterar contrato persistido.

1. Reconciliar T020 e PR #5 com recibos de LOCAL-REAL01; conferir topologia da cadeia.
2. Especificar FR-14–21/US4, contrato derivado, checklist, tarefas e análise antes do código.
3. B registra RED da omissão em consumidor instalado da baseline; A e coordenador
   só então implementam o delta. A: `packages/protocol/src/caderno_protocol/read_model.py`.
   Coordenador: `packages/atlas/src/atlas_viewer/static/app.js` e `style.css`.
4. Reutilizar `refs()`, `types()`, `Package.payload_status`, `entityLink()` e a identidade
   `_sourceId`; nenhuma consulta a produtor/carrier. `Catalog` só tem índice em memória:
   startup/reindex reconstrói a projeção; não há cache persistido a migrar.
5. B mantém `tests/viewer/test_related_references.py`, gerador sintético e scripts de
   navegador existentes. Provar consumo instalado, byte-identidade e normal/`-O`.
   Reutilizar matriz Windows/Ubuntu e Chromium da CI; não acrescentar plataforma.
6. C revisa o delta sem autoria de código/testes. Coordenador corrige achados,
   publica fast-forward na #5 e solicita Codex uma vez por HEAD pertinente.
7. Fechamento pós-commit em comentário append-only; não criar commit apenas para
   registrar PASS. Pendências humanas continuam em R012.

O audit histórico de setup preservava todo o runtime. CLOSE01 usa opt-in explícito
`--allow-presentation-delta` em `scripts/qa/speckit_audit.py`, limitado aos seis
arquivos existentes de apresentação/harness listados no código. O modo padrão
continua estrito; schema, perfil, constituição, ADRs e skills não recebem exceção.
`tests/qa/test_speckit_presentation_audit.py` comprova a fronteira e a rejeição de
exclusões. O gate Spec Kit fixa checkout no HEAD e registra esse SHA no log.

Constitution Check do desenho: ARC-01–09 preservados. SDK não depende da UI;
identidade é local ao pacote; revisão científica, disponibilidade e digest continuam
distintos. Nenhum schema, recurso persistido, ADR, aquisição ou adaptador muda.

## Constitution Check
ARC-01 interface; ARC-02 protocolo independente; ARC-03 índices derivados; ARC-04 produtores específicos fora do núcleo; ARC-05 prova com instalação isolada; ARC-06 validade não equivale a ciência; ARC-07 nenhuma manutenção física; ARC-08 promoção separada; ARC-09 sem desvio arquitetural. Resultado da análise: compatível.

## Delta LOCAL-REAL01
Retomar esta feature e a implementação privada correspondente; não criar outro protocolo ou leitor. Reconfirmar revisões e fonte somente leitura. Procurar snapshot estruturado pelos locators conhecidos; quando ausente, avaliar o alcance da API legada existente antes de executá-la. Distribuição privada autenticada e manifestada fica somente na raiz operacional ignorada; consumidor mantém sua instalação e não carrega produtor.

Capturar bytes com codificação explícita, selecionar por identidade nativa unívoca e converter pelo adaptador existente. Validar com SDK/CLI instalados e navegador real em loopback. Comparar controles efetivamente observados antes/depois; não alegar imutabilidade universal. Dados, comandos específicos, manifesto e capturas ficam locais. Correção de apresentação só se necessária ao objetivo, genérica e coberta. Veto real interrompe a chamada dependente.

Reavaliação constitucional: nenhuma mudança de ARC-01–09, ADR-0001, perfil, schema ou aceite de ADR-0002. Aquisição operacional não transforma projeção legada em autoridade central. Os testes anteriores permanecem evidência sintética histórica.

## Fases
1. Comparar a candidata anterior com APIs/projeções existentes; registrar o que é reutilizado, substituído e mantido.
2. Atualizar spec, clarificações, contratos, checklist e tarefas antes da implementação.
3. Escrever testes que exercitem o pipeline original e exijam a ponte de projeção; registrar RED real.
4. Substituir o leitor paralelo da candidata por um adaptador de projeção. Manter a API sintética anteriormente validada sem relaxar seu gate.
5. Testar conversão, seleção, perdas, estados, precisão, referências e isolamento. Validar o pacote no SDK/viewer público sem introduzir dependência privada.
6. Rodar helpers oficiais do Spec Kit e CI Windows/Ubuntu. Revisão independente pelo Codex; não simular subagentes ausentes.
7. Convergir requisitos/tarefas/evidências e publicar correção nas PRs já abertas, sem merge.

## Limites operacionais
No ensaio remoto histórico REUSE-01 não houve acesso ao host do operador. LOCAL-REAL01 retoma a aquisição local delimitada autorizada, sem ampliar permissões da plataforma. O código novo não executa leitores suspensos, não descobre raízes e não substitui métodos de preservação. PoC real depende de aquisição permitida pelo produtor e fonte explicitamente selecionada.
