# Contrato efêmero de apresentação legada — proposta 0.2.0

Proposta de B (/root/model_b), integrada pelo coordenador.
RECOMMENDED_PROPOSED / ARC09_APPROVAL_REQUIRED. Não aprovado ou implementado.
Descriptor atlas-legacy-presentation, autoridade LEGACY_DERIVED, privado e descartável. Não é Caderno,RO-Crate,ciência aprovada ou nova fonte autoritativa.

## Fronteira e envelope

Candidata O1→O3: processo externo LOCAL lê allowlist autorizada e produz JSON temporário privado; futuro painel segregado seleciona File API,valida e mantém só RAM. Browser não lê fonte original,sem endpoint upload/host paths. Nova entrada contradiz reader003 Caderno-exclusivo: aprovação ARC09 antes de implementar,sem fallback Catalog/load_package/to_read_model. SDK,contextos/schema,validadores e caminho C4 independentes.

Cada descriptor representa UMA fonte/snapshot e um payload qualificante com escopo explícito; até3 arquivos inspecionados pelo externo não se tornam automaticamente uma fonte global. bytes_sha256 é SHA256 dos bytes exatos do arquivo qualificante,sem canonização,hash de parser ou concatenação implícita. Recibo privado externo liga seleção,arquivo/offsets,versão do processo e política de parsing a snapshot_id e access_policy_id; fonte/snapshot não autenticam origem. Se uma entrada exigir múltiplos payloads qualificantes distintos, emitir contextos separados,sem somar snapshots sobrepostos ou fundir fontes.

observed_at/generated_at/expires_at são técnicos; scientific_at null quando desconhecido. Formato/perfil originais são declarações literais,sem prova de conformidade. descriptor_schema,descriptor_semantics,literal_comparison,source_profile_assessment,authenticity e scientific_approval são eixos distintos. PASS de apresentação não afirma autenticidade/ciência/padrão.

## Identidade, árvore e domínio

Chave nativa: fonte+snapshot+native_id comprovado. Navigation IDs sempre DERIVED_FOR_PRESENTATION,temporários e distintos de admissão. Colisões mantêm ocorrências/locator; não escolher primeiro/último. REFERÊNCIA RESOLVED exige alvo original único no contexto,cujos IDs/localizadores comprovem o vínculo. Alvo pode ser nó SOURCE_ENTITY,tabela,linha ou asset original; stub não satisfaz resolução da entidade fonte.

Run original observado no grafo conserva SOURCE_ENTITY e o ID original realmente comprovado,mesmo isolado; seu binding_gap e ausência de percurso contínuo permanecem. Apenas quando há referência a Run NÃO carregado pode existir stub DECLARED_EXTERNAL_REFERENCE,native_id null,EXTERNAL_DECLARED. Stub é conveniência visual e não substitui um Run fonte observado F1.

NULL_ENDPOINT,UNRESOLVED,COLLISION e EXTERNAL_DECLARED são visíveis. Duplicatas têm repeat_group/occurrence,sem deduplicação. Tipos/famílias/parent_key explícitos; Unknown sem inferência. Pertencimento organizacional não prova linhagem. Órfãos/Run isolado sem pai/Project/Experiment inventado.

RF/RNF/RES são opcionais por domínio. UNADMITTED_NATIVE_RF conserva native_id null; campos preenchidos/navigation ID não admitem RF. ADMITTED_NATIVE_RF significa apenas identidade nativa comprovada,sem aceite científico. RNF/RES desconhecidas não são inferidas por nome/MIME/filename. File permanece File; produto exige papel e vínculo explícitos.

## Literais e perdas

Preservar headers,chaves,ordem de colunas/linhas,todas células selecionadas,ordinal de origem,tipo,literal,lexeme,unidade,precisão e ausência. Inteiro/decimal são transportados como texto tipado; string numérica continua string,booleano não é número. Null,missing,string vazia e zero distintos. Categoria ausente MISSING,sem inventar valor. Campos RF apontam índices de células originais,sem cópia normalizada divergente.

Campos selecionados fora da UI entram em unmapped_fields. Campo impossível/quota excedida não é descartado: recusar ou registrar perda explícita com escopo antes de exposição; nunca truncar por quota. Arrays/objetos são texto JSON literal com lexema preservado,sem executar; sua interpretação futura deve validar forma/tipo e profundidade sem coerção. fonte permanece meio de recuperação; descriptor não é cópia integral do acervo.

## Schema candidato fechado

