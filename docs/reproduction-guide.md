# OOPSIE Independent Reproduction Guide

This guide details the exact environment setup, dependencies, commands, data artifacts, and cryptographic verification procedures necessary to independently reproduce the OOPSIE evaluation benchmark.

> [!WARNING] Research Evaluation Notice
> The OOPSIE benchmark is a research evaluation protocol measuring empirical structured JSON generation under zero-tolerance parsing. It is **not** a production-ready automated diagnostic or program repair system. Model outputs must be validated against schema boundaries and reviewed by qualified human developers before applying changes.

> [!CAUTION] Blinding Protocol Notice
> The unblinding key (`unblinded_review_key.json`) maps randomized system labels to experimental conditions for the human review protocol. It is private research metadata excluded by `.gitignore` and **must not be committed or distributed** in public archives.

---

## 1. Environment Specification

- **Operating System**: Linux (Ubuntu 22.04+ recommended; tested in Kaggle GPU and Linux environments) or Windows 10/11.
- **Python Version**: Python 3.10+ (tested on Python 3.10 and Python 3.14).
- **Target Hardware**:
  - **Inference Benchmark**: Single NVIDIA GPU with $\ge 15$ GB VRAM (tested on NVIDIA Tesla T4 with 14.56 GB allocated VRAM under 4-bit NF4 quantization).
  - **Unit & Contract Testing**: CPU-only environment (requires no GPU access; runs with mock engines).

---

## 2. Repository Setup and Installation

### Step 2.1: Clone Repository
```bash
git clone https://github.com/Onyx-Prasai/OOPSIE.git
cd OOPSIE
```

### Step 2.2: Create and Activate Virtual Environment
```bash
# On Linux/macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows (PowerShell):
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Step 2.3: Install Exact Project Dependencies
Install the package in editable mode with all optional dependencies:
```bash
python -m pip install --upgrade pip
python -m pip install -e ".[api,training,test]"
```

Verify that the test suite runs and all contracts pass:
```bash
python -m pytest tests/test_benchmark_contract.py tests/test_data_pipeline.py tests/test_data_validation.py -v
```

---

## 3. Obtaining Models and Checkpoints

### 3.1 Base Model
The foundation model is `google/gemma-4-12b-it` (instruction-tuned Gemma 4, ~11.95B dense parameters), released by Google under the Apache 2.0 license:
- **Hugging Face Model Hub**: `google/gemma-4-12b-it`
- Obtain access via Hugging Face and log in via CLI:
  ```bash
  huggingface-cli login
  ```

### 3.2 OOPSIE Pilot Adapter
The pilot adapter checkpoint was trained with QLoRA ($r=16, \alpha=32$, dropout 0.05) using the configuration in [`artifacts/pilot_v1/artifacts/run_config.json`](../artifacts/pilot_v1/artifacts/run_config.json).
- **Local Checkpoint Path**: `artifacts/pilot_v1/adapter/`
- Contains `adapter_config.json` and adapter weight files (`adapter_model.safetensors`).

---

## 4. Frozen Four-Condition Benchmark Execution

The benchmark protocol (`OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`) evaluates 40 unseen failure scenarios across four frozen conditions:

- **Condition A (Base Zero-Shot + Schema)**: Base model with adapter disabled (`with model.disable_adapter():`), prompt containing system prompt v2, schema text, and error log; formatted with official Gemma chat template.
- **Condition B (Adapter Zero-Shot + Schema)**: Adapted model with active adapter, identical prompt text containing schema text; formatted with `training_aligned_v1` (`<|turn|>model\n`).
- **Condition C (Base 1-Shot Demonstration + Schema)**: Base model with adapter disabled, prompt containing one fixed training exemplar (`syn-dep-001`); formatted with multi-turn chat template.
- **Condition D (Adapter Current Service Prompt)**: Adapted model with active adapter, runtime service prompt containing category enums but **omitting the JSON schema block**; formatted with `training_aligned_v1`.

### 4.1 Running Benchmark Evaluation Programmatically

To execute the benchmark against local GPU weights using the evaluation harness:

```python
import json
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from evaluation.harness import (
    CONDITIONS,
    evaluate_single_case,
    verify_integrity_hashes,
)

# 1. Verify fail-fast integrity hashes before running
hashes = verify_integrity_hashes()
print("Integrity hashes verified:", hashes)

# 2. Load 40 benchmark scenarios
benchmark_records = [
    json.loads(line)
    for line in Path("evaluation/benchmark.jsonl").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
assert len(benchmark_records) == 40

# 3. Load Base Model in 4-bit NF4
base_model_id = "google/gemma-4-12b-it"
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForCausalLM.from_pretrained(
    base_model_id,
    quantization_config=bnb_config,
    device_map="auto",
    torch_dtype=torch.bfloat16,
)

# 4. Attach LoRA Adapter
adapter_path = "artifacts/pilot_v1/adapter"
model = PeftModel.from_pretrained(base_model, adapter_path, adapter_name="oopsie_pilot")
model.eval()

# 5. Evaluate records across all 4 conditions
results = {}
for record in benchmark_records:
    case_id = record["id"]
    results[case_id] = {}
    for cond_id, cond_spec in CONDITIONS.items():
        res = evaluate_single_case(
            record=record,
            condition=cond_spec,
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=1024,
            adapter_name="oopsie_pilot",
        )
        results[case_id][cond_id] = res
```

### 4.2 Running Evaluation via Local API Endpoint

Alternatively, launch the local API service:
```powershell
$env:OOPSIE_MODEL_PATH = "artifacts/pilot_v1/adapter"
uvicorn inference.api.main:app --host 127.0.0.1 --port 8000
```

And evaluate using the benchmark client:
```powershell
python evaluation/evaluate.py --benchmark evaluation/benchmark.jsonl --api-url http://127.0.0.1:8000/v1/analyze --output evaluation/results/run.json
```

---

## 5. Artifact Verification & Cryptographic Checksums

Before evaluating, verify file integrity against official SHA-256 checksums:

```python
import hashlib
from pathlib import Path

CHECKSUMS = {
    "evaluation/benchmark.jsonl": "1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd",
    "data/schema.json": "ce322859f8e4a757847b3e4d02b90ded41054ccbef5b4dd872523a80d681440a",
    "artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz": "cf24eec1a5c3347ae826fec4b5cbfb7133a1c4ce92aace3eab2b048bdd37f4eb",
}

for rel_path, expected_hash in CHECKSUMS.items():
    p = Path(rel_path)
    if not p.exists():
        print(f"[MISSING] {rel_path}")
        continue
    raw_bytes = p.read_bytes()
    # Normalize schema line endings if checking cross-platform
    if p.name == "schema.json":
        raw_bytes = raw_bytes.replace(b"\r\n", b"\n")
    actual_hash = hashlib.sha256(raw_bytes).hexdigest()
    assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}!"
    print(f"[VERIFIED] {rel_path} -> {actual_hash[:16]}...")
```

### Snapshot Verification
The author-adopted qualitative ratings are immutably archived under `docs/research/human_review/snapshots/2026-11-06/`. To verify all 10 snapshot files against their manifest:
```bash
python -c "
import json, hashlib, pathlib
manifest = json.load(open('docs/research/human_review/snapshots/2026-11-06/manifest.json'))
for f in manifest['files']:
    h = hashlib.sha256(pathlib.Path(f['snapshot_path']).read_bytes()).hexdigest()
    assert h == f['sha256'], f'Snapshot mismatch for {f[\"file_name\"]}'
print('All 10 snapshot files cryptographically verified!')
"
```

