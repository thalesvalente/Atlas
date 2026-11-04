"""Independent preflight and adversarial Git histories for the K successor."""
from __future__ import annotations

import ast
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import tokenize
import types
import unittest


ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = "scripts/qa/atlas_parity04_k_doc_ci.py"
TEST_PATH = "tests/qa/test_atlas_parity04_k_doc_ci.py"
EXPECTED_GUARD_SHA256 = '78a49a9183b5942ddb65602997f6ffa089836a405aef9bfc4375a467d937d5e6'
APPROVED_EXTERNAL_HASHES = {'.github/workflows/atlas-parity02.yml': '4af24eca5ac8838b7cde70837e2a280dad8b5e5501185338806cc766533b1b4e', '.github/workflows/atlas-parity03-p03-gates.yml': 'bf9866bad49b578e5d7b11cabcb4205cd6f753fb8e7cc3926bb4cf4d01ead7f0', '.github/workflows/atlas-parity04-doc.yml': 'e59dc02fe16cd9565ba7d4152c6aba0435f53c091e6de2c69173a35dcd31f260', '.github/workflows/atlas003-speckit.yml': '205281c0ef8c75a188fea2236a4dbe7fc82b588d27606612d504846b297dd068', '.github/workflows/atlas021.yml': '03aac2ea8243e8799edfd9bff66a9bb670e5fd0320b480a342311bb16448a2e8', 'docs/missions/atlas-parity-04/c4-k-successor-ci/K-BINDING.json': '24cdb857746b481257f90972c0602cf5b77377286d8be5607224872d1dda4fb7', 'docs/missions/atlas-parity-04/c4-k-successor-ci/RESULT.md': '593dcfb947a8e473d731aef10439fafce022b6b7c48b052c1b3311fea745a148', 'scripts/qa/atlas_parity02_p06_installed_checks.py': 'e59663002278ce231dfbd65b8f5242e49977ce6eab6a877346a2fc79e0d30c5e', 'scripts/qa/atlas_parity03_c4_ci.py': '206052c28d341c399037c6900a912c2310899e1af77134b7ce2d75444137f031', 'scripts/run_checks.py': '7f54ba3033c3ef88fd42781bd7d62aae83ab99d23a825848a35098f16d447a05'}


def normalized_guard_source(raw):
    """Exclude inert hash data only; authorize every executable source byte."""
    encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    if encoding != "utf-8":
        raise RuntimeError("Guard must use UTF-8")
    source = raw.decode("utf-8")
    tree = ast.parse(source)
    tables = [node for node in tree.body
              if isinstance(node, ast.Assign) and len(node.targets) == 1
              and isinstance(node.targets[0], ast.Name)
              and node.targets[0].id == "APPROVED_HASHES"]
    if len(tables) != 1:
        raise RuntimeError("Expected exactly one approved hash table")
    table = tables[0]
    if isinstance(table.value, ast.Dict):
        keys = [ast.literal_eval(key) for key in table.value.keys]
        if len(set(keys)) != len(keys):
            raise RuntimeError("Duplicate approved hash keys")
    try:
        data = ast.literal_eval(table.value)
    except (ValueError, TypeError, SyntaxError) as error:
        raise RuntimeError("Hash table must contain inert literal data") from error
    if isinstance(data, dict):
        pairs = list(data.items())
    elif isinstance(data, tuple):
        pairs = list(data)
    else:
        raise RuntimeError("Unexpected hash-table shape")
    if any(not isinstance(pair, tuple) or len(pair) != 2
           or not all(isinstance(value, str) for value in pair) for pair in pairs):
        raise RuntimeError("Hash table must contain string pairs")
    if len(dict(pairs)) != len(pairs):
        raise RuntimeError("Duplicate approved hash keys")
    lines = source.splitlines(keepends=True)
    first, last = table.lineno - 1, table.end_lineno
    if lines[first].lstrip() != lines[first] or not lines[first].startswith("APPROVED_HASHES = "):
        raise RuntimeError("Hash table must start on its own line")
    for node in tree.body:
        if node is not table and getattr(node, "lineno", 0) <= last and getattr(node, "end_lineno", 0) > first:
            raise RuntimeError("Executable syntax shares excluded table lines")
    # Token positions also reject semicolon statements or trailing expressions
    # that might otherwise be hidden inside the removed physical source lines.
    if lines[last - 1][table.end_col_offset:].strip():
        raise RuntimeError("Unexpected trailing syntax on hash-table line")
    return "".join(lines[:first] + lines[last:]).encode("utf-8")


