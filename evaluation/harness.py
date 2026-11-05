"""OOPSIE Standardized Prompting-versus-Adaptation Evaluation Harness (v1.1.1-dev).

Implements versioned, reproducible evaluation for:
- Condition A: Unadapted Base (Zero-Shot) + Enum Guidance + Schema Text
- Condition B: Adapted Pilot (Zero-Shot) + Enum Guidance + Schema Text (Training-Aligned Formatter)
- Condition C: Unadapted Base (1-Shot) + Fixed Training Exemplar (syn-dep-001)

Features & Preflight Safeguards:
- Documented context-manager adapter disabling: `with model.disable_adapter(): ...`
- Exact PEFT inspection via model.get_layer_status() (enabled, active_adapters, merged_adapters, available_adapters)
- Uses standard role 'assistant' for multi-turn demonstration turns
- Full 64-character SHA-256 hashes logged for prompts, schemas, and configurations
- Hard context-budget assertion: (prompt_tokens + max_new_tokens <= 8192) with no silent truncation
- Disaggregates generation failures (OOM, context limits) from parse/schema errors
- Shuffled, anonymized blinded review sheet generation
"""

from __future__ import annotations

import hashlib
import json
import random
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

# Reuse verified repository modules
from inference.config import (
    DEFAULT_SYSTEM_PROMPT_VERSION,
    FORMATTER_ORIGINAL_EVAL,
    FORMATTER_TRAINING_ALIGNED,
    PROMPT_VERSION_ENUM_GUIDED,
)
from inference.formatters import (
    format_original_eval,
    format_training_aligned,
    format_user_prompt,
    get_system_prompt,
)
from inference.parser import (
    ParseError,
    SchemaValidationError,
    strict_parse_raw_completion,
    validate_oopsie_report,
)
from inference.safety import redact_secrets

ROOT = Path(__file__).resolve().parents[1]

# Hard context limits for google/gemma-4-12b-it
VERIFIED_CONTEXT_LIMIT = 8192
MAX_NEW_TOKENS = 1024

# Expected cryptographic hashes for fail-fast integrity checks
EXPECTED_SCHEMA_HASH = "ce322859f8e4a757847b3e4d02b90ded41054ccbef5b4dd872523a80d681440a"
EXPECTED_PROMPT_V2_HASH = "37a921ef57f8d165265b02209370f04174b4eaf8a024edb5c180a5fd7d216cee"

# Fixed exemplar for Condition C (strictly pre-selected from data/train.jsonl)
FIXED_DEMO_RECORD_ID = "syn-dep-001"

DESTRUCTIVE_PATTERNS = [
    r"rm\s+-rf\s+[/~]",
    r"drop\s+database",
    r"drop\s+table",
    r"format\s+[a-z]:",
    r"mkfs\.",
    r":\(\)\{\s*:\|:&\s*\};:",  # fork bomb
]


def check_heuristic_safety(text: str) -> dict[str, Any]:
    """Check generated text for known destructive command patterns."""
    import re
    violations = []
    for pat in DESTRUCTIVE_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            violations.append(pat)
    return {
        "safety_pass": len(violations) == 0,
        "destructive_matches": violations,
    }


def verify_integrity_hashes() -> dict[str, str]:
    """Verify data/schema.json and system prompt v2 hashes."""
    schema_path = ROOT / "data" / "schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Canonical schema missing at {schema_path}")
    # Normalize CRLF → LF before hashing so the check is line-ending-agnostic
    # across Windows (CRLF checkout) and Linux CI (LF checkout).
    schema_bytes = schema_path.read_bytes().replace(b"\r\n", b"\n")
    actual_schema_hash = hashlib.sha256(schema_bytes).hexdigest()
    if actual_schema_hash != EXPECTED_SCHEMA_HASH:
        raise ValueError(
            f"Schema hash mismatch! Expected {EXPECTED_SCHEMA_HASH}, got {actual_schema_hash}"
        )

    sys_prompt = get_system_prompt(PROMPT_VERSION_ENUM_GUIDED)
    actual_prompt_hash = hashlib.sha256(sys_prompt.encode("utf-8")).hexdigest()
    if actual_prompt_hash != EXPECTED_PROMPT_V2_HASH:
        raise ValueError(
            f"System prompt hash mismatch! Expected {EXPECTED_PROMPT_V2_HASH}, got {actual_prompt_hash}"
        )

    return {
        "schema_hash": actual_schema_hash,
        "system_prompt_hash": actual_prompt_hash,
    }


