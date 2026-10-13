# Dataset

The canonical split files are JSONL with one dataset record per line. Each record follows [`example-schema.json`](example-schema.json), and its `target_report` follows [`schema.json`](schema.json). Preprocessing converts these records into the trainer's `{ "input": ..., "output": ... }` form. Training, validation, test, and evaluation benchmark splits are separate; never copy benchmark records into training data.

The initial synthetic corpus contains 80 train, 10 validation, and 10 test examples. Read [the dataset contribution guide](../docs/dataset-guide.md) before adding examples. Use only synthetic or permissioned, anonymized examples. Run `npm run validate:data` and `python training/preprocess.py`; automated validation/redaction is not a privacy guarantee.
