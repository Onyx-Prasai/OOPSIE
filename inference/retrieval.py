"""Rank community recipes using signatures, keywords, framework, and category clues."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STOP_WORDS = {
    "about", "after", "again", "because", "cannot", "could", "error", "from",
    "have", "into", "that", "their", "there", "these", "this", "when", "with",
    "module", "resolve", "failed", "failure", "undefined", "reading",
}


def classify_error(error_text: str) -> tuple[str, str]:
    rules_path = ROOT / "rules" / "classifiers" / "error-signatures.json"
    try:
        payload: Any = json.loads(rules_path.read_text(encoding="utf-8"))
        rules = payload["rules"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise RuntimeError(f"Could not load OOPSIE classifier rules from {rules_path}: {error}") from error
    normalized = error_text.lower()
    best_rule: dict[str, Any] | None = None
    best_score = 0
    for rule in rules:
        score = sum(len(signature) + 1 for signature in rule.get("signatures", []) if signature.lower() in normalized)
        if score > best_score:
            best_rule = rule
            best_score = score
    if best_rule is None:
        unknown = next(rule for rule in rules if rule["category"] == "unknown")
        return unknown["category"], unknown["framework"]
    return best_rule["category"], best_rule["framework"]

def retrieve_recipes(
    error_text: str,
    limit: int = 3,
    framework: str | None = None,
    category: str | None = None,
) -> list[dict[str, str]]:
    detected_category, detected_framework = classify_error(error_text)
    category = category or detected_category
    framework = (framework or detected_framework).lower()
    recipes: list[tuple[float, dict[str, str]]] = []
    normalized_error = error_text.lower()
    query_tokens = {
        token for token in re.findall(r"[a-zA-Z0-9_./-]{3,}", error_text.lower())
        if token not in STOP_WORDS
    }
    knowledge_root = ROOT / "knowledge-base"
    for path in sorted(knowledge_root.rglob("*.md")):
        if path.name == "_template.md":
            continue
        content = path.read_text(encoding="utf-8")
        signatures_section = re.split(r"^## Target Error Signatures\s*$", content, flags=re.IGNORECASE | re.MULTILINE)
        signature_text = signatures_section[1].split("\n## ", 1)[0] if len(signatures_section) > 1 else ""
        signatures = [
            signature.strip().strip("`\"'")
            for signature in re.findall(r"^\s*-\s*`?(.+?)`?\s*$", signature_text, flags=re.MULTILINE)
        ]
        exact_signature = any(signature.lower() in normalized_error for signature in signatures if signature)
        signature_terms = set(re.findall(r"[a-zA-Z0-9_./-]{3,}", signature_text.lower()))
        body_terms = set(re.findall(r"[a-zA-Z0-9_./-]{3,}", content.lower()))
        overlap = len(query_tokens & signature_terms)
        keyword_overlap = len(query_tokens & body_terms)
        metadata = "\n".join(
            line for line in content.splitlines()
            if line.startswith("- **Category**:") or line.startswith("- **Frameworks**:")
        ).lower()
        category_match = bool(category and category.lower() in metadata)
        framework_aliases = {
            "vercel / netlify": ("vercel", "netlify"),
            "application configuration": ("next", "application"),
            "authentication / identity": ("auth", "identity"),
            "api / backend": ("api", "backend"),
            "npm / node.js": ("npm", "node"),
        }
        clues = framework_aliases.get(framework, (framework,))
        framework_match = bool(framework and any(clue in metadata or clue in path.as_posix().lower() for clue in clues))
        score = (10.0 if exact_signature else 0.0) + min(overlap, 5) * 2 + min(keyword_overlap, 4) * 0.25
        score += 2.5 if category_match else 0
        score += 2.5 if framework_match else 0
        if score < 2.5:
            continue
        title_match = re.search(r"^#\s+(.+)$", content, flags=re.MULTILINE)
        recipe_id_match = re.search(r"^- \*\*ID\*\*:\s*`([^`]+)`", content, flags=re.MULTILINE)
        recipes.append((
            score,
            {
                "id": recipe_id_match.group(1) if recipe_id_match else path.stem,
                "title": title_match.group(1).strip() if title_match else path.stem,
                "path": path.relative_to(ROOT).as_posix(),
                "content": content[:5000],
            },
        ))
    recipes.sort(key=lambda item: (-item[0], item[1]["path"]))
    return [recipe for _, recipe in recipes[:limit]]
