# OOPSIE: Evaluating QLoRA Adaptation for Schema-Compliant Operational Failure Diagnostics

**Author**: Onyx Prasai  
**Contact**: `onyxprasai@gmail.com`  
**Institutional Affiliation**: Independent Researcher *(no institutional affiliation asserted)*  
**Manuscript Version**: Draft v1.5.0 (Pre-Submission Revision)  
**Date**: November 2026  

---

## Abstract

OOPSIE evaluates structured operational-failure diagnostics using a QLoRA adapter paired with an instruction-tuned language model. A frozen four-condition benchmark comprises 40 held-out synthetic failure scenarios and 160 generated responses. Under strict parsing of unmodified outputs, base-model configurations achieved 0/40 schema-conformant responses, while adapted configurations achieved 38/40 with schema guidance and 39/40 without schema text. A post-hoc fence-removal analysis recovered schema-conformant outputs from 40/40 base zero-shot responses and 39/40 base one-shot responses. These findings distinguish direct raw-output compliance from compliance after lightweight normalization and do not establish that adaptation is necessary or preferable to preprocessing. Adapter use also differed alongside input serialization, preventing isolation of the effect of adapter weights. All 160 responses received AI-generated provisional qualitative ratings. The author documented review of 16 flagged responses without changing their ratings; the remaining 144 ratings were adopted without documented case-level review. These exploratory ratings did not establish a diagnostic-quality advantage for adapted configurations. Constrained-decoding baselines were not evaluated. The study motivates controlled comparisons of prompting, normalization, constrained decoding, and adaptation, with schema validation and human oversight required for downstream use.

**Keywords**: Large Language Models, Structured Output Generation, JSON Schema, QLoRA, Operational Error Recovery, Diagnostic Reasoning, Developer Tools, Empirical Software Engineering.

---

## 1. Introduction

When automated builds, CI/CD pipelines, container runtimes, or deployment orchestrators encounter unhandled exceptions, human developers and automated healing agents require three immediate diagnostic deliverables:
1. **Accurate Failure Domain Identification**: Rapid classification of the failure category (e.g., authentication, environment variable misconfiguration, peer dependency conflict).
2. **Safe, Well-Scoped Remediation**: A minimal, non-destructive remediation procedure that avoids overbroad commands.
3. **Sound Verification Procedures**: Concrete, executable verification steps to confirm whether the fix resolved the underlying fault without introducing collateral regressions.

Modern instruction-tuned foundation language models possess extensive parametric knowledge regarding software engineering and debugging, as demonstrated on code generation benchmarks such as HumanEval (Chen et al., 2021) and repository-level issue resolution benchmarks such as SWE-bench (Jimenez et al., 2024). However, deploying general-purpose chat models as programmatic middleware in automated toolchains presents severe operational challenges. Under standard greedy decoding, unadapted chat models frequently emit conversational pleasantries (*"Certainly, here is the explanation..."*), enclose JSON payloads in Markdown code fences (` ```json ... ``` `), or introduce syntactic defects (such as illegal escape sequences). When downstream tooling enforces zero-tolerance RFC 8259 JSON validation (Bray, 2017) and rigid schema conformance (JSON Schema Draft 2020-12; Wright et al., 2022a, 2022b), these formatting deviations cause immediate automated ingestion failure.

Prior work has addressed output structuring primarily through decoding-time grammar constraints, such as finite-state automata (FSM) guidance (Willard & Louf, 2023) or context-free grammar (CFG) token masking (Ugare et al., 2025). While decoding-time masking guarantees syntax correctness, it imposes non-trivial serving requirements, custom runtime dependencies, and token-level vocabulary masking overhead. An alternative approach is parameter-efficient fine-tuning (PEFT), such as Low-Rank Adaptation (LoRA; Hu et al., 2022) and Quantized Low-Rank Adaptation (QLoRA; Dettmers et al., 2023), which internalizes formatting and task conventions directly into the model's weights.

In this work, we present **OOPSIE** (Operational Output Parser & Structured Inference Engine), an open evaluation framework designed to address the following research question:
> *Does QLoRA adaptation improve structured JSON/schema compliance for operational-failure diagnostic reporting, and does it improve qualitative diagnostic reasoning?*

