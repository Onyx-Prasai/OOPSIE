import json
import tempfile
import unittest
from pathlib import Path

from inference.retrieval import retrieve_recipes
from inference.safety import contains_secret_like_text, redact_secrets
from training.validate_data import validate_corpus

ROOT = Path(__file__).resolve().parents[1]


class CorpusValidationTests(unittest.TestCase):
    def test_initial_dataset_and_held_out_benchmark_validate(self) -> None:
        errors = validate_corpus(
            ROOT / "data",
            ROOT / "evaluation" / "benchmark.jsonl",
            ROOT / "data" / "schema.json",
        )
        self.assertEqual(errors, [])

    def test_validator_reports_missing_fields_invalid_risk_and_duplicates(self) -> None:
        valid = json.loads((ROOT / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0])
        invalid = dict(valid)
        invalid["expected_risk"] = "critical"
        invalid.pop("ground_truth_fix")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for split in ("train", "validation", "test"):
                (root / f"{split}.jsonl").write_text(
                    json.dumps(valid) + "\n" + json.dumps(invalid) + "\n",
                    encoding="utf-8",
                )
            benchmark_path = root / "benchmark.jsonl"
            benchmark_path.write_text("", encoding="utf-8")
            errors = validate_corpus(root, benchmark_path, ROOT / "data" / "schema.json")
        self.assertTrue(any("missing required field 'ground_truth_fix'" in error for error in errors))
        self.assertTrue(any("expected_risk must be low, medium, or high" in error for error in errors))
        self.assertTrue(any("duplicate id" in error for error in errors))

    def test_validator_rejects_secret_like_content(self) -> None:
        record = json.loads((ROOT / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0])
        record["raw_error"] += "\nOPENAI_API_KEY=not-a-real-but-secret-shaped-value"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            from training.validate_data import _record_errors

            schema = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
            errors = _record_errors(record, schema, "dataset", path, 1)
        self.assertTrue(any("secret" in error.lower() for error in errors))


class RedactionAndRetrievalTests(unittest.TestCase):
    def test_redacts_requested_credential_formats(self) -> None:
        sensitive_text = "\n".join(
            [
                "SUPABASE_SERVICE_ROLE_KEY=synthetic-value",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY=synthetic-value",
                "FIREBASE_API_KEY=synthetic-value",
                "OPENAI_API_KEY=synthetic-value",
                '"ANTHROPIC_API_KEY": "json-synthetic-value"',
                "ANTHROPIC_API_KEY=synthetic-value",
                "GITHUB_TOKEN=synthetic-value",
                "DATABASE_URL=postgres://user:password@db.example.invalid/name",
                "MONGODB_URI=mongodb://user:password@db.example.invalid/name",
                "Authorization: Bearer synthetic.jwt.value",
                "JWT=eyJhbGciOiJub25l.eyJzdWIiOiJzYW1wbGUi.c2lnbmF0dXJl",
                "sk_live_syntheticStripeKeyValue",
                "AKIA1234567890ABCDEF",
                "-----BEGIN PRIVATE KEY----- synthetic-private-key -----END PRIVATE KEY-----",
            ]
        )
        redacted, count = redact_secrets(sensitive_text)
        self.assertGreaterEqual(count, 14)
        for value in (
            "synthetic-value",
            "json-synthetic-value",
            "db.example.invalid",
            "synthetic.jwt.value",
            "eyJhbGciOiJub25l.eyJzdWIiOiJzYW1wbGUi.c2lnbmF0dXJl",
            "sk_live_syntheticStripeKeyValue",
            "AKIA1234567890ABCDEF",
            "synthetic-private-key",
        ):
            self.assertNotIn(value, redacted)
        self.assertTrue(contains_secret_like_text(sensitive_text))

    def test_retrieval_uses_signature_category_and_framework_clues(self) -> None:
        deployment = retrieve_recipes('Error: Command "npm run build" exited with 1', framework="vercel")
        self.assertTrue(deployment)
        self.assertEqual(deployment[0]["id"], "kb-vercel-build-001")
        authorization = retrieve_recipes(
            'new row violates row-level security policy for table "profiles"',
            framework="supabase",
            category="authorization",
        )
        self.assertTrue(authorization)
        self.assertIn("rls", authorization[0]["id"])


if __name__ == "__main__":
    unittest.main()
