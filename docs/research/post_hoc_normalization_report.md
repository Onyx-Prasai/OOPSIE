# OOPSIE Post-Hoc Normalization Validation Report

**Report date**: 2026-11-13  
**Status**: Final — all numerical statements confirmed against frozen outputs.  
**Frozen outputs unmodified**: Yes — no benchmark records, ratings, or snapshots were altered.

---

## 1. Purpose

This report documents an independent re-validation of all 160 frozen benchmark outputs against the canonical experimental schema, performed to:

1. Distinguish **direct raw-output schema compliance** from **compliance after lightweight normalization** (Markdown fence removal).
2. Confirm, correct, or contradict historical compliance summaries.
3. Provide a fully reproducible provenance record for the manuscript and Zenodo preprint package.

---

## 2. Input Artifact Hashes

| Artifact | Path | SHA-256 |
|:---|:---|:---|
| Frozen benchmark results | `artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json` | `6021aaab2616aec8cd09679532686eb09d424adfb15c2d2e22469f6c75aca397` |
| Canonical schema (LF-normalized) | `data/schema.json` | `ce322859f8e4a757847b3e4d02b90ded41054ccbef5b4dd872523a80d681440a` |
| Canonical schema (raw, CRLF) | `data/schema.json` | `40550bfef007a7078dc3515a0c03e52dec29e351b931e9bb6cd5ea8f447b547a` |

**LF-normalization convention**: SHA-256 is computed over the file content after replacing every `\r\n` byte pair with `\n`. All cross-platform references in the manuscript use the LF-normalized hash.

---

## 3. Validation Environment

| Item | Value |
|:---|:---|
| Python version | 3.14.2 |
| `jsonschema` version | 4.26.0 |
| JSON Schema draft | Draft 2020-12 (`$schema: https://json-schema.org/draft/2020-12/schema`) |
| Validation method | `jsonschema.validate(instance=parsed, schema=schema_obj)` |
| Operating system | Windows 11 |

---

## 4. Exact Validation Command

```
python scripts/evaluate_post_hoc_normalization.py \
  --results artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json \
  --schema  data/schema.json \
  --out     docs/research/post_hoc_normalized_evaluation.json
```

Script: `scripts/evaluate_post_hoc_normalization.py`  
Per-response output: `docs/research/post_hoc_normalized_evaluation.json` (41 KB, 160 entries)

---

## 5. Fence-Removal Procedure

Normalization applies a single transformation only:

```python
def strip_markdown_fences(text: str) -> str:
    s = text.strip()
    lines = s.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return "\n".join(lines[1:-1]).strip()
    return s
```

No regex extraction, no content rewriting, no key injection. If the stripped text still fails `json.loads()`, it is counted as a JSON parse failure. If it parses but fails `jsonschema.validate()`, it is counted as a schema failure.

---

## 6. Raw vs. Normalized Schema Compliance — All Four Conditions

| Condition | Description | Raw JSON valid | Raw schema valid | Norm JSON valid | Norm schema valid |
|:---|:---|:---:|:---:|:---:|:---:|
| **A** | Base zero-shot + schema | 0 / 40 | 0 / 40 | 40 / 40 | **40 / 40 (100.0%)** |
| **B** | Adapted + schema | 38 / 40 | 38 / 40 | 38 / 40 | **38 / 40 (95.0%)** |
| **C** | Base one-shot + schema | 0 / 40 | 0 / 40 | 39 / 40 | **39 / 40 (97.5%)** |
| **D** | Adapted, no schema | 40 / 40 | 39 / 40 | 40 / 40 | **39 / 40 (97.5%)** |

*Total evaluations: 160 (40 scenarios × 4 conditions).*

**Key interpretation**: Conditions A and C show 0 / 40 raw-output schema compliance. This was not due to incorrect semantic content — it was due to outer Markdown code fences (```` ```json ... ``` ````). After fence removal, Condition A recovered to 40 / 40 and Condition C to 39 / 40, confirming the base model already produced structurally valid payloads internally.

---

## 7. Failures Remaining After Normalization (4 total)

These are failures that persisted even after fence removal was applied. They are **not** the only raw-output failures — Conditions A and C each had 40 raw-output failures, all due to Markdown framing.

| Case | Condition | Norm JSON valid? | Failure type | Detail |
|:---|:---|:---:|:---|:---|
| `bench-firebase-01` | B (Adapted + Schema) | No | Invalid `\escape` sequence | Backslash inside a JSON string at character offset 1489; not recoverable by fence removal because no fence was present |
| `bench-nextjs-01` | B (Adapted + Schema) | No | Invalid `\escape` sequence | Backslash inside a backtick-quoted string at character offset 1154 |
| `bench-nextjs-03` | C (Base 1-Shot) | No | Malformed JSON key | Missing opening quote before `plain_explanation`; raw text contains `_explanation":` at line 3, column 3 (`JSONDecodeError`) |
| `bench-npm-03` | D (Adapted, No Schema) | Yes | Schema: missing required key | Valid JSON parsed successfully; `matched_recipes` key absent; all other 9 required keys present |

---

## 8. Historical Correction: Condition C Lenient Parsing

**Historical claim** (appearing in earlier project summaries and draft tables):  
> Condition C lenient parsing: **40 / 40 (100.0%)**

**Corrected count**: **39 / 40 (97.5%)**

**Evidence**: The raw completion for `bench-nextjs-03` (Condition C) contains the token sequence `_explanation":` at the start of the third line — the leading double-quote and `plain` prefix are absent. After fence removal, `json.loads()` raises `JSONDecodeError: Expecting property name enclosed in double quotes: line 3 column 3 (char 81)`. This defect is present in the frozen benchmark record and is not recoverable by fence stripping alone.

The underlying frozen benchmark output was not altered. This report and the manuscript reflect the corrected count.

---

## 9. Frozen Artifact Integrity Statement

The following actions were **not** performed during this validation:

- No benchmark response text was edited.
- No qualitative ratings were changed.
- No snapshot files were modified.
- No frozen JSON files were overwritten.

The validation script operates read-only on the frozen benchmark results file. Output is written only to `docs/research/post_hoc_normalized_evaluation.json` (a new file, not an existing frozen artifact).

---

## 10. Reproducibility Checklist

To reproduce this report from a clean clone:

```bash
# 1. Verify input hashes
python -c "
import hashlib, pathlib
files = {
    'artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json':
        '6021aaab2616aec8cd09679532686eb09d424adfb15c2d2e22469f6c75aca397',
    'data/schema.json':
        'ce322859f8e4a757847b3e4d02b90ded41054ccbef5b4dd872523a80d681440a',
}
for path, expected in files.items():
    raw = pathlib.Path(path).read_bytes().replace(b'\r\n', b'\n')
    actual = hashlib.sha256(raw).hexdigest()
    status = 'OK' if actual == expected else 'MISMATCH'
    print(status, path)
"

# 2. Run validation
python scripts/evaluate_post_hoc_normalization.py \
  --results artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json \
  --schema  data/schema.json \
  --out     docs/research/post_hoc_normalized_evaluation.json

# 3. Expected console output:
# Condition cond_a: Raw Schema= 0/40 | Norm Schema=40/40 (100.0%)
# Condition cond_b: Raw Schema=38/40 | Norm Schema=38/40 (95.0%)
# Condition cond_c: Raw Schema= 0/40 | Norm Schema=39/40 (97.5%)
# Condition cond_d: Raw Schema=39/40 | Norm Schema=39/40 (97.5%)
```

