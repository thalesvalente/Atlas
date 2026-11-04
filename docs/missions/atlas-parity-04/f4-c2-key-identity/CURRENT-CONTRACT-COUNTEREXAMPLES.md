# Contraprovas documentais de identidade — fontes inventadas

Os 14 oráculos JSON em SYNTHETIC-IDENTITY-FIXTURES.json são inventados e preservados byte a byte: dez principais A/B/C1/C2/D/E/F/G/H/I e quatro suplementares J/K/L/M. Não são descriptors completos nem resultados de execução da versão 0.2.1.

## Contrato vigente e delta candidato

`key` é identidade estrutural, `ui_id` é derivado e `native_id` conserva a identidade nativa comprovada ou null. `parent_key/from_key/to_key` são referências estruturais. No 0.2.0, `declared_id`/RESOLVED exige native ID original único no contexto; navigation ID sozinho e unmapped_fields não provam resolução.

O1 propõe somente `node.source_key_literal`, `node.parent_key_presence`, `reference.reference_basis` e `reference.declared_key_literal`, preservando `node.parent` e `node.parent_key_literal` já requeridos. Sem ARC-09, nenhum consumidor é alterado.

| Caso | Entrada inventada | O0 / 0.2.0 | O1 / expectativa não executada |
|---|---|---|---|
| A | Pai key=p-A/native_id=native-A; filho parent_key=p-A | Sem native p-A: UNRESOLVED | Resolver ao pai original; native-A inalterado |
| B | Pai key=rec-B/native=null; records.id=rec-B | C2 recusa R4_V5_PARENT_SCOPE_UNREPRESENTABLE | Resolver somente no namespace estrutural, não ao record |
| C1/C2 | key=shared-C em snapshots diferentes | Texto não prova identidade entre snapshots | Cada referência permanece no próprio snapshot |
| D | 50 pares nativos colidentes e 50 filhos; 150 nodes/50 edges | Colisões nativas não elegem alvo | 50 parents estruturais únicos; native lookup COLLISION |
| E | Nó sem key | Input R4 v5 inválido | REJECT_MISSING_STRUCTURAL_KEY_ATOMIC, sem key inventada |
| F | Duas ocorrências key=dup-F | Input duplicado | REJECT_DUPLICATE_STRUCTURAL_KEY_ATOMIC, sem primeiro/último |
| G | child-G referencia absent-G, sem alvo | Native lookup não resolve | UNRESOLVED, target null, ORPHAN, binding_gap=true |
| H | cycle-H-1 e cycle-H-2 são pais recíprocos | Ciclo não pode desaparecer | Duas refs resolvidas; gap TREE_CYCLE, binding_gap=true, sem árvore acíclica |
| I | MEMBER_OF member-I para group-I por keys | Native null perde ligação | Endpoints estruturais, ORGANIZATIONAL_MEMBERSHIP/NON_CAUSAL; ciência NOT_EVALUATED |
| J | parent_key ausente | Nullable sozinho perde a diferença | ABSENT, NULL_ENDPOINT, PARENT_UNKNOWN |
| K | parent_key:null | Nullable sozinho perde a diferença | EXPLICIT_NULL, NULL_ENDPOINT, PARENT_UNKNOWN; raiz só com root=true comprovado |
| L | parent_key com 3000 caracteres x | Não é ID nativo válido por inferência | PRESENT; 3000 caracteres íntegros, UNRESOLVED/ORPHAN/gap |
| M | NATIVE_ID com key não null; STRUCTURAL com declared_id não null | Não misturar contratos | Ambos rejeitados pelas condições futuras allOf/if/then |

Em A, `{key:"p-A",native_id:"native-A",ui_id:"ui-p-A"}` não permite `declared_id="p-A"` RESOLVED em 0.2.0. Copiar key para native falsifica identidade; não navegar é seguro, porém incompleto. Em B, o mesmo texto pertence a outro namespace. O0 não oferece simultaneamente fidelidade, navegação estrutural e validação native-only.

## Matriz PKEY de entrada — complemento documental, não novos fixtures JSON

Para um nó original com key válida; entradas inventadas. `PRESENT` abaixo conserva exatamente o literal. REJECT_ATOMIC não emite parent, tree_state ou descriptor parcial.

| ID | parent_key na fonte | Presença / resultado exigido |
|---|---|---|
| PKEY-01 | propriedade ausente | ABSENT; parent literal null; NULL_ENDPOINT |
| PKEY-02 | null | EXPLICIT_NULL; parent literal null; NULL_ENDPOINT |
| PKEY-03 | "" | REJECT_ATOMIC |
| PKEY-04 | 0 | REJECT_ATOMIC |
| PKEY-05 | false | REJECT_ATOMIC |
| PKEY-06 | {} | REJECT_ATOMIC |
| PKEY-07 | [] | REJECT_ATOMIC |
| PKEY-08 | "p-A" | PRESENT; RESOLVED somente com alvo original único |
| PKEY-09 | "missing" | PRESENT; UNRESOLVED/ORPHAN se sem alvo |
| PKEY-10 | string de 65.537 caracteres | REJECT_ATOMIC, sem truncamento |
| PKEY-11 | " " | PRESENT; espaço literal, nunca trim para ausência |
| PKEY-12 | string de 65.536 caracteres | PRESENT; íntegra, UNRESOLVED/ORPHAN pois key indexável tem no máximo 2048 |

Para J/K/PKEY-01/02, `node.parent` continua obrigatório: `reference_basis=SOURCE_STRUCTURAL_KEY`, `declared_id=null`, `declared_key_literal=null`, `target_navigation_id=null`, `resolution=NULL_ENDPOINT`, contexto exato e prova de ausência ou de null. Sem root booleano true comprovado: PARENT_UNKNOWN/gap; com ele e sem parent não nulo: ROOT_DECLARED, binding_gap=false para parent. Root=true contraditório com parent não nulo rejeita. String vazia ou tipo inválido não se converte em NULL_ENDPOINT, ORPHAN ou raiz.

H conserva tree_state=PARENT_RESOLVED e refs RESOLVED, mas TREE_CYCLE é gap (contagem 2), não enum de tree_state. Não remover arestas, inventar raiz ou marcar descendentes não cíclicos. ORPHAN é referência válida sem alvo, não ciclo nem input inválido.

## Rejeições e preservações obrigatórias na proposta

Base estrutural com declared_id não null, literal ausente, falso locator/prova, contexto diferente, alvo stub/derivado/record ou key duplicada rejeita. Base nativa com declared_key_literal não null ou escolha de native colidente rejeita. Nenhuma resolução usa ui_id, título, hash, path ou ordinal como identidade. Igualdade de texto não autentica nem aprova ciência.

Para PARENT_RESOLVED estrutural, parent_key_literal == parent.declared_key_literal, alvo original único e navigation ID da ocorrência. Base nativa mantém a igualdade 0.2.0. MEMBER_OF não ganha causalidade; nulls, repetições, órfãos e Run externo continuam explícitos. Quotas, versões desconhecidas e contexto expirado rejeitam/inativam sem apresentar subconjunto como completo. Não criar Project, Experiment, pai, ID científico ou conteúdo privado.

**Método:** inspeção dos bytes e das expectativas documentadas, com checker reproduzível em INDEPENDENT-REVIEW. Não foi executado validate_descriptor 0.2.1, renderer, F3A/F3B, browser ou origem privada. Os oráculos continuam entradas para testes de produto futuros após ARC-09.
