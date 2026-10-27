# OOPSIE Gemma 4 12B Pilot Training Experiment Guide

This guide details the execution, schedule, verification, and artifact export for the first **OOPSIE pilot domain-adaptation training experiment** on Kaggle.

---

## 1. Experiment Overview

* **Objective**: Train a bounded, reproducible QLoRA adapter for `google/gemma-4-12b-it` on the 85-record curated OOPSIE error-recovery training dataset.
* **Architecture**: Gemma 4 unified decoder (`gemma4_unified`) in 4-bit NormalFloat (NF4) with double quantization.
* **Corpus & Split Strategy**:
  * **Train Split**: 85 records (`train_conversational.jsonl`)
  * **Validation Split**: 18 records (`val_conversational.jsonl`)
  * **Independent Test Split**: 17 records (`test_conversational.jsonl`)
  * **Held-Out Disjoint Benchmark**: 40 records (`evaluation/benchmark.jsonl`) reserved for post-training benchmark analysis.
* **Experiment Label**: `small_data_domain_adaptation`
* **Adapter Policy**: Initialized completely fresh with seed `42`. Does not continue from or wrap the 3-step smoke-test adapter.

---

## 2. Environment & Session Settings

In your Kaggle notebook session (**Notebook Options** in the right-hand sidebar):

| Setting | Required Value | Rationale |
| :--- | :--- | :--- |
| **Accelerator** | **GPU T4 × 2** or **GPU P100** | Allocates 14.56 GB primary VRAM on Device 0. |
| **Internet** | **Internet On** | Needed for git main `transformers` and downloading base weights. |
| **Persistence** | **Variables and Files** (Recommended) | Preserves checkpoints in `/kaggle/working`. |
| **Secrets** | `HF_TOKEN` | Required for gated Gemma 4 license access. |

---

## 3. Dataset Requirements

Ensure your Kaggle dataset (`oopsie-dataset`) contains all 3 split files:
* `train_conversational.jsonl` (SHA-256: `6cbcdb625106a244855a4e1bc29061cc5bfc615896443ca11dada9f5e096e09e`)
* `val_conversational.jsonl` (SHA-256: `df709f80671dd2e0406f535ed8af01a71639637609ff6eb4252bc1cc2033b1b6`)
* `test_conversational.jsonl` (SHA-256: `13ddbe0d3e90e8840b4117af68a5f89f0d5da788045a85898ccbee37e02ceb4d`)

---

## 4. Pilot Training Schedule & Hyperparameters

| Parameter | Pilot Value | Technical Rationale |
| :--- | :--- | :--- |
| **Epochs** | `3` | Bounded training schedule to avoid overfitting on 85 examples while establishing domain format. |
| **Per-Device Batch Size** | `1` | Strictly enforces single-sample VRAM ceiling (7.03 GB base allocated). |
| **Gradient Accumulation** | `4` | Yields effective batch size of `4`. |
| **Optimizer Steps** | `~66` | $\lceil 85 / 4 \rceil \times 3 = 22 \times 3 = 66$ total gradient updates. |
| **Learning Rate** | `2e-4` | Retains verified smoke-test learning rate with cosine decay schedule and 5% warmup. |
| **Loss Masking** | `assistant_only_loss=True` | Computes loss strictly on assistant completion tokens (prompt tokens receive `-100`). |
| **Evaluation Strategy** | `epoch` | Evaluates validation loss at the end of each epoch. |
| **Model Selection** | `eval_loss` | Saves checkpoints at each epoch and loads the best checkpoint (`load_best_model_at_end=True`). |

---

## 5. Notebook Execution Structure (`kaggle_pilot_training.ipynb`)

1. **Step 1: Install Bleeding-Edge Dependencies**: Upstream `transformers`, `trl`, `peft`, `bitsandbytes`.
2. **Step 2: Configuration & Seed Management**: Sets seed `42` for strict initialization reproducibility.
3. **Step 3: Hardware Preflight & Tesla T4 Workaround**: Enforces `_MM_OUT_DTYPE = False` for FP32 GEMM on CC 7.5; loads `HF_TOKEN`.
4. **Step 4: Dataset Ingestion, Split Isolation & Integrity Audit**: Computes SHA-256 hashes, verifies 0 ID leakage across all 3 splits, and audits JSON schema.
5. **Step 5: Full Corpus Token Length Verification**: Asserts all 120 records fit within `max_seq_length=1536` without silent truncation.
6. **Step 6: 4-Bit Base Model Loading & Fresh LoRA Setup**: Loads `google/gemma-4-12b-it` and initializes a fresh LoRA adapter (r=16, alpha=32).
7. **Step 7: Pre-Training Zero-Shot Baseline on Validation Set**: Evaluates unadapted base model on the 18 validation examples without answer leakage.
8. **Step 8: Conservative Pilot Training Run**: Executes the 3-epoch loop (~66 steps), evaluating at each epoch boundary and saving the best checkpoint.
9. **Step 9: Post-Training Validation Evaluation & Review**: Re-evaluates on the 18 validation examples; generates side-by-side comparison.
10. **Step 10: Held-Out Independent Test Set Evaluation**: Runs the final selected adapter on the 17 reserved test examples.
11. **Step 11: Export Reproducibility Artifacts**: Serializes configs, manifests, training history, and generations to `/kaggle/working/oopsie-pilot-artifacts`.

---

## 6. Output Artifacts & Directories

The pilot run isolates all outputs from the earlier smoke test:

* `/kaggle/working/oopsie-pilot-checkpoints/`: Intermediate epoch checkpoints.
* `/kaggle/working/oopsie-pilot-adapter/`: Final selected LoRA adapter weights and tokenizer configuration.
* `/kaggle/working/oopsie-pilot-artifacts/`:
  * `run_config.json`: Complete effective configuration and seeds.
  * `env_packages.json`: Exact Python, PyTorch, CUDA, and library versions.
  * `dataset_manifest.json`: Split record counts and SHA-256 checksums.
  * `training_history.json`: Step-by-step train loss, epoch evaluation losses, and best checkpoint metadata.
  * `baseline_validation_generations.json`: Pre-training unadapted generation traces.
  * `post_validation_generations.json`: Post-training validation generation traces.
  * `independent_test_generations.json`: Generation traces on the 17 independent test cases.
  * `eval_metrics.json`: Summary compliance percentages and schema error breakdowns.
