# OOPSIE Pilot Model Card: QLoRA Domain Adaptation of Gemma 4 12B

**Model Name**: `oopsie-pilot-adapter`  
**Base Model**: `google/gemma-4-12b-it` (instruction-tuned Gemma 4, ~11.95 billion dense parameters; Gemma Team, 2026)  
**Adapter Architecture**: 4-bit NormalFloat (NF4) Quantized Low-Rank Adaptation (QLoRA; Dettmers et al., 2023)  
**LoRA Hyperparameters**: Rank $r = 16$, Alpha $\alpha = 32$, Dropout = 0.05, Target Modules: all linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`)  
**Training Checkpoint**: Step 44, Epoch 2 (selected via validation loss minimum on `data/validation.jsonl`)  
**License**: Base model licensed under Apache 2.0 (Google LLC, 2026); OOPSIE adapter configuration and documentation licensed under Apache 2.0.

---

## 1. Summary & Intended Use

OOPSIE (Operational Output Parser & Structured Inference Engine) is an open-source research prototype designed to investigate structured JSON generation for developer error diagnostics without requiring grammar-constrained decoding passes.

- **Intended Purpose**: An advisory diagnostic prototype that converts raw build exceptions, runtime failures, and deployment error logs into RFC 8259-compliant JSON matching the 10-key canonical schema (`data/schema.json`, JSON Schema Draft 2020-12).
- **Intended Users**: Software engineering researchers and developers evaluating structured generation, error diagnostic modeling, and parameter-efficient fine-tuning.
- **Not a Production Diagnostic System**: This checkpoint is a **research artifact**, not a validated production diagnostic or automated remediation system. It does not provide guarantees of correctness, complete bug fixes, or operational safety.

---

## 2. Out-of-Scope and Prohibited Uses

- **Automated Program Repair (APR)**: OOPSIE is explicitly **not** an APR system. It must not be deployed to automatically edit codebases, execute shell commands, mutate repositories, or trigger automated deployments without human review.
- **High-Stakes or Unmonitored Environments**: Must not replace human code review, security audits, financial validation, or infrastructure safety checks.
- **Unsanitized Log Processing**: Logs may contain API keys, access tokens, or sensitive credentials. While best-effort regex redaction is provided, users must sanitize inputs prior to inference.

---

## 3. Training Data Summary

- **Dataset Lineage**: 160 multi-turn developer error scenarios partitioned into disjoint splits:
  - **Training Set (`data/train.jsonl`)**: 85 records (SHA-256: `be401b7f...`)
  - **Validation Set (`data/validation.jsonl`)**: 18 records (SHA-256: `34cc646f...`)
  - **Independent Test Set (`data/test.jsonl`)**: 17 records (SHA-256: `c4b2d10d...`)
  - **Held-Out Final Benchmark (`evaluation/benchmark.jsonl`)**: 40 records (SHA-256: `1676a9bcb9160bd142483cb868b4b652c21e93ef9f29e48f56786312c4a942dd`)
- **Data Character**: Scenarios were synthetically generated using structured prompt templates covering common JavaScript/TypeScript, Python, Docker, Next.js, Firebase, and Supabase workflows.
- **Review Status**: Raw records carry `review.status = "unreviewed"` and must not be treated as human-verified ground truth.

---

## 4. Benchmark Evaluation & Empirical Findings

The model was evaluated under a frozen four-condition benchmark (`OOPSIE-EVAL-PROTOCOL-v1.2.0-frozen`) across 40 unseen held-out failure scenarios (160 forward passes under deterministic greedy decoding, $T=0.0$, budget 1024 tokens):

### Programmatic Output Conformance ($N = 40$ per condition)

| Condition | Raw RFC 8259 JSON Valid | Strict JSON Schema Conformance | Mean Latency per Case |
|---|:---:|:---:|:---:|
| **Condition A** (Base Zero-Shot + Schema) | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 118.62 s |
| **Condition B** (Adapter Zero-Shot + Schema) | **38 / 40 (95.0%)** | **38 / 40 (95.0%)** | 114.42 s |
| **Condition C** (Base 1-Shot Exemplar + Schema) | 0 / 40 (0.0%) | 0 / 40 (0.0%) | 119.35 s |
| **Condition D** (Adapter Service Prompt, No Schema) | **40 / 40 (100.0%)** | **39 / 40 (97.5%)** | **99.88 s** |

- **Statistical Significance**: The improvement in programmatic schema compliance between Condition A and Condition B is statistically significant (exact paired McNemar test $p \approx 7.28 \times 10^{-12}$; Edwards continuity-corrected $\chi^2 = 36.03, p \approx 1.95 \times 10^{-9}$).
- **Latency Advantage**: Omitting the JSON schema from the runtime prompt (Condition D) reduced mean latency by 14.54 seconds (-12.7%) while maintaining 97.5% strict schema validity.

### Qualitative Technical Substance ($N = 40$ per condition, $N = 160$ total)

Qualitative diagnostic soundness was evaluated across all 160 completions using a frozen 5-dimension rubric:
- **Assessability Gate**: All 160 responses (100.0%) contained assessable technical content; zero responses were unassessable.
- **No Severe Failures**: Across all five scored dimensions, **no response received `Fail (Incorrect)`**, `Severe` hallucination, `Fail (Unsound)` verification, or `Cannot Assess`.
- **Technical Correctness**: Condition C achieved 40/40 (100.0%) Pass; Condition A achieved 39/40 (97.5%) Pass and 1/40 Partial; Conditions B and D each achieved 37/40 (92.5%) Pass and 3/40 Partial.
- **Repair Scope & Verification**: Conditions B and D each had one `Harmful / Overbroad` repair rating and one `Incomplete` verification rating on `bench-npm-02` (recommending `npm install --legacy-peer-deps`). Condition B had the only `Overconfident` uncertainty rating (`bench-react-02`).

### Qualitative Review Provenance & Limitations
- **Author-Adopted Review**: Initial ratings were generated provisionally by an automated evaluation pipeline using the frozen rubric. The author systematically reviewed flagged cases on the verification checklist and made final adoption decisions; remaining provisional ratings were retained without case-by-case author review.
- **Not Independent Evaluation**: These ratings represent author-adopted AI-assisted evaluations and **do not constitute independent human inter-rater assessments** or double-blind expert panel review.
- **Absence of Diagnostic Advantage**: Qualitative results demonstrate that domain adaptation improved structural output-format compliance, but **did not confer an advantage in technical diagnostic correctness, hallucination mitigation, or repair scoping** over the unadapted base model.

---

## 5. Technical Limitations & Operational Warnings

1. **Empirical Steering vs. Mathematical Guarantees**: Parameter adaptation steers generation probabilistically. Unlike grammar-constrained decoding (e.g., Outlines, SynCode), LoRA does not provide mathematical validity guarantees. Downstream pipelines must maintain strict schema validation gates.
2. **Synthetic Benchmark Scope**: The 40 scenarios do not capture the long-tail complexity, deep dependency trees, or multi-file repositories of production software.
3. **Formatter Sensitivity**: The primary performance delta reflects both training prompt boundary formatting (`<|turn|>model\n`) and weight adaptation.
4. **Safety Verification**: Heuristic regex scanning does not guarantee semantic safety. Developers must verify all suggested commands prior to execution.

---

## 6. Hardware & Runtime Requirements

- **Inference Hardware**: Requires an NVIDIA GPU with at least 15 GB VRAM (e.g., Tesla T4, RTX 3090/4090, A10G) to run 4-bit NF4 quantized inference.
- **Software Stack**: Python $\ge 3.10$, PyTorch $\ge 2.4$, Hugging Face `transformers >= 4.46`, `peft >= 0.13`, `bitsandbytes >= 0.43`.
- **Inference Settings**: Greedy decoding (`temperature = 0.0`, `do_sample = False`, `max_new_tokens = 1024`).
