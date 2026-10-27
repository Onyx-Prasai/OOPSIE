"""Configuration constants and environment settings for OOPSIE inference."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final

ROOT: Final[Path] = Path(__file__).resolve().parents[1]
SCHEMA_PATH: Final[Path] = ROOT / "data" / "schema.json"

# Model and Adapter Identifiers
BASE_MODEL_ID: Final[str] = "google/gemma-4-12b-it"
MODEL_VERSION: Final[str] = "oopsie-pilot-gemma4-12b-lora-c44"
DEFAULT_ADAPTER_PATH: Final[Path] = ROOT / "artifacts" / "pilot_v1" / "adapter"

# Formatter Identifiers
FORMATTER_TRAINING_ALIGNED: Final[str] = "training_aligned_v1"
FORMATTER_ORIGINAL_EVAL: Final[str] = "original_eval_v1"
DEFAULT_FORMATTER: Final[str] = FORMATTER_TRAINING_ALIGNED

# System Prompt Identifiers
PROMPT_VERSION_FROZEN: Final[str] = "system_prompt_v1"
PROMPT_VERSION_ENUM_GUIDED: Final[str] = "system_prompt_v2_enum_guided"
DEFAULT_SYSTEM_PROMPT_VERSION: Final[str] = PROMPT_VERSION_ENUM_GUIDED

# Service and Configuration Version
CONFIG_VERSION: Final[str] = "oopsie-inference-v2.0"


# Generation Hyperparameters (Greedy, Frozen from Evaluation)
MAX_NEW_TOKENS: Final[int] = 1024
DO_SAMPLE: Final[bool] = False
TEMPERATURE: Final[float] = 0.0
SEED: Final[int] = 42

# EOS and Turn Tokens for Gemma 4
# 1 = <eos>, 106 = <turn|>
EOS_TOKEN_IDS: Final[list[int]] = [1, 106]

# Context and Input Resource Bounds
# Gemma 4 12B IT has an 8192 token window.
MAX_CONTEXT_TOKENS: Final[int] = 8192
MAX_INPUT_TOKENS: Final[int] = MAX_CONTEXT_TOKENS - MAX_NEW_TOKENS  # 7168 tokens
MAX_INPUT_CHARS: Final[int] = 16384  # Strict request payload limit

# Default Concurrency Limit (single worker GPU lock)
DEFAULT_CONCURRENCY: Final[int] = 1

# Environment Variable Lookups
def get_adapter_path() -> Path:
    env_path = os.environ.get("OOPSIE_MODEL_PATH")
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_ADAPTER_PATH

def get_base_model_id() -> str:
    return os.environ.get("OOPSIE_BASE_MODEL_ID", BASE_MODEL_ID)

def get_formatter_id() -> str:
    return os.environ.get("OOPSIE_FORMATTER", DEFAULT_FORMATTER)

def get_concurrency_limit() -> int:
    try:
        return max(1, int(os.environ.get("OOPSIE_CONCURRENCY", str(DEFAULT_CONCURRENCY))))
    except ValueError:
        return DEFAULT_CONCURRENCY

def is_mock_engine_enabled() -> bool:
    return os.environ.get("OOPSIE_USE_MOCK_ENGINE", "").lower() in ("1", "true", "yes")

def get_schema_path() -> Path:
    env_path = os.environ.get("OOPSIE_SCHEMA_PATH")
    if env_path:
        p = Path(env_path).expanduser().resolve()
        if p.exists():
            return p
    if SCHEMA_PATH.exists():
        return SCHEMA_PATH
    candidate = ROOT / "data" / "schema.json"
    if candidate.exists():
        return candidate
    return SCHEMA_PATH

def get_default_system_prompt_version() -> str:
    ver = os.environ.get("OOPSIE_SYSTEM_PROMPT_VERSION", DEFAULT_SYSTEM_PROMPT_VERSION)
    if ver not in (PROMPT_VERSION_FROZEN, PROMPT_VERSION_ENUM_GUIDED):
        raise ValueError(
            f"Invalid OOPSIE_SYSTEM_PROMPT_VERSION '{ver}'. "
            f"Must be '{PROMPT_VERSION_FROZEN}' or '{PROMPT_VERSION_ENUM_GUIDED}'."
        )
    return ver

