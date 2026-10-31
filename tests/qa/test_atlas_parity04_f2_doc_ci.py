"""Independent preflight and adversarial Git epochs for AP04 F2."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import tokenize
import types
import unittest

ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = "scripts/qa/atlas_parity04_f2_doc_ci.py"
TEST_PATH = "tests/qa/test_atlas_parity04_f2_doc_ci.py"
APPROVED_GUARD_SOURCE = "b02d4c03e38722ebf7f3e61fa056afb90cb1e2d672a3e01d63c04746623078a9"
APPROVED_EXTERNAL_CONTROLS = {
    ".github/workflows/atlas-parity02.yml": "d165bdd580d748418fdf24cbc513f1442ac2744874f30a2219169c60c11262a7",
    ".github/workflows/atlas-parity03-p03-gates.yml": "d6f4e39d86e3ee8d3fbc81cec09f4b42b476fa4c5b3c0ca7a694c7ca9bcde652",
    ".github/workflows/atlas-parity04-doc.yml": "abc9d3a672bd9382e9a45b08a2436105e21e53d82583bc564eb99f9f45281115",
    ".github/workflows/atlas003-speckit.yml": "cea45f4f2bb97999e69335ea295bfddded25fcae7bacb37ea0ef711c420ba388",
    ".github/workflows/atlas021.yml": "3214f4bcb2a8515a3318b007e41ac171617e74b95f30d8d9bb542a26358087ea",
    ".github/workflows/atlas-parity03-c4.yml": "0b87ec141ef2cf2606b35b5d9ea7aaf956c7d611a34ee068e9fbf686061ef675",
    "scripts/qa/atlas_parity03_c4_ci.py": "940e0960e055235abbfc95e85ae8e4a817c5ad934206205299d228aea035639f",
}


def source_without_control_table(raw):
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    if encoding != "utf-8":
        raise RuntimeError("Guard must use validated UTF-8 codec")
    text = raw.decode("utf-8")
    tree = ast.parse(text)
    tables = [node for node in tree.body if isinstance(node, ast.Assign)
              and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
              and node.targets[0].id == "APPROVED_CONTROL_HASHES"]
    if len(tables) != 1:
        raise RuntimeError("Expected one explicit approved-control table")
    table = tables[0]
    try:
        pairs = ast.literal_eval(table.value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise RuntimeError("Control table must be inert literal data") from error
    if (not isinstance(pairs, tuple) or any(not isinstance(pair, tuple) or len(pair) != 2
            or not all(isinstance(value, str) for value in pair) for pair in pairs)):
        raise RuntimeError("Control table must be literal tuple of string pairs")
    expected = {**APPROVED_EXTERNAL_CONTROLS,
                TEST_PATH: hashlib.sha256((ROOT / TEST_PATH).read_bytes()).hexdigest()}
    if len(dict(pairs)) != len(pairs) or dict(pairs) != expected:
        raise RuntimeError("Independent approved-control inventory differs")
    lines = text.splitlines(keepends=True)
    first, last = table.lineno - 1, table.end_lineno
    if (lines[first].rstrip("\r\n") != "APPROVED_CONTROL_HASHES = ("
            or lines[last - 1].rstrip("\r\n") != ")"
            or first < 1 or last >= len(lines)
            or lines[first - 1].rstrip("\r\n") != "# BEGIN_APPROVED_CONTROL_HASHES"
            or lines[last].rstrip("\r\n") != "# END_APPROVED_CONTROL_HASHES"):
        raise RuntimeError("Control table spans are not isolated canonical lines")
    for node in tree.body:
        if node is table:
            continue
        if getattr(node, "lineno", 0) <= last and getattr(node, "end_lineno", 0) > first:
            raise RuntimeError("Executable statement shares excluded control-table lines")
    return "".join(lines[:first] + lines[last:]).encode("utf-8")


GUARD_SOURCE = (ROOT / GUARD_PATH).read_bytes()
if hashlib.sha256(source_without_control_table(GUARD_SOURCE)).hexdigest() != APPROVED_GUARD_SOURCE:
    raise RuntimeError("Independent guard source authorization failed before import")
GUARD = types.ModuleType("atlas_parity04_f2_doc_ci")
GUARD.__file__ = str(ROOT / GUARD_PATH)
sys.modules[GUARD.__name__] = GUARD
exec(compile(GUARD_SOURCE.decode("utf-8"), GUARD.__file__, "exec", dont_inherit=True), GUARD.__dict__)


class SyntheticEpochs:
    """A fresh synthetic Git object database, never a product clone/worktree."""
    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.git("init", "-q")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.symlinks", "false")
        self.protected = [
            "AGENTS.md", ".specify/memory/constitution.md",
            ".agents/skills/speckit-implement/SKILL.md",
            "docs/architecture/ADR-0001-atlas-protocol-producers-storage.md",
            "docs/architecture/ADR-0002-protocol-candidate.md",
            "docs/architecture/ADR-0003-legacy-compatibility-proposed.md",
            "docs/missions/atlas-parity-04/ACTION-PLAN.md",
            "docs/missions/atlas-parity-04/GATES.json",
            "docs/missions/atlas-parity-04/ci-repair/MANIFEST.sha256",
            "docs/missions/atlas-parity-03/c4-full-convergence/MANIFEST.sha256",
            "packages/protocol/src/caderno_protocol/resources/schema.json",
            "packages/protocol/src/caderno_protocol/resources/context-catalog.json",
            "specs/003-producer-selective-preview/contracts/reader.md",
            "tests/fixtures/atlas_parity02/p03/table-positive.json",
            "scripts/qa/atlas_parity02_p06_audit.py",
            "scripts/qa/speckit_audit.py",
            "scripts/qa/atlas_parity04_doc_ci.py",
            "tests/qa/test_atlas_parity04_doc_ci.py",
            ".github/workflows/atlas-parity03-c4.yml",
        ]
        for path in self.protected:
            self.write(path, "immutable synthetic baseline for " + path + "\n")
        for path in GUARD.MODIFIED_REPAIR_PATHS:
            self.write(path, "old synthetic control for " + path + "\n")
        self.commit("C4 sintetica")
        self.c4 = self.head
        self.epochs = []
        self.documents = []
        for name, subset in [
            ("AP04", []),
            ("F1", [item for item in GUARD.FROZEN_DOCUMENTS if item["source_sha"] == GUARD.F1_SHA]),
            ("F2", [item for item in GUARD.FROZEN_DOCUMENTS if item["source_sha"] == GUARD.F2_SHA]),
        ]:
            parent = self.head
            self.write("synthetic-epoch.txt", name + "\n")
            for item in subset:
                self.write(item["path"], "synthetic inert document " + item["path"] + "\n")
            self.commit(name)
            self.epochs.append((self.head, self.tree, parent))
            for item in subset:
                raw = (self.root / item["path"]).read_bytes()
                self.documents.append({"path": item["path"], "source_sha": self.head,
                    "blob": self.git("rev-parse", "HEAD:" + item["path"]),
                    "sha256": GUARD.sha256(raw), "mode": "100644"})
        self.documents.sort(key=lambda item: item["path"])
        self.baseline = self.head
        self.baseline_tree = self.tree
        for path in GUARD.REPAIR_PATHS:
            self.write(path, "approved synthetic F2 repair " + path + "\n")
        self.write(GUARD.OVERLAY_PATH, GUARD.canonical_json(GUARD.expected_overlay(
            self.documents, GUARD.REPAIR_PURPOSES, self.baseline, self.epochs[0][0])))
        self.write(GUARD.OWNERSHIP_PATH, GUARD.canonical_json({"authorized_paths": GUARD.REPAIR_PURPOSES}))
        self.controls = tuple((path, GUARD.sha256((self.root / path).read_bytes()))
                              for path in sorted(GUARD.CONTROL_PATHS))
        self.history_controls = {path: {digest} for path, digest in self.controls}
        self.history_controls[GUARD.GUARD_PATH] = {GUARD.sha256((self.root / GUARD.GUARD_PATH).read_bytes())}
        self.manifest()
        self.commit("Sucessor tecnico restrito")
        self.repair_head = self.head
        self.repair_tree = self.tree

    def restore_positive(self):
        self.git("reset", "--hard", self.repair_head)
        self.check()

    def close(self):
        self.temporary.cleanup()

    def git(self, *args, raw=None):
        return subprocess.check_output(["git", *args], cwd=self.root, input=raw).decode("utf-8").strip()

    @property
    def head(self):
        return self.git("rev-parse", "HEAD")

    @property
    def tree(self):
        return self.git("rev-parse", "HEAD^{tree}")

    def write(self, path, raw):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw if isinstance(raw, bytes) else raw.encode("utf-8"))

    def commit(self, message):
        self.git("add", "-A")
        self.git("-c", "user.name=Synthetic AP04 F2", "-c", "user.email=f2@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "--allow-empty", "-qm", message)

    def manifest(self):
        paths = set(GUARD.REPAIR_PATHS) | {item["path"] for item in self.documents}
        paths.remove(GUARD.MANIFEST_PATH)
        self.write(GUARD.MANIFEST_PATH, "".join(
            GUARD.sha256((self.root / path).read_bytes()) + "  " + path + "\n" for path in sorted(paths)))

    def check(self):
        GUARD.verify_epochs(self.root, self.epochs, self.c4)
        GUARD.verify_documents(self.root, self.documents)
        GUARD.verify_repair_history(self.root, self.baseline, self.head, GUARD.REPAIR_PATHS,
                                    self.history_controls)
        GUARD.verify_final_delta(self.root, self.baseline, self.head,
                                 GUARD.REPAIR_PATHS, GUARD.MODIFIED_REPAIR_PATHS)
        GUARD.verify_controls(self.root, self.controls, GUARD.CONTROL_PATHS)
        GUARD.verify_overlay(self.root, self.documents, GUARD.REPAIR_PURPOSES,
                             GUARD.REPAIR_PATHS, GUARD.OVERLAY_PATH, GUARD.MANIFEST_PATH,
                             GUARD.OWNERSHIP_PATH, self.baseline, self.epochs[0][0])

    def mode(self, path, mode):
        blob = self.git("hash-object", "-w", "--stdin", raw=b"inert synthetic target\n")
        target = self.head if mode == "160000" else blob
        self.git("update-index", "--add", "--cacheinfo", mode + "," + target + "," + path)
        self.git("-c", "user.name=Synthetic AP04 F2", "-c", "user.email=f2@example.invalid",
                 "-c", "commit.gpgsign=false", "commit", "-qm", "Forbidden synthetic mode")


class F2EpochAdversarialTests(unittest.TestCase):
    def setUp(self):
        self.repo = SyntheticEpochs()
        self.addCleanup(self.repo.close)

    def assertRed(self):
        with self.assertRaises((GUARD.GuardError, OSError, ValueError)):
            self.repo.check()

    def test_positive_c4_ap04_f1_f2_epochs_and_restricted_successor(self):
        self.repo.check()
        self.assertEqual(GUARD.verify_epochs(self.repo.root, self.repo.epochs, self.repo.c4), self.repo.baseline)
        self.assertEqual(len(self.repo.documents), 19)
        self.assertEqual(len(GUARD.REPAIR_PATHS), 19)

    def test_exact_frozen_epoch_tree_and_parent_are_required(self):
        for index in range(len(self.repo.epochs)):
            for column in (1, 2):
                with self.subTest(epoch=index, column=column):
                    changed = [list(item) for item in self.repo.epochs]
                    changed[index][column] = "0" * 40
                    with self.assertRaises(GUARD.GuardError):
                        GUARD.verify_epochs(self.repo.root, changed, self.repo.c4)

    def test_frozen_epoch_transient_change_and_revert_cannot_replace_pinned_history(self):
        reviewed_sha, reviewed_tree, reviewed_parent = self.repo.epochs[1]
        self.repo.git("reset", "--hard", reviewed_sha)
        path = self.repo.protected[0]
        original = (self.repo.root / path).read_bytes()
        self.repo.write(path, "illicit historical mutation\n")
        self.repo.commit("Transitorio ilicito")
        self.repo.write(path, original)
        self.repo.commit("Revertido")
        self.assertEqual(self.repo.tree, reviewed_tree)
        forged = [(self.repo.head, reviewed_tree, reviewed_parent)]
        with self.assertRaisesRegex(GUARD.GuardError, "Frozen epoch parent changed"):
            GUARD.verify_epochs(self.repo.root, forged, reviewed_parent)

    def test_unlisted_docs_scripts_workflows_tests_and_protocol_are_red(self):
        for path in ("docs/UNLISTED.md", "scripts/unlisted.py", ".github/workflows/unlisted.yml",
                     "tests/unlisted.py", "packages/protocol/unlisted.json"):
            with self.subTest(path=path):
                self.repo.restore_positive()
                self.repo.write(path, "unapproved\n")
                self.repo.commit("Arquivo extra")
                self.assertRed()

    def test_all_nineteen_documents_reject_edits_even_with_rehashed_overlay(self):
        for item in self.repo.documents:
            with self.subTest(path=item["path"]):
                self.repo.restore_positive()
                original = (self.repo.root / item["path"]).read_bytes()
                self.repo.write(item["path"], original + b"changed\n")
                self.repo.manifest()
                self.repo.commit("Documento alterado e manifesto recalculado")
                self.assertRed()
                self.repo.write(item["path"], original)
                self.repo.manifest()
                self.repo.commit("Restaura apenas bytes finais")

    def test_documents_deletion_and_rename_are_red(self):
        for scenario in ("delete", "rename"):
            with self.subTest(scenario=scenario):
                repo = SyntheticEpochs()
                try:
                    path = repo.documents[0]["path"]
                    if scenario == "delete":
                        (repo.root / path).unlink()
                    else:
                        (repo.root / path).rename(repo.root / (path + ".renamed"))
                    repo.commit("Documento removido ou renomeado")
                    with self.assertRaises(GUARD.GuardError):
                        repo.check()
                finally:
                    repo.close()

    def test_all_nineteen_documents_reject_executable_symlink_and_gitlink_modes(self):
        for item in self.repo.documents:
            for mode in ("100755", "120000", "160000"):
                with self.subTest(path=item["path"], mode=mode):
                    self.repo.restore_positive()
                    self.repo.mode(item["path"], mode)
                    self.assertRed()

    def test_repair_transient_unauthorized_change_reverted_remains_red(self):
        path = "packages/protocol/transient.json"
        self.repo.write(path, "{}\n")
        self.repo.commit("Protegido transitorio")
        (self.repo.root / path).unlink()
        self.repo.commit("Reverte transitorio")
        self.assertRed()

    def test_protected_governance_product_audits_manifests_and_reader_are_red(self):
        for path in self.repo.protected:
            with self.subTest(path=path):
                self.repo.restore_positive()
                original = (self.repo.root / path).read_bytes()
                self.repo.write(path, original + b"unauthorized\n")
                self.repo.manifest()
                self.repo.commit("Protecao alterada")
                self.assertRed()
                self.repo.write(path, original)
                self.repo.commit("Reversao nao apaga evidencia")

    def test_overlay_must_be_exact_canonical_and_owned(self):
        overlay = self.repo.root / GUARD.OVERLAY_PATH
        original = overlay.read_bytes()
        scenarios = [
            original + b"\n",
            original.replace(b'"owner": "A"', b'"owner": "B"', 1),
            original.replace(b'"PROPOSED_NOT_APPROVED"', b'"APPROVED"', 1),
            original.replace(b'"path": "scripts/qa/atlas_parity04_f2_doc_ci.py"',
                             b'"path": "scripts/**"', 1),
        ]
        for changed in scenarios:
            with self.subTest(changed=changed[:50]):
                self.repo.restore_positive()
                self.repo.write(GUARD.OVERLAY_PATH, changed)
                self.repo.manifest()
                self.repo.commit("Overlay nao autorizado")
                self.assertRed()
        self.repo.write(GUARD.OVERLAY_PATH, original)

    def test_manifest_missing_duplicate_traversal_folder_reorder_and_wrong_hash_are_red(self):
        manifest = self.repo.root / GUARD.MANIFEST_PATH
        original = manifest.read_text(encoding="utf-8")
        lines = original.splitlines()
        scenarios = [
            "\n".join(lines[1:]) + "\n",
            original + lines[-1] + "\n",
            "0" * 64 + "  ../private\n",
            "0" * 64 + "  docs/**\n",
            "\n".join(reversed(lines)) + "\n",
            "0" * 64 + original[64:],
        ]
        for changed in scenarios:
            with self.subTest(changed=changed[:75]):
                self.repo.restore_positive()
                self.repo.write(GUARD.MANIFEST_PATH, changed)
                self.repo.commit("Manifesto nao autorizado")
                self.assertRed()

    def test_dispatch_test_and_oracle_changes_are_red_after_manifest_rehash(self):
        for path, _digest in self.repo.controls:
            with self.subTest(path=path):
                original = (self.repo.root / path).read_bytes()
                self.repo.write(path, original + b"def weakened_oracle(): return True\n")
                self.repo.manifest()
                self.repo.commit("Controle relaxado e manifesto recalculado")
                with self.assertRaisesRegex(GUARD.GuardError, "Independent control authorization"):
                    GUARD.verify_controls(self.repo.root, self.repo.controls, GUARD.CONTROL_PATHS)
                self.repo.write(path, original)
                self.repo.manifest()
                self.repo.commit("Restauracao final")

    def test_transient_unapproved_control_revision_reverted_remains_red(self):
        for path in sorted(set(self.repo.history_controls) & set(GUARD.REPAIR_PATHS)):
            with self.subTest(path=path):
                self.repo.restore_positive()
                original = (self.repo.root / path).read_bytes()
                self.repo.write(path, original + b"relaxed transient control\n")
                self.repo.manifest()
                self.repo.commit("Semantica transitoria nao aprovada")
                self.repo.write(path, original)
                self.repo.manifest()
                self.repo.commit("Reverte controle e manifesto")
                self.assertEqual(self.repo.tree, self.repo.repair_tree)
                GUARD.verify_controls(self.repo.root, self.repo.controls, GUARD.CONTROL_PATHS)
                with self.assertRaisesRegex(GUARD.GuardError, "Independent control revision authorization"):
                    self.repo.check()


    def test_repair_mode_removal_and_unexpected_parent_are_red(self):
        path = sorted(GUARD.MODIFIED_REPAIR_PATHS)[0]
        for scenario in ("mode", "delete"):
            with self.subTest(scenario=scenario):
                self.repo.restore_positive()
                if scenario == "mode":
                    self.repo.mode(path, "100755")
                else:
                    (self.repo.root / path).unlink()
                    self.repo.commit("Controle removido")
                self.assertRed()
        self.repo.restore_positive()
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_repair_history(self.repo.root, "0" * 40, self.repo.head, GUARD.REPAIR_PATHS)

    def test_branch_name_lookalike_cannot_authorize_unlisted_payload(self):
        self.repo.git("branch", "-m", "docs/atlas-parity04-f2-legacy-contract-20261030-lookalike")
        self.repo.write("docs/unlisted.md", "still unapproved\n")
        self.repo.commit("Nome nao autoriza")
        self.assertRed()

    def test_workflow_bypass_and_unpinned_action_mutations_are_red_after_rehash(self):
        path = ".github/workflows/atlas-parity04-doc.yml"
        markers = ("continue-on-error: true", "paths-ignore:", "run: command || true",
                   "if: false", "uses: actions/checkout@main", "pytest.skip()",
                   "@unittest.skip('bypass')", "xfail", "run: wrong_dispatch.py")
        for marker in markers:
            with self.subTest(marker=marker):
                self.repo.restore_positive()
                self.repo.write(path, (self.repo.root / path).read_bytes() + marker.encode("utf-8"))
                self.repo.manifest()
                self.repo.commit("Bypass nao autorizado")
                with self.assertRaisesRegex(GUARD.GuardError, "Independent control authorization"):
                    GUARD.verify_controls(self.repo.root, self.repo.controls, GUARD.CONTROL_PATHS)


class F2IndependentPreflightTests(unittest.TestCase):
    def test_guard_source_has_independent_authorization(self):
        self.assertEqual(hashlib.sha256(source_without_control_table(GUARD_SOURCE)).hexdigest(),
                         APPROVED_GUARD_SOURCE)
        changed = GUARD_SOURCE.replace(b"        raise GuardError(message)", b"        return None", 1)
        self.assertNotEqual(changed, GUARD_SOURCE)
        self.assertNotEqual(hashlib.sha256(source_without_control_table(changed)).hexdigest(),
                            APPROVED_GUARD_SOURCE)

    def test_control_table_expression_is_rejected_before_import(self):
        changed = GUARD_SOURCE.replace(b"APPROVED_CONTROL_HASHES = (",
                                       b"APPROVED_CONTROL_HASHES = unapproved_effect() or (", 1)
        with self.assertRaisesRegex(RuntimeError, "inert literal"):
            source_without_control_table(changed)

    def test_shared_line_semicolon_cannot_hide_execution_in_excluded_table(self):
        changed = GUARD_SOURCE.replace(b")\n# END_APPROVED_CONTROL_HASHES",
                                       b"); unapproved_effect()\n# END_APPROVED_CONTROL_HASHES", 1)
        with self.assertRaisesRegex(RuntimeError, "isolated canonical lines|shares excluded"):
            source_without_control_table(changed)

    def test_non_utf8_codec_cannot_hide_execution(self):
        changed = b"# coding: raw_unicode_escape\n" + GUARD_SOURCE + b"\n#\\u000aunapproved_effect()\n"
        with self.assertRaisesRegex(RuntimeError, "UTF-8"):
            source_without_control_table(changed)

    def test_control_inventory_and_test_bytes_are_independently_pinned(self):
        expected = {**APPROVED_EXTERNAL_CONTROLS,
                    TEST_PATH: hashlib.sha256((ROOT / TEST_PATH).read_bytes()).hexdigest()}
        self.assertEqual(dict(GUARD.APPROVED_CONTROL_HASHES), expected)
        GUARD.verify_controls(ROOT, GUARD.APPROVED_CONTROL_HASHES, GUARD.CONTROL_PATHS)

    def test_production_epochs_classify_exact_c4_ap04_f1_f2_by_git_identity(self):
        expected = {GUARD.C4_SHA: "C4_BASELINE",
                    GUARD.AP04_SHA: "AP04_DOCUMENTATION_SNAPSHOT",
                    GUARD.F1_SHA: "AP04_F1_DOCUMENTATION_SNAPSHOT",
                    GUARD.F2_SHA: "AP04_F2_DOCUMENTATION_SNAPSHOT"}
        for ref, mode in expected.items():
            with self.subTest(ref=ref):
                self.assertEqual(GUARD.classify_ref(ROOT, ref), mode)

    def test_production_nineteen_document_blobs_hashes_and_modes_are_frozen(self):
        self.assertEqual(len(GUARD.FROZEN_DOCUMENTS), 19)
        GUARD.verify_documents(ROOT, GUARD.FROZEN_DOCUMENTS)

    def test_security_guards_contain_no_optimized_away_assert(self):
        self.assertFalse(any(isinstance(node, ast.Assert)
                             for node in ast.walk(ast.parse(GUARD_SOURCE.decode("utf-8")))))

    def test_inherited_collection_rejects_subsets_and_preserves_exact_191_ids(self):
        spec = importlib.util.spec_from_file_location(
            "ap04_f2_collection_control", ROOT / "scripts/qa/atlas_parity03_c4_ci.py")
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        raw = subprocess.check_output(
            ["git", "show", GUARD.AP04_SHA + ":docs/missions/atlas-parity-04/ci-repair/CI-EVIDENCE.json"],
            cwd=ROOT)
        evidence = json.loads(raw)
        inherited = evidence["installed_regression"]
        ids = set(inherited["inherited_c4_test_ids"]) | set(inherited["new_ap04_test_ids"])
        self.assertEqual(len(ids), 191)
        module.verify_f2_inherited_collection(ids)
        with self.assertRaises(RuntimeError):
            module.verify_f2_inherited_collection(set(sorted(ids)[1:]))

    def test_test_receipts_reject_previous_sha_subsets_duplicates_and_skips(self):
        good = {"status": "PASS", "tested_sha": "a" * 40, "tested_tree": "b" * 40,
                "test_ids": ["case-a", "case-b"], "tests_run": 2, "skips": 0,
                "failures": 0, "errors": 0, "loader_errors": []}
        GUARD.verify_test_receipt(good, "a" * 40, "b" * 40, {"case-a", "case-b"})
        mutations = ({"tested_sha": "c" * 40}, {"tested_tree": "c" * 40},
                     {"test_ids": ["case-a"], "tests_run": 1},
                     {"test_ids": ["case-a", "case-a"]}, {"skips": 1},
                     {"loader_errors": ["failed import"]})
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                with self.assertRaises(GUARD.GuardError):
                    GUARD.verify_test_receipt({**good, **mutation},
                                              "a" * 40, "b" * 40, {"case-a", "case-b"})


    def test_workflow_bypasses_unpinned_actions_and_wrong_selection_are_red(self):
        old = GUARD.load_historical(ROOT)
        for path in sorted(GUARD.WORKFLOW_PATHS):
            raw = (ROOT / path).read_bytes()
            self.assertTrue(old.workflow_action_pins(raw, path))
            for forbidden in ("github.head_ref", "github.ref_name", "continue-on-error",
                              "paths-ignore", "|| true", "if: false", "pytest.skip",
                              "@unittest.skip", "xfail"):
                self.assertNotIn(forbidden, raw.decode("utf-8"))
            with self.assertRaises(old.GuardError):
                old.workflow_action_pins(b"steps:\n  - uses: actions/checkout@main\n", path)
        # The fixed digest, not the supplementary manifest, authorizes workflow selection.
        original = (ROOT / ".github/workflows/atlas-parity04-doc.yml").read_bytes()
        self.assertIn(b"merge-base --is-ancestor", original)
        self.assertIn(b"atlas_parity04_f2_doc_ci.py", original)
        self.assertIn(b"atlas_parity04_doc_ci.py", original)


class ReceiptResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.receipts = []
        self.started = {}

    def startTest(self, test):
        self.started[test.id()] = time.monotonic()
        super().startTest(test)

    def record(self, test, status, detail=""):
        self.receipts.append({"id": test.id(), "status": status, "detail": detail,
                              "seconds": time.monotonic() - self.started.get(test.id(), time.monotonic())})

    def addSuccess(self, test):
        self.record(test, "PASS")
        super().addSuccess(test)

    def addFailure(self, test, err):
        self.record(test, "FAIL", self._exc_info_to_string(err, test))
        super().addFailure(test, err)

    def addError(self, test, err):
        self.record(test, "ERROR", self._exc_info_to_string(err, test))
        super().addError(test, err)

    def addSkip(self, test, reason):
        self.record(test, "SKIP", reason)
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self.record(test, "XFAIL", self._exc_info_to_string(err, test))
        super().addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self.record(test, "XPASS")
        super().addUnexpectedSuccess(test)


def run_regressions(root, output, junit):
    loader = unittest.TestLoader()
    suite = loader.discover(str(root / "tests/qa"), pattern="test_atlas_parity04_f2_doc_ci.py")
    result = unittest.TextTestRunner(verbosity=2, resultclass=ReceiptResult).run(suite)
    ids = [item["id"] for item in result.receipts]
    passed = (result.wasSuccessful() and not loader.errors and result.testsRun > 0
              and len(ids) == len(set(ids)) and len(ids) == result.testsRun
              and not result.skipped and not result.expectedFailures
              and not result.unexpectedSuccesses and all(item["status"] == "PASS" for item in result.receipts))
    report = {"status": "PASS" if passed else "FAIL", "tested_sha": GUARD.git(root, "rev-parse", "HEAD"),
              "tested_tree": GUARD.git(root, "rev-parse", "HEAD^{tree}"), "optimization": sys.flags.optimize,
              "tests_run": result.testsRun, "test_ids": ids, "cases": result.receipts,
              "skips": len(result.skipped), "loader_errors": loader.errors,
              "failures": len(result.failures), "errors": len(result.errors)}
    if passed:
        GUARD.verify_test_receipt(report, GUARD.git(root, "rev-parse", "HEAD"),
                                  GUARD.git(root, "rev-parse", "HEAD^{tree}"), ids)
    GUARD.write_json(output, report)
    junit.parent.mkdir(parents=True, exist_ok=True)
    document = ET.Element("testsuite", name="AP04-F2-regressions", tests=str(result.testsRun),
                          failures=str(len(result.failures)), errors=str(len(result.errors)), skipped=str(len(result.skipped)))
    props = ET.SubElement(document, "properties")
    for key in ("tested_sha", "tested_tree", "optimization"):
        ET.SubElement(props, "property", name=key, value=str(report[key]))
    for item in result.receipts:
        case = ET.SubElement(document, "testcase", classname="AP04F2Regression",
                             name=item["id"], time=str(max(0, item["seconds"])))
        if item["status"] != "PASS":
            ET.SubElement(case, "failure", message=item["status"]).text = item["detail"]
    ET.ElementTree(document).write(junit, encoding="utf-8", xml_declaration=True)
    return 0 if passed else 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--junit", type=Path)
    args, remaining = parser.parse_known_args()
    if args.output is None and args.junit is None:
        unittest.main(argv=[sys.argv[0], *remaining])
    else:
        if args.output is None or args.junit is None or remaining:
            parser.error("Both receipt paths and no extra arguments are required")
        raise SystemExit(run_regressions(ROOT, args.output.resolve(), args.junit.resolve()))
