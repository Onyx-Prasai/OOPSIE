import json

with open('evaluation/benchmark.jsonl', 'r', encoding='utf-8') as f:
    cases = [json.loads(line) for line in f]

for i, c in enumerate(cases):
    print(f"[{i+1:02d}] {c['id']}: expected_cat={c['expected_category']}, risk={c['expected_risk']}")
    print(f"     error: {c['cleaned_error']}")
    print(f"     repair_focus: {c['expected_repair_focus']}")
    print(f"     ground_truth: {c['ground_truth_fix']}")
    print()

