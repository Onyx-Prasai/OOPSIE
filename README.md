# OOPSIE

> OOPSIE is an open-source AI error-recovery model project that turns coding errors, stack traces, terminal output, build logs, and deployment logs into plain-language explanations, likely causes, risk warnings, and safe repair prompts for vibe coders.

Vibe coders often get stuck when AI-generated apps break. OOPSIE is designed to help explain what went wrong, summarize likely causes, flag risk, and prepare a safe repair prompt for a human to review in a coding assistant.

OOPSIE is advisory by design. It does not automatically edit code, execute commands, deploy apps, or guarantee a fix. Use it to understand the problem more clearly and verify every change yourself.

## What OOPSIE does

Given an error message, stack trace, build output, terminal log, or deployment log, OOPSIE is intended to return:

- A plain-English explanation of the issue
- Likely root causes and missing-context questions
- An error category and risk level: low, medium, or high
- Safety warnings for sensitive or high-impact areas
- A copy-ready repair prompt for tools such as Cursor, Claude Code, ChatGPT, Lovable, Bolt, or Replit
- Verification steps to check the fix after applying changes

The output format is defined in [`data/schema.json`](data/schema.json).

## Project status

A pilot QLoRA adapter (`oopsie-pilot-adapter` on `google/gemma-4-12b-it`) and a pre-registered four-condition benchmark evaluation are complete.

- **Empirical Findings**: In our 40-scenario held-out benchmark (160 forward passes), the adapted model achieved 95.0% to 97.5% strict schema compliance under zero-tolerance greedy parsing, whereas unadapted base prompting failed automated ingestion (0.0%) due to conversational prose and markdown wrappers.
- **Qualitative Evaluation**: Systematic qualitative evaluation across all 160 completions demonstrated that domain adaptation was associated with improved structural output-format compliance, but **did not demonstrate a qualitative diagnostic-reasoning advantage** over the unadapted base models.
- **Key Research Artifacts**:
  - **Manuscript Draft**: [`docs/research/manuscript_draft_v1.md`](docs/research/manuscript_draft_v1.md)
  - **Benchmark Report**: [`docs/research/benchmark_evaluation_report_v1.md`](docs/research/benchmark_evaluation_report_v1.md)
  - **Model Card**: [`inference/model-card.md`](inference/model-card.md)
  - **Evaluation Protocol & Reproduction**: [`evaluation/protocols/prompting_vs_adaptation_v1.md`](evaluation/protocols/prompting_vs_adaptation_v1.md)
  - **Evaluation Bundle**: [`dist/oopsie-eval-bundle-v1.2.0-four-conditions.zip`](dist/oopsie-eval-bundle-v1.2.0-four-conditions.zip)
  - **Dataset Splits**: [`data/train.jsonl`](data/train.jsonl), [`data/validation.jsonl`](data/validation.jsonl), [`data/test.jsonl`](data/test.jsonl), and [`evaluation/benchmark.jsonl`](evaluation/benchmark.jsonl)
  - **Result Archive**: [`artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz`](artifacts/benchmark_v1_2_0/oopsie_benchmark_results_v1_2_0.tar.gz)

See the [roadmap](ROADMAP.md) for future project phases.

## Quick start

### Web demo

The demo lives in [`apps/web-demo`](apps/web-demo). By default it runs **Rule + Knowledge Base mode** locally in the browser and labels results as rule-based. It operates via heuristic pattern-matching and community recipe lookup; it does not use or represent fine-tuned 12B model inference. Set `VITE_OOPSIE_API_URL` to enable **Model endpoint mode**; the endpoint's checkpoint and fine-tuning status are not verified by the demo.

```powershell
npm install
npm run dev
```

For a separately running API, set `VITE_OOPSIE_API_URL` to the `/api/analyze` endpoint before building or deploying the web demo. The browser redacts recognized secrets before analysis or sending; redaction is best-effort only.

### Local inference API

Install the API dependencies and point OOPSIE at a local compatible model directory or adapter checkpoint:

```powershell
python -m pip install -e ".[api]"
$env:OOPSIE_MODEL_PATH = "C:\models\oopsie"
uvicorn inference.api.main:app --host 127.0.0.1 --port 8000
```

The API validates generated JSON against [`data/schema.json`](data/schema.json), redacts common secrets, and retrieves relevant community recipes from [`knowledge-base`](knowledge-base).

### Dataset, training, and evaluation

- Add reviewed JSONL records following the [dataset guide](docs/dataset-guide.md)
- Prepare data splits with `python training/preprocess.py`
- Train using the scripts in [`training`](training)
- Validate dataset and benchmark records with `npm run validate:data` (or `python training/validate_data.py`)
- Execute benchmark contract tests with `python -m pytest tests/test_benchmark_contract.py`
- Full 4-condition benchmark reproduction details are documented in [`evaluation/protocols/prompting_vs_adaptation_v1.md`](evaluation/protocols/prompting_vs_adaptation_v1.md) and [`docs/research/benchmark_evaluation_report_v1.md`](docs/research/benchmark_evaluation_report_v1.md)

Never commit credentials, private logs, personal data, proprietary code, or deployment secrets.

The dataset schema is [`data/example-schema.json`](data/example-schema.json); the model report schema is [`data/schema.json`](data/schema.json). Contribute synthetic or permissioned examples through the process in [`docs/dataset-guide.md`](docs/dataset-guide.md). The held-out cases in [`evaluation/benchmark.jsonl`](evaluation/benchmark.jsonl) must not be copied into training data.

## Repository layout

```text
README.md                  Project overview and quick start
LICENSE                    Apache-2.0 license
CONTRIBUTING.md            Contribution guidance
SECURITY.md                Security reporting and responsible use
ROADMAP.md                 Four-phase project roadmap

apps/
├── web-demo/              Demo UI for pasting errors and viewing model output
└── vscode-extension/      Optional future VS Code client, not the core product

data/                     Open error-recovery dataset and structured output schema
training/                 Preprocessing, LoRA training, and adapter merge tooling
evaluation/               Held-out benchmark, evaluator, rubric, and results
inference/                Model card, API, CLI, and schema validation
knowledge-base/           Community recipes used as retrieval context
prompts/                  Prompt templates and response-schema references
rules/                   Error classifiers, safety rules, and redaction patterns
docs/                     Architecture, model, dataset, evaluation, safety, demo, and contribution docs
examples/                 Example logs and error cases
tests/                    Dataset and inference validation tests
.github/                  Issue templates, PR guidance, and CI
```

## Safety and responsible use

OOPSIE does not guarantee bug fixes, security, or production readiness. It does not automatically run commands, apply changes, or deploy software. Treat database, authentication, payment, and production advice with extra caution.

Before sending logs to any hosted endpoint, redact secrets and review the content. See [`docs/safety-guide.md`](docs/safety-guide.md) and [`SECURITY.md`](SECURITY.md).

## Contributing

We welcome help with:

- Verified error-recovery recipes in [`knowledge-base`](knowledge-base)
- Anonymized training examples in [`data`](data)
- Prompt improvements in [`prompts`](prompts)
- Evaluation cases in [`evaluation`](evaluation)
- Web demo improvements in [`apps/web-demo`](apps/web-demo)
- Documentation and translations in [`docs`](docs)
- Later work on the optional VS Code client in [`apps/vscode-extension`](apps/vscode-extension)

Start with [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [contributing guide](docs/contributing-guide.md).

## License

This repository is licensed under the [Apache License 2.0](LICENSE). Dataset examples, model checkpoints, and third-party dependencies may have their own licenses; review those terms separately.