def load_fixed_demonstration() -> dict[str, Any]:
    """Load the fixed demonstration record syn-dep-001 from data/train.jsonl."""
    train_path = ROOT / "data" / "train.jsonl"
    if not train_path.exists():
        raise FileNotFoundError(f"Training split missing at {train_path}")
    for line in train_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("id") == FIXED_DEMO_RECORD_ID:
            return rec
    raise ValueError(f"Fixed demonstration record {FIXED_DEMO_RECORD_ID} not found in {train_path}")


def inspect_peft_layer_status(model: Any, expected_adapter: str = "oopsie_pilot") -> dict[str, Any]:
    """Inspect adapter status across all PEFT layers using model.get_layer_status().

    Inspects:
    - enabled (bool)
    - active_adapters (list or str)
    - merged_adapters (list or bool)
    - available_adapters (list)

    Raises ValueError or AssertionError if:
    - No adapter layers are found
    - Expected status fields are unavailable
    - Layer states are inconsistent across layers
    - Any layer has merged adapters
    - expected_adapter is missing from available_adapters
    """
    if not hasattr(model, "get_layer_status") or not callable(model.get_layer_status):
        raise TypeError(
            f"Model {type(model).__name__} does not implement callable get_layer_status(). "
            "Ensure model is an initialized PeftModel instance."
        )

    statuses = model.get_layer_status()
    if not statuses:
        raise ValueError("No adapter layers found by model.get_layer_status(). Ensure adapters are attached.")

    layer_count = len(statuses)
    enabled_states: list[bool] = []
    merged_states: list[bool] = []
    active_adapter_sets: list[set[str]] = []
    available_adapter_sets: list[set[str]] = []

    for idx, st in enumerate(statuses):
        def get_field(obj: Any, key: str) -> Any:
            if isinstance(obj, dict):
                if key not in obj:
                    raise KeyError(f"Layer status #{idx} missing required field '{key}'")
                return obj[key]
            if not hasattr(obj, key):
                raise AttributeError(f"Layer status #{idx} missing required attribute '{key}'")
            val = getattr(obj, key)
            if callable(val):
                raise TypeError(f"Layer status #{idx} field '{key}' is callable, not state data")
            return val

        # 1. enabled
        enabled_val = get_field(st, "enabled")
        if not isinstance(enabled_val, bool):
            raise TypeError(f"Layer status #{idx} 'enabled' must be bool, got {type(enabled_val).__name__}")
        enabled_states.append(enabled_val)

        # 2. merged_adapters
        merged_val = get_field(st, "merged_adapters")
        if isinstance(merged_val, (list, tuple, set)):
            has_merged = len(merged_val) > 0
        elif isinstance(merged_val, bool):
            has_merged = merged_val
        else:
            raise TypeError(f"Layer status #{idx} 'merged_adapters' must be sequence or bool")
        merged_states.append(has_merged)

        # 3. active_adapters
        act_val = get_field(st, "active_adapters")
        if isinstance(act_val, str):
            act_set = {act_val}
        elif isinstance(act_val, (list, tuple, set)):
            act_set = set(act_val)
        else:
            raise TypeError(f"Layer status #{idx} 'active_adapters' must be sequence or str")
        active_adapter_sets.append(act_set)

        # 4. available_adapters
        avail_val = get_field(st, "available_adapters")
        if isinstance(avail_val, (list, tuple, set)):
            avail_set = set(avail_val)
        else:
            raise TypeError(f"Layer status #{idx} 'available_adapters' must be sequence")
        available_adapter_sets.append(avail_set)

        # Assert expected adapter is among available
        if expected_adapter not in avail_set:
            raise ValueError(
                f"Layer #{idx} does not have expected adapter '{expected_adapter}' in available_adapters: {avail_set}"
            )

    # Cross-layer consistency assertions
    all_enabled = all(enabled_states)
    none_enabled = not any(enabled_states)
    if not (all_enabled or none_enabled):
        raise ValueError(
            f"Inconsistent layer enabled states across {layer_count} layers: "
            f"{sum(enabled_states)} enabled, {layer_count - sum(enabled_states)} disabled."
        )

    any_merged = any(merged_states)
    if any_merged:
        raise ValueError(f"LoRA adapters are merged on {sum(merged_states)}/{layer_count} layers!")

    first_active = active_adapter_sets[0]
    if not all(s == first_active for s in active_adapter_sets):
        raise ValueError("Inconsistent active_adapters across layers.")

    return {
        "layer_count": layer_count,
        "enabled": all_enabled,
        "none_enabled": none_enabled,
        "any_merged": any_merged,
        "active_adapters": sorted(list(first_active)),
        "available_adapters": sorted(list(available_adapter_sets[0])),
    }


