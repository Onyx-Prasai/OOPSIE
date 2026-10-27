"""GPU integration test for OOPSIE Gemma 4 12B pilot adapter inference.

Run this script ONLY on a machine with an NVIDIA GPU (>= 15 GB VRAM) and HF_TOKEN configured.
Do not run this script on CPU-only local development laptops.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from inference.config import (
    DEFAULT_ADAPTER_PATH,
    DEFAULT_FORMATTER,
    get_adapter_path,
    get_base_model_id,
)
from inference.engine import Gemma4PilotEngine
from inference.parser import strict_parse_raw_completion, validate_oopsie_report


def main() -> int:
    print("=" * 60)
    print("OOPSIE GPU End-to-End Integration Test")
    print("=" * 60)

    try:
        import torch
    except ImportError:
        print("[SKIP] PyTorch is not installed. This test requires a GPU environment with PyTorch.")
        print("       For local development, run mocked unit tests: `python -m pytest tests/test_inference_service.py`")
        return 0

    if not torch.cuda.is_available():
        print("[SKIP] CUDA is not available. This test requires an NVIDIA GPU with >= 15 GB VRAM.")
        print("       For local development, run mocked unit tests: `python -m pytest tests/test_inference_service.py`")
        return 0

    device_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"Device: {device_name} ({vram_gb:.2f} GB VRAM)")

    if vram_gb < 14.0:
        print(f"[WARN] Available VRAM ({vram_gb:.2f} GB) is below recommended 14.0 GB.")

    adapter_path = get_adapter_path()
    base_model_id = get_base_model_id()

    print(f"Base Model    : {base_model_id}")
    print(f"Adapter Path  : {adapter_path}")
    print(f"Formatter     : {DEFAULT_FORMATTER}")

    if not adapter_path.exists():
        print(f"[FAIL] Adapter directory not found: {adapter_path}")
        return 1

    print("\n[1/4] Loading model and pilot adapter...")
    t0 = time.perf_counter()
    engine = Gemma4PilotEngine(adapter_path=adapter_path, base_model_id=base_model_id)
    try:
        engine.load()
    except Exception as exc:
        print(f"[FAIL] Failed to load model/adapter: {exc}")
        return 1
    print(f"      Loaded in {time.perf_counter() - t0:.2f}s.")

    sample_error = (
        "[eslint] Warning: 'unusedVar' is defined but never used (no-unused-vars) in src/Header.js:3:7\n"
        "[build] 2 warnings found.\n"
        "[builder] Starting compiler step...\n"
        "[builder] Process finished with exit code 1."
    )
    sample_context = {
        "language_or_framework": "React / Webpack",
        "environment": "ci_build",
    }

    print("\n[2/4] Running generation with training-aligned formatter...")
    t1 = time.perf_counter()
    try:
        gen_result = engine.generate(
            raw_error=sample_error,
            context=sample_context,
            formatter_id=DEFAULT_FORMATTER,
        )
    except Exception as exc:
        print(f"[FAIL] Generation failed: {exc}")
        return 1
    print(f"      Generated {gen_result.generated_tokens} tokens in {gen_result.duration_ms:.1f}ms "
          f"({gen_result.generated_tokens / (gen_result.duration_ms / 1000):.1f} tok/s).")
    print(f"      Budget hit: {gen_result.hit_budget}")

    print("\n[3/4] Parsing raw completion strictly (no fence-stripping)...")
    try:
        parsed = strict_parse_raw_completion(gen_result.completion_text)
    except Exception as exc:
        print(f"[FAIL] Strict parse failed: {exc}")
        print("Raw Completion:\n" + gen_result.completion_text)
        return 1
    print("      Strict JSON parsing succeeded without errors.")

    print("\n[4/4] Validating schema against data/schema.json...")
    try:
        validated = validate_oopsie_report(parsed)
    except Exception as exc:
        print(f"[FAIL] Schema validation failed: {exc}")
        return 1

    print("      Schema validation passed.")
    print("\nSummary of Generated Report:")
    print(f"  Summary    : {validated.get('summary')}")
    print(f"  Risk Level : {validated.get('risk_level')}")
    print(f"  Category   : {validated.get('error_category')}")
    print(f"  Prompt     : {validated.get('repair_prompt')[:120]}...")
    print("\n[PASS] GPU integration test completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
