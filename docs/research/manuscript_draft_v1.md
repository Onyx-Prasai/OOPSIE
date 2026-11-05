# OOPSIE: Structured Developer Error-Recovery Modeling via Low-Rank Domain Adaptation

**Author**: Onyx Prasai  
**Contact**: `[Author Contact Email: author@domain.example]`  
**Institutional Affiliation**: Independent Researcher *(no institutional affiliation asserted)*  
**Manuscript Version**: Draft v1.2.1 (Pre-Review Working Paper)  
**Date**: November 2026  

---

## Abstract

Modern software engineering environments generate high volumes of ambiguous build failures, runtime exceptions, and deployment misconfigurations. While large language models (LLMs) can synthesize troubleshooting advice, applying unconstrained general-purpose chat models as programmatic diagnostic backends suffers from output non-determinism, markdown wrapping, preamble contamination, and structural schema violations under strict automated ingestion. 

In this work, we present **OOPSIE** (Operational Output Parser & Structured Inference Engine), an open framework designed to generate strictly compliant, machine-readable diagnostic and recovery plans directly conforming to an RFC 8259-compliant JSON schema (JSON Schema Draft 2020-12; Wright et al., 2022a, 2022b) without requiring automated post-hoc repair passes or grammar-constrained sampling. We fine-tuned an instruction-tuned foundation model (`google/gemma-4-12b-it`, released by Google under the Apache 2.0 license) using 4-bit NormalFloat (NF4) Quantized Low-Rank Adaptation (QLoRA, rank $r=16$, $\alpha=32$) on a multi-turn developer error-recovery corpus. 

We evaluate the system under a frozen, pre-registered four-condition benchmark across 40 unseen, held-out error scenarios (160 total generation passes) under zero-tolerance greedy decoding:
- **Condition A** (Base Zero-Shot + Schema) achieved **0 / 40 (0.0%)** strict schema compliance due to conversational preambles and markdown fences.
- **Condition B** (Adapter Zero-Shot + Schema) achieved **38 / 40 (95.0%)** strict schema compliance, demonstrating a statistically significant improvement in programmatic conformance (exact paired McNemar test $p \approx 7.28 \times 10^{-12}$; Edwards continuity-corrected $\chi^2 = 36.03, p \approx 1.95 \times 10^{-9}$).
- **Condition C** (Base 1-Shot + Schema) achieved **0 / 40 (0.0%)** compliance, showing that in-context demonstrations alone did not eliminate conversational formatting artifacts under zero-tolerance parsing.
- **Condition D** (Adapter Service Prompt, without in-context schema text) achieved **39 / 40 (97.5%)** strict compliance and **40 / 40 (100.0%)** raw JSON syntax parsing, while reducing mean inference latency by 14.54 seconds (-12.7%).
Across parseable completions, diagnostic category agreement with reference annotations reached 73.7% in Condition B and 70.0% in Condition D (69.2% among schema-valid outputs). 

We present a comprehensive forensic analysis of non-conforming outputs, outline our author-performed, system-label-anonymized technical review protocol (currently pending), and explicitly discuss structural confounds—including the difference in prompt formatting boundaries between base and adapted conditions. All evaluation harnesses, datasets, and cryptographic manifests are documented for reproducibility.

---

## 1. Introduction & Research Questions

When automated builds, CI/CD pipelines, or deployment orchestrators encounter unhandled exceptions, human developers or automated healing agents require three immediate diagnostic deliverables:
1. An accurate identification of the failure domain (e.g., authentication, environment variable misconfiguration, peer dependency conflict).
2. A safe, minimal, and non-destructive remediation procedure.
3. Concrete verification commands to determine whether the fix resolved the underlying fault without creating collateral regressions.