@dataclass
class EvaluationCondition:
    name: str
    condition_id: str
    use_adapter: bool
    formatter_id: str
    include_demonstration: bool
    include_schema_in_prompt: bool
    system_prompt_version: str = PROMPT_VERSION_ENUM_GUIDED
    max_new_tokens: int = MAX_NEW_TOKENS
    temperature: float = 0.0
    do_sample: bool = False


# Formal condition specifications
CONDITION_A = EvaluationCondition(
    name="Unadapted Base (Zero-Shot + Schema)",
    condition_id="condition_a_base_zero_shot",
    use_adapter=False,
    formatter_id=FORMATTER_ORIGINAL_EVAL,
    include_demonstration=False,
    include_schema_in_prompt=True,
)

CONDITION_B = EvaluationCondition(
    name="Adapted Pilot (Zero-Shot + Schema, Training-Aligned)",
    condition_id="condition_b_adapter_zero_shot",
    use_adapter=True,
    formatter_id=FORMATTER_TRAINING_ALIGNED,
    include_demonstration=False,
    include_schema_in_prompt=True,
)

CONDITION_C = EvaluationCondition(
    name="Unadapted Base (1-Shot + Schema)",
    condition_id="condition_c_base_one_shot",
    use_adapter=False,
    formatter_id=FORMATTER_ORIGINAL_EVAL,
    include_demonstration=True,
    include_schema_in_prompt=True,
)

CONDITION_D = EvaluationCondition(
    name="Adapted Pilot (Current Enum-Guided Service Prompt, Deployment Baseline)",
    condition_id="condition_d_adapter_current_service",
    use_adapter=True,
    formatter_id=FORMATTER_TRAINING_ALIGNED,
    include_demonstration=False,
    include_schema_in_prompt=False,
    system_prompt_version=PROMPT_VERSION_ENUM_GUIDED,
)

CONDITIONS: dict[str, EvaluationCondition] = {
    "cond_a": CONDITION_A,
    "cond_b": CONDITION_B,
    "cond_c": CONDITION_C,
    "cond_d": CONDITION_D,
}


def render_prompt_for_condition(
    record: dict[str, Any],
    condition: EvaluationCondition,
    tokenizer: Any,
    fixed_demo: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, str]]]:
    """Construct messages and render formatted prompt string according to condition rules."""
    sys_content = get_system_prompt(condition.system_prompt_version)

    if condition.include_schema_in_prompt:
        schema_path = ROOT / "data" / "schema.json"
        schema_text = schema_path.read_text(encoding="utf-8")
        sys_content += (
            f"\n\nComplete Output JSON Schema:\n```json\n{schema_text}\n```\n"
            "Respond ONLY with a valid JSON object strictly conforming to this schema."
        )

    messages: list[dict[str, str]] = [{"role": "system", "content": sys_content}]

    if condition.include_demonstration:
        if fixed_demo is None:
            fixed_demo = load_fixed_demonstration()
        demo_input = fixed_demo["model_input"]["raw_error"]
        demo_context = fixed_demo["model_input"].get("context")
        demo_user_str = format_user_prompt(demo_input, demo_context)
        demo_target_str = json.dumps(fixed_demo["target_report"], indent=2)

        messages.append({"role": "user", "content": demo_user_str})
        messages.append({"role": "assistant", "content": demo_target_str})

    raw_error = record.get("model_input", {}).get("raw_error") or record.get("raw_error") or ""
    context = record.get("model_input", {}).get("context") or record.get("context")
    if context is None and ("framework" in record or "platform" in record):
        context = {}
        if record.get("framework"):
            context["framework"] = record["framework"]
        if record.get("platform"):
            context["environment"] = record["platform"]
    user_str = format_user_prompt(raw_error, context)
    messages.append({"role": "user", "content": user_str})

    if condition.formatter_id == FORMATTER_TRAINING_ALIGNED:
        rendered = format_training_aligned(messages, tokenizer)
    elif condition.formatter_id == FORMATTER_ORIGINAL_EVAL:
        rendered = format_original_eval(messages, tokenizer)
    else:
        raise ValueError(f"Unknown formatter_id: {condition.formatter_id}")

    return rendered, messages


