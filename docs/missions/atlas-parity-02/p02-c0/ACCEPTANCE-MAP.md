# Mapa de aceite — ATLAS-PARITY-02-P02

Código: `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`.
Origem dos requisitos: prompt P02 e baseline `c2d00fb…`; não substitui estudo C ausente.
Resultado de missão: **P02_IMPLEMENTED_VERIFICATION_PENDING**, pelos gates CI/P06.

| Requisito | Implementação observável | Prova executada | Resultado e limite |
| --- | --- | --- | --- |
| P02-R01 — exploração | Busca título/ID/fonte, sete ordenações determinísticas, filtros de fonte/revisão/métricas/referências, estados vazios e seleção persistente | Testes focais de estado, 22 checks internos; browser `source_review_state_presence_and_unicode_filters`, `all_sort_orders_survive_reload`, `comparison_selection_persists_across_hidden_filters_and_reload` | PASS_SCOPED; seleção até quatro herdada, sem limite de 28 para produto |
| P02-R02 — navegação | Hash v1 vinculado à sessão/snapshot; valida enums/IDs/scope; histórico, reload e fechamento preservam contexto | Casos de sessão/reordenação/rebuild do catálogo; checks stale/missing/scope/legacy do estado; browser `source_scoped_detail_and_hash_keep_duplicate_ids_distinct`, `back_forward_reload_and_close_preserve_context`, `stale_snapshot_never_retargets_entity_or_selection`, `missing_entity_and_malformed_url_have_explanatory_safe_fallback` | PASS_SCOPED; reinício expira links explicitamente; token não é autenticação ou permalink permanente |
| P02-R03 — escopo/cobertura | Painel de fontes/pacotes/snapshots e carregados/filtrados; fonte/elegível/selecionado produtor/convertido permanecem null/não informado | `test_loaded_counts_do_not_invent_source_eligible_selected_or_converted_totals`; browser `loaded_scope_snapshot_and_unknown_coverage_are_separate` | PASS_SCOPED; sem inferir população da origem a partir de contagem local |
| P02-R04 — semântica | Estado/revisão, valor/tipo/unidade/precisão, referências/disponibilidade, inputs/outputs/derivação; texto exato e `mentions` neutra | Focais catálogo; regressões integradas existentes; browser `incompatible_metrics_keep_types_units_and_declared_precision_without_ranking`, `detail_preserves_direction_availability_mentions_and_inert_adversarial_content`, `declared_precision_exceeding_js_integer_range_is_exact_text`, `neutral_reference_navigation_and_back_remain_in_the_same_source` | PASS_SCOPED; não há conversão/ranking implícito ou aprovação científica |
| P02-R05 — tempo/relações | Registros sem datas/isolados; fim sem início; origem temporal preservada; direção declarada | Focal `test_unknown_time_isolated_runs_precision_and_incompatible_metrics_survive`; browser `end_only_timestamp_is_visible_without_inventing_start`, `undated_and_unrelated_runs_remain_reachable_from_time_and_relations` | PASS_SCOPED; não infere evento, ordenação científica ou causalidade |
| P02-R06 — legibilidade | Reflow 1440/390/320, tabelas locais, foco/skip link/Escape, espaçamento e texto longo | Seis capturas; browser reflow ×3, spacing, teclado/foco, amostra de contraste; inspeção visual independente | PASS_SCOPED nos cenários ensaiados; ENV-01 de glifos resolvido por fontes isoladas e repetição no mesmo SHA; zoom nativo NOT_RUN, CSS zoom false, sem certificação WCAG |
| P02-R07 — fronteiras | DOM textual, CSP, origem/Host, allowlist fixa e ausência de leitura externa | Três testes HTTP focais; negativos integrados de segurança; browser `no_external_requests_or_browser_errors`; SHA das fontes antes/depois | PASS_SCOPED: zero requisições externas/erros de página; fontes intactas |
| P02-R08 — execução/empacotamento | 28 runs/duas fontes/IDs repetidos; asset fixo no wheel; SDK/viewer desacoplados de R4 | Instalação limpa, comparação wheel/Git independente, 98 testes em cada modo, browser consumidor fora do checkout | PASS_SCOPED local; CI global pendente de ajustes P06; script browser novo não é automaticamente acionado |

## Arquivos de prova

- [integrated-normal.json](receipts/integrated-normal.json) e [log](receipts/integrated-normal.log).
- [integrated-optimized.json](receipts/integrated-optimized.json) e [log](receipts/integrated-optimized.log).
- [browser.json](receipts/browser.json), [atribuição de ambiente](receipts/environment.json) e [capturas](screenshots/).
- [clean-install-original.json](receipts/clean-install-original.json) e [equivalência dos wheels](receipts/wheel-code-equivalence.json).
- [arquitetura e método](receipts/method-architecture.json), [ownership e preservação](receipts/ownership.json).
- [CI do código](receipts/ci-code.json) e [revisão independente](REVIEW.md).

Os testes Python focais estão diretamente em `tests/viewer/test_atlas_parity02_p02_*.py`.
São 12 casos focais dentro das 36 provas viewer. O teste Python do estado agrega
22 checks Node; contar os dois níveis como provas únicas distintas inflaria o total.
Normal e `-O` executam os mesmos 98 casos. A nova jornada browser tem 23 verificações
de interação separadas, também não somadas como novos casos unittest.

## Gates que impedem a promoção do estado

1. Auditoria Spec Kit global falha em três arquivos P02 não incluídos na allowlist histórica.
2. Harness browser global falha em uma expectativa de texto da célula de métrica;
   também requer seleção por identidade e revisão das suposições de comparação.
3. Conexão explícita da jornada P02 à CI e publicação dos seus artefatos pertencem à P06.

Esses gates têm runs/SHAs reais em `receipts/ci-code.json`; não são falta de teste
simulada. Nenhum deles autoriza P02 a editar os arquivos de outra frente.
