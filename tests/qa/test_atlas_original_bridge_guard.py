"""Regressões do gate de blobs exatos da interface original sem fontes privadas."""
from __future__ import annotations

from pathlib import Path
import unittest

from scripts.qa.speckit_audit import (
    ORIGINAL_BRIDGE_BLOBS, git_blob_id, exact_original_bridge,
)

REPO = Path(__file__).resolve().parents[2]


class ExactOriginalBridgeGuardTests(unittest.TestCase):
    def test_only_the_published_original_implementation_blobs_are_accepted(self):
        self.assertEqual(len(ORIGINAL_BRIDGE_BLOBS), 3)
        for path, expected in ORIGINAL_BRIDGE_BLOBS.items():
            with self.subTest(path=path):
                real_source_bytes = (REPO / path).read_bytes()
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
