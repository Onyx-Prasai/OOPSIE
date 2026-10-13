# Training pipeline

The initial pipeline validates and redacts the repository JSONL splits, then fine-tunes an open-weight causal language model with PEFT LoRA. It is an experimental starting point, not evidence of model quality or a released checkpoint.

```powershell
python -m pip install -e ".[training]"
python training/preprocess.py
python training/train.py --config training/config/qwen2.5-coder-0.5b-lora.yaml
```

The starter config targets `Qwen/Qwen2.5-Coder-0.5B-Instruct`. Confirm upstream model terms before use. Default settings use LoRA without 4-bit quantization. To enable QLoRA, set `load_in_4bit: true` only in a supported PyTorch/CUDA/bitsandbytes environment and install the compatible quantization dependency.

The script uses prompt-masked labels so loss is applied to the target JSON report rather than the input prompt. It saves an adapter under `artifacts/`; generated artifacts are ignored by Git. Update configuration for available GPU memory, dataset size, and desired experiment. Record exact package versions, hardware, data revision, and the resulting run before making claims.

Merge an adapter using `python training/merge_lora.py --adapter <adapter-dir> --output <merged-dir>`. Merged weights inherit the base-model and dataset licensing constraints; see [the model guide](../docs/model-guide.md) and [model card](../inference/model-card.md).
