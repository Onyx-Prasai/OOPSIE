# Controlled Formatting Experiment & Missing Test Baseline: Official Report

**Experiment Date**: October 25, 2026  
**Artifact Directory**: `artifacts/formatting_experiment/`  
**Base Model**: `google/gemma-4-12b-it` (Revision: `main`, 4-bit NF4)  
**Adapter**: `oopsie-pilot-adapter` (`checkpoint-44`, LoRA $r=16, \alpha=32$)  
**Decoding Settings**: Greedy (`temperature=0.0`, `do_sample=False`, `max_new_tokens=1024`, `seed=42`)

---

## 1. Complete Baseline vs. Adapter Scorecard

This run provides the **missing unadapted base model evaluation on the 17 frozen test inputs** and executes the **4-condition validation A/B experiment**:

| Split & Condition | Evaluated Model | Prompt Formatter | JSON Parse Rate | Strict Schema Conformance | Delimiter Loops | Output Budget Hits | Mean Gen Tokens |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Test Baseline (Missing)** | Unadapted Base | Original Eval | 16 / 17 (94.1%) | **0 / 17 (0.0%)** | 0 / 17 (0.0%) | 0 / 17 (0.0%) | 472.1 |
| **Test Adapted (Existing)** | Pilot Adapter | Original Eval | 14 / 17 (82.4%) | **14 / 17 (82.4%)** | 1 / 17 (5.9%) | 3 / 17 (17.6%) | 467.5 |
| **Val Condition A** | Unadapted Base | Original Eval | 16 / 18 (88.9%) | **0 / 18 (0.0%)** | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 451.5 |
| **Val Condition B** | Unadapted Base | Candidate Aligned | 0 / 18 (0.0%)* | **0 / 18 (0.0%)** | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 452.7 |
| **Val Condition C** | Pilot Adapter | Original Eval | 16 / 18 (88.9%) | **16 / 18 (88.9%)** | 4 / 18 (22.2%) | 1 / 18 (5.6%) | 412.4 |
| **Val Condition D** | **Pilot Adapter** | **Candidate Aligned** | **18 / 18 (100.0%)** | **18 / 18 (100.0%)** | **0 / 18 (0.0%)** | **0 / 18 (0.0%)** | **360.8** |

*\*Note on Condition B: The unadapted base model emits plain text `thought\n` when `<|channel>thought\n<channel|>` is omitted, causing raw JSON parsing to fail.*

---

## 2. Key Scientific Findings

### A. The Suffix Delimiter Hypothesis is Confirmed
1. **Condition C (Replicating Original Evaluation)**:
   * Re-evaluating with `format_original_eval` reproduced the exact delimiter loop symptoms on `syn-ath-055` and `syn-cfg-017` with **100% repeatability**.
2. **Condition D (Candidate Training-Aligned Formatting)**:
   * When prompted with the exact training prefix (`...<turn|>\n<|turn>model\n`), **all delimiter loops dropped to 0/18 (0.0%)**.
   * All three previously failing cases generated concise, highly accurate, and 100% schema-valid JSON:
     * **`syn-amb-020`**: 326 tokens (`schema_valid: True`).
     * **`syn-ath-055`**: 461 tokens (`schema_valid: True`). Diagnosis: `"CORS blocked the request because 'Access-Control-Allow-Origin' is set to '*' while 'credentials: include' is active."`
     * **`syn-cfg-017`**: 297 tokens (`schema_valid: True`). Diagnosis: `"Firebase Auth was called before Firebase was initialized with your project configuration."`
   * **Overall Validation Conformance reached 18 / 18 (100.0%)**.

### B. Unadapted Base Model Baseline on Independent Test Set
* Across all 17 independent test cases, the unadapted base Gemma 4 model achieved:
  * **0 / 17 (0.0%) Schema Conformance**
  * Although it generated markdown-wrapped JSON 94.1% of the time, it consistently used non-conforming, invented keys (`error_details`, `status`, `remediation_steps`, `user_advice`).
* In contrast, the fine-tuned OOPSIE adapter achieved **14 / 17 (82.4%)** strict schema conformance under identical original evaluation conditions.

---

## 3. Policy & Production Recommendations

1. **Frozen Benchmark Policy**:
   * The 17 test cases remain a **frozen pilot benchmark**. Because their failure modes and outputs have now been inspected in detail, they must not be used as training data or claimed as unseen in subsequent major evaluation rounds.
2. **Inference Pipeline Recommendation**:
   * When integrating the OOPSIE adapter into an inference service or extension, the **training-aligned prompt format** (`format_training_aligned`) should be adopted as the default formatter, eliminating the out-of-distribution `<|channel>thought\n<channel|>` suffix and preventing turn delimiter loops.