def verify_approved_control_hashes(raw, external_hashes=None, test_bytes=None):
    """Excluded table data requires an inventory independent of the guard."""
    normalized_guard_source(raw)
    tree = ast.parse(raw.decode("utf-8"))
    table = next(node for node in tree.body
                 if isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name)
                 and node.targets[0].id == "APPROVED_HASHES")
    actual = dict(ast.literal_eval(table.value))
    external = APPROVED_EXTERNAL_HASHES if external_hashes is None else external_hashes
    own_bytes = (ROOT / TEST_PATH).read_bytes() if test_bytes is None else test_bytes
    expected = {**external, TEST_PATH: hashlib.sha256(own_bytes).hexdigest()}
    if actual != expected:
        raise RuntimeError("Independent K approved-control inventory differs")


GUARD_SOURCE = (ROOT / GUARD_PATH).read_bytes()
if hashlib.sha256(normalized_guard_source(GUARD_SOURCE)).hexdigest() != EXPECTED_GUARD_SHA256:
    raise RuntimeError("Independent K guard source authorization failed before import")
verify_approved_control_hashes(GUARD_SOURCE)
GUARD = types.ModuleType("atlas_parity04_k_doc_ci")
GUARD.__file__ = str(ROOT / GUARD_PATH)
sys.modules[GUARD.__name__] = GUARD
exec(compile(GUARD_SOURCE.decode("utf-8"), GUARD.__file__, "exec", dont_inherit=True), GUARD.__dict__)


class SyntheticGit:
    """A fresh object database; no real repository, branch, or index is reused."""

    def __init__(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="atlas-k-negative-")
        self.root = Path(self.temporary.name)
        self.environment = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", "--initial-branch=main")
        self.git("config", "user.name", "Synthetic K QA")
        self.git("config", "user.email", "synthetic-k-qa@example.invalid")
        self.git("config", "core.autocrlf", "false")
        self.git("config", "core.filemode", "true")
        self.git("config", "commit.gpgsign", "false")
        self.git("config", "core.hooksPath", str(self.root / "no-hooks"))
        self.write("docs/historical/F2.md", b"Frozen F2 contract\n")
        self.write("docs/historical/MANIFEST.sha256", b"Frozen historical manifest\n")
        self.write("scripts/historical.py", b"historical = True\n")
        self.base = self.commit("Synthetic immutable baseline")

    def git(self, *arguments, data=None):
        result = subprocess.run(["git", "-C", str(self.root), *arguments],
                                input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=self.environment, check=False)
        if result.returncode:
            raise RuntimeError(f"Synthetic Git command failed: {arguments!r}: {result.stderr.decode('utf-8', 'replace')}")
        return result.stdout

    def write(self, path, data):
        destination = self.root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)

    def commit(self, message):
        self.git("add", "--all")
        self.git("commit", "-q", "-m", message)
        return self.head()

    def commit_index(self, message):
        self.git("commit", "-q", "-m", message)
        return self.head()

    def head(self):
        return self.git("rev-parse", "HEAD").decode("ascii").strip()

    def raw_entry(self, path, mode, data=b"synthetic payload\n", oid=None):
        if oid is None:
            oid = self.git("hash-object", "-w", "--stdin", data=data).decode("ascii").strip()
        self.git("update-index", "--add", "--cacheinfo", f"{mode},{oid},{path}")

    def records(self, head, paths):
        result = {}
        for path in paths:
            record = self.git("ls-tree", head, "--", path).decode("utf-8").strip()
            metadata, _ = record.split("\t", 1)
            mode, kind, blob = metadata.split()
            content = self.git("cat-file", "blob", blob)
            result[path] = {"mode": mode, "type": kind, "blob": blob,
                            "sha256": hashlib.sha256(content).hexdigest()}
        return result

    def overlay(self):
        self.write("docs/k/A.md", b"Candidate A, not approval\n")
        return self.commit("Synthetic K overlay")

    def manifested_overlay(self, lines=None):
        payloads = {"docs/k/A.md": b"Candidate A\n", "docs/k/B.json": b'{"candidate": true}\n'}
        for path, payload in payloads.items():
            self.write(path, payload)
        if lines is None:
            lines = [f"{hashlib.sha256(payload).hexdigest()}  {path}\n"
                     for path, payload in sorted(payloads.items())]
        self.write("docs/k/MANIFEST.sha256", "".join(lines).encode("utf-8"))
        head = self.commit("Synthetic manifested overlay")
        return head, set(payloads) | {"docs/k/MANIFEST.sha256"}

    def close(self):
        self.temporary.cleanup()


