"""F3A component oracles. Every browser check executes real Chromium; no skips."""
from __future__ import annotations
import collections
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import unittest

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path(os.environ.get("F3A_OUTPUT", str(ROOT / ".test-output" / "atlas-parity04-f3a")))
EXPECTED_BROWSER_CHECKS = (
    "hierarchy_selection_and_event", "collapse_expand_focus_and_state", "keyboard_traversal",
    "viewport_controls_reset_fit_and_minimap", "pointer_pan_wheel_zoom_and_pinch",
    "typed_edges_and_no_fabricated_parent", "adversarial_occurrences_counts_and_no_mutation",
    "hostile_text_uri_and_zero_io", "stale_context_cross_source_snapshot_and_disposal",
    "expiry_invalidates_selection_and_links", "invalid_descriptors_rejected_atomically",
    "hierarchy_cycles_retained_as_anomalies", "capacity_and_descriptor_extremes",
    "responsive_390", "responsive_320", "reflow_preserves_focus_zoom_and_selection",
    "authority_validation_gaps_and_expiry_visible",
)

def descriptor_schema():
    text = (ROOT / "docs/missions/atlas-parity-04/f2-legacy-contract/EPHEMERAL-PRESENTATION-CONTRACT.md").read_text(encoding="utf-8")
    # Read frozen F2 documentation only; never rewrite it or extend its authority.
    blocks = re.findall(r"\x60\x60\x60json\n([\s\S]*?)\n\x60\x60\x60", text)
    if len(blocks) != 3:
        raise ValueError("Expected exactly F2 schema and two synthetic examples")
    schema = json.loads(blocks[0])
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker()), [json.loads(b) for b in blocks[1:]]

