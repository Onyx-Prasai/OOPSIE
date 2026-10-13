"""Merge a trained PEFT LoRA adapter into its base model."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-model", default="Qwen/Qwen2.5-Coder-0.5B-Instruct")
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer

        adapter_path = args.adapter if args.adapter.is_absolute() else ROOT / args.adapter
        output_path = args.output if args.output.is_absolute() else ROOT / args.output
        tokenizer = AutoTokenizer.from_pretrained(str(adapter_path))
        base_model = AutoModelForCausalLM.from_pretrained(args.base_model)
        model = PeftModel.from_pretrained(base_model, str(adapter_path))
        merged = model.merge_and_unload()
        output_path.mkdir(parents=True, exist_ok=True)
        merged.save_pretrained(output_path, safe_serialization=True)
        tokenizer.save_pretrained(output_path)
        print(f"Merged model saved to {output_path}")
    except ImportError as error:
        print(
            f"Missing training dependency: {error}. Install with "
            "'python -m pip install -e \".[training]\"'.",
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError) as error:
        print(f"merge_lora: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
