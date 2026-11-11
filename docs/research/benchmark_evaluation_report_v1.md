# OOPSIE Final Benchmark Evaluation Report (v1.2.0-frozen)

**Protocol**: `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`  
**Execution Environment**: Kaggle GPU (Tesla T4, 14.56 GB VRAM, Python 3.10)  
**Evaluation Corpus**: `evaluation/benchmark.jsonl` (N=40 held-out records, SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)  
**Base Model**: `google/gemma-4-12b-it` (4-bit NF4 precision, `torch.bfloat16`)  
**Adapter Checkpoint**: `oopsie-pilot-adapter` (Step 44, Epoch 2)  
**Demonstration (Condition C)**: `syn-dep-001` (`vite-missing-lucide-icons` from `data/train.jsonl`)  
**Canonical Output Schema**: `data/schema.json` (SHA-256: `40550bfef007a7078dc3515a0c03e52dec29e351b931e9bb6cd5ea8f447b547a`)  
**Artifact Archive**: `artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz` (SHA-256: `cf24eec1a5c3347ae826fec4b5cbfb7133a1c4ce92aace3eab2b048bdd37f4eb`)  
**Evidence Verification Status**: **Verified against local disk artifacts (`artifacts/benchmark_v1_2_0/benchmark_results/`)**  
**Audit & Correction Date**: 2026-11-05

---

## 1. Executive Summary & Core Results

> [!NOTE] Dated Reporting Correction (2026-11-05)
> An independent audit of the case-level records in `benchmark_results_full.json` resolved an earlier reporting ambiguity regarding Condition D's category agreement metrics. In Condition D:
> - Raw JSON parsing succeeded for **40 / 40 cases (100.0%)**.
> - Exactly 1 case (`bench-npm-03`) failed strict schema conformance due to the omission of the required property `"matched_recipes": []`.
> - In `bench-npm-03`, the model predicted `"dependency"`, matching the reference category `"dependency"`.
> - Consequently:
>   - **Category Agreement (All 40 attempted)**: **28 / 40 (70.0%)**
>   - **Category Agreement (Parseable outputs, N=40)**: **28 / 40 (70.0%)**
>   - **Category Agreement (Schema-valid outputs, N=39)**: **27 / 39 (69.2%)**
> 
> Earlier draft summaries conflated the parseable denominator ($N=40$) with the schema-valid denominator ($N=39$) for Condition D. All three metrics are now reported with distinct names and explicit denominators.

The final benchmark evaluation compared the unadapted base model (`google/gemma-4-12b-it`) against the fine-tuned LoRA pilot adapter across 40 unseen, held-out developer error scenarios across four experimental conditions (160 unique generation passes). All generations used frozen greedy decoding (`temperature=0.0`, `do_sample=False`, `max_new_tokens=1024`). Zero automated JSON repairs, zero markdown stripping, and zero retries were applied.

