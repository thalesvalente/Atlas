"""Build candidate wheels and prove SDK/viewer isolation without source imports.

No release/publication occurs. Inputs are copied into the supplied NEW workspace,
so build backends never modify the product source. Installs use local wheels only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def run(command, *, cwd, env):
    result = subprocess.run([str(x) for x in command], cwd=cwd, env=env, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError("Command failed: " + str(command[:4]) + "\n" + result.stdout[-4000:] + result.stderr[-4000:])
    return result.stdout


def python_in(venv):
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def hashes(root):
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--protocol-source", type=Path)
    parser.add_argument("--atlas-source", type=Path)
    parser.add_argument("--producer", type=Path)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    protocol = (args.protocol_source or repo / "packages/protocol").resolve()
    viewer = (args.atlas_source or repo / "packages/atlas").resolve()
    producer = (args.producer or repo / "examples/environmental/export.py").resolve()
    work = args.work.resolve()
    work.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ)
    for key in ("PYTHONPATH", "PYTHONHOME"):
        env.pop(key, None)
    env.update(PYTHONNOUSERSITE="1", PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_CONFIG_FILE=os.devnull)
    empty = work / "outside-source"
    empty.mkdir()
    wheels = work / "wheels"
    wheels.mkdir()
    source_hashes = {}
    for label, source in (("protocol", protocol), ("atlas", viewer)):
        copy = work / "build-input" / label
        shutil.copytree(source, copy, ignore=shutil.ignore_patterns("build", "dist", "*.egg-info", "__pycache__"))
        source_hashes[label] = hashes(copy)
        run([sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", wheels, copy], cwd=empty, env=env)
    protocol_wheel = next(wheels.glob("caderno_protocol-*.whl"))
    viewer_wheel = next(wheels.glob("atlas_viewer-*.whl"))
    sdk_env, viewer_env = work / "sdk-env", work / "viewer-env"
    for venv in (sdk_env, viewer_env):
        run([sys.executable, "-m", "venv", venv], cwd=empty, env=env)
    sdk_python, viewer_python = python_in(sdk_env), python_in(viewer_env)
    run([sdk_python, "-m", "pip", "install", "--no-index", "--no-deps", protocol_wheel], cwd=empty, env=env)
    run([viewer_python, "-m", "pip", "install", "--no-index", "--no-deps", protocol_wheel, viewer_wheel], cwd=empty, env=env)
    sdk_check = json.loads(run([sdk_python, "-I", "-c", "import importlib.util,json,caderno_protocol; from pathlib import Path; import sys; print(json.dumps({'sdk_imported': True, 'viewer_absent': importlib.util.find_spec('atlas_viewer') is None, 'r4_absent': importlib.util.find_spec('r4') is None, 'installed_module': Path(caderno_protocol.__file__).is_relative_to(Path(sys.prefix))}))"], cwd=empty, env=env))
    if not all(sdk_check.values()):
        raise RuntimeError("SDK isolation failed: " + str(sdk_check))
    viewer_check = json.loads(run([viewer_python, "-I", "-c", "import importlib.util,json,atlas_viewer,caderno_protocol; from pathlib import Path; import sys; print(json.dumps({'r4_absent': importlib.util.find_spec('r4') is None, 'installed_viewer': Path(atlas_viewer.__file__).is_relative_to(Path(sys.prefix)), 'installed_sdk': Path(caderno_protocol.__file__).is_relative_to(Path(sys.prefix))}))"], cwd=empty, env=env))
    if not all(viewer_check.values()):
        raise RuntimeError("Viewer isolation failed: " + str(viewer_check))
    isolated = ["-I"] + (["-O"] if sys.flags.optimize else [])
    source = work / "environmental-crate"
    run([sdk_python, *isolated, producer, source], cwd=empty, env=env)
    before = hashes(source)
    sdk_result = json.loads(run([sdk_python, *isolated, "-m", "caderno_protocol", source], cwd=empty, env=env))
    catalog = json.loads(run([viewer_python, *isolated, "-m", "atlas_viewer", "inspect", source], cwd=empty, env=env))
    dossier = json.loads(run([viewer_python, *isolated, "-m", "atlas_viewer", "dossier", "--source", source], cwd=empty, env=env))
    reindex = json.loads(run([viewer_python, *isolated, "-c", "from atlas_viewer.catalog import Catalog; import json,sys; c=Catalog([sys.argv[1]]); a=c.snapshot(); b=c.rebuild(); print(json.dumps({'rebuild_same_records': a['sources'][0]['read_model'] == b['sources'][0]['read_model'], 'generation_advanced': b['generation'] == a['generation'] + 1}))", source], cwd=empty, env=env))
    count = sum(len(x["read_model"]["runs"]) for x in catalog["sources"] if x.get("read_model"))
    if count != 4 or not all(reindex.values()) or hashes(source) != before:
        raise RuntimeError("Installed product record/rebuild/immutability verification failed")
    if dossier["authority"] != "DERIVED_REBUILDABLE_NOT_SCIENTIFIC_APPROVAL":
        raise RuntimeError("Dossier silently changed authority")
    report = {
        "status": "PASS_SCOPED", "scope": "installed-wheels-isolation-cli-rebuild-immutability",
        "python": sys.version.split()[0], "optimization": sys.flags.optimize, "sdk": sdk_check, "viewer": viewer_check,
        "run_count": count, "source_bytes_unchanged": True, "reindex": reindex,
        "wheel_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(wheels.glob("*.whl"))},
        "source_file_sha256": source_hashes,
        "browser": "NOT_RUN_BY_THIS_SCRIPT", "windows": "NOT_RUN" if os.name != "nt" else "CURRENT_HOST",
        "human_protocol_acceptance": "PENDING", "canonical_promotion": "NOT_AUTHORIZED",
    }
    (work / "clean-install-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k != "source_file_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
