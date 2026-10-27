"""OOPSIE inference engine interface and implementations.

Separates model loading, tensor operations, and generation from the API layer.
Loads the model and pilot adapter once per service process.
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from inference.config import (
    BASE_MODEL_ID,
    DO_SAMPLE,
    EOS_TOKEN_IDS,
    FORMATTER_TRAINING_ALIGNED,
    MAX_CONTEXT_TOKENS,
    MAX_NEW_TOKENS,
    MODEL_VERSION,
    TEMPERATURE,
    DEFAULT_SYSTEM_PROMPT_VERSION,
    get_adapter_path,
    get_base_model_id,
    is_mock_engine_enabled,
)
from inference.formatters import (
    build_conversation_messages,
    get_formatter,
)


class EngineError(Exception):
    """Base exception for inference engine failures."""
    pass


class ContextWindowExceededError(EngineError):
    """Raised when prompt + max_new_tokens exceeds the model's maximum context window."""
    pass


class ModelNotReadyError(EngineError):
    """Raised when inference is attempted on an uninitialized engine."""
    pass


@dataclass(frozen=True)
class GenerationResult:
    """Raw generation outcome produced by the inference engine."""
    completion_text: str
    prompt_tokens: int
    generated_tokens: int
    hit_budget: bool
    raw_with_specials: str
    duration_ms: float
    formatter_id: str
    model_version: str
    system_prompt_version: str = DEFAULT_SYSTEM_PROMPT_VERSION
    engine_mode: str = "real_model"


class BaseInferenceEngine(ABC):
    """Abstract interface for OOPSIE inference engines."""
    engine_mode: str = "real_model"

    @abstractmethod
    def is_ready(self) -> bool:
        """Check whether the model weights and tokenizer are loaded and ready."""
        pass

    @abstractmethod
    def generate(
        self,
        raw_error: str,
        context: dict[str, Any] | None = None,
        formatter_id: str = FORMATTER_TRAINING_ALIGNED,
        system_prompt_version: str = DEFAULT_SYSTEM_PROMPT_VERSION,
    ) -> GenerationResult:
        """Run generation for an error input and optional context."""
        pass


class Gemma4PilotEngine(BaseInferenceEngine):
    """Real GPU inference engine using Gemma 4 12B IT with pilot LoRA adapter."""
    engine_mode: str = "real_model"

    def __init__(
        self,
        adapter_path: Path | None = None,
        base_model_id: str | None = None,
    ) -> None:
        self.adapter_path = adapter_path or get_adapter_path()
        self.base_model_id = base_model_id or get_base_model_id()
        self._tokenizer: Any = None
        self._model: Any = None
        self._ready: bool = False

    def is_ready(self) -> bool:
        return self._ready and self._model is not None and self._tokenizer is not None

    def load(self) -> None:
        """Load base model in 4-bit NF4 and attach pilot LoRA adapter."""
        if self._ready:
            return

        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        # Tesla T4 CC 7.5 patch
        try:
            import trl.kernels.chunked_logprob
            trl.kernels.chunked_logprob._MM_OUT_DTYPE = False
        except Exception:
            pass

        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU is required for Gemma4PilotEngine, but CUDA is unavailable.")

        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        tokenizer = AutoTokenizer.from_pretrained(
            self.base_model_id,
            trust_remote_code=True,
        )

        base_model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            quantization_config=quantization_config,
            device_map="auto",
            trust_remote_code=True,
        )

        adapter_dir = Path(self.adapter_path)
        if not adapter_dir.exists():
            raise FileNotFoundError(f"Pilot adapter not found at {adapter_dir}")

        model = PeftModel.from_pretrained(
            base_model,
            str(adapter_dir),
            adapter_name="oopsie_pilot",
        )
        model.eval()

        self._tokenizer = tokenizer
        self._model = model
        self._ready = True

    def generate(
        self,
        raw_error: str,
        context: dict[str, Any] | None = None,
        formatter_id: str = FORMATTER_TRAINING_ALIGNED,
        system_prompt_version: str = DEFAULT_SYSTEM_PROMPT_VERSION,
    ) -> GenerationResult:
        if not self.is_ready():
            raise ModelNotReadyError("Gemma4PilotEngine is not loaded. Call load() before generation.")

        import torch

        formatter_fn = get_formatter(formatter_id)
        messages = build_conversation_messages(
            raw_error, context, system_prompt_version=system_prompt_version
        )
        prompt_str = formatter_fn(messages, self._tokenizer)

        inputs = self._tokenizer(prompt_str, return_tensors="pt").to("cuda")
        prompt_token_count = int(inputs["input_ids"].shape[1])

        # Strict context-window bound check (do not silently truncate)
        if prompt_token_count + MAX_NEW_TOKENS > MAX_CONTEXT_TOKENS:
            raise ContextWindowExceededError(
                f"Input tokens ({prompt_token_count}) + max_new_tokens ({MAX_NEW_TOKENS}) "
                f"exceeds model context limit of {MAX_CONTEXT_TOKENS} tokens. Input must be shortened."
            )

        t0 = time.perf_counter()
        with torch.inference_mode():
            out_ids = self._model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=DO_SAMPLE,
                temperature=TEMPERATURE,
                pad_token_id=self._tokenizer.eos_token_id,
            )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        gen_tokens_tensor = out_ids[0][prompt_token_count:]
        gen_tokens_list = gen_tokens_tensor.tolist()
        gen_token_count = len(gen_tokens_list)

        hit_budget = (gen_token_count >= MAX_NEW_TOKENS) and not any(
            eos in gen_tokens_list for eos in EOS_TOKEN_IDS
        )

        completion_text = self._tokenizer.decode(
            gen_tokens_tensor, skip_special_tokens=True
        ).strip()
        raw_with_specials = self._tokenizer.decode(
            gen_tokens_tensor, skip_special_tokens=False
        )

        return GenerationResult(
            completion_text=completion_text,
            prompt_tokens=prompt_token_count,
            generated_tokens=gen_token_count,
            hit_budget=hit_budget,
            raw_with_specials=raw_with_specials,
            duration_ms=elapsed_ms,
            formatter_id=formatter_id,
            model_version=MODEL_VERSION,
            system_prompt_version=system_prompt_version,
            engine_mode=self.engine_mode,
        )


