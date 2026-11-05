"""Unit tests for the 4-condition frozen benchmark protocol and input contract."""

import json
from pathlib import Path

import pytest

from evaluation.harness import (
    CONDITION_A,
    CONDITION_B,
    CONDITION_C,
    CONDITION_D,
    CONDITIONS,
    EXPECTED_PROMPT_V2_HASH,
    EXPECTED_SCHEMA_HASH,
    generate_blinded_review_sheet,
    render_prompt_for_condition,
    verify_integrity_hashes,
)
from inference.config import PROMPT_VERSION_ENUM_GUIDED
from inference.formatters import get_system_prompt

ROOT = Path(__file__).resolve().parents[1]


class DummyTokenizer:
    def __init__(self):
        self.eos_token_id = 1
        self.pad_token_id = 0

    def apply_chat_template(self, messages, add_generation_prompt=True, tokenize=False):
        parts = []
        for m in messages:
            parts.append(f"<start_of_turn>{m['role']}\n{m['content']}<end_of_turn>")
        if add_generation_prompt:
            parts.append("<start_of_turn>model\n")
        return "\n".join(parts)


def test_four_conditions_frozen_specification():
    """Assert the exact 4-condition specification requested by the research protocol."""
    assert len(CONDITIONS) == 4
    assert set(CONDITIONS.keys()) == {"cond_a", "cond_b", "cond_c", "cond_d"}

    # Condition A: Base Zero-Shot + Schema
    assert CONDITION_A.use_adapter is False
    assert CONDITION_A.formatter_id == "original_eval_v1"
    assert CONDITION_A.include_schema_in_prompt is True
    assert CONDITION_A.include_demonstration is False
    assert CONDITION_A.system_prompt_version == PROMPT_VERSION_ENUM_GUIDED

    # Condition B: Adapter Zero-Shot + Schema
    assert CONDITION_B.use_adapter is True
    assert CONDITION_B.formatter_id == "training_aligned_v1"
    assert CONDITION_B.include_schema_in_prompt is True
    assert CONDITION_B.include_demonstration is False
    assert CONDITION_B.system_prompt_version == PROMPT_VERSION_ENUM_GUIDED

    # Condition C: Base 1-Shot + Schema
    assert CONDITION_C.use_adapter is False
    assert CONDITION_C.formatter_id == "original_eval_v1"
    assert CONDITION_C.include_schema_in_prompt is True
    assert CONDITION_C.include_demonstration is True
    assert CONDITION_C.system_prompt_version == PROMPT_VERSION_ENUM_GUIDED

    # Condition D: Adapter Current Service Prompt (No Schema)
    assert CONDITION_D.use_adapter is True
    assert CONDITION_D.formatter_id == "training_aligned_v1"
    assert CONDITION_D.include_schema_in_prompt is False
    assert CONDITION_D.include_demonstration is False
    assert CONDITION_D.system_prompt_version == PROMPT_VERSION_ENUM_GUIDED


def test_integrity_hashes_verify():
    """Verify data/schema.json and system prompt v2 match expected SHA-256 hashes."""
    hashes = verify_integrity_hashes()
    assert hashes["schema_hash"] == EXPECTED_SCHEMA_HASH
    assert hashes["system_prompt_hash"] == EXPECTED_PROMPT_V2_HASH


def test_condition_d_prompt_has_no_schema_block():
    """Verify Condition D contains enum guidance but does not append the raw JSON schema."""
    tokenizer = DummyTokenizer()
    dummy_record = {
        "id": "dummy-01",
        "raw_error": "SyntaxError: Unexpected token",
        "framework": "React",
        "platform": "browser",
    }
    rendered_b, msgs_b = render_prompt_for_condition(dummy_record, CONDITION_B, tokenizer)
    rendered_d, msgs_d = render_prompt_for_condition(dummy_record, CONDITION_D, tokenizer)

    # Condition B has the schema markdown block
    assert "Complete Output JSON Schema:" in msgs_b[0]["content"]
    assert "```json" in msgs_b[0]["content"]

    # Condition D does NOT have the schema markdown block
    assert "Complete Output JSON Schema:" not in msgs_d[0]["content"]
    assert "```json" not in msgs_d[0]["content"]

    # Condition D DOES have the enum guidance
    assert "The error_category field must be exactly one of:" in msgs_d[0]["content"]
    assert "'authentication'" in msgs_d[0]["content"]


