# OOPSIE Controlled Formatting Experiment & Missing Test Baseline Guide

This guide provides instructions for running the **controlled evaluation-only formatting experiment** and completing the **missing unadapted base model test evaluation** on Kaggle.

---

## 1. Objectives & Controlled Conditions

1. **Complete Missing Original Test Baseline**:
   * Evaluates unadapted `google/gemma-4-12b-it` on all 17 frozen independent test records using the **original** evaluation formatter (`max_new_tokens=1024`, greedy, `add_generation_prompt=True`).
   * Matches the existing adapter test run exactly.
2. **Validation-Only Formatting A/B Test (N=18)**:
   * **Condition A**: Base Model + Original Formatter (with empty thought channel)
   * **Condition B**: Base Model + Candidate Training-Aligned Formatter
   * **Condition C**: Pilot Adapter + Original Formatter
   * **Condition D**: Pilot Adapter + Candidate Training-Aligned Formatter
3. **Targeted Repeatability Check**:
   * Repeats `syn-ath-055`, `syn-cfg-017`, and `syn-amb-020` once under identical conditions to assess loop repeatability vs. stability.
   * Saved separately and **not** pooled as independent data.
4. **Test Set Isolation**:
   * The candidate formatter is **not** applied to the 17 test cases. The test set remains a frozen pilot benchmark.

---

## 2. Notebook & Kaggle Session Setup

### A. Upload the Notebook
* In Kaggle, open a new notebook or click **File $\rightarrow$ Upload Notebook**.
* Select: [`training/kaggle_controlled_formatting_experiment.ipynb`](file:///c:/Users/onyxe/Desktop/OOPSIE/training/kaggle_controlled_formatting_experiment.ipynb).

### B. Attach Inputs
1. **Dataset (`oopsie-dataset`)**:
   * Must contain `val_conversational.jsonl` (18 records) and `test_conversational.jsonl` (17 records).
2. **Adapter (`oopsie-pilot-adapter`)**:
   * Attach your trained pilot adapter dataset (`adapter_model.safetensors`, `adapter_config.json`, etc.).
3. **Secret**:
   * Ensure `HF_TOKEN` is checked under **Add-ons $\rightarrow$ Secrets**.

### C. Session Settings
* **Accelerator**: `GPU T4 × 2` (or `GPU P100`).
* **Internet**: `On`.

---

## 3. Expected Output Artifacts (`/kaggle/working/oopsie-formatting-experiment/`)

* `test_original_baseline_1024.json`: Complete generation traces for unadapted base model on the 17 test records.
* `validation_condition_A_base_orig.json`: Base model + original formatter traces.
* `validation_condition_B_base_cand.json`: Base model + training-aligned formatter traces.
* `validation_condition_C_adapter_orig.json`: Pilot adapter + original formatter traces.
* `validation_condition_D_adapter_cand.json`: Pilot adapter + training-aligned formatter traces.
* `validation_repeatability_checks.json`: Repeatability runs for `syn-ath-055`, `syn-cfg-017`, and `syn-amb-020`.
* `experiment_summary_metrics.json`: Aggregated scorecard comparing all four validation conditions.
* `experiment_config.json`: Formatter definitions and random seeds.
* `env_packages.json`: Environment package versions.

---

## 4. How to Download Outputs
In a cell at the bottom of the notebook, run:
```python
!zip -r /kaggle/working/formatting_experiment.zip /kaggle/working/oopsie-formatting-experiment
```
Then click the refresh circle `⟳` next to `/kaggle/working` in the right sidebar, and click the download icon next to `formatting_experiment.zip`.
