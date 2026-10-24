from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import struct
import tempfile
import unittest
import zipfile

from caderno_protocol import load_package, to_read_model, validate_document

ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("environmental_export", ROOT / "examples/environmental/export.py")
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class ContractAndRoundTrip(unittest.TestCase):
    def test_environmental_producer_and_lossless_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            base = exporter.export(Path(temp) / "crate")
            before = {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob("*") if p.is_file()}
            package = load_package(base)
            self.assertTrue(package.report.valid, package.report.to_dict())
            result = to_read_model(package)
            self.assertEqual((len(result["projects"]), len(result["experiments"]), len(result["runs"])), (2, 3, 4))
            self.assertEqual({r["status"] for r in result["runs"]}, {"COMPLETED", "PARTIAL", "FAILED", "UNKNOWN"})
            self.assertEqual(result["runs"][2]["metrics"][0]["value"], None)
            self.assertTrue(result["runs"][2]["metrics"][0]["missing_reason"])
            self.assertEqual(before, {p.relative_to(base).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in base.rglob("*") if p.is_file()})

    def test_zip_transport_preserves_bytes_and_projection(self):
        with tempfile.TemporaryDirectory() as temp:
            base = exporter.export(Path(temp) / "crate")
            archive = Path(temp) / "transport.zip"
            with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
                for path in base.rglob("*"):
                    if path.is_file():
                        z.write(path, "snapshot/" + path.relative_to(base).as_posix())
            direct, zipped = load_package(base), load_package(archive)
            self.assertTrue(zipped.report.valid, zipped.report.to_dict())
            self.assertEqual(direct.metadata_sha256, zipped.metadata_sha256)
            self.assertEqual(to_read_model(direct)["runs"], to_read_model(zipped)["runs"])
            self.assertEqual(direct.payload_status, zipped.payload_status)

    def test_export_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            base = exporter.export(Path(temp) / "crate")
            with self.assertRaises(FileExistsError):
                exporter.export(base)

    def test_corrupt_lzma_stream_is_reported_without_losing_readable_records(self):
        try:
            import lzma
        except ImportError:
            self.skipTest("This Python build has no optional LZMA compression support")
        for target in ["ro-crate-metadata.json", "data/water.csv"]:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as temp:
                base = exporter.export(Path(temp) / "crate")
                archive = Path(temp) / "corrupt-lzma.zip"
                with zipfile.ZipFile(archive, "w", zipfile.ZIP_LZMA) as z:
                    for path in base.rglob("*"):
                        if path.is_file():
                            z.write(path, path.relative_to(base).as_posix())
                    offset = z.getinfo(target).header_offset
                damaged = bytearray(archive.read_bytes())
                name_length, extra_length = struct.unpack_from("<HH", damaged, offset + 26)
                compressed_start = offset + 30 + name_length + extra_length
                # Leave ZIP framing intact but invalidate the LZMA filter properties.
                damaged[compressed_start + 4] = 255
                archive.write_bytes(damaged)
                with zipfile.ZipFile(archive) as z:
                    with self.assertRaises(lzma.LZMAError):
                        z.read(target)
                package = load_package(archive)
                self.assertEqual(archive.read_bytes(), bytes(damaged))
                if target == "ro-crate-metadata.json":
                    self.assertFalse(package.report.valid)
                    self.assertIn("SOURCE_INVALID", {x.code for x in package.report.errors})
                else:
                    self.assertTrue(package.report.valid, package.report.to_dict())
                    self.assertEqual(package.payload_status[target]["status"], "UNAVAILABLE")
                    self.assertIn("PAYLOAD_UNAVAILABLE", {x.code for x in package.report.warnings})
                    self.assertEqual(len(to_read_model(package)["runs"]), 4)

    def test_complete_profiles_and_software_metadata_required(self):
        document, _ = exporter.build_document()
        for entity in document["@graph"]:
            if entity.get("@type") == "SoftwareApplication":
                entity.pop("url")
        self.assertIn("SOFTWARE_METADATA", {x.code for x in validate_document(document).errors})

    def test_unknown_unprefixed_terms_not_silently_dropped(self):
        document, _ = exporter.build_document()
        document["@graph"][1]["unregisteredField"] = "lost in RDF without context"
        self.assertIn("UNMAPPED_TERM", {x.code for x in validate_document(document).errors})

    def test_external_missing_relation_is_not_silently_accepted(self):
        document, _ = exporter.build_document()
        next(e for e in document["@graph"] if e.get("@type") == "CreateAction")["object"] = [{"@id": "https://example.invalid/undeclared"}]
        self.assertIn("MISSING_REFERENCE", {x.code for x in validate_document(document).errors})

    def test_aliasing_file_ids_rejected(self):
        document, _ = exporter.build_document()
        original = next(e for e in document["@graph"] if e.get("@id") == "data/water.csv")
        alias = deepcopy(original)
        alias["@id"] = "data/WATER.csv"
        document["@graph"].append(alias)
        self.assertIn("ID_ALIAS_COLLISION", {x.code for x in validate_document(document).errors})

    def test_official_example_is_preserved_and_explicitly_outside_profile(self):
        path = ROOT / "examples/upstream/process-run-0.6/ro-crate-metadata.json"
        before = path.read_bytes()
        report = load_package(path).report
        self.assertFalse(report.valid)
        self.assertIn("UNSUPPORTED_PROFILE", {x.code for x in report.errors})
        self.assertEqual(path.read_bytes(), before)

    def test_serialization_round_trip_preserves_original_graph(self):
        document, _ = exporter.build_document()
        reloaded = json.loads(json.dumps(document, ensure_ascii=False, allow_nan=False))
        self.assertEqual(reloaded, document)
        self.assertTrue(validate_document(reloaded).valid)

    def test_profile_schema_matches_positive_fixture(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("JSON Schema reference validator is a test dependency, not runtime")
        path = ROOT / "packages/protocol/src/caderno_protocol/resources/schema.json"
        schema = json.loads(path.read_text())
        Draft202012Validator.check_schema(schema)
        document, _ = exporter.build_document()
        self.assertEqual(list(Draft202012Validator(schema).iter_errors(document)), [])

    def test_decimal_import_never_silently_rounds_the_source(self):
        cases = [("0.1", True, 0.1), ("1.2345678901234567", True, 1.2345678901234567),
                 ("9007199254740993", True, 9007199254740993),
                 ("0.123456789012345678901", False, None),
                 ("1e309", False, None), ("1e-999", False, None)]
        for literal, accepted, expected in cases:
            with self.subTest(literal=literal), tempfile.TemporaryDirectory() as temp:
                base = exporter.export(Path(temp) / "crate")
                path = base / "ro-crate-metadata.json"
                document = json.loads(path.read_text(encoding="utf-8"))
                metric = next(e for e in document["@graph"] if e.get("cp:valueType") == "number")
                metric["value"] = "DECIMAL_LITERAL_PLACEHOLDER"
                raw = json.dumps(document, ensure_ascii=False).replace('"DECIMAL_LITERAL_PLACEHOLDER"', literal).encode("utf-8")
                path.write_bytes(raw)
                package = load_package(base)
                self.assertEqual(path.read_bytes(), raw)
                self.assertEqual(package.report.valid, accepted, package.report.to_dict())
                if accepted:
                    parsed = next(e for e in package.document["@graph"] if e.get("@id") == metric["@id"])
                    self.assertEqual(parsed["value"], expected)
                    if literal == "9007199254740993":
                        self.assertIsInstance(parsed["value"], int)
                else:
                    self.assertIn("SOURCE_INVALID", {x.code for x in package.report.errors})


if __name__ == "__main__":
    unittest.main()
