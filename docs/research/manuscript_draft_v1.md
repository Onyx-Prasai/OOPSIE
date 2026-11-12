# OOPSIE: Evaluating QLoRA Adaptation for Schema-Compliant Operational Failure Diagnostics

**Author**: Onyx Prasai  
**Contact**: `onyxefforts@gmail.com`  
**Institutional Affiliation**: Independent Researcher *(no institutional affiliation asserted)*  
**Manuscript Version**: Draft v1.4.0 (Pre-Submission Revision)  
**Date**: November 2026  

---

## Abstract

Deploying instruction-tuned language models as programmatic middleware in automated software diagnostics is frequently hindered by structural output instability under zero-tolerance parsing. We present OOPSIE (Operational Output Parser & Structured Inference Engine), an open evaluation framework examining whether Quantized Low-Rank Adaptation (QLoRA) improves structured JSON schema compliance for operational diagnostic reporting, and whether such adaptation alters qualitative diagnostic performance. We trained a QLoRA adapter ($r=16, \alpha=32$) on top of the public model `google/gemma-4-12B-it` (recorded as `google/gemma-4-12b-it` in historical training artifacts) using a multi-turn developer error-recovery corpus and 4-bit NormalFloat quantization.

In a pre-specified frozen benchmark of 40 held-out failure scenarios (160 total greedy-decoding passes), QLoRA adaptation improved strict JSON schema compliance from 0.0% in unadapted base-model conditions to 95.0% (38/40) with schema guidance and 97.5% (39/40) without schema guidance. The comparison between unadapted zero-shot base-model inference and adapted inference with schema guidance was statistically significant under an exact two-sided McNemar test (38 discordant pairs; $b=0, c=38$; $p \approx 7.28 \times 10^{-12}$; Edwards continuity-corrected $\chi^2 = 36.03$, $p \approx 1.95 \times 10^{-9}$). This result concerns programmatic schema compliance, not diagnostic correctness.

An author-adopted qualitative evaluation, based on AI-generated provisional ratings across all 160 completions, did not demonstrate a diagnostic-reasoning or technical-correctness advantage for adapted conditions over unadapted base-model conditions. Within this benchmark, QLoRA adaptation functioned primarily as a structural output-format intervention rather than an amplifier of diagnostic reasoning. The benchmark, protocol, datasets, evaluation bundle, and result archive are publicly available; deployed systems require schema validation and human oversight.

**Keywords**: Large Language Models, Structured Output Generation, JSON Schema, QLoRA, Operational Error Recovery, Diagnostic Reasoning, Developer Tools, Empirical Software Engineering.

---

## 1. Introduction

When automated builds, CI/CD pipelines, container runtimes, or deployment orchestrators encounter unhandled exceptions, human developers and automated healing agents require three immediate diagnostic deliverables:
1. **Accurate Failure Domain Identification**: Rapid classification of the failure category (e.g., authentication, environment variable misconfiguration, peer dependency conflict).
2. **Safe, Well-Scoped Remediation**: A minimal, non-destructive remediation procedure that avoids overbroad commands.
3. **Sound Verification Procedures**: Concrete, executable verification steps to confirm whether the fix resolved the underlying fault without introducing collateral regressions.

Modern instruction-tuned foundation language models possess extensive parametric knowledge regarding software engineering and debugging, as demonstrated on code generation benchmarks such as HumanEval (Chen et al., 2021) and repository-level issue resolution benchmarks such as SWE-bench (Jimenez et al., 2024). However, deploying general-purpose chat models as programmatic middleware in automated toolchains presents severe operational challenges. Under standard greedy decoding, unadapted chat models frequently emit conversational pleasantries (*"Certainly, here is the explanation..."*), enclose JSON payloads in Markdown code fences (` ```json ... ``` `), or introduce syntactic defects (such as illegal escape sequences). When downstream tooling enforces zero-tolerance RFC 8259 JSON validation (Bray, 2017) and rigid schema conformance (JSON Schema Draft 2020-12; Wright et al., 2022a, 2022b), these formatting deviations cause immediate automated ingestion failure.

To address this challenge, two primary architectural paradigms exist:
- **Constrained Decoding**: Enforcing strict grammar transitions at every token generation step via finite-state machines, regular expressions, or context-free grammars (Willard & Louf, 2023; Ugare et al., 2025). Constrained sampling mathematically guarantees output validity according to a defined grammar; however, it requires specialized runtime engine integrations (e.g., vocabulary-masking hooks and custom parser states) that are not natively supported across all deployment environments or cloud inference endpoints.
- **Domain Adaptation (Fine-Tuning)**: Embedding structural output format constraints directly into model parameters via Low-Rank Adaptation (LoRA; Hu et al., 2022) and Quantized Low-Rank Adaptation (QLoRA; Dettmers et al., 2023). This approach operates on standard autoregressive inference engines without specialized grammar-masking dependencies, but yields empirical probabilistic compliance rather than mathematical guarantees.

### Research Questions
This paper investigates the feasibility, reliability, and limitations of domain adaptation for structured operational error recovery, addressing the central question: *Does QLoRA adaptation improve structured JSON/schema compliance for operational-failure diagnostic reporting, and does it improve qualitative diagnostic reasoning?* Specifically, we investigate three research questions:
- **RQ1 (Structural Compliance)**: To what extent does parameter-efficient adaptation induce strict, zero-tolerance JSON schema conformance compared to zero-shot and few-shot in-context prompting of the identical base model?
- **RQ2 (Schema Overhead & Latency)**: Can an adapted model reliably generate schema-compliant structures when the explicit JSON schema definition (~710 tokens) is omitted from the runtime system prompt, and what latency benefits accrue?
- **RQ3 (Diagnostic Fidelity & Qualitative Reasoning)**: Does structural adaptation preserve or improve qualitative diagnostic correctness, hallucination avoidance, and repair scoping, or does it merely alter surface formatting?

---

## 2. Related Work

### 2.1 Structured and Constrained Generation from Language Models
Generating structured data (JSON, SQL, ASTs) from autoregressive transformers has progressed along two major approaches:
1. *Prompt-Guided In-Context Structuring*: Early workflows relied on detailed prompt instructions, schema definitions, and few-shot demonstrations to steer foundation models toward valid formats. However, empirical studies in developer-facing tasks demonstrate that unconstrained models exhibit non-trivial syntax error rates, extraneous conversational preambles, and delimiter confounds under strict parsers (Leinonen et al., 2023). While downstream systems often apply heuristic regex wrappers or markdown-stripping passes, such post-hoc repairs are fragile and unstandardized.
2. *Grammar-Constrained Decoding*: Frameworks such as Outlines (Willard & Louf, 2023) and SynCode (Ugare et al., 2025) utilize regular expressions, context-free grammars (CFGs), and deterministic finite automaton (DFA) mask stores to dynamically restrict vocabulary token logits during decoding. This approach provides formal guarantees of syntactic validity (e.g., adherence to RFC 8259 JSON syntax; Bray, 2017). While optimized implementations mitigate token-evaluation latency, grammar-constrained decoding requires specialized runtime engines with low-level logit-masking hooks, which complicates deployment across heterogeneous edge devices or standard serving stacks.

