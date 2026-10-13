"""Validate, redact, and prepare OOPSIE JSONL splits for fine-tuning."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

from inference.schema import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ("train", "validation", "test")
SYSTEM_PROMPT = (
    "You are OOPSIE, an AI error recovery assistant. Return only a JSON object matching "
    "the supplied response schema. Explain likely causes without certainty, ask for missing "
    "context, surface safety risks, and provide a focused repair prompt with verification steps. "
    "Never execute commands, modify code, deploy applications, or guarantee a fix."
)


def load_redaction_patterns(path: Path) -> list[tuple[re.Pattern[str], str]]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        rules = payload["rules"]
        patterns = [
            (
                re.compile(rule["regex"], re.IGNORECASE if "i" in rule.get("flags", "") else 0),
                re.sub(r"\$(\d+)", lambda match: r"\g<" + match.group(1) + ">", rule["replacement"]),
            )
            for rule in rules
        ]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, re.error) as error:
        raise ValueError(f"Invalid secret-redaction rules in {path}: {error}") from error
    return patterns


def redact_text(text: str, patterns: list[tuple[re.Pattern[str], str]]) -> str:
    for pattern, replacement in patterns:
        text = pattern.sub(replacement, text)
    return text


def validate_example(
    example: Any,
    schema: dict[str, Any],
    source: Path,
    line_number: int,
) -> dict[str, Any]:
    if isinstance(example, dict) and isinstance(example.get("target_report"), dict):
        required = {
            "id", "framework", "platform", "input_type", "raw_error", "cleaned_error",
            "expected_category", "expected_risk", "ground_truth_cause", "ground_truth_fix",
            "safe_repair_prompt", "verification_steps", "warnings", "difficulty",
            "source_type", "target_report",
        }
        missing = required - example.keys()
        if missing:
            raise ValueError(f"{source}:{line_number}: missing dataset fields: {', '.join(sorted(missing))}")
        errors = validate_instance(example["target_report"], schema, "$.target_report")
        if errors:
            raise ValueError(f"{source}:{line_number}: {errors[0]}")
        if example["expected_category"] != example["target_report"]["error_category"]:
            raise ValueError(f"{source}:{line_number}: expected_category does not match target_report")
        if example["expected_risk"] != example["target_report"]["risk_level"]:
            raise ValueError(f"{source}:{line_number}: expected_risk does not match target_report")
        return {
            "input": {
                "error_text": example["cleaned_error"],
                "context": {
                    "framework": example["framework"],
                    "platform": example["platform"],
                    "input_type": example["input_type"],
                },
            },
            "output": example["target_report"],
        }
    if not isinstance(example, dict) or not isinstance(example.get("input"), dict):
        raise ValueError(f"{source}:{line_number}: expected an object with an input object")
    input_record = example["input"]
    if not isinstance(input_record.get("error_text"), str) or not input_record["error_text"].strip():
        raise ValueError(f"{source}:{line_number}: input.error_text must be a non-empty string")
    output = example.get("output")
    errors = validate_instance(output, schema, "$.output")
    if errors:
        raise ValueError(f"{source}:{line_number}: {errors[0]}")
    context = input_record.get("context", {})
    if not isinstance(context, dict):
        raise ValueError(f"{source}:{line_number}: input.context must be an object")
    return {"input": input_record, "output": output}


def redact_strings(value: Any, patterns: list[tuple[re.Pattern[str], str]]) -> Any:
    if isinstance(value, str):
        return redact_text(value, patterns)
    if isinstance(value, list):
        return [redact_strings(item, patterns) for item in value]
    if isinstance(value, dict):
        return {key: redact_strings(item, patterns) for key, item in value.items()}
    return value


def preprocess_split(
    split: str,
    source: Path,
    destination: Path,
    schema_path: Path,
    redaction_path: Path,
) -> int:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    patterns = load_redaction_patterns(redaction_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    with source.open(encoding="utf-8") as input_file, destination.open("w", encoding="utf-8", newline="\n") as output_file:
        for line_number, line in enumerate(input_file, 1):
            if not line.strip():
                continue
            try:
                raw_example = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"{source}:{line_number}: invalid JSON: {error.msg}") from error
            example = validate_example(raw_example, schema, source, line_number)
            example = redact_strings(example, patterns)
            serialized = json.dumps(example, ensure_ascii=False, separators=(",", ":"))
            output_file.write(serialized + "\n")
            count += 1

    print(f"{split}: prepared {count} examples -> {destination}")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=(*SPLITS, "all"), default="all")
    parser.add_argument("--data-dir", type=Path, default=ROOT / "data")
    parser.add_argument("--schema", type=Path, default=ROOT / "data" / "schema.json")
    parser.add_argument(
        "--redaction-rules",
        type=Path,
        default=ROOT / "rules" / "redaction" / "patterns.json",
    )
    args = parser.parse_args()

    selected_splits = SPLITS if args.split == "all" else (args.split,)
    try:
        for split in selected_splits:
            preprocess_split(
                split,
                args.data_dir / f"{split}.jsonl",
                args.data_dir / "processed" / f"{split}.jsonl",
                args.schema,
                args.redaction_rules,
            )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"preprocess: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
