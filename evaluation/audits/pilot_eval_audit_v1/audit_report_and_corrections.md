# OOPSIE Pilot Evaluation Audit & Correction Addendum

**Audit Date**: October 24, 2026  
**Audited Artifacts**:
- `artifacts/pilot_v1/` (Initial 512-token pilot training & evaluation)
- `artifacts/eval_1024/` (1024-token matched validation recheck & test evaluation)

---

## 1. Verified Counts, Hashes & Split Provenance

All metrics below have been re-verified directly against the raw serialization files on disk:

| Split | Canonical Path | Conversational Path | Record Count | SHA-256 Checksum |
| :--- | :--- | :--- | :---: | :--- |
| **Train** | `data/train.jsonl` | `data/processed/train_conversational.jsonl` | **85** | `6cbcdb625106a244855a4e1bc29061cc5bfc615896443ca11dada9f5e096e09e` |
| **Validation** | `data/validation.jsonl` | `data/processed/val_conversational.jsonl` | **18** | `df709f80671dd2e0406f535ed8af01a71639637609ff6eb4252bc1cc2033b1b6` |
| **Test** | `data/test.jsonl` | `data/processed/test_conversational.jsonl` | **17** | `13ddbe0d3e90e8840b4117af68a5f89f0d5da788045a85898ccbee37e02ceb4d` |
| **Held-Out Benchmark** | `evaluation/benchmark.jsonl` | N/A | **40** | `03e9112be8f3ffc8f35c24e6eb2d6a5e173d12fa1e1fc4220be951a316bdf69a` |

---

## 2. Audited Metric Denominators & Observed Performance

### A. Original Pilot Run (512-Token Output Budget)
*Source: `artifacts/pilot_v1/artifacts/eval_metrics.json`*
* **Validation Baseline (Unadapted Base)**:
  * Raw JSON Parse Rate: **14 / 18 (77.8%)**
  * Strict Schema Conformance (`data/schema.json`): **0 / 18 (0.0%)**
* **Validation Adapted (OOPSIE Pilot Adapter)**:
  * Raw JSON Parse Rate: **15 / 18 (83.3%)**
  * Strict Schema Conformance: **15 / 18 (83.3%)**
  * Output Budget Hits ($\ge 512$ tokens): **4 / 18 (22.2%)**
* **Independent Test Split**: **0 / 17 (Not Mounted / Not Evaluated in that run)**

### B. Matched Validation Recheck (1024-Token Output Budget)
*Source: `artifacts/eval_1024/evaluation_summary_metrics.json`*
* **Validation Baseline (Unadapted Base)**:
  * Raw JSON Parse Rate: **16 / 18 (88.9%)**
  * Strict Schema Conformance: **0 / 18 (0.0%)**
  * Output Budget Hits ($\ge 1024$ tokens): **0 / 18 (0.0%)**
* **Validation Adapted (OOPSIE Pilot Adapter)**:
  * Raw JSON Parse Rate: **16 / 18 (88.9%)**
  * Strict Schema Conformance: **16 / 18 (88.9%)**
  * Output Budget Hits ($\ge 1024$ tokens): **1 / 18 (5.6%)**

### C. Independent Test Split Evaluation (1024-Token Output Budget)
*Source: `artifacts/eval_1024/evaluation_summary_metrics.json`*
* **Test Adapted (OOPSIE Pilot Adapter)**:
  * Raw JSON Parse Rate: **14 / 17 (82.4%)**
  * Strict Schema Conformance: **14 / 17 (82.4%)**
  * Output Budget Hits ($\ge 1024$ tokens): **3 / 17 (17.6%)**
* **Test Baseline (Unadapted Base)**:
  * *Omitted from file export*: Calculated in GPU memory during Step 8 but not serialized to `evaluation_summary_metrics.json`. See Section 5 for the missing baseline audit and run plan.

---

## 3. Mandatory Corrections & Claim Alignments

The following claims are formally replaced with precise, evidence-grounded statements:

| Previous Phrasing | Audited Correction | Technical Rationale |
| :--- | :--- | :--- |
| *"Checkpoint-44 is the optimal model"* | **"Checkpoint-44 is the lowest observed validation-loss checkpoint among the 3 epoch boundaries evaluated."** | Only epochs 1, 2, and 3 were evaluated for checkpoint selection; performance on downstream reasoning tasks or intermediate steps was not tested. |
| *"100% safe repair instructions"* | **"Zero dangerous command patterns were flagged by the automated heuristic pattern matcher."** | Heuristic regex matching (`rm -rf /`, `DROP DATABASE`, etc.) cannot guarantee that a multi-step code edit is bug-free or safe in every environment. |
| *"Verified explanation correctness"* | **"Heuristic content completeness checks confirmed non-empty explanations and structured cause objects."** | True technical correctness requires human expert review of the code semantics, not automated string-length thresholds. |
| *"Independent test set proves generalization"* | **"The 17 test records were held out according to recorded dataset provenance."** | While disjoint from training by scenario and ID, 17 synthetic cases constitute a small pilot sample; broad real-world generalization remains to be proven on diverse benchmarks. |