General-purpose instruction-tuned models possess substantial parametric knowledge regarding software development. However, deploying them as programmatic middleware in developer toolchains presents severe operational challenges. Under standard greedy decoding, instruction-tuned chat models frequently emit conversational pleasantries (*"Certainly, here is the explanation..."*), enclose JSON payloads in Markdown code fences (` ```json `), or produce syntactic deviations (such as unescaped quotes or illegal escape sequences). When downstream tooling enforces zero-tolerance RFC 8259 JSON validation (Bray, 2017), these formatting deviations result in total pipeline failures.

To address this challenge, two architectural paradigms exist:
- **Constrained Decoding**: Enforcing strict grammar transitions at every token generation step via finite-state machines or context-free grammars (e.g., Willard & Louf, 2023; Ugare et al., 2025). Constrained sampling mathematically guarantees output validity according to a defined grammar; however, it requires specialized runtime engine integrations (e.g., vocabulary-masking hooks and custom parser states) that are not natively supported across all deployment environments.
- **Domain Adaptation (Fine-Tuning)**: Embedding structural format bias and domain-specific diagnostic scoping directly into model parameters via Low-Rank Adaptation (LoRA; Hu et al., 2022) and QLoRA (Dettmers et al., 2023). This approach operates on standard autoregressive inference engines without specialized grammar-masking dependencies, but yields empirical probabilistic compliance rather than mathematical guarantees.

### Research Questions
This paper investigates the feasibility, reliability, and limitations of domain adaptation for structured error recovery:
- **RQ1 (Structural Compliance)**: To what extent does parameter-efficient adaptation induce strict, zero-tolerance JSON schema conformance compared to zero-shot and few-shot in-context prompting of the identical base model?
- **RQ2 (Schema Overhead & Latency)**: Can an adapted model reliably generate schema-compliant structures when the explicit JSON schema definition (~710 tokens) is omitted from the runtime system prompt, and what latency benefits accrue?
- **RQ3 (Diagnostic Fidelity & Operational Safety)**: Does structural adaptation preserve diagnostic category accuracy, and what failure modes characterize non-conforming generations?

---

## 2. Related Work

### 2.1 Structured and Constrained Generation from Language Models
Generating structured data (JSON, SQL, ASTs) from autoregressive transformers has progressed along two major approaches:
1. *Prompt-Guided In-Context Structuring*: Early workflows relied on detailed prompt instructions, schema definitions, and few-shot demonstrations to steer foundation models toward valid formats. However, empirical studies in developer-facing tasks demonstrate that unconstrained models exhibit non-trivial syntax error rates, extraneous conversational preambles, and delimiter confounds under strict parsers (Leinonen et al., 2023). While downstream systems often apply heuristic regex wrappers or markdown-stripping passes, such post-hoc repairs are fragile and unstandardized.
2. *Grammar-Constrained Decoding*: Recent frameworks such as Outlines (Willard & Louf, 2023) and SynCode (Ugare et al., 2025) utilize regular expressions, context-free grammars (CFGs), and deterministic finite automaton (DFA) mask stores to dynamically restrict vocabulary token logits during decoding. This approach provides formal guarantees of syntactic validity (e.g., adherence to RFC 8259 JSON syntax; Bray, 2017). While optimized implementations (such as SynCode's pre-computed DFA lookup tables) mitigate token-evaluation latency, grammar-constrained decoding requires specialized runtime engines with low-level logit-masking hooks, which complicates deployment across heterogeneous edge devices or standard serving stacks.

*Comparison with OOPSIE*: Rather than enforcing token masking at decoding time, OOPSIE evaluates the behavioral extent to which parameter-efficient fine-tuning can generate complex, multi-property JSON schemas conforming to JSON Schema Draft 2020-12 (Core specification: Wright et al., 2022a; Validation specification: Wright et al., 2022b) directly from standard greedy decoding. While parameter adaptation provides empirical probabilistic reliability rather than formal mathematical guarantees, it eliminates runtime engine dependencies and enables omitting schema text from prompts.

### 2.2 Parameter-Efficient Fine-Tuning for Domain Structuring
Low-Rank Adaptation (LoRA; Hu et al., 2022) freezes pre-trained foundation model weights and injects trainable rank-decomposition matrices into transformer attention and feed-forward projections ($W = W_0 + \frac{\alpha}{r}BA$). Quantized Low-Rank Adaptation (QLoRA; Dettmers et al., 2023) extends this approach by quantizing the base model to 4-bit NormalFloat (NF4) with double quantization and compute-type casting, enabling efficient fine-tuning of 12B+ parameter models on single commodity GPUs (e.g., 16 GB Tesla T4). While LoRA has been extensively evaluated on instruction-following, mathematical reasoning, and general programming benchmarks, its empirical capability to enforce rigid 10-key hierarchical schemas under zero-tolerance parsing without grammar masking remains sparsely benchmarked.

### 2.3 Automated Program Repair vs. Advisory Diagnostics
Automated Program Repair (APR) systems historically employ search-based algorithms, symbolic execution, or neural patch generation to modify source code, re-compile binaries, and validate candidate patches against automated test suites (Zhang et al., 2024). 

*Critical Boundary*: **OOPSIE is explicitly not an automated program repair (APR) system**. OOPSIE does not generate code diffs, execute compiler commands, mutate repositories, or run test suites. Instead, OOPSIE functions strictly as an **advisory diagnostic engine**. It translates raw runtime exceptions and build failures into structured, human-reviewable diagnostic reports comprising causal hypotheses, clarifying questions, risk warnings, copy-ready prompts for developer inspection, and non-destructive verification steps.

---

## 3. Corpus Engineering, Provenance, & Annotation Status

### 3.1 Corpus Specification & Split Lineage
The OOPSIE dataset comprises 160 multi-turn developer error scenarios structured into four disjoint partitions:
- **Training Set (`data/train.jsonl`)**: 85 records (SHA-256: `be401b7f...`)
- **Validation Set (`data/validation.jsonl`)**: 18 records (SHA-256: `34cc646f...`)
- **Independent Test Set (`data/test.jsonl`)**: 17 records (SHA-256: `c4b2d10d...`)
- **Held-Out Final Benchmark (`evaluation/benchmark.jsonl`)**: 40 records (SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)

All records adhere to a canonical 10-key schema ([`data/schema.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/data/schema.json)) formalized under the JSON Schema Draft 2020-12 dialect, utilizing structural applicator keywords (`$schema`, `$id`, `properties`, `additionalProperties`, `items`) specified in the JSON Schema Core specification (Wright et al., 2022a) and structural assertion keywords (`type`, `enum`, `required`, `minLength`) specified in the JSON Schema Validation specification (Wright et al., 2022b):
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

