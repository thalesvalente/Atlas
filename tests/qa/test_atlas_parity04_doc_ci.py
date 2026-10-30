"""Adversarial probes for the exact AP04 documentation-successor contract."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tokenize
import unittest

ROOT = Path(__file__).resolve().parents[2]
APPROVED_GUARD_SEMANTICS = "90f98512b57ac5ca987ea7c06d3a4be4637405938095d6bc9cb3fc2c2240543d"
APPROVED_ORIGINAL_CONTROLS = {
    ".github/workflows/atlas-parity02.yml": "2f17a0711e43f27a465d4b99ae6b887cbc2dcd0cc2dd875a535961bd0dcb0937",
    ".github/workflows/atlas-parity03-p03-gates.yml": "491fa56982ce7d427311a7a3e8fe4992c42381766ef3a3e8872d9c2d5adb1bd7",
    ".github/workflows/atlas-parity04-doc.yml": "82ccfaa17d42b4433ddbb110a90102ac854f32c44eaf76fc68a33df1f955be25",
    ".github/workflows/atlas003-speckit.yml": "c330d85e29925e7df35c834cb1cd1c4f19d995852b3bcf17d5d5c8fd5dd30fd5",
    ".github/workflows/atlas021.yml": "db4589fe1570d0d0aa8d9a8bf39be7362df27b44a66172e2ae958e157098381d",
    "scripts/qa/atlas_parity03_c4_ci.py": "8edd381487b138fa1ad127ee9e4fb1460f515b6268850ab7e1d80563de2263b8",
}


def guard_semantics(raw: bytes) -> str:
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    if encoding != "utf-8":
        raise RuntimeError("Guard source must use the validated UTF-8 codec")
    tree = ast.parse(raw.decode("utf-8"))
    tables = [node for node in tree.body if isinstance(node, ast.Assign)
              and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
              and node.targets[0].id == "APPROVED_CONTROL_HASHES"]
    if len(tables) != 1:
        raise RuntimeError("Expected one explicit approved-control hash table")
    try:
        pairs = ast.literal_eval(tables[0].value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise RuntimeError("Approved-control table must contain only literal data") from error
    if not isinstance(pairs, tuple) or any(
        not isinstance(pair, tuple) or len(pair) != 2
        or not all(isinstance(value, str) for value in pair) for pair in pairs
    ):
        raise RuntimeError("Approved-control table must be a literal tuple of string pairs")
    values = dict(pairs)
    test_path = "tests/qa/test_atlas_parity04_doc_ci.py"
    expected = {**APPROVED_ORIGINAL_CONTROLS,
                test_path: hashlib.sha256((ROOT / test_path).read_bytes()).hexdigest()}
    if len(values) != len(pairs) or values != expected:
        raise RuntimeError("Literal approved-control inventory or hashes changed")
    tree.body.remove(tables[0])
    return hashlib.sha256(ast.dump(tree, include_attributes=False).encode("utf-8")).hexdigest()


# Inspect inert source and literal data before executing any guard module code.
GUARD_SOURCE = (ROOT / "scripts/qa/atlas_parity04_doc_ci.py").read_bytes()
if guard_semantics(GUARD_SOURCE) != APPROVED_GUARD_SEMANTICS:
    raise RuntimeError("Guard executable semantics changed before import")
SPEC = importlib.util.spec_from_file_location(
    "atlas_parity04_doc_ci", ROOT / "scripts/qa/atlas_parity04_doc_ci.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Cannot load AP04 successor guard")
GUARD = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = GUARD
exec(compile(GUARD_SOURCE.decode("utf-8"), str(SPEC.origin), "exec", dont_inherit=True),
     GUARD.__dict__)


class SyntheticSuccessor:
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.symlinks", "false")
        self.protected = {
            "AGENTS.md",
            ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
            "docs/architecture/ADR-0001-atlas-protocol-producers-storage.md",
            "docs/architecture/ADR-0002-protocol-candidate.md",
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            "packages/protocol/src/caderno_protocol/resources/context-catalog.json",
            "packages/atlas/src/atlas_viewer/server.py",
            "packages/atlas/src/atlas_viewer/static/index.html",
            "tests/fixtures/atlas_parity02/p03/table-positive.json",
            "tests/viewer/test_atlas_parity02_p03_harness.py",
        }
        self._create_c4()
        self._create_documents()
        self._create_repair()

    def close(self):
        self.temporary.cleanup()

    def git(self, *args: str, input_bytes: bytes | None = None) -> str:
        return subprocess.check_output(
            ["git", *args], cwd=self.root, input=input_bytes,
        ).decode("utf-8").strip()

    def write(self, path: str, raw: bytes | str):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw.encode("utf-8") if isinstance(raw, str) else raw)

    @staticmethod
    def c4_script(marker: str, *, assets: dict | None = None) -> str:
        values = {
            "INPUTS": {"C1": ("1" * 40, "2" * 40)},
            "P03": "docs/p03", "C1": "docs/c1", "C2": "docs/c2",
            "C3": "docs/c3", "C4": "docs/c4",
            "COMPOSITION": "3" * 40, "COMPOSITION_TREE": "4" * 40,
            "P03_C4_ADAPTERS": {"tests/viewer/adapter.py": "5" * 64},
            "ASSETS": assets if assets is not None else {"/": ("index.html", "text/html")},
        }
        return "\n".join(f"{name} = {value!r}" for name, value in values.items()) \
            + f"\n# {marker}\n"

    @staticmethod
    def ap04_workflow() -> str:
        return "\n".join([
            "name: synthetic AP04",
            "jobs:",
            "  guard:",
            "    steps:",
            *[f"      - uses: {value}" for value in GUARD.NEW_AP04_ACTION_PINS],
            "",
        ])

    def commit(self, message: str):
        self.git("add", "-A")
        self.git(
            "-c", "user.name=Synthetic AP04", "-c", "user.email=ap04@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", message,
        )

    def _create_c4(self):
        for path in GUARD.MODIFIED_REPAIR_PATHS | self.protected:
            self.write(path, "synthetic C4 bytes for " + path + "\n")
        self.write("scripts/qa/atlas_parity03_c4_ci.py", self.c4_script("frozen C4"))
        self.write(GUARD.C4_MANIFEST, "synthetic immutable C4 manifest\n")
        self.write("scripts/qa/atlas_parity02_p06_audit.py", """
