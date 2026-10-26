# A4 — revisão independente da PoC focal

**Missão:** ATLAS021-A-POC-R4-FOCO01. **Data:** 2026-10-24.
**Revisor:** agente nativo `a4_independent_qa`, distinto dos autores da demo,
do adaptador e da integração. **Parecer de código e requisitos:** PASS_SCOPED.
Este parecer não é aprovação humana, review Codex, resultado de CI ou conclusão
de todos os gates da PoC. Esses marcos requerem seus recibos finais próprios.

## Escopo e vínculo dos bytes

Baseline público revalidado: `228fee0af13b15cfacd97b9b122a395b86be10fe`.
Delta A2 revisado: `164990a90c185e60dcba84719f353386d329b446`.
Negativas independentes A4: `87c587383ad991cccfdca819088a528acffa38f8`.
A integração pode ter outros SHAs de commit; a revisão abaixo fixa os arquivos
funcionais examinados e não transfere automaticamente CI entre commits.

| Arquivo público examinado | SHA-256 |
|---|---|
| `scripts/qa/browser.mjs` | `e476087d9deed38863e93a5809f24763e265513dfebef08a7e6186bc1afb7131` |
| `docs/poc-reproducible.md` | `c7cd1ae8a479c2b09133f716e568e8638ff9523af9c2a96873e0d4cf5d77c446` |
| `tests/qa/test_poc_required_boundaries.py` | `454a8237ccb19dd63898f70d0587e2479464cc34369d4f8bf23c3ab19fbeb13f` |

Também foram lidos README, AGENTS, constituição, ADRs, issue #2, pesquisa já
publicada, perfil, manifesto, schema/SDK, testes baseline, contratos e os
artefatos da feature 002. Nenhuma pesquisa de padrões foi reaberta: não foi
encontrado problema normativo concreto que exigisse mudança do candidato.

## Achados e resoluções

| ID | Severidade | Observação | Resolução revisada |
|---|---|---|---|
| Q-01 | Média | A prova de comparação podia selecionar apenas um produtor e representar indevidamente o outro. | Harness mede e exercita par comparável em cada fonte; consumidor do recibo deve exigir cobertura da fonte obrigatória. Cenário específico e recibo do produtor ficam em sua visibilidade própria. |
| Q-02 | Média | O ensaio integrado temporário não deixava uma demonstração reabrível. | Guia público reutiliza `clean_install.py`, snapshots persistentes e comando `serve` explícito. O comando do produtor é examinado em parecer separado. |
| Q-03 | Baixa | Faltavam regressões explícitas de IDs/tipos inválidos e razão excessiva de compressão. | Três testes independentes adicionados sem alterar SDK ou perfil. |

**Achados P1/P2 abertos no delta público examinado: zero.** Q-01–Q-03 são
lacunas de evidência/demonstração, não uma alegação de defeitos novos no runtime
preservado. Não se afirma inspeção ilimitada de todos os cenários possíveis.

## Execução independente A4 nesta sessão

- Três novos testes: **3/3 PASS normal e 3/3 PASS `-O`** usando fontes públicas.
- Os mesmos testes foram executados no **SDK instalado, Python `-I`, sem viewer
  nem produtor nesse ambiente**: **3/3 PASS normal e 3/3 PASS `-O`**.
- O ZIP controlado contém somente 64 KiB de repetição sintética e ocupa menos
  de 16 KiB comprimidos. A razão superior a 200 foi recusada antes de abrir
  qualquer membro; arquivo intacto e fonte saudável ainda legível.
- Guard de fronteiras arquiteturais: **PASS_SCOPED, zero findings**.
- Os quatro digests do manifesto de perfil foram recalculados e coincidem.
  Perfil: `76ae9be325866895e6bcefeefbc7d0f35e295969a7263e71db6d774be1bf794e`.