Schema DOCUMENTAL, Draft2020-12. Objetos fechados; referências cruzadas,contagens,proveniência,bytes,tempos e literalidade exigem invariantes semânticas adicionais. Validador JSON Schema formal não foi executado nesta F2.
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "urn:atlas:proposal:legacy-presentation:0.2.0",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "format",
    "version",
    "authority",
    "synthetic",
    "source",
    "snapshot",
    "validation",
    "policy",
    "nodes",
    "tables",
    "relations",
    "assets",
    "unmapped_fields",
    "coverage",
    "gaps"
  ],
  "properties": {
    "format": {
      "const": "atlas-legacy-presentation"
    },
    "version": {
      "const": "0.2.0"
    },
    "authority": {
      "const": "LEGACY_DERIVED"
    },
    "synthetic": {
      "type": "boolean"
    },
    "source": {
      "$ref": "#/$defs/source"
    },
    "snapshot": {
      "$ref": "#/$defs/snapshot"
    },
    "validation": {
      "$ref": "#/$defs/validation"
    },
    "policy": {
      "$ref": "#/$defs/policy"
    },
    "nodes": {
      "type": "array",
      "maxItems": 10000,
      "items": {
        "$ref": "#/$defs/node"
      }
    },
    "tables": {
      "type": "array",
      "maxItems": 128,
      "items": {
        "$ref": "#/$defs/table"
      }
    },
    "relations": {
      "type": "array",
      "maxItems": 100000,
      "items": {
        "$ref": "#/$defs/relation"
      }
    },
    "assets": {
      "type": "array",
      "maxItems": 10000,
      "items": {
        "$ref": "#/$defs/asset"
      }
    },
    "unmapped_fields": {
      "type": "array",
      "maxItems": 100000,
      "items": {
        "$ref": "#/$defs/unmapped"
      }
    },
    "coverage": {
      "$ref": "#/$defs/coverage"
    },
    "gaps": {
      "type": "array",
      "maxItems": 10000,
      "items": {
        "$ref": "#/$defs/gap"
      }
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "synthetic": {
            "const": false
          }
        }
      },
      "then": {
        "properties": {
          "snapshot": {
            "properties": {
              "binding_basis": {
                "const": "OBSERVED_BYTES_AND_POLICY"
              },
              "digest_status": {
                "const": "OBSERVED_BYTES"
              },
              "bytes_sha256": {
                "type": "string",
                "pattern": "^[0-9a-f]{64}$"
              }
            }
          }
        }
      }
    }
  ],
  "$defs": {
    "text": {
      "type": "string",
      "maxLength": 65536
    },
    "nullable_text": {
      "type": [
        "string",
        "null"
      ],
      "maxLength": 65536
    },
    "navigation_id": {
      "type": "string",
      "pattern": "^nav:[A-Za-z0-9._:-]+$",
      "maxLength": 512
    },
    "source": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "source_id",
        "scope",
        "original_format",
        "original_profile_declared",
        "availability",
        "access_policy_id",
        "declared_scientific_review"
      ],
      "properties": {
        "source_id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 512
        },
        "scope": {
          "$ref": "#/$defs/text"
        },
        "original_format": {
          "type": "string",
          "minLength": 1,
          "maxLength": 256
        },
        "original_profile_declared": {
          "$ref": "#/$defs/nullable_text"
        },
        "availability": {
          "enum": [
            "OBSERVED_AVAILABLE",
            "UNAVAILABLE",
            "UNKNOWN",
            "CHANGED",
            "EXPIRED"
          ]
        },
        "access_policy_id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 512
        },
        "declared_scientific_review": {
          "$ref": "#/$defs/nullable_text"
        }
      }
    },
    "snapshot": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "snapshot_id",
        "binding_basis",
        "bytes_sha256",
        "digest_status",
        "observed_at",
        "scientific_at",
        "generated_at",
        "expires_at",
        "freshness"
      ],
      "properties": {
        "snapshot_id": {
          "type": "string",
          "minLength": 1,
          "maxLength": 512
        },
        "binding_basis": {
          "enum": [
            "OBSERVED_BYTES_AND_POLICY",
            "SYNTHETIC_FIXTURE"
          ]
        },
        "bytes_sha256": {
          "type": [
            "string",
            "null"
          ],
          "pattern": "^[0-9a-f]{64}$"
        },
        "digest_status": {
          "enum": [
            "OBSERVED_BYTES",
            "NOT_COMPUTED"
          ]
        },
        "observed_at": {
          "type": "string",
          "format": "date-time"
        },
        "scientific_at": {
          "type": [
            "string",
            "null"
          ],
          "format": "date-time"
        },
        "generated_at": {
          "type": "string",
          "format": "date-time"
        },
        "expires_at": {
          "type": "string",
          "format": "date-time"
        },
        "freshness": {
          "const": "OBSERVED_SNAPSHOT_ONLY"
        }
      }
    },
    "validation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "descriptor_schema",
        "descriptor_semantics",
        "literal_comparison",
        "source_profile_assessment",
        "authenticity",
        "scientific_approval"
      ],
      "properties": {
        "descriptor_schema": {
          "enum": [
            "NOT_RUN",
            "PASS",
            "FAIL"
          ]
        },
        "descriptor_semantics": {
          "enum": [
            "NOT_RUN",
            "PASS",
            "FAIL"
          ]
        },
        "literal_comparison": {
          "enum": [
            "NOT_PERFORMED",
            "SOURCE_FIELD_COMPARED",
            "SOURCE_ROW_COMPARED"
          ]
        },
        "source_profile_assessment": {
          "const": "NOT_ASSERTED"
        },
        "authenticity": {
          "const": "NOT_VERIFIED"
        },
        "scientific_approval": {
          "const": "NOT_EVALUATED"
        }
      }
    },
    "policy": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "source_access",
        "max_descriptor_bytes",
        "ttl_max_seconds",
        "browser_persistence",
        "automatic_uri_access"
      ],
      "properties": {
        "source_access": {
          "const": "EXTERNAL_EXACT_ALLOWLIST_ONLY"
        },
        "max_descriptor_bytes": {
          "const": 33554432
        },
        "ttl_max_seconds": {
          "const": 3600
        },
        "browser_persistence": {
          "const": "MEMORY_ONLY"
        },
        "automatic_uri_access": {
          "const": false
        }
      }
    },
    "identity": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "native_id",
        "navigation_id",
        "navigation_id_kind",
        "occurrence",
        "locator"
      ],
      "properties": {
        "native_id": {
          "type": [
            "string",
            "null"
          ],
          "minLength": 1,
          "maxLength": 4096
        },
        "navigation_id": {
          "$ref": "#/$defs/navigation_id"
        },
        "navigation_id_kind": {
          "const": "DERIVED_FOR_PRESENTATION"
        },
        "occurrence": {
          "type": "integer",
          "minimum": 0
        },
        "locator": {
          "type": "string",
          "maxLength": 8192
        }
      }
    },
    "reference": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "source_id",
        "snapshot_id",
        "declared_id",
        "target_navigation_id",
        "resolution",
        "evidence_locator"
      ],
      "properties": {
        "source_id": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 512
        },
        "snapshot_id": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 512
        },
        "declared_id": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 4096
        },
        "target_navigation_id": {
          "anyOf": [
            {
              "$ref": "#/$defs/navigation_id"
            },
            {
              "type": "null"
            }
          ]
        },
        "resolution": {
          "enum": [
            "RESOLVED",
            "NULL_ENDPOINT",
            "UNRESOLVED",
            "COLLISION",
            "EXTERNAL_DECLARED"
          ]
        },
        "evidence_locator": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 8192
        }
      }
    },
    "cell": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "type",
        "literal",
        "lexeme",
        "unit",
        "precision",
        "absence"
      ],
      "properties": {
        "type": {
          "enum": [
            "string",
            "integer",
            "decimal",
            "boolean",
            "null",
            "missing",
            "array",
            "object"
          ]
        },
        "literal": {
          "$ref": "#/$defs/nullable_text"
        },
        "lexeme": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 131072
        },
        "unit": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 256
        },
        "precision": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 128
        },
        "absence": {
          "enum": [
            null,
            "NULL",
            "MISSING"
          ]
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "type": {
                "enum": [
                  "string",
                  "integer",
                  "decimal",
                  "boolean",
                  "array",
                  "object"
                ]
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "type": "string"
              },
              "lexeme": {
                "type": "string"
              },
              "absence": {
                "const": null
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "type": {
                "const": "integer"
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "pattern": "^-?(0|[1-9][0-9]*)$"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "type": {
                "const": "decimal"
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "pattern": "^-?(0|[1-9][0-9]*)(\\.[0-9]+)?([eE][+-]?[0-9]+)?$"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "type": {
                "const": "boolean"
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "enum": [
                  "true",
                  "false"
                ]
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "type": {
                "const": "null"
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "const": null
              },
              "lexeme": {
                "const": "null"
              },
              "absence": {
                "const": "NULL"
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "type": {
                "const": "missing"
              }
            }
          },
          "then": {
            "properties": {
              "literal": {
                "const": null
              },
              "lexeme": {
                "const": null
              },
              "absence": {
                "const": "MISSING"
              }
            }
          }
        }
      ]
    },
    "node": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "identity",
        "kind",
        "original_type",
        "entity_status",
        "label_literal",
        "family_literal",
        "parent_key_literal",
        "parent",
        "tree_state",
        "external_reference",
        "binding_gap"
      ],
      "properties": {
        "identity": {
          "$ref": "#/$defs/identity"
        },
        "kind": {
          "enum": [
            "Project",
            "Family",
            "Experiment",
            "Run",
            "Other",
            "Unknown"
          ]
        },
        "original_type": {
          "$ref": "#/$defs/nullable_text"
        },
        "entity_status": {
          "enum": [
            "SOURCE_ENTITY",
            "DECLARED_EXTERNAL_REFERENCE"
          ]
        },
        "label_literal": {
          "$ref": "#/$defs/text"
        },
        "family_literal": {
          "$ref": "#/$defs/nullable_text"
        },
        "parent_key_literal": {
          "$ref": "#/$defs/nullable_text"
        },
        "parent": {
          "$ref": "#/$defs/reference"
        },
        "tree_state": {
          "enum": [
            "ROOT_DECLARED",
            "PARENT_RESOLVED",
            "ORPHAN",
            "PARENT_UNKNOWN",
            "RUN_EXTERNAL_ISOLATED"
          ]
        },
        "external_reference": {
          "anyOf": [
            {
              "$ref": "#/$defs/reference"
            },
            {
              "type": "null"
            }
          ]
        },
        "binding_gap": {
          "type": "boolean"
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "entity_status": {
                "const": "DECLARED_EXTERNAL_REFERENCE"
              }
            }
          },
          "then": {
            "properties": {
              "identity": {
                "properties": {
                  "native_id": {
                    "const": null
                  }
                }
              },
              "tree_state": {
                "const": "RUN_EXTERNAL_ISOLATED"
              },
              "binding_gap": {
                "const": true
              },
              "external_reference": {
                "$ref": "#/$defs/reference"
              }
            }
          }
        }
      ]
    },
    "column": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "ordinal",
        "native_key",
        "header_literal"
      ],
      "properties": {
        "ordinal": {
          "type": "integer",
          "minimum": 0,
          "maximum": 255
        },
        "native_key": {
          "$ref": "#/$defs/nullable_text"
        },
        "header_literal": {
          "$ref": "#/$defs/text"
        }
      }
    },
    "column_index": {
      "type": [
        "integer",
        "null"
      ],
      "minimum": 0,
      "maximum": 255
    },
    "requirement_fields": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "id",
        "module",
        "title",
        "description",
        "acceptance_criteria",
        "category"
      ],
      "properties": {
        "id": {
          "$ref": "#/$defs/column_index"
        },
        "module": {
          "$ref": "#/$defs/column_index"
        },
        "title": {
          "$ref": "#/$defs/column_index"
        },
        "description": {
          "$ref": "#/$defs/column_index"
        },
        "acceptance_criteria": {
          "$ref": "#/$defs/column_index"
        },
        "category": {
          "$ref": "#/$defs/column_index"
        }
      }
    },
    "requirement": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "kind",
        "native_id",
        "admission",
        "admission_evidence_locator",
        "fields",
        "category_status"
      ],
      "properties": {
        "kind": {
          "enum": [
            "RF",
            "RNF",
            "RES"
          ]
        },
        "native_id": {
          "type": [
            "string",
            "null"
          ],
          "minLength": 1,
          "maxLength": 4096
        },
        "admission": {
          "enum": [
            "ADMITTED_NATIVE_RF",
            "UNADMITTED_NATIVE_RF",
            "NOT_EVALUATED",
            "NOT_APPLICABLE"
          ]
        },
        "admission_evidence_locator": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 8192
        },
        "fields": {
          "$ref": "#/$defs/requirement_fields"
        },
        "category_status": {
          "enum": [
            "MISSING",
            "PRESENT",
            "UNKNOWN"
          ]
        }
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "admission": {
                "const": "UNADMITTED_NATIVE_RF"
              }
            }
          },
          "then": {
            "properties": {
              "kind": {
                "const": "RF"
              },
              "native_id": {
                "const": null
              }
            }
          }
        },
        {
          "if": {
            "properties": {
              "admission": {
                "const": "ADMITTED_NATIVE_RF"
              }
            }
          },
          "then": {
            "properties": {
              "kind": {
                "const": "RF"
              },
              "native_id": {
                "type": "string",
                "minLength": 1
              },
              "admission_evidence_locator": {
                "type": "string",
                "minLength": 1
              }
            }
          }
        }
      ]
    },
    "row": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "identity",
        "ordinal",
        "cells",
        "requirement",
        "run_binding",
        "binding_gap"
      ],
      "properties": {
        "identity": {
          "$ref": "#/$defs/identity"
        },
        "ordinal": {
          "type": "integer",
          "minimum": 0
        },
        "cells": {
          "type": "array",
          "maxItems": 256,
          "items": {
            "$ref": "#/$defs/cell"
          }
        },
        "requirement": {
          "anyOf": [
            {
              "$ref": "#/$defs/requirement"
            },
            {
              "type": "null"
            }
          ]
        },
        "run_binding": {
          "$ref": "#/$defs/reference"
        },
        "binding_gap": {
          "type": "boolean"
        }
      }
    },
    "table": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "identity",
        "title_literal",
        "domain",
        "domain_origin",
        "record_binding",
        "columns",
        "rows"
      ],
      "properties": {
        "identity": {
          "$ref": "#/$defs/identity"
        },
        "title_literal": {
          "$ref": "#/$defs/text"
        },
        "domain": {
          "enum": [
            "RF",
            "RNF",
            "RES",
            "UNKNOWN",
            "OTHER"
          ]
        },
        "domain_origin": {
          "enum": [
            "DECLARED",
            "UNKNOWN"
          ]
        },
        "record_binding": {
          "$ref": "#/$defs/reference"
        },
        "columns": {
          "type": "array",
          "maxItems": 256,
          "items": {
            "$ref": "#/$defs/column"
          }
        },
        "rows": {
          "type": "array",
          "maxItems": 100000,
          "items": {
            "$ref": "#/$defs/row"
          }
        }
      }
    },
    "relation": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "identity",
        "kind_literal",
        "semantics",
        "direction",
        "from",
        "to",
        "evidence_locator",
        "issues",
        "repeat_group",
        "repeat_occurrence",
        "binding_gap"
      ],
      "properties": {
        "identity": {
          "$ref": "#/$defs/identity"
        },
        "kind_literal": {
          "$ref": "#/$defs/nullable_text"
        },
        "semantics": {
          "enum": [
            "ORGANIZATIONAL_MEMBERSHIP",
            "DECLARED_LINEAGE",
            "DECLARED_BINDING",
            "NEUTRAL_MENTION",
            "UNKNOWN"
          ]
        },
        "direction": {
          "enum": [
            "FROM_TO",
            "UNDIRECTED",
            "UNKNOWN"
          ]
        },
        "from": {
          "$ref": "#/$defs/reference"
        },
        "to": {
          "$ref": "#/$defs/reference"
        },
        "evidence_locator": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 8192
        },
        "issues": {
          "type": "array",
          "maxItems": 32,
          "items": {
            "type": "string",
            "maxLength": 256
          }
        },
        "repeat_group": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 512
        },
        "repeat_occurrence": {
          "type": "integer",
          "minimum": 1
        },
        "binding_gap": {
          "type": "boolean"
        }
      }
    },
    "asset": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "identity",
        "kind",
        "original_type",
        "label_literal",
        "declared_product_role",
        "declared_binding",
        "media_type_literal",
        "uri_literal",
        "availability",
        "opened"
      ],
      "properties": {
        "identity": {
          "$ref": "#/$defs/identity"
        },
        "kind": {
          "enum": [
            "File",
            "Product",
            "ProductGroup",
            "ResourceDocument",
            "DossierAssessment",
            "DossierPackage",
            "Other",
            "Unknown"
          ]
        },
        "original_type": {
          "$ref": "#/$defs/nullable_text"
        },
        "label_literal": {
          "$ref": "#/$defs/text"
        },
        "declared_product_role": {
          "$ref": "#/$defs/nullable_text"
        },
        "declared_binding": {
          "$ref": "#/$defs/reference"
        },
        "media_type_literal": {
          "type": [
            "string",
            "null"
          ],
          "maxLength": 256
        },
        "uri_literal": {
          "$ref": "#/$defs/nullable_text"
        },
        "availability": {
          "enum": [
            "OBSERVED_AVAILABLE",
            "DECLARED_ONLY",
            "UNVERIFIED",
            "MISSING",
            "EXTERNAL_UNRESOLVED",
            "UNKNOWN",
            "INTEGRITY_MISMATCH"
          ]
        },
        "opened": {
          "const": false
        }
      }
    },
    "unmapped": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "owner_navigation_id",
        "locator",
        "source_key_literal",
        "value"
      ],
      "properties": {
        "owner_navigation_id": {
          "anyOf": [
            {
              "$ref": "#/$defs/navigation_id"
            },
            {
              "type": "null"
            }
          ]
        },
        "locator": {
          "type": "string",
          "maxLength": 8192
        },
        "source_key_literal": {
          "$ref": "#/$defs/text"
        },
        "value": {
          "$ref": "#/$defs/cell"
        }
      }
    },
    "count": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "unit",
        "selected",
        "loaded",
        "visible",
        "unavailable",
        "unknown_reason"
      ],
      "properties": {
        "unit": {
          "type": "string",
          "minLength": 1,
          "maxLength": 256
        },
        "selected": {
          "type": [
            "integer",
            "null"
          ],
          "minimum": 0
        },
        "loaded": {
          "type": "integer",
          "minimum": 0
        },
        "visible": {
          "type": [
            "integer",
            "null"
          ],
          "minimum": 0
        },
        "unavailable": {
          "type": [
            "integer",
            "null"
          ],
          "minimum": 0
        },
        "unknown_reason": {
          "$ref": "#/$defs/nullable_text"
        }
      }
    },
    "coverage": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "population",
        "global_archive",
        "global_history",
        "global_total",
        "global_percentage",
        "snapshot_overlap",
        "counts"
      ],
      "properties": {
        "population": {
          "enum": [
            "SELECTED_QUALIFYING_PAYLOAD",
            "SYNTHETIC_FIXTURE"
          ]
        },
        "global_archive": {
          "const": "UNKNOWN_UPSTREAM"
        },
        "global_history": {
          "const": "GLOBAL_UNPROVEN"
        },
        "global_total": {
          "const": null
        },
        "global_percentage": {
          "const": null
        },
        "snapshot_overlap": {
          "enum": [
            "NOT_SUMMED",
            "UNKNOWN"
          ]
        },
        "counts": {
          "type": "array",
          "maxItems": 256,
          "items": {
            "$ref": "#/$defs/count"
          }
        }
      }
    },
    "gap": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "code",
        "scope",
        "count",
        "unit",
        "note"
      ],
      "properties": {
        "code": {
          "type": "string",
          "minLength": 1,
          "maxLength": 256
        },
        "scope": {
          "$ref": "#/$defs/text"
        },
        "count": {
          "type": [
            "integer",
            "null"
          ],
          "minimum": 0
        },
        "unit": {
          "type": "string",
          "minLength": 1,
          "maxLength": 256
        },
        "note": {
          "$ref": "#/$defs/text"
        }
      }
    }
  }
}
```

## Invariantes adicionais

1. Navigation IDs únicos por importação; contexto operacional inclui sessão+fonte+snapshot+ocorrência. RESOLVED corresponde a alvo original único e ID declarado; nunca a stub. Referência externa desconhecida usa contexto null e não resolve por texto em outra fonte.
2. Native ID nunca vem de ordinal,path,hash,nome ou navigation ID. Colisões retêm todas ocorrências. NULL_ENDPOINT exige declared_id e target null;UNRESOLVED/COLLISION não escolhem target;EXTERNAL_DECLARED pode apontar stub só para navegação visual.
3. SOURCE_ENTITY conserva tipo/ID provados ou Unknown; não exigir native_id existente quando fonte não o tem. Stub tem native_id null e gaptrue. Parent key não vira causalidade; ciclos/órfãos retidos como anomalias sem recursão infinita ou pais inventados.
4. Colunas/linhas têm ordinais de origem contíguos desdezero; cada linha uma célula por coluna. Filtro mantém ordinais e ordem original recuperável. Campos RF apontam colunas existentes;category MISSING deve corresponder célula missing/null declarado ou coluna inexistente explicitamente,sem confundir os estados originais.
5. Literal/lexeme/tipo coerentes,unidades/precisão declaradas sem conversão. Arrays/objetos e strings são parseados somente para validação inerte; token bruto preservado. RF admitida tem evidência e ID consistente com célula quando houver; não admitida tem IDnull.
6. Tipo original File permanece kindFile mesmo com papelproduto declarado. Product exige declaração/vínculo; URI não autoriza abertura. Tabelas domainUNKNOWN mantêm domínio desconhecido; RNF/RES só explícitas.
7. Loaded reconciliado com coleções e unidade;visible null antes de UI real. Contagens SOURCE_ENTITY e stubs devem ser unidades separadas quando ambos existem; nodes inclui ocorrências visuais,sem promover stubs a registros originais. Contagens de endpoints,arestas,colisões,grupos/excedentes podem se sobrepor e NÃO são partição aditiva.
8. Não somar snapshots sobrepostos;global_total/global_percentage null nesta proposta. Zero em tabela conhecida não prova ausência upstream;sem0/0.
9. observed_at<=generated_at<expires_at;expires-generated<=3600s. Quotas byte/depth/linhas agregadas antes/durante parsing. NOT_RUN/FAIL não permitem disponibilizar snapshot como validado na futura UI.
10. Instância real exige bytes_sha256 observado e recibo privado com escopo/política;fixture não inventa digest. Unknownformat/version/extraproperty é recusa,sem downgrade.
11. Toda apresentação mostra LEGACY_DERIVED,validação,gaps,expiração,autenticidade não verificada e ciência não avaliada. Browser OBSERVED_SNAPSHOT_ONLY,sem monitoração da origem.

## Exemplo sintético A — RF literal e referência Run externa

Inteiramente inventado; não reproduz linha/ID/nome/URI/digest F1. Stub NÃO é reclassificação do Run fonte observado F1. Relógio de avaliação ilustrativo:12:05Z em2026-10-30,antes da expiração; datas são dados da fixture. Estados NOT_RUN não alegam execução e visible null significa nenhuma UI.
```json
{
  "format": "atlas-legacy-presentation",
  "version": "0.2.0",
  "authority": "LEGACY_DERIVED",
  "synthetic": true,
  "source": {
    "source_id": "synthetic-a",
    "scope": "Fixture pública inventada A",
    "original_format": "synthetic-json",
    "original_profile_declared": null,
    "availability": "OBSERVED_AVAILABLE",
    "access_policy_id": "fixture-only-a",
    "declared_scientific_review": null
  },
  "snapshot": {
    "snapshot_id": "fixture-a-1",
    "binding_basis": "SYNTHETIC_FIXTURE",
    "bytes_sha256": null,
    "digest_status": "NOT_COMPUTED",
    "observed_at": "2026-10-30T12:00:00Z",
    "scientific_at": null,
    "generated_at": "2026-10-30T12:01:00Z",
    "expires_at": "2026-10-30T13:01:00Z",
    "freshness": "OBSERVED_SNAPSHOT_ONLY"
  },
  "validation": {
    "descriptor_schema": "NOT_RUN",
    "descriptor_semantics": "NOT_RUN",
    "literal_comparison": "NOT_PERFORMED",
    "source_profile_assessment": "NOT_ASSERTED",
    "authenticity": "NOT_VERIFIED",
    "scientific_approval": "NOT_EVALUATED"
  },
  "policy": {
    "source_access": "EXTERNAL_EXACT_ALLOWLIST_ONLY",
    "max_descriptor_bytes": 33554432,
    "ttl_max_seconds": 3600,
    "browser_persistence": "MEMORY_ONLY",
    "automatic_uri_access": false
  },
  "nodes": [
    {
      "identity": {
        "native_id": "FAMILY-SYN-A",
        "navigation_id": "nav:a-family",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/nodes/0"
      },
      "kind": "Family",
      "original_type": "Family",
      "entity_status": "SOURCE_ENTITY",
      "label_literal": "Família sintética A",
      "family_literal": "Família sintética A",
      "parent_key_literal": null,
      "parent": {
        "source_id": "synthetic-a",
        "snapshot_id": "fixture-a-1",
        "declared_id": null,
        "target_navigation_id": null,
        "resolution": "NULL_ENDPOINT",
        "evidence_locator": "/nodes/0/parent"
      },
      "tree_state": "ROOT_DECLARED",
      "external_reference": null,
      "binding_gap": false
    },
    {
      "identity": {
        "native_id": "RECORD-SYN-A",
        "navigation_id": "nav:a-record",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/nodes/1"
      },
      "kind": "Other",
      "original_type": "Record",
      "entity_status": "SOURCE_ENTITY",
      "label_literal": "Registro sintético",
      "family_literal": "Família sintética A",
      "parent_key_literal": "FAMILY-SYN-A",
      "parent": {
        "source_id": "synthetic-a",
        "snapshot_id": "fixture-a-1",
        "declared_id": "FAMILY-SYN-A",
        "target_navigation_id": "nav:a-family",
        "resolution": "RESOLVED",
        "evidence_locator": "/nodes/1/parent"
      },
      "tree_state": "PARENT_RESOLVED",
      "external_reference": null,
      "binding_gap": false
    },
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:a-external-run",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/tables/0/rows/0/run"
      },
      "kind": "Run",
      "original_type": "Run declarado externamente",
      "entity_status": "DECLARED_EXTERNAL_REFERENCE",
      "label_literal": "Execução externa declarada",
      "family_literal": null,
      "parent_key_literal": null,
      "parent": {
        "source_id": null,
        "snapshot_id": null,
        "declared_id": null,
        "target_navigation_id": null,
        "resolution": "NULL_ENDPOINT",
        "evidence_locator": null
      },
      "tree_state": "RUN_EXTERNAL_ISOLATED",
      "external_reference": {
        "source_id": null,
        "snapshot_id": null,
        "declared_id": "RUN-EXT-SYN-A",
        "target_navigation_id": null,
        "resolution": "EXTERNAL_DECLARED",
        "evidence_locator": "/tables/0/rows/0/run"
      },
      "binding_gap": true
    }
  ],
  "tables": [
    {
      "identity": {
        "native_id": "TABLE-SYN-A",
        "navigation_id": "nav:a-table",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/tables/0"
      },
      "title_literal": "RF sintéticas",
      "domain": "RF",
      "domain_origin": "DECLARED",
      "record_binding": {
        "source_id": "synthetic-a",
        "snapshot_id": "fixture-a-1",
        "declared_id": "RECORD-SYN-A",
        "target_navigation_id": "nav:a-record",
        "resolution": "RESOLVED",
        "evidence_locator": "/tables/0/record_id"
      },
      "columns": [
        {
          "ordinal": 0,
          "native_key": "id",
          "header_literal": "ID"
        },
        {
          "ordinal": 1,
          "native_key": "module",
          "header_literal": "Núcleo"
        },
        {
          "ordinal": 2,
          "native_key": "title",
          "header_literal": "Título"
        },
        {
          "ordinal": 3,
          "native_key": "description",
          "header_literal": "Descrição"
        },
        {
          "ordinal": 4,
          "native_key": "acceptance",
          "header_literal": "Critérios de aceite"
        },
        {
          "ordinal": 5,
          "native_key": "category",
          "header_literal": "Categoria"
        }
      ],
      "rows": [
        {
          "identity": {
            "native_id": "ROW-SYN-A",
            "navigation_id": "nav:a-row",
            "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
            "occurrence": 0,
            "locator": "/tables/0/rows/0"
          },
          "ordinal": 0,
          "cells": [
            {
              "type": "string",
              "literal": "RF-SYN-001",
              "lexeme": "\"RF-SYN-001\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "Módulo sintético",
              "lexeme": "\"Módulo sintético\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "Conservar o texto",
              "lexeme": "\"Conservar o texto\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "Exibir o conteúdo literal sem executar marcação.",
              "lexeme": "\"Exibir o conteúdo literal sem executar marcação.\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "O detalhe conserva exatamente esta frase.",
              "lexeme": "\"O detalhe conserva exatamente esta frase.\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "missing",
              "literal": null,
              "lexeme": null,
              "unit": null,
              "precision": null,
              "absence": "MISSING"
            }
          ],
          "requirement": {
            "kind": "RF",
            "native_id": "RF-SYN-001",
            "admission": "ADMITTED_NATIVE_RF",
            "admission_evidence_locator": "/tables/0/rows/0/id",
            "fields": {
              "id": 0,
              "module": 1,
              "title": 2,
              "description": 3,
              "acceptance_criteria": 4,
              "category": 5
            },
            "category_status": "MISSING"
          },
          "run_binding": {
            "source_id": null,
            "snapshot_id": null,
            "declared_id": "RUN-EXT-SYN-A",
            "target_navigation_id": "nav:a-external-run",
            "resolution": "EXTERNAL_DECLARED",
            "evidence_locator": "/tables/0/rows/0/run"
          },
          "binding_gap": true
        }
      ]
    }
  ],
  "relations": [
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:a-binding",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/tables/0/rows/0/run"
      },
      "kind_literal": "declared_run",
      "semantics": "DECLARED_BINDING",
      "direction": "FROM_TO",
      "from": {
        "source_id": "synthetic-a",
        "snapshot_id": "fixture-a-1",
        "declared_id": "ROW-SYN-A",
        "target_navigation_id": "nav:a-row",
        "resolution": "RESOLVED",
        "evidence_locator": "/tables/0/rows/0"
      },
      "to": {
        "source_id": null,
        "snapshot_id": null,
        "declared_id": "RUN-EXT-SYN-A",
        "target_navigation_id": "nav:a-external-run",
        "resolution": "EXTERNAL_DECLARED",
        "evidence_locator": "/tables/0/rows/0/run"
      },
      "evidence_locator": "/tables/0/rows/0/run",
      "issues": [
        "BINDING_GAP"
      ],
      "repeat_group": null,
      "repeat_occurrence": 1,
      "binding_gap": true
    }
  ],
  "assets": [
    {
      "identity": {
        "native_id": "FILE-SYN-A",
        "navigation_id": "nav:a-file",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/files/0"
      },
      "kind": "File",
      "original_type": "File",
      "label_literal": "Documento sintético.txt",
      "declared_product_role": null,
      "declared_binding": {
        "source_id": null,
        "snapshot_id": null,
        "declared_id": null,
        "target_navigation_id": null,
        "resolution": "NULL_ENDPOINT",
        "evidence_locator": null
      },
      "media_type_literal": "text/plain",
      "uri_literal": null,
      "availability": "UNVERIFIED",
      "opened": false
    }
  ],
  "unmapped_fields": [],
  "coverage": {
    "population": "SYNTHETIC_FIXTURE",
    "global_archive": "UNKNOWN_UPSTREAM",
    "global_history": "GLOBAL_UNPROVEN",
    "global_total": null,
    "global_percentage": null,
    "snapshot_overlap": "NOT_SUMMED",
    "counts": [
      {
        "unit": "presentation_node_occurrences",
        "selected": 3,
        "loaded": 3,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "source_nodes",
        "selected": 2,
        "loaded": 2,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "external_reference_stubs",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "tables",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "rows",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "relations",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "assets",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      }
    ]
  },
  "gaps": [
    {
      "code": "RUN_EXTERNAL_ISOLATED",
      "scope": "Fixture A",
      "count": 1,
      "unit": "declared external Run stubs",
      "note": "Stub sem prova de execução carregada ou caminho contínuo."
    },
    {
      "code": "MISSING_CATEGORY",
      "scope": "Fixture A",
      "count": 1,
      "unit": "rows",
      "note": "Categoria ausente preservada."
    },
    {
      "code": "RNF_RES_UNKNOWN",
      "scope": "Fixture A",
      "count": null,
      "unit": "domain populations",
      "note": "Não inferir RNF/RES."
    }
  ]
}
```

## Exemplo sintético B — RF não admitida,precisão e ambiguidades

Inteiramente inventado. Decimal extensa e inteiro>2^53 permanecem texto tipado;string numérica,false,null e missing distintos. Contagens de anomalias são sanitizadas da própria fixture,não F1. Relógio ilustrativo14:05Z em2026-10-30; nenhuma execução real alegada.
```json
{
  "format": "atlas-legacy-presentation",
  "version": "0.2.0",
  "authority": "LEGACY_DERIVED",
  "synthetic": true,
  "source": {
    "source_id": "synthetic-b",
    "scope": "Fixture pública inventada B",
    "original_format": "synthetic-json",
    "original_profile_declared": "rótulo não validado",
    "availability": "OBSERVED_AVAILABLE",
    "access_policy_id": "fixture-only-b",
    "declared_scientific_review": "UNKNOWN"
  },
  "snapshot": {
    "snapshot_id": "fixture-b-1",
    "binding_basis": "SYNTHETIC_FIXTURE",
    "bytes_sha256": null,
    "digest_status": "NOT_COMPUTED",
    "observed_at": "2026-10-30T14:00:00Z",
    "scientific_at": null,
    "generated_at": "2026-10-30T14:01:00Z",
    "expires_at": "2026-10-30T15:01:00Z",
    "freshness": "OBSERVED_SNAPSHOT_ONLY"
  },
  "validation": {
    "descriptor_schema": "NOT_RUN",
    "descriptor_semantics": "NOT_RUN",
    "literal_comparison": "NOT_PERFORMED",
    "source_profile_assessment": "NOT_ASSERTED",
    "authenticity": "NOT_VERIFIED",
    "scientific_approval": "NOT_EVALUATED"
  },
  "policy": {
    "source_access": "EXTERNAL_EXACT_ALLOWLIST_ONLY",
    "max_descriptor_bytes": 33554432,
    "ttl_max_seconds": 3600,
    "browser_persistence": "MEMORY_ONLY",
    "automatic_uri_access": false
  },
  "nodes": [],
  "tables": [
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:b-table",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/tables/0"
      },
      "title_literal": "Linhas sintéticas não admitidas",
      "domain": "RF",
      "domain_origin": "DECLARED",
      "record_binding": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "RECORD-SYN-MISSING",
        "target_navigation_id": null,
        "resolution": "UNRESOLVED",
        "evidence_locator": "/tables/0/record_id"
      },
      "columns": [
        {
          "ordinal": 0,
          "native_key": "module",
          "header_literal": "Módulo"
        },
        {
          "ordinal": 1,
          "native_key": "title",
          "header_literal": "Título"
        },
        {
          "ordinal": 2,
          "native_key": "measure",
          "header_literal": "Valor"
        },
        {
          "ordinal": 3,
          "native_key": "flag",
          "header_literal": "Flag"
        },
        {
          "ordinal": 4,
          "native_key": "numeric_text",
          "header_literal": "Texto numérico"
        }
      ],
      "rows": [
        {
          "identity": {
            "native_id": null,
            "navigation_id": "nav:b-row-0",
            "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
            "occurrence": 0,
            "locator": "/tables/0/rows/0"
          },
          "ordinal": 0,
          "cells": [
            {
              "type": "string",
              "literal": "Módulo sintético B",
              "lexeme": "\"Módulo sintético B\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "Mesmo título",
              "lexeme": "\"Mesmo título\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "decimal",
              "literal": "0.123456789012345678901",
              "lexeme": "0.123456789012345678901",
              "unit": "1",
              "precision": "21",
              "absence": null
            },
            {
              "type": "boolean",
              "literal": "false",
              "lexeme": "false",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "0.100",
              "lexeme": "\"0.100\"",
              "unit": null,
              "precision": null,
              "absence": null
            }
          ],
          "requirement": {
            "kind": "RF",
            "native_id": null,
            "admission": "UNADMITTED_NATIVE_RF",
            "admission_evidence_locator": null,
            "fields": {
              "id": null,
              "module": 0,
              "title": 1,
              "description": null,
              "acceptance_criteria": null,
              "category": null
            },
            "category_status": "MISSING"
          },
          "run_binding": {
            "source_id": null,
            "snapshot_id": null,
            "declared_id": null,
            "target_navigation_id": null,
            "resolution": "NULL_ENDPOINT",
            "evidence_locator": null
          },
          "binding_gap": true
        },
        {
          "identity": {
            "native_id": null,
            "navigation_id": "nav:b-row-1",
            "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
            "occurrence": 1,
            "locator": "/tables/0/rows/1"
          },
          "ordinal": 1,
          "cells": [
            {
              "type": "string",
              "literal": "Módulo sintético B",
              "lexeme": "\"Módulo sintético B\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "string",
              "literal": "Mesmo título",
              "lexeme": "\"Mesmo título\"",
              "unit": null,
              "precision": null,
              "absence": null
            },
            {
              "type": "integer",
              "literal": "9007199254740993",
              "lexeme": "9007199254740993",
              "unit": "1",
              "precision": null,
              "absence": null
            },
            {
              "type": "null",
              "literal": null,
              "lexeme": "null",
              "unit": null,
              "precision": null,
              "absence": "NULL"
            },
            {
              "type": "missing",
              "literal": null,
              "lexeme": null,
              "unit": null,
              "precision": null,
              "absence": "MISSING"
            }
          ],
          "requirement": {
            "kind": "RF",
            "native_id": null,
            "admission": "UNADMITTED_NATIVE_RF",
            "admission_evidence_locator": null,
            "fields": {
              "id": null,
              "module": 0,
              "title": 1,
              "description": null,
              "acceptance_criteria": null,
              "category": null
            },
            "category_status": "MISSING"
          },
          "run_binding": {
            "source_id": null,
            "snapshot_id": null,
            "declared_id": null,
            "target_navigation_id": null,
            "resolution": "NULL_ENDPOINT",
            "evidence_locator": null
          },
          "binding_gap": true
        }
      ]
    }
  ],
  "relations": [
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:b-rel-0",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/relations/0"
      },
      "kind_literal": "related",
      "semantics": "NEUTRAL_MENTION",
      "direction": "UNKNOWN",
      "from": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": null,
        "target_navigation_id": null,
        "resolution": "NULL_ENDPOINT",
        "evidence_locator": "/relations/0/from"
      },
      "to": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "TARGET-SYN-MISSING",
        "target_navigation_id": null,
        "resolution": "UNRESOLVED",
        "evidence_locator": "/relations/0/to"
      },
      "evidence_locator": "/relations/0",
      "issues": [
        "NULL_ENDPOINT",
        "DECLARED_UNRESOLVED"
      ],
      "repeat_group": null,
      "repeat_occurrence": 1,
      "binding_gap": true
    },
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:b-rel-1",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 0,
        "locator": "/relations/1"
      },
      "kind_literal": "related",
      "semantics": "NEUTRAL_MENTION",
      "direction": "UNKNOWN",
      "from": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "COLLIDING-SYN-ID",
        "target_navigation_id": null,
        "resolution": "COLLISION",
        "evidence_locator": "/relations/1/from"
      },
      "to": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "TARGET-SYN-MISSING",
        "target_navigation_id": null,
        "resolution": "UNRESOLVED",
        "evidence_locator": "/relations/1/to"
      },
      "evidence_locator": "/relations/1",
      "issues": [
        "DECLARED_COLLISION",
        "DECLARED_UNRESOLVED",
        "REPEATED_TRIPLE"
      ],
      "repeat_group": "synthetic-repeat-b",
      "repeat_occurrence": 1,
      "binding_gap": true
    },
    {
      "identity": {
        "native_id": null,
        "navigation_id": "nav:b-rel-2",
        "navigation_id_kind": "DERIVED_FOR_PRESENTATION",
        "occurrence": 1,
        "locator": "/relations/2"
      },
      "kind_literal": "related",
      "semantics": "NEUTRAL_MENTION",
      "direction": "UNKNOWN",
      "from": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "COLLIDING-SYN-ID",
        "target_navigation_id": null,
        "resolution": "COLLISION",
        "evidence_locator": "/relations/2/from"
      },
      "to": {
        "source_id": "synthetic-b",
        "snapshot_id": "fixture-b-1",
        "declared_id": "TARGET-SYN-MISSING",
        "target_navigation_id": null,
        "resolution": "UNRESOLVED",
        "evidence_locator": "/relations/2/to"
      },
      "evidence_locator": "/relations/2",
      "issues": [
        "DECLARED_COLLISION",
        "DECLARED_UNRESOLVED",
        "REPEATED_TRIPLE"
      ],
      "repeat_group": "synthetic-repeat-b",
      "repeat_occurrence": 2,
      "binding_gap": true
    }
  ],
  "assets": [],
  "unmapped_fields": [
    {
      "owner_navigation_id": "nav:b-table",
      "locator": "/tables/0/note",
      "source_key_literal": "note",
      "value": {
        "type": "string",
        "literal": "<script>synthetic()</script>",
        "lexeme": "\"<script>synthetic()</script>\"",
        "unit": null,
        "precision": null,
        "absence": null
      }
    }
  ],
  "coverage": {
    "population": "SYNTHETIC_FIXTURE",
    "global_archive": "UNKNOWN_UPSTREAM",
    "global_history": "GLOBAL_UNPROVEN",
    "global_total": null,
    "global_percentage": null,
    "snapshot_overlap": "NOT_SUMMED",
    "counts": [
      {
        "unit": "presentation_node_occurrences",
        "selected": 0,
        "loaded": 0,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "source_nodes",
        "selected": 0,
        "loaded": 0,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "external_reference_stubs",
        "selected": 0,
        "loaded": 0,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada; unidades originais e de apresentação separadas."
      },
      {
        "unit": "tables",
        "selected": 1,
        "loaded": 1,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "rows",
        "selected": 2,
        "loaded": 2,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "relations",
        "selected": 3,
        "loaded": 3,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      },
      {
        "unit": "assets",
        "selected": 0,
        "loaded": 0,
        "visible": null,
        "unavailable": 0,
        "unknown_reason": "UI não executada."
      }
    ]
  },
  "gaps": [
    {
      "code": "UNRESOLVED_RECORD_ID",
      "scope": "Fixture B",
      "count": 1,
      "unit": "tables",
      "note": "Não inventar registro."
    },
    {
      "code": "UNADMITTED_NATIVE_RF",
      "scope": "Fixture B",
      "count": 2,
      "unit": "rows",
      "note": "Native IDs null."
    },
    {
      "code": "NULL_ENDPOINT",
      "scope": "Fixture B",
      "count": 1,
      "unit": "endpoints",
      "note": "Somente relações explícitas, não inclui bindings ausentes."
    },
    {
      "code": "DECLARED_UNRESOLVED",
      "scope": "Fixture B",
      "count": 3,
      "unit": "relation occurrences",
      "note": "Sem resolução por texto."
    },
    {
      "code": "DECLARED_COLLISION",
      "scope": "Fixture B",
      "count": 1,
      "unit": "declared identity groups",
      "note": "Ambiguidade declarada, sem nova auditoria."
    },
    {
      "code": "REPEATED_TRIPLE",
      "scope": "Fixture B",
      "count": 1,
      "unit": "triple groups",
      "note": "Duas ocorrências,uma excedente."
    },
    {
      "code": "RNF_RES_UNKNOWN",
      "scope": "Fixture B",
      "count": null,
      "unit": "domain populations",
      "note": "Classes não comprovadas."
    }
  ]
}
```

## Correspondência F1 sem conteúdo privado

F1 no commit a237f446e54927eeeda8ed5e8e9daa83ee09dcb7: 159 records; cinco tabelas com 39, 85, 28, 0 e 0 linhas (152); uma RF comparada literalmente; 2911 nós, 1595 arestas e 858 parent keys explícitos resolvidos; 162 itens, dez grupos, 80 documentos, 24 avaliações e quatro pacotes. Preservar tabelas vazias e unidades distintas.

Quatro tabelas sem record_id resolúvel usam UNRESOLVED ou NULL_ENDPOINT conforme a declaração original. As 28 RF não admitidas mantêm native_id=null. O Run original isolado conserva SOURCE_ENTITY e ID comprovado, com binding_gap. Categoria ausente é MISSING. Preservar 22 endpoints nulos, 75 relações pendentes, 50 colisões e 40 grupos repetidos com 41 excedentes. Essas categorias podem se sobrepor; não são partição aditiva.

UNKNOWN_UPSTREAM e GLOBAL_UNPROVEN permanecem; brutos e hashes upstream não revalidados; RNF/RES desconhecidas. G1 é disponibilidade selecionada, sem G2–G7, paridade, conformidade ou ciência. Não copiar conteúdo, path, ID, digest, RF ou screenshot privado.

## Segurança, ciclo de vida e padrões

Obrigações completas em SECURITY-AND-INTEROPERABILITY.md e ARCHITECTURE-OPTIONS.md. Quotas propostas: três arquivos de 64 MiB, 192 MiB de entrada; descriptor UTF-8 de 32 MiB; profundidade 20; 10.000 nós, 100.000 relações, 128 tabelas, 256 colunas, 100.000 linhas agregadas, 10.000 assets; literal de célula 64 KiB e lexeme 128 KiB para escapes. O limite total prevalece. maxLength do schema conta caracteres; limites em bytes exigem checagem adicional. Memória de 256 MiB e 30 segundos por abertura devem ser impostos; sem essa capacidade, recusar a execução. Nenhum benchmark ou isolamento foi demonstrado nesta F2.

Root e allowlist exatos, handle e objeto verificados, rejeição de traversal/symlink/reparse/UNC/device/TOCTOU; sem recursão, descompactação ou rede. Arquivo privado temporário fora do acervo/repos. TTL até 60 minutos desde emissão. Browser só RAM, sem storage, service worker, upload ou telemetria. Nova importação, sessão e expiração invalidam links. Crash pode deixar resíduo; não há apagamento físico garantido. Atualização exige releitura externa autorizada; browser não afirma «fonte atual».

Texto, HTML, JS e URI são inertes. JSON tipado é exportação canônica fiel; CSV seguro faz quoting e neutralização declarados, sem substituir o original. Nenhuma porta, servidor, browser privado ou adaptador foi iniciado nesta F2.

RO-Crate 1.3, Process Run 0.6 e Caderno 0.1.0a1 preservados. O2 somente recebe rótulo conforme após todos os validadores relevantes. HL7/FHIR é capacidade futura por domínio, sem versão/IG/perfis, recursos clínicos impostos ao núcleo ou conformidade.

## Consumo e validação futuros

F3A: SVG interativo, expandir/recolher, zoom/pan/minimapa, teclado e legendas. F3B: filtro, ordenação, detalhe e exportação literal de conteúdo opcional de domínio. F4: integração segregada após decisão ARC-09 e pré-requisitos F1/F3. F5: browser Windows e fonte privada autorizada, comparação literal por SHA e recibos privados. Nenhuma fase foi iniciada.

A matriz N01–N24 em PARITY-TRACEABILITY.md integra esta proposta. Inclui identidade, colisões, null/unresolved/repetidos, quatro tabelas e 28 RF, literais, HTML/CSV/paths, fonte alterada e stale links, globais desconhecidos, FHIR não implementado e C4/SDK independentes. Oracles futuros G4/G5: NOT_RUN.

Esta autoria não é revisão independente. Aprovação ARC-09, G4/G5, implementação e paridade continuam pendentes.