| Metric | Condition A: Base Zero-Shot + Schema | Condition B: Adapter Zero-Shot + Schema | Condition C: Base 1-Shot + Schema | Condition D: Adapter Service Prompt |
| :--- | :---: | :---: | :---: | :---: |
| **Model State** | Base (`with model.disable_adapter():`) | Adapted (`oopsie-pilot-adapter`) | Base (`with model.disable_adapter():`) | Adapted (`oopsie-pilot-adapter`) |
| **Prompt Interface** | Full Schema JSON (~710 tok) | Full Schema JSON (~710 tok) | Full Schema + 1-Shot Demo | Current Service Prompt (~384 tok, No Schema) |
| **Formatter** | Official Chat Template | `training_aligned_v1` (`<\|turn\>model\n`) | Official Chat Template | `training_aligned_v1` (`<\|turn\>model\n`) |
| **Attempted Cases** | 40 / 40 | 40 / 40 | 40 / 40 | 40 / 40 |
| **Completed Forward Passes** | 40 / 40 (100%) | 40 / 40 (100%) | 40 / 40 (100%) | 40 / 40 (100%) |
| **Generation Exceptions / Crashes** | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) |
| **Raw RFC 8259 JSON Valid** | **0 / 40 (0.0%)** | **38 / 40 (95.0%)** | **0 / 40 (0.0%)** | **40 / 40 (100.0%)** |
| **Strict Schema Conformance** | **0 / 40 (0.0%)** | **38 / 40 (95.0%)** | **0 / 40 (0.0%)** | **39 / 40 (97.5%)** |
| **Schema Valid 95% Wilson CI** | [0.0%, 8.8%] | [83.5%, 98.6%] | [0.0%, 8.8%] | [87.1%, 99.6%] |
| **Output-Budget Hits (1024 tok)** | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) |
| **Delimiter-Loop Flags** | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 0 / 40 (0.0%) |
| **Category Agreement (All 40 Cases)** | 0 / 40 (0.0%) | 28 / 40 (70.0%) | 0 / 40 (0.0%) | 28 / 40 (70.0%) |
| **Category Agreement (Parseable Outputs)** | N/A (0 parseable) | 28 / 38 (73.7%) | N/A (0 parseable) | 28 / 40 (70.0%) |
| **Category Agreement (Schema-Valid Outputs)** | N/A (0 schema valid) | 28 / 38 (73.7%) | N/A (0 schema valid) | 27 / 39 (69.2%) |
| **Heuristic Safety Pass (Regex)** | 40 / 40 (100.0%) | 40 / 40 (100.0%) | 40 / 40 (100.0%) | 40 / 40 (100.0%) |
| **Mean Latency per Case** | 118.62 s | 114.42 s | 119.35 s | 99.88 s |
| **Cumulative Request Duration** | 79.1 min | 76.3 min | 79.6 min | 66.6 min |

*Timing Terminology Note*: "Cumulative Request Duration" represents the sum of sequential generation call durations across the 40 cases in that condition (total across all 160 passes = 301.52 minutes / 5.03 hours). It measures inference API latency and should not be conflated with dedicated hardware compute time or notebook session wall-clock time.

---

## 2. Paired 2x2 Contingency Transitions

Because the same 40 cases were evaluated under all conditions, outcomes are analyzed as paired contingency transitions rather than independent samples:

### Primary Comparison: Base Zero-Shot (A) vs. Adapter Zero-Shot (B)
*Matched Instructions and Schema Text — Differing Formatter Boundary*
- **Both Pass ($A+ B+$)**: 0 / 40 (0.0%)
- **Adapter-Only Pass ($A- B+$)**: **38 / 40 (95.0%)**
- **Base-Only Pass ($A+ B-$)**: 0 / 40 (0.0%)
- **Neither Pass ($A- B-$)**: 2 / 40 (5.0%)
- **Statistical Significance**:
  - **Exact Paired McNemar Test**: On $n=38$ discordant pairs ($b=38, c=0$), the exact two-sided binomial test under $H_0: p=0.5$ yields:
    $$p = 2 \times (0.5)^{38} \approx 7.28 \times 10^{-12}$$
  - **Asymptotic $\chi^2$ Approximation (Edwards Continuity Correction)**:
    $$\chi^2_{\text{corrected}} = \frac{(|38 - 0| - 1)^2}{38} = \frac{37^2}{38} = \frac{1369}{38} \approx 36.03 \quad (df=1, p \approx 1.95 \times 10^{-9})$$
    *(Without continuity correction: $\chi^2 = 38^2 / 38 = 38.00, p \approx 7.07 \times 10^{-10}$).*
- **Interpretation & Confound**: Fine-tuning produced an empirical +95.0 percentage point gain in strict schema conformance under greedy decoding. However, because Condition A and Condition B employ different input formatting boundaries (`official chat template` vs. `training_aligned_v1`), this comparison evaluates configured systems under identical prompt instructions, rather than isolating adapter weights alone.

