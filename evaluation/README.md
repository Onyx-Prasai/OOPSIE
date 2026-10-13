# Evaluation benchmark

`benchmark.jsonl` is held out from training. Each record contains an `input.error_text` and reviewed `expected.error_category` / `expected.risk_level` labels. The evaluator calls a running local inference API:

```powershell
python evaluation/evaluate.py
```

It reports schema-valid JSON, category and risk exact-match accuracy, transparent length/presence proxies for clarity and actionability, and request latency. It intentionally reports `null` for hallucination rate and user trust/comprehension: those require human review or a documented user study, not a text-length heuristic. See [`rubric.md`](rubric.md) before interpreting results.

Supply `--output evaluation/results/run.json` to save a report. Results and trained weights are not committed by default.
