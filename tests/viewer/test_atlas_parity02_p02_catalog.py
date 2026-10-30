"""C0 regressions against actual public synthetic packages and HTTP boundary."""
from __future__ import annotations

import hashlib
import http.client
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from unittest.mock import patch

from atlas_viewer.catalog import Catalog
from atlas_viewer.server import make_server
from caderno_protocol import load_package, to_read_model

REPO = Path(os.environ.get("ATLAS_TEST_REPO", Path(__file__).resolve().parents[2]))
FIXTURES = REPO / "tests/fixtures/atlas_parity02/p02"
PREFIX = "urn:atlas:synthetic:parity02:p02:"


def hashes(directory):
    return {p.relative_to(directory).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.rglob("*") if p.is_file()}


class P02CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.sources = [self.root / "source-a", self.root / "source-b"]
        for target in self.sources:
            shutil.copytree(FIXTURES / target.name, target)

    def test_fixture_has_28_valid_synthetic_runs_and_duplicate_ids_scoped_by_source(self):
        snapshot = Catalog(self.sources).snapshot()
        self.assertTrue(all(s["report"]["valid"] for s in snapshot["sources"]))
        runs = [r for s in snapshot["sources"] for r in s["read_model"]["runs"]]
        self.assertEqual(len(runs), 28)
        self.assertTrue(all(r["synthetic"] is True for r in runs))
        self.assertEqual(len({r["id"] for r in runs}), 14)
        self.assertTrue(snapshot["collisions"])
        self.assertEqual({r["status"] for r in runs}, {"COMPLETED", "PARTIAL", "FAILED", "RUNNING", "UNKNOWN"})
        self.assertEqual({r["review_status"] for r in runs}, {"UNKNOWN", "HOLD", "REJECTED", "NOT_APPLICABLE"})
        self.assertEqual(len({r["experiment_id"] for r in runs}), 3)

    def test_snapshot_token_is_stable_for_same_instance_and_unchanged_rebuild(self):
        catalog = Catalog(self.sources)
        before = catalog.snapshot()
        self.assertRegex(before["snapshot_id"], r"^[a-f0-9]{64}$")
        self.assertEqual(catalog.snapshot()["snapshot_id"], before["snapshot_id"])
        rebuilt = catalog.rebuild()
        self.assertEqual(rebuilt["snapshot_id"], before["snapshot_id"])
        self.assertGreater(rebuilt["generation"], before["generation"])
        self.assertEqual([s["snapshot_id"] for s in before["sources"]],
                         [s["snapshot_id"] for s in rebuilt["sources"]])

    def test_new_session_and_reordered_allowlist_never_reuse_source_number_scope(self):
        original = Catalog(self.sources).snapshot()
        restarted = Catalog(self.sources).snapshot()
        reversed_sources = Catalog(list(reversed(self.sources))).snapshot()
        self.assertNotEqual(original["snapshot_id"], restarted["snapshot_id"])
        self.assertNotEqual(original["snapshot_id"], reversed_sources["snapshot_id"])
        self.assertNotEqual(original["sources"][0]["name"], reversed_sources["sources"][0]["name"])
        identical = self.root / "identical-copy"
        shutil.copytree(self.sources[0], identical)
        first = Catalog([self.sources[0], identical]).snapshot()
        second = Catalog([identical, self.sources[0]]).snapshot()
        self.assertNotEqual(first["snapshot_id"], second["snapshot_id"])

    def test_changed_source_retains_old_records_and_scope_until_explicit_rebuild(self):
        catalog = Catalog(self.sources)
        old = catalog.snapshot()
        meta = self.sources[0] / "ro-crate-metadata.json"
        document = json.loads(meta.read_text(encoding="utf-8"))
        run = next(e for e in document["@graph"] if e["@id"] == PREFIX + "run:00")
        run["name"] = "Novo título sintético após a indexação"
        meta.write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
        changed = catalog.snapshot()
        self.assertTrue(changed["sources"][0]["changed"])
        self.assertEqual(changed["snapshot_id"], old["snapshot_id"])
        self.assertEqual(changed["sources"][0]["read_model"], old["sources"][0]["read_model"])
        fresh = catalog.rebuild()
        self.assertNotEqual(fresh["snapshot_id"], old["snapshot_id"])
        self.assertNotEqual(fresh["sources"][0]["snapshot_id"], old["sources"][0]["snapshot_id"])
        self.assertEqual(fresh["sources"][1]["snapshot_id"], old["sources"][1]["snapshot_id"])
        self.assertEqual(fresh["sources"][0]["read_model"]["runs"][0]["name"], run["name"])

    def test_loaded_counts_do_not_invent_source_eligible_selected_or_converted_totals(self):
        snapshot = Catalog(self.sources).snapshot()
        for source in snapshot["sources"]:
            coverage = source["coverage"]
            self.assertEqual(coverage["loaded"], 14)
            self.assertEqual(coverage["scope"], "NOT_DECLARED")
            for field in ("source", "eligible", "selected", "converted"):
                self.assertIsNone(coverage[field], field)
        missing = Catalog([self.root / "absent"]).snapshot()["sources"][0]
        self.assertEqual(missing["coverage"]["loaded"], 0)
        self.assertIsNone(missing["coverage"]["source"])
        self.assertIsNone(missing["read_model"])

    def test_unknown_time_isolated_runs_precision_and_incompatible_metrics_survive(self):
        model = Catalog(self.sources).snapshot()["sources"][0]["read_model"]
        runs = {r["id"]: r for r in model["runs"]}
        isolated = runs[PREFIX + "run:08"]
        self.assertIsNone(isolated["started_at"])
        self.assertEqual(isolated["timestamp_origin"], "UNKNOWN")
        self.assertEqual(isolated["inputs"] + isolated["outputs"] + isolated["derived_from"], [])
        self.assertEqual(runs[PREFIX + "run:09"]["timestamp_origin"], "OBSERVED")
        self.assertIsNone(runs[PREFIX + "run:10"]["started_at"])
        self.assertEqual(runs[PREFIX + "run:10"]["ended_at"], "2026-10-11T10:05:00-03:00")
        metrics = [runs[PREFIX + f"run:{n:02d}"]["metrics"][0] for n in (0, 1, 2)]
        self.assertEqual(len({m["property_id"] for m in metrics}), 1)
        self.assertEqual(len({(m["type"], m["unit"]) for m in metrics}), 3)
        self.assertEqual(metrics[0]["precision"], 3)
        exact = runs[PREFIX + "run:05"]["metrics"][0]
        self.assertEqual(exact["display_value"], "9007199254740993")
        missing = runs[PREFIX + "run:04"]["metrics"][0]
        self.assertIsNone(missing["value"])
        self.assertTrue(missing["missing_reason"])
        precision = runs[PREFIX + "run:12"]["metrics"][0]
        self.assertEqual(precision["display_precision"], "9007199254740993")

    def test_mentions_are_neutral_and_adversarial_text_never_loads_external_documents(self):
        before = [hashes(s) for s in self.sources]
        with patch("urllib.request.urlopen", side_effect=AssertionError("No external request allowed")):
            snapshot = Catalog(self.sources).snapshot()
        for source in snapshot["sources"]:
            model = source["read_model"]
            run = model["runs"][0]
            refs = {r["id"]: r for r in run["related_references"]}
            self.assertIn("<img", refs["javascript:window.__atlasP02QA=1"]["name"])
            self.assertIn("<script>", refs["javascript:window.__atlasP02QA=1"]["description"])
            self.assertEqual(refs["https://example.invalid/p02-reference.txt"]["availability"]["status"],
                             "EXTERNAL_UNRESOLVED")
            self.assertEqual(refs["data/output.csv"]["availability"]["status"], "MISSING")
            self.assertEqual(run["inputs"], ["data/input.csv"])
            self.assertEqual(run["outputs"], ["data/output.csv"])
            self.assertFalse(any(r["source"] == PREFIX + "note" or r["target"] == PREFIX + "note"
                                 for r in model["relations"]))
            self.assertIn({"source": PREFIX + "run:02", "target": PREFIX + "run:01", "kind": "derived_from"},
                          model["relations"])
        self.assertEqual([hashes(s) for s in self.sources], before)

    def test_snapshot_and_dossier_only_read_sources_and_do_not_expose_filesystem_paths(self):
        before = [hashes(s) for s in self.sources]
        catalog = Catalog(self.sources)
        observed = [catalog.snapshot(), catalog.dossier(), catalog.rebuild()]
        self.assertEqual([hashes(s) for s in self.sources], before)
        encoded = json.dumps(observed)
        self.assertNotIn(str(self.root), encoded)
        self.assertNotIn("file://", encoded.replace("file:///not-requested.txt", ""))


