"""Build with the product pin and qualify installed P03 wheel bytes in isolation.

The caller supplies pinned test-only build tools. This script builds copies,
uses no package index, creates two new virtual environments outside the checkout,
and compares every packaged source module/resource with the exact Git blob.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tomllib
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run(command: list, *, cwd: Path, env: dict, binary: bool = False):
    result = subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                            capture_output=True, text=not binary,
                            **({} if binary else {"encoding": "utf-8"}))
    if result.returncode:
        stdout = result.stdout.decode("utf-8", errors="replace") if binary else result.stdout
        stderr = result.stderr.decode("utf-8", errors="replace") if binary else result.stderr
        raise RuntimeError("Command failed: " + str(command[:4]) + "\n" + stdout[-5000:] + stderr[-5000:])
    return result.stdout


def git(*args: str, binary: bool = False):
    value = run(["git", *args], cwd=ROOT, env=dict(os.environ), binary=binary)
    return value if binary else value.strip()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def python_in(venv: Path) -> Path:
    return venv / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def source_files(prefix: str) -> dict[str, bytes]:
    paths = git("ls-files", "-z", "--", prefix).split("\0")
    result = {}
    for path in filter(None, paths):
        raw = (ROOT / path).read_bytes()
        require(raw == git("show", "HEAD:" + path, binary=True), "Working package file differs from Git HEAD: " + path)
        result[path] = raw
    return result


def bind_execution(paths: list[str], head: str) -> dict:
    files = []
    for path in sorted(set(paths)):
        result = subprocess.run(["git", "show", "HEAD:" + path], cwd=ROOT, capture_output=True)
        raw = (ROOT / path).read_bytes()
        files.append({"path": path, "sha256": digest(raw),
                      "matches_head": result.returncode == 0 and result.stdout == raw})
    tracked_clean = subprocess.run(["git", "diff", "--quiet", "HEAD", "--"], cwd=ROOT).returncode == 0
    bound = tracked_clean and all(file["matches_head"] for file in files)
    return {"attribution": "GIT_COMMIT" if bound else "PRECOMMIT_UNBOUND",
            "tested_sha": head if bound else None, "tracked_worktree_clean": tracked_clean, "files": files}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True, help="NEW directory outside this checkout")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    work = args.work.resolve()
    receipt = {"status": "FAIL", "scope": "P03_PINNED_BUILD_AND_INSTALLED_WHEELS",
               "observed_head_sha": git("rev-parse", "HEAD"), "head_tree": git("rev-parse", "HEAD^{tree}"),
               "timestamp_utc": datetime.now(timezone.utc).isoformat(),
               "python": platform.python_version(), "platform": platform.platform(),
               "optimization": sys.flags.optimize, "skips": 0, "visible_in_main_app": False,
               "gate_script_sha256": digest(Path(__file__).read_bytes()), "wheel_files": []}
    try:
        require(not work.is_relative_to(ROOT) and not ROOT.is_relative_to(work), "Build/install workspace must be outside the checkout")
        require(not work.exists(), "Build/install workspace already exists")
        tools = {name: importlib.metadata.version(name) for name in ("setuptools", "build", "wheel")}
        require(tools["setuptools"] == "80.9.0", "Product build pin requires setuptools==80.9.0")
        receipt["build_tools"] = tools
        work.mkdir(parents=True)
        outside = work / "outside-checkout"
        outside.mkdir()
        wheel_dir = work / "wheels"
        wheel_dir.mkdir()
        env = dict(os.environ)
        for key in ("PYTHONPATH", "PYTHONHOME"):
            env.pop(key, None)
        env.update(PYTHONNOUSERSITE="1", PYTHONUTF8="1", PIP_NO_INDEX="1",
                   PIP_DISABLE_PIP_VERSION_CHECK="1", PIP_CONFIG_FILE=os.devnull)
        originals = {}
        expected_wheels = {}
        for label, module in (("protocol", "caderno_protocol"), ("atlas", "atlas_viewer")):
            prefix = f"packages/{label}/"
            files = source_files(prefix)
            require(bool(files), "No package source collected: " + label)
            project = tomllib.loads(files[prefix + "pyproject.toml"].decode("utf-8"))
            require(project["build-system"]["requires"] == ["setuptools==80.9.0"], "Product build requirements changed")
            originals.update({path: digest(raw) for path, raw in files.items()})
            copied = work / "build-input" / label
            for path, raw in files.items():
                target = copied / path[len(prefix):]
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(raw)
            run([sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", wheel_dir, copied],
                cwd=outside, env=env)
            wheels = sorted(wheel_dir.glob(module + "-*.whl"))
            require(len(wheels) == 1, "Expected exactly one wheel for " + module)
            wheel = wheels[0]
            expected = {path[len(prefix + "src/"):]: (path, raw) for path, raw in files.items()
                        if path.startswith(prefix + "src/")}
            with zipfile.ZipFile(wheel) as archive:
                members = archive.namelist()
                require(len(members) == len(set(members)), "Duplicate wheel archive entries")
                actual = {name for name in members if name.startswith(module + "/") and not name.endswith("/")}
                require(actual == set(expected), "Wheel source/resource inventory differs from Git: " + module)
                for name, (path, raw) in sorted(expected.items()):
                    packaged = archive.read(name)
                    blob = git("rev-parse", "HEAD:" + path)
                    require(packaged == raw and git_blob(packaged) == blob, "Wheel content differs from Git blob: " + path)
                    receipt["wheel_files"].append({"source_path": path, "wheel": wheel.name, "wheel_path": name,
                                                   "git_blob": blob, "sha256": digest(packaged), "bytes_equal": True})
            expected_wheels[module] = wheel
        receipt["wheels"] = {path.name: digest(path.read_bytes()) for path in expected_wheels.values()}
        sdk_env, viewer_env = work / "sdk-env", work / "viewer-env"
        for venv in (sdk_env, viewer_env):
            run([sys.executable, "-m", "venv", venv], cwd=outside, env=env)
        sdk_python, viewer_python = python_in(sdk_env), python_in(viewer_env)
        run([sdk_python, "-m", "pip", "install", "--no-index", "--no-deps", expected_wheels["caderno_protocol"]], cwd=outside, env=env)
        run([viewer_python, "-m", "pip", "install", "--no-index", "--no-deps", *expected_wheels.values()], cwd=outside, env=env)
        isolated = ["-I", "-X", "utf8"] + (["-O"] if sys.flags.optimize else [])
        sdk_code = """import importlib.util,json,sys