Esses resultados A4 são Linux/Python 3.12.14. Windows e CI final não foram
executados por A4; devem ser atribuídos aos jobs reais do HEAD publicado.
Os recibos A2 de instalação limpa, 18 checks de navegador público e 22 checks
adversariais foram examinados separadamente como evidência do autor, sem
reclassificá-los como execução própria de A4. Capturas desktop/móvel também
foram inspecionadas. Nenhuma evidência privada foi copiada para este documento.

## Negativas exigidas e reaproveitamento

| Fronteira | Teste/arquivo público pertinente |
|---|---|
| Estrutura JSON inválida/ambígua | `test_duplicate_json_keys_are_not_silently_overwritten` em `tests/qa/test_protocol_adversarial.py` |
| IDs e tipos inválidos | `test_poc_required_boundaries.py` |
| Relação pendente | `test_external_missing_relation_is_not_silently_accepted` em `packages/protocol/tests/test_sdk.py` |
| Ciclo | `test_derivation_cycle_is_rejected` em `tests/qa/test_protocol_adversarial.py` |
| Fonte ausente | `test_absent_source_is_not_fabricated_empty_success` no mesmo arquivo |
| Digest divergente | `test_changed_payload_fails_byte_integrity` no mesmo arquivo |
| ZIP corrompido | Casos reais DEFLATE/LZMA de metadata e payload no mesmo arquivo |
| ZIP de expansão controlada | `test_controlled_zip_bomb_is_rejected_before_any_member_is_opened` |
| Precisão numérica | Casos de decimal não representável e inteiro acima do intervalo seguro JavaScript |
| Mutação da fonte e continuidade de fontes saudáveis | `tests/viewer/test_catalog_server.py` |
| Referência externa/contexto sem download | `test_external_payload_remains_unresolved_without_network` e `test_unknown_context_never_causes_network_loading` |

A matriz identifica testes existentes; não declara que todas as suítes foram
reexecutadas por este revisor. A integração executa as suítes afetadas e publica
seus resultados exatos. Provas normativas anteriores mantêm seus próprios SHAs,
escopo RO-Crate base e limite de não certificação integral Process Run 0.6.

## Spec Kit e arquitetura

Skills oficiais `speckit-checklist`, `speckit-analyze` e `speckit-converge` do
Spec Kit 1.2.3 foram lidas integralmente. Aplicação das instruções: manual pelo
agente; helpers de pré-requisitos e template: execução real. Dispatch nativo
Codex CLI: NOT_RUN. Hooks de extensão: nenhum registrado.

Analyze foi realizado sem alterações de código ou dos requisitos: **18 itens
normativos/critério (10 FR, 4 NFR, 4 SC), 16 tarefas, cobertura de 100%**, zero
contradições constitucionais e zero ambiguidades bloqueantes. Os 14 itens de
`specs/002-atlas021-poc-r4/checklists/security-architecture.md` foram gerados
desmarcados e avaliados posteriormente pelo owner A4. Marcação de qualidade não
é marcação de implementação ou aprovação humana.

No confronto de implementação, o incremento público consiste em testes, harness
e instruções. Não altera pacotes, perfil, schema, SDK, viewer, constituição,
licença ou ADRs. O controle ambiental existente continua o único produtor
público; nenhum terceiro produtor ou subsistema de domínio foi acrescentado.

A convergência completa de publicação, CI, review remoto e handoff é fechada
pelo integrador nas tarefas existentes e no recibo append-only dos SHAs finais.
Esses itens não são satisfeitos pela ausência de findings neste parecer.

## Limites e gates preservados

ADR-0002 v1.0 / Caderno 0.1.0a1 permanece **PENDING_HUMAN**. Direção do protocolo,
estabilização, ready/merge, licença/release, promoção, dados reais e operações
físicas permanecem decisões independentes. PUBLIC-SOURCE-TRANSFER continua
vazio. Independência funcional do leitor não prova recuperação histórica,
encerramento de consumidores externos ou permissão para remover fontes.

Mudança dos bytes revisados, dos snapshots ou do par publicado requer
revalidação proporcional. A avaliação específica do produtor e os locators
privados são entregues somente no repositório e handoff privados.
