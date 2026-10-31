"""Synthetic-only wheel independence proof; never loads the external reader."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--output', type=Path, required=True)
    args = cli.parse_args()
    repo = Path(__file__).resolve().parents[2]
    records = []
    result = {'status': 'FAIL', 'synthetic_only': True, 'python': sys.version, 'optimized': sys.flags.optimize, 'platform': platform.platform(), 'commands': records, 'checks': {}}
    environment = dict(os.environ)
    environment.pop('PYTHONPATH', None)
    environment.pop('PYTHONHOME', None)
    environment['PIP_NO_INDEX'] = '1'
    environment['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'

    def run(command, cwd):
        done = subprocess.run([str(x) for x in command], cwd=cwd, env=environment, capture_output=True, timeout=180)
        records.append({'argv': [str(x) for x in command], 'returncode': done.returncode, 'stdout_bytes': len(done.stdout), 'stderr_bytes': len(done.stderr), 'stdout_sha256': hashlib.sha256(done.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(done.stderr).hexdigest()})
        if done.returncode:
            raise RuntimeError('Subprocess failed: '+repr(command)+'\n'+done.stdout.decode('utf-8', 'replace')+done.stderr.decode('utf-8', 'replace'))
        return done.stdout

    flags = ['-I', '-X', 'utf8'] + (['-O'] if sys.flags.optimize else [])
    try:
        result['commit'] = run(['git', 'rev-parse', 'HEAD'], repo).decode().strip()
        result['tree'] = run(['git', 'rev-parse', 'HEAD^{tree}'], repo).decode().strip()
        result['parents'] = run(['git', 'show', '-s', '--format=%P', 'HEAD'], repo).decode().strip().split()
        with tempfile.TemporaryDirectory(prefix='atlas-parity04-f4-c2-wheels-') as tmp:
            isolated = Path(tmp)
            inputs = isolated / 'build-inputs'
            inputs.mkdir()
            wheels = isolated / 'wheels'
            wheels.mkdir()
            for package in ('protocol', 'atlas'):
                project = inputs / package
                shutil.copytree(repo/'packages'/package, project, ignore=lambda p, ns: [n for n in ns if n in {'build', 'dist', '__pycache__'} or n.endswith('.egg-info')])
                run([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--no-build-isolation', '--wheel-dir', wheels, project], isolated)
            artifacts = sorted(wheels.glob('*.whl'))
            if len(artifacts) != 2:
                raise RuntimeError('Expected exactly two independently built public wheels')
            result['wheels'] = []
            for wheel in artifacts:
                with zipfile.ZipFile(wheel) as archive:
                    names = archive.namelist()
                if any('atlas_legacy_presentation' in name or name.startswith(('tools/', 'r4/')) for name in names):
                    raise RuntimeError('External tool or private producer entered a wheel')
                result['wheels'].append({'name': wheel.name, 'sha256': hashlib.sha256(wheel.read_bytes()).hexdigest(), 'external_tool_present': False, 'entries': len(names)})
            sample = isolated / 'invented-environmental-source'
            shutil.copytree(repo/'examples'/'environmental'/'sample', sample)
            public_wheels = {p.name.split('-')[0]: p for p in artifacts}
            for label, install in (('sdk-only', [public_wheels['caderno_protocol']]), ('viewer-and-sdk', artifacts)):
                target = isolated / label
                venv.EnvBuilder(with_pip=True, clear=False).create(target)
                python = target / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
                work = isolated / (label+'-work')
                work.mkdir()
                run([python, '-m', 'pip', 'install', '--no-index', '--no-deps', '--find-links', wheels, *install], work)
                probe = "import importlib.util;p=importlib.util.find_spec('atlas_legacy_presentation');t=importlib.util.find_spec('tools');r=importlib.util.find_spec('r4');raise SystemExit(0 if p is None and t is None and r is None else 1)"
                run([python, *flags, '-c', probe], work)
                run([python, *flags, '-m', 'caderno_protocol', sample], work)
                if label == 'sdk-only':
                    run([python, *flags, '-c', "import importlib.util;raise SystemExit(0 if importlib.util.find_spec('atlas_viewer') is None else 1)"], work)
                else:
                    snapshot = json.loads(run([python, *flags, '-m', 'atlas_viewer', 'inspect', sample], work))
                    if not snapshot.get('sources') or any(s['status'] != 'READY' for s in snapshot['sources']):
                        raise RuntimeError('Installed viewer did not open the independent synthetic source')
                result['checks'][label] = 'PASS'
            result['checks']['external_tool_excluded_from_wheels'] = 'PASS'
            result['checks']['outside_checkout_runtime_without_tools_or_r4'] = 'PASS'
            result['status'] = 'PASS'
    except Exception as exc:
        result['error'] = str(exc)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
