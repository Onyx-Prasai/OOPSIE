# OOPSIE Kaggle Preflight & Smoke-Test Guide

This guide describes how to run the OOPSIE preflight checks, pipeline smoke-test, and pilot fine-tuning using Kaggle's free GPU environments.

---

## 1. Prerequisites & Access Requirements

### A. Hugging Face Access & Token
`google/gemma-4-12b-it` is a gated model released under Google's Gemma Terms of Use.
1. Log in to [Hugging Face](https://huggingface.co).
2. Visit [google/gemma-4-12b-it](https://huggingface.co/google/gemma-4-12b-it) and click **Accept terms and access model**.
3. Create an Access Token (Read permissions) under your Hugging Face account settings (**Settings -> Access Tokens**).

### B. Add Secret to Kaggle
1. Open or create a new notebook on Kaggle.
2. In the top menu bar, click **Add-ons** -> **Secrets**.
3. Add a new secret with:
   - **Label**: `HF_TOKEN`
   - **Value**: Your Hugging Face user access token.
4. Ensure the notebook has access permission checked for `HF_TOKEN`.

---

## 2. Dataset Attachment & Input Configuration

### Files to Attach
Attach the preprocessed conversational dataset files to Kaggle as a private dataset named **`oopsie-dataset`**:
- `data/processed/train_conversational.jsonl`
- `data/processed/val_conversational.jsonl`
- `data/manifest.json`
- `data/schema.json`

### Kaggle Input Paths
When attached, Kaggle will mount your dataset under:
`/kaggle/input/oopsie-dataset/`

The notebook automatically checks the following candidate paths:
- `/kaggle/input/oopsie-dataset/data/processed`
- `/kaggle/input/oopsie-dataset/processed`
- `/kaggle/input/oopsie-dataset`

---

## 3. Kaggle Notebook Session Settings

Configure your Kaggle notebook session using the right-hand **Notebook Options** panel:

| Setting | Required Value | Notes |
| :--- | :--- | :--- |
| **Accelerator** | **GPU P100** or **GPU T4 × 2** | Needs at least 15 GB VRAM for 12B QLoRA. |
| **Internet** | **Internet On** | Required to install git dependencies and fetch model weights. |
| **Persistence** | **Variables and Files** (Optional) | Keeps working directory files across sessions. |
| **Environment** | **Always use latest environment** | Ensures up-to-date CUDA and PyTorch runtimes. |

> [!WARNING]
> Dual GPUs (T4 × 2) do **not** automatically combine memory into 32 GB. Standard QLoRA processes allocate to Device 0 (16 GB). Ensure single-device peak VRAM remains within ~14.5 GB.

---

## 4. Execution Flow & Cell Order

Run all notebook cells sequentially from top to bottom:

| Step | Cell Title | Purpose |
| :---: | :--- | :--- |
| **1** | **Install Dependencies** | Installs `transformers` from git main branch (needed for `gemma4_unified`) and TRL/PEFT/bitsandbytes. |
| **2** | **Active Configuration** | Sets active parameters. By default, **SMOKE-TEST MODE** is active (`max_steps=3`, small subset). |
| **3** | **Hardware & Credentials** | Verifies GPU model, available VRAM, disk space, and retrieves `HF_TOKEN` safely from Kaggle Secrets. |
| **4** | **Dataset Ingestion & Preflight** | Parses records, asserts 0 ID overlap, validates schema compliance, and subsets active records. |
| **5** | **Tokenizer & Sequence Length** | Computes token distribution; ensures no training examples exceed `max_seq_length` (zero truncation). |
| **6** | **Completion Masking Preflight** | Verifies system instructions and user logs receive label `-100`; loss applies strictly to JSON assistant completions. |
| **7** | **4-Bit Model Loading** | Loads base model in 4-bit NF4 with bfloat16 compute dtype; attaches LoRA adapters to linear projections. |
| **8** | **Zero-Shot Baseline** | Runs greedy decoding on 1 held-out validation input before training; logs raw pre-training behavior. |
| **9** | **Smoke-Test Training** | Executes 3 optimizer steps with gradient checkpointing; saves adapter weights. |
| **10** | **Adapter Reload Verification** | Reloads adapter weights from disk and generates output on the same prompt to verify post-training persistence. |
| **11** | **Export Reproducibility Artifacts** | Exports run configuration, package versions, and generations to `/kaggle/working/oopsie-smoke-test-artifacts`. |

---

## 5. What Successful Completion Looks Like

When the smoke test runs successfully:
1. **Preflight Hardware Output**:
   ```
   Detected GPU: Tesla P100-PCIE-16GB (or Tesla T4)
   Available Primary VRAM: 15.90 GB (or 14.75 GB)
   Disk space in /kaggle/working: 19.50 GB available
   Successfully loaded HF_TOKEN from Kaggle Secrets
   ```
2. **Completion Masking Check**:
   ```
   Masking check PASSED: Loss is computed solely on the assistant's JSON completion.
   ```
3. **Training Output**:
   ```
   Step 1: loss = ...
   Step 2: loss = ...
   Step 3: loss = ...
   Adapter weights saved to: /kaggle/working/oopsie-smoke-test-adapter
   [STATUS LABEL]: OOPSIE-PIPELINE-SMOKE-TEST (Pipeline verified; not a production model).
   ```
4. **Adapter Reload Check**:
   ```
   Testing adapter reload from: /kaggle/working/oopsie-smoke-test-adapter...
   [SMOKE-TEST OUTPUT E: POST-SMOKE-TEST GENERATION]
   { ... valid JSON ... }
   ```

---

## 6. Distinguishing Smoke Test from Full Training

| Feature | Smoke-Test Mode (Default) | Full Training Mode |
| :--- | :--- | :--- |
| **Configuration** | `CONFIG["smoke_test"]["enabled"] = True` | Set `CONFIG["smoke_test"]["enabled"] = False` and `CONFIG["full_training"]["enabled"] = True` |
| **Record Count** | 6 training / 2 validation | All 85 training / 18 validation records |
| **Optimizer Steps** | Exactly 3 steps | 3 full epochs (~64 steps with grad accum = 4) |
| **Run Duration** | ~3–5 minutes total | ~25–40 minutes |
| **Output Directory** | `/kaggle/working/oopsie-smoke-test-adapter` | `/kaggle/working/oopsie-gemma4-12b-lora` |
| **Artifact Label** | `OOPSIE-PIPELINE-SMOKE-TEST` | `OOPSIE-FULL-TRAINING-PILOT` |

---

## 7. Output Artifacts to Retain

Download these artifacts from `/kaggle/working` after the run:
- `oopsie-smoke-test-adapter/` (or `oopsie-gemma4-12b-lora/`):
  - `adapter_model.safetensors`
  - `adapter_config.json`
  - `tokenizer.json` / `tokenizer_config.json`
- `oopsie-smoke-test-artifacts/`:
  - `run_config.json`: The active configuration parameters.
  - `env_packages.json`: Exact Python and library versions.
  - `training_history.json`: Step-by-step training loss logs and sample pre/post generations.
