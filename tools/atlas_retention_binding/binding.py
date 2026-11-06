"""Build a read-only report over authenticated identities and verified files."""

from collections import defaultdict

from .contracts import require
from .filesystem import confirm, inspect


def verify_files(roots, files, refs):
    require(all(files[ref].root in roots for ref in refs), "ROOT_NOT_AUTHORIZED")
    observations = {}
    seen = set()
    for ref in sorted(refs):
        file = files[ref]
        observed, _ = inspect(roots[file.root], file.path, expected_sha=file.sha256, size=file.size)
        require(observed.identity not in seen, "FILE_ALIAS_COLLISION")
        seen.add(observed.identity)
        observations[ref] = observed
    for ref, observed in observations.items():
        file = files[ref]
        confirm(roots[file.root], file.path, observed)
    return {ref: observed.identity[0] for ref, observed in observations.items()}


def build_report(inventory, items, selected, roots):
    dependents = defaultdict(set)
    for uid, binding in inventory.bindings.items():
        for ref in binding.files:
            dependents[ref].add(uid)
    primary = set().union(*(binding.files for binding in selected.values()))
    copies = {ref: inventory.backups[ref] for ref in primary if ref in inventory.backups}
    volumes = verify_files(roots, inventory.files, primary | {backup.copy for backup in copies.values()})
    independent = {ref for ref, backup in copies.items()
                   if backup.independence_evidence and volumes[ref] != volumes[backup.copy]}
    restore_supported = {ref for ref, backup in copies.items() if backup.restore_evidence}
    unverified_independence = copies.keys() - independent
    unverified_restore = copies.keys() - restore_supported
    shared = {ref for ref in primary if len(dependents[ref]) > 1}

    index = {uid: number for number, uid in enumerate(items)}
    proposed = {uid for uid, item in items.items() if item.intent == "REVIEW_FOR_REMOVAL"}
    kept = {uid for uid, item in items.items() if item.baseline or item.intent != "REVIEW_FOR_REMOVAL"}
    conflicts = {ref for ref in shared if dependents[ref] & proposed and dependents[ref] & kept}

    protected = set()
    certainly_protected = set()
    item_reports = []
    for uid, item in items.items():
        binding = selected[uid]
        refs = binding.files
        blockers = []
        if item.intent != "REVIEW_FOR_REMOVAL":
            blockers.append(item.intent)
        if item.baseline:
            blockers.append("BASELINE_PROTECTED")
        if item.baseline or item.intent == "KEEP_FULL":
            certainly_protected.update(refs)
        if not binding.complete:
            blockers.append("BINDING_COVERAGE_UNKNOWN")
        if binding.evidence_scope == "DOCUMENTARY_WITNESS":
            blockers.append("DOCUMENTARY_WITNESS_ONLY")
        if not inventory.complete:
            blockers.append("DEPENDENCY_SCOPE_UNKNOWN")
        if refs & shared:
            blockers.append("SHARED_DEPENDENCY")
        if refs & conflicts:
            blockers.append("RETENTION_CONFLICT")
        if refs - copies.keys():
            blockers.append("BACKUP_UNVERIFIED")
        if refs & unverified_independence:
            blockers.append("BACKUP_INDEPENDENCE_UNPROVEN")
        if refs & unverified_restore:
            blockers.append("BACKUP_RESTORE_UNPROVEN")
        if blockers:
            protected.update(refs)
        item_reports.append({
            "index": index[uid], "intent": item.intent, "file_count": len(refs),
            "evidence_scope": binding.evidence_scope,
            "eligibility": "BLOCKED" if blockers else "REVIEW_ONLY",
            "blockers": blockers, "removal_authorized": False,
        })

    complete = all(binding.complete for binding in selected.values())
    zero = complete and primary == certainly_protected
    return {
        "status": "BOUND_READ_ONLY", "plan_status": "PROPOSAL_ONLY",
        "inventories": inventory.segments,
        "dependency_scope": "COMPLETE" if inventory.complete else "UNKNOWN",
        "items": item_reports,
        "files": [{
            "id": ref, "dependents": len(dependents[ref]),
            "selected_indices": sorted(index[uid] for uid in dependents[ref] if uid in index),
            "shared": ref in shared, "retention_conflict": ref in conflicts,
            "backup_copy_verified": ref in copies, "backup_independence_supported": ref in independent,
            "backup_restore_attested": ref in restore_supported,
            "protected": ref in protected,
        } for ref in sorted(primary)],
        "space": {
            "logical_bytes": sum(inventory.files[ref].size for ref in primary),
            "logical_complete": complete,
            "protected_bytes": sum(inventory.files[ref].size for ref in protected),
            "recoverable_bytes": 0 if zero else None,
            "recoverable_status": "ZERO_PROTECTED" if zero else "RECOVERABLE_SPACE_UNKNOWN",
        },
    }
