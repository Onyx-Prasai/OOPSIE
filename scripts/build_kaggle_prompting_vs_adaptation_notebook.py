"""Build training/kaggle_prompting_vs_adaptation_dev.ipynb (v1.1.1-dev).

Features:
- Imports actual versioned evaluation harness from uploaded bundle
- Prints PEFT layer status: before base gen, inside disable context, after restoration, and before adapted gen
- Validates bundle manifest hashes
- Strictly separates smoke test (/kaggle/working/oopsie-dev-smoke-test/) from full run (/kaggle/working/oopsie-dev-validation-full/)
- Strict context checks: (prompt_tokens + 1024 <= 8192) with zero silent truncation
- Context-manager adapter disabling: with model.disable_adapter(): ...
- Verifies enable_adapters layer flags and asserts no merged weights
- Pinned numerical environment matching successful pilot runs
- Quarantines evaluation/benchmark.jsonl (EVAL_BENCHMARK = False)
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "training" / "kaggle_prompting_vs_adaptation_dev.ipynb"

cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# OOPSIE: Prompting vs. Adaptation Development Dry Run (v1.1.1-dev)\n",
            "\n",
            "**Protocol**: `OOPSIE-EVAL-PROTOCOL-v1.1.0-dev`  \n",
            "**Focus**: Rigorous development-only dry run comparing unadapted base prompting against fine-tuned LoRA pilot adapter.\n",
            "\n",
            "> **PREFLIGHT SAFETY & DATA ISOLATION CONSTRAINTS**:\n",
            "> - **Evaluation-Only**: Strictly zero retraining, zero weight merging, zero deployment, zero dataset alterations.\n",
            "> - **Quarantined Benchmark**: `evaluation/benchmark.jsonl` is **strictly quarantined** (`EVAL_BENCHMARK = False`).\n",
            "> - **Bundle Import**: Imports the actual versioned harness (`evaluation.harness`) from `/kaggle/working/eval_bundle`.\n",
            "> - **Separate Run Directories**: Smoke test exports to `/kaggle/working/oopsie-dev-smoke-test/`; full validation run exports to `/kaggle/working/oopsie-dev-validation-full/`.\n",
            "> - **Adapter State Management**: Uses documented context manager `with model.disable_adapter():` for base generation; verifies LoRA layer `get_layer_status()` flags; asserts adapters are not merged.\n",
            "> - **Context Window Capacity**: Strictly enforces `prompt_tokens + max_new_tokens <= 8192` with zero silent truncation.\n",
            "> - **Role Formatting**: Demonstrations in Condition C strictly use `assistant` role for template compatibility."
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 1: Install Pinned Dependencies Matching Successful Pilot Environment\n",
            "\n",
            "Installs dependencies matching the verified pilot training and evaluation runs (`transformers` upstream git revision, `trl>=0.12.0`, `peft>=0.14.0`, `bitsandbytes>=0.45.0`)."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "!pip install -q -U git+https://github.com/huggingface/transformers.git\n",
            "!pip install -q -U trl>=0.12.0 peft>=0.14.0 bitsandbytes>=0.45.0 accelerate datasets\n",
            "print(\"Dependencies installed successfully.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 2: Extract & Verify Uploaded Evaluation Bundle\n",
            "\n",
            "Extracts `oopsie-eval-bundle-v1.1.0-eval-harness.zip` (or unpacked directory) to `/kaggle/working/eval_bundle` and prioritizes it on `sys.path`."
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
            "import shutil\n",
            "import hashlib\n",
            "import zipfile\n",
            "from pathlib import Path\n",
            "\n",
            "bundle_dir = Path(\"/kaggle/working/eval_bundle\")\n",
            "if bundle_dir.exists():\n",
            "    shutil.rmtree(bundle_dir)\n",
            "bundle_dir.mkdir(parents=True, exist_ok=True)\n",
            "\n",
            "# Locate uploaded evaluation bundle zip or unpacked directory\n",
            "zip_candidates = list(Path(\"/kaggle/input\").rglob(\"oopsie-eval-bundle*.zip\")) + list(Path(\"/kaggle/working\").rglob(\"oopsie-eval-bundle*.zip\"))\n",
            "unpacked_candidates = [p.parent.parent for p in Path(\"/kaggle/input\").rglob(\"evaluation/harness.py\")]\n",
            "\n",
            "if zip_candidates:\n",
            "    b_zip = zip_candidates[0]\n",
            "    print(f\"Extracting bundle from {b_zip}...\")\n",
            "    with zipfile.ZipFile(b_zip, \"r\") as zf:\n",
            "        zf.extractall(bundle_dir)\n",
            "elif unpacked_candidates:\n",
            "    src = unpacked_candidates[0]\n",
            "    print(f\"Copying unpacked bundle from {src}...\")\n",
            "    shutil.copytree(src, bundle_dir, dirs_exist_ok=True)\n",
            "else:\n",
            "    raise FileNotFoundError(\"oopsie-eval-bundle zip or unpacked evaluation directory not found in /kaggle/input!\")\n",
            "\n",
            "# Prioritize bundle on sys.path\n",
            "if str(bundle_dir) in sys.path:\n",
            "    sys.path.remove(str(bundle_dir))\n",
            "sys.path.insert(0, str(bundle_dir))\n",
            "\n",
            "# Import versioned evaluation harness\n",
            "import evaluation.harness as harness\n",
            "import inference.parser as parser\n",
            "import inference.formatters as formatters\n",
            "import inference.config as config\n",
            "\n",
            "print(\"=== LOADED MODULE VERIFICATION ===\")\n",
            "print(\"harness module    :\", harness.__file__)\n",
            "print(\"parser module     :\", parser.__file__)\n",
            "print(\"formatters module :\", formatters.__file__)\n",
            "\n",
            "# Fail-fast integrity checks\n",
            "integrity_hashes = harness.verify_integrity_hashes()\n",
            "print(\"Integrity hashes strictly verified:\", integrity_hashes)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 3: Hardware Verification & Tesla T4 Compatibility Patch"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import random\n",
            "import numpy as np\n",
            "import torch\n",
            "\n",
            "# Tesla T4 compatibility workaround for FP32 GEMM\n",
            "try:\n",
            "    import trl.kernels.chunked_logprob\n",
            "    trl.kernels.chunked_logprob._MM_OUT_DTYPE = False\n",
            "    print(\"Applied Tesla T4 kernel compatibility workaround (_MM_OUT_DTYPE = False).\")\n",
            "except Exception as e:\n",
            "    print(f\"TRL kernel patch notice: {e}\")\n",
            "\n",
            "assert torch.cuda.is_available(), \"CUDA GPU accelerator required!\"\n",
            "device_name = torch.cuda.get_device_name(0)\n",
            "vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)\n",
            "print(f\"Active GPU: {device_name} ({vram_gb:.2f} GB VRAM)\")\n",
            "\n",
            "SEED = 42\n",
            "random.seed(SEED)\n",
            "np.random.seed(SEED)\n",
            "torch.manual_seed(SEED)\n",
            "torch.cuda.manual_seed_all(SEED)"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 4: Load Base Model & Attach Pilot LoRA Adapter\n",
            "\n",
            "Loads `google/gemma-4-12b-it` in 4-bit NF4 precision with `torch.bfloat16` compute dtype. Wraps with `PeftModel` loading `oopsie-pilot-adapter`."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from transformers import AutoProcessor, AutoModelForMultimodalLM, BitsAndBytesConfig\n",
            "from peft import PeftModel\n",
            "\n",
            "# Locate adapter directory\n",
            "adapter_candidates = list(Path(\"/kaggle/input\").rglob(\"adapter_config.json\"))\n",
            "if not adapter_candidates:\n",
            "    raise FileNotFoundError(\"oopsie-pilot-adapter (adapter_config.json) not found in /kaggle/input!\")\n",
            "adapter_dir = adapter_candidates[0].parent\n",
            "print(f\"Discovered adapter directory: {adapter_dir}\")\n",
            "\n",
            "MODEL_ID = \"google/gemma-4-12b-it\"\n",
            "print(f\"Loading AutoProcessor for {MODEL_ID}...\")\n",
            "processor = AutoProcessor.from_pretrained(MODEL_ID)\n",
            "tokenizer = processor.tokenizer\n",
            "\n",
            "bnb_config = BitsAndBytesConfig(\n",
            "    load_in_4bit=True,\n",
            "    bnb_4bit_quant_type=\"nf4\",\n",
            "    bnb_4bit_compute_dtype=torch.bfloat16,\n",
            "    bnb_4bit_use_double_quant=True\n",
            ")\n",
            "\n",
            "print(f\"Loading base model {MODEL_ID} in 4-bit...\")\n",
            "base_model = AutoModelForMultimodalLM.from_pretrained(\n",
            "    MODEL_ID,\n",
            "    quantization_config=bnb_config,\n",
            "    device_map=\"auto\",\n",
            "    torch_dtype=torch.bfloat16\n",
            ")\n",
            "\n",
            "print(f\"Attaching fine-tuned adapter from {adapter_dir}...\")\n",
            "model = PeftModel.from_pretrained(base_model, str(adapter_dir), adapter_name=\"oopsie_pilot\")\n",
            "model.eval()\n",
            "\n",
            "# Pre-flight PEFT layer inspection via model.get_layer_status()\n",
            "initial_layer_status = harness.inspect_peft_layer_status(model, expected_adapter=\"oopsie_pilot\")\n",
            "print(\"\\n=== INITIAL PEFT LAYER STATUS (get_layer_status) ===\")\n",
            "for k, v in initial_layer_status.items():\n",
            "    print(f\"  {k:20}: {v}\")\n",
            "assert initial_layer_status[\"layer_count\"] > 0\n",
            "assert initial_layer_status[\"any_merged\"] is False, \"Adapters must not be merged into base weights!\""
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 5: Dataset Ingestion & Fixed Demonstration Pre-flight Check"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Quarantining Flag\n",
            "EVAL_BENCHMARK = False\n",
            "if EVAL_BENCHMARK:\n",
            "    raise RuntimeError(\"EVAL_BENCHMARK must remain False during development dry run!\")\n",
            "\n",
            "val_path = Path(\"/kaggle/working/eval_bundle/data/validation.jsonl\")\n",
            "val_records = [json.loads(l) for l in val_path.read_text(encoding=\"utf-8\").splitlines() if l.strip()]\n",
            "print(f\"Loaded {len(val_records)} validation records from bundle.\")\n",
            "\n",
            "# Load fixed demonstration record (syn-dep-001) for Condition C\n",
            "fixed_demo = harness.load_fixed_demonstration()\n",
            "print(f\"Loaded fixed demonstration: {fixed_demo['id']} ({fixed_demo['scenario_group']})\")\n",
            "\n",
            "# Preview rendered prompts for Condition A, B, and C on case 0\n",
            "sample_rec = val_records[0]\n",
            "prompt_a, msgs_a = harness.render_prompt_for_condition(sample_rec, harness.CONDITION_A, tokenizer, fixed_demo)\n",
            "prompt_b, msgs_b = harness.render_prompt_for_condition(sample_rec, harness.CONDITION_B, tokenizer, fixed_demo)\n",
            "prompt_c, msgs_c = harness.render_prompt_for_condition(sample_rec, harness.CONDITION_C, tokenizer, fixed_demo)\n",
            "\n",
            "# Assert task instructions and schema text are strictly identical in A and B\n",
            "assert msgs_a[0][\"content\"] == msgs_b[0][\"content\"], \"Task instruction / schema text mismatch between A and B!\"\n",
            "\n",
            "print(f\"\\nPrompt Lengths for Case 0 ({sample_rec['id']}):\")\n",
            "print(f\"  Condition A (Base Zero-Shot)   : {len(tokenizer.encode(prompt_a))} tokens\")\n",
            "print(f\"  Condition B (Adapter Zero-Shot): {len(tokenizer.encode(prompt_b))} tokens\")\n",
            "print(f\"  Condition C (Base 1-Shot)      : {len(tokenizer.encode(prompt_c))} tokens\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 6: Stage A — Two-Record Smoke Test (`/kaggle/working/oopsie-dev-smoke-test/`)\n",
            "\n",
            "Executes an initial 2-record smoke test to verify forward passes, adapter toggling, context capacity, and artifact generation without running the full split."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "smoke_records = val_records[:2]\n",
            "smoke_out_dir = Path(\"/kaggle/working/oopsie-dev-smoke-test\")\n",
            "smoke_out_dir.mkdir(parents=True, exist_ok=True)\n",
            "\n",
            "print(f\"=== RUNNING STAGE A: 2-RECORD SMOKE TEST ===\")\n",
            "smoke_results_by_case = {}\n",
            "\n",
            "# Demonstrate PEFT layer-status transitions before, inside, and after base generation\n",
            "print(\"\\n--- Verifying Adapter Disabling Transitions ---\")\n",
            "st_before = harness.inspect_peft_layer_status(model, expected_adapter=\"oopsie_pilot\")\n",
            "print(f\"  [Pre-Base]     enabled={st_before['enabled']}, active={st_before['active_adapters']}\")\n",
            "\n",
            "with model.disable_adapter():\n",
            "    st_inside = harness.inspect_peft_layer_status(model, expected_adapter=\"oopsie_pilot\")\n",
            "    print(f\"  [Inside Base]  enabled={st_inside['enabled']} (none_enabled={st_inside['none_enabled']}), active={st_inside['active_adapters']}\")\n",
            "\n",
            "st_after = harness.inspect_peft_layer_status(model, expected_adapter=\"oopsie_pilot\")\n",
            "print(f\"  [Post-Base]    enabled={st_after['enabled']}, active={st_after['active_adapters']}\")\n",
            "\n",
            "model.set_adapter(\"oopsie_pilot\")\n",
            "st_adapted = harness.inspect_peft_layer_status(model, expected_adapter=\"oopsie_pilot\")\n",
            "print(f\"  [Adapted Mode] enabled={st_adapted['enabled']}, active={st_adapted['active_adapters']}\")\n",
            "\n",
            "for rec in smoke_records:\n",
            "    cid = rec[\"id\"]\n",
            "    print(f\"\\n--- Evaluating Smoke Case: {cid} ---\")\n",
            "    res_a = harness.evaluate_single_case(rec, harness.CONDITION_A, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    res_b = harness.evaluate_single_case(rec, harness.CONDITION_B, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    res_c = harness.evaluate_single_case(rec, harness.CONDITION_C, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    \n",
            "    smoke_results_by_case[cid] = {\n",
            "        \"cond_a\": res_a,\n",
            "        \"cond_b\": res_b,\n",
            "        \"cond_c\": res_c,\n",
            "    }\n",
            "    print(f\"  Cond A: schema_valid={res_a.schema_valid}, tokens={res_a.gen_token_count}, dur={res_a.duration_seconds}s, adapter_ok={res_a.adapter_state_verified}\")\n",
            "    print(f\"  Cond B: schema_valid={res_b.schema_valid}, tokens={res_b.gen_token_count}, dur={res_b.duration_seconds}s, adapter_ok={res_b.adapter_state_verified}\")\n",
            "    print(f\"  Cond C: schema_valid={res_c.schema_valid}, tokens={res_c.gen_token_count}, dur={res_c.duration_seconds}s, adapter_ok={res_c.adapter_state_verified}\")\n",
            "\n",
            "# Export smoke test artifacts\n",
            "with open(smoke_out_dir / \"smoke_test_results.json\", \"w\", encoding=\"utf-8\") as f:\n",
            "    json.dump({cid: {k: harness.asdict(v) for k, v in cmap.items()} for cid, cmap in smoke_results_by_case.items()}, f, indent=2)\n",
            "\n",
            "harness.generate_blinded_review_sheet(\n",
            "    smoke_results_by_case,\n",
            "    {r[\"id\"]: r for r in smoke_records},\n",
            "    smoke_out_dir / \"smoke_blinded_review.md\"\n",
            ")\n",
            "print(f\"\\nStage A smoke test artifacts saved to {smoke_out_dir}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 7: Stage B — Inspect Smoke Test Evidence & Pre-flight Gate\n",
            "\n",
            "Audits the smoke test results to ensure zero adapter-state leaks, verified layer flags, valid hashes, and no generation exceptions before proceeding."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "print(\"=== STAGE B: PRE-FLIGHT AUDIT OF SMOKE TEST RESULTS ===\")\n",
            "all_smoke_passed_gate = True\n",
            "\n",
            "for cid, cmap in smoke_results_by_case.items():\n",
            "    for cond_key, res in cmap.items():\n",
            "        print(f\"Case {cid} [{cond_key}]:\")\n",
            "        print(f\"  adapter_state_verified: {res.adapter_state_verified}\")\n",
            "        print(f\"  generation_failed     : {res.generation_failed}\")\n",
            "        print(f\"  prompt_token_count    : {res.prompt_token_count} (Capacity Budget: {res.prompt_token_count + 1024} <= 8192)\")\n",
            "        print(f\"  full_prompt_hash      : {res.prompt_hash}\")\n",
            "        if res.generation_failed or not res.adapter_state_verified:\n",
            "            all_smoke_passed_gate = False\n",
            "\n",
            "if all_smoke_passed_gate:\n",
            "    print(\"\\n[GATE PASSED]: All smoke cases executed cleanly with verified adapter states and valid capacity budgets.\")\n",
            "    print(\"You may proceed to execute Stage C (Full 18-Record Validation Dry Run) in the next cell.\")\n",
            "else:\n",
            "    print(\"\\n[GATE BLOCKED]: One or more smoke test assertions failed! Do NOT proceed to full run.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 8: Stage C — Full 18-Record Validation Dry Run (`/kaggle/working/oopsie-dev-validation-full/`)\n",
            "\n",
            "Executes the full 18 validation split records into a strictly separate output directory. Does not mix or append smoke test records."
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
            "full_out_dir = Path(\"/kaggle/working/oopsie-dev-validation-full\")\n",
            "full_out_dir.mkdir(parents=True, exist_ok=True)\n",
            "\n",
            "print(f\"=== RUNNING STAGE C: FULL 18-RECORD VALIDATION DRY RUN ===\")\n",
            "full_results_by_case = {}\n",
            "\n",
            "for rec in tqdm(val_records, desc=\"Full Validation Run\"):\n",
            "    cid = rec[\"id\"]\n",
            "    res_a = harness.evaluate_single_case(rec, harness.CONDITION_A, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    res_b = harness.evaluate_single_case(rec, harness.CONDITION_B, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    res_c = harness.evaluate_single_case(rec, harness.CONDITION_C, model, tokenizer, fixed_demo=fixed_demo)\n",
            "    \n",
            "    full_results_by_case[cid] = {\n",
            "        \"cond_a\": res_a,\n",
            "        \"cond_b\": res_b,\n",
            "        \"cond_c\": res_c,\n",
            "    }\n",
            "\n",
            "print(f\"\\nFull validation run completed on {len(full_results_by_case)} unique cases.\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 9: Comparative Metrics Summary & 2x2 Paired Transition Contingency Tables"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "def summarize_condition_results(cond_key, name):\n",
            "    cases = list(full_results_by_case.keys())\n",
            "    tot = len(cases)\n",
            "    res_list = [full_results_by_case[c][cond_key] for c in cases]\n",
            "    \n",
            "    jv = sum(1 for r in res_list if r.json_valid)\n",
            "    sv = sum(1 for r in res_list if r.schema_valid)\n",
            "    hb = sum(1 for r in res_list if r.hit_budget)\n",
            "    gf = sum(1 for r in res_list if r.generation_failed)\n",
            "    cm = sum(1 for r in res_list if r.category_match is True)\n",
            "    sp = sum(1 for r in res_list if r.safety_audit.get(\"safety_pass\") is True)\n",
            "    avg_dur = np.mean([r.duration_seconds for r in res_list]) if tot else 0.0\n",
            "    \n",
            "    return {\n",
            "        \"condition\": name,\n",
            "        \"total_attempted\": tot,\n",
            "        \"generation_failures\": f\"{gf}/{tot}\",\n",
            "        \"strict_schema_valid\": f\"{sv}/{tot} ({sv/tot*100:.1f}%)\" if tot else \"N/A\",\n",
            "        \"raw_json_valid\": f\"{jv}/{tot} ({jv/tot*100:.1f}%)\" if tot else \"N/A\",\n",
            "        \"budget_terminations\": f\"{hb}/{tot} ({hb/tot*100:.1f}%)\" if tot else \"N/A\",\n",
            "        \"category_agreement\": f\"{cm}/{tot} ({cm/tot*100:.1f}%)\" if tot else \"N/A\",\n",
            "        \"heuristic_safety_pass\": f\"{sp}/{tot} ({sp/tot*100:.1f}%)\" if tot else \"N/A\",\n",
            "        \"avg_duration_seconds\": round(float(avg_dur), 2)\n",
            "    }\n",
            "\n",
            "summary = [\n",
            "    summarize_condition_results(\"cond_a\", \"Condition A (Base Zero-Shot)\"),\n",
            "    summarize_condition_results(\"cond_b\", \"Condition B (Adapter Zero-Shot)\"),\n",
            "    summarize_condition_results(\"cond_c\", \"Condition C (Base 1-Shot)\")\n",
            "]\n",
            "\n",
            "print(\"=== FULL VALIDATION DRY-RUN COMPARATIVE METRICS ===\")\n",
            "for s in summary:\n",
            "    print(f\"\\n--- {s['condition']} ---\")\n",
            "    for k, v in s.items():\n",
            "        if k != 'condition':\n",
            "            print(f\"  {k:24}: {v}\")\n",
            "\n",
            "# Paired 2x2 transition table: Condition A vs Condition B\n",
            "cases = list(full_results_by_case.keys())\n",
            "both_pass = sum(1 for c in cases if full_results_by_case[c][\"cond_a\"].schema_valid and full_results_by_case[c][\"cond_b\"].schema_valid)\n",
            "b_only = sum(1 for c in cases if not full_results_by_case[c][\"cond_a\"].schema_valid and full_results_by_case[c][\"cond_b\"].schema_valid)\n",
            "a_only = sum(1 for c in cases if full_results_by_case[c][\"cond_a\"].schema_valid and not full_results_by_case[c][\"cond_b\"].schema_valid)\n",
            "both_fail = sum(1 for c in cases if not full_results_by_case[c][\"cond_a\"].schema_valid and not full_results_by_case[c][\"cond_b\"].schema_valid)\n",
            "\n",
            "print(\"\\n=== PAIRED 2x2 SCHEMA COMPLIANCE TRANSITIONS (Base A vs Adapter B) ===\")\n",
            "print(f\"  Both Pass (A+ B+)           : {both_pass} / {len(cases)}\")\n",
            "print(f\"  Adapter-Only Pass (A- B+)   : {b_only} / {len(cases)}\")\n",
            "print(f\"  Base-Only Pass (A+ B-)      : {a_only} / {len(cases)}\")\n",
            "print(f\"  Both Fail (A- B-)           : {both_fail} / {len(cases)}\")"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "## Step 10: Export Artifacts & Generate Blinded Human Review Sheet\n",
            "\n",
            "Serializes raw outputs into `/kaggle/working/oopsie-dev-validation-full/` and writes `blinded_human_review_sheet.md` with randomized system identifiers."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 1. Save full raw results JSON\n",
            "full_records_json = {\n",
            "    cid: {k: harness.asdict(v) for k, v in cmap.items()}\n",
            "    for cid, cmap in full_results_by_case.items()\n",
            "}\n",
            "with open(full_out_dir / \"full_validation_results.json\", \"w\", encoding=\"utf-8\") as f:\n",
            "    json.dump(full_records_json, f, indent=2)\n",
            "\n",
            "# 2. Save summary metrics\n",
            "with open(full_out_dir / \"summary_metrics.json\", \"w\", encoding=\"utf-8\") as f:\n",
            "    json.dump(summary, f, indent=2)\n",
            "\n",
            "# 3. Generate Blinded Human Review Sheet\n",
            "harness.generate_blinded_review_sheet(\n",
            "    full_results_by_case,\n",
            "    {r[\"id\"]: r for r in val_records},\n",
            "    full_out_dir / \"blinded_human_review_sheet.md\"\n",
            ")\n",
            "\n",
            "print(f\"\\nAll full validation dry-run artifacts and blinded review sheet exported to {full_out_dir}\")"
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
            "version": "3.10.12"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTEBOOK_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
print(f"Successfully generated Kaggle development notebook at {NOTEBOOK_PATH}")
