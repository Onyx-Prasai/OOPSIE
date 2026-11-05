# OOPSIE Prompting vs. Adaptation: Development Dry Run Technical Audit (v1.1.0-dev)

**Protocol**: `OOPSIE-EVAL-PROTOCOL-v1.1.0-dev`  
**Execution Environment**: Kaggle GPU (Tesla T4, 14.56 GB VRAM, Python 3.10)  
**Evaluation Corpus**: `data/validation.jsonl` (N=18 records, SHA-256: `34cc646f169b528716fbb7b26b289af9214a7ca451536287157a2cfbddae8a3a`)  
**Base Model**: `google/gemma-4-12b-it` (4-bit NF4 precision, `torch.bfloat16`)  
**Adapter**: `oopsie-pilot-adapter` (Checkpoint-44)  
**Demonstration (Condition C)**: `syn-dep-001` (`vite-missing-lucide-icons` from `data/train.jsonl`)  
**Canonical Output Schema**: `data/schema.json` (SHA-256: `40550bfef007a7078dc3515a0c03e52dec29e351b931e9bb6cd5ea8f447b547a`)  
**System Prompt Version**: `system_prompt_v2_enum_guided` (Base Hash: `37a921ef57f8...`) + complete JSON schema text  
**Evidence Status**: **Verified against local disk artifacts (`artifacts/dev_validation_full/`)**  
**Recovered Artifact Archive**: `artifacts/dev_val_artifacts.zip` (SHA-256: `df4c5291a9774402108ede4c492b3f52cfbd1cd34e6760e6fa50bc0fab210af1`)  
**Recovered Files**:
- `full_validation_results.json` (SHA-256: `3bde15e1812c03d4cd807a49bb89d734db1b374a865bd743630c15a83f3ae6a1`)
- `summary_metrics.json` (SHA-256: `af5a6d19eb88479739907de4256ed67be9564d66fa841223fc51024efedfe422`)
- `blinded_human_review_sheet.md` (SHA-256: `6474f37ad145cd2cc957c2eb266511c8851ef8e6bfc7a59e1d3c737184627e7d`)  

---

## 1. Disaggregated Comparative Results

All metrics represent first-attempt autoregressive generation with frozen greedy decoding (`temperature=0.0`, `do_sample=False`, `max_new_tokens=1024`). Zero automated JSON repairs, zero markdown fence stripping, and zero retries were applied.

| Metric | Condition A: Base Zero-Shot | Condition B: Adapter Zero-Shot | Condition C: Base 1-Shot |
| :--- | :---: | :---: | :---: |
| **Model State** | Base (`with model.disable_adapter():`) | Adapted (`oopsie-pilot-adapter`) | Base (`with model.disable_adapter():`) |
| **Formatter** | Official Gemma Chat Template | `training_aligned_v1` (`<\|turn\>model\n`) | Official Chat Template (`assistant` role) |
| **Total Attempted Cases** | 18 | 18 | 18 |
| **Completed Forward Passes** | 18 | 18 | 18 |
| **Generation Exceptions / Crashes** | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 / 18 (0.0%) |
| **Raw RFC 8259 JSON Valid** | **0 / 18 (0.0%)** | **12 / 18 (66.7%)** | **0 / 18 (0.0%)** |
| **Strict Schema Conformance** | **0 / 18 (0.0%)** | **12 / 18 (66.7%)** | **0 / 18 (0.0%)** |
| **Output-Budget Terminations (1024 tok)** | 0 / 18 (0.0%) | 1 / 18 (5.6%) | 0 / 18 (0.0%) |
| **Delimiter-Loop Flags** | 0 / 18 (0.0%) | 0 / 18 (0.0%) | 0 / 18 (0.0%) |
| **Category Agreement (All Attempted)** | 0 / 18 (0.0%) | 8 / 18 (44.4%) | 0 / 18 (0.0%) |
| **Category Agreement (Parseable Only)** | N/A (0 parseable) | 8 / 12 (66.7%) | N/A (0 parseable) |
| **Heuristic Safety Pass (Regex)** | 18 / 18 (100.0%) | 18 / 18 (100.0%) | 18 / 18 (100.0%) |
| **Mean Generation Latency** | 110.43 s | 134.73 s | 111.03 s |

### Paired 2x2 Contingency Matrix (Base Condition A vs. Adapter Condition B)
- **Both Pass ($A+ B+$)**: 0 / 18 (0.0%)
- **Adapter-Only Pass ($A- B+$)**: 12 / 18 (66.7%)
- **Base-Only Pass ($A+ B-$)**: 0 / 18 (0.0%)
- **Both Fail ($A- B-$)**: 6 / 18 (33.3%)

---

## 2. Descriptive Prefix Observation across Conditions

- **Base Conditions (A and C)**: Across all 18 cases in both zero-shot and one-shot setups, the unadapted base model emitted conversational preambles, introductory prose, or markdown text wrappers. Under strict zero-tolerance parsing (which forbids substring JSON extraction or markdown stripping), 0/18 completions parsed as raw JSON.
- **Adapted Condition (B)**: All 18 completions began with a JSON-like object prefix (e.g., `{"summary": ...`), demonstrating strong learned bias towards structured syntax; 12/18 completed as strictly valid, conforming JSON objects.