We evaluate this question on a pre-specified, frozen benchmark comprising 40 diverse, held-out software and infrastructure failure scenarios (160 total model completions across four experimental conditions). Our empirical results demonstrate that QLoRA adaptation dramatically improves direct raw JSON schema compliance from 0.0% to 95.0%--97.5% under zero-tolerance greedy parsing ($p \approx 7.28 \times 10^{-12}$). However, a post-hoc analysis reveals that base-model failure was predominantly an outer framing issue: stripping code fences recovered 100.0% (40/40) schema compliance in zero-shot base inference. Furthermore, a systematic qualitative evaluation reveals that domain adaptation confers **no observable advantage in diagnostic reasoning or technical correctness** over the unadapted base model.

---

## 2. Related Work

### 2.1 Structured Generation in Foundation Models
Enforcing structured outputs from autoregressive language models is critical for tool use and workflow orchestration. Constrained decoding approaches such as Outlines (Willard & Louf, 2023) index regular expressions or JSON schemas into deterministic finite automata (DFAs) that mask invalid next-token candidates at each generation step. SynCode (Ugare et al., 2025) generalizes this to context-free grammars (CFGs). In educational and developer error explanation tasks, Leinonen et al. (2023) observed that while LLMs provide helpful diagnostic hints, unadapted models frequently introduce conversational formatting and preamble artifacts that prevent automated programmatic ingestion.

### 2.2 Parameter-Efficient Fine-Tuning
Low-Rank Adaptation (LoRA; Hu et al., 2022) parameterizes weight updates via low-rank decomposition matrices ($W = W_0 + \frac{\alpha}{r}BA$). QLoRA (Dettmers et al., 2023) combines 4-bit NormalFloat (NF4) base quantization with double quantization and compute-type casting, allowing 12B+ parameter models to be adapted on single commodity GPUs. While PEFT has been evaluated on code generation and general NLP benchmarks (Rozière et al., 2023; Li et al., 2023), its efficacy at inducing rigid multi-key JSON schemas under zero-tolerance parsing without grammar masking remains sparsely benchmarked.

### 2.3 Automated Program Repair and Fault Diagnosis
Automated Program Repair (APR) traditionally encompasses fault localization, patch synthesis, and patch validation against test suites (Zhang et al., 2024). As surveyed by Hou et al. (2024), foundation models excel at synthesizing candidate patches but risk benchmark leakage when evaluated on popular public repositories. OOPSIE is designed not as an autonomous repair agent, but as an advisory operational diagnostic parser that translates unstructured system logs (Kent & Souppaya, 2006) into strictly validated machine-readable incident structures.

---

## 3. Method

### 3.1 Canonical Diagnostic Schema
OOPSIE targets a standardized operational diagnostic schema formalized in `data/schema.json` (LF SHA-256: `ce322859f8...`; CRLF SHA-256: `40550bfef0...`) under JSON Schema Draft 2020-12 (Wright et al., 2022a, 2022b). Every output must parse as a single JSON object with no additional properties (`additionalProperties: false`). Ten keys are required:
1. `summary`: Non-empty string.
2. `plain_explanation`: Non-empty string.
3. `error_category`: Closed vocabulary enum of 14 values (`dependency`, `configuration`, `environment_variables`, `database`, `authentication`, `authorization`, `network`, `build`, `deployment`, `runtime`, `typescript`, `frontend`, `other`, `unknown`).
4. `likely_causes`: Array of objects with required `description` (non-empty string) and `confidence` (`low`, `medium`, or `high`); no additional properties.
5. `missing_context_questions`: Array of strings.
6. `risk_level`: Enum of three values (`low`, `medium`, `high`).
7. `warnings`: Array of strings.
8. `repair_prompt`: Non-empty string.
9. `verification_steps`: Array of strings.
10. `matched_recipes`: Array of objects with required `id` and `title` (strings) and optional `path`; no additional properties.

*Historical Schema Note*: Earlier internal design drafts described an alternative schema layout containing fields such as `schema_version`, `root_cause`, and `suggested_fix`. The frozen benchmark and all 160 evaluation passes were executed exclusively against the canonical specification above, stored in `data/schema.json`.

