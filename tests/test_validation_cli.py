import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from nurbs_knowledge.__main__ import main
from nurbs_knowledge.common import sha256_file, text_hash
from nurbs_knowledge.ingest.validation import validate_corpus


class CorpusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ["data/raw", "data/sources", "data/processed", "data/evaluation", "configs"]:
            (self.root / directory).mkdir(parents=True)
        raw = self.root / "data/raw/sample.hxx"
        raw.write_text("//! Surface definition.\n//! Exact API_identifier.\n", encoding="utf-8")
        license_path = self.root / "data/raw/license.txt"
        license_path.write_text("Synthetic testing fixture, not research evidence.", encoding="utf-8")
        self.source = {"source_id": "s1", "title": "Synthetic fixture", "publisher": "Tests",
                       "canonical_url": "https://example.org/sample.hxx", "retrieved_at": "2026-10-22T00:00:00+00:00",
                       "language": "en", "product_version": "test", "license_name": "fixture",
                       "license_url": "https://example.org/license", "permission_status": "approved",
                       "permitted_use": "tests only", "local_path": "data/raw/sample.hxx",
                       "content_sha256": sha256_file(raw), "notes": "Synthetic test fixture only",
                       "license_local_path": "data/raw/license.txt", "license_sha256": sha256_file(license_path),
                       "permission_evidence": "synthetic fixture"}
        text = "Surface definition.\nExact API_identifier."
        self.chunk = {"chunk_id": "c1", "source_id": "s1", "section_title": "Fixture",
                      "locator": "https://example.org/sample.hxx#L1-L2", "text": text, "language": "en",
                      "product_version": "test", "content_sha256": text_hash(text)}
        self.save()
        config = Path(__file__).resolve().parents[1] / "configs/bm25.json"
        (self.root / "configs/bm25.json").write_bytes(config.read_bytes())
        question = {"query_id": "q1", "family_id": "f1", "language": "en", "category": "definition_api",
                    "question": "surface", "evidence_need": "definition", "origin": "synthetic",
                    "source_note": "fixture", "review_status": "pending_human_review"}
        (self.root / "data/evaluation/dev_questions.jsonl").write_text(json.dumps(question) + "\n", encoding="utf-8")

    def save(self, sources=None, chunks=None):
        for path, rows in [("data/sources/registry.jsonl", [self.source] if sources is None else sources),
                           ("data/processed/chunks.jsonl", [self.chunk] if chunks is None else chunks)]:
            (self.root / path).write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

    def errors(self):
        return "\n".join(validate_corpus(self.root)[2])

    def test_valid_fixture_and_raw_integrity(self):
        self.assertEqual(self.errors(), "")
        (self.root / "data/raw/sample.hxx").write_text("//! modified", encoding="utf-8")
        self.assertIn("SHA-256 mismatch", self.errors())

    def test_unapproved_and_missing_sources(self):
        self.source["permission_status"] = "pending"
        self.save()
        self.assertIn("not approved", self.errors())
        self.save(sources=[])
        self.assertIn("unknown source_id", self.errors())

    def test_duplicates(self):
        self.save(sources=[self.source, self.source], chunks=[self.chunk, self.chunk])
        for message in ["duplicate source_id", "duplicate chunk_id", "duplicate normalized chunk text"]:
            self.assertIn(message, self.errors())

    def test_missing_fields_and_invalid_json(self):
        del self.chunk["locator"]
        self.save()
        self.assertIn("locator", self.errors())
        (self.root / "data/processed/chunks.jsonl").write_text("{broken\n", encoding="utf-8")
        self.assertIn("chunks.jsonl:1", self.errors())

    def test_source_license_and_path_checks(self):
        self.source["license_sha256"] = "0" * 64
        self.save()
        self.assertIn("SHA-256 mismatch", self.errors())
        self.source["local_path"] = "../outside.hxx"
        self.save()
        self.assertIn("inside the project", self.errors())

    def test_tampered_text_with_updated_hash_still_fails(self):
        self.chunk["text"] = "Invented evidence"
        self.chunk["content_sha256"] = text_hash(self.chunk["text"])
        self.save()
        self.assertIn("differs from source lines", self.errors())

    def test_exception_evidence_is_validated(self):
        self.source["exception_local_path"] = "data/raw/license.txt"
        self.source["exception_sha256"] = "0" * 64
        self.save()
        self.assertIn("SHA-256 mismatch", self.errors())

    def test_invalid_locator_and_version(self):
        self.chunk["locator"] = "https://example.org/sample.hxx#L1-L999"
        self.chunk["product_version"] = "wrong"
        self.save()
        self.assertIn("outside source line range", self.errors())
        self.assertIn("differs from source", self.errors())

    def call(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(["--root", str(self.root), *args])
        return code, out.getvalue(), err.getvalue()

    def test_cli_search_and_no_overwrite(self):
        output = self.root / "result.json"
        code, stdout, stderr = self.call("search", "--query", "API_identifier", "--output", str(output))
        self.assertEqual(code, 0, stderr)
        result = json.loads(stdout)
        self.assertEqual(result["results"][0]["source_url"], self.source["canonical_url"])
        self.assertEqual(result["results"][0]["locator"], self.chunk["locator"])
        code, _, _ = self.call("search", "--query", "surface", "--output", str(output))
        self.assertEqual(code, 2)

    def test_cli_no_match_empty_query_and_invalid_corpus(self):
        code, stdout, _ = self.call("search", "--query", "несуществующее")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout)["results"], [])
        self.assertEqual(self.call("search", "--query", "")[0], 2)
        self.assertEqual(self.call("search", "--query", "surface", "--top-k", "0")[0], 2)
        self.save(chunks=[])
        self.assertEqual(self.call("validate")[0], 1)

    def test_demo_creates_distinct_runs_with_identical_rankings(self):
        locations = []
        for _ in range(2):
            code, stdout, stderr = self.call("demo")
            self.assertEqual(code, 0, stderr)
            locations.append(Path(stdout.strip()))
        self.assertNotEqual(locations[0], locations[1])
        records = [json.loads((path / "retrieval.jsonl").read_text(encoding="utf-8")) for path in locations]
        self.assertEqual(records[0]["results"], records[1]["results"])
        self.assertTrue((locations[0] / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