class KSuccessorGitTests(unittest.TestCase):
    def setUp(self):
        self.repo = SyntheticGit()
        self.addCleanup(self.repo.close)

    def verify(self, head=None, paths=None, modified=(), records=None):
        return GUARD.verify_leg(self.repo.root, self.repo.base,
                                head or self.repo.head(), paths or {"docs/k/A.md"},
                                modified_paths=set(modified), expected_records=records)

    def test_accepts_exact_addition_and_authorized_control_modification(self):
        self.repo.write("docs/k/A.md", b"Candidate A\n")
        self.repo.write("scripts/historical.py", b"historical = True\nnew_guard = True\n")
        first = self.repo.commit("Synthetic permitted additions and control repair")
        self.repo.write("docs/k/A.md", b"Candidate A revised\n")
        head = self.repo.commit("Synthetic permitted documentary correction")
        self.assertNotEqual(first, head)
        paths = {"docs/k/A.md", "scripts/historical.py"}
        self.verify(head, paths, {"scripts/historical.py"}, self.repo.records(head, paths))

    def test_rejects_extra_path(self):
        self.repo.overlay()
        self.repo.write("docs/k/UNAUTHORIZED.md", b"extra\n")
        self.repo.commit("Synthetic unauthorized extra path")
        with self.assertRaises(GUARD.GuardError):
            self.verify()

    def test_rejects_missing_authorized_path(self):
        self.repo.overlay()
        with self.assertRaises(GUARD.GuardError):
            self.verify(paths={"docs/k/A.md", "docs/k/MISSING.md"})

    def test_rejects_final_historical_document_change(self):
        self.repo.write("docs/historical/F2.md", b"Unauthorized changed contract\n")
        self.repo.write("docs/k/A.md", b"Candidate A\n")
        self.repo.commit("Synthetic historical mutation")
        with self.assertRaises(GUARD.GuardError):
            self.verify()

    def test_rejects_changed_then_reverted_historical_document(self):
        original = self.repo.git("show", self.repo.base + ":docs/historical/F2.md")
        self.repo.write("docs/historical/F2.md", b"Unauthorized transient contract\n")
        self.repo.commit("Synthetic prohibited intermediate history")
        self.repo.write("docs/historical/F2.md", original)
        self.repo.write("docs/k/A.md", b"Candidate A\n")
        self.repo.commit("Synthetic revert does not erase prohibited history")
        self.assertEqual(self.repo.git("show", "HEAD:docs/historical/F2.md"), original)
        with self.assertRaises(GUARD.GuardError):
            self.verify()

    def test_rejects_extra_path_added_then_removed(self):
        self.repo.write("docs/STRANGER.md", b"transient stranger\n")
        self.repo.commit("Synthetic forbidden intermediate object")
        (self.repo.root / "docs/STRANGER.md").unlink()
        self.repo.write("docs/k/A.md", b"Candidate A\n")
        self.repo.commit("Synthetic stranger removal")
        with self.assertRaises(GUARD.GuardError):
            self.verify()

    def test_rejects_pinned_object_substitution(self):
        pinned = self.repo.overlay()
        records = self.repo.records(pinned, {"docs/k/A.md"})
        self.repo.write("docs/k/A.md", b"Substituted candidate object\n")
        self.repo.commit("Synthetic pinned object substitution")
        with self.assertRaises(GUARD.GuardError):
            self.verify(records=records)

    def test_rejects_false_pinned_hash_for_matching_blob(self):
        head = self.repo.overlay()
        records = self.repo.records(head, {"docs/k/A.md"})
        records["docs/k/A.md"]["sha256"] = "0" * 64
        with self.assertRaises(GUARD.GuardError):
            self.verify(records=records)

    def test_rejects_symlink_mode(self):
        self.repo.raw_entry("docs/k/A.md", "120000", data=b"../historical/F2.md")
        head = self.repo.commit_index("Synthetic symlink candidate")
        with self.assertRaises(GUARD.GuardError):
            self.verify(head)

    def test_rejects_executable_document_mode(self):
        self.repo.raw_entry("docs/k/A.md", "100755")
        head = self.repo.commit_index("Synthetic executable document")
        with self.assertRaises(GUARD.GuardError):
            self.verify(head)

    def test_rejects_gitlink_object(self):
        self.repo.raw_entry("docs/k/A.md", "160000", oid=self.repo.base)
        head = self.repo.commit_index("Synthetic gitlink candidate")
        with self.assertRaises(GUARD.GuardError):
            self.verify(head)

    def test_rejects_unauthorized_rename(self):
        (self.repo.root / "docs/k").mkdir(parents=True)
        self.repo.git("mv", "docs/historical/F2.md", "docs/k/A.md")
        head = self.repo.commit_index("Synthetic unauthorized historical rename")
        with self.assertRaises(GUARD.GuardError):
            self.verify(head)

    def test_rejects_added_document_deleted_then_readded(self):
        self.repo.overlay()
        (self.repo.root / "docs/k/A.md").unlink()
        self.repo.commit("Synthetic prohibited deletion")
        self.repo.write("docs/k/A.md", b"Candidate A restored\n")
        self.repo.commit("Synthetic restoration")
        with self.assertRaises(GUARD.GuardError):
            self.verify()

    def test_rejects_unrelated_ancestry(self):
        self.repo.git("checkout", "-q", "--orphan", "unrelated")
        head = self.repo.overlay()
        with self.assertRaises(GUARD.GuardError):
            self.verify(head)

    def test_rejects_merge_ancestry_even_with_only_authorized_paths(self):
        self.repo.git("checkout", "-q", "-b", "side")
        self.repo.write("docs/k/A.md", b"Candidate A\n")
        self.repo.commit("Synthetic side overlay")
        self.repo.git("checkout", "-q", "main")
        self.repo.write("docs/k/B.md", b"Candidate B\n")
        self.repo.commit("Synthetic main overlay")
        self.repo.git("merge", "-q", "--no-ff", "side", "-m", "Synthetic merge")
        with self.assertRaises(GUARD.GuardError):
            self.verify(paths={"docs/k/A.md", "docs/k/B.md"})

    def test_accepts_canonical_full_path_manifest_from_git_blobs(self):
        head, paths = self.repo.manifested_overlay()
        GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)

    def test_rejects_manifest_content_hash_tampering(self):
        head, paths = self.repo.manifested_overlay()
        original = self.repo.git("show", head + ":docs/k/MANIFEST.sha256").decode("utf-8")
        self.repo.write("docs/k/MANIFEST.sha256", ("0" * 64 + original[64:]).encode("utf-8"))
        head = self.repo.commit("Synthetic manifest tampering")
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)

    def test_rejects_path_traversal_in_manifest(self):
        head, paths = self.repo.manifested_overlay(["0" * 64 + "  ../outside.md\n"])
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)

    def test_rejects_manifest_duplicate_path(self):
        digest = hashlib.sha256(b"Candidate A\n").hexdigest()
        head, paths = self.repo.manifested_overlay([f"{digest}  docs/k/A.md\n"] * 2)
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)

    def test_rejects_manifest_missing_entry(self):
        digest = hashlib.sha256(b"Candidate A\n").hexdigest()
        head, paths = self.repo.manifested_overlay([f"{digest}  docs/k/A.md\n"])
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)

    def test_rejects_manifest_unordered_entries(self):
        lines = [f"{hashlib.sha256(payload).hexdigest()}  {path}\n" for path, payload in
                 [("docs/k/B.json", b'{"candidate": true}\n'), ("docs/k/A.md", b"Candidate A\n")]]
        head, paths = self.repo.manifested_overlay(lines)
        with self.assertRaises(GUARD.GuardError):
            GUARD.verify_manifest(self.repo.root, head, "docs/k/MANIFEST.sha256", paths)


