# OOPSIE Kaggle Pilot Adapter Evaluation Guide (1024-Token Budget)

This guide provides step-by-step instructions for running the evaluation-only notebook on Kaggle to evaluate the saved **OOPSIE pilot adapter** for **Gemma 4 12B** (`google/gemma-4-12b-it`).

---

## 1. Scope & Strict Boundaries

* **Evaluation-Only**: Strictly no retraining, no gradient updates, no weight merging, and no deployment.
* **1024-Token Matched Budget**: Evaluates all 18 validation examples for **both** the unadapted base model and the saved adapter using `max_new_tokens=1024` with greedy decoding (`temperature=0.0`).
* **Independent Test Split**: Evaluates the untouched 17-record independent test split (`test_conversational.jsonl`) under identical frozen settings.

---

## 2. Prerequisites & Input Attachments on Kaggle

In your Kaggle evaluation notebook, ensure the following are attached:

### A. Dataset Input (`oopsie-dataset`)
Ensure the dataset contains:
* `val_conversational.jsonl` (18 records)
* `test_conversational.jsonl` (17 records) — *Attach this file if you wish to run the independent test set evaluation in Step 8!*

### B. Adapter Input (`oopsie-pilot-adapter`)
You can provide the saved adapter to the evaluation notebook in either of two ways:
1. **From an existing active session**: If `oopsie-pilot-adapter` is already in `/kaggle/working/oopsie-pilot-adapter`, the notebook finds it automatically.
2. **As an attached dataset / model**: 
   * Go to Kaggle -> **Datasets** -> **New Dataset**.
   * Upload the files inside `pilot_adapter.zip` (or the folder `artifacts/pilot_v1/adapter/`) and name it `oopsie-pilot-adapter`.
   * Attach it to the evaluation notebook via **+ Add Input**.

### C. Gated Model Access
* **`HF_TOKEN`**: Ensure your Hugging Face secret is checked in **Add-ons -> Secrets**.

---

## 3. Session Settings

| Setting | Required Value | Rationale |
| :--- | :--- | :--- |
| **Accelerator** | **GPU T4 × 2** or **GPU P100** | Provides 14.56 GB primary VRAM. |
| **Internet** | **Internet On** | Needed for git main `transformers` installation. |

---

## 4. Execution Steps in `kaggle_pilot_evaluation.ipynb`

1. **Step 1: Install Bleeding-Edge Dependencies**: Upstream `transformers`, `peft`, `trl`, `bitsandbytes`.
2. **Step 2: Configuration & Seed Management**: Sets `max_new_tokens = 1024`, greedy decoding, seed `42`.
3. **Step 3: Hardware Preflight & Tesla T4 Patch**: Enforces `_MM_OUT_DTYPE = False` for FP32 GEMM on CC 7.5.
4. **Step 4: Ingestion & Checksum Audit**: Verifies dataset and adapter paths; audits sequence length budget.
5. **Step 5: Base Model & Adapter Setup**: Loads base model once in 4-bit NF4 (~7.5 GB VRAM) and attaches PEFT adapter.
6. **Step 6: Matched Validation Recheck (N=18)**: Evaluates unadapted base vs. adapter with 1024 tokens.
7. **Step 7: Target Failure Investigation**: Detailed inspection of `syn-amb-020`, `syn-ath-055`, and `syn-cfg-017`.
8. **Step 8: Independent Test Set Evaluation (N=17)**: Evaluates the untouched test split under frozen settings.
9. **Step 9: Content & Quality Assessment Rubric**: Automated heuristic checks for explanation clarity, uncertainty calibration, and safety.
10. **Step 10: Export Comprehensive Evaluation Package**: Exports all traces and metrics to `/kaggle/working/oopsie-evaluation-artifacts/`.

---

## 5. Output Artifacts (`/kaggle/working/oopsie-evaluation-artifacts/`)

* `eval_run_config.json`: Evaluation hyperparameters and seeds.
* `env_packages.json`: PyTorch, CUDA, and library versions.
* `dataset_manifest.json`: Checksums and record counts.
* `validation_recheck_1024_baseline.json`: Complete generation traces for unadapted base model (1024 tokens).
* `validation_recheck_1024_adapter.json`: Complete generation traces for adapted model (1024 tokens).
* `independent_test_1024_adapter.json`: Generation traces on the 17 independent test cases.
* `evaluation_summary_metrics.json`: Aggregated compliance and failure metrics.
