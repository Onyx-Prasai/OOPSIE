# Forensic Investigation: The syn-amb-020 324-Token Inconsistency

**Record ID**: `syn-amb-020`  
**Scenario**: ESLint warnings for unused variable and missing accessibility `alt` prop causing CI build failure due to `max-warnings: 0`.

---

## 1. Observed Inconsistency Across Runs

In the two successive Kaggle runs, record `syn-amb-020` exhibited starkly different outcomes despite using the identical adapter checkpoint (`checkpoint-44`):

| Evaluation Run | Configured Token Limit | Actual Generated Tokens | Raw Decoded Characters | Raw Text Snippet | JSON Parse Result | Strict Schema Result |
| :--- | :---: | :---: | :---: | :--- | :---: | :---: |
| **Pilot v1 (Post-Train)** | 512 | 512 (Budget Hit) | **0 chars** (`""`) | `""` | FAILED | FAILED |
| **Eval 1024 (Recheck)** | 1024 | **324 tokens** | **1,507 chars** | `{"summary":"Build failed with ESLint warnings..."}` | **SUCCESS** | **SUCCESS** |

---

## 2. Forensic Analysis: Prompt & Session Audit

### A. Prompt & Input Verification
* **System Prompt**: Identical (`You are OOPSIE... conforming to data/schema.json...`).
* **User Input**: Identical (ESLint log containing `'unusedVar' is defined but never used` in `Header.js` and `img element lacks alt` in `Footer.js`).
* **Prompt Token Count**: Exactly **354 prompt tokens** across both runs.
* **Input SHA-256**: Identical.

### B. Decoding & Hardware Settings
* **Decoding Strategy**: Greedy decoding (`do_sample=False`, `temperature=0.0`) in both runs.
* **Global Seed**: `42` configured in both notebooks.
* **Model Checkpoint**: Base model `google/gemma-4-12b-it` in 4-bit NF4 with LoRA weights loaded from `/kaggle/working/oopsie-pilot-adapter`.

---

## 3. Why the 512-Token Ceiling Was NOT the Sole Cause

The successful response generated in the second run consumed **only 324 tokens** (1,507 characters). Because 324 tokens is well below 512 tokens ($324 < 512$), the original failure cannot be explained simply by claiming that OOPSIE's answer "could not fit inside 512 tokens."

If the model had generated the exact same 324-token JSON response in the first run, it would have completed with 188 tokens to spare.

---

## 4. Root Cause Analysis: The Delimiter Loop Symptom

### What is Established:
1. **Empty Raw Text with Truncation**:
   * In the first run, `is_truncated = (len(gen_tokens) >= 512)` evaluated to `True`, meaning exactly 512 tokens were generated.
   * However, `raw_text = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()` produced an **empty string** (`""`).
2. **The Special-Token Masking Effect**:
   * When `skip_special_tokens=True` produces `""` across 512 generated tokens, it establishes that **all 512 tokens were special control tokens**.
3. **Observed Delimiter Loops in Matched Cases**:
   * In the 1024-token rerun, logging `raw_with_specials` on the remaining two failure cases (`syn-ath-055` and `syn-cfg-017`) explicitly captured:
     ```text
     '<|turn>\n<|turn>\n<|turn>\n<|turn>\n<|turn>...'
     ```
   * Gemma 4 token ID `105` (`<|turn>`) was emitted continuously in an autoregressive loop.
   * `syn-amb-020` in the first run exhibited the exact same signature (512 special tokens stripped to `""`).

### What is Established vs. What Remains Unknown:

| Aspect | Status | Evidence / Explanation |
| :--- | :---: | :--- |
| **Did syn-amb-020 fit in 512 tokens?** | **Established** | Yes. The full compliant JSON response requires only 324 tokens. |
| **Was the first failure a text truncation?** | **Established (Disproven)** | Disproven. The first run did not write partial JSON text; it generated 512 special tokens that stripped to an empty string. |
| **Was the first failure a delimiter loop?** | **Highly Supported** | Supported by the identical empty-string symptom and 512-token budget hit shared with `syn-ath-055` and `syn-cfg-017`. |
| **Why did syn-amb-020 loop in Run 1 but pass in Run 2?** | **Unknown / Unverified** | In Run 1, the model was evaluated directly from the active `SFTTrainer` object in GPU memory immediately after training. In Run 2, the model and adapter were freshly loaded from disk via `PeftModel.from_pretrained`. Whether transient training KV cache, PyTorch allocator state, or generation loop initial token sampling caused the tie-break difference on token 1 cannot be determined without the raw token ID array from Run 1. |

---

## 5. Summary Conclusion

1. Reaching 512 tokens was the **termination trigger**, not the generative cause.
2. The failure was a **control-token loop** on opening turn formatting, which resolved when evaluated in a clean standalone inference session.
3. Increasing token budgets alone does not resolve control-token loops (as shown by `syn-cfg-017`, which simply looped for 1024 tokens instead of 512). Chat template alignment (audited in `formatting_and_delimiter_audit.md`) is required.
