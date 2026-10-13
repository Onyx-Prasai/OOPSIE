# Dataset guide

The initial corpus has 100 synthetic records: 80 training, 10 validation, and 10 test examples. It spans npm dependencies, React runtime behavior, Next.js build/runtime issues, Supabase, Firebase, Vercel/Netlify deployment, missing environment variables, API/backend errors, authentication, and unclear errors. This is a starter corpus, not evidence of model performance or broad coverage.

## Record formats

`data/example-schema.json` defines a dataset record. Each JSONL line is one record with a unique `id`, framework/platform/input metadata, raw and cleaned synthetic error text, expected category/risk, ground-truth explanation/fix, repair prompt, verification steps, warnings, difficulty, source type, and a `target_report`.

`target_report` must conform to [`../data/schema.json`](../data/schema.json), the structured inference-output schema. `training/preprocess.py` converts dataset records to the trainer's `{ "input": ..., "output": ... }` format. Run `python data/build_initial_corpus.py` only to regenerate the curated synthetic starter batch; review its changes before submitting them.

## Add an example

1. Use an original synthetic error or a log you have explicit permission to share.
2. Replace keys, tokens, passwords, connection strings, private URLs, personal information, usernames, and proprietary code with neutral placeholders or remove them.
3. Write `raw_error` and `cleaned_error`; for a synthetic example, these may be the same.
4. Include cautious cause language, a focused safe repair prompt, and concrete verification steps.
5. Keep `expected_category` and `expected_risk` consistent with `target_report`.
6. Add it to the split chosen by maintainers. Never add held-out benchmark cases to any dataset split.
7. Run validation and preprocessing:

```powershell
npm run validate:data
python training/preprocess.py
```

## Privacy and quality

Only use `synthetic` or permissioned, anonymized examples. Do not include real API keys, tokens, passwords, private keys, private database URLs, personal data, or long copyrighted text. Automated redaction and validation are best-effort and do not replace human review. Do not assume a validator can establish permission or identify every secret.

Use "likely cause" and explain uncertainty unless the supplied evidence proves the cause. State what extra context would help. Never suggest disabling security controls or promise a repair is guaranteed.

The current initial examples were generated from original synthetic scenarios. Provenance, review status, license, and split changes should be documented with future dataset contributions.
