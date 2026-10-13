# Held-out benchmark guide

`evaluation/benchmark.jsonl` contains 40 synthetic cases, four per supported coverage area. These cases are separate from `data/train.jsonl`, `data/validation.jsonl`, and `data/test.jsonl`. Do not train on them, tune prompts against them, or copy their content into training examples.

Each JSONL case includes:

- `id`, `framework`, `platform`, and `input_type`
- `raw_error` and `cleaned_error`
- `expected_category` and `expected_risk`
- `expected_repair_focus` and `ground_truth_fix`
- `verification_steps` and `safety_expectations`

Add new cases only after review. Use synthetic or permissioned anonymized inputs, defensible category/risk labels, one unique ID, and a specific expected repair focus. Check for overlap against all dataset splits before contribution.

Validate the complete corpus with:

```powershell
npm run validate:data
```

The validator checks the benchmark record format, duplicate IDs and normalized errors across the dataset/benchmark, risk values, obvious secret formats, and non-empty verification steps. Validation does not establish that labels or fixes are correct; maintainer review remains necessary.

## Evaluation status

The benchmark corpus exists, but no model has been evaluated against it and no benchmark results are available. `python evaluation/evaluate.py` calls a running configured inference API and must not be used to imply model quality if the endpoint is unavailable or not a fine-tuned checkpoint.
