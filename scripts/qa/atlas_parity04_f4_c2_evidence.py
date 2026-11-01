"""Emit SHA-bound, payload-free JSON evidence from actual JUnit and wheel runs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parents[2]
out = root / '.test-output/atlas-parity04-f4-c2'
out.mkdir(parents=True, exist_ok=True)
ref = lambda arg: subprocess.check_output(['git', 'rev-parse', arg], cwd=root, text=True).strip()
evidence = {'commit': ref('HEAD'), 'tree': ref('HEAD^{tree}'), 'parent': ref('HEAD^'), 'optimized': sys.flags.optimize, 'synthetic_only': True, 'g4': 'BLOCKED', 'hard_budget': 'HARD_BUDGET_UNVERIFIED', 'os_isolation': 'OS_ISOLATION_UNVERIFIED'}
receipt = root/'docs/missions/atlas-parity-04/f4-c2-reader'
manifest = receipt/'MANIFEST.sha256'
if manifest.exists():
    checked = 0
    for line in manifest.read_text(encoding='utf-8').splitlines():
        expected, relative = line.split('  ', 1)
        target = root/relative
        if not target.resolve().is_relative_to(root) or target.is_symlink() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            raise SystemExit('C2_MANIFEST_MISMATCH')
        checked += 1
    evidence['manifest'] = {'status': 'PASS', 'entries': checked, 'sha256': hashlib.sha256(manifest.read_bytes()).hexdigest(), 'self_excluded': True}
evidence['changed_paths'] = subprocess.check_output(['git', 'diff', '--name-only', '54bb16d350f7bc34fafb95438bd64a2397d58bf3', 'HEAD'], cwd=root, text=True).splitlines()
allowed = lambda p: p.startswith(('tools/atlas_legacy_presentation/', 'docs/missions/atlas-parity-04/f4-c2-reader/')) or p == '.github/workflows/atlas-parity04-f4-c2-reader.yml' or ('atlas_parity04_f4_c2_' in p and p.startswith(('scripts/qa/', 'tests/qa/', 'tests/fixtures/')))
if not all(allowed(p) for p in evidence['changed_paths']):
    raise SystemExit('C2_OWNERSHIP_VIOLATION')
evidence['ownership'] = 'PASS'
if (out/'junit.xml').exists():
    junit = ET.parse(out/'junit.xml')
    evidence['tests'] = [{'name': t.attrib['name'], 'class': t.attrib.get('classname'), 'status': 'FAIL' if t.find('failure') is not None or t.find('error') is not None else 'SKIP' if t.find('skipped') is not None else 'PASS'} for t in junit.findall('.//testcase')]
if (out/'independence.json').exists():
    evidence['independence'] = json.loads((out/'independence.json').read_text(encoding='utf-8'))
owned = ['tools/atlas_legacy_presentation', 'scripts/qa', 'tests/qa', 'tests/fixtures']
evidence['inputs'] = {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for folder in owned for p in (root/folder).iterdir() if p.is_file() and (folder.startswith('tools/') or 'atlas_parity04_f4_c2_' in p.name)}
(out/'evidence.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
print('C2_EVIDENCE_JSON='+json.dumps(evidence, separators=(',', ':')))
