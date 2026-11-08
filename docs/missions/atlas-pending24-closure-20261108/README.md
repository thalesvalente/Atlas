# Suplemento documental dos cinco casos negativos de parent_key

A revisão de 24 arquivos de engenharia encontrou cinco inputs sintéticos N1–N5
ausentes do JSON publicado da PR21. Este suplemento preserva somente esse delta
e sua verificação documental. Os 14 oráculos A..M e os cinco blobs ARC09 continuam
intactos em `38f7b07602ed407e1fca54a5053861f7605dd9f5`; o objeto normativo permanece
congelado em `d5bdc86ef68cad2f5d503945ca788c3a74df4839`.

| Caso | parent_key | Correspondência documental congelada |
|---|---|---|
| N1 | string vazia | PKEY-03 |
| N2 | inteiro 17 | PKEY-04 usa 0, da mesma classe de inteiro inválido |
| N3 | booleano false | PKEY-05 |
| N4 | objeto vazio | PKEY-06 |
| N5 | array vazio | PKEY-07 |

As cinco expectativas futuras são `REJECT_ATOMIC`, sem descriptor, campo de
presença ou árvore parcial emitidos. Nenhum mapper, schema ou produto 0.2.1 é
executado por este suplemento. 0.2.0 permanece vigente; 0.2.1 e ARC09 continuam
pendentes de decisão humana. Este material não altera a proposta congelada.

O checker extraído confere valores **e tipos**, inventário e ausência de promoção
de autoridade. Seis adulterações em memória devem ser recusadas. Ele substitui
somente a parte útil do checker local alternativo; os checks documentais gerais
continuam reproduzíveis no bloco Python de `INDEPENDENT-REVIEW.md` da PR21.

```sh
python -B docs/missions/atlas-pending24-closure-20261108/verify_oracles.py
python -B -O docs/missions/atlas-pending24-closure-20261108/verify_oracles.py
```

`DISPOSITIONS-24.json` registra 8 cópias exatas, 14 superadas e 2 fontes com delta
extraído, com justificativas individuais e refs de recuperação. O comentário
terminal da PR fixa o SHA deste suplemento, resultados reais de CI/QA e retirada.
`THIS_SUPPLEMENT_COMMIT` no mapa significa esse SHA imutável; não uma branch móvel.

## Recuperar em outra máquina

```sh
git clone https://github.com/thalesvalente/Atlas.git Atlas
cd Atlas
git fetch origin docs/atlas-pending24-portability-20261108
# Substituir SUPPLEMENT_SHA pelo SHA completo do comentário terminal desta PR.
git checkout --detach SUPPLEMENT_SHA
python -B docs/missions/atlas-pending24-closure-20261108/verify_oracles.py
git fetch origin docs/atlas-parity04-f4-key-identity-20261101
git fetch origin ci/atlas-ap04-c4-k-successor-p02-native-20261104
```

Para cada caminho existente, usar `git show COMMIT:CAMINHO` com os commits exatos
do mapa. Os paths originais `DOCUMENTARY-CHECKS.py` e `P01-EXECUTION.md` estão
ausentes da PR21: o primeiro tem apenas seu delta necessário neste suplemento;
o segundo foi superado pelos recibos remotos e não precisa ser restaurado.
Não sobrepor os arquivos da proposta à main. A PR31 é recuperável em
`6d854b5471473d8548c9e9b271db55a52301ee1c`, com seu binding, guards e regressões.

Somente os 24 arquivos enumerados foram revisados. Backups privados, sessões,
acervos científicos e runtime do host não fazem parte desta prova de portabilidade.
Sem merge, deploy, release, migração ou ratificação ARC09.