@dataclass
class CaseEvaluationResult:
    case_id: str
    condition_id: str
    prompt_hash: str
    prompt_token_count: int
    gen_token_count: int
    hit_budget: bool
    eos_detected: bool
    duration_seconds: float
    raw_completion: str
    raw_with_specials: str
    json_valid: bool
    schema_valid: bool
    validation_errors: list[str] = field(default_factory=list)
    generated_category: str | None = None
    reference_category: str | None = None
    category_match: bool | None = None
    safety_audit: dict[str, Any] = field(default_factory=dict)
    generation_failed: bool = False
    exception_thrown: str | None = None
    adapter_state_verified: bool = False


def evaluate_single_case(
    record: dict[str, Any],
    condition: EvaluationCondition,
    model: Any,
    tokenizer: Any,
    torch_device: str = "cuda",
    fixed_demo: dict[str, Any] | None = None,
) -> CaseEvaluationResult:
    """Execute a single evaluation case under the designated condition with strict adapter management."""
    import torch

    case_id = record.get("id", "unknown_id")
    ref_cat = (
        record.get("reference_annotations", {}).get("reference_category")
        or record.get("target_report", {}).get("error_category")
        or record.get("expected_category")
    )

    t0 = time.perf_counter()
    try:
        prompt_str, _ = render_prompt_for_condition(record, condition, tokenizer, fixed_demo)
        prompt_hash = hashlib.sha256(prompt_str.encode("utf-8")).hexdigest()

        inputs = tokenizer(prompt_str, return_tensors="pt").to(torch_device)
        prompt_len = inputs["input_ids"].shape[1]

        if prompt_len + condition.max_new_tokens > VERIFIED_CONTEXT_LIMIT:
            raise ValueError(
                f"CONTEXT_LIMIT_EXCEEDED: Prompt length ({prompt_len}) + max_new_tokens ({condition.max_new_tokens}) "
                f"exceeds verified context limit ({VERIFIED_CONTEXT_LIMIT})."
            )

        adapter_verified = False

        if condition.use_adapter:
            model.set_adapter("oopsie_pilot")
            pre_state = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
            assert pre_state["enabled"] is True, f"Condition B requires enabled layers, got: {pre_state}"
            assert "oopsie_pilot" in pre_state["active_adapters"], f"Wrong active adapter: {pre_state}"
            assert pre_state["any_merged"] is False, "LoRA weights are merged into base weights!"
            adapter_verified = True

            with torch.no_grad():
                output_tokens = model.generate(
                    **inputs,
                    max_new_tokens=condition.max_new_tokens,
                    do_sample=condition.do_sample,
                    temperature=condition.temperature,
                    pad_token_id=tokenizer.eos_token_id,
                )
        else:
            with model.disable_adapter():
                inside_state = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
                assert inside_state["none_enabled"] is True, f"Condition A/C requires disabled layers, got: {inside_state}"
                assert inside_state["any_merged"] is False, "LoRA weights are merged into base weights!"
                adapter_verified = True

                with torch.no_grad():
                    output_tokens = model.generate(
                        **inputs,
                        max_new_tokens=condition.max_new_tokens,
                        do_sample=condition.do_sample,
                        temperature=condition.temperature,
                        pad_token_id=tokenizer.eos_token_id,
                    )

            # Verify restoration after context exit
            after_state = inspect_peft_layer_status(model, expected_adapter="oopsie_pilot")
            assert after_state["enabled"] is True, f"Failed to restore adapter state after context exit: {after_state}"

        new_tokens = output_tokens[0][prompt_len:]
        gen_len = len(new_tokens)
        hit_budget = gen_len >= condition.max_new_tokens
        eos_detected = tokenizer.eos_token_id in new_tokens.tolist()

        raw_completion = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        raw_with_specials = tokenizer.decode(new_tokens, skip_special_tokens=False)
        duration = time.perf_counter() - t0

        json_valid = False
        schema_valid = False
        val_errors: list[str] = []
        gen_cat: str | None = None
        cat_match: bool | None = None

        try:
            parsed = strict_parse_raw_completion(raw_completion)
            json_valid = True
            gen_cat = parsed.get("error_category")
            if ref_cat and gen_cat:
                cat_match = str(gen_cat).strip().lower() == str(ref_cat).strip().lower()

            try:
                validate_oopsie_report(parsed)
                schema_valid = True
            except SchemaValidationError as sve:
                val_errors = sve.errors
        except ParseError as pe:
            val_errors = [str(pe)]

        safety_res = check_heuristic_safety(raw_completion)

        return CaseEvaluationResult(
            case_id=case_id,
            condition_id=condition.condition_id,
            prompt_hash=prompt_hash,
            prompt_token_count=prompt_len,
            gen_token_count=gen_len,
            hit_budget=hit_budget,
            eos_detected=eos_detected,
            duration_seconds=round(duration, 3),
            raw_completion=raw_completion,
            raw_with_specials=raw_with_specials[:1000],
            json_valid=json_valid,
            schema_valid=schema_valid,
            validation_errors=val_errors,
            generated_category=gen_cat,
            reference_category=ref_cat,
            category_match=cat_match,
            safety_audit=safety_res,
            generation_failed=False,
            exception_thrown=None,
            adapter_state_verified=adapter_verified,
        )

    except Exception as exc:
        duration = time.perf_counter() - t0
        return CaseEvaluationResult(
            case_id=case_id,
            condition_id=condition.condition_id,
            prompt_hash="ERROR",
            prompt_token_count=0,
            gen_token_count=0,
            hit_budget=False,
            eos_detected=False,
            duration_seconds=round(duration, 3),
            raw_completion="",
            raw_with_specials="",
            json_valid=False,
            schema_valid=False,
            validation_errors=[f"GenerationException: {str(exc)}"],
            generated_category=None,
            reference_category=ref_cat,
            category_match=False,
            safety_audit={"safety_pass": False, "destructive_matches": []},
            generation_failed=True,
            exception_thrown=str(exc),
            adapter_state_verified=False,
        )


