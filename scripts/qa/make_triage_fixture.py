"""Public, invented data for navigation and retention QA; no private corpus.

The original identities deliberately distinguish M1, M11 and the M1.1 table.
Only explicit baseline flags designate a baseline. Documentary publication is
independent from execution. This is an engineering fixture, not scientific data.
"""
from __future__ import annotations

from copy import deepcopy


def fixture(revision: str = "INVENTED_TRIAGE_REVISION_A", bulk: int = 1200) -> dict:
    records = [
        {"id": "M1", "title": "M1 · marco sintético", "kind": "milestone", "family": "A · Triagem"},
        {"id": "M11", "title": "M11 · outro marco sintético", "kind": "milestone", "family": "A · Triagem"},
        {"id": "run-rf-proof", "title": "Execução RF comprovada na fixture", "kind": "run",
         "family": "A · Triagem", "execution_state": "SUCCEEDED", "result_group": "failed",
         "publication": "published", "admission": "HOLD", "review": "PENDING", "baseline": True,
         "started_at": "2026-10-01T12:30:00Z", "configuration": {"seed": 71, "mode": "INVENTED"},
         "code_revision": "0123456789abcdef0123456789abcdef01234567",
         "metrics": {"integer": 9007199254740993, "decimal_text": "0.123456789012345678901", "zero": -0.0},
         "results": {"verdict": "SYNTHETIC_ONLY"}, "limitations": ["Invented for software QA"],
         "dependencies": ["resource-shared"], "resources": ["resource-proof"],
         "evidence": [{"source_id": "resource-proof", "kind": "SYNTHETIC_REFERENCE"}]},
        {"id": "run-failed-published", "title": "Falha documentalmente publicada", "kind": "run",
         "family": "A · Triagem", "execution_state": "FAILED", "result_group": "published",
         "publication": "published", "admission": "HOLD", "review": "PENDING"},
        {"id": "run-blocked-published", "title": "Bloqueio documentalmente publicado", "kind": "run",
         "family": "A · Triagem", "execution_state": "BLOCKED", "result_group": "published",
         "publication": "published", "admission": "NOT_ADMITTED", "review": "PENDING"},
        {"id": "name-only-baseline", "title": "baseline published SUCCEEDED sem designação",
         "kind": "experiment", "family": "A · Triagem", "execution_state": "SUCCEEDED",
         "publication": "published"},
        {"id": "state-missing", "title": "Registro sem estado nem retenção", "kind": "record", "family": "A · Triagem",
         "result_group": "published", "result": "PUBLISHED", "publication": "UNKNOWN"},
        {"id": "state-null", "title": "Estado explicitamente NULL", "kind": "run",
         "family": "A · Triagem", "execution_state": None, "status": "SUCCEEDED"},
        {"id": "state-empty", "title": "Estado explicitamente vazio", "kind": "run",
         "family": "A · Triagem", "execution_state": "", "result_group": "failed"},
        {"id": "state-unknown", "title": "Estado UNKNOWN declarado", "kind": "run",
         "family": "A · Triagem", "execution_state": "UNKNOWN"},
        {"id": "hostile-record", "title": '<img src="https://example.invalid/never-request" onerror="globalThis.__triageInjected=true">',
         "kind": "run", "family": "A · Triagem", "execution_state": "__proto__",
         "summary": '<script>globalThis.__triageInjected=true</script>',
         "evidence": "javascript:globalThis.__triageInjected=true", "__proto__": {"polluted": True}},
        {"id": "baseline-reference-only", "title": "Referência para baseline, sem designação própria",
         "kind": "attempt", "family": "A · Triagem", "baseline_ref": "run-rf-proof",
         "execution_state": "FAILED"},
        {"id": "source-document", "title": "Fonte inventada e única", "kind": "artifact",
         "family": "A · Triagem", "unique": True, "retention": None},
    ]
    for index in range(bulk):
        records.append({"id": f"volume-{index:04d}", "title": f"Execução de volume {index:04d}",
                        "kind": "run", "family": "B · Volume sintético",
                        "execution_state": ["SUCCEEDED", "FAILED", "BLOCKED"][index % 3],
                        "result_group": "technical", "publication": "not_published",
                        "started_at": "2026-11-01T10:00:00Z"})
    table = {"id": "M1.1", "label": "M1.1 · RF baseline preservada", "family": "RF sintético",
             "baseline": True, "record_id": "run-rf-proof", "rows": [
                 {"id": f"synthetic-rf-{index:02d}", "nucleus_id": f"INVENTED-CORE-{index % 3}", "cells": {
                     "ID": f"RF-{index:02d}", "Núcleo": "INVENTED", "Nome": f"Requisito inventado {index:02d}",
                     "Descrição": "Linha de requisitos, não uma execução experimental.",
                     "Critério de aceite": "Somente validação de engenharia", "Inteiro exato": 9007199254740993 + index}}
                 for index in range(39)]}
    return {"schema": "synthetic-atlas-triage-qa/1", "atlas_integration": {"notebook_revision": revision},
            "records": records, "lineage_graph": {"nodes": [], "edges": []}, "result_tables": [table],
            "edges": [{"id": "declared-comparison", "from_key": "run-rf-proof", "to_key": "run-failed-published",
                       "type": "COMPARED_WITH"}],
            "resources": [
                {"id": "resource-proof", "title": "Dossiê sintético declarado", "kind": "document",
                 "uri": "https://example.invalid/never-opened", "availability": "UNKNOWN"},
                {"id": "resource-shared", "title": "Dependência compartilhada inventada", "kind": "resource",
                 "shared": True, "availability": "UNKNOWN"}],
            "product_items": [],
            "coverage": {"scope": "INVENTED_DATA_ONLY", "source_rows": {"operational_index": 7}}}


def revised_fixture(data: dict) -> dict:
    """Same original identities, a different revision; no in-place edits."""
    revised = deepcopy(data)
    revised["atlas_integration"]["notebook_revision"] = "INVENTED_TRIAGE_REVISION_B"
    revised["records"][2]["metrics"]["integer"] = 9007199254740995
    return revised
