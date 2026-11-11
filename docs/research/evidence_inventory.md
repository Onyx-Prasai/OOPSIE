# OOPSIE Research Evidence Inventory

**Document Purpose**: Comprehensive, auditable record of empirical claims, supporting artifacts, experimental configurations, limitations, and verification statuses for the OOPSIE error-recovery pilot project.

---

## 1. Executive Evidence Summary Table

| Claim / Stage | Supporting Artifact (Local / Repo) | Configuration | Limitations & Epistemic Boundary | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Original 512-Token Validation** | [`artifacts/pilot_v1/artifacts/eval_metrics.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/pilot_v1/artifacts/eval_metrics.json) *(local-only)* | `google/gemma-4-12b-it` + QLoRA, `max_new_tokens=512`, default chat template, greedy (`temp=0.0`) | 15/18 schema valid. 4/18 flagged with suspected output-budget termination (1 schema-valid; 3 non-compliant with empty decoded strings). Raw token IDs not retained. | **Verified against artifact** |
| **Original-Format 1024-Token Validation Recheck** | [`artifacts/eval_1024/evaluation_summary_metrics.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/eval_1024/evaluation_summary_metrics.json) *(local-only)* | `google/gemma-4-12b-it` + QLoRA, `max_new_tokens=1024`, default chat template, greedy | 16/18 adapter schema valid vs 0/18 unadapted base. 1/18 adapter budget hit (`syn-run-114`). `syn-amb-020` passed in later run; reason for changed output was not established. | **Verified against artifact** |
| **Original-Format 1024-Token Independent Test** | [`artifacts/eval_1024/independent_test_1024_adapter.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/eval_1024/independent_test_1024_adapter.json) *(local-only)* | 17 held-out records, `max_new_tokens=1024`, default chat template, adapter only | 14/17 adapter schema valid; 3/17 budget hits. Unadapted base run omitted from serialization in this run (later evaluated in formatting experiment). | **Verified against artifact** |
| **Aligned-Format Validation (Condition D)** | [`artifacts/formatting_experiment/validation_condition_D_adapter_cand.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/formatting_experiment/validation_condition_D_adapter_cand.json) *(local-only)* | Suffix `<\|turn\>model\n`, `max_new_tokens=1024`, greedy, 18 validation records | Aligned formatter improved schema compliance from 16/18 to 18/18 and produced no heuristic delimiter-loop flags on validation split. Next-token mechanism not proved. | **Verified against artifact** |
| **Missing Test Baseline (Unadapted Base)** | [`artifacts/formatting_experiment/test_original_baseline_1024.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/formatting_experiment/test_original_baseline_1024.json) *(local-only)* | 17 test records, unadapted base model, original chat template, `max_new_tokens=1024` | 16/17 raw JSON valid, 0/17 schema valid. Base model outputs text/markdown wrapper without schema compliance. | **Verified against artifact** |
| **Enum-Guidance Development Comparison** | [`artifacts/verified_rerun_comparison/comparison_summary.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/verified_rerun_comparison/comparison_summary.json) *(local-only)* | 6 fixed development inputs, `system_prompt_v2_enum_guided` (+84 tokens) vs `system_prompt_v1` | 5/6 (83.3%) vs 6/6 (100.0%) schema valid (+16.7 percentage points on 6 development inputs, 0 paired regressions). Single-case improvement; not a general classification claim. | **Verified against artifact** |
| **Full-Schema Prompting vs. Adaptation Dry Run** | [`artifacts/dev_validation_full/full_validation_results.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/dev_validation_full/full_validation_results.json) | Kaggle T4, N=18 validation records, Protocol v1.1.0-dev, greedy, 1024 max tokens | Cond A (Base Zero-Shot): 0/18 (0.0%). Cond B (Adapter Zero-Shot): 12/18 (66.7%), 1 budget hit, 0 delimiter loops. Cond C (Base 1-Shot): 0/18 (0.0%). Base outputs emitted conversational preambles/prose; all 18 adapted outputs began with JSON prefix. | **Verified against local disk artifacts** |
| **Final 40-Case Benchmark Evaluation** | [`artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json) | Kaggle T4, N=40 held-out benchmark records, Protocol v1.2.0-frozen, 4 conditions (160 passes) | Cond A (Base Zero-Shot): 0/40 (0.0%). Cond B (Adapter Zero-Shot): 38/40 (95.0%). Cond C (Base 1-Shot): 0/40 (0.0%). Cond D (Adapter Service Prompt): 39/40 (97.5%). 160/160 passes completed; 0 crashes; 0 budget hits. Human review pending. | **Verified against local disk artifacts** |
| **FastAPI Real-GPU Service In-Process Test** | [`artifacts/gpu_integration/gpu_service_integration_report.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/gpu_integration/gpu_service_integration_report.json) *(local-only)* | Tesla T4 GPU (14.56 GB VRAM), 4-bit NF4, in-process `TestClient` | Load time 225.29s (allocated 5.30 GB VRAM). Health-endpoint latency during active generation was ~3.2 ms. Schema validator correctly rejected out-of-enum output (HTTP 422). | **Verified against artifact** |
| **Automated Client Contract Tests** | [`apps/web-demo/tests/client-contract.test.mjs`](file:///c:/Users/onyxe/Desktop/OOPSIE/apps/web-demo/tests/client-contract.test.mjs) | Node.js test harness verifying HTTP payload parser and error mapping | Validates client parsing logic against sample envelopes; does not execute GPU inference. | **Verified** |
| **Reported Manual Mock-Browser Interaction** | User interaction logs & browser UI capture | Web demo connected to local mock engine (`OOPSIE_USE_MOCK_ENGINE=1` on port 8001) | Evaluates static test fixtures. Does not execute model inference or test live GPU backend. | **Reported / Mechanically Verified for Mock** |
| **Live Browser-to-Real-GPU End-to-End** | None | Public browser connecting to remote GPU server | No public tunnel, reverse proxy, or live GPU web deployment has been hosted or completed. | **Unverified / Not Completed** |

---

## 2. Dataset Lineage & Cryptographic Audit

### 2.1 Reconciled Record Counts & Hashes

The repository dataset splits were cryptographically audited against training artifacts:

| Split | Current Repository File | Current Count | SHA-256 Hash of Current File | Historical Training Export Match |
| :--- | :--- | :---: | :--- | :--- |
| **Train** | [`data/train.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/train.jsonl) | 85 | `be401b7fdb2c4365a5f341e6a46216252855ddcf65bdb3794a886c2e88430846` | Matches export SHA-256 (`6cbcdb...`) |
| **Validation** | [`data/validation.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/validation.jsonl) | 18 | `34cc646f169b528716fbb7b26b289af9214a7ca451536287157a2cfbddae8a3a` | Matches export SHA-256 (`df709f...`) |
| **Independent Test** | [`data/test.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/test.jsonl) | 17 | `c4b2d10d0f59bec9acb91b815069bfa728156be49559b8bc12836b4c3ac0ca72` | Matches eval_1024 SHA-256 (`13ddbe...`) |
| **Held-Out Benchmark** | [`evaluation/benchmark.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/benchmark.jsonl) | 40 | `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd` | Reserved benchmark (Hash reconciled with Git commit `083c9f6`) |

### 2.2 Epistemic Distinction in Training Lineage

To maintain scientific integrity, three distinct levels of evidence must be kept separate:

1. **Level A (Byte-Identical Reconstruction of the Training Export):**
   - Running [`training/export_conversational.py`](file:///c:/Users/onyxe/Desktop/OOPSIE/training/export_conversational.py) on the current repository files generates:
     - `train_conversational.jsonl`: 85 records, SHA-256 = `6cbcdb625106a244855a4e1bc29061cc5bfc615896443ca11dada9f5e096e09e`
     - `val_conversational.jsonl`: 18 records, SHA-256 = `df709f80671dd2e0406f535ed8af01a71639637609ff6eb4252bc1cc2033b1b6`
     - `test_conversational.jsonl`: 17 records, SHA-256 = `13ddbe0d3e90e8840b4117af68a5f89f0d5da788045a85898ccbee37e02ceb4d`
   - *Status: Fully confirmed via independent local execution.*

2. **Level B (Evidence That the Specific Training Run Consumed That Export):**
   - The saved training artifact [`artifacts/pilot_v1/artifacts/dataset_manifest.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/pilot_v1/artifacts/dataset_manifest.json) records:
     - `train`: 85 records, SHA-256 = `6cbcdb625106a244855a4e1bc29061cc5bfc615896443ca11dada9f5e096e09e`
     - `validation`: 18 records, SHA-256 = `df709f80671dd2e0406f535ed8af01a71639637609ff6eb4252bc1cc2033b1b6`
     - `test`: 0 records, SHA-256 = `NOT_FOUND`
   - *Interpretation:* Level B is established by cryptographic log match for train and validation. Level A alone does not prove Level B; the artifact manifest provides the required empirical link.

