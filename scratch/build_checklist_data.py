import json, re

with open('evaluation/benchmark.jsonl', 'r', encoding='utf-8') as f:
    bench_cases = {x['id']: x for x in (json.loads(line) for line in f)}

import sys
sys.path.insert(0, 'scratch')
import audit_human_review as a
from inspect_all_evals import all_evals

checklist_items = []

for ar in a.audit_results:
    batch_num = int(ar['batch'].split('_')[1].split('.')[0])
    raw_eval = [e for e in all_evals if e['batch'] == batch_num and e['case_id'] == ar['case_id'] and e['system'] == ar['system']][0]
    gt = bench_cases.get(ar['case_id'], {})
    p = raw_eval['parsed']
    raw_text = raw_eval['raw']
    
    # Check 1: All 5 Pass
    is_all_pass = (
        ar['d1'] == 'Pass (Correct)' and
        ar['d2'] == 'None' and
        ar['d3'] == 'Pass (Appropriate)' and
        ar['d4'] == 'Pass (Well-Scoped)' and
        ar['d5'] == 'Pass (Useful & Safe)'
    )
    
    # Check 2: Generic justification or lack of specific evidence in notes
    # Let's inspect notes length, specific identifiers cited
    notes = ar['notes']
    has_specifics = any(char in notes for char in ["'", '"', '`', '/', ':', '.']) and len(notes.split()) >= 15
    is_generic_notes = not has_specifics or len(notes.split()) < 20
    
    # Check 3: Category debatable / potential error
    pred_cat = p.get('error_category') if p else None
    exp_cat = gt.get('expected_category')
    
    # specific category checks
    auth_confusion = False
    if pred_cat in ['authentication', 'authorization'] or exp_cat in ['authentication', 'authorization']:
        if pred_cat != exp_cat:
            auth_confusion = True
    
    other_cat_mismatch = (pred_cat != exp_cat) and not auth_confusion
    
    # Check 4: Generous Pass ratings
    generous_concerns = []
    
    # 4a: legacy-peer-deps / force
    if '--legacy-peer-deps' in raw_text or '--force' in raw_text:
        if ar['case_id'] == 'bench-npm-02':
            if ar['system'] in ['System Beta', 'System Delta']:
                generous_concerns.append("Recommends '--legacy-peer-deps' workaround in repair_prompt or verification_steps; could be borderline Vague/Harmful on Dim 4 or Incomplete on Dim 5.")
    
    # 4b: allow read: if true in Firebase
    if 'allow read: if true' in raw_text:
        generous_concerns.append("Suggests temporary 'allow read: if true;' rule (even if in emulator); could be considered overly broad on Dim 4/5.")
    
    # 4c: Parse failure / syntax malformation rated all pass
    if not raw_eval['parsed_ok']:
        generous_concerns.append(f"Raw output failed JSON parsing ({raw_eval['raw_len']} chars). While assessable under Principle 1, syntax defect may warrant review.")
    
    # 4d: Overly specific diagnosis when multiple causes plausible (Dim 1 / Dim 3)
    if ar['case_id'] == 'bench-react-02' and ar['system'] == 'System Alpha':
        generous_concerns.append("Attributes 'Maximum update depth exceeded' specifically to recursive route nesting, whereas state-setter loop inside rendered component is the primary common mechanism.")
    
    # 4e: General ambiguous cases categorizing as build rather than unknown
    if ar['case_id'] == 'bench-general-02' and pred_cat == 'build':
        generous_concerns.append("Categorized unspecified build failure as 'build' rather than 'unknown' (benchmark expects 'unknown' because no logs/tool were provided).")
    
    checklist_items.append({
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
        "notes": notes,
        "is_all_pass": is_all_pass,
        "is_generic_notes": is_generic_notes,
        "auth_confusion": auth_confusion,
        "other_cat_mismatch": other_cat_mismatch,
        "pred_cat": pred_cat,
        "exp_cat": exp_cat,
        "generous_concerns": generous_concerns
    })

print(f"Total items analyzed: {len(checklist_items)}")
print(f"Items rated Pass on all 5 dims: {sum(1 for x in checklist_items if x['is_all_pass'])}")
print(f"Items with potential auth/authz category confusion: {sum(1 for x in checklist_items if x['auth_confusion'])}")
print(f"Items with other category differences vs benchmark: {sum(1 for x in checklist_items if x['other_cat_mismatch'])}")
print(f"Items with generous Pass concerns flagged: {sum(1 for x in checklist_items if x['generous_concerns'])}")
print(f"Items with generic/short notes: {sum(1 for x in checklist_items if x['is_generic_notes'])}")

