#!/usr/bin/env python3
"""Build versioned evaluation code and dataset bundle for Kaggle execution."""

from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
DIST_DIR.mkdir(exist_ok=True)

BUNDLE_VERSION = "1.2.0-four-conditions"
BUNDLE_ZIP_PATH = DIST_DIR / f"oopsie-eval-bundle-v{BUNDLE_VERSION}.zip"
MANIFEST_PATH = DIST_DIR / f"oopsie-eval-bundle-v{BUNDLE_VERSION}-manifest.json"

FILES_TO_PACKAGE = [
    "evaluation/__init__.py",
    "evaluation/harness.py",
    "evaluation/protocols/prompting_vs_adaptation_v1.md",
    "evaluation/benchmark.jsonl",
    "inference/__init__.py",
    "inference/config.py",
    "inference/formatters.py",
    "inference/engine.py",
    "inference/parser.py",
    "inference/safety.py",
    "inference/schema.py",
    "data/schema.json",
    "data/train.jsonl",
    "data/validation.jsonl",
    "rules/safety/destructive-commands.json",
    "rules/redaction/patterns.json",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main() -> None:
    manifest: dict[str, str] = {}
    print(f"Building evaluation bundle v{BUNDLE_VERSION} -> {BUNDLE_ZIP_PATH}")

    with zipfile.ZipFile(BUNDLE_ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path_str in FILES_TO_PACKAGE:
            file_path = ROOT / rel_path_str
            if not file_path.exists():
                raise FileNotFoundError(f"Required bundle file missing: {file_path}")
            h = sha256_file(file_path)
            manifest[rel_path_str] = h
            zf.write(file_path, arcname=rel_path_str)
            print(f"  + {rel_path_str} (SHA-256: {h[:12]}...)")

    bundle_hash = sha256_file(BUNDLE_ZIP_PATH)
    manifest_envelope = {
        "bundle_name": "oopsie-eval-bundle",
        "bundle_version": BUNDLE_VERSION,
        "bundle_zip_sha256": bundle_hash,
        "file_count": len(manifest),
        "files": manifest,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest_envelope, indent=2), encoding="utf-8")
    print(f"\nBundle built successfully: {BUNDLE_ZIP_PATH} ({BUNDLE_ZIP_PATH.stat().st_size} bytes)")
    print(f"Zip SHA-256: {bundle_hash}")
    print(f"Manifest saved to: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()

