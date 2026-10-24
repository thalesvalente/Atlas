"""Disposable, source-scoped index over explicitly declared protocol packages."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from threading import RLock
from typing import Any

from caderno_protocol import PROFILE_VERSION, load_package, to_read_model

MAX_SOURCES = 16
LIMITATIONS = [
    "Perfil candidato; estabilização ainda depende de aceite humano.",
    "Validação e digest não autenticam autoria, data nem aprovação científica.",
    "Referências externas permanecem não resolvidas; anexos não são executados.",
    "Índice e dossiê são derivados; a fonte permanece a autoridade dos registros.",
    "Leitura local não certifica segurança de um host adversarial.",
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(package: Any) -> str:
    """Bind change detection to metadata, payload observations and validation."""
    value = {
        "metadata": package.metadata_sha256,
        "payloads": package.payload_status,
        "report": package.report.to_dict(),
    }
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def presentation_values(model: dict[str, Any]) -> dict[str, Any]:
    """Preserve numeric text across JavaScript's narrower integer representation.

    The typed original value stays in the projection. The browser displays this
    explicit string, and dossier download transports server bytes unchanged.
    """
    for run in model.get("runs", []):
        for value in run.get("metrics", []) + run.get("parameters", []):
            original = value.get("value")
            value["display_value"] = (None if original is None else original if isinstance(original, str)
                                      else json.dumps(original, ensure_ascii=False, allow_nan=False))
    return model


@dataclass(frozen=True)
class Source:
    id: str
    path: Path


class Catalog:
    """All state is rebuildable. No method writes to source storage."""

    def __init__(self, paths: list[str | Path]):
        if len(paths) > MAX_SOURCES:
            raise ValueError(f"At most {MAX_SOURCES} explicitly declared sources are supported.")
        self.sources = tuple(Source(f"source-{i + 1}", Path(p)) for i, p in enumerate(paths))
        self._lock = RLock()
        self._index: dict[str, dict[str, Any]] = {}
        self._fingerprints: dict[str, str] = {}
        self._generation = 0
        self._indexed_at = ""
        self.rebuild()

    def rebuild(self) -> dict[str, Any]:
        """Atomically replace only the in-memory index using declared sources."""
        with self._lock:
            index: dict[str, dict[str, Any]] = {}
            observed: dict[str, str] = {}
            for source in self.sources:
                package = load_package(source.path)
                report = package.report.to_dict()
                model = presentation_values(to_read_model(package)) if package.report.valid else None
                codes = {x.get("code") for x in report.get("errors", [])}
                status = "READY" if package.report.valid else "INVALID"
                if codes & {"SOURCE_INACCESSIBLE", "SOURCE_INVALID", "SOURCE_UNSAFE"}:
                    status = "UNAVAILABLE" if "SOURCE_INACCESSIBLE" in codes else "INVALID"
                index[source.id] = {
                    "id": source.id,
                    "name": model["source"]["name"] if model else source.path.name,
                    "status": status,
                    "version": PROFILE_VERSION if model else "UNSUPPORTED_OR_INVALID",
                    "metadata_sha256": package.metadata_sha256,
                    "report": report,
                    "read_model": model,
                    "changed": False,
                    "authenticity": "NOT_VERIFIED",
                    "scientific_approval": "NOT_EVALUATED",
                }
                observed[source.id] = fingerprint(package)
            self._index = index
            self._fingerprints = observed
            self._generation += 1
            self._indexed_at = now()
            return self.snapshot(check_changes=False)

    def snapshot(self, check_changes: bool = True) -> dict[str, Any]:
        with self._lock:
            sources = deepcopy(list(self._index.values()))
            if check_changes:
                for source, result in zip(self.sources, sources):
                    current = load_package(source.path)
                    if fingerprint(current) != self._fingerprints[source.id]:
                        result["changed"] = True
                        result["status"] = "CHANGED"
                        result["change_message"] = (
                            "A fonte mudou após a abertura. Os registros exibidos pertencem "
                            "ao snapshot anterior. Reconstrua o índice para reler a fonte."
                        )
            ids: dict[str, set[str]] = {}
            for source in sources:
                model = source.get("read_model") or {}
                for entity in model.get("entities", []):
                    eid = entity.get("@id", "")
                    if eid and eid not in {"./", "ro-crate-metadata.json"}:
                        ids.setdefault(eid, set()).add(source["id"])
            collisions = [{"id": eid, "sources": sorted(owners)} for eid, owners in ids.items()
                          if len(owners) > 1]
            return {
                "viewer_version": "0.1.0a1",
                "candidate": True,
                "generation": self._generation,
                "indexed_at": self._indexed_at,
                "observed_at": now(),
                "sources": sources,
                "collisions": collisions,
                "identity_policy": "SOURCE_ID_AND_DECLARED_ID",
                "limits": {"sources": MAX_SOURCES},
                "limitations": LIMITATIONS,
                "authority": "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL",
            }

    def dossier(self) -> dict[str, Any]:
        catalog = self.snapshot()
        return {
            "kind": "ATLAS_DERIVED_DOSSIER",
            "generated_at": now(),
            "authority": catalog["authority"],
            "limitations": LIMITATIONS,
            "indexed_at": catalog["indexed_at"],
            "sources": catalog["sources"],
            "collisions": catalog["collisions"],
            "notice": "Relatório derivado de consulta. Não constitui aceite científico ou autenticação.",
        }
