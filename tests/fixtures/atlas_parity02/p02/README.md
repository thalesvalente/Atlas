# Fixtures públicas sintéticas P02

As duas fontes têm 14 execuções cada (28 no total), com os mesmos IDs declarados
e conteúdo/nome distinto por fonte. Nenhum dado de produtor, host ou acervo privado
foi usado. A quantidade é cobertura de teste, não um limite de produto.

Gerador reproduzível: `scripts/qa/atlas_parity02_p02_fixture.py DESTINO_NOVO`.
Ele usa apenas o SDK público instalado, valida cada documento e recusa sobrescrever
um destino existente. `data/input.csv` é um payload gerado; os outros arquivos de
evidência são declaradamente ausentes ou externos não acessados.

| Caso | ID final | Evidência sintética |
| --- | --- | --- |
| Métrica compatível entre fontes | `run:00` | concentração, number, mg/L, precisão 3 |
| Unidade incompatível | `run:01` | mesma identidade, µg/L |
| Tipo incompatível | `run:02` | mesma identidade, integer |
| Valor ausente | `run:04` | null + motivo, nunca zero |
| Inteiro exato | `run:05` | 9007199254740993 |
| Precisão declarada exata | `run:12` | 9007199254740993, sem arredondamento JS |
| Texto longo/Unicode | `run:06` | português, japonês, grego, emoji e texto sem espaços |
| Conteúdo adversarial | `run:07` e menções | HTML, script, URL externa e URI javascript inertes |
| Sem data/relações/métricas/referências | `run:08` | continua recuperável pelo ID |
| Tempo observado | `run:09` | OBSERVED permanece distinto de evento declarado |
| Somente fim declarado | `run:10` | fim preservado sem fabricar início |
| Outra data ausente | `run:13` | ausência preservada |

Há cinco estados técnicos, quatro estados de revisão (nenhum ACCEPTED sintético),
três famílias representadas por experimentos, inputs/outputs/derivações direcionais
e menções neutras. O universo do produtor, os totais elegível/selecionado/convertido
e o caráter integral/recortado da fonte não são declarados no contrato: devem ser
mostrados como “não informado”, separadamente da contagem de registros carregados.
