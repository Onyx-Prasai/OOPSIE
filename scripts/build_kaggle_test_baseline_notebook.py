"""Build training/kaggle_missing_test_baseline.ipynb to complete unadapted base model evaluation on the 17 test inputs."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "training" / "kaggle_missing_test_baseline.ipynb"

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# OOPSIE: Missing Base Model Test Evaluation (17 Records, 1024 Tokens)\n",
            "\n",
            "This notebook completes the **missing unadapted base model evaluation** on the **17 independent test cases**.\n",
            "\n",
            "> **PURPOSE**: In the previous Kaggle run, the OOPSIE adapter was evaluated on the 17 independent test cases, but the base model test outputs were not serialized to disk. This notebook executes the unadapted base model under the **exact matching configuration** (`max_new_tokens=1024`, greedy decoding, identical chat formatting, no JSON repair).\n",
            "> **EXECUTION TIME**: ~2–3 minutes on a single GPU."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 1: Install Dependencies\n",
            "\n",
            "Installs upstream `transformers`, `bitsandbytes`, and `accelerate`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "!pip install -q -U git+https://github.com/huggingface/transformers.git bitsandbytes>=0.45.0 accelerate\n",
            "print(\"Dependencies installed successfully.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 2: Configuration & Seed Management\n",
            "\n",
            "Initializes the exact matching configuration (`seed=42`, `max_new_tokens=1024`, greedy decoding)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import os\n",
            "import sys\n",
            "import time\n",
            "import json\n",
            "import random\n",
            "import hashlib\n",
            "import numpy as np\n",
            "import torch\n",
            "from pathlib import Path\n",
            "\n",
            "CONFIG = {\n",
            "  \"name\": \"OOPSIE Base Model Test Evaluation\",\n",
            "  \"seed\": 42,\n",
            "  \"model_id\": \"google/gemma-4-12b-it\",\n",
            "  \"generation\": {\n",
            "    \"max_new_tokens\": 1024,\n",
            "    \"do_sample\": False,\n",
            "    \"temperature\": 0.0\n",
            "  },\n",
            "  \"output_dir\": \"/kaggle/working/oopsie-test-baseline-artifacts\"\n",
            "}\n",
            "\n",
            "SEED = CONFIG[\"seed\"]\n",
            "random.seed(SEED)\n",
            "np.random.seed(SEED)\n",
            "torch.manual_seed(SEED)\n",
            "if torch.cuda.is_available():\n",
            "    torch.cuda.manual_seed_all(SEED)\n",
            "\n",
            "print(\"Configuration set to exact matching test parameters.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 3: Hardware Preflight & Secrets Retrieval"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "assert torch.cuda.is_available(), \"CUDA GPU is required!\"\n",
            "device_name = torch.cuda.get_device_name(0)\n",
            "vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)\n",
            "print(f\"GPU: {device_name} ({vram_gb:.2f} GB VRAM)\")\n",
            "\n",
            "COMPUTE_DTYPE = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16\n",
            "\n",
            "hf_token = os.environ.get(\"HF_TOKEN\")\n",
            "if not hf_token:\n",
            "    try:\n",
            "        from kaggle_secrets import UserSecretsClient\n",
            "        hf_token = UserSecretsClient().get_secret(\"HF_TOKEN\")\n",
            "        os.environ[\"HF_TOKEN\"] = hf_token\n",
            "        print(\"Loaded HF_TOKEN from Kaggle Secrets.\")\n",
            "    except Exception:\n",
            "        raise RuntimeError(\"HF_TOKEN secret not found!\")\n",
            "else:\n",
            "    print(\"HF_TOKEN detected.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 4: Dataset Ingestion & Checksum Audit\n",
            "\n",
            "Loads `test_conversational.jsonl` (17 records) and verifies checksum."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "candidate_matches = list(Path(\"/kaggle/input\").rglob(\"test_conversational.jsonl\"))\n",
            "if not candidate_matches:\n",
            "    raise FileNotFoundError(\"test_conversational.jsonl not found under /kaggle/input!\")\n",
            "test_file = candidate_matches[0]\n",
            "print(f\"Found test dataset: {test_file}\")\n",
            "\n",
            "raw_bytes = test_file.read_bytes()\n",
            "test_sha = hashlib.sha256(raw_bytes).hexdigest()\n",
            "test_recs = [json.loads(l) for l in test_file.read_text(encoding=\"utf-8\").splitlines() if l.strip()]\n",
            "print(f\"Loaded {len(test_recs)} test records | SHA-256: {test_sha}\")\n",
            "assert len(test_recs) == 17, f\"Expected 17 records, got {len(test_recs)}\""
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 5: Load 4-Bit Base Model (Zero Adapters Attached)\n",
            "\n",
            "Loads pristine `google/gemma-4-12b-it` in 4-bit NF4 without any adapters."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig\n",
            "\n",
            "MODEL_ID = CONFIG[\"model_id\"]\n",
            "processor = AutoProcessor.from_pretrained(MODEL_ID, token=hf_token)\n",
            "tokenizer = processor.tokenizer\n",
            "\n",
            "bnb_config = BitsAndBytesConfig(\n",
            "    load_in_4bit=True,\n",
            "    bnb_4bit_quant_type=\"nf4\",\n",
            "    bnb_4bit_compute_dtype=COMPUTE_DTYPE,\n",
            "    bnb_4bit_use_double_quant=True\n",
            ")\n",
            "\n",
            "print(f\"Loading unadapted base model {MODEL_ID}...\")\n",
            "model = AutoModelForMultimodalLM.from_pretrained(\n",
            "    MODEL_ID,\n",
            "    quantization_config=bnb_config,\n",
            "    device_map=\"auto\",\n",
            "    torch_dtype=COMPUTE_DTYPE,\n",
            "    token=hf_token\n",
            ")\n",
            "model.eval()\n",
            "print(\"Unadapted base model loaded successfully into VRAM.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 6: Execute Matched Inference on 17 Test Inputs\n",
            "\n",
            "Executes greedy generation (`max_new_tokens=1024`) matching the adapter test run exactly."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from tqdm.auto import tqdm\n",
            "\n",
            "REQUIRED_KEYS = {\n",
            "    \"summary\", \"plain_explanation\", \"error_category\", \"likely_causes\",\n",
            "    \"missing_context_questions\", \"risk_level\", \"warnings\", \"repair_prompt\",\n",
            "    \"verification_steps\", \"matched_recipes\"\n",
            "}\n",
            "\n",
            "results = []\n",
            "gen_cfg = CONFIG[\"generation\"]\n",
            "\n",
            "print(\"Generating test outputs with unadapted base model...\")\n",
            "for r in tqdm(test_recs, desc=\"Base Model Test Evaluation\"):\n",
            "    prompt_msgs = [m for m in r[\"messages\"] if m[\"role\"] != \"assistant\"]\n",
            "    prompt_str = tokenizer.apply_chat_template(prompt_msgs, add_generation_prompt=True, tokenize=False)\n",
            "    inputs = tokenizer(prompt_str, return_tensors=\"pt\").to(\"cuda\")\n",
            "    prompt_token_count = inputs[\"input_ids\"].shape[1]\n",
            "    \n",
            "    t0 = time.perf_counter()\n",
            "    with torch.no_grad():\n",
            "        out_ids = model.generate(\n",
            "            **inputs,\n",
            "            max_new_tokens=gen_cfg[\"max_new_tokens\"],\n",
            "            do_sample=gen_cfg[\"do_sample\"],\n",
            "            pad_token_id=tokenizer.eos_token_id\n",
            "        )\n",
            "    elapsed = time.perf_counter() - t0\n",
            "    \n",
            "    gen_tokens = out_ids[0][prompt_token_count:]\n",
            "    gen_token_count = len(gen_tokens)\n",
            "    eos_detected = (tokenizer.eos_token_id in gen_tokens.tolist())\n",
            "    hit_budget = (gen_token_count >= gen_cfg[\"max_new_tokens\"])\n",
            "    \n",
            "    raw_text = tokenizer.decode(gen_tokens, skip_special_tokens=True).strip()\n",
            "    raw_with_specials = tokenizer.decode(gen_tokens, skip_special_tokens=False)\n",
            "    \n",
            "    json_valid = False\n",
            "    schema_valid = False\n",
            "    parse_error = None\n",
            "    missing_keys = []\n",
            "    parsed = None\n",
            "    \n",
            "    clean_text = raw_text\n",
            "    if clean_text.startswith(\"```json\"):\n",
            "        clean_text = clean_text[7:]\n",
            "    if clean_text.endswith(\"```\"):\n",
            "        clean_text = clean_text[:-3]\n",
            "    clean_text = clean_text.strip()\n",
            "    \n",
            "    try:\n",
            "        parsed = json.loads(clean_text)\n",
            "        json_valid = True\n",
            "        if isinstance(parsed, dict):\n",
            "            missing_keys = list(REQUIRED_KEYS - parsed.keys())\n",
            "            schema_valid = (len(missing_keys) == 0)\n",
            "        else:\n",
            "            parse_error = \"Root JSON is not an object\"\n",
            "    except Exception as e:\n",
            "        parse_error = str(e)\n",
            "    \n",
            "    results.append({\n",
            "        \"id\": r[\"id\"],\n",
            "        \"prompt_tokens\": prompt_token_count,\n",
            "        \"gen_tokens\": gen_token_count,\n",
            "        \"eos_detected\": eos_detected,\n",
            "        \"hit_budget\": hit_budget,\n",
            "        \"elapsed_sec\": round(elapsed, 2),\n",
            "        \"json_valid\": json_valid,\n",
            "        \"schema_valid\": schema_valid,\n",
            "        \"parse_error\": parse_error,\n",
            "        \"missing_keys\": missing_keys,\n",
            "        \"raw_text\": raw_text,\n",
            "        \"raw_with_specials\": raw_with_specials,\n",
            "        \"parsed\": parsed\n",
            "    })\n",
            "\n",
            "json_cnt = sum(1 for r in results if r[\"json_valid\"])\n",
            "schema_cnt = sum(1 for r in results if r[\"schema_valid\"])\n",
            "budget_cnt = sum(1 for r in results if r[\"hit_budget\"])\n",
            "\n",
            "print(\"\\n=== UNADAPTED BASE MODEL TEST RESULTS (N=17, 1024 TOKENS) ===\")\n",
            "print(f\"JSON Parse Rate    : {json_cnt}/17 ({json_cnt/17*100:.1f}%)\")\n",
            "print(f\"Schema Conformance : {schema_cnt}/17 ({schema_cnt/17*100:.1f}%)\")\n",
            "print(f\"Budget Hits        : {budget_cnt}/17\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 7: Export Missing Baseline Artifacts"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "out_dir = Path(CONFIG[\"output_dir\"])\n",
            "out_dir.mkdir(parents=True, exist_ok=True)\n",
            "\n",
            "with open(out_dir / \"independent_test_1024_baseline.json\", \"w\", encoding=\"utf-8\") as f:\n",
            "    json.dump(results, f, indent=2)\n",
            "\n",
            "summary = {\n",
            "    \"model_id\": CONFIG[\"model_id\"],\n",
            "    \"total_test_records\": len(test_recs),\n",
            "    \"dataset_sha256\": test_sha,\n",
            "    \"json_valid_count\": json_cnt,\n",
            "    \"schema_valid_count\": schema_cnt,\n",
            "    \"budget_hits_count\": budget_cnt\n",
            "}\n",
            "with open(out_dir / \"test_baseline_summary.json\", \"w\", encoding=\"utf-8\") as f:\n",
            "    json.dump(summary, f, indent=2)\n",
            "\n",
            "print(f\"Exported missing baseline test artifacts to: {out_dir}\")\n",
            "for p in out_dir.iterdir():\n",
            "    print(f\" - {p.name} ({p.stat().st_size} bytes)\")"
        ]
    }
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Built {NOTEBOOK_PATH} successfully.")
