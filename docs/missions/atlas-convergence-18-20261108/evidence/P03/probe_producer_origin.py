"""Synthetic producer import-origin counterproofs, no private source or install.

Usage: python -B probe_producer_origin.py --repo /path/to/Atlas
The process intentionally loads source-tree packages, not installed wheels.
This observes whether an external module ran BEFORE the rejection guard.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

def run_case(repo, root, case):
    code=root/"selected-code"
    selected=code/"src/r4/campaigns"
    selected.mkdir(parents=True)
    notebook=root/"synthetic-notebook"
    notebook.mkdir()
    marker=root/"unexpected-code-executed"
    sys_paths=[str(repo/"packages/protocol/src"),str(repo/"packages/atlas/src")]
    outsider = "from pathlib import Path\nPath("+repr(str(marker))+").write_text('UNEXPECTED_EXECUTION')\ndef project(root): return {'records': []}\n"
    if case=="module_symlink":
        for p in (selected.parent,selected):
            (p/"__init__.py").write_text("",encoding="utf-8")
        outside=root/"outside-module.py"
        outside.write_text(outsider,encoding="utf-8")
        try:
            (selected/"notebook_query_projection.py").symlink_to(outside)
        except OSError as exc:
            return {"case":case,"result":"SKIP","reason":"symlink unavailable: "+type(exc).__name__}
    elif case=="ambient_package_shadows_selected_namespace":
        (selected/"notebook_query_projection.py").write_text("def project(root): return {'records': []}\n",encoding="utf-8")
        ambient=root/"ambient-site-packages"
        external=ambient/"r4/campaigns"
        external.mkdir(parents=True)
        for p in (external.parent,external):
            (p/"__init__.py").write_text("",encoding="utf-8")
        (external/"notebook_query_projection.py").write_text(outsider,encoding="utf-8")
        sys_paths.append(str(ambient))
    else:
        raise ValueError(case)
    argv=[str(repo/"tools/export_native_notebook.py"),"--r4-code",str(code),"--notebook-root",str(notebook),"--output",str(root/"package")]
    boot="import sys,runpy;sys.path[:0]="+repr(sys_paths)+";sys.argv="+repr(argv)+";runpy.run_path(sys.argv[0],run_name='__main__')"
    p=subprocess.run([sys.executable,"-I","-B","-c",boot],env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1"),capture_output=True,text=True,timeout=20)
    ran=marker.exists()
    return {"case":case,"expected":"source outside selected root rejected before execution","returncode":p.returncode,"stdout":p.stdout,"stderr":p.stderr,"outside_module_executed":ran,"package_published":(root/"package").exists(),"result":"RED" if ran else "PASS" if p.returncode!=0 else "UNEXPECTED_ACCEPT"}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    opts=parser.parse_args()
    area=Path(__file__).resolve().parent
    (area/"tmp").mkdir(exist_ok=True)
    results=[]
    for case in ("module_symlink","ambient_package_shadows_selected_namespace"):
        with tempfile.TemporaryDirectory(prefix="origin-",dir=area/"tmp") as folder:
            results.append(run_case(opts.repo.resolve(),Path(folder),case))
    report={"command":"python -B probe_producer_origin.py --repo <Atlas checkout>","scope":"synthetic source-tree subprocess; no installed-wheel or hostile-host certification","cases":results}
    if opts.output:opts.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if all(x["result"]=="PASS" for x in results) else 1

if __name__=="__main__":raise SystemExit(main())
