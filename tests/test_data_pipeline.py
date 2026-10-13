import json
import tempfile
import unittest
from pathlib import Path

from inference.format import parse_report
from inference.retrieval import retrieve_recipes
from inference.schema import validate_instance
from inference.safety import apply_safety_warnings, redact_secrets
from training.preprocess import preprocess_split

ROOT = Path(__file__).resolve().parents[1]


class DatasetPipelineTests(unittest.TestCase):
    def test_committed_splits_match_report_schema(self) -> None:
        schema = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
        for split in ("train", "validation", "test"):
            path = ROOT / "data" / f"{split}.jsonl"
            rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
            self.assertGreater(len(rows), 0, split)
            for row in rows:
                self.assertIsInstance(row["cleaned_error"], str)
                self.assertEqual(validate_instance(row["target_report"], schema), [], split)

    def test_preprocessor_redacts_input_and_output_text(self) -> None:
        source_data = json.loads((ROOT / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0])
        source_data["raw_error"] += "\nAuthorization: Bearer sample-token-value"
        source_data["cleaned_error"] = source_data["raw_error"]
        source_data["target_report"]["plain_explanation"] += " token=sample-secret-value"
        source_data["safe_repair_prompt"] = source_data["target_report"]["repair_prompt"]
        with tempfile.TemporaryDirectory() as directory:
            temp_root = Path(directory)
            source = temp_root / "source.jsonl"
            destination = temp_root / "processed.jsonl"
            source.write_text(json.dumps(source_data) + "\n", encoding="utf-8")
            count = preprocess_split(
                "test",
                source,
                destination,
                ROOT / "data" / "schema.json",
                ROOT / "rules" / "redaction" / "patterns.json",
            )
            processed = json.loads(destination.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(count, 1)
        serialized = json.dumps(processed)
        self.assertNotIn("sample-token-value", serialized)
        self.assertNotIn("sample-secret-value", serialized)
        self.assertIn("[REDACTED]", serialized)


class InferenceSafetyTests(unittest.TestCase):
    def test_generated_report_must_match_schema(self) -> None:
        report = json.loads((ROOT / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0])["target_report"]
        parsed = parse_report(json.dumps(report))
        self.assertEqual(parsed["error_category"], "dependency")
        with self.assertRaises(ValueError):
            parse_report('{"summary":"missing required fields"}')

    def test_redacts_secrets_and_adds_high_impact_warning(self) -> None:
        redacted, count = redact_secrets(
            "Authorization: Bearer sample-token-value OPENAI_API_KEY=sample-api-value"
        )
        self.assertGreaterEqual(count, 2)
        self.assertNotIn("sample-token-value", redacted)
        self.assertNotIn("sample-api-value", redacted)

        report = json.loads((ROOT / "data" / "train.jsonl").read_text(encoding="utf-8").splitlines()[0])["target_report"]
        report["repair_prompt"] = "Run DROP TABLE users on production."
        assessed = apply_safety_warnings(report, "database maintenance")
        self.assertEqual(assessed["risk_level"], "high")
        self.assertTrue(any("permanently delete" in warning for warning in assessed["warnings"]))

    def test_retrieves_recipe_from_matching_error_signature(self) -> None:
        recipes = retrieve_recipes("Module not found: Can't resolve '@supabase/supabase-js'")
        self.assertTrue(recipes)
        self.assertEqual(recipes[0]["id"], "kb-react-supabase-001")


if __name__ == "__main__":
    unittest.main()