class P02HTTPTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog([FIXTURES / "source-a", FIXTURES / "source-b"])
        self.server = make_server(self.catalog, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.port = self.server.server_address[1]
        self.addCleanup(self.close)

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        result = response.status, dict(response.getheaders()), response.read()
        conn.close()
        return result

    def test_explicit_state_asset_is_served_with_csp_and_no_external_permission(self):
        status, headers, body = self.request("GET", "/parity02_p02_state.js")
        self.assertEqual(status, 200)
        self.assertIn(b"AtlasParity02State", body)
        self.assertIn("script-src 'self'", headers["Content-Security-Policy"])
        self.assertIn("connect-src 'self'", headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-inline", headers["Content-Security-Policy"])
        self.assertNotIn("Access-Control-Allow-Origin", headers)
        self.assertEqual(headers["Cache-Control"], "no-store")
        page = self.request("GET", "/")[2]
        self.assertIn(b'/parity02_p02_state.js', page)

    def test_state_asset_is_not_a_generic_filesystem_server(self):
        for path in ("/parity02_p02_unknown.js", "/static/parity02_p02_state.js", "/../catalog.py",
                     "/%2e%2e/catalog.py", "/packages/protocol/src/caderno_protocol/model.py"):
            with self.subTest(path=path):
                self.assertEqual(self.request("GET", path)[0], 404)

    def test_origin_host_and_allowlist_guards_still_apply_to_new_surface(self):
        for headers in ({"Host": "outside.invalid"}, {"Origin": "https://outside.invalid"},
                        {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.request("GET", "/parity02_p02_state.js", headers=headers)[0], 403)
        headers = {"Origin": f"http://127.0.0.1:{self.port}", "Content-Type": "application/json"}
        self.assertEqual(self.request("POST", "/api/reindex", '{"source":"/unrequested"}', headers)[0], 400)
        self.assertEqual(self.request("POST", "/api/reindex", "{}")[0], 403)
        self.assertEqual(self.request("POST", "/api/reindex", "{}", headers)[0], 200)
        response = json.loads(self.request("GET", "/api/catalog")[2])
        self.assertEqual(sum(s["coverage"]["loaded"] for s in response["sources"]), 28)


if __name__ == "__main__":
    unittest.main()
