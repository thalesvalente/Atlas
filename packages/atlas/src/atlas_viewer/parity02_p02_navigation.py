"""Presentation-only scope binding; it neither changes nor extends the protocol."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def snapshot_binding(session_nonce: str, ordered_snapshots: list[tuple[str, str]]) -> str:
    """Bind positional source IDs to this session and their loaded observations.

    No filesystem locator participates in the token. A fresh Catalog gets a new
    nonce, so links cannot quietly point at another package after a restart or a
    new source ordering, including when two configured copies are byte-identical.
    Rebuilding unchanged snapshots in the same session yields the same token.
    This token is a navigation guard, not authentication or a scientific identity.
    """
    material = ["ATLAS_C0_SESSION_SNAPSHOT_V1", session_nonce, ordered_snapshots]
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def coverage(model: dict[str, Any] | None) -> dict[str, Any]:
    """Report observed loading without guessing source or conversion coverage.

    The current public contract has no whole-source/eligible/selected/converted
    counters or authoritative declaration that a package is a full source. It is
    therefore incorrect to reuse the loaded run count for any of those concepts,
    or to infer a selected subset from names, paths, descriptions or mentions.
    """
    return {
        "scope": "NOT_DECLARED",
        "basis": "PUBLIC_PACKAGE_ONLY",
        "loaded": len(model.get("runs", [])) if model else 0,
        "source": None,
        "eligible": None,
        "selected": None,
        "converted": None,
    }
