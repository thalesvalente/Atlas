"""Feature 005 may only add the three fixed assets to the accepted server bytes."""
from pathlib import Path
import importlib.util
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('triage_scope_audit', ROOT / 'scripts/qa/speckit_audit.py')
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)
NAME = 'packages/atlas/src/atlas_viewer/server.py'


class TriageStaticScopeTests(unittest.TestCase):
    def test_successor_recovers_exact_accepted_server_and_changes_no_handlers(self):
        content = (ROOT / NAME).read_bytes()
        self.assertTrue(AUDIT.exact_triage_static_successor(NAME, content))
        # Recover the accepted bytes without requiring historical objects in a
        # shallow CI checkout. The historical blob pin itself is unchanged.
        baseline = content
        for asset in ('native_triage_model', 'native_retention', 'native_triage_ui'):
            line = (f'          "/{asset}.js": ("{asset}.js", '
                    '"text/javascript; charset=utf-8"),\n').encode('utf-8')
            self.assertEqual(baseline.count(line), 1)
            baseline = baseline.replace(line, b'', 1)
        self.assertEqual(AUDIT.git_blob_id(baseline), 'ccfbbf7e1f10e5f8a5939639c77adf8cb7c8dd43')
        self.assertTrue(AUDIT.exact_original_bridge(NAME, baseline))
        self.assertFalse(AUDIT.exact_triage_static_successor(NAME, baseline))

    def test_arbitrary_routes_paths_duplicates_or_server_mutations_are_rejected(self):
        content = (ROOT / NAME).read_bytes()
        for mutated in (content + b'\n# unexpected runtime mutation\n',
                        content.replace(b'/native_retention.js', b'/arbitrary/path.js'),
                        content.replace(b'connect-src \'self\'', b'connect-src *'),
                        content.replace(b'def make_server(', b'def changed_server('),
                        content.replace(b'"native_triage_ui.js"', b'"../../private"'),
                        content.replace(b'"native_retention.js", "text/javascript', b'"native_retention.js", "text/html')):
            with self.subTest(mutation=mutated[-40:]):
                self.assertFalse(AUDIT.exact_triage_static_successor(NAME, mutated))
        line = b'          "/native_retention.js": ("native_retention.js", "text/javascript; charset=utf-8"),\n'
        self.assertFalse(AUDIT.exact_triage_static_successor(NAME, content + line))
        self.assertFalse(AUDIT.exact_triage_static_successor('packages/protocol/reader.py', content))


if __name__ == '__main__':
    unittest.main()
