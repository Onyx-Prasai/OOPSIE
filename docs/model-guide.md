# Model guide

## Planned base model

The starter training configuration targets `Qwen/Qwen2.5-Coder-0.5B-Instruct` as a small, open-weight candidate. Confirm the upstream checkpoint, current license, intended distribution terms, and hardware compatibility before training or releasing weights. A base-model reference is not evidence that OOPSIE fine-tuning has completed.

## Fine-tuning approach

The starter pipeline uses supervised fine-tuning with PEFT LoRA adapters over input/output JSONL records. Preprocess and validate the data first:

```powershell
python -m pip install -e ".[training]"
python training/preprocess.py
python training/train.py --config training/config/qwen2.5-coder-0.5b-lora.yaml
```

The initial configuration uses a small instruct model and modest defaults for experimentation. Training needs compatible compute and may require changing batch size, precision, sequence length, and memory settings. No quality result is implied by a successful training run.

Merge an adapter for inference when needed:

```powershell
python training/merge_lora.py `
  --adapter artifacts/oopsie-qwen2.5-coder-0.5b-lora/adapter `
  --output artifacts/oopsie-merged
```

For every trained checkpoint, record the exact base revision, license, dataset revision and provenance, training configuration, software versions, hardware, and evaluation results in the [model card](../inference/model-card.md).

## Inference

See [inference setup](../inference/README.md) to run a local API or CLI. The service redacts common secrets, retrieves recipe context, validates the JSON response, and adds rule-based warnings. These layers reduce some risks but cannot guarantee correctness or complete redaction.