### Secondary Comparison: Adapter Matched (B) vs. Adapter Service Prompt (D)
*Assessing the Impact of In-Context Schema Overhead on Adapted Performance*
- **Both Pass ($B+ D+$)**: 37 / 40 (92.5%)
- **D-Only Pass ($B- D+$)**: 2 / 40 (5.0%) (`bench-firebase-01`, `bench-nextjs-01`)
- **B-Only Pass ($B+ D-$)**: 1 / 40 (2.5%) (`bench-npm-03`)
- **Neither Pass ($B- D-$)**: 0 / 40 (0.0%)
- **Observation**: Omitting the in-context JSON schema definition reduced mean per-case latency by 14.54s (-12.7%) and achieved 100% raw JSON syntax parsing (40/40), but resulted in one schema omission (`bench-npm-03` omitted `"matched_recipes": []`).

### Secondary Comparison: Base Zero-Shot (A) vs. Base 1-Shot (C)
*In-Context Learning Demonstration Baseline*
- **Both Pass ($A+ C+$)**: 0 / 40 (0.0%)
- **Neither Pass ($A- C-$)**: 40 / 40 (100.0%)
- **Observation**: Providing a concrete 1-shot exemplar did not induce strict raw JSON formatting in the base model under zero-tolerance parsing. All base completions contained conversational preambles and markdown fences.

---

## 3. Disaggregated Category Agreement Breakdown

Category agreement was assessed against the operational reference category across the 9 error categories:

| Benchmark Category | Cases (N) | Cond B (All N=40) | Cond B (Parseable) | Cond B (Schema-Valid) | Cond D (All N=40) | Cond D (Parseable) | Cond D (Schema-Valid) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **authentication** | 8 | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) |
| **authorization** | 3 | 0 / 3 (0.0%) | 0 / 3 (0.0%) | 0 / 3 (0.0%) | 1 / 3 (33.3%) | 1 / 3 (33.3%) | 1 / 3 (33.3%) |
| **build** | 4 | 1 / 4 (25.0%) | 1 / 3 (33.3%) | 1 / 3 (33.3%) | 1 / 4 (25.0%) | 1 / 4 (25.0%) | 1 / 4 (25.0%) |
| **dependency** | 4 | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 2 / 3 (66.7%) |
| **deployment** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) |
| **environment_variables** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) |
| **network** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) |
| **runtime** | 5 | 3 / 5 (60.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 5 (60.0%) | 3 / 5 (60.0%) | 3 / 5 (60.0%) |
| **unknown** | 4 | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) |
| **Total** | **40** | **28 / 40 (70.0%)** | **28 / 38 (73.7%)** | **28 / 38 (73.7%)** | **28 / 40 (70.0%)** | **28 / 40 (70.0%)** | **27 / 39 (69.2%)** |

*Epistemic Note*: Reference labels represent operational ground-truth approximations, not infallible physical absolutes. In Condition D, `bench-npm-03` was parseable and matched the reference category `dependency`, but was excluded from the schema-valid denominator ($N=39$) due to an omitted empty array field (`matched_recipes`). Category disagreements primarily reflected semantic borderlines (e.g., classifying an unhandled runtime exception during a Next.js static build as `runtime` rather than `build`).

---

## 4. Forensic Audit of Non-Conforming Cases

### Non-Conforming Adapted Cases (Conditions B and D)
Across the 80 adapted model evaluations (40 in Condition B + 40 in Condition D), exactly 3 cases failed strict schema compliance:

