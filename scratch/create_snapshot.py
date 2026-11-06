import os, shutil, hashlib, json
from datetime import datetime

snapshot_dir = r"docs/research/human_review/snapshots/2026-11-06"
os.makedirs(snapshot_dir, exist_ok=True)

files_to_snapshot = [
    "docs/research/human_review/batch_01.md",
    "docs/research/human_review/batch_02.md",
    "docs/research/human_review/batch_03.md",
    "docs/research/human_review/batch_04.md",
    "docs/research/human_review/batch_05.md",
    "docs/research/human_review/batch_06.md",
    "docs/research/human_review/batch_07.md",
    "docs/research/human_review/batch_08.md",
    "docs/research/human_review_verification_checklist.md",
    "docs/research/author_decision_sheet.md",
]

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

manifest_data = {
    "snapshot_date": "2026-11-06",
    "snapshot_timestamp_utc": datetime.utcnow().isoformat() + "Z",
    "provenance_statement": "Ratings in this snapshot were AI-generated provisional ratings reviewed and selectively adopted by the author (Onyx Prasai) prior to unblinding.",
    "files": []
}

for src in files_to_snapshot:
    fname = os.path.basename(src)
    dst = os.path.join(snapshot_dir, fname)
    shutil.copy2(src, dst)
    
    src_hash = sha256_file(src)
    dst_hash = sha256_file(dst)
    assert src_hash == dst_hash, f"Hash mismatch on copy: {src}"
    
    manifest_data["files"].append({
        "original_path": src.replace('\\', '/'),
        "snapshot_path": dst.replace('\\', '/'),
        "file_name": fname,
        "sha256": src_hash,
        "byte_size": os.path.getsize(dst)
    })

# Write JSON manifest
json_manifest_path = os.path.join(snapshot_dir, "manifest.json")
with open(json_manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2)

# Write Markdown manifest
md_lines = [
    "# OOPSIE Pre-Unblinding Human Technical Review Snapshot Manifest",
    "",
    "> **Snapshot Date**: 2026-11-06  ",
    f"> **Timestamp (UTC)**: {manifest_data['snapshot_timestamp_utc']}  ",
    "> **Integrity State**: Pre-unblinding, sealed condition blinding strictly intact.",
    "",
    "## Provenance Statement",
    "",
    manifest_data["provenance_statement"],
    "",
    "## Cryptographic Checksums (SHA-256)",
    "",
    "| File Name | Original Workspace Path | SHA-256 Hash | Size (bytes) |",
    "|---|---|---|---|"
]

for item in manifest_data["files"]:
    md_lines.append(f"| `{item['file_name']}` | `{item['original_path']}` | `{item['sha256']}` | {item['byte_size']} |")

md_lines.append("")
md_lines.append("## Verification Command")
md_lines.append("```bash")
md_lines.append("python -c \"import json, hashlib; m = json.load(open('docs/research/human_review/snapshots/2026-11-06/manifest.json')); assert all(hashlib.sha256(open(f['snapshot_path'], 'rb').read()).hexdigest() == f['sha256'] for f in m['files']); print('ALL HASHES VERIFIED')\"")
md_lines.append("```")

md_manifest_path = os.path.join(snapshot_dir, "SNAPSHOT_MANIFEST.md")
with open(md_manifest_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Snapshot created successfully in {snapshot_dir} with {len(manifest_data['files'])} files.")

