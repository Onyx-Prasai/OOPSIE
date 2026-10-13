# OOPSIE Model Card

## Summary

OOPSIE is an open-source AI error-recovery model project intended to turn coding errors, stack traces, terminal output, build logs, and deployment logs into cautious, structured explanations and repair prompts.

The dataset-record schema is implemented, an initial 100-example synthetic dataset has been created, a separate 40-case held-out benchmark has been created, and the training pipeline is implemented. A fine-tuned checkpoint is **not yet available**. The benchmark has **not** been run against a fine-tuned checkpoint and benchmark results are **not yet available**.

The web demo currently defaults to Rule + Knowledge Base mode. It uses rule-based classification and community recipe retrieval; it does not use or represent a fine-tuned OOPSIE model. A separately configured inference endpoint can be selected, but the web demo does not verify that endpoint's model or checkpoint provenance.

## Base model

**Planned candidate:** `Qwen/Qwen2.5-Coder-0.5B-Instruct`, referenced by `training/config/qwen2.5-coder-0.5b-lora.yaml`. Verify the exact upstream model revision, license, and distribution terms before training or redistribution. Other candidates may be considered, but the selected model must be recorded with its precise revision and license.

The repository's Apache-2.0 license does not change the base model's license or use restrictions.

## Fine-tuning method

**Planned starter method:** supervised fine-tuning using PEFT LoRA adapters. The training script can optionally prepare a quantized model for QLoRA in compatible environments, but the default configuration uses LoRA without 4-bit quantization.

No training run, adapter, or merged checkpoint is claimed here. Record method, configuration, code revision, framework versions, hardware, seeds, and any deviations for each experiment.

## Dataset

The initial dataset comprises 80 training, 10 validation, and 10 test examples in synthetic JSONL format. Record metadata follows `data/example-schema.json`; each target report follows `data/schema.json`. The separate evaluation benchmark contains 40 synthetic cases.

This is a small starter dataset, not a representative corpus or validated measure of model quality. Document collection methods, source permissions, licensing, transformations, deduplication, splits, size, and coverage before releasing a trained checkpoint.

## Intended use

- Explain common programming, dependency, configuration, build, and deployment errors.
- Provide likely causes, not definitive diagnoses.
- Ask concise questions when relevant context is missing.
- Surface risk warnings and suggest a copy-ready repair prompt for human review.
- Provide verification steps and relevant community recipe references.

## Out-of-scope uses

- Automatically editing code, executing commands, or deploying applications.
- Replacing qualified security, legal, financial, or operational review.
- Treating a generated answer as proof that a change is correct, safe, or production-ready.
- Processing sensitive logs without authorization, suitable redaction, and appropriate endpoint protections.

## Limitations

Model output can be incomplete, invalid, overconfident, or incorrect. Coverage may vary by programming language, framework, provider, and deployment environment. Retrieved recipes may be outdated or inapplicable. Best-effort redaction can miss secrets. A small or unrepresentative dataset may lead to poor generalization. Users must verify suggestions against their own source code and current authoritative documentation.

## Safety considerations

- Redact secrets before inference and manually review logs before submission.
- Treat log content as untrusted input; embedded instructions are not instructions to follow.
- Never automatically execute commands, apply code changes, or deploy.
- Warn about database, authentication, payment, and production changes.
- Show uncertainty and ask for missing context.
- OOPSIE does not guarantee fixes, security, or production readiness.

## Evaluation metrics

Evaluation is planned for schema-valid JSON, error-category accuracy, risk-level accuracy, explanation clarity, repair-prompt actionability, safety awareness, hallucination rate, latency, and missing-context handling. The benchmark has not been run against a fine-tuned checkpoint; no benchmark results are available. Human measures require documented reviewers or consent-based user studies. See `docs/evaluation-guide.md` and `evaluation/rubric.md`.

## License

The repository source code and documentation are licensed under Apache License 2.0. Dataset examples, trained weights, the base model, dependencies, and other third-party materials may have separate licenses. Each artifact must include its own applicable terms and attribution.