3. **Level C (Evidence Linking Saved Adapter to the Selected Checkpoint):**
   - The run configuration [`artifacts/pilot_v1/artifacts/run_config.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/pilot_v1/artifacts/run_config.json) and training history [`artifacts/pilot_v1/artifacts/training_history.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/pilot_v1/artifacts/training_history.json) record 3 epochs (66 total training steps), with lowest validation loss at step 44 (eval_loss: 0.693, epoch 2). Checkpoint-44 was exported as the adapter.
   - *Interpretation:* The adapter weights correspond to checkpoint-44.

### 2.3 Preservation of the Historical Missing-Test Entry

The original training manifest's entry (`test`: `{"records": 0, "sha256": "NOT_FOUND"}`) is preserved as an accurate historical record. During the initial Kaggle pilot training bundle creation, `test_conversational.jsonl` was absent from the uploaded archive. The pilot training run proceeded on 85 training and 18 validation examples. The independent test set was subsequently uploaded and evaluated in the dedicated 1024-token evaluation notebook (`artifacts/eval_1024/`), where its SHA-256 matched `13ddbe0d...` exactly.

### 2.4 Reconciliation of Historical Record Counts

- **"60 active examples"** documented in [`data/README.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/README.md): Reflected an earlier development state (41 train, 10 val, 9 test) before Batches 3 and 4 were merged. The README explicitly described this as expanding towards 120 total records.
- **"75 training examples"** mentioned in [`evaluation/audits/pilot_eval_audit_v1/real_gpu_enum_comparison_audit.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/audits/pilot_eval_audit_v1/real_gpu_enum_comparison_audit.md): The exact origin of the 75-record figure is **unresolved** in dated commit history. It may have reflected an informal draft count during category distribution analysis before Batch 4 brought the training split to 85, but no intermediate 75-record commit exists in Git.
- **"40 benchmark records"** in [`evaluation/benchmark.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/benchmark.jsonl) (SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`): Reserved held-out evaluation corpus committed in `083c9f6`. Complete cryptographic audit confirms 0/40 ID collisions and 0/40 exact raw_error text collisions against Train (N=85), Validation (N=18), and Test (N=17). All 9 expected categories match canonical schema enums. Limitation: Synthetic scenarios share common developer failure patterns (e.g. peer dependency conflicts, RLS policies), so distinct IDs/strings do not imply complete domain independence. An earlier draft SHA-256 (`e50df2...`) was identified as an errant reference and reconciled with the verified Git commit.

