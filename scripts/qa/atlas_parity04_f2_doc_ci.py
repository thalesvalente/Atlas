"""Strict supplementary F1/F2 documentation successor; no architectural authority."""
from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import time
import types
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
C4_SHA = "72d9b94e613a57c82a5afd309796f44b271e2185"
C4_TREE = "0a622663ca40232d6143659f82cfe9ce43702e90"
AP04_SHA = "47c94d27aeb7717eebb30804f01cd2cd33507c8a"
AP04_TREE = "a02e8b6e6d82a743de4a31e9835c3d18e29d8947"
F1_SHA = "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7"
F2_SHA = "04373bb910db2e6215cc8bc4212093b649e48456"
F2_TREE = "611306f28557f5d9e27db49108880004399f5768"
HISTORICAL_GUARD = "scripts/qa/atlas_parity04_doc_ci.py"
HISTORICAL_GUARD_BLOB = "b516eabf506f4f15989767dc53e02aceec26bc5e"
HISTORICAL_GUARD_SHA256 = "1e6a18c426c4ab3a7b994c027b251b0b282db73467fbf610219fec3857976d7b"
OVERLAY_ROOT = "docs/missions/atlas-parity-04/f2-doc-ci-repair"
OVERLAY_PATH = OVERLAY_ROOT + "/OVERLAY.json"
MANIFEST_PATH = OVERLAY_ROOT + "/MANIFEST.sha256"
OWNERSHIP_PATH = OVERLAY_ROOT + "/REPAIR-OWNERSHIP.json"
GUARD_PATH = "scripts/qa/atlas_parity04_f2_doc_ci.py"
TEST_PATH = "tests/qa/test_atlas_parity04_f2_doc_ci.py"
FROZEN_EPOCHS = [
  [
    "c25d37998dac7174067a2819391f3af1625f96dc",
    "e6eacdd02a329f88bc0dd656523b84a8fec9217e",
    "72d9b94e613a57c82a5afd309796f44b271e2185"
  ],
  [
    "54ffea9e8fe2ed5cde071a8ec52fbcbff857df60",
    "417d29e1cf051644ce6e1edead7fed3315147286",
    "c25d37998dac7174067a2819391f3af1625f96dc"
  ],
  [
    "47c94d27aeb7717eebb30804f01cd2cd33507c8a",
    "a02e8b6e6d82a743de4a31e9835c3d18e29d8947",
    "54ffea9e8fe2ed5cde071a8ec52fbcbff857df60"
  ],
  [
    "e140d973fd4cbc4547046f25fd620166662c5004",
    "e1d6d8cca7f66aaaff0e13de293d43c04ad0e6ed",
    "47c94d27aeb7717eebb30804f01cd2cd33507c8a"
  ],
  [
    "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "e0626cd274948a9303774593e20ca05fc1d32d62",
    "e140d973fd4cbc4547046f25fd620166662c5004"
  ],
  [
    "bc2e10e9a783227294daa4100ccaeb384d0dddd0",
    "37f3c90e4d9d4e326eb128614c74e759ec892705",
    "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7"
  ],
  [
    "7caffc69dc17b2f0d4ec0906bb1b4a2bba0abc67",
    "045683c64bf2bc5111a80aaa1894d727533475e8",
    "bc2e10e9a783227294daa4100ccaeb384d0dddd0"
  ],
  [
    "c3ea1e82938fd61cc5a22fee973352715a5bb527",
    "986a1ddaf3ceae4c6e0fcb03c7bd1dfd63ef378c",
    "7caffc69dc17b2f0d4ec0906bb1b4a2bba0abc67"
  ],
  [
    "04373bb910db2e6215cc8bc4212093b649e48456",
    "611306f28557f5d9e27db49108880004399f5768",
    "c3ea1e82938fd61cc5a22fee973352715a5bb527"
  ]
]
FROZEN_DOCUMENTS = [
  {
    "path": "docs/missions/atlas-parity-04/f1-legacy-inventory/F1-LOCAL-MISSION.md",
    "source_sha": "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "blob": "57294f1ef604b3a73b62ffb7f7bbb6e2a8dc8654",
    "sha256": "de3c32b4dd874f83261de0a2dfc23cdf47491903291e4d6c5a29032def3aa611",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f1-legacy-inventory/README.md",
    "source_sha": "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "blob": "0b388a02875554df7a8a8e8be5b468b06f5be529",
    "sha256": "361a30e33bc63c5fd4fb172edb9834cd4a55b6bbec27a8a5cc5bf6d2d13beef9",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f1-legacy-inventory/RESULT-REVIEW.sanitized.md",
    "source_sha": "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "blob": "078ce6364fc88bb2c09d37282426938482387c7a",
    "sha256": "39741ae62b24c03fd4f24035adf79b9063daa4c4c1e36c1cf4be6c408d0eedb9",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f1-legacy-inventory/SANITIZED-HANDOFF.json",
    "source_sha": "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "blob": "8b16eb60e2554a337fcaf950df13fa8300e46e87",
    "sha256": "12a3df17391c3a981e87aed9ed80e7ba66a4e549ffb27564e870ac8432d3a8b4",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f1-legacy-inventory/SANITIZED-HANDOFF.md",
    "source_sha": "a237f446e54927eeeda8ed5e8e9daa83ee09dcb7",
    "blob": "bb4840cc44f60a8e1a73d0e3a3b727ad7dd5ac9c",
    "sha256": "08f843d3d6f040a26ba837c3aa6d7a4a0641297600a38cc14f4467bc5950315c",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/ADR-0003-v0.2-CANDIDATE.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "e1283af1ac285937bf02bdf163ce3cf2d00f3081",
    "sha256": "a5c67b508ff94b9f261dcf899cc405ba0f92202af142c79d22a787244a627729",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/ARCHITECTURE-OPTIONS.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "0d1c651a9f521b6d6511732aa24427d932019f1c",
    "sha256": "02a11b8debfd664b2502f80023e051f80a63cae7e2e3f14a4ffee97e55ae9bc5",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/DECISION-REQUEST.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "13882234b324f9038fdd01ec7d6d34f4b3d0e1d8",
    "sha256": "3739fa11087af9a91edd7825484d941debb948f808f137fca36894caf6d6bc44",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/EPHEMERAL-PRESENTATION-CONTRACT.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "25d79a11171c157bd3c7e0f98d1449a78237fd9c",
    "sha256": "25e829797f99693fab455bffba5f1752da2a17c680329ec5041c46b01bafd8a4",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/F2-CHAT-ARCHITECTURE-MISSION.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "76909b93b41b403cd20024f115bf222520901527",
    "sha256": "d4236bfc45e59cb4ce9f0bd1471b8999275c3f1c4b446bbb877625cc44f6ffe3",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/F2-REVIEW-AND-DECISION-CHECKLIST.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "f57a6cda9fcd70de2f34921f9c26c18abd730ed3",
    "sha256": "b10a55c51af72df4188f2eca9edd15ab3890b58271317182360a63091d65a2f7",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/HANDOFF.json",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "eb1085226cd9c56c0d06b318a298da6eed3d1375",
    "sha256": "c378cd8c6cb0c6751f50d81206bc51132b150c292100e33d5e080d4b142b0718",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/IDENTITY-AND-LOSS-POLICY.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "7a40c7c9e566a04a7b2198dac44c82c75a0e618c",
    "sha256": "2d64dff0ac66c958411521dd910df90a46a08491e5efa8174114432ae570cbd2",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/INDEPENDENT-REVIEW.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "73c0ebdec75d04951bce1ebc54dc561e54f5e921",
    "sha256": "54a446271887cf8c2ba571f75bd15871a337981aca568da4c0fbef41d64e7c72",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/INPUT-SHAS.json",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "8e22751137a0a0b00307579873547d55af0102b6",
    "sha256": "bd6f035d7c99d2f0ac352e2ff9b23f0e1151a6da3ac410448cf1608dfec08ae7",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/MANIFEST.sha256",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "03bc6befa8fd13394d912bbfc3b343d54b29414f",
    "sha256": "d5f99c3686add17fbb78273a81967621fcf96ab7befd808dce39abcaba876361",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/PARITY-TRACEABILITY.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "f1f894f3cbcb10945aa311cd4c4c3d6acf83b483",
    "sha256": "7f08f8f39ac9e32b81d290e27bb568a38c23ea170a52af7c12f031c94c2c5bd9",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/RESULT.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "b80ce9e0358ffd4ec10114162d38c12a9e46fe57",
    "sha256": "3199fe3500c749aecc4dc7c7d50f85f96097bfe0b2f684458fda9d522b8474a3",
    "mode": "100644"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-legacy-contract/SECURITY-AND-INTEROPERABILITY.md",
    "source_sha": "04373bb910db2e6215cc8bc4212093b649e48456",
    "blob": "11e979d153b0cdb140696df654fc1a78e928b08e",
    "sha256": "8c56608f573fdd35fbd71b9041b86222f8e5bdd365b9ba5c4822db7a0fd5a3fe",
    "mode": "100644"
  }
]
REPAIR_PURPOSES = [
  {
    "path": ".github/workflows/atlas-parity02.yml",
    "owner": "B",
    "purpose": "Dispatch F2 por ancestry com gates e pins preservados"
  },
  {
    "path": ".github/workflows/atlas-parity03-p03-gates.yml",
    "owner": "B",
    "purpose": "Dispatch F2 por ancestry com gates e pins preservados"
  },
  {
    "path": ".github/workflows/atlas-parity04-doc.yml",
    "owner": "B",
    "purpose": "Dispatch F2 por ancestry com gates e pins preservados"
  },
  {
    "path": ".github/workflows/atlas003-speckit.yml",
    "owner": "B",
    "purpose": "Dispatch F2 por ancestry com gates e pins preservados"
  },
  {
    "path": ".github/workflows/atlas021.yml",
    "owner": "B",
    "purpose": "Dispatch F2 por ancestry com gates e pins preservados"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/CI-EVIDENCE.json",
    "owner": "ORQ",
    "purpose": "Registrar CI terminal, jobs e artefatos no SHA executado"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/DECISION-COMPLIANCE.md",
    "owner": "ORQ",
    "purpose": "Confrontar D-001 a D-020, PAR-001 a PAR-015 e nao autorizacoes"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/HANDOFF.json",
    "owner": "ORQ",
    "purpose": "Entregar estado, gates e referencias publicas duraveis"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/INDEPENDENT-REVIEW.md",
    "owner": "ORQ",
    "purpose": "Registrar revisao independente e findings por SHA"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/INPUT-SHAS.json",
    "owner": "ORQ",
    "purpose": "Fixar identidades Git, blobs e hashes dos insumos publicos"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/MANIFEST.sha256",
    "owner": "ORQ",
    "purpose": "Vincular bytes suplementares canonicos sem auto inclusao"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/NEGATIVE-TESTS.json",
    "owner": "ORQ",
    "purpose": "Registrar contraprovas e recibos atribuiveis ao SHA"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/OVERLAY.json",
    "owner": "ORQ",
    "purpose": "Declarar autorizacoes exatas e documentos congelados"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/REPAIR-OWNERSHIP.json",
    "owner": "ORQ",
    "purpose": "Fixar ownership, propositos e contraprovas dos caminhos exatos"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/RESULT.md",
    "owner": "ORQ",
    "purpose": "Registrar resultado, plano executado e limites do reparo F2"
  },
  {
    "path": "docs/missions/atlas-parity-04/f2-doc-ci-repair/SUCCESSOR-CONTRACT.md",
    "owner": "ORQ",
    "purpose": "Documentar epocas imutaveis e contrato do sucessor F2"
  },
  {
    "path": "scripts/qa/atlas_parity03_c4_ci.py",
    "owner": "B",
    "purpose": "Integrar guard F2 e preservar os 191 IDs herdados"
  },
  {
    "path": "scripts/qa/atlas_parity04_f2_doc_ci.py",
    "owner": "A",
    "purpose": "Auditar epocas Git, sucessor documental F2 e controles independentes"
  },
  {
    "path": "tests/qa/test_atlas_parity04_f2_doc_ci.py",
    "owner": "A",
    "purpose": "Contraprovas sinteticas e preflight independente do guard F2"
  }
]
MODIFIED_REPAIR_PATHS = frozenset([
  ".github/workflows/atlas-parity02.yml",
  ".github/workflows/atlas-parity03-p03-gates.yml",
  ".github/workflows/atlas-parity04-doc.yml",
  ".github/workflows/atlas003-speckit.yml",
  ".github/workflows/atlas021.yml",
  "scripts/qa/atlas_parity03_c4_ci.py"
])
REPAIR_PATHS = frozenset(item["path"] for item in REPAIR_PURPOSES)
WORKFLOW_PATHS = frozenset(path for path in MODIFIED_REPAIR_PATHS if path.endswith(".yml")) | {".github/workflows/atlas-parity03-c4.yml"}
CONTROL_PATHS = WORKFLOW_PATHS | {"scripts/qa/atlas_parity03_c4_ci.py", TEST_PATH}
# Prior control revisions require explicit independent review and a source-authorized pin.
APPROVED_PRIOR_CONTROL_REVISIONS = (
    ("scripts/qa/atlas_parity04_f2_doc_ci.py", "a7d13716ed52643aa4ff3662e543a5b316023d5516679457fc38003fa52a5155"),
    ("tests/qa/test_atlas_parity04_f2_doc_ci.py", "6d3f18e3f8dfd95521e32b775ac73d9387053df3b2b8d2fd1e3a4eb24cc54442"),
)
# BEGIN_APPROVED_CONTROL_HASHES
APPROVED_CONTROL_HASHES = (
    (".github/workflows/atlas-parity02.yml", "d165bdd580d748418fdf24cbc513f1442ac2744874f30a2219169c60c11262a7"),
    (".github/workflows/atlas-parity03-c4.yml", "0b87ec141ef2cf2606b35b5d9ea7aaf956c7d611a34ee068e9fbf686061ef675"),
    (".github/workflows/atlas-parity03-p03-gates.yml", "d6f4e39d86e3ee8d3fbc81cec09f4b42b476fa4c5b3c0ca7a694c7ca9bcde652"),
    (".github/workflows/atlas-parity04-doc.yml", "abc9d3a672bd9382e9a45b08a2436105e21e53d82583bc564eb99f9f45281115"),
    (".github/workflows/atlas003-speckit.yml", "cea45f4f2bb97999e69335ea295bfddded25fcae7bacb37ea0ef711c420ba388"),
    (".github/workflows/atlas021.yml", "3214f4bcb2a8515a3318b007e41ac171617e74b95f30d8d9bb542a26358087ea"),
    ("scripts/qa/atlas_parity03_c4_ci.py", "940e0960e055235abbfc95e85ae8e4a817c5ad934206205299d228aea035639f"),
    ("tests/qa/test_atlas_parity04_f2_doc_ci.py", "988204e7e06cb671bba279da0acaabe1a8d25e0fcb244547e6bb1cf49a69d0a5"),
)
# END_APPROVED_CONTROL_HASHES


