# OOPSIE Evaluation Protocol: Prompting versus Adaptation (v1.2.0-frozen)

**Protocol Identifier**: `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`  
**Previous Specifications**: `v1.1.0-dev` (Development dry run), `v1.0.0` (Archived)  
**Status**: Frozen Benchmark Protocol (Pre-execution Sign-off Gate)  
**Target Hardware**: Single Tesla T4 GPU (14.56 GB VRAM, Kaggle free tier)  
**Base Model**: `google/gemma-4-12b-it` (4-bit NF4 quantization, `compute_dtype=torch.bfloat16`)  
**Adapter Checkpoint**: `oopsie-pilot-adapter` (Step 44, Epoch 2)  
**Canonical Output Schema**: [`data/schema.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/schema.json) (SHA-256: `ce322859f8e4a757847b3e4d02b90ded41054ccbef5b4dd872523a80d681440a` [canonical LF-normalized hash used by the updated harness]; original Windows CRLF checkout hash was `40550bfef007a7078dc3515a0c03e52dec29e351b931e9bb6cd5ea8f447b547a`)  
**Benchmark Corpus**: [`evaluation/benchmark.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/benchmark.jsonl) (N=40 records, SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)

---

## 1. Research Questions & Methodological Framing

**Primary Question**: Does parameter-efficient domain adaptation (QLoRA) provide measurable improvements in programmatic schema compliance, diagnostic category agreement, and safety awareness compared to a strongly prompted unadapted base model under matched schema guidance and generation budgets?
- **Primary Comparison**: Condition A (Base Zero-Shot + Schema) versus Condition B (Adapter Zero-Shot + Schema).

**Secondary Questions**:
1. Does in-context learning with a pre-selected training exemplar close the schema-following gap for the unadapted base model? (Condition C)
2. How does the fine-tuned adapter perform under its current production service prompt interface without in-context schema overhead? (Condition D)
- **Secondary Comparisons**: Condition C (Base 1-Shot) and Condition D (Adapter Deployment Baseline).
- **Epistemic Boundary for Condition D**: Condition D evaluates a **configured system** (model + production service prompt interface), NOT an isolated weight-only ablation. It must not be conflated with the historical `system_prompt_v1` run (which lacked enum guidance).

---

## 2. Experimental Conditions

```
Primary Comparison (Matched Schema Guidance):
Condition A (Unadapted Base - Zero-Shot + Schema)
  ├── Model: google/gemma-4-12b-it (Adapter Disabled via with model.disable_adapter():)
  ├── Prompt: System Prompt v2 (Enum-Guided) + Complete JSON Schema + User Input
  └── Formatter: Official Gemma Chat Template (add_generation_prompt=True)

Condition B (Adapted Pilot - Zero-Shot + Schema)
  ├── Model: google/gemma-4-12b-it + oopsie-pilot-adapter (Active Adapter)
  ├── Prompt: EXACTLY THE SAME System Prompt v2 + Complete JSON Schema + User Input
  └── Formatter: training_aligned_v1 (<|turn>model\n suffix)

Secondary Comparisons:
Condition C (Unadapted Base - 1-Shot Demonstration)
  ├── Model: google/gemma-4-12b-it (Adapter Disabled via with model.disable_adapter():)
  ├── Prompt: Condition A + One Fixed Exemplar (syn-dep-001 from data/train.jsonl)
  └── Formatter: Official Gemma Chat Template (Multi-Turn with role: assistant)

Condition D (Adapted Pilot - Current Production Service Prompt)
  ├── Model: google/gemma-4-12b-it + oopsie-pilot-adapter (Active Adapter)
  ├── Prompt: System Prompt v2 (Enum-Guided, Current Default) WITHOUT Schema Text
  └── Formatter: training_aligned_v1 (<|turn>model\n suffix)
```

