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
if (out/'junit.xml').exists():
    junit = ET.parse(out/'junit.xml')
    evidence['tests'] = [{'name': t.attrib['name'], 'class': t.attrib.get('classname'), 'status': 'FAIL' if t.find('failure') is not None or t.find('error') is not None else 'SKIP' if t.find('skipped') is not None else 'PASS'} for t in junit.findall('.//testcase')]
if (out/'independence.json').exists():
    evidence['independence'] = json.loads((out/'independence.json').read_text(encoding='utf-8'))
owned = ['tools/atlas_legacy_presentation', 'scripts/qa', 'tests/qa', 'tests/fixtures']
evidence['inputs'] = {str(p.relative_to(root)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for folder in owned for p in (root/folder).iterdir() if p.is_file() and (folder.startswith('tools/') or 'atlas_parity04_f4_c2_' in p.name)}
(out/'evidence.json').write_text(json.dumps(evidence, indent=2)+'\n', encoding='utf-8')
print('C2_EVIDENCE_JSON='+json.dumps(evidence, separators=(',', ':')))
