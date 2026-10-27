# Chat Formatting and Loss Boundary Audit

**Subject**: Token-level alignment between training preprocessing and inference prompting for `google/gemma-4-12b-it`.

---

## 1. Special Token Vocabulary & Delimiters

From `artifacts/pilot_v1/adapter/tokenizer.json`:

| Token | Token ID | Purpose in Gemma 4 Architecture |
| :--- | :---: | :--- |
| `<bos>` | `2` | Beginning of sequence |
| `<eos>` | `1` | End of sequence |
| `<|turn>` | `105` | Turn opening delimiter (`<|turn>system\n`, `<|turn>user\n`, `<|turn>model\n`) |
| `<turn|>` | `106` | Turn closing delimiter |
| `<|channel>` | `100` | Sub-channel opening delimiter (e.g., thought or tool channels) |
| `<channel|>` | `101` | Sub-channel closing delimiter |

---

## 2. Token-Level Formatting Audit: Training vs. Inference

A side-by-side token-level comparison between the training pipeline and the inference harness revealed a critical structural discrepancy:

### A. Training Input Structure
During training, the dataset provides 3 conversational turns (`system`, `user`, `assistant`). When rendered by `tokenizer.apply_chat_template(messages, tokenize=False)`:

```text
<bos><|turn>system
You are OOPSIE...<turn|>
<|turn>user
Error log here...<turn|>
<|turn>model
{"summary": "..."}<turn|>
```

**Assistant Prompt Boundary in Training**:
* **Token sequence before JSON**:
  * `<turn|>` (106)
  * `\n` (108)
  * `<|turn>` (105)
  * `model` (4368)
  * `\n` (108)
* **Immediate Next Token**: `{` (ID 235284)
* **Completion Loss Masking**: All tokens up to `model\n` received loss mask `-100`. The cross-entropy loss was calculated starting directly on `{`.

---

### B. Inference Prompt Structure
During inference evaluation in `kaggle_pilot_training.ipynb` and `kaggle_pilot_evaluation.ipynb`, prompts were constructed using:
```python
tokenizer.apply_chat_template(prompt_msgs, add_generation_prompt=True, tokenize=False)
```

In Gemma 4's canonical Jinja chat template (`artifacts/pilot_v1/adapter/chat_template.jinja`, lines 381–386):
```jinja
{%- if add_generation_prompt -%}
    {%- if ns.prev_message_type != 'tool_response' and ns.prev_message_type != 'tool_call' -%}
        {{- '<|turn>model\n' -}}
        {%- if not enable_thinking -%}
            {{- '<|channel>thought\n<channel|>' -}}
        {%- endif -%}
    ...
```

When rendered at inference time with default parameters, the prompt ends with:
```text
...<turn|>
<|turn>model
<|channel>thought
<channel|>
```

**Assistant Prompt Boundary at Inference**:
* **Token sequence before generation**:
  * `<turn|>` (106)
  * `\n` (108)
  * `<|turn>` (105)
  * `model` (4368)
  * `\n` (108)
  * `<|channel>` (100)
  * `thought` (13606)
  * `\n` (108)
  * `<channel|>` (101)  $\leftarrow$ **INJECTED CLOSING CHANNEL DELIMITER**

---

## 3. Discrepancy Findings & Observed Symptoms

1. **Out-of-Distribution Prompt Suffix**:
   * The model was trained with zero thinking channels (`{"summary": ...}` immediately follows `<|turn>model\n`).
   * At inference time, `add_generation_prompt=True` injected an empty closed thinking channel (`<|channel>thought\n<channel|>`).
2. **The Turn-Loop Symptom**:
   * Because `<channel|>` is a closing delimiter, the causal language model on certain prompts interprets `<channel|>` as a cue to start a new turn.
   * Under greedy decoding, when the probability of `<|turn>` exceeds `{`, the model predicts `<|turn>\n`.
   * Because no user turn follows, the model becomes trapped in a recursive loop:
     ```text
     '<|turn>\n<|turn>\n<|turn>\n<|turn>\n...'
     ```
   * This explains the exact failure symptom documented on `syn-ath-055`, `syn-cfg-017`, and `syn-run-058`.

---

## 4. Proposed Minimal Correction

To establish 100% distribution alignment between training and inference:

### Minimal Options:
* **Option 1 (Template Parameter)**: Pass `enable_thinking=True` or custom jinja parameters if supported by the processor.
* **Option 2 (Prompt Suffix Alignment)**: Render `prompt_msgs` with `add_generation_prompt=False`, and manually append the exact training prefix:
  ```python
  prompt_str = tokenizer.apply_chat_template(prompt_msgs, add_generation_prompt=False, tokenize=False) + "<|turn>model\n"
  ```
  This eliminates the unexpected `<|channel>thought\n<channel|>` sequence and matches the exact token boundary on which the model was trained.

> [!IMPORTANT]
> **Approval Gate**: In accordance with task instructions, this formatting correction is **not** silently applied. Any rerun with aligned delimiters must be approved by the user and applied identically to both the base model and the adapter.