### 3.2 Training Corpus and Data Governance
The training dataset comprises synthetic scenarios drawn from real-world error patterns across web development, backend databases, cloud infrastructure, container orchestration, and related domains. Each scenario was paired with a 10-key JSON reference payload constructed by the author following the canonical schema. All manifest records carry `source_type: synthetic`. The corpus was partitioned into **85 training examples, 18 validation examples, and 17 test examples** (120 total curated records). All 40 benchmark scenarios were strictly isolated and held out from all training and hyperparameter tuning.

### 3.3 Model Architecture and QLoRA Adaptation
We configured a QLoRA adapter ($r=16, \alpha=32$, dropout $0.05$) on top of the public instruction-tuned foundation model `google/gemma-4-12B-it` (dense ~11.95B parameters; Gemma Team, 2026; Google LLC, 2026).* The base model was loaded in 4-bit NormalFloat (NF4) with 16-bit bfloat compute dtype and double quantization. Trainable low-rank decomposition matrices were attached across all linear projections in the self-attention and MLP blocks:
$$W = W_0 + \frac{\alpha}{r}BA, \quad r = 16, \quad \alpha = 32$$

Target modules in the training configuration include attention projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`) and feed-forward projections (`gate_proj`, `up_proj`, `down_proj`). Inspection of the saved checkpoint tensor dictionary (`adapter_model.safetensors`) confirms 656 adapter weight tensors totaling 65,568,768 parameters ($65.57\times 10^6$) across all 48 transformer layers. Relative to the ~11.95B base model, this represents approximately 0.55% of base parameters. Earlier draft claims of 42.6M parameters (0.35%) arose from an incomplete estimate omitting Gemma 4's expanded intermediate dimensions and hybrid attention projection ranks.

The training configuration specified 3 epochs with per-device batch size 1 and 4 gradient accumulation steps (effective batch size 4), AdamW optimization, cosine learning rate scheduling ($2 \times 10^{-4}$ peak), and sequence length 1,536 tokens on an NVIDIA Tesla T4 GPU (14.56 GB allocated VRAM, Kaggle free tier). The evaluation checkpoint corresponds to the saved Step 44 checkpoint (`oopsie-pilot-adapter`) associated with Epoch 2 validation tracking. Execution was managed within an interactive notebook environment without independent training-loss log retention; claims of global checkpoint optimality or exact executed step counts are therefore constrained to the saved configuration and checkpoint artifacts.

*\*Provenance Note on Model Identifier*: The official public Hugging Face repository identifier is `google/gemma-4-12B-it`. Historical training run configuration files (`run_config.json` and `adapter_config.json`) in this repository recorded the lowercase identifier `google/gemma-4-12b-it`; both identifiers resolve to the identical model checkpoint on Hugging Face.

---

## 4. Experimental Setup

### 4.1 Four Experimental Conditions
To evaluate the effect of QLoRA adaptation on schema compliance and qualitative diagnostic performance, we tested four conditions across all 40 held-out benchmark scenarios:
- **Condition A (Base Zero-Shot + Schema)**: Unadapted base model with full ~710-token JSON schema embedded in the system prompt.
- **Condition B (Adapted + Schema)**: QLoRA adapted model with full JSON schema in the system prompt.
- **Condition C (Base One-Shot + Schema)**: Unadapted base model with full JSON schema and one complete gold-standard input/output demonstration in context.
- **Condition D (Adapted No-Schema)**: QLoRA adapted model with minimal task prompt, completely omitting the schema text.

**Critical Methodological Confound**: Condition A and Condition B differ in both adapter weights *and* chat-template formatter. Condition A applies the official Gemma instruction-tuned chat template (`apply_chat_template`, `add_generation_prompt=True`); Condition B applies a training-aligned formatter (`add_generation_prompt=False` + `<|turn>model\n` suffix). This comparison therefore evaluates *configured end-to-end systems* under identical prompt text, not an isolated weight-only ablation. The relative contribution of adapter weights versus chat-template format difference cannot be determined from this design. This confound is disclosed explicitly in the frozen evaluation protocol (§9.1 of `OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`).

### 4.2 Decoding Parameters and Ingestion Pipeline
All 160 completions were generated using greedy decoding (`temperature = 0.0`, `top_p = 1.0`, `max_new_tokens = 1024`) to ensure deterministic reproducibility. Programmatic evaluation employs a zero-tolerance ingestion pipeline:
1. **Raw JSON Parse**: `json.loads(output)` without Markdown fence stripping or regex extraction.
2. **Lenient JSON Parse**: Extraction after stripping leading/trailing whitespace and Markdown code fences (` ```json ... ``` `).
3. **Strict Schema Validation**: Formal JSON Schema Draft 2020-12 validation against `data/schema.json`.
4. **Key Completeness**: Verification that all 10 canonical keys are present and no unexpected keys exist.

### 4.3 Qualitative Evaluation Protocol and Documented Review Coverage
To evaluate diagnostic reasoning independently of programmatic syntax checks, qualitative ratings were analyzed across five dimensions: Technical Correctness, Root Cause Accuracy, Fix Actionability, Safety Appropriateness, and Repair Prompt Utility.

**Documented Review Provenance and Workflow Boundaries**:
1. **Initial AI Rating Generation**: All 160 completions across the 40 benchmark scenarios and four experimental conditions were initially rated using an automated AI-assisted evaluation pipeline applying the frozen rubric.
2. **Preparation for Concealed Presentation**: All 160 completions were formatted into eight batch review documents (`batch_01.md` through `batch_08.md`) with randomized condition labels (`System Alpha`, `Beta`, `Gamma`, `Delta`). The first 10 benchmark scenarios (Batches 1--2, comprising 40 completions) were specifically staged for blinded human review.
3. **Documented Author Review**: Rather than conducting de novo blind scoring of all completions, author review focused on evaluating an explicit triage checklist and author decision sheet (`author_decision_sheet.md`). This decision sheet documented author inspection of 16 flagged evaluation entries (involving category boundary disputes such as authentication versus authorization, emulator test advice, syntax malformations, or controversial workaround flags like `--legacy-peer-deps`).
4. **Overlap and Adoption**: Of the 16 flagged entries subjected to documented author review, exactly 1 overlapped with Batches 1--2 (case `bench-authentication-03`, Beta); the other 15 belonged to Batches 3--8. For all 16 flagged cases, the author retained the provisional rating. The remaining 144 evaluations were adopted into the snapshot manifest without case-level human inspection.
5. **Absence of Inter-Rater Reliability**: No secondary independent human annotator scored the completions; consequently, no Cohen's $\kappa$, Krippendorff's $\alpha$, or inter-rater reliability statistic was calculated.

These qualitative results represent author-adopted AI-assisted ratings and must be interpreted as exploratory observations rather than an independently verified human evaluation.

### 4.4 Relationship to Constrained Decoding and JSON Mode
This study did not evaluate constrained-decoding baselines, provider JSON modes, or grammar-guided decoding. Therefore, the results do not establish that QLoRA adaptation is necessary or preferable to constrained decoding for achieving schema compliance. Specifically, the following approaches were not evaluated:
- **Grammar-constrained decoding** (e.g., FSM/CFG masking as in Outlines or SynCode).
- **Provider JSON modes** (inference-time JSON enforcement offered by hosted model providers).
- **Negative-prompting baselines** (e.g., system-prompt instructions such as *"Output raw JSON only, no markdown, no preamble"*). All conditions shared a base system prompt containing the directive *"Return only one JSON object conforming to data/schema.json"*; however, this directive omitted explicit anti-markdown or anti-preamble instructions. A pure no-directive baseline was therefore not evaluated.

The evaluation scope was restricted to parameter adaptation versus standard prompt-only baselines using identical inference infrastructure, without integration of constrained-decoding runtime engines. Future work should compare QLoRA adaptation against constrained-decoding approaches, JSON-mode decoding, and prompt-only formatting controls to determine whether adaptation is necessary or merely one of several viable paths to structural compliance.

---

## 5. Results

### 5.1 Programmatic Parsing and Schema Compliance

| Condition | Raw JSON | Lenient JSON | Strict Schema | Key Compl. | Latency (s) | Fail Reason |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **A: Base Zero-Shot + Schema** | 0/40 (0.0%) | 40/40 (100.0%) | 0/40 (0.0%) | 0/40 (0.0%) | $118.62 \pm 12.73$ | Markdown fences / preambles |
| **B: Adapted + Schema** | 38/40 (95.0%) | 38/40 (95.0%) | 38/40 (95.0%) | 38/40 (95.0%) | $114.42 \pm 11.53$ | Incomplete/syntax defects (2 runs) |
| **C: Base One-Shot + Schema** | 0/40 (0.0%) | 39/40 (97.5%) | 0/40 (0.0%) | 0/40 (0.0%) | $119.35 \pm 9.79$ | Markdown fences / syntax defect |
| **D: Adapted No-Schema** | 40/40 (100.0%) | 40/40 (100.0%) | 39/40 (97.5%) | 39/40 (97.5%) | $99.88 \pm 11.93$ | Missing 1 key (1 run) |

*Table 1: Programmatic parsing and schema compliance results across 40 held-out scenarios (160 total passes). Lenient JSON reflects parser output after removing Markdown code fences. Latency denotes single sequential execution time on an NVIDIA Tesla T4 GPU (mean $\pm$ standard deviation).*

Unadapted base models (Conditions A and C) achieved 0.0% raw JSON parsing and 0.0% strict schema compliance under the primary zero-tolerance protocol. In all failure cases, the raw model emission was enclosed in Markdown code blocks (` ```json ... ``` `) or conversational introductory formatting.

#### Post-Hoc Lenient Extraction Analysis
To evaluate whether base-model non-compliance was exclusively a superficial delimiter framing failure, we parsed and validated outputs after stripping Markdown code fences:
- **Condition A (Base Zero-Shot)**: 40/40 (100.0%) parsed as valid JSON and 40/40 (100.0%) fully satisfied the strict JSON schema, confirming all 10 canonical keys, enum constraints, and type requirements were met once framing delimiters were removed.
- **Condition C (Base One-Shot)**: 39/40 (97.5%) parsed as valid JSON and passed strict schema validation. The single failure (`bench-nextjs-03`) contained an internal syntax defect (a missing opening quote on a key name: `_explanation"`), preventing JSON parsing even after fence stripping.

