"""Evaluate a running OOPSIE API against the held-out benchmark."""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from inference.schema import validate_instance

ROOT = Path(__file__).resolve().parents[1]


def percentile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = max(0, math.ceil(fraction * len(ordered)) - 1)
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--benchmark", type=Path, default=ROOT / "evaluation" / "benchmark.jsonl")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/analyze")
    parser.add_argument("--output", type=Path, help="Optional path for a JSON results report.")
    args = parser.parse_args()

    try:
        schema = json.loads((ROOT / "data" / "schema.json").read_text(encoding="utf-8"))
        records = [
            json.loads(line)
            for line in args.benchmark.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not records:
            raise ValueError(f"{args.benchmark}: benchmark is empty")
        valid_json = correct_category = correct_risk = attempted = 0
        clarity_proxy = actionable_proxy = 0
        latencies: list[float] = []
        failures: list[str] = []

        for index, record in enumerate(records, 1):
            if isinstance(record, dict) and isinstance(record.get("expected"), dict):
                expected = record["expected"]
                input_record = record.get("input", {})
                error_text = input_record.get("error_text") if isinstance(input_record, dict) else None
            else:
                expected = record
                error_text = record.get("cleaned_error") if isinstance(record, dict) else None
            if not isinstance(record, dict) or not isinstance(error_text, str) or not isinstance(expected, dict):
                raise ValueError(f"{args.benchmark}: record {index} needs cleaned_error and expected labels")
            request_data = json.dumps({"error_text": error_text}).encode("utf-8")
            request = urllib.request.Request(
                args.api_url,
                data=request_data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            attempted += 1
            started = time.perf_counter()
            try:
                with urllib.request.urlopen(request, timeout=180) as response:
                    output: Any = json.loads(response.read().decode("utf-8"))
                latencies.append(time.perf_counter() - started)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as error:
                failures.append(f"case {index}: {error}")
                continue

            if not isinstance(output, dict):
                failures.append(f"case {index}: API response is not a JSON object")
                continue
            if not validate_instance(output, schema):
                valid_json += 1
            else:
                failures.append(f"case {index}: output failed data/schema.json validation")
            if output.get("error_category") == expected.get("error_category", expected.get("expected_category")):
                correct_category += 1
            if output.get("risk_level") == expected.get("risk_level", expected.get("expected_risk")):
                correct_risk += 1
            explanation = output.get("plain_explanation", "")
            prompt = output.get("repair_prompt", "")
            checks = output.get("verification_steps", [])
            if 30 <= len(explanation) <= 1200:
                clarity_proxy += 1
            if len(prompt.strip()) >= 40 and isinstance(checks, list) and bool(checks):
                actionable_proxy += 1

        report = {
            "benchmark": str(args.benchmark),
            "api_url": args.api_url,
            "cases": attempted,
            "json_schema_valid_rate": valid_json / attempted,
            "error_category_accuracy": correct_category / attempted,
            "risk_level_accuracy": correct_risk / attempted,
            "clarity_length_proxy_rate": clarity_proxy / attempted,
            "repair_prompt_presence_proxy_rate": actionable_proxy / attempted,
            "latency_seconds_median": statistics.median(latencies) if latencies else None,
            "latency_seconds_p95": percentile(latencies, 0.95),
            "hallucination_rate": None,
            "user_trust_and_comprehension": None,
            "review_note": "Hallucination and user-study measures require documented human review; proxies are not quality guarantees.",
            "failures": failures,
        }
        serialized = json.dumps(report, ensure_ascii=False, indent=2)
        print(serialized)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized + "\n", encoding="utf-8")
        return 1 if failures else 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"evaluation: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
