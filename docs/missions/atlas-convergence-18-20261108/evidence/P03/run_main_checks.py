"""P03 source-tree verification; synthetic only, no package installation."""
from __future__ import annotations
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

AREA = Path(__file__).resolve().parent
ROOT = AREA.parents[1] / "repo"
sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
(AREA / "tmp").mkdir(exist_ok=True)
tempfile.tempdir = str(AREA / "tmp")
sys.path[:0] = [str(ROOT / "packages/protocol/src"), str(ROOT / "packages/atlas/src"), str(ROOT / "scripts/qa")]
BASELINE = "8f8fe01c3041361aa2607194d66af6a640d834ad"

def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()

class RecordingResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = []
    def addSuccess(self, test):
        self.records.append({"id": test.id(), "result": "PASS"})
        super().addSuccess(test)
    def addSkip(self, test, reason):
        self.records.append({"id": test.id(), "result": "SKIP", "reason": reason})
        super().addSkip(test, reason)
    def addError(self, test, err):
        self.records.append({"id": test.id(), "result": "ERROR", "error": self._exc_info_to_string(err,test)})
        super().addError(test, err)
    def addFailure(self, test, err):
        self.records.append({"id": test.id(), "result": "FAIL", "error": self._exc_info_to_string(err,test)})
        super().addFailure(test, err)

def main():
    if git("rev-parse", "HEAD") != BASELINE:
        raise RuntimeError("BASELINE_DRIFT")
    files = [
        "tests/viewer/test_native_notebook.py",
        "tests/viewer/test_native_notebook_review.py",
        "tests/viewer/test_native_notebook_parity.py",
        "tests/viewer/test_native_notebook_http.py",
        "tests/qa/test_architecture_boundaries.py",
    ]
    suites=[]
    sources=[]
    for path in files:
        spec=importlib.util.spec_from_file_location(Path(path).stem, ROOT / path)
        mod=importlib.util.module_from_spec(spec)
        sys.modules[spec.name]=mod
        spec.loader.exec_module(mod)
        suites.append(unittest.defaultTestLoader.loadTestsFromModule(mod))
        sources.append({"path":path,"blob":git("rev-parse",f"{BASELINE}:{path}"),"sha256":hashlib.sha256((ROOT/path).read_bytes()).hexdigest()})
    log=io.StringIO()
    started=time.monotonic()
    result=unittest.TextTestRunner(stream=log,verbosity=2,resultclass=RecordingResult).run(unittest.TestSuite(suites))
    label="optimized" if sys.flags.optimize else "normal"
    (AREA/f"main-source-tests-{label}.log").write_text(log.getvalue())
    record={"baseline_sha":BASELINE,"tree":git("rev-parse",BASELINE+"^{tree}"),"environment":"Chat Linux, source-tree Python; no installed wheel claim","python":sys.version,"optimization":sys.flags.optimize,"run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),"skipped":len(result.skipped),"duration_seconds":round(time.monotonic()-started,3),"sources":sources,"tests":result.records,"log":f"main-source-tests-{label}.log","source_mutation":"synthetic fixtures only","private_source_access":False,"head_unchanged":git("rev-parse","HEAD")==BASELINE,"git_status_after":git("status","--porcelain=v1","--untracked-files=all")}
    (AREA/f"main-source-tests-{label}.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in record.items() if k not in ["sources","tests"]},ensure_ascii=False,indent=2))
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    raise SystemExit(main())
