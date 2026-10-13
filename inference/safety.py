"""Secret redaction and deterministic safety warnings for inference."""

from __future__ import annotations

import json
from functools import lru_cache
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


@lru_cache(maxsize=1)
def load_redaction_rules() -> list[tuple[re.Pattern[str], str]]:
    path = ROOT / "rules" / "redaction" / "patterns.json"
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
        rules = payload["rules"]
        return [
            (
                re.compile(item["regex"], re.IGNORECASE if "i" in item.get("flags", "") else 0),
                re.sub(r"\$(\d+)", lambda match: r"\g<" + match.group(1) + ">", item["replacement"]),
            )
            for item in rules
        ]
    except (OSError, json.JSONDecodeError, KeyError, TypeError, re.error) as error:
        raise RuntimeError(f"Could not load OOPSIE secret-redaction rules from {path}: {error}") from error


def redact_secrets(text: str) -> tuple[str, int]:
    redacted = text
    count = 0
    for pattern, replacement in load_redaction_rules():
        redacted, matches = pattern.subn(replacement, redacted)
        count += matches
    return redacted, count


def contains_secret_like_text(text: str) -> bool:
    redacted, count = redact_secrets(text)
    return count > 0 and redacted != text


@lru_cache(maxsize=1)
def load_safety_rules() -> list[dict[str, str]]:
    risk_rules_path = ROOT / "rules" / "safety" / "destructive-commands.json"
    try:
        safety_rules: Any = json.loads(risk_rules_path.read_text(encoding="utf-8"))
        rules = safety_rules["rules"]
        for rule in rules:
            if rule["risk"] not in RISK_ORDER:
                raise ValueError(f"unsupported risk level: {rule['risk']}")
            re.compile(rule["pattern"])
        return rules
    except (OSError, json.JSONDecodeError, KeyError, TypeError, re.error) as error:
        raise RuntimeError(f"Could not load OOPSIE safety rules from {risk_rules_path}: {error}") from error


def apply_safety_warnings(report: dict[str, Any], input_text: str) -> dict[str, Any]:
    combined = f"{input_text}\n{report['repair_prompt']}"
    matched = [
        rule for rule in load_safety_rules()
        if re.search(rule["pattern"], combined, flags=re.IGNORECASE)
    ]

    warnings = list(report["warnings"])
    for rule in matched:
        warnings.append(rule["message"])

    combined_lower = combined.lower()
    for terms, warning in (
        (("production", "prod database"), "This may affect a production system. Confirm the target environment and use an approved change process."),
        (("payment", "billing", "charge", "refund"), "This may affect payments or billing. Verify amounts, test mode, and authorization before any change."),
        (("authentication", "auth", "login", "credential"), "This may affect authentication or access control. Review identity and authorization behavior before applying changes."),
        (("database", "sql", "migration"), "This may affect stored data. Review backups, migration scope, and rollback options before making changes."),
    ):
        if any(term in combined_lower for term in terms):
            warnings.append(warning)

    if matched:
        risk_level = max(
            [report["risk_level"], *(rule["risk"] for rule in matched)],
            key=RISK_ORDER.__getitem__,
        )
        report["risk_level"] = risk_level
    report["warnings"] = list(dict.fromkeys(warnings))
    return report