*Comparison with OOPSIE*: Rather than enforcing token masking at decoding time, OOPSIE evaluates the behavioral extent to which parameter-efficient fine-tuning can generate complex, multi-property JSON schemas conforming to JSON Schema Draft 2020-12 (Wright et al., 2022a, 2022b) directly from standard greedy decoding. While parameter adaptation provides empirical probabilistic reliability rather than formal mathematical guarantees, it eliminates runtime engine dependencies and enables omitting schema text from prompts.

### 2.2 Parameter-Efficient Fine-Tuning for Domain Structuring
Low-Rank Adaptation (LoRA; Hu et al., 2022) freezes pre-trained foundation model weights and injects trainable rank-decomposition matrices into transformer attention and feed-forward projections ($W = W_0 + \frac{\alpha}{r}BA$). Quantized Low-Rank Adaptation (QLoRA; Dettmers et al., 2023) extends this approach by quantizing the base model to 4-bit NormalFloat (NF4) with double quantization and compute-type casting, enabling efficient fine-tuning of 12B+ parameter models on single commodity GPUs (e.g., 16 GB Tesla T4). While parameter adaptation has been extensively evaluated across instruction-following, mathematical reasoning, and general programming tasks (e.g., Code Llama; Rozière et al., 2023; StarCoder; Li et al., 2023), its empirical capability to induce rigid 10-key hierarchical schemas under zero-tolerance parsing without grammar masking remains sparsely benchmarked.

### 2.3 Automated Program Repair vs. Advisory Diagnostics
Automated Program Repair (APR) systems historically employ search-based algorithms, symbolic execution, or neural patch generation to modify source code, re-compile binaries, and validate candidate patches against automated test suites (Zhang et al., 2024). 

*Critical Scope Boundary*: **OOPSIE is explicitly not an automated program repair (APR) system**. OOPSIE does not generate code diffs, execute compiler commands, mutate repositories, or run test suites. Instead, OOPSIE functions strictly as an **advisory diagnostic engine**. It translates raw runtime exceptions and build failures into structured, human-reviewable diagnostic reports comprising causal hypotheses, clarifying questions, risk warnings, copy-ready prompts for developer inspection, and suggested verification steps for developer review.

---

## 3. Method

### 3.1 Canonical Diagnostic Schema Specification
All diagnostic outputs in OOPSIE adhere to a canonical 10-key schema ([`data/schema.json`](data/schema.json)) formalized under the JSON Schema Draft 2020-12 dialect, utilizing structural applicator keywords (`$schema`, `$id`, `properties`, `additionalProperties`, `items`) specified in the JSON Schema Core specification (Wright et al., 2022a) and structural assertion keywords (`type`, `enum`, `required`, `minLength`) specified in the JSON Schema Validation specification (Wright et al., 2022b):

```json
{
  "summary": "string (10-200 chars)",
  "plain_explanation": "string (20-1000 chars)",
  "error_category": "enum [authentication, authorization, build, dependency, deployment, environment_variables, network, runtime, unknown]",
  "likely_causes": [{"description": "string", "confidence": "enum [low, medium, high]"}],
  "missing_context_questions": ["string"],
  "risk_level": "enum [low, medium, high, critical]",
  "warnings": ["string"],
  "repair_prompt": "string (20-1500 chars)",
  "verification_steps": ["string"],
  "matched_recipes": ["string"]
}
```

The schema mandates that every output be a single JSON object without wrapping text. Additional properties are explicitly forbidden (`"additionalProperties": false`).

### 3.2 Corpus Engineering & Provenance
The OOPSIE dataset comprises 160 multi-turn developer error scenarios partitioned into four disjoint subsets:
- **Training Set (`data/train.jsonl`)**: 85 records (SHA-256: `be401b7f...`)
- **Validation Set (`data/validation.jsonl`)**: 18 records (SHA-256: `34cc646f...`)
- **Independent Test Set (`data/test.jsonl`)**: 17 records (SHA-256: `c4b2d10d...`)
- **Held-Out Final Benchmark (`evaluation/benchmark.jsonl`)**: 40 records (SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)

*Dataset Provenance & Review Status Disclosure*:
1. **Synthetic Generation**: Scenarios were generated synthetically using structured prompt templates covering common JavaScript/TypeScript, Python, Docker, Next.js, Firebase, and Supabase developer workflows.
2. **Review Status**: In the raw dataset metadata, all records carry `review.status = "unreviewed"`. The dataset **must not be characterized as human-curated expert ground truth**. Reference categories represent operational benchmark targets rather than infallible physical absolutes.
3. **Synthetic Benchmark Limitations**: As analyzed in software engineering literature (Hou et al., 2024), synthetic benchmarks carry inherent distribution simplifications. Unique scenario identifiers alone do not guarantee complete semantic independence; recurring error archetypes (e.g., missing dependencies, CORS misconfigurations) exhibit shared structural patterns across web frameworks.

### 3.3 Foundation Model Architecture & QLoRA Adaptation
All experiments utilize the public model `google/gemma-4-12B-it` (instruction-tuned Gemma 4, dense ~11.95 billion parameters; Gemma Team, 2026; Google LLC, 2026), recorded as `google/gemma-4-12b-it` in historical training run configurations.* The model features a unified causal decoder architecture with rotary positional embeddings and hybrid local/global attention, released under the Apache 2.0 license (Google LLC, 2026).

*\*Provenance Note on Model Identifier*: Hugging Face model repository paths are case-insensitive and route both `google/gemma-4-12B-it` and `google/gemma-4-12b-it` to the identical model checkpoint. The official public model identifier published by Google is `google/gemma-4-12B-it`, while historical training configuration files (`run_config.json` and `adapter_config.json`) in this repository recorded the lowercase form.

The pilot adapter (`oopsie-pilot-adapter`) was trained using the following configuration:
- **Quantization**: 4-bit NF4 (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_compute_dtype=torch.bfloat16`, double quantization enabled).
- **LoRA Parameters**: Rank $r=16$, Alpha $\alpha=32$, Dropout $0.05$.
- **Target Projections**: All linear projection layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`).
- **Optimization**: AdamW (`adamw_torch`), learning rate $2 \times 10^{-4}$, cosine learning rate schedule, effective batch size 4 (batch size 1 per device $\times$ 4 gradient accumulation steps), gradient checkpointing enabled.
- **Training Schedule**: 3 epochs (66 total optimizer steps). Validation loss on `data/validation.jsonl` reached its minimum at **Step 44 (Epoch 2, validation loss 0.693)**, which was selected as the frozen evaluation checkpoint.

---

## 4. Experimental Setup

### 4.1 Frozen Four-Condition Benchmark Specification
The benchmark was executed according to the pre-specified protocol `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`:

```
+-----------------------------------------------------------------------------------------+
|                                EXPERIMENTAL CONDITIONS                                  |
+---------------------+-------------------+------------------------+----------------------+
| Condition A         | Condition B       | Condition C            | Condition D          |
| Base Zero-Shot      | Adapter Zero-Shot | Base 1-Shot Demo       | Adapter Service      |
| + Full Schema       | + Full Schema     | + Full Schema          | (No In-Context Schema|
| Official Formatter  | Aligned Formatter | Official Formatter     | Aligned Formatter    |
+---------------------+-------------------+------------------------+----------------------+
```

