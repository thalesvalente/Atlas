# AP04-F4-C2 — PLAN

Missão AP04-F4-C2-EXTERNAL-READER-CHAT-01, prompt c4f1204d75222c1a72678d22f1a4b23f1a33ab8f. Base 54bb16d350f7bc34fafb95438bd64a2397d58bf3, tree 1372dd532b2323fc1ebaa5c2f00b6d537c636dc9. Branch exclusiva feat/atlas-parity04-f4-external-reader-20261031. Aprovação delimitada: PR15 comentário 6539419419, pacote c3ea1e82938fd61cc5a22fee973352715a5bb527.

## PLAN → EXECUTE → REVIEW

1. Congelar entradas públicas e extrair sem alteração o JSON Schema Draft2020-12 do contrato F2 0.2.0. Ler ARC-01–09, ADR-0001 e spec001; não mudar contratos existentes.
2. Implementar CLI externa original em tools/atlas_legacy_presentation, parser inerte com contrato exclusivamente sintético versionado, representação literal sem coerção, validação formal e semântica, aquisição exata allowlisted, provas de estabilidade por handle, quotas e scratch efêmero. Nenhum schema privado será inventado.
3. Qualificar fixtures inventadas e contraprovas em Windows/Ubuntu × normal/-O por GitHub Actions focal. Construir wheels e executar Atlas/Caderno em isolamento sem ferramenta. Guard global congelado pode falhar; registrar para C4 sem alterá-lo.
4. Revisão independente C no SHA técnico sem autoria; corrigir defeitos dentro deste plano. Publicar recibos, manifesto, SHA/tree/parent e handoff no Git; PR Draft sem merge.

## Ownership exclusivo

- A /root/parser_a: proposta parser.py e semantics.py; leitura/proposta sem escrita.
- B /root/qa_b: proposta harness/testes/contraprovas/independência; leitura/proposta sem escrita.
- C /root/review_c: revisão independente sem autoria, leitura sem escrita.
- Coordenador /root: único writer, aquisição/CLI/workflow/integração/recibos. Nenhum outro writer nos arquivos.

Paths permitidos: tools/atlas_legacy_presentation/; harness/testes/fixtures atlas_parity04_f4_c2_*; .github/workflows/atlas-parity04-f4-c2-reader.yml; docs/missions/atlas-parity-04/f4-c2-reader/. Sem worktree/clone/branch extra, acervo privado, R4, Catalog/SDK/Caderno, reader003, shell, guards/manifests globais ou feature.json.

## Critério de honestidade e bloqueio previsto pelo prompt

O schema de saída F2 não é schema de entrada R4. O envelope sintético público prova mecanismos e não compatibilidade com bytes privados. Formato não observado retorna SOURCE_FORMAT_UNSUPPORTED e input mínimo sanitizado para L1. Aquisição operacional deve recusar antes de ler sem separação OS e orçamento 256MiB/30s verificáveis: HARD_BUDGET_UNVERIFIED / OS_ISOLATION_UNVERIFIED. Modo de qualificação sintética não concede G4. Na ausência dessas qualificações, saída F4_C2_BLOCKED_EXACT, ainda que CI sintética passe. Sem mudança de plano: são recusas exigidas pela missão.

## Ambiente

exec_command e node_repl não iniciaram: launcher MXC falhou ao enumerar volume D: com OS error1005. Nenhum acervo local foi lido. Execução por conector GitHub/GitHub Actions, ambiente CHAT previsto no prompt; nenhum fallback para host privado. Não foi possível observar checkout local; somente a branch remota é alterada.
