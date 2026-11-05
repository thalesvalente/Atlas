"""Regressões do gate de blobs exatos da interface original sem fontes privadas."""
from __future__ import annotations

from pathlib import Path
import runpy
import unittest

REPO = Path(__file__).resolve().parents[2]
# scripts/ is an engineering entrypoint, not an installed Python package.
# Load the real checker by path without changing the Atlas package boundary.
AUDIT = runpy.run_path(str(REPO / "scripts/qa/speckit_audit.py"))
ORIGINAL_BRIDGE_BLOBS = AUDIT["ORIGINAL_BRIDGE_BLOBS"]
git_blob_id = AUDIT["git_blob_id"]
exact_original_bridge = AUDIT["exact_original_bridge"]


class ExactOriginalBridgeGuardTests(unittest.TestCase):
    def test_only_the_published_original_implementation_blobs_are_accepted(self):
        self.assertEqual(len(ORIGINAL_BRIDGE_BLOBS), 3)
        for path, expected in ORIGINAL_BRIDGE_BLOBS.items():
            with self.subTest(path=path):
                real_source_bytes = (REPO / path).read_bytes()
                if path == 'packages/atlas/src/atlas_viewer/server.py':
                    # Feature 005 is a strictly constrained successor, never a
                    # replacement of the published original blob's identity.
                    self.assertFalse(exact_original_bridge(path, real_source_bytes))
                    self.assertTrue(AUDIT['exact_triage_static_successor'](path, real_source_bytes))
                    for asset in ('native_triage_model', 'native_retention', 'native_triage_ui'):
                        line = (f'          "/{asset}.js": ("{asset}.js", '
                                '"text/javascript; charset=utf-8"),\n').encode('utf-8')
                        self.assertEqual(real_source_bytes.count(line), 1)
                        real_source_bytes = real_source_bytes.replace(line, b'', 1)
                self.assertEqual(git_blob_id(real_source_bytes), expected)
                self.assertTrue(exact_original_bridge(path, real_source_bytes))
                self.assertFalse(exact_original_bridge(path, real_source_bytes + b" "))
                self.assertFalse(exact_original_bridge(path + ".unexpected", real_source_bytes))

    def test_no_other_baseline_is_silently_whitelisted(self):
        self.assertFalse(exact_original_bridge(
            ".specify/feature.json", b"{}"))
        self.assertFalse(exact_original_bridge(
            "packages/protocol/src/caderno_protocol/read_model.py", b"changed"))


if __name__ == "__main__":
    unittest.main()