*Correction Notice on Condition C Lenient Parsing*: Earlier project summaries and draft tables incorrectly listed Condition C lenient parsing as 40/40 (100.0%). A forensic audit of the frozen benchmark execution records confirmed that the raw completion for `bench-nextjs-03` omitted the leading quote and identifier for `"plain_explanation"`, causing a `JSONDecodeError` on line 3 column 3 upon parsing. The underlying frozen benchmark results remain unaltered; the corrected count of 39/40 (97.5%) is reported here.

This post-hoc analysis demonstrates that unadapted base models under greedy decoding possessed the latent structural ability to generate schema-compliant diagnostic payloads, but failed the operational pipeline entirely due to enclosing delimiters.

Conversely, QLoRA adaptation eliminated Markdown code fences and preambles from direct emission: Condition B achieved 95.0% (38/40) raw and strict schema compliance, while Condition D achieved 100.0% raw JSON parsing and 97.5% (39/40) strict schema compliance directly out of the model. The two Condition B failures (`bench-firebase-01` and `bench-nextjs-01`) contained invalid backslash escape sequences in their raw JSON output — not framing delimiters — and therefore were not recoverable by fence removal. The single Condition D failure (`bench-npm-03`) produced valid JSON but omitted the required `matched_recipes` key while including all other required keys. These four cases (Cond B ×2, Cond C ×1, Cond D ×1) are the failures *remaining after normalization*, not the only raw-output failures (Conditions A and C each produced 40 raw-output failures, all due to Markdown framing).