class KGuardSourcePreflightTests(unittest.TestCase):
    def test_authorizes_all_source_except_literal_hash_table(self):
        raw = b'header = True\nAPPROVED_HASHES = {"a": "b"}\nfooter = True\n'
        self.assertEqual(normalized_guard_source(raw), b"header = True\nfooter = True\n")

    def test_rejects_executable_hash_table(self):
        with self.assertRaises(RuntimeError):
            normalized_guard_source(b'APPROVED_HASHES = dict(a="b")\n')

    def test_rejects_executable_statement_sharing_table_line(self):
        with self.assertRaises(RuntimeError):
            normalized_guard_source(b'APPROVED_HASHES = {"a": "b"}; print("bypass")\n')

    def test_rejects_duplicate_literal_table_keys(self):
        with self.assertRaises(RuntimeError):
            normalized_guard_source(b'APPROVED_HASHES = {"a": "b", "a": "c"}\n')

    def test_rejects_non_utf8_codec_before_execution(self):
        with self.assertRaises(RuntimeError):
            normalized_guard_source(b'# coding: latin-1\nAPPROVED_HASHES = {"a": "b"}\n')

    def test_accepts_independently_pinned_control_inventory(self):
        own_bytes = b"Synthetic independent test source\n"
        inventory = {"workflow.yml": "a" * 64,
                     TEST_PATH: hashlib.sha256(own_bytes).hexdigest()}
        raw = ("APPROVED_HASHES = " + repr(inventory) + "\n").encode("utf-8")
        verify_approved_control_hashes(raw, {"workflow.yml": "a" * 64}, own_bytes)

    def test_rejects_rehashed_external_control_even_with_matching_own_test_hash(self):
        own_bytes = b"Synthetic independent test source\n"
        inventory = {"workflow.yml": "a" * 64,
                     TEST_PATH: hashlib.sha256(own_bytes).hexdigest()}
        original = ("APPROVED_HASHES = " + repr(inventory) + "\n").encode("utf-8")
        inventory["workflow.yml"] = "b" * 64
        tampered = ("APPROVED_HASHES = " + repr(inventory) + "\n").encode("utf-8")
        self.assertEqual(normalized_guard_source(original), normalized_guard_source(tampered))
        with self.assertRaises(RuntimeError):
            verify_approved_control_hashes(tampered, {"workflow.yml": "a" * 64}, own_bytes)


if __name__ == "__main__":
    unittest.main()