def load_checkpoint_records(
    checkpoint_path: Path,
) -> tuple[dict[tuple[str, str], CaseEvaluationResult], list[dict[str, Any]], list[str]]:
    """Safely read incremental checkpoint records from JSONL with corruption isolation.

    Guarantees:
    - Parses line-by-line.
    - Catches and isolates partial/corrupt trailing lines (e.g. from an abrupt session termination)
      as uncommitted incomplete attempts rather than scored model failures.
    - Detects duplicate (case_id, condition_key) pairs: rejects conflicting duplicates with ValueError
      and logs redundant duplicates.
    - Returns (completed_records_dict, incomplete_attempts_list, audit_warnings_list).
    """
    completed: dict[tuple[str, str], CaseEvaluationResult] = {}
    incomplete: list[dict[str, Any]] = []
    warnings: list[str] = []

    if not checkpoint_path.exists():
        return completed, incomplete, warnings

    lines = checkpoint_path.read_text(encoding="utf-8").splitlines()
    for line_num, line in enumerate(lines, 1):
        raw_line = line.strip()
        if not raw_line:
            continue
        try:
            entry = json.loads(raw_line)
        except json.JSONDecodeError as err:
            warning_msg = f"Line {line_num} truncated or corrupt ({err.msg}); logged as uncommitted incomplete attempt."
            warnings.append(warning_msg)
            incomplete.append({"line_num": line_num, "error": str(err), "raw_fragment": raw_line[:200]})
            continue

        cid = entry.get("case_id")
        ckey = entry.get("condition_key")
        res_data = entry.get("result")

        if not cid or not ckey or not isinstance(res_data, dict):
            warnings.append(f"Line {line_num} missing required envelope keys.")
            incomplete.append({"line_num": line_num, "entry": entry})
            continue

        key = (cid, ckey)
        res_obj = CaseEvaluationResult(**res_data)

        if key in completed:
            existing = completed[key]
            if existing.schema_valid == res_obj.schema_valid and existing.raw_completion == res_obj.raw_completion:
                warnings.append(f"Line {line_num}: Redundant identical record for {key}; retained existing.")
            else:
                raise ValueError(
                    f"Conflicting duplicate record detected at line {line_num} for {key}! "
                    f"Existing schema_valid={existing.schema_valid}, new schema_valid={res_obj.schema_valid}."
                )
        else:
            completed[key] = res_obj

    return completed, incomplete, warnings