### 5.2 Inferential Statistical Significance
To test whether the observed improvement in direct raw schema compliance is statistically significant, we construct the paired $2 \times 2$ contingency table across the 40 scenarios for Condition A vs. Condition B:
- Both Pass: 0 ($a$)
- Condition A Pass, Condition B Fail: 0 ($b$)
- Condition A Fail, Condition B Pass: 38 ($c$)
- Both Fail: 2 ($d$)

The contingency table yields 38 discordant pairs ($b=0, c=38$). Under the exact two-sided McNemar test with null hypothesis $H_0: P(b) = P(c) = 0.5$:
$$p = 2 \times (0.5)^{38} \approx 7.276 \times 10^{-12}$$
The Edwards continuity-corrected chi-square statistic is:
$$\chi^{2}_{\text{corrected}} = \frac{(|0 - 38| - 1)^2}{38} = \frac{37^2}{38} \approx 36.0263$$
yielding $p \approx 1.947 \times 10^{-9}$ ($df=1$).

*Statistical Scope and Limitations*: This significance claim pertains strictly to direct programmatic schema compliance under zero-tolerance greedy parsing on the 40 paired benchmark scenarios. It does not measure, imply, or support any claim of superiority in underlying technical diagnostic correctness.

### 5.3 Inference Latency Profile
Omitting the explicit schema text from the prompt (Condition D) yielded an observed mean single-run latency reduction of 14.54 seconds (-12.7%) compared to Condition B ($99.88 \pm 11.93$ s vs. $114.42 \pm 11.53$ s). Latency was measured during a single sequential run on an isolated NVIDIA Tesla T4 GPU with batch size 1 and unpadded inputs; this latency profile is reported as an operational observation of prompt-length savings rather than a general hardware benchmark guarantee.

