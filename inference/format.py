"""Structured output parsing and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from inference.schema import validate_instance

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "schema.json"


def parse_report(generated_text: str) -> dict[str, Any]:
    text = generated_text.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    start = text.find("{")
    if start < 0:
        raise ValueError("Model output did not contain a JSON object.")
    if text[:start].strip():
        raise ValueError("Model output contained text before the JSON report.")
    try:
        report, end = json.JSONDecoder().raw_decode(text[start:])
    except json.JSONDecodeError as error:
        raise ValueError(f"Model output contained invalid JSON: {error.msg}") from error
    if text[start + end:].strip():
        raise ValueError("Model output contained extra text after the JSON report.")

    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = validate_instance(report, schema)
    if errors:
        raise ValueError(f"Model output failed schema validation: {errors[0]}")
    return report
