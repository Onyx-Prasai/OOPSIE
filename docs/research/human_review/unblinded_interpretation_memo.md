# Cautious Interpretation Memo: Unblinded Evaluation Aggregate Results

**Date**: 2026-11-06  
**Author / Reviewer**: Onyx Prasai  
**Study**: OOPSIE (Operational Output Parser & Structured Inference Engine) Benchmark Review  
**Dataset**: 40 Benchmark Scenarios ($N = 160$ Total System Evaluations across 4 Conditions)  
**Status**: Pre-publication Analysis Memo (Subject to Author Approval prior to Manuscript Section 8 Integration)

---

## 1. Experimental Condition Mapping

Blinded system identifiers (`System Alpha`, `System Beta`, `System Gamma`, `System Delta`) were mapped dynamically across scenarios using the unblinding key located at `artifacts/benchmark_v1_2_0/benchmark_results/unblinded_review_key.json`. The four experimental conditions are:

- **Condition A (Base Zero-Shot + Schema)**: Unadapted base model with zero-shot prompt including canonical JSON schema ($N = 40$).
- **Condition B (Adapted Pilot Zero-Shot + Schema)**: LoRA-adapted pilot model with zero-shot prompt including canonical JSON schema ($N = 40$).
- **Condition C (Base 1-Shot Exemplar + Schema)**: Unadapted base model with a single in-context exemplar and canonical JSON schema ($N = 40$).
- **Condition D (Adapted Pilot Production Prompt / No Schema)**: LoRA-adapted pilot model under the production prompt configuration omitting the raw JSON schema ($N = 40$).

---

## 2. Methodology, Provenance, and Review Scope

1. **Review Provenance & Adoption Protocol**:  
   Initial qualitative ratings were generated provisionally by an automated evaluation pipeline using the frozen rubric definitions. The author reviewed the systematic verification checklist and made final adoption decisions for flagged evaluations (recorded in `docs/research/author_decision_sheet.md` and sealed in the dated snapshot manifest `docs/research/human_review/snapshots/2026-11-06/manifest.json`). The remaining provisional ratings were retained without case-by-case author review.
2. **Concealment and Blinding Protocol**:  
   System identities were concealed during initial AI rating generation, but the process was not a formally validated double-blind protocol. The author reviewed the unblinded aggregate results and made adoption decisions after condition identities were known for flagged cases.
3. **Absence of Independent Multi-Rater Structure**:  
   This evaluation does not constitute independent human review, inter-rater evaluation, expert-panel verification, or double-blind human review.
4. **Sample Size**:  
   The benchmark dataset comprises exactly 40 operational scenarios ($N = 40$ per condition, $N = 160$ total observations).

---

## 3. Complete Unblinded Aggregate Distributions

All five rubric dimensions and the unscored administrative gate are reported below with complete counts, exact percentages, and explicit denominators ($N = 40$ per condition, $N = 160$ total).

### Gate A: Administrative Content Eligibility Gate (Unscored)
*Purpose: Verifies whether the system generated assessable text content or failed to emit an evaluable response.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Assessable Content Present` | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 160 (100.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `No Usable Response` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

*All 160 responses (100.0%) across all four conditions were assessable.*

---

### Dimension 1: Technical Correctness
*Assesses whether the diagnosis correctly identifies the underlying technical failure without misleading or invalid assertions.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Correct)` | 39 (97.5%) | 37 (92.5%) | 40 (100.0%) | 37 (92.5%) | 153 (95.6%) |
| `Partial` | 1 (2.5%) | 3 (7.5%) | 0 (0.0%) | 3 (7.5%) | 7 (4.4%) |
| `Fail (Incorrect)` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

---

