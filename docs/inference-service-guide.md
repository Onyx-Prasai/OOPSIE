# OOPSIE Experimental Inference Service Run Guide

This guide details runtime requirements, configuration, and verification procedures for the first experimental OOPSIE inference service using the saved pilot adapter and training-aligned prompt formatter.

> **CRITICAL CONSTRAINTS & SCOPE**:
> - **Experimental Only**: This service is an internal evaluation milestone. Do not deploy publicly or connect to the public website yet.
> - **Hardware Prerequisite**: Base checkpoint `google/gemma-4-12b-it` requires ~14 GB of GPU VRAM in 4-bit NF4 precision. Standard laptops without dedicated NVIDIA CUDA GPUs (>=15 GB VRAM) cannot run the model directly.
> - **Mock Support**: A complete mock engine (`MockInferenceEngine`) is provided for local development, API integration, and unit tests without GPU access or model downloads.

---

## 1. Runtime Architecture

The inference service decouples the HTTP/API layer from the model-loading engine:

1. **API Service (`inference.api.main`)**:
   - Built on FastAPI.
   - Enforces request-size bounds (max 16,384 characters).
   - Validates input format and bounds context-window utilization.
   - Protects GPU from request floods with bounded admission (`asyncio.Semaphore(1)` default).
   - Sanitizes operational logs (metadata only; never logs raw error text or completion tokens).
   - Wraps all responses in standardized outer envelopes.
2. **Inference Engine (`inference.engine.BaseInferenceEngine`)**:
   - `Gemma4PilotEngine`: Loads base model and attaches the pilot adapter (`checkpoint-44`, LoRA $r=16, \alpha=32$) once at startup. Evaluates in `torch.inference_mode()` under greedy decoding (`temperature=0.0`, `max_new_tokens=1024`).
   - `MockInferenceEngine`: Lightweight synthetic engine for unit tests and local API testing.
3. **Strict Parser (`inference.parser`)**:
   - Parses completion text only (not prompt + completion).
   - Preserves raw completion behavior: zero Markdown fence stripping, zero heuristic JSON substring extraction.
   - Rejects duplicate JSON keys and non-standard numeric constants (`NaN`, `Infinity`).
   - Validates against `data/schema.json`.

---

## 2. Configuration & Environment Variables

| Variable | Description | Default |
| :--- | :--- | :--- |
| `OOPSIE_MODEL_PATH` | Path to the directory containing the LoRA pilot adapter (`adapter_model.safetensors`, `adapter_config.json`). | `artifacts/pilot_v1/adapter` |
| `OOPSIE_BASE_MODEL_ID` | Hugging Face model identifier for the base checkpoint. | `google/gemma-4-12b-it` |
| `HF_TOKEN` | Hugging Face user access token required to download gated Gemma 4 weights. | None (required for GPU) |
| `OOPSIE_FORMATTER` | Prompt formatting strategy: `training_aligned_v1` (default, matches SFT training) or `original_eval_v1`. | `training_aligned_v1` |
| `OOPSIE_SYSTEM_PROMPT_VERSION` | System prompt version: `system_prompt_v2_enum_guided` (default, schema-derived enum guidance) or `system_prompt_v1` (frozen baseline). | `system_prompt_v2_enum_guided` |
| `OOPSIE_CONCURRENCY` | Maximum concurrent generations admitted by the service. | `1` |
| `OOPSIE_USE_MOCK_ENGINE` | Set to `1` or `true` to run the service using the mock engine without GPU/weights. | `0` |
| `OOPSIE_CORS_ORIGINS` | Comma-separated list of explicitly allowed origins (wildcard `*` rejected). | `""` |
| `PORT` | HTTP port for uvicorn server. | `8000` |

---

## 3. Local Development & Mock Testing (No GPU Required)

To develop or test the service locally on a standard laptop:

### Run Unit Tests
```bash
python -m pytest tests/test_inference_service.py -v
```
All 23 unit tests pass without requiring a GPU or downloading weights.

### Run Local Mock Server
Start the service in mock mode:
```bash
# Windows PowerShell
$env:OOPSIE_USE_MOCK_ENGINE = "1"
uvicorn inference.api.main:app --host 127.0.0.1 --port 8000 --workers 1

# Linux / macOS
OOPSIE_USE_MOCK_ENGINE=1 uvicorn inference.api.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Probe Health & Readiness
```bash
# Check basic health
curl http://127.0.0.1:8000/health