1. **Condition A (Base Zero-Shot + Schema)**: Base model with adapter disabled (`with model.disable_adapter():`), prompt containing full schema text (~710 tokens), formatted with the official tokenizer chat template (`apply_chat_template`).
2. **Condition B (Adapter Zero-Shot + Schema)**: Adapted model (`oopsie-pilot-adapter`), prompt identical in text and schema to Condition A, formatted using the fine-tuning training template (`training_aligned_v1`, terminating with `<|turn|>model\n`).
3. **Condition C (Base 1-Shot + Schema)**: Base model with adapter disabled, prompt containing full schema text plus a fixed exemplar demonstration (`syn-dep-001`, `vite-missing-lucide-icons`), formatted with the official chat template.
4. **Condition D (Adapter Current Service Prompt)**: Adapted model, prompt matching runtime service deployment (~384 tokens, containing category enums but **omitting the JSON schema block**), formatted using `training_aligned_v1`.

### 4.2 Critical Methodological Confound Disclosure
> [!WARNING] Methodological Confound: System Comparison vs. Isolated Weight Ablation
> **Condition A and Condition B do not isolate adapter weights alone**. Because Condition A utilizes the model's official tokenizer chat template (`apply_chat_template`) while Condition B utilizes the training-aligned raw prompt boundary, this comparison evaluates **configured end-to-end systems under identical prompt text**, rather than an isolated single-variable weight ablation. Condition A and Condition B differ in both adapter presence and chat-template formatting boundaries. Condition D represents an experimental service deployment configuration, not a validated production guarantee.

### 4.3 Deterministic Inference & Execution Environment
All 160 evaluation passes (40 scenarios $\times$ 4 conditions) operated under deterministic greedy decoding:
- `temperature = 0.0`
- `do_sample = False`
- `max_new_tokens = 1024`
- Hardware: Single NVIDIA Tesla T4 GPU (14.56 GB allocated VRAM under 4-bit NF4 quantization, PyTorch 2.x, Python 3.10 / 3.14).

### 4.4 Evaluation Metrics: Programmatic vs. Qualitative
To avoid conflating syntactic formatting with technical correctness, evaluation is divided into two strictly separate tracks:

1. **Programmatic Compliance**:
   - *Raw RFC 8259 Validity*: Zero-tolerance string-to-JSON parsing (`json.loads`). Non-whitespace characters outside the outer braces fail.
   - *Strict Schema Conformance*: Validation against `data/schema.json` with forbidden additional properties, required keys, min-length assertions, and enum restrictions.
   - *Automated Category Agreement*: Exact string match of the `error_category` field against reference benchmark annotations.
   - *Inference Latency*: End-to-end wall-clock request duration per completion.

2. **Qualitative Diagnostic Reasoning**:
   - Assesses technical substance independently of JSON formatting.
   - Initial provisional ratings generated by an automated evaluation pipeline using a frozen rubric.
   - Flagged cases selectively reviewed and adopted by the author (recorded in an immutable snapshot manifest).
   - Evaluated across five scored dimensions: Technical Correctness, Unsupported Specifics / Hallucinations, Appropriate Uncertainty, Actionable Repair Scope, and Verification Steps Usefulness.
   - **Provenance & Review Boundary**: Ratings were AI-generated provisional ratings, selectively reviewed and adopted by the author. No independent human inter-rater evaluation was conducted, and no inter-rater reliability statistic (such as Cohen's $\kappa$) was computed.

---

## 5. Results

Across the 40 benchmark cases and four conditions, 160 consecutive generation passes were executed. Zero generation exceptions occurred, zero token budget terminations were triggered, and zero delimiter loops were detected.

### 5.1 Programmatic Performance Summary

| Metric | Condition A: Base Zero-Shot | Condition B: Adapter Zero-Shot | Condition C: Base 1-Shot | Condition D: Adapter Service |
| :--- | :---: | :---: | :---: | :---: |
| **Attempted Cases** | 40 / 40 | 40 / 40 | 40 / 40 | 40 / 40 |
| **Completed Forward Passes** | 40 / 40 (100%) | 40 / 40 (100%) | 40 / 40 (100%) | 40 / 40 (100%) |
| **Raw RFC 8259 JSON Valid** | **0 / 40 (0.0%)** | **38 / 40 (95.0%)** | **0 / 40 (0.0%)** | **40 / 40 (100.0%)** |
| **Strict Schema Conformance** | **0 / 40 (0.0%)** | **38 / 40 (95.0%)** | **0 / 40 (0.0%)** | **39 / 40 (97.5%)** |
| **Schema Valid 95% Wilson CI** | [0.0%, 8.8%] | [83.5%, 98.6%] | [0.0%, 8.8%] | [87.1%, 99.6%] |
| **Category Agreement (All 40 Attempted)** | 0 / 40 (0.0%) | 28 / 40 (70.0%) | 0 / 40 (0.0%) | 28 / 40 (70.0%) |
| **Category Agreement (Parseable Outputs)** | N/A (0 parseable) | 28 / 38 (73.7%) | N/A (0 parseable) | 28 / 40 (70.0%) |
| **Category Agreement (Schema-Valid Outputs)**| N/A (0 valid) | 28 / 38 (73.7%) | N/A (0 valid) | 27 / 39 (69.2%) |
| **Mean Latency per Case (Single Run)** | 118.62 s ($\pm 12.73$s) | 114.42 s ($\pm 11.53$s) | 119.35 s ($\pm 9.79$s) | 99.88 s ($\pm 11.93$s) |
| **Cumulative Single-Run Request Duration** | 79.1 min | 76.3 min | 79.6 min | 66.6 min |

*Timing Terminology & Latency Measurement Context*: Latency values represent wall-clock elapsed request times recorded in sequential single-instance inference (batch size = 1, `max_new_tokens = 1024`, greedy decoding) executed sequentially on a single NVIDIA Tesla T4 GPU (14.56 GB allocated VRAM under 4-bit NF4 quantization). The benchmark run evaluated each case once in a single sequential run without pre-run GPU warm-up passes or multi-repetition variance averaging; total cumulative execution across all 160 passes was 301.52 minutes (5.03 hours). The observed latency reduction between Condition B and Condition D (14.54 seconds, -12.7%) is reported as an observed operational characteristic under fixed evaluation conditions, not a performance guarantee, reflecting reduced prompt token length (~384 vs. ~1087 tokens).

### 5.2 Paired Contingency Transitions & Hypothesis Testing

Because each of the 40 scenarios was evaluated across all four conditions, comparisons are formally analyzed as paired $2 \times 2$ contingency transitions:

#### Primary Comparison: Base Zero-Shot (Condition A) vs. Adapter Zero-Shot (Condition B)

The empirical paired $2 \times 2$ contingency table for strict schema compliance ($N=40$) is:

| | Condition B: Pass (1) | Condition B: Fail (0) | Total |
| :--- | :---: | :---: | :---: |
| **Condition A: Pass (1)** | 0 | 0 | 0 |
| **Condition A: Fail (0)** | 38 | 2 | 40 |
| **Total** | 38 | 2 | 40 |

- **Concordant Pairs**: Both Pass ($A+ B+$) = 0; Neither Pass ($A- B-$) = 2.
- **Discordant Pairs**: Base only ($A+ B-$, $b$) = 0; Adapter only ($A- B+$, $c$) = 38. Total discordant pairs: $n_{\text{discordant}} = b + c = 38$.

**Inferential Hypothesis Testing**:
- **Null Hypothesis ($H_0$)**: Discordant outcomes are equally likely to favor either condition ($p = 0.5$).
- **Alternative Hypothesis ($H_1$, Two-Sided)**: Discordant outcomes favor one condition over the other ($p \neq 0.5$). Under $n=38$ discordant pairs with $c=38$ and $b=0$, the exact binomial test yields:
  $$p = 2 \times (0.5)^{38} \approx 7.28 \times 10^{-12}$$
  *(One-sided alternative $H_1: p > 0.5$, evaluating whether Condition B outperforms Condition A, yields $p = (0.5)^{38} \approx 3.64 \times 10^{-12}$).*
- **Edwards Continuity-Corrected $\chi^2$ Test**:
  $$\chi^2_{\text{corrected}} = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|0 - 38| - 1)^2}{38} = \frac{37^2}{38} = \frac{1369}{38} \approx 36.0263 \quad (df=1, p \approx 1.95 \times 10^{-9})$$
  *(Uncorrected McNemar test: $\chi^2 = 38^2 / 38 = 38.00, df=1, p \approx 7.07 \times 10^{-10}$).*