def test_benchmark_input_contract_and_deterministic_context():
    """Verify all 40 benchmark records map without error across all 4 conditions."""
    benchmark_path = ROOT / "evaluation" / "benchmark.jsonl"
    assert benchmark_path.exists()
    records = [json.loads(l) for l in benchmark_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(records) == 40

    tokenizer = DummyTokenizer()

    for rec in records:
        assert "id" in rec
        assert "raw_error" in rec
        assert "expected_category" in rec

        # Check rendering across all 4 conditions
        for ckey, cond in CONDITIONS.items():
            rendered, msgs = render_prompt_for_condition(rec, cond, tokenizer)
            assert len(rendered) > 50
            # User message must contain raw error and mapped framework/environment context
            user_msg = msgs[-1]["content"]
            assert rec["raw_error"].strip() in user_msg
            if rec.get("framework"):
                assert f"- Framework/Runtime: {rec['framework']}" in user_msg
            if rec.get("platform"):
                assert f"- Environment: {rec['platform']}" in user_msg


def test_blinded_review_sheet_four_conditions_and_separate_key(tmp_path):
    """Test 4-condition blinded review sheet generation and separate unblinding key."""
    from evaluation.harness import CaseEvaluationResult

    dummy_results = {
        "case-01": {
            "cond_a": CaseEvaluationResult(
                case_id="case-01", condition_id="cond_a", prompt_hash="hA",
                prompt_token_count=100, gen_token_count=50, hit_budget=False,
                eos_detected=True, duration_seconds=1.0, raw_completion="output A",
                raw_with_specials="output A", json_valid=False, schema_valid=False
            ),
            "cond_b": CaseEvaluationResult(
                case_id="case-01", condition_id="cond_b", prompt_hash="hB",
                prompt_token_count=100, gen_token_count=50, hit_budget=False,
                eos_detected=True, duration_seconds=1.0, raw_completion="output B",
                raw_with_specials="output B", json_valid=True, schema_valid=True
            ),
            "cond_c": CaseEvaluationResult(
                case_id="case-01", condition_id="cond_c", prompt_hash="hC",
                prompt_token_count=100, gen_token_count=50, hit_budget=False,
                eos_detected=True, duration_seconds=1.0, raw_completion="output C",
                raw_with_specials="output C", json_valid=False, schema_valid=False
            ),
            "cond_d": CaseEvaluationResult(
                case_id="case-01", condition_id="cond_d", prompt_hash="hD",
                prompt_token_count=80, gen_token_count=40, hit_budget=False,
                eos_detected=True, duration_seconds=0.8, raw_completion="output D",
                raw_with_specials="output D", json_valid=True, schema_valid=True
            ),
        }
    }
    dummy_records = {"case-01": {"id": "case-01", "raw_error": "Err text"}}

    sheet_path = tmp_path / "sheet.md"
    key_path = tmp_path / "key.json"

    generate_blinded_review_sheet(dummy_results, dummy_records, sheet_path, key_path)

    assert sheet_path.exists()
    assert key_path.exists()

    sheet_text = sheet_path.read_text(encoding="utf-8")
    assert "System Alpha" in sheet_text
    assert "System Beta" in sheet_text
    assert "System Gamma" in sheet_text
    assert "System Delta" in sheet_text

    # Verify key JSON maps all 4 labels
    key_data = json.loads(key_path.read_text(encoding="utf-8"))
    assert "case-01" in key_data
    labels_mapped = set(key_data["case-01"].keys())
    assert labels_mapped == {"System Alpha", "System Beta", "System Gamma", "System Delta"}
    conditions_mapped = set(key_data["case-01"].values())
    assert conditions_mapped == {"cond_a", "cond_b", "cond_c", "cond_d"}


def test_load_checkpoint_records_resilience(tmp_path):
    """Test checkpoint loading with corrupt trailing line, duplicate detection, and resumption."""
    from evaluation.harness import CaseEvaluationResult, asdict, load_checkpoint_records

    res1 = CaseEvaluationResult(
        case_id="case-01", condition_id="cond_a", prompt_hash="h1",
        prompt_token_count=50, gen_token_count=20, hit_budget=False,
        eos_detected=True, duration_seconds=0.5, raw_completion="{}",
        raw_with_specials="{}", json_valid=True, schema_valid=True
    )
    res2 = CaseEvaluationResult(
        case_id="case-01", condition_id="cond_b", prompt_hash="h2",
        prompt_token_count=50, gen_token_count=20, hit_budget=False,
        eos_detected=True, duration_seconds=0.5, raw_completion="{}",
        raw_with_specials="{}", json_valid=True, schema_valid=True
    )
    res1_conflict = CaseEvaluationResult(
        case_id="case-01", condition_id="cond_a", prompt_hash="h1",
        prompt_token_count=50, gen_token_count=20, hit_budget=False,
        eos_detected=True, duration_seconds=0.5, raw_completion="different",
        raw_with_specials="different", json_valid=False, schema_valid=False
    )

    ckpt_file = tmp_path / "checkpoint.jsonl"

    # 1. Normal lines + redundant line + incomplete trailing fragment
    line1 = json.dumps({"case_id": "case-01", "condition_key": "cond_a", "result": asdict(res1)})
    line2 = json.dumps({"case_id": "case-01", "condition_key": "cond_b", "result": asdict(res2)})
    line3 = json.dumps({"case_id": "case-01", "condition_key": "cond_a", "result": asdict(res1)})  # identical duplicate
    trailing_fragment = '{"case_id": "case-02", "condition_key": "cond_a", "result": {"raw_completion": "unfini'

    ckpt_file.write_text(f"{line1}\n{line2}\n{line3}\n{trailing_fragment}\n", encoding="utf-8")

    completed, incomplete, warnings = load_checkpoint_records(ckpt_file)

    # Completed records should have exactly the 2 valid keys
    assert len(completed) == 2
    assert ("case-01", "cond_a") in completed
    assert ("case-01", "cond_b") in completed

    # Incomplete records must capture the trailing fragment without throwing
    assert len(incomplete) == 1
    assert incomplete[0]["line_num"] == 4

    # Warnings should mention the duplicate and the truncated line
    assert any("Redundant identical record" in w for w in warnings)
    assert any("truncated or corrupt" in w for w in warnings)

    # 2. Conflicting duplicate must raise ValueError
    conflict_file = tmp_path / "conflict.jsonl"
    line_conflict = json.dumps({"case_id": "case-01", "condition_key": "cond_a", "result": asdict(res1_conflict)})
    conflict_file.write_text(f"{line1}\n{line_conflict}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="Conflicting duplicate record detected"):
        load_checkpoint_records(conflict_file)
