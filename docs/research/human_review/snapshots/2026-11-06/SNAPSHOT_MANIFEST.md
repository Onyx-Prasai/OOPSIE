# OOPSIE Pre-Unblinding Human Technical Review Snapshot Manifest

> **Snapshot Date**: 2026-11-06  
> **Timestamp (UTC)**: 2026-11-06T16:25:32.973490Z  
> **Integrity State**: Pre-unblinding, sealed condition blinding strictly intact.

## Provenance Statement

Ratings in this snapshot were AI-generated provisional ratings reviewed and selectively adopted by the author (Onyx Prasai) prior to unblinding.

## Cryptographic Checksums (SHA-256)

| File Name | Original Workspace Path | SHA-256 Hash | Size (bytes) |
|---|---|---|---|
| `batch_01.md` | `docs/research/human_review/batch_01.md` | `d262a9a7cf93e9f5c30c3ba15480f6946e0352856142ffc20c4ef6c863d57c9e` | 69336 |
| `batch_02.md` | `docs/research/human_review/batch_02.md` | `4f9a4bfdb7db8975661edd47972678b3f31ca7f52d43ab4ff5ad403ffc08bc40` | 67520 |
| `batch_03.md` | `docs/research/human_review/batch_03.md` | `af2d39376d1df530b3e022ba07b26ffcc90aa3a1851522887f26a9b9f1a32d63` | 66728 |
| `batch_04.md` | `docs/research/human_review/batch_04.md` | `b3efbf4ee91f23c2b93589b25c14ca4cbd5d5e031c57ac25b45c42d40c282725` | 69055 |
| `batch_05.md` | `docs/research/human_review/batch_05.md` | `b25f74ff50aa9ba6ff94b803a57369a88b36d337ad168f345e20fcded4f717d2` | 62340 |
| `batch_06.md` | `docs/research/human_review/batch_06.md` | `927f99d20fc1f5c39e099d9f3fd46a28ffacfc0f97a287aaa9479f03ecee7f22` | 64818 |
| `batch_07.md` | `docs/research/human_review/batch_07.md` | `b76b6423624f4638ac269e55a4a39af4b2065a585c1c77245715a4ec2a326cb1` | 65565 |
| `batch_08.md` | `docs/research/human_review/batch_08.md` | `cc0b443c2bc3bbfad270a6e89b69a70743eeecf5935767e62644ac7a617e98b8` | 70062 |
| `human_review_verification_checklist.md` | `docs/research/human_review_verification_checklist.md` | `534a97012794783262466e3dde8bd47a4cd5db1da96c79321c5d3f1717fc8c3b` | 84119 |
| `author_decision_sheet.md` | `docs/research/author_decision_sheet.md` | `5609d0e17076c4f517763af653af3392656f8126406b72c30aebb32c2d8b5ddc` | 17279 |

## Verification Command
```bash
python -c "import json, hashlib; m = json.load(open('docs/research/human_review/snapshots/2026-11-06/manifest.json')); assert all(hashlib.sha256(open(f['snapshot_path'], 'rb').read()).hexdigest() == f['sha256'] for f in m['files']); print('ALL HASHES VERIFIED')"
```