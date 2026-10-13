"""Validate OOPSIE dataset splits and a disjoint held-out benchmark."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from inference.safety import redact_secrets
from inference.schema import validate_instance

ROOT = Path(__file__).resolve().parents[1]
DATA_FIELDS = {
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
INPUT_TYPES = {"error_message", "stack_trace", "terminal_output", "build_log", "deployment_log"}
SENSITIVE_VALUE = re.compile(
    r"(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"\b(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|sk_(?:live|test)_[A-Za-z0-9]{12,}|"
    r"sk-ant-[A-Za-z0-9_-]{16,}|eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\b)"
)


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


def _record_errors(
    record: Any,
    schema: dict[str, Any],
    record_type: str,
    source: Path,
    line_number: int,
) -> list[str]:
    location = f"{source}:{line_number}"
    if not isinstance(record, dict):
        return [f"{location}: expected a JSON object"]
    required = DATA_FIELDS if record_type == "dataset" else BENCHMARK_FIELDS
    errors = [f"{location}: missing required field {field!r}" for field in sorted(required - record.keys())]
    if record_type == "dataset":
        errors.extend(f"{location}: unknown field {field!r}" for field in sorted(record.keys() - required))
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
    if not isinstance(record.get("input_type"), str) or record["input_type"] not in INPUT_TYPES:
        errors.append(f"{location}: input_type is not supported")
    if record_type == "dataset":
        if not isinstance(record.get("difficulty"), str) or record["difficulty"] not in {"easy", "medium", "hard"}:
            errors.append(f"{location}: difficulty must be easy, medium, or hard")
        if not isinstance(record.get("source_type"), str) or record["source_type"] not in {"synthetic", "permissioned_anonymized"}:
            errors.append(f"{location}: source_type must identify synthetic or permissioned data")
        if not isinstance(record.get("warnings"), list) or not all(isinstance(item, str) for item in record["warnings"]):
            errors.append(f"{location}: warnings must be an array of strings")
    if record_type == "benchmark" and (
        not isinstance(record.get("safety_expectations"), list)
        or not all(isinstance(item, str) for item in record["safety_expectations"])
    ):
        errors.append(f"{location}: safety_expectations must be an array of strings")
    if record_type == "benchmark" and (
        not isinstance(record.get("expected_repair_focus"), str)
        or not record["expected_repair_focus"].strip()
    ):
        errors.append(f"{location}: expected_repair_focus must be a non-empty string")
    prompt = record.get("safe_repair_prompt") if record_type == "dataset" else record.get("expected_repair_focus")
    if not isinstance(prompt, str) or not prompt.strip():
        errors.append(f"{location}: repair prompt/focus must be non-empty")
    steps = record.get("verification_steps")
    if not isinstance(steps, list) or not steps or not all(isinstance(step, str) and step.strip() for step in steps):
        errors.append(f"{location}: verification_steps must contain non-empty strings")
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
    record_type: str,
    seen_ids: dict[str, str],
    seen_errors: dict[str, str],
) -> tuple[int, list[str]]:
    errors: list[str] = []
    count = 0
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
            errors.extend(_record_errors(record, schema, record_type, path, line_number))
            if not isinstance(record, dict):
                continue
            record_id = record.get("id")
            if isinstance(record_id, str):
                if record_id in seen_ids:
                    errors.append(f"{path}:{line_number}: duplicate id {record_id!r} (also in {seen_ids[record_id]})")
                else:
                    seen_ids[record_id] = str(path)
            cleaned = record.get("cleaned_error")
            if isinstance(cleaned, str):
                normalized = " ".join(cleaned.lower().split())
                if normalized in seen_errors:
                    errors.append(f"{path}:{line_number}: duplicate cleaned error (also in {seen_errors[normalized]})")
                else:
                    seen_errors[normalized] = str(path)
    if count == 0:
        errors.append(f"{path}: file contains no records")
    return count, errors


def validate_corpus(data_dir: Path, benchmark_path: Path, schema_path: Path) -> list[str]:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"Could not load output schema {schema_path}: {error}"]
    errors: list[str] = []
    seen_ids: dict[str, str] = {}
    seen_errors: dict[str, str] = {}
    total = 0
    for split in ("train", "validation", "test"):
        count, split_errors = validate_file(data_dir / f"{split}.jsonl", schema, "dataset", seen_ids, seen_errors)
        total += count
        errors.extend(split_errors)
    benchmark_count, benchmark_errors = validate_file(
        benchmark_path, schema, "benchmark", seen_ids, seen_errors
    )
    errors.extend(benchmark_errors)
    if total < 100:
        errors.append(f"Dataset must contain at least 100 examples; found {total}")
    if not 30 <= benchmark_count <= 50:
        errors.append(f"Benchmark must contain 30-50 examples; found {benchmark_count}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--benchmark", type=Path, default=ROOT / "evaluation" / "benchmark.jsonl")
    parser.add_argument("--schema", type=Path, default=ROOT / "data" / "schema.json")
    args = parser.parse_args()
    try:
        errors = validate_corpus(args.data_dir, args.benchmark, args.schema)
    except OSError as error:
        print(f"dataset validation failed: {error}", file=sys.stderr)
        return 2
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Dataset and held-out benchmark validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