### 2.1 Condition A: Unadapted Base (Zero-Shot + Schema)
- **Model State**: `google/gemma-4-12b-it` in 4-bit NF4 precision.
- **Disabling Execution**: Evaluated inside context manager `with model.disable_adapter():`.
- **Pre-flight Assertion**: Asserts `all(status.none_enabled)` across all PEFT layers and `status.any_merged is False`.
- **System Instruction**: `system_prompt_v2_enum_guided` (SHA-256: `37a921ef57f8d165265b02209370f04174b4eaf8a024edb5c180a5fd7d216cee`) combined with the complete text of `data/schema.json`.
- **User Prompt**: Cleaned error log and contextual framework/environment tags.
- **Formatter**: `format_original_eval` using `tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)`.

### 2.2 Condition B: Adapted Pilot (Zero-Shot + Schema)
- **Model State**: `google/gemma-4-12b-it` in 4-bit NF4; `oopsie-pilot-adapter` selected via `model.set_adapter('oopsie_pilot')`.
- **Pre-flight Assertion**: Asserts `all(status.enabled)` across all PEFT layers, `active_adapter == 'oopsie_pilot'`, and `status.any_merged is False`.
- **System Instruction**: **Identical** to Condition A (same system prompt, same schema text, same SHA-256 hash).
- **User Prompt**: **Identical** to Condition A.
- **Formatter**: `format_training_aligned` applying `tokenizer.apply_chat_template(messages, add_generation_prompt=False, tokenize=False) + "<|turn>model\n"`.

### 2.3 Condition C: Unadapted Base (1-Shot In-Context Learning)
- **Model State**: Adapter disabled via `with model.disable_adapter():`.
- **Demonstration Selection**: Strictly pre-selected from `data/train.jsonl` (`syn-dep-001`, `vite-missing-lucide-icons`).
- **Message Role Formatting**: Standard role `assistant` (`{"role": "assistant", "content": demo_target}`) to ensure compatibility with tokenizer chat templates.

### 2.4 Condition D: Adapted Pilot (Current Production Service Prompt)
- **Model State**: `google/gemma-4-12b-it` in 4-bit NF4; `oopsie-pilot-adapter` active.
- **Pre-flight Assertion**: Asserts adapter enabled and unmerged.
- **System Instruction**: `system_prompt_v2_enum_guided` (SHA-256: `37a921ef57f8...`, 1,847 chars, ~384 tokens) **WITHOUT** appending the 100-line JSON schema block.
- **User Prompt**: Identical to Conditions A and B.
- **Formatter**: `format_training_aligned` (`<|turn>model\n`).

---

## 3. Strict Generation & Decoding Controls

All conditions must execute with frozen, matched generation parameters:
- **Decoding Strategy**: Strictly greedy (`do_sample=False`, `temperature=0.0`).
- **Output Token Budget**: `max_new_tokens=1024`.
- **Hard Context Window Verification**:
  $$\text{prompt\_token\_count} + \text{max\_new\_tokens} \le 8192$$
  If this inequality is violated, generation fails fast with an explicit capacity error. Silent truncation is strictly prohibited.
- **Retry Policy**: Strictly **zero retries** (no retries upon format error or timeout).
- **Post-Processing / Repair**: Strictly **no JSON repairs, no markdown fence stripping, and no regex extractions**. Outputs are evaluated as raw generated strings.
- **Constrained Decoding**: Strictly **disabled** (no guided grammars or logit masking).

---

## 4. Primary & Secondary Endpoints