### Dimension 2: Unsupported Specifics / Hallucinations
*Assesses whether the response invents non-existent identifiers, fictitious stack traces, or unsupported claims.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `None` | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 40 (100.0%) | 160 (100.0%) |
| `Minor` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Severe` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

---

### Dimension 3: Appropriate Uncertainty
*Assesses calibration of diagnostic confidence relative to available log evidence.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Appropriate)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 40 (100.0%) | 159 (99.4%) |
| `Overconfident` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 0 (0.0%) | 1 (0.6%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

---

### Dimension 4: Actionable Repair Scope
*Assesses whether remediation advice is targeted and safe versus vague, harmful, or overbroad.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Well-Scoped)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 39 (97.5%) | 158 (98.8%) |
| `Vague` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Harmful / Overbroad` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 1 (2.5%) | 2 (1.2%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

---

### Dimension 5: Verification Steps Usefulness
*Assesses whether suggested verification commands or steps provide safe and non-destructive validation.*

| Rating Level | Condition A ($N=40$) | Condition B ($N=40$) | Condition C ($N=40$) | Condition D ($N=40$) | Total ($N=160$) |
|---|---:|---:|---:|---:|---:|
| `Pass (Useful & Safe)` | 40 (100.0%) | 39 (97.5%) | 40 (100.0%) | 39 (97.5%) | 158 (98.8%) |
| `Incomplete` | 0 (0.0%) | 1 (2.5%) | 0 (0.0%) | 1 (2.5%) | 2 (1.2%) |
| `Fail (Unsound)` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| `Cannot Assess` | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |

---

## 4. Key Empirical Observations and Non-Pass Cases

1. **All 160 Responses Were Assessable**:  
   Across all four conditions, 100.0% of responses (160/160) provided evaluateable diagnostic content.
2. **Zero Categorical Failures on Scored Dimensions**:  
   Across all 160 evaluations and all five scored dimensions, **no response received `Fail (Incorrect)`**, `Severe` hallucination, `Fail (Unsound)` verification, or `Cannot Assess`.
3. **Condition C Observed Highest Technical Correctness**:  
   Condition C (Base 1-Shot Exemplar + Schema) achieved the highest observed Pass rate on Technical Correctness at **100.0% (40/40)**, with 0 Partials.
4. **Conditions B and D Each Had Three Partial Technical Correctness Ratings**:  
   - Conditions B and D each recorded **37/40 Pass (92.5%)** and **3/40 Partial (7.5%)** on Technical Correctness.
   - Condition A recorded **39/40 Pass (97.5%)** and **1/40 Partial (2.5%)**.
   - Details of the 7 Partials:
     - `bench-firebase-04` (Condition A, Condition B, Condition D): Firebase Storage rule denials were categorized as `authentication` rather than `authorization`.
     - `bench-firebase-02` (Condition B, Condition D): Firestore security rule denials were categorized as `authentication` rather than `authorization`.
     - `bench-authentication-03` (Condition D): HTTP 403 missing OAuth scope was categorized as `authentication` rather than `authorization`.
     - `bench-react-02` (Condition B): "Maximum update depth exceeded" attributed exclusively to recursive routes rather than state loops.
5. **Actionable Repair Scope and Verification Anomalies**:  
   Conditions B and D each had one `Harmful / Overbroad` repair-scope rating and one `Incomplete` verification rating on scenario `bench-npm-02`, where both adapted conditions recommended running `npm install --legacy-peer-deps`.
6. **Appropriate Uncertainty Calibration**:  
   Condition B had the only `Overconfident` uncertainty rating (`bench-react-02`), where the route recursion explanation was asserted without acknowledging common state update loop mechanisms.

---

## 5. Strict Cautious Interpretation Guidelines

- **No Reliable Advantage for Adapted Conditions**:  
  With 40 evaluations per condition, these descriptive differences do not establish a statistically reliable or qualitative advantage for the adapted conditions (B or D) over the unadapted base model conditions (A or C).
- **No Claims of Outperformance**:  
  The results do not support a claim that LoRA adaptation improved diagnostic correctness, reduced hallucinations, or improved repair scoping.
- **Separation of Formats and Qualitative Soundness**:  
  Programmatic JSON and schema compliance results (where the adapted conditions showed 95.0%–97.5% compliance vs. 0% for base models due to prose and code fences) remain strictly separated from qualitative diagnostic soundness ratings.
- **No Causal Inferences or Composite Scores**:  
  No composite score is calculated, no statistical significance is claimed, and no causal claims are made regarding fine-tuning efficacy.
