# Real-GPU Service Integration Audit Report

**Date**: 2026-10-25 15:16:28 UTC  
**Environment**: Kaggle GPU Session (Tesla T4, 14.56 GB VRAM)  
**Base Model**: `google/gemma-4-12b-it` (4-bit NF4 double-quantized)  
**Adapter**: `checkpoint-44` (`oopsie-pilot-adapter`, LoRA $r=16, \alpha=32$)  
**Artifact Directory**: `artifacts/gpu_integration/`  

---

## 1. Executive Summary

This audit records the first real-GPU end-to-end integration test of the OOPSIE inference service. The test executed inside an in-process FastAPI `TestClient` on a Kaggle NVIDIA Tesla T4 GPU, exercising:
1. Concurrency and event-loop responsiveness before GPU allocation.
2. Single-process model and LoRA adapter loading in 4-bit NF4.
3. API readiness probing (`GET /ready`).
4. An end-to-end inference request (`POST /v1/analyze`).
5. Strict output schema validation and error envelope generation.

---

## 2. Hardware & Memory Footprint

| Metric | Measured Value | Target / Limit | Status |
| :--- | :--- | :--- | :--- |
| **GPU Accelerator** | NVIDIA Tesla T4 | CC $\ge 7.5$ | PASS |
| **Total VRAM** | 14.56 GB | $\ge 14.0\text{ GB}$ | PASS |
| **Allocated VRAM (Post-Load)** | **5.30 GB** | $< 12.0\text{ GB}$ | PASS |
| **Reserved VRAM (Post-Load)** | **5.68 GB** | $< 14.0\text{ GB}$ | PASS |
| **Model Load Duration** | 225.29 seconds | One-time at startup | PASS |
| **Tesla T4 Compatibility Patch** | Applied (`_MM_OUT_DTYPE = False`) | Avoid BFloat16 GEMM fail | PASS |

The 4-bit NF4 double-quantized base model and LoRA adapter occupy only **5.30 GB of allocated VRAM**, leaving $>8.8\text{ GB}$ of free VRAM on the Tesla T4 for KV cache and batch activations.

---

## 3. Concurrency & Lifecycle Pre-Check Outcomes

| Check | Specification | Result | Status |
| :--- | :--- | :--- | :--- |
| **Non-blocking Event Loop** | `GET /health` must answer during ongoing generation | Responded in **3.2 ms** | PASS |
| **Admission Saturation** | 2nd concurrent analyze request must get HTTP 429 | Returned `HTTP 429 CAPACITY_LIMIT` | PASS |
| **Cancellation Safety** | Premature client disconnect must not free GPU semaphore | Capacity held until worker thread termination | PASS |
| **Readiness Endpoint** | `GET /ready` must return HTTP 200 with model version | Returned HTTP 200 `model_ready: True` | PASS |

---

## 4. Inference Request & Strict Schema Validation

A standard synthetic build error was dispatched to `POST /v1/analyze`:
```text
[eslint] Warning: 'unusedVar' is defined but never used (no-unused-vars) in src/Header.js:3:7
[build] 2 warnings found.
[builder] Starting compiler step...
[builder] Process finished with exit code 1.
```

### Result:
- **HTTP Status**: `422 Unprocessable Entity`
- **Outer Failure Envelope**:
  ```json
  {
    "status": "error",
    "request_id": "ffbb49c1-7dc6-430b-82a5-b1df6a01a6b9",
    "error": {
      "code": "SCHEMA_ERROR",
      "message": "Model output failed schema validation: Schema validation failed with 1 error(s): $.error_category: value is not in the allowed enum"
    }
  }
  ```
- **Service Stability**: The API service and GPU execution pipeline operated with zero crashes.
- **Strict Validation Behavior**: The model successfully emitted valid JSON syntax, but hallucinated an unapproved category string for `error_category` (outside `["dependency", "configuration", "environment_variables", "database", "authentication", "authorization", "network", "build", "deployment", "runtime", "typescript", "frontend", "other", "unknown"]`).
- Rather than attempting heuristic repair, silently coercing values, or fabricating a "successful" response, the service strictly enforced the validation contract and returned an informative `SCHEMA_ERROR` envelope.

---

## 5. Artifact Manifest

The following artifacts have been preserved in `artifacts/gpu_integration/`:
- `gpu_service_integration_report.json` (1,518 bytes) — Complete hardware and lifecycle metadata.
- `api_response_envelope.json` (274 bytes) — Captured response payload.
- `integration_summary.md` (751 bytes) — Execution summary.

---

## 6. Boundaries and Next Steps

- **No Public Deployment**: The service was verified in-process using `TestClient`; no public ports or tunnels were opened.
- **Pilot Model Limitation**: The pilot model trained on $N=100$ examples occasionally chooses non-standard enum strings. Future dataset expansions (Batches 3 & 4) will reinforce strict enum adherence.
