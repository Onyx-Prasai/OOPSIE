"""Strict raw JSON parsing and schema validation for OOPSIE completions.

Rules:
1. Parse the generated completion only (never prompt + completion).
2. Do not strip Markdown fences (e.g. ```json), extract substring JSON, or repair syntax.
3. Reject duplicate JSON keys.
4. Reject non-standard numeric constants (NaN, Infinity, -Infinity).
5. Validate strictly against data/schema.json.
6. Diagnostic raw output is excluded from public envelopes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from inference.config import SCHEMA_PATH
from inference.schema import validate_instance


class ParseError(ValueError):
    """Raised when model completion is not valid, strict, duplicate-free JSON."""
    pass


class SchemaValidationError(ValueError):
    """Raised when parsed JSON does not conform to data/schema.json."""

    def __init__(self, message: str, errors: list[str]) -> None:
        super().__init__(message)
        self.errors = errors


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Custom object_pairs_hook that raises ValueError on duplicate keys."""
    res: dict[str, Any] = {}
    for key, value in pairs:
        if key in res:
            raise ValueError(f"Duplicate JSON key detected: '{key}'")
        res[key] = value
    return res


def _reject_constant(constant: str) -> None:
    """Custom parse_constant that rejects non-standard JSON numeric constants."""
    raise ValueError(f"Non-standard numeric constant not allowed in JSON: '{constant}'")


def _load_schema() -> dict[str, Any]:
    """Load and cache the canonical schema."""
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema not found at {SCHEMA_PATH}")
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


_CACHED_SCHEMA: dict[str, Any] | None = None


def get_cached_schema() -> dict[str, Any]:
    global _CACHED_SCHEMA
    if _CACHED_SCHEMA is None:
        _CACHED_SCHEMA = _load_schema()
    return _CACHED_SCHEMA


def strict_parse_raw_completion(completion: str) -> dict[str, Any]:
    """Parse raw completion text strictly.

    Does NOT strip Markdown code fences or perform regex extractions.
    Rejects duplicate keys and non-standard constants (NaN, Infinity).
    """
    text = completion.strip()
    if not text:
        raise ParseError("Model completion is empty.")

    # In strict mode, markdown fences are not silently stripped.
    # If the model produced markdown fences, strict json.loads will raise a syntax error.
    try:
        parsed = json.loads(
            text,
            object_pairs_hook=_reject_duplicates,
            parse_constant=_reject_constant,
        )
    except json.JSONDecodeError as exc:
        raise ParseError(f"Model completion is not valid JSON: {exc.msg} at line {exc.lineno} col {exc.colno}") from exc
    except ValueError as exc:
        raise ParseError(str(exc)) from exc

    if not isinstance(parsed, dict):
        raise ParseError(f"Expected JSON object at root, received {type(parsed).__name__}.")

    return parsed


def validate_oopsie_report(report: dict[str, Any]) -> dict[str, Any]:
    """Validate a parsed JSON report against data/schema.json."""
    schema = get_cached_schema()
    errors = validate_instance(report, schema)
    if errors:
        raise SchemaValidationError(
            f"Schema validation failed with {len(errors)} error(s): {errors[0]}",
            errors=errors,
        )
    return report