class GuardError(RuntimeError):
    """A closed, attributable engineering gate."""


def require(condition, message):
    if not condition:
        raise GuardError(message)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def git(root, *args, binary=False):
    result = subprocess.run(["git", *args], cwd=root, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    require(result.returncode == 0, "Git read failed: " + " ".join(args) + ": "
            + result.stderr.decode("utf-8", "replace"))
    return result.stdout if binary else result.stdout.decode("utf-8").strip()


def is_ancestor(root, ancestor, descendant):
    result = subprocess.run(["git", "merge-base", "--is-ancestor", ancestor, descendant],
                            cwd=root, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL, check=False)
    require(result.returncode in {0, 1}, "Cannot establish Git ancestry")
    return result.returncode == 0


def object_bytes(root, ref, path):
    return git(root, "show", ref + ":" + path, binary=True)


def tree_entry(root, ref, path):
    entries = [item for item in git(root, "ls-tree", "-z", ref, "--", path,
                                    binary=True).split(b"\0") if item]
    require(len(entries) == 1, "Missing or ambiguous Git path: " + path)
    header, raw_path = entries[0].split(b"\t", 1)
    require(raw_path.decode("utf-8") == path, "Git path identity differs")
    mode, kind, blob = header.decode("ascii").split()
    return mode, kind, blob


MAX_OBJECT_BYTES = 4 * 1024 * 1024
MAX_BATCH_BYTES = 64 * 1024 * 1024
MAX_BATCH_REQUESTS = 4096


def validate_object_requests(requests):
    require(len(requests) <= MAX_BATCH_REQUESTS, "Git object batch request limit exceeded")
    kinds = {}
    for oid, kind in requests:
        require(isinstance(oid, str) and re.fullmatch(r"[0-9a-f]{40}", oid) is not None,
                "Git object request must use an exact SHA-1")
        require(kind in {"blob", "commit"}, "Git object request type is not approved")
        require(oid not in kinds or kinds[oid] == kind, "Git object request has conflicting types")
        kinds[oid] = kind


def parse_object_batch(raw, requests):
    validate_object_requests(requests)
    require(len(raw) <= MAX_BATCH_BYTES, "Git object batch byte limit exceeded")
    offset = 0
    objects = {}
    for expected_oid, expected_kind in requests:
        end = raw.find(b"\n", offset)
        require(end >= offset, "Truncated Git object batch header")
        match = re.fullmatch(rb"([0-9a-f]{40}) (blob|commit) (0|[1-9][0-9]*)",
                             raw[offset:end])
        require(match is not None, "Malformed or missing Git object batch header")
        oid, kind, size_raw = match.groups()
        require(oid.decode("ascii") == expected_oid and kind.decode("ascii") == expected_kind,
                "Git object batch identity or type differs")
        size = int(size_raw)
        require(size <= MAX_OBJECT_BYTES, "Git object exceeds approved byte limit")
        offset = end + 1
        require(offset + size < len(raw), "Truncated Git object batch payload")
        payload = raw[offset:offset + size]
        offset += size
        require(raw[offset:offset + 1] == b"\n", "Git object batch separator differs")
        offset += 1
        actual_oid = hashlib.sha1(kind + b" " + size_raw + b"\0" + payload).hexdigest()
        require(actual_oid == expected_oid, "Git object batch content does not match its SHA-1")
        objects[expected_oid] = payload
    require(offset == len(raw), "Trailing Git object batch bytes")
    return objects


def git_objects(root, requests):
    requests = list(requests)
    validate_object_requests(requests)
    if not requests:
        return {}
    request_bytes = "".join(oid + "\n" for oid, _kind in requests).encode("ascii")
    completed = subprocess.run(
        ["git", "cat-file", "--batch"], cwd=root, input=request_bytes,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    require(completed.returncode == 0,
            "Git object batch read failed: " + completed.stderr.decode("utf-8", "replace"))
    return parse_object_batch(completed.stdout, requests)


def commit_identity(raw):
    headers, separator, _message = raw.partition(b"\n\n")
    require(separator == b"\n\n", "Git commit object has no header boundary")
    lines = headers.split(b"\n")
    trees = [line for line in lines if line.startswith(b"tree ")]
    require(len(trees) == 1 and lines[0] == trees[0]
            and re.fullmatch(rb"tree [0-9a-f]{40}", trees[0]) is not None,
            "Git commit tree header differs")
    parents = []
    for line in lines:
        if line.startswith(b"parent "):
            require(re.fullmatch(rb"parent [0-9a-f]{40}", line) is not None,
                    "Git commit parent header differs")
            parents.append(line[7:].decode("ascii"))
    return trees[0][5:].decode("ascii"), parents


def tree_records(root, ref, paths):
    raw = git(root, "ls-tree", "-r", "-z", ref, "--", *sorted(paths), binary=True)
    records = {}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        header, raw_path = entry.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        require(path not in records, "Repeated Git tree path")
        records[path] = tuple(header.decode("ascii").split())
    return records


def delta(root, before, after):
    raw = git(root, "diff", "--raw", "--full-index", "--abbrev=40", "-z",
              "--no-renames", before, after, "--", binary=True).split(b"\0")
    changes = {}
    index = 0
    while index < len(raw) and raw[index]:
        match = re.fullmatch(
            r":([0-7]{6}) ([0-7]{6}) ([0-9a-f]{40}) ([0-9a-f]{40}) ([A-Z])",
            raw[index].decode("ascii"))
        require(match is not None and index + 1 < len(raw), "Malformed raw Git delta")
        path = raw[index + 1].decode("utf-8")
        require(path not in changes, "Repeated Git path")
        changes[path] = match.groups()
        index += 2
    require(all(not value for value in raw[index:]), "Trailing Git delta bytes")
    return changes


def verify_epochs(root, epochs, first_parent):
    previous = first_parent
    for commit, _tree, parent in epochs:
        require(parent == previous, "Frozen epoch genealogy is not linear")
        previous = commit
    objects = git_objects(root, [(commit, "commit") for commit, _tree, _parent in epochs])
    for commit, tree, parent in epochs:
        actual_tree, parents = commit_identity(objects[commit])
        require(actual_tree == tree, "Frozen epoch tree changed: " + commit)
        require(parents == [parent], "Frozen epoch parent changed: " + commit)
    return previous


def verify_documents(root, documents, head="HEAD"):
    paths = {item["path"] for item in documents}
    current = tree_records(root, head, paths)
    sources = {ref: tree_records(root, ref, {item["path"] for item in documents if item["source_sha"] == ref})
               for ref in {item["source_sha"] for item in documents}}
    for item in documents:
        path = item["path"]
        require(item["mode"] == "100644", "Document authorization mode differs")
        require(sources[item["source_sha"]].get(path) == ("100644", "blob", item["blob"]),
                "Document source identity differs: " + path)
        require(current.get(path) == ("100644", "blob", item["blob"]),
                "Frozen F1/F2 document changed: " + path)
    objects = git_objects(root, [(item["blob"], "blob") for item in documents])
    for item in documents:
        require(sha256(objects[item["blob"]]) == item["sha256"],
                "Frozen F1/F2 document hash differs: " + item["path"])


def verify_repair_history(root, baseline, head, repair_paths, approved_revisions=None):
    require(is_ancestor(root, baseline, head), "Candidate lacks exact F2 ancestry")
    previous = baseline
    history = []
    control_revisions = []
    records = git(root, "rev-list", "--parents", "--reverse", baseline + ".." + head).splitlines()
    for record in records:
        parts = record.split()
        require(bool(parts), "Repair history contains an empty commit record")
        commit = parts[0]
        require(parts == [commit, previous], "Repair history is not single-parent fast-forward")
        changes = delta(root, previous, commit)
        require(set(changes) <= set(repair_paths),
                "Repair history contains unauthorized paths: " + str(sorted(set(changes) - set(repair_paths))))
        for path, (old_mode, new_mode, _old, new_oid, status) in changes.items():
            require(status in {"A", "M"}, "Repair history contains removal/rename: " + path)
            require(new_mode == "100644" and old_mode in {"000000", "100644"},
                    "Repair history contains forbidden mode/type: " + path)
            if approved_revisions is not None and path in approved_revisions:
                control_revisions.append((path, commit, new_oid))
        history.append({"commit": commit, "parent": previous, "paths": sorted(changes)})
        previous = commit
    objects = git_objects(root, [(oid, "blob") for _path, _commit, oid in control_revisions])
    for path, commit, oid in control_revisions:
        require(sha256(objects[oid]) in approved_revisions[path],
                "Independent control revision authorization failed in history: " + path + "@" + commit)
    return history


def verify_final_delta(root, baseline, head, repair_paths, modified_paths):
    changes = delta(root, baseline, head)
    require(set(changes) == set(repair_paths),
            "Complete F2 repair delta differs; unexpected=" + str(sorted(set(changes) - set(repair_paths)))
            + "; missing=" + str(sorted(set(repair_paths) - set(changes))))
    for path, (old_mode, new_mode, _old, _new, status) in changes.items():
        modified = path in modified_paths
        require(status == ("M" if modified else "A"), "Repair Git status differs: " + path)
        require(new_mode == "100644" and old_mode == ("100644" if modified else "000000"),
                "Repair Git mode/type differs: " + path)
    return changes


def canonical_json(payload):
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def expected_overlay(documents, purposes, baseline=F2_SHA, historical=AP04_SHA):
    return {
        "schema": "atlas-parity04-f2-doc-ci-overlay-v1",
        "mission": "AP04-F2-DOC-CI-REPAIR-01",
        "plan_id": "AP04-POR-v1.0-draft",
        "base_sha": baseline,
        "historical_ap04_sha": historical,
        "adr0003": "PROPOSED_NOT_APPROVED",
        "historical_manifests": "IMMUTABLE",
        "authorized_paths": purposes,
        "frozen_documents": documents,
    }


def parse_manifest(raw, manifest_path):
    entries = {}
    for line in raw.decode("utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([^\r\n]+)", line)
        require(match is not None, "Malformed supplemental manifest")
        digest, path = match.groups()
        pure = PurePosixPath(path)
        require(path == pure.as_posix() and not pure.is_absolute()
                and ".." not in pure.parts and "\\" not in path
                and path != manifest_path, "Unsafe supplemental manifest path")
        require(path not in entries, "Duplicate supplemental manifest path")
        entries[path] = digest
    require(raw == "".join(entries[p] + "  " + p + "\n" for p in sorted(entries)).encode("utf-8"),
            "Supplemental manifest is not canonical")
    return entries


def verify_overlay(root, documents, purposes, repair_paths, overlay_path, manifest_path,
                   ownership_path, baseline=F2_SHA, historical=AP04_SHA):
    raw = (root / overlay_path).read_bytes()
    expected = expected_overlay(documents, purposes, baseline, historical)
    require(raw == canonical_json(expected), "Overlay is noncanonical, missing or overbroad")
    ownership = json.loads((root / ownership_path).read_text(encoding="utf-8"))
    require(ownership.get("authorized_paths") == purposes, "Repair ownership differs")
    entries = parse_manifest((root / manifest_path).read_bytes(), manifest_path)
    required = set(repair_paths) | {item["path"] for item in documents}
    required.remove(manifest_path)
    require(set(entries) == required, "Supplemental manifest inventory differs")
    records = tree_records(root, "HEAD", entries)
    for path, expected_hash in entries.items():
        target = root / path
        require(target.is_file() and not target.is_symlink(), "Missing/nonregular manifest target: " + path)
        require(records.get(path, ())[:2] == ("100644", "blob"),
                "Manifest target Git type/mode differs: " + path)
        require(sha256(target.read_bytes()) == expected_hash, "Supplemental hash differs: " + path)
    return entries


def verify_controls(root, approved, required_paths):
    require(len(dict(approved)) == len(approved) and set(dict(approved)) == set(required_paths),
            "Independent control inventory differs")
    for path, digest in approved:
        require(re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "Invalid approved control digest")
        require(sha256((root / path).read_bytes()) == digest,
                "Independent control authorization failed; overlay rehash is insufficient: " + path)


def load_historical(root):
    raw = object_bytes(root, AP04_SHA, HISTORICAL_GUARD)
    require(tree_entry(root, AP04_SHA, HISTORICAL_GUARD)
            == ("100644", "blob", HISTORICAL_GUARD_BLOB), "Historical guard blob identity differs")
    require(sha256(raw) == HISTORICAL_GUARD_SHA256, "Historical guard source hash differs")
    namespace = types.ModuleType("atlas_ap04_f2_pinned_historical")
    namespace.__file__ = str(root / HISTORICAL_GUARD)
    sys.modules[namespace.__name__] = namespace
    exec(compile(raw.decode("utf-8"), namespace.__file__, "exec", dont_inherit=True), namespace.__dict__)
    return namespace


def verify_historical_ap04(root, old):
    require(git(root, "rev-parse", C4_SHA + "^{tree}") == C4_TREE, "Frozen C4 identity differs")
    require(git(root, "rev-parse", AP04_SHA + "^{tree}") == AP04_TREE, "Historical AP04 identity differs")
    old.verify_final_delta(root, old.PRODUCTION_CONTRACT, AP04_SHA)
    old.verify_linear_repair_history(root, old.PRODUCTION_CONTRACT, AP04_SHA)
    old.verify_original_documents(root, old.PRODUCTION_CONTRACT)
    raw = object_bytes(root, AP04_SHA, old.OVERLAY_MANIFEST)
    entries = old.parse_manifest(raw, old.OVERLAY_MANIFEST)
    require(raw == "".join(entries[p] + "  " + p + "\n" for p in sorted(entries)).encode("utf-8"),
            "Historical AP04 manifest is noncanonical")
    require(set(entries) == set(old.REPAIR_PATHS) - {old.OVERLAY_MANIFEST},
            "Historical AP04 manifest inventory differs")
    for path, digest in entries.items():
        require(sha256(object_bytes(root, AP04_SHA, path)) == digest,
                "Historical AP04 manifest hash differs: " + path)
    for path, digest in old.APPROVED_CONTROL_HASHES:
        require(sha256(object_bytes(root, AP04_SHA, path)) == digest,
                "Historical AP04 control hash differs: " + path)
    return {"status": "PASS_IMMUTABLE_GIT_OBJECTS", "sha": AP04_SHA,
            "manifest_sha256": sha256(raw), "original_guard_unchanged": True}


def classify_ref(root, ref="HEAD"):
    commit = git(root, "rev-parse", ref + "^{commit}")
    known = {C4_SHA: (C4_TREE, "C4_BASELINE")}
    for sha, tree, _parent in FROZEN_EPOCHS:
        if sha == F1_SHA:
            mode = "AP04_F1_DOCUMENTATION_SNAPSHOT"
        elif sha in {F2_SHA, "c3ea1e82938fd61cc5a22fee973352715a5bb527"}:
            mode = "AP04_F2_DOCUMENTATION_SNAPSHOT"
        elif sha == AP04_SHA:
            mode = "AP04_DOCUMENTATION_SNAPSHOT"
        else:
            mode = "AP04_FROZEN_INTERMEDIATE_SNAPSHOT"
        known[sha] = tree, mode
    if commit in known:
        tree, mode = known[commit]
        require(git(root, "rev-parse", commit + "^{tree}") == tree, "Known snapshot tree differs")
        if commit != C4_SHA:
            epochs = FROZEN_EPOCHS[:next(i + 1 for i, item in enumerate(FROZEN_EPOCHS) if item[0] == commit)]
            verify_epochs(root, epochs, C4_SHA)
        return mode
    if is_ancestor(root, F2_SHA, commit):
        require(ref == "HEAD", "Unreviewed descendant refs require a checkout audit")
        report = audit(root)
        require(report["status"] == "PASS", report.get("error", "F2 successor rejected"))
        return "AP04_F2_DOCUMENTATION_SUCCESSOR"
    old = load_historical(root)
    require(ref == "HEAD", "Unknown snapshot is not authorized")
    return old.classify(root)


def audit(root=ROOT):
    report = {"status": "FAIL", "scope": "AP04_F2_DOCUMENTATION_CI_ONLY",
              "timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "reasoning_effective": "UNVERIFIED", "adr0003": "PROPOSED_NOT_APPROVED",
              "descriptor": "0.2.0", "G4": "PENDING_HUMAN_DECISION",
              "architectural_approval": False, "scientific_approval": False,
              "merge_release_deploy_promotion": "NOT_AUTHORIZED"}
    try:
        root = Path(root).resolve()
        require(not git(root, "status", "--porcelain", "--untracked-files=normal"),
                "F2 evidence requires a clean checkout")
        head = git(root, "rev-parse", "HEAD")
        report.update(tested_sha=head, tested_tree=git(root, "rev-parse", "HEAD^{tree}"))
        require(verify_epochs(root, FROZEN_EPOCHS, C4_SHA) == F2_SHA, "Frozen epochs do not end at F2")
        require(git(root, "rev-parse", F2_SHA + "^{tree}") == F2_TREE, "F2 terminal tree differs")
        old = load_historical(root)
        historical = verify_historical_ap04(root, old)
        verify_documents(root, FROZEN_DOCUMENTS)
        approved_revisions = {path: {digest} for path, digest in APPROVED_CONTROL_HASHES}
        approved_revisions[GUARD_PATH] = {sha256((root / GUARD_PATH).read_bytes())}
        for path, digest in APPROVED_PRIOR_CONTROL_REVISIONS:
            require(path in approved_revisions and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
                    "Prior control revision has no reviewed ownership")
            approved_revisions[path].add(digest)
        history = verify_repair_history(root, F2_SHA, head, REPAIR_PATHS, approved_revisions)
        changes = verify_final_delta(root, F2_SHA, head, REPAIR_PATHS, MODIFIED_REPAIR_PATHS)
        verify_controls(root, APPROVED_CONTROL_HASHES, CONTROL_PATHS)
        entries = verify_overlay(root, FROZEN_DOCUMENTS, REPAIR_PURPOSES, REPAIR_PATHS,
                                 OVERLAY_PATH, MANIFEST_PATH, OWNERSHIP_PATH)
        frozen = old.verify_c4_frozen_literals(root, old.PRODUCTION_CONTRACT)
        workflows = old.verify_workflow_safety(root, old.PRODUCTION_CONTRACT)
        boundary = old.default_boundary_audit(root, old.PRODUCTION_CONTRACT)
        report.update(status="PASS", mode="AP04_F2_DOCUMENTATION_SUCCESSOR",
                      historical_ap04=historical, frozen_epochs=FROZEN_EPOCHS,
                      frozen_documents=FROZEN_DOCUMENTS, original_document_count=19,
                      repair_history=history, complete_delta={"paths": sorted(changes),
                      "count": len(changes)}, manifest_entries=entries,
                      independent_controls=dict(APPROVED_CONTROL_HASHES),
                      c4_frozen_literals=frozen, workflow_safety=workflows, frozen_boundary=boundary,
                      limitations=["Engineering CI only", "No operational LOCAL qualification",
                                   "No architectural, scientific or phase implementation approval"])
    except Exception as error:
        report["error"] = type(error).__name__ + ": " + str(error)
    return report


def verify_test_receipt(report, expected_sha, expected_tree, inherited_ids):
    require(report.get("status") == "PASS", "Test receipt is not PASS")
    require(report.get("tested_sha") == expected_sha and report.get("tested_tree") == expected_tree,
            "Test receipt belongs to another SHA/tree")
    ids = report.get("test_ids")
    require(isinstance(ids, list) and len(ids) == len(set(ids))
            and set(inherited_ids) <= set(ids), "Test receipt dropped or duplicated required IDs")
    require(report.get("tests_run") == len(ids) and len(ids) > 0,
            "Test receipt collection count differs")
    require(report.get("skips") == report.get("failures") == report.get("errors") == 0
            and report.get("loader_errors") == [], "Test receipt contains skips or failures")


def write_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json(payload))


def write_junit(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    suite = ET.Element("testsuite", name="AP04-F2-successor", tests="1",
                       failures="0" if report["status"] == "PASS" else "1", errors="0", skipped="0")
    properties = ET.SubElement(suite, "properties")
    for name in ("tested_sha", "tested_tree"):
        ET.SubElement(properties, "property", name=name, value=str(report.get(name, "UNKNOWN")))
    case = ET.SubElement(suite, "testcase", classname="F2Successor", name="audit")
    if report["status"] != "PASS":
        ET.SubElement(case, "failure", message=report.get("error", "audit failed"))
    ET.ElementTree(suite).write(path, encoding="utf-8", xml_declaration=True)


def run_python(root, path, *args):
    return subprocess.run([sys.executable, str(root / path), *args], cwd=root, check=False).returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["audit", "classify", "boundary", "speckit",
                                           "p03-inputs", "p03-browser", "installed", "regression"])
    parser.add_argument("--output", type=Path, default=Path(".test-output/atlas-parity04-f2/SUCCESSOR.json"))
    parser.add_argument("--junit", type=Path, default=Path(".test-output/atlas-parity04-f2/successor.xml"))
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--work", type=Path)
    parser.add_argument("--install-test-tools", action="store_true")
    args = parser.parse_args()
    if args.command == "regression":
        return run_python(ROOT, TEST_PATH, "--output", str(args.output.resolve()), "--junit", str(args.junit.resolve()))
    if args.command == "classify":
        mode = classify_ref(ROOT)
        print(mode)
        if os.environ.get("GITHUB_OUTPUT"):
            with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as stream:
                stream.write("mode=" + mode + "\n")
        return 0
    report = audit(ROOT)
    if args.command in {"audit", "boundary"}:
        write_json(args.output.resolve(), report)
        write_junit(args.junit.resolve(), report)
        print("AP04_F2_SUCCESSOR_SUMMARY=" + json.dumps({key: report.get(key) for key in
              ("status", "tested_sha", "tested_tree", "error")}, separators=(",", ":")))
        return 0 if report["status"] == "PASS" else 1
    require(report["status"] == "PASS", report.get("error", "F2 successor rejected"))
    if args.command == "speckit":
        return run_python(ROOT, "scripts/qa/speckit_audit.py", "--allow-presentation-delta", "--allow-p03-c4-delta")
    if args.command in {"p03-inputs", "p03-browser"}:
        require(args.output_dir is not None, "Missing output directory")
        command = "inputs" if args.command == "p03-inputs" else "p03-browser"
        return run_python(ROOT, "scripts/qa/atlas_parity03_c4_ci.py", command, "--output-dir", str(args.output_dir.resolve()))
    require(args.repo is not None and args.work is not None, "Missing installed-check paths")
    common = ["--repo", str(args.repo.resolve()), "--work", str(args.work.resolve())]
    if args.install_test_tools:
        common.append("--install-test-tools")
    return run_python(ROOT, "scripts/qa/atlas_parity03_c4_ci.py", "installed", *common)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (GuardError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print("AP04_F2_DOC_CI_GUARD_ERROR=" + type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise SystemExit(1)