class MockInferenceEngine(BaseInferenceEngine):
    """Configurable mock engine for testing without GPU or model checkpoints."""
    engine_mode: str = "mock"

    DEFAULT_VALID_REPORT = {
        "summary": "Process exited with code 1 due to missing environment variable.",
        "plain_explanation": "The application crashed during boot because DATABASE_URL was not set.",
        "error_category": "environment_variables",
        "likely_causes": [
            {
                "description": "DATABASE_URL is missing in local environment or .env file.",
                "confidence": "high",
            }
        ],
        "missing_context_questions": [
            "Is the .env file present in the project root?"
        ],
        "risk_level": "low",
        "warnings": [],
        "repair_prompt": "Please verify that DATABASE_URL is set in .env before running.",
        "verification_steps": [
            "Check that .env contains DATABASE_URL",
            "Re-run application command"
        ],
        "matched_recipes": []
    }

    def __init__(
        self,
        ready: bool = True,
        canned_completion: str | None = None,
        hit_budget: bool = False,
        simulated_exception: Exception | None = None,
        simulated_tokens: tuple[int, int] = (64, 256),
    ) -> None:
        self._ready = ready
        self.canned_completion = canned_completion
        self.hit_budget = hit_budget
        self.simulated_exception = simulated_exception
        self.simulated_tokens = simulated_tokens
        self.last_raw_error: str | None = None
        self.last_context: dict[str, Any] | None = None
        self.last_formatter_id: str | None = None
        self.last_system_prompt_version: str | None = None
        self.last_messages: list[dict[str, str]] | None = None
        self.call_history: list[dict[str, Any]] = []

    def is_ready(self) -> bool:
        return self._ready

    def set_ready(self, ready: bool) -> None:
        self._ready = ready

    def generate(
        self,
        raw_error: str,
        context: dict[str, Any] | None = None,
        formatter_id: str = FORMATTER_TRAINING_ALIGNED,
        system_prompt_version: str = DEFAULT_SYSTEM_PROMPT_VERSION,
    ) -> GenerationResult:
        if not self._ready:
            raise ModelNotReadyError("MockInferenceEngine is not ready.")

        if self.simulated_exception:
            raise self.simulated_exception

        from inference.formatters import build_conversation_messages

        # Capture invocation parameters and actual downstream conversation messages
        self.last_raw_error = raw_error
        self.last_context = context
        self.last_formatter_id = formatter_id
        self.last_system_prompt_version = system_prompt_version
        self.last_messages = build_conversation_messages(
            raw_error, context, system_prompt_version=system_prompt_version
        )
        self.call_history.append({
            "raw_error": raw_error,
            "context": context,
            "formatter_id": formatter_id,
            "system_prompt_version": system_prompt_version,
            "messages": self.last_messages,
        })

        import copy
        import json

        # If no canned completion is configured, return a deepcopy of the valid JSON report
        if self.canned_completion is not None:
            completion = self.canned_completion
        else:
            completion = json.dumps(copy.deepcopy(self.DEFAULT_VALID_REPORT))

        prompt_tokens, gen_tokens = self.simulated_tokens

        return GenerationResult(
            completion_text=completion,
            prompt_tokens=prompt_tokens,
            generated_tokens=gen_tokens,
            hit_budget=self.hit_budget,
            raw_with_specials=completion,
            duration_ms=42.0,
            formatter_id=formatter_id,
            model_version=MODEL_VERSION,
            system_prompt_version=system_prompt_version,
            engine_mode=self.engine_mode,
        )


_ENGINE_INSTANCE: BaseInferenceEngine | None = None


def get_engine() -> BaseInferenceEngine:
    """Retrieve the singleton inference engine."""
    global _ENGINE_INSTANCE
    if _ENGINE_INSTANCE is None:
        if is_mock_engine_enabled():
            _ENGINE_INSTANCE = MockInferenceEngine(ready=True)
        else:
            _ENGINE_INSTANCE = Gemma4PilotEngine()
    return _ENGINE_INSTANCE


def set_engine(engine: BaseInferenceEngine | None) -> None:
    """Explicitly set or reset the engine instance (useful for test fixtures)."""
    global _ENGINE_INSTANCE
    _ENGINE_INSTANCE = engine
