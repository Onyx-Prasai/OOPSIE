import re, json
import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a

# Load benchmark ground truth
with open('evaluation/benchmark.jsonl', 'r', encoding='utf-8') as f:
    bench_cases = {x['id']: x for x in (json.loads(line) for line in f)}

from inspect_all_evals import all_evals

print(f"Total audited records: {len(a.audit_results)}")
print(f"Total extracted raw evals: {len(all_evals)}")

# Join audit results with extracted raw evals
joined = []
for ar in a.audit_results:
    match = [e for e in all_evals if e['batch'] == int(ar['batch'].split('_')[1].split('.')[0]) and e['case_id'] == ar['case_id'] and e['system'] == ar['system']][0]
    gt = bench_cases.get(ar['case_id'], {})
    joined.append({
        "batch": ar['batch'],
        "case_id": ar['case_id'],
        "system": ar['system'],
        "gate": ar['gate'],
        "d1": ar['d1'],
        "d2": ar['d2'],
        "d3": ar['d3'],
        "d4": ar['d4'],
        "d5": ar['d5'],
        "notes": ar['notes'],
        "parsed": match['parsed'],
        "raw": match['raw'],
        "gt": gt
    })

print(f"Joined records: {len(joined)}")

# Let's check category mismatches vs expected_category in benchmark
cat_mismatches = []
for j in joined:
    p = j['parsed']
    pred_cat = p.get('error_category') if p else None
    exp_cat = j['gt'].get('expected_category')
    if pred_cat != exp_cat:
        cat_mismatches.append((j['batch'], j['case_id'], j['system'], pred_cat, exp_cat, j['d1']))

print(f"\nCategory differences vs expected_category: {len(cat_mismatches)}")
for cm in cat_mismatches:
    print(f"  [{cm[0]} | {cm[1]} | {cm[2]}]: Model={cm[3]} vs Expected={cm[4]} (Current D1={cm[5]})")

