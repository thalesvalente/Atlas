"""Production gate composed with the pinned B supervisor, before any source IO.

B supplies synthetic native probes, not a production acquisition capability.
A returning/missing/broken guard never enables acquisition in this revision.
"""
from __future__ import annotations
from .errors import ReaderError
from . import os_supervisor


def require_production_profile() -> None:
    """Fail closed without evaluating paths or accepting a synthetic override."""
    try:
        os_supervisor.require_production_acquisition()
    except os_supervisor.OSProfileNotEnforced:
        # Retain the historical public error contract. Native limits tested on
        # a synthetic worker do not establish a limit for the real parser.
        raise ReaderError("HARD_BUDGET_UNVERIFIED") from None
    except Exception:
        raise ReaderError("OS_ISOLATION_UNVERIFIED") from None
    # A future B implementation must define a reviewed capability/worker
    # contract. A truthy value or a removed guard is NOT that contract.
    raise ReaderError("OS_ISOLATION_UNVERIFIED")