---

## 3. Forensic Audit of the Six Adapter Non-Conforming Cases (Condition B)

To avoid conflating symptoms with verified causes, this audit distinguishes:
1. **Observed parser error** (the exact exception raised by Python's `json.loads`).
2. **Confirmed syntax defect** (the structural anomaly present in the decoded token stream).
3. **Suspected cause** (the plausible generation pathology).

| Case ID | Generated Tokens | Budget Hit | Observed Parser Error | Confirmed Syntax Defect | Verified Mechanism in Completion | Diagnostic Character Context |
| :--- | :---: | :---: | :--- | :--- | :--- | :--- |
| `syn-amb-086` | 412 | False | `Expecting ',' delimiter at line 2 col 718` | Missing structural closing bracket (`}`) on object | Second object in `likely_causes` omits closing `}`, causing following key `missing_context_questions` to parse as invalid dictionary entry | `...confidence":"medium.","missing_context_questions":...` |
| `syn-ath-028` | 441 | False | `Expecting ',' delimiter at line 1 col 1529` | Unescaped internal double quote in SQL snippet | Emitted literal `"` instead of `\"` around policy name `users_can_read_own_projects`, terminating JSON string prematurely | `...'CREATE POLICY "users_can_read_own_projects"...` |
| `syn-cfg-017` | 412 | False | `Invalid \escape at line 1 col 1400` | Illegal escape sequence `\'` (RFC 8259 violation) | Emitted `\'` inside require statement; single quote is not a valid escape in JSON standard | `...require(\'@firebase/app\')...` |
| `syn-dat-116` | 453 | False | `Invalid control character at line 1 col 1336` | Literal unescaped newline byte (`0x0A`) in string | Emitted literal newline (`\n`, ASCII 10) instead of JSON escape `\n` across paragraphs in explanation | `...User.findAll({ include: [Post] }.\n\nIn your model...` |
| `syn-run-053` | 1024 | **True** | `Unterminated string starting at line 1 col 4898` | Output-budget truncation at 1024 tokens | Reached maximum token limit mid-string during verification steps without closing string or root object | `...Confirm that the fix is reviewed by<EOF>` |
| `syn-run-114` | 407 | False | `Expecting ',' delimiter at line 1 col 779` | Unescaped internal double quotes in code snippet | Emitted literal `""` instead of `\"\"` inside JSX fallback snippet, prematurely closing JSON string | `...'value={user.name \|\| ""}\' is missing)...` |

*Note: In accordance with protocol rules, no automated string repair was applied to these outputs prior to scoring.*

---

## 4. Configuration Comparison: Current 12/18 Run vs. Earlier 18/18 Run

In an earlier controlled formatting audit ([`evaluation/audits/pilot_eval_audit_v1/controlled_formatting_experiment_results.md`](file:///c:/Users/onyxe/Desktop/OOPSIE/evaluation/audits/pilot_eval_audit_v1/controlled_formatting_experiment_results.md)), Condition D achieved 18/18 (100.0%) schema validity. The table below documents the multifaceted differences between that experiment and the current 12/18 evaluation:

| Dimension | Earlier Condition D Run (18/18 Pass) | Current Condition B Run (12/18 Pass) |
| :--- | :--- | :--- |
| **System Prompt Version** | `system_prompt_v1` (Frozen, 1,489 chars) | `system_prompt_v2_enum_guided` + Full Schema JSON (3,412 chars) |
| **System Prompt SHA-256** | `36ca7c5b9d1f...` | `37a921ef57f8...` (base) + `40550bfef007...` (schema) |
| **Raw Schema Embedded in Prompt** | **No** (Prompt referenced schema conceptually) | **Yes** (Complete 100-line JSON schema embedded as markdown block) |
| **Enum Guidance Embedded** | **No** | **Yes** (Explicit 14-category enumeration list and fallback instructions) |
| **Mean Prompt Token Count** | ~300 tokens | ~710 tokens (+410 tokens) |
| **Prompt Formatter** | `training_aligned_v1` (`<\|turn\>model\n`) | `training_aligned_v1` (`<\|turn\>model\n`) |
| **Adapter & Checkpoint** | `oopsie-pilot-adapter` (Checkpoint-44) | `oopsie-pilot-adapter` (Checkpoint-44) |
| **Precision & Quantization** | 4-bit NF4, `torch.bfloat16` compute dtype | 4-bit NF4, `torch.bfloat16` compute dtype |
| **Decoding Settings** | Greedy (`temp=0.0`), `max_new_tokens=1024` | Greedy (`temp=0.0`), `max_new_tokens=1024` |
| **Runtime Adapter Verification** | Ad-hoc script execution | Strict PEFT `model.get_layer_status()` assertion check |

### Analytical Caution
Because the prompt content, prompt token length, enum instructions, and embedded schema text were modified simultaneously between these runs, **the 6-case delta cannot be attributed solely to schema inclusion**. Embedding extensive schema JSON inside the prompt more than doubled the prompt length, introducing potential in-context distractors that may have impacted downstream string-escaping dynamics.

