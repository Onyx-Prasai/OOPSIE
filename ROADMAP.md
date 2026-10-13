# OOPSIE roadmap

OOPSIE is an open-source AI error-recovery model project. Roadmap items describe intended work and do not imply a trained release or measured capability.

## Phase 1: Dataset creation and schema

- Define the structured report in `data/schema.json`.
- Curate synthetic or permissioned, anonymized examples across error categories.
- Add provenance, license, split, redaction, and review processes.
- Validate train, validation, test, and separate benchmark examples.

**Exit evidence:** documented dataset provenance and validation reports for reviewed splits.

## Phase 2: Fine-tune a small open-source model

- Confirm a base-model checkpoint and its upstream license.
- Run reproducible LoRA/QLoRA experiments on approved data.
- Record hardware, software, training configuration, and limitations.
- Publish a model card only for checkpoints that actually exist and have been reviewed.

**Exit evidence:** a reproducible training run and documented checkpoint provenance; quality claims remain subject to evaluation.

## Phase 3: Evaluation benchmark and web demo

- Build a distinct held-out benchmark with reviewed category and risk labels.
- Measure structured-output validity, category/risk accuracy, clarity, actionability, hallucinations, latency, and user comprehension.
- Build the web demo with a clearly configured model-backed API and no success-shaped mock fallback.
- Publish evaluation methods, results, limitations, and safety considerations.

**Exit evidence:** reproducible evaluation and a demo that accurately identifies its inference source.

## Phase 4: Optional VS Code extension and community growth

- Develop a VS Code interface as an optional client of the inference API.
- Grow reviewed recipes, anonymized examples, benchmark coverage, and translations.
- Establish sustainable maintainer review, data governance, and safety processes.

**Exit evidence:** the extension remains opt-in and advisory; community processes continue to protect privacy and clearly label uncertainty.
