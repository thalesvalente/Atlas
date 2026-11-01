# AP04-F4-L0-QA-INDEPENDENT-RECEIPTS-01 — revisão distinta e somente leitura

`orq.audit@llm-sec,agentic-pac/seai.qa:`

**EXECUTE a revisão independente dos recibos PRIVADOS F1/L0, não crie outro prompt.** Requer **Codex LOCAL Windows**, no workspace autorizado, e **sessão/agente revisor diferente e não autor** de qualquer recibo auditado. O modelo/esforço sugerido é High, selecionado pelo operador.

## 0. PRECONDIÇÕES

1. Esta missão foi publicada na PR documental #22, derivada do handoff inicial L0. Leia seu README, checklist e os contratos originais pelo SHA. Reconfirme HEAD apenas para proveniência; **não troque branch nem faça checkout, clone, worktree, git reset, git clean ou git push**.
2. O estado de entrada foi **relatado pelo executor**, não revisado: `SOURCE_BYTES_MATCH_F1` ARQUIVO 3; integridade da leitura antes/depois estável; `MTIME_SERIALIZATION_UNVERIFIED`; mtime `AMBIGUOUS`; F1 baseline sem reescrita; G4 `BLOCKED`.
3. Faça um registro local privado de independência com identificador desta NOVA sessão, autorias declaradas dos recibos F1/L0 e comprovante de que você não foi o autor. Uma mudança de prompt/role na mesma sessão autora **não** comprova independência. Se não houver executor realmente distinto, `INDEPENDENT_REVIEW_NOT_PROVEN`; faça no máximo checagem sequencial não independente e não declare QA independente.
4. **NÃO REABRA os três arquivos científicos F1. NÃO os re-hasheie. NÃO calcule timestamp novo do original.** Revise apenas recibos já existentes. A autorização anterior para ler conteúdo científico não é transferida por este prompt.
5. Se a nova sessão local ainda não tiver autorização para acessar os recibos PRIVADOS da F1 e L0, solicite ao operador autorização apenas para leitura exata dessas pastas de recibos. Localize-as mediante caminho seguro fornecido pelo operador no host, **não por scan de drives, busca recursiva, padrões glob, acesso a pastas irmãs ou upload**. Não insira os paths na resposta pública.
6. Antes de qualquer gravação de parecer, confirme pasta privada de QA já autorizada, separada dos arquivos auditados. Se não autorizada, não escreva; informe `QA_OUTPUT_NOT_AUTHORIZED`. Não mude ACL, políticas Windows, firewall ou permissões. Os recibos auditados são SOMENTE LEITURA.

## 1. ANALYZE — identidade da evidência auditada

- Fixe privadamente os hashes e/ou identidades dos recibos F1/L0 históricos e da contraprova SHA-256 mais recente, conforme manifestos locais. Registre qual snapshot F1 e qual ARQUIVO 3 são comparados; não deduza identidade só do nome `index.html`.
- Verifique se os sete recibos originais e os lotes posteriores continuam existentes, e se **nenhum arquivo histórico foi sobrescrito**. Não presuma contagem total de recibos com base no número informado em chat; reconcilie inventário privado e nomes reais.
- Valide estrutura e integridade do manifesto local sem apenas aceitar o marcador `PASS` do executor: recalcule hashes dos **recibos** (não das fontes científicas) a partir de suas cópias locais; verifique quais caminhos o manifesto cobre e se versões anteriores permanecem.
- Revise a cadeia de evidência de SHA-256: (i) digest F1 do mesmo arquivo/snapshot, registrado antes; (ii) digest atual produzido pela L0; (iii) comparação integral dos 256 bits, sem normalização/truncamento; (iv) identidade/handle, estabilidade size/mtime antes/depois da leitura; (v) ausência de recomposição, substituição de baseline ou erro de associação.
- Não reproduza nem imprima os dois hashes nem qualquer caminho do corpus no stdout, no modelo, em logs externos ou em comentário de PR. Use comparação local determinística, de saída redigida `MATCH`/`MISMATCH`/`UNVERIFIED`.

## 2. PLAN → EXECUTE — qualificar claims individualmente

Confronte os recibos com a matriz em REVIEW-CHECKLIST.md:

A. `SOURCE_BYTES_MATCH_F1` apenas para o arquivo 3, se os dois digests íntegros forem iguais e a identidade histórica do arquivo for comprovada. **Não extrapole o resultado aos arquivos 1/2 ou ao acervo inteiro.**

