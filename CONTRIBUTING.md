# Contributing to OOPSIE

Thank you for helping build OOPSIE's open error-recovery dataset, training and evaluation tools, inference interfaces, knowledge base, and documentation.

## Contribution areas

- **Training examples:** add reviewed records to the maintainer-selected split in `data/`, following `data/example-schema.json` and the [dataset guide](docs/dataset-guide.md).
- **Benchmark cases:** add distinct, held-out examples to `evaluation/benchmark.jsonl`; never copy benchmark items into any dataset split. Follow the [benchmark guide](docs/benchmark-guide.md).
- **Knowledge-base recipes:** add a focused Markdown recipe under `knowledge-base/<framework>/` using `knowledge-base/_template.md`. Include exact synthetic/anonymized signatures, likely causes, safe repair guidance, relevant risk, and verification steps.
- **Redaction rules:** improve `rules/redaction/patterns.json` with tests for safe examples and false positives. Redaction is best-effort; do not submit credentials to test it.
- **Classifiers:** add precise signatures and cautious descriptions to `rules/classifiers/`; ambiguous errors should remain unknown or ask for more context.
- **Prompts and tooling:** improve `prompts/`, data validation, preprocessing, evaluation, API/CLI, and demo code without implying unverified model capability.
- **Documentation and translations:** improve `docs/` and keep project status, safety disclaimers, and terminology accurate.
- **Optional VS Code extension:** changes belong in `apps/vscode-extension/`; it remains an optional future interface.

## Dataset and privacy requirements

- Never commit real API keys, tokens, passwords, private keys, private database URLs, personal data, private logs, or proprietary source code.
- Use original synthetic examples or material you have explicit permission to share and have fully anonymized.
- Follow the existing dataset-record schema and keep expected category/risk aligned with the target report.
- Use cautious language such as “likely cause”; do not claim certainty unless the supplied evidence establishes it.
- Include concrete verification steps and focused, safe repair prompts.
- Do not disable authentication, authorization, database protections, or other safety controls as a generic fix.
- Automated redaction and validation do not guarantee that data is safe or shareable; review every contribution manually.

## Validate changes

```powershell
npm run validate:data
python training/preprocess.py
python -m unittest discover -s tests
```

For web demo changes, also run:

```powershell
npm run build
npm run lint
```

For optional extension changes, run its compile and lint scripts from `apps/vscode-extension`.

## Pull requests

- Submit one focused change per pull request.
- Explain the motivation and any limitations.
- Include verification steps and exact command results.
- For data contributions, state synthetic/permissioned provenance and confirm there is no sensitive information.
- For model or evaluation claims, include model/checkpoint, data, prompt, and evaluation provenance. Do not imply a fine-tuned checkpoint or benchmark result exists until verified.
- OOPSIE does not guarantee fixes, security, or production readiness.

See [`docs/contributing-guide.md`](docs/contributing-guide.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