---

## 3. Disaggregated Validation & Test Results

Experimental findings must remain strictly configuration-specific. Below is the detailed disaggregation.

### 3.1 Original 512-Token Validation Run (N=18)
- **Artifact:** `artifacts/pilot_v1/artifacts/eval_metrics.json` and `post_validation_generations.json`.
- **Condition:** `google/gemma-4-12b-it` + QLoRA adapter, greedy, `max_new_tokens=512`, default chat template (`add_generation_prompt=True`).
- **Results:**
  - Strict Schema Valid: **15 / 18 (83.3%)**
  - Flagged Truncated / Suspected Budget Termination: **4 / 18 (22.2%)**
- **Disaggregation of Overlapping Failure Categories:**
  - 1 record (`syn-run-114`) was **schema valid** despite being flagged `truncated=True` (decoded length: 1,873 characters).
  - 3 records (`syn-amb-020`, `syn-ath-055`, `syn-cfg-017`) failed schema compliance (`json_valid=False`, `schema_valid=False`), were flagged `truncated=True`, and decoded to empty strings (`raw_len=0`).
  - *Epistemic Note:* Because raw generated token IDs and special tokens were not retained in this specific run, control-token loops cannot be definitively confirmed from Run 1 artifacts alone; they are recorded as **suspected output-budget terminations**.

