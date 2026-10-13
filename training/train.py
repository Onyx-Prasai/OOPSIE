"""Fine-tune an open-weight causal language model with LoRA."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, 1):
            if not line.strip():
                continue
            record = json.loads(line)
            if not isinstance(record, dict) or not isinstance(record.get("input"), dict) or not isinstance(record.get("output"), dict):
                raise ValueError(f"{path}:{line_number}: expected input and output objects")
            records.append(record)
    if not records:
        raise ValueError(f"{path}: no dataset examples found")
    return records


def render_messages(tokenizer: Any, record: dict[str, Any]) -> tuple[str, str]:
    from training.preprocess import SYSTEM_PROMPT

    request = json.dumps(record["input"], ensure_ascii=False)
    answer = json.dumps(record["output"], ensure_ascii=False)
    prompt_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Analyze this error and return the required JSON report:\n{request}"},
    ]
    full_messages = [*prompt_messages, {"role": "assistant", "content": answer}]
    if getattr(tokenizer, "chat_template", None):
        prompt = tokenizer.apply_chat_template(
            prompt_messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        full_text = tokenizer.apply_chat_template(full_messages, tokenize=False)
        return prompt, full_text
    prompt = f"System:\n{SYSTEM_PROMPT}\n\nUser:\n{request}\n\nAssistant:\n"
    return prompt, f"{prompt}{answer}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "training" / "config" / "qwen2.5-coder-0.5b-lora.yaml")
    args = parser.parse_args()

    try:
        import yaml
        import torch
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from transformers import (
            AutoModelForCausalLM,
            AutoTokenizer,
            DataCollatorForSeq2Seq,
            Trainer,
            TrainingArguments,
        )

        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError(f"{args.config}: expected a YAML object")
        train_records = load_jsonl(ROOT / config["train_file"])
        validation_records = load_jsonl(ROOT / config["validation_file"])

        tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        load_in_4bit = bool(config.get("load_in_4bit", False))
        model_kwargs: dict[str, Any] = {}
        if load_in_4bit:
            from transformers import BitsAndBytesConfig

            model_kwargs["quantization_config"] = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.bfloat16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )

        model = AutoModelForCausalLM.from_pretrained(config["base_model"], **model_kwargs)
        if load_in_4bit:
            model = prepare_model_for_kbit_training(model)
        model = get_peft_model(
            model,
            LoraConfig(
                r=int(config["lora_r"]),
                lora_alpha=int(config["lora_alpha"]),
                lora_dropout=float(config["lora_dropout"]),
                bias="none",
                task_type="CAUSAL_LM",
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            ),
        )

        max_length = int(config["max_sequence_length"])

        def tokenize(record: dict[str, Any]) -> dict[str, list[int]]:
            prompt, full_text = render_messages(tokenizer, record)
            prompt_tokens = tokenizer(prompt, add_special_tokens=False)["input_ids"]
            full_tokens = tokenizer(
                full_text,
                add_special_tokens=False,
                truncation=True,
                max_length=max_length,
            )
            labels = list(full_tokens["input_ids"])
            prompt_length = min(len(prompt_tokens), len(labels))
            labels[:prompt_length] = [-100] * prompt_length
            if all(token == -100 for token in labels):
                raise ValueError("An example exceeds max_sequence_length before the assistant response.")
            return {**full_tokens, "labels": labels}

        train_dataset = [tokenize(record) for record in train_records]
        validation_dataset = [tokenize(record) for record in validation_records]
        output_dir = ROOT / config["output_dir"]
        training_args = TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=float(config["num_train_epochs"]),
            learning_rate=float(config["learning_rate"]),
            per_device_train_batch_size=int(config["per_device_train_batch_size"]),
            per_device_eval_batch_size=int(config["per_device_eval_batch_size"]),
            gradient_accumulation_steps=int(config["gradient_accumulation_steps"]),
            logging_steps=int(config["logging_steps"]),
            save_steps=int(config["save_steps"]),
            eval_steps=int(config["eval_steps"]),
            eval_strategy="steps",
            save_strategy="steps",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            greater_is_better=False,
            fp16=torch.cuda.is_available() and not torch.cuda.is_bf16_supported(),
            bf16=torch.cuda.is_available() and torch.cuda.is_bf16_supported(),
            seed=int(config["seed"]),
            report_to=[],
            remove_unused_columns=False,
        )
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=validation_dataset,
            data_collator=DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model, padding=True),
        )
        trainer.train()
        trainer.save_model(str(output_dir / "adapter"))
        tokenizer.save_pretrained(str(output_dir / "adapter"))
        print(f"LoRA adapter saved to {output_dir / 'adapter'}")
    except ImportError as error:
        print(
            f"Missing training dependency: {error}. Install with "
            "'python -m pip install -e \".[training]\"'.",
            file=sys.stderr,
        )
        return 2
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"training: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