Both exact and asymptotic tests confirm that the observed difference in programmatic schema conformance between the two configured systems is statistically significant. We emphasize that these inferential tests evaluate paired binary outcomes of programmatic format compliance (i.e., whether an output parsed cleanly under zero-tolerance JSON schema assertions), not diagnostic correctness or technical reasoning quality.

#### Secondary Comparison: Adapter Matched (Condition B) vs. Adapter Service Prompt (Condition D)
The paired $2 \times 2$ contingency table between Condition B and Condition D ($N=40$) is:

| | Condition D: Pass (1) | Condition D: Fail (0) | Total |
| :--- | :---: | :---: | :---: |
| **Condition B: Pass (1)** | 37 | 1 | 38 |
| **Condition B: Fail (0)** | 2 | 0 | 2 |
| **Total** | 39 | 1 | 40 |

- Concordant: Both Pass ($B+ D+$) = 37 (92.5%); Neither Pass ($B- D-$) = 0.
- Discordant: Condition D only ($B- D+$) = 2 (`bench-firebase-01`, `bench-nextjs-01`); Condition B only ($B+ D-$) = 1 (`bench-npm-03`).

### 5.3 Disaggregated Category Agreement Breakdown
Category agreement was assessed against reference benchmark labels across 9 failure categories:

| Error Category | Cases ($N$) | Cond B (All) | Cond B (Parseable) | Cond D (All) | Cond D (Parseable) | Cond D (Schema-Valid) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **authentication** | 8 | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) | 6 / 8 (75.0%) |
| **authorization** | 3 | 0 / 3 (0.0%) | 0 / 3 (0.0%) | 1 / 3 (33.3%) | 1 / 3 (33.3%) | 1 / 3 (33.3%) |
| **build** | 4 | 1 / 4 (25.0%) | 1 / 3 (33.3%) | 1 / 4 (25.0%) | 1 / 4 (25.0%) | 1 / 4 (25.0%) |
| **dependency** | 4 | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 2 / 3 (66.7%) |
| **deployment** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) |
| **environment_variables** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) |
| **network** | 4 | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) | 4 / 4 (100.0%) |
| **runtime** | 5 | 3 / 5 (60.0%) | 3 / 4 (75.0%) | 3 / 5 (60.0%) | 3 / 5 (60.0%) | 3 / 5 (60.0%) |
| **unknown** | 4 | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) | 3 / 4 (75.0%) |
| **Total** | **40** | **28 / 40 (70.0%)** | **28 / 38 (73.7%)** | **28 / 40 (70.0%)** | **28 / 40 (70.0%)** | **27 / 39 (69.2%)** |

*Epistemic Qualification*: Category disagreements do not simply represent benign semantic borderlines. While certain cases involve ambiguous cross-domain faults (such as container network timeouts during deployment), others represent substantive diagnostic misclassifications against the reference taxonomy (e.g., misidentifying authorization policies as authentication failures). As evaluated in §5.5, several responses conflated authorization with authentication; however, no response received a Fail rating for technical correctness, unsupported specifics, or verification usefulness.

### 5.4 Forensic Failure Analysis

#### Non-Conforming Adapted Outputs (Conditions B and D)
Across the 80 adapted generation passes, exactly 3 failed strict schema conformance:
1. `bench-firebase-01` (Condition B): Failed raw JSON parsing due to `Invalid \escape at line 1 col 1490`. The model generated a backslash-escaped single quote (`\'`) within a configuration string literal. RFC 8259 permits only `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, and `\uXXXX` (Bray, 2017).
2. `bench-nextjs-01` (Condition B): Failed raw JSON parsing due to `Invalid \escape at line 1 col 1155`. The model emitted an illegal `\'` escape sequence inside an illustrative code snippet string.
3. `bench-npm-03` (Condition D): Successfully parsed as RFC 8259 JSON and correctly predicted error category `dependency`, but failed JSON Schema validation because the required property `"matched_recipes": []` was omitted from the JSON dictionary keys.

*Separation of Observation from Causal Inference*: We record the descriptive finding that `"matched_recipes"` was omitted; we do not assert that the absence of prompt schema text definitively caused this omission, as single-instance omissions can arise from stochastic decoding paths even under greedy search.

#### Base Model Formatting Deviations (Conditions A and C)
All 80 base model outputs failed zero-tolerance raw JSON parsing:
- **Markdown Fences**: 100.0% (80/80) wrapped completions in triple-backtick fences (` ```json ... ``` `).
- **Conversational Prose**: 92.5% (74/80) included conversational introductions (e.g., *"Here is the structured recovery plan for the error you provided:"*) or concluding pleasantries.

Under zero-tolerance parsing (which strictly rejects non-whitespace characters outside the outer JSON braces), these completions fail immediately. A formatting failure does not indicate an absence of underlying technical reasoning; however, it renders the unadapted model unusable for direct programmatic ingestion without brittle heuristic regex wrappers.

### 5.5 Qualitative Technical Evaluation Across Experimental Conditions

#### Protocol, Provenance, and Blinding Methodology
1. **Rubric Architecture**: Evaluations followed the frozen protocol ([`evaluation/protocols/prompting_vs_adaptation_v1.md`](evaluation/protocols/prompting_vs_adaptation_v1.md)), measuring an unscored administrative gate and five scored qualitative dimensions:
   - **Administrative Gate (Unscored)**: Content Assessability (`Assessable Content Present` vs. `Cannot Assess` / `No Usable Response`).
   - **Dimension 1**: Technical Correctness (`Pass (Correct)` / `Partial` / `Fail (Incorrect)`).
   - **Dimension 2**: Unsupported Specifics / Hallucinations (`None` / `Minor` / `Severe`).
   - **Dimension 3**: Appropriate Uncertainty (`Pass (Appropriate)` / `Overconfident`).
   - **Dimension 4**: Actionable Repair Scope (`Pass (Well-Scoped)` / `Vague` / `Harmful / Overbroad`).
   - **Dimension 5**: Verification Steps Usefulness (`Pass (Useful & Safe)` / `Incomplete` / `Fail (Unsound)`).
