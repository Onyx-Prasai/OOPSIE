import json, re

with open('evaluation/benchmark.jsonl', 'r', encoding='utf-8') as f:
    bench_cases = {x['id']: x for x in (json.loads(line) for line in f)}

import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a
from inspect_all_evals import all_evals

# Let's inspect specific response quotes to enrich concerns
records = []
for ar in a.audit_results:
    batch_num = int(ar['batch'].split('_')[1].split('.')[0])
    raw_eval = [e for e in all_evals if e['batch'] == batch_num and e['case_id'] == ar['case_id'] and e['system'] == ar['system']][0]
    gt = bench_cases.get(ar['case_id'], {})
    p = raw_eval['parsed']
    raw_text = raw_eval['raw']
    
    pred_cat = p.get('error_category') if p else None
    exp_cat = gt.get('expected_category')
    
    records.append({
        "batch": ar['batch'],
        "case_id": ar['case_id'],
        "system": ar['system'],
        "gate": ar['gate'],
        "ratings": {
            "d1": ar['d1'],
            "d2": ar['d2'],
            "d3": ar['d3'],
            "d4": ar['d4'],
            "d5": ar['d5']
        },
        "notes": ar['notes'],
        "pred_cat": pred_cat,
        "exp_cat": exp_cat,
        "parsed": p,
        "parsed_ok": raw_eval['parsed_ok'],
        "raw": raw_text,
        "raw_len": raw_eval['raw_len'],
        "gt": gt
    })

print(f"Loaded {len(records)} records for checklist generation.")

