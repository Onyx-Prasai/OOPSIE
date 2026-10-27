"""OOPSIE experimental inference API service.

Provides HTTP endpoints with outer success/failure envelopes, strict output validation,
resource bounding, and operational logging.
"""

from __future__ import annotations

import asyncio
import logging
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from inference.config import (
    CONFIG_VERSION,
    DEFAULT_FORMATTER,
    DEFAULT_SYSTEM_PROMPT_VERSION,
    FORMATTER_ORIGINAL_EVAL,
    FORMATTER_TRAINING_ALIGNED,
    MAX_INPUT_CHARS,
    MODEL_VERSION,
    PROMPT_VERSION_ENUM_GUIDED,
    PROMPT_VERSION_FROZEN,
    get_concurrency_limit,
    get_default_system_prompt_version,
)
from inference.engine import (
    BaseInferenceEngine,
    ContextWindowExceededError,
    GenerationResult,
    ModelNotReadyError,
    get_engine,
)
from inference.parser import (
    ParseError,
    SchemaValidationError,
    strict_parse_raw_completion,
    validate_oopsie_report,
)
from inference.safety import apply_safety_warnings, redact_secrets

# Structured Operational Logger (excludes untrusted inputs and completions)
logger = logging.getLogger("oopsie.service")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "name": "%(name)s", "message": "%(message)s"}'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Global Concurrency Control (Thread-safe admission bounding)
_concurrency_semaphore: threading.Semaphore | None = None


def get_semaphore() -> threading.Semaphore:
    global _concurrency_semaphore
    if _concurrency_semaphore is None:
        _concurrency_semaphore = threading.Semaphore(get_concurrency_limit())
    return _concurrency_semaphore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize engine and semaphore on startup
    get_semaphore()
    engine = get_engine()
    if hasattr(engine, "load") and not engine.is_ready():
        # In GPU mode, load model weights once at process startup if configured
        try:
            logger.info("Initializing inference engine at service startup...")
            engine.load()
            logger.info("Inference engine initialized successfully.")
        except Exception as exc:
            logger.warning(f"Engine deferred loading or failed at startup: {exc}")
    yield


app = FastAPI(
    title="OOPSIE Inference Service",
    description="Experimental inference service for OOPSIE error recovery models.",
    version=CONFIG_VERSION,
    lifespan=lifespan,
)

# CORS configuration
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("OOPSIE_CORS_ORIGINS", "").split(",")
    if origin.strip()
]
if "*" in allowed_origins:
    raise RuntimeError("OOPSIE_CORS_ORIGINS must contain explicit origins, not a wildcard.")
if allowed_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "X-Request-ID"],
        allow_credentials=False,
    )


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error_text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_INPUT_CHARS,
        description="Raw terminal or application error log snippet.",
    )
    context: dict[str, Any] | None = Field(
        default=None,
        description="Optional structured metadata (language, framework, environment).",
    )
    formatter: Literal[
        FORMATTER_TRAINING_ALIGNED, FORMATTER_ORIGINAL_EVAL
    ] | None = Field(
        default=None,
        description=f"Prompt formatter to use. Options: '{FORMATTER_TRAINING_ALIGNED}' (default), '{FORMATTER_ORIGINAL_EVAL}'.",
    )
    system_prompt_version: Literal[
        PROMPT_VERSION_FROZEN, PROMPT_VERSION_ENUM_GUIDED
    ] | None = Field(
        default=None,
        description=f"System prompt condition. Options: '{PROMPT_VERSION_ENUM_GUIDED}' (default), '{PROMPT_VERSION_FROZEN}'.",
    )


def make_error_envelope(
    request_id: str,
    code: str,
    message: str,
    status_code: int,
) -> JSONResponse:
    """Build standardized outer error envelope."""
    payload = {
        "status": "error",
        "request_id": request_id,
        "error": {
            "code": code,
            "message": message,
        },
    }
    return JSONResponse(status_code=status_code, content=payload)