### 5.4 Qualitative Diagnostic Reasoning Review

| Dimension | Condition A (Base) | Condition B (Adapted) | Condition C (1-Shot) | Condition D (No-Schema) |
| :--- | :---: | :---: | :---: | :---: |
| **Technical Correctness** | 37 Pass / 3 Partial / 0 Fail | 37 Pass / 3 Partial / 0 Fail | 40 Pass / 0 Partial / 0 Fail | 37 Pass / 3 Partial / 0 Fail |
| **Root Cause Accuracy** | 38 Pass / 2 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail | 40 Pass / 0 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail |
| **Fix Actionability** | 38 Pass / 2 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail | 40 Pass / 0 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail |
| **Safety Appropriateness** | 40 Pass / 0 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail | 40 Pass / 0 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail |
| **Repair Prompt Utility** | 39 Pass / 1 Partial / 0 Fail | 38 Pass / 2 Partial / 0 Fail | 40 Pass / 0 Partial / 0 Fail | 37 Pass / 3 Partial / 0 Fail |

*Table 2: Systematic qualitative evaluation across all 160 completions (40 scenarios $\times$ 4 conditions). Rating provenance: All 160 ratings were generated by an automated AI evaluation pipeline; 40 were prepared for concealed review, and 16 flagged edge cases received documented author review before ratings were adopted without case-level re-annotation. No inter-rater reliability statistic was computed.*

Qualitative diagnostic ratings were similar across unadapted and adapted models:
- Across all 160 completions, zero completions received a **Fail**, **Severe Risk**, or **Cannot Assess** rating.
- Condition C (Base 1-Shot) was rated 40/40 Pass on technical correctness and root cause accuracy, whereas Conditions B and D were each rated 37/40 Pass and 3/40 Partial.
- In the Partial cases, diagnostic discrepancies (e.g., categorizing an authorization failure as authentication, or misattributing an expired SSL certificate to an intermediate authority) were observed across both base and adapted completions without a clear separation in technical reasoning depth.

---

## 6. Discussion

### 6.1 Raw Direct Emission vs. Superficial Delimiter Framing
A key finding of this investigation is that the 0.0% strict schema compliance observed in unadapted base models under zero-tolerance parsing was primarily a superficial delimiter framing failure. The base model `google/gemma-4-12B-it` already possesses comprehensive parametric domain knowledge regarding software faults, and our post-hoc lenient extraction demonstrated that 40/40 (100.0%) zero-shot base completions and 39/40 (97.5%) one-shot completions were fully compliant with the canonical JSON schema once outer Markdown code fences were removed.