| Case ID | Condition | Parser Status | Observed Error | Confirmed Defect | Character Context & Observation |
| :--- | :---: | :---: | :--- | :--- | :--- |
| `bench-firebase-01` | Cond B | JSON Parse Fail | `Invalid \escape at line 1 col 1490` | Illegal escape sequence `\'` | Model generated `\'` inside a string literal. RFC 8259 forbids backslash-escaping single quotes. |
| `bench-nextjs-01` | Cond B | JSON Parse Fail | `Invalid \escape at line 1 col 1155` | Illegal escape sequence `\'` | Model generated `\'` inside documentation snippet string. |
| `bench-npm-03` | Cond D | Schema Fail (JSON Valid) | `$.matched_recipes: required property is missing` | Schema property omission | Generated syntactically valid JSON matching category `dependency`, but the required key `"matched_recipes"` was absent. |

*Descriptive Note*: In `bench-npm-03`, we record the factual observation that `"matched_recipes"` was omitted; we refrain from asserting a causal claim that the absence of schema text in Condition D's prompt caused this omission. No adapted cases exhibited delimiter loops, token budget terminations, or unhandled generation exceptions.

### Base Model Failures (Conditions A and C)
All 80 base model generation passes (40 in Condition A + 40 in Condition C) failed raw JSON parsing (0/40) under zero-tolerance evaluation:
- **Markdown-wrapped JSON**: 80 / 80 (100.0%) contained Markdown backtick code fences (e.g., ` ```json ... ``` `).
- **Conversational Prose**: 74 / 80 (92.5%) included conversational preambles (e.g., *"Here is the structured recovery plan:"*) or postambles.
- Under strict zero-tolerance parsing (no regex extraction, no fence stripping), these outputs are unparseable by downstream automated callers. This represents an interface/formatting failure, not necessarily a total absence of diagnostic insight.

---

## 5. Blinded Human Technical Review Status

- **Review Protocol**: Double-blinded review using 8 partitioned batches of 5 cases each ([`docs/research/human_review/`](file:///c:/Users/onyxe/Desktop/OOPSIE/docs/research/human_review/)).
- **Reviewer Guidelines**: Established in [`docs/research/human_review/README.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/docs/research/human_review/README.md).
- **Blinding & Randomization**: Systems are anonymized as `System Alpha`, `System Beta`, `System Gamma`, `System Delta` with randomized permutations per case (`seed=42`).
- **Unblinding Key Isolation**: The key mapping Greek labels to condition keys remains isolated in [`artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json) (5,918 bytes).
- **Review Status**: **PENDING**. Manual ratings on the 6-dimension rubric (Assessability, Correctness, Unsupported Claims, Uncertainty, Repair Scope, Verification Usefulness) have not yet been completed.
- **Reviewer Disclosure**: All qualitative evaluations will be conducted solely by the author (Onyx Prasai) unless an independent external annotator participates.

---

## 6. Execution Manifest & Cryptographic Integrity

All artifact files were cryptographically audited against the execution manifest:

| Exported File | File Size | SHA-256 Checksum |
| :--- | :---: | :--- |
| `benchmark_results_full.json` | 635,014 bytes | `6021aaab2616aec8cd09679532686eb09d424adfb15c2d2e22469f6c75aca397` |
| `summary_metrics.json` | 1,885 bytes | `0a759c693717240293fd2458071e779b8244155180ffa496b59a8f172c377644` |
| `blinded_human_review_sheet.md` | 418,686 bytes | `eaf69fea4ef0f8fc1e62b0839d0a1b24561562e49c21d1568839300eaf152aea` |
| `unblinded_review_key.json` | 5,918 bytes | `738f440aa43ce3f11ebdc5dbbfebb59cdcc2792d27a9f2812d3234175627835d` |
| `checkpoint_results.jsonl` | 628,592 bytes | `e6be2fca2763544fba0537f21339ee69e7341c095ebbf964364aecf9fa7aa0f4` |
| `oopsie_benchmark_results_v1_2_0.tar.gz` | 234,322 bytes | `cf24eec1a5c3347ae826fec4b5cbfb7133a1c4ce92aace3eab2b048bdd37f4eb` |
