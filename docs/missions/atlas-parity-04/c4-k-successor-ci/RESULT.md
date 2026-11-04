# P02 — sucessor documental C4-K

## ESTADO

O harness distingue a infraestrutura C4-K de sua entrada documental K. A identidade
K somente é consumida quando K-BINDING.json contém finalized=true, o recibo P01,
SHA, tree, parent, todos os commits intermediários e os objetos exatos de cada path.
Um binding pendente significa C4_K_HARNESS_READY_AWAITING_K_SHA; nunca PASS de K.

Entrada terminal P01 consumida: 38f7b07602ed407e1fca54a5053861f7605dd9f5,
tree f2ba38b893cacf290038fa88b5d782294f36e1c2, parent
d5bdc86ef68cad2f5d503945ca788c3a74df4839. Autoridade documental publicada em
https://github.com/thalesvalente/Atlas/pull/21#issuecomment-6623833840.
Inventário Git real: onze ADDs; seis commits lineares completos desde a base F2;
manifesto dez entradas. Seu digest SHA-256 é
e7a77aaa906bfb074195538d6d29b576ceb521ea8ab8547209eb643449761577.
O estado documental C2_K_REVIEW_BLOCKED_EXACT da P01 não constitui aprovação
arquitetural e não impede a verificação estreita desta sucessão C4/CI.

## PLAN

Preservar C4/AP04/F2 e seus controles históricos. Base exclusiva do reparo:
54bb16d350f7bc34fafb95438bd64a2397d58bf3, tree
1372dd532b2323fc1ebaa5c2f00b6d537c636dc9, parent
bd2166651f159e70a8165e0f12c8ad2a3270a0d6. Branch própria:
ci/atlas-ap04-c4-k-successor-p02-native-20261104. Nenhuma edição na PR #21 ou ownership K.
A Draft #30 preexistente permanece preservada: sua política fixava K 508ccb;
esta implementação usa branch própria, sem sobrescrever seu harness ou recibos.

## EXECUTE

A rejeição original foi reproduzida no SHA K observado
508ccb257a44dc66da13d1edfec7f00ef5231d09, tree
854b57fe00ad9ba93177f9fd975dc2675c3751c6. O run efetivo é 41361052428,
tentativa 1; quatro células Ubuntu/Windows × normal/otimizado falharam com
Repair history contains unauthorized paths, enumerando os onze ADDs K originais.
O run 41359430564 pertencia ao predecessor 0a87fcd, não ao SHA 508ccb.

O sucessor mantém os guards, testes, manifestos e pins históricos. Audita a F2
no checkout temporário da base imutável e compara integralmente as árvores de cada
commit das duas frentes. Todo path fora do ownership exato permanece protegido,
inclusive alterações intermediárias posteriormente revertidas. O histórico próprio
aceita somente oito controles modificados e quatro novos arquivos explícitos.
Os hashes desses controles têm autorização independente antes de executar o guard.

O ownership K possui os onze paths publicados originais. A entrega final somente
é válida se o inventário Git real coincidir exatamente com esses onze paths,
todos ADD 100644, e seu manifesto canônico conferir os dez demais.
Nenhum contrato 0.2.0, reader003, código C2-A/C2-B, runtime ou fonte privada muda.

## REVIEW

Contraprovas executam em bancos Git novos e temporários: positivo, path extra,
documento histórico alterado/revertido, objeto substituído, commit intermediário
proibido, symlink/modo executável/gitlink, traversal, rename/delete, manifesto
adulterado, ancestry inválida e merge inesperado. Os 32 testes F2 executam no
snapshot histórico e conservam seus IDs e atribuição; os testes atuais executam
na árvore própria. Coleções instaladas preservam o corpus herdado de 191 IDs,
sem confundir prova histórica com qualificação atual da sucessão.

Recibos externos da PR própria identificam HEAD, tree, parent, execuções efetivas,
plataforma, versão Python, modo e findings/review. Este arquivo não se autoatribui
um SHA terminal ou CI ainda não observado. ADR-0003 continua PROPOSED_NOT_APPROVED;
ARC-09 e aceite científico/humano permanecem separados. PR #20 e seu bloqueio
C2_B_UNAUTHORIZED_SUCCESSOR_PATH por THREAT-MODEL.md permanecem fora do escopo.

## HANDOFF

Validação do SHA próprio, com checkout limpo e histórico completo:

```text
python scripts/qa/atlas_parity04_k_doc_ci.py audit
python scripts/qa/atlas_parity04_k_doc_ci.py regression
python -O scripts/qa/atlas_parity04_k_doc_ci.py regression
python scripts/qa/atlas_parity03_c4_ci.py inputs
```

Após receber o SHA terminal P01, buscar seus objetos sem alterar sua branch,
conferir o recibo publicado, registrar o binding exato e sua autorização independente
na frente P02, publicar por fast-forward e repetir CI/review no novo SHA próprio.
Somente então:

```text
python scripts/qa/atlas_parity04_k_doc_ci.py validate-k --k-sha SHA_TERMINAL_P01_EXATO
```

O comando rejeita input diferente, ausente ou não terminal. Com K consumido, a
qualificação é C4_K_SUCCESSOR_QUALIFIED_FOR_COMPOSITION, limitada à sucessão
documental de duas frentes verificadas. O merge de composição P03 e seus gates
seguem sendo execução separada. Sem merge, deploy, release, repin histórico,
force-push, squash, rebase, skips ou aprovação arquitetural.