QLoRA adaptation altered this behavior by eliminating outer Markdown code fences and conversational preambles directly from raw generation, achieving 95.0%--97.5% compliance directly out of the model without post-processing. However, because Condition A and Condition B differ in both adapter weights and chat-template formatting boundaries (the official Gemma template versus the training-aligned `<|turn>model` boundary), this structural change cannot be causally isolated to weight adaptation alone. Furthermore, because removing Markdown code fences achieves 100.0% schema compliance in base zero-shot inference, QLoRA adaptation cannot be concluded to be necessary or intrinsically superior to simple string post-processing or constrained decoding.

### 6.2 Prompt Compaction and Schema Omission
Condition D demonstrates that the adapted model reliably produces the 10-key schema structure even when the schema definition is completely omitted from the prompt, reducing prompt context length by ~710 tokens and cutting end-to-end execution latency by 12.7% without degrading schema compliance (97.5%). This indicates that the structural property names and types are reliably reproduced from model parameters.

### 6.3 Operational Safety Implications
Because parameter adaptation does not enhance underlying diagnostic reasoning, it must not be treated as a substitute for validation. Organizations adopting PEFT models for automated operational pipelines must implement strict validation boundaries:
1. **Syntactic and Schema Gate**: Automatic validation against the formal JSON schema before downstream consumption.
2. **Human-in-the-Loop Gate**: Requiring explicit developer review before executing suggested fixes or repair prompts in production environments.

---

## 7. Limitations

We explicitly document the threats to validity and limitations of this study:
1. **Sample Size**: The benchmark contains 40 curated scenarios. While statistically significant for structural parsing ($p < 10^{-11}$), larger corpora are needed to detect subtle qualitative shifts.
2. **Evaluator Scope and Review Coverage**: Initial qualitative rubric ratings across all 160 completions were generated by an automated AI evaluation pipeline. Forty completions (the first 10 scenarios across four conditions) were staged in blinded batches, and 16 flagged edge cases received documented author review via a decision sheet before ratings were adopted without case-level human re-annotation. No Cohen's $\kappa$, Krippendorff's $\alpha$, or multi-rater inter-coder reliability metrics were computed. Furthermore, because base-model completions were framed by Markdown backticks while adapted completions were bare JSON, subtle surface differences may have partially compromised human blinding.
3. **Adapter and Template Confound**: As detailed in Section 4.1, Conditions A and B differ in both adapter weights and chat-template formatting boundary (official Gemma template vs. training-aligned `<|turn>model` boundary). Performance differences reflect the configured systems rather than isolated weight effects.
4. **Synthetic Contexts**: Scenarios were synthetically generated error patterns representing common web and infrastructure failures, evaluated as static isolated logs rather than live interactive environments.
5. **Model and Task Specificity**: Findings are specific to `google/gemma-4-12B-it` and the OOPSIE 10-key schema; generalization to other foundation models or schemas requires empirical verification.
6. **No Constrained-Decoding or JSON-Mode Baselines**: This study did not evaluate grammar-constrained decoding, provider JSON modes, FSM/CFG token masking, or negative-prompting controls. The results do not establish whether QLoRA adaptation is necessary or preferable to these alternatives for achieving schema compliance.

---

## 8. Ethics and Safety

Automating system error remediation presents inherent operational risks. Flawed diagnostic suggestions could lead to catastrophic downtime, data loss, or security vulnerabilities (e.g., executing destructive shell commands or disabling security controls). OOPSIE outputs are strictly advisory; all repair prompts and suggested fixes must be validated by human engineers.

---

## 9. Conclusion

This study investigated whether parameter-efficient fine-tuning via QLoRA can improve structural JSON schema compliance for operational software error recovery, and whether it alters underlying diagnostic reasoning. In a pre-specified frozen benchmark across 40 unseen failure scenarios (160 total passes), QLoRA adaptation of `google/gemma-4-12B-it` improved direct raw JSON schema compliance from 0.0% in unadapted base-model conditions to 95.0%--97.5% under zero-tolerance greedy parsing ($p \approx 7.28 \times 10^{-12}$), eliminating conversational preambles and Markdown code fences. Crucially, a post-hoc analysis revealed that unadapted base-model non-compliance was overwhelmingly a surface formatting issue: removing outer Markdown code fences recovered 100.0% (40/40) schema compliance in zero-shot base inference and 97.5% (39/40) in one-shot base inference.