2. **Review Provenance & Adoption**: Initial qualitative ratings were generated provisionally by an automated evaluation pipeline using the frozen rubric definitions. The author reviewed a systematic verification checklist and made final adoption decisions for flagged evaluations (recorded in [`docs/research/author_decision_sheet.md`](docs/research/author_decision_sheet.md) and archived in the immutable cryptographic snapshot manifest [`docs/research/human_review/snapshots/2026-11-06/manifest.json`](docs/research/human_review/snapshots/2026-11-06/manifest.json)). The remaining provisional ratings were retained without case-by-case author review.
3. **Concealment and Blinding**: System identities (`System Alpha`, `System Beta`, `System Gamma`, `System Delta`) were concealed during initial provisional rating generation. However, this process was not a formally validated double-blind protocol. The author reviewed the unblinded aggregate results and made adoption decisions after condition identities were known for flagged cases.
4. **Scope and Distinction**: This evaluation does not constitute independent human review, inter-rater evaluation, expert-panel verification, or double-blind human review. No inter-rater reliability statistic (such as Cohen's $\kappa$) was computed.
5. **Separation from Programmatic Compliance**: These qualitative ratings assess diagnostic content and reasoning only; they are strictly separated from the programmatic JSON syntax and schema compliance metrics reported in §5.1. Responses with JSON syntax defects remained eligible for qualitative assessment when their diagnostic content was complete and interpretable; however, such defects remain recorded in the programmatic compliance results and may limit immediate machine usability of the response.

#### Qualitative Evaluation Aggregate Results
Every dimension is reported separately below with exact counts, percentages, and denominators ($N = 40$ per condition, $N = 160$ total). No composite score was computed.

##### Gate A: Administrative Content Eligibility Gate (Unscored)
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Assessable Content Present` | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 160 (100.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `No Usable Response` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

*All 160 responses across all conditions contained assessable diagnostic text.*

##### Dimension 1: Technical Correctness
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Correct)` | 39 (97.5%) | 37 (92.5%) | 40 (100.0%) | 37 (92.5%) | 153 (95.6%) |
| `Partial` | 1 (2.5%) | 3 (7.5%) | 0 (0.0%) | 3 (7.5%) | 7 (4.4%) |
| `Fail (Incorrect)` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

##### Dimension 2: Unsupported Specifics / Hallucinations
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `None` | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 160 (100.0%) |
| `Minor` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Severe` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

##### Dimension 3: Appropriate Uncertainty
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Appropriate)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 40 (100.0%) | 159 (99.4%) |
| `Overconfident` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 0 (0.0%) | 1 (0.6%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

##### Dimension 4: Actionable Repair Scope
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Well-Scoped)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 39 (97.5%) | 158 (98.8%) |
| `Vague` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Harmful / Overbroad` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 1 (2.5%) | 2 (1.2%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

##### Dimension 5: Verification Steps Usefulness
| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Useful & Safe)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 39 (97.5%) | 158 (98.8%) |
| `Incomplete` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 1 (2.5%) | 2 (1.2%) |
| `Fail (Unsound)` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

#### Empirical Observations and Descriptive Analysis
1. **Complete Content Assessability**: All 160 responses (100.0%) across the four conditions contained assessable diagnostic text.
2. **Absence of Severe Qualitative Failures**: Across all five scored dimensions, no response in any condition received a rating of `Fail (Incorrect)`, `Severe` hallucination, `Fail (Unsound)` verification, or `Cannot Assess`.
3. **Technical Correctness Distributions**:
   - Condition C (Base 1-Shot Exemplar + Schema) had the highest observed technical-correctness Pass rate: **40/40 (100.0%)**.
   - Condition A (Base Zero-Shot + Schema) had **39/40 Pass (97.5%)** and **1/40 Partial (2.5%)** (`bench-firebase-04`, where a storage security rule denial was categorized as authentication rather than authorization).
   - Conditions B and D each had **37/40 Pass (92.5%)** and **3/40 Partial (7.5%)** for technical correctness:
     - For Condition B: `bench-firebase-02` and `bench-firebase-04` (security rule denials categorized as authentication) and `bench-react-02` (asserting route recursion as the sole explanation for recursive update depth).
     - For Condition D: `bench-authentication-03` (missing OAuth scope categorized as authentication), `bench-firebase-02`, and `bench-firebase-04`.
4. **Repair Scope and Verification Steps**: Conditions B and D each had one `Harmful / Overbroad` repair-scope rating and one `Incomplete` verification rating on scenario `bench-npm-02`, where both adapted configurations recommended running `npm install --legacy-peer-deps`.
5. **Uncertainty Calibration**: Condition B had the only `Overconfident` uncertainty rating (`bench-react-02`), where a singular recursive route hypothesis was asserted without hedging.
6. **Descriptive Interpretation**: With 40 evaluations per condition, these descriptive differences do not establish a reliable advantage for the adapted conditions over the unadapted base model. The qualitative results do not support a claim that LoRA adaptation improved diagnostic correctness, reduced hallucinations, or improved repair scoping relative to the unadapted base model. The principal observed difference in this study concerned structural adherence to the required JSON output format, as reported separately in §5.1. The qualitative results alone do not establish a diagnostic-reasoning advantage for either adaptation condition.

---

## 6. Discussion

### 6.1 Structural Compliance vs. Diagnostic Reasoning
The central empirical finding of this investigation is a decoupling between structural format conformance and technical diagnostic reasoning. Parameter-efficient fine-tuning via QLoRA resolved the zero-tolerance programmatic ingestion failure mode that incapacitated the unadapted base model (converting 0.0% schema compliance to 95.0%–97.5%). However, this structural gain was not accompanied by an increase in diagnostic quality: the unadapted base model demonstrated equivalent or slightly higher raw technical correctness when its completions were parsed directly.

This observation has significant implications for how language model adaptation is conceptualized in software engineering. Fine-tuning on structured outputs primarily acts as a **structural behavioral filter**—suppressing preamble tokens and enforcing JSON syntactic delimiters—rather than expanding domain diagnostic knowledge. Developers seeking to deploy LLMs in automated pipelines can rely on QLoRA to achieve machine-readable output formats, but must not assume that adaptation confers superior diagnostic reasoning.

### 6.2 Schema Omission and Latency Observations
The secondary comparison between Condition B and Condition D demonstrates that an adapted model can reliably generate schema-compliant structures even when the ~710-token JSON schema definition is omitted from the runtime system prompt. Omitting schema text reduced prompt context size by 45.9%, leading to a 14.54-second (-12.7%) reduction in single-run mean response latency (from 114.42s to 99.88s) without degrading strict schema compliance (95.0% vs. 97.5%). As noted in §5.1, this measurement reflects a single sequential evaluation run (batch size 1, single NVIDIA Tesla T4 GPU) without multi-run variance averaging or pre-run GPU warm-up cycles; it represents an observed operational characteristic under fixed benchmark conditions, not a performance guarantee. Nonetheless, this observation indicates a practical operational benefit for developer tooling, where prompt token consumption directly impacts serving costs and response turnaround time.

### 6.3 Implications for Developer Toolchains and Downstream Agents
Automated developer agents and CI/CD healing bots cannot tolerate conversational noise or markdown fences when consuming diagnostic reports. Post-hoc regex wrappers and JSON repair passes introduce failure modes and heuristic complexity. While grammar-constrained decoding (Willard & Louf, 2023; Ugare et al., 2025) offers a formal mathematical guarantee of validity, it imposes specialized engine dependencies. QLoRA adaptation provides a compelling middle ground: high empirical compliance (up to 97.5% strict schema validity) operating on standard autoregressive serving stacks, while enabling lighter runtime prompts.

---

## 7. Limitations

1. **Small Benchmark Scope**: The evaluation is conducted across 40 held-out error scenarios. While each scenario was evaluated across four frozen conditions (160 forward passes), 40 cases represent a modest sample size that limits statistical power for detecting subtle qualitative reasoning shifts.
2. **Synthetic Dataset Lineage**: All benchmark scenarios were synthetically generated using structured templates covering common web, backend, and container workflows. They do not fully capture the long-tail complexity, massive stack traces, proprietary frameworks, and multi-repository dependencies found in enterprise environments (Hou et al., 2024).
3. **Single-Author Adoption of Provisional Ratings**: The qualitative technical evaluation was conducted via author adoption of systematic checklist flags following provisional automated grading, rather than independent multi-rater review. It carries inherent single-annotator subjective bias and lacks inter-rater reliability metrics (such as Cohen's $\kappa$).
4. **Absence of Production Validation**: OOPSIE has been evaluated in controlled offline benchmark settings; it has not been validated in live production CI/CD pipelines, live developer IDEs, or high-throughput telemetry streams.
5. **No Guarantee of Correctness or Safety**: While the adapted model achieved high programmatic compliance, parameter-based adaptation provides empirical probability, not absolute mathematical guarantees of validity or technical accuracy. Model suggestions can contain subtle misclassifications or suboptimal recommendations (e.g., `--legacy-peer-deps`).
6. **Need for Schema Validation and Human Oversight**: Because output validity is probabilistic, production deployments must maintain strict schema validation boundaries and human-in-the-loop developer review before executing any suggested remediation steps.
7. **Limited Generalization**: These findings are specific to `google/gemma-4-12B-it` and the 10-key OOPSIE diagnostic schema; they do not establish generalization to other model families, significantly different parameter scales, or non-diagnostic output schemas.

---

## 8. Ethics and Safety

### 8.1 Research Prototype Boundary
OOPSIE is an experimental **research prototype** designed to evaluate structured generation behaviors. It is explicitly **not a production-ready automated diagnostic or program repair system**. Model outputs must not be deployed in autonomous control loops without intermediate human inspection.

### 8.2 No Autonomous Remediation or Shell Execution
OOPSIE does not execute shell commands, alter file system states, mutate git repositories, or trigger deployment actions. Diagnostic reports contain advisory suggestions and suggested verification commands for human developer review only. System implementers must never pipe model outputs directly to shell interpreters (`sh`, `bash`, `powershell`) or automated healing daemons without human confirmation.

### 8.3 Human Oversight & Schema Validation Requirements
All downstream systems consuming OOPSIE outputs must enforce two mandatory safety gates:
1. **Machine-Level Schema Gate**: Strict automated validation against canonical JSON schemas, rejecting malformed, truncated, or unparseable payloads prior to downstream routing.
2. **Human-in-the-Loop Review**: Mandatory review by qualified software developers before applying recommended configuration changes, dependency modifications, or security rule updates.

### 8.4 Redaction of Sensitive Telemetry
Operational failure logs frequently contain sensitive environment variables, credentials, IP addresses, or internal hostnames. Deployments must implement best-effort regex and entropy-based credential redaction prior to submitting error logs to language model endpoints, adhering to computer security log management guidelines (NIST SP 800-92; Kent & Souppaya, 2006).

---

## 9. Reproducibility & Open Artifact Availability

To ensure full transparency and independent reproducibility, all evaluation harnesses, datasets, frozen protocols, and cryptographic manifests are openly available:

- **Repository**: [https://github.com/Onyx-Prasai/OOPSIE](https://github.com/Onyx-Prasai/OOPSIE)
- **GitHub Release v1.2.0**: [https://github.com/Onyx-Prasai/OOPSIE/releases/tag/v1.2.0](https://github.com/Onyx-Prasai/OOPSIE/releases/tag/v1.2.0)
- **Evaluation Bundle (ZIP)**: [`oopsie-eval-bundle-v1.2.0-four-conditions.zip`](https://github.com/Onyx-Prasai/OOPSIE/releases/download/v1.2.0/oopsie-eval-bundle-v1.2.0-four-conditions.zip)  
  *(SHA-256: `259bd473d9d18e0b13b79591ca1e44b0439667131b9e3966468d044ca05e42c5`)*
- **Benchmark Result Archive (TAR.GZ)**: [`oopsie_benchmark_results_v1_2_0.tar.gz`](https://github.com/Onyx-Prasai/OOPSIE/releases/download/v1.2.0/oopsie_benchmark_results_v1_2_0.tar.gz)  
  *(SHA-256: `cf24eec1a5c3347ae826fec4b5cbfb7133a1c4ce92aace3eab2b048bdd37f4eb`; verified clean archive excluding private unblinding keys)*
- **Reproduction Guide**: [`docs/reproduction-guide.md`](https://github.com/Onyx-Prasai/OOPSIE/blob/main/docs/reproduction-guide.md)
- **Model Card**: [`inference/model-card.md`](https://github.com/Onyx-Prasai/OOPSIE/blob/main/inference/model-card.md)
- **Evaluation Protocol Specification**: [`evaluation/protocols/prompting_vs_adaptation_v1.md`](https://github.com/Onyx-Prasai/OOPSIE/blob/main/evaluation/protocols/prompting_vs_adaptation_v1.md)
- **Committed Dataset Partitions**:
  - `data/train.jsonl` (SHA-256: `be401b7f...`)
  - `data/validation.jsonl` (SHA-256: `34cc646f...`)
  - `data/test.jsonl` (SHA-256: `c4b2d10d...`)
  - `evaluation/benchmark.jsonl` (SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)
  - `data/schema.json` (SHA-256: `40550bfef...`)

*Foundation Model Checkpoint*: The base model `google/gemma-4-12B-it` is publicly downloadable via Hugging Face under the Apache 2.0 license (Google LLC, 2026).

---

## 10. Conclusion

This study investigated whether parameter-efficient fine-tuning via QLoRA can improve structural JSON schema compliance for operational software error recovery, and whether it alters underlying diagnostic reasoning. In a pre-specified frozen benchmark across 40 unseen failure scenarios (160 total passes), QLoRA adaptation of `google/gemma-4-12B-it` dramatically improved programmatic schema compliance from 0.0% (base zero-shot and 1-shot) to 95.0%–97.5% under zero-tolerance greedy parsing, while eliminating conversational preambles and markdown fences. Furthermore, omitting the explicit schema text from the prompt reduced observed single-run latency by 12.7% without compromising structural integrity.

Crucially, the qualitative evaluation did not identify a diagnostic-reasoning or technical-correctness advantage for the adapted conditions over the unadapted base-model conditions. Within this benchmark, QLoRA adaptation functioned primarily as a structural output-format intervention rather than an amplifier of diagnostic reasoning. Consequently, operational deployments can leverage QLoRA for reliable automated JSON ingestion on standard serving stacks, but must maintain rigorous schema validation boundaries and human developer oversight.

---

## 11. AI Use Disclosure

The authors used AI-assisted tools during research and manuscript preparation. Initial qualitative ratings for the 160 benchmark completions were generated by an automated evaluation pipeline using a frozen rubric. The author reviewed key outputs, verification findings, and flagged evaluations, and takes full responsibility for the final work. The remaining provisional qualitative ratings were retained without case-by-case author review and are reported as author-adopted AI-assisted evaluations. These ratings are not independent human inter-rater assessments. AI tools were also used to assist with code development, documentation, manuscript drafting, and consistency checking.

---

## 12. Bibliographic References

1. **[Hu et al., 2022]** Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). *LoRA: Low-Rank Adaptation of Large Language Models*. International Conference on Learning Representations (ICLR 2022). Published conference paper. URL: [https://openreview.net/forum?id=nZeVKeeFYf9](https://openreview.net/forum?id=nZeVKeeFYf9).  
   *Claim Supported*: Low-rank parameter adaptation formulation ($W = W_0 + \frac{\alpha}{r}BA$) applied to transformer weight matrices (§1, §2.2, §3.3).

2. **[Dettmers et al., 2023]** Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). *QLoRA: Efficient Finetuning of Quantized LLMs*. Advances in Neural Information Processing Systems (NeurIPS 2023), Vol. 36, pp. 10088–10115. Published conference paper. URL: [https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html).  
   *Claim Supported*: 4-bit NormalFloat (NF4) base quantization with double quantization and compute-type casting enabling 12B model adaptation on 16 GB GPUs (§1, §2.2, §3.3).

3. **[Bray, 2017]** Bray, T. (Ed.). (2017). *The JavaScript Object Notation (JSON) Data Interchange Format*. Internet Engineering Task Force (IETF) Request for Comments (RFC 8259 / STD 90). Internet Standard. DOI: [10.17487/RFC8259](https://doi.org/10.17487/RFC8259).  
   *Claim Supported*: Defines strict RFC 8259 JSON syntax rules, token boundaries, and escape sequence restrictions. *Distinction*: RFC 8259 defines syntax only, not JSON Schema validation (§1, §2.1, §4.4, §5.4).

4. **[Wright et al., 2022a]** Wright, A., Andrews, H., Hutton, B., & Dennis, G. (Eds.). (2022). *JSON Schema: A Media Type for Describing JSON Documents*. IETF Internet-Draft `draft-bhutton-json-schema-01` (Draft 2020-12 dialect, June 16, 2022). Intended status: Informational. URL: [https://json-schema.org/draft/2020-12/json-schema-core.html](https://json-schema.org/draft/2020-12/json-schema-core.html).  
   *Claim Supported*: Defines JSON Schema Draft 2020-12 core mechanics, meta-schemas, schema identification keywords (`$schema`, `$id`), and applicator keywords (`properties`, `additionalProperties`, `items`) (§1, §2.1, §3.1).

5. **[Wright et al., 2022b]** Wright, A., Andrews, H., & Hutton, B. (Eds.). (2022). *JSON Schema Validation: A Vocabulary for Structural Validation of JSON*. IETF Internet-Draft `draft-bhutton-json-schema-validation-01` (Draft 2020-12 dialect, June 16, 2022). Intended status: Informational. URL: [https://json-schema.org/draft/2020-12/json-schema-validation.html](https://json-schema.org/draft/2020-12/json-schema-validation.html).  
   *Claim Supported*: Defines structural validation assertion keywords used in `data/schema.json`, specifically `type`, `enum`, `required`, and `minLength` (§1, §2.1, §3.1).

6. **[Willard & Louf, 2023]** Willard, B. T., & Louf, R. (2023). *Efficient Guided Generation for Large Language Models*. arXiv preprint arXiv:2307.09702. Preprint. URL: [https://arxiv.org/abs/2307.09702](https://arxiv.org/abs/2307.09702).  
   *Claim Supported*: Finite-state machine and regex-guided constrained decoding algorithms; provides context on decoding-time masking vs. parameter adaptation (§1, §2.1, §6.3).

7. **[Ugare et al., 2025]** Ugare, S., Suresh, T., Kang, H., Misailovic, S., & Singh, G. (2025). *SynCode: LLM Generation with Grammar Augmentation*. Transactions on Machine Learning Research (TMLR), June 2025. ISSN: 2835-8856. Published journal paper. URL: [https://openreview.net/forum?id=7h8p3hB3q5](https://openreview.net/forum?id=7h8p3hB3q5).  
   *Claim Supported*: Context-free grammar-guided decoding via offline DFA mask stores and runtime parser masks; contrasts runtime engine requirements with parameter adaptation (§1, §2.1, §6.3).

8. **[Leinonen et al., 2023]** Leinonen, J., Hellas, A., Sarsa, S., Reeves, B., Denny, P., Prather, J., & Becker, B. A. (2023). *Using Large Language Models to Enhance Programming Error Messages*. Proceedings of the 54th ACM Technical Symposium on Computer Science Education (SIGCSE 2023), Vol. 1, pp. 452–458. Published conference paper. DOI: [10.1145/3545945.3569770](https://doi.org/10.1145/3545945.3569770).  
   *Claim Supported*: Empirical tendency of unadapted LLMs to produce conversational text and formatting variations when explaining programming error traces (§2.1).

9. **[Zhang et al., 2024]** Zhang, Q., Fang, C., Ma, Y., Sun, W., & Chen, Z. (2024). *A Survey of Learning-Based Automated Program Repair*. ACM Transactions on Software Engineering and Methodology (TOSEM), Vol. 33, No. 2, Article 39, pp. 1–45. Published journal paper. DOI: [10.1145/3631974](https://doi.org/10.1145/3631974).  
   *Claim Supported*: Formal taxonomy of Automated Program Repair (fault localization, patch generation, patch validation against test suites); establishes that OOPSIE is an advisory diagnostic engine rather than an APR system (§2.3).

10. **[Hou et al., 2024]** Hou, X., Zhao, Y., Liu, Y., Yang, Z., Wang, K., Li, L., Luo, X., Lo, D., Grundy, J., & Wang, H. (2024). *Large Language Models for Software Engineering: A Systematic Literature Review*. ACM Transactions on Software Engineering and Methodology (TOSEM). Published journal paper. DOI: [10.1145/3695988](https://doi.org/10.1145/3695988).  
    *Claim Supported*: Methodological analysis of synthetic software engineering benchmarks, data leakage risks, and threats to external validity (§3.2, §7).

11. **[Gemma Team, 2026]** Gemma Team (Google DeepMind). (2026). *Gemma 4 Technical Report*. arXiv preprint arXiv:2607.02770. Preprint / Technical Report. URL: [https://arxiv.org/abs/2607.02770](https://arxiv.org/abs/2607.02770).  
    *Claim Supported*: Base architecture specification for `google/gemma-4-12B-it` (unified decoder, ~11.95B dense parameters, hybrid local/global attention) (§3.3).

12. **[Google LLC, 2026]** Google LLC. (2026). *google/gemma-4-12B-it Model Card and Repository*. Hugging Face. Software repository / Model card. URL: [https://huggingface.co/google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it).  
    *Claim Supported*: Official license identification (Apache 2.0) governing the base checkpoint (§3.3, §9).

13. **[Chen et al., 2021]** Chen, M., Tworek, J., Jun, H., Yuan, Q., Pinto, H. P. de O., Kaplan, J., Edwards, H., Burda, Y., Joseph, N., Brockman, G., Ray, A., Puri, R., Dennison, G., Sigler, F., Prashanth, N., Arora, A., Chantzis, P., Gray, M., Zwierzchowska, K., ... & Zaremba, W. (2021). *Evaluating Large Language Models Trained on Code*. arXiv preprint arXiv:2107.03374. URL: [https://arxiv.org/abs/2107.03374](https://arxiv.org/abs/2107.03374).  
    *Claim Supported*: Establishes baseline code reasoning and synthesis capabilities of instruction-tuned code language models via HumanEval (§1).

14. **[Jimenez et al., 2024]** Jimenez, C. E., Yang, J., Wettig, A., Yao, S., Pei, K., Press, O., & Narasimhan, K. (2024). *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*. International Conference on Learning Representations (ICLR 2024). Published conference paper. URL: [https://openreview.net/forum?id=VTColl7Dbx](https://openreview.net/forum?id=VTColl7Dbx).  
    *Claim Supported*: Demonstrates that real-world developer issue resolution requires complex environment interaction and navigation (§1).

15. **[Rozière et al., 2023]** Rozière, B., Gehring, J., Gloeckle, F., Sootla, S., Gat, I., Tan, X. E., Adi, Y., Liu, J., Remez, T., Rapin, J., Kozhevnikov, A., Evtimov, I., Bitton, J., Bhatt, M., Canton-Ferrer, C., Grattafiori, A., Xiong, W., Défossez, A., Copet, J., ... & Synnaeve, G. (2023). *Code Llama: Open Foundation Models for Code*. arXiv preprint arXiv:2308.12950. URL: [https://arxiv.org/abs/2308.12950](https://arxiv.org/abs/2308.12950).  
    *Claim Supported*: Precedent for parameter adaptation and instruction-tuning on developer and code artifacts (§2.2).

16. **[Li et al., 2023]** Li, R., Allal, L. B., Zi, Y., Muennighoff, N., Kocetkov, D., Mou, C., Marone, M., Akiki, C., Li, J., Chim, J., Liu, Q., Zheltonozhskii, E., Zhuo, T. Y., Wang, H., Dehaene, O., Dullaert, M., Shen, C. J., Zhang, C., Kwok, C., ... & Harm de Vries. (2023). *StarCoder: may the source be with you!*. arXiv preprint arXiv:2305.06161. URL: [https://arxiv.org/abs/2305.06161](https://arxiv.org/abs/2305.06161).  
    *Claim Supported*: Precedent for open-source foundation code models and token-level conditioning (§2.2).

17. **[Kent & Souppaya, 2006]** Kent, K., & Souppaya, M. (2006). *Guide to Computer Security Log Management*. National Institute of Standards and Technology (NIST) Special Publication 800-92. DOI: [10.6028/NIST.SP.800-92](https://doi.org/10.6028/NIST.SP.800-92).  
    *Claim Supported*: Authoritative guidance on log privacy, sanitization, and security management requirements for operational error traces (§8.4).

---

## Appendix

### Appendix A: Benchmark Scenario Taxonomies & Distribution
The 40 held-out evaluation scenarios cover nine diagnostic categories:
- `authentication` (8 cases): OAuth redirect URI mismatches, JWT secret misconfigurations, expired session tokens, Supabase client key issues.
- `authorization` (3 cases): Firebase storage security rule denials, AWS IAM policy boundary violations, RBAC permission errors.
- `build` (4 cases): TypeScript type-check failures, Vite bundling errors, Webpack loader syntax issues.
- `dependency` (4 cases): NPM peer dependency conflicts, Python package version mismatches, lockfile discrepancies.
- `deployment` (4 cases): Docker container exit codes, Kubernetes crashloop backoffs, health check probe timeouts.
- `environment_variables` (4 cases): Missing `.env` keys, variable name typos, unexpanded template variables.
- `network` (4 cases): CORS header rejections, DNS lookup failures, reverse proxy 502 bad gateways.
- `runtime` (5 cases): Null pointer dereferences, React infinite re-render loops, unhandled Promise rejections.
- `unknown` (4 cases): Ambiguous mixed-trace failures, truncated logs without clear stack traces.

### Appendix B: Experimental Prompt Formats
- **Condition A (Base Zero-Shot + Schema)**: Utilizes official Gemma chat template with `<start_of_turn>user\n...<end_of_turn>\n<start_of_turn>model\n`. System instruction incorporates the full ~710-token JSON schema.
- **Condition B (Adapter Zero-Shot + Schema)**: Uses fine-tuning aligned template (`training_aligned_v1`) terminating in `<|turn|>model\n`. Identical schema text as Condition A.
- **Condition C (Base 1-Shot + Schema)**: Official chat template containing multi-turn user/model interaction with fixed demonstration `syn-dep-001` prior to the query scenario.
- **Condition D (Adapter Current Service Prompt)**: Uses `training_aligned_v1` without in-context JSON schema definition (~384 tokens), including only category enums and field role guidance.

### Appendix C: Qualitative Evaluation Rubric Definitions
The five scored qualitative evaluation dimensions are evaluated according to the frozen protocol:
1. **Technical Correctness**:
   - `Pass (Correct)`: Diagnoses the underlying failure mechanism accurately based on provided logs.
   - `Partial`: Diagnoses related symptoms or conflates closely coupled categories (e.g., auth vs. authz) without fatal diagnostic error.
   - `Fail (Incorrect)`: Identifies an entirely incorrect cause that would mislead debugging.
2. **Unsupported Specifics / Hallucinations**:
   - `None`: All referenced files, line numbers, variable names, and error strings are grounded in the input prompt.
   - `Minor`: Inconsequential invented names in illustrative examples that do not affect diagnosis.
   - `Severe`: Fabricated libraries, non-existent APIs, or misleading line references presented as factual.
3. **Appropriate Uncertainty**:
   - `Pass (Appropriate)`: Acknowledges missing context when logs are truncated or ambiguous; asks targeted clarifying questions.
   - `Overconfident`: Asserts a singular definitive hypothesis on ambiguous logs without hedging.
4. **Actionable Repair Scope**:
   - `Pass (Well-Scoped)`: Minimal, targeted remediation steps specific to the root cause.
   - `Vague`: Generic advice (*"check your logs and fix permissions"*).
   - `Harmful / Overbroad`: Destructive or security-degrading recommendations (e.g., `chmod 777`, `--legacy-peer-deps` without explanation).
5. **Verification Steps Usefulness**:
   - `Pass (Useful & Safe)`: Concrete, executable commands or checks to verify the fix.
   - `Incomplete`: Advice on what to verify without actionable commands.
   - `Fail (Unsound)`: Commands that would produce false confidence or collateral damage.

### Appendix D: Immutable Cryptographic Snapshot Manifest
The author-adopted qualitative ratings are preserved in an immutable directory structure at `docs/research/human_review/snapshots/2026-11-06/` with the manifest SHA-256 hash verified against the 10 source files:
- `manifest.json`: Cryptographically verifies `blinded_human_review_sheet.md`, `checkpoint_results.jsonl`, `summary_metrics.json`, `execution_manifest.json`, `run_manifest.json`, `benchmark_results_full.json`, and supporting review sheets.
