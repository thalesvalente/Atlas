"""Native View boundary probes: synthetic payloads, no graph-rendering claim."""
import json
from pathlib import Path
import runpy
import sys
import tempfile
import time

AREA=Path(__file__).resolve().parent
REPO=AREA.parents[1]/"repo"
sys.path[:0]=[str(REPO/"packages/protocol/src"),str(REPO/"packages/atlas/src")]
from atlas_viewer.native_notebook import read_source, validate_entries, NativeViewError
from caderno_protocol import load_package
exporter=runpy.run_path(str(REPO/"tools/export_native_notebook.py"))
checks=[]
with tempfile.TemporaryDirectory(prefix="p02-limits-",dir=AREA) as directory:
    for count in (10000,10001):
        data={"records":[],"lineage_graph":{"nodes":[{"key":f"synthetic-{i}","label":f"Synthetic node {i}","parent_key":None} for i in range(count)],"edges":[]}}
        output=Path(directory)/str(count)
        if count==10001:
            try:
                exporter["export"](data,output)
                raise AssertionError("Exporter accepted too many nodes")
            except NativeViewError as exc:
                assert str(exc)=="NATIVE_NODE_LIMIT" and not output.exists()
                checks.append({"nodes":count,"result":"REJECTED_ATOMICALLY_BEFORE_PUBLICATION","error":str(exc),"output_exists":output.exists(),"stage":"exporter_shared_native_validator"})
            continue
        exporter["export"](data,output)
        start=time.perf_counter();result,raw=read_source(output,"synthetic-source");elapsed=time.perf_counter()-start
        valid=load_package(output).report.valid
        expected="READY" if count==10000 else "INVALID"
        if result["status"]!=expected:raise AssertionError(result)
        if count==10000:
            assert json.loads(raw)==data
            assert len([e for e in result["entries"] if e["kind"]=="node"])==10000
        else:
            assert result["errors"]==["NATIVE_NODE_LIMIT"] and not result["entries"]
        checks.append({"nodes":count,"protocol_valid":valid,"native_status":result["status"],"errors":result.get("errors",[]),"entries":len(result["entries"]),"seconds":elapsed,"rendering":"NOT_RUN_IN_THIS_PROBE"})
try:
    validate_entries([None]*100001)
    raise AssertionError("Oversized entry list was accepted")
except NativeViewError as exc:
    assert str(exc)=="NATIVE_ENTRY_LIMIT"
checks.append({"entries":100001,"result":"REJECTED_ATOMICALLY","error":"NATIVE_ENTRY_LIMIT"})
result={"status":"PASS","baseline_sha":"8f8fe01c3041361aa2607194d66af6a640d834ad","scope":"native reader synthetic quotas; no browser or private-corpus claim","checks":checks}
(AREA/"native-limits-probe.json").write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps(result,ensure_ascii=False))
