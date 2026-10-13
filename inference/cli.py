"""Command-line client for the OOPSIE inference API."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from inference.safety import redact_secrets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("error", nargs="*", help="Error message; reads stdin when omitted.")
    parser.add_argument("--file", type=Path, help="Read the error or log from a UTF-8 file.")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/analyze")
    args = parser.parse_args()

    try:
        if args.file:
            error_text = args.file.read_text(encoding="utf-8")
        elif args.error:
            error_text = " ".join(args.error)
        elif not sys.stdin.isatty():
            error_text = sys.stdin.read()
        else:
            parser.error("Provide an error as an argument, with --file, or through stdin.")
            return 2

        if not error_text.strip():
            raise ValueError("The supplied error text is empty.")
        sanitized, _ = redact_secrets(error_text)
        request = urllib.request.Request(
            args.api_url,
            data=json.dumps({"error_text": sanitized}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            result: Any = json.loads(response.read().decode("utf-8"))
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError, urllib.error.URLError) as error:
        print(f"oopsie: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
