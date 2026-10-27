# Tarefas P02

- [x] T01 Conferir base/tree, PR5, instruções, ADRs/features e ownership.
- [x] T02 Especificar critérios, plano, contrato e lacunas de entrada.
- [x] T03 [P] Implementar binding de snapshot/URL/filtros/ordenação e asset allowlist.
- [x] T04 [P] Implementar shell, escopo, detalhe/comparação, tempo/relações e layout.
- [x] T05 [P] Criar fixtures 28 runs e negativos + harness explícito.
- [x] T06 Executar testes focais e regressão existente aplicável.
- [x] T07 Construir/instalar wheels fora do checkout, import/CLI/assets sem R4.
- [x] T08 Executar navegador/screenshot sintético e registrar seus limites.
- [x] T09 Revisão independente do delta, correções e reteste necessário.
- [x] T10 Publicar código/PR Draft e preparar commit documental com recibos e manifesto; leitura final registrada no fechamento externo.

## Evidência de fechamento

Código `b443f9eb25f118e6a68c2ad17c8e21ab7aa99990`, PR Draft #8. 98 casos únicos
PASS no modo normal e os mesmos 98 com -O; 23 checks browser PASS_SCOPED com seis
capturas, incluindo repetição do mesmo SHA para corrigir apenas fontes do ambiente.
Revisão real sem autoria do delta; findings funcionais encerrados. Ver
`docs/missions/atlas-parity-02/p02-c0/RESULT.md` e recibos correspondentes.

Estado de missão continua **P02_IMPLEMENTED_VERIFICATION_PENDING**. Conclusão das
tarefas de autoria P02 não equivale a aprovação da CI/convergência P06:

- [ ] P06-GATE-01: regra estrita para catalog/server/index na auditoria global.
- [ ] P06-GATE-02: harness global por identidade e semântica de métricas.
- [ ] P06-GATE-03: conexão explícita da jornada P02 com consumidor fora do checkout e artefatos na CI.

Essas três tarefas são handoff, não autorização para P02 editar arquivos P06.

T03–05 têm arquivos exclusivos. T06 depende de integração T03–05, T07 dos bytes
congelados; T09 precede fechamento. Ausência de navegador não bloqueia engenharia,
mas impediria `P02_C0_CANDIDATE_VERIFIED`; a prova de navegador foi executada.