from pathlib import Path
import caderno_protocol
print(json.dumps({'sdk_installed':Path(caderno_protocol.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'viewer_absent':importlib.util.find_spec('atlas_viewer') is None,'r4_absent':importlib.util.find_spec('r4') is None,'checkout_absent_from_sys_path':not any(Path(p).resolve().is_relative_to(Path(sys.argv[1]).resolve()) for p in sys.path if p),'isolated':sys.flags.isolated == 1,'optimization':sys.flags.optimize}))
"""
        sdk_result = json.loads(run([sdk_python, *isolated, "-c", sdk_code, ROOT], cwd=outside, env=env))
        require(all(value is True for key, value in sdk_result.items() if key != "optimization"), "SDK isolation check failed")
        require(sdk_result["optimization"] == sys.flags.optimize, "SDK optimization flag differs")
        fixture = outside / "artifact-read-model.json"
        fixture.write_bytes((ROOT / "tests/fixtures/atlas_parity02/p03/artifact-read-model.json").read_bytes())
        fixture_before = digest(fixture.read_bytes())
        viewer_code = """import hashlib,importlib.resources,importlib.util,json,sys
from pathlib import Path
import atlas_viewer,caderno_protocol
from atlas_viewer.parity02_p03_metadata import project_metadata
model=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
before=json.dumps(model,sort_keys=True)
view=project_metadata(model,'synthetic-source-A')
item=next(item for item in view['items'] if item['identity']['id']=='report.pdf')
checks={'viewer_installed':Path(atlas_viewer.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'sdk_installed':Path(caderno_protocol.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()),'r4_absent':importlib.util.find_spec('r4') is None,'checkout_absent_from_sys_path':not any(Path(p).resolve().is_relative_to(Path(sys.argv[2]).resolve()) for p in sys.path if p),'isolated':sys.flags.isolated == 1,'model_unchanged':json.dumps(model,sort_keys=True)==before,'file_not_product':item['kind']=='artifact' and item['types']==['File'] and 'semantic_kind' not in item,'mentions_neutral':item['relations']==[] and all(link['kind']=='mention' for link in item['mentions']) and bool(item['mentions'])}
names=['parity02_p03_table.js','parity02_p03_table.css','parity02_p03_artifacts.js','parity02_p03_artifacts.css']
assets={name:hashlib.sha256(importlib.resources.files('atlas_viewer').joinpath('static',name).read_bytes()).hexdigest() for name in names}
print(json.dumps({'checks':checks,'assets':assets,'item_count':len(view['items']),'optimization':sys.flags.optimize}))
"""
        viewer_result = json.loads(run([viewer_python, *isolated, "-c", viewer_code, fixture, ROOT], cwd=outside, env=env))
        require(all(value is True for value in viewer_result["checks"].values()), "Viewer isolation/semantic check failed")
        require(viewer_result["optimization"] == sys.flags.optimize, "Viewer optimization flag differs")
        require(digest(fixture.read_bytes()) == fixture_before, "Installed smoke changed its fixture")
        for name, installed_hash in viewer_result["assets"].items():
            require(installed_hash == originals["packages/atlas/src/atlas_viewer/static/" + name], "Installed asset bytes differ: " + name)
        after = {path: digest((ROOT / path).read_bytes()) for path in originals}
        require(after == originals, "Build/install modified product source")
        binding = bind_execution([*originals, "scripts/qa/atlas_parity03_p03_build.py",
                                  "tests/fixtures/atlas_parity02/p03/artifact-read-model.json"], receipt["observed_head_sha"])
        receipt.update(status="PASS", sdk=sdk_result, viewer=viewer_result,
                       tested_sha=binding["tested_sha"], attribution=binding["attribution"], execution_binding=binding,
                       source_bytes_unchanged=True, fixture_bytes_unchanged=True,
                       package_source_sha256=originals, outside_checkout=True,
                       installs_offline=True, build_isolation=False,
                       network="PIP_NO_INDEX=1; --no-isolation build; --no-index --no-deps local wheel installs",
                       main_application_composition="NOT_PERFORMED")
    except Exception as error:
        receipt["error"] = f"{type(error).__name__}: {error}"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: receipt.get(key) for key in ("status", "scope", "tested_sha", "attribution", "optimization", "skips")}, indent=2))
    if receipt["status"] != "PASS":
        print(receipt.get("error", "Build/install qualification failed"), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
