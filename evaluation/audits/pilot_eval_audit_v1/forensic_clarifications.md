# Forensic Clarifications & Claim Bounds

**Subject**: Refinement of preliminary forensic conclusions regarding pilot evaluation generation symptoms.  
**Audit Reference**: `evaluation/audits/pilot_eval_audit_v1/`  
**Date**: October 24, 2026

---

## 1. Verified Observations vs. Working Hypotheses

To maintain absolute scientific rigor, the boundary between directly recorded facts and explanatory hypotheses is explicitly demarcated:

| Topic | Direct Observation (Established Fact) | Working Hypothesis (Unverified Pending Testing) |
| :--- | :--- | :--- |
| **Prefix Mismatch** | **Established**: Calling `apply_chat_template(..., add_generation_prompt=True)` injects `<|turn>model\n<|channel>thought\n<channel|>`. In contrast, training preprocessing prepends `<|turn>model\n` immediately before `{`. | **Hypothesis**: The presence of `<channel|>` at the prompt boundary triggers the model to predict `<|turn>\n` instead of `{`. This remains a hypothesis until confirmed by controlled A/B testing. |
| **Delimiter Loops** | **Established**: In the 1024-token rerun, records `syn-ath-055` and `syn-cfg-017` emitted repeated `<|turn>\n` strings (confirmed by `raw_with_specials`). | **Hypothesis**: The exact next-token probability distribution, logit bias, or tie-breaking mechanism that favored `<|turn>` over `{` on these specific inputs is unverified. |
| **Run 1 Empty Outputs** | **Established**: In the original 512-token pilot run, `syn-amb-020`, `syn-ath-055`, and `syn-cfg-017` had `is_truncated = True` and decoded to `raw_text = ""` under `skip_special_tokens=True`. | **Hypothesis**: That all 512 tokens were specifically `<|turn>\n` control tokens is a strong inference based on later runs, but remains **unverified** because raw generated token IDs (`gen_token_ids`) were not preserved during Run 1. |
| **syn-amb-020 Inconsistency** | **Established**: Record `syn-amb-020` generated 0 characters and hit 512 tokens in Run 1, but generated 324 tokens of valid JSON in Run 2. | **Hypothesis**: That differences in internal `SFTTrainer` state immediately after training vs. fresh `PeftModel` loading altered the initial token prediction is a plausible hypothesis, but cannot be proven without identical state reproduction. |

---

## 2. Epistemological Principle

Raw generated token IDs cannot be inferred with certainty from empty decoded text alone. 

Future evaluation runs must explicitly serialize:
1. Exact integer token IDs (`gen_token_ids`).
2. Raw strings with special tokens preserved (`raw_with_specials`).
3. Raw strings with special tokens skipped (`raw_text`).
4. Exact prompt token count and prompt SHA-256 hash.
