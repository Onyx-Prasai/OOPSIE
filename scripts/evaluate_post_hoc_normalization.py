#!/usr/bin/env python3
"""Tracked post-hoc evaluation of frozen OOPSIE benchmark outputs.

Evaluates raw-output parsing and normalized parsing (after Markdown code fence removal)
against the canonical 10-key JSON schema (data/schema.json).
Does not modify any frozen benchmark records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from importlib.metadata import version as get_package_version
from pathlib import Path
from typing import Any

import jsonschema


def compute_sha256(path: Path, lf_normalize: bool = False) -> str:
    """Compute SHA-256 hash, optionally normalizing CRLF line endings to LF."""
    raw = path.read_bytes()
    if lf_normalize:
        raw = raw.replace(b"\r\n", b"\n")
    return hashlib.sha256(raw).hexdigest()


def strip_markdown_fences(text: str) -> str:
    """Strip leading and trailing markdown code block delimiters."""
    s = text.strip()
    lines = s.splitlines()
    if len(lines) >= 2 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return "\n".join(lines[1:-1]).strip()
    return s


def run_evaluation(
    benchmark_results_path: Path,
    schema_path: Path,
    output_json_path: Path | None = None,
) -> dict[str, Any]:
    """Execute evaluation and return comprehensive metadata and per-response results."""
    # Hash verification
    schema_lf_hash = compute_sha256(schema_path, lf_normalize=True)
    schema_raw_hash = compute_sha256(schema_path, lf_normalize=False)
    results_hash = compute_sha256(benchmark_results_path, lf_normalize=False)

    schema_obj = json.loads(schema_path.read_text(encoding="utf-8"))
    benchmark_data = json.loads(benchmark_results_path.read_text(encoding="utf-8"))

    validator_version = get_package_version("jsonschema")

    conditions = ["cond_a", "cond_b", "cond_c", "cond_d"]
    summary: dict[str, dict[str, Any]] = {}
    per_response: dict[str, dict[str, Any]] = {}

    for cond in conditions:
        raw_json_pass = 0
        raw_schema_pass = 0
        norm_json_pass = 0
        norm_schema_pass = 0
        failures: list[dict[str, Any]] = []

        for case_id in sorted(benchmark_data.keys()):
            if case_id not in per_response:
                per_response[case_id] = {}

            item = benchmark_data[case_id].get(cond, {})
            raw_text = item.get("raw_completion", "")

            # Raw validation
            raw_json_ok = False
            raw_schema_ok = False
            raw_err = None
            try:
                parsed_raw = json.loads(raw_text)
                raw_json_ok = True
                try:
                    jsonschema.validate(instance=parsed_raw, schema=schema_obj)
                    raw_schema_ok = True
                except Exception as err:
                    raw_err = str(getattr(err, "message", err))
            except Exception as err:
                raw_err = str(err)

            # Normalized validation (strip fences)
            norm_text = strip_markdown_fences(raw_text)
            norm_json_ok = False
            norm_schema_ok = False
            norm_err = None
            try:
                parsed_norm = json.loads(norm_text)
                norm_json_ok = True
                try:
                    jsonschema.validate(instance=parsed_norm, schema=schema_obj)
                    norm_schema_ok = True
                except Exception as err:
                    norm_err = str(getattr(err, "message", err))
            except Exception as err:
                norm_err = str(err)

            if raw_json_ok:
                raw_json_pass += 1
            if raw_schema_ok:
                raw_schema_pass += 1
            if norm_json_ok:
                norm_json_pass += 1
            if norm_schema_ok:
                norm_schema_pass += 1

            if not norm_schema_ok:
                failures.append({
                    "case_id": case_id,
                    "condition": cond,
                    "norm_json_ok": norm_json_ok,
                    "error": norm_err,
                })

            per_response[case_id][cond] = {
                "raw_json_valid": raw_json_ok,
                "raw_schema_valid": raw_schema_ok,
                "norm_json_valid": norm_json_ok,
                "norm_schema_valid": norm_schema_ok,
                "raw_error": raw_err,
                "norm_error": norm_err,
            }

        total_cases = len(benchmark_data)
        summary[cond] = {
            "total_cases": total_cases,
            "raw_json_valid": raw_json_pass,
            "raw_schema_valid": raw_schema_pass,
            "norm_json_valid": norm_json_pass,
            "norm_schema_valid": norm_schema_pass,
            "norm_schema_pct": round(norm_schema_pass / total_cases * 100, 1),
            "unrecovered_failures": failures,
        }

    out = {
        "metadata": {
            "validator": "jsonschema",
            "validator_version": validator_version,
            "schema_path": str(schema_path),
            "schema_sha256_lf": schema_lf_hash,
            "schema_sha256_raw": schema_raw_hash,
            "benchmark_results_path": str(benchmark_results_path),
            "benchmark_results_sha256": results_hash,
            "total_cases": len(benchmark_data),
            "total_evaluations": len(benchmark_data) * len(conditions),
        },
        "summary": summary,
        "per_response": per_response,
    }

    if output_json_path:
        output_json_path.parent.mkdir(parents=True, exist_ok=True)
        output_json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        default=Path("artifacts/benchmark_v1_2_0/benchmark_results/benchmark_results_full.json"),
        help="Path to frozen benchmark_results_full.json",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("data/schema.json"),
        help="Path to canonical schema.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/research/post_hoc_normalized_evaluation.json"),
        help="Output path for evaluation JSON report",
    )
    args = parser.parse_args()

    report = run_evaluation(args.results, args.schema, args.out)
    print("=== OOPSIE Post-Hoc Raw vs Normalized Parsing Evaluation ===")
    print(f"Validator: jsonschema v{report['metadata']['validator_version']}")
    print(f"Schema LF SHA-256: {report['metadata']['schema_sha256_lf']}")
    print(f"Benchmark Results SHA-256: {report['metadata']['benchmark_results_sha256']}")
    print("-" * 65)
    for cond, s in report["summary"].items():
        print(f"Condition {cond:6}: Raw Schema={s['raw_schema_valid']:2d}/{s['total_cases']} | Norm Schema={s['norm_schema_valid']:2d}/{s['total_cases']} ({s['norm_schema_pct']}%)")
    print("-" * 65)
    print(f"Detailed output saved to: {args.out}")


if __name__ == "__main__":
    main()

