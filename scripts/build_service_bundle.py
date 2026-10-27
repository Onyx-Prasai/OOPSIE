#!/usr/bin/env python3
"""Build versioned service code bundle with cryptographic manifest."""

from __future__ import annotations

import hashlib
import json
import os
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
DIST_DIR.mkdir(exist_ok=True)

BUNDLE_VERSION = "2.0.0-enum-wiring-verified"

FILES_TO_PACKAGE = [
    "inference/__init__.py",
    "inference/config.py",
    "inference/formatters.py",
    "inference/engine.py",
    "inference/parser.py",
    "inference/safety.py",
    "inference/schema.py",
    "inference/retrieval.py",
    "inference/format.py",
    "inference/cli.py",
    "inference/api/__init__.py",
    "inference/api/main.py",
    "data/schema.json",
    "data/service_verification_inputs.json",
    "rules/redaction/patterns.json",
    "rules/safety/destructive-commands.json",
    "rules/classifiers/error-signatures.json",
]




def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def sha256_str(content: str) -> str:
    h = hashlib.sha256()
    h.update(content.encode("utf-8"))
    return h.hexdigest()


def main():
    print(f"Building OOPSIE Service Code Bundle [Version: {BUNDLE_VERSION}]...")

    # 1. Verify existence and calculate individual file hashes
    file_manifest: dict[str, dict[str, str | int]] = {}
    for rel_path in FILES_TO_PACKAGE:
        abs_path = ROOT / rel_path
        if not abs_path.exists():
            raise FileNotFoundError(f"Required package file missing: {abs_path}")
        file_sha = sha256_file(abs_path)
        file_size = abs_path.stat().st_size
        file_manifest[rel_path] = {
            "sha256": file_sha,
            "size_bytes": file_size,
        }
        print(f"  + {rel_path} ({file_size} bytes, sha: {file_sha[:12]}...)")

    # 2. Extract schema hash and prompt hashes
    schema_path = ROOT / "data" / "schema.json"
    schema_sha = sha256_file(schema_path)

    # Import prompt templates directly from codebase
    import sys
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    from inference.formatters import (
        PROMPT_VERSION_ENUM_GUIDED,
        PROMPT_VERSION_FROZEN,
        get_system_prompt,
    )

    prompt_a = get_system_prompt(PROMPT_VERSION_FROZEN)
    prompt_b = get_system_prompt(PROMPT_VERSION_ENUM_GUIDED)

    sha_prompt_a = sha256_str(prompt_a)
    sha_prompt_b = sha256_str(prompt_b)

    manifest_data = {
        "bundle_version": BUNDLE_VERSION,
        "build_timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "schema_hash": schema_sha,
        "prompt_hashes": {
            PROMPT_VERSION_FROZEN: {
                "sha256": sha_prompt_a,
                "sha256_12": sha_prompt_a[:12],
                "char_length": len(prompt_a),
            },
            PROMPT_VERSION_ENUM_GUIDED: {
                "sha256": sha_prompt_b,
                "sha256_12": sha_prompt_b[:12],
                "char_length": len(prompt_b),
            },
        },
        "files": file_manifest,
    }

    manifest_json_path = DIST_DIR / "bundle_manifest.json"
    manifest_json_path.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")
    print(f"\nManifest written to: {manifest_json_path}")

    # 3. Create zip archives (versioned and canonical)
    v2_zip_path = DIST_DIR / f"oopsie-service-code-{BUNDLE_VERSION}.zip"
    canonical_zip_path = DIST_DIR / "oopsie-service-code.zip"

    for zip_out in (v2_zip_path, canonical_zip_path):
        with zipfile.ZipFile(zip_out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            # Add all source files
            for rel_path in FILES_TO_PACKAGE:
                abs_path = ROOT / rel_path
                zf.write(abs_path, arcname=rel_path)
            # Embed the manifest into the archive itself
            zf.write(manifest_json_path, arcname="bundle_manifest.json")

        zip_sha = sha256_file(zip_out)
        print(f"Archive created: {zip_out.name} ({zip_out.stat().st_size} bytes)")
        print(f"  SHA-256: {zip_sha}")

    # Save archive hash separately
    archive_sha = sha256_file(canonical_zip_path)
    (DIST_DIR / "archive_sha256.txt").write_text(f"{archive_sha}  oopsie-service-code.zip\n", encoding="utf-8")

    print("\nService bundle build completed successfully.")


if __name__ == "__main__":
    main()