### 3.2 Original-Format 1024-Token Validation Recheck (N=18)
- **Artifact:** `artifacts/eval_1024/evaluation_summary_metrics.json` and `validation_recheck_1024_adapter.json`.
- **Condition:** Identical prompt format, expanded budget `max_new_tokens=1024`.
- **Results:**
  - Unadapted Base Model: JSON Parse Valid: 16/18 (88.9%), Schema Valid: **0 / 18 (0.0%)**
  - Adapted Pilot Model: JSON Parse Valid: 16/18 (88.9%), Schema Valid: **16 / 18 (88.9%)**
  - Suspected Output-Budget Terminations: **1 / 18 (5.6%)** (`syn-run-114`)
- **Key Observation on `syn-amb-020`:**
  - `syn-amb-020` passed in this later run (generated 324 tokens, 1,507 characters, valid schema). The underlying cause for the changed output between runs was **not established** because raw generation states and token IDs were not logged in Run 1.

### 3.3 Original-Format 1024-Token Test Evaluation (N=17)
- **Artifact:** `artifacts/eval_1024/independent_test_1024_adapter.json`.
- **Condition:** 17 held-out records, `max_new_tokens=1024`, default chat template, adapted model.
- **Results:**
  - Adapted Pilot Model: JSON Parse Valid: 14/17 (82.4%), Schema Valid: **14 / 17 (82.4%)**
  - Flagged Budget Hits: **3 / 17 (17.6%)**
  - Unadapted Base Run: Was not serialized to disk during this specific evaluation execution (later evaluated under matching conditions in the formatting experiment).

### 3.4 Missing Test Baseline Evaluation (N=17)
- **Artifact:** `artifacts/formatting_experiment/test_original_baseline_1024.json`.
- **Condition:** 17 test records, unadapted base model, `max_new_tokens=1024`, default chat template.
- **Results:**
  - JSON Parse Valid: **16 / 17 (94.1%)**
  - Schema Conformance: **0 / 17 (0.0%)**
  - *Observation:* The base model predominantly outputs unstructured markdown explanations containing code snippets or generic JSON keys that do not adhere to the required 10-key schema.

### 3.5 Aligned-Format Validation Evaluation (N=18)
- **Artifact:** `artifacts/formatting_experiment/validation_condition_D_adapter_cand.json`.
- **Condition:** Suffix delimiter formatted to match training data exactly (`<|turn>model\n`), suppressing extra `<|channel>` tags.
- **Results:**
  - Adapted Pilot Model: JSON Parse Valid: **18 / 18 (100.0%)**, Schema Valid: **18 / 18 (100.0%)**
  - Delimiter-Loop Flags: **0 / 18 (0.0%)**
- **Bounded Finding:** The aligned formatter improved schema compliance from 16/18 to 18/18 and produced no heuristic delimiter-loop flags in the evaluated validation condition. The exact logit-level next-token prediction mechanism remains unestablished.

### 3.6 Enum-Guidance Controlled Development Comparison (N=6)
- **Artifact:** `artifacts/verified_rerun_comparison/comparison_summary.json`.
- **Condition:** 6 fixed service verification inputs evaluated on Kaggle Tesla T4 via FastAPI in-process service.
- **Results:**
  - Condition A (`system_prompt_v1`, unguided enums): Schema Valid: **5 / 6 (83.3%)**, 1 category enum error (`svc_regression_eslint_006`).
  - Condition B (`system_prompt_v2_enum_guided`, +84 prompt tokens): Schema Valid: **6 / 6 (100.0%)**, 0 category enum errors.
- **Bounded Finding:** Enum guidance provided a one-case improvement on 6 fixed development inputs (+16.7 percentage points, with no observed paired regressions). It resolves category drift on this specific test case, but does not constitute a generalized domain classification improvement.

