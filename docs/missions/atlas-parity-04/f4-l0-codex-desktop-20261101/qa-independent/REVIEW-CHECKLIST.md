# Checklist adversarial L0 — somente recibos; não reabrir as fontes

| ID | Predicado | Evidência mínima privada | Falha relevante |
|---|---|---|---|
| QA01 | Revisor **realmente distinto** dos autores F1/L0; sessão/execução separada | recibo privado de autoria, sessão distinta, logs locais | `INDEPENDENT_REVIEW_NOT_PROVEN` |
| QA02 | Recibos antigos intactos; manifesto QA não substitui manifestos F1/L0 | inventário antes/depois, hashes de recibos | `RECEIPT_INTEGRITY_FAIL` |
| QA03 | Proveniência F1 para **o arquivo 3 exato**, não apenas nome semelhante | vínculo local de fonte, snapshot e digest F1 | `BASELINE_IDENTITY_UNVERIFIED` |
| QA04 | SHA-256 atual calculado pelo executor L0 e digest F1 idêntico em 256 bits | evidência local com comparaçao determinística | `SHA_MISMATCH` ou `HASH_EVIDENCE_INSUFFICIENT` |
| QA05 | No rehash L0 a identidade/size/mtime permaneceu estável antes/depois | recibo de handle, períodos e invariantes | `READ_STABILITY_UNVERIFIED` |
| QA06 | mtime histórico arredondado/truncado segue **não comprovado**; nenhum rebaseline | recibo de proveniência temporal negativa | `UNSUPPORTED_MTIME_MATCH_CLAIM` |
| QA07 | Nenhum payload R4, HTML/JSON científico reaberto por QA; nenhum dado privado enviado | escopo de acessos e outputs auditado | `SOURCE_ACCESS_OUT_OF_SCOPE` |
| QA08 | Novos recibos QA só em pasta privada autorizada; leitura de volta e manifesto | write permission, integridade QA | `QA_OUTPUT_NOT_AUTHORIZED` / `QA_MANIFEST_FAIL` |
| QA09 | Nenhuma alteração ao checkout, fontes, baseline, B, C2-D, contrato 0.2.0 | status/controles conhecidos e ausência de operações | `OWNERSHIP_OR_MUTATION_VIOLATION` |
| QA10 | Veredito **restrito** à igualdade de bytes do arquivo 3; G4 e L1 continuam bloqueados | revisão de claims, gates explícitos | `UNSUPPORTED_PROMOTION` |

**Distinções obrigatórias:** `SOURCE_BYTES_MATCH_F1` para o arquivo 3 **não significa** `SOURCE_DRIFT_RESOLVED` para todos os metadados; `F4_L0_QA_PASS_SCOPED_BYTES_ONLY` **não significa** `F4_L0_REAL_SOURCE_SHAPE_WITNESSED_SCOPED` ou `F4_L1_LOCAL_REAL_READER_QUALIFIED_SCOPED`.

Revisor não deve modificar o próprio objeto auditado para torná-lo verificável. Para findings, indicar categoria, consequência, reprodução privada e owner responsável. Não incluir caminho real/identificador científico no resumo público.