Furthermore, qualitative diagnostic evaluation across all 160 completions did not demonstrate a diagnostic-reasoning or technical-correctness advantage for adapted conditions over the unadapted base model. Within the evaluated configurations, QLoRA adaptation functioned as an effective formatting mechanism for direct raw emission, but adaptation was not causally isolated from chat-template conventions and was not demonstrated to be necessary relative to fence stripping or constrained decoding. Operational software diagnostic pipelines can utilize QLoRA for automated direct JSON formatting, but must maintain rigorous programmatic schema validation gates and mandatory human developer oversight.

---

## AI Use Disclosure

The author used AI-assisted tools during research and manuscript preparation. Initial qualitative ratings for the 160 benchmark completions were generated by an automated evaluation pipeline using a frozen rubric. The author reviewed key outputs, verification findings, and flagged evaluations, and takes full responsibility for the final work. The remaining provisional qualitative ratings were retained without case-by-case author review and are reported as author-adopted AI-assisted evaluations. These ratings are not independent human inter-rater assessments. AI tools were also used to assist with code development, documentation, manuscript drafting, and consistency checking.

---

## References

- Bray, T. (2017). *The JavaScript Object Notation (JSON) Data Interchange Format*. RFC 8259, Internet Engineering Task Force.
- Chen, M., Tworek, J., Jun, H., et al. (2021). Evaluating large language models trained on code. *arXiv preprint arXiv:2107.03374*.
- Dettmers, T., Pagnoni, A., Holtzman, A., & Zettlemoyer, L. (2023). QLoRA: Efficient finetuning of quantized LLMs. *Advances in Neural Information Processing Systems (NeurIPS)*, 36, 10088–10115.
- Gemma Team. (2026). Gemma 4 Technical Report. *arXiv preprint arXiv:2607.02770*.
- Google LLC. (2026). *google/gemma-4-12B-it Model Card and Repository*. Hugging Face.
- Hou, X., Zhao, Y., Liu, Y., et al. (2024). Large language models for software engineering: A systematic literature review. *ACM Transactions on Software Engineering and Methodology (TOSEM)*.
- Hu, E. J., Shen, Y., Wallis, P., et al. (2022). LoRA: Low-rank adaptation of large language models. *International Conference on Learning Representations (ICLR)*.
- Jimenez, C. E., Yang, J., Wettig, A., et al. (2024). SWE-bench: Can language models resolve real-world GitHub issues? *International Conference on Learning Representations (ICLR)*.
- Kent, K., & Souppaya, M. (2006). *Guide to Computer Security Log Management*. NIST Special Publication 800-92.
- Leinonen, J., Hellas, A., Sarsa, S., et al. (2023). Using large language models to enhance programming error messages. *Proceedings of the 54th ACM Technical Symposium on Computer Science Education (SIGCSE)*, 452–458.
- Li, R., Ben Allal, L., Zi, Y., et al. (2023). StarCoder: may the source be with you! *arXiv preprint arXiv:2305.06161*.
- Rozière, B., Gehring, J., Gloeckle, F., et al. (2023). Code Llama: Open foundation models for code. *arXiv preprint arXiv:2308.12950*.
- Ugare, S., Suresh, T., Kang, H., Misailovic, S., & Singh, G. (2025). SynCode: LLM generation with grammar augmentation. *Transactions on Machine Learning Research (TMLR)*.
- Willard, B. T., & Louf, R. (2023). Efficient guided generation for large language models. *arXiv preprint arXiv:2307.09702*.
- Wright, A., Andrews, H., Hutton, B., & Dennis, G. (2022a). *JSON Schema: A Media Type for Describing JSON Documents*. Internet-Draft draft-bhutton-json-schema-01.
- Wright, A., Andrews, H., & Hutton, B. (2022b). *JSON Schema Validation: A Vocabulary for Structural Validation of JSON*. Internet-Draft draft-bhutton-json-schema-validation-01.
- Zhang, Q., Fang, C., Ma, Y., Sun, W., & Chen, Z. (2024). A survey of learning-based automated program repair. *ACM Transactions on Software Engineering and Methodology (TOSEM)*, 33(2), 39:1–39:45.