def generate_blinded_review_sheet(
    cases_results: dict[str, dict[str, CaseEvaluationResult]],
    records_by_id: dict[str, dict[str, Any]],
    output_path: Path,
    key_output_path: Path | None = None,
    seed: int = 42,
) -> None:
    """Generate a blinded, randomized human evaluation markdown sheet and separate unblinding key."""
    rng = random.Random(seed)
    lines: list[str] = [
        "# OOPSIE Blinded Human Technical Review Sheet",
        "",
        "> **Review Guidelines**:",
        "> - Evaluate each anonymized candidate output on factual correctness, risk warning scope, and verification usefulness.",
        "> - System labels (System Alpha, System Beta, System Gamma, System Delta) are randomized per case to prevent bias.",
        "> - All scoring fields are intentionally left blank for manual human evaluation.",
        "> - Unblinding keys are stored in a separate file (unblinded_review_key.json) and must remain concealed until all manual ratings are locked.",
        "",
        "---",
        "",
    ]

    unblinded_key: dict[str, dict[str, str]] = {}

    for case_id in sorted(cases_results.keys()):
        cond_map = cases_results[case_id]
        rec = records_by_id.get(case_id, {})
        raw_error = rec.get("model_input", {}).get("raw_error") or rec.get("raw_error") or "N/A"
        context = rec.get("model_input", {}).get("context") or rec.get("context") or {}

        lines.extend([
            f"## Case: `{case_id}`",
            "",
            "### Developer Error Input",
            "```",
            raw_error,
            "```",
            f"**Context**: {context}",
            "",
            "---",
            "",
        ])

        cond_keys = list(cond_map.keys())
        rng.shuffle(cond_keys)
        labels = ["System Alpha", "System Beta", "System Gamma", "System Delta"][: len(cond_keys)]
        unblinded_key[case_id] = {label: ckey for label, ckey in zip(labels, cond_keys)}

        for label, ckey in zip(labels, cond_keys):
            res = cond_map[ckey]
            lines.extend([
                f"### {label}",
                "",
                "```json",
                res.raw_completion if res.raw_completion else "(Empty / Unparseable Completion)",
                "```",
                "",
                f"- **Parsed JSON**: {'PASS' if res.json_valid else 'FAIL'}",
                f"- **Schema Valid**: {'PASS' if res.schema_valid else 'FAIL'}",
                f"- **Budget Hit (1024 tokens)**: {'YES' if res.hit_budget else 'NO'}",
                f"- **Generation Failed**: {'YES (' + str(res.exception_thrown) + ')' if res.generation_failed else 'NO'}",
                "",
                "#### Human Scoring Rubric (Fill in for manual review):",
                "1. **Technical Correctness** [Pass / Partial / Fail]: _________",
                "2. **Unsupported Claims** [None / Minor / Severe]: _________",
                "3. **Appropriate Uncertainty** [Pass / Overconfident]: _________",
                "4. **Repair Scope Actionable** [Pass / Vague / Harmful]: _________",
                "5. **Verification Steps Useful** [Pass / Incomplete / Fail]: _________",
                "",
                "**Reviewer Notes**: ____________________________________________________",
                "",
                "---",
                "",
            ])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    if key_output_path is not None:
        key_output_path.parent.mkdir(parents=True, exist_ok=True)
        key_output_path.write_text(json.dumps(unblinded_key, indent=2), encoding="utf-8")