B. `MTIME_SERIALIZATION_UNVERIFIED` e `AMBIGUOUS` devem permanecer: comparação de arredondamento versus truncamento, sem recuperar função F1, não prova equivalência de metadados. Uma igualdade de bytes não encerra discrepância de mtime.

C. Estado das autorizações: três paths F1 anteriormente autorizados na execução autora, mas **nesta revisão não há permissão implícita para fonte**. Nenhum `reader.prepare`, L1, interpretação HTML/JSON, parser real ou script da fonte; nenhuma nova hashada científica.

D. Preservação: baseline F1, repositório Atlas, dados R4, recibos e checkout sem alterações atribuíveis a este QA. Não afirme que a origem continua imutável após a janela histórica apenas por ler recibos antigos.

E. Independência: revisor efetivamente distinto, não autor, e possibilidade de atestar o fato por recibo LOCAL. Sem isso, só `INDEPENDENT_REVIEW_NOT_PROVEN`.

F. Privacidade: compare apenas números/flags e referências locais opacas. Se logs de ferramenta expõem material privado à interface/modelo remoto, encerre `PRIVATE_PAYLOAD_EXPOSURE_UNVERIFIED` e não continue.

O teste de um sintético pode ser usado para confirmar *lógica* de comparação SHA e de timestamp, sem substituir prova factual do arquivo 3. Nunca execute payloads científicos, scripts R4, ataques ao host, mudanças OS ou operações de rede/provider.

## 3. REVIEW — parecer real e handoff

Se a escrita privada de QA estiver autorizada, publique **somente no host** novos arquivos com nomes exclusivos, sem alterar os originais: `INDEPENDENT-REVIEW.private.md` (ou sufixo exclusivo se já existir), `REVIEW-EVIDENCE.private.json` e manifesto QA. Atribua identificador distinto ao executor (privado), evidências verificadas por ID de recibo (privado), achados materiais com causa, reprodução, limite e próximo ato. Releia os novos arquivos e valide manifestos, sem publicar o conteúdo.

Opcionalmente preencha `HANDOFF-REVIEW.template.json` como relatório **sanitizado**, mas NÃO envie ao GitHub automaticamente nem alegue aprovação de publicação sem revisão de privacidade e autorização humana separada. Não usar uploads de recibos privados como atalho.

Estados admissíveis de saída:
- `F4_L0_QA_PASS_SCOPED_BYTES_ONLY`: prova por recibos revisada por executor distinto, sem achado material **no escopo da comparação de bytes**.
- `F4_L0_QA_FINDINGS`: inconsistência na cadeia de hash, identidade, fonte, manifesto, autorização, procedimento ou preservação; apresentar apenas categoria e próximo ato.
- `INDEPENDENT_REVIEW_NOT_PROVEN`: não há revisor realmente distinto/não autor.
- `QA_EVIDENCE_INSUFFICIENT`: faltam recibos, proveniência, integridade ou acesso para sustentar conclusão.
- `QA_OUTPUT_NOT_AUTHORIZED` ou `PRIVATE_PAYLOAD_EXPOSURE_UNVERIFIED` quando pertinentes.

**Todos os estados mantêm:** `MTIME_SERIALIZATION_UNVERIFIED`, `SOURCE_DRIFT=UNVERIFIED` no conjunto de metadados, `G4=BLOCKED`, `L1=NOT_EXECUTED`, `C3_dependency_satisfied=false`. QA deste recibo **não** demonstra leitura real v5 estrutural, não libera worker/sandbox Windows, não aceita descriptor 0.2.1, não autoriza F4-C3/C4/F5, merge, release, deploy, promoção, migração ou limpeza.

## 4. SAÍDA AO OPERADOR (sem bytes privados)

Em até 10 linhas: estado final, independência PROVEN/NOT_PROVEN, revisão dos digests MATCH/MISMATCH/UNVERIFIED, identidade de snapshot PROVEN/UNVERIFIED, preservação dos recibos PASS/FAIL/UNVERIFIED, mtime AMBIGUOUS, G4 BLOCKED, prova escrita privada PASS/BLOCKED, findings materiais e menor ato seguinte.

Não apresente valores, caminhos, nomes de cliente, IDs científicos, RF literal, código privado ou conteúdo de recibo. O único resultado publicável por esta instrução é o resumo em categorias acima, jamais recibos.