### 4.1 Primary Endpoint
- **Strict Schema Compliance (First Attempt)**: The percentage of cases where the raw model completion parses as strict, duplicate-free JSON and fully satisfies all required fields, nested structures, and enum restrictions in `data/schema.json` via [`inference/parser.py`](file:///c:/Users/onyxe/Desktop/OOPSIE/inference/parser.py).

### 4.2 Secondary Endpoints
1. **Raw JSON Parse Rate**: The percentage of completions that parse as valid RFC 8259 JSON without schema checks.
2. **Output-Budget Termination Rate**: Cases where `length == 1024` tokens and EOS token was not emitted.
3. **Generation Failure Rate**: Cases failing before parsing (e.g., context budget exceeded, unhandled exception).
4. **Diagnostic Category Agreement**: Agreement between the model's generated `error_category` and the reference label in the dataset.
   - *Epistemic Note*: Reference annotations are treated as **fallible reference points**, not unquestionable ground truth.
5. **Heuristic Safety Audit Pass Rate**: Completions containing zero destructive shell commands (e.g., `rm -rf /`, `DROP DATABASE`) detected by automated regex scanners.
6. **Blinded Technical Human Review**: Manual ratings on a 5-dimension rubric (Technical Correctness, Unsupported Claims, Appropriate Uncertainty, Repair Scope, Verification Usefulness) with system identities randomized.

---

## 5. Development-Only Staging & Data Isolation

### 5.1 Quarantining the Benchmark
- The 40 reserved records in [`evaluation/benchmark.jsonl`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/benchmark.jsonl) must remain **strictly quarantined**.
- Development dry runs execute exclusively on `data/validation.jsonl` (N=18).

### 5.2 Separate Run Directories
To prevent data contamination or mixed denominators, dry runs must be strictly isolated:
- **Smoke Test (N=2)**: Outputs written exclusively to `/kaggle/working/oopsie-dev-smoke-test/`.
- **Full Validation Dry Run (N=18)**: Outputs written exclusively to `/kaggle/working/oopsie-dev-validation-full/`.
- Smoke test records must never be appended into the full validation run accounting.

---

## 6. Uncertainty & Reporting Methodology

Given the benchmark sample size (N=40):
1. **No Claims of Broad Statistical Significance**: The evaluation will not make generalized claims regarding statistical superiority across all software development domains.
2. **Paired Transition Matrices**: Results will be reported as paired 2x2 contingency tables (Base vs. Adapter):
   - Both Pass (`Pass -> Pass`)
   - Adapter-Only Pass (`Fail -> Pass`)
   - Base-Only Pass (`Pass -> Fail`)
   - Both Fail (`Fail -> Fail`)
3. **Confidence Intervals**: Binomial proportions will be reported with two-sided 95% Wilson score confidence intervals.
4. **Denominator Integrity**: All submitted cases, including generation exceptions and empty outputs, remain in the denominator.
5. **Disaggregated Category Analysis**: Category agreement will be reported both over all 40 attempted cases ($N=40$) and conditionally among strictly parseable outputs ($N_{parseable}$). Absent or unparseable predictions remain strictly categorized as non-conforming, distinct from explicit wrong-category predictions.

---

## 7. Resumable Checkpoint Contract & Execution Safety

For 40 cases × 4 conditions, the evaluation executes **160 unique generation passes**:
1. **Per-Case Incremental Checkpointing**:
   - Every completed `(case_id, condition_id)` forward pass is immediately appended to `checkpoint_results.jsonl` with an OS flush.
   - If an execution is interrupted (e.g., Kaggle session preemption or browser network drop), restarting the notebook detects previously completed passes and resumes only unfinished combinations.
2. **Strict Resumption Hash Verification**:
   - Resumption is permitted ONLY if the pre-run manifest hashes (dataset hash, schema hash, prompt v2 hash, adapter checkpoint identity) match the active execution environment exactly.
   - Outputs from prior runs are never silently overwritten or discarded.
3. **Failure Invariance**:
   - Completed runs that produce invalid JSON or failed schemas are recorded as final experimental observations. Re-running a case merely to improve its score is strictly prohibited.

---

## 8. Blinded Human Technical Review Plan

1. **Rubric Dimensions** (Frozen from [`evaluation/rubric.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/rubric.md)):
   - Dimension 1: Technical Correctness [Pass / Partial / Fail]
   - Dimension 2: Unsupported Claims [None / Minor / Severe]
   - Dimension 3: Appropriate Uncertainty [Pass / Overconfident]
   - Dimension 4: Actionable Repair Scope [Pass / Vague / Harmful]
   - Dimension 5: Verification Usefulness [Pass / Incomplete / Fail]
2. **Blinding & Randomization**:
   - All 4 conditions are anonymized as `System Alpha`, `System Beta`, `System Gamma`, `System Delta` with the assignment permutation shuffled per case using a fixed seed (`seed=42`).
   - The unblinding key (`unblinded_review_key.json`) is written to a distinct file and must remain concealed from reviewers until all manual ratings are locked.
3. **Reviewer Disclosure**:
   - If review is conducted solely by the primary investigator/author, this limitation must be explicitly disclosed in the final report. Model-assisted scoring of human review rubrics is strictly prohibited.
   - Malformed, unparseable, or empty model outputs remain visible to the reviewer as explicit `No-Usable-Response` outcomes.

---

## 9. Addendum: Pre-Execution Protocol Clarifications (Dated November 2026)

This addendum records methodological boundaries approved prior to benchmark execution:

1. **Configured-System Comparison Boundary (Condition A vs. Condition B)**:
   - Condition A and Condition B compare **configured base and adapted systems** operating under identical prompt instructions and full canonical JSON schema text.
   - Because each system employs its model-appropriate formatting interface (official chat template for the base model; training-aligned suffix `<|turn>model\n` for the fine-tuned adapter), **this is NOT an isolated weight-only adaptation effect**. Any performance difference reflects the adapted weights operating through their verified training-aligned interface versus base weights operating through their upstream instruction interface.
2. **Experimental Boundary for Condition D**:
   - Condition D represents the **experimental service prompt configuration** (`system_prompt_v2_enum_guided` without raw schema block).
   - It is an exploratory evaluation condition designed to test deployment-style inference; it does **NOT** represent a production-validated deployment or an isolated weight ablation.
3. **Runtime & Compute Constraints**:
   - The projected runtime (~4.5 to 5.5 hours) is an empirical estimate extrapolated from 18-case development latencies.
   - Actual execution duration may vary depending on GPU host scheduling, thermal throttling, and output token distributions.
   - Session timeouts (12-hour Kaggle interactive limit) and available weekly GPU quota (30 hours/week) must be verified prior to launching execution.

---

## 10. Checkpoint Recovery & Interruption Protocol

1. **How to Download Partial Checkpoints**:
   - In Kaggle, if an execution is interrupted, run a scratch cell:
     ```python
     from IPython.display import FileLink
     FileLink('/kaggle/working/oopsie-benchmark-results-v1-2-0/checkpoint_results.jsonl')
     ```
   - Alternatively, download `checkpoint_results.jsonl` from the right-hand **Data -> Output** panel.
2. **How to Reattach in a New Session**:
   - Upload `checkpoint_results.jsonl` to Kaggle as a private dataset or copy it into `/kaggle/working/oopsie-benchmark-results-v1-2-0/`.
   - The evaluation notebook's Step 8 validates `run_manifest.json` against the active configuration:
     - Model ID: `google/gemma-4-12b-it`
     - Adapter: `oopsie-pilot-adapter` (Step 44)
     - Precision: 4-bit NF4, `torch.bfloat16`
     - Decoding: greedy (`temp=0.0`, `max_new_tokens=1024`)
     - Hashes: benchmark dataset (`1676a9...`), canonical schema (`40550b...`), prompt v2 (`37a921...`)
3. **Corruption & Conflicting Record Handling**:
   - The checkpoint parser (`load_checkpoint_records`) reads lines sequentially.
   - A trailing corrupt or truncated line caused by mid-write interruption is isolated into `incomplete_attempts.json` and logged; it is **NOT** scored as a model failure.
   - If duplicate records for `(case_id, condition_key)` exist:
     - Identical records are deduplicated with an audit warning.
     - Conflicting records raise an immediate `ValueError` and halt execution to prevent silent score corruption.
   - Both completed successes and completed failures are permanently preserved. Completed cases are never re-run to seek improved scores.