### 3.7 Full-Schema Prompting vs. Adaptation Development Dry Run (N=18, Protocol v1.1.0-dev)
- **Status**: **Verified against local disk artifacts (`artifacts/dev_validation_full/`).**
- **Recovered Artifact Hashes**:
  - Archive `artifacts/dev_val_artifacts.zip` (61,940 bytes): SHA-256 = `df4c5291a9774402108ede4c492b3f52cfbd1cd34e6760e6fa50bc0fab210af1`
  - Raw results `full_validation_results.json` (220,246 bytes): SHA-256 = `3bde15e1812c03d4cd807a49bb89d734db1b374a865bd743630c15a83f3ae6a1`
  - Summary metrics `summary_metrics.json` (1,099 bytes): SHA-256 = `af5a6d19eb88479739907de4256ed67be9564d66fa841223fc51024efedfe422`
  - Review sheet `blinded_human_review_sheet.md` (154,071 bytes): SHA-256 = `6474f37ad145cd2cc957c2eb266511c8851ef8e6bfc7a59e1d3c737184627e7d`
- **Recomputation Verification**: Independent local recomputation from `raw_completion` using [`inference/parser.py`](file:///c:/Users/onyxe/Desktop/OOPSIE/inference/parser.py) confirmed 100% agreement with logged values across all 54 executions (18 cases x 3 conditions):
  - Condition A: 0/18 JSON valid, 0/18 schema valid, 18/18 adapter disabled verified.
  - Condition B: 12/18 JSON valid, 12/18 schema valid, 1/18 budget hit, 8/18 category agreement, 18/18 adapter enabled verified.
  - Condition C: 0/18 JSON valid, 0/18 schema valid, 18/18 adapter disabled verified.
- **Technical Report:** [`docs/research/development_dry_run_report_v1.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/docs/research/development_dry_run_report_v1.md).
- **Environment:** Kaggle Tesla T4 GPU (14.56 GB VRAM, Python 3.10), greedy decoding (`temp=0.0`), `max_new_tokens=1024`.
- **System Prompt**: `system_prompt_v2_enum_guided` + complete 100-line JSON schema embedded as markdown block.
- **Results by Condition**:
  - **Condition A (Base Zero-Shot)**: Attempted: 18, Completed: 18, Crashes: 0. Raw JSON Parse Valid: **0 / 18 (0.0%)**, Schema Valid: **0 / 18 (0.0%)**, Budget Hits: 0/18 (0.0%), Category Agreement: 0/18 (0.0%), Heuristic Safety Pass: 18/18 (100.0%). Mean latency: 110.43s.
  - **Condition B (Adapter Zero-Shot, Training-Aligned Suffix)**: Attempted: 18, Completed: 18, Crashes: 0. Raw JSON Parse Valid: **12 / 18 (66.7%)**, Strict Schema Valid: **12 / 18 (66.7%)**, Budget Hits: 1/18 (5.6%) (`syn-run-053`), Delimiter Loops: 0/18 (0.0%), Category Agreement (All Attempted): 8/18 (44.4%), Category Agreement (Parseable Only): 8/12 (66.7%), Heuristic Safety Pass: 18/18 (100.0%). Mean latency: 134.73s.
  - **Condition C (Base 1-Shot, syn-dep-001)**: Attempted: 18, Completed: 18, Crashes: 0. Raw JSON Parse Valid: **0 / 18 (0.0%)**, Schema Valid: **0 / 18 (0.0%)**, Budget Hits: 0/18 (0.0%), Category Agreement: 0/18 (0.0%), Heuristic Safety Pass: 18/18 (100.0%). Mean latency: 111.03s.
- **Paired 2x2 Transitions (Base A vs. Adapter B)**: Both Pass: 0/18, Adapter-Only Pass: 12/18, Base-Only Pass: 0/18, Both Fail: 6/18.
- **Descriptive Prefix Finding**: The base conditions (A and C) achieved 0/18 raw JSON parse validity under the evaluated setup, emitting conversational preambles/prose. All 18 adapted outputs reportedly began with a JSON-like object prefix; 12/18 passed strict parsing and schema validation.
- **Six Adapter Non-Conforming Cases**:
  - `syn-run-053`: Output-budget termination at 1024 tokens mid-string (`hit_budget=True`, `eos_detected=False`).
  - `syn-cfg-017`: Unrecognized backslash escape sequence (`Invalid \escape`).
  - `syn-dat-116`: Unescaped ASCII control character inside string literal (`Invalid control character`).
  - `syn-amb-086`, `syn-ath-028`, `syn-run-114`: Unexpected tokens where delimiters were expected (`Expecting ',' delimiter`).
- **Configuration Delta vs. Earlier 18/18 Result**: Earlier Condition D run used `system_prompt_v1` without enum guidance and without embedding the raw JSON schema text (~300 tokens vs. ~710 tokens). Because prompt length, embedded schema, and enum text varied simultaneously, the performance delta cannot be attributed solely to schema inclusion. Neither result replaces or is averaged with the other.

### 3.8 Final 40-Case Held-Out Benchmark Evaluation (N=40, Protocol v1.2.0-frozen)
- **Status**: **Verified against local disk artifacts (`artifacts/benchmark_v1_2_0/benchmark_results/`).**
- **Artifact Hashes**:
  - Downloaded Tarball `oopsie_benchmark_results_v1_2_0.tar.gz` (234,322 bytes): SHA-256 = `cf24eec1a5c3347ae826fec4b5cbfb7133a1c4ce92aace3eab2b048bdd37f4eb`
  - Raw results `benchmark_results_full.json` (635,014 bytes): SHA-256 = `6021aaab2616aec8cd09679532686eb09d424adfb15c2d2e22469f6c75aca397`
  - Summary metrics `summary_metrics.json` (1,885 bytes): SHA-256 = `0a759c693717240293fd2458071e779b8244155180ffa496b59a8f172c377644`
  - Review sheet `blinded_human_review_sheet.md` (418,686 bytes): SHA-256 = `eaf69fea4ef0f8fc1e62b0839d0a1b24561562e49c21d1568839300eaf152aea`
  - Unblinded key `unblinded_review_key.json` (5,918 bytes): SHA-256 = `738f440aa43ce3f11ebdc5dbbfebb59cdcc2792d27a9f2812d3234175627835d`
  - Checkpoint stream `checkpoint_results.jsonl` (628,592 bytes): SHA-256 = `e6be2fca2763544fba0537f21339ee69e7341c095ebbf964364aecf9fa7aa0f4`
- **Execution Accounting**: 160 attempted, 160 completed, 0 generation exceptions, 0 budget hits (0.0%). Total GPU runtime: 301.6 minutes (5.03 hours) on Kaggle Tesla T4.
- **Results Across Four Conditions**:
  - **Condition A (Base Zero-Shot + Schema)**: Strict Schema Valid: **0 / 40 (0.0%)** (95% CI: [0.0%, 8.8%]), Raw JSON Valid: 0/40 (0.0%), Budget Hits: 0/40, Category Agreement: 0/40, Mean Latency: 118.62s. Emitted conversational prose/markdown wrappers.
  - **Condition B (Adapter Zero-Shot + Schema, Training-Aligned Suffix)**: Strict Schema Valid: **38 / 40 (95.0%)** (95% CI: [83.5%, 98.6%]), Raw JSON Valid: 38/40 (95.0%), Budget Hits: 0/40, Category Agreement (All Attempted): 28/40 (70.0%), Category Agreement (Parseable Only): 28/38 (73.7%), Mean Latency: 114.42s.
  - **Condition C (Base 1-Shot + Schema, syn-dep-001)**: Strict Schema Valid: **0 / 40 (0.0%)** (95% CI: [0.0%, 8.8%]), Raw JSON Valid: 0/40 (0.0%), Budget Hits: 0/40, Category Agreement: 0/40, Mean Latency: 119.35s. Emitted multi-turn conversational markdown wrappers.
  - **Condition D (Adapter Current Service Prompt, No Schema Block)**: Strict Schema Valid: **39 / 40 (97.5%)** (95% CI: [87.1%, 99.6%]), Raw JSON Valid: **40 / 40 (100.0%)**, Budget Hits: 0/40, Category Agreement (All Attempted): 28/40 (70.0%), Category Agreement (Parseable Only, N=40): 28/40 (70.0%), Category Agreement (Schema-Valid Only, N=39): 27/39 (69.2%), Mean Latency: 99.88s.
- **Paired 2x2 Contingency Transitions**:
  - *Base A vs. Adapter B (Primary)*: Both Pass: 0/40 (0.0%), Adapter-Only Pass: 38/40 (95.0%), Base-Only Pass: 0/40 (0.0%), Neither Pass: 2/40 (5.0%). Exact paired McNemar binomial test: $p \approx 7.28 \times 10^{-12}$; Edwards continuity-corrected $\chi^2 = 36.03, p \approx 1.95 \times 10^{-9}$.
  - *Adapter B vs. Adapter D (Prompt Delta)*: Both Pass: 37/40 (92.5%), D-Only Pass: 2/40 (5.0%), B-Only Pass: 1/40 (2.5%), Neither Pass: 0/40 (0.0%).
- **Forensic Check on Non-Conforming Cases**:
  - Condition B (`bench-firebase-01`, `bench-nextjs-01`): Emitted invalid backslash escape sequence (`\'`) inside require/import string literals; structurally complete JSON objects otherwise.
  - Condition D (`bench-npm-03`): Emitted valid JSON matching category `dependency`, but omitted the required empty list property `matched_recipes: []`. No causal claim regarding prompt schema omission is asserted.
- **Human Technical Review Status**: Blinded review sheet generated with randomized `System Alpha`, `Beta`, `Gamma`, `Delta` assignments. Manual human technical scoring remains pending.

---

## 4. Systems & Integration Verification

### 4.1 Automated Contract & Unit Tests
- **Artifacts:** [`apps/web-demo/tests/client-contract.test.mjs`](file:///c:/Users/onyxe/Desktop/OOPSIE/apps/web-demo/tests/client-contract.test.mjs), [`tests/test_inference_service.py`](file:///c:/Users/onyxe/Desktop/OOPSIE/tests/test_inference_service.py).
- **Scope:** Verifies HTTP response envelope deserialization, HTTP error code translation (400, 422, 429, 503), client timeout fallbacks, and mock engine configuration switches.
- **Status:** PASS.

### 4.2 Reported Mock-Engine Web Demo Interaction
- **Artifacts:** Local browser session logs, user-facing screenshot artifacts.
- **Scope:** Web interface rendered on local Vite server connecting to `http://127.0.0.1:8001/v1/analyze` running under `OOPSIE_USE_MOCK_ENGINE=1`.
- **Finding:** Browser UI correctly displays the mock-mode banner and displays pre-configured static test fixtures. This confirms client-side UI rendering and local IPC, but does not evaluate model inference.

### 4.3 In-Process Real-GPU FastAPI Verification
- **Artifacts:** `artifacts/gpu_integration/gpu_service_integration_report.json`.
- **Environment:** Kaggle Tesla T4 GPU (14.56 GB total VRAM).
- **Execution:** FastAPI `TestClient` (in-process).
- **Observations:**
  - Model load duration: 225.29 seconds; VRAM allocated: 5.30 GB, reserved: 5.68 GB.
  - Non-blocking event loop check: `GET /health` answered in **3.2 ms** during active background generation.
  - Concurrency control: GPU semaphore correctly held worker threads and returned HTTP 429 upon capacity saturation.
  - Inference validation: Model generated syntactically valid JSON with an unallowed category string, which the service validator intercepted and rejected with HTTP 422 `SCHEMA_ERROR`. This demonstrates strict service boundary enforcement.

### 4.4 Live Browser-to-Real-GPU Integration
- **Status:** **Unverified / Not completed.**
- No public URL, reverse proxy tunnel, or cloud-hosted GPU backend has been connected to the web demo.

---

## 5. Safety, Review & Operational Boundaries

1. **Advisory Boundary:** OOPSIE is strictly an advisory tool. It does not execute terminal commands, modify source code, or deploy applications.
2. **Redaction Limitations:** Secret redaction uses heuristic regex patterns. Secret removal is best-effort and not guaranteed; users must manually sanitize logs.
3. **Schema Validity vs. Correctness:** Schema compliance measures JSON structural conformance, not factual correctness, technical accuracy, or diagnostic relevance.
4. **Safety Heuristics vs. Semantic Safety:** Safety checks are automated regex filters scanning for known destructive strings (e.g., `rm -rf /`, `DROP DATABASE`). They do not establish semantic safety or prevent subtle architectural errors.
5. **Human Review State:** The 17-case independent test split review sheet ([`evaluation/audits/pilot_eval_audit_v1/test_set_blinded_review_sheet.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/audits/pilot_eval_audit_v1/test_set_blinded_review_sheet.md)) contains empty evaluation cells. Blinded human technical review remains incomplete.
6. **Corpus Review State:** Dataset records carry `review.status = "unreviewed"` in scenario metadata. The corpus must not be described as expert-reviewed or human-curated without supporting records.