### 3.2 Dataset Provenance & Review Status Disclosure
To maintain scientific transparency, we disclose the following provenance characteristics:
1. **Synthetic Generation**: Scenarios were generated synthetically using structured prompt templates covering common JavaScript/TypeScript, Python, Docker, Next.js, Firebase, and Supabase developer workflows.
2. **Review Status**: In the raw dataset metadata, all records carry `review.status = "unreviewed"`. The dataset **must not be characterized as human-curated expert ground truth**. Reference categories represent operational benchmark targets rather than infallible physical absolutes.
3. **Synthetic Benchmark Limitations**: As analyzed in software engineering literature (Hou et al., 2024), synthetic benchmarks carry inherent distribution simplifications. Unique scenario identifiers alone do not guarantee complete semantic independence; recurring error archetypes (e.g., missing dependencies, CORS misconfigurations) exhibit shared structural patterns across web frameworks.

---

## 4. Model Architecture & Adaptation Configuration

### 4.1 Base Foundation Model
All experiments utilize `google/gemma-4-12b-it` (instruction-tuned Gemma 4, dense ~11.95 billion parameters; Gemma Team, 2026). The model features a unified causal decoder architecture with rotary positional embeddings and hybrid local/global attention.

*Licensing & Governance*: `google/gemma-4-12b-it` is released by Google under the permissive **Apache 2.0 license** (Google LLC, 2026), permitting open commercial and research use, modification, and redistribution.

