# Evaluation guide

Use the 40-case synthetic held-out benchmark at `evaluation/benchmark.jsonl`. Keep it separate from training, validation, and test examples. Read the [benchmark guide](benchmark-guide.md) before adding cases. The benchmark has not yet been run against a fine-tuned checkpoint and has no results.

Run a local API first, then:

```powershell
python evaluation/evaluate.py
python evaluation/evaluate.py --output evaluation/results/experiment.json
```

The evaluator measures:

- **JSON validity:** valid response against `data/schema.json`.
- **Error-category accuracy:** exact match against reviewed category labels.
- **Risk-level accuracy:** exact match against reviewed low/medium/high labels; inspect under-warning separately.
- **Explanation clarity:** the current automated result is only a length/empty-output proxy. Use the 1–5 human rubric for actual clarity.
- **Repair-prompt actionability:** current automated result checks presence and verification steps only. Review focus, context, and safety with human raters.
- **Hallucination rate:** requires human annotation of unsupported claims; the runner reports `null` rather than pretending to measure this automatically.
- **Latency:** median and p95 request latency for the evaluated environment.
- **User trust and comprehension:** measure with a documented, consent-based user study. Ask users to restate the error and rate trust/usefulness; clicks alone are not a trust measure.

Publish dataset and prompt versions, base and fine-tuned model IDs, inference settings, hardware, sample size, human-rating method, failures, and limitations with results. Follow the [evaluation rubric](../evaluation/rubric.md). Metrics do not guarantee a repair, security, or production readiness.