def audit(root):
    return {"status": "FAIL", "errors": [
        {"path": "docs/architecture/ADR-0003-legacy-compatibility-proposed.md",
         "reason": "UNEXPECTED_PROTECTED_FILE"}
    ]}
""")
        self.commit("C4 sintética")
        self.c4_sha = self.git("rev-parse", "HEAD")
        self.c4_tree = self.git("rev-parse", "HEAD^{tree}")

    def _create_documents(self):
        for path in GUARD.DOC_PATHS:
            if path == GUARD.GATES_PATH:
                payload = {
                    "plan_id": "AP04-POR-v1.0-draft",
                    "adr0003": "PROPOSED_NOT_APPROVED",
                    "scope": "DOCUMENTATION_ONLY",
                    "non_authorizations": ["merge_main", "release", "deploy", "promotion"],
                }
                self.write(path, json.dumps(payload, sort_keys=True) + "\n")
            elif path == GUARD.ADR_PATH:
                self.write(path, "# ADR-0003\n\nStatus: PROPOSED_NOT_APPROVED\n")
            else:
                self.write(path, "synthetic original AP04 document: " + path + "\n")
        self.commit("Documentação AP04 sintética")
        self.doc_sha = self.git("rev-parse", "HEAD")
        self.doc_tree = self.git("rev-parse", "HEAD^{tree}")

    def _overlay_payload(self):
        return {
            "schema": "atlas-parity04-doc-ci-overlay-v1",
            "plan_id": "AP04-POR-v1.0-draft",
            "base_sha": self.c4_sha,
            "baseline_doc_sha": self.doc_sha,
            "adr0003": "PROPOSED_NOT_APPROVED",
            "historical_manifests": "IMMUTABLE",
            "authorized_paths": [
                {"path": path, "purpose": "synthetic authorized repair"}
                for path in sorted(GUARD.REPAIR_PATHS)
            ],
        }

    def _rewrite_manifest(self):
        lines = []
        for path in sorted(GUARD.REPAIR_PATHS - {GUARD.OVERLAY_MANIFEST}):
            raw = (self.root / path).read_bytes()
            lines.append(hashlib.sha256(raw).hexdigest() + "  " + path)
        self.write(GUARD.OVERLAY_MANIFEST, "\n".join(lines) + "\n")

    def _create_repair(self):
        for path in GUARD.MODIFIED_REPAIR_PATHS:
            if path == "scripts/qa/atlas_parity03_c4_ci.py":
                self.write(path, self.c4_script("authorized AP04 repair"))
            else:
                self.write(path, "synthetic authorized repair for " + path + "\n")
        for path in GUARD.NEW_REPAIR_PATHS - {GUARD.OVERLAY_CONTRACT, GUARD.OVERLAY_MANIFEST}:
            if path == ".github/workflows/atlas-parity04-doc.yml":
                self.write(path, self.ap04_workflow())
            else:
                self.write(path, "synthetic new repair file: " + path + "\n")
        self.write(GUARD.OVERLAY_CONTRACT, json.dumps(self._overlay_payload(), indent=2) + "\n")
        self.approved_control_hashes = tuple(
            (path, hashlib.sha256((self.root / path).read_bytes()).hexdigest())
            for path in sorted(GUARD.CONTROL_PATHS)
        )
        self._rewrite_manifest()
        self.commit("Reparo AP04 sintético")
        self.repair_sha = self.git("rev-parse", "HEAD")

    @property
    def contract(self):
        return GUARD.SuccessorContract(
            c4_sha=self.c4_sha,
            c4_tree=self.c4_tree,
            doc_sha=self.doc_sha,
            doc_tree=self.doc_tree,
            doc_paths=GUARD.DOC_PATHS,
            repair_paths=GUARD.REPAIR_PATHS,
            modified_repair_paths=GUARD.MODIFIED_REPAIR_PATHS,
            adr_path=GUARD.ADR_PATH,
            gates_path=GUARD.GATES_PATH,
            c4_manifest=GUARD.C4_MANIFEST,
            overlay_contract=GUARD.OVERLAY_CONTRACT,
            overlay_manifest=GUARD.OVERLAY_MANIFEST,
            approved_control_hashes=self.approved_control_hashes,
        )

    @staticmethod
    def boundary(_root, _contract):
        return {"status": "PASS_EXACT_SUCCESSOR_EXCEPTION", "historical_protection_weakened": False}

    def report(self):
        return GUARD.audit(self.root, contract=self.contract, boundary_audit=self.boundary)

    def mutate_and_commit(self, path: str, raw: str = "unauthorized mutation\n"):
        self.write(path, raw)
        self.commit("Mutação adversarial")

    def remove_and_commit(self, path: str):
        target = self.root / path
        if target.is_dir() and not target.is_symlink():
            shutil.rmtree(target)
        else:
            target.unlink()
        self.commit("Remoção adversarial")

    def symlink_mode_and_commit(self, path: str):
        blob = self.git("hash-object", "-w", "--stdin", input_bytes=b"target\n")
        self.git("update-index", "--add", "--cacheinfo", "120000," + blob + "," + path)
        self.git(
            "-c", "user.name=Synthetic AP04", "-c", "user.email=ap04@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Symlink adversarial",
        )
        self.git("reset", "--hard", "HEAD")

    def executable_mode_and_commit(self, path: str):
        self.git("update-index", "--chmod=+x", "--", path)
        self.git(
            "-c", "user.name=Synthetic AP04", "-c", "user.email=ap04@example.invalid",
            "-c", "commit.gpgsign=false", "commit", "-qm", "Mode adversarial",
        )
        self.git("reset", "--hard", "HEAD")


class AP04SuccessorGuardTests(unittest.TestCase):
    def setUp(self):
        self.repo = SyntheticSuccessor()
        self.addCleanup(self.repo.close)

    def assertRed(self, report):
        self.assertEqual(report["status"], "FAIL", report)
        self.assertIn("error", report)

    def test_exact_documentation_and_manifested_controls_pass_on_arbitrary_branch_name(self):
        self.repo.git("branch", "-m", "arbitrary/successor-name-without-magic")
        report = self.repo.report()
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["original_document_count"], 9)
        self.assertEqual(set(report["complete_delta"]["paths"]),
                         set(GUARD.DOC_PATHS | GUARD.REPAIR_PATHS))
        self.assertFalse(report["frozen_boundary"]["historical_protection_weakened"])

    def test_edit_remove_and_symlink_of_adr0003_are_red(self):
        scenarios = ("edit", "remove", "symlink")
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                repo = SyntheticSuccessor()
                try:
                    if scenario == "edit":
                        repo.mutate_and_commit(GUARD.ADR_PATH)
                    elif scenario == "remove":
                        repo.remove_and_commit(GUARD.ADR_PATH)
                    else:
                        repo.symlink_mode_and_commit(GUARD.ADR_PATH)
                    self.assertRed(repo.report())
                finally:
                    repo.close()

    def test_adr0004_and_changes_to_adr0001_or_adr0002_are_red(self):
        paths = (
            "docs/architecture/ADR-0004-unapproved.md",
            "docs/architecture/ADR-0001-atlas-protocol-producers-storage.md",
            "docs/architecture/ADR-0002-protocol-candidate.md",
        )
        for path in paths:
            with self.subTest(path=path):
                repo = SyntheticSuccessor()
                try:
                    repo.mutate_and_commit(path)
                    self.assertRed(repo.report())
                finally:
                    repo.close()

    def test_protocol_context_governance_skill_fixture_and_agents_changes_are_red(self):
        paths = (
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            "packages/protocol/src/caderno_protocol/resources/new-schema.json",
            "packages/protocol/src/caderno_protocol/resources/context-catalog.json",
            ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
            "tests/fixtures/atlas_parity02/p03/table-positive.json",
            "AGENTS.md",
        )
        for path in paths:
            with self.subTest(path=path):
                repo = SyntheticSuccessor()
                try:
                    repo.mutate_and_commit(path)
                    self.assertRed(repo.report())
                finally:
                    repo.close()

    def test_runtime_p03_adapter_and_asset_allowlist_changes_are_red(self):
        paths = (
            "packages/atlas/src/atlas_viewer/server.py",
            "packages/atlas/src/atlas_viewer/static/index.html",
            "tests/viewer/test_atlas_parity02_p03_harness.py",
        )
        for path in paths:
            with self.subTest(path=path):
                repo = SyntheticSuccessor()
                try:
                    repo.mutate_and_commit(path)
                    self.assertRed(repo.report())
                finally:
                    repo.close()

    def test_arbitrary_document_outside_original_and_repair_paths_is_red(self):
        self.repo.mutate_and_commit("docs/missions/atlas-parity-04/UNLISTED.md")
        self.assertRed(self.repo.report())

    def test_branch_name_lookalike_cannot_override_bad_bytes(self):
        self.repo.git("branch", "-m", "lookalike/atlas-parity03-c4-full-candidate-20261027-copy")
        self.repo.mutate_and_commit("packages/atlas/src/atlas_viewer/server.py")
        self.assertRed(self.repo.report())

    def test_mode_change_in_authorized_repair_path_is_red(self):
        self.repo.executable_mode_and_commit(".github/workflows/atlas021.yml")
        self.assertRed(self.repo.report())

    def test_asset_allowlist_change_is_red_even_when_overlay_hash_is_updated(self):
        path = "scripts/qa/atlas_parity03_c4_ci.py"
        self.repo.write(path, self.repo.c4_script(
            "malicious asset change", assets={"/wildcard": ("private.html", "text/html")}))
        self.repo._rewrite_manifest()
        self.repo.commit("Asset allowlist adversarial")
        self.assertRed(self.repo.report())

    def test_c4_control_flow_cannot_be_relaxed_by_rehashing_the_manifest(self):
        path = "scripts/qa/atlas_parity03_c4_ci.py"
        original = (self.repo.root / path).read_bytes()
        for name in ("inputs", "installed", "main", "require"):
            with self.subTest(function=name):
                self.repo.write(path, original + (
                    f"\ndef {name}(*args, **kwargs):\n    return {{'status': 'PASS'}}\n"
                ).encode("utf-8"))
                self.repo._rewrite_manifest()
                self.repo.commit("Corpo de controle C4 adulterado com manifesto atualizado")
                report = self.repo.report()
                self.assertRed(report)
                self.assertIn("Approved CI control bytes changed", report["error"])

    def test_workflow_conditions_and_commands_cannot_be_reauthorized_by_manifest(self):
        path = ".github/workflows/atlas-parity04-doc.yml"
        original = (self.repo.root / path).read_text(encoding="utf-8")
        for condition in ("${{ false }}", "${{ 1 == 0 }}", "cancelled()"):
            with self.subTest(condition=condition):
                self.repo.write(path, original + (
                    "      - name: Skipped mandatory real-history guard\n"
                    f"        if: {condition}\n"
                    "        run: python scripts/qa/atlas_parity04_doc_ci.py audit\n"
                ))
                self.repo._rewrite_manifest()
                self.repo.commit("Step de auditoria ignorado com manifesto atualizado")
                report = self.repo.report()
                self.assertRed(report)
                self.assertIn("Approved CI control bytes changed", report["error"])

    def test_manifest_hash_divergence_missing_entry_deletion_and_reordering_are_red(self):
        for scenario in ("hash", "entry", "delete", "order"):
            with self.subTest(scenario=scenario):
                repo = SyntheticSuccessor()
                try:
                    manifest = repo.root / GUARD.OVERLAY_MANIFEST
                    if scenario == "hash":
                        text = manifest.read_text(encoding="utf-8")
                        manifest.write_text("0" * 64 + text[64:], encoding="utf-8")
                        repo.commit("Hash divergente")
                    elif scenario == "entry":
                        lines = manifest.read_text(encoding="utf-8").splitlines()
                        manifest.write_text("\n".join(lines[1:]) + "\n", encoding="utf-8")
                        repo.commit("Entrada removida")
                    elif scenario == "delete":
                        repo.remove_and_commit(GUARD.OVERLAY_MANIFEST)
                    else:
                        lines = manifest.read_text(encoding="utf-8").splitlines()
                        manifest.write_text("\n".join(reversed(lines)) + "\n", encoding="utf-8")
                        repo.commit("Manifesto reordenado")
                    self.assertRed(repo.report())
                finally:
                    repo.close()

    def test_original_document_bytes_cannot_be_replaced_even_with_correct_ancestry(self):
        self.repo.mutate_and_commit(GUARD.GATES_PATH, json.dumps({
            "plan_id": "AP04-POR-v1.0-draft",
            "adr0003": "APPROVED",
            "scope": "DOCUMENTATION_ONLY",
            "non_authorizations": ["merge_main", "release", "deploy", "promotion"],
        }) + "\n")
        self.assertRed(self.repo.report())

    def test_historical_c4_manifest_cannot_be_changed(self):
        self.repo.mutate_and_commit(GUARD.C4_MANIFEST)
        self.assertRed(self.repo.report())

    def test_repair_history_rejects_transient_unauthorized_change_even_if_reverted(self):
        path = "packages/protocol/src/caderno_protocol/resources/schema.json"
        original = (self.repo.root / path).read_bytes()
        self.repo.mutate_and_commit(path)
        self.repo.write(path, original)
        self.repo.commit("Reversão não apaga histórico")
        self.assertRed(self.repo.report())

    def test_default_boundary_accepts_only_the_single_strict_p06_rejection(self):
        result = GUARD.default_boundary_audit(self.repo.root, self.repo.contract)
        self.assertEqual(result["status"], "PASS_EXACT_SUCCESSOR_EXCEPTION")
        self.assertFalse(result["historical_protection_weakened"])
        script = self.repo.root / "scripts/qa/atlas_parity02_p06_audit.py"
        script.write_text("def audit(root):\n    return {'status': 'PASS_SCOPED', 'errors': []}\n",
                          encoding="utf-8")
        with self.assertRaises(GUARD.GuardError):
            GUARD.default_boundary_audit(self.repo.root, self.repo.contract)

    def test_wrong_base_or_document_tree_is_red(self):
        wrong = GUARD.SuccessorContract(
            **{**self.repo.contract.__dict__, "doc_tree": "0" * 40}
        )
        self.assertRed(GUARD.audit(
            self.repo.root, contract=wrong, boundary_audit=self.repo.boundary))


class AP04WorkflowRoutingTests(unittest.TestCase):
    def test_non_utf8_cookie_cannot_hide_executable_code_from_preflight(self):
        hidden = (b"# coding: raw_unicode_escape\n" + GUARD_SOURCE
                  + b"\n#\\u000aunapproved_effect()\n")
        with self.assertRaisesRegex(RuntimeError, "UTF-8 codec"):
            guard_semantics(hidden)

    def test_nonliteral_control_table_is_rejected_before_guard_import(self):
        tree = ast.parse(GUARD_SOURCE.decode("utf-8"))
        table = next(node for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(target, ast.Name)
                             and target.id == "APPROVED_CONTROL_HASHES"
                             for target in node.targets))
        table.value = ast.Subscript(
            value=ast.Tuple(elts=[ast.Call(func=ast.Name(id="unapproved_effect", ctx=ast.Load()),
                                          args=[], keywords=[]), table.value], ctx=ast.Load()),
            slice=ast.Constant(value=1), ctx=ast.Load())
        changed = ast.unparse(ast.fix_missing_locations(tree)).encode("utf-8")
        with self.assertRaisesRegex(RuntimeError, "literal data"):
            guard_semantics(changed)

    def test_guard_control_flow_has_independent_semantic_authorization(self):
        raw = (ROOT / "scripts/qa/atlas_parity04_doc_ci.py").read_bytes()
        self.assertEqual(guard_semantics(raw), APPROVED_GUARD_SEMANTICS)
        changed = raw.replace(
            b"    if not condition:\n        raise GuardError(message)",
            b"    return None",
        )
        self.assertNotEqual(changed, raw)
        self.assertNotEqual(guard_semantics(changed), APPROVED_GUARD_SEMANTICS)

    def test_approved_controls_are_fixed_and_the_independent_tests_are_bound(self):
        actual = dict(GUARD.APPROVED_CONTROL_HASHES)
        test_path = "tests/qa/test_atlas_parity04_doc_ci.py"
        self.assertEqual(set(actual), GUARD.CONTROL_PATHS)
        self.assertEqual({path: value for path, value in actual.items() if path != test_path},
                         APPROVED_ORIGINAL_CONTROLS)
        self.assertEqual(actual[test_path], hashlib.sha256((ROOT / test_path).read_bytes()).hexdigest())

    def test_dispatch_is_not_based_on_branch_name_and_forbidden_bypasses_are_absent(self):
        paths = (
            ".github/workflows/atlas-parity02.yml",
            ".github/workflows/atlas-parity03-p03-gates.yml",
            ".github/workflows/atlas003-speckit.yml",
            ".github/workflows/atlas021.yml",
            ".github/workflows/atlas-parity04-doc.yml",
        )
        combined = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in paths)
        for forbidden in (
            "github.head_ref", "github.ref_name", "continue-on-error", "if: false",
            "|| true", "paths-ignore", "pytest.skip", "@unittest.skip",
        ):
            self.assertNotIn(forbidden, combined)
        self.assertIn("atlas_parity04_doc_ci.py p03-inputs", combined)
        self.assertIn("atlas_parity04_doc_ci.py boundary", combined)
        self.assertIn("atlas_parity04_doc_ci.py installed", combined)
        self.assertIn("atlas_parity04_doc_ci.py speckit", combined)

    def test_dedicated_guard_runs_linux_windows_normal_and_optimized(self):
        text = (ROOT / ".github/workflows/atlas-parity04-doc.yml").read_text(encoding="utf-8")
        self.assertIn("os: [ubuntu-latest, windows-latest]", text)
        self.assertIn("optimize: ['0', '1']", text)
        self.assertIn("python -m unittest", text)
        self.assertIn("atlas_parity04_doc_ci.py audit", text)


if __name__ == "__main__":
    unittest.main()