### 4.2 LoRA Configuration & Effective Training Settings
The adapter (`oopsie-pilot-adapter`) was trained using the following verified settings from `artifacts/pilot_v1/artifacts/run_config.json`:
- **Quantization**: 4-bit NF4 (`load_in_4bit=True`, `bnb_4bit_quant_type="nf4"`, `bnb_4bit_compute_dtype=torch.bfloat16`, with double quantization `bnb_4bit_use_double_quant=True`)
- **LoRA Rank ($r$)**: 16
- **LoRA Alpha ($\alpha$)**: 32
- **LoRA Dropout**: 0.05
- **Target Modules**: All linear projection layers (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`)
- **Optimization**: Standard AdamW (`adamw_torch`), learning rate $2 \times 10^{-4}$, cosine learning rate schedule, per-device batch size 1 with gradient accumulation steps 4 (effective batch size 4).
- **Gradient Checkpointing**: Enabled (`gradient_checkpointing=True`).
- **Training Epochs**: 3 epochs (66 total optimizer steps). Checkpoint selection was determined by validation loss on `data/validation.jsonl`, which reached its minimum at **Step 44 (Epoch 2, validation loss 0.693)**.

### 4.3 Inference Configuration
All evaluation passes operated under strict deterministic parameters:
- `temperature = 0.0` (greedy decoding)
- `do_sample = False`
- `max_new_tokens = 1024`
- Hardware: Single Kaggle GPU instance (NVIDIA Tesla T4, 14.56 GB allocated VRAM, Python 3.10 / 3.13, PyTorch 2.x).

---

## 5. Frozen Four-Condition Evaluation Protocol

The evaluation was executed according to pre-registered protocol `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`:

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

### Condition Definitions
1. **Condition A (Base Zero-Shot + Schema)**: Base model (`model.disable_adapter()`), prompt containing the full canonical JSON schema (~710 tokens), formatted with the official tokenizer chat template.
2. **Condition B (Adapter Zero-Shot + Schema)**: Adapted model (`oopsie-pilot-adapter`), prompt identical in text and schema to Condition A, formatted using the fine-tuning training template (`training_aligned_v1`, terminating with `<|turn|>model\n`).
3. **Condition C (Base 1-Shot + Schema)**: Base model (`model.disable_adapter()`), prompt containing full schema text plus a fixed exemplar demonstration (`syn-dep-001`, `vite-missing-lucide-icons`), formatted with the official chat template.
4. **Condition D (Adapter Current Service Prompt)**: Adapted model, prompt matching the production inference service configuration (~384 tokens, containing category enums but **omitting the JSON schema block**), formatted using `training_aligned_v1`.

### Critical Methodological Confound Disclosure
> [!WARNING] Methodological Confound: System Comparison vs. Isolated Weight Ablation
> **Condition A and Condition B do not isolate adapter weights alone**. Because Condition A utilizes the model's official tokenizer chat template (`apply_chat_template`) while Condition B utilizes the training-aligned raw prompt boundary, this comparison evaluates **configured end-to-end systems under identical prompt text**, rather than an isolated single-variable weight ablation. Condition D represents an experimental service deployment configuration, not a validated production guarantee.

---

## 6. Empirical Results & Paired Statistical Transitions

Across the 40 benchmark cases and four conditions, 160 consecutive generation passes were executed. Zero generation exceptions occurred, zero token budget terminations were triggered, and zero delimiter loops were detected.

### 6.1 Core Performance Summary

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
| **Mean Latency per Case** | 118.62 s | 114.42 s | 119.35 s | 99.88 s |
| **Cumulative Request Duration** | 79.1 min | 76.3 min | 79.6 min | 66.6 min |

*Timing Terminology*: Cumulative request duration measures total wall-clock elapsed time across sequential inference requests (total across all 160 passes: 301.52 minutes / 5.03 hours). It represents end-to-end API latency and must not be described as pure GPU compute time.

### 6.2 Paired Contingency Transitions & Hypothesis Testing

Because each test case was evaluated across all four conditions, results are analyzed as paired 2x2 contingency transitions:

#### Primary Comparison: Base Zero-Shot (A) vs. Adapter Zero-Shot (B)
- **Both Pass ($A+ B+$)**: 0 / 40 (0.0%)
- **Adapter-Only Pass ($A- B+$)**: **38 / 40 (95.0%)**
- **Base-Only Pass ($A+ B-$)**: 0 / 40 (0.0%)
- **Neither Pass ($A- B-$)**: 2 / 40 (5.0%)

**Statistical Significance**:
- **Exact Binomial McNemar Test**: On $n=38$ discordant pairs ($b=38, c=0$), the exact two-sided binomial test under null hypothesis $H_0: p=0.5$ yields:
  $$p = 2 \times (0.5)^{38} \approx 7.28 \times 10^{-12}$$
- **Asymptotic $\chi^2$ Approximation (Edwards Continuity Correction)**:
  $$\chi^2_{\text{corrected}} = \frac{(|38 - 0| - 1)^2}{38} = \frac{37^2}{38} = \frac{1369}{38} \approx 36.03 \quad (df=1, p \approx 1.95 \times 10^{-9})$$
  *(Without continuity correction: $\chi^2 = 38^2 / 38 = 38.00, p \approx 7.07 \times 10^{-10}$).*

The empirical advantage in strict schema conformance is statistically significant under both exact and asymptotic tests.

#### Secondary Comparison: Adapter Matched (B) vs. Adapter Service Prompt (D)
- **Both Pass ($B+ D+$)**: 37 / 40 (92.5%)
- **D-Only Pass ($B- D+$)**: 2 / 40 (5.0%) (`bench-firebase-01`, `bench-nextjs-01`)
- **B-Only Pass ($B+ D-$)**: 1 / 40 (2.5%) (`bench-npm-03`)
- **Neither Pass ($B- D-$)**: 0 / 40 (0.0%)

Omitting the in-context JSON schema definition reduced mean latency by 14.54 seconds (-12.7%) while increasing raw JSON validity from 95.0% to 100.0%.

### 6.3 Disaggregated Category Agreement Breakdown

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

*Epistemic Qualification*: Category disagreements do not simply represent benign semantic borderlines. While certain cases involve ambiguous cross-domain faults (such as container network timeouts during deployment), others represent substantive diagnostic misclassifications against the reference taxonomy (e.g., misidentifying authorization policies as authentication failures). Qualitative human review is necessary to assess the validity of these diagnoses.

---

## 7. Forensic Failure Analysis

### 7.1 Non-Conforming Adapted Outputs (Conditions B and D)
Across the 80 adapted model generation passes, exactly 3 failed strict schema conformance:
1. `bench-firebase-01` (Condition B): Failed raw JSON parsing due to `Invalid \escape at line 1 col 1490`. The model generated a backslash-escaped single quote (`\'`) within a configuration string literal. RFC 8259 permits only `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, and `\uXXXX` (Bray, 2017).
2. `bench-nextjs-01` (Condition B): Failed raw JSON parsing due to `Invalid \escape at line 1 col 1155`. The model emitted an illegal `\'` escape sequence inside an illustrative code snippet string.
3. `bench-npm-03` (Condition D): Successfully parsed as RFC 8259 JSON and correctly predicted error category `dependency`, but failed JSON Schema validation because the required property `"matched_recipes": []` was omitted from the JSON dictionary keys.

*Separation of Observation from Causal Inference*: We record the descriptive finding that `"matched_recipes"` was omitted; we do not assert that the absence of prompt schema text definitively caused this omission, as single-instance omissions can arise from stochastic decoding paths even under greedy search.

### 7.2 Base Model Formatting Deviations (Conditions A and C)
All 80 base model outputs failed zero-tolerance raw JSON parsing:
- **Markdown Fences**: 100.0% (80/80) wrapped completions in triple-backtick fences (` ```json ... ``` `).
- **Conversational Prose**: 92.5% (74/80) included conversational introductions (e.g., *"Here is the structured recovery plan for the error you provided:"*) or concluding pleasantries.

Under zero-tolerance parsing (which strictly rejects non-whitespace characters outside the outer JSON braces), these completions fail immediately. We emphasize that a formatting failure does not indicate an absence of underlying technical reasoning; however, it renders the unadapted model unusable for direct programmatic ingestion without brittle heuristic regex wrappers.

---

## 8. Author-Performed, System-Label-Anonymized Technical Evaluation: PENDING

To evaluate qualitative diagnostic soundness, we established an author-performed, system-label-anonymized review protocol:

### 8.1 Protocol & Partitioning
- The 40 benchmark cases were partitioned into 8 review batches of 5 cases each ([`docs/research/human_review/`](file:///c:/Users/onyxe/Desktop/OOPSIE/docs/research/human_review/)).
- Systems are anonymized as `System Alpha`, `System Beta`, `System Gamma`, and `System Delta` in randomized presentation order per case.
- The unblinding key remains sealed in a separate isolated file ([`artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json)).

### 8.2 Rubric Consistency & Structure (Dated 2026-11-05)
The frozen evaluation protocol ([`evaluation/protocols/prompting_vs_adaptation_v1.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/protocols/prompting_vs_adaptation_v1.md), Section 8) establishes exactly **five scored qualitative dimensions**:
1. **Technical Correctness** [Pass / Partial / Fail]
2. **Unsupported Claims** [None / Minor / Severe]
3. **Appropriate Uncertainty** [Pass / Overconfident]
4. **Actionable Repair Scope** [Pass / Vague / Harmful]
5. **Verification Steps Usefulness** [Pass / Incomplete / Fail]

To operationalize the protocol's rule that *"malformed, unparseable, or empty model outputs remain visible to the reviewer as explicit No-Usable-Response outcomes"*, an **Administrative Eligibility Gate** (**Content Assessability**) is recorded prior to scoring:
- **Administrative Gate (Unscored)**: Records whether the completion contains assessable semantic text versus being unassessable (empty string, binary garbage) or an uninformative refusal (`No Usable Response`).
- **Scored Dimensions (5 Frozen Dimensions)**: Only completions possessing assessable content are scored across dimensions 1–5. When flagged as `Cannot Assess` or `No Usable Response`, the reviewer marks `[x] Cannot Assess` across the five scored dimensions and records the observation in the notes.

### 8.3 Evaluation Status & Methodological Disclosures
> [!IMPORTANT] Review Status: PENDING
> As of this manuscript draft, **manual human technical review scores have not been completed**. Scoring cells remain intentionally blank to prevent premature or unvalidated claims.
> 
> *Review Design Disclosure*: All qualitative evaluations will be conducted as single-annotator ratings by the study author (Onyx Prasai), unless an independent external annotator participates. **This protocol is not double-blind**: because the author designed the systems and conducts the review, and because surface formatting cues (e.g., markdown fences in base completions vs. raw JSON in adapted completions) readily distinguish model configurations, full cognitive blinding is not achievable. The reviewer evaluates technical substance independently of output formatting.

---

## 9. Limitations & Threats to Validity

1. **Formatter Boundary Confound**: The primary comparison (Condition A vs. Condition B) uses different input formatting boundaries (`apply_chat_template` vs. `training_aligned_v1`). Therefore, the +95.0% performance delta reflects the combined effect of format alignment and weight adaptation, rather than isolated weight fine-tuning.
2. **Synthetic Dataset & Benchmark Scope**: The 40 benchmark cases are synthetic scenarios. While modeled on authentic developer workflows, they do not capture the long-tail complexity, massive stack traces, and multi-file dependencies encountered in enterprise environments (Hou et al., 2024).
3. **Absence of Direct Schema Internalization Measurement**: Our experiments evaluate **behavioral token compliance** under greedy decoding. We did not perform internal mechanistic interpretability, probe attention heads, or measure internal representations. Consequently, we claim behavioral format conformance, not that the model has formally "internalized" the grammar.
4. **Heuristic Safety vs. Semantic Safety**: All 160 outputs passed automated heuristic safety filtering. However, regex-based scanning for destructive commands (e.g., `rm -rf`, `DROP DATABASE`) does not establish semantic safety or protect against subtle configuration regressions.
5. **Single-Annotator Qualitative Review**: Pending human evaluations reflect author-only scoring, which carries inherent subjective bias.
6. **Absence of Universal Reliability Guarantees**: While the adapted model achieved 97.5% schema compliance in Condition D, parameter-based adaptation provides empirical probability, not absolute mathematical guarantees of validity (contrasting with constrained decoding; Willard & Louf, 2023; Ugare et al., 2025).

---

## 10. Reproducibility & Open Artifact Availability

All code, evaluation harnesses, datasets, and execution manifests are preserved locally:
- **Evaluation Bundle**: [`dist/oopsie-eval-bundle-v1.2.0-four-conditions.zip`](file:///c:/Users/onyxe/Desktop/OOPSIE/dist/oopsie-eval-bundle-v1.2.0-four-conditions.zip)
- **Execution Archive**: [`artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz) (SHA-256: `dea688ab35b9cc42fd9cb4d913f07ea334599bce38a5aab94a9e67e59899e703`)
- **Raw Evaluation Records**: [`artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json`](file:///c:/Users/onyxe/Desktop/OOPSIE/artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json)
- **Audit Reports**: [`docs/research/benchmark_evaluation_report_v1.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/docs/research/benchmark_evaluation_report_v1.md)

*Public Availability Disclosure*: Base model weights (`google/gemma-4-12b-it`) are publicly available on Hugging Face under the Apache 2.0 license. Adapter weights and evaluation datasets are currently stored locally; public repository release readiness requirements are documented in the project release checklist.

---

## 11. Conclusion

This study demonstrated that QLoRA domain adaptation of `google/gemma-4-12b-it` enables a 12B-parameter foundation model to reliably generate complex 10-key JSON recovery plans under zero-tolerance parsing (achieving 95.0% to 97.5% strict schema conformance), whereas zero-shot and 1-shot in-context prompting of the base model fail entirely due to conversational prose and markdown wrappers. Furthermore, omitting the explicit JSON schema definition from the prompt reduced latency by 12.7% without degrading structural validity. However, domain adaptation remains an empirical steering mechanism rather than a mathematical guarantee; production deployments must maintain strict schema validation boundaries and human-in-the-loop oversight.

---

## 12. AI-Assistance Disclosure Placeholder

> [!NOTE] Author Disclosure Statement (For Author Review & Customization)
> *Placeholder*: In accordance with academic disclosure norms, the author notes that large language model assistants (e.g., Google DeepMind Antigravity / Gemini) were utilized during this investigation for code generation, harness scaffolding, syntactic refactoring, and initial drafting assistance. All experimental designs, protocol specifications, empirical verifications, forensic classifications, and final interpretations were directed and verified by the primary author (Onyx Prasai).

---

## 13. Bibliographic References

1. **[Hu et al., 2022]** Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., & Chen, W. (2022). *LoRA: Low-Rank Adaptation of Large Language Models*. International Conference on Learning Representations (ICLR 2022). Published conference paper. URL: [https://openreview.net/forum?id=nZeVKeeFYf9](https://openreview.net/forum?id=nZeVKeeFYf9).  
   *Claim Supported*: Low-rank parameter adaptation formulation ($W = W_0 + \frac{\alpha}{r}BA$) applied to transformer weight matrices (§1, §2.2, §4.2).

2. **[Dettmers et al., 2023]** Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). *QLoRA: Efficient Finetuning of Quantized LLMs*. Advances in Neural Information Processing Systems (NeurIPS 2023), Vol. 36, pp. 10088–10115. Published conference paper. URL: [https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html](https://proceedings.neurips.cc/paper_files/paper/2023/hash/1feb87871436031bdc0f2beaa62a049b-Abstract-Conference.html).  
   *Claim Supported*: 4-bit NormalFloat (NF4) base quantization with double quantization and compute-type casting enabling 12B model adaptation on 16 GB GPUs (§1, §2.2, §4.2).

3. **[Bray, 2017]** Bray, T. (Ed.). (2017). *The JavaScript Object Notation (JSON) Data Interchange Format*. Internet Engineering Task Force (IETF) Request for Comments (RFC 8259 / STD 90). Internet Standard. DOI: [10.17487/RFC8259](https://doi.org/10.17487/RFC8259).  
   *Claim Supported*: Defines strict RFC 8259 JSON syntax rules, token boundaries, and escape sequence restrictions. *Distinction*: RFC 8259 defines syntax only, not JSON Schema validation (§1, §2.1, §7.1).

4. **[Wright et al., 2022a]** Wright, A., Andrews, H., Hutton, B., & Dennis, G. (Eds.). (2022). *JSON Schema: A Media Type for Describing JSON Documents*. IETF Internet-Draft `draft-bhutton-json-schema-01` (Draft 2020-12 dialect, June 16, 2022). Intended status: Informational. URL: [https://json-schema.org/draft/2020-12/json-schema-core.html](https://json-schema.org/draft/2020-12/json-schema-core.html).  
   *Claim Supported*: Defines JSON Schema Draft 2020-12 core mechanics, meta-schemas, schema identification keywords (`$schema`, `$id`), and applicator keywords (`properties`, `additionalProperties`, `items`) (§1, §2.1, §3.1).

5. **[Wright et al., 2022b]** Wright, A., Andrews, H., & Hutton, B. (Eds.). (2022). *JSON Schema Validation: A Vocabulary for Structural Validation of JSON*. IETF Internet-Draft `draft-bhutton-json-schema-validation-01` (Draft 2020-12 dialect, June 16, 2022). Intended status: Informational. URL: [https://json-schema.org/draft/2020-12/json-schema-validation.html](https://json-schema.org/draft/2020-12/json-schema-validation.html).  
   *Claim Supported*: Defines structural validation assertion keywords used in `data/schema.json`, specifically `type`, `enum`, `required`, and `minLength` (§1, §2.1, §3.1).

6. **[Willard & Louf, 2023]** Willard, B. T., & Louf, R. (2023). *Efficient Guided Generation for Large Language Models*. arXiv preprint arXiv:2307.09702. Preprint. URL: [https://arxiv.org/abs/2307.09702](https://arxiv.org/abs/2307.09702).  
   *Claim Supported*: Finite-state machine and regex-guided constrained decoding algorithms; provides context on decoding-time masking vs. parameter adaptation (§1, §2.1, §9).

7. **[Ugare et al., 2025]** Ugare, S., Suresh, T., Kang, H., Misailovic, S., & Singh, G. (2025). *SynCode: LLM Generation with Grammar Augmentation*. Transactions on Machine Learning Research (TMLR), June 2025. ISSN: 2835-8856. Published journal paper. URL: [https://openreview.net/forum?id=7h8p3hB3q5](https://openreview.net/forum?id=7h8p3hB3q5).  
   *Claim Supported*: Context-free grammar-guided decoding via offline DFA mask stores and runtime parser masks; contrasts runtime engine requirements with parameter adaptation (§1, §2.1, §9).

8. **[Leinonen et al., 2023]** Leinonen, J., Hellas, A., Sarsa, S., Reeves, B., Denny, P., Prather, J., & Becker, B. A. (2023). *Using Large Language Models to Enhance Programming Error Messages*. Proceedings of the 54th ACM Technical Symposium on Computer Science Education (SIGCSE 2023), Vol. 1, pp. 452–458. Published conference paper. DOI: [10.1145/3545945.3569770](https://doi.org/10.1145/3545945.3569770).  
   *Claim Supported*: Empirical tendency of unadapted LLMs to produce conversational text and formatting variations when explaining programming error traces (§2.1).

9. **[Zhang et al., 2024]** Zhang, Q., Fang, C., Ma, Y., Sun, W., & Chen, Z. (2024). *A Survey of Learning-Based Automated Program Repair*. ACM Transactions on Software Engineering and Methodology (TOSEM), Vol. 33, No. 2, Article 39, pp. 1–45. Published journal paper. DOI: [10.1145/3631974](https://doi.org/10.1145/3631974).  
   *Claim Supported*: Formal taxonomy of Automated Program Repair (fault localization, patch generation, patch validation against test suites); establishes that OOPSIE is an advisory diagnostic engine rather than an APR system (§2.3).

10. **[Hou et al., 2024]** Hou, X., Zhao, Y., Liu, Y., Yang, Z., Wang, K., Li, L., Luo, X., Lo, D., Grundy, J., & Wang, H. (2024). *Large Language Models for Software Engineering: A Systematic Literature Review*. ACM Transactions on Software Engineering and Methodology (TOSEM). Published journal paper. DOI: [10.1145/3695988](https://doi.org/10.1145/3695988).  
    *Claim Supported*: Methodological analysis of synthetic software engineering benchmarks, data leakage risks, and threats to external validity (§3.2, §9).

11. **[Gemma Team, 2026]** Gemma Team (Google DeepMind). (2026). *Gemma 4 Technical Report*. arXiv preprint arXiv:2607.02770. Preprint / Technical Report. URL: [https://arxiv.org/abs/2607.02770](https://arxiv.org/abs/2607.02770).  
    *Claim Supported*: Base architecture specification for `google/gemma-4-12b-it` (unified decoder, ~11.95B dense parameters, hybrid local/global attention) (§4.1).

12. **[Google LLC, 2026]** Google LLC. (2026). *google/gemma-4-12B-it Model Card and Repository*. Hugging Face. Software repository / Model card. URL: [https://huggingface.co/google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it).  
    *Claim Supported*: Official license identification (Apache 2.0) governing the base checkpoint (§4.1, §10).