class F3AGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads((ROOT / "tests/fixtures/atlas_parity04_f3a_graph.json").read_text(encoding="utf-8"))
        cls.validator, cls.f2_examples = descriptor_schema()
        OUTPUT.mkdir(parents=True, exist_ok=True)
        command = ["node", str(ROOT / "scripts/qa/atlas_parity04_f3a_browser.mjs"), str(ROOT), str(OUTPUT)]
        result = subprocess.run(command, cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=600, check=False)
        (OUTPUT / "browser-stdout.log").write_text(result.stdout, encoding="utf-8")
        (OUTPUT / "browser-stderr.log").write_text(result.stderr, encoding="utf-8")
        print(result.stdout, flush=True)
        if result.stderr:
            print(result.stderr, flush=True)
        path = OUTPUT / "browser-receipt.json"
        cls.browser = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"fatal": "Browser runner produced no receipt", "checks": []}
        cls.browser_exit = result.returncode
        cls.checks = {c["name"]: c for c in cls.browser.get("checks", [])}

    def browser_check(self, name):
        self.assertIn(name, self.checks, self.browser.get("fatal", "Missing browser oracle"))
        self.assertTrue(self.checks[name].get("passed"), self.checks[name].get("error"))

    def test_fixture_matches_frozen_descriptor_schema(self):
        self.validator.validate(self.fixture)
        self.assertIs(self.fixture["synthetic"], True)
        self.assertEqual(self.fixture["authority"], "LEGACY_DERIVED")
        self.assertEqual(self.fixture["source"]["source_id"], "synthetic-f3a")
        self.assertEqual(self.fixture["snapshot"]["digest_status"], "NOT_COMPUTED")
        self.assertIsNone(self.fixture["snapshot"]["bytes_sha256"])

    def test_frozen_f2_examples_remain_schema_valid(self):
        for item in self.f2_examples:
            with self.subTest(source=item["source"]["source_id"]):
                self.validator.validate(item)
                self.assertIs(item["synthetic"], True)

    def test_independent_schema_rejects_invalid_version_extra_and_identity(self):
        for mutate in (
            lambda d: d.update(version="9.0.0"),
            lambda d: d.update(unknown=True),
            lambda d: d["nodes"][0]["identity"].update(occurrence=-1),
            lambda d: d["nodes"][0]["identity"].update(navigation_id="javascript:alert(1)"),
        ):
            d = json.loads(json.dumps(self.fixture)); mutate(d)
            self.assertTrue(list(self.validator.iter_errors(d)), "Formal schema unexpectedly admitted invalid fixture")

    def test_occurrences_null_unresolved_collision_and_repeats_reconciled(self):
        d = self.fixture
        self.assertEqual((len(d["nodes"]), len(d["relations"])), (109, 210))
        endpoints = [ref for r in d["relations"] for ref in (r["from"], r["to"])]
        counts = collections.Counter(ref["resolution"] for ref in endpoints)
        self.assertEqual(counts["NULL_ENDPOINT"], 22)
        self.assertEqual(counts["UNRESOLVED"], 75)
        self.assertEqual(counts["COLLISION"], 50)
        native = collections.Counter(n["identity"]["native_id"] for n in d["nodes"] if n["identity"]["native_id"] is not None)
        self.assertEqual(sum(v == 2 for v in native.values()), 50)
        groups = collections.Counter(r["repeat_group"] for r in d["relations"] if r["repeat_group"] is not None)
        self.assertEqual(len(groups), 40)
        self.assertEqual(sum(v - 1 for v in groups.values()), 41)
        navs = [n["identity"]["navigation_id"] for n in d["nodes"]] + [r["identity"]["navigation_id"] for r in d["relations"]]
        self.assertEqual(len(set(navs)), len(navs))
        isolated = next(n for n in d["nodes"] if n["identity"]["navigation_id"] == "nav:isolated")
        self.assertEqual(isolated["entity_status"], "SOURCE_ENTITY")
        self.assertEqual(isolated["identity"]["native_id"], "SYN-ISOLATED")
        self.assertIs(isolated["binding_gap"], True)

    def test_browser_receipt_complete_and_sha_bound(self):
        self.assertNotIn("fatal", self.browser, self.browser.get("fatal"))
        self.assertEqual(self.browser_exit, 0, "Real Chromium runner failed")
        self.assertTrue(self.browser["passed"], "Component browser gate failed")
        self.assertEqual(set(self.checks), set(EXPECTED_BROWSER_CHECKS))
        self.assertEqual(len(self.browser["checks"]), len(EXPECTED_BROWSER_CHECKS))
        self.assertEqual(self.browser["outside_requests"], [])
        self.assertEqual(self.browser["page_errors"], [])
        self.assertEqual(self.browser["storage_calls"], [])
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        tree = subprocess.check_output(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT, text=True).strip()
        self.assertEqual(self.browser["sha"], sha)
        self.assertEqual(self.browser["tree"], tree)
        self.assertTrue(self.browser["browser"])
        self.assertEqual({p["name"] for p in self.browser["screenshots"]}, {"desktop.png", "mobile-390.png", "mobile-320.png"})
        for item in self.browser["screenshots"]:
            data = (OUTPUT / item["name"]).read_bytes()
            self.assertGreater(len(data), 1000)
            self.assertEqual(hashlib.sha256(data).hexdigest(), item["sha256"])
            self.assertEqual(len(data), item["bytes"])

    def test_hierarchy_selection_and_event(self): self.browser_check("hierarchy_selection_and_event")
    def test_collapse_expand_focus_and_state(self): self.browser_check("collapse_expand_focus_and_state")
    def test_keyboard_traversal(self): self.browser_check("keyboard_traversal")
    def test_viewport_controls_reset_fit_and_minimap(self): self.browser_check("viewport_controls_reset_fit_and_minimap")
    def test_pointer_pan_wheel_zoom_and_pinch(self): self.browser_check("pointer_pan_wheel_zoom_and_pinch")
    def test_typed_edges_and_no_fabricated_parent(self): self.browser_check("typed_edges_and_no_fabricated_parent")
    def test_adversarial_occurrences_counts_and_no_mutation(self): self.browser_check("adversarial_occurrences_counts_and_no_mutation")
    def test_hostile_text_uri_and_zero_io(self): self.browser_check("hostile_text_uri_and_zero_io")
    def test_stale_context_cross_source_snapshot_and_disposal(self): self.browser_check("stale_context_cross_source_snapshot_and_disposal")
    def test_expiry_invalidates_selection_and_links(self): self.browser_check("expiry_invalidates_selection_and_links")
    def test_invalid_descriptors_rejected_atomically(self): self.browser_check("invalid_descriptors_rejected_atomically")
    def test_hierarchy_cycles_retained_as_anomalies(self): self.browser_check("hierarchy_cycles_retained_as_anomalies")
    def test_capacity_and_descriptor_extremes(self): self.browser_check("capacity_and_descriptor_extremes")
    def test_responsive_390(self): self.browser_check("responsive_390")
    def test_responsive_320(self): self.browser_check("responsive_320")
    def test_reflow_preserves_focus_zoom_and_selection(self): self.browser_check("reflow_preserves_focus_zoom_and_selection")
    def test_authority_validation_gaps_and_expiry_visible(self): self.browser_check("authority_validation_gaps_and_expiry_visible")

if __name__ == "__main__":
    unittest.main(verbosity=2)
