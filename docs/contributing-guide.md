# Contribution guide

OOPSIE welcomes focused contributions to the dataset, held-out benchmark, community recipes, classifiers, redaction rules, prompts, demo, and documentation. Start with the root [CONTRIBUTING.md](../CONTRIBUTING.md).

## JSONL training examples

Use the maintainer-selected split under `data/`. Each record follows `data/example-schema.json`, and its `target_report` follows `data/schema.json`. Use synthetic or permissioned anonymized data only. Do not include real secrets or private information. Be cautious about likely causes and include safe repair prompts and verification steps.

## Benchmark cases

Add distinct cases to `evaluation/benchmark.jsonl` using the [benchmark guide](benchmark-guide.md). Keep benchmark inputs and labels out of all training/validation/test splits and avoid prompt tuning against the held-out cases.

## Knowledge-base recipes

Create one recipe at `knowledge-base/<framework>/<slug>.md` from `knowledge-base/_template.md`. Use precise error signatures, a plain-language explanation, cautious repair guidance, explicit high-impact warnings, and verification steps. The retrieval layer uses signatures, keywords, framework, and category clues, so keep recipe metadata and signatures specific.

## Rules and other contributions

Add tested patterns to `rules/redaction/patterns.json` and narrow signatures to `rules/classifiers/`. For UI changes, preserve clear labels distinguishing rule-based fallback from model endpoint mode. Documentation and translation updates must retain the current-status and safety disclaimers.

## Required checks

```powershell
npm run validate:data
python training/preprocess.py
python -m unittest discover -s tests
```

Include exact commands and results in your PR. Automated checks cannot prove data permission, anonymization, or advice correctness; maintainers review those manually.