def make_success_envelope(
    request_id: str,
    model_version: str,
    formatter_version: str,
    data: dict[str, Any],
    metadata: dict[str, Any],
) -> JSONResponse:
    """Build standardized outer success envelope."""
    payload = {
        "status": "success",
        "request_id": request_id,
        "model_version": model_version,
        "formatter_version": formatter_version,
        "data": data,
        "metadata": metadata,
    }
    return JSONResponse(status_code=200, content=payload)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Intercept Pydantic validation errors and return consistent error envelope."""
    req_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    details = exc.errors()
    error_msgs = []
    for err in details:
        loc = [str(x) for x in err.get("loc", []) if str(x) not in ("body", "request")]
        field_str = ".".join(loc)
        m = err.get("msg", "Invalid value")
        error_msgs.append(f"{field_str}: {m}" if field_str else m)
    msg = "; ".join(error_msgs) if error_msgs else "Invalid request payload."
    logger.warning(f"Request validation failure [req_id={req_id}]: {msg}")
    return make_error_envelope(
        request_id=req_id,
        code="INVALID_INPUT",
        message=f"Request validation failed: {msg}",
        status_code=400,
    )


@app.get("/health")
def health() -> dict[str, Any]:
    """Basic service health check."""
    engine = get_engine()
    engine_mode = getattr(engine, "engine_mode", "mock")
    return {
        "status": "ok",
        "service": "oopsie-inference",
        "version": CONFIG_VERSION,
        "engine_mode": engine_mode,
    }


@app.get("/ready")
def ready() -> JSONResponse:
    """Model readiness probe.

    Returns HTTP 200 if model weights are loaded and ready to serve,
    or HTTP 503 if model is still loading or unconfigured.
    """
    engine = get_engine()
    is_ready = engine.is_ready()
    status_code = 200 if is_ready else 503
    engine_mode = getattr(engine, "engine_mode", "mock")
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "model_ready": is_ready,
            "engine_mode": engine_mode,
            "model_version": MODEL_VERSION,
            "default_formatter": DEFAULT_FORMATTER,
        },
    )


@app.post("/v1/analyze", response_model=None)
@app.post("/api/analyze", response_model=None)
async def analyze_error(
    request: AnalyzeRequest,
    raw_request: Request,
) -> JSONResponse:
    """Analyze an untrusted error log and return a validated OOPSIE report."""
    request_id = raw_request.headers.get("X-Request-ID") or str(uuid.uuid4())
    t_start = time.perf_counter()

    # 1. Input sanitization and bounds check
    error_text = request.error_text.strip()
    if not error_text:
        return make_error_envelope(
            request_id=request_id,
            code="INVALID_INPUT",
            message="Input error_text cannot be empty or only whitespace.",
            status_code=400,
        )

    # 2. Formatter selection
    # 2. Formatter and prompt version selection
    formatter_id = request.formatter or DEFAULT_FORMATTER
    if formatter_id not in (FORMATTER_TRAINING_ALIGNED, FORMATTER_ORIGINAL_EVAL):
        return make_error_envelope(
            request_id=request_id,
            code="INVALID_INPUT",
            message=f"Unsupported formatter '{formatter_id}'. Use '{FORMATTER_TRAINING_ALIGNED}' or '{FORMATTER_ORIGINAL_EVAL}'.",
            status_code=400,
        )

    system_prompt_version = (
        request.system_prompt_version or get_default_system_prompt_version()
    )
    if system_prompt_version not in (PROMPT_VERSION_FROZEN, PROMPT_VERSION_ENUM_GUIDED):
        return make_error_envelope(
            request_id=request_id,
            code="INVALID_INPUT",
            message=f"Unsupported system_prompt_version '{system_prompt_version}'. Use '{PROMPT_VERSION_FROZEN}' or '{PROMPT_VERSION_ENUM_GUIDED}'.",
            status_code=400,
        )

    # 3. Model readiness check
    engine = get_engine()
    if not engine.is_ready():
        logger.error(f"Inference rejected [req_id={request_id}]: Model unavailable.")
        return make_error_envelope(
            request_id=request_id,
            code="MODEL_UNAVAILABLE",
            message="The inference model is not initialized or ready.",
            status_code=503,
        )

    # 4. Admission and Concurrency Bounding
    semaphore = get_semaphore()
    if not semaphore.acquire(blocking=False):
        logger.warning(f"Inference rejected [req_id={request_id}]: Capacity limit reached.")
        return make_error_envelope(
            request_id=request_id,
            code="CAPACITY_LIMIT",
            message="The inference service is currently at maximum capacity. Please retry shortly.",
            status_code=429,
        )

    # 5. Redaction (defense-in-depth, not guaranteed)
    redacted_input, redaction_count = redact_secrets(error_text)

    # 6. Execute Generation inside protected lock
    # To protect the GPU, the semaphore must NOT be released on HTTP cancellation
    # while the background thread is still executing on the GPU.
    def _generation_worker() -> GenerationResult:
        try:
            return engine.generate(
                raw_error=redacted_input,
                context=request.context,
                formatter_id=formatter_id,
                system_prompt_version=system_prompt_version,
            )
        finally:
            semaphore.release()

    try:
        gen_result: GenerationResult = await asyncio.to_thread(_generation_worker)
    except ContextWindowExceededError as exc:
        logger.warning(f"Context window exceeded [req_id={request_id}]: {exc}")
        return make_error_envelope(
            request_id=request_id,
            code="INVALID_INPUT",
            message=str(exc),
            status_code=400,
        )
    except ModelNotReadyError as exc:
        logger.error(f"Engine not ready [req_id={request_id}]: {exc}")
        return make_error_envelope(
            request_id=request_id,
            code="MODEL_UNAVAILABLE",
            message="The inference engine was unloaded or not ready.",
            status_code=503,
        )
    except Exception as exc:
        logger.exception(f"Generation failure [req_id={request_id}]: {type(exc).__name__}")
        return make_error_envelope(
            request_id=request_id,
            code="GENERATION_ERROR",
            message="An error occurred while generating the model response.",
            status_code=500,
        )

    duration_ms = (time.perf_counter() - t_start) * 1000.0

    # 7. Output Budget Policy:
    # If the output budget was hit without emitting an EOS token, incomplete generation
    # poses severe risk of truncated advice. Reject with OUTPUT_BUDGET_EXCEEDED.
    if gen_result.hit_budget:
        logger.warning(
            f"Budget hit [req_id={request_id}]: Generated {gen_result.generated_tokens} tokens without EOS."
        )
        return make_error_envelope(
            request_id=request_id,
            code="OUTPUT_BUDGET_EXCEEDED",
            message="Generation reached maximum token budget without completion. Incomplete outputs are rejected for safety.",
            status_code=422,
        )

    # 8. Strict Raw JSON Parsing (no Markdown stripping, reject duplicates)
    try:
        parsed_report = strict_parse_raw_completion(gen_result.completion_text)
    except ParseError as exc:
        logger.warning(f"Parse error [req_id={request_id}]: {exc}")
        return make_error_envelope(
            request_id=request_id,
            code="PARSE_ERROR",
            message=f"Model output could not be parsed as strict JSON: {exc}",
            status_code=422,
        )

    # 9. Strict Schema Validation against data/schema.json
    try:
        validated_report = validate_oopsie_report(parsed_report)
    except SchemaValidationError as exc:
        logger.warning(f"Schema violation [req_id={request_id}]: {exc}")
        return make_error_envelope(
            request_id=request_id,
            code="SCHEMA_ERROR",
            message=f"Model output failed schema validation: {exc}",
            status_code=422,
        )

    # 10. Post-processing: Deterministic safety warnings
    validated_report = apply_safety_warnings(validated_report, redacted_input)
    if redaction_count > 0:
        validated_report["warnings"] = list(dict.fromkeys([
            *validated_report.get("warnings", []),
            "Secret-like text was detected and recognized patterns were redacted; manually review input because redaction is not guaranteed.",
        ]))

    # 11. Operational Audit Logging (Metadata only, NO error_text or raw completion)
    logger.info(
        f"Inference completed [req_id={request_id}]: status=success, "
        f"duration_ms={duration_ms:.1f}, prompt_tokens={gen_result.prompt_tokens}, "
        f"gen_tokens={gen_result.generated_tokens}, formatter={formatter_id}, "
        f"prompt_version={gen_result.system_prompt_version}"
    )

    metadata = {
        "prompt_tokens": gen_result.prompt_tokens,
        "generated_tokens": gen_result.generated_tokens,
        "budget_hit": gen_result.hit_budget,
        "duration_ms": round(duration_ms, 2),
        "system_prompt_version": gen_result.system_prompt_version,
        "engine_mode": gen_result.engine_mode,
    }

    return make_success_envelope(
        request_id=request_id,
        model_version=gen_result.model_version,
        formatter_version=formatter_id,
        data=validated_report,
        metadata=metadata,
    )