# Check model readiness
curl http://127.0.0.1:8000/ready
```

### Send Sample Inference Request
```bash
curl -X POST http://127.0.0.1:8000/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"error_text": "FATAL: connection to server on socket failed: Connection refused"}'
```

---

## 4. GPU Runtime Environment & Real Model Requirements

When deploying the service to a GPU environment (e.g. Kaggle GPU accelerator or dedicated server):

### Hardware Requirements
- **Accelerator**: NVIDIA GPU with >= 15 GB VRAM (e.g. Tesla T4 16GB, RTX 4090, A10G, or A100).
- **Compute Capability**: CUDA CC 7.5 or higher.
- **Tesla T4 Patch**: Handled automatically in `Gemma4PilotEngine` via `trl.kernels.chunked_logprob._MM_OUT_DTYPE = False` to prevent CC 7.5 bfloat16 GEMM kernel failures.
- **Quantization**: 4-bit NF4 with double quantization and bfloat16 compute dtype (~8.5 GB base model memory footprint + ~3 GB KV cache and adapter).

### Dependencies
Install API dependencies:
```bash
pip install -e ".[api]"
```
Ensure Hugging Face token is exported:
```bash
export HF_TOKEN="hf_..."
```

### Adapter Weights
Verify that the pilot adapter files are present:
```bash
ls -la artifacts/pilot_v1/adapter/
# Must contain adapter_model.safetensors, adapter_config.json, tokenizer.json
```

### Launch Service
Always run with a **single worker** (`--workers 1`):
```bash
export OOPSIE_MODEL_PATH="artifacts/pilot_v1/adapter"
export OOPSIE_BASE_MODEL_ID="google/gemma-4-12b-it"
uvicorn inference.api.main:app --host 0.0.0.0 --port 8000 --workers 1
```

> [!WARNING]
> Do NOT run with multiple uvicorn workers (e.g. `--workers 4`). Multiple processes would attempt to independently load the 12B model into GPU memory, causing instant CUDA out-of-memory errors. Concurrency is managed via async semaphore inside a single process.

---

## 5. Startup, Shutdown, and Cancellation Semantics

### Startup & Health vs. Readiness
- **Startup**: The FastAPI `lifespan` handler initializes the inference engine. If running with real GPU weights, `engine.load()` runs once at process startup.
- **`/health` (Liveness)**: Returns HTTP 200 `{"status": "ok"}` as long as the HTTP process is running. Used by orchestrators to determine whether to restart the container.
- **`/ready` (Readiness)**: Returns HTTP 200 only when model weights are fully loaded into memory and ready to accept inference requests. Returns HTTP 503 `{"status": "not_ready"}` during initial loading or if model initialization failed. Orchestrators should not route traffic until `/ready` returns 200.

### GPU Cancellation & Work Semantics
- **HTTP Cancellation Limitation**: In PyTorch, once a CUDA forward pass or generation loop begins (`model.generate()`), terminating or timing out the HTTP connection on the client side does **not** interrupt the underlying C++/CUDA kernel on the GPU. The GPU execution runs to completion.
- **Protection**: To prevent runaway generation, `max_new_tokens` is hard-frozen at `1024`, and admission is bounded to 1 concurrent request. Clients cannot cause infinite GPU loops.

---

## 6. API Contracts: Envelopes, Codes, & Errors

### Outer Success Envelope
```json
{
  "status": "success",
  "request_id": "8fa20216-17b5-41e9-9130-1c883e4c4984",
  "model_version": "oopsie-pilot-gemma4-12b-lora-c44",
  "formatter_version": "training_aligned_v1",
  "data": {
    "summary": "...",
    "plain_explanation": "...",
    "error_category": "environment_variables",
    "likely_causes": [...],
    "missing_context_questions": [...],
    "risk_level": "low",
    "warnings": [...],
    "repair_prompt": "...",
    "verification_steps": [...],
    "matched_recipes": []
  },
  "metadata": {
    "prompt_tokens": 128,
    "generated_tokens": 412,
    "budget_hit": false,
    "duration_ms": 1450.2
  }
}
```

### Outer Failure Envelope
```json
{
  "status": "error",
  "request_id": "8fa20216-17b5-41e9-9130-1c883e4c4984",
  "error": {
    "code": "OUTPUT_BUDGET_EXCEEDED",
    "message": "Generation reached maximum token budget without completion. Incomplete outputs are rejected for safety."
  }
}
```

### Error Code Summary
- `INVALID_INPUT` (HTTP 400): Empty, whitespace, oversized (>16,384 chars), or prompt exceeds context window (8192 tokens).
- `MODEL_UNAVAILABLE` (HTTP 503): Engine uninitialized or model weights not loaded.
- `CAPACITY_LIMIT` (HTTP 429): Service admission full (concurrent request already active).
- `OUTPUT_BUDGET_EXCEEDED` (HTTP 422): Generation hit the 1024-token budget without emitting an EOS token. Rejected to prevent truncated advice.
- `PARSE_ERROR` (HTTP 422): Completion contained invalid JSON, duplicate keys, non-standard constants (`NaN`), or Markdown code fences.
- `SCHEMA_ERROR` (HTTP 422): JSON is syntactically valid but fails validation against `data/schema.json`.
- `GENERATION_ERROR` (HTTP 500): Internal model runtime error (CUDA OOM, tensor failure). Stack traces are never exposed to clients.
