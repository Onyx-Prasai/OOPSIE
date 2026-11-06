import json
import hashlib
from pathlib import Path

def main():
    snapshot_dir = Path("docs/research/human_review/snapshots/2026-11-06")
    manifest_path = snapshot_dir / "manifest.json"
    
    if not manifest_path.exists():
        print("Manifest does not exist!")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("Snapshot Date:", manifest.get("snapshot_date"))
    print("Snapshot Timestamp UTC:", manifest.get("snapshot_timestamp_utc"))
    print("Provenance statement:", manifest.get("provenance_statement"))
    print(f"Number of files: {len(manifest.get('files', []))}\n")

    all_match = True
    for entry in manifest.get("files", []):
        snap_path = Path(entry["snapshot_path"])
        orig_path = Path(entry["original_path"])
        
        if not snap_path.exists():
            print(f"MISSING SNAPSHOT: {snap_path}")
            all_match = False
            continue
        if not orig_path.exists():
            print(f"MISSING ORIGINAL: {orig_path}")
            all_match = False
            continue

        snap_hash = hashlib.sha256(snap_path.read_bytes()).hexdigest()
        orig_hash = hashlib.sha256(orig_path.read_bytes()).hexdigest()
        
        match = (snap_hash == entry["sha256"] == orig_hash)
        if not match:
            print(f"MISMATCH for {entry['file_name']}: recorded={entry['sha256'][:16]}, snap={snap_hash[:16]}, orig={orig_hash[:16]}")
            all_match = False
        else:
            print(f"VERIFIED {entry['file_name']}: {snap_hash} ({entry['byte_size']} bytes)")

    print("\nALL SNAPSHOT HASHES AND SOURCE FILES PERFECTLY VERIFIED:", all_match)

if __name__ == "__main__":
    main()
