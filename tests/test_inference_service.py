"""Comprehensive unit test suite for the experimental OOPSIE inference service.

All tests use MockInferenceEngine and run without GPU access or model weights.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from typing import Any

import unittest

try:
    import pytest
    from starlette.testclient import TestClient
    from inference.api.main import app, get_semaphore
except ImportError as exc:
    raise unittest.SkipTest(
        f"Skipping test_inference_service: {exc}. Install 'oopsie-ai[test]'."
    )
from inference.config import (
    CONFIG_VERSION,
    DEFAULT_FORMATTER,
    FORMATTER_ORIGINAL_EVAL,
    FORMATTER_TRAINING_ALIGNED,
    MAX_INPUT_CHARS,
    MODEL_VERSION,
    PROMPT_VERSION_ENUM_GUIDED,
    PROMPT_VERSION_FROZEN,
)
from inference.engine import (
    ContextWindowExceededError,
    GenerationResult,
    MockInferenceEngine,
    set_engine,
)

client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def reset_engine():
    """Ensure each test runs with a fresh, ready MockInferenceEngine and clean semaphore."""
    import inference.api.main as api_main
    api_main._concurrency_semaphore = threading.Semaphore(1)
    mock = MockInferenceEngine(ready=True)
    set_engine(mock)
    yield mock
    set_engine(None)
    api_main._concurrency_semaphore = None


# 1. Health and Readiness Checks
def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "oopsie-inference"
    assert data["version"] == CONFIG_VERSION


def test_ready_endpoint_when_model_ready(reset_engine: MockInferenceEngine):
    reset_engine.set_ready(True)
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["model_ready"] is True
    assert data["model_version"] == MODEL_VERSION


def test_ready_endpoint_when_model_unready(reset_engine: MockInferenceEngine):
    reset_engine.set_ready(False)
    resp = client.get("/ready")
    assert resp.status_code == 503
    data = resp.json()
    assert data["status"] == "not_ready"
    assert data["model_ready"] is False


# 2. Valid Request and Schema-Valid Output
def test_valid_request_returns_success_envelope(reset_engine: MockInferenceEngine):
    payload = {
        "error_text": "FATAL: connection to server on socket failed: Connection refused",
        "context": {
            "language_or_framework": "PostgreSQL",
            "environment": "local_development",
        },
    }
    resp = client.post("/v1/analyze", json=payload)
    assert resp.status_code == 200
    body = resp.json()

    assert body["status"] == "success"
    assert "request_id" in body and body["request_id"]
    assert body["model_version"] == MODEL_VERSION
    assert body["formatter_version"] == DEFAULT_FORMATTER

    data = body["data"]
    assert "summary" in data
    assert "likely_causes" in data
    assert "recovery_steps" not in data or isinstance(data.get("recovery_steps"), list)
    assert "risk_level" in data
    assert "repair_prompt" in data

    metadata = body["metadata"]
    assert metadata["prompt_tokens"] > 0
    assert metadata["generated_tokens"] > 0
    assert metadata["budget_hit"] is False
    assert "duration_ms" in metadata


# 3. Input Validation (Empty, Whitespace, Oversized)
def test_empty_input_rejected():
    resp = client.post("/v1/analyze", json={"error_text": ""})
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_INPUT"


def test_whitespace_only_input_rejected():
    resp = client.post("/v1/analyze", json={"error_text": "   \n\t   "})
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_INPUT"


def test_oversized_input_rejected():
    oversized = "A" * (MAX_INPUT_CHARS + 1)
    resp = client.post("/v1/analyze", json={"error_text": oversized})
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_INPUT"


def test_context_window_exceeded_error(reset_engine: MockInferenceEngine):
    reset_engine.simulated_exception = ContextWindowExceededError(
        "Input prompt tokens (7200) + max_new_tokens (1024) exceeds limit (8192)."
    )
    resp = client.post("/v1/analyze", json={"error_text": "large error text"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_INPUT"
    assert "exceeds limit" in body["error"]["message"]


# 4. Strict Raw Parsing: Reject Syntax Errors, Duplicates, and Non-Standard Numbers
def test_invalid_json_syntax_rejected(reset_engine: MockInferenceEngine):
    reset_engine.canned_completion = '{"summary": "Incomplete text'
    resp = client.post("/v1/analyze", json={"error_text": "syntax error log"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "PARSE_ERROR"


def test_duplicate_json_keys_rejected(reset_engine: MockInferenceEngine):
    # Valid report json but with duplicate key
    valid_copy = dict(MockInferenceEngine.DEFAULT_VALID_REPORT)
    dumped = json.dumps(valid_copy)
    # Inject duplicate key at the front
    duplicate_json = '{"summary": "Duplicate summary", ' + dumped[1:]
    reset_engine.canned_completion = duplicate_json

    resp = client.post("/v1/analyze", json={"error_text": "some error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "PARSE_ERROR"
    assert "Duplicate JSON key detected" in body["error"]["message"]


def test_non_standard_numbers_rejected(reset_engine: MockInferenceEngine):
    # Inject NaN or Infinity
    non_standard = json.dumps(MockInferenceEngine.DEFAULT_VALID_REPORT).replace(
        '"risk_level": "low"', '"risk_level": "low", "bad_val": NaN'
    )
    reset_engine.canned_completion = non_standard
    resp = client.post("/v1/analyze", json={"error_text": "some error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "PARSE_ERROR"


def test_no_silent_markdown_fence_stripping(reset_engine: MockInferenceEngine):
    # Completion wrapped in markdown code fence ```json ... ```
    # Under strict raw parsing, markdown fences are NOT silently stripped!
    raw_markdown = f"```json\n{json.dumps(MockInferenceEngine.DEFAULT_VALID_REPORT)}\n```"
    reset_engine.canned_completion = raw_markdown

    resp = client.post("/v1/analyze", json={"error_text": "some error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "PARSE_ERROR"


# 5. Schema Validation Failures
def test_schema_invalid_missing_required_keys(reset_engine: MockInferenceEngine):
    # Missing 'risk_level' and 'repair_prompt'
    incomplete = {
        "summary": "Incomplete report",
        "plain_explanation": "Missing required fields.",
        "error_category": "runtime",
        "likely_causes": [],
    }
    reset_engine.canned_completion = json.dumps(incomplete)
    resp = client.post("/v1/analyze", json={"error_text": "some error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "SCHEMA_ERROR"


def test_schema_invalid_bad_enum_value(reset_engine: MockInferenceEngine):
    bad_enum = dict(MockInferenceEngine.DEFAULT_VALID_REPORT)
    bad_enum["risk_level"] = "critical"  # Allowed: low, medium, high
    reset_engine.canned_completion = json.dumps(bad_enum)

    resp = client.post("/v1/analyze", json={"error_text": "some error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "SCHEMA_ERROR"


# 6. Output Budget Termination Policy
def test_output_budget_termination_rejected(reset_engine: MockInferenceEngine):
    # When model reached max_new_tokens without emitting EOS
    reset_engine.hit_budget = True
    resp = client.post("/v1/analyze", json={"error_text": "infinite loop error"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "OUTPUT_BUDGET_EXCEEDED"
    assert "maximum token budget" in body["error"]["message"]


# 7. Model Unavailability & Generation Failure
def test_model_unavailable_returns_503(reset_engine: MockInferenceEngine):
    reset_engine.set_ready(False)
    resp = client.post("/v1/analyze", json={"error_text": "any error"})
    assert resp.status_code == 503
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "MODEL_UNAVAILABLE"


def test_generation_exception_returns_500(reset_engine: MockInferenceEngine):
    reset_engine.simulated_exception = RuntimeError("CUDA out of memory: tried to allocate 2.0 GiB")
    resp = client.post("/v1/analyze", json={"error_text": "heavy error log"})
    assert resp.status_code == 500
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "GENERATION_ERROR"
    # Verify no raw stack trace or CUDA details are leaked to client
    assert "CUDA" not in body["error"]["message"]


# 8. Capacity Limit / Concurrency Bounding
def test_capacity_limit_returns_429():
    # Acquire the semaphore to simulate saturation
    sem = get_semaphore()
    assert sem.acquire(blocking=False) is True

    try:
        resp = client.post("/v1/analyze", json={"error_text": "concurrent request"})
        assert resp.status_code == 429
        body = resp.json()
        assert body["status"] == "error"
        assert body["error"]["code"] == "CAPACITY_LIMIT"
    finally:
        sem.release()


# 9. Formatter Selection
def test_formatter_selection_training_aligned():
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "formatter": FORMATTER_TRAINING_ALIGNED,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["formatter_version"] == FORMATTER_TRAINING_ALIGNED


def test_formatter_selection_original_eval():
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "formatter": FORMATTER_ORIGINAL_EVAL,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["formatter_version"] == FORMATTER_ORIGINAL_EVAL


def test_unsupported_formatter_rejected():
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "formatter": "unsupported_template_v9",
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert "formatter" in body["error"]["message"] or "Unsupported formatter" in body["error"]["message"]


# 9b. System Prompt Condition Selection & Downstream Capturing
def test_version_a_produces_original_system_prompt():
    from inference.formatters import SYSTEM_PROMPT_V1, get_system_prompt
    prompt_a = get_system_prompt(PROMPT_VERSION_FROZEN)
    assert prompt_a == SYSTEM_PROMPT_V1
    assert "The error_category field must be exactly one of:" not in prompt_a


def test_version_b_includes_enum_values_from_actual_schema():
    from inference.config import get_schema_path
    from inference.formatters import get_system_prompt
    schema = json.loads(get_schema_path().read_text(encoding="utf-8"))
    enums = schema["properties"]["error_category"]["enum"]
    prompt_b = get_system_prompt(PROMPT_VERSION_ENUM_GUIDED)

    assert "The error_category field must be exactly one of:" in prompt_b
    assert "Use 'unknown' when the evidence does not clearly support another allowed category." in prompt_b
    for cat in enums:
        assert f"'{cat}'" in prompt_b
    assert len(enums) == 14
    # Confirm no accidental substitution of filename without guidance
    assert prompt_b != "data/schema.json"
    assert len(prompt_b) > len(enums) * 10


def test_version_b_passed_through_real_service_to_engine_path(reset_engine: MockInferenceEngine):
    from inference.formatters import get_system_prompt
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample syntax error",
            "system_prompt_version": PROMPT_VERSION_ENUM_GUIDED,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["system_prompt_version"] == PROMPT_VERSION_ENUM_GUIDED

    # Inspect the capturing engine to verify what was received downstream
    assert reset_engine.last_system_prompt_version == PROMPT_VERSION_ENUM_GUIDED
    assert reset_engine.last_messages is not None
    assert reset_engine.last_messages[0]["role"] == "system"
    assert reset_engine.last_messages[0]["content"] == get_system_prompt(PROMPT_VERSION_ENUM_GUIDED)
    assert "The error_category field must be exactly one of:" in reset_engine.last_messages[0]["content"]


def test_default_behavior_is_now_enum_guided(reset_engine: MockInferenceEngine):
    from inference.formatters import get_system_prompt
    resp = client.post(
        "/v1/analyze",
        json={"error_text": "sample syntax error"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["system_prompt_version"] == PROMPT_VERSION_ENUM_GUIDED

    # Verify downstream capturing engine received enum-guided prompt
    assert reset_engine.last_system_prompt_version == PROMPT_VERSION_ENUM_GUIDED
    assert reset_engine.last_messages is not None
    assert reset_engine.last_messages[0]["role"] == "system"
    assert reset_engine.last_messages[0]["content"] == get_system_prompt(PROMPT_VERSION_ENUM_GUIDED)
    assert "The error_category field must be exactly one of:" in reset_engine.last_messages[0]["content"]


def test_frozen_version_a_remains_available_for_reproducibility(reset_engine: MockInferenceEngine):
    from inference.formatters import get_system_prompt
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample syntax error",
            "system_prompt_version": PROMPT_VERSION_FROZEN,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["metadata"]["system_prompt_version"] == PROMPT_VERSION_FROZEN

    # Verify downstream capturing engine received frozen prompt
    assert reset_engine.last_system_prompt_version == PROMPT_VERSION_FROZEN
    assert reset_engine.last_messages is not None
    assert reset_engine.last_messages[0]["role"] == "system"
    assert reset_engine.last_messages[0]["content"] == get_system_prompt(PROMPT_VERSION_FROZEN)
    assert "The error_category field must be exactly one of:" not in reset_engine.last_messages[0]["content"]



def test_unsupported_system_prompt_version_rejected():
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "system_prompt_version": "unknown_prompt_condition_v99",
        },
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["status"] == "error"
    assert body["error"]["code"] == "INVALID_INPUT"


def test_misspelled_or_unexpected_selection_fields_fail_validation():
    # Attempting to pass misspelled or unknown experiment parameters must fail validation
    resp1 = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "prompt_version": "system_prompt_v2_enum_guided",  # misspelled key
        },
    )
    assert resp1.status_code == 400
    body1 = resp1.json()
    assert body1["status"] == "error"
    assert body1["error"]["code"] == "INVALID_INPUT"
    assert "Extra inputs are not permitted" in body1["error"]["message"]

    resp2 = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "sys_prompt": "system_prompt_v1",  # unexpected key
        },
    )
    assert resp2.status_code == 400
    body2 = resp2.json()
    assert body2["error"]["code"] == "INVALID_INPUT"
    assert "Extra inputs are not permitted" in body2["error"]["message"]


def test_free_form_user_context_fields_permitted(reset_engine: MockInferenceEngine):
    # Context dictionary must remain open to arbitrary user metadata
    resp = client.post(
        "/v1/analyze",
        json={
            "error_text": "sample error",
            "context": {
                "custom_language": "rust",
                "nested_toolchain": {"cargo_version": "1.80.0"},
                "arbitrary_flag": True,
            },
        },
    )
    assert resp.status_code == 200
    assert reset_engine.last_context is not None
    assert reset_engine.last_context["custom_language"] == "rust"
    assert reset_engine.last_context["nested_toolchain"]["cargo_version"] == "1.80.0"


def test_capturing_fake_tokenizer_and_rendered_message_divergence():
    # Verify that rendered strings for Condition A and Condition B differ
    from inference.formatters import (
        build_conversation_messages,
        format_training_aligned,
    )

    class CapturingTokenizer:
        def __init__(self):
            self.eos_token_id = 1
        def apply_chat_template(self, messages, add_generation_prompt=False, tokenize=False):
            return "\n".join(f"[{m['role']}]: {m['content']}" for m in messages)

    tok = CapturingTokenizer()
    msgs_a = build_conversation_messages("error A", system_prompt_version=PROMPT_VERSION_FROZEN)
    msgs_b = build_conversation_messages("error A", system_prompt_version=PROMPT_VERSION_ENUM_GUIDED)

    rendered_a = format_training_aligned(msgs_a, tok)
    rendered_b = format_training_aligned(msgs_b, tok)

    assert rendered_a != rendered_b
    assert "The error_category field must be exactly one of:" in rendered_b
    assert "The error_category field must be exactly one of:" not in rendered_a



# 10. Operational Logging & Data Protection
def test_logs_do_not_contain_user_error_or_secrets(caplog):
    caplog.set_level(logging.INFO, logger="oopsie.service")
    secret_string = "ghp_0123456789abcdefghijklmnopqrstuvwxyz"
    sensitive_log = f"Build failed with secret token {secret_string} in repo/path"

    resp = client.post("/v1/analyze", json={"error_text": sensitive_log})
    assert resp.status_code == 200

    captured_logs = caplog.text
    # Log must contain operational metadata
    assert "status=success" in captured_logs
    assert "prompt_tokens=" in captured_logs

    # Log must NOT contain the sensitive error string or secret
    assert secret_string not in captured_logs
    assert "Build failed with secret token" not in captured_logs


# 11. Legacy Endpoint Alias Compatibility
def test_legacy_api_analyze_alias():
    resp = client.post(
        "/api/analyze",
        json={"error_text": "Error: connection timeout"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "success"


# 12. Concurrency, Non-Blocking Event Loop, and Cancellation Safety
class SlowMockEngine(MockInferenceEngine):
    def __init__(self, delay_s: float = 0.3):
        super().__init__(ready=True)
        self.delay_s = delay_s
        self.started_event = threading.Event()
        self.completed_event = threading.Event()

    def generate(
        self,
        raw_error: str,
        context: dict[str, Any] | None = None,
        formatter_id: str = FORMATTER_TRAINING_ALIGNED,
        system_prompt_version: str = "system_prompt_v1",
    ) -> GenerationResult:
        self.started_event.set()
        time.sleep(self.delay_s)
        self.completed_event.set()
        return super().generate(
            raw_error, context, formatter_id, system_prompt_version=system_prompt_version
        )


def test_health_remains_responsive_during_generation():
    slow_engine = SlowMockEngine(delay_s=0.4)
    set_engine(slow_engine)

    t1_result = {}

    def run_slow_request():
        t1_result["resp"] = client.post(
            "/v1/analyze",
            json={"error_text": "slow generation log"},
        )

    thread = threading.Thread(target=run_slow_request)
    thread.start()

    # Wait until engine starts generation
    assert slow_engine.started_event.wait(timeout=2.0)

    # Concurrently probe /health
    t0 = time.perf_counter()
    health_resp = client.get("/health")
    health_duration = time.perf_counter() - t0

    assert health_resp.status_code == 200
    assert health_resp.json()["status"] == "ok"
    # Health check must return promptly and not be blocked by generation
    assert health_duration < 0.2

    thread.join()
    assert t1_result["resp"].status_code == 200


def test_concurrent_request_receives_capacity_limit():
    slow_engine = SlowMockEngine(delay_s=0.4)
    set_engine(slow_engine)

    t1_result = {}

    def run_first_request():
        t1_result["resp"] = client.post(
            "/v1/analyze",
            json={"error_text": "first long task"},
        )

    thread = threading.Thread(target=run_first_request)
    thread.start()

    # Wait until engine starts generation
    assert slow_engine.started_event.wait(timeout=2.0)

    # Second request must be immediately rejected with CAPACITY_LIMIT
    resp2 = client.post(
        "/v1/analyze",
        json={"error_text": "second concurrent request"},
    )
    assert resp2.status_code == 429
    body2 = resp2.json()
    assert body2["status"] == "error"
    assert body2["error"]["code"] == "CAPACITY_LIMIT"

    thread.join()
    assert t1_result["resp"].status_code == 200


def test_cancellation_does_not_release_gpu_capacity_early():
    # If client disconnects or times out, the worker thread continues running.
    # GPU semaphore must remain locked until the generation completes.
    slow_engine = SlowMockEngine(delay_s=0.3)
    set_engine(slow_engine)

    sem = get_semaphore()

    def run_worker():
        try:
            client.post(
                "/v1/analyze",
                json={"error_text": "task to abandon"},
            )
        except Exception:
            pass

    thread = threading.Thread(target=run_worker)
    thread.start()

    assert slow_engine.started_event.wait(timeout=2.0)

    # While slow generation is ongoing, semaphore must be held (cannot acquire)
    assert sem.acquire(blocking=False) is False
    assert not slow_engine.completed_event.is_set()

    # Wait for background generation to fully finish
    slow_engine.completed_event.wait(timeout=2.0)
    thread.join()

    # After completion, semaphore is released and can be acquired again
    time.sleep(0.05)
    acquired = sem.acquire(blocking=False)
    assert acquired is True
    sem.release()


def test_engine_mode_metadata_identification(reset_engine: MockInferenceEngine):
    # Verify health, ready, and analyze metadata identify engine_mode as 'mock'
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["engine_mode"] == "mock"

    ready_resp = client.get("/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["engine_mode"] == "mock"

    analyze_resp = client.post("/v1/analyze", json={"error_text": "sample error"})
    assert analyze_resp.status_code == 200
    body = analyze_resp.json()
    assert body["metadata"]["engine_mode"] == "mock"


def test_real_engine_mode_reported():
    from inference.engine import Gemma4PilotEngine
    real_engine = Gemma4PilotEngine()
    assert real_engine.engine_mode == "real_model"


def test_warning_provenance_and_shared_fixture_immutability(reset_engine: MockInferenceEngine):
    # 1. Verify that DEFAULT_VALID_REPORT is clean initially
    assert MockInferenceEngine.DEFAULT_VALID_REPORT["warnings"] == []

    # 2. Submit request with text that triggers both production and database warnings
    resp1 = client.post(
        "/v1/analyze",
        json={"error_text": "Production build failure: DROP TABLE users migration failed"},
    )
    assert resp1.status_code == 200
    data1 = resp1.json()["data"]
    # Check that deterministic post-generation warnings were added to the response
    assert any("production" in w.lower() for w in data1["warnings"])
    assert any("stored data" in w.lower() or "database" in w.lower() for w in data1["warnings"])

    # 3. CRITICAL: Verify that MockInferenceEngine.DEFAULT_VALID_REPORT was NOT mutated
    assert MockInferenceEngine.DEFAULT_VALID_REPORT["warnings"] == []

    # 4. Submit an innocent request with no production or database terms
    resp2 = client.post(
        "/v1/analyze",
        json={"error_text": "Simple syntax error on line 42"},
    )
    assert resp2.status_code == 200
    data2 = resp2.json()["data"]
    # Warning from mock repair_prompt ("DATABASE_URL") may fire, but the production warning from resp1 must NOT leak!
    assert not any("production" in w.lower() for w in data2["warnings"])


