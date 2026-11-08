"""Independent evidence verification; read-only product/P01, writes only P03."""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess

BASE = pathlib.Path(__file__).resolve().parents[2]
REPO = BASE / "repo"
AUTHOR = BASE / "agents/P01"
OUT = pathlib.Path(__file__).resolve().parent


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def read(name: str):
    return json.loads((AUTHOR / name).read_text())


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


checks = []


def check(label: str, okay: bool, **detail):
    checks.append({"id": label, "status": "PASS" if okay else "FAIL", **detail})


head = git("rev-parse", "HEAD").decode().strip()
tree = git("rev-parse", "HEAD^{tree}").decode().strip()
matrix = read("P01-MATRIX.json")
handoff = read("P01-HANDOFF.json")
check("baseline", head == matrix["baseline_sha"] and tree == matrix["baseline_tree"], head=head, tree=tree)
check("ownership", matrix["owner"] != "/root/p03_reader", author=matrix["owner"], reviewer="/root/p03_reader")
check("matrix_pin", digest((AUTHOR / "P01-MATRIX.json").read_bytes()) == "d26f129f6cb3d10a7306557db0abdd6333dc38e87763e3815ca71d2fa82c70f4")
check("handoff_pin", digest((AUTHOR / "P01-HANDOFF.json").read_bytes()) == "35137f1a25f5c679e3f670cd2fe4ad3a0743924bf967a310f8d082821af5728a")

artifacts = []
for name, info in handoff["artifacts"].items():
    data = (AUTHOR / name).read_bytes()
    artifacts.append({"path": str(AUTHOR / name), "sha256": digest(data), "bytes": len(data)})
    check("artifact:" + name, digest(data) == info["sha256"] and len(data) == info["bytes"])

sources = []
for row in read("P01-ALL-SOURCES.json"):
    ref = row.get("sha", row.get("ref"))
    path = row["path"]
    data = git("show", f"{ref}:{path}")
    blob = git("rev-parse", f"{ref}:{path}").decode().strip()
    expected = blob == row["blob"]
    if "sha256" in row:
        expected = expected and digest(data) == row["sha256"]
    if "bytes" in row:
        expected = expected and len(data) == row["bytes"]
    check("source:" + ref + ":" + path, expected)
    sources.append({"sha": ref, "path": path, "blob": blob, "sha256": digest(data), "bytes": len(data)})

coverage = {}
for name, count, key in [
    ("P01-JOURNEY-CROSSWALK.json", 28, "capability_id"),
    ("P01-EXAMPLE-CROSSWALK.json", 46, "id"),
    ("P01-C2-28-FILES.json", 28, "path"),
    ("C2-P03-35-TEST-CROSSWALK.json", 35, "id"),
    ("P01-PAR005-010.json", 6, "id"),
    ("P01-N01-24.json", 24, "id"),
    ("P01-ARC09-FROZEN.json", 5, "path"),
    ("K-NEGATIVES-PRESERVED.json", 68, "id"),
]:
    rows = read(name)
    actual = len(rows)
    unique = len({row[key] for row in rows})
    coverage[name] = {"count": actual, "unique": unique, "expected": count}
    check("coverage:" + name, actual == count and unique == count)

expected_prs = {6, 7, 9, 10, 12, 14, 15, 19, 21, 31}
check("matrix_prs", {row["pr"] for row in matrix["rows"]} == expected_prs and len(matrix["rows"]) == 10)
check("matrix_requirements", sum(len(row["requirements"]) for row in matrix["rows"]) == 38)
for row in matrix["rows"]:
    for req in row["requirements"]:
        check("requirement_shape:" + req["id"], all(req.get(k) for k in ("historical", "current", "tests", "counterevidence", "disposition")))

for row in read("P01-C2-28-FILES.json"):
    check("c2_blob:" + row["path"], git("rev-parse", row["sha"] + ":" + row["path"]).decode().strip() == row["blob"])

for row in read("P01-ARC09-FROZEN.json"):
    frozen = git("rev-parse", row["sha"] + ":" + row["path"]).decode().strip()
    terminal = git("rev-parse", "38f7b07602ed407e1fca54a5053861f7605dd9f5:" + row["path"]).decode().strip()
    check("arc09_terminal:" + row["path"], frozen == terminal == row["blob"])

parsed = {}
for file in ("C2-P03-35-TEST-CROSSWALK.json", "K-NEGATIVES-PRESERVED.json"):
    for row in read(file):
        path, klass, name = row["id"].split("::")
        key = (row["sha"], path)
        if key not in parsed:
            content = git("show", key[0] + ":" + key[1])
            methods = set()
            for node in ast.parse(content).body:
                if isinstance(node, ast.ClassDef):
                    methods.update((node.name, item.name) for item in node.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)))
            parsed[key] = methods
        blob = git("rev-parse", key[0] + ":" + key[1]).decode().strip()
        check("historical_method:" + row["id"], (klass, name) in parsed[key] and blob == row["blob"])

cases = json.loads(git("show", "2cd0e4686fb7456cb7c114bd778bb32a6bd9fad7:docs/contracts/atlas-parity-02/p01/examples/cases.json"))
if isinstance(cases, dict):
    cases = cases.get("cases", cases.get("examples"))
check("examples_exact_ids", {x["id"] for x in cases} == {x["id"] for x in read("P01-EXAMPLE-CROSSWALK.json")})
for row in read("P01-EXAMPLE-CROSSWALK.json"):
    original = next(x for x in cases if x["id"] == row["id"])
    same = all(row[k] == original[k] for k in ("file", "format", "expected_valid", "expected_errors"))
    check("example_original:" + row["id"], same)

result = {
    "reviewer": "/root/p03_reader",
    "subject": "/root/p01_contracts",
    "status": "PASS" if all(x["status"] == "PASS" for x in checks) else "FAIL",
    "head": head,
    "tree": tree,
    "read_only_repo_status": git("status", "--porcelain").decode(),
    "artifact_count": len(artifacts),
    "source_count": len(sources),
    "coverage": coverage,
    "artifacts": artifacts,
    "sources": sources,
    "checks": checks,
    "scope": "Hash/pin/count/AST identity validation. No historical execution claimed; semantic review recorded separately.",
}
(OUT / "P03-REVIEW-P01-EVIDENCE.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: result[k] for k in ("status", "head", "tree", "artifact_count", "source_count", "coverage")}))
print("checks", len(checks), "failures", [x for x in checks if x["status"] != "PASS"])
