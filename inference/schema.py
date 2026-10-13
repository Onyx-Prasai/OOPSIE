"""Small dependency-free validator for the JSON Schema keywords used here."""

from __future__ import annotations

from typing import Any


def validate_instance(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []
    expected_type = schema.get("type")
    if expected_type == "object":
        if not isinstance(instance, dict):
            return [f"{path}: expected object"]
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}.{key}: required property is missing")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            child_schema = properties.get(key)
            if child_schema is None:
                if schema.get("additionalProperties") is False:
                    errors.append(f"{path}.{key}: additional property is not allowed")
                continue
            errors.extend(validate_instance(value, child_schema, f"{path}.{key}"))
    elif expected_type == "array":
        if not isinstance(instance, list):
            return [f"{path}: expected array"]
        item_schema = schema.get("items")
        if item_schema:
            for index, value in enumerate(instance):
                errors.extend(validate_instance(value, item_schema, f"{path}[{index}]"))
    elif expected_type == "string":
        if not isinstance(instance, str):
            return [f"{path}: expected string"]
        if len(instance) < schema.get("minLength", 0):
            errors.append(f"{path}: string is shorter than minLength")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: value is not in the allowed enum")
    return errors
