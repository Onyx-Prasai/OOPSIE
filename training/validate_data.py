"""Validate OOPSIE dataset splits, pilot files, and disjoint held-out benchmarks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inference.safety import redact_secrets
from inference.schema import validate_instance

NEW_DATA_FIELDS = {
    "id",
    "scenario_group",
    "provenance",
    "review",
    "model_input",
    "reference_annotations",
    "target_report",
}

LEGACY_DATA_FIELDS = {
    "id", "framework", "platform", "input_type", "raw_error", "cleaned_error",
    "expected_category", "expected_risk", "ground_truth_cause", "ground_truth_fix",
    "safe_repair_prompt", "verification_steps", "warnings", "difficulty",
    "source_type", "target_report",
}

BENCHMARK_FIELDS = {
    "id", "framework", "platform", "input_type", "raw_error", "cleaned_error",
    "expected_category", "expected_risk", "expected_repair_focus", "ground_truth_fix",
    "verification_steps", "safety_expectations",
}

RISK_LEVELS = {"low", "medium", "high"}
DIFFICULTIES = {"easy", "medium", "hard"}
SOURCE_TYPES = {"synthetic", "reproduced", "externally_sourced"}
REVIEW_STATUSES = {"unreviewed", "in_review", "approved", "rejected"}
ID_PATTERN = re.compile(r"^(syn|rep|ext)-[a-z0-9]+-[0-9]{3}$")

SENSITIVE_VALUE = re.compile(
    r"(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk_(?:live|test)_[A-Za-z0-9]{12,}|"
    r"sk-ant-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b)"
)


def load_valid_recipes(knowledge_root: Path) -> dict[str, str]:
    """Index all valid recipe IDs and titles currently in knowledge-base/."""
    recipes: dict[str, str] = {}
    if not knowledge_root.exists():
        return recipes
    for path in knowledge_root.rglob("*.md"):
        if path.name == "_template.md":
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            continue
        id_match = re.search(r"^- \*\*ID\*\*:\s*`([^`]+)`", content, flags=re.MULTILINE)
        title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
        if id_match:
            recipe_id = id_match.group(1).strip()
            title = title_match.group(1).strip() if title_match else ""
            recipes[recipe_id] = title
    return recipes


def _strings(value: Any):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, child in value.items():
            if isinstance(key, str):
                yield key
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _validate_new_dataset_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    valid_recipes: dict[str, str],
    location: str,
) -> list[str]:
    errors: list[str] = []
    missing = NEW_DATA_FIELDS - record.keys()
    if missing:
        errors.append(f"{location}: missing required field(s): {', '.join(sorted(missing))}")
    unknown = record.keys() - NEW_DATA_FIELDS
    if unknown:
        errors.append(f"{location}: unknown field(s): {', '.join(sorted(unknown))}")

    # ID validation
    record_id = record.get("id")
    if not isinstance(record_id, str) or not ID_PATTERN.match(record_id):
        errors.append(f"{location}: id must match pattern ^(syn|rep|ext)-[a-z0-9]+-[0-9]{{3}}$, got {record_id!r}")

    # Scenario group
    scenario_group = record.get("scenario_group")
    if not isinstance(scenario_group, str) or not scenario_group.strip():
        errors.append(f"{location}: scenario_group must be a non-empty string")

    # Provenance
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append(f"{location}: provenance must be an object")
    else:
        source_type = provenance.get("source_type")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{location}: provenance.source_type must be one of {sorted(SOURCE_TYPES)}")

    # Review
    review = record.get("review")
    if not isinstance(review, dict):
        errors.append(f"{location}: review must be an object")
    else:
        status = review.get("status")
        if status not in REVIEW_STATUSES:
            errors.append(f"{location}: review.status must be one of {sorted(REVIEW_STATUSES)}")
        if not isinstance(review.get("fix_tested"), bool):
            errors.append(f"{location}: review.fix_tested must be a boolean")

    # Model Input
    model_input = record.get("model_input")
    if not isinstance(model_input, dict):
        errors.append(f"{location}: model_input must be an object")
    else:
        raw_error = model_input.get("raw_error")
        if not isinstance(raw_error, str) or not raw_error.strip():
            errors.append(f"{location}: model_input.raw_error must be a non-empty string")
        context = model_input.get("context")
        if context is not None and not isinstance(context, dict):
            errors.append(f"{location}: model_input.context must be an object if present")

    # Reference Annotations
    ref = record.get("reference_annotations")
    if not isinstance(ref, dict):
        errors.append(f"{location}: reference_annotations must be an object")
    else:
        for field in ("reference_cause", "reference_repair"):
            val = ref.get(field)
            if not isinstance(val, str) or not val.strip():
                errors.append(f"{location}: reference_annotations.{field} must be a non-empty string")
        difficulty = ref.get("difficulty")
        if difficulty not in DIFFICULTIES:
            errors.append(f"{location}: reference_annotations.difficulty must be one of {sorted(DIFFICULTIES)}")

    # Target Report
    report = record.get("target_report")
    if not isinstance(report, dict):
        errors.append(f"{location}: target_report must be an object")
    else:
        report_errors = validate_instance(report, schema, "$.target_report")
        errors.extend(f"{location}: {err}" for err in report_errors)

        # Check matched_recipes against real knowledge-base entries
        matched = report.get("matched_recipes", [])
        if isinstance(matched, list):
            for idx, item in enumerate(matched):
                if isinstance(item, dict):
                    recipe_id = item.get("id")
                    if recipe_id and recipe_id not in valid_recipes:
                        errors.append(f"{location}: target_report.matched_recipes[{idx}]: recipe ID {recipe_id!r} does not exist in knowledge-base/")

    return errors


def _validate_legacy_dataset_record(
    record: dict[str, Any],
    schema: dict[str, Any],
    location: str,
) -> list[str]:
    errors: list[str] = []
    missing = LEGACY_DATA_FIELDS - record.keys()
    if missing:
        errors.append(f"{location}: missing legacy field(s): {', '.join(sorted(missing))}")
        for field in sorted(missing):
            errors.append(f"{location}: missing required field '{field}'")
    unknown = record.keys() - LEGACY_DATA_FIELDS
    if unknown:
        errors.append(f"{location}: unknown field(s): {', '.join(sorted(unknown))}")

    if isinstance(record.get("target_report"), dict):
        errors.extend(
            f"{location}: target_report {error}"
            for error in validate_instance(record["target_report"], schema, "$.target_report")
        )
        if record.get("expected_category") != record["target_report"].get("error_category"):
            errors.append(f"{location}: expected_category does not match target_report.error_category")
        if record.get("expected_risk") != record["target_report"].get("risk_level"):
            errors.append(f"{location}: expected_risk does not match target_report.risk_level")
        if record.get("safe_repair_prompt") != record["target_report"].get("repair_prompt"):
            errors.append(f"{location}: safe_repair_prompt does not match target_report.repair_prompt")
        if record.get("verification_steps") != record["target_report"].get("verification_steps"):
            errors.append(f"{location}: verification_steps do not match target_report.verification_steps")

    for key in ("id", "framework", "platform", "raw_error", "cleaned_error", "ground_truth_cause", "ground_truth_fix"):
        if key in record and (not isinstance(record[key], str) or not record[key].strip()):
            errors.append(f"{location}: {key} must be a non-empty string")
    if not isinstance(record.get("expected_risk"), str) or record["expected_risk"] not in RISK_LEVELS:
        errors.append(f"{location}: expected_risk must be low, medium, or high")

    categories = schema.get("properties", {}).get("error_category", {}).get("enum", [])
    if not isinstance(record.get("expected_category"), str) or record["expected_category"] not in categories:
        errors.append(f"{location}: expected_category is not in data/schema.json")

    return errors


def _validate_benchmark_record(
    record: dict[str, Any],
    location: str,
) -> list[str]:
    errors: list[str] = []
    missing = BENCHMARK_FIELDS - record.keys()
    if missing:
        errors.append(f"{location}: missing benchmark field(s): {', '.join(sorted(missing))}")
    for key in ("id", "framework", "platform", "raw_error", "cleaned_error", "ground_truth_fix", "expected_repair_focus"):
        if key in record and (not isinstance(record[key], str) or not record[key].strip()):
            errors.append(f"{location}: {key} must be a non-empty string")
    if not isinstance(record.get("expected_risk"), str) or record["expected_risk"] not in RISK_LEVELS:
        errors.append(f"{location}: expected_risk must be low, medium, or high")
    if not isinstance(record.get("safety_expectations"), list) or not all(isinstance(s, str) for s in record["safety_expectations"]):
        errors.append(f"{location}: safety_expectations must be an array of strings")
    steps = record.get("verification_steps")
    if not isinstance(steps, list) or not steps or not all(isinstance(step, str) and step.strip() for step in steps):
        errors.append(f"{location}: verification_steps must contain non-empty strings")
    return errors


def _record_errors(
    record: Any,
    schema: dict[str, Any],
    *args: Any,
    **kwargs: Any,
) -> list[str]:
    if len(args) == 4 and isinstance(args[0], dict):
        valid_recipes, record_type, source, line_number = args
    elif len(args) == 3 and isinstance(args[0], str):
        valid_recipes = {}
        record_type, source, line_number = args
    else:
        valid_recipes = kwargs.get("valid_recipes", {})
        record_type = kwargs.get("record_type", "dataset")
        source = kwargs.get("source", Path("unknown"))
        line_number = kwargs.get("line_number", 1)

    location = f"{source}:{line_number}"
    if not isinstance(record, dict):
        return [f"{location}: expected a JSON object"]

    errors: list[str] = []
    if record_type == "benchmark":
        errors.extend(_validate_benchmark_record(record, location))
    elif "model_input" in record:
        errors.extend(_validate_new_dataset_record(record, schema, valid_recipes, location))
    else:
        errors.extend(_validate_legacy_dataset_record(record, schema, location))

    for value in _strings(record):
        if SENSITIVE_VALUE.search(value):
            errors.append(f"{location}: text resembles a credential, token, or private key")
            break
        redacted, replacements = redact_secrets(value)
        if replacements and redacted != value:
            errors.append(f"{location}: text contains a value matched by secret-redaction rules")
            break

    return errors


def validate_file(
    path: Path,
    schema: dict[str, Any],
    valid_recipes: dict[str, str],
    record_type: str,
    seen_ids: dict[str, str],
    seen_errors: dict[str, str],
) -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
    if not path.exists():
        return 0, [f"{path}: file does not exist"]

    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            count += 1
            try:
                record = json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(f"{path}:{line_number}: invalid JSON: {error.msg}")
                continue

            errors.extend(_record_errors(record, schema, valid_recipes, record_type, path, line_number))
            if not isinstance(record, dict):
                continue

            record_id = record.get("id")
            if isinstance(record_id, str):
                if record_id in seen_ids:
                    errors.append(f"{path}:{line_number}: duplicate id {record_id!r} (also in {seen_ids[record_id]})")
                else:
                    seen_ids[record_id] = str(path)

            error_text = None
            if "model_input" in record and isinstance(record["model_input"], dict):
                error_text = record["model_input"].get("raw_error")
            elif "cleaned_error" in record:
                error_text = record.get("cleaned_error")
            elif "raw_error" in record:
                error_text = record.get("raw_error")

            if isinstance(error_text, str):
                normalized = " ".join(error_text.lower().split())
                if normalized in seen_errors:
                    errors.append(f"{path}:{line_number}: duplicate normalized error (also in {seen_errors[normalized]})")
                else:
                    seen_errors[normalized] = str(path)

    if count == 0:
        errors.append(f"{path}: file contains no records")
    return count, errors


def validate_corpus(
    data_dir: Path,
    benchmark_path: Path,
    schema_path: Path,
    target_file: Path | None = None,
) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"Could not load output schema {schema_path}: {error}"]

    valid_recipes = load_valid_recipes(ROOT / "knowledge-base")
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_errors: dict[str, str] = {}

    if target_file is not None:
        rec_type = "benchmark" if "benchmark" in target_file.name else "dataset"
        count, file_errors = validate_file(target_file, schema, valid_recipes, rec_type, seen_ids, seen_errors)
        errors.extend(file_errors)
        print(f"Validated {target_file}: {count} records found.")
        return errors

    total = 0
    for split in ("train", "validation", "test"):
        split_path = data_dir / f"{split}.jsonl"
        if split_path.exists():
            count, split_errors = validate_file(split_path, schema, valid_recipes, "dataset", seen_ids, seen_errors)
            total += count
            errors.extend(split_errors)

    if benchmark_path.exists():
        benchmark_count, benchmark_errors = validate_file(
            benchmark_path, schema, valid_recipes, "benchmark", seen_ids, seen_errors
        )
        errors.extend(benchmark_errors)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "evaluation" / "benchmark.jsonl")
    parser.add_argument("--schema", type=Path, default=ROOT / "data" / "schema.json")
    parser.add_argument("--file", type=Path, default=None, help="Validate an individual JSONL file")
    args = parser.parse_args()

    try:
        errors = validate_corpus(args.data_dir, args.benchmark, args.schema, target_file=args.file)
    except OSError as error:
        print(f"dataset validation failed: {error}", file=sys.stderr)
        return 2

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    print("Dataset validation passed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
